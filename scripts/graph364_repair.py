"""Split oversized producers and reuse completed FOCUS364 evidence."""
import research_queue as q
import research_graph
from research_campaign340 import pin, decision

OUT = None


def summarize():
    cfg = q.load(OUT / 'config.json')
    for ref in cfg['inputs']:
        q.require(q.digest(q.ROOT / ref['path']) == ref['sha256'], 'input_changed')
    deps = q.load(OUT / 'dependencies.json'); comparisons = []; native = None
    for dep in deps:
        for ref in dep['outputs']:
            doc = q.load(q.ROOT / ref['path'])
            if doc.get('version') == 'graph364-comparison-v1':
                comparisons.append((ref, doc))
            elif doc.get('version') == 'research-condition-v1':
                native = doc
    q.require(len(comparisons) == 6 and native is not None, 'incomplete_graph')
    totals = {}; failures = []; membership = set()
    for ref, doc in comparisons:
        for row in doc['rows']:
            q.require(row['id'] not in membership, 'duplicate_membership')
            membership.add(row['id'])
        for name, result in doc['scores'].items():
            summary = totals.setdefault(name, dict(count=0, correct=0, falseChange=0, missedChange=0,
                                                   abstentions=0, lost=0, gained=0))
            for count in result['counts'].values():
                for key in summary:
                    summary[key] += count[key]
            for row, probability in zip(doc['rows'], result['probabilities']):
                if decision(probability) != row['changed']:
                    failures.append(dict(model=name, case=row['id'], group=row['group'], condition=row['condition'],
                                         label=row['changed'], probability=probability, evidence=ref))
    q.require(len(membership) == 224, 'membership_count')
    q.save(OUT / 'decision.json', dict(version='graph364-decision-v1', graph='FOCUS364-r2',
        evidence=[r for r, _ in comparisons], totals=totals, failures=failures, nativeQualification=native,
        modelAccepted=False, productionChanged=False, independentGroups=2,
        nextAction='Target false-change conditions only if matched movement remains correct. Qualify native transfer before training admission.',
        coverage=dict(layouts=4, themes=['renderer-default'], nativeHCF=0),
        limitation='Related artwork and reversed pairs are not independent trials. No candidate trains in this diagnostic batch.'))


def register():
    root = q.ROOT / 'Research/ResearchSpecs/FOCUS364-r2'
    q.require(not root.exists(), 'revision_exists'); root.mkdir()
    nodes = []; specs = {}
    def existing(ident, kind):
        spec = q.load(q.QUEUE / 'jobs' / ident / 'spec.json'); specs[ident] = spec
        nodes.append(dict(job=ident, specSHA256=q.text_digest(spec), kind=kind, question=spec['hypothesis']))
    for name, kind in [('00-renderer', 'producer'), ('05-native-evidence', 'qualification'),
                       ('11-grid', 'producer'), ('13-top_nav_shelf', 'producer'),
                       ('21-grid', 'experiment'), ('23-top_nav_shelf', 'experiment')]:
        existing('focus364-' + name, kind)
    def dep(ident, outputs):
        return dict(job=ident, specSHA256=q.text_digest(specs[ident]), outputs=outputs)
    comparison_deps = [dep('focus364-'+s, ['diagnostic.json']) for s in ('21-grid', '23-top_nav_shelf')]
    for original in ('10-shelf', '12-hero_detail'):
        old = q.load(q.QUEUE / 'jobs' / ('focus364-'+original) / 'spec.json')
        old_config = q.load(q.ROOT / old['stage'][0]['from']['path'])
        for family in old_config['families']:
            ident = 'focus364-r2-' + original + '-' + family['id']
            cfg = dict(old_config, families=[family])
            cp = root / (ident+'-config.json'); q.save(cp, cfg)
            spec = dict(old, id=ident, stage=[{'from':pin(cp), 'to':'config.json'}],
                        hypothesis=old['hypothesis']+' Use 1 artwork family per output part.')
            sp = root / (ident+'.json'); q.save(sp,spec); q.submit(sp); existing(ident,'producer')
            old_score = q.load(q.QUEUE/'jobs'/('focus364-2'+original[1:])/'spec.json')
            score_id = ident+'-score'
            score_spec = dict(old_score,id=score_id,dependencies=[dep(ident,['corpus.json','qualification.json'])],
                conditions=[dict(job=ident,output='qualification.json',outcome='supported')])
            sp = root/(score_id+'.json');q.save(sp,score_spec);q.submit(sp);existing(score_id,'experiment')
            comparison_deps.append(dep(score_id,['diagnostic.json']))
    ident='focus364-r2-90-decision'; refs=[pin(q.ROOT/'scripts/graph364_repair.py')]
    cp=root/(ident+'-config.json');q.save(cp,dict(inputs=refs))
    old=q.load(q.QUEUE/'jobs/focus364-90-decision/spec.json')
    spec=dict(old,id=ident,inputs=refs,stage=[{'from':pin(cp),'to':'config.json'}],
        dependencies=comparison_deps+[dep('focus364-05-native-evidence',['qualification.json'])],
        adapter=dict(type='python-callable',steps=['graph364_repair.summarize'],outputAttributes=['graph364_repair.OUT']))
    sp=root/(ident+'.json');q.save(sp,spec);q.submit(sp);existing(ident,'decision')
    graph=dict(version='research-graph-v1',id='FOCUS364-r2',supersedes='FOCUS364-r1',nodes=nodes,
        reason='Split 2 oversized producers. Reuse completed build, native review, grid, and top navigation evidence.')
    graph['budget']=research_graph.validate_graph(graph);q.save(root/'graph.json',graph);print(graph['budget'])


if __name__=='__main__':register()
