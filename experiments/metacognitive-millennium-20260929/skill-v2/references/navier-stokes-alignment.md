# Navier–Stokes comparison, revisited 2026-09-29

Scope: selected statement, construction and process review, not an independent
verification of the 166-page proof. Inspected Theorem 1.1, the physical account
in §2, the residual formulation opening §3, and formalization metadata. Neither
the Lean build nor comparator was run. The previous local trial remains historical.

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

The [official statement](https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf),
pp. 1–2, permits existentially chosen smooth forcing in C/D, whereas A/B require
zero forcing. C/D are not the logical negations of A/B with identical hypotheses.
The claimed forced construction does not decide unforced global regularity.
On [11 September 2026](https://www.claymath.org/news/navier-stokes-announcement/),
Clay described the problem as apparently settled and said evaluation and credit
assignment would take time. OpenAI's account says it does not intend to claim the
prize. These sources establish a public claimed resolution and a Clay response;
they do not establish a private submission's contents or final prize adjudication.

## What “minimal assumptions” means in this comparison

Our interpretation of the available degrees of freedom, not a claim about the
agents' discovery chronology:

| Requirement or choice | Classification | Consequence for exploration |
|---|---|---|
| Three dimensions, positive viscosity, incompressibility | Target requirements | Preserve on the Navier–Stokes route |
| Smoothness/decay of data and force in the chosen alternative | Target requirements | Defining a force by residual does not discharge these |
| A prescribed specific force versus existential choice of admissible force | Depends on the statement | Read the quantifier before deciding what must be fixed |
| Rest initial data, compact support, a particular ansatz | Construction choices compatible with the claim | Useful sufficient choices; not globally minimal hypotheses |
| Symmetry, scale relations, decomposition | Representation choices | Vary provisionally; recheck the actual conditions |
| Zero viscosity | Different equation | An auxiliary route needs a transfer argument |

The reusable lesson is to separate restrictions introduced by the researcher
from those imposed by the statement. It is not permission to delete inconvenient
hypotheses or to assume the cancellation one hopes to prove.

## A concrete operator extracted for the skill

For the defined momentum residual

```text
Rν(u,p) = ∂t u + (u·∇)u − νΔu + ∇p,
```

direct algebra, for smooth fields where the expressions are defined, gives

```text
Rν(u+w,p+q) = Rν(u,p) + ∂t w − νΔw + ∇q
              + (u·∇)w + (w·∇)u + (w·∇)w.
```

This identity is a small checkable mathematical extraction, not a blowup proof.
It tells a branch what to carry forward after introducing a correction: the two
mixed transport terms, the quadratic term, and all admissibility conditions.
An intended cancellation has to survive those new terms. If divergence-free
motion is required, the correction must preserve it too. Smoothness of a
residual for every time below the singular time does not imply extension through
that time with all required derivatives.

The upgraded [metacognitive protocol](metacognitive-exploration.md) generalizes
this as: identify the obstruction, construct an object that can act on it,
compute the coupled remainder, and revise the next operation from that remainder.
Other problems need their own objects and checks, not a fluid analogy imposed on
them. The [three-role protocol](fresh-context-trials.md) tests whether these
instructions change observable work, without attributing the paper's success to
our skill.

## Assessment retained from the 2026-09-28 revision

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
