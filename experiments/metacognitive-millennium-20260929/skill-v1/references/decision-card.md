# One decision, one comparison

Use the project's existing notes and test runner. This card is a convenient
format, not a mandatory new subsystem. Fill the first block before asking; use
a commit, timestamped file, or append-only log to retain it. Do not backfill an
answer-to-action mapping after seeing the answer.

Ask for the missing operating rule before proposing a preferred policy. Keep
one pending decision in focus; do not turn several defaults into one agreement
question. For example, ask “What tells you this fault has ended?” before deciding
whether one NORMAL reading clears it. If the answer leaves a meaningful choice,
show its concrete consequences and give the alternatives comparable detail.
Ask about reminders separately only when their behavior remains consequential
and unknown. This is an example of question shape, not a fixed questionnaire.

```text
Decision / artifact version:
Current direction / evidence:
Assumption temporarily released:
Concrete original and alternative on the same input:
Tradeoff each exposes:
Constraints retained / proposed revisions requiring user judgment:

Question and full presented material (including order):
Why ask now / interaction budget:
Before answer:
  Keep original ->
  Choose alternative ->
  Combine / introduce another distinction ->
  Neither / uncertain / no response ->
Plausible alternatives not shown:

Answer (verbatim, source, date):
Speaker provenance: real user / simulated user / other evidence source
What is new relative to existing evidence:
Scope / exceptions / unknowns:
User's account, if offered: discovered / formed / revised / uncertain
Decision and concrete artifact change, or reason for no change:
Outcome: changed behavior / selected existing alternative / confirmed / unresolved

Live benchmark version:
  Case | expected behavior | authority and scope | tested version | observation | status
  Demonstrated situation:
  Different relevant situation:
  Where the original has an advantage:
  Shared requirements:
Retired criterion and reason (retain previous version):

Result: keep original / keep change / revise / unresolved
Actual cost: user questions and time; build/evaluation time
Next decision, only if unresolved evidence warrants one:
```

Not every row needs a separate test. A case can check a shared requirement and
a tradeoff together. Keep the smallest set that distinguishes the actual choices.

“Unknown” is a valid expectation. “Pending judgment” is a valid result. Label
defaults and illustrative examples as such; selecting a product direction does
not endorse every automatically proposed acceptance criterion.

When memory is useful, retain the answer, scope, evidence, artifact delta, and
case results. Do not place every discarded hypothesis into the working prompt.
An agent summary is an interpretation; keep a link to the underlying answer.
If a simulated user supplied the answer, repeat that attribution in each
standalone report or handoff that relies on it. Confirmation is not a new
behavioral change, and a simulated endorsement is not real-user validation.

For a comparative study, use the richer record in
[episode-template.json](../experiments/runtime-questioning/episode-template.json)
and the associated protocol. This small card alone does not enforce blinding,
independent evaluation, or immutable records.
