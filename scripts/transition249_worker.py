"""Run the fixed replication batch from verified, portable arrays."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import types
import numpy as np
import torch
from focus_temporal_transition import make_model


def require(ok,reason):
    if not ok:raise ValueError(reason)


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def read_package(root):
    manifest=json.loads((root/'manifest.json').read_text())
    require(manifest['version']=='transition249-v1','version')
    for name,ref in manifest['files'].items():
        path=root/name
        require(path.parent==root and path.resolve()==path and path.is_file(),'member_path')
        require(path.stat().st_size==ref['bytes'] and digest(path)==ref['sha256'],'member_hash')
    return manifest


def score(net,array):
    with torch.inference_mode():
        return np.concatenate([torch.sigmoid(net.change(net.change_inputs(
            torch.from_numpy(np.array(array[i:i+8],copy=True))))).flatten().numpy()
            for i in range(0,len(array),8)])


def run(root,out,execute=False):
    require(not out.exists(),'output_collision');manifest=read_package(root)
    torch.set_num_threads(2)
    state=torch.load(root/'initializer.pt',map_location='cpu',weights_only=True)['state']
    net=make_model(torch,paired_context=True);net.load_state_dict(state);net.eval()
    sanity=np.load(root/'sanity.npy',mmap_mode='r',allow_pickle=False)
    expected=np.load(root/'sanity_scores.npy',allow_pickle=False)
    observed=score(net,sanity)
    require(np.max(np.abs(expected-observed))<=1e-4,'baseline_parity')
    print('verified',len(manifest['files']),'files; baseline parity passed',flush=True)
    if not execute:return
    out.mkdir();namespace=dict(np=np,time=time,d=types.SimpleNamespace(torch_runtime=lambda:torch),
                               h=types.SimpleNamespace(require=require))
    # The exact reviewed trainer function is copied by the package builder.
    exec(compile((root/'fit.py').read_text(),'fit.py','exec'),namespace)
    for item in manifest['runs']:
        dest=out/item['id'];dest.mkdir()
        net=make_model(torch,paired_context=True);net.load_state_dict(state)
        x=np.load(root/'training.npy',mmap_mode='c',allow_pickle=False)
        y=np.load(root/'labels.npy',allow_pickle=False)
        w=np.load(root/item['weights'],allow_pickle=False)
        tick=time.monotonic()
        net,history=namespace['fit'](net,torch.from_numpy(x),torch.from_numpy(y),item['configuration'],
            lambda r:print(item['id'],r,flush=True),weights=torch.from_numpy(w))
        del x
        torch.save(dict(state=net.state_dict(),manifestSHA256=digest(root/'manifest.json'),run=item),dest/'last.pt')
        predictions={}
        for name in manifest['evaluation']:
            values=np.load(root/name,mmap_mode='r',allow_pickle=False)
            predictions[name]=score(net,values).tolist();del values
        (dest/'result.json').write_text(json.dumps(dict(id=item['id'],history=history,predictions=predictions,
             seconds=time.monotonic()-tick,torchVersion=torch.__version__,numpyVersion=np.__version__,
             backend='cpu',manifestSHA256=digest(root/'manifest.json'),checkpointSHA256=digest(dest/'last.pt'))))
    (out/'complete.json').write_text(json.dumps(dict(runs=[r['id'] for r in manifest['runs']],
         manifestSHA256=digest(root/'manifest.json'),productionEligible=False)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--execute',action='store_true');a=p.parse_args();run(a.root.resolve(),a.output.resolve(),a.execute)
