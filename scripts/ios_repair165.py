"""Pin and stage full-corpus repair comparisons, then use the existing trainer."""
import argparse
from collections import Counter
import os
import importlib.metadata
from pathlib import Path
import shutil
import subprocess
import sys
import time
import yaml
import native_repair159 as repair
h=repair.h
BASE=h.ROOT/'reports/work/IOS-REPAIR-165'
ART=BASE/'artifacts'
OVERLAY_SHA='032dd334f9ccae483809283d6659df19b03abe96af26de831caf76e08e84f35a'
WEIGHT_SHA='88c3cffb51b0b29dd71672fb64f6e60be56757e6de507886ef2f5c2ff86dd9b7'


def compare_membership(old,new):
    h.require(len(old)==len(new)==19740,'membership_count')
    h.require(Counter(r['split'] for r in old)==Counter(r['split'] for r in new)==dict(train=14540,val=2800,test=2400),'split_counts')
    changed=[];seen=set()
    for a,b in zip(old,new):
        key=a['split']+'/'+Path(a['image']['path']).name
        h.require(key==b['id'] and key not in seen,'membership_identity');seen.add(key)
        different=any(a[k]!=b[k] for k in ('image','label'))
        if different:
            h.require(a['split']=='train' and b['replaced'],'evaluation_or_unplanned_change');changed.append(key)
        else:h.require(not b['replaced'],'missing_replacement')
    h.require(len(changed)==900,'replacement_count')
    return changed


def prepare():
    source=repair.BASE/'overlay/manifest.json'
    h.require(h.sha(source)==OVERLAY_SHA,'overlay_identity')
    overlay=h.read(source,64*1024**2);oldpath=h.ROOT/'reports/work/REAL-TRANSFER-42/ios-export-verified.json'
    old=h.read(oldpath,64*1024**2)['rows'];new=overlay['rows'];changed=compare_membership(old,new)
    h.require(not overlay['duplicates'] and overlay['evaluationPreserved']==5200 and overlay['manualPreserved']==666,'overlay_admission')
    for ref in overlay['sources']:h.checked(h.ROOT,ref,64*1024**2)
    weights=repair.storage.resolve_input(h.ROOT/'NativeUITrainer/yolo_runs/phase6a_r013/weights/best.pt')
    h.require(weights.is_file() and h.sha(weights)==WEIGHT_SHA,'initializer_identity')
    h.require(shutil.disk_usage(h.ROOT).free>8*1024**3,'space')
    checked={}
    def resolve(ref):
        key=(ref['path'],ref['sha256'])
        if key not in checked:checked[key]=h.checked(h.ROOT,ref)
        return checked[key]
    # All bytes verified before staging. Cache only identical immutable refs.
    for i,(a,b) in enumerate(zip(old,new)):
        for row in (a,b):
            for k in ('image','label'):resolve(row[k])
        if i%4000==0:print('verified',i+1,'/19740',flush=True)
    ART.mkdir(parents=True)
    common=ART/'common'
    def stage(root,rows):
        for row in rows:
            split=row['split'];name=Path(row['image']['path']).name
            for kind,key,filename in [('images','image',name),('labels','label',Path(name).with_suffix('.txt').name)]:
                dest=root/split/kind;dest.mkdir(parents=True,exist_ok=True)
                (dest/filename).symlink_to(resolve(row[key]))
    stage(common,[r for r in old if r['split']!='train'])
    names=yaml.safe_load((repair.BASE/'overlay/data.yaml').read_text())['names']
    configs={}
    for arm,rows in [('r014-prior',old),('r015-repaired',new)]:
        root=ART/arm;stage(root,[r for r in rows if r['split']=='train'])
        config=dict(path=str(root),train='train/images',val=str(common/'val/images'),test=str(common/'test/images'),names=names)
        with (root/'dataset.yaml').open('x') as f:yaml.safe_dump(config,f)
        configs[arm]=h.ref(root/'dataset.yaml')
    h.write(ART/'protocol.json',dict(version='ios-repair165-v1',initializer=dict(path=str(weights),sha256=WEIGHT_SHA),
        inputs=[h.ref(oldpath),h.ref(source)],configs=configs,changedIDs=changed,
        source=[h.ref(__file__),h.ref(h.ROOT/'scripts/train_ios_model.py')],
        packages={k:importlib.metadata.version(k) for k in ('torch','torchvision','ultralytics','numpy','Pillow')},
        evaluation=[h.ref(h.ROOT/'reports/work/IOS-R013-EVAL'/(name+'_manifest.json')) for name in ('combined','withheld','addon')]+
            [h.ref(repair.PROBES/'page156-manifest.json'),h.ref(repair.PROBES/'page156-predictions.json'),
             h.ref(h.ROOT/'reports/work/IOS-R013-EVAL/candidate_predictions.json')],
        profile='full-frame-finetune',epochs=5,batch=8,imgsz=640,workers=0,
        counts=dict(train=14540,val=2800,test=2400),outputBudget=4*1024**3,
        independentEvaluation=False,selection='fixed-last',authority='Standing local training; fixed two-arm165comparison'),sealed=True)
    print('prepared two full-corpus arms',flush=True)


def freeze(corrected=False):
    """Seal launch-time evaluator/runtime pins without rewriting preparation evidence."""
    p=h.read(ART/'protocol.json');h.require(p['seal']==h.digest({k:v for k,v in p.items() if k!='seal'}),'protocol_seal')
    p.pop('seal');p['preparation']=h.ref(ART/'protocol.json');p['preparationSource']=p['source']
    for ref in p['inputs']+list(p['configs'].values()):h.checked(h.ROOT,ref,64*1024**2)
    p['source']=[h.ref(__file__),h.ref(h.ROOT/'scripts/train_ios_model.py')]
    p['packages']={k:importlib.metadata.version(k) for k in ('torch','torchvision','ultralytics','numpy','Pillow')}
    p['evaluation']=[h.ref(h.ROOT/'reports/work/IOS-R013-EVAL'/(name+'_manifest.json')) for name in ('combined','withheld','addon')]+[
        h.ref(repair.PROBES/'page156-manifest.json'),h.ref(repair.PROBES/'page156-predictions.json'),
        h.ref(h.ROOT/'reports/work/IOS-R013-EVAL/candidate_predictions.json')]
    name='launch-corrected.json' if corrected else 'launch.json'
    if corrected:
        failed=h.read(ART/'r014-prior-completion.json');h.require(failed['exitCode']==-2,'prior_attempt_not_stopped')
        h.require(not (ART/'r015-repaired-execution.json').exists(),'prior_second_arm_started')
        p['configs']={'r016-prior':p['configs']['r014-prior'],'r017-repaired':p['configs']['r015-repaired']}
        p['supersedes']=h.ref(ART/'launch.json');p['correction']='Explicit bias warmup .0001; fresh initialization, never resume014'
    h.require(not (ART/name).exists(),'launch_collision');h.write(ART/name,p,sealed=True)
    print('launch pins frozen',h.sha(ART/name))


def execute(corrected=False):
    import torch
    h.require(torch.backends.mps.is_available(),'mps_unavailable')
    launch=ART/('launch-corrected.json' if corrected else 'launch.json')
    p=h.read(launch);h.require(p['seal']==h.digest({k:v for k,v in p.items() if k!='seal'}),'protocol_seal')
    for ref in p['source']+p['inputs']:h.checked(h.ROOT,ref,64*1024**2)
    for package,version in p['packages'].items():h.require(importlib.metadata.version(package)==version,'dependency_changed')
    for ref in p['evaluation']:h.checked(h.ROOT,ref,256*1024**2)
    weights=Path(p['initializer']['path']);h.require(h.sha(weights)==WEIGHT_SHA,'initializer_changed')
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','YOLO_OFFLINE':'true','YOLO_AUTOINSTALL':'false'}
    for key,rel in [('TMPDIR','.build'),('MPLCONFIGDIR','NativeUITrainer/.mplconfig'),('TORCH_HOME','NativeUITrainer/.torch'),('YOLO_CONFIG_DIR','NativeUITrainer/.ultralytics')]:
        env[key]=str(h.ROOT/rel)
    outcomes={};started=time.monotonic()
    for arm,ref in p['configs'].items():
        config=h.checked(h.ROOT,ref);out=h.ROOT/'NativeUITrainer/yolo_runs'/('repair165-'+arm)
        h.require(not out.exists() and shutil.disk_usage(h.ROOT).free>8*1024**3,'output_collision_or_space')
        doc=h.read(h.checked(h.ROOT,p['inputs'][0 if arm.endswith('-prior') else 1],64*1024**2),64*1024**2)
        for row in doc['rows']:
            root=config.parent if row['split']=='train' else ART/'common'
            for kind,key in [('images','image'),('labels','label')]:
                original=h.checked(h.ROOT,row[key]);name=Path(row[key]['path']).name
                h.require((root/row['split']/kind/name).resolve()==original,'staged_input_changed')
        command=[sys.executable,str(h.ROOT/'scripts/train_ios_model.py'),'--dataset',str(config.parent),
            '--initial-weights',str(weights),'--model','yolo11m','--epochs','5','--batch','8','--imgsz','640',
            '--workers','0','--name',out.name,'--full-frame-finetune','--timing']
        with (ART/(arm+'.log')).open('x') as log:
            child=subprocess.Popen(command,cwd=h.ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
            h.write(ART/(arm+'-execution.json'),dict(pid=child.pid,command=command,protocol=h.ref(launch),state='running'))
            print('started',arm,'pid',child.pid,flush=True);code=child.wait()
        result=dict(exitCode=code,seconds=time.monotonic()-started,log=h.ref(ART/(arm+'.log')))
        if code==0:
            checkpoint=out/'weights/last.pt';h.require(checkpoint.is_file(),'missing_last');result['checkpoint']=h.ref(checkpoint)
        outcomes[arm]=result;h.write(ART/(arm+'-completion.json'),result,sealed=True)
        h.require(code==0,'training_failed_preserved')
        h.require(sum(f.stat().st_size for root in (h.ROOT/'NativeUITrainer/yolo_runs').glob('repair165-*') for f in root.rglob('*') if f.is_file())<p['outputBudget'],'output_budget')
    h.write(ART/('training-corrected-complete.json' if corrected else 'training-complete.json'),dict(outcomes=outcomes,seconds=time.monotonic()-started),sealed=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','freeze','execute']);parser.add_argument('--corrected',action='store_true');args=parser.parse_args()
    if args.mode=='prepare':
        h.require(not args.corrected,'prepare_not_repeated');prepare()
    else:globals()[args.mode](corrected=args.corrected)
