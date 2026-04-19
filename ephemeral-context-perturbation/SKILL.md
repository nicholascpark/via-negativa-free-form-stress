---
name: ephemeral-context-perturbation
description: >
  Defeats conversation-level context anchoring by forking to a throwaway branch,
  applying aggressive directed /compact to reconstruct context under an explicit
  discard rule, generating a de-anchored answer, and returning only the finding
  to the main thread — history preserved, anchor bypassed. Use when the
  conversation is long and accumulated, when the assistant seems stuck in prior
  framing, when new evidence conflicts with earlier direction, when the user
  expresses doubt ("wait", "are we sure", "rethink this", "start fresh"), when
  reasoning loops, or when the current working answer cannot be re-derived from
  visible evidence alone. Sibling skill to via-negativa-free-form-stress: that
  one perturbs concepts at the thought layer, this one perturbs context at the
  conversation layer. Same generator, different layer. Trigger on any request
  to escape accumulated framing, verify which conclusions are evidence-backed
  vs inertia-backed, or run a clean-room pass without losing the working thread.
---

# Ephemeral Context Perturbation

## What This Skill Is

A protocol for defeating context anchoring at the infrastructure layer rather
than the prompt layer. Adding more text to a contaminated conversation is still
text sitting on top of the anchor. This skill intervenes one level below: it
reconstructs what enters the next turn.

**The move:**

1. Fork the conversation to a throwaway branch (history preserved in main)
2. Apply an aggressive, directed `/compact` in the fork — surgical, not
   summarizing
3. Regenerate the answer in the reconstructed context
4. Return **only the finding** to main as a self-contained artifact
5. Discard the fork

The fork is an **instrument**, not a destination. Nothing lives there
permanently. The main thread is the judge of what returns.

## Core Principle

Prompt-level interventions ("rethink from scratch", "challenge your
assumptions") are themselves anchored — they're more tokens produced inside
the same contaminated window. The model telling itself to de-bias is still the
biased model.

Context-level interventions operate on what the model sees, not on what the
model adds. Directed `/compact` rewrites the input rather than appending to it.
Combined with an ephemeral fork, failure is costless: a bad compact just gets
thrown away.

**The asymmetry that makes this work:** in a persistent branch, `/compact` has
to be cautious — wrong discards are permanent. In an ephemeral fork, `/compact`
can be violent. Strip everything. Adopt an adversarial frame. Invert the goal.
The worst case is you learn nothing and return to main unchanged.

## Relationship to Via Negativa

This skill is a sibling to `via-negativa-free-form-stress`. Same generator,
different layer:

- **via-negativa**: perturbs *concepts* to escape local associative neighborhoods
- **ephemeral-context-perturbation**: perturbs *context* to escape accumulated
  conversation frames

Via negativa's Stage C (stochastic perturbation) displaces ideas into alien
conceptual territory to see what survives. This skill does the structurally
identical move one layer below: it displaces the conversation's accumulated
context to see which conclusions survive.

**They chain:**

- Via negativa identifies the frame the thinker is using
- Ephemeral-context-perturbation tests whether that frame was derived from
  evidence or from conversational accumulation

A frame surfaced by via-negativa becomes the target directive for a compact
in this skill: "reconstruct this conversation without the [planning / deficit /
optimization] frame."

## When to Invoke

Detect anchoring before acting. Signals:

- **Length pressure**: conversation exceeds ~20 turns and recent answers
  reference early framing that may no longer be load-bearing
- **Doubt signal**: user says "wait", "are we sure", "I think we're off",
  "rethink", "start fresh", "go back"
- **Evidence-conclusion gap**: the current working answer cannot be
  re-derived from visible tool outputs and files alone
- **Loop**: the same considerations keep surfacing; progress stalls
- **Drift**: current work has diverged from the originally stated goal and
  nobody named the transition
- **Frame lock**: via-negativa flagged a frame and you want to test its source

**Do not invoke when:**
- Conversation is short and recent (nothing to anchor yet)
- Current answer is clearly evidence-backed and user is making progress
- The user is in flow and the question is tactical, not strategic

The worst failure mode is invoking this on clear, moving work. Disruption has
a cost even when fork is free.

## Two Modes

### Single Ephemeral Fork (default)

One fork, one compact directive, one returned finding. Use when anchoring is
suspected but cheap verification is enough.

### Parallel Adversarial Forks (stress mode)

Multiple forks in parallel, each with a different compact directive. Findings
that appear in all branches are probably evidence-backed. Findings that only
appear in the original thread are probably anchored. Findings that only appear
under one specific directive are diagnostic of what that directive stripped.

Use when:
- Stakes are high (design decision, architectural commitment)
- Multiple reasonable directions exist and the choice feels arbitrary
- The user explicitly asks for adversarial coverage

## The Mechanism

### Step 1: Detect Anchoring

Before forking, state explicitly: **what is the suspected anchor?**

Not "the context is long" — that's not specific. Name the candidate:
- "The early assumption that this is a migration, not a rewrite, is shaping
  every current answer"
- "The user's first hypothesis about the bug was accepted and never revisited
  even though two tool outputs since then are inconsistent with it"
- "The framing 'we need to ship fast' has been load-bearing on every
  architectural choice for 15 turns"

If you can't name the candidate anchor in one sentence, the problem is
diffuse and this skill won't help. Try via-negativa first to surface the frame.

### Step 2: Select Fork Point

The fork point controls what the compact has to work with. Options:

- **Pre-interpretation**: fork from right after the user's original task
  statement, before the first assistant interpretation. Preserves the ask,
  drops all accumulated framing.
- **Post-evidence**: fork from right after key tool outputs or files were
  gathered. Preserves evidence, drops what was built on it.
- **Last-decision**: fork from the most recent explicit user decision.
  Preserves decisions, drops subsequent speculation.

Default: pre-interpretation. It's the most aggressive and the findings are
cleanest.

### Step 3: Choose Compact Directive(s)

The directive is the surgical plan. Pick one (single mode) or several
(parallel mode). Each template below is meant to be instantiated with the
specific task.

**Evidence-only**
> Reconstruct this conversation preserving only: (a) the user's original task
> statement verbatim, (b) verified file contents and tool outputs, (c) explicit
> user decisions. Discard: all assistant interpretation, early hypotheses,
> working theories, transitional reasoning, and any framing the assistant
> introduced that the user did not confirm.

**Minimal brief**
> Reconstruct as if a new assistant is joining this conversation right now.
> Include only: the user's current ask in one paragraph; the list of files
> that have been read (paths only); any artifacts the user has directly
> created or approved. Discard everything else.

**Adversarial reframe**
> Reconstruct this conversation as if the user's goal were [INVERSE_GOAL]
> instead of the apparent current goal. Preserve only what would be relevant
> under that reframed goal. Surface any evidence that actually supports the
> reframed goal even though it was dismissed or not noticed under the current
> frame.

**Latest-first**
> Reconstruct with inverse chronological weighting. The most recent 3 turns
> are source of truth. Earlier turns are summarized in one line each, and
> only if they contain information still referenced by the recent turns.
> Early interpretive framing is explicitly discarded.

**Cold-start**
> Reconstruct as a fresh arrival with zero assumptions about what the user is
> trying to do. Only explicit statements from the user about goals, constraints,
> or preferences survive. Inferred goals, assumed constraints, and carried-over
> framing are stripped.

**Frame-excision (chains with via-negativa)**
> Via-negativa surfaced that the current thinking is in a [FRAME] frame.
> Reconstruct this conversation with all [FRAME]-shaped interpretation removed.
> Evidence that doesn't fit the [FRAME] frame but was noticed-and-dismissed
> should be surfaced instead of discarded.

Aggression is a feature. If a directive seems too extreme, that's usually the
right directive — the fork is throwaway.

### Step 4: Generate in the Ephemeral Branch

In the fork, after `/compact`, regenerate the answer to the user's current
question. Do not port over reasoning from main. Let the reconstructed context
produce its own answer.

If the reconstructed answer matches main: the anchor wasn't load-bearing on
this question. Valuable null result.

If the reconstructed answer differs: proceed to Return Gate.

**Agent-level fallback:** if chat-level fork+compact is not available in the
environment, simulate via the Task tool. Spawn a subagent with the compact
directive's output as its entire context — no parent thread inheritance. This
is weaker (same model, same session) but approximates the effect.

### Step 5: Return Gate

Not everything generated in the fork deserves to return. Apply this gate
(adapted from via-negativa's Relevance Gate):

**A finding passes the Return Gate only if ALL FOUR are true:**

1. **Self-contained**: the finding makes sense in the main thread without
   needing the compacted context to be ported back. State it as a standalone
   observation, not as "given the compact we did…"

2. **Differential**: the finding explicitly names where it diverges from the
   current main-thread direction. "Main thread was assuming X, reconstructed
   pass produced Y, here is the specific divergence point."

3. **Diagnostic**: the finding classifies its own likely cause. Either
   (a) this divergence is plausibly due to deanchoring — main was held by
   accumulated framing the compact stripped, or (b) this divergence is
   plausibly due to context loss — the compact discarded something the
   reconstructed pass needed but didn't have.

4. **Discardable**: the finding is presented as a proposal, not an
   imposition. The main thread can reject it without damage.

Findings that fail the gate are dropped. The fork is thrown away. You return
to main with nothing — and that's a valid, non-damaging outcome.

### Step 6: Adjudication in the Main Thread

Returned findings arrive in main as a labeled artifact. Format:

```
### De-anchored pass result

**Compact directive used:** [which template]
**Fork point:** [where it branched from]

**Reconstructed conclusion:** [the answer generated in the fork]

**Divergence from current direction:** [specific point where main and fork
disagree]

**Self-estimate:** [deanchoring / context-loss / mixed] because [reason]
```

The main thread decides:
- **Accept**: the reconstructed conclusion replaces the current working
  direction
- **Partial merge**: specific elements of the reconstruction are integrated;
  main direction adjusts
- **Reject**: main direction stands; returned finding is logged as
  "considered and dismissed" so it doesn't keep resurfacing

**Rejection is free** and must be available. If the skill becomes a pressure
to accept its own findings, it's weaponizing itself. The whole design rests
on the fork being costless to throw away — including its outputs.

## Composition with Via Negativa

Typical chain:

1. User has accumulated a long conversation about a plan
2. Via-negativa Stage A surfaces the frame ("you're in a planning frame when
   this might be an exploration problem")
3. User asks: is that frame coming from my actual situation, or from how this
   conversation accumulated?
4. Ephemeral-context-perturbation runs a `frame-excision` compact removing
   planning-shaped interpretation
5. The fork answers the question again; returned finding shows which parts
   of the current plan survive frame removal
6. Main thread adjudicates

The two skills are composable because they share a generator ("aggressive
displacement to reveal what's load-bearing") at different layers. Via-negativa
tells you *what* to perturb; ephemeral-context-perturbation tells you *how*
to test whether perturbing it actually matters.

## Usage Notes

### Aggression as feature

The fork is throwaway. The compact can be as extreme as you can justify. A
half-hearted compact is worse than none — it leaves partial anchoring and
adds confusion. Commit to the directive or don't fork.

### When context loss is the real finding

Sometimes the reconstructed answer is worse because the compact stripped
something that mattered. That's information too. It tells you which pieces
of accumulated context were actually load-bearing — and therefore *not*
anchors. The stuff that breaks the reconstruction is evidence, not inertia.

### Don't recursively re-fork

If the returned finding itself feels anchored, do not fork from the fork. One
ephemeral layer only. Recursion here is the same anti-pattern as recursive
metacognition in via-negativa's Step R — it spirals without adding signal.

### Name the anchor before forking

If you can't state the suspected anchor in one sentence before Step 2, you're
guessing. Forking on a guess still works sometimes, but the directive will be
generic and the finding will be noise. Get the anchor candidate specific
first.

### Parallel forks need cross-validation, not voting

In parallel mode, don't average. Look for:
- Conclusions that survive across multiple aggressive compacts → probably
  evidence-backed
- Conclusions that only appear in main → probably anchored
- Conclusions that appear under exactly one directive → diagnostic of what
  that directive stripped (that stripped thing was load-bearing)

This is pattern-reading, not majority rule.

### What this skill cannot do

- It cannot compact context the current model can't see. Tool outputs already
  dropped from the window are gone either way.
- It cannot make the compactor neutral — same model, same biases, just
  operating under an explicit discard rule that pushes against the bias.
- It cannot replace domain judgment. A reconstruction that "disagrees" with
  main is not automatically right.
- It cannot fix a diffuse anchor. If the accumulated framing can't be
  localized to a specific suspected anchor, this skill's findings will be
  weak.

### Scaling

- **Single ephemeral fork**: default. Fast, cheap, one directive.
- **Parallel adversarial forks**: for high-stakes divergences or when user
  explicitly asks for robust coverage. Cost is N subagent spawns or N user
  fork operations.

## Quick Reference

For composition patterns, see sibling skill `via-negativa-free-form-stress`
— specifically Stage A (frame identification) and Stage C (stochastic
perturbation as the thought-layer analog of this skill's context-layer move).
