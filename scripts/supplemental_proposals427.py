"""Compare baseline-first detector evidence without changing runtime selection."""
import research_queue as q
from template_inputs398 import checked
from cached_selection405 import verified_report
from proposal_tier_policy import compare

OUT = None


def load(ref):
    q.require(set(ref) == {'report', 'result', 'spec'}, 'supplemental_reference')
    report = verified_report({k: ref[k] for k in ('report', 'result')})
    spec = q.load(checked(ref['spec']))
    receipt = q.load(checked(ref['result']))
    q.require(receipt['specSHA256'] == q.text_digest(spec), 'supplemental_spec')
    q.require(spec.get('template', {}).get('id') == 'T57', 'supplemental_producer')
    return report


def evaluate(baseline, supplemental):
    cards = [q.load(checked(r['inputs']['scorecard'])) for r in (baseline, supplemental)]
    q.require(cards[0]['inputs'] == cards[1]['inputs'], 'supplemental_labels')
    q.require(cards[0]['settings'] == cards[1]['settings'], 'supplemental_settings')
    q.require(cards[0]['frames'] == cards[1]['frames'], 'supplemental_frames')
    identities = [card['identity']['detector'] for card in cards]
    q.require(identities[0]['weightsSHA256'] != identities[1]['weightsSHA256'], 'supplemental_same_detector')
    q.require({k:v for k,v in identities[0].items() if k != 'weightsSHA256'} ==
              {k:v for k,v in identities[1].items() if k != 'weightsSHA256'}, 'supplemental_runtime')
    capture = q.load(checked(baseline['inputs']['capture']))
    q.require(capture['plan'].get('trainingEligible') is False and capture['plan']['cases'] and
              all(c['role'] == 'development' for c in capture['plan']['cases']), 'supplemental_role')
    # Reuse the tested score-only branch rule. Never use truth to select a detector.
    result = compare(baseline, supplemental, 'high-first')
    result['version'] = 'supplemental-proposal-comparison-v1'
    result['policy'] = 'baseline-single-selection-else-supplemental'
    result['detectors'] = {'baseline': identities[0], 'supplemental': identities[1]}
    for row in result['rows']:
        row['source'] = 'baseline' if row['source'] == 'high' else 'supplemental'
    result['regressionGatePassed'] = not result['lostPriorSuccesses'] and not result['newWrongSelections']
    result['modelAccepted'] = False
    result['limitation'] += ' This switches between scored proposal sets; it does not merge boxes or correct baseline single wrong selections.'
    return result


def run():
    spec = q.load(OUT.parents[2] / 'spec.json')
    ref = next(s['from'] for s in spec['stage'] if s['to'] == 'bundle.json')
    source = checked(ref)
    q.require(q.digest(source) == q.digest(OUT / 'bundle.json'), 'supplemental_stage_changed')
    bundle = q.load(source)
    q.require(set(bundle) == {'version', 'baseline', 'supplemental'} and
              bundle['version'] == 'supplemental-proposals-v1', 'supplemental_bundle')
    result = evaluate(load(bundle['baseline']), load(bundle['supplemental']))
    q.save(OUT / 'benchmark_summary.json', result)
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path='benchmark_summary.json', sha256=q.digest(OUT / 'benchmark_summary.json'))]))
