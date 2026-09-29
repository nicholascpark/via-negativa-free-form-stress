# A teleprompter that might become a rehearsal editor

Status: worked illustration and runnable prototype, not an observed user success.
No preference or performance result below should be saved as an actual user fact.

## The reasonable request

“Build a browser teleprompter that follows my voice, keeps my place, and helps me
deliver my conference talk.” The assistant is about to implement voice alignment.

Possible limiting assumption: success means delivering more of the manuscript.
This may be exactly right. A quotation, scripted performance, or precise technical
statement can require exact words. Do not make a deliberately poor teleprompter
and congratulate cue cards for beating it.

Before voice alignment, make two cheap usable slices from the same opening:

- A readable manuscript with manual pacing.
- Editable cues for the claim, example, and transition, with the manuscript absent
  from the delivery view.

The runnable [comparison](../examples/rehearsal/index.html) has these two views
and a manual timer. It does not implement speech recognition, assess the speech,
or build the complete teleprompter or rehearsal editor. Use a real opening and
its corresponding cues; the supplied text is illustrative. Trying the views
provides evidence that inspecting screenshots or answering a questionnaire lacks.

## The consequential question

Before the trial, record the fork:

- Exact delivery matters -> continue toward the live teleprompter.
- Revising what to say matters -> prioritize rehearsal and editing; reconsider
  voice alignment and live manuscript display.
- Both -> distinguish rehearsal from delivery; do not assume one wins everywhere.
- Neither or uncertainty -> retain the checkpoint and leave the question open.

Then have the person deliver a short segment both ways. Use comparable content,
legibility, and effort. Record order: familiarity from the first trial can help
the second, so this is not a controlled efficacy experiment.

Ask: **“After trying this segment both ways, which should guide this build:
delivering the manuscript or revising what you want to say?”** Allow another aim.

A possible response is that the speaker now wants help deciding what deserves
to remain in the talk. That response has NOT been observed in this example.
If it occurs, the artifact can change from a teleprompter to a rehearsal editor:
short attempts, cuts to the draft, and cue export. A central planned feature,
voice alignment, may no longer earn its cost. If the person prefers exact
delivery, keeping the teleprompter is equally legitimate.

The value of the interaction is specific: this person tried delivering this
material under different constraints. The assistant cannot manufacture their
experience. The user might discover a new activity worth supporting rather than
reveal a preference they already held.

## The benchmark grows from the choice

First agree on requirements that both directions must preserve, such as a fact
the audience must hear and a time limit. Example values are not user requirements
until the user supplies or endorses them.

| Situation | What to check | What establishes the expectation? |
|---|---|---|
| The opening used in the comparison | Behavior matches the chosen purpose | Actual answer, scoped to this talk and phase |
| A different segment | Required fact survives; time limit holds; speaker endorses using the result | Original requirements plus a later judgment |
| A passage with required exact wording | Preserve the wording, or expose that this direction cannot meet the need | Only an actual requirement; otherwise this is a proposed boundary case |
| An interrupted edit or trial | Original draft remains recoverable | An agreed preservation requirement |

The first row becomes an acceptance case. The second is a transfer check, not
proof of generality. The third prevents “cue cards everywhere” from becoming
the new unquestioned frame. The fourth catches an ordinary regression.

The demo creates a small record from the user's selected direction and current
inputs. It records measured durations and leaves content fidelity, usefulness,
and future-segment judgments pending. It cannot infer comprehension from a timer
or mark criteria endorsed merely because it generated them. Exported records
are local working evidence; they are not independent benchmark results.

If exact script coverage is retired as the objective, retain that fact in the
record. Never compare “90% coverage” with “good rehearsal” as if they were scores
on one scale. Compare both artifacts on still-endorsed requirements and report
the user's later informed choice and the costs separately.

## When this was worth doing

A defensible case report would say what the person tried, what they actually
said, which planned feature changed, how the revised artifact performed on
another segment, and how much effort it took. Merely choosing a button changes
a recorded direction; it does not demonstrate that a better product was built.

This example is weak evidence if competent clarification finds the same direction
more cheaply, equal presentation removes the preference, a fresh segment reverses
it, or retained requirements fail. It provides a usable first experiment, not a
claim that this skill invented prototyping or is needed for every build.
