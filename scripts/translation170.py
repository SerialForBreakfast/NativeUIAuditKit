"""One source-pinned matched translation arm; reuse trainer and evaluation contracts."""
import argparse
import os
import shutil
import subprocess
import sys
import time
import importlib.metadata
from pathlib import Path
import eval_repair165 as e
h=e.h
OUT=h.ROOT/'reports/work/IOS-TRANSLATION-170/attempt02/artifacts'
RUN=h.ROOT/'NativeUITrainer/yolo_runs/translation170-r018'

def execute():
    import torch
    import ultralytics.data.augment as augment
    h.require(torch.backends.mps.is_available(),'mps_unavailable')
    control,refs=e.ready('r017-repaired')
    prior=h.read(e.r.ART/'launch-corrected.json')
    config=h.checked(h.ROOT,prior['configs']['r017-repaired'])
    initializer=Path(prior['initializer']['path'])
    h.require(h.sha(initializer)==e.r.WEIGHT_SHA,'initializer_changed')
    h.require(not OUT.exists() and not RUN.exists(),'output_collision')
    h.require(shutil.disk_usage(h.ROOT).free>8*1024**3,'space')
    overlay=h.read(h.checked(h.ROOT,prior['inputs'][1],64*1024**2),64*1024**2)
    for index,row in enumerate(overlay['rows']):
        root=config.parent if row['split']=='train' else e.r.ART/'common'
        for kind,key in [('images','image'),('labels','label')]:
            path=h.checked(h.ROOT,row[key])
            staged=root/row['split']/kind/Path(row[key]['path']).name
            h.require(staged.resolve()==path,'staged_input_changed')
        if index%5000==0:print('verified',index+1,flush=True)
    OUT.mkdir(parents=True)
    command=[sys.executable,str(h.ROOT/'scripts/train_ios_model.py'),'--dataset',str(config.parent),
        '--initial-weights',str(initializer),'--epochs','5','--batch','8','--imgsz','640',
        '--workers','0','--name',RUN.name,'--full-frame-finetune','--translation-ablation','--timing']
    h.write(OUT/'protocol.json',dict(initializer=h.ref(initializer),control=h.ref(control),
        dataset=h.ref(config),overlay=prior['inputs'][1],evaluation=[h.ref(x) for x in refs],
        settings=dict(e.full_frame_finetune_kwargs(),translate=.35,epochs=5,batch=8,imgsz=640,workers=0,seed=42),
        sources=[h.ref(__file__),h.ref(h.ROOT/'scripts/train_ios_model.py')],
        augmentationSourceSHA256=h.sha(Path(augment.__file__)),
        packages={k:importlib.metadata.version(k) for k in ('torch','ultralytics','numpy')},
        command=command,budgetBytes=2*1024**3,selection='fixed-last',independentEvaluation=False),sealed=True)
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','YOLO_OFFLINE':'true','YOLO_AUTOINSTALL':'false'}
    for key,rel in [('TMPDIR','.build/tmp'),('MPLCONFIGDIR','NativeUITrainer/.mplconfig'),
                    ('TORCH_HOME','NativeUITrainer/.torch'),('YOLO_CONFIG_DIR','NativeUITrainer/.ultralytics')]:env[key]=str(h.ROOT/rel)
    started=time.monotonic()
    with (OUT/'training.log').open('x') as log:
        child=subprocess.Popen(command,cwd=h.ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        h.write(OUT/'execution.json',dict(pid=child.pid,command=command,state='running',protocol=h.ref(OUT/'protocol.json')))
        print('Run018 pid',child.pid,flush=True);code=child.wait()
    result=dict(exitCode=code,elapsedSeconds=time.monotonic()-started,log=h.ref(OUT/'training.log'))
    if code==0:result['checkpoint']=h.ref(RUN/'weights/last.pt')
    h.write(OUT/'completion.json',result,sealed=True)
    h.require(code==0,'training_failed_preserved')
    h.require(sum(p.stat().st_size for p in RUN.rglob('*') if p.is_file())<2*1024**3,'output_budget')
    print('Run018 terminal',code,flush=True)

if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args();execute()
