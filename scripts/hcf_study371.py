"""Native HCF study inputs, storage checks, and admission through the existing queue."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import plistlib
import shutil
import subprocess
import time

from PIL import Image
import research_queue as q
from hcf_spatial_audit import body_bounds

OUT = None
ROLES = {'train', 'development', 'calibration', 'audit'}
_storage_check = {}


def progress(step, completed=None, total=None):
    q.save(OUT.parent/'progress.json', dict(step=step, completed=completed, total=total,
                                         updatedAt=time.time()), replace=True)


def verify_storage(storage):
    volume = Path(storage['mountPoint'])
    q.require(volume == Path('/Volumes/training-drive') and volume.is_mount(), 'study_volume_unmounted')
    if time.monotonic()-_storage_check.get('time', -100) > 20:
        info = plistlib.loads(subprocess.check_output(['diskutil', 'info', '-plist', str(volume)], timeout=10))
        q.require(info.get('VolumeUUID') == storage['volumeUUID'], 'study_volume_changed')
        _storage_check.update(time=time.monotonic())
    root = Path(storage['root'])
    q.require(root == volume/'data/NUIAK/HCF371' and root.resolve() == root, 'study_root')
    usage = shutil.disk_usage(volume)
    q.require(usage.free > max(usage.total*.2, storage['reserveBytes']), 'study_storage_reserve')
    if root.exists():
        q.require(q.live_output_bytes(root) + storage['reserveBytes'] <= storage['maximumBytes'], 'study_storage_ceiling')
    return root


def validate_capture_plan(plan):
    if plan.get('version') == 'native-hcf402-v1':
        from native_coverage402 import validate
        return validate(plan)
    if plan.get('version') == 'native-controls-t45-v1':
        from native_coverage402 import validate_controls
        return validate_controls(plan)
    import native343 as native
    q.require(plan['binding']['simulatorUDID'] == native.TARGET and
              plan['binding']['endpoint'] == 'http://127.0.0.1:8080', 'study_target')
    q.require(plan['role'] == 'study-pending' and plan['trainingEligible'] is False, 'study_capture_role')
    q.require(plan['profiles'] == ['standard', 'hcf'] and plan['repeats'] == 1, 'study_profiles')
    cases = plan['cases']
    q.require(1 <= len(cases) <= 50 and len({c['id'] for c in cases}) == len(cases), 'study_case_count')
    q.require(plan['expectedFrames'] == len(cases)*8, 'study_frame_count')
    q.require(plan['captureBudgetBytes'] == 2*1024**3, 'study_capture_budget')
    q.require(plan['qualification']['complete'] and plan['qualification']['restoration'] == 'verified', 'study_qualification')
    for case in cases:
        q.require(q.ID.fullmatch(case['id']) and case['role'] in ROLES, 'study_case_identity')
        q.require(case['targets'] == ['item-0', 'item-1', 'item-2', 'item-3'], 'study_targets')
        composition = case['recipe']['appearance']['composition']
        q.require(case['recipe']['theme'] == 'dark' and case['theme'] in ('dark','light'), 'composition_theme_contract')
        q.require(all(s['focus']['kind'] == 'native_image' for s in composition['styles'].values()), 'study_authored_focus')
        q.require(len(composition['regions']) == 4, 'study_regions')
        for region in composition['regions']:
            x,y,w,h = region['frame']
            q.require(x >= 0 and y >= 0 and x+w <= 1920 and y+h <= 1080, 'study_region_bounds')


def capture(output, plan):
    import hcf_capture362
    validate_capture_plan(plan)
    root = verify_storage(plan['storage'])
    root.mkdir(parents=True, exist_ok=True)
    destination = root/plan['shard']
    q.require(not destination.exists(), 'study_shard_collision')
    actual = copy.deepcopy(plan)
    actual['progressPath'] = str(output.parent/'progress.json')
    try:
        hcf_capture362.capture(destination, actual)
    finally:
        # Mirror the cleanup receipt for the existing recovery guard, including failed captures.
        receipt = destination/'capture.json'
        if receipt.exists():
            (output/'capture').mkdir(exist_ok=True)
            q.save(output/'capture/capture.json', q.load(receipt))
            q.save(output/'artifact.json', dict(path=str(receipt), sha256=q.digest(receipt),
                storage=plan['storage'], plan=plan, bytes=q.live_output_bytes(destination)))


def dependency(output_name):
    deps = q.load(OUT/'dependencies.json')
    found = []
    for dep in deps:
        for ref in dep['outputs']:
            if ref['path'].endswith('/'+output_name):
                path = q.ROOT/ref['path']
                q.require(q.digest(path) == ref['sha256'], 'study_dependency_changed')
                found.append(q.load(path))
    q.require(found, 'study_dependency_missing:'+output_name)
    return found


def validate_groups(cases):
    roles = {}
    seeds = {}
    for case in cases:
        for key in ('family', 'group'):
            identity = (key, case[key])
            q.require(identity not in roles or roles[identity] == case['role'], 'cross_role_ancestry')
            roles[identity] = case['role']
        for seed in case['artworkSeeds']:
            q.require(seed not in seeds or seeds[seed] == case['role'], 'cross_role_artwork')
            seeds[seed] = case['role']
    return roles


def admit():
    artifact, = dependency('artifact.json')
    root = verify_storage(artifact['storage'])
    path = Path(artifact['path'])
    q.require(path.resolve().is_relative_to(root) and q.digest(path) == artifact['sha256'], 'study_capture_changed')
    doc = q.load(path); plan = artifact['plan']
    validate_capture_plan(plan); validate_groups(plan['cases'])
    q.require(doc['complete'] and doc['cleanup'] and len(doc['frames']) == plan['expectedFrames'], 'study_capture_incomplete')
    cases = {c['id']: c for c in plan['cases']}
    rows, seen, decoded = [], set(), {}
    for index, frame in enumerate(doc['frames']):
        case = cases[frame['case']]
        key = frame['case'], frame['profile'], frame['focus']
        q.require(key not in seen and frame['repeat'] == 0, 'study_duplicate_capture'); seen.add(key)
        receipt = frame['profileReceipt']['receipt']['hcf']
        import hcf_capture362
        hcf_capture362.verified_profile(frame['profileReceipt']['receipt'], frame['profile'])
        boxes = body_bounds(frame)
        image = path.parent/frame['path']
        q.require(image.resolve().is_relative_to(path.parent) and q.digest(image) == frame['sha256'], 'study_image_changed')
        with Image.open(image) as im:
            rgb = im.convert('RGB'); width,height = rgb.size
            pixel_hash = hashlib.sha256(rgb.tobytes()).hexdigest()
        q.require(pixel_hash not in decoded or decoded[pixel_hash] == (case['group'], frame['focus'], frame['profile']),
                  'study_duplicate_pixels_conflicting_label')
        decoded[pixel_hash] = (case['group'], frame['focus'], frame['profile'])
        for box in boxes.values():
            x,y,w,h = box
            q.require(x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= width+.1 and y+h <= height+.1, 'study_body_bounds')
        rows.append(dict(id=frame['id'], path=str(image), sha256=frame['sha256'], decodedSHA256=pixel_hash,
            width=width, height=height, boxes=boxes, focus=frame['focus'], profile=frame['profile'],
            role=case['role'], family=case['family'], group=case['group'], theme=case['theme'],
            case=case['id'], artworkSeeds=case['artworkSeeds']))
        progress('Verify native labels and image hashes', index+1, len(doc['frames']))
    q.require(seen == {(c['id'], p, t) for c in plan['cases'] for p in plan['profiles'] for t in c['targets']}, 'study_membership')
    import numpy as np
    from hcf_spatial_audit import rectangle_mask
    paired = {(r['case'],r['profile'],r['focus']): r for r in rows}
    effects = []
    for case in plan['cases']:
        for target in case['targets']:
            a,b = [paired[case['id'],profile,target] for profile in plan['profiles']]
            with Image.open(a['path']) as image: standard = np.asarray(image.convert('RGB'), dtype=np.int16)
            with Image.open(b['path']) as image: hcf = np.asarray(image.convert('RGB'), dtype=np.int16)
            q.require(standard.shape == hcf.shape, 'profile_dimensions_changed')
            delta = np.abs(standard-hcf).sum(axis=2)
            mask = rectangle_mask(delta.shape,[a['boxes'][target],b['boxes'][target]],64)
            total = int(delta.sum())
            fraction = float(delta[mask].sum()/total) if total else 0
            q.require(total > 0 and fraction >= .9, 'native_effect_not_localized:'+case['id']+':'+target)
            effects.append(dict(case=case['id'],focus=target,absoluteRGBDifference=total,nearFocusFraction=fraction))
    result = dict(version='hcf-study-admission-v1', rows=rows, storage=artifact['storage'],
                  sourceSHA256=artifact['sha256'], cases=plan['cases'], effects=effects, trainingAdmitted=True,
                  limitation='Native image-card observations. No physical-device or unseen-control-family qualification.')
    q.save(OUT/'admission.json', result)


def merge():
    documents = dependency('admission.json')
    rows = [r for doc in documents for r in doc['rows']]
    cases = [c for doc in documents for c in doc['cases']]
    q.require(len({r['id'] for r in rows}) == len(rows), 'study_duplicate_membership')
    validate_groups(cases)
    by_pixels = {}
    for row in rows:
        prior = by_pixels.setdefault(row['decodedSHA256'], row['role'])
        q.require(prior == row['role'], 'study_cross_role_pixels')
    q.save(OUT/'admission.json', dict(version='hcf-study-admission-v1', rows=rows, cases=cases,
        storage=documents[0]['storage'], trainingAdmitted=True))


def load_config():
    return q.load(OUT/'config.json')


def catalog():
    merge()
    doc = q.load(OUT/'admission.json')
    counts = {role: sum(r['role'] == role and r['profile'] == 'hcf' for r in doc['rows']) for role in ROLES}
    cfg = load_config()
    q.require(counts == cfg['expectedCounts'], 'study_incomplete_stage')
    cases = doc['cases']; validate_groups(cases)
    q.save(OUT/'summary.json', dict(counts=counts, frames=len(doc['rows']),
        families={role: len({c['family'] for c in cases if c['role'] == role}) for role in ROLES},
        groups={role: len({c['group'] for c in cases if c['role'] == role}) for role in ROLES},
        modelAccepted=False, limitation='Scene groups share layout families. Do not count frames as independent trials.'))


# JITTER413: box jitter for training crops only. Each side moves by at most this many pixels.
JITTER_LIMIT = 2.0


def jitter_config(value):
    """Validate the optional jitter block of a crop configuration."""
    q.require(isinstance(value, dict) and set(value) == {'variants', 'maxSidePixels', 'seed'}, 'jitter_fields')
    q.require(type(value['variants']) is int and 1 <= value['variants'] <= 8, 'jitter_variants')
    limit = value['maxSidePixels']
    q.require(type(limit) in (int, float) and 0 < limit <= JITTER_LIMIT, 'jitter_limit')
    q.require(type(value['seed']) is int, 'jitter_seed')
    return value


def jitter_sides(seed, key, variant, limit):
    """Return fixed [left, top, right, bottom] edge moves in [-limit, limit]. Positive moves an edge outward.

    A hash of (seed, key, variant) sets each value, so the result does not depend on process or row order.
    Values are multiples of 1/64 px, so JSON keeps them exactly.
    """
    digest = hashlib.sha256(f'{seed}:{key}:{variant}'.encode()).digest()
    units = [int.from_bytes(digest[4*i:4*i+4], 'big')/0xFFFFFFFF for i in range(4)]
    return [round((2*u-1)*limit*64)/64 for u in units]


def jitter_box(box, sides):
    """Apply edge moves to an [x, y, width, height] top-left pixel box."""
    x, y, w, h = box
    left, top, right, bottom = sides
    changed = [x-left, y-top, w+left+right, h+top+bottom]
    q.require(changed[2] > 0 and changed[3] > 0, 'jitter_empty_box')
    return changed


def check_jitter_roles(doc_rows, rows):
    """Refuse jitter when a training group or training pixels also occur in another role."""
    train = [r for r in rows if r['role'] == 'train']
    other = [r for r in doc_rows if r['role'] != 'train']
    q.require(not {r['group'] for r in train} & {r['group'] for r in other}, 'jitter_group_leak')
    q.require(not {r['decodedSHA256'] for r in train} & {r['decodedSHA256'] for r in other}, 'jitter_pixel_leak')


def write_crops(items, results, destination):
    written = []
    for item, result in zip(items, results):
        data = base64.b64decode(result['png'], validate=True)
        target = destination/(item['id']+'.png')
        with target.open('xb') as stream: stream.write(data)
        written.append((target, hashlib.sha256(data).hexdigest()))
    return written


def decoded_pixels(path):
    with Image.open(path) as image:
        return hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()


def prepare_crops():
    import focus_runtime
    doc, = dependency('admission.json')
    cfg = load_config()
    q.require(set(cfg) <= {'destination', 'roles', 'jitter'}, 'crop_config_fields')
    roles = set(cfg['roles'])
    q.require('audit' not in roles and roles <= ROLES, 'audit_locked')
    jitter = jitter_config(cfg['jitter']) if 'jitter' in cfg else None
    root = verify_storage(doc['storage'])
    destination = root/cfg['destination']
    q.require(not destination.exists(), 'crop_destination_exists')
    rows = [r for r in doc['rows'] if r['role'] in roles]
    if jitter:
        check_jitter_roles(doc['rows'], rows)
        if 'cases' in doc: validate_groups(doc['cases'])
    destination.mkdir()
    crop_rows = []
    # The trainer removes repeated (pixels, label) crops. Jitter each unique crop once, so repeats add no weight.
    jittered = set()
    for index, row in enumerate(rows):
        image = Path(row['path'])
        q.require(q.digest(image) == row['sha256'], 'crop_source_changed')
        items = [dict(id=row['id']+'-'+key, path=str(image), sha256=row['sha256'], bounds=box)
                 for key,box in row['boxes'].items()]
        reply = focus_runtime.invoke(items, image_root=root)
        variants = []
        for item, (target, _) in zip(items, write_crops(items, reply['results'], destination)):
            key = item['id'][len(row['id'])+1:]
            crop = dict(id=item['id'], frame=row['id'], path=str(target), sha256=q.digest(target),
                label=int(key == row['focus']), control=key, role=row['role'], profile=row['profile'], group=row['group'],
                family=row['family'], box=row['boxes'][key])
            crop_rows.append(crop)
            if jitter and row['role'] == 'train':
                pixels = decoded_pixels(target)
                if (pixels, crop['label']) in jittered: continue
                jittered.add((pixels, crop['label']))
                for variant in range(jitter['variants']):
                    sides = jitter_sides(jitter['seed'], pixels+':'+str(crop['label']), variant, jitter['maxSidePixels'])
                    variants.append((crop, variant, sides, jitter_box(crop['box'], sides)))
        if variants:
            # Use the same production crop tool (FocusRingClassifier.makeCrop) for every changed box.
            extra = [dict(id=c['id']+'-j'+str(v), path=str(image), sha256=row['sha256'], bounds=box)
                     for c, v, _, box in variants]
            q.require(len(extra) <= 128, 'jitter_batch_limit')
            reply = focus_runtime.invoke(extra, image_root=root)
            for item, (crop, variant, sides, box), (target, _) in zip(extra, variants,
                                                                    write_crops(extra, reply['results'], destination)):
                crop_rows.append(dict(crop, id=item['id'], path=str(target), sha256=q.digest(target), box=box,
                                      jitter=dict(variant=variant, sides=sides, source=crop['id'])))
        progress('Make original production crops', index+1, len(rows))
    result = dict(rows=crop_rows, frames=rows, runtime=focus_runtime.identity(),
                  storage=doc['storage'], preprocessing=focus_runtime.RUNTIME_PREPROCESSING)
    if jitter:
        result['jitter'] = dict(jitter, roles=['train'], sources=len(jittered),
                                variantRows=sum('jitter' in r for r in crop_rows))
    q.save(OUT/'crops.json', result)


def merge_crops():
    documents = dependency('crops.json')
    rows = [r for doc in documents for r in doc['rows']]
    frames = [r for doc in documents for r in doc['frames']]
    q.require(len({r['id'] for r in rows}) == len(rows), 'duplicate_crops')
    q.require(len({r['id'] for r in frames}) == len(frames), 'duplicate_crop_frames')
    q.require(all(d['runtime'] == documents[0]['runtime'] and
                  d['preprocessing'] == documents[0]['preprocessing'] for d in documents), 'crop_runtime_changed')
    q.save(OUT/'crops.json', dict(documents[0], rows=rows, frames=frames))
