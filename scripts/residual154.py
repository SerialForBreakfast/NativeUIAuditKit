"""One source-balanced comparison after exact encoded-label conflict checks."""
import hashlib
import argparse
import os
import time
import numpy as np
import native_adapt152 as n
from diagnose_reflow115 import decisions
h=n.h


def conflicts(x,y):
    bank={}
    for i,v in enumerate(x):bank.setdefault(hashlib.sha256(v.tobytes()).hexdigest(),[]).append(i)
    return [ids for ids in bank.values() if len(set(y[ids].tolist()))>1]


def balanced(groups,count):
    flat=sum(groups.values(),[])
    h.require(sorted(flat)==list(range(count)) and all(groups.values()),'group_partition')
    w=np.empty(count,np.float32)
    for ids in groups.values():w[ids]=count/(len(groups)*len(ids))
    return w


def run(control=False):
    start=time.monotonic();torch=n.d.torch_runtime();torch.set_num_threads(2)
    x,y,mask,groups,px,rows,ids,ny,tx,ty=n.inputs()
    experiment='DTM054' if control else 'DTM053'
    out=n.d.old.fresh_run('residual158-dtm054' if control else 'residual154-dtm053-attempt2');out.mkdir(parents=True)
    allgroups=dict(groups,native=list(range(433,442)),globalNegative=list(range(442,668)))
    weights=np.ones(len(tx),np.float32) if control else balanced(allgroups,len(tx));bad=conflicts(tx,ty)
    parent=h.ROOT/'NativeUITrainer/focus_ring_runs/native152-dtm049/result.json';r=h.read(parent)
    old=np.r_[r['probabilities'],[r['nativeCases'][i]['probability'] for i in ids],r['stress']['global8']['probabilities']]
    failures=[]
    for i in np.flatnonzero(decisions(old)!=ty):
        candidates=np.flatnonzero(ty!=ty[i]);dist=[]
        for j in candidates:dist.append((float(np.sqrt(np.mean((tx[i]-tx[j])**2))),int(j)))
        failures.append(dict(index=int(i),label=int(ty[i]),probability=float(old[i]),
            nearestOpposite=[dict(index=j,rms=v) for v,j in sorted(dist)[:5]],
            meanFrameDifference=float(np.abs(tx[i,:3]-tx[i,3:]).mean())))
    h.write(out/'audit.json',dict(conflicts=bad,failures=failures,count=len(tx),groups=allgroups),sealed=True)
    h.require(not bad,'contradictory_encoded_labels')
    saved=torch.load(h.checked(h.ROOT,r['model']),weights_only=True,map_location='cpu')
    net=n.make_model(torch,paired_context=True);net.load_state_dict(saved['state']);net.eval()
    # Reproduce the parent's separate scoring calls, including batch boundaries.
    # Combining433original +9selected native rows changes floating-point kernels.
    parent_replay=np.r_[n.score(net,torch.from_numpy(x)),
        n.score(net,torch.from_numpy(px))[ids],n.score(net,torch.from_numpy(tx[442:]))]
    h.require(np.array_equal(parent_replay,old.astype(np.float32)),'parent_replay')
    h.require(experiment in (h.ROOT/'Research/ExperimentLog.md').read_text(),'unregistered')
    protocol=dict(experiment=experiment,initializer=r['model'],source=h.ref(__file__),trainer=h.ref(n.__file__),
        configuration=n.CONFIG,trainingSHA256=hashlib.sha256(tx.tobytes()).hexdigest(),
        labelsSHA256=hashlib.sha256(ty.tobytes()).hexdigest(),weightsSHA256=hashlib.sha256(weights.tobytes()).hexdigest(),
        groups=allgroups,independentEvaluation=False,authority='Standing training; one registered residual comparison;2GiB cap',uniformControl=control)
    h.write(out/'protocol.json',protocol,sealed=True);h.write(out/'execution.json',dict(pid=os.getpid(),status='started'))
    def progress(v):print(v,flush=True)
    net,history=n.fit(net,torch.from_numpy(tx),torch.from_numpy(ty),n.CONFIG,progress,torch.from_numpy(weights))
    torch.save(dict(version='residual154-v1',state=net.state_dict(),configuration=n.CONFIG),out/'last.pt')
    p=n.score(net,torch.from_numpy(tx));replay=n.make_model(torch,paired_context=True)
    replay.load_state_dict(torch.load(out/'last.pt',weights_only=True,map_location='cpu')['state']);replay.eval()
    h.require(np.array_equal(p,n.score(replay,torch.from_numpy(tx))),'checkpoint_replay')
    result=dict(experiment=experiment,model=h.ref(out/'last.pt'),history=history,probabilities=p.tolist(),
        groups={k:n.w.summary(p[v],ty[v]) for k,v in allgroups.items()},stress={},
        fitGatePassed=bool((decisions(p)==ty).all()),productionEligible=False,seconds=time.monotonic()-start)
    for mode in ('global8','left8','center8'):
        prob=n.score(net,torch.from_numpy(n.nuisance.localized(x[207:],mask[207:],mode)))
        result['stress'][mode]=dict(summary=n.w.summary(prob,np.zeros(226)),probabilities=prob.tolist())
    rev=n.score(net,torch.from_numpy(np.concatenate([tx[:,3:],tx[:,:3]],axis=1)))
    result['reversal']={k:n.w.summary(rev[v],ty[v]) for k,v in allgroups.items()}
    h.write(out/'result.json',result,sealed=True)
    h.require(sum(v.stat().st_size for v in out.iterdir())<2*1024**3,'output_cap')
    h.write(out/'completion.json',dict(status='completed',result=h.ref(out/'result.json')))
    print({k:v for k,v in result.items() if k in ('groups','fitGatePassed','seconds')})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unweighted-control',action='store_true');run(p.parse_args().unweighted_control)
