"""Freeze the assigned context diagnostic and gate its conditional candidate."""
import argparse
from pathlib import Path
import focus_direct_transition as d
from prepare_spatial56 import audit, candidate_gate

BASE=d.h.ROOT/'reports/work/GLOBAL-CONTEXT-57'


def verify_gate(reference,corpus,rows):
    evaluation=d.h.sealed(d.h.checked(d.h.ROOT,reference),'direct-checkpoint-evaluation-v1')
    result=d.h.read(d.h.checked(d.h.ROOT,evaluation['source']))
    protocol=d.h.read(d.h.checked(d.h.ROOT,result['protocol']))
    d.h.require(protocol['configuration']==d.CONTEXT_DIAGNOSTIC and
        protocol['corpusSHA256']==corpus['corpusSHA256'] and protocol['pins']==d.pins()
        and evaluation['model']==result['model'],'diagnostic_gate_binding')
    d.h.checked(d.h.ROOT,evaluation['model'])
    selected=candidate_gate(evaluation,rows)
    d.h.require(sorted(result['trainingIDs'])==selected,'diagnostic_fit_membership')
    return selected


def prepare(kind):
    directory=d.h.fresh(BASE/(kind+'-ready'))
    source=d.h.read(d.h.ROOT/'reports/work/DIRECT-TRANSITION-55/protocol.json')
    corpus=d.collect(source['sources'])
    rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,source['admission'])))
    config=d.CONTEXT_DIAGNOSTIC if kind=='diagnostic' else d.CONTEXT_CONFIG
    gate=None
    if kind=='candidate':
        gate=d.h.ref(BASE/'diagnostic-evaluation.json');verify_gate(gate,corpus,rows)
    report=audit(rows)
    selected={r['id'] for r in d.training_rows([r for r in rows if r['split']=='train'],config)}
    d.h.require(not [v for v in report['encodedTargetConflicts']
        if len([r for r in v['members'] if r['id'] in selected])>1], 'contradictory_encoded_training_targets')
    directory.mkdir(parents=True)
    d.h.write(directory/'coverage.json',report,sealed=True)
    protocol=dict(version=d.VERSION,sources=corpus['sources'],corpusSHA256=corpus['corpusSHA256'],
        admission=source['admission'],configuration=config,implementation=d.h.ref(Path(d.__file__)),
        pins=d.pins(),diagnosticGate=gate)
    protocol['protocolSHA256']=d.digest(protocol)
    d.h.write(directory/'protocol.json',protocol)
    name='context57-dtm004' if kind=='diagnostic' else 'context57-dtm005'
    d.h.write(directory/'approval.json',dict(version='focus-direct-approval-v1',approved=True,
        protocolSHA256=protocol['protocolSHA256'],arm=d.ARM,runName=name,
        decisionReference='2026-10-03 maintainer: continue with the next tranche. GLOBAL-CONTEXT-57 fixed diagnostic and conditional candidate; two runs, combined2GiB, no wall-time cap.',gate=gate))
    print(dict(runName=name,protocolSHA256=protocol['protocolSHA256'],trainingIDs=sorted(selected)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['diagnostic','candidate']);prepare(p.parse_args().kind)
