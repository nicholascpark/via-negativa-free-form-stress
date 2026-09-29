# Actual result of this local forward test

Raw supplied illustrative inputs: x=1,2,4; reported mean response y=2,4,8 with three repeats and approximate variation +/-0.2. No individual repeats or new measurements were supplied.

What changed: the proposed inference is now expressed as separate production and gain ratios. Two exact synthetic mechanisms reproduce the original curve: p=x,g=2 and p=2,g=x. Unknown constant gain alone would preserve relative production ratios; condition-dependent gain creates the confounding. The gain-only explanation remains a rival, not a finding.

The continuing calibration branch constructed a reusable observable, Q(sample-blank)/(standard-blank), and a conditional six-well design: sample, zero-analyte matched blank and known same-analyte standard in each reagent condition. It makes progress only if calibration transfers to the cellular sample and the signal is linear. The plan and the consequential feasibility question are in next-experiment.md. No answer or observation was invented.

Actual executable outcome: evaluator.py passed seven synthetic development checks. Production-only, gain-only, cancellation and background effects were recovered exactly in their stipulated noiseless models. A small effect remained ambiguous under the illustrative error envelope; a weak calibration was rejected as inconclusive. A deliberately mismatched calibration produced a false twofold production estimate for truly unchanged production, preserving the central transfer limitation instead of hiding it.

Computed production-ratio sensitivity envelopes at illustrative per-reading bound +/-0.2:

- Production-only: 27/22 to 121/36 (approximately 1.2273 to 3.3611), excluding 1 in this sensitivity model.
- Gain-only: 9/14 to 121/76 (approximately 0.6429 to 1.5921), compatible with 1.
- Cancellation: 1 to 33/8 (1 to 4.125), so no-change is not excluded by this conservative envelope despite exact noiseless recovery of ratio 2.
- Small effect: output file contains exact bounds; the interval includes 1.

These are deterministic sensitivity envelopes, not confidence intervals. The stated +/-0.2 is approximate and not a validated bound. Shared-blank dependence is handled conservatively by outward interval bounds. Biological variability and calibration model error are not included.

Run locally:

    python3 experiments/research-trajectories/assay-identifiability/evaluator.py

After collecting readings, fill a copy of observations-template.json and pass its path as the sole argument. Null readings cause an error rather than being imputed. Passing measurements to the calculator does not verify matrix matching, standard stability, linearity or a production-rate interpretation.

Limits: six wells contain no independent biological replication per condition and only one nonzero calibration level; the production mechanism remains unresolved. No external datasets, wet-lab work, network or paid services were used. A requested independent worker was unavailable due to the agent-thread limit, so both branches and checks came from one worker. Predictions and development fixtures were not independent empirical evidence. No comparison against ordinary prompting was run, and no method-superiority claim is made. Model-token cost and wall-clock compute cost were not measured.
