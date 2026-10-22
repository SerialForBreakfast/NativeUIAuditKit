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
    sources={k:refs[k] for k in ('membership','initialization')}
    if proof.get('scopeVersion') == 'training-subset-parity-v1':
        q.require(proof['sources']['initialization']==sources['initialization'], 'restore_configuration_not_qualified')
    else:
        q.require(proof['sources']==sources,'restore_configuration_not_qualified')
    q.require(spec['training']['initialization']==refs['initialization'] and
              refs['membership'] in spec['training']['membership'],'restore_training_binding')
    q.require(spec['training']['epochs']==30 and spec['limits']['timeoutSeconds']<=800,'restore_limits')
    return refs


def validate_contract(checkpoint, qualified, subset=False):
    actual=checkpoint.get('resumeContract'); tested=qualified.get('resumeContract')
    q.require(isinstance(actual,dict) and isinstance(tested,dict),'restore_contract_not_qualified')
    if subset:
        q.require({k:v for k,v in actual.items() if k!='rows'} ==
                  {k:v for k,v in tested.items() if k!='rows'},'restore_contract_not_qualified')
        q.require(tested['rows'] and all(row in actual['rows'] for row in tested['rows']),
                  'restore_qualification_not_training_subset')
    else:
        q.require(actual==tested,'restore_contract_not_qualified')
    return actual.get('repeat',1)


def run():
    spec=q.load(OUT.parents[2]/'spec.json');refs=validate_inputs(spec)
    import torch
    checkpoint=torch.load(checked(refs['checkpoint']),map_location='cpu',weights_only=False)
    proof=q.load(checked(refs['qualification']))
    qualified=torch.load(checked(proof['checkpoint']),map_location='cpu',weights_only=False)
    repeat=validate_contract(checkpoint,qualified,proof.get('scopeVersion')=='training-subset-parity-v1')
    from train_focus_ring_detector import train_native_hcf
    rows=q.load(checked(refs['membership']))['rows']
    for row in rows:q.require(q.digest(Path(row['path']))==row['sha256'],'restore_crop_changed')
    result=train_native_hcf(rows,checked(refs['initialization']),OUT,seed=371,profile='balanced',
        selection='fixed-last',deduplicate=True,resume=checked(refs['checkpoint']),repeat=repeat)
    q.save(OUT/'fit.json',dict(result,modelAccepted=False))
