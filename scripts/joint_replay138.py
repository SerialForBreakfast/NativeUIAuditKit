"""One joint replay experiment using admitted native and existing contrast views."""
import argparse
import hashlib
import os
from pathlib import Path
import time
import numpy as np
import adapt_retained137 as a

h,d,c=a.h,a.d,a.c


def bank(cache,labels,families):
    h.require(labels.shape==(433,) and np.isin(labels,[0,1]).all(), 'joint_labels')
    zs,ys=[],[]
    for family,count in [('within_screen',5),('screen_transition',2),('identical_control',2)]:
        ids=families[family];h.require(len(ids)==count and len(set(ids))==count, 'joint_family')
        z=cache['peer'][ids]
        zs.append(np.tile(z,(4330//count,1)))
        ys.append(np.full(4330,0 if family=='identical_control' else 1,np.float32))
    for name in ('contrast_0','contrast_1'):
        h.require(cache[name].shape==(433,1153), 'joint_contrast')
        zs.append(np.tile(cache[name],(10,1)));ys.append(np.tile(labels,10))
    x,y=np.concatenate(zs),np.concatenate(ys)
    h.require(x.shape==(21650,1153) and np.isfinite(x).all(), 'joint_bank')
    return x,y


def protected(cache,labels,reference):
    zs=[cache['original'][:207]];ys=[labels[:207]];indices={}
    for name in ('contrast_0','contrast_1'):
        ids=np.flatnonzero(d.q.decisions(reference[name])==labels)
        indices[name]=ids.tolist();zs.append(cache[name][ids]);ys.append(labels[ids])
    return np.concatenate(zs),np.concatenate(ys),indices


def config():
    return dict(a.configuration(),initializer='DTM036-joint-five-family',lossWeighting='equal-five-family-means',batch=21650)


def pins():
    return dict(adapter=a.pins(),source=h.ref(__file__))


def inputs():
    p,cache,ref,_,_,families,prior=a.load();labels=np.asarray(p['labels'],np.float32)
    z,y=bank(cache,labels,families);guard,truth,ids=protected(cache,labels,ref)
    return p,cache,ref,families,prior,labels,z,y,guard,truth,ids


def prepare(ready):
    out=h.fresh(ready);p,cache,ref,families,prior,labels,z,y,guard,truth,ids=inputs()
    out.mkdir(parents=True)
    h.write(out/'protocol.json',dict(version='joint138-v1',pins=pins(),configuration=config(),
        constraintIndices=ids,bankSHA256=hashlib.sha256(z.tobytes()).hexdigest(),
        labelsSHA256=hashlib.sha256(y.tobytes()).hexdigest(),families=families,
        cacheHashes={k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in cache.items()},
        weightedRows=len(z),sourceViews=875,independentEvaluation=False),sealed=True)
    print('prepared',len(z),'rows; contrast constraints',{k:len(v) for k,v in ids.items()},flush=True)


def train(ready):
    started=time.monotonic();protocol=c.audit.sealed(ready/'protocol.json')
    h.require(protocol['pins']==pins() and protocol['configuration']==config() and
              'Run DTM038 — JOINT-REPLAY-138' in (h.ROOT/'Research/ExperimentLog.md').read_text(),'changed_or_unlogged')
    p,cache,ref,families,prior,labels,z,y,guard,truth,ids=inputs()
    h.require(protocol['constraintIndices']==ids and protocol['families']==families and
              protocol['bankSHA256']==hashlib.sha256(z.tobytes()).hexdigest() and
              protocol['labelsSHA256']==hashlib.sha256(y.tobytes()).hexdigest() and
              protocol['cacheHashes']=={k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in cache.items()},'prepared_changed')
    net=a.t.retention.constrained_model(guard,truth);torch=d.a.r.d.torch_runtime()
    out=d.a.r.d.old.fresh_run('joint138-dtm038');out.mkdir(parents=True)
    h.write(out/'execution.json',dict(experiment='DTM038',pid=os.getpid(),protocol=h.ref(ready/'protocol.json'),
        authority='Standing training; assigned JOINT138; existing contrast and ADMISSION136 roles',status='started'),sealed=True)
    tick=time.monotonic();net,history=d.a.r.d.fit_change_features(net,torch.from_numpy(z),torch.from_numpy(y),config());fit=time.monotonic()-tick
    with torch.no_grad():weight,radius=net.change.effective();weight=weight.detach().clone()
    torch.save(dict(version='joint138-v1',correction=weight,baseline=prior['model'],configuration=config(),
                    protocol=h.ref(ready/'protocol.json')),out/'last.pt')
    saved=torch.load(out/'last.pt',weights_only=True,map_location='cpu');replay=d.model()
    replay.change.linear.weight.data.copy_(saved['correction']);records={}
    with torch.inference_mode():
        for name,f in cache.items():
            tx=torch.from_numpy(f);logits=net.change(tx)
            probs=logits.sigmoid().flatten().numpy() if name=='peer' else d.probabilities(logits)
            again=replay.change(tx).sigmoid().flatten().numpy() if name=='peer' else d.probabilities(replay.change(tx))
            h.require(np.array_equal(probs,again),'checkpoint_replay')
            if name=='peer':records[name]=[dict(v,probability=float(q),decision=c.decision(float(q))) for v,q in zip(p['peer'],probs)]
            else:records[name]=dict(probabilities=probs.tolist(),summary=d.q.summarize(probs,labels,p['groups'],ref[name]))
    original=all(v['count']==v['correct'] for v in records['original']['summary'].values())
    preserved={name:bool(np.all(d.q.decisions(np.asarray(records[name]['probabilities']))[ii]==labels[ii])) for name,ii in ids.items()}
    h.require(np.array_equal(np.asarray(records['original']['probabilities'],np.float32)[207:],ref['original'][207:]),'identity_changed')
    pp=np.asarray([v['probability'] for v in records['peer']]);summary={}
    for family,ii in families.items():
        decisions=d.q.decisions(pp[ii]);wanted=0 if family=='identical_control' else 1
        summary[family]=dict(count=len(ii),correct=int((decisions==wanted).sum()),abstentions=int((decisions==-1).sum()))
    h.write(out/'result.json',dict(experiment='DTM038',model=h.ref(out/'last.pt'),protocol=h.ref(ready/'protocol.json'),
        records=records,history=history,admittedSummary=summary,originalRetained=original,contrastRetained=preserved,
        radius=float(radius),fitSeconds=fit,seconds=time.monotonic()-started,productionEligible=False,independentEvaluation=False),sealed=True)
    h.require(sum(v.stat().st_size for v in out.rglob('*') if v.is_file())<2*1024**3,'output_budget')
    print('original',original,'contrast',preserved,'admitted',summary,'radius',float(radius),'fitSeconds',fit,flush=True)
    print({k:{g:v['correct'] for g,v in r['summary'].items()} for k,r in records.items() if k!='peer'},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','train']);parser.add_argument('--ready',type=Path,required=True)
    args=parser.parse_args();prepare(args.ready) if args.mode=='prepare' else train(args.ready)
