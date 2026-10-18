"""Isolate profile coverage and repeated crop weighting through the resident trainer."""
from pathlib import Path
import research_queue as q
import hcf_study371 as study

OUT=None


def validate_config(cfg):
    q.require(cfg.get('profile') in ('hcf','balanced'),'profile_invalid')
    q.require(type(cfg.get('deduplicate')) is bool,'deduplicate_invalid')
    q.require(type(cfg.get('seed')) is int and cfg['seed'] in (371,372,373),'seed_changed')
    # ACTIONS417: optional exposure control after deduplication. Absent means 1, the original sampling.
    q.require(type(cfg.get('repeat',1)) is int and 1<=cfg.get('repeat',1)<=16,'repeat_invalid')
    return cfg


def train():
    cfg=validate_config(q.load(OUT/'config.json'));study.OUT=OUT
    document,=study.dependency('crops.json');rows=document['rows'];groups={}
    q.require({r['role'] for r in rows}=={'train','development'},'training_roles')
    for row in rows:
        q.require(groups.setdefault(row['group'],row['role'])==row['role'],'group_leak')
        q.require(q.digest(Path(row['path']))==row['sha256'],'crop_changed')
    ref=cfg['initialization'];initial=q.ROOT/ref['path']
    q.require(q.digest(initial)==ref['sha256'],'initialization_changed')
    from train_focus_ring_detector import train_native_hcf
    result=train_native_hcf(rows,initial,OUT,epochs=30,batch=16,seed=cfg['seed'],progress=study.progress,
                           profile=cfg['profile'],deduplicate=cfg['deduplicate'],selection='fixed-last',
                           repeat=cfg.get('repeat',1))
    q.save(OUT/'fit.json',dict(**result,modelAccepted=False,profile=cfg['profile'],
        membershipSHA256=q.text_digest(rows),initialization=ref,configuration=cfg,
        limitation='Equal epochs do not imply equal update counts after duplicate removal.'))
    q.save(OUT/'model.json',dict(path=str(OUT/'final.pt'),sha256=q.digest(OUT/'final.pt'),kind='crop'))
