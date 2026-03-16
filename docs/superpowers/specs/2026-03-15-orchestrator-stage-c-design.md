# Design: Stage C Orchestrator + Auto-Progression

**Date**: 2026-03-15
**Status**: Approved (design phase)

## Problem

The via-negativa skill's Stage C (Stochastic Perturbation) describes a multi-tool algorithm — Bash for `perturb.py`, Agent tool for seed agents and watcher — inside skill markdown. When the skill runs:

1. **Stage C never fires.** The LLM reads the instructions as context and either skips Stage C entirely or generates text that mimics the output format without ever calling tools.
2. **Auto-progression stalls.** The skill stops between layers (consent gates, or simply not advancing) instead of running Layers 1-2-3 continuously when depth is "stress test."

Root cause: markdown instructions are weak signals to an LLM. "USE THE BASH TOOL" in caps is still just text in a prompt. The gravitational pull of next-token generation is toward producing text that *describes* what the tools would produce.

## Design Principle

**Move the algorithm into code. Reduce the LLM's job to "execute this manifest."**

- **Python** owns: entropy, hashing, token sampling, prompt generation, scoring formulas, iteration logic
- **LLM** owns: predicate formalization (where its reasoning is genuinely valuable), tool dispatch (Bash + Agent calls), and final synthesis of results back to the thinker
- **Skill markdown** owns: when to trigger Stage C, hard gates that block text generation until tools have been called, and how to present results

## Approach

Approach B (Orchestrator Script) with elements of Approach A (Hardened Skill Instructions).

Extend `perturb.py` into a full orchestrator that produces not just seeds but complete, ready-to-execute agent prompts as structured JSON. The LLM's job shrinks from "interpret the algorithm spec and figure out what tool calls to make" to "pipe this output to the Agent tool." Add hard gates in SKILL.md to enforce tool usage and auto-progression.

---

## Component 1: `perturb.py --orchestrate` Mode

### New Inputs

| Flag | Purpose |
|------|---------|
| `--orchestrate` | Triggers manifest output instead of raw seeds |
| `--concern-summary` / `--concern-file` | Natural-language concern summary (2-3 sentences) |
| `--predicates` / `--predicates-file` | First-order predicate formalization of thinker's concern + L1-2/Stage A-B findings |
| `--stage-b-synthesis` / `--stage-b-file` | Stage B output (pattern, latent thought, reframing question) for watcher's Novelty criterion |

Existing flags (`--artifact`, `--seeds`, `--tokens`, `--round`, `--rounds`, `--seeds-only`) remain unchanged.

### What `--orchestrate` Does

1. Runs the existing pipeline unchanged: entropy extraction, SHA-256 hashing, NLLB-200 token sampling
2. Builds **seed agent prompts** by combining:
   - Sampled tokens (from step 1)
   - Concern summary (from `--concern-summary`)
   - Predicates (from `--predicates`)
   - A **hardcoded prompt template** containing the full Step 2 + Step 3 instructions from the algorithm spec — including all three bridge types (structural isomorphism, negation revelation, compositional insight) with formal notation examples, the burn-in explanation, the 5-field output format, and the "signal: 0 if no bridge" instruction
3. Builds the **watcher prompt** by combining:
   - A slot marker for seed agent results (the LLM fills this after collecting responses)
   - The Stage B synthesis (from `--stage-b-synthesis`) for Novelty evaluation
   - The **hardcoded scoring formula** with all four criteria definitions (Specificity, Novelty, FormalValidity, Actionability), weights (0.3, 0.3, 0.2, 0.2), thresholds (<0.3 noise, 0.3-0.5 faint echo, 0.5-0.7 actionable, >=0.7 significant), anti-pattern detection rules, and meta-assessment question — verbatim from the algorithm spec
4. Builds the **iteration block** with the exact next-round command pre-computed
5. Outputs the full manifest as JSON

### Manifest Output Format

```json
{
  "protocol": "via-negativa-stochastic-perturbation",
  "version": 1,
  "round": 1,
  "steps": [
    {
      "step": "seed_agents",
      "dispatch": "parallel",
      "agents": [
        {
          "id": "seed_1",
          "prompt": "<complete seed agent prompt with tokens, concern summary, predicates, full Step 2-3 spec, bridge types, output format>"
        },
        {
          "id": "seed_2",
          "prompt": "..."
        },
        {
          "id": "seed_3",
          "prompt": "..."
        }
      ]
    },
    {
      "step": "watcher",
      "dispatch": "after_seed_agents",
      "input_from": "seed_agents",
      "input_fields": ["bridge_predicates", "reflection", "signal"],
      "stage_b_synthesis": "<Stage B output for Novelty evaluation>",
      "prompt": "<complete watcher prompt with scoring formula, thresholds, anti-pattern detection, meta-assessment question>"
    }
  ],
  "iteration": {
    "signal_threshold": 0.5,
    "max_rounds": 3,
    "next_round_command": "python3 ${CLAUDE_SKILL_DIR}/perturb.py --orchestrate --artifact-file /tmp/vn-artifact.txt --predicates-file /tmp/vn-predicates.txt --concern-file /tmp/vn-concern.txt --stage-b-file /tmp/vn-stageb.txt --round 2"
  }
}
```

### What's Hardcoded vs. Parameterized

| Hardcoded in Python (source of truth) | Parameterized (LLM provides) |
|---|---|
| Seed agent prompt template (Steps 2-3 spec) | Sampled tokens (computed) |
| Three bridge types with formal examples | Thinker's concern summary |
| Watcher scoring formula + weights + thresholds | Predicate formalization |
| Anti-pattern detection rules | Stage B synthesis |
| Output format requirements | Round number |
| Iteration logic + max rounds | N seeds, K tokens per seed |

### Watcher Prompt Slot Mechanics

The watcher prompt is pre-generated at manifest time, before seed agents have run. It contains a literal placeholder string `{{SEED_AGENT_RESULTS}}` that the LLM replaces after collecting seed agent responses.

**Extraction rule**: The SKILL.md replacement text instructs the LLM to extract ONLY `bridge_predicates` and `reflection` from each seed agent's response. The stories, story_predicates, and self-assessed signal fields are deliberately excluded — this enforces the algorithm's watcher information isolation invariant (the watcher cannot see narratives).

**Substitution format**: The LLM replaces `{{SEED_AGENT_RESULTS}}` with a structured block:
```
=== Seed 1 ===
Bridge predicates: <extracted from seed agent 1>
Reflection: <extracted from seed agent 1>
Self-assessed signal: <extracted from seed agent 1>

=== Seed 2 ===
...
```

Note: self-assessed signal IS included (the watcher needs it for Forced Connection detection per Step 4.3), but stories and story_predicates are NOT.

### Input Handling: Inline vs. File Flags

Both inline (`--concern-summary`, `--predicates`, `--stage-b-synthesis`) and file (`--concern-file`, `--predicates-file`, `--stage-b-file`) variants are supported. The preference:

- **First call**: Use inline flags. The LLM passes values directly on the command line. This avoids the overhead of writing temp files.
- **Iteration rounds**: Use file flags. On the first call, `perturb.py --orchestrate` writes the received inputs to `/tmp/vn-*.txt` automatically, so that the `next_round_command` can reference them without the LLM needing to re-pass them. The script handles this internally — the LLM just runs the next-round command as-is.

This means the LLM never needs to write temp files manually. The script manages file persistence across rounds.

### Error Handling

- **`perturb.py` fails** (missing dependencies, malformed input): The Bash tool returns stderr output. The SKILL.md replacement text instructs the LLM: "If the Bash call fails, report the error to the thinker and deliver Stages A-B findings without Stage C. Do NOT generate fake Stage C output as a fallback."
- **Seed agent fails or returns malformed output**: The LLM proceeds with the agents that did return. The watcher evaluates whatever results are available. If zero agents returned usable output, treat as a null-signal round and iterate.
- **Watcher agent fails**: The LLM reports Stage C as inconclusive and delivers Stages A-B findings. Stage C non-completion is a valid outcome — the skill already defines null results as increasing confidence in Stage B.
- **Malformed manifest JSON**: Same as script failure — report and fall back to Stages A-B.

### Manifest Versioning

The manifest includes a `"version": 1` field. If the manifest format changes in future iterations, the SKILL.md dispatch instructions can reference a specific version to detect incompatibility.

### No Breaking Changes

The existing `--seeds-only` mode remains the default. `--orchestrate` is a new mode. All existing behavior is preserved.

### No New Dependencies

`--orchestrate` mode uses only the same dependencies as today: `sentencepiece`, `transformers`. No API keys. The script generates prompt text and JSON — it does not make any network calls beyond the initial tokenizer download.

---

## Component 2: Auto-Progression in SKILL.md

### Problem

The current progressive disclosure design has consent gates between layers:
- After Layer 2: *"There's a framing pattern underneath. Want me to look at it?"*
- After Layer 3 Stage B: no explicit gate, but the LLM treats Stage C as optional

When depth is "stress test" (the default), these gates cause the skill to stall or stop early.

### SKILL.md Sections Affected

The following existing sections in SKILL.md must be **rewritten or removed** to resolve contradictions with the new hard gate:

1. **"Depth levels" paragraph (lines ~93-107)**: Rewrite to define only two depths ("stress test" and "quick check") without mentioning progressive disclosure as an interactive default.
2. **"Progressive Disclosure (default)" subsection (lines ~109-119)**: **Remove entirely.** This subsection defines consent gates after Layer 2 and conditional Layer 3 entry, which directly contradicts the auto-progression hard gate. The new hard gate replaces it.

The current text says: *"Don't pre-select depth. Start at Layer 1 and let each layer's output determine whether to go deeper."* This is replaced by: *"Stress test runs all layers. Quick check runs Layers 1-2. No runtime depth decisions."*

### Solution

Two modes of progression, enforced with hard gates:

**Stress test (default):** Layers 1-2-3 (all stages A, B, C) run as a single continuous execution. No consent gates between layers. Deliver all findings together at the end, then enter Step R.

**Quick check:** Layers 1-2 only. Deliver and move to Step R.

Only two pause points in the entire flow:
- Step Q (Elicitation) — must wait for thinker's answers
- Step R (Response Reading) — must wait for thinker's reaction

### Hard Gate (top of "How It Works" section)

```
<HARD-GATE>
DEPTH = "STRESS TEST" (DEFAULT): Execute Layers 1->2->3 (all stages
A, B, C) as a single continuous pass. Do NOT pause between layers.
Do NOT ask the thinker if they want to go deeper. The ONLY pause
points are Step Q (wait for thinker's answers) and Step R (wait for
thinker's reaction to findings). Deliver all findings together.

DEPTH = "QUICK CHECK": Execute Layers 1->2 only. Deliver and move
to Step R.

The thinker can request either depth explicitly. If no depth is
specified, use STRESS TEST.
</HARD-GATE>
```

### Resulting Flow (Stress Test)

```
Step 0 (Intake)
  -> Step Q (Elicitation — WAIT for answers)
  -> Layer 1 (Absence Inventory)
  -> Layer 2 (Load-Bearing Assumptions)
  -> Layer 3 Stage A (Frame Exclusions)
  -> Layer 3 Stage B (Generative Synthesis)
  -> Formalize predicates + concern summary
  -> Bash: perturb.py --orchestrate
  -> Agent x N: seed agents (parallel dispatch)
  -> Agent: watcher
  -> Evaluate scores -> iterate or deliver
  -> Step R (Response Reading — WAIT for reaction)
```

---

## Component 3: Stage C Section Replacement in SKILL.md

### What Gets Removed

The current Stage C section (~100 lines) that narratively explains the algorithm with inline instructions for Bash and Agent tool usage. This includes:
- Phase 1/Phase 2 descriptions
- Seed agent prompt templates embedded in markdown
- Watcher prompt embedded in markdown
- Self-checks
- Iteration logic described in prose

### What Replaces It

A short orchestrator dispatch block (~40 lines) that tells the LLM:
1. What inputs to prepare (concern summary, predicates, Stage B synthesis)
2. The exact Bash command to run
3. How to read the manifest and dispatch Agent calls — **with an explicit instruction to send ALL seed agent Agent tool calls in a SINGLE message for parallel dispatch** (this is the exact kind of "weak signal" problem this spec solves; the instruction must be unambiguous)
4. How to extract only `bridge_predicates`, `reflection`, and `signal` from seed agent responses (excluding stories and story_predicates) and substitute them into the watcher prompt at the `{{SEED_AGENT_RESULTS}}` placeholder
5. How to handle iteration based on watcher scores

Plus a hard gate:

```
<HARD-GATE>
You have NOT completed Stage C until you have:
1. Called the Bash tool to run perturb.py --orchestrate
2. Called the Agent tool to spawn seed agents from the manifest
3. Called the Agent tool to spawn the watcher from the manifest
If you are about to write Stage C findings without having made
ALL THREE types of tool calls, STOP. You are generating fake output.
</HARD-GATE>
```

### What Stays Unchanged in SKILL.md

- Steps 0, D, Q, R
- Layers 1, 2
- Layer 3 Stages A and B
- All reference files (anti-patterns.md, frame-catalog.md, thinking-examples.md, diagnostic-examples.md)
- Usage Notes, tone guidance, Relevance Gate, scaling section, limitations

---

## Coherence with Algorithm Spec

Cross-checked against every step in `stochastic-perturbation-algorithm.txt`:

| Algorithm Step | Design Coverage |
|---|---|
| Step 1: Seed generation (1.1-1.3) | Unchanged — perturb.py already implements this |
| Step 2: Random walk story generation | Seed agent prompt template includes tokens, concern summary, burn-in explanation |
| Step 3.1: Formalize thinker's concern | LLM does this before calling --orchestrate (its creative contribution) |
| Step 3.2: Formalize story | Seed agent prompt instructs this |
| Step 3.3: Identify bridges (3 types) | All three types (structural isomorphism, negation revelation, compositional insight) with formal examples hardcoded in prompt template |
| Step 3.4: Generate reflection | Seed agent prompt specifies 150-200 words, predicate-grounded |
| Seed agent output (5 fields) | Prompt template specifies: story, story_predicates, bridge_predicates, reflection, signal |
| Step 4.1: Scoring formula | Hardcoded in watcher prompt with weights and criteria definitions |
| Step 4.2: Signal thresholds | Hardcoded in watcher prompt |
| Step 4.3: Anti-pattern detection | Hardcoded in watcher prompt (Forced Connection check) |
| Step 4.4: Meta-assessment | Hardcoded in watcher prompt; Stage B synthesis passed in for Novelty evaluation |
| Step 5: Iteration | Manifest includes signal_threshold, max_rounds, next_round_command |
| Watcher cannot see stories | Manifest specifies input_fields: bridge_predicates + reflection only |
| Null result is valid | Skill markdown includes null result delivery language |

---

## Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `perturb.py` | Extended | Add `--orchestrate` mode, new input flags, prompt templates, manifest output |
| `SKILL.md` | Modified | Add hard gates, replace Stage C section with orchestrator dispatch, remove consent gates for stress test depth |
| `stochastic-perturbation-algorithm.txt` | Unchanged | Remains the algorithm reference document |
| `references/*` | Unchanged | All reference files untouched |

---

## What This Does NOT Change

- The algorithm itself — all math, scoring, thresholds, bridge types remain identical
- Layers 1-2, Stages A-B — untouched
- The skill's tone, Relevance Gate, anti-patterns guidance — untouched
- Dependencies — no new packages, no API keys
- The `--seeds-only` mode of perturb.py — backward compatible
