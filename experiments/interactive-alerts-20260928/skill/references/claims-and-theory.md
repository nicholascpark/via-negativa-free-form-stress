# What the skill can honestly claim

The active research protocol now develops representations, constructions and
reusable operations through continuing branches. Its
[Navier–Stokes comparison](navier-stokes-alignment.md) separates published
evidence, transferable instructions and missing runtime capabilities.
The following exploration and interaction hypotheses remain distinct components;
none is established by the success of an external research system.

The current exploration hypothesis is that context-retaining stochastic paths
with delayed grounding sometimes produce useful alternatives missed by equal-cost
ordinary brainstorming and grounded restarts. The [semantic exploration reference](semantic-exploration.md)
defines the runnable sampler, bounded predicate example and necessary comparisons.
Measured cue distances and finite checks do not establish that benefit.

A separate proposed benefit of the interaction stage is avoiding a costly commitment to an inadequate definition
of the product. A concrete alternative can supply an experience the user has not
had, after which they may keep, revise, or replace that definition. This is a
hypothesis about collaboration. It uses familiar techniques; packaging does not
establish novelty or superiority to a good prompt.

The apophatic inspiration is practical and limited: withhold final authority from
our descriptions. Removing “must deliver the whole manuscript” makes another
activity possible. It does not establish “manuscripts are bad,” an inaccessible
true purpose, or a privileged faculty for seeing what others cannot.

## Three distinct problems

1. **Conversational anchoring:** prior messages make one interpretation sticky.
   Compare the same assignment with and without that rationale, preserving facts
   and constraints. Fresh context is a harness intervention, not literal deletion
   of model priors. Measure relevant decisions and outcomes, not lexical diversity.
2. **Preference uncertainty within a model:** several known purposes or policies
   are plausible. Choose comparisons that inform a pending decision. The existing
   ANY/ALL filter experiment tests this narrow problem.
3. **Revision of the model or purpose:** an experience introduces a distinction
   absent from the candidate set, or changes what the person wants to create.
   Expand or revise the representation and the benchmark explicitly. Do not
   report this as merely locating a fixed preference more accurately.

These require different evidence. Success at one does not establish the others.

## A useful mathematical starting point

For a *fixed* hypothesis set H, observations D, candidate build actions A,
well-defined utility U(a,h), query q, and response y, a conventional value-of-
information criterion is:

```
VOI(q) = E_y [max_a E[U(a,h) | D,q,y]]
         - max_a E[U(a,h) | D]
         - cost(q)
```

Use a positive value to justify asking only when the probabilities, utility
scale, and costs are meaningful. It formalizes why uncertainty alone does not
warrant interruption: the answer should improve a decision enough to repay its
cost. In an ordinary skill, a written answer-to-action map is a qualitative
approximation. Do not attach invented numerical confidence or utility to it.

[Active Inverse Reward Design](https://arxiv.org/abs/1809.03060) selects reward
queries by expected information gain, using a model of a designer's choices.
Its experiments use simulated humans. It supports active comparison as a
research direction, not this skill's effectiveness. Its misspecified reward
model experiment also illustrates why confidence can coexist with poor decisions.

Information gain and decision value are different criteria: a question may teach
something without changing the best available action. The formula above assumes
a stable utility model and available actions. If interaction creates a new aim
or introduces a new action, its original calculation is incomplete. Version the
model and reassess; do not pretend novelty was sampled from a defined posterior.

Sequential variants could model the user, artifact, observations, and querying
costs as a partially observed decision problem. Auditing such a policy would
require specified transition and response models, eligible query opportunities,
and independent task outcomes. This repository does not implement or validate
that RL system. A runtime skill can orchestrate experiments without being a
learned exploration policy or altering post-training.

## What the first evidence should be

- **Local utility:** an actual encounter leads to a traceable decision; another
  relevant situation supports the choice; retained requirements hold; costs are
  recorded. No change can be a useful result, but should not be counted as an
  improvement without a relevant comparison.
- **Method utility:** outperform competent clarification and prototyping under
  comparable human/compute budgets across repeated independent episodes. Include
  fully specified tasks where interruption is wasteful. Keep context isolation,
  memory, and benchmark generation as separate ablations when attributing gains.
- **Preference formation:** report the person's account and later informed
  endorsement, while testing sensitivity to equivalent presentations separately.
  No benchmark reveals an untouched, context-free preference.

The live benchmark records and exercises an evolving commitment. The external
benchmark evaluates whether this way of working helps. The first must adapt;
the second must control that adaptation enough to support its stated claim.
There is no irrefutable benchmark of creative usefulness.
