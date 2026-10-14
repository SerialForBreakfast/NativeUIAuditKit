"""Prepare the HCF study and measure retained pixels without assigning training labels."""
import argparse
import hashlib
import math
from pathlib import Path

import numpy as np
from PIL import Image
import research_queue as q
from focus_dataset_contract import crop_frame, expanded_box

OUT = None
STAGES = (1000, 5000, 20000, 50000)
ROLES = ('train', 'development', 'calibration', 'audit')


def design(frames, seed=361):
    """Reserve roles before collection. A requested group is not measured independence."""
    q.require(frames in STAGES and type(seed) is int, 'unsupported_stage')
    groups = []
    counts = dict(train=frames // 4, development=30, calibration=30, audit=30)
    # Separate seed namespaces keep earlier stages and reserved groups unchanged.
    for role in ROLES:
        for index in range(counts[role]):
            identity = f'hcf361:{seed}:{role}:{index}'
            group = hashlib.sha256(identity.encode()).hexdigest()
            groups.append(dict(id=group, role=role, sceneSeed=int(group[:8], 16),
                ancestryRequirement='Keep related templates and artwork derivatives in this role.',
                targetRegion=index % 9, theme=('light', 'dark', 'highContrast')[(index // 9) % 3],
                focusTargetsPerScene=4, profiles=['standard', 'hcf'],
                requestedHCFFrames=4, requestedStandardFrames=4))
    return dict(version='hcf361-design-v1', trainingFrames=frames,
        groups=groups, requestedGroups=counts, framesPerProfile=sum(counts.values()) * 4,
        totalFrames=sum(counts.values()) * 8, acceptedFrames=0,
        sourceDomain='nativeFixtureSimulator', modelTask='focused-control selection',
        regionMeaning='3 by 3 screen regions, top-left to bottom-right',
        themeMeaning='Artwork theme; this does not set OS Focus Style.',
        trainingEligible=False, finalAuditOpened=False,
        captureRequirements=[
            'Verify observed OS Focus Style before each profile block and after restoration.',
            'Use the same recipe, artwork, viewport, control IDs, and settled state across profiles.',
            'Record observed native focus and measured body bounds around each screenshot.',
            'Pin source, installed app, OS, target, recipe, artwork, and image hashes.',
            'Reject changed recipes, uncertain focus, incomplete restoration, and duplicate training pixels.',
            'Close immutable shards before 70% of producer quota. Verify offload before continuing.',
            'Resolve connected ancestry before collection. Role conflicts block the affected group.'],
        stageGate='The prior comparison must justify expansion. This design does not start capture.',
        budgets=dict(gpuHoursStudy=48, retainedGiB=250, maxEpochs=100,
            gpuHoursPerRun=4, earlyStopPatience=10, maxTrainingFrames=50000))


def validate_roles(rows):
    """Reject connected ancestry across roles, including transitive connections."""
    owners, ids = {}, set()
    for row in rows:
        q.require(row['role'] in ROLES and row['id'] not in ids, 'role_or_duplicate_id')
        ids.add(row['id'])
        ancestry = row.get('ancestry', [])
        q.require(isinstance(ancestry, list) and ancestry and all(isinstance(a, str) and a for a in ancestry), 'missing_ancestry')
        for key in ancestry:
            q.require(key not in owners or owners[key] == row['role'], 'cross_role_ancestry')
            owners[key] = row['role']
    return dict(rows=len(ids), roles={role: sum(r['role'] == role for r in rows) for role in ROLES})


def measure(left, right):
    q.require(left.shape == right.shape and left.ndim == 3 and left.shape[2] == 3, 'image_shape')
    delta = np.abs(left.astype(np.float32) - right.astype(np.float32))
    return dict(pixels=left.shape[0] * left.shape[1],
        changedPixels=int(np.any(delta > 0, axis=2).sum()),
        meanAbsoluteDifference=float(delta.mean()), maximumDifference=float(delta.max()))


def union_box(boxes, size, padding=.16):
    q.require(boxes, 'missing_boxes')
    for box in boxes:
        expanded_box(box, size)  # Reuse finite, positive, in-image geometry checks.
    x = min(b[0] for b in boxes); y = min(b[1] for b in boxes)
    right = max(b[0] + b[2] for b in boxes); bottom = max(b[1] + b[3] for b in boxes)
    q.require(math.isfinite(padding) and 0 <= padding <= 1, 'padding')
    return [max(0, x - (right-x)*padding), max(0, y-(bottom-y)*padding),
            min(size[0], right+(right-x)*padding), min(size[1], bottom+(bottom-y)*padding)]


def review(config):
    """Compare each profile on the same retained control. Do not infer accuracy."""
    docs = {}; frames = {}; boxes = {}
    for profile, ref in config['metadata'].items():
        doc = q.load(q.ROOT/ref['path']); docs[profile] = doc
        folder = (q.ROOT/ref['path']).parent
        for state, scene_key in (('unfocused', 'baseline_scene'), ('focused', 'focused_scene')):
            key = (profile, state)
            name = doc[state + '_png']
            q.require(Path(name).name == name, 'unsafe_image_name')
            path = folder/name
            q.require(q.digest(path) == doc[state+'_sha256'], 'image_changed')
            with Image.open(path) as image:
                q.require(image.width*image.height <= 40_000_000, 'image_size')
                frames[key] = image.convert('RGB')
            elements = doc[scene_key]['elements']
            matches = [e for e in elements if e['element_id'] == doc['focused_element_id']]
            q.require(len(matches) == 1, 'missing_control')
            geometry = matches[0]['rendered_body_geometry']
            q.require(geometry['availability'] == 'measured', 'unmeasured_geometry')
            boxes[key] = geometry['visible_pixel_bounds']
    q.require(frames and len({im.size for im in frames.values()}) == 1, 'incompatible_dimensions')
    if len(docs) == 2:
        q.require(docs['standard']['recipe'] == docs['hcf']['recipe'], 'unmatched_recipe')
        q.require(docs['standard']['focused_element_id'] == docs['hcf']['focused_element_id'], 'unmatched_control')
    size = next(iter(frames.values())).size
    region = union_box(list(boxes.values()), size)
    representations = {'full-resolution': {k: np.asarray(im) for k, im in frames.items()},
        'whole-screen-640': {k: np.asarray(im.resize((640, round(640*im.height/im.width)), Image.Resampling.BILINEAR)) for k, im in frames.items()},
        'fixed-boundary-256': {k: np.asarray(crop_frame(im, region)) for k, im in frames.items()},
        'production-crop-256': {k: np.asarray(crop_frame(im, expanded_box(boxes[k], im.size))) for k, im in frames.items()}}
    results = {}
    for name, views in representations.items():
        row = dict(focusArrival={p: measure(views[p, 'unfocused'], views[p, 'focused']) for p in docs})
        row['profileDifference'] = ({s: measure(views['standard', s], views['hcf', s]) for s in ('unfocused', 'focused')}
            if len(docs) == 2 else None)
        results[name] = row
    return dict(version='hcf361-cue-review-v1', views=results, fixedBoundary=region,
        profileQualification='unqualified', trainingEligible=False, modelAccepted=False,
        nativeFamily=docs[next(iter(docs))]['focused_element_id'], independentGroups=1,
        decision=('Check the OS profile and a native positive control before collection. Identical profiles cannot teach an HCF-specific cue.'
            if len(docs) == 2 and all(r['changedPixels'] == 0 for r in results['full-resolution']['profileDifference'].values())
            else 'Measure matched profiles and repeat noise before admitting an HCF-specific cue.'),
        limitations=['Pixel differences are not model accuracy or visible-effect qualification.',
            'Fixed-boundary views use observed boxes. They are diagnostic, not deployable proposals.',
            'Production crops can normalize growth. Original crops and frames remain unchanged.',
            'One control does not establish that HCF is untrainable.'])


def prototype_decision(report):
    """A successful process is not an accepted model. Reject incomplete comparisons."""
    required = ('eligibleNativeHCF', 'frozenMembership', 'baselineComplete',
                'retainedSuiteComplete', 'coreMLParity', 'auditFrozen')
    missing = [name for name in required if report.get(name) is not True]
    counts = ('cases', 'correct', 'wrong', 'abstained', 'baselineCorrect', 'baselineWrong', 'lostPreviousSuccesses')
    for name in counts:
        q.require(type(report.get(name)) is int and report[name] >= 0, 'invalid_counts:'+name)
    n = report['cases']
    q.require(report['correct']+report['wrong']+report['abstained'] == n, 'count_total')
    q.require(report['baselineCorrect']+report['baselineWrong'] <= n, 'baseline_total')
    if n == 0: missing.append('nonzero_support')
    if report['correct'] <= report['baselineCorrect']: missing.append('target_improvement')
    if report['wrong'] > report['baselineWrong']: missing.append('no_added_wrong_selections')
    if report['lostPreviousSuccesses']: missing.append('preserved_previous_successes')
    return dict(prototypeAccepted=not missing, missing=missing, navigationAuthority=False,
        realAppQualification=False, deploymentApproved=False)


def run():
    config = q.load(OUT/'config.json')
    for ref in config['inputs']:
        q.require(q.digest(q.local_path(q.ROOT, ref['path'])) == ref['sha256'], 'input_changed')
    if config['mode'] == 'cue-review':
        result = review(config)
    elif config['mode'] == 'design':
        result = design(config['frames'])
    else:
        raise ValueError('unsupported_mode')
    q.save(OUT/'summary.json', result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); OUT = args.output; run()
