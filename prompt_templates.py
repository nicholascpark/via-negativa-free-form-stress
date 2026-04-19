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
    artifact_anchors: list[str] | None = None,
    perturbation_profile: dict | None = None,
) -> str:
    """Build a complete seed agent prompt with tokens, concern, and predicates embedded."""
    anchors = artifact_anchors or []
    profile = perturbation_profile or {}
    round_strategy = profile.get("round_strategy", "unknown")
    round_description = profile.get("round_description", "No round description provided.")
    dominant_scripts = profile.get("artifact_dominant_scripts", [])
    sampled_scripts = profile.get("sampled_scripts", [])
    selection_strategy = profile.get("selection_strategy", "unknown")
    displacement_mode = profile.get("displacement_mode", "unknown")
    displacement_note = profile.get("displacement_note", "No displacement note provided.")

    return f"""You are a stochastic perturbation seed agent. Complete all three tasks below.
Your final answer must be ONLY valid JSON. Do not wrap it in prose.

**Your random tokens** (sampled computationally from NLLB-200 multilingual tokenizer):
{json.dumps(tokens, ensure_ascii=False)}

**Thinker's concern summary:**
{concern_summary}

**Artifact anchor terms** (high-salience words from the original artifact):
{json.dumps(anchors, ensure_ascii=False)}

**Perturbation profile**:
- Round strategy: {round_strategy}
- Strategy intent: {round_description}
- Dominant artifact scripts: {json.dumps(dominant_scripts, ensure_ascii=False)}
- Sampled token scripts: {json.dumps(sampled_scripts, ensure_ascii=False)}
- Displacement mode: {displacement_mode}
- Displacement note: {displacement_note}
- Selection strategy: {selection_strategy}

---

**Task 1 — Random Walk Story (100-200 words)**

Write a coherent paragraph that incorporates ALL of the random tokens above.
The tokens may appear as character names, place names, sounds, concepts, or
morphological components of words. Generate past initial incoherence into a
local semantic basin — a coherent story that exists in an alien region of
concept space because its starting conditions were genuinely random.

The paragraph is SCAFFOLDING — its value is in the semantic territory it
occupies, not in its content.
Treat the random tokens as detours away from the anchor terms, not as hidden
answers. Your job is to leave the artifact's default phrasing, then return
with a structurally defensible bridge.

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

2c. Name the single strongest bridge type you found:
    structural_isomorphism | negation_revelation | compositional_insight | none

2d. State one counterevidence clause:
    What observation would make your bridge invalid, over-forced, or redundant
    with Stage B?

---

**Task 3 — Reflection (150-200 words)**

Using the bridge as backbone, reflect on what the story reveals about the
thinker's negative space. Reference specific predicates from both sides.
Ground the reflection in at least one artifact anchor term if possible.

---

**Output schema**:
Return ONLY valid JSON matching this shape:
{{
  "story": "your generated paragraph",
  "story_predicates": ["Predicate(...)", "Predicate(...)"],
  "bridge_type": "structural_isomorphism" | "negation_revelation" | "compositional_insight" | "none",
  "bridge_predicates": ["Predicate(...)", "Predicate(...)"],
  "counterevidence": "one falsification or redundancy condition",
  "reflection": "natural language, predicate-grounded",
  "signal": 0-5
}}

Schema rules:
- If bridge_type is "none", set bridge_predicates to [] and signal to 0 or 1.
- If bridge_type is not "none", bridge_predicates must not be empty.
- story_predicates and bridge_predicates must be JSON arrays, not a single string.
- counterevidence must name a real condition that would weaken, falsify, or trivialize the bridge."""


def render_watcher_prompt(stage_b_synthesis: str) -> str:
    """Build the watcher agent prompt with scoring formula and Stage B context."""
    return f"""You are a stochastic perturbation watcher agent. You evaluate seed agent
reflections for signal quality. You have NO access to the random walk stories —
you evaluate logical structure only.

**Stage B's deterministic synthesis** (for Novelty evaluation):
{stage_b_synthesis}

---

**Seed agent results to evaluate** (JSON array of watcher-safe records):

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
  1 = valid structural isomorphism, negation, or composition with specific
  predicates and a real counterevidence clause.

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
predicates that are too abstract. Also override downward if the
counterevidence is vacuous or would never actually falsify the bridge.

**Output format:**
For each seed object in the JSON array:
- Bridge type + one-sentence sanity check
- Specificity score + justification (1 sentence)
- Novelty score + justification (1 sentence)
- FormalValidity score + justification (1 sentence)
- Actionability score + justification (1 sentence)
- Counterevidence quality check (1 sentence)
- Composite S score
- Signal classification (noise / faint echo / actionable / significant)

Then provide a **meta-assessment**: Did any seed reach territory that Stage B's
deterministic synthesis could NOT have reached? This is the key question —
stochastic perturbation is only valuable when it extends the deterministic
pass, not when it restates it in different imagery."""
