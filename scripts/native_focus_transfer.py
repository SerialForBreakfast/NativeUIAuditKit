"""Frozen Native26 cue diagnostics and explicitly gated offline advisory caller."""
import argparse
import base64
from collections import Counter
import io
import json
import math
from pathlib import Path
import time

import native_focus_spike as n
import native_focus_spike_model as metrics
import focus_runtime as runtime

PROTOCOL=n.ROOT/'reports/work/NATIVE-FOCUS-EFFECT-SPIKE-26/model-protocols/native26-common.json'
RUN=n.ROOT/'NativeUITrainer/focus_ring_runs/fdr036-native26-common'
READINESS=n.ROOT/'reports/work/FOCUS-REVIEWED-TRANSITIONS-21/artifacts/listrow-reviewed-readiness.json'


def checked(ref):
    p=Path(ref['path'])
    if not p.is_absolute():p=n.ROOT/p
    p=p.resolve()
    n.require(p.is_relative_to(n.ROOT) or p.is_relative_to(n.USB),'input_outside_scope')
    if p.is_relative_to(n.USB):n.mounted()
    n.require(p.is_file() and n.sha(p)==ref['sha256'],'changed_input')
    return p


def geometry(bounds,size):
    n.require(len(bounds)==4 and all(type(v) in (int,float) and math.isfinite(v) for v in bounds),
              'invalid_geometry')
    x,y,w,h=bounds;W,H=size
    n.require(W>0 and H>0 and W*H<=40_000_000 and w>0 and h>0 and x>=0 and y>=0 and
              x+w<=W and y+h<=H,'invalid_geometry')
    window=[x-.2*w,y-.2*h,1.4*w,1.4*h]
    n.require(window[0]>=0 and window[1]>=0 and window[0]+window[2]<=W and
              window[1]+window[3]<=H,'reference_context_clipped')
    return window


def gate(request):
    """Caller attestations are prerequisites, not proof of live observation."""
    n.require(request.get('version')==1,'request_version')
    reasons=[]
    for field in ('knownUnfocusedReference','sameScreen','settled','nativeEffect',
                  'correspondenceVerified','contextClear','unoccluded'):
        if request.get(field) is not True:reasons.append(field)
    for field in ('imageAgeSeconds','referenceAgeSeconds'):
        value=request.get(field)
        if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=5:
            reasons.append(field)
    for field in ('referenceEvidence','contextEvidence'):
        if not isinstance(request.get(field),str) or not request[field].strip():reasons.append(field)
    if reasons:return dict(status='unavailable',reasons=reasons,advisoryOnly=True)
    geometry(request['referenceBounds'],request['imageSize'])
    return dict(status='eligible',reasons=[],advisoryOnly=True)


class Scorer:
    def __init__(self):
        import torch
        import focus_visual_experiment as visual
        from focus_dataset_contract import digest
        from focus_pretrained_experiment import state_digest
        self.torch=torch;self.started=time.monotonic()
        self.protocol=json.loads(PROTOCOL.read_text());p=self.protocol
        n.require(p['protocolSHA256']==digest({k:v for k,v in p.items() if k!='protocolSHA256'}),'protocol_digest')
        result=json.loads((RUN/'result.json').read_text())
        checkpoint=torch.load(RUN/'weights/final.pt',map_location='cpu',weights_only=True)
        n.require(checkpoint['protocolSHA256']==result['protocolSHA256']==p['protocolSHA256'],
                  'checkpoint_protocol')
        n.require(torch.backends.mps.is_available(),'mps_unavailable')
        self.prefix=visual.make_network(p['representation']).features[:9].eval().to('mps')
        n.require(state_digest(self.prefix)==p['prefixSHA256'],'prefix_changed')
        self.model=visual.make_model(p['representation'],'visual-local-partial','mps')
        self.model.load_state_dict(checkpoint['state_dict'],strict=True);self.model.eval()
        n.require(state_digest(self.model)==result['modelSHA256'],'model_changed')
        self.identity=dict(protocol=metrics.local_ref(PROTOCOL),checkpoint=metrics.local_ref(RUN/'weights/final.pt'),
            result=metrics.local_ref(RUN/'result.json'),packages=visual.packages(),device='mps')

    def score(self,images):
        import numpy as np
        t=self.torch
        n.require(0<len(images)<=32 and time.monotonic()-self.started<1800,'inference_budget')
        n.require(all(im.size==(256,256) for im in images),'crop_size')
        rep=self.protocol['representation']['normalization']
        with t.no_grad():
            x=t.stack([t.from_numpy(np.array(im.convert('RGB'),copy=True)).permute(2,0,1) for im in images]).to('mps').float()/255
            mean=t.tensor(rep['mean'],device='mps')[None,:,None,None]
            std=t.tensor(rep['std'],device='mps')[None,:,None,None]
            f=self.prefix((x-mean)/std)
            f=t.cat([f,t.ones_like(f[:,:1])],dim=1)[:,None]
            return t.sigmoid(self.model(f)).flatten().cpu().tolist()


def crop(item,root):
    from PIL import Image
    row=runtime.invoke([item],image_root=root)['results'][0]
    im=Image.open(io.BytesIO(base64.b64decode(row['png'],validate=True)));im.load()
    n.require(im.size==(256,256),'runtime_crop_size')
    return im.convert('RGB')


def advisory(request,scorer_factory=Scorer):
    from PIL import Image
    status=gate(request)
    if status['status']!='eligible':return status
    path=checked(request['image']);ref=checked(request['referenceImage'])
    with Image.open(path) as im:n.require(list(im.size)==request['imageSize'],'image_size')
    with Image.open(ref) as im:n.require(list(im.size)==request['imageSize'],'reference_size')
    item=dict(id='candidate',path=str(path),sha256=request['image']['sha256'],
              bounds=n.common_window(request['referenceBounds']))
    im=crop(item,n.USB if path.is_relative_to(n.USB) else n.ROOT)
    scorer=scorer_factory();prob=scorer.score([im])[0]
    return dict(status='scored',probability=prob,
        candidateState='focused' if prob>=.85 else 'unfocused' if prob<=.15 else 'uncertain',
        advisoryOnly=True,qualification='synthetic-only; caller-asserted prerequisites; uncalibrated score',
        model=scorer.identity,request=request,runtime=runtime.identity())


def audit_real():
    import human_annotation_review as h
    import focus_recorded_readiness as r
    old=json.loads(READINESS.read_text());refs=old['inputs']
    for value in refs.values():checked(value)
    args=[n.ROOT/refs[k]['path'] for k in ('batch','baseline','pending','revision','completeness')]
    fresh=r.run(*args)
    truth=r.reviewed_frames(r.baseline_reader.baseline(args[1]),*args[2:])
    selected=[]
    for a in fresh['actions']:
        if not (a['metadataReady'] and a['annotationsComplete']):continue
        b,c=[truth[a['endpoints'][side]['sha256']] for side in ('before','after')]
        selected.append(dict(actionID=a['actionID'],screens=[b['screen'],c['screen']],
            beforeTypes=dict(Counter(h.control_label(x) for x in b['controls'])),
            afterTypes=dict(Counter(h.control_label(x) for x in c['controls'])),
            unfocusedBefore=sum(x['state']=='unfocused' for x in b['controls']),
            qualifiedNativeArtworkPair=False,
            gaps=['native_effect_applicability_unverified','persistent_identity_unverified']))
    return dict(inputs=refs,counts=fresh['counts'],reviewedActions=selected,
        eligibleNativeArtworkPairs=0,
        scope='Existing recorded action ledger and immutable reviewed endpoints, not every stored screenshot',
        missing='Reviewed native-artwork transition with independently known unfocused reference and correspondence',
        readiness=fresh)


def neutralize(image,body,reference):
    """Diagnostic-only oracle rectangular mask; never runtime preprocessing."""
    import numpy as np
    from PIL import Image
    x,y,w,h=reference;wx=x-.2*w;wy=y-.2*h
    bx,by,bw,bh=body
    xs=wx+(np.arange(256)+.5)*1.4*w/256
    ys=wy+(np.arange(256)+.5)*1.4*h/256
    mask=(ys[:,None]>=by)&(ys[:,None]<by+bh)&(xs[None,:]>=bx)&(xs[None,:]<bx+bw)
    pixels=np.array(image.convert('RGB'),copy=True);pixels[mask]=128
    return Image.fromarray(pixels)


def probes(output):
    from PIL import Image
    out=Path(output).resolve();n.require(out.is_relative_to(n.ROOT) and not out.exists(),'output_collision')
    scorer=Scorer();p=scorer.protocol
    rows=[s for s in p['samples'] if s['role']=='evaluation'];n.require(len(rows)==500,'evaluation_count')
    saved=json.loads((RUN/'result.json').read_text())['predictions']
    n.require([s['id'] for s in rows]==[s['id'] for s in saved],'evaluation_order')
    # No source or label selection by model error. Preserve every reserved example.
    out.mkdir(parents=True);source={};images={k:[] for k in ('common','equal-size','body-neutralized')}
    scores={k:[] for k in images};sample_refs=[];started=time.monotonic()
    for i,row in enumerate(rows):
        n.require(time.monotonic()-started<1800,'probe_wall_budget')
        with Image.open(checked(dict(path=row['path'],sha256=row['sha256']))) as im:common=im.convert('RGB')
        group=row['configurationGroup'];variant=int(row['caseID'].rsplit('v',1)[1]);chunk=group*5+variant//25
        if chunk not in source:
            f=n.ROOT/f'reports/work/NATIVE-FOCUS-EFFECT-SPIKE-26/batch/chunk-{chunk:03d}/accepted.json'
            expected=next(x for x in p['sourceEvidence'] if x['path']==str(f.relative_to(n.ROOT)))
            checked(expected);source[chunk]={r['caseID']:r for r in json.loads(f.read_text())['rows']}
        pair=source[chunk][row['caseID']];frame=pair['frames'][row['label']];ref=pair['frames'][0]['bounds']
        path=checked(dict(path=frame['path'],sha256=frame['sha256']))
        equal=crop(dict(id=row['id'],path=str(path),sha256=frame['sha256'],
            bounds=n.common_window(frame['bounds'])),n.USB)
        values=dict(common=common,**{'equal-size':equal,'body-neutralized':neutralize(common,frame['bounds'],ref)})
        if variant==0:
            for kind,image in values.items():
                dest=out/f'{row["caseID"]}-{row["label"]}-{kind}.png';image.save(dest)
                sample_refs.append(dict(id=row['id'],kind=kind,image=metrics.local_ref(dest)))
        for kind,image in values.items():images[kind].append(image)
        if len(images['common'])==32 or i==len(rows)-1:
            for kind in images:scores[kind]+=scorer.score(images[kind]);images[kind].clear()
            print('scored',i+1,flush=True)
    difference=max(abs(a-b['probability']) for a,b in zip(scores['common'],saved))
    n.require(difference<1e-5,'baseline_score_parity')
    result=dict(model=scorer.identity,runtime=runtime.identity(),code=metrics.local_ref(Path(__file__)),
        seconds=time.monotonic()-started,baselineMaximumScoreDifference=difference,
        rows=rows,samples=sample_refs,comparisons={})
    for kind,values in scores.items():
        strata={}
        for bg in ('dark','light'):
            ids=[i for i,r in enumerate(rows) if r['background']==bg]
            strata[bg]=metrics.metric([rows[i] for i in ids],[values[i] for i in ids],.85)
        result['comparisons'][kind]=dict(at05=metrics.metric(rows,values,.5),at085=metrics.metric(rows,values,.85),
            backgrounds=strata,predictions=[dict(id=r['id'],label=r['label'],probability=s) for r,s in zip(rows,values)])
    n.write(out/'results.json',result)
    print(json.dumps({k:v['at085'] for k,v in result['comparisons'].items()}))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['audit','probes','advisory'])
    parser.add_argument('--request');parser.add_argument('--output',required=True);a=parser.parse_args()
    output=Path(a.output).resolve();n.require(output.is_relative_to(n.ROOT) and not output.exists(),'output_collision')
    if a.mode=='probes':probes(output);return
    if a.mode=='audit':result=audit_real()
    else:
        request=Path(a.request).resolve();n.require(request.is_relative_to(n.ROOT) and request.stat().st_size<65536,'request_scope')
        result=advisory(json.loads(request.read_text()))
    n.write(output,result);print(json.dumps({k:v for k,v in result.items() if k in ('status','counts','eligibleNativeArtworkPairs')}))


if __name__=='__main__':main()
