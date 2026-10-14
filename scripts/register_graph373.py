"""Prepare bounded cached jobs without starting or stopping execution."""
import copy
import research_queue as q
from research_campaign340 import pin


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS373'
    folder.mkdir(exist_ok=True)
    specs=[]
    code=[pin(q.ROOT/'scripts/graph373.py'),pin(q.ROOT/'scripts/focus_evidence.py')]
    def add(ident,step,question,answer,cfg,refs=(),deps=()):
        cfg=dict(cfg,pins=list(refs)); cp=folder/(ident+'-config.json')
        if cp.exists():q.require(q.load(cp)==cfg,'config_revision_changed')
        else:q.save(cp,cfg)
        spec=dict(version=q.SPEC_VERSION,id=ident,task='FOCUS373',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis=question,decisionRule=answer,inputs=list(refs)+code,
            stage=[{'from':pin(cp),'to':'config.json'}],adapter=dict(type='python-callable',steps=['graph373.'+step],outputAttributes=['graph373.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        if deps:spec['dependencies']=list(deps)
        p=folder/(ident+'.json')
        if p.exists():q.require(q.load(p)==spec,'spec_revision_changed')
        else:q.save(p,spec)
        if not (q.QUEUE/'jobs'/ident/'spec.json').exists():q.submit(p)
        specs.append(spec)
        return dict(job=ident,specSHA256=q.text_digest(spec),outputs=['summary.json'])
    for arm in ('control','notification'):
        deps=[]
        for part in range(3):
            path=q.QUEUE/f'jobs/focus366-{arm}-notifications-{part}/attempts/1/out/comparison.json'
            q.require(q.state(path.parents[3])[0]=='complete','comparison_not_complete')
            deps.append(add(f'focus373-a-{arm}-{part}','audit',
                f'Do repeated scenes or abstentions change the reported benefit of {arm}, part {part+1}?',
                'Preserve raw counts and per-group counts. Report every gained and lost decision without changing thresholds.',
                dict(comparison=q.relative(path)),[pin(path)]))
        add(f'focus373-b-{arm}-decision','aggregate',
            f'Does {arm} improve all 392 authored cases when related scenes have equal influence?',
            'Report both false-stable denominators and condition errors. Any lost success rejects replacement; native outcomes remain separate.',
            dict(arm=arm),deps=deps)
    requests=[pin(p) for p in sorted((q.ROOT/'docs/experiment-graph-v1-requests').glob('*.json'))]
    add('focus373-c-request-roles','request_audit','Can the 7 supplied TTR requests supply the proposed training comparisons?',
        'Keep calibration roles and identify target, capacity, and producer checks. Do not capture or admit data.',
        dict(requests=requests,target='9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'),requests)
    add('focus373-d-risk-support','risk_plan','How many independent changed cases are needed for illustrative risk bounds?',
        'Report 19, 59, and 299-trial bounds separately from measured model risk. Do not change deployment gates.',{})
    # Preserve failed empty batches. New summaries consume the complete 392-case membership.
    remap={}
    oldids=['focus366-control-summary-3','focus366-notification-summary-3','focus366-decision','focus366-preserve-gains']
    for oldid in oldids:
        spec=copy.deepcopy(q.load(q.QUEUE/'jobs'/oldid/'spec.json'))
        ident=oldid.replace('focus366-','focus373-repair-'); spec.update(id=ident,task='FOCUS373')
        dependencies=[]
        for dep in spec['dependencies']:
            if dep['job'].endswith('-notifications-3'):
                old=q.load(q.QUEUE/'jobs'/dep['job']/'spec.json')
                config=q.load(q.ROOT/old['stage'][0]['from']['path'])
                q.require(config['sources']==[],'omitted_nonempty_batch')
                continue
            dependencies.append(remap.get(dep['job'],dep))
        spec['dependencies']=dependencies
        spec['hypothesis']='Finish the complete retained comparison without repeating the empty batch: '+oldid
        spec['decisionRule']='Reuse all 392 notification cases and every retained comparison. Any missing result or lost success blocks advancement.'
        path=folder/(ident+'.json')
        if path.exists():q.require(q.load(path)==spec,'repair_spec_changed')
        else:q.save(path,spec)
        if not (q.QUEUE/'jobs'/ident/'spec.json').exists():q.submit(path)
        output='summary.json' if 'summary' in oldid else 'decision.json' if oldid.endswith('decision') else 'review.json'
        remap[oldid]=dict(job=ident,specSHA256=q.text_digest(spec),outputs=[output]);specs.append(spec)
    q.save(folder/'additions.json',[dict(id=s['id'],sha256=q.text_digest(s)) for s in specs])
    print('Registered',len(specs),'jobs; execution remains with the background runner.')


if __name__=='__main__':register()
