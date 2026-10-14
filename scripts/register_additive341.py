"""Register the 2 approved comparisons without changing earlier specifications."""
from pathlib import Path
import research_queue as q
from research_campaign340 import pin


def main():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS341';folder.mkdir(exist_ok=True)
    source=q.ROOT/'reports/work/FOCUS-341'
    membership=[pin(q.ROOT/p) for p in ['reports/work/TRANSITION-249/artifacts/package/membership.json',
        'reports/work/FOCUS-326/corpus.json','reports/work/FOCUS-319/corpus.json',
        'reports/work/FOCUS-341/negatives.json']]
    for arm in ('added-detail','added-detail-and-content'):
        name='focus341-'+arm
        q.require(not (q.QUEUE/'jobs'/name).exists(),'existing_job')
        config=folder/(name+'-config.json');q.save(config,dict(arms=[arm]))
        inputs=membership+[pin(q.ROOT/p) for p in ['scripts/additive341.py','scripts/native_adapt152.py',
            'scripts/edge329.py','scripts/regions331.py','scripts/regions313.py','scripts/detail307.py',
            'scripts/filters327.py','reports/work/FOCUS-329/run/last.pt','reports/work/FOCUS-341/audit.json']]
        spec=dict(version=q.SPEC_VERSION,id=name,task='FOCUS341',owner='research-host-NUIAK',kind='confirm',authority='training',
            hypothesis='Added boundary detail improves thin-effect decisions while preserving original views: '+arm,
            decisionRule='Use fixed last weights and thresholds 0.15/0.85. Require gains without lost previous successes.',
            adapter=dict(type='python-callable',steps=['additive341.train'],outputAttributes=['additive341.OUT']),
            inputs=inputs,stage=[dict(**{'from':pin(path)},to=target) for path,target in
                [(config,'config.json'),(source/'audit.json','audit.json'),(source/'negatives.json','negatives.json')]],
            limits=dict(timeoutSeconds=1800,maxOutputBytes=2*1024**3,maxAttempts=1),
            training=dict(experimentLogRunId='FOCUS341',membership=membership,
                initialization=pin(q.ROOT/'reports/work/FOCUS-329/run/last.pt'),epochs=30,
                storageBudgetBytes=2*1024**3,acceptanceEvidence='Complete retained regression comparisons and unchanged original crops.',resume='restart'))
        path=folder/(name+'.json');q.save(path,spec);print(q.submit(path))


if __name__=='__main__':main()
