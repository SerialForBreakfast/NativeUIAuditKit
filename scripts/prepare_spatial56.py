"""Freeze the approved spatial experiment and audit coverage without capture or training."""
import argparse
from collections import Counter,defaultdict
import hashlib
from pathlib import Path
import numpy as np
import focus_direct_transition as d

BASE=d.h.ROOT/'reports/work/SPATIAL-TRANSITION-56'


def audit(rows):
    encodings=defaultdict(list);coverage=Counter();details=[]
    for row in rows:
        before,after=[d.pixels(v) for v in row['images']]
        encoded=d.encode(before,after)
        key=hashlib.sha256(encoded.tobytes()).hexdigest()
        target=[*[d.target_box(b,row['size']) for b in row['boxes']],row['changed']]
        encodings[key].append(dict(id=row['id'],target=target,split=row['split']))
        displaced=not np.allclose(row['boxes'][0],row['boxes'][1],rtol=0,atol=1)
        coverage[(row['split'],row['group'],row['changed'],displaced)]+=1
        details.append(dict(id=row['id'],split=row['split'],changed=row['changed'],
            endpointBoxDisplaced=displaced,encodedSHA256=key,
            endpointBoxSizeAtInput=[[v[2]*96,v[3]*64] for v in target[:2]],
            encodedMeanAbsoluteFrameDifference=float(np.abs(encoded[:3]-encoded[3:]).mean())))
    conflicting=[dict(encodedSHA256=k,members=v) for k,v in encodings.items()
                 if len({d.digest(r['target']) for r in v})>1]
    return dict(version='spatial56-coverage-v1',details=details,encodedTargetConflicts=conflicting,
        coverage=[dict(split=k[0],group=k[1],changed=k[2],endpointBoxDisplaced=k[3],pairs=n)
                  for k,n in sorted(coverage.items())],
        limitations=['Box displacement is not scrolling ground truth.',
                     'Only one Fixture renderer and one exposed Settings journey; no independent final evaluation.',
                     'Exactly-one-known-focus admission excludes absent-focus/unknown-focus scenes.',
                     'No declared coverage of dialogs, broad app identities or animation-negative cases.'],
        priorities=['Add independently grouped native/custom focus-switch and no-op journeys.',
                    'Label scroll versus no-scroll separately from semantic focus change; fill all four cells.',
                    'Add absent-focus, transient/animation, overlay and hard-negative cases with trustworthy labels.'])


def candidate_gate(evaluation,rows):
    selected={r['id'] for r in d.training_rows([r for r in rows if r['split']=='train'],d.SPATIAL_DIAGNOSTIC)}
    scored=[r for r in evaluation['results'] if r['id'] in selected]
    d.h.require(len(scored)==4 and {r['id'] for r in scored}==selected and
        all(r['split']=='train' and min(r['boxIoUs'])>=.5 and r['rawChangeCorrect'] for r in scored),
        'memorization_gate_failed')
    return sorted(selected)


def verify_gate(reference,corpus,rows):
    path=d.h.checked(d.h.ROOT,reference)
    evaluation=d.h.sealed(path,'direct-checkpoint-evaluation-v1')
    result=d.h.read(d.h.checked(d.h.ROOT,evaluation['source']))
    protocol=d.h.read(d.h.checked(d.h.ROOT,result['protocol']))
    d.h.require(protocol['configuration']==d.SPATIAL_DIAGNOSTIC and
                protocol['corpusSHA256']==corpus['corpusSHA256'] and
                protocol['pins']==d.pins() and evaluation['model']==result['model'], 'diagnostic_gate_binding')
    d.h.checked(d.h.ROOT,evaluation['model'])
    selected=candidate_gate(evaluation,rows)
    d.h.require(sorted(result['trainingIDs'])==selected,'diagnostic_fit_membership')
    return selected


def prepare(kind):
    directory=d.h.fresh(BASE/(kind+'-ready'))
    source=d.h.read(d.h.ROOT/'reports/work/DIRECT-TRANSITION-55/protocol.json')
    corpus=d.collect(source['sources'])
    rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,source['admission'])))
    config=d.SPATIAL_DIAGNOSTIC if kind=='diagnostic' else d.SPATIAL_CONFIG
    gate=None
    if kind=='candidate':
        gate=d.h.ref(BASE/'diagnostic-evaluation.json');verify_gate(gate,corpus,rows)
    report=audit(rows)
    selected={r['id'] for r in d.training_rows([r for r in rows if r['split']=='train'],config)}
    conflicts=[v for v in report['encodedTargetConflicts'] if len([r for r in v['members'] if r['id'] in selected])>1]
    d.h.require(not conflicts,'contradictory_encoded_training_targets')
    directory.mkdir(parents=True)
    d.h.write(directory/'coverage.json',report,sealed=True)
    protocol=dict(version=d.VERSION,sources=corpus['sources'],corpusSHA256=corpus['corpusSHA256'],
        admission=source['admission'],configuration=config,implementation=d.h.ref(Path(d.__file__)),pins=d.pins(),
        diagnosticGate=gate)
    protocol['protocolSHA256']=d.digest(protocol)
    d.h.write(directory/'protocol.json',protocol)
    name='spatial56-dtm003' if kind=='diagnostic' else 'spatial56-dtm004'
    d.h.write(directory/'approval.json',dict(version='focus-direct-approval-v1',approved=True,
        protocolSHA256=protocol['protocolSHA256'],arm=d.ARM,runName=name,
        decisionReference='2026-10-03 maintainer: Yes do that and any other pending tasks to make the tranche meaningful. Spatial56 fixed diagnostic and conditional candidate.',
        gate=gate))
    print(dict(runName=name,protocolSHA256=protocol['protocolSHA256'],trainingIDs=sorted(selected),coverage=report['coverage']))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['diagnostic','candidate']);prepare(p.parse_args().kind)
