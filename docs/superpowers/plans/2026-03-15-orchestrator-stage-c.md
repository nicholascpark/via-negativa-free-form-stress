# Stage C Orchestrator + Auto-Progression Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Stage C (Stochastic Perturbation) actually execute by moving the algorithm into Python and reducing the LLM's role to manifest dispatch.

**Architecture:** Extend `perturb.py` with `--orchestrate` mode that outputs complete execution manifests (seed agent prompts, watcher prompts, iteration commands) as JSON. Harden `SKILL.md` with hard gates and auto-progression. No new dependencies or API keys.

**Tech Stack:** Python 3.10+, transformers, sentencepiece, JSON, pytest

**Spec:** `docs/superpowers/specs/2026-03-15-orchestrator-stage-c-design.md`
**Algorithm reference:** `stochastic-perturbation-algorithm.txt`

---

## File Structure

| File | Responsibility |
|------|---------------|
| `perturb.py` | Seed generation (existing) + orchestrator manifest generation (new) + prompt templates (new) + file persistence (new) |
| `prompt_templates.py` | Hardcoded seed agent and watcher prompt templates — extracted to keep perturb.py focused |
| `SKILL.md` | Skill instructions with hard gates and orchestrator dispatch block |
| `tests/test_perturb.py` | Unit tests for orchestrator mode, manifest structure, file persistence |
| `tests/conftest.py` | Adds repo root to sys.path for portable imports |
| `tests/test_prompt_templates.py` | Unit tests for prompt template rendering |

---

## Chunk 1: Prompt Templates

### Task 1: Create seed agent prompt template

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_prompt_templates.py`
- Create: `prompt_templates.py`

- [ ] **Step 1: Write the failing test for seed agent prompt rendering**

```python
# tests/conftest.py — create this file first
import sys
from pathlib import Path

# Add repo root to sys.path so tests can import prompt_templates
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
```

```python
# tests/test_prompt_templates.py
from prompt_templates import render_seed_agent_prompt


def test_seed_agent_prompt_contains_tokens():
    tokens = ["Esituluilo", "риб", "وحد"]
    concern = "Thinker is planning a career change to consulting."
    predicates = "Plans(thinker, career_change)\nAssumes(plan, network_converts)"
    result = render_seed_agent_prompt(tokens, concern, predicates)
    for token in tokens:
        assert token in result


def test_seed_agent_prompt_contains_predicates():
    tokens = ["foo", "bar"]
    concern = "Test concern."
    predicates = "Plans(thinker, X)\nAbsent(plan, Y)"
    result = render_seed_agent_prompt(tokens, concern, predicates)
    assert "Plans(thinker, X)" in result
    assert "Absent(plan, Y)" in result


def test_seed_agent_prompt_contains_concern_summary():
    tokens = ["foo"]
    concern = "Thinker is stuck on a decision about moving cities."
    predicates = "Plans(thinker, X)"
    result = render_seed_agent_prompt(tokens, concern, predicates)
    assert "moving cities" in result


def test_seed_agent_prompt_contains_bridge_types():
    tokens = ["foo"]
    concern = "Test."
    predicates = "X(y)"
    result = render_seed_agent_prompt(tokens, concern, predicates)
    assert "Structural isomorphism" in result
    assert "Negation revelation" in result
    assert "Compositional insight" in result


def test_seed_agent_prompt_contains_output_format():
    tokens = ["foo"]
    concern = "Test."
    predicates = "X(y)"
    result = render_seed_agent_prompt(tokens, concern, predicates)
    assert "story" in result
    assert "story_predicates" in result
    assert "bridge_predicates" in result
    assert "reflection" in result
    assert "signal" in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/nicholaspark/Documents/via-negativa-free-form-stress && python -m pytest tests/test_prompt_templates.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'prompt_templates'`

- [ ] **Step 3: Implement `prompt_templates.py` with seed agent template**

```python
# prompt_templates.py
"""
Hardcoded prompt templates for the stochastic perturbation protocol.
These are the source of truth for seed agent and watcher instructions.
The algorithm spec lives in stochastic-perturbation-algorithm.txt.
"""

import json


def render_seed_agent_prompt(
    tokens: list[str],
    concern_summary: str,
    predicates: str,
) -> str:
    """Build a complete seed agent prompt with tokens, concern, and predicates embedded."""
    return f"""You are a stochastic perturbation seed agent. Complete all three tasks below.

**Your random tokens** (sampled computationally from NLLB-200 multilingual tokenizer):
{json.dumps(tokens, ensure_ascii=False)}

**Thinker's concern summary:**
{concern_summary}

---

**Task 1 — Random Walk Story (100-200 words)**

Write a coherent paragraph that incorporates ALL of the random tokens above.
The tokens may appear as character names, place names, sounds, concepts, or
morphological components of words. Generate past initial incoherence into a
local semantic basin — a coherent story that exists in an alien region of
concept space because its starting conditions were genuinely random.

The paragraph is SCAFFOLDING — its value is in the semantic territory it
occupies, not in its content.

---

**Task 2 — Predicate Calculus Bridge**

The thinker's concern (formalized as first-order predicates):
{predicates}

2a. Formalize your story as predicates. Extract key concepts and relationships:
    Example: TransformsUnder(X, pressure), BuiltFor(raft, crossing) ∧ NatureOf(river, reflecting)

2b. Identify bridges between your story predicates and the thinker's predicates.
    Three types of valid bridges:

    **Structural isomorphism:**
    ∀x: P(x) → Q(x) in story maps to ∀x: P'(x) → Q'(x) in concern.
    Example: BuiltFor(raft, crossing) ∧ NatureOf(river, reflecting)
             ≅ BuiltFor(plan, transition) ∧ NatureOf(consulting, exposing)

    **Negation revelation:**
    Story contains ¬R(x) where thinker assumes R(x).
    Example: ¬Portable(identity_across_media) negates
             Assumes(plan, skills_transfer_directly)

    **Compositional insight:**
    Combining story + thinker predicates yields a new predicate in neither.
    Example: Obligation(imagined_self) ∧ LatentQuestion(thinker) →
             DebtTo(thinker, unauthorized_version_of_self)

    If NO formally articulable bridge exists, report signal: 0.
    The predicate calculus step is the anti-bullshit filter: connections must
    be logically statable, not merely associatively felt.

---

**Task 3 — Reflection (150-200 words)**

Using the bridge as backbone, reflect on what the story reveals about the
thinker's negative space. Reference specific predicates from both sides.

---

**Output format** (use these exact field names):
1. story: your generated paragraph
2. story_predicates: formal notation
3. bridge_predicates: formal notation (or "none — signal: 0")
4. reflection: natural language, predicate-grounded
5. signal: self-assessed 1-5 (1 = noise, 5 = significant structural insight)"""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/nicholaspark/Documents/via-negativa-free-form-stress && python -m pytest tests/test_prompt_templates.py -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_prompt_templates.py prompt_templates.py
git commit -m "feat: add seed agent prompt template with bridge types and output format"
```

---

### Task 2: Add watcher prompt template

**Files:**
- Modify: `tests/test_prompt_templates.py`
- Modify: `prompt_templates.py`

- [ ] **Step 1: Write the failing tests for watcher prompt rendering**

```python
# append to tests/test_prompt_templates.py
from prompt_templates import render_watcher_prompt


def test_watcher_prompt_contains_scoring_formula():
    stage_b = "Pattern: plan is detailed about WHAT, silent about WHO."
    result = render_watcher_prompt(stage_b)
    assert "0.3*Specificity" in result or "0.3 * Specificity" in result
    assert "0.3*Novelty" in result or "0.3 * Novelty" in result
    assert "0.2*FormalValidity" in result or "0.2 * FormalValidity" in result
    assert "0.2*Actionability" in result or "0.2 * Actionability" in result


def test_watcher_prompt_contains_thresholds():
    stage_b = "Test synthesis."
    result = render_watcher_prompt(stage_b)
    assert "0.3" in result  # faint echo lower bound
    assert "0.5" in result  # actionable lower bound
    assert "0.7" in result  # significant lower bound


def test_watcher_prompt_contains_stage_b_for_novelty():
    stage_b = "The latent thought is about identity transformation."
    result = render_watcher_prompt(stage_b)
    assert "identity transformation" in result


def test_watcher_prompt_contains_placeholder():
    stage_b = "Test."
    result = render_watcher_prompt(stage_b)
    assert "{{SEED_AGENT_RESULTS}}" in result


def test_watcher_prompt_contains_forced_connection_check():
    stage_b = "Test."
    result = render_watcher_prompt(stage_b)
    assert "Forced Connection" in result


def test_watcher_prompt_contains_meta_assessment():
    stage_b = "Test."
    result = render_watcher_prompt(stage_b)
    assert "Stage B" in result
    assert "deterministic" in result.lower()
```

- [ ] **Step 2: Run tests to verify the new tests fail**

Run: `cd /Users/nicholaspark/Documents/via-negativa-free-form-stress && python -m pytest tests/test_prompt_templates.py -v`
Expected: New watcher tests FAIL with `ImportError` (render_watcher_prompt not defined)

- [ ] **Step 3: Implement `render_watcher_prompt` in `prompt_templates.py`**

```python
# append to prompt_templates.py

def render_watcher_prompt(stage_b_synthesis: str) -> str:
    """Build the watcher agent prompt with scoring formula and Stage B context."""
    return f"""You are a stochastic perturbation watcher agent. You evaluate seed agent
reflections for signal quality. You have NO access to the random walk stories —
you evaluate logical structure only.

**Stage B's deterministic synthesis** (for Novelty evaluation):
{stage_b_synthesis}

---

**Seed agent results to evaluate:**

{{{{SEED_AGENT_RESULTS}}}}

---

**Scoring formula:**

For each seed agent's reflection, score on four criteria (each 0-1):

S = 0.3*Specificity + 0.3*Novelty + 0.2*FormalValidity + 0.2*Actionability

- **Specificity (0-1):** Could this reflection apply to a different thinker with
  a different problem? 0 = generic ("change is hard"), 1 = unique to THIS
  thinker's specific situation and concern.

- **Novelty (0-1):** Is this insight already captured in Stage B's deterministic
  synthesis (provided above)? 0 = redundant restatement, 1 = entirely new
  structural insight.

- **FormalValidity (0-1):** Is the predicate bridge logically sound?
  0 = association masquerading as logic (e.g., "both involve change"),
  1 = valid structural isomorphism or negation with specific predicates.

- **Actionability (0-1):** Does the thinker gain a new question, frame, or
  distinction they can use? 0 = interesting but inert, 1 = changes what
  the thinker does next.

**Signal thresholds:**
- S < 0.3  → noise (discard silently)
- 0.3 ≤ S < 0.5 → faint echo (mention only if nothing better)
- 0.5 ≤ S < 0.7 → actionable (include in output)
- S ≥ 0.7  → significant (foreground in output)

**Forced Connection check:**
If a seed agent self-assessed signal ≥ 3 but the bridge predicates contain
only abstract mappings (e.g., Changes(X) rather than
ReorganizesIdentityUnder(X, pressure)), override the score downward.
The predicate formalization makes this detectable — shallow bridges have
predicates that are too abstract.

**Output format:**
For each seed:
- Specificity score + justification (1 sentence)
- Novelty score + justification (1 sentence)
- FormalValidity score + justification (1 sentence)
- Actionability score + justification (1 sentence)
- Composite S score
- Signal classification (noise / faint echo / actionable / significant)

Then provide a **meta-assessment**: Did any seed reach territory that Stage B's
deterministic synthesis could NOT have reached? This is the key question —
stochastic perturbation is only valuable when it extends the deterministic
pass, not when it restates it in different imagery."""
```

Note: The `{{SEED_AGENT_RESULTS}}` placeholder uses doubled braces `{{{{` / `}}}}` in the f-string to produce the literal `{{SEED_AGENT_RESULTS}}` in the output.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/nicholaspark/Documents/via-negativa-free-form-stress && python -m pytest tests/test_prompt_templates.py -v`
Expected: All 11 tests PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_prompt_templates.py prompt_templates.py
git commit -m "feat: add watcher prompt template with scoring formula and thresholds"
```

---

## Chunk 2: Orchestrator Mode in `perturb.py`

### Task 3: Add new CLI flags for orchestrate mode

**Files:**
- Create: `tests/test_perturb.py`
- Modify: `perturb.py`

- [ ] **Step 1: Write the failing test for new CLI flags**

```python
# tests/test_perturb.py
import subprocess
import sys


def test_orchestrate_flag_requires_concern_and_predicates():
    """--orchestrate without --concern-summary and --predicates should error."""
    result = subprocess.run(
        [sys.executable, "perturb.py", "--orchestrate", "--artifact", "test text here"],
        capture_output=True,
        text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
    )
    assert result.returncode != 0
    assert "concern" in result.stderr.lower() or "predicates" in result.stderr.lower()


def test_orchestrate_flag_accepted_with_all_inputs():
    """--orchestrate with all required inputs should not error on flag parsing."""
    result = subprocess.run(
        [
            sys.executable, "perturb.py",
            "--orchestrate",
            "--artifact", "test text for entropy extraction",
            "--concern-summary", "Thinker is planning a career change.",
            "--predicates", "Plans(thinker, career_change)",
            "--stage-b-synthesis", "Pattern: plan is detailed about WHAT.",
        ],
        capture_output=True,
        text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        timeout=120,
    )
    # May fail on tokenizer load, but should NOT fail on argument parsing
    if result.returncode != 0:
        assert "argument" not in result.stderr.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/nicholaspark/Documents/via-negativa-free-form-stress && python -m pytest tests/test_perturb.py -v`
Expected: FAIL — `--orchestrate` flag not recognized

- [ ] **Step 3: Add new argument flags to `perturb.py`**

Add to the `main()` function's argument parser block (after the existing `--seeds-only` line):

```python
    parser.add_argument("--orchestrate", action="store_true", default=False,
                        help="Output full execution manifest with agent prompts (JSON)")
    parser.add_argument("--concern-summary", type=str, help="Natural-language concern summary")
    parser.add_argument("--concern-file", type=str, help="Path to concern summary file")
    parser.add_argument("--predicates", type=str, help="Predicate formalization string")
    parser.add_argument("--predicates-file", type=str, help="Path to predicates file")
    parser.add_argument("--stage-b-synthesis", type=str, help="Stage B synthesis output")
    parser.add_argument("--stage-b-file", type=str, help="Path to Stage B synthesis file")
```

Add validation after argument parsing (after the existing artifact loading block):

```python
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
```

For now, add a placeholder after the validation that just falls through to the existing seed generation. The orchestrate output logic comes in the next task.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/nicholaspark/Documents/via-negativa-free-form-stress && python -m pytest tests/test_perturb.py -v`
Expected: Both tests PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_perturb.py perturb.py
git commit -m "feat: add --orchestrate CLI flags with input validation"
```

---

### Task 4: Implement manifest generation

**Files:**
- Modify: `tests/test_perturb.py`
- Modify: `perturb.py`

- [ ] **Step 1: Write the failing test for manifest output**

```python
# append to tests/test_perturb.py
import json
import os

# Skip these tests if transformers not installed
try:
    import transformers
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

import pytest


@pytest.mark.skipif(not HAS_TRANSFORMERS, reason="transformers not installed")
def test_orchestrate_outputs_valid_manifest():
    """--orchestrate should output a valid JSON manifest."""
    result = subprocess.run(
        [
            sys.executable, "perturb.py",
            "--orchestrate",
            "--artifact", "I am planning to leave my engineering role and start consulting.",
            "--concern-summary", "Thinker is planning a career change to consulting.",
            "--predicates", "Plans(thinker, career_change)\nAssumes(plan, network_converts)",
            "--stage-b-synthesis", "Pattern: plan detailed about WHAT, silent about WHO.",
        ],
        capture_output=True,
        text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        timeout=120,
    )
    assert result.returncode == 0
    manifest = json.loads(result.stdout)
    assert manifest["protocol"] == "via-negativa-stochastic-perturbation"
    assert manifest["version"] == 1
    assert manifest["round"] == 1
    assert len(manifest["steps"]) == 2
    assert manifest["steps"][0]["step"] == "seed_agents"
    assert manifest["steps"][0]["dispatch"] == "parallel"
    assert manifest["steps"][1]["step"] == "watcher"


@pytest.mark.skipif(not HAS_TRANSFORMERS, reason="transformers not installed")
def test_orchestrate_seed_agents_contain_tokens():
    """Each seed agent prompt should contain its assigned tokens."""
    result = subprocess.run(
        [
            sys.executable, "perturb.py",
            "--orchestrate",
            "--artifact", "Test artifact for token sampling.",
            "--concern-summary", "Test concern.",
            "--predicates", "Test(predicate)",
            "--stage-b-synthesis", "Test synthesis.",
            "--seeds", "2",
            "--tokens", "3",
        ],
        capture_output=True,
        text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        timeout=120,
    )
    manifest = json.loads(result.stdout)
    agents = manifest["steps"][0]["agents"]
    assert len(agents) == 2
    for agent in agents:
        assert "prompt" in agent
        # Prompt should contain the bridge type instructions
        assert "Structural isomorphism" in agent["prompt"]


@pytest.mark.skipif(not HAS_TRANSFORMERS, reason="transformers not installed")
def test_orchestrate_watcher_contains_placeholder():
    """Watcher prompt should contain the {{SEED_AGENT_RESULTS}} placeholder."""
    result = subprocess.run(
        [
            sys.executable, "perturb.py",
            "--orchestrate",
            "--artifact", "Test artifact.",
            "--concern-summary", "Test.",
            "--predicates", "X(y)",
            "--stage-b-synthesis", "Test synthesis.",
        ],
        capture_output=True,
        text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        timeout=120,
    )
    manifest = json.loads(result.stdout)
    watcher = manifest["steps"][1]
    assert "{{SEED_AGENT_RESULTS}}" in watcher["prompt"]
    assert watcher["stage_b_synthesis"] == "Test synthesis."


@pytest.mark.skipif(not HAS_TRANSFORMERS, reason="transformers not installed")
def test_orchestrate_iteration_block():
    """Manifest should contain iteration config with next_round_command."""
    result = subprocess.run(
        [
            sys.executable, "perturb.py",
            "--orchestrate",
            "--artifact", "Test artifact.",
            "--concern-summary", "Test.",
            "--predicates", "X(y)",
            "--stage-b-synthesis", "Test.",
        ],
        capture_output=True,
        text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        timeout=120,
    )
    manifest = json.loads(result.stdout)
    iteration = manifest["iteration"]
    assert iteration["signal_threshold"] == 0.5
    assert iteration["max_rounds"] == 3
    assert "--round 2" in iteration["next_round_command"]
```

- [ ] **Step 2: Run tests to verify the new tests fail**

Run: `cd /Users/nicholaspark/Documents/via-negativa-free-form-stress && python -m pytest tests/test_perturb.py -v`
Expected: New tests FAIL (manifest not generated yet)

- [ ] **Step 3: Implement manifest generation in `perturb.py`**

Add a `build_manifest` function and call it from the `--orchestrate` branch in `main()`. Import `prompt_templates` at the top of the file.

```python
# Add imports at top of perturb.py (after existing imports)
# Portable import: ensure prompt_templates.py is found regardless of cwd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompt_templates import render_seed_agent_prompt, render_watcher_prompt


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
```

In `main()`, restructure the execution flow. The `--orchestrate` block must go **after** artifact loading but **before** the existing `word_tokens = load_tokenizer()` line. The existing seed-only code becomes an `else` branch. This avoids loading the tokenizer twice.

```python
    # --- Existing artifact loading code stays here (lines 110-115) ---

    # Load artifact
    artifact = args.artifact
    if args.artifact_file:
        artifact = Path(args.artifact_file).read_text()
    if not artifact:
        parser.error("Provide --artifact or --artifact-file")

    if args.orchestrate:
        # (input loading/validation code from Task 3 goes here)

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

    # --- Existing seeds-only code (lines 117-130) stays as-is below ---
    word_tokens = load_tokenizer()
    features = extract_entropy(artifact)
    # ... rest of existing round/seeds logic ...
```

Note: `round_num` defaults to `1` (not `0`) when `args.round is None`. This eliminates the zero/None ambiguity in `build_manifest`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/nicholaspark/Documents/via-negativa-free-form-stress && python -m pytest tests/test_perturb.py -v`
Expected: All tests PASS (tests requiring transformers will skip if not installed)

- [ ] **Step 5: Run existing seeds-only mode to verify no regression**

Run: `cd /Users/nicholaspark/Documents/via-negativa-free-form-stress && python3 perturb.py --seeds-only --artifact "test regression check"`
Expected: JSON output with seed tokens, same format as before

- [ ] **Step 6: Commit**

```bash
git add tests/test_perturb.py perturb.py
git commit -m "feat: implement --orchestrate manifest generation with prompt templates"
```

---

### Task 5: Test file persistence for iteration rounds

**Files:**
- Modify: `tests/test_perturb.py`

- [ ] **Step 1: Write the failing test for file persistence**

```python
# append to tests/test_perturb.py

@pytest.mark.skipif(not HAS_TRANSFORMERS, reason="transformers not installed")
def test_orchestrate_persists_inputs_to_tmp():
    """First --orchestrate call should write inputs to /tmp/vn-*.txt."""
    # Clean up any existing files
    for f in ["/tmp/vn-artifact.txt", "/tmp/vn-concern.txt",
              "/tmp/vn-predicates.txt", "/tmp/vn-stageb.txt"]:
        if os.path.exists(f):
            os.remove(f)

    result = subprocess.run(
        [
            sys.executable, "perturb.py",
            "--orchestrate",
            "--artifact", "Persist test artifact.",
            "--concern-summary", "Persist test concern.",
            "--predicates", "Persist(test)",
            "--stage-b-synthesis", "Persist test synthesis.",
        ],
        capture_output=True,
        text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        timeout=120,
    )
    assert result.returncode == 0
    assert os.path.exists("/tmp/vn-artifact.txt")
    assert os.path.exists("/tmp/vn-concern.txt")
    assert os.path.exists("/tmp/vn-predicates.txt")
    assert os.path.exists("/tmp/vn-stageb.txt")
    assert Path("/tmp/vn-artifact.txt").read_text() == "Persist test artifact."
    assert Path("/tmp/vn-predicates.txt").read_text() == "Persist(test)"
```

- [ ] **Step 2: Run tests to verify they pass (persistence was implemented in Task 4)**

Run: `cd /Users/nicholaspark/Documents/via-negativa-free-form-stress && python -m pytest tests/test_perturb.py::test_orchestrate_persists_inputs_to_tmp -v`
Expected: PASS (if Task 4 was implemented correctly). If FAIL, debug and fix.

- [ ] **Step 3: Write tests for file-loading flag variants**

```python
# append to tests/test_perturb.py

@pytest.mark.skipif(not HAS_TRANSFORMERS, reason="transformers not installed")
def test_orchestrate_with_file_flags():
    """--orchestrate should work with file flags for iteration rounds."""
    # Write input files
    Path("/tmp/vn-test-artifact.txt").write_text("File flag test artifact.")
    Path("/tmp/vn-test-concern.txt").write_text("File flag test concern.")
    Path("/tmp/vn-test-predicates.txt").write_text("FileTest(predicate)")
    Path("/tmp/vn-test-stageb.txt").write_text("File flag test synthesis.")

    result = subprocess.run(
        [
            sys.executable, "perturb.py",
            "--orchestrate",
            "--artifact-file", "/tmp/vn-test-artifact.txt",
            "--concern-file", "/tmp/vn-test-concern.txt",
            "--predicates-file", "/tmp/vn-test-predicates.txt",
            "--stage-b-file", "/tmp/vn-test-stageb.txt",
            "--round", "2",
        ],
        capture_output=True,
        text=True,
        cwd="/Users/nicholaspark/Documents/via-negativa-free-form-stress",
        timeout=120,
    )
    assert result.returncode == 0
    manifest = json.loads(result.stdout)
    assert manifest["round"] == 2
    assert "--round 3" in manifest["iteration"]["next_round_command"]
    # Verify file content was loaded into agent prompts
    assert "FileTest(predicate)" in manifest["steps"][0]["agents"][0]["prompt"]
```

- [ ] **Step 4: Run the new test**

Run: `cd /Users/nicholaspark/Documents/via-negativa-free-form-stress && python -m pytest tests/test_perturb.py::test_orchestrate_with_file_flags -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_perturb.py
git commit -m "test: add persistence verification for /tmp/vn-*.txt files"
```

---

## Chunk 3: SKILL.md Modifications

### Task 6: Replace depth levels and remove progressive disclosure

**Files:**
- Modify: `SKILL.md`

- [ ] **Step 1: Locate the sections to change**

In `SKILL.md`, find:
- Lines ~93-107: "Depth levels" paragraph
- Lines ~109-119: "Progressive Disclosure (default)" subsection

- [ ] **Step 2: Replace "Depth levels" and remove "Progressive Disclosure"**

Replace SKILL.md lines 93-120 (from `### Depth levels:` through the end of `### Progressive Disclosure (default)` including the `---` separator) with:

```markdown
### Depth levels:

Two depths. No runtime depth decisions.

- "Quick check" → Layers 1–2 only. Deliver and move to Step R.
- "Stress test" → Layers 1–3, all stages (A, B, C). Default.

The thinker can request either depth explicitly. If no depth is
specified, use "stress test."

<HARD-GATE>
DEPTH = "STRESS TEST" (DEFAULT): Execute Layers 1->2->3 (all stages
A, B, C) as a single continuous pass. Do NOT pause between layers.
Do NOT ask the thinker if they want to go deeper. The ONLY pause
points are Step Q (wait for thinker's answers) and Step R (wait for
thinker's reaction to findings). Deliver all findings together.

DEPTH = "QUICK CHECK": Execute Layers 1->2 only. Deliver and move
to Step R.
</HARD-GATE>

---
```

- [ ] **Step 3: Verify the edit is clean**

Read the modified section and confirm:
- No remnant of "Progressive Disclosure (default)" subsection
- No consent gate language ("Want me to look at it?")
- Hard gate is present with both depth modes

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "feat: replace progressive disclosure with auto-progression hard gate"
```

---

### Task 7: Replace Stage C section with orchestrator dispatch

**Files:**
- Modify: `SKILL.md`

- [ ] **Step 1: Locate Stage C section**

In `SKILL.md`, find `### Stage C: Stochastic Perturbation` (line ~497) through the `---` separator before `## Step R:` (line ~606).

- [ ] **Step 2: Replace the entire Stage C section**

Replace SKILL.md from `### Stage C: Stochastic Perturbation` through the `---` before `## Step R:` with:

```markdown
### Stage C: Stochastic Perturbation

**"What survives displacement into alien conceptual territory?"**

Stage C is executed programmatically via `perturb.py --orchestrate`.
Do NOT simulate, approximate, or linguistically generate Stage C output.
Follow the steps below exactly.

<HARD-GATE>
You have NOT completed Stage C until you have:
1. Called the Bash tool to run perturb.py --orchestrate
2. Called the Agent tool to spawn seed agents from the manifest
3. Called the Agent tool to spawn the watcher from the manifest
If you are about to write Stage C findings without having made
ALL THREE types of tool calls, STOP. You are generating fake output.
</HARD-GATE>

#### Step 1: Prepare inputs

Before calling Bash, prepare three inputs from your L1-2 and
Stage A-B work:

1. **CONCERN SUMMARY**: 2-3 sentences describing the thinker's
   situation in natural language.
2. **PREDICATES**: Formalize the thinker's concern + your findings
   as first-order predicates. Example:
     Plans(thinker, X)
     Assumes(plan, Y)
     Absent(plan, Z)
     ExcludesFrame(plan, W)
     LatentThought(thinker, "...")
3. **STAGE B SYNTHESIS**: Your Stage B output (pattern in the
   negative space, latent thought, reframing question).

#### Step 2: Run the orchestrator

Call the Bash tool:

    python3 ${CLAUDE_SKILL_DIR}/perturb.py --orchestrate \
      --artifact "the thinker's artifact text" \
      --concern-summary "your concern summary" \
      --predicates "your predicate formalization" \
      --stage-b-synthesis "your Stage B output"

If `transformers` or `sentencepiece` are not installed, first run:
`pip install sentencepiece transformers`

If the Bash call fails, report the error to the thinker and deliver
Stages A-B findings without Stage C. Do NOT generate fake Stage C
output as a fallback.

#### Step 3: Dispatch seed agents

Read the manifest JSON from the Bash output. Look at
`steps[0].agents` — call the Agent tool once per seed agent.
**Send ALL Agent tool calls in a SINGLE message for parallel
dispatch.** Use each agent's `"prompt"` field as-is — do not
modify it.

#### Step 4: Collect results and dispatch watcher

After all seed agents return, extract from each response ONLY:
- `bridge_predicates`
- `reflection`
- `signal` (self-assessed score)

Do NOT pass stories or story_predicates to the watcher. This
enforces the algorithm's information isolation invariant.

Format the extracted results as:

    === Seed 1 ===
    Bridge predicates: <extracted>
    Reflection: <extracted>
    Self-assessed signal: <extracted>

    === Seed 2 ===
    ...

Read `steps[1].prompt` from the manifest. Replace the placeholder
`{{SEED_AGENT_RESULTS}}` with the formatted results above. Call
the Agent tool with the completed watcher prompt.

#### Step 5: Evaluate and iterate

Read the watcher's scores:
- **Any S >= 0.5**: Include those findings in your delivery.
  Integrate with Stages A-B. Explain how stochastic findings
  extend or confirm the deterministic pass.
- **All S < 0.5**: Run `iteration.next_round_command` from the
  manifest. Repeat Steps 3-5 with new results.
- **After 3 rounds with no signal**: Report null result:
  "Stochastic perturbation confirmed the deterministic synthesis."
  This is a valid outcome that increases confidence in Stage B.
  (Note: the algorithm spec suggests asking the thinker if they
  want more rounds. This is intentionally simplified per the
  auto-progression design — no consent gates during execution.)

If seed agents fail or return malformed output, proceed with the
agents that did return. If zero agents returned usable output,
treat as a null-signal round and iterate.

For algorithm details, see `stochastic-perturbation-algorithm.txt`.

---
```

- [ ] **Step 3: Verify the edit is clean**

Read the modified section and confirm:
- Hard gate is present
- Five numbered steps with exact tool call instructions
- Parallel dispatch instruction is explicit
- `{{SEED_AGENT_RESULTS}}` placeholder substitution is specified
- Error handling is included
- No remnant of old Phase 1/Phase 2 structure

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "feat: replace Stage C narrative with orchestrator dispatch block"
```

---

## Chunk 4: Integration Verification

### Task 8: Update docstring and verify backward compatibility

**Files:**
- Modify: `perturb.py`

- [ ] **Step 1: Update the module docstring in `perturb.py`**

Replace the existing docstring (lines 2-19) with:

```python
"""
Stochastic Perturbation — Seed Generator & Orchestrator (Stage C)

Computational seed generation and execution manifest builder for the
via-negativa stochastic perturbation protocol. Handles the math (entropy
extraction, SHA-256 hashing, NLLB-200 multilingual token sampling) and
the orchestration (complete agent prompts, scoring formulas, iteration).
No API key required.

Usage:
  # Seed generation only (original mode)
  python perturb.py --artifact "text..."
  python perturb.py --artifact-file path/to/artifact.txt

  # Full orchestrator manifest
  python perturb.py --orchestrate \\
    --artifact "text..." \\
    --concern-summary "thinker's concern" \\
    --predicates "Plans(thinker, X)" \\
    --stage-b-synthesis "pattern in negative space"

  # Iteration (uses persisted /tmp files from first call)
  python perturb.py --orchestrate --artifact-file /tmp/vn-artifact.txt \\
    --predicates-file /tmp/vn-predicates.txt \\
    --concern-file /tmp/vn-concern.txt \\
    --stage-b-file /tmp/vn-stageb.txt --round 2

Requires:
  pip install sentencepiece transformers
"""
```

- [ ] **Step 2: Run the full test suite**

Run: `cd /Users/nicholaspark/Documents/via-negativa-free-form-stress && python -m pytest tests/ -v`
Expected: All tests PASS (tests requiring transformers skip if not installed)

- [ ] **Step 3: Run `--seeds-only` regression check**

Run: `cd /Users/nicholaspark/Documents/via-negativa-free-form-stress && python3 perturb.py --artifact "regression test" --seeds 2 --tokens 3`
Expected: JSON output with 2 seeds, 3 tokens each — same format as before this work

- [ ] **Step 4: Commit**

```bash
git add perturb.py
git commit -m "docs: update perturb.py docstring for orchestrator mode"
```

---

### Task 9: End-to-end orchestrate test (manual, requires transformers)

**Files:** None — this is a manual verification step.

- [ ] **Step 1: Run the full orchestrate pipeline**

```bash
cd /Users/nicholaspark/Documents/via-negativa-free-form-stress
python3 perturb.py --orchestrate \
  --artifact "I am planning to leave my engineering role at a large company and start an independent consulting practice. I have 3 months of savings, 15 contacts who said they would hire me, and a plan to market through LinkedIn and conferences." \
  --concern-summary "Thinker is planning to leave stable engineering employment to start a consulting business with 3 months runway." \
  --predicates "Plans(thinker, career_transition)
Assumes(plan, network_converts_to_clients)
Assumes(plan, skills_transfer_directly)
Absent(plan, failure_criteria)
Absent(plan, identity_of_operator)
ExcludesFrame(plan, identity_cost)
LatentThought(thinker, 'will_I_thrive_as_businessperson')" \
  --stage-b-synthesis "Pattern: plan is detailed about WHAT (services, pricing, timeline) and silent about WHO (the thinker as businessperson). The latent thought: Am I the kind of person who will thrive doing this? The reframing question: What would a version of this plan look like that I would enjoy on the worst day?"
```

Expected: Valid JSON manifest with:
- `protocol: "via-negativa-stochastic-perturbation"`
- `version: 1`
- `round: 1`
- 3 seed agents with complete prompts containing bridge type definitions
- 1 watcher with scoring formula and `{{SEED_AGENT_RESULTS}}` placeholder
- Iteration block with `--round 2` command

- [ ] **Step 2: Verify manifest structure is correct**

Check manually:
- Each seed agent prompt contains different NLLB-200 tokens
- Each seed agent prompt contains the career transition predicates
- Watcher prompt contains the Stage B synthesis text
- Watcher prompt contains all four scoring criteria definitions
- `next_round_command` references `/tmp/vn-*.txt` files

- [ ] **Step 3: Verify iteration files were persisted**

```bash
cat /tmp/vn-artifact.txt | head -1
cat /tmp/vn-predicates.txt | head -1
cat /tmp/vn-concern.txt
cat /tmp/vn-stageb.txt | head -1
```

Expected: Each file contains the corresponding input from Step 1.

- [ ] **Step 4: Final commit with any fixes**

If any issues found, fix and commit. Otherwise, no commit needed.
