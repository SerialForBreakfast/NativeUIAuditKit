"""Audit retained pairs and compare 3 fixed representations in one batch."""
import argparse
from collections import Counter, defaultdict
import time
import numpy as np
import transition245 as t

OUT=t.h.ROOT/'reports/work/TRANSITION-247/artifacts'


def audit(values, labels, rows):
    """Count exact ordered and reversal-equivalent inputs without changing membership."""
    ordered=defaultdict(list); unordered=defaultdict(list)
    for i, pair in enumerate(values):
        a,b=(t.p.sha(v.tobytes()) for v in (pair[:3],pair[3:]))
        ordered[(a,b)].append(i);unordered[tuple(sorted((a,b)))].append(i)
    conflicts=[ids for ids in unordered.values() if len(set(labels[ids].tolist()))>1]
    groups=Counter(r['group'] for r in rows)
    return dict(rows=len(values),orderedUnique=len(ordered),reversalUnique=len(unordered),
                maximumMultiplicity=max(map(len,unordered.values())),conflicts=conflicts,
                labels=dict(Counter(map(int,labels))),groups=dict(groups),
                independentTrials=False)


def ridge_fit(features, labels, penalty=.01):
    t.p.review.require(features.ndim==2 and len(features)==len(labels) and
                       np.isfinite(features).all() and set(labels.tolist())=={0,1},'probe_inputs')
    mean=features.mean(0);scale=features.std(0);scale[scale<1e-6]=1
    x=np.column_stack(((features-mean)/scale,np.ones(len(features))))
    weights=np.array([.5/(labels==v).sum() for v in labels])
    regularizer=np.eye(x.shape[1])*penalty;regularizer[-1,-1]=0
    coef=np.linalg.solve(x.T@(weights[:,None]*x)+regularizer,x.T@(weights*labels))
    return dict(mean=mean,scale=scale,coef=coef)


def predict(model,features):
    return np.clip(np.column_stack(((features-model['mean'])/model['scale'],np.ones(len(features))))@model['coef'],0,1)


def features(values, torch, net=None):
    result=[]
    with torch.inference_mode():
        for start in range(0,len(values),8):
            x=torch.from_numpy(np.ascontiguousarray(values[start:start+8]))
            if net is not None:
                z=net.change[:8](net.change_inputs(x))
            else:
                a,b=x[:,:3],x[:,3:];delta=b-a
                # Edge differences retain signed changes in local contrast.
                ea=torch.nn.functional.pad(a[:,:,:,1:]-a[:,:,:,:-1],(0,1))
                eb=torch.nn.functional.pad(b[:,:,:,1:]-b[:,:,:,:-1],(0,1))
                va=torch.nn.functional.pad(a[:,:,1:,:]-a[:,:,:-1,:],(0,0,0,1))
                vb=torch.nn.functional.pad(b[:,:,1:,:]-b[:,:,:-1,:],(0,0,0,1))
                z=torch.nn.functional.adaptive_avg_pool2d(
                    torch.cat((delta,delta.abs(),(eb-ea).abs(),(vb-va).abs()),1),(4,6)).flatten(1)
            result.append(z.numpy().copy())
    return np.concatenate(result).astype(np.float64)


def counts(prob,labels):
    abstaining=t.n.w.summary(prob,labels)
    forced=t.n.w.summary(np.where(prob>=.5,1.,0.),labels)
    return dict(abstaining=abstaining,forced=forced)


def run():
    t.p.review.require(not OUT.exists(),'output_collision')
    started=time.monotonic();rows,x,_,prior=t.prepare()
    torch=t.n.d.torch_runtime();torch.set_num_threads(2)
    old_x,_,mask,_,_,_,_,_,replay,replay_y=t.n.inputs()
    control=t.h.read(t.p.CONTROL/'protocol.json')
    t.p.review.require(t.p.sha(replay.tobytes())==control['trainingSHA256'] and
                       t.p.sha(replay_y.tobytes())==control['labelsSHA256'],'replay_changed')
    train=np.array([i for i,r in enumerate(rows) if r['role']=='train']);truth=np.array([r['changed'] for r in rows])
    OUT.mkdir(parents=True)
    report=audit(x,truth,rows)
    report.update(excluded=prior['excluded'],roleCounts=dict(Counter(r['role'] for r in rows)),
                  conditionCounts=dict(Counter(c for r in rows for c in r['conditions'])),
                  absent=['qualified real-app efficacy','scrolling condition','modal condition','temporal settling sequences'])
    t.h.write(OUT/'audit.json',report,sealed=True)
    t.p.review.require(not report['conflicts'],'conflicting_labels')
    ty=np.concatenate((replay_y,truth[train],truth[train]))
    t.h.write(OUT/'protocol.json',dict(source=t.h.ref(__file__),trainer='closed-form diagnostic ridge',
        penalty=.01,weighting='equal class mass; original row membership retained',
        rows=rows,trainingIDs=[r['id'] for r in rows if r['role']=='train'],
        labelsSHA256=t.p.sha(ty.tobytes()),replayProtocol=t.h.ref(t.p.CONTROL/'protocol.json'),
        thresholds=[.15,.5,.85],selection='none; report all 3',productionEligible=False),sealed=True)
    models={
        'DTM054_features':t.h.checked(t.h.ROOT,t.h.read(t.p.CONTROL/'result.json')['model']),
        'DTM063_features':t.h.checked(t.h.ROOT,t.sealed(t.h.ROOT/'reports/work/TRANSITION-245/artifacts/DTM063/result.json')['model']),
        'spatial_differences':None}
    output={}
    for name,checkpoint in models.items():
        tick=time.monotonic();net=None
        if checkpoint:
            net=t.n.make_model(torch,paired_context=True)
            net.load_state_dict(torch.load(checkpoint,map_location='cpu',weights_only=True)['state']);net.eval()
        native=features(x,torch,net);reverse_native=features(t.reverse(x),torch,net)
        rf=features(replay,torch,net)
        training=np.concatenate((rf,native[train],reverse_native[train]))
        fitted=ridge_fit(training,ty)
        np.savez(OUT/(name+'.npz'),native=native,reverseNative=reverse_native,replay=rf,**fitted)
        prob=predict(fitted,native)
        entry=dict(checkpoint=t.h.ref(checkpoint) if checkpoint else None,cache=t.h.ref(OUT/(name+'.npz')),
                   native=t.summaries(prob,rows),nativeForced=t.summaries(np.where(prob>=.5,1.,0.),rows),
                   probabilities=prob.tolist(),training=counts(predict(fitted,training),ty),
                   reverseNative=t.summaries(predict(fitted,reverse_native),rows),
                   replay=counts(predict(fitted,rf),replay_y),regression={})
        for condition,values,labels in [('reversedReplay',t.reverse(replay),replay_y)]+[
            (mode,t.n.nuisance.localized(old_x[207:],mask[207:],mode),np.zeros(len(old_x)-207))
            for mode in ('global8','left8','center8')]:
            scores=predict(fitted,features(values,torch,net))
            entry['regression'][condition]=dict(**counts(scores,labels),scores=scores.tolist())
        entry['seconds']=time.monotonic()-tick;output[name]=entry
        t.h.write(OUT/(name+'.json'),entry,sealed=True)
        print(name,entry['native'],'seconds',entry['seconds'],flush=True)
    t.h.write(OUT/'result.json',dict(models=output,seconds=time.monotonic()-started,
        protocol=t.h.ref(OUT/'protocol.json'),audit=t.h.ref(OUT/'audit.json'),
        cachedPixelBaseline=t.h.ref(t.diagnostic.OUT/'result.json'),
        calibratedProbabilities=False,independentEvaluation=False,productionEligible=False),sealed=True)
    t.p.review.require(sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<2*1024**3,'output_budget')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args();run()
