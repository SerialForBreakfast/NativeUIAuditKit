"""Bounded Settings25 replay: arithmetic parity, then Vision tracking substitution."""
import argparse
import base64
import copy
import json
import os
import subprocess
import time
from PIL import Image
import human_annotation_review as h
import focus_recorded_semantics as semantic
import focus_recorded_comparison as comparison
import focus_recorded_transition_eval as evaluate
import focus_transition_verifier as visual
import settings_focus_stability as stability
import settings_context_probe as context
import focus_runtime as native

TOOL=h.ROOT/'.build/debug/SettingsProbeTool'


def invoke(mode,items):
    r=subprocess.run([str(TOOL)],input=json.dumps(dict(version=1,root=str(h.ROOT),mode=mode,items=items)),
        capture_output=True,text=True,timeout=120,env={**os.environ,'TMPDIR':str(h.ROOT/'.build/debug-output/accessibility29/tmp')})
    h.require(r.returncode==0,'swift_probe_failed: '+r.stderr[-1000:])
    rows=json.loads(r.stdout);h.require([r['id'] for r in rows]==[r['id'] for r in items],'swift_membership')
    return rows


def measure(images,ident,clipped):
    return invoke('measure',[dict(id=ident,beforeRGB=base64.b64encode(images[0].tobytes()).decode(),
        afterRGB=base64.b64encode(images[1].tobytes()).decode(),clipped=clipped)])[0]


def vision(before,after,controls):
    with Image.open(h.checked(h.ROOT,before)) as im: size=im.size
    results=invoke('track',[dict(id=c['id'],before=dict(path=str(h.checked(h.ROOT,before)),sha256=before['sha256']),
        after=dict(path=str(h.checked(h.ROOT,after)),sha256=after['sha256']),bounds=c['bounds']) for c in controls])
    rows=[]
    for c,r in zip(controls,results):
        t=dict(status=r['status'],reason=r.get('reason'),milliseconds=r['milliseconds'])
        if r.get('bounds'):
            t.update(afterBounds=r['bounds'],dx=r['bounds'][0]-c['bounds'][0],dy=r['bounds'][1]-c['bounds'][1])
        if t['status']=='matched':
            windows=visual.common_support(c['bounds'],r['bounds'],size)
            if windows is None:t=dict(status='unavailable',reason='clipping_support')
            else:t.update(beforeCropBounds=windows[0],afterCropBounds=windows[1])
        p=dict(id=c['id'],tracking=t,decision='unavailable')
        if t['status']=='identical':p['decision']='unchanged'
        if t['status']=='matched':
            ims,_=context.crops(before,after,c['bounds'],t)
            s=measure(ims,c['id'],any(visual.footprint(c['bounds'],size)))
            p.update(decision=s['decision'],swift=s)
        rows.append(p)
    return rows


def score(predictions,before,after,matches):
    # compare() already applies semantic truth ONLY at scoring, but expects diagnostic arm fields.
    ps=copy.deepcopy(predictions)
    for p in ps: p.update(brightness=p['decision'],growth=p['decision'])
    return comparison.compare(ps,before,after,matches)


def run(previous,output):
    previous=h.local(previous);source=h.sealed(previous,'settings-stability-v1')
    h.checked(h.ROOT,source['implementation'])
    baseline=h.sealed(h.checked(h.ROOT,source['baseline']),'focus-recorded-comparison-v1')
    for ref in baseline['implementation']:h.checked(h.ROOT,ref)
    sem=h.sealed(h.checked(h.ROOT,baseline['semantics']),'focus-recorded-semantics-v1')
    h.checked(h.ROOT,sem['implementation'])
    args={k:str(h.checked(h.ROOT,v)) for k,v in sem['inputs'].items() if k!='events'}
    _,truth,_,_=semantic.inputs(**args)
    out=h.fresh(output);out.mkdir(parents=True)
    pins=dict(source=h.ref(previous),semantics=baseline['semantics'],tool=h.ref(TOOL),runtime=native.identity(),
        implementation=[h.ref(h.ROOT/'scripts'/s) for s in ('settings_swift_spike.py','settings_focus_stability.py','focus_transition_verifier.py')])
    h.write(out/'execution.json',dict(**pins,policy=stability.POLICY,changePolicy=stability.CHANGE_POLICY,
        tracking='VNTrackObjectRequest revision1 accurate, reciprocal .15h, confidence .55, scale .06',
        scope='five retained same-screen pairs, two page-change exclusions, 14 generated cases',
        maxSeconds=300,maxControls=100,training=False))
    start=time.monotonic();actions=[];parity=[];timings=[]
    for action in baseline['actions']:
        if action['status']!='retrospective-diagnostic':continue
        h.require(time.monotonic()-start<300,'spike_deadline')
        b,a=[truth[action['endpoints'][k]['sha256']] for k in ('before','after')]
        with Image.open(h.checked(h.ROOT,b['image'])) as im: size=im.size
        controls=[dict(id=c['id'],bounds=c['bounds']) for c in b['controls']]
        # Recompute current Python tracking rather than compare stale timing or predictions.
        ts=time.monotonic();python,_=evaluate.predict(b['image'],a['image'],controls)
        py_tracking=time.monotonic()-ts
        swsame=copy.deepcopy(python)
        for c,p,s in zip(controls,python,swsame):
            if p['tracking']['status']!='matched':continue
            ims,_=context.crops(b['image'],a['image'],c['bounds'],p['tracking'])
            py=stability.measure(*ims)
            p['decision']=stability.guard(stability.extend(p,py,settings_context=True),py)['decision']
            swift=measure(ims,c['id'],any(visual.footprint(c['bounds'],size)))
            errors={k:abs(py[k]-swift['metrics'][k]) for k in ('mean','p95','maximum','changedFraction')}
            parity.append(dict(actionID=action['actionID'],id=c['id'],errors=errors,
                decisionEqual=p['decision']==swift['decision'],python=p['decision'],swift=swift['decision']))
            s['decision']=swift['decision']
        ts=time.monotonic();sv=vision(b['image'],a['image'],controls);vision_seconds=time.monotonic()-ts
        rows={k:score(ps,b['controls'],a['controls'],action['matches']) for k,ps in [('python',python),('swiftSameTracking',swsame),('swiftVision',sv)]}
        actions.append(dict(actionID=action['actionID'],arms=rows,completeEndpoints=action['completeEndpoints'],
            outcomes={k:stability.action_outcome([r['arms']['combined'] for r in rs],action['completeEndpoints']) for k,rs in rows.items()}))
        timings.append(dict(actionID=action['actionID'],pythonTrackAndCropSeconds=py_tracking,visionTrackCropAndRuleSeconds=vision_seconds))
    summary={k:evaluate.summarize([r['arms']['combined'] for a in actions for r in a['arms'][k]]) for k in ('python','swiftSameTracking','swiftVision')}
    h.require(summary['python']==source['summaries']['guarded'],'python_baseline_changed')
    report=dict(version='settings-swift-spike-v1',**h.FLAGS,**pins,summaries=summary,parity=parity,actions=actions,
        exclusions=[a for a in baseline['actions'] if a['status']!='retrospective-diagnostic'],
        timings=timings,elapsedSeconds=time.monotonic()-start)
    h.write(out/'result.json',report,sealed=True);print(summary);return report


def stress(output):
    out=h.fresh(output);out.mkdir(parents=True);rows=[];start=time.monotonic()
    for name,path in [('stability','reports/work/SETTINGS-STABILITY-23/stress-final/result.json'),('context','reports/work/SETTINGS-CONTEXT-24/stress/result.json')]:
        d=h.read(h.ROOT/path)
        for c in d['cases']:
            h.require(time.monotonic()-start<300,'stress_deadline')
            refs=c['inputs'];controls=[dict(id='row',bounds=[200,200,160,60])]
            p,_=evaluate.predict(*refs,controls);p=p[0];same=comparison.decision(p,'combined');eq=True;error=0
            if p['tracking']['status']=='matched':
                ims,_=context.crops(*refs,controls[0]['bounds'],p['tracking'])
                py=stability.measure(*ims);same=stability.guard(stability.extend(p,py,settings_context=True),py)['decision']
                sw=measure(ims,'row',False)
                eq=same==sw['decision'];error=max(abs(py[k]-sw['metrics'][k]) for k in ('mean','p95','maximum','changedFraction'))
            v=vision(*refs,controls)[0]
            rows.append(dict(name=name+'-'+c['name'],expected=c['expected'],python=same,swiftVision=v['decision'],
                parity=eq,maxMetricError=error,vision=v))
    result=dict(version='settings-swift-stress-v1',cases=rows,elapsedSeconds=time.monotonic()-start)
    h.write(out/'result.json',result,sealed=True);print([(r['name'],r['python'],r['swiftVision']) for r in rows]);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--previous');p.add_argument('--stress',action='store_true');p.add_argument('--output',required=True)
    a=p.parse_args()
    if a.stress:stress(a.output)
    else:run(a.previous,a.output)
