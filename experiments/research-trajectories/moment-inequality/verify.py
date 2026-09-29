from fractions import Fraction as F
from itertools import combinations
import json
from pathlib import Path
rows=[]
for n in range(2,13):
    v=[n-1]+[-1]*(n-1)
    p2=sum(x*x for x in v)
    fourth=F(sum(x**4 for x in v),p2*p2)
    e4=F(sum(a*b*c*d for a,b,c,d in combinations(v,4)),p2*p2)
    expected=F(n*n-3*n+3,n*(n-1))
    assert sum(v)==0 and p2==n*(n-1)
    assert fourth==expected
    assert fourth==F(1,2)-4*e4
    assert fourth-F(1,2)==F((n-2)*(n-3),2*n*(n-1))
    rows.append({'n':n,'unnormalized_vector':v,'normalizer_squared':p2,'sum_fourth':str(fourth),'e4':str(e4),'status':'exact rational checks passed'})
assert rows[2]['sum_fourth']=='7/12'
assert rows[2]['e4']=='-1/48'
Path(__file__).with_name('verification.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Exact checks passed for n=2,...,12; n=4 witness gives 7/12, e4=-1/48. Finite checks are supplementary.')
