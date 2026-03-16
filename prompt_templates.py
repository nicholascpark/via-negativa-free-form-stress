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
