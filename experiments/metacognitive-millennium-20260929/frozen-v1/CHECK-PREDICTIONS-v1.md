# Frozen finite-check predictions

Recorded before the branch-specific test program is run. Inputs are synthetic exact finite structures; tests are development checks, not independent evidence for a universal theorem.

1. Exhaust all 3-by-3 binary matrices and all unordered pairs of right hand sides. For k=0,1,2,3 the independently enumerated marginal signatures agree iff k<d_A(b+b'), with d computed by exhaustive dual enumeration. Include equal right hand sides, zero rows, dependencies and full-rank matrices.
2. On connected K4 and prism C3 square K2 and C4 square K2, compare b=0 with a single odd charge. Rank is m-1; all proper row-subset violation histograms match and are uniform; solution counts are 2^(n-m+1) and 0. Raw energy moments agree exactly through degree m-1 and differ at m.
3. Canonical 3-CNF conversion has four clauses per parity row, exactly three literals per clause, and eight occurrences per variable. Exhaust all assignments: CNF violation count equals parity violation count. Histograms match equation (3) coefficient by coefficient.
4. The more ambitious transfer to all individual CNF clause marginals is not expected. On K4 search for the smallest individual clause subset whose violation histogram distinguishes the two encodings with a fixed explicit clause ordering. A distinguishing pair is allowed and would preserve the limitation in DERIVATION-v1.
5. Evaluate exact contrast at t=1/2 (prediction 3^(-m)), and numerically evaluate the β threshold for c=1/2 at m=6,12,24,48. Numerical values merely illustrate equation (4).

Meaningful extension check reserved until after these pass: a disconnected graph should replace one global charge constraint by a charge constraint per component. The theorem uses connectedness exactly at D={0,1}; no disconnected instance is used to steer the main derivation.
