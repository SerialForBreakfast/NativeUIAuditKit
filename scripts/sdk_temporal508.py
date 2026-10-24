"""Compare frozen temporal candidates on native SDK action pairs, including absence."""
from collections import Counter
from pathlib import Path
import research_queue as q
from experiment_templates import pin,checked
from sdk_campaign508 import pair
from temporal_pairs414 import decision,outcome

OUT=None

def rows(request):
    q.require(request['version']=='sdk-temporal-request-v1' and set(request['models'])=={'baseline','seed42','seed44'},'sdk_temporal_contract')
    q.require(0<len(request['pairs'])<=6 and len({p['path'] for p in request['pairs']})==len(request['pairs']),'sdk_temporal_scope')
    result=[]
    for ref in request['pairs']:
        p=pair(ref);a,b=p['frames']
        result.append(dict(id=p['id'],group=a['group'],role='review_only',split=a['split'],
            expected=p['expected'],observed=p['observed'],issues=p['issues'],
            changed=int(a['focusID']!=b['focusID']),images=[a['image'],b['image']],
            endpoints=dict(before=a['focusID'],after=b['focusID'])))
    for ref in request['models'].values():checked(ref)
    return result

def build(path):
    r=q.load(path);rows(r);refs=[pin(path),*r['pairs'],*r['models'].values(),pin(Path(__file__).resolve())]
    return dict(version='research-spec-v2',id=r['id'],task='SDK508',owner='Maximum-mini-NUIAK',kind='screen',
        jobKind='artifact',authority='diagnostic',dependencies=[],inputs=refs,
        adapter=dict(type='python-callable',steps=['sdk_temporal508.run'],outputAttributes=['sdk_temporal508.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),evidence=dict(artifactReceipt='artifact-receipt.json',reads=[p['path'] for p in refs[:-1]]),
        question='Do retained temporal improvements preserve native movement, arrival, departure, and unchanged-focus outcomes?',
        hypothesis='Temporal candidates can identify native focus changes despite crop-selection failures.',
        controlledComparison='Same 6 native pairs and fixed 0.15/0.85 thresholds. Compare baseline against retained seeds 42 and 44.',
        decisionRule='Report case-linked gains, losses, false changes, and abstentions. Arrival and departure remain separate. Do not promote.',
        nextActionByOutcome=dict(supported='Broaden qualified native transition groups without retraining this slice.',contradicted='Preserve failed cases and diagnose before preparing training-role data.'))

def run():
    import additive341 as a
    import report_additive341 as scoring
    spec=q.load(OUT.parents[2]/'spec.json');request=q.load(checked(spec['inputs'][0]));data=rows(request)
    a.t.set_num_threads(2);results={}
    for name,ref in request['models'].items():
        model=a.e.load_candidate(checked(ref));model.eval()
        with a.t.inference_mode():scores=scoring.score_rows(model,data,False).tolist()
        q.require(len(scores)==len(data),'sdk_temporal_score_count')
        results[name]=[dict(**r,probability=s,outcome=outcome(decision(s),r['changed'])) for r,s in zip(data,scores)]
    comparisons={}
    for name in ('seed42','seed44'):
        comparisons[name]=[dict(id=old['id'],baseline=old['outcome'],candidate=new['outcome'],
            gain=old['outcome']!='correct' and new['outcome']=='correct',loss=old['outcome']=='correct' and new['outcome']!='correct') for old,new in zip(results['baseline'],results[name])]
    q.save(OUT/'benchmark_summary.json',dict(version='sdk-temporal-comparison-v1',models=request['models'],results=results,comparisons=comparisons,
        counts={n:dict(Counter(r['outcome'] for r in rr)) for n,rr in results.items()},modelAccepted=False,trainingEligible=False,
        limitation='Native review-only endpoints from one group. Temporal change does not identify the destination. Content motion remains unverified.'))
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
