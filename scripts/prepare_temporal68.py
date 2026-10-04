"""One explicit temporal-head comparison on already admitted data."""
from pathlib import Path
import focus_direct_transition as d
from prepare_data67 import verify_gate as expanded_gate


def verify_gate(reference,corpus,rows):
    d.h.require(reference is not None,'missing_temporal_gate')
    report=d.h.sealed(d.h.checked(d.h.ROOT,reference),'data67-batched-comparison-v1')
    result=d.h.read(d.h.checked(d.h.ROOT,report['candidate']))
    protocol=d.h.read(d.h.checked(d.h.ROOT,result['protocol']))
    d.h.require(protocol['configuration']==d.EXPOSURE_CONFIG and report['models']['DTM012']==result['model'] and
        report['corpusSHA256']==protocol['corpusSHA256']==corpus['corpusSHA256'],'temporal_gate_binding')
    d.h.checked(d.h.ROOT,result['model'])
    train={r['id'] for r in rows if r['split']=='train'}
    scores=[r for r in report['results'] if r['model']=='DTM012' and r['condition']=='baseline' and r['group']!='development']
    d.h.require(len(train)==len(scores)==32 and set(result['trainingIDs'])==train and
        {r['id'] for r in scores}==train and all(r['bothBoxesCorrect'] and r['rawChangeCorrect'] for r in scores),
        'temporal_reference_fit_failed')
    return protocol


def prepare():
    from prepare_transition_inputs import prepare as prepare_inputs,manifest
    base=d.h.fresh(d.h.ROOT/'reports/work/TEMPORAL-68/ready');base.mkdir(parents=True)
    source=d.h.ROOT/'reports/work/GENERALIZATION-65/admission'
    prepare_inputs(source/'corpus.json',source/'admission.json',d.h.ROOT/'.build/temporal68-bank')
    prepared=d.h.ROOT/'.build/temporal68-bank/manifest.json';inputs,corpus,rows=manifest(prepared)
    prior=d.h.read(d.h.ROOT/'reports/work/DATA-67/ready/protocol.json')
    expanded_gate(prior['expandedGate'],corpus,rows,inputs['admission'])
    gate=d.h.ref(d.h.ROOT/'reports/work/DATA-67/comparison.json');verify_gate(gate,corpus,rows)
    protocol=dict(version=d.VERSION,sources=corpus['sources'],corpusSHA256=corpus['corpusSHA256'],
        admission=inputs['admission'],configuration=d.TEMPORAL_CONFIG,implementation=d.h.ref(Path(d.__file__)),
        pins=d.pins(),expandedGate=prior['expandedGate'],temporalGate=gate,preparedInputs=d.h.ref(prepared))
    protocol['protocolSHA256']=d.digest(protocol);d.h.write(base/'protocol.json',protocol)
    d.h.write(base/'approval.json',dict(version='focus-direct-approval-v1',approved=True,
        protocolSHA256=protocol['protocolSHA256'],arm=d.ARM,runName='temporal68-dtm013',
        decisionReference='2026-10-03 active goal and standing experiment envelope: TEMPORAL-68 explicitly includes one absolute-difference change-head architecture comparison,600epochs,unchanged32/5roles,2GiB/no wall-time cap; no capture/export/promotion.'))
    print(protocol['protocolSHA256'])


if __name__=='__main__':prepare()
