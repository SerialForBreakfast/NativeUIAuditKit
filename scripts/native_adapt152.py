"""Two fixed matched native adaptations of the existing paired-image CNN branch."""
import argparse
import hashlib
import os
from pathlib import Path
import time
import numpy as np
import worker_candidate151 as w
import content127 as content
import conditioned133 as peer
import adapt_retained137 as admission
import retention134 as nuisance
import focus_direct_transition as d
import focus_change_adaptation as scorer
from focus_temporal_transition import make_model

h=content.h
CONFIG=dict(epochs=120,lr=.0001,batch=16,seed=42,threads=2,inputSize=[192,128],selection='fixed-last')


def project_conflicting_gradients(first,second):
    """Remove opposing components using both original gradient vectors."""
    torch=d.torch_runtime()
    h.require(first.shape==second.shape and first.ndim==1
              and torch.isfinite(first).all() and torch.isfinite(second).all(),'projection_inputs')
    # Use double precision for dot products and zero-norm checks.
    a,b=first.double(),second.double()
    dot=torch.dot(a,b); aa=torch.dot(a,a); bb=torch.dot(b,b)
    if dot>=0 or aa==0 or bb==0:
        return first,second,False
    return (a-dot/bb*b).to(first.dtype),(b-dot/aa*a).to(second.dtype),True


def fit(net,x,y,config,progress=None,weights=None,conflict_groups=None,alternate_inputs=None):
    torch=d.torch_runtime();torch.set_num_threads(config['threads']);torch.manual_seed(config['seed'])
    h.require(x.ndim==4 and x.shape[1:]==(6,128,192) and y.shape==(len(x),) and len(x)>0
              and torch.isfinite(y).all() and ((y==0)|(y==1)).all(),'training_inputs')
    # Bound validation masks without changing sample order or optimization.
    for part in x.split(8):
        h.require(torch.isfinite(part).all() and ((part>=0)&(part<=1)).all(),'training_inputs')
    if alternate_inputs is not None:
        h.require(alternate_inputs.shape==x.shape and alternate_inputs.dtype==x.dtype,
                  'alternate_inputs')
        for part in alternate_inputs.split(8):
            h.require(torch.isfinite(part).all() and ((part>=0)&(part<=1)).all(),'alternate_inputs')
    h.require(type(config['epochs']) is int and config['epochs']>0 and type(config['batch']) is int
              and config['batch']>0 and np.isfinite(config['lr']) and config['lr']>0,'training_config')
    if weights is not None:
        h.require(weights.shape==y.shape and torch.isfinite(weights).all().item()
                  and (weights>0).all().item(),'training_weights')
    if conflict_groups is not None:
        h.require(conflict_groups.shape==y.shape and conflict_groups.dtype==torch.int64
                  and ((conflict_groups>=-1)&(conflict_groups<=1)).all(),'conflict_groups')
        h.require(((conflict_groups!=0)|(y==0)).all()
                  and ((conflict_groups!=1)|(y==1)).all(),'conflict_labels')
    linear_only=config.get('linearOnly',False)
    h.require(type(linear_only) is bool,'training_scope')
    if linear_only:
        h.require(isinstance(net.change,torch.nn.Sequential) and len(net.change)==11 and
            isinstance(net.change[8],torch.nn.Linear) and isinstance(net.change[10],torch.nn.Linear),'linear_scope_architecture')
    trainable=set()
    for name,p in net.named_parameters():
        active=name.startswith(('change.8.','change.10.')) if linear_only else name.startswith('change.')
        p.requires_grad_(active)
        if active:trainable.add(name)
    h.require(bool(trainable),'empty_trainable_scope')
    frozen={k:v.clone() for k,v in net.state_dict().items() if k not in trainable}
    optimizer=torch.optim.Adam([p for p in net.parameters() if p.requires_grad],lr=config['lr'])
    generator=torch.Generator().manual_seed(config['seed']);history=[];started=time.monotonic();net.train()
    for epoch in range(config['epochs']):
        # Keep labels, row order, weights, and update counts unchanged.
        epoch_inputs=alternate_inputs if alternate_inputs is not None and epoch%2 else x
        total=0.; paired_batches=0; projected_batches=0
        for ids in torch.randperm(len(x),generator=generator).split(config['batch']):
            optimizer.zero_grad(set_to_none=True)
            logits=net.change(net.change_inputs(epoch_inputs[ids])).flatten()
            loss=torch.nn.functional.binary_cross_entropy_with_logits(logits,y[ids],
                weight=None if weights is None else weights[ids])
            h.require(torch.isfinite(loss).item(),'nonfinite_loss')
            groups=None if conflict_groups is None else conflict_groups[ids]
            if groups is not None and (groups==0).any() and (groups==1).any():
                paired_batches+=1
                parameters=[p for p in net.change.parameters() if p.requires_grad]
                elements=torch.nn.functional.binary_cross_entropy_with_logits(logits,y[ids],
                    weight=None if weights is None else weights[ids],reduction='none')
                gradients=[]
                for group in (0,1):
                    contribution=elements[groups==group].sum()/len(ids)
                    parts=torch.autograd.grad(contribution,parameters,retain_graph=True)
                    gradients.append(torch.cat([p.flatten() for p in parts]))
                a,b,projected=project_conflicting_gradients(*gradients)
                loss.backward()
                if projected:
                    projected_batches+=1
                    correction=(a-gradients[0])+(b-gradients[1]); offset=0
                    for p in parameters:
                        p.grad.add_(correction[offset:offset+p.numel()].reshape_as(p))
                        offset+=p.numel()
            else:
                loss.backward()
            h.require(all(p.grad is None or torch.isfinite(p.grad).all().item() for p in net.change.parameters()),'nonfinite_gradient')
            optimizer.step();total+=float(loss.detach())*len(ids)
        h.require(all(torch.isfinite(p).all().item() for p in net.parameters()),'nonfinite_weight')
        row=dict(epoch=epoch+1,loss=total/len(x),seconds=time.monotonic()-started);history.append(row)
        if conflict_groups is not None:
            row.update(pairedBatches=paired_batches,projectedBatches=projected_batches)
        if progress is not None and (epoch==0 or (epoch+1)%10==0):progress(row)
    h.require(all(torch.equal(v,net.state_dict()[k]) for k,v in frozen.items()),'geometry_changed')
    return net.eval(),history


def score(net,x):
    torch=d.torch_runtime()
    with torch.inference_mode():
        return torch.cat([scorer.score_change(net,v,CONFIG) for v in x.split(8)]).numpy()


def inputs():
    x,y,mask,_,_,groups,_=content.setup()
    cases=peer.peer_inputs();px=np.stack([v[0] for v in cases]);rows=[v[2] for v in cases]
    h.require(hashlib.sha256(admission.ADMISSION.read_bytes()).hexdigest()==admission.ADMISSION_SHA,'native_admission')
    _,_,families=admission.reviewed_indices(h.read(admission.ADMISSION),rows)
    ids=sum(families.values(),[]);ny=np.asarray([int(rows[i]['nativeHint']) for i in ids],np.float32)
    role=h.read(h.ROOT/'reports/work/GLOBAL-REPLAY-146/admission.json')
    h.require(role['version']=='global146-admission-v1' and role['role']=='train' and role['cache']=='global8'
              and role['count']==226 and role['changed'] is False and role['external_transfer'] is False
              and role['source_tensor_sha256']==hashlib.sha256(x.tobytes()).hexdigest()
              and np.array_equal(x[207:,:3],x[207:,3:]) and (y[207:]==0).all(),'global_admission')
    global_x=nuisance.localized(x[207:],mask[207:],'global8')
    train_x=np.concatenate([x,px[ids],global_x]);train_y=np.concatenate([y,ny,np.zeros(226,np.float32)])
    h.require(train_x.shape==(668,6,128,192) and len(ids)==9,'membership')
    return x,y,mask,groups,px,rows,ids,ny,train_x,train_y


def run():
    torch=d.torch_runtime();torch.set_num_threads(2);started=time.monotonic()
    x,y,mask,groups,px,rows,ids,ny,tx,ty=inputs()
    baseline=h.read(w.BASE/'evaluation.json');peer_result=w.t.document(w.BASE/'peer-result.json')
    h.require(baseline['encodedInputSHA256']==hashlib.sha256(x.tobytes()).hexdigest(),'evaluation_inputs')
    frozen_manifest=w.t.document(w.BASE/'extracted/manifest.json')
    for ref in frozen_manifest['files']:w.t.verified(w.BASE/'extracted'/ref['path'],ref)
    for name in ('focus_temporal_transition.py','focus_spatial_transition.py'):
        h.require((w.BASE/'extracted/source'/name).read_bytes()==(h.ROOT/'scripts'/name).read_bytes(),'model_source')
    report=h.fresh(h.ROOT/'reports/work/NATIVE-ADAPT-152/artifacts/result.json')
    report.parent.mkdir(parents=True,exist_ok=True)
    tensor=torch.from_numpy(tx);labels=torch.from_numpy(ty);results={}
    for source,experiment in [('DTM044','DTM048'),('DTM045','DTM049')]:
        h.require(experiment in (h.ROOT/'Research/ExperimentLog.md').read_text(),'unregistered')
        out=d.old.fresh_run('native152-'+experiment.lower());out.mkdir(parents=True)
        path=w.BASE/'extracted'/source.lower()/'last.pt';expected=peer_result['runs'][source]
        w.t.verified(path,expected['checkpoint'])
        saved=torch.load(path,weights_only=True,map_location='cpu')
        net=w.checked_state(torch,make_model(torch,paired_context=True),saved,source,expected)
        old=score(net,torch.from_numpy(x))
        h.require(np.array_equal(old,np.asarray(baseline['models'][source]['originalProbabilities'],np.float32)),'initializer_replay')
        protocol=dict(experiment=experiment,initializer=h.ref(path),source=h.ref(__file__),trainerModel=h.ref(h.ROOT/'scripts/focus_temporal_transition.py'),
            configuration=CONFIG,trainingSHA256=hashlib.sha256(tx.tobytes()).hexdigest(),labelsSHA256=hashlib.sha256(ty.tobytes()).hexdigest(),
            nativeAdmission=h.ref(admission.ADMISSION),globalAdmission=h.ref(h.ROOT/'reports/work/GLOBAL-REPLAY-146/admission.json'),
            membership=dict(original=433,native=9,globalNegative=226),nativeIDs=[rows[i]['id'] for i in ids],
            authority='Standing local training; matched152two-run assignment; no-wall-time-limit override;2GiB output cap',independentEvaluation=False)
        h.write(out/'protocol.json',protocol,sealed=True)
        h.write(out/'execution.json',dict(pid=os.getpid(),status='started',protocol=h.ref(out/'protocol.json')),sealed=True)
        def progress(row):
            h.write(out/f"epoch-{row['epoch']:04d}.json",row)
            print(experiment,row,flush=True)
        net,history=fit(net,tensor,labels,CONFIG,progress)
        torch.save(dict(version='native152-v1',state=net.state_dict(),configuration=CONFIG,protocol=h.ref(out/'protocol.json')),out/'last.pt')
        replay=make_model(torch,paired_context=True)
        replay.load_state_dict(torch.load(out/'last.pt',weights_only=True,map_location='cpu')['state']);replay.eval()
        p=score(net,torch.from_numpy(x));native=score(net,torch.from_numpy(px))
        h.require(np.array_equal(p,score(replay,torch.from_numpy(x))) and np.array_equal(native,score(replay,torch.from_numpy(px))),'checkpoint_replay')
        stress={}
        for mode in ('global8','left8','center8'):
            prob=score(net,torch.from_numpy(nuisance.localized(x[207:],mask[207:],mode)))
            stress[mode]=dict(summary=w.summary(prob,np.zeros(226)),probabilities=prob.tolist())
        reverse=score(net,torch.from_numpy(np.concatenate([x[:,3:],x[:,:3]],axis=1)))
        summaries={k:w.summary(p[v],y[v]) for k,v in groups.items()}
        native_summary=w.summary(native[ids],ny)
        result=dict(experiment=experiment,initializer=source,model=h.ref(out/'last.pt'),history=history,
            groups=summaries,native=native_summary,probabilities=p.tolist(),
            nativeCases=[dict(row,probability=float(prob),scored=i in ids) for i,(row,prob) in enumerate(zip(rows,native))],
            stress=stress,reversal={k:w.summary(reverse[v],y[v]) for k,v in groups.items()},checkpointReplay=True,
            fitGatePassed=all(v['correct']==v['count'] for v in [*summaries.values(),native_summary,stress['global8']['summary']]),
            independentEvaluation=False,productionEligible=False)
        h.write(out/'result.json',result,sealed=True)
        h.require(sum(p.stat().st_size for p in out.iterdir())<1024**3,'output_budget')
        h.write(out/'completion.json',dict(status='completed',result=h.ref(out/'result.json')),sealed=True)
        results[experiment]=dict(result=h.ref(out/'result.json'),groups=summaries,native=native_summary,fitGatePassed=result['fitGatePassed'])
        print(experiment,results[experiment],flush=True)
    h.write(report,dict(models=results,seconds=time.monotonic()-started),sealed=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true',required=True);p.parse_args();run()
