# Research trajectory and retained obligations

## A1 — from fitted curve to an equivalence class

Parent: raw brief in run.json. Exact transformation under the given multiplicative model: y=g p is unchanged by p -> c p, g -> g/c for any c>0. An unknown *constant* gain prevents absolute production calibration but does not prevent relative comparisons when it truly stays constant. If gain can vary with dose/reagent, independent positive rescalings at those conditions also preserve the observations. The raw means alone do not resolve that assumption.

## A2 — develop rival mechanisms

Parent A1. Construct two synthetic families at x=1,2,4. Production model: p(x)=x, g(x)=2. Gain model: p(x)=2, g(x)=x. Both predict y=2x exactly at every supplied dose. The second is eligible only if reagent/dose can alter gain; it is not evidence that this occurs. Repeated measurements of the same confounded observable reduce random uncertainty but do not separate these families.

## A3 — new target observable

Parent A2. For reagent conditions r=0,1, define production ratio R_p=p_1/p_0 and gain ratio R_g=g_1/g_0. With properly background-corrected raw readings, R_y=R_g R_p. A raw twofold effect can have (R_p,R_g)=(2,1), (1,2), or many other decompositions; no visible raw effect can hide (2,1/2). The task remains the reagent's production effect, now distinguished from its optical effect. Concentration, timing, cell count and assay endpoint remain needed to interpret that quantity biologically.

## B1 — an auxiliary known input for the instrument

Parent: raw brief. Proposed refinement: allow reagent-specific additive background b_r and a linear gain g_r. Construct three specimen types in each reagent condition: production-free matrix blank B_r=b_r; that matched matrix containing known quantity Q of the same measured analyte C_r=b_r+g_r Q; cellular sample S_r=b_r+g_r p_r. Assumptions: common background and gain transfer among these specimens, stable reagent exposure at readout, a genuine zero-analyte blank, a known same-analyte standard, and linear unsaturated response. These are feasibility/transfer obligations, not guaranteed by naming a control.

## B2 — reusable cancellation operator

Parent B1. Exact algebra under those assumptions:
  g_hat_r=(C_r-B_r)/Q;
  p_hat_r=Q(S_r-B_r)/(C_r-B_r).
Thus R_p is the ratio of the two corrected production estimates, and R_g is the ratio of calibration increments. The original nuisance gain becomes measurable through a known analyte input. A control fluorophore with different quenching or chemistry does not discharge this obligation. A cell-free blank with a different matrix can produce false conclusions.

## B3 — fit the construction to six wells

Parent B2. One sample, one blank, one known standard under vehicle/no reagent; the same three under one selected reagent exposure: exactly six wells. Match primary stimulus, assay timing, solvent, initial cellular input and handling. The intended contrast is reagent addition; keep other causes fixed. If x is reagent concentration, choose x=2 versus vehicle; if x is another stimulus, hold x=2 fixed in both arms and use the original specified reagent exposure. Neither mapping is inferred from the existing numbers. This allocation buys calibration and background separation at the cost of having one biological sample per arm and one standard level. It is a diagnostic pilot, not a replication or nonlinear calibration study.

## Checkpoint — combine A3 with B3

Parents A3, B3. Freeze synthetic predictions in predictions.json; then run evaluator.py. The construction should distinguish synthetic production-only and gain-only twofold sample signals; it should expose cancellation and an uncertainty-limited case. A matrix-mismatch witness must remain a failure of transfer: the same equations can return a spurious production change. No synthetic success determines whether the reagent changes production in the supplied scenario.

## Remaining empirical obligations

No new measurements exist. Verify availability and validity of the matched blank and same-analyte standard before using this allocation. One standard level does not test linearity; old three-dose linear-looking means do not validate instrument linearity. A calibration standard can itself be chemically changed by reagent; matching timing/species and validating stability are necessary. A measured amount at one endpoint is not automatically a production *rate* or per-cell synthesis: degradation, secretion, recovery, cell number, and viability remain possible distinctions. Six wells do not estimate biological variance or establish a reproducible causal population effect. Randomized allocation can reduce placement/handling bias but cannot provide replication that is absent.

No unexposed empirical validation set exists. The synthetic cases are development checks written and evaluated by the same worker. Method superiority is not tested.
