# Navier–Stokes comparison, inspected 2026-09-28

Scope: comparison of published architecture and reported process, not an
independent verification or reproduction of OpenAI's result.

## Primary evidence

The [paper](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf)
claims forced blowup from rest with bounded energy and smooth compactly supported
forcing: Theorem 1.1 and Corollary 10.6 address alternatives C/D. Its construction
turns a residual into annular stress supplied by oscillatory corrections;
geometry, auxiliary coordinates and subsequent corrections support that design
(§§2–3, especially Figures 5–6). The finished proof does not reveal the order in
which these ideas were discovered.

The [research account](https://openai.com/index/navier-stokes-solution/)
reports separate problem variants, an Euler stepping stone, sharing intermediate
results across groups, resource reallocation, and later formalization. It does
not document image cues, semantic-distance sampling, or our proposed operators
as causes of the outcome.

The [formalization metadata](https://github.com/openai/NavierStokesAndEuler/blob/main/formalization.yaml)
declares theorem mappings and zero sorry counts, with review status self-assessed.
[Comparator instructions](https://github.com/openai/NavierStokesAndEuler/blob/main/ComparatorChallenges/README.md)
provide a separate checking path. Neither build nor comparator was run here.

## Assessment of this repository

Before this revision, SKILL.md already supported continuity, delayed grounding,
scoped memory and concrete tests. The missing instruction was to make generated
objects control the next operation, including changes to the representation.

| Capability | Revised instructions | Runnable support here |
|---|---|---|
| Preserve distinct formulations and routes | Explicit target and variant record | Host agents and project artifacts |
| Develop auxiliary problems | Keep a transfer obligation to the target | Host reasoning/code; no automatic transfer prover |
| Turn an obstruction into a new object | Construction operators and residual recomputation | Host tools; domain implementation still required |
| Let artifacts drive continuation | Parent-linked branch state and next operation | Archive helper preserves records and artifact hashes; host chooses operations |
| Exchange intermediate results | Checkpoints carrying definitions and assumptions | Archive packets and available agent messaging; no bundled scheduler |
| Return to an exact target | Statement correspondence and verification status | Depends on available domain checker or experiment |

The revision strengthens a research protocol. It does not grant this model the
capabilities, compute, or theorem-proving success of another research system.
The semantic sampler and viewer remain an optional perturbation experiment.

## Consequence for the design

Treat an incomplete construction as a state that can be extended. Preserve its
obstruction, build the object suggested by that obstruction, and recompute what
remains. Exchange such artifacts while distinct routes continue. The claimed
result must still refer to the exact original problem or clearly state the
restriction. This is our proposed reusable instruction, not a reconstruction of
undisclosed agent conversations.

## Small forward test of the revised instructions

A worker received the revised skill and a synthetic universal fourth-moment
conjecture supported by low-dimensional examples, without a proposed solution.
It introduced an elementary symmetric interaction term, derived an exact identity,
and combined it with a constraint-preserving family yielding a counterexample.
The record separates symbolic proof from finite rational checks:
[trajectory and mathematical result](../experiments/research-trajectories/moment-inequality/trajectory.md).
The checks were rerun successfully. This exercises artifact continuation and
complementary routes on an elementary case; it establishes neither advanced
research ability nor an advantage over ordinary mathematical reasoning.
