# Continuing research objects

These concise records describe external constructions and their dependencies, not a private reasoning transcript. They were written before executing the fixtures.

## Route A — a profile becomes a signed spectrum

- A1, parent brief/question-v1: replace a single smooth-looking profile or peak summary with the discrete basis exp(2 pi i k j/N). Exact invertible coordinate change on N periodic samples. No physical resonance is introduced.
- A2, parent A1: diagonalize the central-difference/forward-Euler update. Each basis coefficient evolves by g_k=1-4r sin²(pi k/N), with r=alpha dt/dx². This converts an unexplained shape into mode-specific, falsifiable one-step predictions.
- A3, parent A2: isolate the signed checkerboard coefficient a_alt=(1/N) sum_j (-1)^j u_j for even N; distinguish sign reversal from increasing magnitude. Carry this measurement into every saved trace. The supplied perturbation gives an observable known initial seed rather than relying on incidental roundoff.
- Return: the r value and mode gain can be checked against a direct stencil implementation. Remaining obligation: how the original team code handles endpoints, units, and updates is unknown.

## Route B — the update becomes a transfer operation

- B1, parent brief/question-v1: rewrite the same stencil as u_new_j = r*u_left + (1-2r)*u_j + r*u_right. Exact local transfer representation; row sums are one.
- B2, parent B1: require nonnegative transfer weights, obtaining 0<=r<=1/2. This yields a discrete maximum principle, conservation of the periodic mean, and an impulse witness when the central weight becomes negative. This is independent of inspecting a plotted smooth wave.
- B3, parent B2 plus A2 exchange: construct a reusable advance_output function that splits a requested output interval into ceil(alpha*output_dt/(0.4*dx²)) equal steps. It preserves the requested output cadence while making the actual numerical step explicit. The 0.4 value is a chosen safety margin, not an optimized accuracy tolerance.
- B4, parent B3: expose the coupled cost and accuracy obligations. At N=80, output_dt=0.1 requires 16 internal steps. At fixed r, doubling N quadruples step count per physical duration and multiplies 1D cell updates by eight. Verify continuum accuracy separately from mere boundedness.
- Return: executable safe-step prototype and reporting policy, plus a cost/accuracy decision. Physical validity remains open.

## Route C — a candidate smoother develops a counterexample family

- C1, parent A3: proposed refinement (not an equivalent discretization): append nearest-neighbor averaging with weights 1/4,1/2,1/4 to each original Euler macro step. It removes the visible checkerboard, making it an initially plausible diagnostic correction.
- C2, parent C1 plus A2 exchange: compose the operators before judging the repair. The filter gain is 1-sin²(pi k/N), so the combined gain is [1-4r q]*(1-q), q=sin²(pi k/N). This alters low-frequency diffusion as well as high frequencies.
- C3, parent C2: generate a failure witness from the coupled gain, not from the original benchmark: k=N/4 gives q=1/2 and gain -5.9 for N=80, dt=0.1. Extend the input with a 0.001 sine at that frequency. The original checkerboard test alone would reward the wrong correction.
- Return: keep the failed smoother and witness as regression material. Its failure does not falsify all filters; a different method needs its own consistency, stability, and accuracy analysis.

## Reconnection

A's mode measurement checks B's bounded step operator. C challenges the temptation to certify a correction on the failure that inspired it. Save direct-stencil outputs, mode gains, mean, energy, maximum, continuum errors, and cell-update counts. Expected values come from the declared equations; they are not thermal measurements.

All cases are development checks generated from these artifacts. They do not independently establish that the skill is better than an ordinary numerical-analysis workflow. Any new material term would require separately sourced physical observations and an identified model discrepancy after numerical controls.
