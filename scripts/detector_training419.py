"""Restart-only detector training using pinned membership and the resident YOLO trainer.

This adapter does not qualify checkpoint restoration or change shipped models.
"""
import csv
import os
import shutil
from pathlib import Path
import research_queue as q
from template_inputs398 import checked, pin
from template_adapters395 import document, resolve_inputs
from detector_native_inputs import bounds

OUT = None
VERSION = 'detector-training-membership-v1'
TRAIN_ONLY_VERSION = 'detector-training-membership-v2'


def learning_rate(config, initialization):
    base=dict(initialization=initialization,selection='fixed-last',patience=0)
    q.require(set(base) <= set(config) <= set(base)|{'learningRate','checkpointRetention','freezeBackbone','warmupBiasRate'} and
              all(config[k]==v for k,v in base.items()),'detector_training_configuration')
    q.require(config.get('checkpointRetention','all') in ('all','last-best-final'), 'detector_checkpoint_retention')
    q.require(type(config.get('freezeBackbone',False)) is bool, 'detector_freeze_backbone_boolean')
    value=config.get('learningRate',.001)
    q.require(type(value) in (int,float) and value in (.001,.0001),'detector_training_learning_rate')
    if 'warmupBiasRate' in config:
        q.require(type(config['warmupBiasRate']) in (int,float) and config['warmupBiasRate']==value,'detector_warmup_bias_rate')
    return value


def prepare(data, output):
    from PIL import Image
    train_only=data.get('version') == TRAIN_ONLY_VERSION
    q.require(data.get('version') in (VERSION,TRAIN_ONLY_VERSION) and data.get('trainingAdmitted') is True, 'detector_training_admission')
    if train_only:
        q.require(data.get('calibrationPolicy')=='none-fixed-last-training-diagnostics', 'detector_training_calibration_policy')
    names = data['names']
    q.require(isinstance(names, list) and names and len(names)==len(set(names))
              and all(isinstance(n,str) and n for n in names), 'detector_training_names')
    rows=data['rows']
    q.require(rows and {r['role'] for r in rows} == ({'train'} if train_only else {'train','calibration'}), 'detector_training_roles')
    groups, pixels, ids = {}, {}, set()
    verified=[]
    for row in rows:
        q.require(row.get('trainingEligible') is (row['role']=='train'), 'detector_training_eligibility')
        q.require(q.ID.fullmatch(row['id']) and row['id'] not in ids, 'detector_training_id')
        ids.add(row['id'])
        q.require(groups.setdefault(row['group'],row['role']) == row['role'], 'detector_training_group_leak')
        image=checked(row['image'])
        signature=(row['role'],row['group'],row['controls'])
        q.require(pixels.setdefault(row['image']['sha256'],signature)==signature, 'detector_training_pixel_conflict')
        with Image.open(image) as im:
            q.require(im.size==(row['width'],row['height']), 'detector_training_dimensions')
        q.require(row.get('labelsComplete') is True, 'detector_training_incomplete_labels')
        labels=[]
        for control in row['controls']:
            q.require(control['class'] in names, 'detector_training_class')
            x,y,w,h=bounds(control['bounds'],row['width'],row['height'])
            labels.append(f"{names.index(control['class'])} {(x+w/2)/row['width']:.9f} {(y+h/2)/row['height']:.9f} {w/row['width']:.9f} {h/row['height']:.9f}\n")
        verified.append((row,image,labels))
    # Validate every input before writing any dataset file.
    dataset=output/'dataset'
    q.require(not dataset.exists(), 'detector_training_dataset_exists')
    seen=set()
    counts={'train':0,'calibration':0}
    for row,image,labels in verified:
        sha=row['image']['sha256']
        if sha in seen: continue
        seen.add(sha)
        role=row['role']; counts[role]+=1
        images=dataset/'images'/role; images.mkdir(parents=True,exist_ok=True)
        targets=dataset/'labels'/role; targets.mkdir(parents=True,exist_ok=True)
        os.link(image,images/(row['id']+image.suffix))
        (targets/(row['id']+'.txt')).write_text(''.join(labels))
    import yaml
    path=dataset/'dataset.yaml'
    # The resident trainer computes validation metrics even for fixed-last runs.
    # In v2 these are explicitly training diagnostics, never held-out accuracy.
    path.write_text(yaml.safe_dump(dict(path=str(dataset),train='images/train',
        val='images/train' if train_only else 'images/calibration',names=dict(enumerate(names)))))
    return path, counts


def run():
    cfg=q.load(OUT.parents[2]/'spec.json')['template']
    refs=resolve_inputs(cfg,OUT)
    config=document(refs['configuration'])
    rate=learning_rate(config,refs['initialization'])
    initialization=checked(refs['initialization'])
    membership=document(refs['membership'])
    dataset,counts=prepare(membership,OUT)
    from train_yolo import train_native_hcf
    import hcf_study371 as study
    study.OUT=OUT
    options=dict(weights='last',patience=0)
    if 'learningRate' in config:options['learning_rate']=rate
    if 'warmupBiasRate' in config:options['warmup_bias_lr']=config['warmupBiasRate']
    if config.get('freezeBackbone'):options['freeze_backbone']=True
    if config.get('checkpointRetention') == 'last-best-final':
        import detector_retention478 as retention
        from ultralytics.utils.callbacks import default_callbacks
        callbacks=default_callbacks['on_pretrain_routine_end']
        retention.OUT=OUT
        callbacks.append(retention.apply_retention)
        try:
            model=train_native_hcf(dataset,initialization,OUT,study.progress,**options)
        finally:
            callbacks.remove(retention.apply_retention)
    else:
        model=train_native_hcf(dataset,initialization,OUT,study.progress,**options)
    with (OUT/'detector/results.csv').open() as stream:
        rows=[{k.strip():v for k,v in row.items()} for row in csv.DictReader(stream)]
    history=[dict(epoch=int(r['epoch']),trainLoss=sum(float(r[k]) for k in ('train/box_loss','train/cls_loss','train/dfl_loss'))) for r in rows]
    q.require([r['epoch'] for r in history]==list(range(1,31)), 'detector_training_incomplete')
    if 'warmupBiasRate' in config:
        import yaml
        args=yaml.safe_load((OUT/'detector/args.yaml').read_text())
        q.require(args['warmup_bias_lr']==config['warmupBiasRate'] and args['lr0']==rate,'detector_effective_rate_changed')
        rates=[float(v) for row in rows for k,v in row.items() if k.startswith('lr/')]
        q.require(rates and all(0<=v<=rate*1.0001 for v in rates),'detector_effective_rate_exceeded')
        q.save(OUT/'effective-rates.json',dict(lr0=rate,warmupBiasRate=config['warmupBiasRate'],maximumLoggedRate=max(rates),samples=len(rates)))
    q.require(model.is_file(), 'detector_training_checkpoint_missing')
    shutil.copyfile(model,OUT/'final.pt')
    q.save(OUT/'history.json',history)
    q.save(OUT/'fit.json',dict(epochs=30,initialization=refs['initialization'],membership=refs['membership'],
        frames=counts,selection='fixed-last',learningRate=rate,warmupBiasRate=config.get('warmupBiasRate'),freezeBackbone=config.get('freezeBackbone',False),resumeQualified=False,modelAccepted=False,
        validationMetricRole='training-diagnostic' if membership['version']==TRAIN_ONLY_VERSION else 'calibration',
        calibrationUsedForSelection=False))
    q.save(OUT/'benchmark_summary.json',dict(epochs=30,frames=counts,modelAccepted=False,
        validationMetricRole='training-diagnostic' if membership['version']==TRAIN_ONLY_VERSION else 'calibration',
        decision='Score the candidate on retained evaluation groups. Training completion is not acceptance.'))


def checkpoint_review():
    """Read only a named, hash-verified local checkpoint. Never resume from state presence alone."""
    cfg=q.load(OUT.parents[2]/'spec.json')['template']
    refs=resolve_inputs(cfg,OUT)
    import torch
    from hcf_resume_review import assess
    state=torch.load(checked(refs['checkpoint']),map_location='cpu',weights_only=False)
    result=assess(state)
    result.update(checkpoint=refs['checkpoint'],modelAccepted=False,
                  limitation='State presence does not establish resumed versus uninterrupted parity.')
    q.save(OUT/'benchmark_summary.json',result)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
