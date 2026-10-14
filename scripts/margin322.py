"""Test score separation and preserve known training decision margins."""
import argparse
import math
from pathlib import Path
import time
import warnings
import numpy as np
from scipy.optimize import linprog, OptimizeWarning
from scipy import sparse
import fusion321 as f

b=f.b;t=f.t;r=f.r
OUT=b.ROOT/'reports/work/FOCUS-322'
H=math.log(.85/.15)


def design(scores,labels):
    f.margins(scores,labels)
    return np.column_stack((scores,np.ones(len(scores))))*(2*labels-1)[:,None]


def solve(c,A,rhs,bounds):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',OptimizeWarning)
        result=linprog(c,A_ub=A,b_ub=rhs,bounds=bounds,method='highs',options={'threads':2})
    b.require(result.status in (0,2),'solver_failure:'+str(result.message))
    return result


def feasible(scores,labels,positive=True):
    z=design(scores,labels)
    q=solve(np.zeros(3),-z,np.full(len(z),-H),[(0,None) if positive else (None,None)]*2+[(None,None)])
    return dict(feasible=q.success,status=int(q.status),parameters=q.x.tolist() if q.success else None)


def protected(z):
    baseline=z@np.array([1.,1.,0.]);keep=baseline>=H
    return z[keep],np.minimum(baseline[keep],H+.25),keep


def separation(scores,labels,weights):
    z=design(scores,labels);p,floor,keep=protected(z);n=len(z)
    b.require(weights.shape==(n,) and np.isfinite(weights).all() and (weights>0).all(),'audit_weights')
    A=sparse.vstack([sparse.hstack([-z,-sparse.eye(n)]),
                     sparse.hstack([-p,sparse.csr_matrix((len(p),n))])]).tocsr()
    q=solve(np.r_[np.zeros(3),weights],A,np.r_[np.full(n,-(H+.25)),-floor],
            [(1e-6,None)]*2+[(None,None)]+[(0,None)]*n)
    b.require(q.success,'protected_problem_infeasible')
    baseline=float(np.dot(weights,np.maximum(0,H+.25-z@np.array([1.,1.,0.]))))
    return dict(positive=feasible(scores,labels),unrestricted=feasible(scores,labels,False),
                protectedCount=int(keep.sum()),baselineHinge=baseline,minimumHinge=float(q.fun),
                diagnosticParameters=q.x[:3].tolist(),minimumProtectedSlack=float((p@q.x[:3]-floor).min()),
                supportsCorrection=bool(q.fun<baseline-1e-4))


class MarginGuard:
    """Keep a proposed update inside the training constraints."""
    def __init__(self,scores,labels):
        self.z,self.floor,self.keep=protected(design(scores,labels))
        b.require(len(self.z)>0,'empty_protected_set')
        self.calls=0;self.limited=0;self.minimumFraction=1.

    def __call__(self,net):
        layer=net.change.fusion
        with t.no_grad():
            coeff=t.nn.functional.softplus(layer.raw).double().numpy()
            proposal=np.r_[coeff,float(layer.bias[0])];base=np.array([1.,1.,0.])
            delta=self.z@(proposal-base);slack=self.z@base-self.floor
            bad=delta<0
            alpha=min(1.,float(np.min(np.maximum(slack[bad],0)/-delta[bad]))) if bad.any() else 1.
            if alpha<1:alpha*=.999
            accepted=base+alpha*(proposal-base)
            layer.raw.copy_(t.as_tensor(np.log(np.expm1(accepted[:2])),dtype=layer.raw.dtype))
            layer.bias.fill_(float(accepted[2]))
            self.calls+=1;self.limited+=int(alpha<1);self.minimumFraction=min(self.minimumFraction,alpha)
            actual=np.r_[t.nn.functional.softplus(layer.raw).double().numpy(),float(layer.bias[0])]
            b.require(np.min(self.z@actual-self.floor)>=-2e-5,'margin_guard_failed')


def inputs():
    reg=b.read(f.OUT/'registration.json')
    b.checked(b.read(f.OUT/'margins.json')['registration'])
    for key in ('model','runner','regions','sourceDetail','corpus','review','membership','manifest'):b.checked(reg[key])
    data=np.load(b.checked(reg['scores']),allow_pickle=False)
    b.require(np.array_equal(data['labels'],data['authoredLabels'][data['auxiliaryIndices']]),'auxiliary_labels')
    b.require(b.sha(data['labels'].tobytes())==reg['originalHashes']['labelsSHA256'],'labels_hash')
    b.require(b.sha(data['weights'].tobytes())==reg['originalHashes']['weightsSHA256'],'weights_hash')
    return reg,data


def audit():
    started=time.monotonic();reg,d=inputs();OUT.mkdir(exist_ok=True)
    b.require(not (OUT/'separation.json').exists(),'output_collision')
    count=np.bincount(d['auxiliaryIndices'],weights=d['weights'],minlength=len(d['authored']))
    ids=np.flatnonzero(count)
    scores=np.concatenate((d['original'],d['authored'][ids]));labels=np.r_[d['labels'],d['authoredLabels'][ids]]
    weights=np.r_[d['weights'],.25*count[ids]]/len(d['original'])
    result=separation(scores,labels,weights)
    result.update(original=feasible(d['original'],d['labels']),authored=feasible(d['authored'],d['authoredLabels']),
                  originalRows=len(d['original']),authoredRows=len(ids),seconds=time.monotonic()-started,
                  parent=b.ref(f.OUT/'registration.json'),runner=b.ref(Path(__file__)),evaluationUsed=False)
    b.write(OUT/'separation.json',result);print(result,flush=True)


def train():
    t.set_num_threads(2);started=time.monotonic();reg,d=inputs();audit=b.read(OUT/'separation.json')
    b.checked(audit['parent']);b.checked(audit['runner']);b.require(audit['supportsCorrection'],'no_supported_correction')
    run=OUT/'run';b.require(not run.exists(),'run_collision');run.mkdir()
    net=f.extend(r.load_candidate(b.checked(reg['model'])))
    frozen={k:v.clone() for k,v in net.state_dict().items() if not k.startswith('change.fusion.')}
    x=d['original'];y=d['labels'];ax=d['authored'][d['auxiliaryIndices']]
    guard=MarginGuard(np.concatenate((x,ax)),np.r_[y,y])
    config=dict(reg['configuration'],marginLoss=True)
    b.write(run/'registration.json',dict(parent=b.ref(f.OUT/'registration.json'),audit=b.ref(OUT/'separation.json'),
        runner=b.ref(Path(__file__)),trainer=b.ref(Path(b.trainer.__file__)),configuration=config,thresholds=[.15,.85],
        trainableParameters=3,selection='fixed-last',rolesChanged=False,guardedTrainingExamples=int(guard.keep.sum()),
        authority='User-approved FOCUS322. No wall limit. Output cap 256 MiB; memory budget 8 GiB.'))
    def progress(row):print(row,flush=True)
    net,history=b.trainer.fit(net,t.from_numpy(x),t.from_numpy(y),config,progress,t.from_numpy(d['weights']),
        auxiliary_inputs=t.from_numpy(ax),auxiliary_weight=.25,step_guard=guard)
    b.require(all(t.equal(v,net.state_dict()[k]) for k,v in frozen.items()),'frozen_changed')
    t.save(dict(state=net.state_dict(),representation=f.VERSION),run/'last.pt');restored=f.load_candidate(run/'last.pt')
    sanity=np.load(b.checked(reg['parityImages']),allow_pickle=False);imagep=b.worker.score(restored,sanity)
    with t.inference_mode():cachep=restored.change(t.from_numpy(x[:8])).sigmoid().flatten().numpy()
    b.require(np.max(np.abs(imagep-cachep))<1e-6,'cache_image_parity')
    b.require(np.array_equal(imagep,b.worker.score(net,sanity)),'checkpoint_parity')
    with t.inference_mode():
        op=net.change(t.from_numpy(x)).sigmoid().flatten().numpy()
        ap=net.change(t.from_numpy(d['authored'])).sigmoid().flatten().numpy()
    b.write(run/'fit.json',dict(history=history,seconds=time.monotonic()-started,coefficients=t.nn.functional.softplus(net.change.fusion.raw).detach().tolist(),
        bias=float(net.change.fusion.bias.detach()[0]),frozenTensors=len(frozen),cacheImageMaximumError=float(np.max(np.abs(imagep-cachep))),
        guardCalls=guard.calls,limitedUpdates=guard.limited,minimumFraction=guard.minimumFraction,
        original=b.trainer.w.summary(op,y),authored=b.trainer.w.summary(ap,d['authoredLabels'])))
    membership=b.read(b.checked(reg['membership']));native=np.load(b.PACKAGE/'native.npy',allow_pickle=False)
    nd,_=r.prepare(native,membership['rows'],2)
    def transform(key,v):
        if key=='native.npy':return np.concatenate((v,nd),1)
        if key=='reverse_native.npy':return np.concatenate((v,r.reverse_details(nd)),1)
        return v
    initializer=b.checked(b.read(r.OUT/'registration.json')['initializer'])
    result=b.evaluate_full(restored,{'DTM085':r.s.c.model.load_candidate(initializer)},b.read(b.checked(reg['manifest'])),input_transform=transform)
    b.write(run/'evaluation.json',result)
    import report_authored319
    report_authored319.main(OUT,loader=f.load_candidate)
    b.write(OUT/'completion.json',dict(seconds=time.monotonic()-started,model=b.ref(run/'last.pt'),report=b.ref(OUT/'report.json'),productionEligible=False))
    b.require(sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<256*1024**2,'output_budget')
    print('Complete',time.monotonic()-started,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['audit','train']);args=parser.parse_args()
    audit() if args.mode=='audit' else train()
