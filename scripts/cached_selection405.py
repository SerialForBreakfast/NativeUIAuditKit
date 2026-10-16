"""Explain cached native selections without changing predictions or labels."""
from collections import Counter
import math
import research_queue as q
from template_adapters395 import document, resolve_inputs

OUT = None
ARMS = ('known-box', 'raw-proposal', 'mapped-proposal')
OUTCOMES = {'correct', 'miss', 'wrong', 'correct-abstention', 'false-selection'}
SUCCESS = {'correct', 'correct-abstention'}


def analyze(pairs):
    """Each pair contains a selection report and its matching geometry report."""
    rows, seen = [], set()
    for selection, geometry in pairs:
        q.require(selection.get('threshold') == .85, 'threshold_changed')
        a, b = selection['rows'], geometry['rows']
        q.require(a and len(a) == len(b), 'membership_count')
        for row, spatial in zip(a, b):
            q.require(all(row[k] == spatial[k] for k in ('id', 'group', 'profile', 'noFocus')), 'row_identity')
            q.require(row['id'] not in seen, 'duplicate_frame')
            seen.add(row['id'])
            q.require(row['profile'] in ('standard', 'hcf') and type(row['noFocus']) is bool, 'profile_or_focus')
            q.require(set(row['arms']) == set(ARMS), 'arm_membership')
            details = {}
            for name in ARMS:
                arm = row['arms'][name]
                scores, boxes, outcome = arm['scores'], arm['boxes'], arm['outcome']
                q.require(outcome in OUTCOMES, 'unknown_outcome')
                q.require(len(scores) == len(boxes), 'score_count')
                q.require(all(type(s) in (int, float) and math.isfinite(s) and 0 <= s <= 1 for s in scores), 'invalid_score')
                q.require(all(len(box) == 4 and all(type(x) in (int, float) and math.isfinite(x) for x in box)
                              and box[2] > 0 and box[3] > 0 for box in boxes), 'invalid_box')
                selected = sum(s >= .85 for s in scores)
                if row['noFocus']:
                    q.require(outcome == ('false-selection' if selected == 1 else 'correct-abstention'), 'no_focus_outcome')
                    reason = 'false_selection' if selected == 1 else 'ambiguous_abstention' if selected > 1 else 'below_threshold_abstention'
                else:
                    q.require(outcome in {'correct', 'miss', 'wrong'}, 'focused_outcome')
                    q.require((outcome == 'miss') == (selected != 1), 'selection_outcome')
                    overlap = None if name == 'known-box' else spatial['rawBestIoU' if name == 'raw-proposal' else 'mappedBestIoU']
                    q.require(overlap is None and name == 'known-box' or type(overlap) in (int, float)
                              and math.isfinite(overlap) and 0 <= overlap <= 1, 'invalid_overlap')
                    reason = ('correct' if outcome == 'correct' else 'no_proposals' if not boxes
                              else 'insufficient_overlap' if overlap is not None and overlap < .5
                              else 'multiple_above_threshold' if selected > 1
                              else 'below_threshold' if selected == 0 else 'wrong_selection')
                    if outcome == 'correct' and overlap is not None:
                        q.require(overlap >= .5, 'correct_without_overlap')
                details[name] = dict(outcome=outcome, reason=reason, proposals=len(boxes), aboveThreshold=selected,
                                     scores=scores, boxes=boxes)
            q.require(row['profile'] != 'standard' or row['arms']['raw-proposal'] == row['arms']['mapped-proposal'], 'standard_changed')
            rows.append(dict(id=row['id'], group=row['group'], profile=row['profile'], noFocus=row['noFocus'],
                             rawBestIoU=spatial['rawBestIoU'], mappedBestIoU=spatial['mappedBestIoU'], arms=details,
                             gain=row['arms']['raw-proposal']['outcome'] not in SUCCESS and row['arms']['mapped-proposal']['outcome'] in SUCCESS,
                             loss=row['arms']['raw-proposal']['outcome'] in SUCCESS and row['arms']['mapped-proposal']['outcome'] not in SUCCESS))
    q.require(rows, 'empty_comparison')
    slices = {}
    for profile in ('standard', 'hcf'):
        subset = [r for r in rows if r['profile'] == profile]
        slices[profile] = dict(frames=len(subset), groups=len({r['group'] for r in subset}),
                              noFocusFrames=sum(r['noFocus'] for r in subset),
                              arms={arm: dict(outcomes=dict(Counter(r['arms'][arm]['outcome'] for r in subset)),
                                              reasons=dict(Counter(r['arms'][arm]['reason'] for r in subset))) for arm in ARMS},
                              gains=[r['id'] for r in subset if r['gain']], losses=[r['id'] for r in subset if r['loss']])
    return dict(version='cached-selection-diagnosis-v1', rows=rows, slices=slices, modelAccepted=False,
                threshold=.85, matchingIoU=.5, frames=len(rows), groups=len({r['group'] for r in rows}),
                nextAction='Repair proposal coverage and diagnose each lost success before more crop training.',
                limitation='Cached inspected development groups. Best overlap does not identify which proposal received a score. No causal mapping fix is inferred.')


def verified_report(entry):
    q.require(set(entry) == {'report', 'result'}, 'report_reference')
    receipt = document(entry['result'])
    q.require(receipt['status'] == 'complete', 'producer_incomplete')
    ref = entry['report']
    prefix = entry['result']['path'].rsplit('/', 1)[0] + '/out/'
    q.require(ref['path'].startswith(prefix), 'producer_scope')
    name = ref['path'][len(prefix):]
    q.require(any(o['path'] == name and o['sha256'] == ref['sha256'] for o in receipt['outputs']), 'producer_hash')
    return document(ref)


def run():
    cfg = q.load(OUT.parents[2] / 'spec.json')['template']
    refs = resolve_inputs(cfg, OUT)
    bundle = document(refs['bundle'])
    q.require(set(bundle) == {'version', 'role', 'pairs'} and bundle['version'] == 'cached-selection-inputs-v1', 'bundle_version')
    q.require(bundle['role'] == 'development' and 1 <= len(bundle['pairs']) <= 32, 'bundle_scope')
    pairs = []
    for pair in bundle['pairs']:
        q.require(set(pair) == {'selection', 'geometry'}, 'pair_fields')
        pairs.append((verified_report(pair['selection']), verified_report(pair['geometry'])))
    report = analyze(pairs)
    report['sources'] = bundle['pairs']
    q.save(OUT / 'benchmark_summary.json', report)
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path='benchmark_summary.json', sha256=q.digest(OUT / 'benchmark_summary.json'))]))
