"""Exact finite development checks for DERIVATION-v1.md; standard library only."""
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
import math
from pathlib import Path
from affine import dot, rank, count_by_rank, dual_vectors, rhs_mask, shared_self_check

OUT = Path(__file__).parent


def syndrome(rows, b, x):
    return sum((dot(row, x) ^ ((b >> i) & 1)) << i for i, row in enumerate(rows))


def signatures(rows, b, n):
    vs = [syndrome(rows, b, x) for x in range(1 << n)]
    return [Counter(v & subset for v in vs) for subset in range(1 << len(rows))]


def matrix_checks():
    matrices = pairs = comparisons = 0
    for rows in product(range(8), repeat=3):
        dual = list(dual_vectors(rows))
        sigs = [signatures(rows, b, 3) for b in range(8)]
        for b in range(8):
            for c in range(b, 8):
                candidates = [z.bit_count() for z in dual if dot(z, b ^ c)]
                d = min(candidates, default=math.inf)
                for k in range(4):
                    equal = all(sigs[b][s] == sigs[c][s]
                                for s in range(8) if s.bit_count() <= k)
                    assert equal == (k < d), (rows, b, c, k, d)
                    comparisons += 1
                if d != math.inf:
                    z = next(z for z in dual if z.bit_count() == d and dot(z, b ^ c))
                    assert set(sigs[b][z]).isdisjoint(sigs[c][z])
                pairs += 1
        matrices += 1
    return dict(matrices=matrices, rhs_pairs=pairs, threshold_comparisons=comparisons)


def incidence(vertices, edges):
    return [sum(1 << i for i, e in enumerate(edges) if v in e) for v in range(vertices)]


def prism(l):
    edges = set()
    for layer in range(2):
        for i in range(l):
            edges.add(tuple(sorted((layer*l+i, layer*l+(i+1)%l))))
    for i in range(l):
        edges.add((i, l+i))
    return 2*l, sorted(edges)


def cnf_for(rows, b, n):
    clauses = []
    for vertex, row in enumerate(rows):
        variables = [i for i in range(n) if row >> i & 1]
        assert len(variables) == 3
        for assignment in range(8):
            if assignment.bit_count() % 2 == ((b >> vertex) & 1):
                continue
            # Integer ±(i+1): positive literal is x_i; negative is not x_i.
            clause = tuple(-(i+1) if assignment >> j & 1 else i+1
                           for j, i in enumerate(variables))
            clauses.append(clause)
    return clauses


def violated(clause, x):
    return not any(bool(x >> (abs(lit)-1) & 1) == (lit > 0) for lit in clause)


def graph_checks(name, vertices, edges):
    rows, n, m = incidence(vertices, edges), len(edges), vertices
    assert rank(rows) == m-1
    even, odd = signatures(rows, 0, n), signatures(rows, 1, n)
    for subset in range((1 << m)-1):
        assert even[subset] == odd[subset]
        assert len(even[subset]) == 1 << subset.bit_count()
        assert set(even[subset].values()) == {1 << (n-subset.bit_count())}
    histograms, clause_masks = [], []
    for b in (0, 1):
        clauses = cnf_for(rows, b, n)
        assert len(clauses) == 4*m
        assert Counter(abs(lit) for clause in clauses for lit in clause) == Counter({i+1:8 for i in range(n)})
        hist, masks = Counter(), []
        for x in range(1 << n):
            energy = syndrome(rows, b, x).bit_count()
            mask = sum(int(violated(c, x)) << i for i, c in enumerate(clauses))
            assert mask.bit_count() == energy
            hist[energy] += 1
            masks.append(mask)
        prediction = {j: (1 << (n-m+1))*math.comb(m,j)
                      for j in range(m+1) if j % 2 == b}
        assert dict(sorted(hist.items())) == prediction
        histograms.append(hist)
        clause_masks.append(masks)
        rhs = [(b >> i) & 1 for i in range(m)]
        assert count_by_rank(rows, rhs, n) == hist.get(0, 0)
        dimacs = f'p cnf {n} {len(clauses)}\n' + ''.join(' '.join(map(str,c))+' 0\n' for c in clauses)
        (OUT/f'{name}-{"even" if b==0 else "odd"}.cnf').write_text(dimacs)
    moments = [[sum(count*j**degree for j,count in hist.items()) for degree in range(m+1)]
               for hist in histograms]
    assert moments[0][:-1] == moments[1][:-1]
    assert moments[0][-1] != moments[1][-1]
    t = Fraction(1,2)
    zs = [sum(count*t**j for j,count in hist.items()) for hist in histograms]
    assert (zs[0]-zs[1])/(zs[0]+zs[1]) == Fraction(1,3**m)
    result = dict(name=name, vertices=m, edges=n, clauses=4*m,
                  proper_subsets_checked=(1<<m)-1,
                  even_histogram=dict(sorted(histograms[0].items())),
                  odd_histogram=dict(sorted(histograms[1].items())),
                  raw_moments_equal_through=m-1,
                  first_different_raw_moment=m,
                  total_solution_counts=[hist.get(0,0) for hist in histograms],
                  exact_contrast_at_half=str(Fraction(1,3**m)))
    if name == 'k4':
        found = None
        for size in range(1,4):
            for indexes in combinations(range(4*m),size):
                sub = sum(1<<i for i in indexes)
                a,c = (Counter(v & sub for v in masks) for masks in clause_masks)
                if a != c:
                    found = dict(indices_zero_based=indexes, size=size,
                                 even_histogram=dict(sorted(a.items())),
                                 odd_histogram=dict(sorted(c.items())),
                                 even_clauses=[cnf_for(rows,0,n)[i] for i in indexes],
                                 odd_clauses=[cnf_for(rows,1,n)[i] for i in indexes])
                    break
            if found:
                break
        assert found is not None
        result['individual_clause_transfer_failure'] = found
    return result


def disconnected_check():
    # New extension case: two triangles. A component-local odd charge is visible
    # at order 3, not at the full number of vertices (6).
    edges = [(0,1),(1,2),(0,2),(3,4),(4,5),(3,5)]
    rows = incidence(6,edges)
    dual = list(dual_vectors(rows))
    assert len(dual) == 4
    thresholds = {}
    for b in (0,1,(1<<0)|(1<<3)):
        d = min((z.bit_count() for z in dual if dot(z,b)),default=math.inf)
        a,c=signatures(rows,0,6),signatures(rows,b,6)
        for k in range(7):
            assert all(a[s]==c[s] for s in range(64) if s.bit_count()<=k) == (k<d)
        thresholds[str(b)] = 'infinity' if d==math.inf else d
    return dict(components=2, thresholds=thresholds)


def main():
    report = {'shared_rank_checks':shared_self_check(), 'matrix_checks':matrix_checks()}
    graphs = [('k4',4,list(combinations(range(4),2)))]
    graphs += [(f'prism{l}',*prism(l)) for l in (3,4)]
    report['graphs']=[graph_checks(*g) for g in graphs]
    report['thermal_half_contrast_threshold'] = [
        {'m':m,'beta_for_contrast_half':math.log((1+0.5**(1/m))/(1-0.5**(1/m)))}
        for m in (6,12,24,48)]
    report['disconnected_extension']=disconnected_check()
    report['status']='All assertions passed.'
    (OUT/'check-output.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
