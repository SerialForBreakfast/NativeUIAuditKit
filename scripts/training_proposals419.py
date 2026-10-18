"""Prepare and measure detector errors on admitted training groups only."""
import math
import os
import random
from pathlib import Path

import research_queue as q
from template_inputs398 import checked, pin
from template_adapters395 import document, resolve_inputs
from detector_native_inputs import bounds
from detector_case_match411 import iou

OUT = None
VERSION = 'training-proposals-v1'


def settings(count, seed):
    q.require(type(count) is int and 1 <= count <= 10000 and type(seed) is int and seed > 0, 'proposal_sample_settings')


def prepare(admission, family, out):
    from PIL import Image
    q.require(admission.get('version') == 'native-control-admission-v1'
              and admission.get('trainingAdmitted') is True, 'proposal_admission')
    q.require(family in ('button', 'row', 'tab'), 'proposal_family')
    groups, pixels = {}, {}
    for row in admission['rows']:
        role = row['role']
        q.require(role in ('train', 'development', 'calibration', 'audit'), 'proposal_role')
        q.require(groups.setdefault(row['group'], role) == role, 'proposal_group_leak')
        signature = (role, row['group'], row['boxes'], row['focus'])
        q.require(pixels.setdefault(row['sha256'], signature) == signature, 'proposal_pixel_conflict')
    frames, seen = [], set()
    for row in admission['rows']:
        if row['role'] != 'train' or row['family'] != family:
            continue
        path = Path(row['path'])
        storage = Path(admission['storage']['root']).resolve()
        q.require(path.resolve().is_relative_to(storage), 'proposal_storage_scope')
        q.require(path.is_file() and q.digest(path) == row['sha256'], 'proposal_image_changed')
        with Image.open(path) as image:
            q.require(image.size == (row['width'], row['height']), 'proposal_dimensions')
        q.require(row['focus'] in row['boxes'], 'proposal_unknown_focus')
        controls = {ident: bounds(box, row['width'], row['height']) for ident, box in row['boxes'].items()}
        q.require(controls, 'proposal_no_controls')
        if row['sha256'] in seen:
            continue
        seen.add(row['sha256'])
        target = out / 'images' / (row['sha256'] + '.png')
        target.parent.mkdir(exist_ok=True)
        os.link(path, target)
        q.require(q.digest(target) == row['sha256'], 'proposal_copy_changed')
        frames.append(dict(id=row['id'], image=pin(target), sha256=row['sha256'],
                           group=row['group'], family=family, profile=row['profile'], role='train',
                           width=row['width'], height=row['height'], boxes=controls,
                           focus=row['focus']))
    q.require(frames, 'proposal_empty_training')
    return dict(version=VERSION, role='train', frames=frames,
                groups=sorted({f['group'] for f in frames}), modelAccepted=False)


def match(frame, doc):
    q.require(frame.get('role') == 'train', 'proposal_frames_role')
    for box in frame['boxes'].values():
        bounds(box, frame['width'], frame['height'])
    q.require(doc['status'] == 'success' and doc['inputSHA256'] == frame['sha256'], 'proposal_prediction_identity')
    q.require((doc['width'], doc['height']) == (frame['width'], frame['height']), 'proposal_prediction_dimensions')
    proposals, rejected = [], 0
    for element in doc['runtime']['result']['elements']:
        b = element['boundingBoxPixels']
        box = [b[k] for k in ('x', 'y', 'width', 'height')]
        q.require(all(type(v) in (int, float) and math.isfinite(v) for v in box), 'proposal_nonfinite')
        if box[0] < 0 or box[1] < 0 or box[2] <= 0 or box[3] <= 0 or box[0]+box[2] > frame['width'] or box[1]+box[3] > frame['height']:
            rejected += 1
            continue
        if box not in proposals:
            proposals.append(box)
    xyxy = lambda b: [b[0], b[1], b[0]+b[2], b[1]+b[3]]
    links = {key: [i for i, p in enumerate(proposals) if iou(xyxy(body), xyxy(p)) >= .1]
             for key, body in frame['boxes'].items()}
    matches, ambiguous, missed = [], [], []
    for key, candidates in links.items():
        if not candidates:
            missed.append(key)
            continue
        if len(candidates) != 1 or sum(candidates[0] in v for v in links.values()) != 1:
            ambiguous.append(key)
            continue
        body, p = frame['boxes'][key], proposals[candidates[0]]
        offset = [(p[0]+p[2]/2-body[0]-body[2]/2)/body[2],
                  (p[1]+p[3]/2-body[1]-body[3]/2)/body[3],
                  p[2]/body[2]-1, p[3]/body[3]-1]
        matches.append(dict(frame=frame['id'], group=frame['group'], imageSHA256=frame['sha256'],
                            control=key, body=body, proposal=p, offset=offset, role='train'))
    used = {i for values in links.values() for i in values}
    return dict(matches=matches, ambiguous=ambiguous, missed=missed, rejected=rejected,
                unmatchedProposals=len(proposals)-len(used))


def sample(matches, count, seed):
    settings(count, seed)
    q.require(matches and all(m.get('role') == 'train' for m in matches), 'proposal_sample_role')
    groups = {}
    for row in matches:
        q.require(len(row['offset']) == 4 and all(type(x) in (int, float) and math.isfinite(x) for x in row['offset']), 'proposal_offset')
        q.require(isinstance(row['group'], str) and row['group'], 'proposal_group')
        groups.setdefault(row['group'], []).append(row)
    rng = random.Random(seed)
    names = sorted(groups)
    # Select groups equally before selecting a control. Duplicate frames do not add weight.
    return [rng.choice(groups[rng.choice(names)]) for _ in range(count)]


def receipt(names):
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=name, sha256=q.digest(OUT/name)) for name in names]))


def run():
    cfg = q.load(OUT.parents[2]/'spec.json')['template']
    q.require(cfg['id'] in ('T87', 'T88'), 'proposal_template')
    refs = resolve_inputs(cfg, OUT)
    params = cfg['parameters']
    if cfg['id'] == 'T87':
        data = prepare(document(refs['admission']), params['family'], OUT)
        data['source'] = refs['admission']
        q.save(OUT/'training-frames.json', data)
        q.save(OUT/'benchmark_summary.json', dict(frames=len(data['frames']), groups=len(data['groups']),
                                                role='train', modelAccepted=False))
        receipt(['training-frames.json', 'benchmark_summary.json'] +
                ['images/'+r['sha256']+'.png' for r in data['frames']])
    else:
        settings(params['count'], params['seed'])
        os.environ['YOLO_OFFLINE'] = 'true'
        os.environ.setdefault('YOLO_CONFIG_DIR', str(q.ROOT/'NativeUITrainer/.ultralytics'))
        os.environ.setdefault('MPLCONFIGDIR', str(q.ROOT/'NativeUITrainer/.mplconfig'))
        import detector_inference412 as inference
        data = document(refs['frames'])
        q.require(data.get('version') == VERSION and data.get('role') == 'train', 'proposal_frames_role')
        q.require(data['frames'] and all(r['role'] == 'train' for r in data['frames']), 'proposal_frames_role')
        q.require(len(data['frames']) <= inference.FRAME_LIMIT, 'proposal_frame_limit')
        for frame in data['frames']:
            checked(frame['image'])
            q.require(frame['sha256'] == frame['image']['sha256'], 'proposal_frame_identity')
        q.require(len({f['sha256'] for f in data['frames']}) == len(data['frames']), 'proposal_duplicate_frame')
        raw = OUT/'raw'
        raw.mkdir()
        inference.OUT = OUT
        identity = inference.pytorch(checked(refs['model']), data['frames'], .5, 640, raw)
        results = []
        for i, frame in enumerate(data['frames']):
            doc = q.load(raw/('%03d.json' % i))
            q.require(doc['runtime']['detector'] == identity, 'proposal_model_identity')
            results.append(dict(frame=frame['id'], **match(frame, doc)))
        matches = [m for r in results for m in r['matches']]
        sampled = sample(matches, params['count'], params['seed']) if matches else []
        q.save(OUT/'errors.json', dict(version=VERSION, role='train', source=refs, identity=identity,
                                     matches=matches, frames=results, sampled=sampled))
        q.save(OUT/'benchmark_summary.json', dict(matches=len(matches), independentGroups=len({m['group'] for m in matches}),
            missed=sum(len(r['missed']) for r in results), ambiguous=sum(len(r['ambiguous']) for r in results),
            unmatchedProposals=sum(r['unmatchedProposals'] for r in results),
            samplerReady=bool(matches), modelAccepted=False,
            decision='Review correspondence support before training.' if matches else 'No unique matches. Do not train an error sampler.'))
        receipt(['errors.json', 'benchmark_summary.json']+['raw/'+p.name for p in sorted(raw.glob('*.json'))])
