"""Fit the retained nonlinear output layer with explicit training constraints."""
from pathlib import Path
import time
import numpy as np
import scipy
import diagnose_guard322 as diagnostic

n=diagnostic.n;m=n.m;b=n.b;t=n.t;r=n.r;OUT=b.ROOT/'reports/work/FOCUS-323'


def apply_coefficients(net,coefficients):
    values=np.asarray(coefficients)
    b.require(values.shape==(9,) and np.isfinite(values).all() and (np.abs(values)<=1+1e-8).all(),'output_coefficients')
    layer=net.change.fusion.layers[2]
    with t.no_grad():
        layer.weight.copy_(t.as_tensor(values[:8],dtype=layer.weight.dtype)[None])
        layer.bias.copy_(t.as_tensor(values[8:],dtype=layer.bias.dtype))


def check_margins(scores,labels,logits):
    z=m.design(scores,labels);_,floor,keep=m.protected(z)
    b.require(logits.shape==labels.shape and np.isfinite(logits).all(),'output_logits')
    signed=(2*labels-1)*logits
    slack=signed[keep]-floor
    lost=int((signed[keep]<m.H).sum())
    b.require(slack.min()>=-2e-5 and lost==0,'protected_margin_failed')
    return dict(protectedRows=int(keep.sum()),minimumSlack=float(slack.min()),lostProtectedDecisions=lost)


def run():
    started=time.monotonic();t.set_num_threads(2);t.manual_seed(42)
    reg,d=m.inputs();prior=b.read(m.OUT/'nonlinear/registration.json');bound=b.read(m.OUT/'guard-diagnosis.json')
    for key in ('runner','trainer'):b.checked(prior[key])
    b.checked(bound['source']);b.checked(bound['candidateRegistration'])
    out=OUT/'run';b.require(not out.exists(),'output_collision');out.mkdir(parents=True)
    net=n.make(r.load_candidate(b.checked(reg['model'])),prior['center'],prior['scale'])
    frozen={k:v.clone() for k,v in net.state_dict().items() if not k.startswith('change.fusion.layers.2.')}
    scores=np.concatenate((d['original'],d['authored']));labels=np.r_[d['labels'],d['authoredLabels']]
    counts=np.bincount(d['auxiliaryIndices'],weights=d['weights'],minlength=len(d['authored']))
    b.require((counts>0).all(),'unscheduled_authored')
    weights=np.r_[d['weights'],.25*counts]/len(d['original'])
    with t.inference_mode():
        layer=net.change.fusion
        features=layer.layers[:2]((t.from_numpy(scores)-layer.center)/layer.scale).numpy()
    features=np.column_stack((features,np.ones(len(scores))))
    b.require(b.sha(features.tobytes())==bound['featureSHA256'],'feature_hash')
    b.write(out/'registration.json',dict(parent=b.ref(n.f.OUT/'registration.json'),prior=b.ref(m.OUT/'nonlinear/registration.json'),
        diagnostic=b.ref(m.OUT/'guard-diagnosis.json'),runner=b.ref(Path(__file__)),trainer=b.ref(Path(diagnostic.__file__)),
        modelSource=b.ref(Path(n.__file__)),solverSource=b.ref(Path(m.__file__)),evaluator=b.ref(Path(b.__file__)),
        torch=t.__version__,scipy=scipy.__version__,numpy=np.__version__,solver='HiGHS',threads=2,
        coefficientBounds=[-1,1],targetMargin=m.H+.25,thresholds=[.15,.85],featureSHA256=bound['featureSHA256'],
        trainableParameters=9,selection='Single direct constrained solve; no evaluation selection.',rolesChanged=False,
        outputCapBytes=256*1024**2,memoryBudgetBytes=8*1024**3))
    fit_start=time.monotonic();fit=diagnostic.fixed_feature_bound(scores,labels,weights,features)
    apply_coefficients(net,fit['diagnosticCoefficients'])
    b.require(all(t.equal(v,net.state_dict()[k]) for k,v in frozen.items()),'frozen_changed')
    with t.inference_mode():logits=net.change(t.from_numpy(scores)).flatten().numpy()
    constraints=check_margins(scores,labels,logits)
    fit.update(isTrainedModel=True,seconds=time.monotonic()-fit_start,constraints=constraints,frozenTensors=len(frozen),
        actualHinge=float(weights@np.maximum(0,m.H+.25-(2*labels-1)*logits)))
    b.require(abs(fit['actualHinge']-fit['minimumHinge'])<2e-5,'objective_parity')
    t.save(dict(state=net.state_dict(),representation=n.VERSION),out/'last.pt');restored=n.load(out/'last.pt')
    sanity=np.load(b.checked(reg['parityImages']),allow_pickle=False);imagep=b.worker.score(restored,sanity)
    with t.inference_mode():cachep=restored.change(t.from_numpy(d['original'][:8])).sigmoid().flatten().numpy()
    b.require(np.max(np.abs(imagep-cachep))<1e-6,'cache_image_parity')
    b.require(np.array_equal(imagep,b.worker.score(net,sanity)),'checkpoint_parity')
    p=1/(1+np.exp(-np.clip(logits,-80,80)))
    fit.update(original=b.trainer.w.summary(p[:len(d['original'])],d['labels']),
        authored=b.trainer.w.summary(p[len(d['original']):],d['authoredLabels']),
        probabilities=p.tolist(),cacheImageMaximumError=float(np.max(np.abs(imagep-cachep))))
    b.write(out/'fit.json',fit);print({k:v for k,v in fit.items() if k!='probabilities'},flush=True)
    membership=b.read(b.checked(reg['membership']));native=np.load(b.PACKAGE/'native.npy',allow_pickle=False)
    nd,_=r.prepare(native,membership['rows'],2)
    def transform(key,v):
        if key=='native.npy':return np.concatenate((v,nd),1)
        if key=='reverse_native.npy':return np.concatenate((v,r.reverse_details(nd)),1)
        return v
    initializer=b.checked(b.read(r.OUT/'registration.json')['initializer'])
    result=b.evaluate_full(restored,{'DTM085':r.s.c.model.load_candidate(initializer)},b.read(b.checked(reg['manifest'])),input_transform=transform)
    b.write(out/'evaluation.json',result)
    import report_authored319
    report_authored319.main(OUT,loader=n.load)
    b.write(OUT/'completion.json',dict(seconds=time.monotonic()-started,model=b.ref(out/'last.pt'),report=b.ref(OUT/'report.json'),productionEligible=False))
    b.require(sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<256*1024**2,'output_budget')
    print('Complete',time.monotonic()-started,flush=True)


if __name__=='__main__':run()
