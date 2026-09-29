# Frozen before implementation checks

Fresh-context continuation of supplied frozen-v1/REPORT.md and simulated-user feedback; not an independent replication. Scope: one operation, test and repair canonical affine-state merging by future-boundary aggregation.

Target: deterministic uniform worst-case SAT decision; exact counting is only a sufficient route, never a necessary condition for efficient decision.

Input family S_q = AND_{i=1}^q (s OR x_i), no initial affine equations. For q>=1 its variable interaction graph is connected, two clauses intersect in at most one variable, and ordering s,x_1,...,x_q leaves a boundary of size one.

Predictions: after j clauses, a signed dictionary of canonical affine restrictions has exactly 2^j nonzero keys, including the unrestricted key. Connected-component factorization of the input does not split S_q. The exact count is 2^q+1. Summing processed leaves while retaining only s yields weights (1,2^j), hence at most two states. On q disjoint two-variable positive clauses, component factoring instead gives q factors of two keys and count 3^q.

Check plan: q=0,...,8 families; generic affine-plus-clause cases compared by independent assignment enumeration, canonical merging, component factorization, and boundary dynamic programming. Include contradictory/zero affine rows, empty/tautological/duplicate clauses, unused variables, reversed variable orders. New random checks use a fixed reproducible seed and are development data.

Decision rule: exponential canonical-state growth at boundary width one retires canonical merging plus global component splitting as a stand-alone promising general compression mechanism. If boundary aggregation fixes it exactly, preserve its forget operation and polynomial bound for a supplied bounded-width order, while retaining the missing general transfer. A restricted parameter bound alone does not justify a claim of progress on unrestricted P versus NP. Further investment needs a new operation or an independently bounded class/reduction, not larger versions of these tests.

General-decision relevance: a polynomially executable decision-preserving representation with polynomial updates, size, construction and zero/nonzero query on arbitrary formulas would provide an algorithmic advance. Finding many states does not establish a lower bound. Requiring exact counts can be strictly stronger than the original decision objective, so failure of counting compression will not count as evidence against P=NP.
