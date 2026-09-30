"""Audit prepared representative selection using retained predictions only."""
import argparse
from collections import Counter
import json

import focus_representative_experiment as e
from focus_dataset_contract import ROOT, local


def audit(path):
    doc=e.appearance.sealed(e.a.reference(path),e.VERSION,'protocolSHA256')
    base=e.a.object_json(e.a.checked(doc['inputs']['base']))
    by_id={r['id']:r for r in doc['samples']}
    e.require(all(by_id.get(r['id'])==r for r in base['samples']),'changed_base_members')
    real=[r for r in doc['samples'] if r['use']=='representative-selection']
    retained=[r for r in doc['samples'] if r['use']=='retention-validation']
    train=[r for r in doc['samples'] if r['split']=='train']
    # These are synthetic perfect-retention scores solely to isolate real guards.
    # No claim that a checkpoint's retention was remeasured here.
    ret=[dict(id=r['id'],label=r['label'],probability=float(r['label'])) for r in retained]
    replay={'fdr010':e.selection_metrics(ret+doc['baseline'],retained+real,doc['selection'])}
    predictions=[];artifacts=[]
    for name in ('batch01','batch02','batch03','photos','supplement'):
        ref=e.a.reference(ROOT/'reports/work/FDR-012'/(name+'-candidate.json'))
        old=e.a.object_json(e.a.checked(ref));artifacts.append(ref)
        e.require(old['state']=='complete' and not old['unscored'] and not old['invalidPredictions'], 'incomplete_retained_scores')
        for p in old['predictions']:
            sid=name+':'+p['id']
            if sid in by_id:
                predictions.append(dict(id=sid,label=by_id[sid]['label'],probability=p['probability']))
    e.require(len(predictions)==len(real) and len({p['id'] for p in predictions})==len(real),'prediction_membership')
    values={p['id']:p for p in predictions}
    replay['fdr012']=e.selection_metrics(ret+[values[r['id']] for r in real],retained+real,doc['selection'])
    blocked={r[k]['pixelSHA256'] for r in train for k in ('frame','crop')}
    e.require(not blocked.intersection(r['pixelSHA256'] for r in real),'selection_leakage')
    e.require(all(r['id'] not in doc['sampling']['weights'] for r in real),'selection_in_training_sampler')
    negative={}
    for name, mutate in (
        ('missing_score',lambda p:p.pop()),
        ('duplicate_score',lambda p:p.append(p[0])),
        ('invalid_score',lambda p:p[0].update(probability=float('nan')))):
        scores=[dict(p) for p in ret+doc['baseline']];mutate(scores)
        try:e.selection_metrics(scores,retained+real,doc['selection'])
        except ValueError as error:negative[name]=str(error)
        else:raise ValueError('negative_case_accepted:'+name)
    return dict(version='representative-selection-audit-v1',protocol=e.a.reference(path),
        retainedScoreArtifacts=artifacts,counts=doc['counts'],baseRowsPreserved=len(base['samples']),
        excludedSelection=len(doc['excludedSelection']),
        objectiveMass={s:sum(doc['selection']['weights'][r['id']] for r in real if e.stratum(r)==s) for s in e.FLOORS},
        supportedLabels=dict(Counter(str(r['label']) for r in real)),
        realGuardReplay=replay,negativeChecks=negative,
        retentionReplay='synthetic perfect scores; only real guards audited, not new model inference',
        trainingSelectionDisjoint=True,trainingLaunched=False,modelGatePassed='not_assessed')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol',required=True,type=local)
    parser.add_argument('--output',required=True,type=local)
    args=parser.parse_args()
    e.require(not args.output.exists(),'output_collision')
    report=audit(args.protocol)
    with args.output.open('x') as stream:json.dump(report,stream,indent=2,allow_nan=False)
    print(json.dumps(dict(counts=report['counts'],negativeChecks=report['negativeChecks'])))
