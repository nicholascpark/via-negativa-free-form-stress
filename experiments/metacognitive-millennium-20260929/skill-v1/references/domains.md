# Reconnecting across scientific and engineering domains

Use only the sections relevant to the task. These criteria guide what a return
artifact means and which claims it supports. They do not police every exploratory
transformation. A hybrid task may require several kinds of evidence.

| Endeavor | Useful object to invent | Concrete return |
|---|---|---|
| Formal mathematics | Definition, coordinate system, construction, lemma | Precise statement, derivation or counterexample, remaining obligations |
| Empirical science / inverse problem | Observable, rival model, identifiable parameter combination | Measurement definition and an experiment or analysis separating explanations |
| Numerical / computational model | Formulation, approximation, discretization, reduced state | Executable calculation with assumptions, settings and error evidence |
| Software / distributed system | Invariant, protocol, abstraction, schedule generator | Code, behavioral model, or trace under stated operating assumptions |
| Physical design / control / VLA | Geometry, controller, affordance, action representation | Design or control artifact with an operating envelope and a testable prediction |

## Formal mathematics

Preserve quantifiers, domains, hypotheses and the statement sought. Keep proof,
counterexample and auxiliary routes available where they address the question.
A new definition or partial lemma can be useful before a full proof exists.

Return definitions, derivation, dependency assumptions and outstanding lemmas.
For a counterexample, check every hypothesis and the violated conclusion. For
formal verification, examine the encoded statement, definitions, axioms and gaps
as well as checker output. Finite numerical samples do not establish universal
claims. An identity in a restricted case remains scoped to that case.

Generate checks from exceptional cases, boundary conditions, missing hypotheses,
and attempted transfers. Preserve failures as witness families when possible;
the family may expose what the current variables hide.

## Empirical science and inverse problems

Capture what was measured, how, with which units, calibration, sampling process
and uncertainty. Distinguish observations from labels, fitted parameters and
mechanistic interpretations. Ask for consequential missing measurement context;
do not invent it. Rival explanations can remain observationally indistinguishable.

A productive branch might construct a new observable, expose an identifiable
parameter combination, or design an intervention where live models disagree.
Return the operational definition, predicted difference, competing explanation,
detectability conditions and relevant uncertainty. Separate simulation, fitted
observations and newly collected measurements.

For an illustrative inverse problem, suppose readings obey y(t)=b+A exp(-kt).
If the only observation is y(0), it constrains b+A and supplies no information
about k in this model. Returning that equivalence class plus proposed time points
is legitimate; inventing a fitted decay rate is not. This is a disclosed example,
not a general model to impose on experimental data.

Generate cases from rival predictions, detection limits, alternative calibration
assumptions and feasible measurement regimes. Keep data used for model selection
separate from subsequent confirmation when possible. Observational fit alone
does not establish causation. A proposed experiment remains proposed until run.

## Numerical and computational models

Record equations or algorithms, units, initial and boundary conditions, solver
settings, resolution, tolerances, random seeds where relevant, and outputs.
An executable reformulation can enable a calculation without improving accuracy.

Match checks to the claimed change: discretization refinement, stability,
conservation, reference solutions, parameter sensitivity, or approximation limits.
Distinguish numerical error, error from simplifying the model, and disagreement
between the model and observations. An apparently stable plot does not establish
convergence. Keep constants and estimates that depend on resolution explicit.

Generate stress cases around regime transitions, parameter extremes and coupled
effects. Compare cost and accuracy under compatible conditions. For stochastic
methods, record uncertainty and the relevant repeated runs; one favorable seed
cannot establish a robust improvement.

## Software and distributed systems

Capture the observable contract, current implementation and relevant workload,
concurrency, timing, consistency and failure assumptions. A useful representation
can be a state machine, dependency graph, invariant or counterexample schedule.

Return executable behavior or an operational model and its correspondence to the
implementation. Generate histories where the proposed representation matters:
ordering, retries, recovery, load changes, resource limits or boundary inputs.
Retain regression witnesses. Select what is relevant rather than running a
universal checklist.

Separate functional behavior, safety, liveness and performance. A finite test
suite supports its exercised cases. Liveness conclusions may depend on fairness
or eventual delivery; write that assumption explicitly. A proof about a model
needs an argument connecting the model's transitions to implementation behavior.
Performance claims need the workload and measurement conditions.

## Physical design, control and VLA

Record the operating envelope, material or plant assumptions, units, loads,
sensors, actuators, delays, disturbances and constraints that matter. The
representation can include geometry, an action space, contact modes or a model
of what the system can do under stated conditions.

Return a design, controller, action representation or failure envelope with
predicted behavior. Distinguish calculations, simulations, hardware measurements
and authorized physical trials. Simulation success is evidence about the model;
transfer to hardware requires checking the relevant mismatch.

Generate cases at coupled limits such as saturation, delay, contact transitions,
power consumption or recovery when they affect this design. Preserve physical
constraints and the task's authorized operating envelope. A speculative model
may change an assumption; it does not authorize changing real hardware limits.

## Human purposes and hybrid endeavors

When the work includes a user's preferences or a revised purpose, use concrete
comparisons and scoped judgments alongside technical evidence. A test cannot
replace the person's decision about which tradeoff serves their purpose.

For a hybrid example, a learned controller can require numerical checks of its
simulation, empirical evidence about its sensors, software checks of execution,
and physical trials within its operating envelope. Record the gaps between those
layers. Do not promote evidence from one layer into a conclusion about all of them.
