"""RESET604 T1.3: Deterministic non-model Vision geometry + OCR draft proposer for blinded review.

Never loads Core ML, YOLO, FocusRing, or Arm B weights, and never prints per-frame
sealed outputs. Outputs `real_app_review554.check`-compatible pending drafts
(`provenance: "nonmodel-draft:vision-geometry"`) plus optional non-binding `hints/`
ranking top deterministic focus candidates for 1-click UI triage.
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

import perception_benchmark as pb
import real_app_review554 as rev554
import research_queue as q

PROVENANCE = 'nonmodel-draft:vision-geometry'
DEFAULT_PROBE_BIN = q.ROOT / '.build/vision_geometry_probe'
DEFAULT_PROBE_SRC = q.ROOT / 'scripts/vision_geometry_probe.swift'


def ensure_probe_binary(bin_path=DEFAULT_PROBE_BIN, src_path=DEFAULT_PROBE_SRC):
    bin_path = Path(bin_path)
    src_path = Path(src_path)
    if bin_path.is_file() and bin_path.stat().st_mtime >= src_path.stat().st_mtime:
        return bin_path
    bin_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['swiftc', '-O', str(src_path), '-o', str(bin_path)], check=True, capture_output=True, text=True)
    return bin_path


def run_vision_probe(image_paths, bin_path=DEFAULT_PROBE_BIN):
    if not image_paths:
        return {}
    bin_path = ensure_probe_binary(bin_path=bin_path)
    with tempfile.NamedTemporaryFile('w', suffix='.json') as tf:
        json.dump({'images': [str(p) for p in image_paths]}, tf)
        tf.flush()
        raw = subprocess.check_output([str(bin_path), tf.name], text=True)
    return {row['path']: row for row in json.loads(raw)}


def _clamp_box(box, width, height):
    x, y, w, h = [float(v) for v in box]
    x = max(0.0, min(x, width - 1.0))
    y = max(0.0, min(y, height - 1.0))
    w = max(1.0, min(w, width - x))
    h = max(1.0, min(h, height - y))
    return [round(x, 1), round(y, 1), round(w, 1), round(h, 1)]


def _center_in(inner, outer, margin=4.0):
    cx = inner[0] + inner[2] * 0.5
    cy = inner[1] + inner[3] * 0.5
    return (
        outer[0] - margin <= cx <= outer[0] + outer[2] + margin
        and outer[1] - margin <= cy <= outer[1] + outer[3] + margin
    )


def _snap_edge_box(gray, seed_box, width, height):
    """Expand or snap a text-seeded pill/row box if strong symmetric contrast edges surround it."""
    sx, sy, sw, sh = seed_box
    pad_x = max(sh * 0.85, 24.0 * (width / 1920.0))
    pad_y = max(sh * 0.42, 12.0 * (height / 1080.0))
    return _clamp_box([sx - pad_x, sy - pad_y, sw + 2.0 * pad_x, sh + 2.0 * pad_y], width, height)


def _classify_box(box, width, height, text_inside_count, app=''):
    x, y, w, h = box
    nw, nh = w / width, h / height
    ny = (y + 0.5 * h) / height
    if 'TVSettings' in app and nw >= 0.25 and 0.03 <= nh <= 0.11:
        return 'listRow'
    if nw >= 0.45 and nh <= 0.10:
        return 'listRow'
    if nw >= 0.11 and nh >= 0.12:
        return 'collectionItem'
    if ny <= 0.22 and nh <= 0.09:
        return 'secondaryButton'
    if nh <= 0.11 and nw <= 0.35:
        return 'secondaryButton'
    if text_inside_count >= 1 and nh > 0.11:
        return 'collectionItem'
    return 'secondaryButton'


def _merge_line_texts(text_boxes, width, height):
    """Merge horizontal fragments on the same pill baseline before snapping unwrapped controls."""
    scale = width / 1920.0
    ordered = sorted(text_boxes, key=lambda b: (b[1], b[0]))
    merged = []
    for tb in ordered:
        tx, ty, tw, th = tb
        tcy = ty + 0.5 * th
        matched = None
        for cur in merged:
            cx, cy, cw, ch = cur
            ccy = cy + 0.5 * ch
            if abs(tcy - ccy) <= 0.55 * max(th, ch):
                gap = max(tx - (cx + cw), cx - (tx + tw))
                if -8.0 * scale <= gap <= 26.0 * scale:
                    matched = cur
                    break
        if matched is None:
            merged.append(list(tb))
        else:
            nx0 = min(matched[0], tx)
            ny0 = min(matched[1], ty)
            nx1 = max(matched[0] + matched[2], tx + tw)
            ny1 = max(matched[1] + matched[3], ty + th)
            matched[:] = [nx0, ny0, nx1 - nx0, ny1 - ny0]
    return merged


def _focus_outlier_scores(rgb_arr, boxes, width, height):
    """Pure pixel contrast/lift/ring outlier score per box relative to screen peers (no ML weights)."""
    if not boxes:
        return []
    gray = 0.299 * rgb_arr[:, :, 0] + 0.587 * rgb_arr[:, :, 1] + 0.114 * rgb_arr[:, :, 2]
    sat = rgb_arr.max(axis=2) - rgb_arr.min(axis=2)
    h_img, w_img = gray.shape
    raw = []
    for box in boxes:
        bx, by, bw, bh = [float(v) for v in box]
        x0 = max(0, min(w_img - 2, int(round(bx))))
        y0 = max(0, min(h_img - 2, int(round(by))))
        x1 = max(x0 + 2, min(w_img, int(round(bx + bw))))
        y1 = max(y0 + 2, min(h_img, int(round(by + bh))))
        inner = gray[y0:y1, x0:x1]
        in_mean = float(inner.mean())
        in_p90 = float(np.percentile(inner, 90))
        in_sat = float(sat[y0:y1, x0:x1].mean())
        pad = max(4, int(round(min(bw, bh) * 0.12)))
        rx0, ry0 = max(0, x0 - pad), max(0, y0 - pad)
        rx1, ry1 = min(w_img, x1 + pad), min(h_img, y1 + pad)
        rim_patch = gray[ry0:ry1, rx0:rx1]
        mask = np.ones(rim_patch.shape, dtype=bool)
        mask[y0 - ry0:y1 - ry0, x0 - rx0:x1 - rx0] = False
        rim = rim_patch[mask] if mask.any() else inner.ravel()
        rim_mean = float(rim.mean())
        rim_p95 = float(np.percentile(rim, 95))
        bright_ring = float((rim > 215.0).mean())
        contrast = abs(in_mean - rim_mean) + 0.4 * max(0.0, rim_p95 - rim_mean)
        area_norm = (bw * bh) / float(width * height)
        raw.append([in_mean, in_p90, in_sat, rim_p95, bright_ring, contrast, area_norm])

    mat = np.asarray(raw, dtype=np.float64)
    med = np.median(mat, axis=0)
    iqr = np.maximum(np.std(mat, axis=0), 1e-4)
    z = (mat - med) / iqr
    # tvOS focus typically shows lifted brightness/ring/contrast outlier vs peers on the same row/screen.
    scores = (
        1.15 * np.maximum(0.0, z[:, 0])
        + 0.70 * np.maximum(0.0, z[:, 1])
        + 1.35 * np.maximum(0.0, z[:, 4])
        + 0.85 * np.maximum(0.0, z[:, 5])
        + 0.25 * z[:, 2]
        + 0.15 * np.maximum(0.0, z[:, 6])
    )
    return [float(s) for s in scores]


def propose_for_frame(image_path, probe_row, app='', max_objects=36):
    """Build non-model control & focus draft proposals for one frame."""
    with Image.open(image_path) as im:
        rgb = np.asarray(im.convert('RGB'), dtype=np.float32)
    height, width = rgb.shape[:2]
    gray = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    frame_area = float(width * height)
    scale = width / 1920.0

    rects = []
    for r in probe_row.get('rects', []):
        x0, y0, x1, y1 = r['xyxy']
        w, h = x1 - x0, y1 - y0
        area = w * h
        if w < 28.0 * scale or h < 22.0 * scale:
            continue
        if area / frame_area > 0.42:
            continue
        if w / width > 0.90 and h / height > 0.18:
            continue
        rects.append((float(r.get('confidence', 0.5)), _clamp_box([x0, y0, w, h], width, height)))

    # Keep highest-confidence non-duplicate rects
    rects.sort(key=lambda item: (-item[0], item[1][1], item[1][0]))
    kept_rects = []
    for _, rb in rects:
        if any(pb._iou(rb, kb) >= 0.58 for kb in kept_rects):
            continue
        kept_rects.append(rb)

    # Filter out container rects that strictly enclose >= 2 smaller kept rects (likely section cards/panels)
    pruned_rects = []
    for i, rb in enumerate(kept_rects):
        enclosed = sum(
            1 for j, ob in enumerate(kept_rects)
            if i != j and _center_in(ob, rb, margin=-4.0) and (ob[2] * ob[3]) < 0.6 * (rb[2] * rb[3])
        )
        if enclosed >= 2 and (rb[2] * rb[3]) / frame_area > 0.08:
            continue
        pruned_rects.append(rb)

    # Collect clean text lines (skip tiny footer text or huge paragraph blocks)
    text_boxes = []
    for t in probe_row.get('texts', []):
        if float(t.get('confidence', 0.0)) < 0.25:
            continue
        x0, y0, x1, y1 = t['xyxy']
        w, h = x1 - x0, y1 - y0
        if w < 14.0 * scale or h < 10.0 * scale or h > 110.0 * scale:
            continue
        if w / width > 0.65:
            continue
        # Ignore status/header right-edge tiny captions above y=0.05 only if super small
        text_boxes.append(_clamp_box([x0, y0, w, h], width, height))

    merged_texts = _merge_line_texts(text_boxes, width, height)

    # First check how many texts sit inside each pruned rect; drop rects with zero text unless media card shaped
    final_boxes = []
    for rb in pruned_rects:
        inside = sum(1 for tb in merged_texts if _center_in(tb, rb, margin=2.0))
        if inside == 0 and (rb[2] / width > 0.45 or rb[3] / height < 0.06):
            continue
        final_boxes.append((rb, inside, 'rect'))

    # Wrap uncovered short text spans in top nav / control bands as pill or row proposals
    for tb in merged_texts:
        if any(_center_in(tb, fb, margin=4.0) for fb, _, _ in final_boxes):
            continue
        # Skip likely body copy or standalone non-interactive long titles unless in TVSettings list column
        ny = (tb[1] + 0.5 * tb[3]) / height
        if tb[2] / width > 0.42 and 'TVSettings' not in app:
            continue
        if ny > 0.93 and tb[3] / height < 0.025:
            continue
        snapped = _snap_edge_box(gray, tb, width, height)
        if any(pb._iou(snapped, fb) >= 0.45 for fb, _, _ in final_boxes):
            continue
        final_boxes.append((snapped, 1, 'ocr-pill'))

    # Sort top-to-bottom, left-to-right and cap cleanly
    final_boxes.sort(key=lambda item: (round(item[0][1] / 24.0), item[0][0]))
    final_boxes = final_boxes[:max_objects]

    objects = []
    for idx, (box, inside, kind) in enumerate(final_boxes):
        cls = _classify_box(box, width, height, inside, app=app)
        objects.append({
            'id': f'draft-{idx:02d}',
            'class': cls,
            'box': box,
            'visibility': 'unknown',
            'provenance': f'{PROVENANCE}:{kind}',
        })

    boxes_only = [o['box'] for o in objects]
    scores = _focus_outlier_scores(rgb, boxes_only, width, height)
    ranked = sorted(
        [{'index': i, 'id': objects[i]['id'], 'class': objects[i]['class'], 'box': objects[i]['box'], 'score': round(scores[i], 3)}
         for i in range(len(objects))],
        key=lambda item: -item['score'],
    )
    if ranked and ranked[0]['score'] >= 8.6:
        focus = {'state': 'focused', 'box': list(ranked[0]['box'])}
    else:
        focus = {'state': 'unknown', 'box': None}

    return {
        'objects': objects,
        'focus': focus,
        'focusCandidates': ranked[:4],
    }


def evaluate_on_dev(manifest_path=q.ROOT / 'dataset/real_apps/tvbench-v1/dev-manifest-v2.json'):
    """Measure non-model proposal recall on the open 42 dev frames (never sealed)."""
    manifest = q.load(manifest_path)
    probes = run_vision_probe([c['image']['path'] for c in manifest['cases']])
    gt_boxes = 0
    matched_50 = 0
    matched_30 = 0
    proposed_total = 0
    focus_gt = 0
    focus_top1 = 0
    focus_top3 = 0

    for c in manifest['cases']:
        lbl = q.load(c['labels']['path'])
        res = propose_for_frame(c['image']['path'], probes[c['image']['path']], app=c['app'])
        props = [o['box'] for o in res['objects']]
        proposed_total += len(props)
        for o in lbl['objects']:
            if not o.get('class'):
                continue
            gt_boxes += 1
            best = max((pb._iou(o['box'], p) for p in props), default=0.0)
            if best >= 0.5:
                matched_50 += 1
            if best >= 0.3:
                matched_30 += 1
        f = lbl['focus']
        if f['state'] == 'focused' and f.get('box'):
            focus_gt += 1
            cands = res['focusCandidates']
            if cands and pb._iou(f['box'], cands[0]['box']) >= 0.3:
                focus_top1 += 1
            if any(pb._iou(f['box'], cand['box']) >= 0.3 for cand in cands[:3]):
                focus_top3 += 1

    return {
        'frames': len(manifest['cases']),
        'proposedTotal': proposed_total,
        'meanProposedPerFrame': round(proposed_total / max(1, len(manifest['cases'])), 2),
        'gtBoxes': gt_boxes,
        'recallAt50': round(matched_50 / max(1, gt_boxes), 4),
        'recallAt30': round(matched_30 / max(1, gt_boxes), 4),
        'focusGT': focus_gt,
        'focusTop1At30': focus_top1,
        'focusTop3At30': focus_top3,
    }


def populate_review_dir(review_dir, force=False, allow_deprecated_heuristic=False):
    """Deprecated non-SDK heuristic drafter; requires explicit opt-in and must not feed TVBench."""
    q.require(
        allow_deprecated_heuristic,
        'deprecated_vision_geometry_drafts:pass_--allow-deprecated-heuristic_only_for_experiments',
    )
    review_dir = Path(review_dir)
    doc = q.load(review_dir / 'cases.json')
    pending_cases = []
    for c in doc['cases']:
        label_path = review_dir / 'labels' / f"{c['id']}.json"
        if label_path.is_file():
            continue
        draft_path = review_dir / 'drafts' / f"{c['id']}.json"
        if not force and draft_path.is_file():
            existing = q.load(draft_path)
            if existing.get('objects'):
                continue
        pending_cases.append(c)

    probes = run_vision_probe([c['image'] for c in pending_cases])
    hints_dir = review_dir / 'hints'
    hints_dir.mkdir(parents=True, exist_ok=True)
    updated = 0
    total_objs = 0
    focused_drafts = 0

    for c in pending_cases:
        res = propose_for_frame(c['image'], probes[c['image']], app=c.get('app', ''))
        draft = {
            'imageSHA256': c['sha256'],
            'complete': False,
            'objects': res['objects'],
            'focus': res['focus'],
            'review': {'blinded': True, 'reviewer': '', 'status': 'pending'},
        }
        rev554.check(draft, c)
        q.save(review_dir / 'drafts' / f"{c['id']}.json", draft, replace=True)
        q.save(hints_dir / f"{c['id']}.json", {'focusCandidates': res['focusCandidates']}, replace=True)
        updated += 1
        total_objs += len(res['objects'])
        if res['focus']['state'] == 'focused':
            focused_drafts += 1

    return {
        'reviewDir': str(review_dir),
        'totalCases': len(doc['cases']),
        'draftsUpdated': updated,
        'totalProposedObjects': total_objs,
        'meanObjectsPerUpdatedFrame': round(total_objs / max(1, updated), 2),
        'focusedFocusDrafts': focused_drafts,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)
    sub.add_parser('eval-dev')
    p = sub.add_parser('populate')
    p.add_argument('--dir', type=Path, required=True)
    p.add_argument('--force', action='store_true')
    p.add_argument('--allow-deprecated-heuristic', action='store_true')
    args = parser.parse_args()
    if args.cmd == 'eval-dev':
        print(json.dumps(evaluate_on_dev(), indent=2))
    else:
        print(json.dumps(populate_review_dir(args.dir, force=args.force, allow_deprecated_heuristic=args.allow_deprecated_heuristic), indent=2))


if __name__ == '__main__':
    main()
