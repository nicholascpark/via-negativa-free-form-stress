# Target and first cycle

Source: a **simulated user** requests a substantial fresh research attempt on P versus NP, useful checkable intermediate results, and involvement before consequential choices. No prior research context is being used.

Original target v1: decide whether every language with a polynomial-time verifier and polynomially bounded certificates has a deterministic polynomial-time decision algorithm. Preserve uniformity and worst-case polynomial time in encoded input length. A result on a restricted solver, Boolean representation, or input class is auxiliary until its transfer is proved.

Primary source retrieved: Stephen Cook, *The P versus NP Problem*, https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf . Used for the verifier definition, SAT completeness, and the distinction between algorithms and circuit lower bounds. Its historical performance claims will not be used as current facts.

Scope: one local episode, two preliminary representations, a consequential choice if their deliverables diverge, then a few transformations of the chosen object followed by proofs, finite checks, and an explicit transfer audit. No literature-wide novelty claim. No subagents. Standard finite combinatorics and exact arithmetic suffice for the first construction; no unproved complexity conjecture is assumed.

## Assumption map v1

| Kind | Entry | Where it matters |
|---|---|---|
| Target | Deterministic, uniform, worst-case polynomial in input bit length | Any claimed SAT algorithm must satisfy all three |
| Established dependency | SAT is NP-complete | A general polynomial SAT solver would imply P=NP |
| Definition | A residual function records all completions after a partial assignment | State-merging route |
| Habit to vary | Explicitly enumerate each distinguishable residual | May be replaceable by symbolic algebra |
| Habit to vary | Judge difficulty from low-order aggregate constraint statistics | May erase a global obstruction |
| Working hypothesis, unadopted | A rich enough compressed statistic remains easy to update for general SAT | Would require an independent proof; cannot be assumed |

## Initial route objects

A. Assignment-prefix route: for a Boolean relation f(x,y), study the family f(a,·). First compare explicit state enumeration with symbolic affine representations. Potential return: exact state count and a compact operator, plus a precise obstacle to generalizing it.

B. Constraint-interaction route: for a conjunction of constraints, study joint violation probabilities under a uniform assignment. First use parity systems to compare local statistics and global satisfiability. Potential return: an explicit indistinguishability family and a theorem about the order of information required by this summary, then a repaired representation.

Both are auxiliary and neither yet bounds general deterministic algorithms.
