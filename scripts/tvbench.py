"""RESET604 T1.4: TVBench v1 scorer (shipping Core ML path, aggregate-only for sealed apps).

Thin wrapper over `real_app_benchmark543.py` and `coreml_parity562.py`.
Rules (RESET604):
- Shipping path only: Core ML `.mlpackage`, 640 x 640 centered gray-114 letterbox, explicit thresholds.
- Never accepts PyTorch checkpoints for scoring or prediction-derived reference labels.
- Sealed test apps output aggregate counts, per-app metrics, and bootstrap intervals only (no per-frame rows or image paths).
Usage:
  tvbench.py score --manifest MANIFEST.json --predictions PREDS.json [--focus-all FOCUS.json] --out REPORT.json
  tvbench.py eval --manifest MANIFEST.json --mlpackage MODEL.mlpackage [--conf 0.25] --out REPORT.json
  tvbench.py pilot [--out REPORT.json]
"""
import argparse
import ast
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

import coreml_parity562 as cp562
import real_app_benchmark543 as r543
import research_queue as q
from roles559 import ROLES, CLASS_ROLE, role as map_role

VERSION = 'tvbench-v2'
MODEL_PIPELINE_IOU = 0.45
NMS_IOU = 0.30  # Matches NativeUIModelContracts recommendedNMSIoUThreshold (0.30)
MATCH_IOU = 0.5
DEFAULT_FOCUS_THRESHOLD = 0.85
DEFAULT_AMBIGUITY_THRESHOLD = 0.70

SWIFT_FOCUSABLE_RAW = frozenset({
    'collectionItem', 'listRow', 'primaryButton', 'secondaryButton',
    'tabBar', 'cancelAction', 'toggle', 'secureField', 'textField',
    'segmentedControl', 'stepperControl', 'slider',
})
SWIFT_FOCUSABLE_ROLES = frozenset(r for r in (map_role(c) for c in SWIFT_FOCUSABLE_RAW) if r is not None)


def model_class_names(model, explicit=None):
    """Extract class labels from a Core ML model spec or explicit list."""
    if explicit:
        return list(explicit)
    spec = model.get_spec()
    desc = spec.description
    user_def = dict(desc.metadata.userDefined)
    if 'names' in user_def:
        parsed = ast.literal_eval(user_def['names'])
        if isinstance(parsed, dict):
            return [parsed[k] for k in sorted(parsed)]
        if isinstance(parsed, (list, tuple)):
            return list(parsed)
    if 'classes' in user_def:
        return [c.strip() for c in user_def['classes'].split(',') if c.strip()]
    for field in desc.output:
        if field.name == 'confidence' and field.type.WhichOneof('Type') == 'multiArrayType':
            # Fallback to 12 detector roles if shape is 12 or 13 with focus
            shape = list(field.type.multiArrayType.shape)
            if shape and shape[-1] == len(ROLES):
                return list(ROLES)
    # Check Core ML classifier/pipeline labels
    for sub in ('pipeline', 'pipelineClassifier', 'neuralNetwork', 'mlProgram'):
        if spec.HasField(sub):
            pass
    if desc.predictedFeatureName and spec.neuralNetworkClassifier.stringClassLabels.vector:
        return list(spec.neuralNetworkClassifier.stringClassLabels.vector)
    raise ValueError('tvbench_missing_class_names: pass --classes or include metadata.userDefined["classes"]')


def greedy_same_class_nms(detections, iou_threshold=NMS_IOU):
    """Greedy same-class NMS matching NativeUIDetectionRequest.nms."""
    ordered = sorted(detections, key=lambda d: -d['score'])
    kept = []
    for pred in ordered:
        if any(k['cls'] == pred['cls'] and r543._iou(k['box'], pred['box']) >= iou_threshold for k in kept):
            continue
        kept.append(pred)
    return kept


def _is_focusable_class(cls_name, class_names=None):
    if cls_name in SWIFT_FOCUSABLE_RAW:
        return True
    # Only fall back to 12-role focusability when the model taxonomy itself is role-based (12 D3 roles + optional text/focused)
    is_role_model = class_names is not None and set(class_names) <= (set(ROLES) | {'text', 'focused'})
    if is_role_model:
        return cls_name in SWIFT_FOCUSABLE_ROLES
    return False


def _cg_letterbox_image(image_path, size=640):
    """Letterbox via CoreGraphics matching NativeUIDetectionRequest.letterbox byte-for-byte on macOS."""
    import sys
    if sys.platform != 'darwin':
        return None
    import ctypes
    import numpy as np
    from PIL import Image

    cg = ctypes.CDLL('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
    iio = ctypes.CDLL('/System/Library/Frameworks/ImageIO.framework/ImageIO')
    cf = ctypes.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')

    cf.CFDataCreate.restype = ctypes.c_void_p
    cf.CFDataCreate.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long]
    cf.CFStringCreateWithCString.restype = ctypes.c_void_p
    cf.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]
    cf.CFRelease.argtypes = [ctypes.c_void_p]
    iio.CGImageSourceCreateWithData.restype = ctypes.c_void_p
    iio.CGImageSourceCreateWithData.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    iio.CGImageSourceCreateImageAtIndex.restype = ctypes.c_void_p
    iio.CGImageSourceCreateImageAtIndex.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p]
    cg.CGImageGetWidth.restype = ctypes.c_size_t
    cg.CGImageGetWidth.argtypes = [ctypes.c_void_p]
    cg.CGImageGetHeight.restype = ctypes.c_size_t
    cg.CGImageGetHeight.argtypes = [ctypes.c_void_p]
    cg.CGColorSpaceCreateDeviceRGB.restype = ctypes.c_void_p
    cg.CGColorSpaceCreateWithName.restype = ctypes.c_void_p
    cg.CGColorSpaceCreateWithName.argtypes = [ctypes.c_void_p]
    cg.CGColorCreate.restype = ctypes.c_void_p
    cg.CGColorCreate.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_double)]
    cg.CGBitmapContextCreate.restype = ctypes.c_void_p
    cg.CGBitmapContextCreate.argtypes = [
        ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t,
        ctypes.c_size_t, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_uint32,
    ]
    cg.CGContextSetFillColorWithColor.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    class CGRect(ctypes.Structure):
        _fields_ = [('x', ctypes.c_double), ('y', ctypes.c_double), ('w', ctypes.c_double), ('h', ctypes.c_double)]

    cg.CGContextFillRect.argtypes = [ctypes.c_void_p, CGRect]
    cg.CGContextDrawImage.argtypes = [ctypes.c_void_p, CGRect, ctypes.c_void_p]

    raw = Path(image_path).read_bytes()
    handles = []
    try:
        cf_data = cf.CFDataCreate(None, raw, len(raw))
        handles.append(cf_data)
        src = iio.CGImageSourceCreateWithData(cf_data, None)
        handles.append(src)
        img = iio.CGImageSourceCreateImageAtIndex(src, 0, None)
        handles.append(img)
        orig_w, orig_h = int(cg.CGImageGetWidth(img)), int(cg.CGImageGetHeight(img))
        scale = min(float(size) / orig_w, float(size) / orig_h)
        nw, nh = int(orig_w * scale), int(orig_h * scale)
        px, py = (size - nw) // 2, (size - nh) // 2
        buf = (ctypes.c_uint8 * (size * size * 4))()
        dev_rgb = cg.CGColorSpaceCreateDeviceRGB()
        handles.append(dev_rgb)
        gen_name = cf.CFStringCreateWithCString(None, b'kCGColorSpaceGenericRGB', 0x08000100)
        handles.append(gen_name)
        gen_rgb = cg.CGColorSpaceCreateWithName(gen_name)
        handles.append(gen_rgb)
        comps = (ctypes.c_double * 4)(114.0 / 255.0, 114.0 / 255.0, 114.0 / 255.0, 1.0)
        col = cg.CGColorCreate(gen_rgb, comps)
        handles.append(col)
        # kCGImageAlphaNoneSkipLast == 5
        ctx = cg.CGBitmapContextCreate(buf, size, size, 8, size * 4, dev_rgb, 5)
        handles.append(ctx)
        cg.CGContextSetFillColorWithColor(ctx, col)
        cg.CGContextFillRect(ctx, CGRect(0.0, 0.0, float(size), float(size)))
        cg.CGContextDrawImage(ctx, CGRect(float(px), float(py), float(nw), float(nh)), img)
        arr = np.frombuffer(buf, dtype=np.uint8).reshape((size, size, 4))[:, :, :3].copy()
        return Image.fromarray(arr, 'RGB'), orig_w, orig_h, nw, nh, px, py
    finally:
        for h in reversed(handles):
            if h:
                cf.CFRelease(h)


def _coreml_predict_preproc_keyed(model, class_names, cases, conf=0.25, nms_iou=NMS_IOU, size=640):
    """Run Core ML inference using CoreGraphics 640 x 640 letterbox matching Swift NativeUIDetectionRequest."""
    from PIL import Image
    cache_dir = q.ROOT / '.build/debug-output/tvbench-letterbox'
    cache_dir.mkdir(parents=True, exist_ok=True)
    raw = {}
    for c in cases:
        if c.get('status', 'captured') != 'captured':
            continue
        p = q.ROOT / c['image']['path']
        actual_sha = q.digest(p)
        q.require(actual_sha == c['image']['sha256'], 'tvbench_image_sha_mismatch:' + c['id'])
        cg_res = _cg_letterbox_image(p, size=size)
        if cg_res is not None:
            lb_im, orig_w, orig_h, nw, nh, px, py = cg_res
            cache_key = f"{actual_sha[:16]}-sz{size}-cg-genrgb114-v1.png"
        else:
            im = Image.open(p).convert('RGB')
            orig_w, orig_h = im.width, im.height
            scale = min(size / orig_w, size / orig_h)
            nw, nh = int(orig_w * scale), int(orig_h * scale)
            px, py = (size - nw) // 2, (size - nh) // 2
            lb_im = Image.new('RGB', (size, size), (114, 114, 114))
            lb_im.paste(im.resize((nw, nh), Image.BILINEAR), (px, py))
            cache_key = f"{actual_sha[:16]}-sz{size}-rgb-bilin-114.png"
        sq = cache_dir / cache_key
        if not sq.exists():
            lb_im.save(sq)
        y = model.predict({'image': Image.open(sq).convert('RGB'), 'iouThreshold': MODEL_PIPELINE_IOU, 'confidenceThreshold': conf})
        dets = []
        for conf_vec, (cx, cy, w, h) in zip(y['confidence'], y['coordinates']):
            idx = int(conf_vec.argmax())
            score = float(conf_vec[idx])
            if score < conf:
                continue
            x1, y1 = (cx - w / 2) * size, (cy - h / 2) * size
            dets.append(dict(
                cls=class_names[idx],
                box=[
                    float((x1 - px) * orig_w / nw),
                    float((y1 - py) * orig_h / nh),
                    float(w * size * orig_w / nw),
                    float(h * size * orig_h / nh),
                ],
                score=score,
            ))
        raw[c['id']] = greedy_same_class_nms(dets, iou_threshold=nms_iou)
    return raw


def score_focus_with_focusring(
    cases,
    detections_by_id,
    focusring_model,
    conf=0.25,
    threshold=DEFAULT_FOCUS_THRESHOLD,
    ambiguity_threshold=DEFAULT_AMBIGUITY_THRESHOLD,
    class_names=None,
    invoke_fn=None,
):
    """Run shipping Stage 2 FocusRingDetector scoring over focusable Stage 1 boxes with full candidate dispositions."""
    if invoke_fn is None:
        import focus_runtime as fr
        def _invoke(batch, path):
            return fr.invoke(batch, path, allow_out_of_frame=True)
        invoke_fn = _invoke
    fr_path = Path(focusring_model)
    items, lookup = [], {}
    per_case_candidates = {}

    for c in cases:
        if c.get('status', 'captured') != 'captured':
            continue
        p = q.ROOT / c['image']['path']
        w_lim, h_lim = c.get('width'), c.get('height')
        if not w_lim or not h_lim:
            from PIL import Image
            with Image.open(p) as im:
                w_lim, h_lim = im.size
        cands = []
        for idx, d in enumerate(detections_by_id.get(c['id'], [])):
            if d['cls'] == 'focused' or d['score'] < conf:
                continue
            cand = dict(index=idx, cls=d['cls'], box=list(d['box']), score=d['score'])
            if not _is_focusable_class(d['cls'], class_names=class_names):
                cand.update(disposition='unsupportedRole', probability=None, modelInputRGBSHA256=None, isFocused=None)
                cands.append(cand)
                continue
            bx, by, bw, bh = d['box']
            valid_finite = all(isinstance(v, (int, float)) for v in (bx, by, bw, bh))
            if not valid_finite or bw <= 0 or bh <= 0:
                cand.update(disposition='cropRejected', probability=None, modelInputRGBSHA256=None, isFocused=None)
                cands.append(cand)
                continue
            # Match FocusRingClassifier.expandedCropRect intersection test (expand 16%, clamp to frame)
            ex, ey = bw * 0.16, bh * 0.16
            ix1, iy1 = max(0.0, float(bx) - ex), max(0.0, float(by) - ey)
            ix2, iy2 = min(float(w_lim), float(bx) + float(bw) + ex), min(float(h_lim), float(by) + float(bh) + ey)
            if ix2 - ix1 <= 0.0 or iy2 - iy1 <= 0.0:
                cand.update(disposition='cropRejected', probability=None, modelInputRGBSHA256=None, isFocused=None)
                cands.append(cand)
                continue
            item_id = f"{c['id']}|{idx}"
            items.append(dict(id=item_id, path=str(p), sha256=c['image']['sha256'], bounds=[float(bx), float(by), float(bw), float(bh)]))
            lookup[item_id] = (c['id'], len(cands))
            cands.append(cand)
        per_case_candidates[c['id']] = cands

    results_by_item = {}
    batch, seen_paths, batch_pixels = [], {}, 0
    dims_by_id = {
        c['id']: (c.get('width') or 3840, c.get('height') or 2160)
        for c in cases if c.get('status', 'captured') == 'captured'
    }
    for item in items:
        cid = item['id'].split('|', 1)[0]
        iw, ih = dims_by_id.get(cid, (3840, 2160))
        ipx = iw * ih
        new_img_px = 0 if item['path'] in seen_paths else ipx
        if batch and (len(batch) >= 100 or (len(seen_paths) >= 8 and new_img_px) or (batch_pixels + new_img_px > 40_000_000)):
            reply = invoke_fn(batch, fr_path)
            for res in reply['results']:
                results_by_item[res['id']] = res
            batch, seen_paths, batch_pixels = [], {}, 0
            new_img_px = ipx
        batch.append(item)
        if item['path'] not in seen_paths:
            seen_paths[item['path']] = ipx
            batch_pixels += ipx
    if batch:
        reply = invoke_fn(batch, fr_path)
        for res in reply['results']:
            results_by_item[res['id']] = res

    executions = {}
    for c in cases:
        if c.get('status', 'captured') != 'captured':
            continue
        cid = c['id']
        cands = per_case_candidates[cid]
        scored = []
        for idx, cand in enumerate(cands):
            if 'disposition' in cand:
                continue
            item_id = f"{cid}|{cand['index']}"
            res = results_by_item.get(item_id)
            prob = None if res is None else next(
                (float(res[k]) for k in ('probability', 'focusProbability', 'score', 'focused') if isinstance(res.get(k), (int, float))),
                None,
            )
            if prob is None:
                cand.update(disposition='predictionFailed', probability=None, modelInputRGBSHA256=None, isFocused=None)
            else:
                cand.update(
                    disposition='scored',
                    probability=prob,
                    modelInputRGBSHA256=res.get('modelInputRGBSHA256'),
                    cropMilliseconds=res.get('cropMilliseconds'),
                    inferenceMilliseconds=res.get('inferenceMilliseconds'),
                )
                scored.append((prob, idx, cand['box']))
        winner = max(scored, key=lambda t: t[0]) if scored else None
        has_winner = winner is not None and winner[0] >= threshold
        winner_idx = winner[1] if has_winner else None
        for idx, cand in enumerate(cands):
            if cand['disposition'] == 'scored':
                p_val = cand['probability']
                if idx == winner_idx:
                    cand['isFocused'] = True
                    cand['isAmbiguous'] = False
                elif ambiguity_threshold <= p_val < threshold:
                    cand['isFocused'] = None
                    cand['isAmbiguous'] = True
                else:
                    cand['isFocused'] = False
                    cand['isAmbiguous'] = False
        executions[cid] = dict(
            threshold=threshold,
            ambiguityThreshold=ambiguity_threshold,
            focusBox=winner[2] if has_winner else None,
            winnerProbability=winner[0] if has_winner else None,
            maxProbability=winner[0] if winner is not None else None,
            eligibleCount=sum(1 for x in cands if x['disposition'] != 'unsupportedRole'),
            scoredCount=len(scored),
            unsupportedRoleCount=sum(1 for x in cands if x['disposition'] == 'unsupportedRole'),
            cropRejectedCount=sum(1 for x in cands if x['disposition'] == 'cropRejected'),
            failedCount=sum(1 for x in cands if x['disposition'] == 'predictionFailed'),
            candidates=cands,
        )
    return executions


def predict_coreml(mlpackage, cases, conf=0.25, names=None, focusring_model=None, focusring_threshold=DEFAULT_FOCUS_THRESHOLD, nms_iou=NMS_IOU):
    """Run shipping Core ML inference (640 x 640 letterbox, second greedy NMS, focusable-filtered FocusRing)."""
    ml_path = Path(mlpackage)
    q.require(ml_path.suffix == '.mlpackage' and ml_path.exists(), 'tvbench_shipping_mlpackage_required')
    import coremltools as ct
    model = ct.models.MLModel(str(ml_path))
    class_names = model_class_names(model, names)
    dets_by_id = _coreml_predict_preproc_keyed(model, class_names, cases, conf=conf, nms_iou=nms_iou)
    fr_exec = (
        score_focus_with_focusring(cases, dets_by_id, focusring_model, conf=conf, threshold=focusring_threshold, class_names=class_names)
        if focusring_model
        else {}
    )
    out = {}
    for c in cases:
        if c.get('status', 'captured') != 'captured':
            continue
        dets = dets_by_id[c['id']]
        # If detector includes 'focused' box (Arm A, Phase 4), extract highest-scoring focus box
        focused_dets = [d for d in dets if d['cls'] == 'focused' and d['score'] >= conf]
        if focused_dets:
            focus_box = max(focused_dets, key=lambda d: d['score'])['box']
            focus_exec = dict(policy='detector-focused-class-v1', focusBox=focus_box)
        elif c['id'] in fr_exec:
            focus_exec = fr_exec[c['id']]
            focus_box = focus_exec['focusBox']
        else:
            focus_box, focus_exec = None, None
        out[c['id']] = dict(
            id=c['id'],
            imageSHA256=c['image']['sha256'],
            pixelSHA256=c.get('pixelSHA256'),
            status='ok',
            detections=[dict(d, **{'class': d['cls']}) for d in dets if d['cls'] != 'focused'],
            focusBox=focus_box,
            focusExecution=focus_exec,
            latencyScope='unavailable',
            latencyUnavailableReason='offline_tvbench_coreml_eval',
        )
    return out


def _map_box_class(cls_name, target_classes):
    if cls_name in target_classes or cls_name is None:
        return cls_name
    mapped = map_role(cls_name)
    return mapped if mapped in target_classes else None


def _bootstrap_recall_and_focus(rows, apps, samples=2000):
    """Stratified whole-flow bootstrap 95% CIs within apps for both control recall and focus accuracy."""
    rng = random.Random(604)
    grouped = {a: defaultdict(list) for a in apps}
    for r in rows:
        grouped[r['app']][r['flow']].append(r)
    focus_draws, recall_draws = [], []
    for _ in range(samples):
        f_rates, r_rates = [], []
        for app in apps:
            flows = list(grouped[app].values())
            sampled = [r for flow in rng.choices(flows, k=len(flows)) for r in flow] if flows else []
            known_f = [r for r in sampled if r.get('focusState', 'unknown') != 'unknown']
            if known_f:
                f_rates.append(sum(r.get('focusOutcome') in ('correct', 'correct-abstention') for r in known_f) / len(known_f))
            tot_obj = sum(len(r.get('objects', [])) for r in sampled)
            if tot_obj:
                tot_det = sum(len(r.get('detected', [])) for r in sampled)
                r_rates.append(tot_det / tot_obj)
        if f_rates:
            focus_draws.append(sum(f_rates) / len(f_rates))
        if r_rates:
            recall_draws.append(sum(r_rates) / len(r_rates))
    focus_draws.sort()
    recall_draws.sort()
    ci = lambda arr: [round(arr[int(0.025 * len(arr))], 4), round(arr[min(len(arr) - 1, int(0.975 * len(arr)))], 4)] if arr else None
    return dict(method='stratified whole-flow bootstrap within apps', samples=samples, seed=604,
                focusInterval95=ci(focus_draws), controlRecallInterval95=ci(recall_draws))


CONTRACT_CLASSES666 = frozenset(('button', 'cell', 'picture', 'textField', 'toggle',
                                  'segmentedControl', 'pageControl', 'bar', 'dialog', 'indicator'))


def prediction_class_map666(manifest, classes):
    """Project predicted labels only. Reviewed native truth stays unchanged."""
    mapping = {}
    if set(classes) == CONTRACT_CLASSES666:
        # Generic containers and adjustable controls have no single contract class.
        mapping = {raw: role if role in CONTRACT_CLASSES666 else None
                   for raw, role in CLASS_ROLE.items()}
    mapping.update(manifest.get('predictionClassMap', {}))
    q.require(all(value is None or value in classes for value in mapping.values()),
              'tvbench_prediction_class_map')
    return mapping


TRAIN666_METRICS = ('localizationRecall', 'localizationPrecision', 'roleAccuracy',
                    'focusTop1', 'falseSelectionRate')


def _train666_counts(labels, detections, prediction):
    """Match geometry first. Unknown roles do not remove localized targets."""
    reviewed_objects = [o for o in labels['objects']
                        if o.get('sourceFlag') not in ('not-control', 'wrong-box')]
    targets = [o for o in reviewed_objects if o['visibility'] != 'unknown']
    detections = [d for d in detections if d.get('class', d.get('cls')) != 'focused']
    detections = detections if prediction.get('status', 'ok') == 'ok' else []
    used, pairs = set(), []
    for detection in sorted(detections, key=lambda d: -d['score']):
        eligible = [(r543._iou(detection['box'], o['box']), i)
                    for i, o in enumerate(targets) if i not in used]
        overlap, index = max(eligible, default=(0, -1))
        if overlap >= MATCH_IOU:
            used.add(index)
            pairs.append((targets[index], detection))
    role_pairs = [(o, d) for o, d in pairs if o['class'] is not None]
    confusion = defaultdict(lambda: defaultdict(int))
    for obj, detection in role_pairs:
        confusion[obj['class']][detection['class']] += 1
    # Unknown visibility makes unmatched predictions ambiguous, even on a complete screen.
    precision_known = labels['complete'] and len(targets) == len(reviewed_objects)
    focus = labels['focus']['state']
    selected = prediction.get('focusBox')
    success = prediction.get('status', 'ok') == 'ok'
    focus_available = ('focusBox' in prediction or prediction.get('focusStatus') == 'failed') and prediction.get('focusStatus') != 'unavailable'
    if 'focusExecution' in prediction and prediction['focusExecution'] is None:
        focus_available = False
    return dict(
        localizationRecall=[len(pairs), len(targets)],
        localizationPrecision=[len(pairs), len(detections)] if precision_known else [0, 0],
        roleAccuracy=[sum(o['class'] == d['class'] for o, d in role_pairs), len(role_pairs)],
        focusTop1=[int(focus_available and success and selected is not None and focus == 'focused' and
                       r543._iou(selected, labels['focus']['box']) >= MATCH_IOU), int(focus == 'focused' and focus_available)],
        falseSelectionRate=[int(selected is not None), int(focus in ('no_focus', 'known_no_focus'))]
            if focus_available and focus in ('no_focus', 'known_no_focus') else [0, 0],
        focusUnavailable=int(not focus_available),
        roleConfusion={role: dict(values) for role, values in confusion.items()},
    )


def _train666_aggregate(rows):
    result = {}
    for metric in TRAIN666_METRICS:
        numerator = sum(r['train666Counts'][metric][0] for r in rows)
        denominator = sum(r['train666Counts'][metric][1] for r in rows)
        result[metric] = dict(numerator=numerator, denominator=denominator,
                              value=numerator / denominator if denominator else None)
    confusion = defaultdict(lambda: defaultdict(int))
    for row in rows:
        for actual, predicted in row['train666Counts']['roleConfusion'].items():
            for role, count in predicted.items():
                confusion[actual][role] += count
    result['focusUnavailableScreens'] = sum(r['train666Counts'].get('focusUnavailable', 0) for r in rows)
    result['roleConfusion'] = {role: dict(values) for role, values in confusion.items()}
    return result


def train666_summary(rows, apps, samples=2000):
    """Report equal-app rates and layout-cluster intervals without a model verdict."""
    rows = [r for r in rows if 'train666Counts' in r]
    grouped = {app: defaultdict(list) for app in apps}
    for row in rows:
        grouped[row['app']][row.get('layoutId') or row['flow']].append(row)
    per_app = {app: _train666_aggregate([r for group in grouped[app].values() for r in group])
               for app in apps}
    equal = {}
    for metric in TRAIN666_METRICS:
        rates = [summary[metric]['value'] for summary in per_app.values()
                 if summary[metric]['value'] is not None]
        equal[metric] = dict(value=sum(rates) / len(rates) if rates else None, apps=len(rates))
    rng = random.Random(666)
    draws = {app: {metric: [] for metric in TRAIN666_METRICS} for app in apps}
    mean_draws = {metric: [] for metric in TRAIN666_METRICS}
    for _ in range(samples):
        rates = defaultdict(list)
        for app in apps:
            groups = list(grouped[app].values())
            sampled = [r for group in rng.choices(groups, k=len(groups)) for r in group] if groups else []
            summary = _train666_aggregate(sampled)
            for metric in TRAIN666_METRICS:
                value = summary[metric]['value']
                if value is not None:
                    draws[app][metric].append(value)
                    rates[metric].append(value)
        for metric, values in rates.items():
            # Keep the eligible app set fixed for each metric.
            if len(values) == equal[metric]['apps']:
                mean_draws[metric].append(sum(values) / len(values))
    def interval(values):
        values = sorted(values)
        return [values[int(.025 * len(values))], values[min(len(values) - 1, int(.975 * len(values)))]] if values else None
    for app in apps:
        for metric in TRAIN666_METRICS:
            per_app[app][metric]['interval95'] = interval(draws[app][metric])
    for metric in TRAIN666_METRICS:
        equal[metric]['interval95'] = interval(mean_draws[metric])
    layouts = {(r['app'], r['layoutId']) for r in rows if r.get('layoutId')}
    missing = sum(not r.get('layoutId') for r in rows)
    eligible = len(layouts) >= 30 and missing == 0
    return dict(perApplication=per_app, equalAppMean=equal,
                independentLayoutCount=len(layouts), missingLayoutIdCount=missing,
                decisionEligible=eligible,
                verdict='not_requested' if eligible else 'refused',
                refusalReasons=(['fewer_than_30_independent_layouts'] if len(layouts) < 30 else []) +
                               (['missing_independent_layout_ids'] if missing else []),
                uncertainty=dict(method='whole-layout bootstrap within apps; equal-app mean',
                                 samples=samples, seed=666),
                denominatorPolicy=dict(localizationRecall='visible, clipped, or occluded reviewed boxes, including unknown roles; failures count as misses',
                    localizationPrecision='predictions on complete screens without unknown visibility only',
                    roleAccuracy='class-agnostic matched targets with known roles only',
                    focusTop1='focused screens with executed focus, including failures; absent focusBox or unavailable focusStatus is excluded',
                    falseSelectionRate='known_no_focus screens only; legacy no_focus is an alias'),
                modelAccepted=False, metricsStatus='provisional')


def score_manifest(manifest, predictions_by_id, classes=None, map_to_roles=False, focus_all=None, allow_sealed_rows=False):
    """Score a TVBench / real-app manifest against predictions without reading sealed test artifacts."""
    classes = list(classes or (ROLES if map_to_roles else manifest['classes']))
    conf = manifest['baseline']['confidence'] if 'baseline' in manifest else 0.25
    sealed_apps = {a['id'] for a in manifest.get('apps', []) if a.get('sealed') or a.get('split') == 'sealed'}
    if manifest.get('split') == 'sealed' or manifest.get('sealed'):
        sealed_apps.update(a['id'] for a in manifest.get('apps', []))

    rows = []
    for c in manifest['cases']:
        row = dict(id=c['id'], app=c['app'], flow=c['flow'], status=c.get('status', 'captured'))
        if row['status'] != 'captured':
            rows.append(row)
            continue
        lbl_path = q.ROOT / c['labels']['path']
        if 'sha256' in c['labels']:
            q.require(q.digest(lbl_path) == c['labels']['sha256'], 'tvbench_labels_sha_mismatch:' + c['id'])
        labels = q.load(lbl_path)
        img_path = q.ROOT / c['image']['path']
        if img_path.is_file() and len(c['image']['sha256']) == 64:
            q.require(q.digest(img_path) == c['image']['sha256'], 'tvbench_source_image_sha_mismatch:' + c['id'])
        if labels['focus']['state'] == 'known_no_focus':
            labels = dict(labels, focus=dict(labels['focus'], state='no_focus'))
        # Reject prediction-derived labels unconditionally
        r543.validate_labels(labels, c, manifest['classes'])
        geometry_labels = labels
        if map_to_roles:
            mapped_objs = []
            for o in labels['objects']:
                mc = _map_box_class(o['class'], classes)
                if mc is not None:
                    mapped_objs.append(dict(o, **{'class': mc}))
            labels = dict(labels, objects=mapped_objs)

        p = predictions_by_id[c['id']]
        q.require(p['imageSHA256'] == c['image']['sha256'], 'tvbench_image_sha_mismatch:' + c['id'])
        raw_dets = p.get('detections', [])
        norm_dets = []
        for d in raw_dets:
            dc = d.get('class', d.get('cls'))
            mc = _map_box_class(dc, classes) if map_to_roles else dc
            if mc in classes:
                norm_dets.append(dict(cls=mc, box=d['box'], score=d['score'], **{'class': mc}))

        geometry_objects = [dict(o, **{'class': _map_box_class(o['class'], classes) if map_to_roles else o['class']})
                            for o in geometry_labels['objects']]
        prediction_class_map = prediction_class_map666(manifest, classes)
        geometry_dets = [dict(d, **{'class': (_map_box_class(d.get('class', d.get('cls')), classes)
                                             if map_to_roles else prediction_class_map.get(d.get('class', d.get('cls')),
                                                                                          d.get('class', d.get('cls')))) or 'unknown'})
                         for d in raw_dets if d['score'] >= conf and d.get('class', d.get('cls')) != 'focused']
        row['train666Counts'] = _train666_counts(dict(geometry_labels, objects=geometry_objects), geometry_dets, p)
        row['layoutId'] = c.get('independentLayoutId') or c.get('layoutId')
        above = [d for d in norm_dets if d['score'] >= conf]
        known, found, extra, wrong, loc = r543.match(labels, above, MATCH_IOU)
        f = labels['focus']
        sel = p.get('focusBox')
        outcome = 'unknown'
        if f['state'] != 'unknown':
            if p.get('status', 'ok') == 'failed':
                outcome = 'execution-failure'
            elif f['state'] == 'no_focus':
                outcome = 'correct-abstention' if sel is None else 'false-selection'
            elif sel is None:
                outcome = 'abstention'
            else:
                outcome = 'correct' if r543._iou(sel, f['box']) >= MATCH_IOU else 'wrong-selection'

        row.update(
            missedControls=len(known) - len(found),
            unmatchedDetectionCount=len(extra),
            status=p.get('status', 'ok'),
            objects=known,
            detected=sorted(found),
            unmatched=extra,
            wrongClass=wrong,
            localization=loc,
            allDetections=norm_dets,
            complete=labels['complete'],
            unresolved=len(labels['objects']) - len(known),
            focusState=f['state'],
            focusOutcome=outcome,
            latencyMs=None,
            measuredLatencyMs=p.get('latencyMs'),
            latencyScope=p.get('latencyScope', 'unavailable'),
        )
        rows.append(row)

    apps = [a['id'] for a in manifest['apps']]
    per_app = {}
    for app_id in apps:
        app_rows = [r for r in rows if r['app'] == app_id]
        agg = r543.aggregate(app_rows, classes)
        app_coco = r543.official_ap(app_rows, classes)
        app_official_ap50 = app_coco.get('metrics', {}).get('AP50') if app_coco.get('status') == 'available' else None
        app_custom_ap50 = None
        if app_coco.get('status') != 'available':
            app_eligible = [r for r in app_rows if r.get('complete') and r.get('status') == 'ok' and not r.get('unresolved')]
            if app_eligible:
                custom_res = r543.custom_ap(app_eligible, classes)
                app_coco = dict(app_coco, customFallback=custom_res)
                app_custom_ap50 = (custom_res.get('metrics') or {}).get('AP50')
        agg['officialCOCO'] = app_coco
        agg['officialAP50'] = app_official_ap50
        agg['customAP50'] = app_custom_ap50
        tp = sum(v['recall']['numerator'] for v in agg['perClass'].values())
        tot = sum(v['recall']['denominator'] for v in agg['perClass'].values())
        agg['controlsFound'] = r543.ratio(tp, tot)
        per_app[app_id] = agg

    overall = r543.aggregate(rows, classes)
    overall_tp = sum(v['recall']['numerator'] for v in overall['perClass'].values())
    overall_tot = sum(v['recall']['denominator'] for v in overall['perClass'].values())
    overall['controlsFound'] = r543.ratio(overall_tp, overall_tot)
    coco = r543.official_ap(rows, classes)
    official_ap50 = coco.get('metrics', {}).get('AP50') if coco.get('status') == 'available' else None
    custom_ap50 = None
    if coco.get('status') != 'available':
        eligible = [r for r in rows if r.get('complete') and r.get('status') == 'ok' and not r.get('unresolved')]
        if eligible:
            custom_res = r543.custom_ap(eligible, classes)
            coco = dict(coco, customFallback=custom_res)
            custom_ap50 = (custom_res.get('metrics') or {}).get('AP50')
    ci = _bootstrap_recall_and_focus(rows, apps)

    # Focus summary across all apps (incorporating optional focus_all multi-app pilot)
    focus_summary = dict(
        all=dict(
            frames=sum(1 for r in rows if 'focusOutcome' in r),
            focusedFrames=sum(1 for r in rows if r.get('focusState') == 'focused'),
            correct=sum(1 for r in rows if r.get('focusOutcome') in ('correct', 'correct-abstention')),
            correctFocused=sum(1 for r in rows if r.get('focusState') == 'focused' and r.get('focusOutcome') == 'correct'),
            noFocusFrames=sum(1 for r in rows if r.get('focusState') == 'no_focus'),
            falseNoFocusSelections=sum(1 for r in rows if r.get('focusState') == 'no_focus' and r.get('focusOutcome') == 'false-selection'),
        )
    )
    if focus_all is not None:
        focus_summary['extendedFocusAll'] = focus_all['summary']

    report = dict(
        version=VERSION,
        train666=dict(train666_summary(rows, apps),
                      predictionProjection=dict(version='predicted-role-to-contract-v1',
                                                mapping=prediction_class_map666(manifest, classes))),
        manifestSHA256=hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest(),
        classes=classes,
        confidence=conf,
        nmsIoU=NMS_IOU,
        matchingIoU=MATCH_IOU,
        sealed=bool(sealed_apps),
        sealedApps=sorted(sealed_apps),
        overall=overall,
        officialCOCO=coco,
        officialAP50=official_ap50,
        customAP50=custom_ap50,
        perApplication=per_app,
        focusSummary=focus_summary,
        uncertainty=ci,
        modelAccepted=False,
        metricsStatus='provisional',
    )

    if not sealed_apps or allow_sealed_rows:
        # Expose rows only when no sealed app is present
        report['rows'] = [
            {k: v for k, v in r.items() if k not in ('objects', 'allDetections', 'unmatched')}
            for r in rows
        ]
    return report


def score_pilot():
    """Reproduce the REALAPP554 pilot baseline numbers (23/207 controls, AP50 0.206, focus 0/15)."""
    manifest = q.load(q.ROOT / 'reports/work/REALAPP554/pilot-v2/manifest.json')
    preds = q.load(q.ROOT / 'reports/work/REALAPP554/pilot-v2/predictions.json')
    focus_all = q.load(q.ROOT / 'reports/work/REALAPP554/pilot-v2/focus-all.json')
    by_id = {r['id']: r for r in preds['cases']}
    return score_manifest(manifest, by_id, classes=manifest['classes'], map_to_roles=False, focus_all=focus_all)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='cmd', required=True)

    p_score = sub.add_parser('score', help='Score precomputed predictions against a manifest')
    p_score.add_argument('--manifest', type=Path, required=True)
    p_score.add_argument('--predictions', type=Path, required=True)
    p_score.add_argument('--focus-all', type=Path)
    p_score.add_argument('--roles', action='store_true', help='Map classes to 12 RESET604 roles')
    p_score.add_argument('--out', type=Path)

    p_eval = sub.add_parser('eval', help='Evaluate a Core ML .mlpackage on a manifest')
    p_eval.add_argument('--manifest', type=Path, required=True)
    p_eval.add_argument('--mlpackage', type=Path, required=True)
    p_eval.add_argument('--conf', type=float, default=0.25)
    p_eval.add_argument('--classes', nargs='*')
    p_eval.add_argument('--roles', action='store_true', help='Map classes to 12 RESET604 roles')
    p_eval.add_argument('--focusring', type=Path, help='Optional Stage 2 FocusRingDetector.mlmodelc/.mlpackage')
    p_eval.add_argument('--focusring-threshold', type=float, default=0.85)
    p_eval.add_argument('--out', type=Path)

    p_pilot = sub.add_parser('pilot', help='Reproduce REALAPP554 pilot baseline numbers')
    p_pilot.add_argument('--out', type=Path)

    args = parser.parse_args()
    if args.cmd == 'pilot':
        report = score_pilot()
    elif args.cmd == 'score':
        manifest = q.load(args.manifest)
        preds = q.load(args.predictions)
        by_id = {r['id']: r for r in preds['cases']} if isinstance(preds, dict) and 'cases' in preds else preds
        focus_all = q.load(args.focus_all) if args.focus_all else None
        report = score_manifest(manifest, by_id, map_to_roles=args.roles, focus_all=focus_all)
    else:
        manifest = q.load(args.manifest)
        if manifest.get('baseline'):
            manifest = dict(manifest, baseline=dict(manifest['baseline'], confidence=args.conf))
        preds = predict_coreml(
            args.mlpackage,
            manifest['cases'],
            conf=args.conf,
            names=args.classes,
            focusring_model=args.focusring,
            focusring_threshold=args.focusring_threshold,
        )
        report = score_manifest(manifest, preds, map_to_roles=args.roles)

    summary = dict(
        version=report['version'],
        train666=report['train666'],
        controlsFound=report['overall']['controlsFound'],
        officialAP50=report['officialAP50'],
        customAP50=report['customAP50'],
        focusSummary=report['focusSummary'],
        sealed=report['sealed'],
        uncertainty=report['uncertainty'],
    )
    print(json.dumps(summary, indent=2))
    if getattr(args, 'out', None):
        args.out.parent.mkdir(parents=True, exist_ok=True)
        q.save(args.out, report, replace=True)


if __name__ == '__main__':
    main()
