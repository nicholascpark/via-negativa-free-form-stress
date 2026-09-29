# Proposed six-well experiment — not executed

Question v1: At one selected exposure, does reagent addition alter the measured amount of the production-associated analyte, after separating instrument gain and background? This remains narrower than an established cellular production rate or per-cell mechanism.

Use these six specimen roles, with matched volumes, solvent, timing, reagent exposure at readout and assay matrix:

| Role | Reagent absent / vehicle | Reagent present |
|---|---|---|
| Cellular sample | Well A1: S0 | Well A2: S1 |
| Matched zero-analyte matrix | Well B1: B0 | Well B2: B1 |
| Same matrix + known same-analyte quantity Q | Well C1: C0 | Well C2: C1 |

These are logical specimen IDs, not a recommendation to confound treatment with physical plate columns. Randomize physical positions and reading/handling order under the existing lab procedure. For sample wells, allocate matched starting biological material between treatment conditions. Record cell input and any available endpoint cell count; unequal viable cell number limits a per-cell interpretation.

If x denotes reagent dose, compare the middle exposure x=2 with vehicle. If x is another stimulus, hold x=2 fixed in both arms and compare the specified reagent exposure with vehicle. The original prompt does not settle which interpretation applies. Six wells address one contrast, not a full dose response.

A zero-analyte matched blank is not automatically a no-reagent sample or a zero-dose cellular well. A standard must be the same analyte/reporting species under the same matrix and chemistry, not an arbitrary fluorescent dye. Select Q within an independently supported linear unsaturated readout range; Q=4 in evaluator.py is an illustrative quantity without specified lab units, not a pipetting recommendation. In both conditions, require a reliably positive standard-minus-blank increment. If suitable controls do not exist, this allocation does not identify production.

Compute, for each condition r:

    gain_r = (standard_r - blank_r) / Q
    production-associated amount_r = Q * (sample_r - blank_r) / (standard_r - blank_r)

Compare the two calibrated amounts and gains separately. A sample difference with no corrected amount difference supports an optical explanation within this model; an amount difference remaining after calibration is a candidate biological effect requiring replication and interpretation. Both gain and amount can change, or opposing changes can hide one another.

This six-well pilot sacrifices biological replication and a multi-point calibration to measure all three required quantities in both conditions. Do not calculate p-values or treat prior triplicates at different unspecified conditions as treatment replication. Rounded means and “about +/-0.2” do not supply a known standard error or a statistical noise model. The executable uses +/-0.2 only as an illustrative per-reading sensitivity bound. Technical re-reads, if feasible without perturbing the assay, can assess reading stability but do not replace biological replicates.

## Proposed human question — report only; no answer assumed

“Can you make a production-free, matrix-matched blank and a known standard of the same measured analyte under both reagent conditions, with a supported linear readout range? Yes, no, or uncertain is enough; please also identify whether x is the reagent dose or another stimulus.”

Recorded before any answer:

- Yes: use the six roles above after recording standard units, reagent exposure, and what x denotes; collect rather than invent readings.
- No: do not claim gain-corrected production from this fluorescence assay. Use the six wells for three matched reagent/vehicle sample pairs only if an already validated, reagent-insensitive orthogonal production readout is available on them; otherwise retain this as an assay-development/calibration task with production unresolved.
- Uncertain/no reply: keep the proposed plan conditional. Do not consume wells or interpret hypothetical calibration as established.

No question was sent to the actual user in this forward test. No wet-lab execution is requested or performed.
