"""Measure disturbance strength and order without changing model decisions."""
import argparse
import time
import numpy as np
import transition245 as t
import transition249_worker as worker

OUT=t.h.ROOT/'reports/work/TRANSITION-250/artifacts'
PACKAGE=t.h.ROOT/'reports/work/TRANSITION-249/artifacts/package'


def interpolate(x,strength):
    t.p.review.require(strength in (0.,.25,.5,1.) and x.ndim==4 and x.shape[1]==6,'interpolation_contract')
    y=x.copy();y[:,3:]=x[:,:3]+strength*(x[:,3:]-x[:,:3])
    if strength==1:y[:,3:]=x[:,3:]
    return y


def run():
    t.p.review.require(not OUT.exists(),'output_collision')
    start=time.monotonic();torch=t.n.d.torch_runtime();torch.set_num_threads(2)
    refs={'DTM054':t.h.read(t.p.CONTROL/'result.json')['model']}
    cached={'DTM054':t.sealed(t.h.ROOT/'reports/work/TRANSITION-245/artifacts/baseline-regression.json')}
    for name in ('DTM066','DTM067'):
        doc=t.sealed(t.h.ROOT/f'reports/work/TRANSITION-248/artifacts/{name}/result.json')
        refs[name]=doc['model'];cached[name]=doc['regression']
    manifest=t.h.read(PACKAGE/'manifest.json');results=[]
    for name,ref in refs.items():
        net=t.n.make_model(torch,paired_context=True)
        net.load_state_dict(torch.load(t.h.checked(t.h.ROOT,ref),map_location='cpu',weights_only=True)['state']);net.eval()
        for mode in ('global8','left8','center8'):
            path=PACKAGE/(mode+'.npy');pin=manifest['files'][path.name]
            t.p.review.require(worker.digest(path)==pin['sha256'],'input_changed')
            x=np.load(path,mmap_mode='r',allow_pickle=False)
            for strength in (0.,.25,.5,1.):
                values=interpolate(x,strength)
                p=worker.score(net,values);reverse=worker.score(net,t.reverse(values))
                if strength==1:
                    t.p.review.require(np.allclose(p,cached[name][mode]['probabilities'],atol=1e-6,rtol=0),'retained_parity')
                results.append(dict(model=name,condition=mode,strength=strength,
                    summary=t.n.w.summary(p,np.zeros(len(p))),reverse=t.n.w.summary(reverse,np.zeros(len(p))),
                    orderDecisionChanges=int((t.p.decisions(p)!=t.p.decisions(reverse)).sum()),
                    probabilities=p.tolist(),reverseProbabilities=reverse.tolist()))
    OUT.mkdir(parents=True)
    t.h.write(OUT/'result.json',dict(source=t.h.ref(__file__),models=refs,manifest=t.h.ref(PACKAGE/'manifest.json'),
        results=results,seconds=time.monotonic()-start,retainedParity=True,
        independentTrials=False,productionEligible=False),sealed=True)
    for r in results:
        print(r['model'],r['condition'],r['strength'],r['summary'],'order_changes',r['orderDecisionChanges'])


if __name__=='__main__':argparse.ArgumentParser().parse_args();run()
