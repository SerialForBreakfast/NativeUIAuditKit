"""Replay bounded capture policies against observed episodes; never claim live speedups."""
import research_queue as q
from sdk_episode529 import intake
from experiment_templates import checked, pin
from pathlib import Path
OUT = None


def compare(episode, fixed_ms, maximum_ms):
    q.require(type(fixed_ms) is int and type(maximum_ms) is int and 0 <= fixed_ms <= maximum_ms <= 800000,
              'sdk529_policy_budget')
    frames = episode['frames']
    if not episode['eligibility']['temporalReview']:
        return dict(id=episode['id'], state='unavailable', reasons=episode['reasons'])
    start = frames[0]['producerIntervalNS'][0]
    samples = []
    for i, frame in enumerate(frames):
        interval = frame['producerIntervalNS']
        # Both bounds must meet the policy window. Ambiguous samples remain excluded.
        lower, upper = [(v-start)/1e6 for v in interval]
        samples.append(dict(index=i, earliestMS=lower, latestMS=upper,
                            stable=frame['frameReviewable'], bytes=frame['bytes'],
                            observedFocus=frame['focusID'], frameFocus=frame['frameFocusState']))
    arms = {}
    for name in ('fixed-delay', 'observed-stability'):
        eligible = [s for s in samples if s['latestMS'] <= maximum_ms and
                    (s['earliestMS'] >= fixed_ms if name == 'fixed-delay' else s['stable'])]
        selected = eligible[0] if eligible else None
        arms[name] = dict(state='selected' if selected else 'no_observed_sample', sample=selected)
    # A sparse retained sequence cannot establish when an unseen transient occurred.
    return dict(id=episode['id'], state='compared', group=episode['group'], scenario=episode['scenario'],
                arms=arms, sampledFrames=len(samples), retainedBytes=sum(s['bytes'] for s in samples),
                eventNames=sorted({e['name'] for e in episode['events']}),
                timeOrigin='first_retained_capture_not_action_dispatch',
                liveLatencyMeasured=False, transientCoverageQualified=False,
                limitation='Retained-frame replay tests selection only. Prospective matched captures must measure latency and transient coverage.')


def evaluate(request):
    q.require(set(request)=={'version','id','episodes','fixedDelayMS','maximumWaitMS'} and
              request['version']=='sdk-timing-request-v1' and q.ID.fullmatch(request['id']), 'sdk529_timing_request')
    source=intake(q.load(checked(request['episodes'])))
    rows=[compare(e,request['fixedDelayMS'],request['maximumWaitMS']) for e in source['episodes']]
    return dict(version='sdk-timing-replay-v1',rows=rows,modelAccepted=False,policyAccepted=False)


def build(path):
    r=q.load(path);evaluate(r)
    source=q.load(checked(r['episodes']))
    refs=[pin(path),r['episodes']]+[v for e in source['episodes'] for f in e['frames'] for v in f.values()]
    refs=list({v['path']:v for v in refs}.values())
    return dict(version='research-spec-v2',id=r['id'],task='SDK529',owner='Maximum-mini-NUIAK',kind='screen',jobKind='artifact',authority='diagnostic',
        dependencies=[],inputs=refs+[pin(Path(__file__))],adapter=dict(type='python-callable',steps=['sdk_timing529.run'],outputAttributes=['sdk_timing529.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),evidence=dict(reads=[v['path'] for v in refs],artifactReceipt='artifact-receipt.json'),
        question='Which retained frames do fixed-delay and observed-stability policies select?',
        hypothesis='Observed stability can avoid unstable endpoint labels without waiting for stable background pixels.',
        controlledComparison='Identical frames, intervals, event history, groups, and maximum wait.',
        decisionRule='Report unavailable evidence. Require prospective timing and transient coverage before policy adoption.',
        nextActionByOutcome=dict(supported='Run the bounded prospective policy comparison.',contradicted='Keep the current policy and inspect exact missing or unstable observations.'))


def run():
    spec=q.load(OUT.parents[2]/'spec.json');result=evaluate(q.load(checked(spec['inputs'][0])))
    q.save(OUT/'benchmark_summary.json',result)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
