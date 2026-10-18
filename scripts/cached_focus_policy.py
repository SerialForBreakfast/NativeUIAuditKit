"""Test fixed selection policies on retained scores. Never change deployed behavior."""
from collections import Counter
from pathlib import Path
import research_queue as q
import native343
from cached_selection405 import verified_report
from template_adapters395 import document, resolve_inputs
from native_selection404 import outcome
from coverage_reports402 import rectangle

OUT = None
SUCCESS = {'correct', 'correct-abstention'}
POLICIES = {'unchanged', 'hcf-ring-first', 'abstention-fallback'}


def select(row, truth, policy):
    q.require(policy in POLICIES, 'focus_policy_unknown')
    q.require(row['profile'] in ('standard','hcf') and row['noFocus'] == (truth is None), 'focus_policy_truth')
    arm=row['arms']['detector-plus-ring']
    boxes=[c['box'] for c in arm['candidates']]
    models=arm['models']
    for name in ('baseline','candidate'):
        scores=models[name]['scores']
        q.require(len(scores)==len(boxes), 'focus_policy_membership')
        q.require(outcome(scores,boxes,truth)==models[name]['outcome'], 'focus_policy_reference')
    chosen='candidate'; indices=list(range(len(boxes)))
    if policy=='hcf-ring-first' and row['profile']=='hcf':
        rings=[i for i,c in enumerate(arm['candidates']) if c['source']=='mapped-ring']
        if rings: indices=rings
    elif policy=='abstention-fallback':
        # Runtime decisions use scores only. Truth is used only for evaluation.
        if sum(s>=.85 for s in models['candidate']['scores'])!=1 and sum(s>=.85 for s in models['baseline']['scores'])==1:
            chosen='baseline'
    scores=[models[chosen]['scores'][i] for i in indices]
    decision=outcome(scores,[boxes[i] for i in indices],truth)
    prior=models['candidate']['outcome']; baseline=models['baseline']['outcome']
    return dict(id=row['id'],group=row['group'],profile=row['profile'],noFocus=row['noFocus'],
                reference=prior,baseline=baseline,outcome=decision,selectedModel=chosen,indices=indices,
                gain=prior not in SUCCESS and decision in SUCCESS,
                loss=prior in SUCCESS and decision not in SUCCESS,
                baselineLoss=baseline in SUCCESS and decision not in SUCCESS,
                newWrong=decision in ('wrong','false-selection') and prior not in ('wrong','false-selection'))


def summarize(rows, policy):
    q.require(rows and len({r['id'] for r in rows})==len(rows), 'focus_policy_rows')
    slices={}
    for profile in ('standard','hcf'):
        subset=[r for r in rows if r['profile']==profile]
        slices[profile]=dict(frames=len(subset),groups=len({r['group'] for r in subset}),
            noFocusFrames=sum(r['noFocus'] for r in subset),
            outcomes=dict(Counter(r['outcome'] for r in subset)),
            reference=dict(Counter(r['reference'] for r in subset)),
            gains=[r['id'] for r in subset if r['gain']],
            lostPriorSuccesses=[r['id'] for r in subset if r['loss']],
            baselineLosses=[r['id'] for r in subset if r['baselineLoss']],
            newWrongSelections=[r['id'] for r in subset if r['newWrong']])
    return dict(version='cached-focus-policy-v1',policy=policy,threshold=.85,rows=rows,slices=slices,
        gains=[r['id'] for r in rows if r['gain']],lostPriorSuccesses=[r['id'] for r in rows if r['loss']],
        baselineLosses=[r['id'] for r in rows if r['baselineLoss']],
        newWrongSelections=[r['id'] for r in rows if r['newWrong']],modelAccepted=False,
        limitation='Inspected development cases. Frozen scores and boxes. No threshold tuning, training, or runtime change.')


def run():
    cfg=q.load(OUT.parents[2]/'spec.json')['template']; refs=resolve_inputs(cfg,OUT)
    q.require(set(cfg['parameters'])=={'policy'} and cfg['parameters']['policy'] in POLICIES,'focus_policy_unknown')
    policy=cfg['parameters']['policy']
    report=verified_report(dict(report=refs['report'],result=refs['receipt']))
    q.require(report.get('version')=='detector-focus-pilot-v1' and report.get('threshold')==.85,'focus_policy_version')
    artifact=document(report['inputs']['capture']); path=Path(artifact['path'])
    q.require(path.resolve()==path and path.is_relative_to('/Volumes/training-drive/data/NUIAK/HCF371'),'focus_policy_source')
    q.require(q.digest(path)==artifact['sha256'],'focus_policy_capture_changed')
    plan=artifact['plan']
    q.require(plan.get('trainingEligible') is False and all(c['role']=='development' for c in plan['cases']),'focus_policy_role')
    capture=q.load(path); q.require(capture['complete'] and capture['cleanup'],'focus_policy_capture')
    q.require([f['id'] for f in capture['frames']]==[r['id'] for r in report['rows']],'focus_policy_membership')
    rows=[]
    for frame,row in zip(capture['frames'],report['rows']):
        native343.signature(frame['before'],frame['before'],frame['focus'])
        native343.signature(frame['after'],frame['before'],frame['focus'])
        q.require((frame['sha256'],frame['profile'],frame['case'])==(row['sha256'],row['profile'],row['group']),'focus_policy_identity')
        scene=frame['before']['scene']
        focused=[e for e in scene['elements'] if e['is_focused']]
        q.require(len(focused)<=1,'focus_policy_truth')
        body=rectangle(focused[0]['rendered_body_geometry']['visible_pixel_bounds']) if focused else None
        truth=[body[k] for k in ('x','y','width','height')] if body else None
        rows.append(select(row,truth,policy))
    result=summarize(rows,policy);result['inputs']=refs
    q.save(OUT/'benchmark_summary.json',result)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
