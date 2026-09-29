"""Independent finite checks of the practitioner's stated affine identities.

No practitioner implementation is imported. This is development validation,
not an independent task, a proof assistant, or evidence of skill efficacy.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json


def bits(width):
    return list(product((0, 1), repeat=width))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b)) % 2


def run():
    counts = {"matrices": 0, "threshold_comparisons": 0, "partition_identities": 0}
    for m, n in ((0, 0), (1, 0), (2, 3), (3, 2), (4, 1)):
        xs, rhs = bits(n), bits(m)
        subsets = [j for k in range(m + 1) for j in combinations(range(m), k)]
        for flat in product((0, 1), repeat=m * n):
            matrix = [flat[i * n:(i + 1) * n] for i in range(m)]
            dual = [z for z in rhs if all(sum(z[i] * matrix[i][j] for i in range(m)) % 2 == 0 for j in range(n))]
            samples = {b: [tuple(dot(row, x) ^ bi for row, bi in zip(matrix, b)) for x in xs] for b in rhs}
            signatures = {b: {j: Counter(tuple(v[i] for i in j) for v in vs) for j in subsets} for b, vs in samples.items()}
            for i, b in enumerate(rhs):
                for c in rhs[i:]:
                    delta = tuple(x ^ y for x, y in zip(b, c))
                    distances = [sum(z) for z in dual if dot(z, delta)]
                    d = min(distances, default=float("inf"))
                    for k in range(m + 1):
                        actual = all(signatures[b][j] == signatures[c][j] for j in subsets if len(j) <= k)
                        assert actual == (k < d), (matrix, b, c, k)
                        counts["threshold_comparisons"] += 1
                for t in (Fraction(0), Fraction(1, 2), Fraction(1), Fraction(2)):
                    enumerated = sum(t ** sum(v) for v in samples[b])
                    transformed = Fraction(2) ** (n - m) * sum(
                        (-1) ** dot(z, b) * (1 + t) ** (m - sum(z)) * (1 - t) ** sum(z)
                        for z in dual
                    )
                    assert enumerated == transformed, (matrix, b, t)
                    counts["partition_identities"] += 1
            counts["matrices"] += 1
    return {"status": "passed", "scope": "exact finite rectangular and degenerate affine cases", **counts}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
