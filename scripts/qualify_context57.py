"""Actual image-only prediction CLI parity for current and retained legacy models."""
import subprocess
import sys
import argparse
import re
import focus_direct_transition as d
from evaluate_direct_transition import parity


def protocol_rows(protocol):
    if protocol.get('preparedInputs') is not None:
        from prepare_transition_inputs import manifest
        prepared,corpus,rows=manifest(d.h.checked(d.h.ROOT,protocol['preparedInputs']))
        d.h.require(corpus['corpusSHA256']==protocol['corpusSHA256'] and
            prepared['admission']==protocol['admission'] and corpus['sources']==protocol['sources'],
            'parity_prepared_binding')
        return rows
    corpus=d.collect(protocol['sources'])
    return d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,protocol['admission'])))


def run(base=None,names=None,protocol_path=None):
    base=d.h.local(base) if base else d.h.ROOT/'reports/work/GLOBAL-CONTEXT-57'
    names=names or ('context57-dtm004','spatial56-dtm003','direct55-dtm002')
    protocol=d.h.read(d.h.local(protocol_path) if protocol_path else base/'diagnostic-ready/protocol.json')
    rows=protocol_rows(protocol)
    row=next(r for r in rows if r['split']=='development')
    request=d.h.fresh(base/'prediction-request.json')
    d.h.write(request,dict(version='focus-direct-request-v1',before=row['images'][0],after=row['images'][1],
        context=dict(sameScene=True,settled=True,fresh=True)))
    evidence=[]
    for name in names:
        d.h.require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',name),'run_name')
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


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base');p.add_argument('--runs',nargs='+');p.add_argument('--protocol')
    a=p.parse_args();run(a.base,a.runs,a.protocol)
