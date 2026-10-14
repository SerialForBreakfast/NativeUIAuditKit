"""Register fixed FOCUS342 comparisons using measured training-only evidence."""
from pathlib import Path
import research_queue as q
from research_campaign340 import pin


def main():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS342';folder.mkdir(exist_ok=True)
    source=q.ROOT/'reports/work/FOCUS-341';audit=q.ROOT/'reports/work/FOCUS-342/audit.json'
    decision=q.load(audit)
    q.require(decision['balancedJustified'] and decision['preservationJustified'],'candidate_not_justified')
    membership=[pin(q.ROOT/p) for p in ['reports/work/TRANSITION-249/artifacts/package/membership.json',
        'reports/work/FOCUS-326/corpus.json','reports/work/FOCUS-319/corpus.json',
        'reports/work/FOCUS-341/negatives.json']]
    for name,weight in [('balanced',0.),('balanced-preservation',1.)]:
        id='focus342-'+name;q.require(not (q.QUEUE/'jobs'/id).exists(),'existing_job')
        config=folder/(id+'-config.json')
        q.save(config,dict(arms=['added-detail-and-content'],balance342=True,preservationWeight=weight))
        inputs=membership+[pin(q.ROOT/p) for p in ['scripts/additive341.py','scripts/balance342.py',
            'scripts/native_adapt152.py','scripts/edge329.py','scripts/regions331.py','scripts/regions313.py',
            'scripts/detail307.py','scripts/filters327.py','reports/work/FOCUS-329/run/last.pt',
            'reports/work/FOCUS-341/audit.json','reports/work/FOCUS-342/audit.json']]
        spec=dict(version=q.SPEC_VERSION,id=id,task='FOCUS342',owner='research-host-NUIAK',kind='confirm',authority='training',
            hypothesis='Rotate old negatives at the same update budget; test training-only margin preservation: '+name,
            decisionRule='Use fixed last weights and thresholds 0.15/0.85. Require target gains without lost previous successes.',
            adapter=dict(type='python-callable',steps=['balance342.run'],outputAttributes=['balance342.OUT']),
            inputs=inputs,stage=[dict(**{'from':pin(path)},to=target) for path,target in
                [(config,'config.json'),(source/'audit.json','audit.json'),(source/'negatives.json','negatives.json'),
                 (audit,'balance-audit.json')]],limits=dict(timeoutSeconds=1800,maxOutputBytes=2*1024**3,maxAttempts=1),
            training=dict(experimentLogRunId='FOCUS342',membership=membership,
                initialization=pin(q.ROOT/'reports/work/FOCUS-329/run/last.pt'),epochs=30,
                storageBudgetBytes=2*1024**3,acceptanceEvidence='Retained regressions, original crop hashes, frozen branches, and reload parity.',resume='restart'))
        path=folder/(id+'.json');q.save(path,spec);print(q.submit(path))


if __name__=='__main__':main()
