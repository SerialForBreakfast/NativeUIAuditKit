"""Fit one guarded nonlinear correction over retained branch scores."""
import argparse
from pathlib import Path
import time
import numpy as np
import margin322 as m

f=m.f;b=m.b;t=m.t;r=m.r;OUT=m.OUT
VERSION='nonlinear322-v1'


class Residual(t.nn.Module):
    def __init__(self,center,scale):
        super().__init__()
        self.register_buffer('center',t.as_tensor(center,dtype=t.float32))
        self.register_buffer('scale',t.as_tensor(scale,dtype=t.float32))
        b.require(self.center.shape==self.scale.shape==(2,) and t.isfinite(self.center).all()
                  and t.isfinite(self.scale).all() and (self.scale>0).all(),'normalization')
        self.layers=t.nn.Sequential(t.nn.Linear(2,8),t.nn.Tanh(),t.nn.Linear(8,1))
        t.nn.init.zeros_(self.layers[2].weight);t.nn.init.zeros_(self.layers[2].bias)

    def forward(self,scores):
        return scores.sum(1,keepdim=True)+self.layers((scores-self.center)/self.scale)


def make(base,center,scale):
    net=f.extend(base);net.change.fusion=Residual(center,scale);return net


def load(path):
    saved=t.load(path,map_location='cpu',weights_only=True)
    b.require(saved.get('representation')==VERSION,'nonlinear_checkpoint')
    state=saved['state']
    net=make(r.extend(r.s.c.model.extend(b.worker.make_model(t,paired_context=True)),2),
             state['change.fusion.center'],state['change.fusion.scale'])
    net.load_state_dict(state);return net.eval()


class Guard:
    """Backtrack unsafe updates using training scores only."""
    def __init__(self,net,scores,labels):
        z=m.design(scores,labels);_,floor,keep=m.protected(z)
        b.require(keep.any(),'empty_protected_set')
        self.x=t.from_numpy(scores[keep]);self.sign=t.from_numpy((2*labels[keep]-1).astype(np.float32))
        self.floor=t.as_tensor(floor,dtype=t.float32);self.count=int(keep.sum())
        self.previous=[p.detach().clone() for p in net.change.fusion.parameters()]
        self.calls=0;self.limited=0;self.reverted=0;self.minimumGap=0.

    def valid(self,net):
        with t.no_grad():
            values=net.change.fusion(self.x).flatten()*self.sign
            return bool(t.isfinite(values).all() and (values>=self.floor-1e-6).all()
                        and (values>=m.H).all())

    def __call__(self,net):
        params=list(net.change.fusion.parameters());proposed=[p.detach().clone() for p in params]
        self.calls+=1
        with t.no_grad():
            if not self.valid(net):
                self.limited+=1
                for exponent in range(1,13):
                    fraction=2.**(-exponent)
                    for p,old,new in zip(params,self.previous,proposed):p.copy_(old+fraction*(new-old))
                    if self.valid(net):break
                else:
                    for p,old in zip(params,self.previous):p.copy_(old)
                    self.reverted+=1
            b.require(self.valid(net),'nonlinear_guard_failed')
            self.previous=[p.detach().clone() for p in params]


def run():
    t.set_num_threads(2);t.manual_seed(42);started=time.monotonic();reg,d=m.inputs()
    audit=b.read(OUT/'separation.json');b.checked(audit['parent']);b.checked(audit['runner'])
    b.require(not audit['positive']['feasible'] and not audit['supportsCorrection'],'unexpected_linear_result')
    out=OUT/'nonlinear';b.require(not out.exists(),'run_collision');out.mkdir()
    x=d['original'];y=d['labels'];ids=d['auxiliaryIndices'];ax=d['authored'][ids]
    scores=np.concatenate((x,ax));labels=np.r_[y,y]
    center=scores.mean(0);scale=np.maximum(scores.std(0),1.)
    net=make(r.load_candidate(b.checked(reg['model'])),center,scale)
    frozen={k:v.clone() for k,v in net.state_dict().items() if not k.startswith('change.fusion.layers.')}
    config=dict(reg['configuration'],nonlinearFusion=True,marginLoss=True,lr=.001)
    guard=Guard(net,scores,labels)
    b.require(guard.valid(net),'initial_guard')
    b.write(out/'registration.json',dict(parent=b.ref(f.OUT/'registration.json'),audit=b.ref(OUT/'separation.json'),
        runner=b.ref(Path(__file__)),trainer=b.ref(Path(b.trainer.__file__)),configuration=config,thresholds=[.15,.85],
        trainableParameters=33,selection='fixed-last',rolesChanged=False,guardedScheduledExamples=guard.count,
        center=center.tolist(),scale=scale.tolist(),guard='12 bounded halvings, then revert; training successes only',
        authority='User-approved FOCUS322. One nonlinear correction after infeasible scalar audit. Output 256 MiB; memory 8 GiB.'))
    net,history=b.trainer.fit(net,t.from_numpy(x),t.from_numpy(y),config,lambda row:print(row,flush=True),t.from_numpy(d['weights']),
        auxiliary_inputs=t.from_numpy(ax),auxiliary_weight=.25,step_guard=guard)
    b.require(all(t.equal(v,net.state_dict()[k]) for k,v in frozen.items()),'frozen_changed')
    t.save(dict(state=net.state_dict(),representation=VERSION),out/'last.pt');restored=load(out/'last.pt')
    sanity=np.load(b.checked(reg['parityImages']),allow_pickle=False);imagep=b.worker.score(restored,sanity)
    with t.inference_mode():cachep=restored.change(t.from_numpy(x[:8])).sigmoid().flatten().numpy()
    b.require(np.max(np.abs(imagep-cachep))<1e-6,'cache_image_parity')
    b.require(np.array_equal(imagep,b.worker.score(net,sanity)),'checkpoint_parity')
    with t.inference_mode():
        op=net.change(t.from_numpy(x)).sigmoid().flatten().numpy()
        ap=net.change(t.from_numpy(d['authored'])).sigmoid().flatten().numpy()
    b.write(out/'fit.json',dict(history=history,seconds=time.monotonic()-started,frozenTensors=len(frozen),
        cacheImageMaximumError=float(np.max(np.abs(imagep-cachep))),guardCalls=guard.calls,limitedUpdates=guard.limited,
        revertedUpdates=guard.reverted,original=b.trainer.w.summary(op,y),authored=b.trainer.w.summary(ap,d['authoredLabels']),
        originalProbabilities=op.tolist(),authoredProbabilities=ap.tolist()))
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
    report_authored319.main(OUT,loader=load,run_folder=out)
    b.write(OUT/'completion.json',dict(seconds=time.monotonic()-started,model=b.ref(out/'last.pt'),report=b.ref(OUT/'report.json'),productionEligible=False))
    b.require(sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<256*1024**2,'output_budget')
    print('Complete',time.monotonic()-started,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args();run()
