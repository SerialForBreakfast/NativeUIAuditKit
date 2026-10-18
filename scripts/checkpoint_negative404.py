"""Exercise actual restore rejection paths. Never edit original checkpoints."""
from pathlib import Path
import research_queue as q
from template_adapters395 import resolve_inputs, document
from template_inputs398 import checked

OUT=None


def run():
    import torch
    from train_focus_ring_detector import train_native_hcf
    cfg=q.load(OUT.parents[2]/'spec.json')['template']
    refs=resolve_inputs(cfg,OUT);proof=document(refs['qualification'])
    q.require(proof['passed'] is True,'positive_restore_missing')
    original=checked(proof['checkpoint']);before=q.digest(original)
    source=proof['sources'];rows=document(source['membership'])['rows'];initial=checked(source['initialization'])
    altered=torch.load(original,map_location='cpu',weights_only=False);altered.pop('optimizer')
    missing=OUT/'missing-optimizer.pt';torch.save(altered,missing)
    outcomes=[]
    for name,checkpoint,seed,membership,expected in (
        ('missing-optimizer',missing,371,rows,'hcf_resume_state_missing'),
        ('changed-seed',original,372,rows,'hcf_resume_contract_changed'),
        ('changed-order',original,371,list(reversed(rows)),'hcf_resume_contract_changed')):
        out=OUT/name;out.mkdir()
        try:
            train_native_hcf(membership,initial,out,seed=seed,profile='balanced',selection='fixed-last',
                deduplicate=True,resume=checkpoint,stop_after_epoch=13)
        except ValueError as error:
            q.require(str(error)==expected,'unexpected_restore_rejection:'+str(error))
            q.require(not (out/'last.pt').exists(),'rejection_wrote_checkpoint')
            outcomes.append(dict(case=name,rejected=True,reason=str(error)))
        else:raise ValueError('invalid_restore_accepted:'+name)
    q.require(q.digest(original)==before,'original_checkpoint_changed')
    q.save(OUT/'negative-results.json',dict(cases=outcomes,originalPreserved=True,modelAccepted=False))
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path='negative-results.json',sha256=q.digest(OUT/'negative-results.json'))]))
