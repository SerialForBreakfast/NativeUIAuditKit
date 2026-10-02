"""Fixed body-versus-context diagnostic on identical production crop pixels."""
import argparse
import base64
import copy
import io
import math
import time
import numpy as np
from PIL import Image,ImageDraw
import human_annotation_review as h
import settings_focus_stability as stability
import focus_recorded_comparison as comparison
import focus_recorded_semantics as semantic
import focus_recorded_transition_eval as evaluate
import focus_runtime as native


def body_mask(body,window,size):
    """Project source pixel centers through native expandedCropRect/redrawCrop."""
    for box in (body,window):
        h.require(len(box)==4 and all(type(v) in (int,float) and math.isfinite(v) for v in box)
                  and box[2]>2 and box[3]>2,'mask_bounds')
    x,y,w,ht=window;W,H=size
    left=max(0,x-.16*w);top=max(0,y-.16*ht)
    width=min(W,x+1.16*w)-left;height=min(H,y+1.16*ht)-top
    h.require(width>0 and height>0,'mask_outside')
    xs=left+(np.arange(256)+.5)*math.floor(width+.5)/256
    ys=top+(np.arange(256)+.5)*math.floor(height+.5)/256
    bx,by,bw,bh=body
    return ((ys[:,None]>=by+1)&(ys[:,None]<by+bh-1)&
            (xs[None,:]>=bx+1)&(xs[None,:]<bx+bw-1))


def metrics(before,after,mask):
    h.require(mask.shape==(256,256) and mask.dtype==bool and mask.sum()>=256,'mask_support')
    delta=np.abs(np.asarray(after.convert('RGB'),dtype=float)-np.asarray(before.convert('RGB'),dtype=float))/255
    h.require(delta.shape==(256,256,3),'crop_shape')
    values=delta[mask]
    return dict(mean=float(values.mean()),p95=float(np.quantile(values,.95)),
        changedFraction=float((values>stability.POLICY['changedThreshold']).mean()),maximum=float(values.max()))


def crops(before,after,body,tracking):
    refs=[before,after];windows=[tracking.get('beforeCropBounds',body),tracking.get('afterCropBounds',tracking['afterBounds'])]
    items=[];masks=[]
    for i,(ref,window,b) in enumerate(zip(refs,windows,[body,tracking['afterBounds']])):
        path=h.checked(h.ROOT,ref)
        with Image.open(path) as im:masks.append(body_mask(b,window,im.size))
        items.append(dict(id=str(i),path=str(path),sha256=ref['sha256'],bounds=window))
    result=native.invoke(items)['results']
    images=[Image.open(io.BytesIO(base64.b64decode(r['png'],validate=True))).convert('RGB') for r in result]
    return images,masks[0]&masks[1]


def proposals(prediction,images,mask):
    full=stability.measure(*images);body=metrics(*images,mask)
    # Region changes only stability; highlight evidence keeps the original full crop.
    decisions={name:stability.guard(stability.extend(prediction,m,settings_context=True),full)['decision']
               for name,m in [('full',full),('body',body)]}
    return dict(full=full,body=body,decisions=decisions,bodyPixels=int(mask.sum()),
        outside=metrics(*images,~mask) if (~mask).sum()>=256 else None)


def sheet(images,mask,path):
    delta=np.abs(np.asarray(images[1],dtype=float)-np.asarray(images[0],dtype=float))
    heat=Image.fromarray(np.uint8(np.clip(delta*4,0,255)))
    overlay=images[1].copy();a=np.asarray(overlay).copy();a[~mask]=(a[~mask]*.25).astype('uint8')
    panels=[images[0],images[1],heat,Image.fromarray(a)]
    canvas=Image.new('RGB',(1024,280),(30,30,30));draw=ImageDraw.Draw(canvas)
    for i,(im,label) in enumerate(zip(panels,['Before','Tracked after','Absolute difference x4','Measured body mask'])):
        canvas.paste(im,(i*256,24));draw.text((i*256+5,5),label,fill='white')
    canvas.save(path)


def run(previous,output):
    previous=h.local(previous);source=h.sealed(previous,'settings-stability-v1')
    h.checked(h.ROOT,source['implementation'])
    h.require(source['policy']==stability.POLICY and source['changePolicy']==stability.CHANGE_POLICY,'changed_stability_policy')
    baseline=h.sealed(h.checked(h.ROOT,source['baseline']),'focus-recorded-comparison-v1')
    for ref in baseline['implementation']:h.checked(h.ROOT,ref)
    sem=h.sealed(h.checked(h.ROOT,baseline['semantics']),'focus-recorded-semantics-v1')
    h.checked(h.ROOT,sem['implementation'])
    args={k:str(h.checked(h.ROOT,v)) for k,v in sem['inputs'].items() if k!='events'}
    _,truth,_,_=semantic.inputs(**args)
    output=h.fresh(output);output.mkdir(parents=True);runtime=native.identity();start=time.monotonic()
    actions=[];gallery=['# Settings crop diagnosis','','Same production crops in every arm. Difference panel is amplified4x.',''];count=0
    for action in baseline['actions']:
        if action['status']!='retrospective-diagnostic':continue
        before,after=[truth[action['endpoints'][k]['sha256']] for k in ('before','after')]
        by={c['id']:c for c in before['controls']};predictions=[copy.deepcopy(c['prediction']) for c in action['controls']]
        diagnostic=[];arms={k:copy.deepcopy(predictions) for k in ('full','body')}
        for i,p in enumerate(predictions):
            count+=1;h.require(count<=100 and time.monotonic()-start<300,'context_budget')
            if p['tracking']['status']!='matched':continue
            ims,mask=crops(before['image'],after['image'],by[p['id']]['bounds'],p['tracking'])
            measured=proposals(p,ims,mask);diagnostic.append(dict(id=p['id'],tracking=p['tracking'],**measured))
            for arm in arms:arms[arm][i]['decision']=measured['decisions'][arm]
            if measured['decisions']['full'] in ('unknown','unavailable'):
                path=output/f'{count:03d}.png';sheet(ims,mask,path)
                gallery += [f"## Frame{action['endpoints']['before']['sequence']} — {action['controls'][i]['text']}",
                    f"Full: {measured['decisions']['full']}; body: {measured['decisions']['body']}; tracking dx/dy: {p['tracking']['dx']:.3f}/{p['tracking']['dy']:.3f}",
                    f'![Before, after, difference and mask]({path.resolve()})','']
        scored={k:comparison.compare(ps,before['controls'],after['controls'],action['matches']) for k,ps in arms.items()}
        actions.append(dict(actionID=action['actionID'],endpoints=action['endpoints'],diagnostic=diagnostic,arms=scored,
            fullScreenOutcome={k:stability.action_outcome([r['arms']['combined'] for r in rs],
                action['completeEndpoints'] and all(r['expected'] is not None for r in rs)) for k,rs in scored.items()}))
    h.require(native.identity()==runtime,'context_runtime_changed')
    summaries={k:evaluate.summarize([r['arms']['combined'] for a in actions for r in a['arms'][k]]) for k in arms}
    h.require(summaries['full']==source['summaries']['guarded'],'baseline_replay_mismatch')
    report=dict(version='settings-context-v1',**h.FLAGS,source=h.ref(previous),runtime=runtime,actions=actions,
        summaries=summaries,implementation=h.ref(h.ROOT/'scripts/settings_context_probe.py'),elapsedSeconds=time.monotonic()-start)
    h.write(output/'result.json',report,sealed=True);(output/'gallery.md').write_text('\n'.join(gallery))
    print(summaries);return report


def stress(output):
    from focus_transition_stress import scene
    output=h.fresh(output);output.mkdir(parents=True);a=scene()
    neighbor=scene();ImageDraw.Draw(neighbor).rectangle((190,185,370,194),fill='white')
    outline=scene();ImageDraw.Draw(outline).rectangle((198,198,361,261),outline='white',width=2)
    content=scene();ImageDraw.Draw(content).rectangle((220,210,335,225),fill='white')
    cases=[('neighbor_only',neighbor,'unchanged'),('focus_outline',outline,'unknown'),
        ('content_only',content,'unknown'),('highlight',scene(shade=235),'arrival'),
        ('scroll',scene(dy=-100),'unchanged')]
    rows=[];runtime=native.identity()
    for name,after,expected in cases:
        refs=[]
        for side,im in [('before',a),('after',after)]:
            path=output/(name+'-'+side+'.png');im.save(path);refs.append(h.ref(path))
        predictions,_=evaluate.predict(*refs,[dict(id='row',bounds=[200,200,160,60])]);p=predictions[0]
        if p['tracking']['status']=='matched':
            ims,mask=crops(*refs,[200,200,160,60],p['tracking']);r=proposals(p,ims,mask)
            sheet(ims,mask,output/(name+'-diagnosis.png'))
        else:r=dict(decisions=dict.fromkeys(('full','body'),comparison.decision(p,'combined')))
        rows.append(dict(name=name,expected=expected,prediction=p,inputs=refs,**r))
    h.require(native.identity()==runtime,'stress_runtime_changed')
    report=dict(version='settings-context-stress-v1',**h.FLAGS,generatedSoftwareFixture=True,cases=rows,
        correct={k:sum(r['decisions'][k]==r['expected'] for r in rows) for k in ('full','body')},
        runtime=runtime,implementation=h.ref(h.ROOT/'scripts/settings_context_probe.py'))
    h.write(output/'result.json',report,sealed=True);print(report['correct']);return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--previous');p.add_argument('--output',required=True)
    p.add_argument('--stress',action='store_true');a=p.parse_args()
    if a.stress:
        if a.previous:p.error('--stress cannot use --previous')
        stress(a.output)
    else:
        if not a.previous:p.error('--previous is required')
        run(a.previous,a.output)
