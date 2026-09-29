"""Exact finite GF(2) helpers. Rows are nonnegative Python integer bit masks."""
from itertools import product


def dot(a, b):
    return (a & b).bit_count() & 1


def rank(rows):
    basis = {}
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def count_by_rank(rows, rhs, n):
    assert len(rows) == len(rhs)
    r = rank(rows)
    augmented = [row | ((bit & 1) << n) for row, bit in zip(rows, rhs)]
    return 0 if rank(augmented) != r else 1 << (n - r)


def violations(rows, rhs, x):
    return tuple(dot(row, x) ^ bit for row, bit in zip(rows, rhs))


def brute_count(rows, rhs, n):
    return sum(not any(violations(rows, rhs, x)) for x in range(1 << n))


def dual_vectors(rows):
    for z in range(1 << len(rows)):
        total = 0
        for i, row in enumerate(rows):
            if (z >> i) & 1:
                total ^= row
        if total == 0:
            yield z


def rhs_mask(rhs):
    return sum((bit & 1) << i for i, bit in enumerate(rhs))


def shared_self_check():
    # Exhaust every 2-by-3 binary matrix and every right hand side.
    checked = 0
    for rows in product(range(8), repeat=2):
        for rhs in product(range(2), repeat=2):
            actual = brute_count(rows, rhs, 3)
            assert count_by_rank(rows, rhs, 3) == actual
            dual_sum = sum((-1) ** dot(z, rhs_mask(rhs)) for z in dual_vectors(rows))
            assert (1 << 2) * actual == (1 << 3) * dual_sum
            checked += 1
    return checked


if __name__ == '__main__':
    print(f'Shared rank/dual count check: {shared_self_check()} systems passed.')
