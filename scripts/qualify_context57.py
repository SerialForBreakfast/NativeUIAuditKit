"""Actual image-only prediction CLI parity for current and retained legacy models."""
import subprocess
import sys
import focus_direct_transition as d
from evaluate_direct_transition import parity


def run():
    base=d.h.ROOT/'reports/work/GLOBAL-CONTEXT-57'
    protocol=d.h.read(base/'diagnostic-ready/protocol.json')
    corpus=d.collect(protocol['sources'])
    rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,protocol['admission'])))
    row=next(r for r in rows if r['split']=='development')
    request=d.h.fresh(base/'prediction-request.json')
    d.h.write(request,dict(version='focus-direct-request-v1',before=row['images'][0],after=row['images'][1],
        context=dict(sameScene=True,settled=True,fresh=True)))
    evidence=[]
    for name in ('context57-dtm004','spatial56-dtm003','direct55-dtm002'):
        result=d.h.read(d.h.ROOT/'NativeUITrainer/focus_ring_runs'/name/'result.json')
        model=d.h.checked(d.h.ROOT,result['model']);output=d.h.fresh(base/(name+'-prediction.json'))
        completed=subprocess.run([sys.executable,str(d.h.ROOT/'scripts/focus_direct_transition.py'),
            '--request',str(request),'--model',str(model),'--output',str(output)],capture_output=True,text=True)
        d.h.require(completed.returncode==0,completed.stderr)
        expected=next(v['prediction'] for v in result['results'] if v['id']==row['id'])
        parity(expected,d.h.read(output))
        evidence.append(dict(model=result['model'],exitCode=completed.returncode,parity=True,output=d.h.ref(output)))
    t=d.torch_runtime()
    counts={name:sum(p.numel() for p in d.model(config).parameters())
        for name,config in [('local',d.SPATIAL_CONFIG),('context',d.CONTEXT_CONFIG)]}
    d.h.write(d.h.fresh(base/'cli-parity.json'),dict(evidence=evidence,parameterCounts=counts,
        trainingEligible=False,releaseEligible=False),sealed=True)
    print(dict(parityPassed=len(evidence),parameterCounts=counts))


if __name__=='__main__':run()
