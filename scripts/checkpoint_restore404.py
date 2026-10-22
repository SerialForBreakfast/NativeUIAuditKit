"""Restore only the qualified fixed-last crop configuration. Preserve all inputs.

RECOVERY488: `resumeStopEpoch` stops a continuation chunk at an epoch boundary. A later chunk can take its checkpoint
from a declared dependency output. Both uses require a passed 2-step chain parity proof.
"""
from pathlib import Path
import research_queue as q
from template_inputs398 import checked

OUT=None


CHAIN='training-subset-chain-parity-v1'


def chained(spec):
    """True when this chunk stops early or resumes from another chunk's output."""
    return 'resumeStopEpoch' in spec or 'job' in spec.get('resumeInputs',{}).get('checkpoint',{})


def validate_inputs(spec):
    refs=spec.get('resumeInputs',{})
    q.require(set(refs)=={'checkpoint','qualification','membership','initialization'},'restore_inputs')
    for key,ref in refs.items():
        if key=='checkpoint' and isinstance(ref,dict) and 'job' in ref:
            # The queue resolves and hash-checks dependency outputs before the run.
            q.require(set(ref)=={'job','output'} and ref['output']=='last.pt' and
                      any(d['job']==ref['job'] and 'last.pt' in d['outputs'] for d in spec.get('dependencies',[])),
                      'restore_checkpoint_dependency')
            continue
        q.require(ref in spec['inputs'],'restore_input_not_pinned')
        checked(ref)
    stop=spec.get('resumeStopEpoch')
    q.require(stop is None or (type(stop) is int and 1<=stop<30),'restore_stop_epoch')
    proof=q.load(checked(refs['qualification']))
    q.require(proof.get('version')=='hcf-crop-restoration-v1' and proof.get('passed') is True,'restore_unqualified')
    q.require(not chained(spec) or proof.get('scopeVersion')==CHAIN,'restore_chain_unqualified')
    sources={k:refs[k] for k in ('membership','initialization')}
    if proof.get('scopeVersion') in ('training-subset-parity-v1', CHAIN):
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


def checkpoint_path(ref):
    """Return a pinned checkpoint, or a dependency output that the queue already verified."""
    if 'job' not in ref:
        return checked(ref)
    resolved=q.load(OUT/'dependencies.json')
    match=[o for d in resolved if d['job']==ref['job'] for o in d['outputs'] if o['path'].endswith('/out/'+ref['output'])]
    q.require(len(match)==1,'restore_checkpoint_dependency')
    path=q.local_path(q.ROOT,match[0]['path'])
    q.require(path.is_file() and q.digest(path)==match[0]['sha256'],'restore_checkpoint_changed')
    return path


def run():
    spec=q.load(OUT.parents[2]/'spec.json');refs=validate_inputs(spec)
    import torch
    checkpoint=torch.load(checkpoint_path(refs['checkpoint']),map_location='cpu',weights_only=False)
    proof=q.load(checked(refs['qualification']))
    qualified=torch.load(checked(proof['checkpoint']),map_location='cpu',weights_only=False)
    repeat=validate_contract(checkpoint,qualified,proof.get('scopeVersion') in ('training-subset-parity-v1',CHAIN))
    stop=spec.get('resumeStopEpoch')
    q.require(stop is None or checkpoint.get('epoch',30)<stop,'restore_stop_before_checkpoint')
    from train_focus_ring_detector import train_native_hcf
    rows=q.load(checked(refs['membership']))['rows']
    for row in rows:q.require(q.digest(Path(row['path']))==row['sha256'],'restore_crop_changed')
    result=train_native_hcf(rows,checked(refs['initialization']),OUT,seed=371,profile='balanced',
        selection='fixed-last',deduplicate=True,resume=checkpoint_path(refs['checkpoint']),repeat=repeat,
        stop_after_epoch=stop)
    q.save(OUT/'fit.json',dict(result,modelAccepted=False))
