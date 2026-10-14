"""Score private visual pairs for review without inventing accuracy labels."""
import time
import appearance348 as m
import report_additive341 as scoring

q=m.q;OUT=None


def decision(value):return 'changed' if value>=.85 else 'stable' if value<=.15 else 'abstain'


def run():
    config=q.load(OUT/'config.json');m.check_inputs(config);m.t.set_num_threads(2)
    predictions={};timings={}
    for name,ref in config['models'].items():
        start=time.monotonic();net=m.a.e.load_candidate(q.ROOT/ref['path'])
        timings[name]=dict(preprocessingSeconds=0.,inferenceSeconds=0.,examples=0)
        predictions[name]=scoring.score_rows(net,config['rows'],False,timings[name]).tolist()
        timings[name]['totalSeconds']=time.monotonic()-start
    rows=[]
    for i,row in enumerate(config['rows']):
        scores={name:values[i] for name,values in predictions.items()};decisions={k:decision(v) for k,v in scores.items()}
        rows.append(dict(row,probabilities=scores,decisions=decisions,
            disagreement=len(set(decisions.values()))>1,focusChanged=None,trainingEligible=False))
    q.save(OUT/'shadow.json',dict(version='office-shadow349-v1',rows=rows,models=config['models'],timing=timings,
        accuracy=None,trainingEligible=False,productionEligible=False,
        limitations=['Selected visual pairs are development review cases, not command-linked transitions.',
            'No reviewed focus labels exist. Scores do not establish accuracy.',
            'All images belong to one human session. Do not count them as independent evaluation groups.']))


def register():
    base=q.ROOT/'reports/work/FOCUS-349';intake=q.load(base/'office-intake/intake.json')
    audit=q.load(base/'office/final-audit.json');cases=q.load(base/'office/office-eval-20261012-case-index.json')
    byid={v['case_id']:v for v in cases};rows=[]
    for pair in audit['proposedVisualPairReview']:
        images=[intake['frames'][byid[pair[k]]['frame_id']]['image'] for k in ('before','after')]
        rows.append(dict(id=pair['before']+'-'+pair['after'],images=images,role='development',
            sourceDomain='physical-human-recording',group=intake['counts'] and audit['sessionID'],actionLinked=False))
    models={'baseline329':m.f.pin(m.a.e.OUT/'run/last.pt'),
        'gamma348':m.f.pin(q.QUEUE/'jobs/focus348-00-gamma/attempts/1/out/last.pt'),
        'movement349':m.f.pin(q.QUEUE/'jobs/focus349-00-gamma/attempts/1/out/last.pt')}
    refs=list(models.values())+[ref for row in rows for ref in row['images']]
    refs += [m.f.pin(p) for p in [base/'office-intake/intake.json',base/'office/final-audit.json',
        base/'office/office-eval-20261012-case-index.json',q.ROOT/'scripts/office_shadow349.py',
        q.ROOT/'scripts/report_additive341.py',q.ROOT/'scripts/regions313.py',q.ROOT/'scripts/edge329.py']]
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS349';ident='focus349-36-office-shadow'
    cp=folder/(ident+'-config.json');q.save(cp,dict(rows=rows,models=models,inputs=refs))
    spec=dict(version=q.SPEC_VERSION,id=ident,task='FOCUS349',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        hypothesis='Real visual pairs expose disagreement and abstention cases worth review.',
        decisionRule='Return all 11 pairs and 3 pinned model scores. Do not report accuracy without labels.',inputs=refs,
        stage=[{'from':m.f.pin(cp),'to':'config.json'}],adapter=dict(type='python-callable',steps=['office_shadow349.run'],
            outputAttributes=['office_shadow349.OUT']),limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    path=folder/(ident+'.json');q.save(path,spec);print(q.submit(path))


if __name__=='__main__':register()
