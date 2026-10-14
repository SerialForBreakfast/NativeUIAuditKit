"""Keep previous notification gains separate from gains against the original model."""
import research_queue as q
from research_campaign340 import decision, pin

OUT=None


def compare(previous, current):
    q.require(set(previous)==set(current), 'gain_membership')
    lost=[]
    for ident, old in previous.items():
        new=current[ident]
        q.require(old['changed']==new['changed'], 'gain_label_mismatch')
        correct=[name for name,p in old['scores'].items() if decision(p)==old['changed']]
        if correct and decision(new['probability'])!=old['changed']:
            lost.append(dict(id=ident,changed=old['changed'],previousCorrect=correct,
                probability=new['probability'],condition=new['condition']))
    return lost


def run():
    cfg=q.load(OUT/'config.json');previous={};current={};prior=None
    for ref in cfg['previous']:
        q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'previous_changed')
        doc=q.load(q.ROOT/ref['path'])
        for i,row in enumerate(doc['rows']):
            q.require(row['id'] not in previous,'duplicate_previous')
            previous[row['id']]=dict(changed=row['changed'],scores={name:v['probabilities'][i] for name,v in doc['scores'].items()})
    for dep in q.load(OUT/'dependencies.json'):
        for ref in [dep['result'],*dep['outputs']]:
            q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'result_changed')
        for ref in dep['outputs']:
            doc=q.load(q.ROOT/ref['path'])
            if ref['path'].endswith('/decision.json'):prior=doc;continue
            for item in doc['sets'].values():
                for row,p in zip(item['rows'],item['probabilities']['gamma']):
                    q.require(row['id'] not in current,'duplicate_current')
                    current[row['id']]=dict(row,probability=p)
    q.require(prior is not None and len(previous)==392,'review_incomplete')
    lost=compare(previous,current)
    q.save(OUT/'review.json',dict(previousDecision=prior,lostPreviousGains=lost,
        passesDevelopmentRule=prior['passesDevelopmentRule'] and not lost,modelAccepted=False,
        nextAction='Review native transfer.' if prior['passesDevelopmentRule'] and not lost else 'Diagnose the listed losses before another correction.',
        limitation='This strict comparison preserves the union of correct FOCUS329, gamma348, and movement349 decisions on 392 development pairs.'))


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS366';graph=q.load(folder/'graph.json')
    development=q.load(folder/'focus366-admission-config.json')['development']
    wanted={r['path'] for r in development};found={}
    for path in sorted((q.QUEUE/'jobs').glob('focus36*/attempts/1/out/diagnostic.json')):
        doc=q.load(path)
        if doc.get('version')=='graph364-comparison-v1' and doc['corpus']['path'] in wanted:
            found[doc['corpus']['path']]=pin(path)
    q.require(set(found)==wanted,'previous_comparisons_missing')
    deps=[]
    for ident in ['focus366-decision']+[f'focus366-notification-notifications-{i}' for i in range(4)]:
        spec=q.load(q.QUEUE/'jobs'/ident/'spec.json')
        deps.append(dict(job=ident,specSHA256=q.text_digest(spec),outputs=['decision.json' if ident.endswith('decision') else 'comparison.json']))
    ident='focus366-preserve-gains';refs=list(found.values())+[pin(q.ROOT/'scripts/review_notification366.py')]
    cp=folder/(ident+'-config.json');q.save(cp,dict(previous=list(found.values())))
    spec=dict(version=q.SPEC_VERSION,id=ident,task='FOCUS366',owner='research-host-NUIAK',kind='confirm',authority='diagnostic',
        hypothesis='Does the correction preserve earlier notification gains, not only original-model successes?',
        decisionRule='List every lost correct decision across all 3 prior models. Any loss blocks advancement.',
        inputs=refs,stage=[{'from':pin(cp),'to':'config.json'}],dependencies=deps,
        adapter=dict(type='python-callable',steps=['review_notification366.run'],outputAttributes=['review_notification366.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    sp=folder/(ident+'.json');q.save(sp,spec);q.submit(sp)
    graph['id']='FOCUS366-r2';graph['supersedes']='FOCUS366-r1'
    graph['nodes'].append(dict(job=ident,specSHA256=q.text_digest(spec),question=spec['hypothesis'],kind='decision'))
    import research_graph
    graph['budget']=research_graph.validate_graph(graph);q.save(folder/'graph-r2.json',graph)
    additions=q.load(folder/'additions.json')+[dict(id=ident,sha256=q.text_digest(spec))]
    q.save(folder/'additions-r2.json',additions)
    print(graph['budget'])


if __name__=='__main__':register()
