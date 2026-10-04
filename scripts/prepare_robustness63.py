"""Bind one augmentation experiment to retained full-fit evidence and exact roles."""
import argparse
from pathlib import Path
import focus_direct_transition as d

BASE=d.h.ROOT/'reports/work/ROBUSTNESS-63'


def verify_gate(reference,corpus,rows):
    d.h.require(reference is not None,'missing_full_fit_gate')
    evaluation=d.h.sealed(d.h.checked(d.h.ROOT,reference),'direct-checkpoint-evaluation-v1')
    result=d.h.read(d.h.checked(d.h.ROOT,evaluation['source']))
    protocol=d.h.read(d.h.checked(d.h.ROOT,result['protocol']))
    d.h.require(protocol['configuration']==d.FULL_FIT_CONFIG and
        protocol['corpusSHA256']==corpus['corpusSHA256'] and evaluation['model']==result['model'],'full_fit_gate_binding')
    d.h.checked(d.h.ROOT,result['model'])
    pins=d.pins();previous=protocol['pins']
    d.h.require(pins['dependencies']==previous['dependencies'] and pins['python']==previous['python'],'full_fit_runtime_changed')
    architecture='scripts/focus_spatial_transition.py'
    d.h.require(next(r for r in previous['code'] if r['path']==architecture)==
        d.h.ref(d.h.ROOT/architecture),'full_fit_architecture_changed')
    train={r['id'] for r in rows if r['split']=='train'}
    d.h.require(len(train)==24 and set(result['trainingIDs'])==train,'full_fit_membership')
    scored=[r for r in evaluation['results'] if r['split']=='train']
    d.h.require(len(scored)==24 and {r['id'] for r in scored}==train and
        all(r['bothBoxesCorrect'] and r['rawChangeCorrect'] for r in scored),'full_fit_gate_failed')
    return sorted(train)


def prepare(matched_exposure=False):
    base=d.h.ROOT/'reports/work/EXPOSURE-64' if matched_exposure else BASE
    name='exposure64-dtm011' if matched_exposure else 'robustness63-dtm010'
    config=d.EXPOSURE_CONFIG if matched_exposure else d.TRANSLATION_CONFIG
    directory=d.h.fresh(base/'ready')
    source=d.h.read(d.h.ROOT/'reports/work/FIT-61/ready/protocol.json')
    corpus=d.collect(source['sources']);rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,source['admission'])))
    gate=d.h.ref(d.h.ROOT/'reports/work/FIT-61/evaluation.json');verify_gate(gate,corpus,rows)
    directory.mkdir(parents=True)
    protocol=dict(version=d.VERSION,sources=source['sources'],corpusSHA256=corpus['corpusSHA256'],
        admission=source['admission'],configuration=config,
        implementation=d.h.ref(Path(d.__file__)),pins=d.pins(),diagnosticGate=gate)
    protocol['protocolSHA256']=d.digest(protocol);d.h.write(directory/'protocol.json',protocol)
    d.h.write(directory/'approval.json',dict(version='focus-direct-approval-v1',approved=True,
        protocolSHA256=protocol['protocolSHA256'],arm=d.ARM,runName=name,
        decisionReference=('2026-10-03 active goal and standing local experiment envelope: EXPOSURE-64 one600epoch matched-view-exposure comparison, same24/5roles,2GiB/no wall-time cap.' if matched_exposure else
            '2026-10-03 active goal and standing local experiment envelope: ROBUSTNESS-63 one120epoch paired-translation comparison, same24/5roles,2GiB/no wall-time cap.')))
    print(protocol['protocolSHA256'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--matched-exposure',action='store_true')
    prepare(p.parse_args().matched_exposure)
