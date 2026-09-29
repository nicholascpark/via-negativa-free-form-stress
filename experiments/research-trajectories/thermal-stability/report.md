# Thermal-model forward exercise: runnable result

Retained from an isolated worker exercise. The script was then rerun from this
repository; `results.json` contains that latest execution. The original worker's
scope and observations below are preserved.

Build a resolution-aware stepping guard and modal diagnostics next. The stated numerical update already produces the reported type of growing ringing. These synthetic results give no evidential reason to add a material resonance term now; they do not prove that real material resonance is absent.

## Scope and evidence

This was a synthetic task supplied for a skill capability exercise. The user described a periodic length-one heat equation with alpha=0.01, central differences, forward Euler, dt=0.10, and differing behavior at N=20 and N=80. No original solver, physical measurements, material units, accuracy tolerance, or human response was provided. I used N unique periodic points x_j=j/N and the supplied possible initial condition. All observations below are outputs of the standard-library Python fixture.

The work stayed in this directory. No network, paid tools, external packages, repository modifications, or physical experiments were used. This is not a comparison against ordinary prompting and does not establish the skill's superiority.

## Representation carried into code

The first transformation replaces a smooth-looking temperature profile with signed spatial-mode coefficients. Let dx=1/N and r=alpha*dt/dx². The exact gain of sampled mode k under the stated update is

    g_k = 1 - 4 r sin²(pi k/N).

For even N, the alternating pattern (-1)^j is mode N/2. Its directly measured coefficient is

    a_alt = (1/N) sum_j (-1)^j u_j,

and its one-step gain is 1-4r. Sign reversal and growing magnitude are now separate observables. The script applies the local stencil directly and measures the coefficients; it does not simulate by multiplying only the predicted coefficient.

A second, exactly equivalent representation writes an update as the local transfer

    u_new_j = r u_left + (1-2r) u_j + r u_right.

The weights sum to one. For 0<=r<=1/2 they are nonnegative, so values stay within the old range, and periodic summation preserves the mean. The Fourier representation shows that r<=1/2 is also the sharp all-mode magnitude-stability threshold for these even grids. At equality the checkerboard reverses sign without decaying, so strict damping needs a margin.

## Actual outcomes

| Run | r per internal step | Perturbation result at t=1 |
|---|---:|---:|
| N=20, original dt=0.10 | 0.4 | checkerboard amplitude 6.0466176e-6 |
| N=80, original dt=0.10 | 6.4 | checkerboard amplitude 8.1161688e10 |
| N=80, 16 substeps per output interval | 0.4 | checkerboard amplitude 2.47e-18, at roundoff scale |

The measured one-step checkerboard gains were -0.5999999999999913 and -24.599999999999987, matching the independently stated modal formulas. At N=80, after only three original steps, the alternating amplitude was -14.886935999999958; the frozen prediction was -14.886936. The smooth low-frequency mode can decay while an initially tiny high-frequency component grows. A smooth appearance therefore does not certify stability.

For N=80, the threshold is dt<=0.0078125. The prototype uses r<=0.4, making dt_internal=0.00625. `advance_output` computes a sufficient integer subdivision while preserving an output interval of 0.10. It does not introduce new physics.

### A correction that failed and yielded a new check

The exploratory filter appended weights (1/4,1/2,1/4) after each original Euler step. It removed the checkerboard in one step, passing the visible-failure test. Composing its multiplier with Euler exposed a new obligation:

    G(q) = (1-4r q)(1-q), q=sin²(pi k/N).

At k=N/4 and r=6.4, G=-5.9. A generated 0.001 perturbation at that mode grew to 51111.675330065045 by t=1. This is a concrete regression witness against adopting that particular smoother. It also changed the smooth amplitude to 0.6583607392, illustrating a coupled low-frequency effect. Other filters remain separate, untested proposals.

## Checks created from the artifacts

All 15 development checks passed, including the checks whose expected result was failure of an unsafe candidate. Each record in `results.json` stores inputs, expected result and source, observation, artifact version, and pass status. The covered obligations were:

- Direct-stencil one-step modal gains and three-step growth.
- Nonincreasing mean-square for the two stable runs.
- The filter's eliminated checkerboard and its new N/4 failure witness.
- The stability boundary at r=0.499, 0.500, and 0.501.
- Constant preservation, periodic mean preservation, and range bounds on an odd grid with a seed-42 fixture.
- A nonnegative impulse at r=0.4, and its negative center -0.2 at r=0.6.
- Continuum accuracy under coupled space/time refinement.

For that last check, I used only sin(2*pi*x), whose exact PDE solution is exp(-4*pi²*alpha*t) sin(2*pi*x). The supplied checkerboard changes its physical wavelength with N and is unsuitable as a common smooth continuum convergence fixture.

| N | dt | RMS error at t=1 | Cell updates |
|---:|---:|---:|---:|
| 20 | 0.1000000 | 0.002203473670 | 200 |
| 40 | 0.0250000 | 0.000543787805 | 1,600 |
| 80 | 0.0062500 | 0.000135512819 | 12,800 |
| 160 | 0.0015625 | 0.000033851200 | 102,400 |

Successive error ratios were 4.0521, 4.0128, and 4.0032. This supports the predicted second-order combined refinement behavior on the exercised smooth solution. It is not an application accuracy certification. At fixed r and time horizon, doubling N multiplies 1D cell updates by eight; the safer step has a concrete computational cost.

## Next build and remaining decision

1. Port the explicit step guard and report N, dx, alpha, requested output interval, actual internal dt, and r. Preserve periodic simultaneous updates.
2. Add the checkerboard and N/4 regression witnesses, plus mean and modal-energy diagnostics. Retain the continuum reference check.
3. Choose numerical resolution from an actual accuracy requirement, not from a stable plot. If explicit substep cost is unacceptable, compare an implicit or other justified integrator against the same modal and continuum checks before adoption.
4. Consider new material dynamics only if a discrepancy remains after numerical controls and is supported by independent physical observations.

Proposed consequential question, recorded only and not asked in this fixture: **Is 0.10 merely the required output interval, or must the application perform only one solver update per 0.10, and what temperature error is acceptable over the intended time horizon?** If it is output cadence, the current substep construction is directly usable. If the computation budget forbids it, the next construction is a different integrator with a cost/accuracy comparison. If the intended accuracy is tighter than the table supports, refine or change the approximation even though it is stable. No answer has been supplied or assumed.

The original implementation may differ in endpoint handling, units, or in-place updates; this fixture cannot certify it. Mean preservation does not guarantee stability, small modal coefficients lose relative precision once a growing mode dominates, and missing physical data remains missing. No production change was made.

## Reproduce and continue

    python3 experiments/research-trajectories/thermal-stability/thermal_lab.py

The script regenerates `results.json` and `traces.csv`. `predictions.json` was written before the first simulation and its SHA-256 is recorded in the results. `brief.md` retains the supplied task and assumptions; `trajectories.md` records the three continuing routes and exchanged constructions. The original worker's duplicate console log is omitted from this retained fixture.

Original worker resource use: two complete simulation runs. Reported script wall times were approximately 0.01395 and 0.04053 seconds, excluding agent reasoning, file editing, tool overhead, and output serialization. Each run counted 132,686 Euler cell updates and 1,600 filtering cell updates. The second run corrected only a check-report mismatch between constant value and maximum error; the simulated method did not change. The subsequent repository rerun passed all 15 checks; its timing is in `results.json`. No dollar cost or peak-memory measurement was collected.
