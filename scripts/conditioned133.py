"""One train-only scaled DTM032 comparison, with retained cases excluded from fit."""
import hashlib
import os
import time
import numpy as np
from PIL import Image
import dual130 as d
import diagnose131 as audit
import shared_transfer as transfer
from diagnose_signal95 import encoded
from verify_transition_shadow106 import decision
a=d.a;h=d.h


def scale_for(z):
    h.require(z.ndim==2 and z.shape[1]==1153 and len(z)>0 and np.isfinite(z).all(),'scale_inputs')
    return np.maximum(z[:,1:].astype(np.float64).std(axis=0),.001).astype(np.float32)


def scaled(z,scale):
    h.require(z.ndim==2 and z.shape[1]==1153 and scale.shape==(1152,) and
              np.isfinite(z).all() and np.isfinite(scale).all() and (scale>=.001).all(),'scale_contract')
    out=z.copy();out[:,1:]/=scale;return out


def peer_inputs():
    result=[]
    for name in ('survey26','navbar29'):
        root=h.ROOT/f'reports/work/RETAINED-FEEDBACK-132/artifacts/{name}/{name}-handoff'
        manifest=transfer.document(root/'manifest.json')
        for row in manifest['files']:transfer.verified(transfer.path_under(root,row['path']),row)
        request=transfer.document(root/'transition/request.template.json')
        prior=transfer.document(root/'transition/result.json')['results']
        comparison=transfer.document(root/'transition_dtm030/result.json')['results']
        bindings=transfer.document(root/'transition/bindings-private.json')
        h.require(len(request['pairs'])==len(prior)==len(comparison)==len(bindings),'peer_membership')
        for pair,p,q,b in zip(request['pairs'],prior,comparison,bindings):
            h.require(pair['id']==p['id']==q['id']==b['id'],'peer_order')
            ims=[]
            for side in ('before','after'):
                ref=pair[side];h.require(ref['path']==f"$ROOT/originals/{ref['sha256']}.png",'peer_path')
                with Image.open(root/'originals'/f"{ref['sha256']}.png") as im:ims.append(im.convert('RGB'))
            x,transform=encoded(*ims,size=(192,128));mask=np.zeros_like(x,dtype=bool)
            h.require(ims[0].size==ims[1].size,'peer_geometry')
            sx,sy,px,py=transform;w,ht=ims[0].size;mask[:,py:py+round(ht*sy),px:px+round(w*sx)]=True
            digest=hashlib.sha256(x.tobytes()).hexdigest();h.require(digest==p['encodedSHA256']==q['encodedSHA256'],'peer_encoding')
            result.append((x,mask,dict(id=pair['id'],encodedSHA256=digest,manifest=h.ref(root/'manifest.json'),
                dtm025=p['decision'],dtm030=q['decision'],nativeHint=b['native_focus_changed'])))
    return result


def run():
    start=time.monotonic();p=audit.sealed(d.READY/'protocol.json')
    for key in ('source','trainer','normalizer','model'):h.checked(h.ROOT,p[key])
    h.require(p['configuration']==d.CONFIG,'configuration')
    h.require('Run DTM033 — CONDITIONED-133' in (h.ROOT/'Research/ExperimentLog.md').read_text(),'unlogged')
    cache={k:np.load(h.checked(h.ROOT,v),allow_pickle=False) for k,v in p['featureCache'].items()}
    labels=np.asarray(p['labels'],dtype=np.float32)
    z=np.concatenate([cache['original'][:207],cache['contrast_0'],cache['contrast_1'],cache['original'][207:]])
    y=np.concatenate([labels[:207],labels,labels,labels[207:]])
    h.require(z.shape==(1299,1153) and (z[-226:,1:]==0).all(),'membership')
    scale=scale_for(z);train=scaled(z,scale)
    peer=peer_inputs() # Validate available diagnostic inputs before fitting; never used in scale/loss.
    out=a.r.d.old.fresh_run('conditioned133-dtm033');out.mkdir(parents=True)
    torch=a.r.d.torch_runtime();torch.set_num_threads(2)
    config=dict(d.CONFIG,initializer='DTM031-scaled-dual',featureScale='training-population-std-floor-0.001-no-center')
    h.write(out/'execution.json',dict(experiment='DTM033',pid=os.getpid(),configuration=config,source=h.ref(__file__),
        parent=h.ref(d.READY/'protocol.json'),trainer=h.ref(a.r.d.__file__),scaleSHA256=hashlib.sha256(scale.tobytes()).hexdigest(),
        authority='Standing local training; assigned CONDITIONED133',status='started',peerTraining=False),sealed=True)
    tick=time.monotonic();net,history=a.r.d.fit_change_features(d.model(),torch.from_numpy(train),torch.from_numpy(y),config);fit=time.monotonic()-tick
    torch.save(dict(version='scaled-dual-v1',state=net.state_dict(),scale=torch.from_numpy(scale),configuration=config,baseline=p['model']),out/'last.pt')
    saved=torch.load(out/'last.pt',weights_only=True,map_location='cpu');replay=d.model();replay.load_state_dict(saved['state'])
    h.require(np.array_equal(saved['scale'].numpy(),scale),'scale_roundtrip');records={}
    reference=d.probabilities(torch.from_numpy(cache['original'][:,0]))
    with torch.inference_mode():
        for name,f in cache.items():
            tx=torch.from_numpy(scaled(f,scale));after=d.probabilities(net.change(tx))
            h.require(np.array_equal(after,d.probabilities(replay.change(tx))),'checkpoint_replay')
            records[name]=dict(summary=d.q.summarize(after,labels,p['groups'],d.probabilities(torch.from_numpy(f[:,0]))),probabilities=after.tolist())
    h.require(np.array_equal(np.asarray(records['original']['probabilities'],dtype=np.float32)[207:],reference[207:]),'identity_changed')
    base=a.r.model(a.r.d.model(a.r.d.PAIRED_TEMPORAL_CONFIG));base.load_state_dict(torch.load(h.checked(h.ROOT,p['model']),weights_only=True,map_location='cpu')['state']);base.eval()
    cases=[]
    for x,mask,row in peer:
        f=d.features(base,x[None],mask[None])
        with torch.inference_mode():
            baseline=float(torch.from_numpy(f[:,0].copy()).sigmoid()[0]);after=float(net.change(torch.from_numpy(scaled(f,scale))).sigmoid()[0,0])
        cases.append(dict(row,dtm031=decision(baseline),dtm033=decision(after),dtm031Probability=baseline,dtm033Probability=after))
    retained=all(r['correct']==r['count'] for r in records['original']['summary'].values())
    h.write(out/'result.json',dict(experiment='DTM033',model=h.ref(out/'last.pt'),execution=h.ref(out/'execution.json'),
        history=history,records=records,retainedCases=cases,retentionPassed=retained,fitSeconds=fit,totalSeconds=time.monotonic()-start,
        independentEvaluation=False,productionEligible=False),sealed=True)
    h.require(sum(v.stat().st_size for v in out.iterdir())<2*1024**3,'output_budget')
    print('retention',retained,'fitSeconds',fit)
    print({k:{g:r['correct'] for g,r in v['summary'].items()} for k,v in records.items()})
    print([(r['id'].split(':')[-2:],r['dtm025'],r['dtm030'],r['dtm031'],r['dtm033']) for r in cases])


if __name__=='__main__':run()
