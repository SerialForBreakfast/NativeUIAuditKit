"""Build one immutable input package for the 3-run replication batch."""
import inspect
import shutil
import tarfile
import numpy as np
import transition248 as previous
import transition249_worker as worker

t=previous.t
OUT=t.h.ROOT/'reports/work/TRANSITION-249/artifacts'


def run():
    t.p.review.require(not OUT.exists(),'output_collision')
    protocol=t.sealed(previous.OUT/'protocol.json');rows,x,_,_=t.prepare()
    t.p.review.require(rows==protocol['rows'],'membership_changed')
    old_x,_,mask,_,_,_,_,_,replay,labels=t.n.inputs()
    selected=protocol['selected'];y=np.array([r['changed'] for r in rows],np.float32)
    tx=np.concatenate((replay,x[selected],t.reverse(x[selected])))
    ty=np.concatenate((labels,y[selected],y[selected]))
    t.p.review.require(t.p.sha(tx.tobytes())==protocol['trainingSHA256'] and
                       t.p.sha(ty.tobytes())==protocol['labelsSHA256'],'training_changed')
    OUT.mkdir(parents=True);root=OUT/'package';root.mkdir()
    np.save(root/'training.npy',tx);del tx
    np.save(root/'labels.npy',ty)
    arrays={'native.npy':x,'replay.npy':replay,'reverse_native.npy':t.reverse(x),'reverse_replay.npy':t.reverse(replay)}
    for name,array in arrays.items():np.save(root/name,array)
    for mode in ('global8','left8','center8'):
        np.save(root/(mode+'.npy'),t.n.nuisance.localized(old_x[207:],mask[207:],mode))
    groups=[protocol['components'][rows[i]['group']] for i in selected]
    w=previous.weights(groups,len(replay),True);np.save(root/'group_weights.npy',w)
    native=w[len(replay):len(replay)+len(selected)];truth=y[selected]
    class_weights=np.array([native[truth==v].sum()/(truth==v).sum() for v in truth],np.float32)
    cw=np.concatenate((np.ones(len(replay),np.float32),class_weights,class_weights))
    t.p.review.require(np.isclose(w.sum(),cw.sum()),'class_mass')
    np.save(root/'class_weights.npy',cw)
    checkpoint=t.h.checked(t.h.ROOT,protocol['initializer']);shutil.copyfile(checkpoint,root/'initializer.pt')
    for name in ['focus_temporal_transition.py','focus_spatial_transition.py','transition249_worker.py']:
        shutil.copyfile(t.h.ROOT/'scripts'/name,root/name)
    (root/'fit.py').write_text(inspect.getsource(t.n.fit))
    baseline=t.sealed(t.h.ROOT/'reports/work/TRANSITION-245/artifacts/DTM063/result.json')
    np.save(root/'sanity.npy',x[:8]);np.save(root/'sanity_scores.npy',np.array(baseline['initializerProbabilities'][:8],np.float32))
    t.h.write(root/'membership.json',dict(rows=rows,selected=selected,held=protocol['held'],
        source=t.h.ref(previous.OUT/'protocol.json'),replayLabels=labels.tolist()))
    runs=[dict(id=name,weights=weights,configuration=dict(t.n.CONFIG,seed=seed)) for name,seed,weights in
          [('DTM068',43,'group_weights.npy'),('DTM069',44,'group_weights.npy'),('DTM070',42,'class_weights.npy')]]
    manifest=dict(version='transition249-v1',runs=runs,evaluation=list(arrays)+['global8.npy','left8.npy','center8.npy'],
        files={p.name:dict(bytes=p.stat().st_size,sha256=worker.digest(p)) for p in root.iterdir()},
        sourceTrainer=t.h.ref(t.n.__file__),scope='Diagnostic CPU fits only. No selection, capture, export, or promotion.')
    t.h.write(root/'manifest.json',manifest)
    archive=OUT/'transition249-inputs-v1.tar.gz'
    with tarfile.open(archive,'w:gz',compresslevel=1) as tar:
        for p in sorted(root.iterdir()):tar.add(p,arcname=p.name,recursive=False)
    t.h.write(OUT/'transfer.json',dict(file='nuiak/transition249-inputs-v1.tar.gz',bytes=archive.stat().st_size,
        sha256=worker.digest(archive),members=len(list(root.iterdir())),expandedBytes=sum(p.stat().st_size for p in root.iterdir())))
    print('built',archive,flush=True)


if __name__=='__main__':run()
