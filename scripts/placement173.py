"""One full-corpus native-placement candidate using the existing exporter/trainer."""
import argparse
import collections
import csv
import importlib.metadata
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import yaml
import placement172 as data
import eval_repair165 as control
import eval_translation170 as comparison
from export_coco import load_category_map,CATEGORY_MAP
from page_regeneration41 import checked_export_labels
h=data.h
OUT=h.ROOT/'reports/work/IOS-PLACEMENT-173/artifacts'
RUN=h.ROOT/'NativeUITrainer/yolo_runs/placement173-r019'
ADMISSION_SHA='ef2e1f9ca25ee6371a0931ab220450cd4ab47f059db6045e0bb545ff723ae0c8'


def sealed(path,limit=64*1024**2):
    doc=h.read(path,limit)
    h.require(doc['seal']==h.digest({k:v for k,v in doc.items() if k!='seal'}),'changed_seal')
    return doc


def check_membership(base,added,reused):
    h.require(len(base)==19740 and collections.Counter(r['split'] for r in base)==dict(train=14540,val=2800,test=2400),'base_membership')
    h.require(len(added)==264 and len(reused)==24 and len({r['id'] for r in added})==264,'additional_membership')
    parents={Path(r['id']).stem for r in base if r['split']=='train'}
    h.require(all(r['split']=='train' and r['group'] in parents for r in added),'training_ancestry')
    h.require(not ({r['id'] for r in added}&{r['id'] for r in reused}),'reused_control_added')
    pixels={r['pixelSHA256'] for r in base}
    for row in added:
        h.require(row['pixelSHA256'] not in pixels,'duplicate_or_split_leakage');pixels.add(row['pixelSHA256'])


def prepare():
    h.require(not OUT.exists() and not RUN.exists(),'output_collision')
    admission_path=data.OUT/'corpus-audit.json'
    h.require(h.sha(admission_path)==ADMISSION_SHA,'admission_changed')
    admission=sealed(admission_path)
    h.require(admission['eligible'] and not admission['duplicates'],'unqualified_corpus')
    basepath=h.checked(h.ROOT,admission['baseManifest'],64*1024**2);base=h.read(basepath,64*1024**2)['rows']
    added=admission['newTrainingRows'];check_membership(base,added,admission['reusedControls'])
    h.require(shutil.disk_usage(h.ROOT).free>8*1024**3,'space')
    # Verify complete base bytes once, not repeated decode/checkpoint checkpoints.
    for i,row in enumerate(base):
        for key in ('image','annotation','label'):h.checked(h.ROOT,row[key])
        if i%5000==0:print('verified base',i+1,flush=True)
    for row in added:
        for key in ('image','annotation','hidden'):h.checked(h.ROOT,row[key])
    OUT.mkdir(parents=True);source=OUT/'export-input/train';source.mkdir(parents=True)
    for row in added:
        for key in ('image','annotation'):
            path=h.checked(h.ROOT,row[key]);(source/path.name).symlink_to(path)
    export=OUT/'export'
    command=[sys.executable,str(h.ROOT/'scripts/export_coco.py'),'--dataset',str(source.parent),'--output',str(export)]
    with (OUT/'export.log').open('x') as log:
        result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,cwd=h.ROOT)
    h.require(result.returncode==0,'export_failed')
    categories,names=load_category_map(CATEGORY_MAP);new=[]
    h.require({p.stem for p in (export/'train/images').iterdir()}=={r['id'] for r in added} and
        {p.stem for p in (export/'train/labels').iterdir()}=={r['id'] for r in added},'export_membership')
    for split in ('val','test'):
        h.require(not list((export/split/'images').iterdir()) and not list((export/split/'labels').iterdir()),'export_role_change')
    for row in added:
        image=h.checked(h.ROOT,row['image']);annotation=h.checked(h.ROOT,row['annotation'])
        label=export/'train/labels'/(row['id']+'.txt')
        h.require(h.sha(export/'train/images'/image.name)==row['image']['sha256'],'export_pixels')
        checked_export_labels(h.read(annotation),label.read_text(),categories)
        new.append(dict(row,label=h.ref(label)))
    root=OUT/'dataset'
    for row in base+new:
        for kind,key in [('images','image'),('labels','label')]:
            path=h.checked(h.ROOT,row[key]);dest=root/row['split']/kind/path.name
            dest.parent.mkdir(parents=True,exist_ok=True);h.require(not dest.exists(),'staging_collision');dest.symlink_to(path)
    config=dict(path=str(root),train='train/images',val='val/images',test='test/images',names=names)
    with (root/'dataset.yaml').open('x') as f:yaml.safe_dump(config,f)
    h.write(OUT/'membership.json',dict(version='ios-placement173-v1',rows=base+new,admission=h.ref(admission_path),
        base=h.ref(basepath),counts=dict(train=14804,val=2800,test=2400),added=264,reused=24,
        evaluationPreserved=5200,config=h.ref(root/'dataset.yaml')),sealed=True)
    print('exported/verified/staged20004 members;264added;24duplicates excluded',flush=True)


def execute():
    for key,rel in [('TMPDIR','.build/tmp'),('MPLCONFIGDIR','NativeUITrainer/.mplconfig'),
                    ('TORCH_HOME','NativeUITrainer/.torch'),('YOLO_CONFIG_DIR','NativeUITrainer/.ultralytics')]:os.environ[key]=str(h.ROOT/rel)
    os.environ.update(PYTHONDONTWRITEBYTECODE='1',YOLO_OFFLINE='true',YOLO_AUTOINSTALL='false')
    import torch
    h.require(torch.backends.mps.is_available(),'mps_unavailable')
    h.require(not RUN.exists() and not (OUT/'protocol.json').exists(),'launch_collision')
    membership=sealed(OUT/'membership.json');config=h.checked(h.ROOT,membership['config'])
    h.checked(h.ROOT,membership['admission']);h.checked(h.ROOT,membership['base'],64*1024**2)
    h.require(shutil.disk_usage(h.ROOT).free>8*1024**3,'space')
    for i,row in enumerate(membership['rows']):
        for kind,key in [('images','image'),('labels','label')]:
            path=h.checked(h.ROOT,row[key]);staged=config.parent/row['split']/kind/path.name
            h.require(staged.resolve()==path,'staged_input_changed')
        if i%5000==0:print('launch byte verification',i+1,flush=True)
    prior=h.read(control.r.ART/'launch-corrected.json');initializer=Path(prior['initializer']['path'])
    h.require(h.sha(initializer)==control.r.WEIGHT_SHA,'initializer_changed')
    checkpoint,refs=control.ready('r017-repaired')
    # Bind the reused compatible control exports before spending training compute.
    control_refs=[]
    for name,index in [('combined',0),('page',3)]:
        path=comparison.OUT/('017-'+name+'-predictions.json');doc=h.read(path,256*1024**2)
        control.e.validated_artifact(doc,control.e.load_request(refs[index],41),h.sha(checkpoint),expected_settings=comparison.SETTINGS)
        control_refs.append(h.ref(path))
    command=[sys.executable,str(h.ROOT/'scripts/train_ios_model.py'),'--dataset',str(config.parent),
        '--initial-weights',str(initializer),'--epochs','5','--batch','8','--imgsz','640','--workers','0',
        '--name',RUN.name,'--full-frame-finetune','--timing']
    h.write(OUT/'protocol.json',dict(command=command,initializer=h.ref(initializer),control=h.ref(checkpoint),
        controlPredictions=control_refs,evaluation=[h.ref(p) for p in refs],membership=h.ref(OUT/'membership.json'),
        settings=dict(control.full_frame_finetune_kwargs(),epochs=5,batch=8,imgsz=640,workers=0,seed=42),
        sources=[h.ref(__file__),h.ref(h.ROOT/'scripts/train_ios_model.py')],
        packages={k:importlib.metadata.version(k) for k in ('torch','ultralytics','numpy')},
        budgetBytes=2*1024**3,wallTimeLimit=None,authority='Standing local training/no-wall-cap',selection='fixed-last',
        independentEvaluation=False),sealed=True)
    started=time.monotonic()
    with (OUT/'training.log').open('x') as log:
        child=subprocess.Popen(command,cwd=h.ROOT,env=os.environ.copy(),stdout=log,stderr=subprocess.STDOUT)
        h.write(OUT/'execution.json',dict(pid=child.pid,command=command,protocol=h.ref(OUT/'protocol.json')))
        print('Run019 PID',child.pid,flush=True);code=child.wait()
    result=dict(exitCode=code,elapsedSeconds=time.monotonic()-started,log=h.ref(OUT/'training.log'))
    if code==0:result['checkpoint']=h.ref(RUN/'weights/last.pt')
    h.write(OUT/'completion.json',result,sealed=True)
    h.require(code==0,'training_failed_preserved')
    h.require(sum(p.stat().st_size for p in RUN.rglob('*') if p.is_file())<2*1024**3,'output_budget')
    print('Run019 terminal',code,flush=True)


def check_terminal(args,old,rows):
    expected=dict(old,data=str(OUT/'dataset/dataset.yaml'),name=RUN.name,save_dir=str(RUN));expected.pop('save_dir',None)
    h.require(all(args.get(k)==v for k,v in expected.items()),'nonmatched_settings')
    h.require(len(rows)==5 and [r['epoch'] for r in rows]==['1','2','3','4','5'],'epoch_count')
    required={'time','train/box_loss','train/cls_loss','train/dfl_loss','val/box_loss','val/cls_loss','val/dfl_loss','metrics/mAP50(B)','metrics/mAP50-95(B)'}
    h.require(all(required<=r.keys() and all(math.isfinite(float(v)) for v in r.values()) for r in rows),'nonfinite_or_missing_epochs')


def ready():
    import shared_transfer
    receipt=sealed(OUT/'completion.json');protocol=sealed(OUT/'protocol.json')
    h.require(receipt['exitCode']==0,'incomplete_run')
    for ref in protocol['sources']+[protocol['membership'],protocol['initializer'],protocol['control']]+protocol['controlPredictions']:
        h.checked(h.ROOT,ref,256*1024**2)
    checkpoint=h.checked(h.ROOT,receipt['checkpoint'],256*1024**2)
    h.require(checkpoint.resolve()==(RUN/'weights/last.pt').resolve(),'wrong_checkpoint')
    prior,_=control.ready('r017-repaired')
    with (RUN/'results.csv').open() as f:rows=list(csv.DictReader(f))
    check_terminal(shared_transfer.document(RUN/'args.yaml'),shared_transfer.document(prior.parent.parent/'args.yaml'),rows)
    return checkpoint,[h.checked(h.ROOT,ref,256*1024**2) for ref in protocol['evaluation']]


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','execute']);args=parser.parse_args();globals()[args.mode]()
