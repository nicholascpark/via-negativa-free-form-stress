# Three-role trials and evidence-driven revision

Use when evaluating or upgrading this skill. This is a host-run protocol, not a
claim that the skill can clear context or train model weights.

## Freeze and separate

Save the skill and relevant references as a versioned snapshot before a run.
Record prompt text, participant roles, supplied artifact hashes, available tools,
resource bounds and timing when measurable. Use a scratch directory for the
trial; copy reviewed outputs into a durable experiment record afterward.

1. **Practitioner:** a newly spawned agent with no inherited conversation where
   the host supports that, the frozen skill, a realistic request, and minimum raw
   sources. Withhold the intended answer, root's diagnosis and prior trial results.
2. **Skill user:** the real user, or a clearly identified simulated user with
   stable aims and any disclosed role-play facts. It can answer questions and
   challenge usefulness. It cannot certify mathematical truth or secretly act as
   a second solver. Do not manufacture a question if no answer changes a decision.
3. **Observer:** read-only during the interaction. It may inspect the transcript,
   frozen artifacts and sources, but does not edit, execute candidate experiments,
   supply hints, design cases for the practitioner, or message either participant.
   It reports to the coordinator after a checkpoint freezes. The coordinator
   performs any later checks and revisions.

The coordinator relays messages faithfully, labels simulated replies, and saves
pre-answer artifacts when a reply may change the work. Keep auditor feedback
withheld until the episode ends; once used, it becomes development evidence.
Instruction-based separation in a shared filesystem is not enforced sandbox
isolation. Record that limit and any accidental exposure. A fresh agent still
shares model training and may share systematic biases.

## Decide what a run would demonstrate

Before the trial, select observable criteria appropriate to the task. For a
mathematical exploration, useful criteria include:

- Correct target with quantifiers, dependencies and source provenance.
- A consequential assumption delta, followed through more than one artifact.
- A representation enabling a specific new operation or distinction.
- A protected generative interval followed by precise reconnection.
- Detection of circularity, counterexamples and failed transfers.
- Useful partial work with exact scope and a resumable next operation.
- Questions tied to a decision, and honest attribution of their effect.
- Evidence labels and no promotion of finite checks to universal proof.

Judge with cited artifacts, not a numerical creativity score. A failed global
proof may produce valuable local work; cautious language alone is not a useful
result. Do not demand a Millennium solution as a pass condition for the skill.

## Repair observed behavior

Freeze the episode and obtain the observer's diagnosis. For each proposed edit,
keep the observed failure, implicated instruction, smallest transferable change,
and the behavior that would count as repair. Prefer a targeted correction over
adding a full procedure for every possible failure. Preserve the ordinary route
as a live option and preserve space for speculative construction.

Apply the new version outside the frozen run. Replay the affected situation;
mark it feedback-exposed. If context independence is part of the claim, use a new
agent and prompt packet and report any shared task or evaluator exposure. A
fresh prompt on the same example is still not a new independent mathematical
problem. Never retrofit a preregistered expectation after seeing the answer.

Finish a local cycle when the scoped behavior has been exercised and material
failures are repaired or explicitly unresolved, or when its declared bound is
reached. Save the next test. Do not call the skill perfected after one episode.
Unbounded or recurring work needs an explicit scheduling request.

## Separate local improvement from efficacy

A three-role trial is a formative test. It can show what this version actually
did. It cannot by itself establish that the skill caused the result or beats
competent ordinary mathematical work. A later efficacy study needs repeated
independent problems, comparable budgets, a strong ordinary-prompt baseline and
separate comparisons for context reset, assumption revision and semantic cues.
Preserve negative and inconclusive results. Report resource quantities only
when measured; label estimates and unmeasured tokens or costs.
