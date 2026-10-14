"""Summarize fixed interventions without assigning labels to altered images."""
import json
import argparse
import hashlib
import math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import focus_evidence

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/work/TRANSITION-297'


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def decision(score):
    require(isinstance(score, (int, float)) and math.isfinite(score) and 0 <= score <= 1, 'invalid_score')
    return 0 if score <= 0.15 else 1 if score >= 0.85 else -1


def counts(labels, decisions):
    require(len(labels) == len(decisions), 'count_mismatch')
    require(all(type(x) is int and x in (0, 1) for x in labels), 'invalid_label')
    require(all(x in (-1, 0, 1) for x in decisions), 'invalid_decision')
    positive = sum(labels)
    missed = sum(y == 1 and d == 0 for y, d in zip(labels, decisions))
    false = sum(y == 0 and d == 1 for y, d in zip(labels, decisions))
    abstain = decisions.count(-1)
    emitted_unchanged = decisions.count(0)
    shared = focus_evidence.summary([dict(truth=bool(y), decision=None if d == -1 else bool(d))
                                     for y, d in zip(labels, decisions)])
    return dict(count=len(labels), changed=positive, unchanged=len(labels)-positive,
                correct=sum(y == d for y, d in zip(labels, decisions)),
                missedChanges=missed, falseChanges=false, abstentions=abstain,
                changeAbstentions=sum(y == 1 and d == -1 for y, d in zip(labels, decisions)),
                emittedUnchanged=emitted_unchanged,
                missedChangeRate=shared['missedPositive']['value'],
                falseChangeRate=shared['falsePositive']['value'],
                errorAmongUnchanged=shared['errorAmongNegativeDecisions']['value'],
                coverage=shared['coverage']['value'], sharedMetrics=shared)


def proposal_decision(score, area, rule):
    require(rule in ('all-empty', 'changed-only'), 'unknown_proposal_rule')
    require(type(area) is int and 0 <= area <= 192*128, 'invalid_area')
    original = decision(score)
    return -1 if area == 0 and (rule == 'all-empty' or original == 1) else original


def audit_proposals(rows, rule='all-empty'):
    require(rule in ('all-empty', 'changed-only'), 'unknown_proposal_rule')
    seen = set()
    roles = {}
    buckets = defaultdict(list)
    cases = []
    models = None
    for row in rows:
        key = (row['set'], row['id'])
        require(key not in seen, 'duplicate_case')
        seen.add(key)
        require(type(row['changed']) is int and row['changed'] in (0, 1), 'invalid_label')
        area = row['regions']['proposal']['area']
        require(type(area) is int and 0 <= area <= 192*128, 'invalid_area')
        if models is None:
            models = set(row['models'])
        require(set(row['models']) == models, 'model_mismatch')
        group = row.get('group')
        if group:
            require(group not in roles or roles[group] == row['role'], 'cross_role_group')
            roles[group] = row['role']
        for model, scores in row['models'].items():
            original = decision(scores['original'])
            gated = proposal_decision(scores['original'], area, rule)
            item = dict(id=row['id'], input=row['set'], group=group, role=row['role'],
                        conditions=row['conditions'], model=model, truth=row['changed'],
                        original=original, diagnostic=gated, emptyProposal=area == 0)
            cases.append(item)
            buckets[(row['set'], model)].append(item)
    output = []
    for (name, model), items in sorted(buckets.items()):
        labels = [r['truth'] for r in items]
        a = [r['original'] for r in items]
        b = [r['diagnostic'] for r in items]
        output.append(dict(input=name, model=model, original=counts(labels, a),
                           diagnostic=counts(labels, b),
                           lostCorrect=sum(x == y and z != y for y, x, z in zip(labels, a, b)),
                           caughtWrong=sum(x not in (-1, y) and z == -1 for y, x, z in zip(labels, a, b)),
                           emptyProposals=sum(r['emptyProposal'] for r in items),
                           relatedGroups=len({r['group'] for r in items if r['group']}),
                           unknownGroupCases=sum(r['group'] is None for r in items)))
    return dict(rule=rule, summaries=output, cases=cases, independentBounds=None,
                limits=['Related groups are not certified independent trials.',
                        'Native weak-effect strata lack qualified labels in this cache.',
                        'Authored disturbance results do not establish native performance.',
                        'Empty proposals cause abstention, not an unchanged label.'])


def audit_regressions(comparison):
    require(comparison['version'] == 'condition292-v1', 'comparison_version')
    result = {}
    for name, contrast in comparison['contrasts'].items():
        grouped = defaultdict(Counter)
        seen = set()
        for row in contrast['cases']:
            key = (row['input'], row['id'])
            require(key not in seen, 'duplicate_prediction')
            seen.add(key)
            y, a, b = row['changed'], row['controlDecision'], row['candidateDecision']
            require(type(y) is int and y in (0, 1), 'invalid_label')
            require(a == decision(row['controlProbability']) and b == decision(row['candidateProbability']), 'decision_mismatch')
            require(a != b, 'unchanged_case')
            gain, loss = a != y and b == y, a == y and b != y
            require(gain == row['gainedCorrect'] and loss == row['lostCorrect'], 'gain_loss_mismatch')
            bucket = grouped[(row['input'], row['group'], row['role'])]
            bucket.update(changedDecisions=1, gains=int(gain), losses=int(loss))
        for source, summary in contrast['conditions'].items():
            items = [v for k, v in grouped.items() if k[0] == source]
            require(sum(v['gains'] for v in items) == summary['gainedCorrect'], 'gains_mismatch')
            require(sum(v['losses'] for v in items) == summary['lostCorrect'], 'losses_mismatch')
            require(sum(v['changedDecisions'] for v in items) == summary['decisionChanges'], 'changes_mismatch')
        result[name] = dict(before=contrast['before'], after=contrast['after'],
                            groups=[dict(input=k[0], group=k[1], role=k[2], **v)
                                    for k, v in sorted(grouped.items(), key=lambda item: str(item[0]))])
    return result


def audit_coverage(coverage):
    require(coverage['version'] == 'coverage290-v1', 'coverage_version')
    buckets = defaultdict(lambda: dict(images=set(), groups=set(), cells=set(), entries=0))
    for row in coverage['records']:
        cell = row['cell']
        require(len(cell) == 2 and all(type(x) is int and 0 <= x <= 2 for x in cell), 'invalid_cell')
        bucket = buckets[(row['variant'], row['condition'])]
        bucket['images'].add(row['imageSHA256']); bucket['groups'].add(row['group'])
        bucket['cells'].add(tuple(cell)); bucket['entries'] += 1
    return [dict(variant=k[0], condition=k[1], uniqueImages=len(v['images']),
                 relatedGroups=len(v['groups']), endpointEntries=v['entries'],
                 cells=sorted(v['cells']), missingCells=[(x,y) for y in range(3) for x in range(3) if (x,y) not in v['cells']])
            for k,v in sorted(buckets.items())]


def run_audit(destination):
    destination = destination.resolve()
    require(destination.is_relative_to(ROOT) and not destination.exists(), 'output_collision_or_boundary')
    inputs = {}
    def read(path, expected=None):
        path = path.resolve()
        require(path.is_relative_to(ROOT), 'input_boundary')
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        require(expected is None or digest == expected, 'altered_hash')
        inputs[str(path.relative_to(ROOT))] = dict(sha256=digest, bytes=len(raw))
        return json.loads(raw)
    registration = read(OUT/'registration.json')
    require(registration['version'] == 'spatial297-v1' and registration['noiseThreshold'] == 24, 'registration_mismatch')
    spatial = read(OUT/'result.json')
    require(spatial['version'] == 'spatial297-v1' and not spatial['exclusions'], 'spatial_version_or_exclusions')
    membership = read(ROOT/registration['membership']['path'], registration['membership']['sha256'])
    native = [r for r in spatial['rows'] if r['set'] == 'native.npy']
    require([r['id'] for r in native] == registration['selectedIDs'], 'native_membership')
    for row, source in zip(native, membership['rows']):
        require(all(row[k] == source[k] for k in ('id','changed','role','group','conditions')), 'native_labels')
    for name, refs in registration['models'].items():
        evaluation = read(ROOT/refs['evaluation']['path'], refs['evaluation']['sha256'])
        for source in sorted({r['set'] for r in spatial['rows']}):
            rows = [r for r in spatial['rows'] if r['set'] == source]
            scores = evaluation['conditions'][source]['probabilities']
            require(len(rows) == len(scores), 'cache_count')
            require(all(r['models'][name]['original'] == p for r,p in zip(rows,scores)), 'cache_score')
    comparison = read(ROOT/'reports/work/TRANSITION-292/comparison.json')
    for ref in comparison['inputs'].values():
        read(ROOT/ref['path'], ref['sha256'])
    coverage = read(ROOT/'reports/work/TRANSITION-290/coverage.json')
    read(ROOT/coverage['membership']['path'], coverage['membership']['sha256'])
    result = dict(version='focus301-retained-audit-v1', proposals=audit_proposals(spatial['rows']),
                  changedOnlyProposals=audit_proposals(spatial['rows'], 'changed-only'),
                  regressions=audit_regressions(comparison), coverage=audit_coverage(coverage),
                  inputs=inputs, runnerSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  inference=False, training=False, rolesChanged=False, productionEligible=False)
    raw = json.dumps(result, indent=2, allow_nan=False).encode()
    require(len(raw) <= 128*1024**2, 'output_budget')
    destination.mkdir()
    with (destination/'result.json').open('xb') as file:
        file.write(raw)
    print(json.dumps(dict(output=str(destination), bytes=len(raw), summaries=result['proposals']['summaries']), indent=2))


def summarize(rows):
    results = {}
    for name in sorted({r['set'] for r in rows}):
        group = [r for r in rows if r['set'] == name]
        positives = [r for r in group if r['changed']]
        entry = dict(count=len(group), changed=len(positives),
                     emptyProposals=sum(r['regions']['proposal']['area'] == 0 for r in group),
                     changedWithEmptyProposal=sum(r['regions']['proposal']['area'] == 0 for r in positives),
                     meanProposalFrameFraction=float(np.mean([r['regions']['proposal']['area'] / (192*128) for r in group])),
                     models={})
        coverage = [r['regions']['proposal']['observedOverlap'] / r['regions']['observed']['area']
                    for r in positives if 'observed' in r['regions']]
        entry['medianChangedObservedCoverage'] = None if not coverage else float(np.median(coverage))
        for model in sorted(group[0]['models']):
            false = [r for r in group if not r['changed'] and r['models'][model]['original'] >= 0.85]
            shifts = {}
            for changed in (0, 1):
                subset = [r for r in group if r['changed'] == changed]
                if not subset:
                    continue
                shifts[str(changed)] = {key: float(np.mean([
                    r['models'][model]['interventions'][key] - r['models'][model]['original'] for r in subset]))
                    for key in subset[0]['models'][model]['interventions']}
            entry['models'][model] = dict(originalFalseChanges=len(false),
                falseChangesWithEmptyProposal=sum(r['regions']['proposal']['area'] == 0 for r in false),
                meanProbabilityShiftByOriginalLabel=shifts)
        results[name] = entry
    return dict(version='spatial297-summary-v1', sets=results, accuracyOnAlteredImages=False,
                deploymentDecision='No change; test weak native effects before any proposal gate')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit-output', type=Path)
    args = parser.parse_args()
    if args.audit_output:
        run_audit(args.audit_output)
    else:
        result = summarize(json.loads((OUT / 'result.json').read_text())['rows'])
        with (OUT / 'summary.json').open('x') as file:
            json.dump(result, file, indent=2)
