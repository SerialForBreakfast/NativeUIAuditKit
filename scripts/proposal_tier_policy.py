"""Compare fixed confidence tiers from verified full-screen reports. No new inference."""
import math
from collections import Counter
import research_queue as q
from cached_selection405 import verified_report, SUCCESS, OUTCOMES
from template_adapters395 import document, resolve_inputs

OUT = None


def compare(high, low, policy):
    q.require(policy in ('unchanged', 'high-first'), 'tier_policy')
    for report in (high, low):
        q.require(report.get('version') == 'detector-focus-pilot-v1' and
                  report.get('threshold') == .85 and report.get('matchingIoU') == .5 and
                  report.get('duplicateIoU') == .5, 'tier_version')
    q.require(set(high['inputs']) == set(low['inputs']) and all(
        high['inputs'][k] == low['inputs'][k] for k in high['inputs'] if k != 'scorecard'), 'tier_inputs')
    a, b = high['rows'], low['rows']
    q.require(a and len({r['id'] for r in a}) == len(a) and
              [r['id'] for r in a] == [r['id'] for r in b], 'tier_membership')
    rows = []
    for old, new in zip(a, b):
        q.require(all(old[k] == new[k] for k in ('id','sha256','group','profile','noFocus')), 'tier_identity')
        q.require(old['arms']['known-box'] == new['arms']['known-box'], 'tier_known_reference')
        for arm in ('detector', 'detector-plus-ring'):
            for model in ('baseline', 'candidate'):
                values = []
                for row in (old, new):
                    data = row['arms'][arm]; value = data['models'][model]; scores = value['scores']
                    q.require(len(scores) == len(data['candidates']) and all(
                        type(s) in (int,float) and math.isfinite(s) and 0 <= s <= 1 for s in scores), 'tier_scores')
                    count = sum(s >= .85 for s in scores)
                    q.require(value['aboveThreshold'] == count and value['outcome'] in OUTCOMES, 'tier_outcome')
                    if row['noFocus']:
                        q.require(value['outcome'] == ('false-selection' if count == 1 else 'correct-abstention'), 'tier_no_focus')
                    else:
                        q.require(value['outcome'] in ('correct','wrong','miss') and
                                  (value['outcome'] == 'miss') == (count != 1), 'tier_focus')
                    values.append(value)
                prior, lower = values
                # Selection uses scores only. Recorded truth affects evaluation, never branch choice.
                use_low = policy == 'high-first' and prior['aboveThreshold'] != 1
                result = lower['outcome'] if use_low else prior['outcome']
                rows.append(dict(id=old['id'], group=old['group'], profile=old['profile'], noFocus=old['noFocus'],
                    arm=arm, model=model, source='low' if use_low else 'high', reference=prior['outcome'], outcome=result,
                    gain=prior['outcome'] not in SUCCESS and result in SUCCESS,
                    loss=prior['outcome'] in SUCCESS and result not in SUCCESS,
                    newWrong=prior['outcome'] not in ('wrong','false-selection') and result in ('wrong','false-selection')))
    slices = {}
    for profile in ('standard','hcf'):
        for arm in ('detector','detector-plus-ring'):
            for model in ('baseline','candidate'):
                subset = [r for r in rows if (r['profile'],r['arm'],r['model']) == (profile,arm,model)]
                slices['/'.join((profile,arm,model))] = dict(frames=len(subset),groups=len({r['group'] for r in subset}),
                    outcomes=dict(Counter(r['outcome'] for r in subset)),
                    gains=[r['id'] for r in subset if r['gain']], lostPriorSuccesses=[r['id'] for r in subset if r['loss']],
                    newWrongSelections=[r['id'] for r in subset if r['newWrong']])
    key = lambda r: '/'.join((r['profile'],r['arm'],r['model'],r['id']))
    return dict(version='proposal-tier-policy-v1',policy=policy,rows=rows,slices=slices,
        gains=[key(r) for r in rows if r['gain']],lostPriorSuccesses=[key(r) for r in rows if r['loss']],
        newWrongSelections=[key(r) for r in rows if r['newWrong']],modelAccepted=False,
        limitation='Inspected development data. Models, arms, and profile counterparts are related comparisons, not independent trials.')


def run():
    cfg=q.load(OUT.parents[2]/'spec.json')['template'];refs=resolve_inputs(cfg,OUT)
    high=verified_report(dict(report=refs['highReport'],result=refs['highReceipt']))
    low=verified_report(dict(report=refs['lowReport'],result=refs['lowReceipt']))
    cards=[document(r['inputs']['scorecard']) for r in (high,low)]
    q.require(cards[0]['identity'] == cards[1]['identity'] and cards[0]['inputs'] == cards[1]['inputs'], 'tier_detector')
    q.require(cards[0]['settings'] == dict(cards[1]['settings'],confidence=.5) and
              cards[1]['settings']['confidence'] == .25, 'tier_thresholds')
    artifact=document(high['inputs']['capture'])
    q.require(artifact['plan'].get('trainingEligible') is False and artifact['plan']['cases'] and
              all(c['role']=='development' for c in artifact['plan']['cases']), 'tier_role')
    result=compare(high,low,cfg['parameters']['policy']);result['inputs']=refs
    q.save(OUT/'benchmark_summary.json',result)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
