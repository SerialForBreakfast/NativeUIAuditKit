"""Falsify simple nuisance normalization without changing production inference."""
import argparse
from pathlib import Path
import time
import numpy as np
import asymmetric128 as s
c=s.c;a=s.a;h=s.h;q=s.q


def trimmed(values):
    flat=np.asarray(values).ravel();n=max(1,int(len(flat)*.8))
    return float(np.partition(flat,n-1)[:n].mean())


def affine(before,after):
    out=after.copy();params=[]
    for channel in range(3):
        x=after[channel].ravel().astype(np.float64);y=before[channel].ravel().astype(np.float64)
        ids=np.arange(len(x));gain=1.;offset=0.
        for _ in range(3):
            xm=x[ids].mean();ym=y[ids].mean();variance=np.mean((x[ids]-xm)**2)
            if variance>1e-10:
                gain=float(np.clip(np.mean((x[ids]-xm)*(y[ids]-ym))/variance,.5,2))
            offset=float(np.clip(ym-gain*xm,-.3,.3))
            residual=np.abs(gain*x+offset-y);n=max(1,int(len(x)*.8));ids=np.argpartition(residual,n-1)[:n]
        raw=gain*after[channel]+offset
        out[channel]=np.clip(raw,0,1);params.append(dict(gain=gain,offset=offset,clipped=int(((raw<0)|(raw>1)).sum())))
    return out,params


def align(before,after):
    width=before.shape[-1];scores={}
    for dx in range(-2,3):
        lo=max(0,-dx);hi=min(width,width-dx)
        scores[dx]=trimmed(np.abs(before[:,:,lo:hi]-after[:,:,lo+dx:hi+dx]))
    best=min(scores,key=lambda dx:(scores[dx],abs(dx),dx))
    if scores[0]<1e-8 or scores[best]>.8*scores[0]:best=0
    result=np.zeros_like(after);lo=max(0,-best);hi=min(width,width-best)
    result[:,:,lo:hi]=after[:,:,lo+best:hi+best]
    return result,dict(dx=best,scores={str(k):v for k,v in scores.items()})


def normalize(x,mask,mode):
    h.require(mode in ('affine','align','combined') and mask.shape==x.shape,'normalization_contract')
    out=x.copy();records=[]
    for i in range(len(x)):
        h.require(np.array_equal(mask[i,:3],mask[i,3:]),'viewport')
        ys,xs=np.where(mask[i,0]);top,bottom=ys.min(),ys.max()+1;left,right=xs.min(),xs.max()+1
        before=x[i,:3,top:bottom,left:right];after=x[i,3:,top:bottom,left:right]
        record={}
        if mode in ('align','combined'):after,record['alignment']=align(before,after)
        if mode in ('affine','combined'):after,record['affine']=affine(before,after)
        out[i,3:,top:bottom,left:right]=after;records.append(record)
    h.require(np.array_equal(out[~mask],x[~mask]),'padding_changed')
    return out,records


def run(output,reuse_alignment=None):
    start=time.monotonic();out=h.fresh(output);x,y,mask,net,_,groups,_=c.setup()
    previous=h.read(h.ROOT/'reports/work/ASYMMETRIC-ROBUSTNESS-128/artifacts/audit/report.json')
    h.require(previous['seal']==h.digest({k:v for k,v in previous.items() if k!='seal'}),'prior_seal')
    model_ref=previous['modelReferences']['DTM031'];torch=a.r.d.torch_runtime()
    reused=h.read(reuse_alignment) if reuse_alignment else None
    if reused:
        h.require(reused['seal']==h.digest({k:v for k,v in reused.items() if k!='seal'}) and
                  reused['model']==model_ref and reused['parent']==h.ref(h.ROOT/'reports/work/ASYMMETRIC-ROBUSTNESS-128/artifacts/audit/report.json'),'reuse_binding')
    net.load_state_dict(torch.load(h.checked(h.ROOT,model_ref),weights_only=True,map_location='cpu')['state']);net.eval()
    candidate=h.read(h.ROOT/'NativeUITrainer/focus_ring_runs/content127-dtm031/result.json')
    with torch.no_grad():reference=a.score(net,torch.from_numpy(x)).numpy()
    h.require(np.array_equal(reference,np.asarray(candidate['reports']['original']['probabilities'],dtype=np.float32)),'replay')
    results={}
    for name,config in [('original',None)]+[(n,r['configuration']) for n,r in previous['conditions'].items()]:
        v=x if config is None else s.intensity(x,mask,config['gain'],config['offset'],config['endpoint']) if config['kind']=='intensity' else s.shift(x,mask,config['dx'],config['both'])
        row={}
        for mode in ('affine','align','combined'):
            if mode=='align' and reused:
                row[mode]=reused['results'][name][mode];continue
            tick=time.monotonic();normalized,records=normalize(v,mask,mode)
            with torch.no_grad():p=a.score(net,torch.from_numpy(normalized)).numpy()
            row[mode]=dict(summary=q.summarize(p,y,groups,reference),probabilities=p.tolist(),transforms=records,seconds=time.monotonic()-tick)
        results[name]=row
    out.mkdir(parents=True);h.write(out/'report.json',dict(version=1,model=model_ref,source=h.ref(__file__),
        parent=h.ref(h.ROOT/'reports/work/ASYMMETRIC-ROBUSTNESS-128/artifacts/audit/report.json'),results=results,
        elapsedSeconds=time.monotonic()-start,training=False,productionChange=False,independentEvaluation=False,
        alignmentReusedFrom=h.ref(reuse_alignment) if reuse_alignment else None),sealed=True)
    print({name:{mode:(sum(r['summary'][g]['correct'] for g in ('oldTrain','admittedSettings','region')),r['summary']['identical']['correct']) for mode,r in row.items()} for name,row in results.items()})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--reuse-alignment',type=Path)
    args=p.parse_args();run(args.output,args.reuse_alignment)
