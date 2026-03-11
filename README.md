# Via Negativa Free-Form Stress

## Introduction

"Whereof one cannot speak, thereof one must be silent." — Ludwig Wittgenstein.

Language has strict limits. When we push LLMs to explore topics beyond factual, logical description, standard generation falls short.

This project operates on three foundational facts:

- As idea-to-action time decreases, our cognitive debt will inevitably increase.
- Next-token-prediction accuracy will continue to approach perfection.
- Surfacing all thoughts and details into structured architectural plans is the definitive path forward.

Because next-token prediction inherently limits out-of-the-box reasoning, LLM nodes require a different kind of activation. This repository introduces a method for perturbing and activating trained models to produce intentional noise—introducing creative thinking "via-negativa."

## What is this?

A metacognitive skill that applies via-negativa perception to **thinking itself** — plans, reasoning, decisions, notes, drafts, and ideas. Surfaces what's absent, assumed, and structurally excluded not just from the artifact but from the cognition that produced it.

Most feedback asks *"is what you wrote correct?"*
Most planning advice asks *"what's the next step?"*
This asks *"what are you NOT thinking, and does that absence matter?"*

## Two Modes

**Reflective** (stress test thinking): The thinking isn't broken yet. What's absent from this reasoning that will become the failure point? What's the thought you're not having that would change everything?

**Diagnostic** (stuck / circular thinking): The thinking IS the problem. Why does this plan keep stalling? Why does this reasoning feel circular? What structural absence in the cognition itself keeps producing the same stuck point?

## Relationship to via-negativa-stress-test

This skill adapts the [via-negativa-stress-test](https://github.com/nicholaspark09/via-negativa-stress-test) methodology from analyzing external artifacts (code, PRs, bugs) to analyzing **thinking itself**. Same four-layer progressive structure, different target: instead of asking what's missing from the code, it asks what's missing from the cognition.

The progression is increasingly metacognitive:
1. What's missing from what you wrote? (content-level)
2. What's missing from how you're thinking about it? (reasoning-level)
3. What's missing from the frame you're using to think? (paradigm-level)
4. What does the shape of your not-thinking reveal? (generative-level)

## Quick Start

### As a Claude Skill

Drop `SKILL.md` and `references/` into your Claude project or skill directory. Then:

```
# Reflective mode
stress test this plan
what am I not thinking about?
challenge my reasoning here
what assumptions am I making?

# Diagnostic mode
why do I keep going in circles on this?
why does this plan never work?
what am I avoiding thinking about?
```

## The Skill

**Elicitation** (ask before telling — diagnostic questions that reveal more than the artifact) -> **Absence Inventory** (what's not being thought) -> **Load-Bearing Assumptions** (what the thinking stands on) -> **Frame Exclusions** (what the thinking paradigm renders invisible) -> **Via Negativa Design** (what the negative space reveals) -> **Response Reading** (the thinker's resistance pattern as a second artifact). Default depth includes frame analysis (Layers 1-3).

### Depth Levels
- **Quick check** → Layers 1–2 (fast but less differentiated)
- **Stress test** → Layers 1–3 (default — includes frame analysis)
- **Full via negativa** → All four layers (deterministic synthesis)
- **Deep reflection** → All four layers + stochastic perturbation protocol (Monte Carlo sampling of conceptual space to surface insights beyond the analyst's associative range)

See `SKILL.md` for full methodology.

## References

| File | Purpose |
|------|---------|
| `references/anti-patterns.md` | What bad metacognitive feedback looks like -- calibrate against these |
| `references/thinking-examples.md` | Worked examples for plans, decisions, and reasoning (reflective mode) |
| `references/diagnostic-examples.md` | Worked examples for stuck and circular thinking (diagnostic mode) |
| `references/frame-catalog.md` | Common thinking frames, their strengths, and their structural blindspots |

## License

MIT
