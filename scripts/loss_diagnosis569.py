"""Diagnose retained detector losses. Never train or accept models."""
from collections import Counter
import research_queue as q
from template_inputs398 import checked
from template_adapters395 import resolve_inputs,document
from perception_benchmark import _iou
OUT=None


def classify(truth,detections):
    same=[d for d in detections if d['cls']==truth['cls']]
    hits=[d for d in same if _iou(d['box'],truth['box'])>=.5]
    if any(d['score']>=.5 for d in hits):return 'assignment-ambiguity'
    if hits:return 'confidence-below-fixed-threshold'
    if any(d['score']>=.5 and _iou(d['box'],truth['box'])>=.5 for d in detections):return 'class-or-assignment'
    if any(_iou(d['box'],truth['box'])>=.1 for d in same):return 'localization'
    return 'proposal-missing'


def tvos():
    import roles559_evaluate as evaluator
    r=resolve_inputs(q.load(OUT.parents[2]/'spec.json')['template'],OUT)
    comparison=document(r['comparison']);manifest=document(r['manifest'])
    before,after=document(r['controlReport']),document(r['candidateReport'])
    q.require(before['manifest']==after['manifest']==r['manifest'],'loss_manifest_changed')
    q.require(before['model']==r['control'] and after['model']==r['candidate'],'loss_models_changed')
    wanted=comparison['lostPriorSuccesses'];q.require(len(wanted)==len(set(wanted))>0,'loss_cases')
    truth={f['id']+'|'+t['id']:(f,t) for f in manifest['frames'] for t in f['truth']}
    q.require(set(wanted)<=truth.keys(),'loss_reference_missing')
    images=list(dict.fromkeys(checked(truth[i][0]['image']) for i in wanted))
    evaluator.SQUARE=True
    predictions={name:evaluator.rule_b(evaluator.predict(checked(r[name]),images,.001)) for name in ('control','candidate')}
    rows=[]
    for ident in wanted:
        frame,label=truth[ident];image=checked(frame['image'])
        for ref in frame['references']:checked(ref)
        rows.append(dict(id=ident,group=frame['group'],className=label['cls'],truth=label,
            diagnosis=classify(label,predictions['candidate'][image]),control=predictions['control'][image],candidate=predictions['candidate'][image]))
    q.save(OUT/'benchmark_summary.json',dict(version='loss-diagnosis569-v1',models={k:r[k] for k in ('control','candidate')},
        rows=rows,counts=dict(Counter(row['diagnosis'] for row in rows)),metricsStatus='provisional',modelAccepted=False,
        nextAction='Use the cause to choose classification, geometry, confidence, or evaluator repair. Preserve thresholds and do not promote.'))
    receipt()


def ios_rows(original,diagnoses):
    rows=[]
    for pair in diagnoses:
        matches=[r for r in original['reports'] if r['comparison']=='Run013' and r['condition']==pair['condition']]
        q.require(len(matches)==1,'loss_comparison_scope')
        indexed={r['id']:r for r in pair['cases']['rows']}
        for ident in matches[0]['lostPriorSuccesses']:
            q.require(ident in indexed,'loss_case_missing');r=indexed[ident]
            a,b=r['baseline']['status'],r['candidate']['status']
            category='baseline-assignment-changed' if a!='detected' else 'class-or-assignment' if b=='detected' else b
            rows.append(dict(condition=pair['condition'],id=ident,className=r['labelClass'],diagnosis=category,baseline=r['baseline'],candidate=r['candidate']))
    return rows


def ios():
    cfg=q.load(OUT.parents[2]/'spec.json')['template'];r=resolve_inputs(cfg,OUT)
    request=document(r['request']);original=document(r['reference'])
    pairs=[dict(condition=p['condition'],cases=document(r[p['key']])) for p in request['pairs']]
    rows=ios_rows(original,pairs)
    q.save(OUT/'benchmark_summary.json',dict(version='loss-diagnosis569-v1',rows=rows,counts=dict(Counter(row['diagnosis'] for row in rows)),
        metricsStatus='provisional',modelAccepted=False,trainingOrInferenceRepeated=False,
        nextAction='If geometry losses remain, test preservation of original box predictions on training-only anchors. If classes dominate, inspect classification preservation. Do not change evaluation labels.'))
    receipt()


def receipt():
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
