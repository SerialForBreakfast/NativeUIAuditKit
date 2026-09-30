"""Freeze and supervise one diagnostic-only MPS run through the existing trainer.

prepare never imports Torch; execute checks resources before spawning a worker.
All outputs are fresh and project-local. No downloads, retries or promotion.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
LIMITS = dict(seconds=1800, launch_available_bytes=8*2**30,
              runtime_available_bytes=3*2**30, free_disk_bytes=10*2**30,
              output_bytes=2*2**30)


def local(path):
    p = Path(path).expanduser().resolve()
    if not p.is_relative_to(ROOT):
        raise ValueError('path_outside_project')
    return p


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()


def pin(path):
    p = local(path)
    return dict(path=str(p.relative_to(ROOT)), sha256=digest(p))


def verified(record):
    p = local(ROOT/record['path'])
    if digest(p) != record['sha256']: raise ValueError('changed_hash: '+record['path'])
    return p


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def validate_member(image, label, classes):
    from PIL import Image
    with Image.open(image) as im:
        im.load()
        if min(im.size) <= 0: raise ValueError('invalid_dimensions')
        pixels = hashlib.sha256(str(im.size).encode()+im.convert('RGB').tobytes()).hexdigest()
    for line in label.read_text().splitlines():
        values = list(map(float, line.split()))
        if (len(values)!=5 or any(not math.isfinite(v) for v in values)
                or values[0]!=int(values[0]) or not 0<=values[0]<classes
                or any(not 0<=v<=1 for v in values[1:]) or min(values[3:])<=0):
            raise ValueError('invalid_yolo_label')
    return pixels


def prepare(spec_path, dataset, output, batch=8):
    import yaml
    if type(batch) is not int or batch not in (8,16): raise ValueError('unsupported_batch')
    spec_path, dataset, output = map(local, (spec_path, dataset, output))
    if output.exists(): raise ValueError('output_collision')
    spec = json.loads(spec_path.read_text())
    config_path = dataset/'dataset.yaml'
    config = yaml.safe_load(config_path.read_text())
    if config.get('nc')!=41 or len(config.get('names',{}))!=41:
        raise ValueError('wrong_taxonomy')
    saved = spec['savedRequestedConfiguration']
    if Path(saved['data']).resolve()!=config_path: raise ValueError('wrong_dataset')
    members = spec['membership']
    if len(members)!=512 or any(m['split']!='train' for m in members):
        raise ValueError('wrong_training_membership')
    rows=[]; paths=set(); pixels_by_split={'train':set(),'val':set()}
    def add(image, label, split):
        if image in paths: raise ValueError('duplicate_member')
        paths.add(image)
        pixels=validate_member(image,label,41)
        pixels_by_split[split].add(pixels)
        rows.append(dict(split=split,image=pin(image),label=pin(label),pixels_sha256=pixels))
    for member in members:
        # Check declared source split before resolving symlink targets.
        if not (ROOT/member['image']['path']).is_relative_to(dataset/'train'/'images'):
            raise ValueError('wrong_training_source')
        image,label=verified(member['image']),verified(member['label'])
        add(image,label,'train')
    val=sorted((dataset/'val/images').glob('*.png'),key=lambda p: hashlib.sha256(p.name.encode()).hexdigest())[:64]
    if len(val)!=64: raise ValueError('missing_validation')
    for image in val: add(image.resolve(),(dataset/'val/labels'/(image.stem+'.txt')).resolve(),'val')
    if pixels_by_split['train'] & pixels_by_split['val']: raise ValueError('cross_split_duplicate_pixels')
    weights=spec['sameInitialization']
    weight_record=pin(weights['path'])
    if weight_record['sha256']!=weights['sha256']: raise ValueError('changed_initial_weights')
    sources=[ROOT/'scripts'/name for name in ('mps_training_diagnostic.py','train_ios_model.py','ohem_callback.py','training_timing.py')]
    site=ROOT/'.venv-yolo/lib/python3.13/site-packages'
    sources += [site/'ultralytics'/p for p in ('engine/trainer.py','engine/model.py','data/base.py','data/dataset.py','data/utils.py','utils/checks.py')]
    versions={}
    for package in ('torch','ultralytics','numpy','pillow','psutil'):
        matches=list(site.glob(package+'-*.dist-info/METADATA'))
        if len(matches)!=1: raise ValueError('ambiguous_runtime: '+package)
        sources+=matches
        versions[package]=next(line[9:] for line in matches[0].read_text().splitlines() if line.startswith('Version: '))
    plan=dict(schema='mps-host-diagnostic-v2',created_at=datetime.now(timezone.utc).isoformat(),
              source_spec=pin(spec_path),taxonomy=pin(config_path),weights=weight_record,
              sources=[pin(p) for p in sources],versions=versions,members=rows,
              settings=dict(device='mps',batch=batch,imgsz=640,epochs=2,workers=0,seed=42),
              limits=LIMITS,quality_eligible=False,
              semantics='early-training host-wall diagnostic; not steady-state or model qualification')
    output.mkdir(parents=True)
    write(output/'plan.json',plan)
    return pin(output/'plan.json')


def load_plan(path, expected):
    path=local(path)
    if digest(path)!=expected: raise ValueError('changed_plan')
    plan=json.loads(path.read_text())
    batch=plan.get('settings',{}).get('batch')
    allowed=(8,) if plan.get('schema')=='mps-host-diagnostic-v1' else (8,16)
    if (plan.get('schema') not in ('mps-host-diagnostic-v1','mps-host-diagnostic-v2') or plan.get('limits')!=LIMITS
            or type(batch) is not int or batch not in allowed
            or plan.get('settings')!=dict(device='mps',batch=batch,imgsz=640,epochs=2,workers=0,seed=42)
            or plan.get('quality_eligible') is not False): raise ValueError('incompatible_plan')
    if [m['split'] for m in plan['members']].count('train')!=512 or len(plan['members'])!=576:
        raise ValueError('wrong_membership')
    if any(m['split'] not in ('train','val') for m in plan['members']): raise ValueError('protected_or_unknown_split')
    paths=[m['image']['path'] for m in plan['members']]
    if len(set(paths))!=len(paths): raise ValueError('duplicate_member')
    for record in [plan['source_spec'],plan['taxonomy'],plan['weights'],*plan['sources']]: verified(record)
    for member in plan['members']:
        verified(member['image']);verified(member['label'])
    return plan


def resources(path):
    import psutil
    memory=psutil.virtual_memory()
    return dict(available_bytes=memory.available,total_bytes=memory.total,
                free_disk_bytes=shutil.disk_usage(path).free)


def resource_block(snapshot, launch=True, size=0):
    key='launch_available_bytes' if launch else 'runtime_available_bytes'
    if snapshot['available_bytes']<LIMITS[key]: return 'insufficient_available_memory'
    if snapshot['free_disk_bytes']<LIMITS['free_disk_bytes']: return 'insufficient_disk'
    if size>LIMITS['output_bytes']: return 'output_budget_exceeded'
    return None


def stage(plan, output):
    import yaml
    dataset=output/'dataset'; dataset.mkdir()
    for split in ('train','val'):
        for kind in ('images','labels'): (dataset/split/kind).mkdir(parents=True)
    for index, member in enumerate(plan['members']):
        image,label=verified(member['image']),verified(member['label'])
        name=f'{index:04d}'
        for source,destination,record in ((image,dataset/member['split']/'images'/(name+image.suffix),member['image']),
                                         (label,dataset/member['split']/'labels'/(name+'.txt'),member['label'])):
            shutil.copyfile(source,destination)
            if digest(destination)!=record['sha256']: raise ValueError('staged_hash_mismatch')
    taxonomy=yaml.safe_load(verified(plan['taxonomy']).read_text())
    config=dict(path=str(dataset),train='train/images',val='val/images',nc=41,names=taxonomy['names'])
    with (dataset/'dataset.yaml').open('x') as stream: yaml.safe_dump(config,stream)
    return dataset


def supervise(command, output, env, clock=time.monotonic, sample=resources, max_seconds=1800):
    if not 0<max_seconds<=LIMITS['seconds']: raise ValueError('invalid_deadline')
    started=clock(); reason=None; samples=[]
    with (output/'trainer.log').open('xb') as log:
        process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        try:
            while process.poll() is None:
                snapshot=sample(output)
                size=sum(p.stat().st_size for p in output.rglob('*') if p.is_file())
                reason=resource_block(snapshot,False,size)
                if clock()-started>=max_seconds: reason='deadline_exceeded'
                samples.append(dict(elapsed_seconds=clock()-started,**snapshot,output_bytes=size))
                if reason: break
                time.sleep(2)
        except Exception as error:
            reason='supervisor_error: '+type(error).__name__
        finally:
            if process.poll() is None:
                process.terminate()
                try: process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill();process.wait()
    return dict(outcome='stopped' if reason else ('completed' if process.returncode==0 else 'failed'),
                reason=reason,returncode=process.returncode,pid=process.pid,
                elapsed_seconds=clock()-started,max_seconds=max_seconds,resource_samples=samples)


def execute(plan_path, expected, output, deadline=None):
    output=local(output)
    if output.exists(): raise ValueError('output_collision')
    plan=load_plan(plan_path,expected)
    output.mkdir(parents=True)
    snapshot=resources(output);reason=resource_block(snapshot)
    write(output/'preflight.json',dict(plan_sha256=expected,resources=snapshot,limits=LIMITS,
          outcome='blocked' if reason else 'ready',reason=reason,model_loaded=False))
    if reason: return dict(outcome='blocked',reason=reason,resources=snapshot)
    stage(plan,output)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',YOLO_OFFLINE='true',YOLO_AUTOINSTALL='false')
    for variable,folder in [('TMPDIR','tmp'),('YOLO_CONFIG_DIR','yolo'),('MPLCONFIGDIR','mpl'),('TORCH_HOME','torch'),('XDG_CACHE_HOME','cache')]:
        destination=output/folder;destination.mkdir();env[variable]=str(destination)
    command=[str(ROOT/'.venv-yolo/bin/python'),str(Path(__file__).resolve()),'worker',
             '--plan',str(local(plan_path)),'--sha256',expected,'--output',str(output)]
    remaining=LIMITS['seconds'] if deadline is None else min(LIMITS['seconds'],deadline-time.monotonic())
    result=(dict(outcome='stopped',reason='aggregate_deadline_exceeded',pid=None)
            if remaining<=0 else supervise(command,output,env,max_seconds=remaining))
    write(output/'receipt.json',dict(plan_sha256=expected,quality_eligible=False,**result))
    return {k:v for k,v in result.items() if k!='resource_samples'}


def worker(plan_path, expected, output):
    import yaml
    plan=load_plan(plan_path,expected);output=local(output)
    if not (output/'preflight.json').is_file() or resource_block(resources(output)):
        raise ValueError('worker_preflight_failed')
    if (output/'runs').exists(): raise ValueError('worker_output_collision')
    expected_config=dict(path=str(output/'dataset'),train='train/images',val='val/images',nc=41,
                         names=yaml.safe_load(verified(plan['taxonomy']).read_text())['names'])
    if yaml.safe_load((output/'dataset/dataset.yaml').read_text())!=expected_config:
        raise ValueError('changed_staged_config')
    for index,member in enumerate(plan['members']):
        image=output/'dataset'/member['split']/'images'/(f'{index:04d}'+Path(member['image']['path']).suffix)
        label=output/'dataset'/member['split']/'labels'/f'{index:04d}.txt'
        if digest(image)!=member['image']['sha256'] or digest(label)!=member['label']['sha256']:
            raise ValueError('changed_staged_member')
    # Fail closed on accidental network use, even if optional library checks change.
    def offline(event,args):
        if event in ('socket.connect','socket.getaddrinfo'): raise RuntimeError('diagnostic_network_forbidden')
    sys.addaudithook(offline)
    import torch
    if not torch.backends.mps.is_available(): raise RuntimeError('mps_unavailable')
    import train_ios_model
    sys.argv=['train_ios_model','--dataset',str(output/'dataset'),'--initial-weights',str(verified(plan['weights'])),
              '--model','yolo11m','--epochs','2','--batch',str(plan['settings']['batch']),'--workers','0','--imgsz','640',
              '--name','diagnostic-only','--output-dir',str(output/'runs'),'--timing']
    train_ios_model.main()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('prepare');p.add_argument('--spec',required=True);p.add_argument('--dataset',required=True);p.add_argument('--output',required=True)
    for name in ('execute','worker'):
        p=sub.add_parser(name);p.add_argument('--plan',required=True);p.add_argument('--sha256',required=True);p.add_argument('--output',required=True)
    args=parser.parse_args()
    if args.mode=='prepare': result=prepare(args.spec,args.dataset,args.output)
    elif args.mode=='execute': result=execute(args.plan,args.sha256,args.output)
    else: result=worker(args.plan,args.sha256,args.output)
    print(json.dumps(result))
