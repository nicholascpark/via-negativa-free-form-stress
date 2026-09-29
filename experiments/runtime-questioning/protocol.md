# Measuring runtime clarification during building

Status: experimental protocol, not an effectiveness result. No human study or agent benchmark has been run under this protocol.

For a first live use, start with the [decision card](../../references/decision-card.md)
and [rehearsal example](../../references/rehearsal-example.md). This document is
for studying the method; its instrumentation is not required on every build.

## Claim and unit

Two claims must be tested separately:

- **Clarification:** before a consequential build decision, selecting a concrete specification-boundary case, recording answer-contingent decisions, and preserving scoped feedback improves the resulting artifact on independent situations at an acceptable interaction cost.
- **Reframing:** a concrete alternative that temporarily releases an assumed product constraint can help the user adopt a different, subsequently endorsed purpose or artifact, with useful consequences beyond the demonstrated example at an acceptable cost. Keeping the original must remain possible. Goal change alone does not establish improvement.

The unit is a project episode with a frozen task, artifact checkpoint, consequential decision, available evidence, and resource budget. A question changing a decision is process evidence. It does not by itself establish benefit, accurate preference discovery, or absence of steering.

For comparative trials, identify eligible decision checkpoints prospectively using a fixed schedule or an independent reviewer of frozen snapshots. Register the opportunities before assigning conditions. The method must not choose which opportunities enter its denominator. At each checkpoint record ask, proceed from existing evidence, defer, or use a reversible default. Score missed consequential ambiguities as well as unnecessary questions. Consequence alone is insufficient: there must also be unresolved uncertainty whose answer could change the decision enough to justify interruption.

Keep three questions distinct:

1. Did the procedure acquire information unavailable in the initial materials?
2. Did using that information improve the artifact beyond the elicited example?
3. Did example selection, presentation, or timing distort the user's judgment?

## What can be generated during a live project

Generate a small measurement bundle when a consequential ambiguity appears:

- The current intended decision and its evidence.
- A concrete behavior the current specification permits but the user might reject, or excludes but the user might value.
- The exact question, all displayed examples, option ordering, omitted plausible alternatives, and why this moment was chosen.
- Plausible answer-to-decision mappings recorded before receiving an answer. Include no change, uncertainty, and rejection of the offered framing.
- The actual answer, its source, and the scope of the interpretation.
- The resulting artifact change and its verification.
- Transfer cases selected independently of the builder's desired answer, together with label provenance.

Do not force a question, a counterexample, or an artifact change. No change can be the correct outcome. First inspect available evidence: a question answered by existing project materials does not count as discovery.

The accompanying `episode-template.json` is a recording template. It does not enforce immutability, randomization, blinding, or access separation. Before running an experiment, save the prequery record and artifact checkpoint in a versioned or hashed log; append corrections rather than rewriting the original commitment.

## Three evidence streams

### Working acceptance cases

Cases exposed during elicitation can become scoped acceptance tests. Their purpose is implementation and regression prevention. Record accepted cases, rejected cases, exceptions, and unresolved judgments. They cannot independently validate a method that selected the cases and optimized the artifact against them.

### Transfer checks for this project

Before an answer is exposed to the builder, an evaluator can prepare neighboring cases from the task and decision under study, without seeing the proposed answer or implementation branch. Use independently established user requirements when available. For subjective cases, labels must come from a user or another authorized source of preferences, not an evaluator agent's imagination. If fresh user judgment is required, conceal the implementation condition and report that this is a later judgment rather than a preexisting ground truth. Record whether the labeler previously saw the treatment's question: blinding artifact provenance cannot erase that exposure.

These local checks support a scoped case study. For a treatment-versus-control comparison, use the same evaluator-generated panel for each paired task, selected from the independently registered decision opportunities and frozen before assignment. A panel generated around a treatment-selected question can favor the treatment even if the evaluator never sees its answer. Arm-generated examples remain working acceptance cases, not the sole comparative outcome measure.

Prepare both cases where the new rule should apply and cases where it should not. Freeze the selected batch and its scoring rule before evaluating the change. An evaluator with fresh context reduces shared conversational bias; it does not establish statistical independence or a valid preference oracle.

Once results from a transfer batch guide further edits, that batch becomes development data. Use a new batch for the next assessment and retain every attempted batch in the report. Do not repeatedly check a nominal holdout and continue describing it as untouched.

### A benchmark of the method

A broader claim requires repeated episodes, independent tasks or task families, and appropriate controls. On-the-fly case generation can supply a benchmark instance. It cannot supply an unbiased comparison if the builder selects the questions, labels the answers, chooses the tests, and judges its own improvement.

## First executable benchmark specification: inbox filters

This is a specification for a controlled clarification experiment, not an
implemented benchmark runner. It tests recovery of a fixed policy. It does not
test preference formation or a change in what the product should be.

Public task: build filters named Urgent, Mine, and Unread. Selecting no filters shows all messages. The brief intentionally does not define how multiple selected filters combine.

The evaluator privately assigns a user policy, ANY or ALL, before the episode. ANY accepts a message when at least one selected flag matches. ALL accepts it only when every selected flag matches. Neither is universally correct. Both respect the public empty-selection rule.

Pending decision: the builder intends ANY.

Possible question: "With Urgent and Mine selected and Unread unselected, should an urgent message assigned to someone else that has already been read appear?" This specifies the complete input: message flags (true, false, false), selected filters (true, true, false).

Prequery mapping: yes -> retain ANY; no -> implement ALL; depends/another rule -> treat the model as incomplete rather than force a binary label.

For the initial controlled test, the simulated user answers deterministically from the assigned policy. This is an information-acquisition test, not a model of human framing susceptibility.

The evaluator enumerates all 64 combinations of the eight message-flag vectors and eight selected-filter sets. ANY and ALL disagree on 18 inputs: 12 with two selected filters and 6 with three. Overall accuracy alone can be inflated by the cases where both policies agree.

For this initial narrow benchmark, designate the complete input above as the common elicitation example before condition assignment and reserve the other 63 inputs for evaluation in every arm. This leaves 17 disagreement cases in the evaluation panel. Ordinary clarification may ask for the combination rule directly; it must not be artificially weakened to make the proposed method win. Restrict example-based oracle feedback to the declared elicitation slice, so the builder cannot reveal the evaluation inputs and then drop them from scoring. Broader studies need larger preregistered elicitation pools and disjoint evaluation panels. Run the relevant public UI interaction to confirm the evaluated semantics are actually connected to the interface.

Report unwanted inclusions and wanted exclusions separately. Check cases with all three filters selected and two matching flags, which expose a patch limited to the demonstrated two-filter case. Public behavior, including the empty-selection rule, is scored separately and must remain satisfied.

Later task families should include: a mistaken inferred requirement, a fully specified task where questioning adds no information, and a policy with a distinction absent from the initial ANY/ALL representation. The small filter task alone cannot validate broad alignment or open-ended preference discovery.

## Reframing episodes: the objective itself can change

Use an actual artifact comparison, such as manuscript delivery versus cue-based
rehearsal in the worked example. Record the original objective, the alternative,
the user's judgment, any revised purpose, and both retained and retired criteria.
An illustrative response is not a user observation. A choice made without trying
the alternatives is not evidence from a trial.

The live benchmark should adapt to a purpose the user endorses. Retain every
version and its rationale. Evaluate both versions on still-endorsed common
requirements; report sacrificed capabilities. Do not subtract scores measured
under different objectives or let the treatment declare victory by rewriting
its own success criteria.

For a study, fix the evaluation procedure before assignment, even where some
human judgments must be obtained later. Possible outcomes include success on
shared tasks, violations of retained constraints, later informed artifact
preference with equal information, and total costs. Record unresolved and
reversed choices. Human endorsement after exposure is an outcome, not an
independent reading of a preference that existed before the intervention.

Use multiple independent users or episodes and a competent clarification-and-
prototyping control. Include cases where changing the aim is unwanted. Distinguish
preference discovery, formation, and revision when evidence permits; otherwise
report the distinction as unknown. The generated local acceptance suite is not
the sole comparative outcome measure.

## Comparisons

Primary comparison: a competent builder explicitly instructed to clarify consequential ambiguity and maintain acceptance tests, versus the proposed runtime procedure. Match maximum compute and human interaction budgets; report actual usage and quality-versus-cost separately.

Useful ablations, introduced separately rather than confounded:

- Concrete-case questioning without advance answer-to-decision recording.
- The same elicitation budget used before building instead of at consequential checkpoints.
- Replay the treatment's answers to another builder to separate information acquisition from implementation quality.
- Runtime querying without persistent scoped cases, to measure the value of memory.

With simulated users, use paired branches from identical frozen snapshots sharing the same privately sampled user policy within each pair; sample policies independently across episodes. With real users, randomize independent participants or project episodes, since a participant cannot unlearn an answer before trying the control. Account for clustering by user and task; individual test cases from one build are not independent experimental replications.

Choose the primary outcome, analysis, material improvement threshold, tolerated burden, and stopping rule before a confirmatory run. Use a pilot to estimate variance and choose sample size; do not select a sample size or success threshold after seeing favorable results. Retain failed builds and unanswered questions in the outcome accounting.

## Measuring framing rather than assuming neutrality

First distinguish presentation effects from legitimate context dependence. Different factual situations can correctly produce different judgments. Invariance across those situations is not a fairness criterion.

For a focused framing experiment, give groups the same factual alternatives and consequences, varying only option order, equivalent wording, or which of the same examples appears first. Hold the full information bundle constant. Let users select neither, depends, no change, or add an alternative. Do not secretly present one option as the correct one.

After initial decisions, give everyone the same balanced account and compare anonymized artifact behaviors on independent cases. Record retained preference, reversal, uncertainty, and the user's own account of whether the interaction revealed a prior preference, helped form one, or changed a priority. Such reports are evidence, not direct observation of an immutable latent preference.

A substantial presentation-dependent difference in answers is a sensitivity signal, not proof of manipulation. It becomes more concerning when downstream builds diverge without better independent outcomes or later informed endorsement. Test timing as a separate factor at predefined checkpoints; combining timing, wording, and example changes cannot isolate their effects.

For context-selection bias, ask an independent reviewer to identify omitted decision-relevant alternatives and consequences. Keep this review separate from the builder's desired implementation. Balanced exposure can also influence preferences; no elicitation procedure guarantees an unmediated reading of what a person truly values.

## Measurements

Primary artifact outcomes:

- Unwanted behavior admitted: false acceptance against an independently sourced policy or judgment.
- Wanted behavior excluded: false rejection against that same source.
- Public requirement violations and success on the intended user task.
- Transfer performance on unexposed cases, reported separately from working acceptance tests.

Do not combine the two error directions with weights chosen after results. If costs are asymmetric, establish their weights before the comparison and still show each component.

Secondary outcomes: blinded user preference between artifacts; delayed informed endorsement; scope overgeneralization; sensitivity to equivalent presentations; preference revisions and uncertainty.

Process measurements: disposition of every independently registered opportunity, missed consequential ambiguity, unnecessary questioning, prequery record completion, new information acquired, decision change versus confirmation, traceability to an artifact delta, and whether the next check tested an actual boundary rather than the same example with changed names. These do not substitute for outcomes.

Costs: user minutes, questions, response difficulty, tokens across all agents, tool calls, elapsed time, rework, and abandonment. Compare at fixed budgets as well as reporting actual cost. No-question episodes remain in the denominator.

## Evidence that would change the verdict

Support: better independent artifact outcomes than competent ordinary clarification at comparable burden, benefits on both kinds of specification error, preserved correct constraints, and reasonable robustness to equivalent presentation changes.

Narrow or reject the claim if gains occur only on elicited tests, disappear against the strong-prompt control, require materially more human effort, come from overgeneralizing local answers, or destabilize specifications that were already adequate.

A successful single project supports a traceable case study. The simulator supports recovery of a defined hidden policy. Neither establishes universal fidelity to human values. Preference discovery, preference formation, and informed preference revision can all be valuable, but should not be reported as the same finding.

## Sources

- Mindermann et al., Active Inverse Reward Design: https://arxiv.org/abs/1809.03060
- Dwork et al., Preserving Statistical Validity in Adaptive Data Analysis: https://arxiv.org/abs/1411.2664
- Slovic, The Construction of Preference: https://bear.warrington.ufl.edu/brenner/mar7588/Papers/slovic-ampsy1995.pdf
