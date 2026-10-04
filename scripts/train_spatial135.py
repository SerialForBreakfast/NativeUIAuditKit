"""Single equal-capacity raw/raw versus local/global frozen-feature comparison."""
import argparse
import hashlib
import os
from pathlib import Path
import time
import numpy as np
import spatial135 as s
import retention134 as retention

c, d, h = s.c, s.d, s.h


def pair_masks(x, frames):
    by = {}
    for frame in frames.values():
        key = frame['encodedSHA256']
        mask = s.proposal_mask(frame['candidates'], frame['size'])
        h.require(key not in by or np.array_equal(by[key], mask), 'ambiguous_encoded_proposals')
        by[key] = mask
    result = []
    for pair in x:
        keys = [hashlib.sha256(v.tobytes()).hexdigest() for v in (pair[:3], pair[3:])]
        h.require(all(key in by for key in keys), 'missing_proposal_frame')
        result.append(by[keys[0]] | by[keys[1]])
    return np.stack(result)


def features(net, x, mask):
    torch = d.a.r.d.torch_runtime()
    h.require(x.ndim == 4 and x.shape[1:] == (6,128,192) and
              mask.shape == (len(x),128,192) and mask.dtype == bool and
              np.isfinite(x).all() and ((x>=0)&(x<=1)).all(), 'spatial_feature_inputs')
    raw, local = [], []
    with torch.inference_mode():
        for at in range(0, len(x), 16):
            tx = torch.from_numpy(x[at:at+16])
            a, b = tx[:,:3], tx[:,3:]
            diff = (b-a).abs()
            aa = net.encoder(torch.cat([torch.zeros_like(a),a,a],1))
            bb = net.encoder(torch.cat([torch.zeros_like(b),b,b],1))
            center = (aa+bb)/2
            phi = net.encoder(torch.cat([diff,a,b],1))
            residual = phi-center
            base = net.change(torch.cat([net.base_readout(phi),residual],1))
            keep = torch.from_numpy(mask[at:at+16])[:,None]
            inside = net.encoder(torch.cat([diff*keep,a,b],1))-center
            outside = net.encoder(torch.cat([diff*~keep,a,b],1))-center
            raw.append(torch.cat([base,residual,residual],1).numpy())
            local.append(torch.cat([base,inside,outside],1).numpy())
    result = dict(raw=np.concatenate(raw), spatial=np.concatenate(local))
    identical = np.all(x[:,:3] == x[:,3:], axis=(1,2,3))
    h.require(all(np.isfinite(z).all() and (z[identical,1:]==0).all() for z in result.values()), 'spatial_identity')
    return result


def prepare(output):
    started = time.monotonic()
    out = h.fresh(output)
    audit_path = h.ROOT/'reports/work/SPATIAL-135/artifacts/audit/report.json'
    audit = c.audit.sealed(audit_path)
    proposal = c.audit.sealed(h.checked(h.ROOT,audit['proposals']))
    for ref in (audit['source'], audit['scorer'], proposal['source'], proposal['retainedSource']):
        h.checked(h.ROOT,ref)
    x,y,content,net,_,groups,_ = d.c.setup()
    h.require(hashlib.sha256(x.tobytes()).hexdigest()==audit['tensorSHA256'] and
              groups==audit['groups'] and np.array_equal(y,audit['labels']), 'spatial_membership')
    net.load_state_dict(d.a.r.d.torch_runtime().load(h.checked(h.ROOT,audit['model']), weights_only=True,map_location='cpu')['state'])
    net.eval()
    masks = pair_masks(x,proposal['frames'])
    h.require([r['maskPixels'] for r in s.support(x,masks)] == [r['maskPixels'] for r in audit['support']], 'mask_replay')
    peer = c.peer_inputs()
    peer_x = np.stack([r[0] for r in peer])
    peer_masks = pair_masks(peer_x,proposal['frames'])
    out.mkdir(parents=True)
    cache = {}
    for name in ('original','contrast_0','contrast_1','global8','left8','center8','peer'):
        if name=='original':v=x
        elif name.startswith('contrast_'):v=d.s.intensity(x,content,.8,.1,int(name[-1]))
        elif name=='peer':v=peer_x
        else:v=retention.localized(x,content,name)
        f = features(net,v,peer_masks if name=='peer' else masks)
        cache[name] = {}
        for arm,z in f.items():
            np.save(out/f'{name}-{arm}.npy',z,allow_pickle=False)
            cache[name][arm] = h.ref(out/f'{name}-{arm}.npy')
        if name=='original':
            torch=d.a.r.d.torch_runtime()
            probs=d.probabilities(torch.from_numpy(f['raw'][:,0]))
            h.require(np.allclose(probs,audit['probabilities']['baseline'],atol=1e-6,rtol=0) and
                      np.array_equal(d.q.decisions(probs),d.q.decisions(np.asarray(audit['probabilities']['baseline']))), 'spatial_baseline')
        print('prepared',name,flush=True)
    h.write(out/'protocol.json',dict(version='spatial135-feature-comparison-v1',source=h.ref(__file__),
        trainer=h.ref(d.a.r.d.__file__),constraint=h.ref(retention.__file__),scaler=h.ref(c.__file__),
        audit=h.ref(audit_path),model=audit['model'],cache=cache,labels=y.tolist(),groups=groups,
        peer=[row[2] for row in peer],configuration=d.CONFIG,seconds=time.monotonic()-started,
        fixedSourceProposals=True,peerTraining=False,independentEvaluation=False),sealed=True)


def train(ready, output):
    started=time.monotonic()
    out=h.fresh(output)
    p=c.audit.sealed(ready/'protocol.json')
    for key in ('source','trainer','constraint','scaler','model'):h.checked(h.ROOT,p[key])
    h.require(p['configuration']==d.CONFIG and 'Runs DTM035 / DTM036 — SPATIAL-135' in
              (h.ROOT/'Research/ExperimentLog.md').read_text(),'comparison_protocol')
    cache={name:{arm:np.load(h.checked(h.ROOT,ref),allow_pickle=False) for arm,ref in arms.items()}
           for name,arms in p['cache'].items()}
    labels=np.asarray(p['labels'],dtype=np.float32)
    y=np.concatenate([labels[:207],labels,labels,labels[207:]])
    torch=d.a.r.d.torch_runtime();torch.set_num_threads(2)
    results={}
    # Both arms fixed before either run; no selection based on the first result.
    for arm,experiment in [('raw','DTM035'),('spatial','DTM036')]:
        run_dir=d.a.r.d.old.fresh_run(f'spatial135-{experiment.lower()}')
        z=np.concatenate([cache['original'][arm][:207],cache['contrast_0'][arm],
                          cache['contrast_1'][arm],cache['original'][arm][207:]])
        h.require(z.shape==(1299,1153),'comparison_membership')
        scale=c.scale_for(z);z=c.scaled(z,scale)
        net=retention.constrained_model(z[:207],y[:207])
        config=dict(d.CONFIG,initializer=f'DTM031-{arm}-dual',constraintFloor=retention.FLOOR,
                    constraintInterior=.999,representation=arm)
        run_dir.mkdir(parents=True)
        h.write(run_dir/'execution.json',dict(experiment=experiment,pid=os.getpid(),
            protocol=h.ref(ready/'protocol.json'),configuration=config,
            authority='Standing training; assigned SPATIAL135 matched comparison',status='started'),sealed=True)
        tick=time.monotonic()
        net,history=d.a.r.d.fit_change_features(net,torch.from_numpy(z),torch.from_numpy(y),config)
        fit=time.monotonic()-tick
        with torch.no_grad():weight,radius=net.change.effective();weight=weight.detach().clone()
        torch.save(dict(version='spatial135-dual-v1',weights=weight,rawState=net.state_dict(),
                        scale=torch.from_numpy(scale),configuration=config,baseline=p['model']),run_dir/'last.pt')
        saved=torch.load(run_dir/'last.pt',weights_only=True,map_location='cpu')
        replay=d.model();replay.change.linear.weight.data.copy_(saved['weights'])
        h.require(np.array_equal(saved['scale'].numpy(),scale),'spatial_scale_replay')
        records={}
        with torch.inference_mode():
            for name,arms in cache.items():
                f=arms[arm];tx=torch.from_numpy(c.scaled(f,scale))
                logits=replay.change(tx)
                if name=='peer':
                    probs=logits.sigmoid().flatten().numpy()
                    again=net.change(tx).sigmoid().flatten().numpy()
                    records[name]=[dict(row,decision=c.decision(float(v)),probability=float(v))
                                   for row,v in zip(p['peer'],probs)]
                else:
                    probs=d.probabilities(logits);again=d.probabilities(net.change(tx))
                    records[name]=dict(summary=d.q.summarize(probs,labels,p['groups'],d.probabilities(torch.from_numpy(f[:,0]))),
                                       probabilities=probs.tolist())
                h.require(np.array_equal(probs,again),'spatial_materialized_replay')
        reference=d.probabilities(torch.from_numpy(cache['original'][arm][:,0]))
        h.require(np.array_equal(np.asarray(records['original']['probabilities'],dtype=np.float32)[207:],reference[207:]),'identity_changed')
        passed=all(r['correct']==r['count'] for r in records['original']['summary'].values())
        h.require(passed,'original_retention_failed')
        report=dict(experiment=experiment,model=h.ref(run_dir/'last.pt'),execution=h.ref(run_dir/'execution.json'),
            history=history,records=records,fitSeconds=fit,radius=float(radius),retentionPassed=passed,
            productionEligible=False,independentEvaluation=False)
        h.write(run_dir/'result.json',report,sealed=True);results[experiment]=h.ref(run_dir/'result.json')
        print(experiment, 'fitSeconds',fit,{k:{g:r['correct'] for g,r in v['summary'].items()}
              for k,v in records.items() if k!='peer'},flush=True)
    out.mkdir(parents=True)
    h.write(out/'report.json',dict(version='spatial135-comparison-v1',protocol=h.ref(ready/'protocol.json'),
        results=results,seconds=time.monotonic()-started,trainingRolesUnchanged=True,
        productionEligible=False,independentEvaluation=False),sealed=True)
    roots=[ready,out]+[h.ROOT/f'NativeUITrainer/focus_ring_runs/spatial135-dtm0{i}' for i in (35,36)]
    h.require(sum(v.stat().st_size for root in roots for v in root.rglob('*') if v.is_file())<2*1024**3,'output_budget')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=['prepare','train'])
    parser.add_argument('--ready',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.mode=='prepare':prepare(args.ready)
    else:
        parser.error('--output required') if args.output is None else train(args.ready,args.output)
