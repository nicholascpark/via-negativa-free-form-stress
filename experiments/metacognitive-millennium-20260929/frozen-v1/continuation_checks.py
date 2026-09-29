from itertools import product, combinations_with_replacement
from pathlib import Path
import json
from affine import count_by_rank, violations
from checks import violated


def affine_clause_count(rows, rhs, n, clauses):
    answer=0
    for subset in range(1 << len(clauses)):
        extended_rows=list(rows)
        extended_rhs=list(rhs)
        for i, clause in enumerate(clauses):
            if subset >> i & 1:
                for lit in clause:
                    extended_rows.append(1 << (abs(lit)-1))
                    extended_rhs.append(int(lit<0))
        value=count_by_rank(extended_rows,extended_rhs,n)
        answer += -value if subset.bit_count() & 1 else value
    return answer


def brute(rows,rhs,n,clauses):
    return sum(not any(violations(rows,rhs,x)) and not any(violated(c,x) for c in clauses)
               for x in range(1 << n))


def main():
    clauses=[tuple(-(i+1) if mask>>i&1 else i+1 for i in range(3)) for mask in range(8)]
    count=0
    for rows in product(range(8),repeat=2):
        for rhs in product(range(2),repeat=2):
            for pair in combinations_with_replacement(clauses,2):
                assert affine_clause_count(rows,rhs,3,pair)==brute(rows,rhs,3,pair)
                count+=1
    edgecases=[]
    for cs in [[],[()],[ (1,-1) ],[(1,),(1,)],[(1,),(-1,)],[(1,1)]]:
        actual=affine_clause_count([],[],1,cs)
        assert actual==brute([],[],1,cs)
        edgecases.append({'clauses':cs,'count':actual})
    disjoint=[]
    for q in range(6):
        cs=[(3*i+1,3*i+2,3*i+3) for i in range(q)]
        value=affine_clause_count([],[],3*q,cs)
        assert value==7**q
        assert value==brute([],[],3*q,cs)
        disjoint.append({'q':q,'count':value,'expanded_terms':1<<q})
    output={'exhaustive_affine_two_clause_cases':count,'edgecases':edgecases,
            'disjoint_clause_family':disjoint,'status':'All assertions passed.'}
    (Path(__file__).parent/'continuation-output.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))


if __name__=='__main__':
    main()
