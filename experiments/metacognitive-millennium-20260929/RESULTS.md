# Metacognitive skill upgrade and Millennium-problem trial

Completed 2026-09-29. The active [skill](../../SKILL.md) now has explicit assumption
revision, bounded generative intervals, and checks that turn a candidate insight
into an operation with stated transfer obligations. A three-role P-versus-NP
episode and a fresh-context continuation exercised those instructions. Neither
episode solved P versus NP, established novel mathematics, or demonstrated that
the skill outperforms ordinary expert prompting.

## What changed

| Version | Change | Basis and observed result |
|---|---|---|
| Baseline → v1 | Separate target requirements, definitions, established dependencies, working hypotheses and representational habits; record consequential deltas; bound generative intervals; inspect circularity and transfer; define observer-only trials | Source review and initial read-only assessment motivated the changes. The practitioner produced precise objects, a failed-transfer witness and a continuation. No material proof or epistemic error was found by the observer. |
| v1 → v2 | At a checkpoint, state which decision the next operation informs, what would justify continuation, and what would redirect it | The simulated user wanted a clearer reason to pursue the next experiment. A fresh practitioner exercised the refinement and returned explicit stop/pursue criteria with an implemented algebraic operation. |

The [metacognitive reference](../../references/metacognitive-exploration.md)
operationalizes the user's “psychedelic revelation” metaphor as temporary freedom
to vary habitual assumptions and construct unfamiliar objects, followed by exact
reconnection. It does not claim subjective altered consciousness, access to
hidden cognition, erasure of model priors, globally weakest assumptions, or
automatic discovery. External research artifacts suffice.

The [three-role protocol](../../references/fresh-context-trials.md) keeps the
practitioner, simulated user and read-only observer distinct. A local cycle can
end with useful partial work and a specific next operation. “Perfected” would
overstate the evidence.

## Navier–Stokes source review

The [updated comparison](../../references/navier-stokes-alignment.md) reviews the
public claim, selected construction passages, official statement and formalization
metadata. The real user confirmed this was the recent OpenAI result they meant.
This was not an independent review of every step of the 166-page proof, a Lean
build, or a comparator run.

The crucial distinction is that the [official alternatives C/D](https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf)
allow existentially chosen admissible smooth forcing; A/B require zero forcing.
The [paper's claimed construction](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf)
uses forced blowup. It does not settle unforced global regularity. Clay's
[11 September announcement](https://www.claymath.org/news/navier-stokes-announcement/)
described the problem as apparently settled while retaining its evaluation
process. We did not establish the contents of any private submission or a final
prize adjudication.

Our transferable interpretation is to distinguish genuinely available degrees of
freedom from restrictions introduced by a chosen representation. A directly
derived residual expansion makes a second lesson concrete: a correction creates
mixed and quadratic terms, which must be carried forward rather than silently
dropped. The [source record](source-review.json) separates inspected evidence from
unperformed verification and inferred design lessons. Published proof architecture
does not reveal hidden discovery chronology or establish this skill's efficacy.

## Trial 1: P versus NP

Three freshly spawned roles used no inherited parent conversation. The
practitioner received frozen v1, the simulated request and primary sources. The
simulated user selected the local-information route, then challenged its relevance
to unrestricted computation. The observer inspected artifacts only after the
episode froze and never executed experiments, edited files or coached participants.

The [reader report](REPORT-v1-corrected.md) gives an exact threshold for when all
k-coordinate violation marginals of two affine Boolean systems agree. It develops
connected graph examples into sparse CNF, explicitly refutes an overstrong
individual-clause transfer, derives a global algebraic repair, and extends the
same machinery by signed inclusion-exclusion to ordinary clauses.

The important diagnostic result is that high interaction order need not mean
high runtime: the global parity information missed by the summaries is cheap to
compute. The work rejects its own unrestricted lower-bound inference. Its
mathematics is presented as familiar algebra and a local synthesis, not novelty.

The [observer audit](audit/v1.md) found no material proof or epistemic failure and
recommended retaining v1, with one small clause-wording clarification. It did
**not** recommend another general rule or a replay. Separately, the
[simulated user feedback](relay/user-feedback-v1.md) identified an unmet explanation
need: what outcome would justify more effort on the proposed continuation?
That feedback motivated the small v2 usability refinement. This distinction is
preserved in the [revision log](revision-log.md).

## Continuation: useful forgetting with algebra preserved

A new practitioner received frozen v2, the previous report as an explicit input,
and the simulated follow-up. This is a fresh-context, feedback-exposed continuation
on the same problem, not an independent replication.

The [continuation report](REPORT-v2-corrected.md) proves that canonical equality
merging retains 2^q affine states on the easy connected family
S_q = AND_i(s OR x_i), which has 2^q+1 satisfying assignments. Original/global
component splitting cannot split this family; conditional factoring is a
different operation and is not ruled out.

The worker then derives and implements weighted affine projection: sum variables
that no remaining clause can inspect, retain their induced linear constraints,
and account for their constant affine fiber multiplicity. At q=8 the unprojected
dictionary has 256 states, while the projected one peaks at two and returns the
same count, 257. A converse example prevents overgeneralization: a raw boundary
table expands exponentially on a single parity equation, whereas affine
projection keeps one state. The combined operation handles both exhibited defects.

The report stops the unchanged merging experiment, preserves the projection
operator, and proposes testing how affine information passes between clause
blocks. Any general advance still needs a noncircular, constructible bound on
state growth and updates. Failure of an exact-counting representation does not
settle the weaker decision problem.

The [second observer audit](audit/v2.md) found the arguments sound by inspection
and the decision criteria responsive to the feedback. It requested two reader-copy
clarifications, which were applied without modifying frozen artifacts. The
[simulated user](relay/user-feedback-v2.md) reported no consequential clarification
remaining for this bounded episode. That is role-play usefulness feedback, not
real-user endorsement or proof certification.

## Verification and reproducibility

- Trial 1's recorded outputs reproduced: 73,728 threshold comparisons on 512
  binary 3×3 matrices, graph/encoding checks, and 9,216 affine-plus-clause cases.
- The coordinator separately implemented 22,023 threshold comparisons and 4,108
  exact partition evaluations on 146 small rectangular/degenerate matrices.
- The continuation's outputs reproduced on all 915 generic fixtures and its
  star, disjoint-clause and parity families. Only measured elapsed time differed.
- Skill structural validation passed; all 13 checked active local reference links
  resolved; active instruction files matched the frozen v2 manifest.

See [v1 checks](coordinator/verification-summary.json),
[v2 checks](coordinator/v2-verification.json), and
[skill checks](coordinator/skill-checks.json). These are development checks and
reruns, not hidden holdouts or formal certification. The observer did not execute
them. No proof assistant ran.

For reproduction, copy [frozen-v1](frozen-v1/REPORT.md) to a scratch directory and
run `python3 checks.py` and `python3 continuation_checks.py` there. For the next
episode, copy [frozen-v2](frozen-v2/REPORT.md) and run `python3 checks.py` in the copy.
The scripts write outputs, so running in a copy preserves the delivered hashes.
The separate checker is [independent_checks.py](coordinator/independent_checks.py).

The [protocol](protocol.json), [context exposure record](contexts.json),
[interaction record](TRANSCRIPT.md), frozen skill versions and manifests preserve
the run. Separation was instructed in a shared filesystem, not enforced by an
isolated sandbox. A fresh conversation does not remove shared model priors.
The initial v2 prediction was captured before implementation files were visible;
later internal chronology is not independently attested. Token and monetary costs
were not measured. No claim of causal skill benefit is justified without repeated
independent problems and matched ordinary-prompt baselines.
