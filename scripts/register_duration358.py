"""Register the matched duration test and every dependent regression check."""
import copy
import research_queue as q
from research_campaign340 import pin


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS358';folder.mkdir(exist_ok=True)
    source=pin(q.ROOT/'scripts/duration358.py');all_specs=[];summaries=[]
    def publish(spec):
        path=folder/(spec['id']+'.json');q.save(path,spec);q.submit(path);all_specs.append(spec)
        return dict(job=spec['id'],specSHA256=q.text_digest(spec),outputs=['summary.json'])
    for arm in ('control','position'):
        base=q.load(q.ROOT/'Research/ResearchSpecs/FOCUS355/focus355-position-train.json')
        config=q.load(q.ROOT/base['stage'][0]['from']['path']);config['arm']=arm
        config['inputs'].append(source)
        cp=folder/(arm+'-config.json');q.save(cp,config)
        ident='focus358-'+arm+'-train'
        base.update(id=ident,task='FOCUS358',hypothesis='Test whether 30 epochs improve '+arm+' beyond its 10-epoch result.',
            decisionRule='Keep original crops, initialization, membership, and thresholds. Require target gains with zero lost retained successes.')
        base['inputs'].append(source);base['stage']=[{'from':pin(cp),'to':'config.json'}]
        base['adapter']=dict(type='python-callable',steps=['duration358.training'],outputAttributes=['duration358.OUT'])
        base['training'].update(epochs=30,experimentLogRunId='FOCUS358')
        publish(base)
        deps=[]
        for path in sorted((q.ROOT/'Research/ResearchSpecs/FOCUS355').glob('focus355-position-*.json')):
            old=q.load(path)
            if old.get('adapter',{}).get('steps') != ['position355.evaluate']:continue
            # Exclude the separate whole-frame branch arm.
            if old['id'].startswith('focus355-position-branch-'):continue
            spec=copy.deepcopy(old);suffix=old['id'][len('focus355-position-'):]
            spec.update(id='focus358-'+arm+'-'+suffix,task='FOCUS358',
                hypothesis='Compare the 30-epoch '+arm+' candidate with the frozen baseline on '+suffix+'.')
            c=q.load(q.ROOT/spec['stage'][0]['from']['path'])
            c['modelNames']={'control':'FOCUS329','gamma':arm+'-30epochs'}
            cp=folder/(spec['id']+'-config.json');q.save(cp,c)
            spec['stage']=[{'from':pin(cp),'to':'config.json'}]
            spec['dependencies']=[dict(job=ident,specSHA256=q.text_digest(base),outputs=['last.pt','fit.json'])]
            publish(spec)
            deps.append(dict(job=spec['id'],specSHA256=q.text_digest(spec),
                outputs=['diagnostic.json' if c.get('capture') else 'comparison.json']))
        q.require(len(deps)==24,'comparison_count')
        for i in range(3):
            spec=dict(version=q.SPEC_VERSION,id=f'focus358-{arm}-summary-{i}',task='FOCUS358',
                owner='research-host-NUIAK',kind='screen',authority='diagnostic',
                hypothesis='Account for retained comparisons before accepting a candidate.',
                decisionRule='Missing comparisons and lost successes block acceptance.',inputs=[source,pin(q.ROOT/'scripts/position355.py')],
                dependencies=deps[i*8:(i+1)*8],adapter=dict(type='python-callable',steps=['duration358.collect'],outputAttributes=['duration358.OUT']),
                limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
            summaries.append(publish(spec))
    final=copy.deepcopy(spec);final.update(id='focus358-final-comparison',dependencies=summaries)
    publish(final)
    q.save(q.ROOT/'reports/work/HCF358/duration-additions.json',
        [dict(id=s['id'],sha256=q.text_digest(s)) for s in all_specs])


if __name__=='__main__':register()
