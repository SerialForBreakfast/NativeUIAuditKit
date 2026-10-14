"""Register the complete FOCUS366 graph without starting the runner."""
import copy
import authored319
import research_queue as q
import research_graph
from research_campaign340 import pin


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS366'
    q.require(not folder.exists(), 'revision_exists'); folder.mkdir()
    specs={}; kinds={}
    code=[pin(q.ROOT/'scripts'/name) for name in ('notification366.py','graph364.py','visibility364.py','position355.py')]
    source=pin(q.ROOT/'reports/work/FOCUS364/render-headless-screen.swift')
    development=[]
    for path in sorted((q.QUEUE/'jobs').glob('focus36*/attempts/1/out/corpus.json')):
        job=path.parents[3]
        if not job.name.startswith(('focus364-','focus365-')) or q.state(job)[0]!='complete':continue
        doc=q.load(path)
        if doc.get('version')=='graph364-corpus-v1': development.append(pin(path))
    q.require(sum(len(q.load(q.ROOT/r['path'])['rows']) for r in development)==392, 'development_count')
    def add(ident,step,question,answer,inputs=None,cfg=None,deps=None,kind='experiment',conditions=None,base=None):
        spec=copy.deepcopy(base) if base else dict(version=q.SPEC_VERSION,owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        refs=list({r['path']:r for r in (inputs or [])+code}.values())
        spec.update(id=ident,task='FOCUS366',hypothesis=question,decisionRule=answer,inputs=refs,
            adapter=dict(type='python-callable',steps=[step],outputAttributes=[step.rsplit('.',1)[0]+'.OUT']))
        if cfg is not None:
            cfg=dict(cfg,inputs=refs); cp=folder/(ident+'-config.json'); q.save(cp,cfg)
            spec['stage']=[dict(from_=pin(cp),to='config.json')]
            spec['stage'][0]['from']=spec['stage'][0].pop('from_')
        if deps:spec['dependencies']=deps
        if conditions:spec['conditions']=conditions
        path=folder/(ident+'.json'); q.save(path,spec); q.submit(path)
        specs[ident]=spec;kinds[ident]=kind
        return spec
    def dep(spec,*names):return dict(job=spec['id'],specSHA256=q.text_digest(spec),outputs=list(names))
    plan=authored319.plan(); producers=[]
    for index in (2,3,4):
        family=dict(id='notification366-s'+str(index),assets=[a for a in plan['assets'] if f'-s{index}-' in a['id']])
        q.require(len(family['assets'])==2,'artwork_count')
        replacements=[['"System Preferences & Device Configuration"',f'"Library profile {index}: display and playback"'],
            ['"Clear Viewing History?"',f'"Remove saved collection {index}?"'],
            ['"This will remove all recommendations and resume positions."',f'"This removes the saved items for profile {index}."'],
            ['"This action cannot be undone."',f'"Other profiles keep their saved items. Profile {index}."']]
        for n,name in enumerate(('Network & Wi-Fi','Accounts & Profiles','Video & Audio','Remotes & Accessories','Accessibility & Display','System & Software Updates')):
            replacements.append(['"'+name+'"',f'"Profile {index} option {n+1}: {name}"'])
        build=add(f'focus366-build-{index}','notification366.build','Can fresh text distinguish training scenes from inspected development scenes?',
            'Compile the pinned renderer with fixed text changes. Do not edit TTR.',inputs=[source],cfg=dict(source=source,replacements=replacements),kind='producer')
        for layout,targets in [('settings_list',['settings_row_1','settings_row_4']),('action_dialog',['dialog_btn_cancel','dialog_btn_confirm']),('focus_maze',['maze_card_nw','maze_card_se'])]:
            refs=[source]+[a['image'] for a in family['assets']]
            job=add(f'focus366-generate-{index}-{layout}','notification366.produce',
                f'Generate matched notifications, dimming, and movements for {layout}, family {index}.',
                'Require visible changes with fixed geometry. Keep these fresh examples out of development.',inputs=refs,
                cfg=dict(source=source,layout=dict(name=layout,targets=targets),families=[family]),deps=[dep(build,'renderer','build.json')],kind='producer')
            producers.append(dep(job,'corpus.json','qualification.json'))
    admission=add('focus366-admission','notification366.admission','Can the 252 fresh pairs enter training without copying development images?',
        'Reject overlapping pixels, hidden targets, changed inputs, or missing dimmed movements.',inputs=development,
        cfg=dict(development=development),deps=producers,kind='qualification',
        conditions=[dict(job=d['job'],output='qualification.json',outcome='supported') for d in producers])
    summaries=[]
    for arm in ('control','notification'):
        base=q.load(q.ROOT/'Research/ResearchSpecs/FOCUS355/focus355-position-train.json')
        old=q.load(q.ROOT/base['stage'][0]['from']['path'])
        # Preserve old pins. A changed historical input needs investigation, not automatic replacement.
        base['training'].update(epochs=10,experimentLogRunId='FOCUS366')
        base['limits']=dict(timeoutSeconds=1800,maxOutputBytes=2*1024**3,maxAttempts=1)
        train=add(f'focus366-{arm}-train','notification366.training',
            'Compare fresh notification training with label-matched retained examples at equal cost: '+arm+'.',
            'Keep original crops, 10 epochs, initialization, loss, thresholds, and schedule fixed. Change only the extra examples.',
            inputs=old['inputs'],cfg=dict(arm=arm),deps=[dep(admission,'admission.json','qualification.json')],base=base,
            conditions=[dict(job=admission['id'],output='qualification.json',outcome='supported')])
        evaluations=[]
        templates=[]
        for path in sorted((q.ROOT/'Research/ResearchSpecs/FOCUS355').glob('focus355-position-*.json')):
            oldspec=q.load(path)
            if oldspec.get('adapter',{}).get('steps')!=['position355.evaluate'] or oldspec['id'].startswith('focus355-position-branch-'):continue
            templates.append((oldspec['id'][len('focus355-position-'):],q.load(q.ROOT/oldspec['stage'][0]['from']['path'])))
        q.require(len(templates)==24,'retained_count')
        for index in range(4):
            sources=development[index*4:(index+1)*4]
            templates.append((f'notifications-{index}',dict(sources=sources,inputs=sources)))
        for suffix,cfg in templates:
            cfg['modelNames']={'control':'FOCUS329','gamma':arm};cfg.pop('models',None)
            evaluation=add(f'focus366-{arm}-{suffix}','position355.evaluate',
                f'Does {arm} preserve previous successes on {suffix}?',
                'Report false changes, missed movements, abstentions, gains, and losses at unchanged thresholds.',
                inputs=cfg['inputs'],cfg=cfg,deps=[dep(train,'last.pt','fit.json')])
            evaluations.append(dep(evaluation,'diagnostic.json' if cfg.get('capture') else 'comparison.json'))
        for index in range(4):
            summary=add(f'focus366-{arm}-summary-{index}','notification366.collect','Account for each matched comparison and its lost successes.',
                'Preserve case-linked notification scores and all retained losses.',deps=evaluations[index*7:(index+1)*7])
            summaries.append(dep(summary,'summary.json'))
    add('focus366-decision','notification366.decision','Does notification training reduce false changes without losing dimmed-corner movement or previous successes?',
        'Require complete results, fewer false changes than control, more correct decisions, and zero lost baseline successes. Do not promote.',deps=summaries,kind='decision')
    graph=dict(version='research-graph-v1',id='FOCUS366-r1',nodes=[dict(job=k,specSHA256=q.text_digest(v),question=v['hypothesis'],kind=kinds[k]) for k,v in specs.items()])
    graph['budget']=research_graph.validate_graph(graph);q.save(folder/'graph.json',graph)
    q.save(folder/'additions.json',[dict(id=k,sha256=q.text_digest(v)) for k,v in specs.items()])
    print(graph['budget'])


if __name__=='__main__':register()
