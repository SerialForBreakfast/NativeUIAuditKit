"""T48: score the fixed crop classifier on retained frames under 1 representation change. Keep pixels, labels,
boxes, model, and threshold fixed.

Supported changes use the production crop path (`FocusRingClassifier.makeCrop` through FocusRingTool, BP-46):
- `context`: a different crop expansion. The tool keeps its 0.16 expansion. The adapter scales the box about its
  center so that the tool crop rectangle equals the requested expansion. Selection still matches the source box.
- `aspect-fit`: the tool `experimentalAspectFit` crop. It letterboxes the expanded rectangle into 256x256
  instead of stretching it. The padding fraction comes from geometry, not from black pixels.

Each job also scores the unchanged crops. They must reproduce the cached T37 scores within 1e-4.
Gains and losses compare the changed representation with the cached outcome of the same source arm.

Not supported, because their inputs do not exist in the retained bundle (see Research/Plans/Backlog410.md):
scale-aware input, position transfer, screen-level selection, alternative encoders, and a joint detector.
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
from box_intervention410 import SOURCES, SUCCESS, TOLERANCE, producer

OUT = None
EXPANSION = .16  # FocusRingClassifier.defaultExpansionFactor. The tool does not take another value.
SIZE = 256
KINDS = {'none': set(), 'context': {'expansion'}, 'aspect-fit': set()}


def parameters(value):
    """Return (source, representation) or raise. One changed factor per job."""
    q.require(isinstance(value, dict) and set(value) == {'source', 'representation'}, 'representation_parameters')
    source, change = value['source'], value['representation']
    q.require(source in SOURCES, 'representation_source')
    q.require(isinstance(change, dict) and change.get('kind') in KINDS, 'representation_kind')
    q.require(set(change) == KINDS[change['kind']] | {'kind'}, 'representation_fields')
    if change['kind'] == 'context':
        e = change['expansion']
        q.require(type(e) in (int, float) and math.isfinite(e) and 0 <= e <= .5, 'representation_value')
        q.require(abs(e - EXPANSION) > 1e-9, 'representation_no_change')
    return source, change


def tool_box(box, change):
    """Return the box sent to the tool. Only `context` changes it."""
    r = rectangle(box)
    if change['kind'] != 'context':
        return [r['x'], r['y'], r['width'], r['height']]
    k = (.5 + change['expansion']) / (.5 + EXPANSION)
    w, h = r['width'] * k, r['height'] * k
    return [r['x'] + (r['width'] - w) / 2, r['y'] + (r['height'] - h) / 2, w, h]


def crop_geometry(box, image, change):
    """Mirror FocusRingClassifier.expandedCropRect for the tool box. Report clamping and letterbox padding."""
    x, y, w, h = tool_box(box, change)
    x1, y1 = max(0., x - w * EXPANSION), max(0., y - h * EXPANSION)
    x2, y2 = min(image[0], x + w * (1 + EXPANSION)), min(image[1], y + h * (1 + EXPANSION))
    cw, ch = max(0., x2 - x1), max(0., y2 - y1)
    q.require(cw > 0 and ch > 0, 'representation_empty_crop')
    padding = 0.
    if change['kind'] == 'aspect-fit':
        ratio = min(SIZE / cw, SIZE / ch)
        padding = 1 - (cw * ratio) * (ch * ratio) / SIZE ** 2
    return dict(rect=[x1, y1, cw, ch], clamped=(x1, y1, x2, y2) != (x - w * EXPANSION, y - h * EXPANSION,
                x + w * (1 + EXPANSION), y + h * (1 + EXPANSION)), padding=padding)


def orientation(box):
    r = rectangle(box)
    ratio = r['width'] / r['height']
    return 'wide' if ratio >= 1.25 else 'tall' if ratio <= .8 else 'square'


def compare(row, truth, source, change, reference, scores, crops, geometry):
    """Build 1 result row. Selection always matches the unchanged source boxes."""
    from hcf_compare371 import iou
    cached = row['arms'][source]
    boxes = cached['boxes']
    q.require(len(scores) == len(reference) == len(crops) == len(geometry) == len(boxes) == len(cached['scores']),
              'score_count')
    new = outcome(scores, boxes, truth)
    candidates = [dict(index=i, sourceBox=b, toolBox=tool_box(b, change), cachedScore=s0, referenceScore=r, score=s,
                       cropSHA256=c, orientation=orientation(b), **g)
                  for i, (b, s0, r, s, c, g) in enumerate(zip(boxes, cached['scores'], reference, scores, crops, geometry))]
    target = None
    if truth is not None:
        overlaps = [iou(rectangle(b), rectangle(truth)) for b in boxes]
        best = max(range(len(overlaps)), key=overlaps.__getitem__, default=None)
        if best is not None and overlaps[best] >= .5:
            target = dict(index=best, sourceIoU=overlaps[best], cachedScore=cached['scores'][best], score=scores[best],
                          orientation=orientation(boxes[best]))
    return dict(id=row['id'], group=row['group'], profile=row['profile'], noFocus=truth is None,
                orientation=target['orientation'] if target else 'none',
                cachedOutcome=cached['outcome'], outcome=new, aboveThreshold=sum(s >= .85 for s in scores),
                gain=cached['outcome'] not in SUCCESS and new in SUCCESS,
                loss=cached['outcome'] in SUCCESS and new not in SUCCESS, target=target, candidates=candidates)


def summary(subset):
    targets = [r['target'] for r in subset if r['target'] is not None]
    deltas = [t['score'] - t['cachedScore'] for t in targets]
    return dict(frames=len(subset), groups=len({r['group'] for r in subset}),
                cachedOutcomes=dict(Counter(r['cachedOutcome'] for r in subset)),
                outcomes=dict(Counter(r['outcome'] for r in subset)),
                gains=[r['id'] for r in subset if r['gain']], losses=[r['id'] for r in subset if r['loss']],
                targetScoreDelta=dict(count=len(deltas), mean=sum(deltas) / len(deltas) if deltas else None,
                                      min=min(deltas, default=None), max=max(deltas, default=None)))


def summarize(rows, source, change):
    q.require(rows, 'empty_comparison')
    deviation = max((abs(c['referenceScore'] - c['cachedScore']) for r in rows for c in r['candidates']), default=0.)
    # The unchanged production crop must reproduce the cached scores. This proves candidate correspondence.
    q.require(deviation <= TOLERANCE, 'cached_score_mismatch')
    keys = sorted({(r['profile'], r['orientation']) for r in rows})
    slices = {p: summary([r for r in rows if r['profile'] == p]) for p in ('standard', 'hcf')}
    slices.update({f'{p}-{o}': summary([r for r in rows if (r['profile'], r['orientation']) == (p, o)]) for p, o in keys})
    candidates = [c for r in rows for c in r['candidates']]
    decisions = dict(changed=[dict(id=r['id'], before=r['cachedOutcome'], after=r['outcome']) for r in rows
                              if r['outcome'] != r['cachedOutcome']],
                     transitions=dict(Counter(f"{r['cachedOutcome']}->{r['outcome']}" for r in rows)))
    return dict(version='representation-comparison-v1', source=source, representation=change, threshold=.85,
                matchingIoU=.5, frames=len(rows), groups=len({r['group'] for r in rows}), rows=rows, slices=slices,
                decisions=decisions, gains=[r['id'] for r in rows if r['gain']],
                lostPriorSuccesses=[r['id'] for r in rows if r['loss']],
                abstentions=sum(r['aboveThreshold'] != 1 for r in rows), maxCachedScoreDeviation=deviation,
                geometry=dict(clampedCandidates=sum(c['clamped'] for c in candidates),
                              meanPadding=sum(c['padding'] for c in candidates) / len(candidates) if candidates else 0.,
                              orientations=dict(Counter(c['orientation'] for c in candidates))),
                modelAccepted=False,
                limitation='Inspected development groups. Inference-only change for a model trained on stretched '
                           '0.16 crops. One representation change per job. No correction is accepted from one job.')


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
    model = load_mobilenetv4_conv_small()(pretrained=False, num_classes=1).eval()
    model.load_state_dict(torch.load(checked(refs['model']), map_location='cpu', weights_only=True)['state_dict'], strict=True)
    torch.set_num_threads(2); focus_runtime.TOOL = checked(refs['tool'])

    def score(path, sha256, boxes, aspect):
        if not boxes:
            return [], []
        q.require(len(boxes) <= 128, 'native_proposal_limit')
        items = [dict(id=str(i), path=str(path), sha256=sha256, bounds=b) for i, b in enumerate(boxes)]
        reply = focus_runtime.invoke(items, experimental_aspect_fit=aspect, image_root=Path('/Volumes/training-drive/data/NUIAK'))
        arrays, crops = [], []
        for item in reply['results']:
            raw = base64.b64decode(item['png'], validate=True)
            crops.append(hashlib.sha256(raw).hexdigest())
            with Image.open(io.BytesIO(raw)) as image:
                q.require(image.size == (SIZE, SIZE), 'runtime_crop_size')
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
            with Image.open(path) as image:
                size = image.size
            controls = [e for e in scene['elements'] if e['element_id'] in scene['focus_observation']['plannedFocusIDs']]
            known = [[rectangle(e['rendered_body_geometry']['visible_pixel_bounds'])[k] for k in ('x', 'y', 'width', 'height')]
                     for e in controls]
            q.require(known == row['arms']['known-box']['boxes'], 'known_box_correspondence')
            truth = next((b for e, b in zip(controls, known) if e['is_focused']), None)
            q.require((truth is None) == row['noFocus'], 'focus_label_changed')
            boxes = row['arms'][source]['boxes']
            reference, crops = score(path, frame['sha256'], boxes, False)
            scores = reference
            if change['kind'] != 'none':
                scores, crops = score(path, frame['sha256'], [tool_box(b, change) for b in boxes], change['kind'] == 'aspect-fit')
            geometry = [crop_geometry(b, size, change) for b in boxes]
            rows.append(compare(row, truth, source, change, reference, scores, crops, geometry))
    report = summarize(rows, source, change)
    report['sources'] = bundle['pairs']
    report['scoringModel'] = refs['model']
    q.save(OUT / 'benchmark_summary.json', report)
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path='benchmark_summary.json', sha256=q.digest(OUT / 'benchmark_summary.json'))]))
