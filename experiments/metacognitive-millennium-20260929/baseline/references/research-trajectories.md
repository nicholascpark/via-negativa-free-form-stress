# Developing and exchanging research objects

Use this reference for sustained scientific or engineering exploration. It is
a host-executed protocol: this repository does not supply an autonomous theorem
prover or an artifact-aware scheduler. Available agents, code tools and project
records can perform the operations without a new orchestration service.

## Branch state

Use the project's existing notebook or artifact format. A compact record is enough:

```yaml
id: branch-a-step-2
parents: [branch-a-step-1]
target: versioned working question and user commitments, with source
route: original / equivalent / auxiliary / changed-objective
representation: defined objects, equations, code or rendered geometry
transformation: operation applied to the parent artifact
kind: exact / proposed-refinement / lossy-abstraction / counterfactual
assumptions: assumptions used here, separately from target requirements
artifacts: paths and versions of definitions, code, diagrams or derivations
observations: what was actually computed, inspected or measured
obstruction: exact residual, failure, counterexample or unresolved step
return_obligation: what connects this state to the original target
evidence: claims with kind, source, scope and conditions
next: the operation or question now made possible
```

Use field values that describe the actual work; the example is a format, not a
required ceremony. External definitions and derivations are useful artifacts;
an exhaustive private reasoning transcript is unnecessary.

Evidence kinds describe what happened, not a ladder every domain must climb.
Label a simulation as simulated, a measurement as measured, and a proposed
intervention as proposed. Record versions of both the artifact and measurement
definition. A changed empirical question can be productive; an altered theorem
does not establish the original statement. See [domains](domains.md).

## Operators with consequences

An operator should change what subsequent work can do. Examples:

| Obstruction | Constructive operation | Artifact to carry forward |
|---|---|---|
| A scalar summary hides an interaction | Add an interaction observable | Definition and evolution equation, with unclosed terms |
| Several mechanisms fit the same observations | Find a measurement or intervention where predictions separate | Rival predictions, measurement definition and detectability conditions |
| An update fixes one constraint and breaks another | Jointly design the update and its surrounding state | Coupled equations or an executable constrained update |
| A representation merges behaviorally different cases | Exhibit the two cases and add a distinguishing variable | Counterexample pair and a revised representation |
| Direct search has too many equivalent arrangements | Change coordinates or quotient a proved symmetry | Transformation and its preservation argument |
| The full problem obscures a mechanism | Explore a restricted or limiting problem | A result plus explicit transfer conditions |
| Repeated work needs the same nontrivial construction | Implement a reusable operation | Signature, definition/code, assumptions and known failures |

The branch may also try unfamiliar metaphors or counterfactual worlds. Preserve
the original artifact so invented behavior is never mistaken for an equivalence.
When a picture suggests a relation, define the relation before another branch
uses it as a mathematical or engineering object.

## A productive failed correction

Suppose a candidate artifact a violates a condition, expressed as a residual R(a).
An exploratory branch proposes a correction delta. Compute or derive

    R(a + delta)

including interactions and changes to other required conditions. For nonlinear
R, assuming R(a + delta) = R(a) + R(delta) silently loses the important terms.
If one error disappears but another appears, record the new error explicitly.
It may suggest a coupled update, a new variable, or a different representation.

This schematic is a research move, not a claim that every problem admits a
convergent correction scheme. Each problem determines its update operation,
notion of error, invariants, and limiting obligations.
An unexplained observation or an indistinguishable pair of mechanisms may be
the obstacle; it need not reduce to a scalar residual.

## Exchange partial results

A checkpoint should transmit a usable artifact, not a popularity vote:

1. What object or operation now exists?
2. Under which assumptions is it defined or justified?
3. Which obstruction did it remove, and what remains?
4. What concrete operation could another branch now perform?

For example, send a proved special-case identity to a construction branch and
a family defeating its proposed generalization to a branch revising variables.
Or send an identifiable parameter combination to an experiment-design branch,
which can construct measurements that separate the remaining possibilities.
Keep hypotheses labeled when shared. Similar terminology across branches does
not establish compatible definitions or assumptions.

Allocate remaining resources using actual opportunities and unresolved tasks.
The budget must include combination and verification work. Preserve enough
separation for alternative routes to develop; do not distribute every speculative
message to every worker. Record which information a recipient saw.

## Benchmarks grow from obligations

Generate tests from the proposed construction and its failure conditions. These
can include witness searches, limiting regimes, conservation checks, coupled
effects, boundary cases, or comparisons between old and new behavior. Record
the source of each expected result. A test generator does not supply missing truth.

A special-case result may be useful while its generalization fails. Preserve
both the result and the failed transfer. Finite samples cannot discharge a
universal quantifier. Computational evidence can guide an analytic proof while
remaining an observation. Formal verification needs correspondence between the
encoded statement and the intended target, not just a successful build command.

Exploration can continue while obligations remain unresolved. Their existence
does not demand an immediate human approval or terminate the branch. Promotion
to a claimed solution requires the evidence appropriate to the domain and claim.

## Human judgment and reusable memory

Ask when an answer changes a research choice, supplies missing observations,
or selects a purpose. Examples: whether a restricted theorem would serve an
application, whether an observed discrepancy reflects a measurement artifact,
or which operating assumptions the engineering system can actually support.
Do not ask the user to vote a mathematical identity true.

Save reusable operations with their input/output types, definitions, assumptions,
evidence and counterexamples. Retain exploratory versions too. A later branch
can transform one instead of treating past failure as permanent prohibition.
This grows a working library in project memory; it does not train model weights.

## Optional archive helper

Use an existing project notebook when it already handles provenance and versions.
For a small shared file archive, [research_archive.py](../scripts/research_archive.py)
uses Python 3.10+ and the standard library. It stores an immutable brief and
parent-linked records, then assembles a selected record with its ancestry for
another agent. It neither launches workers nor verifies their research claims.

Prepare a brief JSON file:

```json
{
  "id": "thermal-model-v1",
  "objective": "Explain unexpected ringing in a thermal calculation",
  "constraints": ["Keep the stated physical model identifiable"],
  "domain": "numerical",
  "source": "User task; illustrative example"
}
```

Initialize an archive in the project, then put the actual artifacts under that
archive directory. Prepare each node as JSON, for example:

```json
{
  "id": "spectrum-1",
  "target_id": "thermal-model-v1",
  "parents": [],
  "representation": "Discrete spatial modes and their time-step amplification",
  "operation": "Express the existing update in a mode basis",
  "artifacts": [{"path": "artifacts/modes.py", "description": "Candidate mode calculation"}],
  "assumptions": ["Periodic uniform grid; update matches the supplied implementation"],
  "obstruction": "Observed growth is not yet attributed to model or discretization",
  "return_obligation": "Compare mode predictions against the original update",
  "evidence": [{"kind": "proposed", "claim": "Mode growth could distinguish causes", "source": "This branch"}],
  "next": "Run the comparison across grid and time-step settings"
}
```

The artifact path in this example must refer to a real file before adding the
node. From the skill directory, with paths adjusted to the working project:

```sh
python3 scripts/research_archive.py init /path/to/project/exploration --brief brief.json
python3 scripts/research_archive.py add /path/to/project/exploration --node node.json
python3 scripts/research_archive.py packet /path/to/project/exploration --ids spectrum-1
```

Required fields are shown above. `parents`, `artifacts`, `assumptions`, and
`evidence` may be empty arrays; `obstruction` and `return_obligation` may be empty
strings. Other strings must be nonempty. Evidence kinds are `proposed`, `observed`,
`bounded-check`, `proved`, or `refuted`; describe simulated/measured context and
scope in the claim, source, or additional metadata. Labels remain the author's
assertions. Additional metadata is preserved: for example `worker`,
`context_exposure`, `question`, `measurement_version`, or `supersedes`.

IDs contain letters, digits, underscores, or hyphens. Parents must already exist
and the target must match the brief. Records are published atomically without
overwriting, including when several writers choose the same ID. Give each worker
distinct IDs. Add a new node to revise a claim; use a new brief/archive for a
changed objective and record the connection to the old one.

Artifact paths must stay under the archive root. Keep versioned artifact copies
there; record hashes identify content, but the helper does not make file contents
immutable. `add` computes each artifact's `sha256` and rejects a supplied hash
that differs. Packets contain `brief`, `selected_ids`, parent-first `nodes`, and
`artifact_integrity`. Each integrity entry names the node and path, recorded and
current SHA-256, and a status: `unchanged`, `changed`, `missing`, or `unreadable`.
Missing/unreadable entries have a null current hash; unreadable entries also
include the error. Hashing reads bytes but packets contain no artifact contents.
A changed or missing artifact needs its recorded version recovered or a new
node. Checkpoint packets can be passed through available agent messaging without
copying the whole conversation.
