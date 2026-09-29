# Context-retaining semantic exploration

This is the optional cue-sampling component. The main research protocol now
develops representations and exchanges generated artifacts; read
[research trajectories](research-trajectories.md) for that workflow. The code
and viewer below remain a bounded geometry demonstration and do not implement
an artifact-aware research scheduler.

The hypothesis: short continuing trajectories with stochastic cues and delayed
grounding yield more verified useful alternatives than equally expensive grounded
restarts and ordinary brainstorming. This is unproven. The prototype makes the
sampling and a bounded relational bridge inspectable.

## Runnable parts

`scripts/semantic_walk.py` is a standard-library cue sampler. It accepts actual
vectors, records selection probabilities, and emits paths. It does not run an
LLM, interpret images, execute proposals, or assess usefulness. The host following
SKILL.md supplies the continuing worker and bridge stages.

```sh
python3 scripts/semantic_walk.py examples/semantic-exploration/input.json \
  --seed 7 --walks 3 --hops 3 --output /tmp/semantic-walk.json
python3 experiments/semantic-walk/test_sampler.py
```

Serve `examples/semantic-exploration/` with a local HTTP server to inspect its
`index.html`. Cached vectors and three seeded runs require no model or API.
The 18 text cues and two photographs are a curated fixture, not a broad corpus
or an effectiveness benchmark. Two images cannot populate three distance bands;
the sampler explicitly omits empty bands.

The fixture uses [TinyCLIP](https://huggingface.co/wkcn/TinyCLIP-ViT-8M-16-Text-3M-YFCC15M),
revision `a2a8c6eaa2549ad66eb7c31b85022bf58273a26c`, with 512-dimensional joint
image/text projections. Image vectors come from pixels, not captions. Exact
texts, image and checkpoint hashes, and library versions are recorded. Original
photo credits and CC BY 2.0 licence are retained in `images/README.txt`.
The task is illustrative; no product or user improvement has been measured.

Regenerate using a local snapshot of that checkpoint:

```sh
python3 scripts/build_semantic_demo.py --model-path /path/to/local/snapshot
```

The optional builder needs PyTorch, transformers, NumPy, Pillow and scikit-learn
(for its sample photos). It downloads nothing and uploads no data. The sampler
needs none of those dependencies. CLIP-style encoders have short text limits;
use a disclosed compact task description for geometry while retaining full
evidence for the agent. The builder checks local files against recorded hashes
of the pinned demonstration checkpoint before encoding.

## Defined sampling

Let C be the finite corpus, g the objective text, E the pinned joint encoder, and
e(x)=E(x)/||E(x)||. Cosine dissimilarity is

    d(x,y) = 1 - e(x)^T e(y), in [0,2].

It is neither a probability of relevance nor a causal distance; it is not a
metric satisfying the triangle inequality. Shared coordinates permit cross-modal
comparisons but do not remove modality bias. Rank within each modality instead
of letting all images occupy a pooled “far” band.

At each hop, remove cues visited on that path. Within each available modality m,
sort by d(parent,cue), break ties by ID, and split into three balanced rank bands
B_(m,b). Extra members go to near, then middle. Sample

    q(c | parent, visited) = 1/|M| × w_b/(sum of nonempty-band weights in m)
                            × 1/|B_(m,b)|.

M contains available modalities. Defaults w=(0.2,0.5,0.3) are pilot settings,
not optimized values. Sample an operator uniformly from its finite supplied list;
the recorded joint probability is q(c|state)/number_of_operators. The first
parent is g; later parents are the previous cues. Recurrence across paths is
allowed. Modality balancing is a deliberate sampling bias, not a correction
guaranteed to improve utility.

The visited set is part of the state; transitions are not memoryless in the cue
alone. This is finite stochastic search, not MCMC from a known target posterior.
No mixing or convergence claim is made. Seed, input hash and configuration
reproduce controller choices, not LLM outputs or independent conceptual diversity.

The controller reports distances to the parent, objective, and earlier selected
cues. The last measures cue recurrence, not behavioral novelty. To measure a new
agent interpretation, encode that artifact separately. Never assign an imagined
embedding distance to generated text or a described image.

PCA is for display only. The bundled two-dimensional projection retains about
38.2% of variance. All displayed distances use the original 512 dimensions.
Batch and cache embeddings. The reference implementation sorts N cues per hop:
roughly O(L H (N d + N log N)) for L paths, H hops and d dimensions, plus archive
comparisons. It is suitable for small corpora, not optimized large-scale retrieval.

## The worker supplies generative continuity

A cue sequence is not a discovered solution. Give a worker the grounding packet
and continuity across a few cue/operator pairs. Request external artifacts such
as a relation sketch or changed behavior, not an exhaustive private reasoning
transcript. An image hop requires inspecting the image. A worker can ignore an
unproductive cue and need not establish immediate relevance at every hop.

The main builder receives retained candidates, evidence, predictions and
mismatches. Speculative trails remain in scratch records. Several workers can
run independent paths where useful; no fixed agent panel is required.

One actual worker trial is saved in `examples/semantic-exploration/path-trial.json`.
It received seed 1's first path (flower → pavilion → germination), inspected both
images, and produced three external sketches and a request-coalescing hypothesis.
The worker received the task objective but no implementation evidence or preferred
solution. The proposal includes an experiment and explicit unknowns; that
experiment has not run. This checks that the workflow can return a testable
candidate, not that the detour adds value. The predicate example below was
authored separately and is not a test of the worker's complete proposal.

The search objective can be described, not claimed solved, as

    maximize E[max_(y in validated proposals plus baseline) U_g(y) - U_g(baseline)]
    subject to total measured cost <= B and preserved task constraints.

Operationalize U_g for the task; do not invent a scalar human utility. Count
encoder setup, failed proposals, bridge construction, testing and human time.
Amortize caches only under a stated reuse workload. Delay expensive bridges until
checkpoints. Add adaptive bandit allocation only when repeated, consistently
evaluated outcomes support learning a policy; a few subjective scores do not.

## The relational bridge

[Structure mapping](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog0702_3)
offers a useful precedent: map relations rather than shared adjectives. “One
announcement serves many equivalent listeners” suggests sharing production. It
does not establish anything about a particular service.

An illustrative target is a burst of product requests. Inspection would need to
show duplicate concurrent database reads contributing to latency. Map listeners
to requests, production to the read, and audience eligibility to full response
identity/access context. A proposal is a bounded map of in-flight reads keyed by
that identity, cleaned up after settlement: ordinary request coalescing.

Prediction: fewer duplicate reads reduce queuing on the same burst. Measure
latency, read count, errors, freshness and isolation. If reads fall but latency
does not, the bottleneck story was incomplete. Cancellation, shared failures,
serialization cost, multiple processes and snapshot timing are mismatches to
check. This example was not discovered or validated by the bundled cue paths.

A flower image could suggest concentric grouping or shared centers. These are
proposed readings of visual structure, not botanical facts or engineering
evidence. The relation and target correspondence still need to be specified.

## A finite predicate search and generated cases

For a formalizable relation, define a finite domain D and bounded grammar G:

    exists P in G such that for all (a,b) in D×D: C(P,a,b).

The unknown is a predicate, making this a bounded form of second-order synthesis.
Enumerating a finite grammar needs no general second-order solver. Guarantees
reach only the encoded constraints and domain.

`experiments/semantic-walk/bridge_example.py` enumerates eight predicates, one
for each subset K of three fields:

    P_K(a,b) = all a[field] == b[field] for field in K.

Its independently declared fictional contract says tenant, SKU and locale all
affect response identity. The checker finds the smallest admissible K, rejects
unsafe candidates with counterexamples, and generates concrete cases where
SKU-only and full-key sharing disagree. Desired answers come from the contract,
not from the winning candidate. Timing/freshness, cancellation and real latency
remain outside the model and pending. Run:

```sh
python3 experiments/semantic-walk/bridge_example.py
```

If the contract is unknown, find a feasible x where build_A(x) != build_B(x),
then ask which behavior is wanted. Record the answer-to-action map before asking.
A solver generates a disagreement; an authorized source supplies its label.
A grammar can anchor search too: new primitives may be proposed, but need explicit
definitions before entering the checkable layer.

## Evidence still needed

The demonstration checks mechanics. Evaluate the method on representative tasks
with fixed original criteria, randomized assignments, and equal total budgets:

- Competent contextual brainstorming, including challenged assumptions.
- Fresh grounded attempts with the same raw evidence and constraints.
- Continuing paths with uniform cues and the same bridge/test stages.
- Continuing paths with embedding-stratified cues.

The last comparison isolates geometry from random prompting. Test text-only vs
joint image/text, immediate vs delayed grounding, and memory vs no memory as
separate ablations. Control corpus choice, selection/judging cost and evidence.

Measure verified useful changes per budget, selection misses, false positives,
regressions, human burden and held-out outcomes. Save predictions before checks;
blind method labels where possible. Cases used to steer a build are development
data, not independent proof of the method that generated them. A purpose change
requires explicit versioning; scores under different objectives are incomparable.

Embeddings propose where to look. A testable relation supplies the return path.
Actual artifact outcomes decide whether the detour was worthwhile.
