"""T52: measure native HCF ring pixels around the known focused body, with the outer-ring-v2 gates.

For each focused HCF frame in the retained T37 bundle, and its paired Standard frame, the adapter:
- draws the frame into the kernel's analysis space (longest side 960 px, grayscale);
- finds the bright component (>= 160) that reaches the band just outside the known body;
- applies the kernel's geometry gates and its side support and contrast gates to that component.

It reports the first failed gate per frame. Frames where the kernel produced a raw proposal serve as a
self-check: the port must classify them as passing. Labels, pixels, and thresholds stay fixed. No model runs.
Limitation: grayscale drawing differs slightly from CoreGraphics device gray; the self-check measures agreement.
"""
from collections import Counter
from pathlib import Path

import research_queue as q
from template_adapters395 import document, resolve_inputs
from cached_selection405 import verified_report
from coverage_reports402 import rectangle

OUT = None
ANALYSIS = 960.0
BRIGHT = 160
SEARCH = 16  # Analysis pixels around the body where the ring is searched. HCF399: rings extend ~28 px at 4K (~7 px here).


def analysis_image(path):
    import numpy as np
    from PIL import Image
    with Image.open(path) as image:
        scale = min(1.0, ANALYSIS / max(image.size))
        w, h = max(1, int(image.size[0] * scale)), max(1, int(image.size[1] * scale))
        gray = image.convert('L').resize((w, h), Image.BILINEAR)
        return np.asarray(gray, dtype=np.uint8), scale


def side(pix, box, band, horizontal, leading):
    """Port of HCFOuterRingDetector side(): (support fraction, mean contrast) for 1 side."""
    left, right, top, bottom = box
    lo, hi = (left, right) if horizontal else (top, bottom)
    edge = (top if leading else bottom) if horizontal else (left if leading else right)
    direction = 1 if leading else -1
    inset = max(1, (hi - lo) // 5)
    value = (lambda along, across: pix[across, along] / 255.0) if horizontal else (lambda along, across: pix[along, across] / 255.0)
    supported = count = 0
    contrast = 0.0
    for along in range(lo + inset, hi - inset + 1):
        peak = max(value(along, edge + direction * k) for k in range(band))
        inner = min(max(value(along, edge + direction * k), value(along, edge + direction * (k + 1))) for k in range(1, band + 1))
        outer = value(along, edge - direction * band)
        delta = min(peak - inner, peak - outer)
        if peak >= BRIGHT / 255.0 and delta >= 0.12:
            supported += 1
        contrast += delta
        count += 1
    return (supported / count, contrast / count) if count else (0.0, 0.0)


def measure(pix, body):
    """Classify the ring around 1 body box (analysis pixels [x, y, w, h]). Return a dict with the first failed gate."""
    import numpy as np
    from scipy import ndimage
    h, w = pix.shape
    x0, y0 = int(round(body[0])), int(round(body[1]))
    x1, y1 = int(round(body[0] + body[2])) - 1, int(round(body[1] + body[3])) - 1
    wx0, wy0, wx1, wy1 = max(0, x0 - SEARCH), max(0, y0 - SEARCH), min(w - 1, x1 + SEARCH), min(h - 1, y1 + SEARCH)
    window = pix[wy0:wy1 + 1, wx0:wx1 + 1]
    zone = np.ones(window.shape, bool)
    zone[max(0, y0 - wy0):y1 - wy0 + 1, max(0, x0 - wx0):x1 - wx0 + 1] = False  # Band outside the body only.
    band_peak = int(window[zone].max()) if zone.any() else 0
    result = dict(bandPeak=band_peak)
    labels, _ = ndimage.label(pix >= BRIGHT, structure=np.ones((3, 3), int))
    touching = labels[wy0:wy1 + 1, wx0:wx1 + 1][zone & (window >= BRIGHT)]
    if touching.size == 0:
        result['class'] = 'below-brightness' if band_peak >= 128 else 'no-bright-ring'
        return result
    component = Counter(touching.tolist()).most_common(1)[0][0]
    ys, xs = np.nonzero(labels == component)
    left, right, top, bottom = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    bw, bh = right - left + 1, bottom - top + 1
    fraction, fill = bw * bh / (w * h), len(xs) / (bw * bh)
    band = max(2, min(12, min(bw, bh) // 10))
    result.update(component=[left, top, bw, bh], fill=round(fill, 4), fraction=round(fraction, 5), band=band)
    gates = [('size', bw >= 18 and bh >= 12), ('fraction-small', fraction >= 0.002), ('fraction-large', fraction <= 0.45),
             ('fill-low', fill >= 0.02), ('fill-high', fill <= 0.55), ('aspect', bw / bh < 20),
             ('clipped', left >= band and top >= band and right + band < w and bottom + band < h)]
    failed = [name for name, ok in gates if not ok]
    if failed:
        result['class'] = 'geometry:' + failed[0]
        result['failedGates'] = failed
        return result
    sides = [side(pix, (left, right, top, bottom), band, hz, lead) for hz, lead in ((True, True), (True, False), (False, True), (False, False))]
    support, contrast = min(s[0] for s in sides), min(s[1] for s in sides)
    result.update(support=round(support, 4), contrast=round(contrast, 4),
                  sides={name: dict(support=round(v[0], 4), contrast=round(v[1], 4))
                         for name, v in zip(('top', 'bottom', 'left', 'right'), sides)})
    result['class'] = 'support' if support < 0.65 else 'contrast' if contrast < 0.12 else 'pass'
    return result


def summarize(rows):
    """Count classes for frames with and without a kernel proposal. The proposal frames check the port."""
    def count(selected):
        return dict(Counter(r['hcf']['class'] for r in selected).most_common())
    missed = [r for r in rows if not r['hasProposal']]
    found = [r for r in rows if r['hasProposal']]
    agree = sum(r['hcf']['class'] == 'pass' for r in found)
    trusted = not found or agree == len(found)
    classes = count(missed)
    top = max(classes, key=classes.get) if classes else None
    standard_rings = sum(r['standard']['class'] == 'pass' for r in rows)
    return dict(frames=len(rows), missedFrames=len(missed), proposalFrames=len(found),
                missedClasses=classes, proposalClasses=count(found),
                selfCheck=dict(proposalFramesPassing=agree, proposalFrames=len(found), trusted=trusted),
                standardPassing=standard_rings,
                decisions=[dict(slice='missed', dominantClass=top, count=classes.get(top, 0) if top else 0,
                                trusted=trusted)],
                gains=[], lostPriorSuccesses=[], modelAccepted=False)


def run():
    import native343
    from box_intervention410 import producer
    cfg = q.load(OUT.parents[2] / 'spec.json')['template']
    refs = resolve_inputs(cfg, OUT)
    bundle = document(refs['bundle'])
    q.require(set(bundle) == {'version', 'role', 'pairs'} and bundle['version'] == 'cached-selection-inputs-v1', 'bundle_version')
    q.require(bundle['role'] == 'development' and 1 <= len(bundle['pairs']) <= 32, 'bundle_scope')
    rows = []
    for pair in bundle['pairs']:
        selection = verified_report(pair['selection'])
        artifact = document(producer(pair['selection'], refs['model'], refs['tool']))
        capture_path = Path(artifact['path'])
        q.require(capture_path.resolve() == capture_path and capture_path.is_relative_to('/Volumes/training-drive/data/NUIAK/HCF371'),
                  'native_source_scope')
        q.require(q.digest(capture_path) == artifact['sha256'], 'native_source_changed')
        capture = q.load(capture_path)
        frames = {f['id']: f for f in capture['frames']}
        selected = {r['id']: r for r in selection['rows']}
        for frame in capture['frames']:
            row = selected[frame['id']]
            if frame['profile'] != 'hcf' or row['noFocus']:
                continue
            twin = next((f for f in capture['frames'] if f['profile'] == 'standard' and f['case'] == frame['case']
                         and f['focus'] == frame['focus'] and f['repeat'] == frame['repeat']), None)
            q.require(twin is not None, 'standard_pair_missing')
            native343.signature(frame['before'], frame['before'], frame['focus'])
            scene = frame['before']['scene']
            q.require([scene['scene_width'], scene['scene_height']] == [3840, 2160], 'native_mapping_size')
            focused = [e for e in scene['elements'] if e['is_focused']]
            q.require(len(focused) == 1, 'focused_body_count')
            body = rectangle(focused[0]['rendered_body_geometry']['visible_pixel_bounds'])
            out = {}
            for name, item in (('hcf', frame), ('standard', twin)):
                path = q.local_path(capture_path.parent, item['path'])
                q.require(q.digest(path) == item['sha256'], 'native_pixels_changed')
                pix, scale = analysis_image(path)
                box = [body['x'] * scale, body['y'] * scale, body['width'] * scale, body['height'] * scale]
                out[name] = measure(pix, box)
            rows.append(dict(id=frame['id'], case=frame['case'], hasProposal=bool(row['arms']['raw-proposal']['boxes']),
                             retainedOutcome=row['arms']['raw-proposal']['outcome'], **out))
    q.require(rows, 'no_focused_hcf_frames')
    report = summarize(rows)
    report.update(rows=rows, version='ring-pixels-v1', analysisSide=ANALYSIS, brightThreshold=BRIGHT, searchBand=SEARCH,
                  limitation='Port of outer-ring-v2 gates on a PIL grayscale drawing. Trust missed-frame classes only when '
                             'the self-check passes. Inspected development frames; no model or threshold changes.')
    q.save(OUT / 'benchmark_summary.json', report)
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path='benchmark_summary.json', sha256=q.digest(OUT / 'benchmark_summary.json'))]))
