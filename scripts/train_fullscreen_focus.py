"""Validate exact admitted membership, or supervise one bounded local YOLO experiment.

Validation never imports a model. An execution contract records scope, not permission
to train by itself; the caller must hold the matching user assignment.
"""
import argparse
import importlib.metadata
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from types import SimpleNamespace

import human_annotation_review as h


def runtime_identity():
    return dict(python=sys.version,packages={name:importlib.metadata.version(name)
                for name in ('ultralytics','torch','Pillow')})


def augmentation_options(doc):
    value=doc.get('augmentation')
    if value is None:return dict(translate=0.,scale=0.)
    h.require(doc['version']=='fullscreen-focus-run-v2' and isinstance(value,dict) and
              set(value)=={'version','translate','scale'} and type(value['version']) is int and
              value['version']==1,'augmentation_contract')
    for key,limit in [('translate',.1),('scale',.3)]:
        v=value[key]
        h.require(type(v) in (int,float) and math.isfinite(v) and 0<=v<=limit,'augmentation_'+key)
    return {k:float(value[k]) for k in ('translate','scale')}


def source_image(reference, verified=None):
    """Read only a project image or an exact mounted native26 original."""
    import native_focus_spike as n
    from PIL import Image
    import hashlib
    p=Path(reference['path'])
    if p.is_absolute() and p.is_relative_to(n.USB):
        n.mounted()
        h.require(p.resolve()==p and p.is_file() and p.stat().st_size<=32*1024*1024,'unsafe_usb_image')
        h.require(h.sha(p)==reference['sha256'],'changed_usb_image')
    else:p=h.checked(h.ROOT,reference)
    if verified is not None:
        h.require(verified['image']==reference,'cached_image_identity_changed')
        return p,tuple(verified['size']),verified['pixelSHA256']
    with Image.open(p) as image:
        h.require(image.format=='PNG' and image.width*image.height<=20_000_000,'invalid_source_image')
        rgb=image.convert('RGB');size=rgb.size
        pixel=hashlib.sha256(str(size).encode()+rgb.tobytes()).hexdigest()
    return p,size,pixel


def validate(path, *, inputs_only=False, _verified_frames=None):
    doc=h.read(path)
    h.require(doc.get('version') in ('fullscreen-focus-run-v1','fullscreen-focus-run-v2'),'unsupported_run_contract')
    direct=doc['version']=='fullscreen-focus-run-v2'
    augmentation_options(doc)
    if direct:h.require(doc.get('evaluationPolicy')=='terminal-last-checkpoint' and doc.get('storage')=='read-through','invalid_v2_policy')
    h.require(doc.get('runtime')==runtime_identity(),'runtime_identity_changed')
    frames=doc['frames'];budget=doc['budget']
    h.require(0<len(frames)<=5000 and len({f['id'] for f in frames})==len(frames),'invalid_membership')
    if budget['seconds'] is None:
        h.require(direct and 'timeLimitOverride' in doc,'missing_time_limit_authority')
        authority=h.read(h.checked(h.ROOT,doc['timeLimitOverride']))
        h.require(authority.get('version')=='local-training-time-override-v1' and
            authority.get('approved') is True and authority.get('wallTimeLimit') is None and
            bool(authority.get('approvedBy')),'invalid_time_limit_authority')
    else:h.require(type(budget['seconds']) is int and 1<=budget['seconds']<=300,'invalid_budget')
    h.require(type(budget['bytes']) is int and 1024*1024<=budget['bytes']<=2*1024**3,'invalid_budget')
    h.require(type(doc['epochs']) is int and 1<=doc['epochs']<=100 and
              type(doc['batch']) is int and 1<=doc['batch']<=32 and
              doc['imgsz'] in (640,960,1280) and type(doc['seed']) is int,'invalid_training_configuration')
    checkpoint=h.checked(h.ROOT,doc['checkpoint'],128*1024*1024)
    h.require(checkpoint.suffix=='.pt','local_checkpoint_required')
    admission=h.read(h.checked(h.ROOT,doc['admission']))
    admitted=(admission.get('version')=='fullscreen-focus-admission-v1' and
        admission.get('approved') is True and admission.get('purpose')=='full-screen-focus-training'
        and admission.get('membershipSHA256')==h.digest(frames) and
        isinstance(admission.get('approvedBy'),str) and bool(admission['approvedBy'].strip()))
    h.require(admitted or inputs_only,'membership_not_admitted')
    splits=('train','evaluation') if direct else ('train','development')
    groups={};pixels={};prepared=[];total_bytes=0
    for index,f in enumerate(frames):
        h.require(f['split'] in splits and isinstance(f['group'],str) and f['group'].strip(),
                  'invalid_split_group')
        h.require(groups.setdefault(f['group'],f['split'])==f['split'],'cross_split_source_group')
        if direct:image,size,pixel=source_image(f['image'],None if _verified_frames is None else _verified_frames[index])
        else:
            image=h.checked(h.ROOT,f['image']);size=h.image(h.ROOT,f['image'])
            pixel=h.pixel_digest(h.ROOT,f['image'])
        h.require(pixels.setdefault(pixel,f['split'])==f['split'],'cross_split_pixel_duplicate')
        ann=h.read(h.checked(h.ROOT,f['annotation']))
        h.require(ann.get('version')=='fullscreen-focus-annotation-v1' and
            ann.get('image')==f['image'] and ann.get('completeFocus') is True and
            ann.get('profile')=='ordinary','incomplete_or_assisted_annotations')
        controls=ann['controls'];h.require(len({c['id'] for c in controls})==len(controls),'duplicate_control')
        labels=[]
        for c in controls:
            h.require(c['state'] in ('focused','unfocused'),'unknown_focus')
            from compare_annotation_proposals import validate_boxes
            validate_boxes([c['bounds']],*size)
            if c['state']=='focused':
                x,y,w,v=c['bounds'];labels.append(f'0 {(x+w/2)/size[0]:.9f} {(y+v/2)/size[1]:.9f} {w/size[0]:.9f} {v/size[1]:.9f}')
        total_bytes+=image.stat().st_size
        prepared.append(dict(id=f['id'],split=f['split'],image=f['image'],labels=labels,
                             annotation=f['annotation'],pixelSHA256=pixel))
        if direct:prepared[-1].update(size=list(size),absoluteImage=str(image))
    h.require(set(groups.values())==set(splits),'both_splits_required')
    for split in splits:
        h.require(any(f['labels'] for f in prepared if f['split']==split),'positive_focus_required_per_split')
    h.require((0 if direct else total_bytes)+64*1024*1024<budget['bytes'],'insufficient_output_budget_for_staging')
    return doc,dict(contract=h.ref(h.local(path)),checkpoint=h.ref(checkpoint),admission=doc['admission'],
                    runtime=runtime_identity(),sources=[h.ref(Path(__file__).resolve()),
                        h.ref(h.ROOT/'scripts/train_tvos_model.py'),h.ref(h.ROOT/'scripts/fullscreen_readthrough.py')],
                    frames=prepared,stagingBytes=0 if direct else total_bytes,groups=groups)


def output_bytes(root):
    files=list(root.rglob('*'))
    h.require(not any(p.is_symlink() for p in files),'unexpected_output_link')
    return sum(p.stat().st_size for p in files if p.is_file())


def supervise(command, out, seconds, byte_limit, env=None):
    """Own child group only; terminal receipts distinguish stops from completed runs."""
    start=time.monotonic();reason='completed';peak=output_bytes(out);scan_error=None
    with (out/'child.log').open('x') as log:
        proc=subprocess.Popen(command,cwd=h.ROOT,stdout=log,stderr=subprocess.STDOUT,
                              env=env,start_new_session=True)
        try:
            while proc.poll() is None:
                peak=max(peak,output_bytes(out))
                if seconds is not None and time.monotonic()-start>=seconds:reason='wall_time_limit';break
                if peak>=byte_limit:reason='output_limit';break
                time.sleep(.05)
        except BaseException:
            reason='supervisor_error';raise
        finally:
            if proc.poll() is None:
                try:os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    try:os.killpg(proc.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    proc.wait(timeout=2)
            try:peak=max(peak,output_bytes(out))
            except (OSError,ValueError) as error:
                reason='supervisor_error';scan_error=str(error)
            if reason=='completed' and seconds is not None and time.monotonic()-start>=seconds:reason='wall_time_limit'
            if reason=='completed' and peak>=byte_limit:reason='output_limit'
            if reason=='completed' and proc.returncode!=0:reason='child_failed'
            receipt=dict(pid=proc.pid,exitCode=proc.returncode,outcome=reason,
                wallSeconds=time.monotonic()-start,peakObservedBytes=peak,
                timeBudgetSeconds=seconds,outputBudgetBytes=byte_limit,
                outputOvershootBytes=max(0,peak-byte_limit),command=command,
                scanError=scan_error,
                interpretation='Monitored limits, not a hard disk quota; stopped runs are partial.')
            h.write(out/'receipt.json',receipt)
    return receipt


def stage(doc, checked, out):
    if doc['version']=='fullscreen-focus-run-v2':
        h.write(out/'validated.json',checked);h.write(out/'configuration.json',doc)
        return
    for split in ('train','development'):
        for kind in ('images','labels'):(out/'dataset'/split/kind).mkdir(parents=True)
    for i,f in enumerate(checked['frames']):
        source=h.checked(h.ROOT,f['image']);dest=out/'dataset'/f['split']/'images'/f'{i:06d}.png'
        shutil.copyfile(source,dest);h.require(h.sha(dest)==f['image']['sha256'],'staging_copy_changed')
        (out/'dataset'/f['split']/'labels'/f'{i:06d}.txt').write_text('\n'.join(f['labels'])+'\n')
    # JSON is a YAML subset; no untrusted dataset download/script fields are copied.
    h.write(out/'dataset.yaml',dataset_configuration(out))
    h.write(out/'validated.json',checked)
    h.write(out/'configuration.json',doc)


def dataset_configuration(out):
    return dict(path=str(out/'dataset'),train='train/images',val='development/images',names=['focusedControl'])


def child(out):
    h.require(os.environ.get('NUIAK_SUPERVISOR_PID')==str(os.getppid()),'supervised_child_required')
    doc=h.read(out/'configuration.json');checked=h.read(out/'validated.json')
    direct=doc['version']=='fullscreen-focus-run-v2'
    if direct:h.require(os.environ.get('NUIAK_VALIDATED_SHA256')==h.sha(out/'validated.json'),'changed_parent_validation')
    fresh_doc,fresh_checked=validate(h.checked(h.ROOT,checked['contract']),
        _verified_frames=checked['frames'] if direct else None)
    h.require(fresh_doc==doc and fresh_checked==checked,'inputs_changed_after_staging')
    if doc['version']=='fullscreen-focus-run-v2':
        from fullscreen_readthrough import train_terminal
        return train_terminal(doc,checked,out)
    h.require(h.read(out/'dataset.yaml')==dataset_configuration(out),'staged_dataset_configuration_changed')
    for i,f in enumerate(checked['frames']):
        image=out/'dataset'/f['split']/'images'/f'{i:06d}.png'
        label=out/'dataset'/f['split']/'labels'/f'{i:06d}.txt'
        h.require(h.sha(image)==f['image']['sha256'] and
                  label.read_text()=='\n'.join(f['labels'])+'\n','staged_inputs_changed')
    # Set offline behavior before importing the resident training stack.
    os.environ.update(YOLO_OFFLINE='true',YOLO_AUTOINSTALL='false',PYTHONDONTWRITEBYTECODE='1')
    def offline(event, args):
        if event in ('socket.connect','socket.getaddrinfo'):
            raise RuntimeError('network_disabled_for_local_training')
    sys.addaudithook(offline)
    from train_tvos_model import training_options
    from ultralytics import YOLO
    checkpoint=h.checked(h.ROOT,checked['checkpoint'],128*1024*1024)
    model=YOLO(str(checkpoint))
    args=SimpleNamespace(dry_run=False,epochs=doc['epochs'],batch=doc['batch'],imgsz=doc['imgsz'],
        patience=doc['epochs'],workers=0,output_dir=str(out),name='model')
    kwargs=training_options(args,out/'dataset.yaml')
    kwargs.update(exist_ok=False,workers=0,plots=False,save_period=-1,cache=False,
                  mosaic=0.,mixup=0.,copy_paste=0.,flipud=0.,fliplr=0.,seed=doc['seed'],
                  hsv_h=0.,hsv_s=0.,hsv_v=0.,scale=0.,translate=0.,degrees=0.,shear=0.,perspective=0.,
                  deterministic=True,amp=False,resume=False)
    model.train(**kwargs)


def execute(path, output):
    doc,checked=validate(path)
    out=h.fresh(output)
    h.require(shutil.disk_usage(h.ROOT).free>doc['budget']['bytes']+5*1024**3,'disk_reserve')
    out.mkdir(parents=True);stage(doc,checked,out)
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','YOLO_OFFLINE':'true','YOLO_AUTOINSTALL':'false',
         'NUIAK_SUPERVISOR_PID':str(os.getpid())}
    if doc['version']=='fullscreen-focus-run-v2':env['NUIAK_VALIDATED_SHA256']=h.sha(out/'validated.json')
    for key in ('TMPDIR','YOLO_CONFIG_DIR','MPLCONFIGDIR','TORCH_HOME'):
        target=out/'cache'/key.lower();target.mkdir(parents=True,exist_ok=True);env[key]=str(target)
    receipt=supervise([sys.executable,str(Path(__file__).resolve()),'--child',str(out)],out,
                      doc['budget']['seconds'],doc['budget']['bytes'],env)
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--contract');p.add_argument('--output')
    p.add_argument('--execute',action='store_true');p.add_argument('--child',help=argparse.SUPPRESS)
    p.add_argument('--check-inputs',action='store_true',help='Read-only qualification, not admission or execution')
    a=p.parse_args()
    if a.child:child(h.local(a.child))
    elif not a.contract:p.error('--contract is required')
    elif a.execute:
        if a.check_inputs:p.error('--check-inputs cannot execute')
        if not a.output:p.error('--execute requires --output')
        r=execute(a.contract,a.output);print(json.dumps(r));sys.exit(0 if r['outcome']=='completed' else 2)
    else:
        _,checked=validate(a.contract,inputs_only=a.check_inputs)
        print(json.dumps(dict(valid=True,mode='input-check-only' if a.check_inputs else 'validation-only',
            frames=len(checked['frames']),groups=checked['groups'],stagingBytes=checked['stagingBytes'])))
