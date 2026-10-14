"""Run the 2 approved HCF candidates through the resident training code."""
import os
from pathlib import Path
import shutil
import research_queue as q
import hcf_study371 as study

OUT = None


def crop():
    study.OUT=OUT
    cfg=q.load(OUT/'config.json')
    document,=study.dependency('crops.json')
    rows=document['rows']
    q.require({r['role'] for r in rows} == {'train','development'},'training_roles')
    groups={}
    for row in rows:
        q.require(groups.setdefault(row['group'],row['role'])==row['role'],'training_group_leak')
        q.require(q.digest(Path(row['path']))==row['sha256'],'training_crop_changed')
    reference=cfg['initialization'];path=q.ROOT/reference['path']
    q.require(q.digest(path)==reference['sha256'],'training_initialization_changed')
    from train_focus_ring_detector import train_native_hcf
    result=train_native_hcf(rows,path,OUT,progress=study.progress)
    q.save(OUT/'fit.json',dict(**result,modelAccepted=False,profile='hcf',selection='lowest-development-bce-earliest-tie',
        membershipSHA256=q.text_digest(rows),initialization=reference))
    q.save(OUT/'model.json',dict(path=str(OUT/'best.pt'),sha256=q.digest(OUT/'best.pt'),kind='crop'))


def detector():
    study.OUT=OUT
    cfg=q.load(OUT/'config.json');document,=study.dependency('admission.json')
    root=study.verify_storage(document['storage'])
    dataset=root/'yolo-training';q.require(not dataset.exists(),'detector_dataset_exists');dataset.mkdir()
    rows=[r for r in document['rows'] if r['role'] in ('train','development') and r['profile']=='hcf']
    q.require({r['role'] for r in rows}=={'train','development'},'detector_training_roles')
    for role in ('train','development'):
        (dataset/'images'/role).mkdir(parents=True)
        (dataset/'labels'/role).mkdir(parents=True)
    for row in rows:
        source=Path(row['path']);q.require(q.digest(source)==row['sha256'],'detector_image_changed')
        target=dataset/'images'/row['role']/(row['id']+'.png')
        # Same-volume hard links keep one immutable image payload.
        os.link(source,target)
        x,y,w,h=row['boxes'][row['focus']];width,height=row['width'],row['height']
        label=f'0 {(x+w/2)/width:.9f} {(y+h/2)/height:.9f} {w/width:.9f} {h/height:.9f}\n'
        with (dataset/'labels'/row['role']/(row['id']+'.txt')).open('x') as stream:stream.write(label)
    import yaml
    configuration=dict(path=str(dataset),train='images/train',val='images/development',names={0:'focused_control'})
    with (dataset/'dataset.yaml').open('x') as stream:yaml.safe_dump(configuration,stream)
    ref=cfg['initialization'];initialization=q.ROOT/ref['path']
    q.require(q.digest(initialization)==ref['sha256'],'detector_initialization_changed')
    from train_yolo import train_native_hcf
    best=train_native_hcf(dataset/'dataset.yaml',initialization,OUT,study.progress)
    q.require(best.is_file(),'detector_checkpoint_missing')
    q.save(OUT/'model.json',dict(path=str(best),sha256=q.digest(best),kind='detector'))
    q.save(OUT/'fit.json',dict(modelAccepted=False,frames=len(rows),epochsMaximum=30,patience=10,
        membershipSHA256=q.text_digest(rows),initialization=ref,selection='resident-yolo-development-fitness',
        resumeStateSaved=True,resumeQualified=False))
