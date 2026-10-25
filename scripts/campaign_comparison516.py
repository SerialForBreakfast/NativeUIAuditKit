"""Preserve completed captures while reporting a changed execution runtime explicitly."""
import research_queue as q
import ttr_campaign_queue493 as campaign
OUT=None

def run():
    campaign.OUT=OUT
    campaign.compare()
    result=q.load(OUT/'comparison.json')
    spec=q.load(OUT.parents[2]/'spec.json')
    change=spec['runtimeChange']
    q.require(change['oldHelperSHA256']!=change['newHelperSHA256'],'campaign516_runtime_change')
    result.update(outcome='inconclusive' if result['matchedLabels'] else 'contradicted',runtimeChange=change,timingCausalClaim=False,
                  nextAction='Review label parity and cleanup. Do not attribute elapsed-time differences to session reuse across runtime changes.')
    result['limitation']+=' Execution helper changed after the retained first arm. No repeated capture is authorized to remove this confound.'
    q.save(OUT/'comparison.json',result,replace=True)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='comparison.json',sha256=q.digest(OUT/'comparison.json'))]),replace=True)
