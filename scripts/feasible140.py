"""Source-pinned linear feasibility diagnosis through the real transition head."""
import argparse
import os
from pathlib import Path
import time
import numpy as np
import scipy
import correct_joint139 as a
import linear_feasibility as lp

j,h,d,c=a.j,a.h,a.d,a.c


def run(ready):
    started=time.monotonic();out=h.fresh(ready)
    p,cache,ref,families,prior,labels,z,y,guard,truth,ids=a.inputs()
    native=sum(families.values(),[]);ny=np.asarray([0 if i in families['identical_control'] else 1 for i in native],np.float32)
    x=np.concatenate([guard,cache['peer'][native]]);target=np.concatenate([truth,ny])
    h.require(x.shape==(993,1153) and len(set(native))==9,'witness_membership')
    h.require('DTM040 — FEASIBILITY-140' in (h.ROOT/'Research/ExperimentLog.md').read_text(),'unlogged')
    run_dir=d.a.r.d.old.fresh_run('feasible140-dtm040');out.mkdir(parents=True);run_dir.mkdir(parents=True)
    h.write(out/'protocol.json',dict(version='feasibility140-v1',source=h.ref(__file__),solver=h.ref(lp.__file__),
        parent=h.ref(a.PARENT),admission=h.ref(j.a.ADMISSION),baseline=prior['model'],configuration=dict(
        solver='highs-ds',scipy=scipy.__version__,timeLimit=60,target=lp.TARGET,objective='min-infinity-norm'),
        nativeIndices=native,constraintIndices=ids,featuresSHA256=j.hashlib.sha256(x.tobytes()).hexdigest(),
        labelsSHA256=j.hashlib.sha256(target.tobytes()).hexdigest(),independentEvaluation=False),sealed=True)
    h.write(run_dir/'execution.json',dict(experiment='DTM040',pid=os.getpid(),protocol=h.ref(out/'protocol.json'),
        authority='Standing development training; assigned one feasibility witness',status='started'),sealed=True)
    tick=time.monotonic();report,w=lp.solve(x,target);seconds=time.monotonic()-tick
    records={};checks={};model=None
    if w is not None:
        torch=d.a.r.d.torch_runtime();net=d.model();net.change.linear.weight.data.copy_(torch.from_numpy(w.astype(np.float32)[None]))
        torch.save(dict(version='feasible140-v1',correction=net.change.linear.weight.detach().clone(),baseline=prior['model'],
                        protocol=h.ref(out/'protocol.json')),run_dir/'last.pt');model=h.ref(run_dir/'last.pt')
        saved=torch.load(run_dir/'last.pt',weights_only=True,map_location='cpu');replay=d.model()
        replay.change.linear.weight.data.copy_(saved['correction'])
        with torch.inference_mode():
            margins=(2*target-1)*net.change(torch.from_numpy(x)).flatten().numpy()
            checks=dict(float32MinimumMargin=float(margins.min()),float32GatesPassed=bool((margins>=lp.TARGET-1e-6).all()))
            for name,f in cache.items():
                tx=torch.from_numpy(f);logits=net.change(tx)
                probs=logits.sigmoid().flatten().numpy() if name=='peer' else d.probabilities(logits)
                again=replay.change(tx).sigmoid().flatten().numpy() if name=='peer' else d.probabilities(replay.change(tx))
                h.require(np.array_equal(probs,again),'witness_replay')
                if name=='peer':records[name]=[dict(v,probability=float(q),decision=c.decision(float(q))) for v,q in zip(p['peer'],probs)]
                else:records[name]=dict(probabilities=probs.tolist(),summary=d.q.summarize(probs,labels,p['groups'],ref[name]))
        h.require(np.array_equal(np.asarray(records['original']['probabilities'],np.float32)[207:],ref['original'][207:]),'identity_changed')
        pp=d.q.decisions(np.asarray([r['probability'] for r in records['peer']]))
        checks['native']={k:dict(count=len(ii),correct=int((pp[ii]==(0 if k=='identical_control' else 1)).sum())) for k,ii in families.items()}
        checks['originalRetained']=all(v['correct']==v['count'] for v in records['original']['summary'].values())
        checks['contrastRetained']={k:bool(np.all(d.q.decisions(np.asarray(records[k]['probabilities']))[ii]==labels[ii])) for k,ii in ids.items()}
    h.write(run_dir/'result.json',dict(experiment='DTM040',protocol=h.ref(out/'protocol.json'),solver=report,
        checks=checks,records=records,model=model,solveSeconds=seconds,seconds=time.monotonic()-started,
        independentEvaluation=False,productionEligible=False),sealed=True)
    h.require(sum(v.stat().st_size for v in run_dir.rglob('*') if v.is_file())<2*1024**3,'output_budget')
    print(report,checks,'solveSeconds',seconds,flush=True)
    print({k:{g:v['correct'] for g,v in r['summary'].items()} for k,r in records.items() if k!='peer'},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--ready',type=Path,required=True);run(parser.parse_args().ready)
