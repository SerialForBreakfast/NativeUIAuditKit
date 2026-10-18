"""Restore only the qualified fixed-last crop configuration. Preserve all inputs."""
from pathlib import Path
import research_queue as q
from template_inputs398 import checked

OUT=None


def validate_inputs(spec):
    refs=spec.get('resumeInputs',{})
    q.require(set(refs)=={'checkpoint','qualification','membership','initialization'},'restore_inputs')
    for ref in refs.values():
        q.require(ref in spec['inputs'],'restore_input_not_pinned')
        checked(ref)
    proof=q.load(checked(refs['qualification']))
    q.require(proof.get('version')=='hcf-crop-restoration-v1' and proof.get('passed') is True,'restore_unqualified')
    q.require(proof['sources']=={k:refs[k] for k in ('membership','initialization')},'restore_configuration_not_qualified')
    q.require(spec['training']['initialization']==refs['initialization'] and
              refs['membership'] in spec['training']['membership'],'restore_training_binding')
    q.require(spec['training']['epochs']==30 and spec['limits']['timeoutSeconds']<=800,'restore_limits')
    return refs


def run():
    spec=q.load(OUT.parents[2]/'spec.json');refs=validate_inputs(spec)
    import torch
    checkpoint=torch.load(checked(refs['checkpoint']),map_location='cpu',weights_only=False)
    proof=q.load(checked(refs['qualification']))
    qualified=torch.load(checked(proof['checkpoint']),map_location='cpu',weights_only=False)
    q.require(checkpoint.get('resumeContract')==qualified.get('resumeContract') and
              checkpoint.get('resumeContract') is not None,'restore_contract_not_qualified')
    from train_focus_ring_detector import train_native_hcf
    rows=q.load(checked(refs['membership']))['rows']
    for row in rows:q.require(q.digest(Path(row['path']))==row['sha256'],'restore_crop_changed')
    result=train_native_hcf(rows,checked(refs['initialization']),OUT,seed=371,profile='balanced',
        selection='fixed-last',deduplicate=True,resume=checked(refs['checkpoint']))
    q.save(OUT/'fit.json',dict(result,modelAccepted=False))
