"""Score one fixed box change on retained native frames. Keep pixels, labels, model, and threshold fixed.

Optional input `candidate` (JITTER413) turns the model cache off. The job then scores the candidate weights.
It scores the unchanged source boxes again with the candidate and compares each changed box with that fresh
reference, not with the cached T37 scores of the pinned model. The pinned `model` stays the provenance check.
"""
import base64
import hashlib
import io
import math
from collections import Counter
from pathlib import Path
import research_queue as q
from template_inputs398 import checked
from template_adapters395 import document, resolve_inputs
from cached_selection405 import verified_report
from coverage_reports402 import rectangle
from native_selection404 import outcome

OUT = None
SOURCES = ('known-box', 'raw-proposal', 'mapped-proposal')
SUCCESS = {'correct', 'correct-abstention'}
LIMIT = 64.0
# A 'none' arm must reproduce the cached T37 scores. This proves candidate correspondence.
TOLERANCE = 1e-4


def parameters(value):
    """Return (source, intervention) or raise. One changed factor per job."""
    q.require(isinstance(value, dict) and set(value) == {'source', 'intervention'}, 'intervention_parameters')
    source, change = value['source'], value['intervention']
    q.require(source in SOURCES, 'intervention_source')
    q.require(isinstance(change, dict) and 'kind' in change, 'intervention_kind')
    fields = {'none': set(), 'round': set(), 'translate': {'dx', 'dy'}, 'margin': {'dw', 'dh'}}.get(change['kind'])
    q.require(fields is not None and set(change) == fields | {'kind'}, 'intervention_fields')
    numbers = [change[k] for k in sorted(fields)]
    q.require(all(type(v) in (int, float) and math.isfinite(v) and abs(v) <= LIMIT for v in numbers), 'intervention_value')
    q.require(change['kind'] in ('none', 'round') or any(v != 0 for v in numbers), 'intervention_no_change')
    return source, change


def intervene(box, change):
    """Change 1 factor of an [x, y, width, height] top-left pixel box."""
    x, y, w, h = [rectangle(box)[k] for k in ('x', 'y', 'width', 'height')]
    kind = change['kind']
    if kind == 'round':
        # Round the edges, not the size. This changes only pixel-grid alignment.
        left, top, right, bottom = round(x), round(y), round(x + w), round(y + h)
        x, y, w, h = left, top, right - left, bottom - top
    elif kind == 'translate':
        x, y = x + change['dx'], y + change['dy']
    elif kind == 'margin':
        # Keep the center fixed. dw and dh are total size changes in pixels.
        x, y, w, h = x - change['dw'] / 2, y - change['dh'] / 2, w + change['dw'], h + change['dh']
    q.require(w > 0 and h > 0, 'intervention_empty_box')
    return [x, y, w, h]


def summarize(rows, source, change):
    """Compare each changed arm with the cached outcome of the same source arm."""
    q.require(rows, 'empty_comparison')
    slices = {}
    for profile in ('standard', 'hcf'):
        subset = [r for r in rows if r['profile'] == profile]
        targets = [r['target'] for r in subset if r['target'] is not None]
        deltas = [t['score'] - t['cachedScore'] for t in targets]
        slices[profile] = dict(frames=len(subset), groups=len({r['group'] for r in subset}),
            noFocusFrames=sum(r['noFocus'] for r in subset),
            cachedOutcomes=dict(Counter(r['cachedOutcome'] for r in subset)),
            outcomes=dict(Counter(r['outcome'] for r in subset)),
            abstentions=sum(r['aboveThreshold'] != 1 for r in subset),
            gains=[r['id'] for r in subset if r['gain']], losses=[r['id'] for r in subset if r['loss']],
            targetScoreDelta=dict(count=len(deltas), mean=sum(deltas) / len(deltas) if deltas else None,
                                  min=min(deltas, default=None), max=max(deltas, default=None)))
    deviation = max((abs(c['score'] - c['cachedScore']) for r in rows for c in r['candidates']), default=0.0)
    if change['kind'] == 'none':
        q.require(deviation <= TOLERANCE, 'cached_score_mismatch')
    return dict(version='box-intervention-v1', source=source, intervention=change, threshold=.85, matchingIoU=.5,
                frames=len(rows), groups=len({r['group'] for r in rows}), rows=rows, slices=slices,
                gains=[r['id'] for r in rows if r['gain']], lostPriorSuccesses=[r['id'] for r in rows if r['loss']],
                abstentions=sum(r['aboveThreshold'] != 1 for r in rows), maxCachedScoreDeviation=deviation,
                modelAccepted=False,
                limitation='Inspected development groups. One box change per job. No correction is accepted from one job.')


def compare(row, truth, source, change, scores, crops):
    """Build 1 result row from cached T37 values and new scores of the changed boxes."""
    from hcf_compare371 import iou
    cached = row['arms'][source]
    changed = [intervene(b, change) for b in cached['boxes']]
    q.require(len(scores) == len(changed) == len(crops) == len(cached['scores']), 'score_count')
    new = outcome(scores, changed, truth)
    candidates = [dict(index=i, sourceBox=b, changedBox=c, cachedScore=s0, score=s, cropSHA256=h)
                  for i, (b, c, s0, s, h) in enumerate(zip(cached['boxes'], changed, cached['scores'], scores, crops))]
    target = None
    if truth is not None:
        overlaps = [iou(rectangle(b), rectangle(truth)) for b in cached['boxes']]
        best = max(range(len(overlaps)), key=overlaps.__getitem__, default=None)
        if best is not None and overlaps[best] >= .5:
            target = dict(index=best, sourceIoU=overlaps[best], cachedScore=cached['scores'][best], score=scores[best])
    return dict(id=row['id'], group=row['group'], profile=row['profile'], noFocus=truth is None,
                cachedOutcome=cached['outcome'], outcome=new, aboveThreshold=sum(s >= .85 for s in scores),
                gain=cached['outcome'] not in SUCCESS and new in SUCCESS,
                loss=cached['outcome'] in SUCCESS and new not in SUCCESS, target=target, candidates=candidates)


def fresh_reference(row, source, truth, scores):
    """Replace the cached source arm with scores of the unchanged boxes by the scoring model."""
    q.require(len(scores) == len(row['arms'][source]['scores']), 'score_count')
    arm = dict(row['arms'][source], scores=scores, outcome=outcome(scores, row['arms'][source]['boxes'], truth))
    return dict(row, arms=dict(row['arms'], **{source: arm}))


def producer(entry, model, tool):
    """Return the capture pin of a completed T37 job. Require the same model and crop tool."""
    receipt = document(entry['result'])
    folder = Path(entry['result']['path']).parents[2]
    q.require(folder.parent.name == 'jobs', 'producer_scope')
    spec = q.load(q.local_path(q.ROOT, str(folder / 'spec.json')))
    q.require(q.text_digest(spec) == receipt['specSHA256'], 'producer_spec_changed')
    template = spec['template']
    q.require(template['id'] == 'T37', 'producer_template')
    q.require(template['inputs']['model'] == model and template['inputs']['tool'] == tool, 'producer_model_changed')
    return template['inputs']['capture']


def run():
    import numpy as np
    from PIL import Image
    import torch
    import focus_runtime
    import native343
    from train_focus_ring_detector import load_mobilenetv4_conv_small
    cfg = q.load(OUT.parents[2] / 'spec.json')['template']
    source, change = parameters(cfg['parameters'])
    refs = resolve_inputs(cfg, OUT)
    bundle = document(refs['bundle'])
    q.require(set(bundle) == {'version', 'role', 'pairs'} and bundle['version'] == 'cached-selection-inputs-v1', 'bundle_version')
    q.require(bundle['role'] == 'development' and 1 <= len(bundle['pairs']) <= 32, 'bundle_scope')
    candidate = refs.get('candidate')
    model = load_mobilenetv4_conv_small()(pretrained=False, num_classes=1).eval()
    weights = checked(candidate if candidate else refs['model'])
    model.load_state_dict(torch.load(weights, map_location='cpu', weights_only=True)['state_dict'], strict=True)
    torch.set_num_threads(2); focus_runtime.TOOL = checked(refs['tool'])

    def score(path, sha256, boxes):
        if not boxes:
            return [], []
        q.require(len(boxes) <= 128, 'native_proposal_limit')
        items = [dict(id=str(i), path=str(path), sha256=sha256, bounds=b) for i, b in enumerate(boxes)]
        reply = focus_runtime.invoke(items, image_root=Path('/Volumes/training-drive/data/NUIAK'))
        arrays, crops = [], []
        for item in reply['results']:
            raw = base64.b64decode(item['png'], validate=True)
            crops.append(hashlib.sha256(raw).hexdigest())
            with Image.open(io.BytesIO(raw)) as image:
                q.require(image.size == (256, 256), 'runtime_crop_size')
                arrays.append(np.array(image.convert('RGB'), copy=True))
        with torch.no_grad():
            values = torch.sigmoid(model(torch.from_numpy(np.stack(arrays)).permute(0, 3, 1, 2).float() / 255)).reshape(-1).tolist()
        return values, crops
    rows, seen = [], set()
    for pair in bundle['pairs']:
        q.require(set(pair) == {'selection', 'geometry'}, 'pair_fields')
        selection = verified_report(pair['selection'])
        q.require(selection.get('threshold') == .85, 'threshold_changed')
        artifact = document(producer(pair['selection'], refs['model'], refs['tool']))
        capture_path = Path(artifact['path'])
        q.require(capture_path.resolve() == capture_path and capture_path.is_relative_to('/Volumes/training-drive/data/NUIAK/HCF371'),
                  'native_source_scope')
        q.require(q.digest(capture_path) == artifact['sha256'], 'native_source_changed')
        capture = q.load(capture_path); q.require(capture['complete'] and capture['cleanup'], 'native_capture_incomplete')
        frames = capture['frames']
        q.require([f['id'] for f in frames] == [r['id'] for r in selection['rows']], 'native_membership')
        for frame, row in zip(frames, selection['rows']):
            q.require(row['id'] not in seen, 'duplicate_frame'); seen.add(row['id'])
            native343.signature(frame['before'], frame['before'], frame['focus'])
            native343.signature(frame['after'], frame['before'], frame['focus'])
            scene = frame['before']['scene']
            q.require([scene['scene_width'], scene['scene_height']] == [3840, 2160], 'native_mapping_size')
            path = q.local_path(capture_path.parent, frame['path'])
            q.require(q.digest(path) == frame['sha256'], 'native_pixels_changed')
            controls = [e for e in scene['elements'] if e['element_id'] in scene['focus_observation']['plannedFocusIDs']]
            known = [[rectangle(e['rendered_body_geometry']['visible_pixel_bounds'])[k] for k in ('x', 'y', 'width', 'height')]
                     for e in controls]
            # The cached known arm must name the same labelled bodies. Labels stay fixed.
            q.require(known == row['arms']['known-box']['boxes'], 'known_box_correspondence')
            truth = next((b for e, b in zip(controls, known) if e['is_focused']), None)
            q.require((truth is None) == row['noFocus'], 'focus_label_changed')
            boxes = [intervene(b, change) for b in row['arms'][source]['boxes']]
            scores, crops = score(path, frame['sha256'], boxes)
            prior = row['arms'][source]['outcome']
            if candidate:
                reference = scores if change['kind'] == 'none' else score(path, frame['sha256'], row['arms'][source]['boxes'])[0]
                row = fresh_reference(row, source, truth, reference)
            rows.append(dict(compare(row, truth, source, change, scores, crops), pinnedModelOutcome=prior))
    report = summarize(rows, source, change)
    report['sources'] = bundle['pairs']
    report['reference'] = 'candidate-unchanged-box' if candidate else 'cached-T37'
    report['scoringModel'] = candidate if candidate else refs['model']
    q.save(OUT / 'benchmark_summary.json', report)
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path='benchmark_summary.json', sha256=q.digest(OUT / 'benchmark_summary.json'))]))
