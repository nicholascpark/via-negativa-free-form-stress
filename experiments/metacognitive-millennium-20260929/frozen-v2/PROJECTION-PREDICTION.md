# Refinement frozen before the second run

The first run confirmed the predictions in PREDICTIONS.md and exposed the converse one-parity-row boundary-table blowup. Do not treat these observations as unexposed checks of the refinement.

New operation: after each clause insertion, sum every variable absent from all remaining clauses directly inside each affine indicator, multiplying by the uniform affine fiber size, then merge canonical projected affine sets. The initial affine system can retain arbitrary couplings; unlike a raw boundary table, the operation need not enumerate its solutions.

Derived prediction: projection of A_E z + A_B y=b is 2^(|E|-rank A_E) times the indicator of L A_B y=L b, where the rows of L span ker(A_E^T). On the star the intermediate function of s becomes 2^j+(1-2^j)1[s=0], so at most two nonzero affine keys survive projection. Pure affine input uses at most one key and is counted by Gaussian elimination. Recheck all prior development cases against enumeration; this is a repair replay, not an independent validation trial. No general state-count bound is predicted.
