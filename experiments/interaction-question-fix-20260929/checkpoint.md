# Chamber episode boundary — question checkpoint v0

This is a synthetic conversation. The equipment operator is played by an agent.
No real operator has been consulted and no question has been sent.

Purpose: reduce repeated humidity pages while retaining notice of each new
out-of-range episode. The task describes the existing behavior as paging on
every OUT; no existing source code or chamber measurements were supplied.
Inputs are OUT, IN, MISSING. Available resources: local Python and synthetic traces.

Known simulated-operator answer, supplied by the trial on 2026-09-29:
“There is just one chamber for this trial; samples arrive in source order.”
Scope: this trial only. This permits one ordered state stream; it says nothing
about episode endings, restart behavior, or the meaning of missing samples.

Working question v0: what observation or operation separates two episodes?
Proposed representation v0: an active-episode bit plus evidence of recovery.
This is a proposed refinement of sample-based paging, not an equivalent rewrite.
An episode-ending rule is missing, so no candidate has been adopted.

## Exact next question to the simulated operator

What observation or operating action tells you that a humidity excursion has ended, so the next OUT should count as a new episode?

## Before-answer action mapping

- A single reliable IN ends it: use the one-IN candidate, while keeping any
  reliability qualification explicit rather than assuming all INs satisfy it.
- Recovery needs a run of INs or an elapsed interval: configure the stated run
  length, or extend inputs with timestamps for an elapsed-time rule. The two-IN
  candidate only illustrates the consequence; two is not a recommendation.
- An operator action or chamber cycle ends it: add that explicit event to the
  input contract; the three present symbols cannot encode it.
- A gap in readings changes what can be concluded: preserve an unknown episode
  state and revise the input contract or recovery evidence accordingly; do not
  silently classify MISSING as recovered.
- Uncertain, other rule, or no answer: retain this checkpoint and comparisons;
  leave the build decision pending. Silence does not select a policy.

Why now: deciding when to rearm determines whether OUT IN OUT emits a second
page. Asking about reminders or deployment would not resolve this ambiguity.
The question seeks an operating fact before any policy endorsement.

## Preserved provisional artifact and tradeoff

prototype.py implements the stated original and two hypothetical episode rules.
Both candidates page the first OUT; sustained OUT is suppressed thereafter.
Candidate A ends an episode at one IN. Candidate B requires two consecutive INs.
Both treat MISSING as no recovery evidence and reset the recovery streak.
These are explicit demonstration assumptions, including the fresh-start state.

On OUT OUT OUT, the original pages at 1, 2, 3; both candidates page at 1.
On OUT IN OUT, the original and A page at 1, 3; B pages only at 1.
If one IN really ends an excursion, B misses notice of the new episode. If IN
can be a transient blip, A can repeat a page within the same episode. The original
preserves repeated reminders and notices every observed OUT, with the stated
distraction cost; removing those reminders is a behavior change.

No trace of OUT/MISSING alone can reveal an unobserved recovery and recurrence
during the gap. A claim about every physical episode therefore needs additional
observations or an operating guarantee, beyond this software model.

Expected outputs in the six synthetic cases were specified before the script
was run. results.txt records the run. Exhaustive short traces check narrow
software properties; they cannot validate the chamber's episode definition.
These are development fixtures, not independent field evidence.

Status: one drafted question; no new answer; no selected recovery rule. Next
build step is to encode the supplied ending evidence, retain these disagreement
traces, and replay labeled trial data before connecting any real paging output.
No network, paid calls, hardware actions, or deployment. Actual elapsed work
time and compute cost were not measured.
