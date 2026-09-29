"""Exact, synthetic development checks; Python standard library only."""
from collections import defaultdict
from itertools import product
import json
import random
import time
from pathlib import Path


def rref(rows, n):
    """Canonical affine solution set; None is inconsistency."""
    a = [mask | (rhs << n) for mask, rhs in rows]
    p = 0
    for col in range(n):
        k = next((k for k in range(p, len(a)) if a[k] >> col & 1), None)
        if k is None:
            continue
        a[p], a[k] = a[k], a[p]
        for k in range(len(a)):
            if k != p and (a[k] >> col & 1):
                a[k] ^= a[p]
        p += 1
    if any(row == 1 << n for row in a):
        return None
    return tuple((row & ((1 << n) - 1), row >> n) for row in a[:p])


def signed(n, rows, clauses):
    root = rref(rows, n)
    states = {} if root is None else {root: 1}
    trace = [len(states)]
    for clause in clauses:
        nxt = defaultdict(int)
        # literal (variable, satisfying value); falsification fixes the opposite
        false_rows = [(1 << v, 1 - val) for v, val in clause]
        for key, coeff in states.items():
            nxt[key] += coeff
            child = rref(list(key) + false_rows, n)
            if child is not None:
                nxt[child] -= coeff
        states = {k: v for k, v in nxt.items() if v}
        trace.append(len(states))
    count = sum(coeff * (1 << (n - len(key))) for key, coeff in states.items())
    return count, trace


def project_affine(key, eliminate, n):
    """Sum eliminated variables: return projected key and constant fiber size."""
    a = [mask | (rhs << n) for mask, rhs in key]
    p = 0
    for col in eliminate:
        k = next((k for k in range(p, len(a)) if a[k] >> col & 1), None)
        if k is None:
            continue
        a[p], a[k] = a[k], a[p]
        for k in range(len(a)):
            if k != p and a[k] >> col & 1:
                a[k] ^= a[p]
        p += 1
    remaining = [(row & ((1 << n) - 1), row >> n) for row in a[p:]]
    return rref(remaining, n), 1 << (len(eliminate) - p)


def projected_signed(n, rows, clauses):
    root = rref(rows, n)
    states = {} if root is None else {root: 1}
    active = set(range(n))
    trace = []
    def forget(future):
        nonlocal states, active
        used = {v for c in future for v, _ in c}
        eliminate = sorted(active - used)
        nxt = defaultdict(int)
        for key, coeff in states.items():
            projected, multiplicity = project_affine(key, eliminate, n)
            if projected is not None:
                nxt[projected] += coeff * multiplicity
        states = {k: v for k, v in nxt.items() if v}
        active -= set(eliminate)
        trace.append(len(states))
    forget(clauses)
    for j, clause in enumerate(clauses):
        nxt = defaultdict(int)
        false_rows = [(1 << v, 1 - val) for v, val in clause]
        for key, coeff in states.items():
            nxt[key] += coeff
            child = rref(list(key) + false_rows, n)
            if child is not None:
                nxt[child] -= coeff
        states = {k: v for k, v in nxt.items() if v}
        forget(clauses[j+1:])
    assert not active
    assert all(not key for key in states)
    return states.get((), 0), trace


def factors(n, rows, clauses):
    fs = []
    for mask, rhs in rows:
        fs.append((tuple(v for v in range(n) if mask >> v & 1), ('xor', rhs)))
    for clause in clauses:
        fs.append((tuple(sorted({v for v, _ in clause})), ('or', tuple(clause))))
    return fs


def accepts(scope, body, assignment):
    if body[0] == 'xor':
        return sum(assignment[v] for v in scope) % 2 == body[1]
    return any(assignment[v] == value for v, value in body[1])


def brute(n, rows, clauses):
    fs = factors(n, rows, clauses)
    return sum(all(accepts(scope, body, dict(enumerate(x))) for scope, body in fs)
               for x in product((0, 1), repeat=n))


def boundary_dp(n, rows, clauses, order=None):
    """Count by exactly summing variables no unprocessed factor can observe."""
    order = list(range(n)) if order is None else list(order)
    assert sorted(order) == list(range(n))
    pos = {v: i for i, v in enumerate(order)}
    fs = factors(n, rows, clauses)
    if not all(accepts(scope, body, {}) for scope, body in fs if not scope):
        return 0, [0], [0]
    closing = defaultdict(list)
    for scope, body in fs:
        if scope:
            closing[max(pos[v] for v in scope)].append((scope, body))
    old_boundary = []
    table = {(): 1}
    trace, widths = [1], [0]
    for i, variable in enumerate(order):
        new_boundary = sorted({v for scope, _ in fs
                               if any(pos[u] > i for u in scope)
                               for v in scope if pos[v] <= i})
        nxt = defaultdict(int)
        for bits, weight in table.items():
            assignment = dict(zip(old_boundary, bits))
            for bit in (0, 1):
                assignment[variable] = bit
                if all(accepts(scope, body, assignment) for scope, body in closing[i]):
                    key = tuple(assignment[v] for v in new_boundary)
                    nxt[key] += weight
        table = dict(nxt)
        old_boundary = new_boundary
        trace.append(len(table))
        widths.append(len(new_boundary))
    return table.get((), 0), trace, widths


def component_count(n, rows, clauses):
    parent = list(range(n))
    def find(v):
        while parent[v] != v:
            v = parent[v]
        return v
    def join(a, b):
        parent[find(a)] = find(b)
    for scope, body in factors(n, rows, clauses):
        if not scope and not accepts(scope, body, {}):
            return 0, []
        for v in scope[1:]:
            join(scope[0], v)
    groups = defaultdict(list)
    for v in range(n):
        groups[find(v)].append(v)
    total, records = 1, []
    for vs in groups.values():
        relabel = {v: i for i, v in enumerate(vs)}
        local_rows = []
        for mask, rhs in rows:
            if mask and any(mask >> v & 1 for v in vs):
                local_rows.append((sum(1 << relabel[v] for v in vs if mask >> v & 1), rhs))
        local_clauses = [tuple((relabel[v], val) for v, val in c)
                         for c in clauses if c and c[0][0] in relabel]
        count, trace = signed(len(vs), local_rows, local_clauses)
        total *= count
        records.append({'variables': len(vs), 'trace': trace})
    return total, records


def verify(n, rows, clauses, counters):
    expected = brute(n, rows, clauses)
    actual, _ = signed(n, rows, clauses)
    factored, _ = component_count(n, rows, clauses)
    direct, _, _ = boundary_dp(n, rows, clauses)
    reversed_, _, _ = boundary_dp(n, rows, clauses, list(reversed(range(n))))
    projected, _ = projected_signed(n, rows, clauses)
    assert (actual, factored, direct, reversed_, projected) == (expected,) * 5, (n, rows, clauses)
    counters['generic_instances'] += 1


def main():
    start = time.perf_counter()
    counters = {'generic_instances': 0}
    star_records, disjoint_records = [], []
    for q in range(9):
        clauses = [((0, 1), (i, 1)) for i in range(1, q + 1)]
        count, trace = signed(q + 1, [], clauses)
        dp_count, dp_trace, widths = boundary_dp(q + 1, [], clauses)
        fac_count, components = component_count(q + 1, [], clauses)
        projected_count, projected_trace = projected_signed(q + 1, [], clauses)
        assert count == dp_count == fac_count == projected_count == brute(q + 1, [], clauses) == 2**q + 1
        assert max(projected_trace) <= 2
        assert trace == [2**j for j in range(q + 1)]
        assert max(widths) <= 1 and max(dp_trace) <= 2
        if q:
            assert len(components) == 1
        star_records.append({'q': q, 'count': count, 'signed_trace': trace,
                             'boundary_trace': dp_trace, 'width': max(widths),
                             'projected_signed_trace': projected_trace})
        disjoint = [((2*i, 1), (2*i+1, 1)) for i in range(q)]
        count, trace = signed(2*q, [], disjoint)
        fac_count, components = component_count(2*q, [], disjoint)
        dp_count, _, _ = boundary_dp(2*q, [], disjoint)
        assert count == fac_count == dp_count == 3**q
        assert trace == [2**j for j in range(q + 1)]
        assert all(max(c['trace']) == 2 for c in components)
        disjoint_records.append({'q': q, 'count': count, 'global_keys': trace[-1],
                                 'component_count': len(components),
                                 'sum_component_peak_keys': sum(max(c['trace']) for c in components)})

    # Exhaust all one-row affine systems and pairs of boundary-sensitive clauses at n=2.
    clause_pool = [(), ((0, 1),), ((0, 0),), ((1, 1),), ((1, 0),),
                   ((0, 1), (0, 0)), ((0, 1), (1, 1)), ((0, 1), (0, 1))]
    for mask in range(4):
        for rhs in (0, 1):
            for c1, c2 in product(clause_pool, repeat=2):
                verify(2, [(mask, rhs)], [c1, c2], counters)
    rng = random.Random(6292026)
    for _ in range(400):
        n = rng.randrange(1, 7)
        rows = [(rng.randrange(1 << n), rng.randrange(2)) for _ in range(rng.randrange(5))]
        clauses = [tuple((rng.randrange(n), rng.randrange(2)) for _ in range(rng.randrange(5)))
                   for _ in range(rng.randrange(9))]
        verify(n, rows, clauses, counters)
    verify(0, [], [], counters)
    verify(0, [(0, 1)], [], counters)
    verify(0, [], [()], counters)

    # Transfer-obligation check, reserved until all tests above pass:
    # one long parity is easy by elimination but raw variable-boundary DP expands.
    parity_records = []
    for n in range(1, 10):
        rows = [((1 << n) - 1, 0)]
        expected = 1 << (n - 1)
        count, trace, widths = boundary_dp(n, rows, [])
        assert count == signed(n, rows, [])[0] == expected
        projected_count, projected_trace = projected_signed(n, rows, [])
        assert projected_count == expected and max(projected_trace) == 1
        assert max(widths) == n - 1 and max(trace) == 1 << (n - 1)
        parity_records.append({'n': n, 'count': count, 'width': max(widths),
                               'peak_boundary_states': max(trace), 'signed_states': 1,
                               'projected_signed_trace': projected_trace})
    result = {'status': 'all checks passed', 'seed': 6292026, **counters,
              'star': star_records, 'disjoint': disjoint_records,
              'reserved_parity_transfer_check': parity_records,
              'elapsed_seconds': time.perf_counter() - start}
    Path(__file__).with_name('check-output.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
