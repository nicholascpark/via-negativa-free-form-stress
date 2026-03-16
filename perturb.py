#!/usr/bin/env python3
"""
Stochastic Perturbation — Seed Generator (Stage C, Phase 1)

Computational seed generation for the via-negativa stochastic perturbation
protocol. Handles ONLY the math: entropy extraction, SHA-256 hashing, and
NLLB-200 multilingual token sampling. No API key required.

Agent spawning (Phase 2) is handled by the skill's imperative instructions
within the Claude conversation — not by this script.

Usage:
  python perturb.py --seeds-only --artifact "text..."
  python perturb.py --seeds-only --artifact-file path/to/artifact.txt
  python perturb.py --seeds-only --artifact "text..." --rounds 2 --seeds 4 --tokens 7
  python perturb.py --seeds-only --artifact "text..." --round 2  # specific round number

Requires:
  pip install sentencepiece transformers
"""

import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path

# Portable import: ensure prompt_templates.py is found regardless of cwd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompt_templates import render_seed_agent_prompt, render_watcher_prompt


def extract_entropy(text: str) -> list[str]:
    """Extract numerical features from artifact text for seeding RNG."""
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
    """Load NLLB-200 tokenizer and filter to pure word tokens (~213K tokens, 15+ scripts)."""
    try:
        from transformers import AutoTokenizer
    except ImportError:
        print("ERROR: pip install sentencepiece transformers", file=sys.stderr)
        sys.exit(1)

    print("Loading NLLB-200 tokenizer...", file=sys.stderr)
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
    print(f"Filtered vocab: {len(word_tokens)} word tokens", file=sys.stderr)
    return word_tokens


def sample_tokens(word_tokens: list, seeds: list[int], k: int) -> dict[str, list[str]]:
    """Sample K random tokens per seed from multilingual vocabulary."""
    result = {}
    for i, seed in enumerate(seeds):
        rng = random.Random(seed)
        selected = rng.sample(word_tokens, k)
        result[f"seed_{i + 1}"] = [t[1] for t in selected]
    return result


def persist_inputs(artifact: str, concern: str, predicates: str, stage_b: str):
    """Write inputs to /tmp for iteration round reuse. Restricts permissions to owner-only."""
    import os
    for path, content in [
        ("/tmp/vn-artifact.txt", artifact),
        ("/tmp/vn-concern.txt", concern),
        ("/tmp/vn-predicates.txt", predicates),
    ]:
        Path(path).write_text(content)
        os.chmod(path, 0o600)
    if stage_b:
        Path("/tmp/vn-stageb.txt").write_text(stage_b)
        os.chmod("/tmp/vn-stageb.txt", 0o600)


def build_manifest(
    seed_tokens: dict[str, list[str]],
    concern: str,
    predicates: str,
    stage_b: str,
    round_num: int,
    script_path: str,
) -> dict:
    """Build the complete execution manifest with agent prompts."""
    agents = []
    for seed_id, tokens in seed_tokens.items():
        agents.append({
            "id": seed_id,
            "prompt": render_seed_agent_prompt(tokens, concern, predicates),
        })

    next_round = round_num + 1
    manifest = {
        "protocol": "via-negativa-stochastic-perturbation",
        "version": 1,
        "round": round_num,
        "steps": [
            {
                "step": "seed_agents",
                "dispatch": "parallel",
                "agents": agents,
            },
            {
                "step": "watcher",
                "dispatch": "after_seed_agents",
                "input_from": "seed_agents",
                "input_fields": ["bridge_predicates", "reflection", "signal"],
                "stage_b_synthesis": stage_b,
                "prompt": render_watcher_prompt(stage_b),
            },
        ],
        "iteration": {
            "signal_threshold": 0.5,
            "max_rounds": 3,
            "next_round_command": (
                f"python3 {script_path} --orchestrate"
                f" --artifact-file /tmp/vn-artifact.txt"
                f" --predicates-file /tmp/vn-predicates.txt"
                f" --concern-file /tmp/vn-concern.txt"
                f" --stage-b-file /tmp/vn-stageb.txt"
                f" --round {next_round}"
            ),
        },
    }
    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Stochastic Perturbation — Seed Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--artifact", type=str, help="Thinker's artifact text")
    parser.add_argument("--artifact-file", type=str, help="Path to artifact text file")
    parser.add_argument("--rounds", type=int, default=1, help="Number of rounds to generate (default: 1)")
    parser.add_argument("--round", type=int, default=None, help="Specific round number (for iteration)")
    parser.add_argument("--seeds", type=int, default=3, help="Seeds per round (default: 3)")
    parser.add_argument("--tokens", type=int, default=6, help="Tokens per seed (default: 6)")
    parser.add_argument("--seeds-only", action="store_true", default=True, help="(default, kept for compatibility)")
    parser.add_argument("--orchestrate", action="store_true", default=False,
                        help="Output full execution manifest with agent prompts (JSON)")
    parser.add_argument("--concern-summary", type=str, help="Natural-language concern summary")
    parser.add_argument("--concern-file", type=str, help="Path to concern summary file")
    parser.add_argument("--predicates", type=str, help="Predicate formalization string")
    parser.add_argument("--predicates-file", type=str, help="Path to predicates file")
    parser.add_argument("--stage-b-synthesis", type=str, help="Stage B synthesis output")
    parser.add_argument("--stage-b-file", type=str, help="Path to Stage B synthesis file")

    args = parser.parse_args()

    # Load artifact
    artifact = args.artifact
    if args.artifact_file:
        artifact = Path(args.artifact_file).read_text()
    if not artifact:
        parser.error("Provide --artifact or --artifact-file")

    if args.orchestrate:
        # Load concern summary
        concern = args.concern_summary
        if args.concern_file:
            concern = Path(args.concern_file).read_text()
        if not concern:
            parser.error("--orchestrate requires --concern-summary or --concern-file")

        # Load predicates
        predicates = args.predicates
        if args.predicates_file:
            predicates = Path(args.predicates_file).read_text()
        if not predicates:
            parser.error("--orchestrate requires --predicates or --predicates-file")

        # Load stage B synthesis (optional but recommended)
        stage_b = args.stage_b_synthesis or ""
        if args.stage_b_file:
            stage_b = Path(args.stage_b_file).read_text()

        # Orchestrate mode: generate manifest and return
        word_tokens = load_tokenizer()
        features = extract_entropy(artifact)

        round_num = args.round if args.round is not None else 1
        seeds = generate_seeds(features, args.seeds, round_num)
        seed_tokens = sample_tokens(word_tokens, seeds, args.tokens)

        persist_inputs(artifact, concern, predicates, stage_b)

        script_path = "${CLAUDE_SKILL_DIR}/perturb.py"
        manifest = build_manifest(
            seed_tokens, concern, predicates, stage_b,
            round_num, script_path,
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return

    # Seeds-only mode (existing behavior)
    word_tokens = load_tokenizer()
    features = extract_entropy(artifact)

    if args.round is not None:
        # Single specific round
        seeds = generate_seeds(features, args.seeds, args.round)
        seed_tokens = sample_tokens(word_tokens, seeds, args.tokens)
        print(json.dumps({"round": args.round, "seeds": seed_tokens}, ensure_ascii=False, indent=2))
    else:
        # Multiple rounds
        for round_num in range(args.rounds):
            seeds = generate_seeds(features, args.seeds, round_num)
            seed_tokens = sample_tokens(word_tokens, seeds, args.tokens)
            print(json.dumps({"round": round_num + 1, "seeds": seed_tokens}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
