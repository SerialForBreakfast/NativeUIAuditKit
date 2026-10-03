"""Opt-in retrospective Settings stability probe; never issues device controls."""
import argparse
import base64
import copy
import io
import time
import numpy as np
from PIL import Image
import human_annotation_review as h
import focus_recorded_comparison as comparison
import focus_recorded_semantics as semantic
import focus_recorded_transition_eval as evaluate
import focus_runtime as native

POLICY=dict(mean=.01,p95=.03,changedThreshold=.04,changedFraction=.02,maximum=.25)
CHANGE_POLICY=dict(delta=.08,minQuadrantFraction=.6)


def measure(before,after):
    a=np.asarray(before.convert('RGB'),dtype=float)/255
    b=np.asarray(after.convert('RGB'),dtype=float)/255
    h.require(a.shape==b.shape==(256,256,3),'stability_crop_dimensions')
    delta=np.abs(b-a)
    signed=(b[64:192,64:192]-a[64:192,64:192])@np.array([.2126,.7152,.0722])
    quadrants=[signed[y:y+64,x:x+64] for y in (0,64) for x in (0,64)]
    return dict(mean=float(delta.mean()),p95=float(np.quantile(delta,.95)),
        changedFraction=float((delta>POLICY['changedThreshold']).mean()),maximum=float(delta.max()),
        directionalCoverage={d:[float((q*sign>=CHANGE_POLICY['delta']).mean()) for q in quadrants]
            for d,sign in [('arrival',1),('departure',-1)]})


def extend(prediction,metrics,*,settings_context):
    original=comparison.decision(prediction,'combined')
    if not settings_context:return dict(decision='unavailable',reason='unsupported_context')
    if original!='unknown':return dict(decision=original,reason='existing_decision')
    if prediction.get('illuminationWarning'):return dict(decision='unknown',reason='illumination')
    if metrics is None:return dict(decision='unknown',reason='missing_measurement')
    keys={'mean','p95','changedFraction','maximum'}
    h.require(keys<=set(metrics) and all(type(metrics[k]) in (float,int) and np.isfinite(metrics[k]) and
        0<=metrics[k]<=1 for k in keys),'invalid_stability_metrics')
    stable=all(metrics[k]<=POLICY[k] for k in keys)
    return dict(decision='unchanged' if stable else 'unknown',reason='near_identical' if stable else 'changed_pixels')


def guard(proposal,metrics):
    decision=proposal['decision']
    if decision not in ('arrival','departure'):return dict(proposal)
    values=(metrics or {}).get('directionalCoverage',{}).get(decision,[])
    h.require(isinstance(values,list) and len(values) in (0,4) and
        all(type(v) in (float,int) and np.isfinite(v) and 0<=v<=1 for v in values),'invalid_directional_coverage')
    return dict(decision=decision if len(values)==4 and min(values)>=CHANGE_POLICY['minQuadrantFraction'] else 'unknown',
        reason='coherent_highlight' if len(values)==4 and min(values)>=CHANGE_POLICY['minQuadrantFraction'] else 'localized_or_unsupported_change')


def action_outcome(rows,complete):
    """Decisions only: expected focus must not enter action selection."""
    if not complete:return 'incomplete'
    decisions=[r['decision'] for r in rows]
    if not decisions or any(d in ('unknown','unavailable') for d in decisions):return 'abstained'
    if all(d=='unchanged' for d in decisions):return 'unchanged'
    if decisions.count('arrival')==decisions.count('departure')==1:return 'switch'
    return 'ambiguous'


def crop_metrics(before,after,controls,predictions):
    items=[];pairs={};runtime=native.identity()
    for c,p in zip(controls,predictions):
        h.require(c['id']==p['id'],'stability_prediction_order')
        if p['tracking']['status']!='matched':continue
        t=p['tracking'];windows=[t.get('beforeCropBounds',c['bounds']),t.get('afterCropBounds',t['afterBounds'])]
        for k,(ref,bounds) in enumerate(zip((before,after),windows)):
            items.append(dict(id=str(len(items)),path=str(h.checked(h.ROOT,ref)),sha256=ref['sha256'],bounds=bounds))
        pairs[c['id']]=[items[-2]['id'],items[-1]['id']]
    crops={}
    for block in native.bounded_batches(items):
        response=native.invoke(block)['results']
        h.require([r['id'] for r in response]==[r['id'] for r in block],'stability_crop_membership')
        for r in response:
            crops[r['id']]=Image.open(io.BytesIO(base64.b64decode(r['png'],validate=True))).convert('RGB')
    h.require(native.identity()==runtime,'stability_runtime_changed')
    return {k:measure(*(crops[i] for i in ids)) for k,ids in pairs.items()},runtime


def run(semantics,output,*,tracker='template'):
    output=h.fresh(output);output.mkdir(parents=True);start=time.monotonic()
    # Recompute the existing source-bound comparison through its real caller.
    baseline=comparison.run(semantics,output/'baseline',tracker=tracker)
    doc=h.sealed(h.local(semantics),'focus-recorded-semantics-v1')
    args={k:str(h.checked(h.ROOT,v)) for k,v in doc['inputs'].items() if k!='events'}
    _,truth,_,_=semantic.inputs(**args)
    rows=[];total=0;runtimes=[]
    for action in baseline['actions']:
        if action['status']!='retrospective-diagnostic':continue
        h.require(time.monotonic()-start<300,'stability_deadline')
        before,after=[truth[action['endpoints'][k]['sha256']] for k in ('before','after')]
        controls=[dict(id=c['id'],bounds=c['bounds']) for c in before['controls']]
        predictions=[c['prediction'] for c in action['controls']]
        total+=len(controls);h.require(total<=100,'stability_control_limit')
        metrics,runtime=crop_metrics(before['image'],after['image'],controls,predictions)
        if runtime not in runtimes:runtimes.append(runtime)
        modified=copy.deepcopy(predictions)
        for p in modified:
            proposal=extend(p,metrics.get(p['id']),settings_context=action['sameTitle'])
            p['decision']=proposal['decision'];p['stability']=dict(proposal,metrics=metrics.get(p['id']))
        scored=comparison.compare(modified,before['controls'],after['controls'],action['matches'])
        guarded=copy.deepcopy(modified)
        for p in guarded:p['decision']=guard(p['stability'],metrics.get(p['id']))['decision']
        guarded_scored=comparison.compare(guarded,before['controls'],after['controls'],action['matches'])
        old=[c['arms']['combined'] for c in action['controls']]
        new=[c['arms']['combined'] for c in scored]
        matched=all(r['scorable'] for r in new)
        rows.append(dict(actionID=action['actionID'],endpoints=action['endpoints'],controls=scored,
            guardedControls=guarded_scored,baseline=evaluate.summarize(old),extended=evaluate.summarize(new),
            guarded=evaluate.summarize([c['arms']['combined'] for c in guarded_scored]),
            reviewedSubsetOutcome=dict(baseline=action_outcome(old,matched),extended=action_outcome(new,matched)),
            fullScreenOutcome=action_outcome(new,matched and action['completeEndpoints']),
            completeEndpoints=action['completeEndpoints']))
    h.require(len(runtimes)<=1,'stability_runtime_changed')
    summaries=dict(baseline=baseline['summaries']['combined'],extended=evaluate.summarize(
        [c['arms']['combined'] for a in rows for c in a['controls']]),guarded=evaluate.summarize(
        [c['arms']['combined'] for a in rows for c in a['guardedControls']]))
    report=dict(version='settings-stability-v1',**h.FLAGS,policy=POLICY,actions=rows,summaries=summaries,tracker=tracker,
        changePolicy=CHANGE_POLICY,baseline=h.ref(output/'baseline/comparison.json'),runtime=runtimes,elapsedSeconds=time.monotonic()-start,
        implementation=h.ref(h.ROOT/'scripts/settings_focus_stability.py'))
    h.write(output/'result.json',report,sealed=True)
    print(summaries);return report


def stress(output):
    from focus_transition_stress import scene
    output=h.fresh(output);output.mkdir(parents=True)
    a=scene();b=np.asarray(a).copy();b[205:220,210:330]=220
    changed=Image.fromarray(b)
    duplicate=scene();duplicate.paste(a.crop((200,200,360,260)),(200,100))
    cases=[('identical',a,a,'unchanged'),('small_noise',a,a.point(lambda v:min(255,v+1)),'unchanged'),
        ('scroll_only',a,scene(dy=-100),'unchanged'),
        ('highlight',a,scene(shade=235),'arrival'),('dim',scene(shade=235),a,'departure'),
        ('scroll_highlight',a,scene(dy=-100,shade=235),'arrival'),
        ('content_change',a,changed,'unknown'),
        ('illumination',a,a.point(lambda v:min(255,v+30)),'unknown'),
        ('duplicate',a,duplicate,'unavailable')]
    results=[];start=time.monotonic()
    for name,before,after,expected in cases:
        h.require(time.monotonic()-start<300,'stress_deadline')
        refs=[]
        for side,im in [('before',before),('after',after)]:
            path=output/(name+'-'+side+'.png');im.save(path);refs.append(h.ref(path))
        controls=[dict(id='row',bounds=[200,200,160,60])]
        predictions,_=evaluate.predict(*refs,controls)
        metrics,runtime=crop_metrics(*refs,controls,predictions)
        result=extend(predictions[0],metrics.get('row'),settings_context=True)
        guarded=guard(result,metrics.get('row'))
        results.append(dict(name=name,expected=expected,predicted=result['decision'],guarded=guarded,
            guardedPassed=guarded['decision']==expected,
            passed=result['decision']==expected,proposal=result,prediction=predictions[0],
            metrics=metrics.get('row'),inputs=refs,runtime=runtime))
    report=dict(version='settings-stability-stress-v1',**h.FLAGS,generatedSoftwareFixture=True,
        policy=POLICY,changePolicy=CHANGE_POLICY,cases=results,passed=sum(r['passed'] for r in results),
        guardedPassed=sum(r['guardedPassed'] for r in results),total=len(results),
        implementation=h.ref(h.ROOT/'scripts/settings_focus_stability.py'))
    h.write(output/'result.json',report,sealed=True);print(report['passed'], '/', report['total']);return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--semantics');p.add_argument('--output',required=True)
    p.add_argument('--stress',action='store_true')
    p.add_argument('--tracker',choices=('template','wide-template-v1','feature-consensus-v1'),default='template')
    a=p.parse_args()
    if a.stress:
        if a.tracker!='template':p.error('--tracker is only available for retained replay')
        if a.semantics:p.error('--stress and --semantics are mutually exclusive')
        stress(a.output)
    else:
        if not a.semantics:p.error('--semantics is required for retained replay')
        run(a.semantics,a.output,tracker=a.tracker)
