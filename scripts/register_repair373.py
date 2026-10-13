"""Replace only unstarted repair decisions. Preserve their original specifications."""
import copy
import research_queue as q
from research_campaign340 import pin

if __name__=='__main__':
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS373'; expected={}
    for arm in ('control','notification'):
        expected[arm]=[]
        for index in range(4):
            old=q.load(q.QUEUE/f'jobs/focus366-{arm}-summary-{index}/spec.json')
            expected[arm]+=[d['job'] for d in old['dependencies'] if not d['job'].endswith('-notifications-3')]
        q.require(len(expected[arm])==27,'expected_comparisons')
    cp=folder/'repair-v2-config.json';q.save(cp,dict(expected=expected))
    spec=copy.deepcopy(q.load(folder/'focus373-repair-decision.json'))
    spec.update(id='focus373-repair-decision-v2',adapter=dict(type='python-callable',steps=['repair373.run'],outputAttributes=['repair373.OUT']),
        inputs=[pin(q.ROOT/'scripts/repair373.py')],stage=[{'from':pin(cp),'to':'config.json'}])
    path=folder/(spec['id']+'.json');q.save(path,spec);q.submit(path)
    review=copy.deepcopy(q.load(folder/'focus373-repair-preserve-gains.json'));review['id']='focus373-repair-preserve-gains-v2'
    review['dependencies']=[dict(job=spec['id'],specSHA256=q.text_digest(spec),outputs=['decision.json']) if d['job']=='focus373-repair-decision' else d for d in review['dependencies']]
    path=folder/(review['id']+'.json');q.save(path,review);q.submit(path)
    obsolete=['focus373-repair-decision','focus373-repair-preserve-gains']
    with q.host_lock(q.QUEUE/'approval.lock'):
        doc=q.load(q.QUEUE/'approved-additions.json')
        for ident in obsolete:
            q.require(not q.attempts_of(q.QUEUE/'jobs'/ident),'repair_already_started')
            doc['jobs'].pop(ident,None)
        q.save(q.QUEUE/'approved-additions.json',doc,replace=True)
    q.save(folder/'repair-v2-additions.json',[dict(id=s['id'],sha256=q.text_digest(s)) for s in (spec,review)])
    print('Registered 2 successor decisions; withdrew 2 unstarted approvals. Original specifications remain.')
