"""Full-frame difference-channel interventions; never a cropper or deployable policy."""
import argparse
import math
from pathlib import Path
import time
import numpy as np
import focus_identity_residual as r
from diagnose_reflow115 import decisions

h=r.h


def mask(boxes,size,target=(192,128)):
    w,hg=size;W,H=target
    h.require(w>0 and hg>0 and len(boxes)==2,'mask_input')
    s=min(W/w,H/hg);rw,rh=max(1,round(w*s)),max(1,round(hg*s));px,py=(W-rw)//2,(H-rh)//2
    m=np.zeros((H,W),dtype=bool)
    for box in boxes:
        h.require(box is not None and len(box)==4 and all(math.isfinite(v) for v in box),'mask_box')
        l,t,bw,bh=box
        h.require(l>=0 and t>=0 and bw>0 and bh>0 and l+bw<=w+1e-5 and t+bh<=hg+1e-5,'mask_bounds')
        x0,y0=max(0,math.floor(l*rw/w+px)),max(0,math.floor(t*rh/hg+py))
        x1,y1=min(W,math.ceil((l+bw)*rw/w+px)),min(H,math.ceil((t+bh)*rh/hg+py))
        m[y0:y1,x0:x1]=True
    h.require(m.any(),'mask_empty')
    return m


def score(net,x,m,mode):
    torch=r.d.torch_runtime()
    h.require(mode in ('baseline','inside','outside') and tuple(m.shape)==(len(x),128,192),'intervention')
    results=[]
    with torch.no_grad():
        for at in range(0,len(x),16):
            a,b=x[at:at+16,:3],x[at:at+16,3:];diff=(b-a).abs()
            if mode!='baseline':
                keep=m[at:at+16] if mode=='inside' else ~m[at:at+16]
                diff=diff*keep[:,None]
            phi=net.encoder(torch.cat([diff,a,b],1))
            aa=net.encoder(torch.cat([torch.zeros_like(a),a,a],1))
            bb=net.encoder(torch.cat([torch.zeros_like(b),b,b],1))
            z=torch.cat([net.base_readout(phi),phi-(aa+bb)/2],1)
            results.extend(net.change(z).sigmoid().flatten().tolist())
    return np.array(results)


def summary(prob,baseline,truth,ids):
    p,b,t=prob[ids],baseline[ids],truth[ids]
    good=(decisions(p)==t.astype(int));old=(decisions(b)==t.astype(int))
    return dict(count=len(ids),confidentCorrect=int(good.sum()),lostSuccesses=int((old&~good).sum()),
        abstentions=int((decisions(p)==-1).sum()),falseChanges=int(((decisions(p)==1)&~t).sum()),
        missedChanges=int(((decisions(p)==0)&t).sum()))


def run(output):
    start=time.monotonic();out=h.fresh(output)
    p=h.read(r.PARENT);h.require(p['protocolSHA256']==h.digest({k:v for k,v in p.items() if k!='protocolSHA256'}),'protocol')
    old=h.read(h.checked(h.ROOT,p['oldProtocol']))
    rows=r.d.admitted(h.read(h.checked(h.ROOT,old['corpus'])),h.read(h.checked(h.ROOT,old['admission'])))[:73]
    ref=h.read(h.checked(h.ROOT,old['ranker']))
    h.require(ref['seal']==h.digest({k:v for k,v in ref.items() if k!='seal'}),'reference')
    h.checked(h.ROOT,ref['model']);h.checked(h.ROOT,ref['inputs'])
    h.require([v['id'] for v in ref['results'][:73]]==[v['id'] for v in rows],'proposal_membership')
    result_path=h.ROOT/'NativeUITrainer/focus_ring_runs/identity114-dtm029/result.json'
    result=h.read(result_path);h.require(result['seal']==h.digest({k:v for k,v in result.items() if k!='seal'}),'result')
    x=np.load(h.checked(h.ROOT,p['inputs']['evaluation'],256*1024**2),allow_pickle=False)[:73]
    torch=r.d.torch_runtime();torch.set_num_threads(2)
    state=torch.load(h.checked(h.ROOT,p['initializer']),map_location='cpu',weights_only=True)
    base=r.d.model(state['configuration']);base.load_state_dict(state['state']);net=r.model(base)
    state=torch.load(h.checked(h.ROOT,result['model']),map_location='cpu',weights_only=True)
    h.require(state['version']==r.VERSION,'model_version');net.load_state_dict(state['state']);net.eval()
    truth=np.array([v['changed'] for v in rows]);tx=torch.from_numpy(x)
    groups=dict(training=[i for i,v in enumerate(rows) if v['split']=='train'],settings=[24,25,26,27,28],
        positives=np.flatnonzero(truth).tolist(),negatives=np.flatnonzero(~truth).tolist())
    baseline=np.array(result['after'][:73]);arms={}
    for name,boxes in [('oracle',[v['boxes'] for v in rows]),
        ('DTM020',[[v['bounds'] if v else None for v in row['selected']] for row in ref['results'][:73]])]:
        masks=np.stack([mask(b,v['size']) for b,v in zip(boxes,rows)])
        variants={mode:score(net,tx,torch.from_numpy(masks),mode) for mode in ('baseline','inside','outside')}
        h.require(np.allclose(variants['baseline'],baseline,atol=1e-6,rtol=0),'baseline_replay')
        arms[name]=dict(probabilities={k:v.tolist() for k,v in variants.items()},
            groups={mode:{g:summary(v,baseline,truth,ids) for g,ids in groups.items()} for mode,v in variants.items()},
            sourceBoxes=boxes,maskPixels=masks.sum((1,2)).tolist(),failedReflow={k:float(v[25]) for k,v in variants.items()})
    out.mkdir(parents=True)
    doc=dict(version='focus116-difference-intervention-v1',input=p['inputs']['evaluation'],
        sourceProtocol=h.ref(r.PARENT),model=result['model'],proposalReference=old['ranker'],
        rowIDs=[v['id'] for v in rows],arms=arms,proposalIoUs=[v['boxIoUs'] for v in ref['results'][:73]],
        excluded=dict(new40='unresolved source geometry conflicts',region94='no admitted body geometry'),
        elapsedSeconds=time.monotonic()-start,implementation=h.ref(__file__),
        limitation='OOD diagnostic; oracle uses labels. Neither mask is a validated deployable input policy.',training=False)
    h.write(out/'report.json',doc,sealed=True)
    for name,arm in arms.items():print(name,arm['failedReflow'],arm['groups'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);run(p.parse_args().output)
