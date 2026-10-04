"""Content/padding isolation and a single fixed residual robustness candidate."""
import argparse
import hashlib
import os
import time
from pathlib import Path
import numpy as np
import robustness126 as q
from diagnose_signal95 import encoded
from audit_transition119 import endpoint_bank
a=q.a;h=a.h
BASE=h.ROOT/'reports/work/CONTENT-ROBUSTNESS-127/artifacts'
CONFIG=dict(a.CONFIG,originalGroupCount=414,derivedGroupCount=452,initializer='DTM030',batch=414)


def intervene(x,mask,gain,offset,content=True):
    h.require(mask.shape==x.shape and mask.dtype==bool,'mask')
    return np.where(mask if content else ~mask,q.transform(x,gain,offset),x)


def setup():
    parent,rows,x,y,_=a.inputs()
    region=h.read(h.checked(h.ROOT,parent['admission']))['images']
    pairs=[v['images'] for v in rows]+[[b,c] for b,c in zip(region,region[1:])]
    bank=endpoint_bank(pairs,x[:207]); masks={}
    for entry in bank:
        im=a.r.d.pixels(entry['image']);tensor,t=encoded(im,im,size=(192,128))
        h.require(np.array_equal(tensor[:3],entry['pixels']),'production_encoding')
        sx,sy,px,py=t;rw,rh=round(im.width*sx),round(im.height*sy)
        mask=np.zeros((3,128,192),dtype=bool);mask[:,py:py+rh,px:px+rw]=True
        h.require((entry['pixels'][~mask]==0).all(),'nonzero_padding')
        key=hashlib.sha256(entry['pixels'].tobytes()).hexdigest()
        if key in masks:h.require(np.array_equal(mask,masks[key]),'ambiguous_content')
        masks[key]=mask
    mask=np.stack([np.concatenate([masks[hashlib.sha256(v[:3].tobytes()).hexdigest()],
                                  masks[hashlib.sha256(v[3:].tobytes()).hexdigest()]]) for v in x])
    torch=a.r.d.torch_runtime();torch.set_num_threads(2)
    bs=torch.load(h.checked(h.ROOT,parent['initializer']),weights_only=True,map_location='cpu')
    base=a.r.d.model(bs['configuration']);base.load_state_dict(bs['state']);base.eval()
    result=h.read(h.ROOT/'NativeUITrainer/focus_ring_runs/reflow117-dtm030/result.json')
    state=torch.load(h.checked(h.ROOT,result['model']),weights_only=True,map_location='cpu')
    net=a.r.model(base);net.load_state_dict(state['state']);net.eval()
    with torch.no_grad():ref=a.score(net,torch.from_numpy(x)).numpy()
    h.require(np.array_equal(ref,np.asarray(result['after'],dtype=np.float32)),'baseline_replay')
    groups=dict(oldTrain=parent['oldTrainIndices'],admittedSettings=parent['relatedSettingsIndices'],
                region=list(range(113,207)),identical=list(range(207,433)))
    return x,y,mask,net,ref,groups,result


def diagnose():
    out=h.fresh(BASE/'diagnosis');start=time.monotonic();x,y,mask,net,ref,groups,result=setup()
    torch=a.r.d.torch_runtime();reports={}
    with torch.no_grad():
        for name,(gain,offset) in q.TRANSFORMS.items():
            reports[name]={}
            for content in (True,False):
                v=intervene(x,mask,gain,offset,content)
                p=a.score(net,torch.from_numpy(v)).numpy()
                reports[name]['content' if content else 'padding']=dict(summary=q.summarize(p,y,groups,ref),probabilities=p.tolist())
    doc=dict(version=1,source=h.ref(__file__),encoder=h.ref(h.ROOT/'scripts/diagnose_signal95.py'),
        model=result['model'],tensorSHA256=hashlib.sha256(x.tobytes()).hexdigest(),
        maskSHA256=hashlib.sha256(mask.tobytes()).hexdigest(),reports=reports,elapsedSeconds=time.monotonic()-start,
        uniqueSourcesVerified=282,training=False)
    out.mkdir(parents=True);h.write(out/'report.json',doc,sealed=True)
    print({n:{kind:{g:v['correct'] for g,v in row['summary'].items()} for kind,row in r.items()} for n,r in reports.items()})


def train():
    start=time.monotonic();diag=h.read(BASE/'diagnosis/report.json')
    h.require(diag['seal']==h.digest({k:v for k,v in diag.items() if k!='seal'}),'diagnosis_seal')
    h.checked(h.ROOT,diag['source']);h.checked(h.ROOT,diag['encoder'])
    h.require(any(v['lostCorrect'] for v in diag['reports']['contrast']['content']['summary'].values()),'no_content_failure')
    h.require('Run DTM031 — CONTENT-ROBUSTNESS-127' in (h.ROOT/'Research/ExperimentLog.md').read_text(),'unlogged')
    out=a.r.d.old.fresh_run('content127-dtm031');x,y,mask,net,ref,groups,result=setup()
    h.require(hashlib.sha256(x.tobytes()).hexdigest()==diag['tensorSHA256'] and
              hashlib.sha256(mask.tobytes()).hexdigest()==diag['maskSHA256'],'changed_inputs')
    v=intervene(x,mask,.8,.1)
    tx=np.concatenate([x[:207],v[:207],x[207:],v[207:]])
    labels=np.concatenate([y[:207],y[:207],y[207:],y[207:]])
    torch=a.r.d.torch_runtime();out.mkdir(parents=True)
    h.write(out/'execution.json',dict(pid=os.getpid(),configuration=CONFIG,diagnosis=h.ref(BASE/'diagnosis/report.json'),
        initializer=result['model'],authority='User continued conditional CONTENT127 tranche; standing local training approval',status='started'))
    frozen={k:v.clone() for k,v in net.state_dict().items() if not k.startswith('change.')}
    tick=time.monotonic();net,history=a.r.d.fit_change_head(net,torch.from_numpy(tx),torch.from_numpy(labels),CONFIG)
    fit=time.monotonic()-tick;del tx,v
    h.require(all(torch.equal(v,net.state_dict()[k]) for k,v in frozen.items()),'frozen_changed')
    torch.save(dict(version=a.r.VERSION,configuration=CONFIG,state=net.state_dict(),initializer=result['model']),out/'last.pt')
    reports={}
    with torch.no_grad():
        for name,params in [('original',None),*q.TRANSFORMS.items()]:
            v=x if params is None else intervene(x,mask,*params)
            p=a.score(net,torch.from_numpy(v)).numpy()
            reports[name]=dict(summary=q.summarize(p,y,groups,ref),probabilities=p.tolist())
        saved=net.state_dict();net.load_state_dict(torch.load(out/'last.pt',weights_only=True,map_location='cpu')['state'])
        replay=a.score(net,torch.from_numpy(x)).numpy()
    h.require(np.array_equal(replay,np.asarray(reports['original']['probabilities'],dtype=np.float32)),'checkpoint_replay')
    retained=all(v['correct']==v['count'] for v in reports['original']['summary'].values())
    h.require(np.array_equal(replay[207:],ref[207:]),'identity_changed')
    h.write(out/'result.json',dict(experiment='DTM031',model=h.ref(out/'last.pt'),configuration=CONFIG,
        reports=reports,history=history,fitSeconds=fit,totalSeconds=time.monotonic()-start,retentionPassed=retained,
        frozenUnchanged=True,identityPreserved=True,checkpointReplay=True,productionEligible=False),sealed=True)
    h.require(sum(p.stat().st_size for p in out.iterdir())<2*1024**3,'output_cap')
    print({n:{g:v['correct'] for g,v in r['summary'].items()} for n,r in reports.items()})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['diagnose','train']);args=p.parse_args()
    diagnose() if args.mode=='diagnose' else train()
