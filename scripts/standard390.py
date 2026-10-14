"""Review retained Standard predictions without changing models or data roles."""
from collections import Counter, defaultdict
import math

import research_queue as q

OUT = None


def decision(value):
    q.require(type(value) in (float, int) and math.isfinite(value) and 0 <= value <= 1, 'invalid_probability')
    return 1 if value >= .85 else 0 if value <= .15 else None


def compare(control, candidate):
    q.require(control['sets'].keys() == candidate['sets'].keys(), 'set_membership_changed')
    cases = []
    seen = set()
    for name, old in control['sets'].items():
        new = candidate['sets'][name]
        q.require(old['rows'] and old['rows'] == new['rows'], 'case_membership_changed')
        q.require(old['originalProbabilities'] == new['originalProbabilities'], 'baseline_changed')
        arrays = [old['originalProbabilities'], old['probabilities']['gamma'], new['probabilities']['gamma']]
        q.require(all(len(x) == len(old['rows']) for x in arrays), 'prediction_count')
        for row, baseline, a, b in zip(old['rows'], *arrays):
            key = (name, row['id'])
            q.require(key not in seen, 'duplicate_case')
            seen.add(key)
            q.require(type(row['changed']) is int and row['changed'] in (0, 1), 'invalid_label')
            q.require(row.get('group') and row.get('role') and row.get('sourceDomain'), 'missing_role_or_group')
            q.require(row['role'] not in ('audit', 'final', 'final-audit'), 'final_audit_refused')
            scores = dict(baseline=baseline, control=a, notification=b)
            correct = {k: decision(v) == row['changed'] for k, v in scores.items()}
            margins = {k: v - .85 if row['changed'] else .15 - v for k, v in scores.items()}
            cases.append(dict(set=name, id=row['id'], group=row['group'], role=row['role'],
                sourceDomain=row['sourceDomain'], condition=row['condition'], layout=row.get('layout'),
                changed=row['changed'], scores=scores, correct=correct, margins=margins,
                candidateLoss=correct['baseline'] and not correct['notification'],
                controlLoss=correct['baseline'] and not correct['control'],
                candidateGain=not correct['baseline'] and correct['notification']))
    groups = defaultdict(list)
    for row in cases:
        groups[(row['role'], row['sourceDomain'], row['condition'])].append(row)
    slices = []
    for key, members in sorted(groups.items()):
        counts = {}
        for arm in ('baseline', 'control', 'notification'):
            counts[arm] = dict(correct=sum(r['correct'][arm] for r in members),
                falseChanges=sum(r['changed'] == 0 and decision(r['scores'][arm]) == 1 for r in members),
                missedChanges=sum(r['changed'] == 1 and decision(r['scores'][arm]) != 1 for r in members),
                abstentions=sum(decision(r['scores'][arm]) is None for r in members))
        slices.append(dict(role=key[0], sourceDomain=key[1], condition=key[2], count=len(members),
            recordedGroups=len({r['group'] for r in members}), counts=counts,
            lost=sum(r['candidateLoss'] for r in members), gained=sum(r['candidateGain'] for r in members),
            sharedLosses=sum(r['candidateLoss'] and r['controlLoss'] for r in members),
            candidateOnlyLosses=sum(r['candidateLoss'] and not r['controlLoss'] for r in members)))
    return dict(cases=cases, slices=slices, models=dict(control=control['configuration']['models'],
        notification=candidate['configuration']['models']), modelAccepted=False,
        limitation='Recorded groups can share ancestry. Training rows are not development accuracy. No thresholds change.')


def read_dependencies():
    refs = []
    docs = {}
    for dep in q.load(OUT / 'dependencies.json'):
        refs.extend(dep['outputs'])
        docs[dep['job']] = []
        for ref in dep['outputs']:
            path = q.local_path(q.ROOT, ref['path'])
            q.require(q.digest(path) == ref['sha256'], 'dependency_changed')
            docs[dep['job']].append(q.load(path))
    q.save(OUT / 'sources.json', refs)
    return docs


def run():
    config = q.load(OUT / 'config.json')
    docs = read_dependencies()
    results = []
    for control, candidate in config['pairs']:
        a, = docs[control]
        b, = docs[candidate]
        results.append(dict(controlJob=control, candidateJob=candidate, **compare(a, b)))
    q.save(OUT / 'review.json', dict(version='standard390-review-v1', comparisons=results,
        modelAccepted=False, productionChanged=False, finalAuditOpened=False,
        nextDecision=config['decision']))


def detector_gaps(report, inputs):
    q.require(report['partition'] == 'development' and report['trainingEligible'] is False, 'detector_data_role')
    frames = {f['sha256']: f for f in inputs['frames']}
    q.require(len(frames) == len(inputs['frames']) == len(report['frames']), 'detector_membership')
    result = defaultdict(Counter)
    missing = []
    seen = set()
    for frame in report['frames']:
        q.require(frame['image'] in frames and frame['image'] not in seen, 'detector_image_membership')
        seen.add(frame['image'])
        truth = {c['id']: c for c in frames[frame['image']]['controls']}
        q.require(len(truth) == len(frame['controls']) and {c['id'] for c in frame['controls']} == truth.keys(), 'detector_control_membership')
        for c in frame['controls']:
            counts = result[c['role']]
            counts['reviewed'] += 1
            counts['missed'] += not c['localized']
            counts['localized'] += c['localized']
            counts['roleMismatchOnLocalized'] += c['localized'] and c['predictedRole'] != c['role']
            if not c['localized'] or c['predictedRole'] != c['role']:
                missing.append(dict(image=frame['image'], id=c['id'], role=c['role'],
                    bounds=truth[c['id']]['bounds'], localized=c['localized'], predictedRole=c['predictedRole']))
    return dict(byRole=dict(result), cases=missing, focusOutcomes=dict(Counter(f['focusOutcome'] for f in report['frames'])),
        sourceDomain='retained-real-app-development', osFocusStyle='not_verified_in_this_report',
        falsePositiveRate=None, independentGroups=None,
        limitation='Unmatched predictions lack exhaustive labels. Class names need taxonomy review; mismatches are not automatically label errors.')


def prepare():
    config = q.load(OUT / 'config.json')
    docs = read_dependencies()
    loaded = {}
    for ref in config['externalEvidence']:
        path = q.local_path(q.ROOT, ref['path'])
        q.require(q.digest(path) == ref['sha256'], 'external_evidence_changed')
        loaded[ref['path']] = q.load(path)
    report = loaded[config['scorecard']]
    inputs = loaded[report['inputs']['path']]
    q.require(q.digest(q.ROOT / report['inputs']['path']) == report['inputs']['sha256'], 'scorecard_input_changed')
    for ref in report['rawPredictions']:
        q.require(q.digest(q.ROOT / ref['path']) == ref['sha256'], 'raw_prediction_changed')
        q.require(ref['path'] in loaded, 'raw_prediction_missing')
    reviews = [d for values in docs.values() for d in values]
    q.require(len(reviews) == 4, 'missing_comparison')
    losses = [dict(controlJob=c['controlJob'], candidateJob=c['candidateJob'], **r)
        for doc in reviews for c in doc['comparisons'] for r in c['cases'] if r['candidateLoss']]
    q.save(OUT / 'preparation.json', dict(version='standard390-preparation-v1',
        detector=detector_gaps(report, inputs), retainedLosses=losses,
        externalEvidence=config['externalEvidence'], modelAccepted=False, productionChanged=False,
        nextSteps=[
            'Review detector misses by class and body size. Prepare matched Standard capture recipes for supported gaps.',
            'Preserve every listed success in later candidate comparisons. Do not tune thresholds to remove a reported loss.',
            'Use completed control seeds before attributing shared failures to notification training.',
            'Keep OS profile uncertainty separate from verified Standard data. Do not use this report as training admission.'],
        limitation='This report prepares data requests. It does not generate data, train a model, or establish deployment accuracy.'))
