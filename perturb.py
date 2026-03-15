#!/usr/bin/env python3
"""
Stochastic Perturbation Engine (Stage C)
Monte Carlo concept-space exploration via Anthropic API.

Usage:
  python perturb.py --artifact "text..." --findings "predicates..."
  python perturb.py --artifact-file path/to/artifact.txt --findings-file path/to/findings.txt
  python perturb.py --artifact "text..." --findings "predicates..." --rounds 2 --seeds 4 --tokens 7

Requires:
  pip install anthropic sentencepiece transformers

Environment:
  ANTHROPIC_API_KEY must be set (or in .env file in working directory)
"""

import argparse
import asyncio
import hashlib
import json
import os
import random
import re
import sys
import time
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: pip install anthropic", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL = "claude-sonnet-4-20250514"
SEED_AGENT_MAX_TOKENS = 4096
WATCHER_MAX_TOKENS = 4096

SCORE_WEIGHTS = {"specificity": 0.3, "novelty": 0.3, "formal_validity": 0.2, "actionability": 0.2}
SIGNAL_THRESHOLDS = {"noise": 0.3, "faint_echo": 0.5, "actionable": 0.7, "significant": 1.0}

SEED_AGENT_PROMPT = """You are a stochastic perturbation seed agent. Complete all three tasks exactly.

**Your random tokens** (sampled computationally from NLLB-200 multilingual tokenizer):
{tokens}

**Task 1 — Random Walk Story (100-200 words)**:
Write a coherent paragraph incorporating ALL tokens above. They may appear as parts of words, sounds, names, or concepts. Generate past initial incoherence into a locally coherent story fragment.

**Task 2 — Predicate Calculus Bridge**:
The thinker's concern (formalized):
```
{findings}
```

Formalize your story's key concepts as predicates. Then identify logical bridges between the story predicates and the thinker's predicates:
- Structural isomorphism: ∀x: P(x) → Q(x) in story maps to ∀x: P'(x) → Q'(x) in concern
- Negation revelation: story contains ¬R(x) where thinker assumes R(x)
- Compositional insight: combining predicates yields a new predicate not in either set alone

If no formally articulable bridge exists, report signal: 0.

**Task 3 — Reflection (150-200 words)**:
Using the predicate bridge as backbone, reflect on what the story reveals about the thinker's negative space. Reference specific predicates from both sides.

**Output as JSON** with keys: story, story_predicates, bridge_predicates, reflection, signal (integer 1-5)"""

WATCHER_PROMPT = """You are a watcher agent for a stochastic perturbation protocol. You must evaluate seed agent reflections using ONLY the scoring formula below. You have NO access to the random walk stories — only the reflections and predicate bridges.

**Thinker's concern**:
```
{findings}
```

**Stage B (deterministic) already found**:
{stage_b_summary}

---

{reflections_block}

---

**SCORING FORMULA:**
```
S = 0.3 * Specificity + 0.3 * Novelty + 0.2 * FormalValidity + 0.2 * Actionability

Specificity (0-1): Could this apply to a different thinker? 0=generic, 1=unique
Novelty (0-1): Already in Stage B? 0=redundant, 1=new
FormalValidity (0-1): Bridge logically sound? 0=association, 1=valid isomorphism
Actionability (0-1): Thinker gains new question/distinction? 0=inert, 1=actionable
```

Thresholds: S < 0.3 noise, 0.3-0.5 faint echo, 0.5-0.7 actionable, >= 0.7 significant.

Check for Forced Connection anti-pattern: if self-assessed signal >= 3 but bridge predicates are abstract (e.g., Changes(X)), override score downward.

**Output as JSON** with keys:
- scores: list of objects with keys: seed_id, specificity, novelty, formal_validity, actionability, S, band, inflated (bool)
- meta_assessment: string — did any seed reach territory Stage B could not?
- top_findings: list of strings — the reflections worth delivering (S >= 0.5)"""


# ---------------------------------------------------------------------------
# Step 1: Seed Generation (computational)
# ---------------------------------------------------------------------------

def extract_entropy(text: str) -> list[str]:
    """Extract numerical features from artifact text."""
    lower = text.lower()
    return [
        str(sum(1 for c in lower if c in "aeiou")),
        str(sum(1 for c in lower if c.isalpha() and c not in "aeiou")),
        str(len(text)),
        str(text.count(".")),
        str(text.count(" ")),
        str(len(text.split("."))),
    ]


def generate_seeds(features: list[str], n: int, round_num: int = 0) -> list[int]:
    """Hash features into N deterministic seeds. round_num shifts the hash."""
    payload = "|".join(features)
    if round_num > 0:
        payload = payload[::-1] + f"|round={round_num}"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return [int(digest[i : i + 16], 16) for i in range(0, n * 16, 16)]


def load_tokenizer():
    """Load NLLB-200 tokenizer and filter to pure word tokens."""
    try:
        from transformers import AutoTokenizer
    except ImportError:
        print("ERROR: pip install sentencepiece transformers", file=sys.stderr)
        sys.exit(1)

    print("  Loading NLLB-200 tokenizer...", file=sys.stderr)
    tok = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
    vocab = tok.get_vocab()

    pure_word = re.compile(
        r"^[\u0041-\u005A\u0061-\u007A\u00C0-\u024F"
        r"\u0400-\u04FF\u0600-\u06FF\u0900-\u097F"
        r"\u0980-\u09FF\u0A00-\u0A7F\u0B00-\u0B7F"
        r"\u0C00-\u0C7F\u0D00-\u0D7F\u0E00-\u0E7F"
        r"\u1000-\u109F\u3040-\u30FF\u3400-\u9FFF"
        r"\uAC00-\uD7AF\u4E00-\u9FFF\u0530-\u058F"
        r"\u10A0-\u10FF]+$"
    )

    word_tokens = [
        (tid, s.replace("\u2581", ""))
        for s, tid in vocab.items()
        if pure_word.match(s.replace("\u2581", "")) and len(s.replace("\u2581", "")) >= 2
    ]
    print(f"  Filtered vocab: {len(word_tokens)} word tokens", file=sys.stderr)
    return word_tokens


def sample_tokens(word_tokens: list, seeds: list[int], k: int) -> dict[str, list[str]]:
    """Sample K random tokens per seed from multilingual vocabulary."""
    result = {}
    for i, seed in enumerate(seeds):
        rng = random.Random(seed)
        selected = rng.sample(word_tokens, k)
        result[f"seed_{i + 1}"] = [t[1] for t in selected]
    return result


# ---------------------------------------------------------------------------
# Steps 2-3: Seed Agents (parallel API calls)
# ---------------------------------------------------------------------------

async def run_seed_agent(
    client: anthropic.AsyncAnthropic,
    seed_id: str,
    tokens: list[str],
    findings: str,
) -> dict:
    """Run one seed agent via the Anthropic API."""
    prompt = SEED_AGENT_PROMPT.format(
        tokens=json.dumps(tokens, ensure_ascii=False),
        findings=findings,
    )

    t0 = time.time()
    response = await client.messages.create(
        model=MODEL,
        max_tokens=SEED_AGENT_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed = time.time() - t0
    text = response.content[0].text

    # Try to extract JSON from the response
    parsed = _extract_json(text)
    if parsed is None:
        parsed = {
            "story": "",
            "story_predicates": "",
            "bridge_predicates": "",
            "reflection": text,
            "signal": 0,
            "raw": True,
        }

    parsed["seed_id"] = seed_id
    parsed["tokens"] = tokens
    parsed["elapsed_s"] = round(elapsed, 1)
    parsed["input_tokens"] = response.usage.input_tokens
    parsed["output_tokens"] = response.usage.output_tokens
    return parsed


async def run_seed_agents(
    client: anthropic.AsyncAnthropic,
    seed_tokens: dict[str, list[str]],
    findings: str,
) -> list[dict]:
    """Run all seed agents in parallel."""
    tasks = [
        run_seed_agent(client, seed_id, tokens, findings)
        for seed_id, tokens in seed_tokens.items()
    ]
    return await asyncio.gather(*tasks)


# ---------------------------------------------------------------------------
# Step 4: Watcher Agent
# ---------------------------------------------------------------------------

async def run_watcher(
    client: anthropic.AsyncAnthropic,
    seed_results: list[dict],
    findings: str,
    stage_b_summary: str,
) -> dict:
    """Run the watcher agent — receives only reflections and bridges, NOT stories."""
    reflections_parts = []
    for r in seed_results:
        block = f"**{r['seed_id'].upper()}**\n"
        block += f"Bridge:\n```\n{r.get('bridge_predicates', 'N/A')}\n```\n"
        block += f"Self-assessed signal: {r.get('signal', 0)}\n\n"
        block += f"Reflection: {r.get('reflection', 'N/A')}\n"
        reflections_parts.append(block)

    prompt = WATCHER_PROMPT.format(
        findings=findings,
        stage_b_summary=stage_b_summary,
        reflections_block="\n---\n".join(reflections_parts),
    )

    t0 = time.time()
    response = await client.messages.create(
        model=MODEL,
        max_tokens=WATCHER_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed = time.time() - t0
    text = response.content[0].text

    parsed = _extract_json(text)
    if parsed is None:
        parsed = {"raw_text": text, "parse_failed": True}

    parsed["elapsed_s"] = round(elapsed, 1)
    parsed["input_tokens"] = response.usage.input_tokens
    parsed["output_tokens"] = response.usage.output_tokens
    return parsed


# ---------------------------------------------------------------------------
# Step 5: Iteration Loop
# ---------------------------------------------------------------------------

async def run_perturbation(
    artifact: str,
    findings: str,
    stage_b_summary: str = "",
    max_rounds: int = 3,
    n_seeds: int = 3,
    k_tokens: int = 6,
) -> dict:
    """Run the full stochastic perturbation pipeline."""

    client = anthropic.AsyncAnthropic()

    # Load tokenizer once
    print("[Step 0] Loading tokenizer...", file=sys.stderr)
    word_tokens = load_tokenizer()

    features = extract_entropy(artifact)
    all_rounds = []
    best_score = 0.0

    for round_num in range(max_rounds):
        print(f"\n[Round {round_num + 1}/{max_rounds}]", file=sys.stderr)

        # Step 1: Seed generation
        print("  [Step 1] Generating seeds...", file=sys.stderr)
        seeds = generate_seeds(features, n_seeds, round_num)
        seed_tokens = sample_tokens(word_tokens, seeds, k_tokens)

        for sid, toks in seed_tokens.items():
            print(f"    {sid}: {toks}", file=sys.stderr)

        # Steps 2-3: Parallel seed agents
        print(f"  [Steps 2-3] Spawning {n_seeds} seed agents in parallel...", file=sys.stderr)
        seed_results = await run_seed_agents(client, seed_tokens, findings)

        for r in seed_results:
            sig = r.get("signal", 0)
            print(f"    {r['seed_id']}: signal={sig}, elapsed={r['elapsed_s']}s", file=sys.stderr)

        # Step 4: Watcher
        print("  [Step 4] Spawning watcher agent...", file=sys.stderr)
        watcher_result = await run_watcher(client, seed_results, findings, stage_b_summary)
        print(f"    Watcher elapsed: {watcher_result.get('elapsed_s', '?')}s", file=sys.stderr)

        round_data = {
            "round": round_num + 1,
            "seeds": seed_tokens,
            "seed_results": seed_results,
            "watcher": watcher_result,
        }
        all_rounds.append(round_data)

        # Check if we have signal
        scores = watcher_result.get("scores", [])
        for s in scores:
            score_val = s.get("S", 0)
            if isinstance(score_val, (int, float)):
                best_score = max(best_score, score_val)

        if best_score >= 0.5:
            print(f"\n  Signal found (best S={best_score:.2f}). Delivering.", file=sys.stderr)
            break
        else:
            print(f"  No signal (best S={best_score:.2f}). ", file=sys.stderr, end="")
            if round_num < max_rounds - 1:
                print("Trying next round...", file=sys.stderr)
            else:
                print("Max rounds reached.", file=sys.stderr)

    # Compile final output
    output = {
        "rounds_run": len(all_rounds),
        "best_score": best_score,
        "signal_found": best_score >= 0.5,
        "rounds": all_rounds,
        "top_findings": watcher_result.get("top_findings", []),
        "meta_assessment": watcher_result.get("meta_assessment", ""),
    }

    # Compute total token usage
    total_in = sum(
        r.get("input_tokens", 0)
        for rd in all_rounds
        for r in rd["seed_results"]
    ) + sum(rd["watcher"].get("input_tokens", 0) for rd in all_rounds)

    total_out = sum(
        r.get("output_tokens", 0)
        for rd in all_rounds
        for r in rd["seed_results"]
    ) + sum(rd["watcher"].get("output_tokens", 0) for rd in all_rounds)

    output["total_input_tokens"] = total_in
    output["total_output_tokens"] = total_out

    return output


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> dict | None:
    """Try to extract a JSON object from LLM output."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON block in markdown
    patterns = [
        r"```json\s*\n(.*?)\n```",
        r"```\s*\n(\{.*?\})\n```",
        r"(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue

    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Stochastic Perturbation Engine (Stage C)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--artifact", type=str, help="Thinker's artifact text")
    parser.add_argument("--artifact-file", type=str, help="Path to artifact text file")
    parser.add_argument("--findings", type=str, help="Predicate formalization of L1-2 + Stage A-B findings")
    parser.add_argument("--findings-file", type=str, help="Path to findings file")
    parser.add_argument("--stage-b-summary", type=str, default="", help="Summary of Stage B findings")
    parser.add_argument("--rounds", type=int, default=3, help="Max iteration rounds (default: 3)")
    parser.add_argument("--seeds", type=int, default=3, help="Seeds per round (default: 3)")
    parser.add_argument("--tokens", type=int, default=6, help="Tokens per seed (default: 6)")
    parser.add_argument("--seeds-only", action="store_true", help="Only run Step 1 (seed generation), skip API calls")
    parser.add_argument("--output", type=str, help="Output file path (default: stdout)")

    args = parser.parse_args()

    # Load artifact
    artifact = args.artifact
    if args.artifact_file:
        artifact = Path(args.artifact_file).read_text()
    if not artifact:
        parser.error("Provide --artifact or --artifact-file")

    # Load findings
    findings = args.findings or ""
    if args.findings_file:
        findings = Path(args.findings_file).read_text()
    if not findings and not args.seeds_only:
        parser.error("Provide --findings or --findings-file")

    # Seeds-only mode (no API key needed)
    if args.seeds_only:
        word_tokens = load_tokenizer()
        features = extract_entropy(artifact)
        for round_num in range(args.rounds):
            seeds = generate_seeds(features, args.seeds, round_num)
            seed_tokens = sample_tokens(word_tokens, seeds, args.tokens)
            print(json.dumps({"round": round_num + 1, "seeds": seed_tokens}, ensure_ascii=False, indent=2))
        return

    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        # Try .env file
        env_path = Path(".env")
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    os.environ["ANTHROPIC_API_KEY"] = line.split("=", 1)[1].strip().strip('"\'')
                    break

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY environment variable or create .env file", file=sys.stderr)
        sys.exit(1)

    # Run
    result = asyncio.run(
        run_perturbation(
            artifact=artifact,
            findings=findings,
            stage_b_summary=args.stage_b_summary,
            max_rounds=args.rounds,
            n_seeds=args.seeds,
            k_tokens=args.tokens,
        )
    )

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output)
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
