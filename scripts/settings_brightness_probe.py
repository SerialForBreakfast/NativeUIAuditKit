"""Fixed mean-brightness comparison using retained tracking and reviewed scoring."""
import argparse
import copy
import time
import numpy as np
import human_annotation_review as h
import focus_runtime as runtime
import focus_recorded_comparison as comparison
import focus_recorded_semantics as semantic
import focus_recorded_transition_eval as evaluate
import settings_context_probe as context
import settings_focus_stability as stability

SOURCE=h.ROOT/'reports/work/SETTINGS-SWIFT-SPIKE-25/retained-host/result.json'
STRESS=h.ROOT/'reports/work/ACCESSIBILITY-TRACKING-30/stress-verified/result.json'


def brightness(before,after):
    a=np.asarray(before.convert('RGB'),dtype=float)/255
    b=np.asarray(after.convert('RGB'),dtype=float)/255
    h.require(a.shape==b.shape==(256,256,3),'brightness_dimensions')
    return float((b-a).mean(axis=(0,1))@np.array([.2126,.7152,.0722]))


def decide(prediction,delta,metrics,guarded):
    status=prediction['tracking']['status']
    if status=='identical':return 'unchanged'
    if status!='matched':return 'unavailable'
    if prediction.get('illuminationWarning'):return 'unknown'
    h.require(type(delta) in (int,float) and np.isfinite(delta) and abs(delta)<=1,'invalid_brightness')
    if not guarded:return 'arrival' if delta>0 else 'departure' if delta<0 else 'unchanged'
    h.require(metrics is not None,'missing_metrics')
    if all(metrics[k]<=stability.POLICY[k] for k in ('mean','p95','changedFraction','maximum')):
        return 'unchanged'
    if abs(delta)<stability.CHANGE_POLICY['delta']:return 'unknown'
    return stability.guard(dict(decision='arrival' if delta>0 else 'departure'),metrics)['decision']


def proposals(prediction,images):
    delta=brightness(*images) if images else None
    measured=stability.measure(*images) if images else None
    return dict(delta=delta,metrics=measured,
                decisions={k:decide(prediction,delta,measured,g) for k,g in [('sign',False),('guardedMean',True)]})


def run(output):
    start=time.monotonic();source=h.sealed(SOURCE,'settings-swift-spike-v1')
    for ref in source['implementation']:h.checked(h.ROOT,ref)
    prior=h.sealed(h.checked(h.ROOT,source['source']),'settings-stability-v1')
    baseline=h.sealed(h.checked(h.ROOT,prior['baseline']),'focus-recorded-comparison-v1')
    for ref in baseline['implementation']:h.checked(h.ROOT,ref)
    sem=h.sealed(h.checked(h.ROOT,source['semantics']),'focus-recorded-semantics-v1')
    h.checked(h.ROOT,sem['implementation'])
    args={k:str(h.checked(h.ROOT,v)) for k,v in sem['inputs'].items() if k!='events'}
    _,truth,_,_=semantic.inputs(**args)
    out=h.fresh(output);out.mkdir(parents=True);identity=runtime.identity();actions=[];count=0
    eligible=[a for a in baseline['actions'] if a['status']=='retrospective-diagnostic']
    h.require([a['actionID'] for a in eligible]==[a['actionID'] for a in source['actions']],'membership')
    for action,saved in zip(eligible,source['actions']):
        before,after=[truth[action['endpoints'][k]['sha256']] for k in ('before','after')]
        bodies={c['id']:c['bounds'] for c in before['controls']};arms={k:[] for k in ('sign','guardedMean')};measurements=[]
        for row in saved['arms']['python']:
            count+=1;h.require(count<=100 and time.monotonic()-start<300,'probe_budget')
            p=row['prediction'];images=None
            if p['tracking']['status']=='matched':images,_=context.crops(before['image'],after['image'],bodies[p['id']],p['tracking'])
            m=proposals(p,images);measurements.append(dict(id=p['id'],**m))
            for arm in arms:
                q=copy.deepcopy(p);q.update(decision=m['decisions'][arm],brightness=m['decisions'][arm],growth=m['decisions'][arm]);arms[arm].append(q)
        scored={k:comparison.compare(ps,before['controls'],after['controls'],action['matches']) for k,ps in arms.items()}
        scored['existing']=saved['arms']['python']
        actions.append(dict(actionID=action['actionID'],measurements=measurements,arms=scored,
            fullScreenOutcomes={k:stability.action_outcome([r['arms']['combined'] for r in rs],
                action['completeEndpoints'] and all(r['expected'] is not None for r in rs)) for k,rs in scored.items()}))
    summaries={k:evaluate.summarize([r['arms']['combined'] for a in actions for r in a['arms'][k]]) for k in ('existing','sign','guardedMean')}
    h.require(summaries['existing']==source['summaries']['python'],'baseline_changed')
    generated=h.sealed(STRESS,'settings-tracking-stress-v1');cases=[]
    h.checked(h.ROOT,generated['implementation'])
    for ref in generated['generatedInputs']:h.checked(h.ROOT,ref)
    for c in generated['cases']:
        h.require(len(cases)<30 and time.monotonic()-start<300,'stress_budget')
        refs=c['inputs'];p=evaluate.predict(*refs,[dict(id='row',bounds=[200,200,160,60])])[0][0]
        images=None
        if p['tracking']['status']=='matched':images,_=context.crops(*refs,[200,200,160,60],p['tracking'])
        m=proposals(p,images)
        existing=stability.guard(stability.extend(p,m['metrics'],settings_context=True),m['metrics'])['decision']
        cases.append(dict(name=c['name'],expected=c['expected'],inputs=refs,existing=existing,**m))
    h.require(runtime.identity()==identity,'runtime_changed')
    result=dict(version='settings-brightness-v1',**h.FLAGS,source=h.ref(SOURCE),stress=h.ref(STRESS),
        implementation=h.ref(__file__),runtime=identity,policy=stability.POLICY,changePolicy=stability.CHANGE_POLICY,
        seconds=time.monotonic()-start,actions=actions,summaries=summaries,generatedCases=cases,
        generatedExact={k:sum((r['existing'] if k=='existing' else r['decisions'][k])==r['expected'] for r in cases)
                        for k in ('existing','sign','guardedMean')})
    h.write(out/'result.json',result,sealed=True)
    lines=['# Settings brightness comparison','',
           'Retained development sequence; generated cases separately labeled. No threshold tuning.',
           '', '| Method | Correct | Wrong | Abstained | Scorable |', '| --- | --- | --- | --- | --- |']
    for k,s in summaries.items():lines.append(f"| {k} | {s['correct']} | {s['wrong']} | {s['abstained']} | {s['scorable']} |")
    lines+=['',f"Generated exact matches out of{len(cases)}: {result['generatedExact']}",'',
            '| Generated case | Expected | Existing | Sign | Guarded mean |','| --- | --- | --- | --- | --- |']
    for c in cases:lines.append(f"| {c['name']} | {c['expected']} | {c['existing']} | {c['decisions']['sign']} | {c['decisions']['guardedMean']} |")
    (out/'result.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    run(p.parse_args().output)
