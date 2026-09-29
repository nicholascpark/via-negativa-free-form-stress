# Cross-domain development checks — 2026-09-28

This record checks whether the skill can produce usable, inspectable work across
different domains. It does not measure an improvement over ordinary prompting.
The tasks are synthetic and deliberately small. They are now disclosed examples,
not an unexposed evaluation set.

The revised core used for the empirical and numerical runs has SHA-256
`aa670ae34fc81a5772e18699079ae94faf03d1188d52b636d75876ce666b8f41`.
Separate workers received the current skill, a raw task and resource constraints,
without a proposed solution. These were separate executions using existing
workers, not a study of fresh-context isolation. Each worker developed local
branches; further delegation was unavailable. No outside data, paid tools, wet
lab work, hardware deployment, or real human responses were used. Root reviewed
the new artifacts and reran their retained executable checks.

| Endeavor | Change in representation | Useful return | Actual check and limit |
|---|---|---|---|
| Mathematics, earlier trial | Fourth moment becomes a symmetric interaction term | Exact counterexample family, identity and scoped consequences | Exact rational checks at dimensions 2–12 supplement the derivation; no proof-assistant check |
| Empirical inverse problem | Raw fluorescence becomes separate production-associated amount and gain | Conditional six-well experiment and calibration operator | Seven synthetic cases, including a false positive when calibration fails to transfer; no new measurements |
| Numerical engineering | Ringing becomes a spectrum of signed amplification factors | Substepping operator, cost/accuracy comparison and a failed-filter witness | Fifteen development checks; no original production solver or physical material validation |

## A benchmark generated during a build

In the thermal run, a smoothing filter removed the original checkerboard
perturbation. Composing its operator with the time update exposed another mode
with predicted gain −5.9. The worker generated that input and measured the same
gain in the direct stencil calculation. The proposed filter consequently failed
a case that arose from developing the correction itself.

The retained alternative splits each requested output interval into stable
internal steps. It also exposes the cost: at the finer grid, 16 internal steps
per output interval. Smooth-solution refinement checks measure accuracy separately.
This is a concrete example of a local benchmark growing from a new artifact.
It remains standard numerical analysis, not evidence of a new scientific method.

The assay run similarly generated a calibration-transfer failure. Its operator
can separate amount from gain in stipulated models, yet returns a false amount
change when the standard and cellular sample have different gains. That failure
is preserved as an empirical obligation, not explained away by passing other
synthetic checks. The proposed human question records how feasibility answers
would change the six-well allocation; it was not asked or answered in this test.

## Reproduce and inspect

From the repository root, using Python 3.10+ and its standard library:

```sh
python3 experiments/research-trajectories/moment-inequality/verify.py
python3 experiments/research-trajectories/assay-identifiability/evaluator.py
python3 experiments/research-trajectories/thermal-stability/thermal_lab.py
python3 experiments/research-trajectories/test_archive.py
```

The scientific example scripts write their generated output beside themselves.
The archive test suite uses temporary directories. Its 11 passing tests exercise
record collisions, concurrent publication, ancestry, path constraints, hash
matching, changed/missing artifacts and CLI behavior. Those are storage tests,
not scientific evidence.

Inspect the [mathematical derivation](moment-inequality/trajectory.md),
[assay report](assay-identifiability/REPORT.md),
[proposed experiment and question](assay-identifiability/next-experiment.md),
and [thermal trajectories](thermal-stability/trajectories.md). Each example keeps
its assumptions and evidence limits with the artifact.

The core also includes domain guidance for distributed systems, physical design,
control and VLA. Those domains were not exercised in these new runs. The image/text
sampler has separate existing fixtures and was not needed for either new case.
No equal-budget baseline, real-user outcome, or advanced open-problem result was
measured. Agent tokens, orchestration overhead and human reading time were not
measured; numerical run timing covers the local script only.
