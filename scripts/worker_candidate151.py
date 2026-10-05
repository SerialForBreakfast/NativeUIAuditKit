"""Bounded CUDA145 result intake; never imports or executes returned code."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import time

from focus_surface_intake import safe_members
import shared_transfer as t

BASE=t.ROOT/'reports/work/WORKER-CUDA-145/artifacts/return01'


def checked_state(torch, net, saved, run_id, expected):
    t.require(saved.get('version')=='cuda145-checkpoint-v1' and saved.get('epoch')==600 and
              saved.get('steps')==21600,'checkpoint_version_or_completion')
    config=saved['pins']['configuration']
    t.require(config==expected['configuration'] and config['run_id']==run_id and
              config['epochs']==600 and config['selection']=='fixed-last' and
              config['thresholds']==dict(changed_min=.85,unchanged_max=.15),'checkpoint_configuration')
    state=saved['model'];reference=net.state_dict()
    t.require(set(state)==set(reference),'checkpoint_keys')
    for key,value in state.items():
        t.require(isinstance(value,torch.Tensor) and value.shape==reference[key].shape and
                  value.dtype==reference[key].dtype and torch.isfinite(value).all().item(),'checkpoint_tensor')
    net.load_state_dict(state,strict=True)
    return net.eval()


def summary(probabilities, labels):
    import numpy as np
    from diagnose_reflow115 import decisions
    p=np.asarray(probabilities);y=np.asarray(labels)
    t.require(p.shape==y.shape and np.isin(y,[0,1]).all(),'score_labels')
    d=decisions(p)
    return dict(count=len(y),correct=int((d==y).sum()),falseChange=int(((d==1)&(y==0)).sum()),
                missedChange=int(((d==0)&(y==1)).sum()),abstentions=int((d==-1).sum()))


def evaluate():
    import numpy as np
    import torch
    import content127 as content
    import retention134 as nuisance
    import conditioned133 as peer
    import adapt_retained137 as admission
    from focus_temporal_transition import make_model
    output=BASE/'evaluation.json';t.require(not output.exists(),'output_collision')
    started=time.monotonic();torch.set_num_threads(2)
    root=BASE/'extracted';result=t.document(BASE/'peer-result.json')
    manifest=t.document(root/'manifest.json')
    for ref in manifest['files']:t.verified(root/ref['path'],ref)
    for name in ('focus_temporal_transition.py','focus_spatial_transition.py'):
        t.require((root/'source'/name).read_bytes()==(t.ROOT/'scripts'/name).read_bytes(),'resident_architecture_changed')
    # Established loaders reverify retained bytes, encoding and reviewed labels.
    x,y,mask,_,baseline,groups,_=content.setup()
    cases=peer.peer_inputs();px=np.stack([v[0] for v in cases]);rows=[v[2] for v in cases]
    t.require(hashlib.sha256(admission.ADMISSION.read_bytes()).hexdigest()==admission.ADMISSION_SHA,'native_admission_changed')
    _,_,families=admission.reviewed_indices(t.document(admission.ADMISSION),rows)
    native_indices=sum(families.values(),[])
    native_y=np.array([int(rows[i]['nativeHint']) for i in native_indices])
    export=BASE.parent/'export01/payload';producer=t.document(export/'manifest.json')
    for ref in producer['files']:t.verified(export/ref['path'],ref)
    training=torch.load(export/'training.pt',weights_only=True,map_location='cpu')
    endpoints={}
    for image in training['images']:
        for endpoint in (image[:3],image[3:]):
            key=hashlib.sha256(endpoint.contiguous().numpy().tobytes()).hexdigest()
            endpoints.setdefault(key,torch.cat([endpoint,endpoint]))
    controls=torch.stack(list(endpoints.values()))
    t.require(len(controls)==178,'control_membership')
    def score(net,values):
        tx=torch.from_numpy(np.ascontiguousarray(values)) if isinstance(values,np.ndarray) else values
        with torch.inference_mode():
            p=torch.cat([net.change(net.change_inputs(v)).flatten().sigmoid() for v in tx.split(8)]).numpy()
        t.require(np.isfinite(p).all(),'nonfinite_predictions')
        return p
    outcomes={}
    for run_id in ('DTM044','DTM045'):
        expected=result['runs'][run_id];checkpoint=root/run_id.lower()/'last.pt'
        t.verified(checkpoint,expected['checkpoint'])
        saved=torch.load(checkpoint,weights_only=True,map_location='cpu')
        t.require(saved['pins']['data']['manifest']['sha256']==hashlib.sha256((export/'manifest.json').read_bytes()).hexdigest() and
                  saved['pins']['data']['data']['sha256']==hashlib.sha256((export/'training.pt').read_bytes()).hexdigest(),'checkpoint_data')
        net=checked_state(torch,make_model(torch,paired_context=True),saved,run_id,expected)
        tick=time.monotonic();original=score(net,training['images']);identities=score(net,controls)
        fit=summary(original,training['labels'].numpy());ic=summary(identities,np.zeros(len(controls)))
        t.require(fit['correct']==expected['original']['confident_correct'] and
                  fit['abstentions']==expected['original']['abstentions'] and
                  ic['correct']==expected['controls']['confident_correct'],'worker_decision_replay')
        predictions=score(net,x);native=score(net,px)
        stress={}
        for mode in ('global8','left8','center8'):
            p=score(net,nuisance.localized(x[207:],mask[207:],mode))
            stress[mode]=dict(summary=summary(p,np.zeros(len(p))),probabilities=p.tolist(),
                role='exposed robustness diagnostic; localized labels not admitted for training')
        reversed_x=np.concatenate([x[:,3:],x[:,:3]],axis=1)
        reversed_p=score(net,reversed_x)
        replay=score(net,px)
        t.require(np.array_equal(native,replay),'local_repeatability')
        outcomes[run_id]=dict(checkpointSHA256=expected['checkpoint']['sha256'],training=fit,trainingIdentities=ic,
            groups={k:summary(predictions[ids],y[ids]) for k,ids in groups.items()},
            originalProbabilities=predictions.tolist(),reversalGroups={k:summary(reversed_p[ids],y[ids]) for k,ids in groups.items()},
            nativeReviewed=summary(native[native_indices],native_y),
            nativeCases=[dict(row,probability=float(p),scored=i in native_indices) for i,(row,p) in enumerate(zip(rows,native))],
            stress=stress,seconds=time.monotonic()-tick,localRepeatability=True)
        print(run_id,outcomes[run_id]['groups'],outcomes[run_id]['nativeReviewed'],flush=True)
    report=dict(version='worker-eval151-v1',models=outcomes,sourceSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        baselineDTM030={k:summary(baseline[ids],y[ids]) for k,ids in groups.items()},
        encodedInputSHA256=hashlib.sha256(x.tobytes()).hexdigest(),nativeAdmissionSHA256=admission.ADMISSION_SHA,
        seconds=time.monotonic()-started,backend='CPU float32 batch8',torch=str(torch.__version__),
        independentEvaluation=False,productionEligible=False,
        limits='Retained development cases; native data not in these worker fits but exposed to earlier model selection. Geometry branch untrained. No deployment gate passed.')
    with output.open('x') as f:json.dump(report,f,indent=2,allow_nan=False)


def extract(archive, output, expected, kind='cuda145'):
    t.require(kind in ('cuda145','robust153'),'unsupported_return_kind')
    t.require(output.resolve()==output and output.is_relative_to(t.ROOT) and not output.exists(),'output_collision_or_boundary')
    t.verified(archive,expected)
    with tarfile.open(archive) as tar:
        members,size=safe_members(tar)
        t.require(len(members)==expected['members'] and size==expected['expanded_bytes'] and
                  size<=80_000_000 and all(m.isfile() for m in members),'archive_scope')
        raw=tar.extractfile('manifest.json').read()
        t.require(len(raw)<1_000_000 and hashlib.sha256(raw).hexdigest()==expected['manifest_sha256'],'manifest_hash')
        manifest=json.loads(raw)
        version,request=('cuda145-worker-return-v1','nuiak-20261004-joe-big-dog-cuda145') if kind=='cuda145' else (
            'robust153-return-v1','nuiak-20261004-worker-robust153')
        t.require(manifest['version']==version and manifest['request_id']==request,'manifest_identity')
        refs=manifest['files'] if kind=='cuda145' else [dict(path=r['file'],bytes=r['bytes'],sha256=r['sha256']) for r in manifest['files']]
        t.require(len(refs)==len(members)-1 and len({r['path'] for r in refs})==len(refs) and
                  {r['path'] for r in refs}|{'manifest.json'}=={m.name for m in members},'manifest_membership')
        for ref in refs:
            member=tar.getmember(ref['path'])
            t.require(member.size==ref['bytes'],'member_size')
            digest=hashlib.sha256()
            with tar.extractfile(member) as f:
                for chunk in iter(lambda:f.read(1_048_576),b''):digest.update(chunk)
            t.require(digest.hexdigest()==ref['sha256'],'member_hash')
        t.require(shutil.disk_usage(output.parent).free>=size+1_000_000_000,'storage_reserve')
        output.mkdir()
        for member in members:
            dest=output/member.name;dest.parent.mkdir(parents=True,exist_ok=True)
            with tar.extractfile(member) as src,dest.open('xb') as dst:shutil.copyfileobj(src,dst)
    t.verified(archive,expected)
    for ref in refs:t.verified(output/ref['path'],ref)
    return {'members':len(members),'expandedBytes':size,'allHashesVerified':True,'executedPeerCode':False}


if __name__=='__main__':
    p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--extract',action='store_true');mode.add_argument('--evaluate',action='store_true');args=p.parse_args()
    if args.extract:
        expected=t.document(BASE/'peer-result.json')['return_artifact']
        report=extract(BASE/'candidates.tar.gz',BASE/'extracted',expected)
        print(json.dumps(report,indent=2))
    else:evaluate()
