"""Compare the actual crop trainer across a process restart. No model promotion."""
import argparse
import json
from pathlib import Path
import subprocess
import shutil
import sys
import time
import research_queue as q
from template_inputs398 import checked, pin

OUT = None


def repeat_value(cfg):
    value = cfg.get('repeat', 1)
    q.require(type(value) is int and 1 <= value <= 16, 'resume_repeat')
    q.require(set(cfg) <= {'membership', 'initialization', 'repeat'}, 'resume_configuration_fields')
    return value


def phase(config, output, mode, resume=None):
    from train_focus_ring_detector import train_native_hcf
    cfg=q.load(config)
    rows=q.load(checked(cfg['membership']))['rows']
    for row in rows:
        q.require(q.digest(Path(row['path'])) == row['sha256'], 'resume_crop_changed')
    initial=checked(cfg['initialization'])
    output.mkdir(parents=True, exist_ok=False)
    result=train_native_hcf(rows,initial,output,seed=371,profile='balanced',selection='fixed-last',
        deduplicate=True,resume=resume,stop_after_epoch=12 if mode=='boundary' else None,
        repeat=repeat_value(cfg))
    q.save(output/'fit.json',dict(result,modelAccepted=False))


def tensor_difference(a,b):
    import torch
    if isinstance(a,torch.Tensor):
        q.require(isinstance(b,torch.Tensor) and a.shape==b.shape and a.dtype==b.dtype,'resume_tensor_shape')
        q.require(torch.isfinite(a).all().item() and torch.isfinite(b).all().item(),'resume_nonfinite')
        return float((a.double()-b.double()).abs().max()) if a.numel() else 0.0
    if isinstance(a,dict):
        q.require(isinstance(b,dict) and set(a)==set(b),'resume_state_keys')
        return max((tensor_difference(a[k],b[k]) for k in a),default=0.0)
    if isinstance(a,(list,tuple)):
        q.require(type(a)==type(b) and len(a)==len(b),'resume_state_sequence')
        return max((tensor_difference(x,y) for x,y in zip(a,b)),default=0.0)
    q.require(a==b,'resume_state_value')
    return 0.0


def qualify():
    from template_adapters395 import document, resolve_inputs
    refs=resolve_inputs(q.load(OUT.parents[2]/'spec.json')['template'],OUT)
    cfg=document(refs['configuration'])
    document(refs['membership']);checked(refs['initialization']).read_bytes()
    config=OUT/'config.json'
    q.require(q.load(config)==cfg,'resume_configuration_changed')
    repeat = repeat_value(cfg)
    for key in ('membership', 'initialization'):checked(cfg[key])
    start=time.monotonic()
    checkpoint=None
    for name in ('uninterrupted','boundary','restored'):
        q.save(OUT.parent/'progress.json',dict(step='Checkpoint comparison: '+name,
            completed=('uninterrupted','boundary','restored').index(name),total=3,updatedAt=time.time()),replace=True)
        args=[sys.executable,str(Path(__file__).resolve()),str(config),str(OUT/name),name]
        if name=='restored':args+=['--resume',str(checkpoint)]
        with (OUT/(name+'.log')).open('w') as log:
            subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=550)
        if name=='boundary':checkpoint=OUT/name/'last.pt';checkpoint_hash=q.digest(checkpoint)
    import torch
    a=torch.load(OUT/'uninterrupted/last.pt',map_location='cpu',weights_only=False)
    b=torch.load(OUT/'restored/last.pt',map_location='cpu',weights_only=False)
    q.require(a['resumeContract']==b['resumeContract'] and a['epoch']==b['epoch']==30,'resume_endpoint')
    metrics={key:tensor_difference(a[key],b[key]) for key in ('state_dict','optimizer','scheduler','torchRNG','mpsRNG')}
    q.require(a['pythonRNG']==b['pythonRNG'],'resume_python_rng')
    import numpy as np
    q.require(a['numpyRNG'][0]==b['numpyRNG'][0] and np.array_equal(a['numpyRNG'][1],b['numpyRNG'][1])
              and a['numpyRNG'][2:]==b['numpyRNG'][2:],'resume_numpy_rng')
    loss_delta=max(abs(x['trainLoss']-y['trainLoss']) for x,y in zip(a['history'],b['history']))
    passed=all(v==0 for v in metrics.values()) and loss_delta==0 and q.digest(checkpoint)==checkpoint_hash
    report=dict(version='hcf-crop-restoration-v1',passed=passed,metrics=metrics,lossMaximumDifference=loss_delta,
        endpointEpoch=30,interruptionEpoch=12,totalTrainingEpochs=60,checkpoint=pin(checkpoint),
        sources={key:cfg[key] for key in ('membership','initialization')},
        repeat=repeat,scopeVersion='training-subset-parity-v1',seconds=time.monotonic()-start,modelAccepted=False,
        scope='Fixed-last crop trainer on retained tiny training membership and this MPS runtime. No detector or arbitrary checkpoint qualification.')
    q.save(OUT/'restoration.json',report)
    q.require(passed,'resume_comparison_failed')
    shutil.copyfile(OUT/'restored/final.pt',OUT/'final.pt')
    shutil.copyfile(OUT/'restored/history.json',OUT/'history.json')
    q.save(OUT/'fit.json',dict(epochs=30,modelAccepted=False,qualificationOnly=True,totalTrainingEpochs=60))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('config',type=Path);p.add_argument('output',type=Path)
    p.add_argument('mode',choices=['uninterrupted','boundary','restored']);p.add_argument('--resume',type=Path)
    args=p.parse_args();phase(args.config,args.output,args.mode,args.resume)
