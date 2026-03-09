# Anti-Patterns: What Bad Via Negativa Output Looks Like

These are failure modes of the skill itself. Study them so you can recognize
when you're producing noise instead of insight. If your output resembles any
of these, stop and recalibrate.

---

## 1. The Performative Critique

**What it looks like**: Manufacturing findings for an artifact that's actually solid.

> **Bad**: "This PR lacks a distributed tracing strategy, has no chaos
> engineering plan, and doesn't address multi-region failover."
>
> (The PR adds a 20-line utility function to a single-region internal tool.)

**Why it fails**: The findings are technically "absences" but they fail the
Relevance Gate on all three criteria. They're not proximate, not consequential
for this artifact, and the creator intentionally didn't address them because
they're irrelevant.

**The fix**: If the Relevance Gate filters out most candidates, say so: "This
artifact is well-considered. I don't see significant absences." That's a valid,
valuable output. Silence is better than noise.

---

## 2. The Obvious Finding in Fancy Clothes

**What it looks like**: Restating something any competent reviewer would catch,
but wrapping it in via negativa language to make it sound deeper.

> **Bad**: "The structural absence that makes this system fragile is the lack
> of input validation on the user-facing endpoint — a missing boundary that
> exposes the system to injection attacks."
>
> (This is just "add input validation." Every code reviewer checks for this.)

**Why it fails**: It fails the non-obvious criterion. The finding is correct
but the creator almost certainly knows about it or would catch it in standard
review. Dressing it up in "structural absence" language doesn't make it an
insight.

**The fix**: If a finding is standard review territory, either skip it or be
honest: "This is a straightforward review finding, not a structural insight,
but it's worth flagging for completeness."

---

## 3. The Tautological Frame Analysis

**What it looks like**: Layer 3 "identifying" a frame that's so obvious it
provides no information.

> **Bad**: "The frame of this PR is that it's an incremental code change.
> This frame illuminates: what changed. It structurally excludes: everything
> that didn't change. An alternative frame would be to consider the entire
> system holistically."

**Why it fails**: Every PR is an incremental change. Saying so is true and
useless. The frame analysis adds nothing the creator didn't already know.

**The fix**: Layer 3 should identify a *specific* frame mismatch — where the
artifact's paradigm conflicts with its context. "This PR adds synchronous
coupling to a system migrating toward async" is a frame finding. "This PR
is incremental" is not. If you can't find a real frame mismatch, skip Layer 3
and say so.

---

## 4. The Infinite Regression

**What it looks like**: Findings that could apply to literally any artifact.

> **Bad**: "This architecture document doesn't address what happens if the
> company's strategic priorities change." / "This PR doesn't account for
> the possibility that the programming language itself becomes obsolete."

**Why it fails**: These are true of everything. They're not findings — they're
philosophical observations. They fail the consequential criterion because you
can't name a specific, plausible scenario.

**The fix**: Every finding must connect to a specific, plausible failure
scenario you can describe in one sentence. "If X happens, then Y breaks"
where X is realistic and Y is concrete.

---

## 5. The Inherited Assumption Dump

**What it looks like**: Surfacing every assumption the system makes, including
stable, well-known ones unaffected by the change.

> **Bad** (for a PR adding a new API endpoint): "This assumes a relational
> database. This assumes HTTP as the transport protocol. This assumes the
> team will continue using TypeScript. This assumes cloud hosting."

**Why it fails**: These are inherited assumptions that are stable, well-known,
and unaffected by the change. Listing them is noise. Layer 2 for embedded
artifacts should only surface inherited assumptions that are *newly fragile*
because of this change.

**The fix**: Ask "does this change make any existing assumption more fragile
than it was before?" If no, don't surface the assumption.

---

## 6. The Forced Layer 3

**What it looks like**: Generating a frame analysis when the frame is
appropriate and there's no mismatch to find.

> **Bad**: "The frame is REST. REST excludes event-driven patterns.
> Consider whether event-driven would be better."
>
> (The system is a simple CRUD app with no real-time requirements.)

**Why it fails**: Not every artifact has a frame problem. REST is the right
frame for a CRUD app. Suggesting alternatives for the sake of completing
Layer 3 is the skill at its worst — it's performing insight rather than
producing it.

**The fix**: "The framing is appropriate for the problem. No frame mismatch
detected." Say it and move on.

---

## 7. The Laundry List

**What it looks like**: 15+ findings of varying quality, presented without
prioritization.

**Why it fails**: The skill's value is in the Relevance Gate, not in
exhaustive enumeration. A list of 15 findings signals that you haven't
filtered. The creator will skim, miss the 2 findings that actually matter,
and dismiss the whole analysis.

**The fix**: 3-7 findings per layer, ruthlessly filtered. If you have more,
you haven't been honest about which ones actually pass the gate.

---

## The Meta-Pattern

All seven anti-patterns share a root cause: **prioritizing completeness over
signal.** The skill's value is not in finding everything that's absent — it's
in finding the *few things* whose absence actually matters. When in doubt,
cut the finding. A short list where every item changes the creator's thinking
is worth infinitely more than a long list that gets ignored.

---

## Agent Mode Anti-Patterns

These apply when via negativa is used inside agentic loops (pre-execution
audits, loop-break diagnostics, task-framing challenges). See the Agent
Mode section of `SKILL.md` for full definitions.

### 8. The Rubber-Stamp Audit

**What it looks like**: A pre-execution audit that always says "proceed."

**Why it fails**: An audit that never catches anything is not filtering —
it's performing safety without providing it. If the frame check always
says "fit" and blind spots are always empty, the threshold is too high
or the audit is doing reflection (validating the plan) instead of via
negativa (finding what the plan is blind to).

**The fix**: Track audit outcomes. If > 90% are "proceed" with no caveats,
the audit needs recalibration — either tighter assumption scrutiny or
genuine frame-level questioning. Alternatively, the audit may be triggering
on too many trivial decisions (see #9).

---

### 9. The Overthinking Stall

**What it looks like**: Running a pre-execution audit on trivial actions —
renaming a variable, adding a log line, fixing a typo.

**Why it fails**: Agent mode is designed for consequential decision points.
Auditing every action trains the agent (or user) to ignore audit output,
and the latency cost adds up. The skill becomes overhead instead of insight.

**The fix**: Only trigger on plan commits, architecture choices, and
debugging direction changes. The test: "If this action is wrong, does it
waste more than 5 minutes?" If no, skip the audit.

---

### 10. The Reflection Disguise

**What it looks like**: Audit output that validates or iterates on the
plan instead of surfacing what it's blind to.

> **Bad**: "Your plan to add an index is sound. The migration syntax is
> correct and the column choice is appropriate for the query pattern."

**Why it fails**: This is reflection, not via negativa. It answers "is
this good?" instead of "what is this blind to?" The plan may be correct
for the wrong problem.

**The fix**: Test every audit output: does it surface something the agent
wasn't already considering? If the output only confirms what the agent
already believes, it's reflection regardless of the formatting.

---

### 11. The Infinite Regress

**What it looks like**: Running via negativa on the via negativa output,
then auditing the audit.

**Why it fails**: Meta-analysis has diminishing returns that become
negative after one pass. The second audit will either agree with the
first (wasted compute) or disagree (now you need a third to break the
tie). This is a loop, and loops are the problem agent mode is supposed
to solve.

**The fix**: Hard limit: one audit pass. If the audit recommends a
reframe, execute the reframe and re-audit once. Maximum two passes, ever.

---

### 12. The Condescending Challenge

**What it looks like**: Task-framing challenges that second-guess
well-considered user requests.

> **Bad** (to a user with 50 microservices): "Your request to add a
> service assumes microservices are the right architecture. Have you
> considered a monolith?"

**Why it fails**: Fails the non-obvious criterion from the Relevance
Gate. The user clearly already made this decision. Surfacing it wastes
their time and erodes trust in the skill.

**The fix**: Apply the Relevance Gate's non-obvious criterion with
extra weight in task-framing challenges. The user knows more about
their context than the agent does. Challenge assumptions that are
genuinely implicit, not decisions that are clearly intentional.

---

## Layer 3b (Stochastic Perturbation) Anti-Patterns

These apply when running the stochastic perturbation pass (Layer 3b). The
general anti-patterns above also apply to any findings that emerge from the
perturbation process.

### 13. Forced Predicate Manufacturing

**What it looks like**: Manufacturing emergent predicates when the product
space P × {yᵢ} didn't yield any. The agent produces an elaborate analogy
between the seed and the artifact, dressed up as structural insight.

> **Bad**: "This microservice architecture is like a coral reef — many small
> organisms working together to create something larger. This suggests the
> architecture should be more 'organic' in its evolution."
>
> (This is metaphor, not an emergent predicate. It does not restructure
> understanding of P. It does not predict any specific failure mode or reveal
> any specific blindspot. "More organic" is not actionable.)

**Why it fails**: The entire value of the perturbation pass depends on the
honesty of the empty return. A perturbation agent that always returns non-empty
is not exploring — it's pattern-completing. The process of extended exploration
IS the computation; if the computation yields nothing, that's the correct
output. Manufacturing a predicate to fill the silence destroys the
signal-to-noise ratio of the entire protocol.

**The fix**: Every perturbation finding must survive the evaluation agent's
phase-transition test. If the finding doesn't restructure how P's predicates
relate to each other, it's not a phase transition — it's noise or at best
incremental. The perturbation pass producing zero phase transitions is a
normal, expected outcome. It is not a failure of the protocol.

---

### 14. Entropy Collapse

**What it looks like**: Generating seeds that are all from adjacent or familiar
domains, producing the illusion of diverse sampling while actually staying
within K.

> **Bad** (for a software architecture artifact): Seeds are "a different
> software architecture pattern," "a database design pattern," "a networking
> protocol," "a cloud deployment strategy."

**Why it fails**: These seeds are all within the software engineering predicate
space. They sample from K, not ¬K. The perturbation pass becomes a dressed-up
version of "consider alternative technical approaches" — which is just
analytical Layer 3 in disguise. The Monte Carlo integration collapses to a
neighborhood of the known.

**The fix**: Check the domain distance of your seeds. If a practitioner in the
artifact's field would recognize the seed as "related work," yᵢ ∈ K. At least
one seed should come from a domain that has no professional connection to the
artifact's field — ecology, liturgical practice, game theory, phenomenology,
supply chain logistics. The discomfort of the juxtaposition is signal.

---

### 15. The Mystification Play

**What it looks like**: Using the mathematical framing (predicate calculus,
phase transitions, emergent predicates) to package a trivial observation as a
profound discovery.

> **Bad**: "Through stochastic sampling from ¬K weakly conditioned on P, we
> discover that R(microservice_architecture, jazz_improvisation) reveals that
> the system lacks 'improvisation space' — room for developers to creatively
> deviate from patterns."

**Why it fails**: "Developers need flexibility" is not a phase transition.
Wrapping it in the perturbation protocol's language does not make it one. The
mathematical framing exists to make the method precise, not to elevate the
findings. If you strip the formalism and the seed reference and the finding
is obvious, the protocol didn't earn it.

**The fix**: Strip the formalism. Strip the seed reference. State the finding
in plain language. Ask: "Is this genuinely non-obvious? Does it restructure
understanding?" If the creator would say "obviously," the perturbation
protocol is being used as packaging, not as a cognitive mechanism.
