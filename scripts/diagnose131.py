"""Frozen nuisance abstention and feature-separation diagnostics; not inference policy."""
import argparse
import hashlib
import time
from pathlib import Path
import numpy as np
import dual130 as d
n=d.n; c=d.c; a=d.a; h=d.h; q=d.q; s=d.s
TOLERANCES={'numerical':1e-5,'quantization_control':1/255}


def residuals(x,mask):
    h.require(x.ndim==4 and x.shape[1]==6 and mask.shape==x.shape and
              np.isfinite(x).all() and mask.dtype==bool,'input_contract')
    normalized,_=n.normalize(x,mask,'affine');records=[]
    for i in range(len(x)):
        support=mask[i,:3]
        h.require(support.any(),'empty_content')
        raw=np.abs(x[i,:3]-x[i,3:])[support]
        error=np.abs(normalized[i,3:]-x[i,:3])[support]
        records.append(dict(exactIdentity=bool((raw==0).all()),maximum=float(error.max()),
            mean=float(error.mean()),fractionAboveQuantization=float((error>1/255).mean()),
            rawMean=float(raw.mean())))
    return records


def abstain(p,records,tolerance):
    p=np.asarray(p,dtype=np.float32)
    h.require(len(p)==len(records) and np.isfinite(p).all() and
              ((p>=0)&(p<=1)).all() and tolerance>0,'guard_contract')
    out=p.copy()
    flagged=np.array([not r['exactIdentity'] and r['maximum']<=tolerance for r in records])
    out[flagged & (q.decisions(p)==1)]=.5
    return out,flagged


def separation(features,labels):
    z=np.asarray(features,dtype=np.float64);y=np.asarray(labels)
    h.require(z.ndim==2 and len(z)==len(y) and np.isfinite(z).all() and
              set(np.unique(y))=={0,1} and min((y==0).sum(),(y==1).sum())>=2,'separation_contract')
    # Direct subtraction avoids cancellation when checking near/exact collisions.
    opposite=[];same=[];neighbors=[];conflicts=[]
    for i in range(len(z)):
        distances=np.linalg.norm(z-z[i],axis=1)
        other=np.flatnonzero(y!=y[i]);own=np.flatnonzero((y==y[i])&(np.arange(len(y))!=i))
        j=int(other[np.argmin(distances[other])]);opposite.append(float(distances[j]));same.append(float(distances[own].min()));neighbors.append(j)
        conflicts.extend([i,int(k)] for k in other if k>i and np.array_equal(z[i],z[k]))
    std=z.std(axis=0);active=std[std>1e-12]
    singular=np.linalg.svd(z-z.mean(axis=0),compute_uv=False)
    rank=int((singular>singular[0]*1e-7).sum()) if singular[0]>0 else 0
    denom=float(np.median(same))
    return dict(count=len(z),dimensions=z.shape[1],activeDimensions=len(active),
        standardDeviationRange=[float(active.min()),float(active.max())] if len(active) else None,
        numericalRank=rank,conditionAtRank=float(singular[0]/singular[rank-1]) if rank else None,
        oppositeDistances=opposite,sameDistances=same,oppositeIndices=neighbors,exactConflicts=conflicts,
        oppositeMedian=float(np.median(opposite)),sameMedian=denom,
        relativeMedian=float(np.median(opposite)/denom) if denom>0 else None)


def sealed(path):
    value=h.read(path)
    h.require(value['seal']==h.digest({k:v for k,v in value.items() if k!='seal'}),'seal')
    return value


def run(output):
    start=time.monotonic();out=h.fresh(output)
    protocol=sealed(d.READY/'protocol.json')
    for key in ('source','trainer','normalizer','model'):h.checked(h.ROOT,protocol[key])
    cache={name:np.load(h.checked(h.ROOT,ref),allow_pickle=False) for name,ref in protocol['featureCache'].items()}
    x,y,mask,_,_,groups,_=c.setup()
    h.require(hashlib.sha256(x.tobytes()).hexdigest()==protocol['tensorSHA256'] and
              hashlib.sha256(mask.tobytes()).hexdigest()==protocol['maskSHA256'] and
              np.array_equal(y,protocol['labels']) and groups==protocol['groups'],'input_binding')
    previous_path=h.ROOT/'reports/work/ASYMMETRIC-ROBUSTNESS-128/artifacts/audit/report.json'
    previous=sealed(previous_path);conditions={};torch=a.r.d.torch_runtime();torch.set_num_threads(2)
    reference=d.probabilities(torch.from_numpy(cache['original'][:,0]))
    for name,cfg in [('original',None)]+[(k,v['configuration']) for k,v in previous['conditions'].items()]:
        v=x if cfg is None else s.intensity(x,mask,cfg['gain'],cfg['offset'],cfg['endpoint']) if cfg['kind']=='intensity' else s.shift(x,mask,cfg['dx'],cfg['both'])
        p=d.probabilities(torch.from_numpy(cache[name][:,0]));rows=residuals(v,mask);controls={}
        for key,tol in TOLERANCES.items():
            after,flagged=abstain(p,rows,tol)
            controls[key]=dict(summary=q.summarize(after,y,groups,p),flaggedIndices=np.flatnonzero(flagged).tolist(),probabilities=after.tolist())
        conditions[name]=dict(residuals=rows,before=q.summarize(p,y,groups,reference),controls=controls)
        print('audited',name,flush=True)
    tick=time.monotonic()
    z=np.concatenate([cache['original'][:207],cache['contrast_0'],cache['contrast_1'],cache['original'][207:]])
    labels=np.concatenate([y[:207],y,y,y[207:]])
    feature_report={key:separation(z[:,columns],labels) for key,columns in
                    [('raw',slice(1,577)),('normalized',slice(577,None)),('combined',slice(1,None))]}
    out.mkdir(parents=True)
    h.write(out/'report.json',dict(version=1,source=h.ref(__file__),normalizer=h.ref(n.__file__),
        protocol=h.ref(d.READY/'protocol.json'),parent=h.ref(previous_path),tolerances=TOLERANCES,
        conditions=conditions,featureDiagnostics=feature_report,featureSeconds=time.monotonic()-tick,
        totalSeconds=time.monotonic()-start,training=False,productionEligible=False,independentEvaluation=False),sealed=True)
    sealed(out/'report.json')
    print('completed',out,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.output)
