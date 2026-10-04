"""Frozen-model channel and spatial interventions, never new ground truth."""
import argparse
import math
from pathlib import Path
import time
import numpy as np
import focus_direct_transition as d


def window(original=(3840,2160),target=(192,128),region=(2080,1590,3720,1840)):
    w,h=original;W,H=target;s=min(W/w,H/h);rw,rh=round(w*s),round(h*s)
    px,py=(W-rw)//2,(H-rh)//2;l,t,r,b=region
    return (max(0,math.floor(l*rw/w+px)),max(0,math.floor(t*rh/h+py)),
            min(W,math.ceil(r*rw/w+px)),min(H,math.ceil(b*rh/h+py)))


def intervention(net,x,mode):
    d.h.require(x.ndim==4 and tuple(x.shape[1:])==(6,128,192),'input_shape')
    torch=d.torch_runtime()
    if mode=='reversed':return net.change_inputs(torch.cat((x[:,3:],x[:,:3]),dim=1))
    y=net.change_inputs(x).clone()
    if mode=='baseline':pass
    elif mode=='difference_only':y[:,3:]=0
    elif mode=='context_only':y[:,:3]=0
    elif mode in ('focus_difference_only','outside_difference_only'):
        l,t,r,b=window()
        if mode=='outside_difference_only':y[:,:3,t:b,l:r]=0
        else:
            selected=y[:,:3,t:b,l:r].clone();y[:,:3]=0;y[:,:3,t:b,l:r]=selected
    else:raise ValueError('unknown_intervention')
    return y


def summarize(values,baseline,ids):
    a=values[ids];b=baseline[ids]
    return dict(count=len(ids),minimum=float(a.min()),maximum=float(a.max()),mean=float(a.mean()),
        confidentChanged=int((a>=.85).sum()),confidentUnchanged=int((a<=.15).sum()),
        uncertain=int(((a>.15)&(a<.85)).sum()),meanAbsoluteShift=float(np.abs(a-b).mean()),
        decisionChanges=int((((a>=.85)!=(b>=.85))|((a<=.15)!=(b<=.15))).sum()))


def run(output):
    h=d.h;out=h.fresh(output);start=time.monotonic()
    p=h.read(h.ROOT/'reports/work/REGION-REVIEW-112/artifacts/ready02/protocol.json')
    h.require(p['protocolSHA256']==h.digest({k:v for k,v in p.items() if k!='protocolSHA256'}),'protocol')
    prior=h.read(h.ROOT/'NativeUITrainer/focus_ring_runs/region112-dtm028/result.json')
    h.require(prior['seal']==h.digest({k:v for k,v in prior.items() if k!='seal'}) and prior['protocolSHA256']==p['protocolSHA256'],'result')
    x=np.load(h.checked(h.ROOT,p['inputs']['evaluation'],256*1024**2),allow_pickle=False)
    h.require(x.shape==(424,6,128,192) and x.dtype==np.float32 and np.isfinite(x).all(),'tensor')
    torch=d.torch_runtime();torch.set_num_threads(2);tx=torch.from_numpy(x)
    groups=dict(oldTrain=p['oldTrainIndices'],relatedSettings=p['relatedSettingsIndices'],region=list(range(113,207)),
        oldIdentical=list(range(207,329)),regionIdentical=list(range(329,424)))
    modes=('baseline','reversed','difference_only','context_only','focus_difference_only','outside_difference_only')
    results={}
    for name,ref,expected in [('DTM025',p['initializer'],prior['before']),('DTM028',prior['model'],prior['after'])]:
        state=torch.load(h.checked(h.ROOT,ref),map_location='cpu',weights_only=True)
        h.require(state['configuration']==d.PAIRED_TEMPORAL_CONFIG,'model_configuration')
        net=d.model(state['configuration']);net.load_state_dict(state['state']);net.eval();predictions={}
        for mode in modes:
            parts=[]
            with torch.inference_mode():
                for at in range(0,len(tx),16):parts.extend(net.change(intervention(net,tx[at:at+16],mode)).sigmoid().flatten().tolist())
            predictions[mode]=np.array(parts)
        h.require(np.allclose(predictions['baseline'],expected,atol=1e-6,rtol=0),'baseline_replay')
        summaries={mode:{g:summarize(v,predictions['baseline'],ids) for g,ids in groups.items()
            if mode not in ('focus_difference_only','outside_difference_only') or g in ('region','regionIdentical')}
            for mode,v in predictions.items()}
        gradients=[]
        for at in range(0,len(tx),16):
            y=net.change_inputs(tx[at:at+16]).detach().requires_grad_(True)
            grad=torch.autograd.grad(net.change(y).sum(),y)[0].detach()
            for v in grad:gradients.append([float(v[:3].abs().mean()),float(v[3:].abs().mean())])
        gradients=np.array(gradients)
        results[name]=dict(checkpoint=ref,variants={k:v.tolist() for k,v in predictions.items()},summaries=summaries,
            meanAbsoluteLogitInputGradient={g:dict(difference=float(gradients[ids,0].mean()),context=float(gradients[ids,1].mean())) for g,ids in groups.items()})
    out.mkdir(parents=True)
    h.write(out/'report.json',dict(version='region113-channel-intervention-v1',sourceProtocol=h.ref(h.ROOT/'reports/work/REGION-REVIEW-112/artifacts/ready02/protocol.json'),
        implementation=h.ref(__file__),input=p['inputs']['evaluation'],focusWindow=window(),results=results,
        elapsedSeconds=time.monotonic()-start,training=False,interventionsAreLabeledExamples=False,
        interpretation='Out-of-distribution sensitivity, not causal proof or generalization.'),sealed=True)
    for name,r in results.items():
        print(name,{mode:r['summaries'][mode]['region'] for mode in modes})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.output)
