"""T51 (B405-127): run the shipped Swift resolveTVOSFocus fallback on the boxes of cached learned selections.

Inputs: a T40 bundle (cached-selection-inputs-v1) and the FocusFallbackTool binary.
Each T37 selection job pins its capture. The adapter reads the native frames and rendered focused bodies from it.
The fallback sees the same boxes that the learned crop selection scored, without labels or learned scores.
"""
import json
import math
import subprocess
import time
import uuid
from collections import Counter
from pathlib import Path

import research_queue as q
from template_adapters395 import document, resolve_inputs
from template_inputs398 import checked
from cached_selection405 import ARMS, SUCCESS, verified_report

OUT = None
# The fixture controls carry the isButton trait. collectionItem enables the peer-expansion rule.
ELEMENT_TYPES = ('primaryButton', 'collectionItem')
MATCHING_IOU = .5
POLICY = 'legacy-visual-heuristic-v1'


def parameters(values):
    q.require(set(values) == {'arm', 'elementType'}, 'fallback_parameters')
    q.require(values['arm'] in ARMS, 'fallback_arm')
    q.require(values['elementType'] in ELEMENT_TYPES, 'fallback_element_type')
    return values


def iou(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    w = max(0., min(ax + aw, bx + bw) - max(ax, bx)); h = max(0., min(ay + ah, by + bh) - max(ay, by))
    union = aw * ah + bw * bh - w * h
    return w * h / union if union > 0 else 0.


def observation(box, width, height, element_type, index):
    x, y, w, h = box
    # Fixed identities keep requests reproducible. Vision coordinates use a bottom-left origin.
    ident = str(uuid.UUID(int=index + 1))
    return dict(id=ident, elementType=element_type, confidence=1.0, confidenceSource='pixelModel',
                boundingBox=dict(x=x / width, y=1 - (y + h) / height, width=w / width, height=h / height),
                boundingBoxPixels=dict(x=x, y=y, width=w, height=h), inferredTraits=[], issues=[],
                state=dict(isEnabled=True, isSelected=False))


def outcome(selected, body, no_focus):
    """Same outcome names as T37: one selected box decides; 0 or more than 1 is an abstention."""
    if no_focus:
        return 'false-selection' if len(selected) == 1 else 'correct-abstention'
    if len(selected) != 1:
        return 'miss'
    return 'correct' if iou(selected[0], body) >= MATCHING_IOU else 'wrong'


def capture_frames(selection_result):
    """Follow the T37 selection job to its pinned capture. Return frames by ID with the focused body."""
    job = q.local_path(q.ROOT, selection_result['path']).parents[2]
    spec = q.load(job / 'spec.json')
    q.require(spec['template']['id'] == 'T37', 'selection_template')
    artifact = document(spec['template']['inputs']['capture'])
    source = Path(artifact['path'])
    q.require(source.resolve() == source and source.is_relative_to('/Volumes/training-drive/data/NUIAK/HCF371'), 'capture_scope')
    q.require(q.digest(source) == artifact['sha256'], 'capture_changed')
    capture = q.load(source)
    q.require(capture['complete'] and capture['cleanup'], 'capture_incomplete')
    frames = {}
    for frame in capture['frames']:
        scene = frame['before']['scene']
        focused = [e for e in scene['elements'] if e['is_focused']]
        q.require(len(focused) == (0 if frame['focus'] is None else 1), 'focus_count')
        body = None
        if focused:
            geometry = focused[0]['rendered_body_geometry']
            q.require(geometry['availability'] == 'measured', 'body_unmeasured')
            body = list(geometry['visible_pixel_bounds'])
        frames[frame['id']] = dict(path=q.local_path(source.parent, frame['path']), sha256=frame['sha256'],
                                   width=scene['scene_width'], height=scene['scene_height'], body=body)
    return frames


def fallback(tool, frame, boxes, element_type, output, name):
    observations = [observation(b, frame['width'], frame['height'], element_type, i) for i, b in enumerate(boxes)]
    request = dict(version=1, root=str(frame['path'].parent), path=str(frame['path']), sha256=frame['sha256'],
                   observations=observations)
    process = subprocess.run([str(tool)], input=json.dumps(request), text=True, capture_output=True, timeout=60)
    q.require(process.returncode == 0, 'fallback_failed:' + process.stderr[-200:])
    reply = json.loads(process.stdout)
    q.require(reply['version'] == 1 and reply['sha256'] == frame['sha256'] and reply['policy'] == POLICY, 'fallback_reply')
    q.require([o['id'] for o in reply['observations']] == [o['id'] for o in observations], 'fallback_membership')
    for a, b in zip(observations, reply['observations']):
        q.require(a['boundingBoxPixels'] == b['boundingBoxPixels'] and a['elementType'] == b['elementType'], 'fallback_changed_boxes')
    (output / 'replies').mkdir(exist_ok=True)
    q.save(output / 'replies' / (name + '.json'), reply)
    return [boxes[i] for i, o in enumerate(reply['observations']) if o['state'].get('isFocused') is True], reply


def compare(pairs, tool, params, output):
    arm, element_type = params['arm'], params['elementType']
    rows, seen = [], set()
    for selection, frames in pairs:
        q.require(selection.get('threshold') == .85, 'threshold_changed')
        for row in selection['rows']:
            q.require(row['id'] not in seen and row['id'] in frames, 'frame_identity')
            seen.add(row['id'])
            frame = frames[row['id']]
            q.require(frame['body'] is None if row['noFocus'] else frame['body'] is not None, 'focus_identity')
            learned = row['arms'][arm]
            boxes = learned['boxes']
            q.require(all(len(b) == 4 and all(type(v) in (int, float) and math.isfinite(v) for v in b) for b in boxes), 'invalid_box')
            if boxes:
                selected, reply = fallback(tool, frame, boxes, element_type, output, row['id'])
                milliseconds = reply['milliseconds']
            else:
                selected, milliseconds = [], None
            result = outcome(selected, frame['body'], row['noFocus'])
            rows.append(dict(id=row['id'], group=row['group'], profile=row['profile'], noFocus=row['noFocus'],
                             proposals=len(boxes), learned=learned['outcome'], fallback=result,
                             selected=len(selected), milliseconds=milliseconds,
                             gain=learned['outcome'] not in SUCCESS and result in SUCCESS,
                             loss=learned['outcome'] in SUCCESS and result not in SUCCESS))
    q.require(rows, 'empty_comparison')
    slices = {}
    for profile in sorted({r['profile'] for r in rows}):
        subset = [r for r in rows if r['profile'] == profile]
        slices[profile] = dict(frames=len(subset), groups=len({r['group'] for r in subset}),
            noFocusFrames=sum(r['noFocus'] for r in subset),
            outcomes=dict(learned=dict(Counter(r['learned'] for r in subset)), fallback=dict(Counter(r['fallback'] for r in subset))),
            gains=[r['id'] for r in subset if r['gain']], losses=[r['id'] for r in subset if r['loss']])
    return dict(version='swift-fallback-comparison-v1', arm=arm, elementType=element_type, policy=POLICY,
                matchingIoU=MATCHING_IOU, rows=rows, slices=slices, frames=len(rows),
                gains=[r['id'] for r in rows if r['gain']], lostPriorSuccesses=[r['id'] for r in rows if r['loss']],
                modelAccepted=False,
                limitation='Development frames already inspected. Learned outcomes are cached T37 results at 0.85. '
                           'The fallback sees the same boxes with a fixed element type; no runtime detector proposals.')


def run():
    cfg = q.load(OUT.parents[2] / 'spec.json')['template']
    start = time.monotonic()
    try:
        params = parameters(cfg['parameters'])
        refs = resolve_inputs(cfg, OUT)
        bundle = document(refs['bundle'])
        q.require(set(bundle) == {'version', 'role', 'pairs'} and bundle['version'] == 'cached-selection-inputs-v1', 'bundle_version')
        q.require(bundle['role'] == 'development' and 1 <= len(bundle['pairs']) <= 32, 'bundle_scope')
        tool = checked(refs['tool'])
        pairs = [(verified_report(p['selection']), capture_frames(p['selection']['result'])) for p in bundle['pairs']]
        report = compare(pairs, tool, params, OUT)
        report['sources'] = dict(bundle=refs['bundle'], tool=refs['tool'])
        q.save(OUT / 'benchmark_summary.json', report)
        q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
            dict(path=str(p.relative_to(OUT)), sha256=q.digest(p)) for p in sorted(OUT.rglob('*')) if p.is_file()]))
        q.save(OUT / 'template-result.json', dict(template='T51', execution='complete', modelAccepted=False,
                                                  seconds=time.monotonic() - start))
    except Exception as error:
        q.save(OUT / 'template-result.json', dict(template='T51', execution='failed', code=str(error)[:500],
                                                  modelAccepted=False, seconds=time.monotonic() - start))
        raise
