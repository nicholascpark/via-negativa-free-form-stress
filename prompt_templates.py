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
