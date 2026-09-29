# Continuation: distinguish affine-state growth from decision difficulty

This is a **fresh-context continuation from the supplied prior report and simulated feedback**, not an independent replication. I read frozen-v1/REPORT.md, skill-v2/SKILL.md and its domain, metacognition and trajectory references. I did not inspect the prior implementation or other trial material. The simulated user's remaining need was a clearer reason to pursue affine-plus-clauses: what would advance understanding of general uniform decision complexity, and what would exhaust this direction's usefulness? No additional simulated-user question was needed because that distinction determined the operation.

The answer is conditional and concrete. **Pursue a new operation when it removes a demonstrated representation cost while preserving the answer and exposing its own computational cost. Stop treating raw state growth as a hardness signal.** This run produced such an operation—weighted affine projection—and proved that canonical merging alone fails exponentially even on a connected, easily decided family. Projection fixes that family and preserves polynomial affine solving. This earns the repaired operator a narrowly scoped next test; it is not progress toward a proof of P≠NP or an unrestricted polynomial SAT algorithm.

## Original target and why this continuation bears on it

The target remains a deterministic, uniform, worst-case polynomial-time SAT decision procedure, or a valid obstruction covering all such procedures, as motivated by [Cook's official P-versus-NP problem description](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf). The input length N includes the explicitly represented variables, equations and literals. A single algorithm must handle every finite input; an order, decomposition or compressed representation cannot be supplied for free unless it is explicitly an extra input of a restricted theorem.

The prior report supplies the exact identity

    #solutions(Ax=b AND all clauses) = Σ_J (-1)^|J| #solutions(Ax=b AND falsifications of clauses in J).

Every summand is an affine count and can be evaluated by Gaussian elimination. This makes affine-plus-clauses an executable representation of arbitrary SAT (take A empty), rather than a toy problem with no return path. Its obstacle is the cost of representing and combining many terms.

**Exact counting is stronger than the requested decision output.** Efficient exact counting would suffice for decision by testing positivity; failure of an exact-count representation says nothing by itself against efficient decision. In particular, an algorithm might decide existence without constructing any of these counts.

What would improve general understanding is an independently justified, efficiently executable closure or forgetting operation, with explicit size and update bounds, that survives examples defeating the previous representation. A genuinely general advance would additionally need a polynomial construction and polynomial bounds for arbitrary formulas, or a new theorem identifying a previously unaccounted-for tractable class/reduction. Merely assuming a polynomial compressed representation with a polynomial zero test would package the desired conclusion inside a hypothesis.

What would exhaust the **tested mechanism's** usefulness is repeated growth on inputs already having a cheap answer, with no new operation beyond enumerating more states, or a repair whose only guarantee restates that there are few states. Neither outcome would exhaust every algebraic approach to SAT. This run already retires “canonical equality merging plus global component splitting” as a sufficient general compression proposal.

## One focused operation and its ancestry

Parent: frozen-v1's proposed continuation—canonical row-reduced affine restrictions, merge identical signed states, factor variable-disjoint components, and inspect small overlapping cases.

Changed habit: retaining every processed variable and distinguishing affine histories even when future clauses cannot observe them.

Fixed requirements: exact answers, all Boolean assignments, arbitrary affine input, ordinary clauses including degenerate clauses, explicit computational costs, and the original general decision target.

New object: a signed sum of affine indicators **after summing variables absent from all remaining clauses**. This is an exact transformation, not a relaxation. Initial unused variables are projected as well. The implementation keeps one integer coefficient per canonical affine solution set and deletes zero coefficients or inconsistent states.

Minimal local assumptions: finite Boolean variables; linear algebra over F_2; explicit clauses; exact integer arithmetic. Gaussian elimination is used for canonicalization, intersections and projection. These are construction dependencies, not a claim about globally minimal axioms. No unproved hardness assumption is used.

The frozen initial predictions are in PREDICTIONS.md. After the first checks exposed a converse failure of raw boundary tables, PROJECTION-PREDICTION.md froze the derived repair before the second run. The second run reuses development cases; it is a repair replay, not independent evidence.

## A proved failure family for canonical merging

For every q≥1, define

    S_q(s,x_1,...,x_q) = AND_{i=1}^q (s OR x_i).

This is a deliberately easy synthetic sanity test, not a representative sample of hard SAT. Its interaction graph is connected. Every pair of clauses intersects in one variable. In the variable order s,x_1,...,x_q, only s need remain visible to future clauses.

**Proposition 1.** After inserting j of these clauses without forgetting variables, the canonical signed affine dictionary has exactly 2^j nonzero keys, irrespective of the insertion order among these j clauses.

**Proof.** The empty subset contributes the unrestricted space. Each nonempty J⊆[j] contributes coefficient (-1)^|J| to the affine set

    s=0, x_i=0 for i∈J.

All these sets are consistent and distinct: if J and K differ at i, assigning x_i=1 distinguishes the corresponding restrictions in the appropriate direction. Therefore canonical equality merging never combines two terms, and no coefficient cancels. There are 2^j keys. Global component splitting does nothing because the clause graph is connected. ∎

Yet

    #S_q = 2^q + 1,

because s=1 allows all leaf assignments and s=0 forces every leaf to 1. Decision has the explicit all-ones witness. Thus exponential key growth occurs on a simple polynomial-time decision family. No lower-bound inference survives this test.

For comparison, q disjoint clauses (a_i OR b_i) have the same 2^q global expansion but split into q independent two-key factors, giving count 3^q. Component factoring repairs disconnected examples; the star proves that it does not address conditional independence through a shared variable.

## The new exact operator: weighted affine projection

Split the variables of a consistent affine state into z∈F_2^e to forget and y to retain:

    A_E z + A_B y = b.

Let r_E=rank(A_E), and let the rows of L be a basis of ker(A_E^T), interpreted as row vectors acting on equation space.

**Lemma 2.** For every retained assignment y,

    Σ_z 1[A_E z + A_B y=b]
      = 2^(e-r_E) · 1[L A_B y=L b].

**Proof.** A z exists exactly when b−A_B y lies in im(A_E), equivalently when every left-null vector annihilates it. These are exactly the displayed projected equations. If one z exists, all solutions are its translate by ker(A_E), which has 2^(e-r_E) elements. Otherwise the sum is zero. ∎

The lemma includes zero eliminated variables, free eliminated variables, dependent rows and zero-dimensional retained spaces. An inconsistent state is discarded before projection. Computing the projected system and the fiber exponent uses polynomial-time row operations; it never enumerates the eliminated assignments.

For a signed sum, apply this map term by term, multiply coefficients by the fiber size, canonicalize, and merge again. If future clauses depend only on y, their product g(y) satisfies

    Σ_z f(z,y)g(y) = g(y)Σ_z f(z,y).

This is the precise permission to forget a variable. An affine equation may still couple z and y: projection carries that coupling into the projected equations, so it is unnecessary to keep z merely because the initial affine core mentions it.

**Algorithm invariant.** After processing j clauses and forgetting E_j, the stored signed sum is exactly

    f_j(y) = Σ_{z on E_j} 1[Ax=b] ∏_{i≤j} 1[C_i].

All unprocessed clauses involve only retained variables. Clause insertion multiplies by 1−1[falsifying affine restriction]; Lemma 2 proves the subsequent projection. This establishes the invariant inductively. After the last clause all variables can be forgotten, leaving the exact satisfying count. The sign of individual coefficients is immaterial to exactness; the final count is nonnegative. There is no general polynomial bound on the number of surviving states.

On S_q, after j leaves are summed while s is retained,

    f_j(s) = 2^j + (1−2^j)1[s=0].

This follows either from the two cases s=0,1 or the recurrence f_{j+1}(s)=2f_j(s)−f_j(0)1[s=0]. Thus at most two affine keys remain after each forgetting step; the final projection gives 2^q+1. Each clause temporarily at most doubles the dictionary, so the intermediate update is bounded as well. On pure affine input, initial projection eliminates all variables and gives zero or 2^(n−rank A) from a single state. Integer coefficients have polynomial bit length in n+q; this does not bound how many coefficients there are.

This is the checkable improvement over the prior proposal: **one exact Gaussian operator preserves both affine solvability and a conditional factorization that equality merging misses.** No literature novelty is asserted.

## A useful comparator and its limits

A second implementation provides an independent exact comparator using ordinary variable-boundary tables. Given a variable order, B_i consists of processed variables occurring in any constraint that also mentions an unprocessed variable; affine rows and clauses both count as constraints. Keep the weighted assignments to B_i, check each constraint when its last variable arrives, and sum variables leaving B_i.

If w=max_i |B_i|, this uses at most 2^w stored assignments and polynomial(N)·2^(w+1) bit operations, including exact counts of at most n+1 bits. The proof is the same “future factors cannot observe forgotten variables” identity, now applied to an explicit truth table. With the order supplied, w is directly computable. Boolean OR in place of addition gives a decision version; counting is not required for that restricted guarantee. No small-width order is asserted for arbitrary inputs.

This comparator is not itself the final repair. One parity row x_1+...+x_n=0 keeps every processed variable in its raw boundary until the last variable arrives. It stores 2^(n−1) assignments, while Gaussian elimination and weighted affine projection each use a single affine state. This opposite failure is why the repair projects affine sets directly rather than replacing all of them by truth tables.

## Checks and actual outcome

All arithmetic was exact. checks.py contains canonical signed expansion, component factorization, the boundary-table comparator, weighted affine projection, and independent assignment enumeration.

| Case | Prediction/source | Observed |
|---|---|---|
| Stars q=0,...,8 | Proposition 1 and case split | Unprojected trace 1,2,...,2^q; projected peak ≤2; counts 2^q+1 |
| Eight-clause star | Same | 256 unprojected keys, projected peak 2, count 257 |
| Disjoint pairs q=0,...,8 | Direct product | Count 3^q; each component peak 2; global expansion 2^q |
| All 512 two-variable one-row/two-clause fixtures from the fixed pool | Enumeration | Every method and both boundary orders agreed |
| 400 seeded affine-plus-clause fixtures, n≤6, q≤8 | Enumeration | Every method agreed, including projection |
| Three zero-variable edge cases | Enumeration | Empty instance 1; contradictory row 0; empty clause 0 |
| One parity row, n=1,...,9 | Rank and boundary argument | Boundary peak 2^(n−1); projected affine peak 1; count 2^(n−1) |

The 915 generic fixtures include empty, duplicate and tautological clauses; zero and contradictory rows; repeated literals; unused variables; and reversed variable orders. The parity comparator was reserved until the first main checks passed, but became development input for the repair. No hidden holdout claim is made. The final run exited successfully and recorded approximately 0.124 seconds of Python runtime, not a performance benchmark. Proofs establish the universal identities; bounded checks test implementation consistency. No proof assistant was run.

## What the result changes, and where to stop

The proposed canonical-merging experiment has now served its diagnostic purpose: it exhibited exponential state retention unrelated to decision hardness. More stars, larger q, or another raw state-growth plot would add little. **Stop that unchanged branch.**

The repaired branch has a precise remaining obstacle: many distinct projected affine spaces can survive even after every safely forgettable variable is summed. Future clause overlap and information transmitted through the affine core can both matter. Cheap local projection does not imply cheap composition. A useful next experiment must bound or defeat that joint effect, not repeat the solved star.

One resumable next operation is to hold future clause overlap small while adding an affine core that transmits constraints between otherwise disjoint clause blocks. Specify the family and an insertion order first; measure projected keys and affine ranks; compare with exact small-instance counts. Attempt a bound using an explicitly defined interface of transmitted linear constraints. A noncircular bound, with an order/interface constructible within the claimed runtime, would justify further restricted algorithm work. An exponential family despite the proposed small interface would refute that parameter and redirect or retire this repair. If every tractability claim merely assumes the desired small dictionary, stop advertising the direction as explanatory of general complexity.

Neither present outcome settles unrestricted decision complexity. The gain is an explicit distinction and operation: canonical equality is too fine for histories that future constraints cannot observe, while raw variable boundaries are too fine for linear dependencies. Weighted affine projection addresses both demonstrated defects. The general uniform transfer remains open, and counting remains only one possible route to decision.

Reproduce with `python3 /private/tmp/via-negativa-millennium-gckb_mh2/practitioner-v2/checks.py`. Outputs are check-output.json; predictions and the refinement are separately preserved. The episode used one focused mechanism test with an algebraic repair and rechecks, no subagents and no further simulated-user exchange. Work was bounded to approximately eight minutes; exact end-to-end time and token cost were not measured.
