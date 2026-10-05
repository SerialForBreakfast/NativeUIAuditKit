"""Bind compact content masks to the already admitted CUDA145 Fixture tensors."""
import hashlib
import json
from pathlib import Path
import tarfile
import numpy as np
import content127 as c
import prepare_worker145 as w

BASE=c.h.ROOT/'reports/work/WORKER-ROBUST-153/artifacts'
PIN='2af4c6896480b4ebc35d61320c13f26173dd7b9c544dfb9167b135924f574058'


def validate(x,mask,original):
    if x.shape!=(108,6,128,192) or mask.shape!=x.shape or mask.dtype!=bool:
        raise ValueError('mask_shape')
    if not np.array_equal(x,original) or not np.isfinite(x).all():raise ValueError('tensor_binding')
    if np.any(x[~mask]!=0) or not mask.any():raise ValueError('padding')
    bank={}
    for row,m in zip(x,mask):
        for start in (0,3):
            key=hashlib.sha256(row[start:start+3].tobytes()).hexdigest()
            value=m[start:start+3]
            if key in bank and not np.array_equal(bank[key],value):raise ValueError('endpoint_mask_conflict')
            bank[key]=value
    if len(bank)!=178:raise ValueError('endpoint_count')
    return sorted(bank)


def main():
    out=c.h.fresh(BASE/'export01');source=c.h.ROOT/'reports/work/WORKER-CUDA-145/artifacts/export01/payload/training.pt'
    if hashlib.sha256(source.read_bytes()).hexdigest()!=PIN:raise ValueError('source_hash')
    x,y,mask,_,_,groups,_=c.setup();parent,rows,*_=w.a.inputs()
    selected=w.selected(rows,groups['oldTrain']);indices=groups['oldTrain']
    torch=w.a.r.d.torch_runtime();original=torch.load(source,weights_only=True,map_location='cpu')
    x=x[indices].copy();mask=mask[indices].copy()
    endpoints=validate(x,mask,original['images'].numpy())
    if not np.array_equal(y[indices],original['labels'].numpy()):raise ValueError('labels')
    out.mkdir(parents=True);payload=out/'payload';payload.mkdir()
    torch.save({'contentMask':torch.from_numpy(mask)},payload/'masks.pt')
    manifest=dict(version='worker-robust153-masks-v1',trainingTensorSHA256=PIN,
        pairIDs=[r['id'] for r in selected],shape=list(mask.shape),dtype='bool',
        maskBytesSHA256=hashlib.sha256(mask.tobytes()).hexdigest(),endpointHashes=endpoints,
        sourceKind='fixture-procedural-renderer-v1',role='train',independentEvaluation=False,
        files=[dict(path='masks.pt',bytes=(payload/'masks.pt').stat().st_size,
                    sha256=hashlib.sha256((payload/'masks.pt').read_bytes()).hexdigest())])
    c.h.write(payload/'manifest.json',manifest)
    archive=out/'nuiak-worker-robust153-masks-v1.tar.gz'
    with tarfile.open(archive,'w:gz') as t:
        for p in sorted(payload.iterdir()):t.add(p,arcname=p.name,recursive=False)
    with tarfile.open(archive) as t:
        if sorted(t.getnames())!=['manifest.json','masks.pt']:raise ValueError('members')
        for p in payload.iterdir():
            if t.extractfile(p.name).read()!=p.read_bytes():raise ValueError('archive_replay')
    tx=dict(version=2,peer='joe-big-dog/NUIAK',requestID='nuiak-20261004-worker-robust153',
        sharedPath='nuiak/'+archive.name,localPath=str(archive.relative_to(c.h.ROOT)),
        bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
        receiptPath='joe-big-dog/robust153-receipt.json')
    c.h.write(out/'transaction.json',tx);print(json.dumps(tx,indent=2))


if __name__=='__main__':main()
