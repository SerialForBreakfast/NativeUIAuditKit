"""Pinned dual evidence preparation and one frozen-feature correction fit."""
import argparse
import hashlib
import os
import time
import numpy as np
import nuisance129 as n
s=n.s;c=n.c;a=n.a;h=n.h;q=n.q
BASE=h.ROOT/'reports/work/DUAL-EVIDENCE-130/artifacts'
READY=BASE/'ready03'
CONFIG=dict(c.CONFIG,originalGroupCount=1073,derivedGroupCount=226,initializer='DTM031',batch=1073)


def probabilities(logits):
    torch=a.r.d.torch_runtime();flat=logits.reshape(-1).contiguous()
    h.require(len(flat)==433,'score_membership')
    return torch.cat([flat[:424].sigmoid(),flat[424:].sigmoid()]).numpy()


def model():
    torch=a.r.d.torch_runtime()
    class Head(torch.nn.Module):
        def __init__(self):
            super().__init__();self.linear=torch.nn.Linear(1152,1,bias=False)
            torch.nn.init.zeros_(self.linear.weight)
        def forward(self,z):return z[:,:1]+self.linear(z[:,1:])
    class Net(torch.nn.Module):
        def __init__(self):super().__init__();self.change=Head()
    return Net().eval()


def features(net,x,mask):
    if len(x)==433:
        return np.concatenate([features(net,x[:424],mask[:424]),features(net,x[424:],mask[424:])])
    torch=a.r.d.torch_runtime();normalized,_=n.normalize(x,mask,'affine')
    identical=np.all(x[:,:3]==x[:,3:],axis=(1,2,3));normalized[identical]=x[identical]
    with torch.no_grad():
        raw=net.change_inputs(torch.from_numpy(x));norm=net.change_inputs(torch.from_numpy(normalized))
        z=torch.cat([net.change(raw),raw[:,1:],norm[:,1:]],1).numpy()
    h.require(np.isfinite(z).all() and z.shape==(len(x),1153) and (z[identical,1:]==0).all(),'feature_identity')
    return z


def prepare():
    start=time.monotonic();out=h.fresh(READY);x,y,mask,net,_,groups,_=c.setup()
    candidate=h.read(h.ROOT/'NativeUITrainer/focus_ring_runs/content127-dtm031/result.json')
    torch=a.r.d.torch_runtime();net.load_state_dict(torch.load(h.checked(h.ROOT,candidate['model']),weights_only=True,map_location='cpu')['state']);net.eval()
    parent=h.read(h.ROOT/'reports/work/ASYMMETRIC-ROBUSTNESS-128/artifacts/audit/report.json')
    h.require(parent['seal']==h.digest({k:v for k,v in parent.items() if k!='seal'}),'parent')
    cache={};out.mkdir(parents=True)
    for name,cfg in [('original',None)]+[(k,v['configuration']) for k,v in parent['conditions'].items()]:
        v=x if cfg is None else s.intensity(x,mask,cfg['gain'],cfg['offset'],cfg['endpoint']) if cfg['kind']=='intensity' else s.shift(x,mask,cfg['dx'],cfg['both'])
        z=features(net,v,mask);np.save(out/(name+'.npy'),z,allow_pickle=False);cache[name]=h.ref(out/(name+'.npy'))
        p=probabilities(torch.from_numpy(z[:,0]))
        expected=candidate['reports']['original']['probabilities'] if cfg is None else parent['conditions'][name]['models']['DTM031']['probabilities']
        h.require(np.array_equal(p,np.asarray(expected,dtype=np.float32)),'frozen_replay')
        print('prepared',name,flush=True)
    doc=dict(version=1,experiment='DTM032',configuration=CONFIG,model=candidate['model'],source=h.ref(__file__),
        trainer=h.ref(a.r.d.__file__),normalizer=h.ref(n.__file__),featureCache=cache,labels=y.tolist(),groups=groups,
        sourceProtocol=h.ref(a.READY/'protocol.json'),tensorSHA256=hashlib.sha256(x.tobytes()).hexdigest(),
        maskSHA256=hashlib.sha256(mask.tobytes()).hexdigest(),seconds=time.monotonic()-start,
        trainingVariants=['original','contrast_0','contrast_1'],shiftAdmission=False,independentFinalEligible=False)
    h.write(out/'protocol.json',doc,sealed=True)


def execute():
    start=time.monotonic();p=h.read(READY/'protocol.json')
    h.require(p['seal']==h.digest({k:v for k,v in p.items() if k!='seal'}) and p['configuration']==CONFIG,'protocol')
    for key in ('source','trainer','normalizer','model'):h.checked(h.ROOT,p[key])
    h.require('Run DTM032 — DUAL-EVIDENCE-130' in (h.ROOT/'Research/ExperimentLog.md').read_text(),'unlogged')
    out=a.r.d.old.fresh_run('dual130-dtm032');torch=a.r.d.torch_runtime();torch.set_num_threads(2)
    cache={name:np.load(h.checked(h.ROOT,ref),allow_pickle=False) for name,ref in p['featureCache'].items()}
    labels=np.asarray(p['labels'],dtype=np.float32)
    z=np.concatenate([cache['original'][:207],cache['contrast_0'],cache['contrast_1'],cache['original'][207:]])
    y=np.concatenate([labels[:207],labels,labels,labels[207:]])
    h.require(z.shape==(1299,1153) and (z[-226:,1:]==0).all(),'membership')
    net=model();out.mkdir(parents=True);h.write(out/'execution.json',dict(pid=os.getpid(),protocol=h.ref(READY/'protocol.json'),authority='Assigned autonomous experiment tranche',configuration=CONFIG,status='started'))
    tick=time.monotonic();net,history=a.r.d.fit_change_features(net,torch.from_numpy(z),torch.from_numpy(y),CONFIG);fit=time.monotonic()-tick
    torch.save(dict(version='dual-evidence-v1',state=net.state_dict(),configuration=CONFIG,baseline=p['model']),out/'last.pt')
    replay=model();replay.load_state_dict(torch.load(out/'last.pt',weights_only=True,map_location='cpu')['state'])
    records={};reference=probabilities(torch.from_numpy(cache['original'][:,0]))
    with torch.no_grad():
        for name,f in cache.items():
            tx=torch.from_numpy(f);before=probabilities(tx[:,0]);after=probabilities(net.change(tx))
            h.require(np.array_equal(after,probabilities(replay.change(tx))),'checkpoint_replay')
            records[name]=dict(before=q.summarize(before,labels,p['groups'],reference),after=q.summarize(after,labels,p['groups'],before),probabilities=after.tolist())
    h.require(np.array_equal(np.array(records['original']['probabilities'],dtype=np.float32)[207:],reference[207:]),'identity_changed')
    retained=all(v['correct']==v['count'] for v in records['original']['after'].values())
    h.write(out/'result.json',dict(experiment='DTM032',model=h.ref(out/'last.pt'),protocol=h.ref(READY/'protocol.json'),records=records,
        history=history,fitSeconds=fit,totalSeconds=time.monotonic()-start,retentionPassed=retained,identityPreserved=True,
        checkpointReplay=True,productionEligible=False),sealed=True)
    h.require(sum(v.stat().st_size for v in out.iterdir())<2*1024**3,'output_budget')
    print({name:{g:r['correct'] for g,r in row['after'].items()} for name,row in records.items()})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','execute']);args=parser.parse_args()
    prepare() if args.mode=='prepare' else execute()
