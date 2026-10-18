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


def prepare(data, output):
    from PIL import Image
    q.require(data.get('version') == VERSION and data.get('trainingAdmitted') is True, 'detector_training_admission')
    names = data['names']
    q.require(isinstance(names, list) and names and len(names)==len(set(names))
              and all(isinstance(n,str) and n for n in names), 'detector_training_names')
    rows=data['rows']
    q.require(rows and {r['role'] for r in rows} == {'train','calibration'}, 'detector_training_roles')
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
    path.write_text(yaml.safe_dump(dict(path=str(dataset),train='images/train',val='images/calibration',names=dict(enumerate(names)))))
    return path, counts


def run():
    cfg=q.load(OUT.parents[2]/'spec.json')['template']
    refs=resolve_inputs(cfg,OUT)
    config=document(refs['configuration'])
    q.require(config==dict(initialization=refs['initialization'],selection='fixed-last',patience=0), 'detector_training_configuration')
    initialization=checked(refs['initialization'])
    dataset,counts=prepare(document(refs['membership']),OUT)
    from train_yolo import train_native_hcf
    import hcf_study371 as study
    study.OUT=OUT
    model=train_native_hcf(dataset,initialization,OUT,study.progress,weights='last',patience=0)
    with (OUT/'detector/results.csv').open() as stream:
        rows=[{k.strip():v for k,v in row.items()} for row in csv.DictReader(stream)]
    history=[dict(epoch=int(r['epoch']),trainLoss=sum(float(r[k]) for k in ('train/box_loss','train/cls_loss','train/dfl_loss'))) for r in rows]
    q.require([r['epoch'] for r in history]==list(range(1,31)), 'detector_training_incomplete')
    q.require(model.is_file(), 'detector_training_checkpoint_missing')
    shutil.copyfile(model,OUT/'final.pt')
    q.save(OUT/'history.json',history)
    q.save(OUT/'fit.json',dict(epochs=30,initialization=refs['initialization'],membership=refs['membership'],
        frames=counts,selection='fixed-last',resumeQualified=False,modelAccepted=False))
    q.save(OUT/'benchmark_summary.json',dict(epochs=30,frames=counts,modelAccepted=False,
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
