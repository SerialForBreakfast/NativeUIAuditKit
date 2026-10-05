"""Export only admitted procedural Fixture tensors for the assigned CUDA worker."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import adapt_reflow117 as a


def selected(rows,indices):
    expected=list(range(24))+list(range(29,113))
    if indices!=expected or len(rows)!=113:raise ValueError('worker_membership')
    result=[rows[i] for i in indices]
    if any(r['group']!='fixture-procedural-renderer-v1' or r['split']!='train' or type(r['changed']) is not bool for r in result):
        raise ValueError('worker_source_role')
    if len({r['id'] for r in result})!=108:raise ValueError('worker_duplicate_id')
    return result


def build(destination):
    out=a.h.fresh(destination);parent,rows,pixels,labels,_=a.inputs()
    indices=parent['oldTrainIndices'];chosen=selected(rows,indices)
    for row in chosen:
        for ref in row['images']:a.h.checked(a.h.ROOT,ref)
    torch=a.r.d.torch_runtime();x=torch.from_numpy(pixels[indices].copy());y=torch.from_numpy(labels[indices].copy())
    a.h.require(x.shape==(108,6,128,192) and torch.isfinite(x).all() and ((x>=0)&(x<=1)).all()
                and y.tolist()==[float(r['changed']) for r in chosen],'worker_tensor')
    out.mkdir(parents=True);bundle=out/'payload';bundle.mkdir()
    torch.save(dict(images=x,labels=y),bundle/'training.pt')
    for name in ('focus_temporal_transition.py','focus_spatial_transition.py'):
        shutil.copyfile(a.h.ROOT/'scripts'/name,bundle/name)
    manifest=dict(version='worker-cuda145-v1',role='train',independentEvaluation=False,
        sourceKind='fixture-procedural-renderer-v1',excluded='Settings, Region112, retained surveys and final evaluation',
        shape=list(x.shape),positiveCount=int(y.sum()),negativeCount=int((y==0).sum()),
        pairIDs=[r['id'] for r in chosen],sourceImageHashes=[[v['sha256'] for v in r['images']] for r in chosen],
        inputIndices=indices,sourceProtocolSHA256=hashlib.sha256(a.r.PARENT.read_bytes()).hexdigest(),
        files=[dict(path=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(bundle.iterdir())])
    a.h.write(bundle/'manifest.json',manifest,sealed=True)
    archive=out/'nuiak-worker-cuda145-fixture108-v1.tar.gz'
    with tarfile.open(archive,'w:gz') as tar:
        for p in sorted(bundle.iterdir()):tar.add(p,arcname=p.name,recursive=False)
    with tarfile.open(archive) as tar:
        a.h.require(len(tar.getmembers())==4 and all(m.isfile() and '/' not in m.name for m in tar.getmembers()),'archive_members')
        for entry in manifest['files']:
            raw=tar.extractfile(entry['path']).read()
            a.h.require(len(raw)==entry['bytes'] and hashlib.sha256(raw).hexdigest()==entry['sha256'],'archive_hash')
    result=dict(path=str(archive.relative_to(a.h.ROOT)),bytes=archive.stat().st_size,
                sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),manifest=a.h.ref(bundle/'manifest.json'),
                pairs=108,positiveCount=manifest['positiveCount'],negativeCount=manifest['negativeCount'])
    a.h.write(out/'transfer.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
