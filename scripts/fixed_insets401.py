"""Fit one mapping on named groups and report separate evaluation groups."""
import copy
import math
import statistics
import time
import research_queue as q
from template_adapters395 import document, resolve_inputs
from template_analysis397 import matched

OUT = None


def partition(rows, policy):
    q.require(policy.get('version') == 'fixed-inset-groups-v1', 'partition_version')
    fit, evaluate = policy['fitGroups'], policy['evaluationGroups']
    q.require(fit and evaluate and len(set(fit)) == len(fit) and len(set(evaluate)) == len(evaluate), 'partition_groups')
    q.require(not set(fit) & set(evaluate), 'partition_overlap')
    q.require(set(fit) | set(evaluate) == {r['group'] for r in rows}, 'partition_membership')
    q.require(rows and len({r['id'] for r in rows}) == len(rows), 'partition_rows')
    hashes, roles = {}, {}
    for row in rows:
        group = row['group']
        q.require(row['role'] in ('development', 'retained'), 'audit_locked')
        q.require(roles.setdefault(group, row['role']) == row['role'], 'group_role_conflict')
        q.require(group not in fit or row['role'] == 'development', 'fit_role')
        arm = 'fit' if group in fit else 'evaluation'
        q.require(hashes.setdefault(row['sha256'], arm) == arm, 'duplicate_across_partition')
    return set(fit), set(evaluate)


def correct(proposals, geometry, policy):
    fit, _ = partition(proposals['rows'], policy)
    indexed = {r['id']: r for r in geometry['rows']}
    q.require(len(indexed) == len(geometry['rows']) and set(indexed) == {r['id'] for r in proposals['rows']}, 'geometry_membership')
    for row in proposals['rows']:
        q.require(all(row[k] == indexed[row['id']][k] for k in ('group', 'role', 'profile')), 'geometry_identity')
    eligible = [r for r in geometry['rows'] if r['group'] in fit and r['profile'] == 'hcf' and 'ringInsetsPixels' in r]
    groups = sorted({r['group'] for r in eligible})
    q.require(len(groups) >= 3, 'insufficient_fit_groups')
    for row in eligible:
        values = row['ringInsetsPixels']
        q.require(len(values) == 4 and all(type(v) in (int, float) and math.isfinite(v) for v in values), 'invalid_insets')
    medians = [[statistics.median(r['ringInsetsPixels'][i] for r in eligible if r['group'] == g) for i in range(4)] for g in groups]
    offsets = [statistics.median(row[i] for row in medians) for i in range(4)]
    q.require(all(v <= 0 for v in offsets), 'expansion_not_approved')
    result = copy.deepcopy(proposals)
    result['rows'] = [copy.deepcopy(row) for row in proposals['rows']]
    for row in result['rows']:
        if row['profile'] != 'hcf':
            continue
        boxes = []
        for box in row['prediction']['candidates']:
            q.require(len(box) == 4 and all(type(v) in (int, float) and math.isfinite(v) for v in box), 'invalid_box')
            x, y, w, h = box
            left, top, right, bottom = offsets
            changed = [x-left, y-top, w+left+right, h+top+bottom]
            q.require(x >= 0 and y >= 0 and changed[2] > 0 and changed[3] > 0, 'collapsed_box')
            boxes.append(changed)
        row['prediction']['candidates'] = boxes
    result.update(method='TTR-outer-ring-v2-fixed-insets', modelAccepted=False,
                  limitation='One development-fitted mapping. Separate inspected groups are not an untouched audit.')
    return result, dict(version='fixed-inset-map-v1', offsets=offsets, fitGroups=sorted(fit), supportedFitGroups=groups,
                        evaluationGroups=policy['evaluationGroups'], modelAccepted=False)


def compare(baseline, candidate, policy):
    fit, evaluate = partition(baseline['rows'], policy)
    matched(baseline, candidate)
    reports = {}
    for name, groups in [('fit', fit), ('evaluation', evaluate)]:
        reports[name] = matched(dict(rows=[r for r in baseline['rows'] if r['group'] in groups]),
                                dict(rows=[r for r in candidate['rows'] if r['group'] in groups]))
    standard = [r for r in baseline['rows'] if r['profile'] == 'standard']
    indexed = {r['id']: r for r in candidate['rows']}
    return dict(version='fixed-inset-comparison-v1', partitions=reports, modelAccepted=False,
                standardPredictionsIdentical=all(r['prediction'] == indexed[r['id']]['prediction'] for r in standard),
                limitation='Inspected groups only. Role and group separation do not establish family independence.')


def run():
    contract = q.load(OUT.parents[2]/'spec.json')['template']; start = time.monotonic()
    try:
        inputs = {k: document(v) for k, v in resolve_inputs(contract, OUT).items()}
        if contract['id'] == 'T31':
            result, mapping = correct(inputs['proposals'], inputs['geometry'], inputs['partition'])
            q.save(OUT/'comparison.json', result); q.save(OUT/'mapping.json', mapping)
        else:
            q.require(contract['id'] == 'T32', 'operation')
            q.save(OUT/'comparison.json', compare(inputs['baseline'], inputs['candidate'], inputs['partition']))
        q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
            dict(path=str(p.relative_to(OUT)), sha256=q.digest(p)) for p in sorted(OUT.rglob('*')) if p.is_file()]))
        q.save(OUT/'template-result.json', dict(execution='complete', modelAccepted=False, seconds=time.monotonic()-start))
    except Exception as error:
        q.save(OUT/'template-result.json', dict(execution='failed', code=str(error)[:500], modelAccepted=False)); raise
