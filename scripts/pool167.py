"""One preregistered change-pooling comparison; all production models unchanged."""
import hashlib
import os
import time
import numpy as np
import native_adapt152 as n
import replay_spatial163 as spatial
from diagnose_reflow115 import decisions
h=n.h
BASE=h.ROOT/'NativeUITrainer/focus_ring_runs/pool167-dtm060'


def pooled(net,torch):
    h.require(isinstance(net.change[6],torch.nn.AdaptiveAvgPool2d),'pool_architecture')
    class BroadcastMean(torch.nn.Module):
        def forward(self,x):return x.mean(dim=(-2,-1),keepdim=True).expand(-1,-1,4,6)
    net.change[6]=BroadcastMean();return net


def load(torch,saved):
    h.require(saved.get('version')=='pool167-v1' and saved.get('pooling')=='global-broadcast-4x6','checkpoint_architecture')
    net=pooled(n.make_model(torch,paired_context=True),torch);net.load_state_dict(saved['state']);return net.eval()


def public_inputs(torch):
    v=spatial.v;export=v.w.BASE.parent/'export01/payload';maskroot=v.BASE.parent/'export01/payload'
    for root in (export,maskroot):
        for ref in v.w.t.document(root/'manifest.json')['files']:v.w.t.verified(root/ref['path'],ref)
    old=torch.load(export/'training.pt',weights_only=True,map_location='cpu');m=torch.load(maskroot/'masks.pt',weights_only=True,map_location='cpu')['contentMask']
    endpoints={}
    for row,mask in zip(old['images'],m):
        for offset in (0,3):endpoints.setdefault(v.digest(row[offset:offset+3]),(row[offset:offset+3],mask[offset:offset+3]))
    pins=h.read(spatial.BASE/'extracted/evidence/attempt01/manifest.json',1024**2)
    h.require(list(endpoints)==pins['endpointOrder'],'endpoint_identity')
    controls=torch.stack([torch.cat((im,im)) for im,_ in endpoints.values()]);masks=[mask for _,mask in endpoints.values()]
    return controls,masks,pins


def run():
    torch=n.d.torch_runtime();torch.set_num_threads(2);started=time.monotonic()
    x,y,mask,groups,px,rows,ids,ny,tx,ty=n.inputs()
    control=h.ROOT/'NativeUITrainer/focus_ring_runs/residual158-dtm054'
    prior=h.read(control/'protocol.json');result=h.read(control/'result.json')
    for doc in (prior,result):h.require(doc['seal']==h.digest({k:v for k,v in doc.items() if k!='seal'}),'control_seal')
    h.require(prior['configuration']==n.CONFIG and prior['uniformControl'] and
        hashlib.sha256(tx.tobytes()).hexdigest()==prior['trainingSHA256'] and
        hashlib.sha256(ty.tobytes()).hexdigest()==prior['labelsSHA256'],'matched_control')
    initializer=h.checked(h.ROOT,prior['initializer']);saved=torch.load(initializer,weights_only=True,map_location='cpu')
    net=n.make_model(torch,paired_context=True);net.load_state_dict(saved['state']);net=pooled(net,torch)
    h.require('DTM060' in (h.ROOT/'Research/ExperimentLog.md').read_text(),'unregistered')
    BASE.mkdir();protocol=dict(experiment='DTM060',initializer=prior['initializer'],configuration=n.CONFIG,
        source=h.ref(__file__),trainer=h.ref(n.__file__),control=h.ref(control/'protocol.json'),
        trainingSHA256=prior['trainingSHA256'],labelsSHA256=prior['labelsSHA256'],pooling='global-broadcast-4x6',
        authority='Standing local training; one POOL167comparison;2GiB cap; no wall limit')
    h.write(BASE/'protocol.json',protocol,sealed=True);h.write(BASE/'execution.json',dict(pid=os.getpid(),state='started'))
    net,history=n.fit(net,torch.from_numpy(tx),torch.from_numpy(ty),n.CONFIG,lambda row:print(row,flush=True),torch.ones(len(tx)))
    torch.save(dict(version='pool167-v1',pooling='global-broadcast-4x6',state=net.state_dict(),protocol=h.ref(BASE/'protocol.json')),BASE/'last.pt')
    replay=load(torch,torch.load(BASE/'last.pt',weights_only=True,map_location='cpu'))
    p=n.score(net,torch.from_numpy(tx));h.require(np.array_equal(p,n.score(replay,torch.from_numpy(tx))),'checkpoint_replay')
    baseline=n.make_model(torch,paired_context=True)
    baseline.load_state_dict(torch.load(h.checked(h.ROOT,result['model']),weights_only=True,map_location='cpu')['state']);baseline.eval()
    h.require(np.array_equal(n.score(baseline,torch.from_numpy(tx)),np.asarray(result['probabilities'],np.float32)),'control_replay')
    controls,masks,pins=public_inputs(torch);results={}
    allgroups=dict(groups,native=list(range(433,442)),globalNegative=list(range(442,668)))
    for name,model in [('DTM054',baseline),('DTM060',net)]:
        full=n.score(model,torch.from_numpy(tx));reverse=n.score(model,torch.from_numpy(np.concatenate((tx[:,3:],tx[:,:3]),axis=1)))
        stress={};public={}
        for mode in ('global8','left8','center8'):
            q=n.score(model,torch.from_numpy(n.nuisance.localized(x[207:],mask[207:],mode)))
            stress[mode]=n.w.summary(q,np.zeros(len(q)))
        for arm in spatial.ARMS:
            selected=torch.from_numpy(np.stack([spatial.region(m.numpy(),arm) for m in masks]));values=controls.clone()
            values[:,3:]=torch.where(selected,torch.round((values[:,3:]*.8+.1).clamp(0,1)*255)/255,values[:,3:])
            h.require(spatial.v.digest(values)==pins['arms'][arm]['tensorSHA256'],'arm_identity')
            q=n.score(model,values);public[arm]=n.w.summary(q,np.zeros(len(q)))
        results[name]=dict(training=n.w.summary(full,ty),groups={k:n.w.summary(full[v],ty[v]) for k,v in allgroups.items()},
            reversal=n.w.summary(reverse,ty),stress=stress,publicDiagnostics=public,probabilities=full.tolist())
    h.write(BASE/'result.json',dict(results=results,history=history,seconds=time.monotonic()-started,
        productionEligible=False,independentEvaluation=False,model=h.ref(BASE/'last.pt'),
        diagnosticLabels='Counterfactual baseline agreement, not guaranteed focus truth'),sealed=True)
    h.require(sum(p.stat().st_size for p in BASE.iterdir())<2*1024**3,'output_budget')
    h.write(BASE/'completion.json',dict(state='completed',result=h.ref(BASE/'result.json')),sealed=True)
    print({k:{x:v[x] for x in ('training','reversal','stress')} for k,v in results.items()},flush=True)


if __name__=='__main__':run()
