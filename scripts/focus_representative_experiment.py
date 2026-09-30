"""Development-only representative checkpoint selection. Preparation never loads models."""
import argparse
from collections import Counter, defaultdict
import json
import math
import re

import focus_appearance_experiment as appearance
import focus_mixed_assembly as a
import focus_retention_experiment as retention
import focus_training_extension as extension
from focus_dataset_contract import ROOT, digest, local, pixel_digest, validate_manifest
from focus_representative_validation import stratum, summarize

VERSION = 'focus-representative-experiment-v1'
INPUT = 'focus-representative-input-v1'
FORMAT = 'focus-representative-preflight-v1'
POLICY = 'minimum-balanced-real-bce-guarded-earliest-tie'
LANES = ('buttons', 'tabs', 'artwork', 'rows')
FLOORS = {'buttons': (0, 0), 'tabs': (0, 0), 'artwork': (1, 9), 'rows': (2, 0), 'other': (0, 0)}
require = appearance.require


def checked_pixels(ref):
    a.checked({k: ref[k] for k in ('path', 'sha256')})
    require(pixel_digest(ROOT, ref) == ref['pixelSHA256'], 'changed_pixels')


def objective_weights(rows):
    require(rows and len({r['id'] for r in rows}) == len(rows), 'invalid_membership')
    labels = {}
    groups = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    weights = {r['id']: 0. for r in rows}
    for r in rows:
        require(type(r['label']) is int and r['label'] in (0, 1), 'invalid_label')
        pix = r['pixelSHA256']
        require(pix not in labels or labels[pix] == r['label'], 'conflicting_pixel_labels')
        labels[pix] = r['label']
        lane = stratum(r)
        require(lane in FLOORS, 'unsupported_stratum')
        require(isinstance(r['family'], str) and r['family'], 'missing_family')
        if lane in LANES:
            groups[lane, r['label']][r['family']][pix].append(r['id'])
    for lane in LANES:
        for label in (0, 1):
            families = groups[lane, label]
            require(bool(families), 'missing_required_selection_bucket')
            for pixels in families.values():
                for ids in pixels.values():
                    for sid in ids:
                        weights[sid] = .125 / len(families) / len(pixels) / len(ids)
    require(math.isclose(sum(weights.values()), 1), 'invalid_objective_mass')
    return weights


def selection_metrics(predictions, rows, selection):
    require(selection['policy'] == POLICY and selection['threshold'] == .85, 'invalid_selection_policy')
    require(len({r['id'] for r in rows}) == len(rows) and
            [r['id'] for r in rows] == [p.get('id') for p in predictions], 'prediction_membership')
    for r, p in zip(rows, predictions):
        q = p.get('probability')
        require(type(q) in (float, int) and math.isfinite(q) and 0 <= q <= 1
                and p.get('label') == r['label'], 'invalid_prediction')
    require(all(r['split'] == 'validation' and r['use'] in
                ('retention-validation', 'representative-selection') for r in rows), 'invalid_selection_role')
    values = {p['id']: p for p in predictions}
    retained = [r for r in rows if r['use'] == 'retention-validation']
    require(len(retained) == 18, 'changed_retention_membership')
    ret = retention.selection_metrics([values[r['id']] for r in retained], retained,
        dict(policy=retention.POLICY, threshold=.85, nativeRetentionFloor=1))
    real = [r for r in rows if r['use'] == 'representative-selection']
    require(objective_weights(real) == selection['weights'], 'changed_objective_weights')
    policy = selection['framePolicy']
    require(set(policy['populations']['candidate']) == {r['id'] for r in real}
            and len(policy['populations']['candidate']) == len(real), 'changed_frame_membership')
    report = summarize(real, [values[r['id']] for r in real], policy)
    frame = report['metrics']['completeFrameSelection']
    counts = frame['counts']
    overall = report['metrics']['candidate']['groups']['overall']
    checks = {'retention': ret['checkpointEligible'],
              'realImprovement': overall['tp'] > 3 and overall['fp'] <= 9,
              'completeFrames': frame['supported'] == selection.get('expectedCompleteFrames', 13) and counts.get('unique_correct', 0) >= 2
                  and counts.get('wrong', 0) == counts.get('multiple_focus', 0) == 0}
    for lane, (tp, fp) in FLOORS.items():
        m = report['strata'][lane]
        checks[lane] = m['status'] == 'available' and m.get('tp', -1) >= tp and m.get('fp', 999999) <= fp
    loss = 0.
    for r in real:
        q = max(1e-12, min(1-1e-12, values[r['id']]['probability']))
        loss -= selection['weights'][r['id']] * math.log(q if r['label'] else 1-q)
    return dict(selectionLoss=loss, checkpointEligible=all(checks.values()), checks=checks,
                retention=ret, real=report)


def real_inputs(ref):
    freeze = a.object_json(a.checked(ref))
    require(freeze['version'] == 'fdr012-comparison-freeze-v1', 'incompatible_comparison')
    sources = [s for s in freeze['inputs'] if s['name'] in ('batch01', 'batch02', 'batch03', 'photos', 'supplement')]
    require(len(sources) == 5 and len({s['name'] for s in sources}) == 5, 'missing_real_protocol')
    rows, excluded, frames, baseline = [], [], [], []
    for s in sources:
        doc = a.object_json(a.checked(s['protocol']))
        require(doc.get('finalChallengeScored') is False and doc.get('trainingEligible') is False
                and doc.get('developmentEvaluationEligible') is True, 'wrong_real_role')
        require([r['id'] for r in doc['samples']] == s['membership'], 'changed_real_membership')
        for artifact in s['baselineArtifacts']: a.checked(artifact)
        scores = s['baselines']['fdr010']['predictions']
        require([p['id'] for p in scores] == s['membership'], 'changed_baseline_membership')
        # Reuse existing metrics to reject invalid scores and malformed role accounting.
        summarize(doc['samples'], scores, doc.get('roleAdmission'))
        prefix = s['name'] + ':'
        for r, p in zip(doc['samples'], scores):
            a.checked(r['image']); checked_pixels({**r['crop'], 'pixelSHA256': r['pixelSHA256']})
            row = {**r, 'id': prefix+r['id'], 'frameID': prefix+r['frameID'],
                   'split': 'validation', 'use': 'representative-selection', 'samplingWeight': 0.,
                   'population': r.get('population', 'candidate'), 'settlement': r.get('settlement', 'settled')}
            if row['population'] != 'candidate' or row['settlement'] != 'settled':
                excluded.append(dict(id=row['id'], reason='not_settled_candidate', source=s['protocol']))
            else:
                rows.append(row); baseline.append(dict(id=row['id'], label=row['label'], probability=p['probability']))
        if doc.get('roleAdmission'):
            frames += [{**f, 'id': prefix+f['id']} for f in doc['roleAdmission']['frames']]
        else:
            frames += [dict(id=prefix+fid, settlement='settled', coverage='unknown')
                       for fid in sorted({r['frameID'] for r in doc['samples']})]
    require(len(rows) == 453 and len(excluded) == 64 and len(frames) == 40, 'changed_selection_population')
    require(sum(f['coverage'] == 'complete' and f['settlement'] == 'settled' for f in frames) == 13,
            'changed_complete_frame_support')
    return rows, excluded, frames, baseline


def reviewed_additions(ref):
    review = a.object_json(a.checked(ref))
    require(review['version'] == 'qualified44-final-review-v1' and len(review['pairs']) == 44,
            'incompatible_review')
    require(len({(p['corpusID'], p['pairID']) for p in review['pairs']}) == 44, 'duplicate_review_member')
    require(Counter(p['disposition'] for p in review['pairs']) ==
            {'eligible-development-candidate': 38, 'geometry-blocked': 3, 'duplicate-excluded': 3}, 'changed_review_dispositions')
    for key in ('inventory', 'overlap', 'geometry'): a.checked(review[key])
    manifests, rows = {}, []
    for p in review['pairs']:
        e = p['evidence']; mref = e['manifest']; mpath = a.checked(mref)
        if mref['path'] not in manifests:
            doc = a.object_json(mpath); validate_manifest(doc, mpath.parent)
            require(doc['version'] == '1.5' and doc['sourceKind'] == 'simulatorFixture'
                    and doc['evidenceKind'] == 'test-only', 'unsupported_addition_source')
            manifests[mref['path']] = doc
        doc = manifests[mref['path']]
        require(doc['corpusID'] == p['corpusID'], 'changed_corpus')
        pair = next(x for x in doc['pairs'] if x['pair_id'] == p['pairID'])
        require(pair['split'] == 'development', 'wrong_addition_partition')
        for role, label in (('focused', 1), ('unfocused', 0)):
            frame, crop = e['frames'][role], e['crops'][role]
            checked_pixels(frame); checked_pixels(crop)
            raw = pair['frames'][role]
            require(frame['bounds'] == raw['bounds'] and frame['sha256'] == raw['sha256']
                    and crop['sha256'] == pair[role+'_crop_sha256'], 'changed_review_geometry_or_crop')
            if p['disposition'] != 'eligible-development-candidate': continue
            require(not p['evaluationOverlap'] and not p['labelConflict'], 'review_conflict')
            rows.append(dict(id=digest([p['corpusID'], p['pairID'], role]), sourceID=p['corpusID'],
                pairID=p['pairID'], label=label, sourceKind='simulatorFixture', manifestVersion='1.5',
                labelSource='fixtureGroundTruth', frameLabelSource=raw['labelSource'], split='development',
                relatedGroup=pair['recipe_group'], intrinsicGroup=pair['recipe_group'],
                scene=pair['fixture_scene'], style=pair['theme'], control=pair['element_type'],
                runtime=doc['runtimeCrop'], elementID=pair['elementID'], bounds=raw['bounds'],
                frame={k:frame[k] for k in ('path','sha256','pixelSHA256')}, crop=crop,
                priorUse='development', sourceBlockers=['development_only_source_contract'],
                recipeSeed=pair['recipe_seed'], admissionReview=ref))
    return rows, review['pairs']


def assemble(spec):
    require(spec.get('version') == INPUT, 'unsupported_representative_input')
    base = appearance.sealed(spec['base'], retention.VERSION, 'protocolSHA256')
    require(base['counts'] == {'train-candidate': 650, 'retention-validation': 18}, 'changed_base_counts')
    require(base['configuration'] == {**appearance.CONFIG, 'selection':retention.POLICY}
            and base['selection']['policy'] == retention.POLICY
            and base['selection']['nativeRetentionFloor'] == 1, 'changed_base_configuration')
    require(dict(Counter(r['use'] for r in base['samples'])) == base['counts']
            and all((r['split'],r['use']) in {('train','train-candidate'),('validation','retention-validation')}
                    for r in base['samples']), 'changed_base_roles')
    appearance.check_pairs(base['samples'])
    for row in base['samples']:
        checked_pixels(row['frame']); checked_pixels(row['crop'])
    a.checked(base['warmCheckpoint'])
    additions, dispositions = reviewed_additions(spec['review'])
    reserved = appearance.sealed(spec['reservedPixels'], 'surface-crops-v1', 'seal')
    reserved_pixels = {v for r in reserved['samples'] for v in (r['framePixelSHA256'], r['crop']['pixelSHA256'])}
    # Reuse protected lineage metadata only: never reopen/render challenge images.
    prior_extension = appearance.sealed(base['inputs']['extension'], extension.VERSION, 'protocolSHA256')
    prior_appearance = appearance.sealed(prior_extension['inputs']['base'], appearance.VERSION, 'protocolSHA256')
    protected_ref = prior_appearance['inputs']['protected']
    protected = appearance.sealed(protected_ref, 'appearance-protected-evidence-audit-v1', 'auditSHA256')
    rows, decisions, lineage = extension.extend(base, additions, protected['remotesSamples'], reserved_pixels)
    require(Counter(d['disposition'] for d in decisions) == {'admitted-training-pair':38}, 'unexpected_admission')
    require(all(next(r for r in rows if r['id'] == old['id']) == old for old in base['samples']), 'changed_base_member')
    real, excluded, frames, baseline = real_inputs(spec['comparison'])
    real_pixels = {r['pixelSHA256'] for r in real}
    real_pixels.update(pixel_digest(ROOT, r['image']) for r in real)
    require(not any(r[k]['pixelSHA256'] in real_pixels for r in rows for k in ('frame','crop')), 'selection_leakage')
    selection = dict(policy=POLICY, threshold=.85, weights=objective_weights(real),
        framePolicy=dict(populations=dict(candidate=[r['id'] for r in real], auxiliary=[], unresolved=[]), frames=frames))
    runtime = retention.runtime_identity()
    runtime['code'] += [a.reference(ROOT/'scripts'/f) for f in
        ('focus_representative_experiment.py','focus_representative_validation.py','human_focus_evaluation.py',
         'human_focus_roles.py','focus_training_preflight.py')]
    doc = dict(version=VERSION, inputs=spec, runtime=runtime, samples=rows+real,
        selection=selection, excludedSelection=excluded, admissionDispositions=dispositions,
        admissionDecisions=decisions, lineage=lineage, baseline=baseline,
        configuration={**base['configuration'], 'selection':POLICY}, sampling=appearance.weights(rows),
        priorSelection=base['selection'], protectedMetadata=protected_ref,
        counts=dict(Counter(r['use'] for r in rows+real)), warmCheckpoint=base['warmCheckpoint'],
        unmetQualificationBlockers=base['unmetQualificationBlockers'],
        releaseEligible=False, modelGatePassed='not_assessed')
    doc['protocolSHA256'] = digest(doc)
    return doc


def load_protocol(path, arm, run_name, approval_path=None):
    path = local(path)
    doc = appearance.sealed(a.reference(path), VERSION, 'protocolSHA256')
    require(doc == assemble(doc['inputs']), 'changed_representative_protocol_or_runtime')
    require(arm == 'warm-stretch' and isinstance(run_name,str) and
            re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',run_name), 'invalid_arm_or_run_name')
    out = ROOT/'NativeUITrainer/focus_ring_runs'/run_name
    require(not out.exists() and not any(p.is_symlink() for p in (out,*out.parents)), 'output_collision')
    blockers, approval_ref = [], None
    if approval_path is None: blockers.append('missing_experiment_approval')
    else:
        approval_ref = a.reference(local(approval_path)); approval = a.object_json(a.checked(approval_ref))
        require(approval.get('version') == 'focus-representative-approval-v1' and approval.get('approved') is True
                and approval.get('protocolSHA256') == doc['protocolSHA256'] and approval.get('arm') == arm
                and approval.get('runName') == run_name and approval.get('reviewer') and approval.get('reviewReference'),
                'missing_or_stale_representative_approval')
    rows = [{**r, 'path':a.checked({k:r['crop'][k] for k in ('path','sha256')}),
             'samplingWeight':doc['sampling']['weights'].get(r['id'],0.)} for r in doc['samples']]
    return dict(formatVersion=FORMAT, configurationValid=True, launchEligible=not blockers,
        blockers=blockers, executionAuthorized=False, releaseEligible=False,
        **{k:doc[k] for k in ('configuration','selection','sampling','counts','warmCheckpoint','runtime',
                            'protocolSHA256','unmetQualificationBlockers')},
        protocolFile=a.reference(path), approval=approval_ref, arm=arm, output=str(out.relative_to(ROOT))), rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', required=True, type=local)
    parser.add_argument('--output', required=True, type=local)
    args = parser.parse_args()
    require(not args.output.exists(), 'output_collision')
    doc = assemble(a.object_json(args.inputs))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as stream: json.dump(doc,stream,indent=2,allow_nan=False)
    print(json.dumps(dict(counts=doc['counts'], protocolSHA256=doc['protocolSHA256'])))


if __name__ == '__main__': main()
