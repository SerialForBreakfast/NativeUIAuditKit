"""Explicit historical-gate compatibility and one full-corpus convergence run."""
import argparse
import ast
import hashlib
from pathlib import Path
import focus_direct_transition as d
from prepare_spatial56 import candidate_gate

BASE=d.h.ROOT/'reports/work/FIT-61'
NUMERICAL=('geometry','pixels','encode','target_box','image_box','collect','admitted',
           'torch_runtime','model','training_rows','fit','infer')


def numerical():
    tree=ast.parse(Path(d.__file__).read_text())
    return {v.name:hashlib.sha256(ast.dump(v,include_attributes=False).encode()).hexdigest()
        for v in tree.body if isinstance(v,ast.FunctionDef) and v.name in NUMERICAL}


def snapshot():
    result=d.h.read(d.h.ROOT/'NativeUITrainer/focus_ring_runs/geometry60-dtm007/result.json')
    protocol=d.h.read(d.h.checked(d.h.ROOT,result['protocol']))
    d.h.require(protocol['pins']==d.pins(),'snapshot_requires_original_sources')
    BASE.mkdir(parents=True,exist_ok=True)
    d.h.write(d.h.fresh(BASE/'compatibility-baseline.json'),dict(version='fit61-baseline-v1',**d.h.FLAGS,
        source=d.h.ref(Path(d.__file__)),pins=d.pins(),numerical=numerical(),
        configuration=d.LOGIT_DIAGNOSTIC,gate=d.h.ref(d.h.ROOT/'reports/work/GEOMETRY-60/diagnostic-evaluation.json')),sealed=True)


def verify_gate(reference,corpus,rows):
    baseline=d.h.sealed(d.h.checked(d.h.ROOT,reference),'fit61-baseline-v1')
    current=d.pins();old=baseline['pins']
    d.h.require(current['dependencies']==old['dependencies'] and current['python']==old['python'],'runtime_changed')
    previous={r['path']:r for r in old['code']};now={r['path']:r for r in current['code']}
    allowed={'scripts/focus_direct_transition.py','scripts/evaluate_direct_transition.py','scripts/prepare_fit61.py'}
    d.h.require(set(previous)<=set(now) and all(previous.get(k)==v or k in allowed for k,v in now.items()),'unreviewed_code_change')
    d.h.require(baseline['numerical']==numerical() and len(numerical())==len(NUMERICAL),'numerical_behavior_changed')
    d.h.require(baseline['configuration']==d.LOGIT_DIAGNOSTIC and baseline['source']==previous['scripts/focus_direct_transition.py'],'baseline_binding')
    evaluation=d.h.sealed(d.h.checked(d.h.ROOT,baseline['gate']),'direct-checkpoint-evaluation-v1')
    result=d.h.read(d.h.checked(d.h.ROOT,evaluation['source']))
    protocol=d.h.read(d.h.checked(d.h.ROOT,result['protocol']))
    d.h.require(protocol['pins']==old and protocol['configuration']==d.LOGIT_DIAGNOSTIC and
        protocol['corpusSHA256']==corpus['corpusSHA256'] and evaluation['model']==result['model'],'historical_gate_binding')
    d.h.checked(d.h.ROOT,result['model'])
    selected=candidate_gate(evaluation,rows)
    d.h.require(sorted(result['trainingIDs'])==selected,'historical_fit_ids')
    return selected


def prepare():
    directory=d.h.fresh(BASE/'ready')
    source=d.h.read(d.h.ROOT/'reports/work/GEOMETRY-60/candidate-ready/protocol.json')
    corpus=d.collect(source['sources']);rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,source['admission'])))
    gate=d.h.ref(BASE/'compatibility-baseline.json');verify_gate(gate,corpus,rows)
    directory.mkdir(parents=True)
    protocol=dict(version=d.VERSION,sources=source['sources'],corpusSHA256=corpus['corpusSHA256'],
        admission=source['admission'],configuration=d.FULL_FIT_CONFIG,implementation=d.h.ref(Path(d.__file__)),
        pins=d.pins(),diagnosticGate=gate)
    protocol['protocolSHA256']=d.digest(protocol);d.h.write(directory/'protocol.json',protocol)
    d.h.write(directory/'approval.json',dict(version='focus-direct-approval-v1',approved=True,
        protocolSHA256=protocol['protocolSHA256'],arm=d.ARM,runName='fit61-dtm009',
        decisionReference='2026-10-03 active goal continuation: FIT-61 one fresh120epoch all24fit, fixed-last,2GiB/no wall-time cap.'))
    print(protocol['protocolSHA256'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['snapshot','prepare']);a=p.parse_args()
    snapshot() if a.mode=='snapshot' else prepare()
