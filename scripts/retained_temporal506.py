"""Measure temporal information on qualified retained calibration pairs."""
from pathlib import Path
import research_queue as q
from experiment_templates import pin, checked
from fixture_evidence501 import audit
from temporal_pairs414 import decision, outcome

OUT=None

def prepare(request):
    q.require(set(request)=={'version','id','fixtureRequest','model'},'retained_temporal_fields')
    q.require(request['version']=='retained-temporal-request-v1' and q.ID.fullmatch(request['id']),'retained_temporal_version')
    source=q.load(checked(request['fixtureRequest']))
    q.require(source['view']=='geometry','retained_temporal_view')
    data=audit(source);checked(request['model'])
    frames={(f['case'],f['endpoint']):f for f in data['frames']}
    rows=[]
    for pair in data['pairs']:
        before=frames[(pair['case'],'before')];after=frames[(pair['case'],'after')]
        q.require(before['role']==after['role']=='calibration','retained_temporal_role')
        rows.append(dict(id=pair['case'],group=pair['group'],role='calibration',
            changed=int(pair['observedFocusChanged']),images=[before['image'],after['image']],
            observedScrollChanged=pair['observedScrollChanged'],requestedCondition=pair['requestedCondition']))
    q.require(0<len(rows)<=16,'retained_temporal_scope')
    return rows

def build(path):
    r=q.load(path);prepare(r)
    refs=[pin(path),r['fixtureRequest'],r['model'],pin(Path(__file__).resolve())]
    return dict(version='research-spec-v2',id=r['id'],task='SDK506',owner='Maximum-mini-NUIAK',kind='screen',
        jobKind='artifact',authority='diagnostic',dependencies=[],inputs=refs,
        adapter=dict(type='python-callable',steps=['retained_temporal506.run'],outputAttributes=['retained_temporal506.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),
        evidence=dict(artifactReceipt='artifact-receipt.json',reads=[x['path'] for x in refs[:3]]),
        question='Does the retained temporal model use the before frame to distinguish observed focus changes from unchanged focus?',
        hypothesis='Removing before-frame information loses genuine changes or reveals content-driven decisions.',
        controlledComparison='Same model, thresholds, group, and original calibration labels. Compare ordered pairs against duplicated after frames.',
        decisionRule='Report gains, lost successes, false changes, and abstentions. No independent accuracy or moving-background claim.',
        nextActionByOutcome=dict(supported='Qualify additional independent transitions when producer evidence arrives.',
                                 contradicted='Diagnose temporal or scene sensitivity before training or promotion.'))

def run():
    import additive341 as a
    import report_additive341 as scoring
    spec=q.load(OUT.parents[2]/'spec.json');request=q.load(checked(spec['inputs'][0]));rows=prepare(request)
    a.t.set_num_threads(2);net=a.e.load_candidate(checked(request['model']));net.eval()
    control=[dict(r,images=[r['images'][1],r['images'][1]]) for r in rows]
    with a.t.inference_mode():
        paired=scoring.score_rows(net,rows,False).tolist()
        repeated=scoring.score_rows(net,control,False).tolist()
    q.require(len(paired)==len(repeated)==len(rows),'retained_temporal_count')
    results=[]
    for r,p,c in zip(rows,paired,repeated):
        good=outcome(decision(p),r['changed']);old=outcome(decision(c),r['changed'])
        results.append(dict(**r,pairedProbability=p,repeatedAfterProbability=c,pairedOutcome=good,
            repeatedAfterOutcome=old,gain=good=='correct' and old!='correct',lost=old=='correct' and good!='correct'))
    q.save(OUT/'benchmark_summary.json',dict(version='retained-temporal-comparison-v1',model=request['model'],rows=results,
        gains=sum(r['gain'] for r in results),losses=sum(r['lost'] for r in results),
        trainingEligible=False,modelAccepted=False,
        limitation='Calibration diagnostic from one related group. Repeated-after input is an intervention, not a single-frame classifier. Scroll evidence does not establish arbitrary moving-background coverage.'))
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
