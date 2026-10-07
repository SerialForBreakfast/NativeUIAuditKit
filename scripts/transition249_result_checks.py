"""Reject incomplete or changed worker predictions before local model replay."""
import numpy as np


def validate(result, run, manifest_hash, sizes):
    if result.get('id')!=run or result.get('manifestSHA256')!=manifest_hash:
        raise ValueError('result_identity')
    if result.get('backend')!='cpu':raise ValueError('backend_changed')
    if set(result.get('predictions',{}))!=set(sizes):raise ValueError('prediction_membership')
    for name,count in sizes.items():
        values=np.asarray(result['predictions'][name],dtype=float)
        if values.shape!=(count,) or not np.isfinite(values).all() or not ((values>=0)&(values<=1)).all():
            raise ValueError('invalid_predictions')
    history=result.get('history',[])
    if [r.get('epoch') for r in history]!=list(range(1,121)):raise ValueError('incomplete_training')
    if not all(np.isfinite(r.get('loss',np.nan)) for r in history):raise ValueError('invalid_loss')
    return True


def review(package,returned,output):
    import json
    import torch
    import shared_transfer as s
    import transition249_worker as worker
    import transition245 as t
    if output.exists():raise ValueError('output_collision')
    manifest=worker.read_package(package);pin=worker.digest(package/'manifest.json')
    complete=s.document(returned/'complete.json')
    if complete.get('manifestSHA256')!=pin or complete.get('runs')!=[r['id'] for r in manifest['runs']]:
        raise ValueError('completion_identity')
    torch.set_num_threads(2)
    sizes={name:len(np.load(package/name,mmap_mode='r',allow_pickle=False)) for name in manifest['evaluation']}
    # This local member already passed the pinned package hash check.
    # The shared-status parser has a smaller event limit than this corpus manifest.
    membership=json.loads((package/'membership.json').read_text())
    rows=membership['rows'];native=np.array([r['changed'] for r in rows]);replay=np.array(membership['replayLabels'])
    initializer=torch.load(package/'initializer.pt',map_location='cpu',weights_only=True)['state']
    reports={}
    for item in manifest['runs']:
        root=returned/item['id'];result=s.document(root/'result.json')
        validate(result,item['id'],pin,sizes)
        checkpoint=root/'last.pt'
        if checkpoint.is_symlink() or checkpoint.stat().st_size>8*1024**2 or worker.digest(checkpoint)!=result['checkpointSHA256']:
            raise ValueError('checkpoint_hash_or_size')
        saved=torch.load(checkpoint,map_location='cpu',weights_only=True)
        if saved['manifestSHA256']!=pin or saved['run']!=item:raise ValueError('checkpoint_configuration')
        if any(not torch.isfinite(value).all() for value in saved['state'].values()):
            raise ValueError('nonfinite_weights')
        if any(not torch.equal(value,saved['state'][key]) for key,value in initializer.items() if not key.startswith('change.')):
            raise ValueError('geometry_changed')
        net=worker.make_model(torch,paired_context=True);net.load_state_dict(saved['state']);net.eval();conditions={}
        for name in manifest['evaluation']:
            values=np.load(package/name,mmap_mode='r',allow_pickle=False);local=worker.score(net,values)
            if not np.isfinite(local).all():raise ValueError('nonfinite_local_predictions')
            peer=np.asarray(result['predictions'][name]);error=float(np.max(np.abs(local-peer)))
            if error>1e-4 or not np.array_equal(t.p.decisions(local),t.p.decisions(peer)):
                raise ValueError('prediction_parity')
            truth=native if 'native' in name else replay if 'replay' in name else np.zeros(len(local))
            conditions[name]=dict(summary=t.n.w.summary(local,truth),maximumError=error)
            if name=='native.npy':conditions[name]['byRoleAndCondition']=t.summaries(local,rows)
        reports[item['id']]=dict(conditions=conditions,checkpointSHA256=worker.digest(checkpoint))
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(dict(manifestSHA256=pin,results=reports,localReplayVerified=True,productionEligible=False),indent=2))


if __name__=='__main__':
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);p.add_argument('returned',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();review(a.package,a.returned,a.output)
