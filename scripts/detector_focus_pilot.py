"""Compare crop models on fixed native detector proposals. Never train or promote."""
import base64
import hashlib
import io
import math
import time
from collections import Counter
from pathlib import Path

import research_queue as q
from template_adapters395 import document, resolve_inputs
from template_inputs398 import checked
from detector_native_inputs import bounds
from native_selection404 import outcome
from coverage_reports402 import rectangle
from hcf_compare371 import iou

OUT = None
VERSION = 'detector-focus-pilot-v1'
SUCCESS = {'correct', 'correct-abstention'}
ARMS = ('known-box', 'detector', 'detector-plus-ring')


def detector_predictions(card):
    q.require(card.get('version') == 'real-model-scorecard-v1', 'pilot_scorecard_version')
    q.require(card.get('partition') == 'development' and card.get('trainingEligible') is False, 'pilot_role')
    labels = document(card['inputs'])
    q.require(labels.get('role') == 'development' and labels.get('trainingEligible') is False, 'pilot_role')
    q.require(len(card['frames']) == len(set(card['frames'])) == len(card['rawPredictions']) == len(labels['frames']),
              'pilot_detector_membership')
    result = {}
    for sha, ref, label in zip(card['frames'], card['rawPredictions'], labels['frames']):
        raw = document(ref)
        q.require(raw.get('status') == 'success', 'pilot_detector_failed')
        q.require(sha == raw['inputSHA256'] == label['sha256'], 'pilot_detector_pixels')
        q.require(raw['coordinates'] in ('boundingBoxPixels: pixels top-left',
                  'boundingBox: normalized bottom-left; boundingBoxPixels: pixels top-left'), 'pilot_coordinates')
        q.require(raw['runtime']['detector'] == card['identity']['detector'], 'pilot_detector_identity')
        w, h = raw['width'], raw['height']
        q.require((w, h) == (label['width'], label['height']), 'pilot_dimensions')
        candidates, rejected = [], []
        for index, element in enumerate(raw['runtime']['result']['elements']):
            score = element['confidence']
            q.require(type(score) in (int, float) and math.isfinite(score) and 0 <= score <= 1, 'pilot_detector_score')
            if score < card['settings']['confidence']:
                continue
            raw_box = [element['boundingBoxPixels'][k] for k in ('x','y','width','height')]
            try:
                box = bounds(raw_box, w, h)
            except ValueError:
                rejected.append(dict(box=raw_box, sourceIndex=index, reason='detector_bounds'))
                continue
            candidates.append(dict(box=box, source='detector', sourceIndex=index, confidence=score,
                                   predictedClass=element['elementType']))
        q.require(len(candidates) <= 128, 'pilot_candidate_limit')
        result[sha] = dict(width=w, height=h, candidates=candidates, rejected=rejected)
    return result


def merge(detector, rings):
    """Keep detector order. Add rings only when overlap with kept boxes is below 0.5."""
    kept, removed = [], []
    for candidate in detector + rings:
        duplicate = next((i for i, old in enumerate(kept)
                          if iou(rectangle(candidate['box']), rectangle(old['box'])) >= .5), None)
        if duplicate is None:
            kept.append(candidate)
        else:
            removed.append(dict(candidate=candidate, retainedIndex=duplicate))
    q.require(len(kept) <= 128, 'pilot_candidate_limit')
    return kept, removed


def compare_frame(frame, known, truth, detector, rings, score):
    """Use labels only for the known-box arm and outcome measurements."""
    joined, removed = merge(detector, rings if frame['profile'] == 'hcf' else [])
    # Apply the same duplicate rule to both deployable arms.
    unique_detector, detector_removed = merge(detector, [])
    sources = {'known-box':[dict(box=b, source='known-box', sourceIndex=i) for i,b in enumerate(known)],
               'detector':unique_detector, 'detector-plus-ring':joined}
    rows = {}
    for name, candidates in sources.items():
        boxes = [c['box'] for c in candidates]
        overlaps = [iou(rectangle(b), rectangle(truth)) for b in boxes] if truth is not None else []
        models = {}
        for model in ('baseline', 'candidate'):
            values, hashes = score(model, boxes)
            q.require(len(values) == len(hashes) == len(boxes), 'pilot_score_count')
            decision = outcome(values, boxes, truth)
            models[model] = dict(scores=values, cropSHA256=hashes, outcome=decision,
                                 aboveThreshold=sum(s >= .85 for s in values),
                                 margins=[s-.85 for s in values])
        old, new = models['baseline']['outcome'], models['candidate']['outcome']
        rows[name] = dict(candidates=candidates, focusedProposalPresent=max(overlaps, default=0) >= .5 if truth is not None else None,
                         bestFocusIoU=max(overlaps, default=0) if truth is not None else None,
                         models=models, gain=old not in SUCCESS and new in SUCCESS,
                         loss=old in SUCCESS and new not in SUCCESS)
    return dict(id=frame['id'], sha256=frame['sha256'], group=frame['case'], profile=frame['profile'],
                noFocus=truth is None, arms=rows, removedDuplicates=removed, detectorDuplicates=detector_removed)


def summarize(rows):
    q.require(rows and len({r['id'] for r in rows}) == len(rows), 'pilot_frame_membership')
    summary = {}
    for profile in ('standard', 'hcf'):
        subset = [r for r in rows if r['profile'] == profile]
        summary[profile] = dict(frames=len(subset), groups=len({r['group'] for r in subset}),
                               noFocusFrames=sum(r['noFocus'] for r in subset), arms={})
        for arm in ARMS:
            summary[profile]['arms'][arm] = dict(
                focusedFrames=sum(not r['noFocus'] for r in subset),
                focusedProposed=sum(r['arms'][arm]['focusedProposalPresent'] is True for r in subset),
                outcomes={m:dict(Counter(r['arms'][arm]['models'][m]['outcome'] for r in subset))
                          for m in ('baseline','candidate')},
                gains=[r['id'] for r in subset if r['arms'][arm]['gain']],
                lostPriorSuccesses=[r['id'] for r in subset if r['arms'][arm]['loss']])
    return dict(version=VERSION, rows=rows, profiles=summary, modelAccepted=False,
                threshold=.85, matchingIoU=.5, duplicateIoU=.5,
                limitation='Inspected native development groups. Known boxes are diagnostic. No runtime or promotion change.')


def run():
    import numpy as np
    import torch
    from PIL import Image
    import focus_runtime
    import native343
    from train_focus_ring_detector import load_mobilenetv4_conv_small
    start = time.monotonic()
    cfg = q.load(OUT.parents[2]/'spec.json')['template']
    refs = resolve_inputs(cfg, OUT)
    artifact = document(refs['capture'])
    source = Path(artifact['path'])
    q.require(source.resolve() == source and source.is_relative_to('/Volumes/training-drive/data/NUIAK/HCF371'), 'pilot_source_scope')
    q.require(q.digest(source) == artifact['sha256'], 'pilot_capture_changed')
    capture = q.load(source)
    q.require(capture['complete'] and capture['cleanup'], 'pilot_capture_incomplete')
    q.require(artifact['plan'].get('trainingEligible') is False and
              all(c['role'] == 'development' for c in artifact['plan']['cases']), 'pilot_role')
    predictions = detector_predictions(document(refs['scorecard']))
    raw_rings, mapping = document(refs['ringProposals']), document(refs['mapping'])
    references = {m:document(refs[m+'Selection']) for m in ('baseline','candidate')}
    frames = capture['frames']
    ids = [f['id'] for f in frames]
    q.require(0 < len(ids) <= 64 and len(ids) == len(set(ids)), 'pilot_frame_membership')
    q.require(ids == [r['id'] for r in raw_rings], 'pilot_ring_membership')
    for reference in references.values():
        q.require(reference['threshold'] == .85 and ids == [r['id'] for r in reference['rows']], 'pilot_reference_membership')
    models = {}
    torch.set_num_threads(2)
    focus_runtime.TOOL = checked(refs['tool'])
    for name in ('baseline','candidate'):
        model = load_mobilenetv4_conv_small()(pretrained=False, num_classes=1).eval()
        model.load_state_dict(torch.load(checked(refs[name]), map_location='cpu', weights_only=True)['state_dict'], strict=True)
        models[name] = model
    results = []
    for index, (frame, ring) in enumerate(zip(frames, raw_rings)):
        native343.signature(frame['before'], frame['before'], frame['focus'])
        native343.signature(frame['after'], frame['before'], frame['focus'])
        scene = frame['before']['scene']; w,h = scene['scene_width'],scene['scene_height']
        path = q.local_path(source.parent, frame['path'])
        q.require(q.digest(path) == frame['sha256'] == ring['sha256'], 'pilot_pixels_changed')
        q.require(frame['sha256'] in predictions, 'pilot_missing_detector_frame')
        predicted = predictions[frame['sha256']]
        q.require((w,h) == (predicted['width'],predicted['height']) == (3840,2160), 'pilot_dimensions')
        controls = [e for e in scene['elements'] if e['element_id'] in scene['focus_observation']['plannedFocusIDs']]
        known = [bounds([rectangle(e['rendered_body_geometry']['visible_pixel_bounds'])[k]
                         for k in ('x','y','width','height')],w,h) for e in controls]
        focused = [b for e,b in zip(controls,known) if e['is_focused']]
        q.require(len(focused) <= 1, 'pilot_multiple_focus_labels')
        truth = focused[0] if focused else None
        rings = []
        if frame['profile'] == 'hcf':
            l,t,r,b = mapping['offsets']
            for j,c in enumerate(ring['report']['candidates']):
                box = c['bounds']; x,y,bw,bh = box['x']*w,box['y']*h,box['width']*w,box['height']*h
                rings.append(dict(box=bounds([x-l,y-t,bw+l+r,bh+t+b],w,h),source='mapped-ring',sourceIndex=j))
        cache = {}
        def score(name, boxes):
            if not boxes:
                return [], []
            key = tuple(tuple(b) for b in boxes)
            if key not in cache:
                items = [dict(id=str(i),path=str(path),sha256=frame['sha256'],bounds=b) for i,b in enumerate(boxes)]
                reply = focus_runtime.invoke(items,image_root=Path('/Volumes/training-drive/data/NUIAK'))
                q.require(len(reply['results']) == len(items), 'pilot_crop_count')
                arrays, hashes = [], []
                for item in reply['results']:
                    data = base64.b64decode(item['png'],validate=True)
                    hashes.append(hashlib.sha256(data).hexdigest())
                    with Image.open(io.BytesIO(data)) as image:
                        q.require(image.size == (256,256), 'pilot_crop_size')
                        arrays.append(np.array(image.convert('RGB'),copy=True))
                cache[key] = (torch.from_numpy(np.stack(arrays)).permute(0,3,1,2).float()/255, hashes)
            tensor, hashes = cache[key]
            with torch.no_grad():
                scores = torch.sigmoid(models[name](tensor)).reshape(-1).tolist()
            return scores, hashes
        row = compare_frame(frame,known,truth,predicted['candidates'],rings,score)
        row['rejectedDetectorBoxes'] = predicted['rejected']
        for name, reference in references.items():
            old = reference['rows'][index]
            q.require(old['noFocus'] == row['noFocus'] and old['arms']['known-box']['boxes'] == known, 'pilot_reference_geometry')
            current = row['arms']['known-box']['models'][name]
            previous = old['arms']['known-box']
            q.require(len(current['scores']) == len(previous['scores']) and
                      all(abs(a-b) <= 1e-4 for a,b in zip(current['scores'],previous['scores'])) and
                      current['outcome'] == previous['outcome'], 'pilot_reference_score')
        results.append(row)
        q.save(OUT.parent/'progress.json',dict(step='Score detector boxes: '+frame['id'],completed=index+1,
               total=len(frames),unit='frames',updatedAt=time.time()),replace=True)
    report = summarize(results)
    report.update(inputs=refs, wallSeconds=time.monotonic()-start)
    q.save(OUT/'benchmark_summary.json',report)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))


def report():
    """Join matched pilot branches. Missing reports cannot become acceptance."""
    cfg = q.load(OUT.parents[2]/'spec.json')['template']
    refs = resolve_inputs(cfg, OUT)
    reports = [document(refs[name]) for name in ('button','row','tab')]
    q.require(all(r.get('version') == VERSION for r in reports), 'pilot_report_version')
    for key in ('baseline','candidate','tool','mapping'):
        q.require(all(r['inputs'][key] == reports[0]['inputs'][key] for r in reports), 'pilot_comparison_identity')
    rows = [dict(row,family=family) for family,value in zip(('button','row','tab'),reports) for row in value['rows']]
    result = summarize(rows)
    result['sources'] = refs
    result['families'] = {name:value['profiles'] for name,value in zip(('button','row','tab'),reports)}
    q.save(OUT/'benchmark_summary.json',result)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
