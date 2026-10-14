"""Extend the matched graph to the 3 newly available authored layouts."""
import research_queue as q
import research_graph
from research_campaign340 import pin

OUT = None
LAYOUTS = [dict(name='settings_list', targets=['settings_row_0', 'settings_row_5']),
           dict(name='action_dialog', targets=['dialog_btn_cancel', 'dialog_btn_confirm']),
           dict(name='focus_maze', targets=['maze_card_nw', 'maze_card_se'])]


def summarize():
    cfg=q.load(OUT/'config.json')
    for ref in cfg['inputs']:
        q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'input_changed')
    evidence=[]; totals={}; conditions={}; members=set()
    for dep in q.load(OUT/'dependencies.json'):
        for ref in dep['outputs']:
            doc=q.load(q.ROOT/ref['path']);evidence.append(ref)
            q.require(doc.get('version')=='graph364-comparison-v1','comparison_version')
            for row in doc['rows']:
                q.require(row['id'] not in members,'duplicate_membership');members.add(row['id'])
            for name,result in doc['scores'].items():
                target=totals.setdefault(name,dict(count=0,correct=0,falseChange=0,missedChange=0,abstentions=0,lost=0,gained=0))
                for condition, counts in result['counts'].items():
                    item=conditions.setdefault(name+'/'+condition,{k:0 for k in target})
                    for key in target:
                        target[key]+=counts[key];item[key]+=counts[key]
    q.require(len(members)==168,'membership_count')
    q.save(OUT/'decision.json',dict(version='focus365-decision-v1',evidence=evidence,totals=totals,conditions=conditions,
        modelAccepted=False,productionChanged=False,sourceDomain='authored-headless',role='development',
        independentGroups=None,artworkFamilies=2,
        nextAction='Separate wrong stable decisions from abstentions. Check cue visibility before choosing new training examples.',
        limitation='These layouts extend the first 4 layouts. Artwork families are reused, not new independent trials. Native HCF remains unqualified.'))


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS365';q.require(not folder.exists(),'revision_exists');folder.mkdir()
    original=q.load(q.QUEUE/'jobs/focus364-10-shelf/spec.json')
    base=q.load(q.ROOT/original['stage'][0]['from']['path'])
    score_template=q.load(q.QUEUE/'jobs/focus364-20-shelf/spec.json')
    specs={};comparisons=[]
    def submit(spec,cfg=None):
        if cfg is not None:
            cp=folder/(spec['id']+'-config.json');q.save(cp,cfg)
            spec['stage']=[{'from':pin(cp),'to':'config.json'}]
        sp=folder/(spec['id']+'.json');q.save(sp,spec);q.submit(sp);specs[spec['id']]=spec
    for index,layout in enumerate(LAYOUTS):
        for family in base['families']:
            ident=f'focus365-{index}-{layout["name"]}-{family["id"]}'
            cfg=dict(base,layout=layout,families=[family])
            spec=dict(original,id=ident,task='FOCUS365',hypothesis=f'Can the {layout["name"]} layout supply matched movement and appearance pairs?',
                decisionRule='Verify exact focus identity, geometry, and visible pixel changes. Keep authored data separate from OS HCF.')
            submit(spec,cfg)
            score_id=ident+'-score';dep=dict(job=ident,specSHA256=q.text_digest(spec),outputs=['corpus.json','qualification.json'])
            score=dict(score_template,id=score_id,task='FOCUS365',dependencies=[dep],
                conditions=[dict(job=ident,output='qualification.json',outcome='supported')],
                hypothesis=f'Do existing models detect movement across {layout["name"]} controls without following dimming or notifications?',
                decisionRule='Measure new successes and lost successes against the pinned original model. Check hidden cues before training.')
            submit(score);comparisons.append(dict(job=score_id,specSHA256=q.text_digest(score),outputs=['diagnostic.json']))
    refs=[pin(q.ROOT/'scripts/graph365.py')]
    ident='focus365-90-decision'
    spec=dict(version=q.SPEC_VERSION,id=ident,task='FOCUS365',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        hypothesis='Which of the 3 new authored layouts exposes useful training gaps?',
        decisionRule='Compare all 168 matched pairs. Preserve per-condition errors and reject promotion without the retained suite and native qualification.',
        inputs=refs,dependencies=comparisons,
        adapter=dict(type='python-callable',steps=['graph365.summarize'],outputAttributes=['graph365.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    submit(spec,dict(inputs=refs))
    build=q.load(q.QUEUE/'jobs/focus364-00-renderer/spec.json');specs[build['id']]=build
    nodes=[dict(job=s['id'],specSHA256=q.text_digest(s),question=s['hypothesis'],
        kind='decision' if s['id'].endswith('decision') else 'experiment' if s['id'].endswith('score') else 'producer') for s in specs.values()]
    graph=dict(version='research-graph-v1',id='FOCUS365-r1',nodes=nodes,
        evidence=[pin(q.QUEUE/'jobs/focus364-r2-90-decision/attempts/1/out/decision.json'),
                  pin(q.QUEUE/'jobs/focus364-r2-91-visibility/attempts/1/out/visibility.json')])
    graph['budget']=research_graph.validate_graph(graph);q.save(folder/'graph.json',graph);print(graph['budget'])


if __name__=='__main__':register()
