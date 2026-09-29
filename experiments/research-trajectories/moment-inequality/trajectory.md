# Exact target and branch artifacts

Target and assumptions are preserved in run.json. No assumption that the inequality is true was adopted. These are mathematical artifacts and proof steps, not claims about private reasoning or generic method superiority.

## Branch A: expose the missing interaction

A1, parent target — Exact representation. Define power sums p_k=sum_i x_i^k and elementary symmetric sums e_k=sum_{i_1<...<i_k} x_{i_1}...x_{i_k}, with e_k=0 when k>n. The target gives p_1=e_1=0, p_2=1 and e_2=(p_1^2-p_2)/2=-1/2. Obstruction: p_4 is not determined by those first two constraints in general.

A2, parent A1 — Exact transformation. The fourth Newton identity is p_4-e_1 p_3+e_2 p_2-e_3 p_1+4e_4=0. Substitution gives the reusable identity p_4=1/2-4e_4. The proposed inequality is therefore exactly equivalent, under the original constraints, to e_4>=0. This promotes the uncontrolled fourth-order interaction into an explicit object.

A3, parent A2 — Proved restricted result and unresolved transfer. For n=2 or n=3 the defining sum e_4 is empty, hence p_4=1/2 for every admissible vector. This explains all of the user's small-dimensional examples. Extending the claim requires a sign condition on e_4 absent in those dimensions. Request to branch B: inspect a sign-unbalanced construction rather than extrapolating the empty sum.

## Branch B: preserve the constraints by construction

B1, parent target — Exact auxiliary restriction. Impose x_1=a and x_2=...=x_n=b. This explores a subclass, so it can provide counterexamples but cannot establish the global maximum. Zero sum forces a=-(n-1)b.

B2, parent B1 — Exact normalization operator. For any nonzero real zero-sum vector v, N(v)=v/sqrt(sum v_i^2) preserves zero sum and yields unit square norm. Take v=(n-1,-1,...,-1). Then sum v_i^2=n(n-1), giving a=sqrt((n-1)/n), b=-1/sqrt(n(n-1)).

B3, parent B2 — Proved family. Its fourth-power sum is ((n-1)^4+(n-1))/(n^2(n-1)^2)=(n^2-3n+3)/(n(n-1)). Subtracting 1/2 yields (n-2)(n-3)/(2n(n-1)). Therefore it is a counterexample for every integer n>=4. An independent worker derived the same family from the exact original constraints; it did not receive branch A's residual or a proposed answer. Its calculation also explicitly declined to claim a global maximum.

## Checkpoint: combine artifacts

Parents A3 and B3. At n=4 choose x=(3,-1,-1,-1)/sqrt(12). Direct verification gives sum x_i=0, sum x_i^2=1, sum x_i^4=84/144=7/12>1/2. Here e_4=-3/144=-1/48; substituting into A2 returns 1/2+1/12=7/12. Both routes agree exactly. verify.py checks rational invariants for the normalized integer family at n=2,...,12 without rounded radicals. The finite checks are bounded evidence; the symbolic formulas prove the family statements for every n>=2.

## Usable mathematical consequences

1. The proposed universal inequality is false. The n=4 vector is a complete exact counterexample, requiring no remaining transfer obligation.
2. At n=2 and n=3 the fourth-power sum is identically 1/2, not merely bounded by it.
3. For any n under the constraints, sum x_i^4=1/2-4e_4. A restricted argument establishing e_4>=0 would establish the original inequality on that restricted class.
4. The sharp upper bound independent of dimension is 1 as a supremum: sum x_i^4 <= (sum x_i^2)^2=1; equality would allow at most one nonzero coordinate, incompatible with zero sum and unit norm. The family gives 1-(2n-3)/(n(n-1)) -> 1. Thus every admissible vector has sum x_i^4<1, but no smaller constant works uniformly over n.

No fixed-n maximization theorem or proof-assistant verification is claimed. No user question can certify or alter this theorem. The original target is resolved; optional stronger fixed-n optimization remains outside this compact run.
