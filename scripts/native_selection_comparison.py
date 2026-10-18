"""Compare verified T37 reports. Keep no-focus outcomes and model identities explicit."""
import math
from pathlib import Path
from collections import Counter
import research_queue as q
from cached_selection405 import verified_report, ARMS, OUTCOMES, SUCCESS
from template_adapters395 import document, resolve_inputs
from template_inputs398 import checked

OUT = None


def compare(left, right):
    q.require(left.get('threshold') == right.get('threshold') == .85, 'comparison_threshold')
    a, b = left['rows'], right['rows']
    q.require(a and len({r['id'] for r in a}) == len(a), 'comparison_duplicate_or_empty')
    q.require([r['id'] for r in a] == [r['id'] for r in b], 'comparison_membership')
    rows = []
    for old, new in zip(a, b):
        q.require(all(old[k] == new[k] for k in ('id', 'group', 'profile', 'noFocus')), 'comparison_identity')
        q.require(old['profile'] in ('standard', 'hcf') and type(old['noFocus']) is bool, 'comparison_profile')
        q.require(set(old['arms']) == set(new['arms']) == set(ARMS), 'comparison_arms')
        for arm in ARMS:
            x, y = old['arms'][arm], new['arms'][arm]
            q.require(x['boxes'] == y['boxes'], 'comparison_geometry')
            for value in (x, y):
                scores = value['scores']; outcome = value['outcome']
                q.require(len(scores) == len(value['boxes']) and all(
                    type(s) in (int, float) and math.isfinite(s) and 0 <= s <= 1 for s in scores), 'comparison_scores')
                q.require(outcome in OUTCOMES, 'comparison_outcome')
                count = sum(s >= .85 for s in scores)
                if old['noFocus']:
                    q.require(outcome == ('false-selection' if count == 1 else 'correct-abstention'), 'comparison_no_focus')
                else:
                    q.require(outcome in {'correct', 'wrong', 'miss'} and (outcome == 'miss') == (count != 1), 'comparison_focus')
            rows.append(dict(id=old['id'], group=old['group'], profile=old['profile'], noFocus=old['noFocus'], arm=arm,
                baseline=x['outcome'], candidate=y['outcome'], gain=x['outcome'] not in SUCCESS and y['outcome'] in SUCCESS,
                loss=x['outcome'] in SUCCESS and y['outcome'] not in SUCCESS,
                newWrong=x['outcome'] not in {'wrong', 'false-selection'} and y['outcome'] in {'wrong', 'false-selection'}))
    slices = {}
    for profile in ('standard', 'hcf'):
        slices[profile] = {}
        for arm in ARMS:
            subset = [r for r in rows if r['profile'] == profile and r['arm'] == arm]
            slices[profile][arm] = dict(frames=len(subset), groups=len({r['group'] for r in subset}),
                baseline=dict(Counter(r['baseline'] for r in subset)), candidate=dict(Counter(r['candidate'] for r in subset)),
                gains=[r['id'] for r in subset if r['gain']], losses=[r['id'] for r in subset if r['loss']],
                newWrongSelections=[r['id'] for r in subset if r['newWrong']])
    return dict(rows=rows, slices=slices, modelAccepted=False)


def load_source(ref):
    q.require(set(ref) == {'report', 'result', 'spec'}, 'comparison_reference')
    report = verified_report({k: ref[k] for k in ('report', 'result')})
    spec = document(ref['spec']); receipt = document(ref['result'])
    q.require(receipt['specSHA256'] == q.text_digest(spec), 'comparison_spec')
    q.require(spec['template']['id'] == 'T37', 'comparison_template')
    output = checked(ref['result']).parent/'out'
    inputs = resolve_inputs(spec['template'], output)
    capture = document(inputs['capture'])
    q.require(capture['plan'].get('trainingEligible') is False and capture['plan']['cases'] and
              all(c['role'] == 'development' for c in capture['plan']['cases']), 'comparison_role')
    return report, inputs


def run():
    cfg = q.load(OUT.parents[2]/'spec.json')['template']; refs = resolve_inputs(cfg, OUT)
    bundle = document(refs['bundle'])
    q.require(bundle.get('version') == 'native-selection-comparisons-v1' and 0 < len(bundle['pairs']) <= 32, 'comparison_bundle')
    results = []
    q.require(len({p['id'] for p in bundle['pairs']}) == len(bundle['pairs']), 'comparison_duplicate_pair')
    for pair in bundle['pairs']:
        left, a = load_source(pair['baseline']); right, b = load_source(pair['candidate'])
        q.require(set(a) == set(b), 'comparison_inputs')
        q.require(all((a[k]['path'], a[k]['sha256']) == (b[k]['path'], b[k]['sha256'])
                      for k in a if k != 'model'), 'comparison_inputs')
        result = compare(left, right)
        result.update(id=pair['id'], models={name: data['model'] for name, data in [('baseline', a), ('candidate', b)]})
        results.append(result)
    q.save(OUT/'benchmark_summary.json', dict(version='native-selection-comparisons-v1', comparisons=results,
        modelAccepted=False, sources=refs, limitation='Inspected development groups. Proposal arms and related profiles are not independent trials.'))
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path='benchmark_summary.json', sha256=q.digest(OUT/'benchmark_summary.json'))]))
