# Controlled continuation v2 — adding non-affine constraints

Parent: DERIVATION-v1.md, transformation B3. Motivation from the **simulated user's** request: make the missing general-SAT transfer concrete, rather than ending at a local-observable limitation. The theorem below is an elementary inclusion-exclusion continuation, with no novelty claim.

## Exact operation

For an affine system Ax=b and an ordinary Boolean clause C, let E_C be the coordinate equations that make all literals of C false. A positive literal x_i contributes x_i=0; a negative literal not-x_i contributes x_i=1. A tautological clause contributes an inconsistent E_C, and an empty clause contributes no equations. Then

    # (Ax=b AND C) = # (Ax=b) - # (Ax=b AND E_C).

Both terms on the right are affine counts. Thus the repair from the parity example extends across one arbitrary clause without leaving exact linear algebra, provided a signed *sum* of affine counts is allowed.

For q clauses C_1,...,C_q, the exact continuation is

    # (Ax=b AND all C_i)
       = sum_{J subset [q]} (-1)^|J| N(A,b; E_C for C in J),       (5)

where N is zero if the combined affine equations are inconsistent, and otherwise equals 2^(n-rank of combined coefficient matrix).

Proof. For each assignment, write its clause-satisfaction indicator as product_i(1-1[E_Ci]). Expand, multiply by 1[Ax=b], and sum over all assignments. Row reduction evaluates each term by the shared rank lemma. This also proves the edge cases of repeated literals, repeated clauses, tautologies and empty clauses.

If L is the total number of literal occurrences, a direct implementation uses 2^q row-reduction calls on at most m+L rows and n variables. A conservative bound is

    O(2^q ((m+L)n^2+n+q)) bit operations

under straightforward bitwise elimination and binary integer arithmetic; transient signed sums have at most n+q+O(1) bits. Storage can remain polynomial by regenerating each subset and its matrix. This gives polynomial time for fixed q, and also for q=O(log N) when n,m,L are bounded by the explicit input size N. It is not a polynomial algorithm for arbitrary SAT, where q is unrestricted. Computing #SAT here is stronger than merely deciding it; no claim that exact counting is required by the P-versus-NP target is being made.

## What obstruction this now localizes

The operation is available, but a q-step generic expansion has up to 2^q terms. Treating that expansion count as a lower bound would repeat the earlier error: with q clauses on disjoint triples of variables and no affine equations, all 2^q subset restrictions are distinct, yet the answer is simply 7^q by factorization. A compact repair therefore needs to exploit composition and cancellation as well as global parity. This is an example of representation blow-up, not evidence that all algorithms blow up.

Next operation, concretely scoped: implement canonical row-reduced affine restrictions and merge identical terms after each clause insertion, while factoring variable-disjoint components. Input: generated affine-plus-CNF systems with q≤8 and a mixture of overlapping and disjoint clauses. Output: exact counts, the number of distinct signed states after each insertion, and witness pairs showing which overlaps survive both reductions. Freeze a proposed bound in terms of an explicit overlap parameter before testing it. No polynomial bound or general-SAT transfer has been established in this episode.

## Frozen predictions before continuation checks

- For every 2-by-3 A, every b, and every pair (with repetition) of signed 3-clauses on the three variables, equation (5) agrees with exhaustive assignment counting.
- The empty clause forces zero; the tautology x_1 OR not-x_1 changes nothing; duplicate clauses change nothing after their first copy.
- With q disjoint positive clauses on triples, the count is 7^q; the direct inclusion-exclusion enumerator still visits 2^q terms. Check q=0,...,5. These are development cases selected from the algebraic obligations, not held-out evidence for a runtime theorem.
