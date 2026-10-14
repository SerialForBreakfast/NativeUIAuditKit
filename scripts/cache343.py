"""Qualify fixed-input frozen outputs without changing training models."""
import copy
import hashlib
import json
import os
import time
import numpy as np
import research_queue as q
from research_campaign340 import pin

OUT=None


def cache_key(inputs,identities):
    h=hashlib.sha256(json.dumps(identities,sort_keys=True,allow_nan=False).encode())
    h.update(str(inputs.shape).encode());h.update(str(inputs.dtype).encode());h.update(inputs.tobytes())
    return h.hexdigest()


def store(folder,key,values):
    path=folder/(key+'.npz');q.require(not path.exists(),'cache_collision')
    temporary=folder/(key+'.partial')
    with temporary.open('xb') as stream:
        np.savez(stream,values=values,key=np.array(key),digest=np.array(hashlib.sha256(values.tobytes()).hexdigest()))
        stream.flush();os.fsync(stream.fileno())
    temporary.rename(path)
    return path


def read(folder,key):
    path=folder/(key+'.npz');q.require(path.is_file(),'cache_not_complete')
    with np.load(path,allow_pickle=False) as data:
        q.require(str(data['key'])==key,'cache_identity');values=data['values'].copy()
        q.require(str(data['digest'])==hashlib.sha256(values.tobytes()).hexdigest(),'cache_corrupt')
    q.require(values.dtype==np.float32 and np.isfinite(values).all(),'cache_values')
    return values


def run():
    import additive341 as a
    a.t.set_num_threads(2);config=q.load(OUT/'config.json');start=time.monotonic()
    for ref in config['inputs']:q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'input_hash')
    negatives=q.load(q.ROOT/'reports/work/FOCUS-341/negatives.json')['rows'][:4]
    source={r['id']:r for r in q.load(q.ROOT/'reports/work/FOCUS-326/corpus.json')['rows']['independent']}
    rows=negatives+[source[r['matchedMovementID']] for r in negatives]
    q.require(all(r['role']=='train' for r in rows),'role')
    x=np.stack([a.r.s.encoded(*[a.r.s.image(v['path'],v['sha256']) for v in row['images']],(192,128))[0] for row in rows])
    detail,_=a.r.prepare(x,rows,2);inputs=np.concatenate((x,detail,a.added_details(x,rows)),1)
    identities=dict(inputs=config['inputs'],images=[r['images'] for r in rows],settings='CPU-float32-fixed-original-plus-boundary-v1')
    key=cache_key(inputs,identities);tensor=a.t.from_numpy(inputs);model=a.load(q.ROOT/config['model']['path'])
    with a.t.no_grad():frozen=model.change.whole(tensor[:,:18]).numpy()
    path=store(OUT,key,frozen);loaded=a.t.from_numpy(read(OUT,key))
    q.require(np.array_equal(frozen,loaded.numpy()),'disk_parity')
    models=[copy.deepcopy(model),copy.deepcopy(model)];values=[];gradients=[]
    for i,net in enumerate(models):
        for name,p in net.named_parameters():p.requires_grad_(name.startswith(('change.detail.','change.correction.')))
        optimizer=a.t.optim.SGD([p for p in net.parameters() if p.requires_grad],lr=.001)
        if i:
            added=tensor[:,18:];features=a.t.cat((a.r.s.c.model.change_inputs(None,added),a.e.gradient_channels(added)),1)
            prediction=loaded+net.change.correction(net.change.detail(features))
        else:prediction=net.change(tensor)
        prediction.square().mean().backward();values.append(prediction.detach())
        gradients.append({k:p.grad.clone() for k,p in net.named_parameters() if p.requires_grad});optimizer.step()
    errors=dict(logits=float((values[0]-values[1]).abs().max()),
        gradients=max(float((gradients[0][k]-gradients[1][k]).abs().max()) for k in gradients[0]),
        update=max(float((p-models[1].state_dict()[k]).abs().max()) for k,p in models[0].state_dict().items()))
    q.require(max(errors.values())<=1e-6,'cache_parity')
    q.save(OUT/'diagnostic.json',dict(inputs=config['inputs'],cache=pin(path),key=key,errors=errors,
        cases=len(rows),seconds=time.monotonic()-start,checkpointSaved=False,
        limitation='One fixed CPU update. Full-run caching is not enabled and no end-to-end speedup is claimed.'))


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS343';id='focus343-cache-parity'
    q.require(not (q.QUEUE/'jobs'/id).exists(),'existing_job')
    paths=['scripts/cache343.py','scripts/additive341.py','scripts/edge329.py','scripts/regions313.py',
        'reports/work/FOCUS-341/negatives.json','reports/work/FOCUS-326/corpus.json',
        'reports/work/research-queue/jobs/focus341-added-detail/attempts/1/out/run/added-detail/last.pt']
    refs=[pin(q.ROOT/path) for path in paths];config=folder/(id+'-config.json');q.save(config,dict(inputs=refs,model=refs[-1]))
    spec=dict(version=q.SPEC_VERSION,id=id,task='FOCUS343',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        hypothesis='Fixed frozen outputs preserve one update after storage and retrieval.',
        decisionRule='Require logits, gradients, and updated weights within 1e-6. Save no candidate.',
        adapter=dict(type='python-callable',steps=['cache343.run'],outputAttributes=['cache343.OUT']),
        inputs=refs,stage=[{'from':pin(config),'to':'config.json'}],limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    path=folder/(id+'.json');q.save(path,spec);print(q.submit(path))


if __name__=='__main__':register()
