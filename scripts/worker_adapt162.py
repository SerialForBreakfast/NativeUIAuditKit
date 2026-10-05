"""Fixed three-way local adaptation of independently checked worker candidates."""
import hashlib
import os
import time
import numpy as np
import native_adapt152 as n
import worker_eval161 as e
from diagnose_reflow115 import decisions
h=n.h


def run(linear_only=False):
    config=dict(n.CONFIG,linearOnly=True) if linear_only else n.CONFIG
    packet='frozen164' if linear_only else 'worker162'
    assignments=[('DTM050','DTM058'),('DTM051','DTM059')] if linear_only else [('DTM050','DTM055'),('DTM051','DTM056'),('DTM052','DTM057')]
    torch=n.d.torch_runtime();torch.set_num_threads(2)
    x,y,mask,groups,px,peer_rows,ids,ny,tx,ty=n.inputs()
    prior=h.read(e.BASE/'evaluation.json');h.require(prior['seal']==h.digest({k:v for k,v in prior.items() if k!='seal'}),'evaluation_seal')
    records={};started=time.monotonic()
    for parent,experiment in assignments:
        h.require(experiment in (h.ROOT/'Research/ExperimentLog.md').read_text(),'unregistered')
        reference=prior['results'][parent]['checkpoint'];checkpoint=h.checked(h.ROOT,reference)
        saved=torch.load(checkpoint,weights_only=True,map_location='cpu')
        net=e.checked(torch,n.make_model(torch,paired_context=True),saved,parent)
        p=n.score(net,torch.from_numpy(x));h.require(np.array_equal(p,np.asarray(prior['results'][parent]['probabilities'],np.float32)),'parent_replay')
        out=h.ROOT/'NativeUITrainer/focus_ring_runs'/(packet+'-'+experiment.lower());out.mkdir()
        h.write(out/'protocol.json',dict(experiment=experiment,initializer=reference,configuration=config,
            trainingSHA256=hashlib.sha256(tx.tobytes()).hexdigest(),labelsSHA256=hashlib.sha256(ty.tobytes()).hexdigest(),
            source=h.ref(__file__),trainer=h.ref(n.__file__),evaluation=h.ref(e.BASE/'evaluation.json'),
            authority='Standing training; fixed '+packet+' comparison;2GiB total,no-wall-cap override',
            independentEvaluation=False),sealed=True)
        h.write(out/'execution.json',dict(pid=os.getpid(),status='started'))
        tick=time.monotonic()
        net,history=n.fit(net,torch.from_numpy(tx),torch.from_numpy(ty),config,
            lambda row:print(experiment,row,flush=True))
        torch.save(dict(version=packet+'-v1',state=net.state_dict(),configuration=config,initializer=reference),out/'last.pt')
        replay=n.make_model(torch,paired_context=True)
        replay.load_state_dict(torch.load(out/'last.pt',weights_only=True,map_location='cpu')['state']);replay.eval()
        p=n.score(net,torch.from_numpy(x));native=n.score(net,torch.from_numpy(px));full=n.score(net,torch.from_numpy(tx))
        h.require(np.array_equal(full,n.score(replay,torch.from_numpy(tx))),'checkpoint_replay')
        reverse=n.score(net,torch.from_numpy(np.concatenate([tx[:,3:],tx[:,:3]],axis=1)))
        stress={}
        for mode in ('global8','left8','center8'):
            prob=n.score(net,torch.from_numpy(n.nuisance.localized(x[207:],mask[207:],mode)))
            stress[mode]=dict(summary=n.w.summary(prob,np.zeros(226)),probabilities=prob.tolist())
        result=dict(experiment=experiment,initializer=parent,model=h.ref(out/'last.pt'),history=history,
            groups={k:n.w.summary(p[v],y[v]) for k,v in groups.items()},native=n.w.summary(native[ids],ny),
            probabilities=p.tolist(),nativeCases=[dict(r,probability=float(v),scored=i in ids) for i,(r,v) in enumerate(zip(peer_rows,native))],
            fullTraining=n.w.summary(full,ty),fullReversal=n.w.summary(reverse,ty),stress=stress,
            seconds=time.monotonic()-tick,independentEvaluation=False,productionEligible=False)
        h.write(out/'result.json',result,sealed=True);h.write(out/'completion.json',dict(status='completed',result=h.ref(out/'result.json')))
        records[experiment]=h.ref(out/'result.json')
        h.require(sum(p.stat().st_size for r in records.values() for p in (h.ROOT/r['path']).parent.iterdir())<2*1024**3,'output_budget')
        print(experiment,'completed',result['fullTraining'],{k:v['summary'] for k,v in stress.items()},flush=True)
    dest=h.ROOT/('reports/work/FROZEN-ADAPT-164/artifacts' if linear_only else 'reports/work/WORKER-ADAPT-162/artifacts');dest.mkdir(parents=True)
    h.write(dest/'result.json',dict(results=records,seconds=time.monotonic()-started),sealed=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--linear-only',action='store_true')
    run(parser.parse_args().linear_only)
