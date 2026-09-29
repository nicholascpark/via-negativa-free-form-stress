# Via Negativa Exploration

**What could we construct that makes the next step possible?**

This skill develops representations, constructions and reusable operations for
hard scientific and engineering problems. Continuing branches can turn an
obstruction into a new object, explore auxiliary problems, and exchange partial
results before reconnecting to the scientific or engineering purpose. Words,
images and seeded semantic walks remain available as exploratory inputs.

The active instructions are in [SKILL.md](SKILL.md), with operational detail in
[research trajectories](references/research-trajectories.md). [Domain guidance](references/domains.md)
distinguishes mathematical proofs, empirical and inverse problems, numerical
models, software and distributed systems, and physical design/control/VLA. The
[Navier–Stokes comparison](references/navier-stokes-alignment.md) distinguishes
published research evidence, instructions we can adopt, and capabilities still
dependent on the host and domain tools. This is an experimental research protocol.

## Use the skill

The skill is named `via-negativa-exploration`. This repository retains its
historical `via-negativa-stress-test` name. It is separate from the older
`via-negativa-free-form-stress` skill.

Point the agent at this repository's `SKILL.md` and give it the actual problem,
current artifacts, and any resource constraints. For example:

> Use via-negativa-exploration on this obstruction. Let distinct branches develop new
> representations through several transformations. Exchange intermediate
> artifacts, generate checks from what they reveal, and return something we
> can use in the next experiment, proof, or build.

The core is the same across domains: preserve observations and commitments,
develop an object that changes the next available operation, carry it forward,
and reconnect with appropriate evidence. An experiment proposal, a new variable,
a counterexample, or a revised controller can each be a useful return.

The agent can ask concrete questions when answers would change a consequential
choice. Scoped memory keeps definitions, assumptions, human answers, failures,
and the next operation. The optional [archive helper](scripts/research_archive.py)
provides parent-linked records and exchange packets; its schema and commands
are in [research trajectories](references/research-trajectories.md).

The skill does not require embeddings, multiple agents, or a proof assistant.
Those tools expand the available operations when the host provides them. No
global installation or model training is performed by the files in this repository.

## What the questions sound like

They are short questions about a real choice in the work. For example:

- “Are these readings from separate fault sources, or two views of the same one?”
  The answer determines whether the build tracks one fault or two.
- “Can this counter restart, or does a smaller number always mean an older reading?”
  The answer determines whether a record can safely be ignored.
- “What tells you a fault has ended?”
  The answer determines when the next fault should create a new alert.

The agent records what each answer would change before asking. It asks about
the uncertain rule first, then shows a concrete comparison if a choice remains.
It keeps real user answers, simulated replies, and its own hypotheses distinct.

## Inspect the working prototype

The runnable prototype below exercises the optional cue sampler. The broader
research protocol is executed by the host agent using project artifacts and
available tools; this repository does not bundle an autonomous research scheduler.

[The semantic exploration viewer](examples/semantic-exploration/index.html) shows
18 text cues and two photographs embedded by one pinned TinyCLIP checkpoint.
It includes actual 512-dimensional distances, a clearly approximate PCA map,
and three seeded runs of three short cue paths. Image embeddings come from pixels.
The tiny curated pool demonstrates mechanics, not broad conceptual coverage.

Serve the directory from the repository root:

```sh
python3 -m http.server 8787 --bind 127.0.0.1 --directory examples/semantic-exploration
```

Then open `http://127.0.0.1:8787`. Cached data needs no model or API.
Sample a new run or exercise the finite relational example:

```sh
python3 scripts/semantic_walk.py examples/semantic-exploration/input.json \
  --seed 7 --walks 3 --hops 3 --output /tmp/semantic-walk.json
python3 experiments/semantic-walk/bridge_example.py
python3 experiments/semantic-walk/test_sampler.py
```

The sampler records modality, distance band, operator, selection probability,
parent, objective distance and input hash. It selects cues; the host agent still
has to inspect them, continue an interpretation, and build a defensible bridge.
The prototype is not an autonomous LLM orchestration service.

An [actual worker trial](examples/semantic-exploration/path-trial.json) follows
flower → pavilion → germination, records three external sketches, and proposes
a bounded request-coalescing experiment. It inspected both images. The experiment
has not run; this is a candidate with stated unknowns, not a measured improvement.

The finite bridge example searches eight request-sharing predicates and generates
cases where candidate builds disagree. Its fictional contract supplies expected
behavior. It checks bounded identity relations, not actual latency or a discovery
caused by the cue walk. Freshness and execution effects remain pending.

Read [semantic exploration](references/semantic-exploration.md) for the exact
sampling rule, regeneration instructions, bridge example, cost model and proposed
evaluation. The encoder checkpoint is external and is not bundled here. The photo
licence and original credits are in [the retained attribution](examples/semantic-exploration/images/README.txt).

## The human comparison stage

The earlier [rehearsal comparison](examples/rehearsal/index.html) lets a speaker
try a manuscript and three cues. That encounter might support keeping a
teleprompter or building a rehearsal editor instead. No such user outcome has
been measured. It illustrates downstream interaction, not stochastic search.

The [decision card](references/decision-card.md) records how answers change a
pending decision before asking. The [questioning protocol](experiments/runtime-questioning/protocol.md)
tests that separate component. A local benchmark guides a build; evaluating the
skill requires independent tasks and equal-budget comparisons, including strong
ordinary prompting. See [claims and theory](references/claims-and-theory.md).

Earlier Git investigation scripts and code/debugging/strategy/checklist references
remain optional legacy material. Their former layer terminology does not imply
proven access to unknown concepts.

## Development checks

The [cross-domain record](experiments/research-trajectories/validation.md) retains
a mathematical counterexample, an assay-identifiability experiment design, and
a thermal-simulation investigation. The latter two were exercised by separate
workers using the revised skill. Their generated checks and limits are preserved;
these small cases do not establish an advantage over ordinary prompting.

A later [interactive fresh-context trial](experiments/interactive-alerts-20260928/RESULTS.md)
used a practitioner, simulated user, and independent auditor. It preserves three
question/answer rounds, pre-answer candidate snapshots, withheld cases, and the
auditor's functional results and process criticisms. The skill remained frozen
throughout that trial.

The current instructions address its findings: avoid bundled policy-endorsement
questions, distinguish confirmation from changed behavior, and label simulated
speakers in standalone handoffs. The historical trial and its hashes remain
intact; its passing results describe the tested version.
The [corrected handoff](experiments/interactive-alerts-20260928/HANDOFF.md)
identifies the simulated technician explicitly.
A [focused post-fix exercise](experiments/interaction-question-fix-20260929/RESULTS.md)
produced an open question about recovery evidence and a clearly labeled simulated
handoff; its hypothetical policies remained unadopted pending an answer.

```sh
python3 experiments/research-trajectories/test_archive.py
python3 experiments/research-trajectories/assay-identifiability/evaluator.py
python3 experiments/research-trajectories/thermal-stability/thermal_lab.py
```

## License

Code: MIT. The two sample photographs retain their separate CC BY 2.0 attribution.


## Metacognitive assumption revision

The [2026-09-29 Millennium-problem trial](experiments/metacognitive-millennium-20260929/RESULTS.md)
records a Navier–Stokes assumption review, a fresh three-role P-versus-NP episode,
and a fresh-context continuation. The active skill now distinguishes target
requirements from representational habits, records consequential assumption
changes, and ties follow-up experiments to explicit continue/redirect decisions.
The mathematical artifacts and independent read-only audits are preserved.
These formative results do not establish a Millennium solution, novelty, or
superiority over ordinary mathematical prompting.
