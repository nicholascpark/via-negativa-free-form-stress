"""Six-reading calibration calculator plus SYNTHETIC development checks.
No scientific packages, services, random draws, or actual measurements required.
The error envelope is conditional sensitivity, not a confidence interval.
"""
from fractions import Fraction as F
import json
from pathlib import Path
import sys

def rational(x):
    if x is None: raise ValueError('Missing reading; no observations may be invented.')
    return F(str(x))

def evaluate(data, epsilon=F(1,5)):
    q=rational(data['known_standard_quantity'])
    if q<=0 or epsilon<0: raise ValueError('Q must be positive; epsilon nonnegative.')
    arms={}
    for name in ('absent','present'):
        d=data[name]; b,s,c=(rational(d[k]) for k in ('blank','sample','standard'))
        num=s-b; den=c-b; delta=2*epsilon
        if den<=delta:
            return {'status':'inconclusive: calibration increment too small for specified sensitivity bound'}
        if num<0:
            return {'status':'inconclusive: sample below blank under nonnegative-production model'}
        # Outward bound; ignores shared-blank correlation, so may be conservative.
        arms[name]={'p':q*num/den,'g':den/q,
                    'p_interval':(q*max(F(0),num-delta)/(den+delta),q*(num+delta)/(den-delta))}
    a,b=arms['absent'],arms['present']
    interval=None if a['p_interval'][0]<=0 else (b['p_interval'][0]/a['p_interval'][1],b['p_interval'][1]/a['p_interval'][0])
    return {'status':'calculated under unverified transfer/linearity assumptions',
            'production_ratio':b['p']/a['p'] if a['p'] else None,
            'gain_ratio':b['g']/a['g'],'production_ratio_sensitivity':interval,
            'arms':arms}

def fixture(p1,g1,b0=0,b1=0,standard_g1=None):
    q=F(4); p0=F(2); g0=F(1)
    def arm(p,g,b,cg):
        p,g,b,cg=map(rational,(p,g,b,cg))
        return {'blank':b,'sample':b+g*p,'standard':b+cg*q}
    return {'provenance':'synthetic; not measured','known_standard_quantity':q,
            'absent':arm(p0,g0,b0,g0),
            'present':arm(p1,g1,b1,g1 if standard_g1 is None else standard_g1)}

def encode(obj):
    if isinstance(obj,F): return str(obj)
    raise TypeError(type(obj).__name__)

def selfcheck():
    cases=[('production_only',fixture(4,1),F(2),F(1)),
           ('gain_only',fixture(2,2),F(1),F(2)),
           ('cancellation',fixture(4,'0.5'),F(2),F(1,2)),
           ('small_effect',fixture('2.1',1),F(21,20),F(1)),
           ('background_change',fixture(4,1,'0.5','0.8'),F(2),F(1))]
    out=[]
    for name,data,rp,rg in cases:
        result=evaluate(data)
        assert result['production_ratio']==rp and result['gain_ratio']==rg
        lo,hi=result['production_ratio_sensitivity']
        if name in ('production_only','background_change'): assert lo>1
        else: assert lo<=1<=hi
        out.append({'name':name,'input':data,'result':result,'check':'passed'})
    weak=evaluate(fixture(2,'0.05'))
    assert weak['status'].startswith('inconclusive')
    out.append({'name':'weak_calibration','result':weak,'check':'passed'})
    mismatch=evaluate(fixture(2,2,standard_g1=1))
    assert mismatch['production_ratio']==2
    out.append({'name':'matrix_mismatch','result':mismatch,
                'true_production_ratio':1,'check':'expected failure of calibration transfer reproduced; false production signal'})
    dest=Path(__file__).with_name('synthetic-results.json')
    dest.write_text(json.dumps({'version':'assay-v1','kind':'synthetic development checks','cases':out},default=encode,indent=2)+'\n')
    print('7 synthetic checks passed, including a reproduced calibration-transfer false positive. No lab measurements or empirical conclusion.')
    for row in out[:5]:
        r=row['result']; bounds=tuple(round(float(v),4) for v in r['production_ratio_sensitivity'])
        print(row['name'], 'production ratio',str(r['production_ratio']),'sensitivity',bounds)

if __name__=='__main__':
    if len(sys.argv)==2:
        print(json.dumps(evaluate(json.loads(Path(sys.argv[1]).read_text())),default=encode,indent=2))
    else: selfcheck()
