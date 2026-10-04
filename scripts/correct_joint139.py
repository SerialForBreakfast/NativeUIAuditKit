"""Matched corrected-margin experiment, using existing caches and feature trainer."""
import argparse
import os
from pathlib import Path
import time
import numpy as np
import joint_replay138 as j
import margin_retention as m

h,d,c=j.h,j.d,j.c
PARENT=h.ROOT/'reports/work/JOINT-REPLAY-138/artifacts/ready/protocol.json'


def inputs():
    p=c.audit.sealed(PARENT)
    h.require(p['pins']==j.pins() and p['configuration']==j.config(),'parent_changed')
    values=j.inputs();cache,z,y,ids=values[1],values[6],values[7],values[10]
    h.require(p['constraintIndices']==ids and p['bankSHA256']==j.hashlib.sha256(z.tobytes()).hexdigest() and
              p['labelsSHA256']==j.hashlib.sha256(y.tobytes()).hexdigest() and
              p['cacheHashes']=={k:j.hashlib.sha256(v.tobytes()).hexdigest() for k,v in cache.items()},'parent_bank_changed')
    return values


def pins():return dict(parent=h.ref(PARENT),source=h.ref(__file__),guard=h.ref(m.__file__))


def prepare(ready):
    out=h.fresh(ready);v=inputs();preflight=m.preflight(v[8],v[9],v[6],v[7]);out.mkdir(parents=True)
    h.write(out/'protocol.json',dict(version='margin139-v1',pins=pins(),configuration=j.config(),
        guard=m.VERSION,preflight=preflight,independentEvaluation=False),sealed=True)
    print(preflight,flush=True)


def train(ready):
    started=time.monotonic();protocol=c.audit.sealed(ready/'protocol.json')
    h.require(protocol['pins']==pins() and protocol['configuration']==j.config() and protocol['guard']==m.VERSION and
              'DTM039 — MARGIN-REPAIR-139' in (h.ROOT/'Research/ExperimentLog.md').read_text(),'changed_or_unlogged')
    p,cache,ref,families,prior,labels,z,y,guard,truth,ids=inputs()
    torch=d.a.r.d.torch_runtime();net=m.model(guard,truth)
    out=d.a.r.d.old.fresh_run('margin139-dtm039');out.mkdir(parents=True)
    h.write(out/'execution.json',dict(experiment='DTM039',pid=os.getpid(),protocol=h.ref(ready/'protocol.json'),
        authority='Standing training; assigned MARGIN139 fixed comparison',status='started'),sealed=True)
    trace=[];weights=[];gradients=[]
    def forward(head,args,output):
        trace.append(dict(radius=float(head.effective()[1].detach()),rawNorm=float(head.linear.weight.detach().norm())))
        weights.append(head.linear.weight.detach().numpy().copy())
    def gradient(value):gradients.append(value.detach().numpy().copy())
    fh=net.change.register_forward_hook(forward);gh=net.change.linear.weight.register_hook(gradient)
    tick=time.monotonic()
    net,history=d.a.r.d.fit_change_features(net,torch.from_numpy(z),torch.from_numpy(y),j.config())
    fit=time.monotonic()-tick;fh.remove();gh.remove()
    h.require(len(trace)==len(weights)==len(gradients)==600,'trace_membership')
    with torch.no_grad():weight,radius=net.change.effective();weight=weight.detach().clone()
    torch.save(dict(version='margin139-v1',correction=weight,rawState=net.state_dict(),baseline=prior['model'],
                    protocol=h.ref(ready/'protocol.json'),configuration=j.config()),out/'last.pt')
    np.savez(out/'optimization-trace.npz',rawWeights=np.stack(weights),gradients=np.stack(gradients))
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
    retained=all(v['count']==v['correct'] for v in records['original']['summary'].values())
    contrast={name:bool(np.all(d.q.decisions(np.asarray(records[name]['probabilities']))[ii]==labels[ii])) for name,ii in ids.items()}
    h.require(np.array_equal(np.asarray(records['original']['probabilities'],np.float32)[207:],ref['original'][207:]),'identity_changed')
    pp=np.asarray([v['probability'] for v in records['peer']]);summary={}
    for family,ii in families.items():
        decisions=d.q.decisions(pp[ii]);wanted=0 if family=='identical_control' else 1
        summary[family]=dict(count=len(ii),correct=int((decisions==wanted).sum()),abstentions=int((decisions==-1).sum()))
    h.write(out/'result.json',dict(experiment='DTM039',model=h.ref(out/'last.pt'),protocol=h.ref(ready/'protocol.json'),
        trace=h.ref(out/'optimization-trace.npz'),radiusHistory=trace,history=history,records=records,
        admittedSummary=summary,originalRetained=retained,contrastRetained=contrast,radius=float(radius),
        fitSeconds=fit,seconds=time.monotonic()-started,independentEvaluation=False,productionEligible=False),sealed=True)
    h.require(sum(v.stat().st_size for v in out.rglob('*') if v.is_file())<2*1024**3,'output_budget')
    print('retained',retained,'contrast',contrast,'admitted',summary,'radius',float(radius),'fitSeconds',fit,flush=True)
    print({k:{g:v['correct'] for g,v in r['summary'].items()} for k,r in records.items() if k!='peer'},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','train']);parser.add_argument('--ready',type=Path,required=True)
    args=parser.parse_args();prepare(args.ready) if args.mode=='prepare' else train(args.ready)
