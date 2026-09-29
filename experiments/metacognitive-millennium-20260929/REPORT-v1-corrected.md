# Reader copy with coordinator clarifications

The frozen v1 report remains unchanged. The observer requested the distinct-variable/non-tautological qualifier for the seven-assignment example. The coordinator also padded the displayed operation bound with +1 terms so it covers zero-variable inputs; this does not change its claimed asymptotic tractable regimes. These are artifact clarifications, not skill findings.

# Research episode: local visibility can be maximal while decision cost is small

This episode did **not** resolve P versus NP. It produced a precise auxiliary theorem, an explicit sparse 3-CNF family, an exact algebraic repair, and a controlled extension to affine systems with ordinary clauses. The useful return is a checkable account of where a plausible representation-based attack succeeds and where its complexity inference fails. No result is asserted to be new to the literature.

The original request was from a **simulated user**: make a substantial fresh mathematical attempt, retain the full P-versus-NP target, and return a checkable intermediate result. The simulated user selected the local-information route and added: “Please explain why the chosen summaries are relevant to a serious attempt at general decision complexity; I don’t want the limitation to come only from making the summaries weak.” That preference, its pre-answer action map, and the resulting change are recorded in QUESTION-1-PREANSWER.md and DECISION-1.md. It is preference evidence, not mathematical evidence.

The target remains the deterministic, uniform, worst-case polynomial-time decision question from [Cook’s official statement](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf). Because SAT is NP-complete, a general polynomial SAT algorithm would suffice for P=NP. Bounds for a restricted summary interface do not establish P≠NP.

## A precise representation and its exact visibility threshold

Work over the two-element field F_2. Let A be an m×n binary matrix, b∈F_2^m, and X a uniformly random Boolean assignment. Define the violation vector

\[
V_b=AX+b\in\mathbb F_2^m.
\]

Its i-th coordinate is 1 exactly when the i-th equation is violated. Define S_k(A,b) as the indexed collection of the **complete joint distributions** of (V_b)_J, for every J⊆[m] with |J|≤k. This contains every atom probability and every statistic of each such marginal, not just pair correlations or approximate moments. All quantities here are exact. Uniform sampling is a mathematical definition, not an empirical claim about typical SAT inputs.

Let D=ker(Aᵀ), δ=b+b′, and define

\[
d_A(\delta)=\min\{|z|:z\in D,\ z\cdot\delta=1\},
\]

with the minimum of the empty set equal to infinity.

**Theorem 1.** For every A,b,b′ and 0≤k≤m,

\[
S_k(A,b)=S_k(A,b')\quad\Longleftrightarrow\quad k<d_A(b+b').
\]

When d is finite, at order d there is a marginal whose two distributions have disjoint supports.

**Proof.** For any z∈F_2^m,

\[
\mathbb E(-1)^{z\cdot V_b}
 =(-1)^{z\cdot b}\mathbb E(-1)^{(A^Tz)\cdot X}
 =\begin{cases}(-1)^{z\cdot b}&z\in D,\\0&z\notin D.\end{cases}
\]

The last expectation is zero by pairing assignments differing in a coordinate where Aᵀz is 1. The characters supported on J form a basis for all real functions on F_2^J, so the J-marginals agree exactly when all these character expectations agree. They differ precisely if a z supported on J lies in D and z·δ=1. Minimizing the support proves the equivalence. At a minimum-support witness, the parity z·V has opposite deterministic values under the two laws, proving disjointness. ∎

For b′=0, d_A(b) is also the minimum number of equations in an inconsistent subsystem. Indeed an inconsistent subsystem has a linear combination of its rows giving 0=1, and conversely such a combination certifies inconsistency. This uses only the elementary identity im(A)=ker(Aᵀ)⊥. If d=∞ the two *entire* violation distributions agree. A contradictory zero row gives d=1. These boundary cases are included in the checks.

## Sparse SAT/UNSAT examples that agree on every proper block subset

Let G=(V,E) be a connected simple graph. Set m=|V|, n=|E|, and let A be its vertex-edge incidence matrix over F_2. Since Aᵀz=0 says that z has equal values at the endpoints of each edge, connectivity gives

\[
D=\{0,\mathbf1_V\},\qquad\operatorname{rank}A=m-1.
\]

Compare charge b=0 with charge b′ having a 1 at just one vertex. The first system has 2^(n−m+1) solutions; the second has none. Yet d_A(b+b′)=m, so **every proper-subset joint violation distribution agrees**. In fact each proper marginal is uniform: every proper set of incidence rows is linearly independent.

For arbitrarily large bounded-arity examples, use the prism graph C_ℓ□K_2, ℓ≥3. It has m=2ℓ vertices, n=3ℓ edges and degree 3. Encode each equation x_a+x_b+x_c=q as four 3-clauses, one forbidding each wrong-parity assignment. There are 4m clauses and no auxiliary variables. Each variable occurs in eight clauses. This is the established Tseitin construction; its use in serious restricted-model lower bounds is illustrated by [Pitassi and Robere’s research paper](https://eccc.weizmann.ac.il/report/2016/188/download/), where additional lifting machinery is essential.

The proper-subset theorem concerns the m **parity blocks**, each containing four CNF clauses. It does not automatically transfer to every individual clause marginal. This distinction is consequential, and the stronger transfer actually fails.

On the K4 example with six variables, a pair of clauses in the even-charge encoding is

\[
(\neg x_1\vee x_2\vee x_3),\quad
(\neg x_1\vee x_4\vee x_5).
\]

Both are violated with probability 1/32. In the odd-charge encoding the first becomes (x_1∨x_2∨x_3), so simultaneous violation is impossible. Thus a two-clause statistic can distinguish this fixed ordering of the CNF encodings. The claim of full clause-marginal indistinguishability is refuted, not left implicit.

One strong statement **does** transfer exactly: for every assignment, a violated parity block violates exactly one of its four clauses, while a satisfied block violates none. Therefore the total number U of violated CNF clauses equals |AX+b|.

## The full global correction and energy polynomial

Define Z_b(t)=∑_x t^|Ax+b|. The identity

\[
t^v=\tfrac12\big((1+t)+(1-t)(-1)^v\big),\quad v\in\{0,1\},
\]

combined with the character calculation above yields

\[
Z_b(t)=2^{n-m}\sum_{z\in D}(-1)^{z\cdot b}
 (1+t)^{m-|z|}(1-t)^{|z|}.                 \tag{1}
\]

This is a polynomial identity. For connected graphs it reduces to

\[
Z_\pm(t)=2^{n-m}\big((1+t)^m\pm(1-t)^m\big), \tag{2}
\]

where + denotes even total charge and − denotes odd total charge. Equivalently, the energy histogram is 2^(n−m+1)·binom(m,j) on the charge-compatible parity of j, and zero elsewhere.

Consequently the two actual 3-CNF formulas have identical expectations of **every polynomial in their total violated-clause count of degree below m**, even though one is satisfiable and the other is not. To see this, Z_+−Z_− has a zero of order m at t=1, giving agreement of the first m−1 factorial moments and hence ordinary moments. Here m is one quarter of the number of CNF clauses; the invisible moment order grows linearly with formula size.

For 0<t<1, their exact relative contrast is

\[
\frac{Z_+(t)-Z_-(t)}{Z_+(t)+Z_-(t)}
  =\left(\frac{1-t}{1+t}\right)^m.
\]

It is exponentially small at fixed t. With t=e^(−β), contrast at least a fixed c∈(0,1) requires exactly

\[
\beta\ge\log\frac{1+c^{1/m}}{1-c^{1/m}}
 =\log m+\log\frac{2}{-\log c}+o(1).
\]

This describes the sensitivity of a chosen thermal observable; it is not a lower bound on numerical algorithms. Equation (2) can itself be evaluated symbolically with a compact expression.

The key repair is even simpler: compute a basis of D and test z·b on its basis vectors. Row reduction is polynomial-time, and all systems here can be decided this way. On a connected graph, just summing the charges suffices. The distinguishing character ∏_i(−1)^(V_i) has degree m but takes O(m) operations to evaluate. **Interaction order and computation cost are different quantities.**

## One controlled step toward ordinary SAT

A non-tautological clause on three distinct variables has seven satisfying assignments on those three variables, so that satisfying set cannot itself be an affine coset, whose nonempty cardinality is a power of two. Nevertheless the algebraic repair admits an exact signed continuation.

For a clause C, let E_C be the coordinate equations that falsify all of its literals. A positive literal x_i gives x_i=0; a negative literal gives x_i=1. For q clauses,

\[
\#\{Ax=b\ \wedge\ C_1\wedge\cdots\wedge C_q\}
 =\sum_{J\subseteq[q]}(-1)^{|J|}
   N\big(Ax=b,\ E_{C_j}\ (j\in J)\big),            \tag{3}
\]

where N is zero for an inconsistent affine system and otherwise 2^(n−rank). The proof is direct: expand ∏_j(1−1[E_Cj]), multiply by 1[Ax=b], and sum over assignments. It handles tautologies, empty clauses and duplicates without special mathematical exceptions.

If L is the total literal count, direct evaluation takes 2^q polynomial-size row reductions, with a conservative bit-operation bound O(2^q((m+L+1)(n+1)²+n+q+1)). The signed accumulator needs only O(n+q) bits. It is polynomial for fixed q, or q=O(log N) with explicitly represented inputs of size N. No bound on q for general SAT has been shown.

Nor does the 2^q expansion prove hardness: for q positive clauses on disjoint triples the answer is 7^q, although all 2^q subset restrictions are distinct. Factorization compresses what naive signed enumeration expands. A future general algorithm would have to control composition, cancellation and factorization; merely counting intermediate objects would repeat the failed lower-bound inference.

## Relevance, evidence and limits

These summaries were chosen because they truncate an exact general identity: for arbitrary constraints with violation indicators V_i,

\[
\#\mathrm{SAT}=2^n\mathbb E\prod_i(1-V_i).
\]

All joint violation moments appear in its expansion, and Z(0) encodes the same count. The constructed pair shows that even the complete, possibly exponentially large collection of proper block marginals can omit the decisive invariant. It tests a natural counting/compression route with unusually rich information. It still imposes an interface restriction.

The proved impossibility is precise: a rule receiving only S_(m−1), even with the common graph A and dimensions supplied, gets identical input on this SAT/UNSAT pair. The same holds for randomized rules, which then have identical output distributions and cannot exceed 1/2 correctness on both instances. An unrestricted algorithm receives b or the actual formula and can immediately escape the interface. A claim that every polynomial-time algorithm factors through these summaries is false on this very example. Therefore this is a failed general lower-bound attempt with a useful diagnostic result, not evidence favoring P≠NP.

| Evidence | What was actually established |
|---|---|
| Mathematical derivations | Theorem 1, sparse realization, equations (1)–(3), moment equality, and thermal contrast under their explicit hypotheses |
| Exact exhaustive checks | 512 binary 3×3 matrices, 18,432 unordered RHS pairs, 73,728 threshold comparisons; all passed |
| Explicit graph checks | K4 and prisms with 6 and 8 vertices; all assignments, all proper block subsets, CNF encoding and exact histograms; all passed |
| Counterexample | Two individual K4 clauses refute the stronger clause-marginal transfer, also verified by enumeration |
| Boundary/extension checks | 256 smaller rank/count cases; disconnected triangles; 9,216 affine-plus-two-clause cases; empty, tautological and duplicate clauses; disjoint-clause family q=0,…,5 |
| Not established | General SAT algorithm, unrestricted lower bound, polynomial closure for non-affine composition, literature novelty, or proof-assistant certification |

For the 6-vertex prism the even energy histogram is {0:16, 2:240, 4:240, 6:16}; the odd histogram is {1:96, 3:320, 5:96}. Both have 512 assignments and equal moments through degree 5, while their satisfying counts are 16 and 0. This provides a small directly checkable instance.

Finite checks are development data and do not replace the universal proofs. The disconnected extension was reserved until the main checks passed; it confirms that each component contributes its own parity obstruction. All code uses exact integer/rational arithmetic except the illustrative decimal β values. No proof assistant was run. The underlying algebra and Tseitin family are established ideas; this bounded episode offers a local derivation and synthesis, not a priority claim.

## Reproduce and continue

From this directory, run `python3 checks.py` and `python3 continuation_checks.py`. Their actual outputs are check-output.json and continuation-output.json (also preserved as text). Six generated DIMACS files give the even/odd K4 and prism examples. Both runs exited successfully; the shell reported approximately 0.56 and 0.27 seconds respectively, not a controlled performance benchmark. One simulated-user question round was used. Full wall time and token cost were not measured.

The next concrete operation is to implement canonical row-reduced affine restrictions for equation (3), merge identical signed states after each clause insertion, and factor variable-disjoint components. On synthetic q≤8 overlapping and disjoint inputs, record exact counts and surviving state counts after every insertion. A proposed bound must name an explicit overlap parameter and be frozen before testing. This may expose a useful restricted class or a new obstruction; it would still need a separate proof before any general-SAT transfer.

Supporting records: BRIEF.md, SHARED-AFFINE-SETUP.md, DERIVATION-v1.md, CONTINUATION-v2.md, CHECK-PREDICTIONS-v1.md, SOURCES.md, and the decision artifacts. The standalone report is this file.
