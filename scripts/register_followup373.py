"""Register 5 fixed diagnostics for the background runner."""
import research_queue as q
from research_campaign340 import pin

TESTS = {
    'losses': ('Which earlier successes does notification training lose?',
               'Separate shared control failures from new notification failures before selecting a correction.'),
    'margins': ('Are the lost successes near the decision boundary or strongly wrong?',
                'Choose margin preservation or representation diagnosis from fixed scores. Do not tune thresholds.'),
    'conditions': ('Which layout and notification combinations still fail?',
                   'Select matched native generation cases from per-condition misses and false changes.'),
    'groups': ('Do the same errors occur in both recorded artwork groups?',
               'Prioritize repeated errors. Treat one-group gains as weak evidence, not generalization.'),
    'ancestry': ('Does development evidence share training artwork or layouts?',
                 'Report exact encoded overlap and known ancestry. Keep these cases out of final audit.')}

def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS373-followup';folder.mkdir(exist_ok=True)
    previous=q.load(q.ROOT/'Research/ResearchSpecs/FOCUS366/focus366-preserve-gains-config.json')['previous']
    comparisons={arm:[pin(q.QUEUE/f'jobs/focus366-{arm}-notifications-{i}/attempts/1/out/comparison.json')
                      for i in range(3)] for arm in ('control','notification')}
    training=pin(q.QUEUE/'jobs/focus366-admission/attempts/1/out/admission.json')
    models=[]
    for p in previous:models += [v['model'] for v in q.load(q.ROOT/p['path'])['scores'].values()]
    for refs in comparisons.values():
        models += [q.load(q.ROOT/p['path'])['configuration']['models']['gamma'] for p in refs]
    refs=previous+sum(comparisons.values(),[])+[training]+models
    refs=list({p['path']:p for p in refs}.values())
    code=[pin(q.ROOT/'scripts'/name) for name in ('followup373.py','graph373.py','focus_evidence.py')]
    additions=[]
    for mode,(question,decision) in TESTS.items():
        ident='focus373-followup-'+mode
        cp=folder/(ident+'-config.json');q.save(cp,dict(mode=mode,previous=previous,comparisons=comparisons,training=training))
        spec=dict(version=q.SPEC_VERSION,id=ident,task='FOCUS373',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis=question,decisionRule=decision,inputs=refs+code,
            stage=[dict(**{'from':pin(cp)},to='config.json')],
            adapter=dict(type='python-callable',steps=['followup373.run'],outputAttributes=['followup373.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        path=folder/(ident+'.json');q.save(path,spec);q.submit(path)
        additions.append(dict(id=ident,sha256=q.text_digest(spec)))
    q.save(folder/'additions.json',additions)
    print('Registered 5 diagnostics. Execution remains with the background runner.')

if __name__=='__main__':register()
