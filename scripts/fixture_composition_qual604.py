"""RESET604 Component 1: Pre-capture expectation & reconciliation qualifier for Fixture `appearance.composition` v5 recipes.

Before generating thousands of training frames, validates starter ScreenLibrary scenes
(shelf, text-heavy storefront detail, modal, and edge/offscreen variants) against pre-capture
control expectations, rendered PNG edge/diff pixel reconciliation, static-text exclusion,
and native UIFocusSystem focus truth.
"""
import os
import argparse
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

import fixture_batch_runner604 as fbr
import perception_benchmark as pb
import research_queue as q
from roles559 import role as map_role

DEFAULT_TTR_EXAMPLES = Path(os.environ.get('NUIAK_TTR_ROOT', Path.home() / 'Developer/TVTestRig')) / 'Examples'
STARTER_RECIPES = {
    'shelf': 'ScreenLibrary/recipes/queue-up-next-rail.json',
    'detail_text': 'ScreenLibrary/recipes/info-storefront-panel.json',
    'modal': 'ScreenLibrary/recipes/dialogs-centered-modal.json',
    'side_modal': 'ScreenLibrary/recipes/dialogs-side-action-sheet.json',
    'edge_text_shelf': 'FixtureCompositions/atlas-native-v1/packet/atlas-shelf-edge.json',
}
SECOND_LAYOUT_RECIPES = {
    'hero_full_rail': 'ScreenLibrary/recipes/hero-full-rail.json',
    'dashboard_info': 'ScreenLibrary/recipes/info-news-sports-dashboard.json',
}

# ScreenLibrary & Fixture composition maps `tab` -> `menuButton` (`button` role in roles559)
# and `text`/`label` -> `label` (dropped by D3 `map_role` -> None).
KIND_TO_ROLE = {
    'button': 'button',
    'tab': 'button',
    'composite_card': 'cell',
    'thumbnail': 'cell',
    'poster': 'cell',
    'ranked_row': 'cell',
    'hero': 'cell',
    'artwork': 'picture',
    'text': None,
    'label': None,
}


def expected_from_composition(recipe, scene_width=3840, scene_height=2160):
    """Derive expected visible controls, offscreen IDs, static text IDs, and target focus BEFORE capture.

    Matches `ProceduralSceneView` tvOS overscan-safe composition projection (`scale = (scene_height / 1080) * (8/9)`,
    `origin = (80 * scale_pts, 60 * scale_pts)`).
    """
    comp = (recipe.get('appearance') or {}).get('composition') or {}
    q.require(comp, 'composition_missing')
    defs = comp.get('definitions') or {}
    pts_scale = scene_height / 1080.0
    comp_scale = pts_scale * (8.0 / 9.0)
    ox = 80.0 * pts_scale
    oy = 60.0 * pts_scale

    visible_controls = {}
    offscreen_controls = []
    static_text_ids = []

    for region in comp.get('regions', []):
        rx, ry, rw, rh = [float(v) for v in region['frame']]
        insets = region.get('content_insets') or [0, 0, 0, 0]
        top, left, bottom, right = [float(v) for v in insets]
        gap = float(region.get('gap', 0.0))
        axis = region.get('axis', 'row')
        columns = max(1, int(region.get('columns') or 1))
        cur_x = rx + left
        cur_y = ry + top
        row_max_h = 0.0

        for idx, item in enumerate(region.get('items', [])):
            eid = item['id']
            d = defs[item['component']]
            kind = d['kind']
            iw, ih = float(d['width']), float(d['height'])
            px_box = [
                round(ox + cur_x * comp_scale, 2),
                round(oy + cur_y * comp_scale, 2),
                round(iw * comp_scale, 2),
                round(ih * comp_scale, 2),
            ]
            if axis == 'grid':
                row_max_h = max(row_max_h, ih)
                if (idx + 1) % columns == 0:
                    cur_x = rx + left
                    cur_y += row_max_h + gap
                    row_max_h = 0.0
                else:
                    cur_x += iw + gap
            elif axis in ('row', 'shelf', 'horizontal'):
                cur_x += iw + gap
            else:
                cur_y += ih + gap

            expected_role = KIND_TO_ROLE.get(kind, map_role(kind, eid))
            if expected_role is None:
                static_text_ids.append(eid)
                continue

            # Offscreen when fully outside the rendered screen frame [0, W] x [0, H]
            # (or outside non-scrolling fixed region bounds when explicit overflow occurs beyond viewport).
            ix1 = max(0.0, px_box[0])
            iy1 = max(0.0, px_box[1])
            ix2 = min(float(scene_width), px_box[0] + px_box[2])
            iy2 = min(float(scene_height), px_box[1] + px_box[3])
            if ix2 - ix1 < 2.0 or iy2 - iy1 < 2.0:
                offscreen_controls.append(eid)
            else:
                clipped_box = [round(ix1, 2), round(iy1, 2), round(ix2 - ix1, 2), round(iy2 - iy1, 2)]
                visible_controls[eid] = dict(id=eid, kind=kind, role=expected_role, box=clipped_box)

    targets = (recipe.get('capture_selection') or {}).get('target_element_ids') or []
    return dict(
        visibleControls=visible_controls,
        offscreenControls=offscreen_controls,
        staticTextIDs=static_text_ids,
        targetFocusID=targets[0] if targets else None,
        allTargetFocusIDs=list(targets),
    )


def _edge_error(a, b):
    ax2, ay2 = a[0] + a[2], a[1] + a[3]
    bx2, by2 = b[0] + b[2], b[1] + b[3]
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(ax2 - bx2), abs(ay2 - by2))


def _crop_stats(rgb_arr, box):
    h, w = rgb_arr.shape[:2]
    x0 = max(0, min(w - 1, int(round(box[0]))))
    y0 = max(0, min(h - 1, int(round(box[1]))))
    x1 = max(x0 + 1, min(w, int(round(box[0] + box[2]))))
    y1 = max(y0 + 1, min(h, int(round(box[1] + box[3]))))
    return rgb_arr[y0:y1, x0:x1]


def _box_has_rendered_pixels(rgb_arr, box, min_std=0.5):
    if rgb_arr is None:
        return True
    return float(_crop_stats(rgb_arr, box).std()) >= min_std


def _focus_pixel_delta(rgb_base, rgb_foc, box, pad=18):
    """Verify the reported focused region (including halo/border) visibly changed vs baseline."""
    if rgb_base is None or rgb_foc is None:
        return None
    h, w = rgb_base.shape[:2]
    expanded = [max(0, box[0] - pad), max(0, box[1] - pad), box[2] + 2 * pad, box[3] + 2 * pad]
    c0 = _crop_stats(rgb_base, expanded)
    c1 = _crop_stats(rgb_foc, expanded)
    if c0.shape != c1.shape or not c0.size:
        return None
    return float(np.abs(c1 - c0).mean())


def reconcile_frame(
    scene,
    expected,
    expected_focused_id=None,
    allowed_focus_ids=None,
    image_path=None,
    baseline_image_path=None,
    pixel_tolerance_px=8.0,
    min_iou=0.90,
    focus_frame=False,
):
    """Score one baseline or focused Fixture scene against pre-registered control/focus expectations."""
    rgb = np.asarray(Image.open(image_path).convert('RGB'), dtype=np.float32) if image_path and Path(image_path).is_file() else None
    rgb_base = (
        np.asarray(Image.open(baseline_image_path).convert('RGB'), dtype=np.float32)
        if baseline_image_path and Path(baseline_image_path).is_file()
        else None
    )

    all_elements = [
        e
        for e in (scene.get('elements') or [])
        if not e.get('is_hidden') and not e.get('is_occluded') and e.get('visibility') != 'occluded'
    ]
    interactive_by_id = {}
    static_leaks = []
    for e in all_elements:
        eid = e.get('element_id')
        if not eid:
            continue
        r = map_role(e.get('taxonomy_class', ''), eid)
        if r is None:
            # Static text (`label`) correctly excluded from 12-role detector controls
            if eid in expected['visibleControls']:
                static_leaks.append({'id': eid, 'reason': 'expected_control_typed_as_label'})
            continue
        interactive_by_id[eid] = (r, e)

    exp_vis = expected['visibleControls']
    offscreen = set(expected['offscreenControls'])
    static_ids = set(expected['staticTextIDs'])

    exact_matches = 0
    missing_controls = []
    extra_controls = list(static_leaks)
    wrong_roles = []
    geometry_errors = []
    max_edge_err_px = 0.0
    min_observed_iou = 1.0

    for sid in static_ids:
        if sid in interactive_by_id:
            extra_controls.append({'id': sid, 'reason': 'static_text_emitted_as_control'})

    for oid in offscreen:
        if oid in interactive_by_id:
            extra_controls.append({'id': oid, 'reason': 'offscreen_control_emitted_onscreen'})

    obs_focused_ids = [e['element_id'] for e in all_elements if e.get('is_focused')]
    active_focus_id = expected_focused_id or (obs_focused_ids[0] if len(obs_focused_ids) == 1 else None)

    for eid, exp in exp_vis.items():
        pair = interactive_by_id.get(eid)
        if pair is None:
            missing_controls.append(eid)
            continue
        obs_role, obs = pair
        if obs_role != exp['role']:
            wrong_roles.append({'id': eid, 'expected': exp['role'], 'observed': obs_role})
        pbounds = obs.get('pixel_bounds')
        if not pbounds or len(pbounds) != 4:
            geometry_errors.append({'id': eid, 'reason': 'missing_bounds'})
            continue
        obs_box = [float(v) for v in pbounds]
        tol = pixel_tolerance_px * (2.5 if focus_frame and eid == active_focus_id else 1.0)
        iou = pb._iou(obs_box, exp['box'])
        err = _edge_error(obs_box, exp['box'])
        max_edge_err_px = max(max_edge_err_px, err)
        min_observed_iou = min(min_observed_iou, iou)
        if not _box_has_rendered_pixels(rgb, obs_box):
            geometry_errors.append({'id': eid, 'reason': 'uniform_blank_pixels', 'box': obs_box})
        elif iou < min_iou and err > tol:
            geometry_errors.append({'id': eid, 'expectedBox': exp['box'], 'observedBox': obs_box, 'iou': round(iou, 4), 'edgeErrPx': round(err, 2)})
        else:
            if obs_role == exp['role']:
                exact_matches += 1

    for eid in interactive_by_id:
        if eid not in exp_vis and eid not in offscreen and eid not in static_ids:
            extra_controls.append({'id': eid, 'reason': 'undeclared_extra_control'})

    si = scene.get('semantic_inventory') or {}
    focus_known = si.get('focus_known')
    focus_errors = []
    if focus_known is False:
        focus_errors.append({'reason': 'focus_unknown'})
    if not focus_frame:
        if obs_focused_ids or scene.get('focused_element_id') is not None:
            focus_errors.append({'reason': 'unexpected_focus_on_no_focus_frame', 'observed': obs_focused_ids or [scene.get('focused_element_id')]})
    else:
        if expected_focused_id is not None:
            if obs_focused_ids != [expected_focused_id] or scene.get('focused_element_id') != expected_focused_id:
                focus_errors.append({'reason': 'focused_id_mismatch', 'expected': expected_focused_id, 'observed': obs_focused_ids})
        elif len(obs_focused_ids) != 1 or (allowed_focus_ids is not None and obs_focused_ids[0] not in allowed_focus_ids):
            focus_errors.append({'reason': 'focused_id_invalid_or_missing', 'observed': obs_focused_ids})
        elif rgb_base is not None and rgb is not None:
            foc_pair = interactive_by_id.get(obs_focused_ids[0])
            if foc_pair is not None:
                delta = _focus_pixel_delta(rgb_base, rgb, foc_pair[1]['pixel_bounds'])
                if delta is not None and delta < 0.25:
                    focus_errors.append({'reason': 'focused_box_unchanged_from_baseline', 'id': obs_focused_ids[0], 'meanDelta': round(delta, 4)})

    coverage_ok = si.get('coverage') == 'complete_declared_composition' and not (si.get('exclusions') or {})
    passed = (
        coverage_ok
        and not missing_controls
        and not extra_controls
        and not wrong_roles
        and not geometry_errors
        and not focus_errors
    )

    return dict(
        passed=passed,
        coverage=si.get('coverage'),
        expectedControls=len(exp_vis),
        exactMatches=exact_matches,
        maxEdgeErrPx=round(max_edge_err_px, 2),
        minObservedIoU=round(min_observed_iou, 4) if exp_vis else 1.0,
        missingControls=missing_controls,
        extraControls=extra_controls,
        wrongRoles=wrong_roles,
        geometryErrors=geometry_errors,
        focusErrors=focus_errors,
    )


def qualify_recipes(recipe_paths, out_dir, pixel_tolerance_px=8.0, min_iou=0.90, capture=True, runner=fbr.invoke_aatv_batch, batch_dir=None):
    """Run (or evaluate existing) Starter composition recipes against pre-capture expectations.

    `batch_dir` evaluates an existing captured batch directory in place (offline audit; requires capture=False).
    """
    out_dir = Path(out_dir)
    q.require(batch_dir is None or not capture, 'comp_qual_batch_dir_requires_no_capture')
    out_dir.mkdir(parents=True, exist_ok=True)
    work_recipes = fbr.DEFAULT_PROJECT / '.local-work/reset604/comp-qual-recipes' if capture else (out_dir / 'recipes')
    if work_recipes.exists() and capture:
        shutil.rmtree(work_recipes)
    work_recipes.mkdir(parents=True, exist_ok=True)

    expectations = {}
    for label, src in recipe_paths.items():
        src_path = Path(src)
        doc = json.loads(src_path.read_text())
        expectations[src_path.name] = dict(label=label, recipe=doc)
        if capture or not (work_recipes / src_path.name).exists():
            shutil.copy2(src_path, work_recipes / src_path.name)
        if capture:
            # Keep the exact tested recipe beside the report; fixture_recipes604 loads qualified sources from here.
            (out_dir / 'recipes').mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, out_dir / 'recipes' / src_path.name)

    batch_out = Path(batch_dir) if batch_dir is not None else out_dir / 'batch-raw'
    if capture:
        abs_ttr_out = fbr.DEFAULT_PROJECT / '.local-work/reset604/comp-qual-out'
        if abs_ttr_out.exists():
            shutil.rmtree(abs_ttr_out)
        ok, detail = runner(fbr.DEFAULT_AATV, fbr.DEFAULT_PROJECT, work_recipes, abs_ttr_out, fbr.DEFAULT_URL, fbr.DEFAULT_UDID)
        q.require(ok, f'comp_qual_batch_failed:{detail}')
        if batch_out.exists():
            shutil.rmtree(batch_out)
        shutil.copytree(abs_ttr_out, batch_out)

    manifest = json.loads((batch_out / 'manifest.json').read_text())
    rows = []
    attempted_frames = 0
    qualified_frames = 0
    rejected_frames = 0
    totals = dict(expectedControls=0, exactMatches=0, missingControls=0, extraControls=0, wrongRoles=0, geometryErrors=0, focusErrors=0)

    for entry in manifest:
        meta_rel = (entry.get('metadata') or {}).get('metadataPath')
        rname = (entry.get('metadata') or {}).get('recipeFile') or (Path(meta_rel).parent.name + '.json')
        meta = json.loads((batch_out / meta_rel).read_text())
        exp_entry = expectations.get(rname)
        if not exp_entry:
            continue
        w, h = int(meta['scene_width']), int(meta['scene_height'])
        expected = expected_from_composition(exp_entry['recipe'], scene_width=w, scene_height=h)
        focusable_ids = set(expected['visibleControls'])
        base_img_path = batch_out / meta['unfocused_png'] if meta.get('unfocused_png') else None

        for frame_kind, scene_key, png_key, is_foc in (
            ('baseline_no_focus', 'baseline_scene', 'unfocused_png', False),
            ('focused', 'focused_scene', 'focused_png', True),
        ):
            attempted_frames += 1
            if not meta.get('is_settled', False):
                rejected_frames += 1
                rows.append(dict(id=entry['id'], recipe=rname, frame=frame_kind, passed=False, reason='scene_not_settled'))
                continue
            scene = meta.get(scene_key) or {}
            img_path = batch_out / meta[png_key]
            # Verify swept target_id matches both recipe's focusable set & declared capture target
            rec = reconcile_frame(
                scene,
                expected,
                expected_focused_id=None if not is_foc else None,
                allowed_focus_ids=focusable_ids if is_foc else None,
                image_path=img_path,
                baseline_image_path=base_img_path if is_foc else None,
                pixel_tolerance_px=pixel_tolerance_px,
                min_iou=min_iou,
                focus_frame=is_foc,
            )
            if rec['passed']:
                qualified_frames += 1
            else:
                rejected_frames += 1
            totals['expectedControls'] += rec['expectedControls']
            totals['exactMatches'] += rec['exactMatches']
            totals['missingControls'] += len(rec['missingControls'])
            totals['extraControls'] += len(rec['extraControls'])
            totals['wrongRoles'] += len(rec['wrongRoles'])
            totals['geometryErrors'] += len(rec['geometryErrors'])
            totals['focusErrors'] += len(rec['focusErrors'])
            rows.append(dict(id=entry['id'], label=exp_entry['label'], recipe=rname, frame=frame_kind, **rec))

    report = dict(
        version='fixture-composition-qual-v1',
        attemptedFrames=attempted_frames,
        qualifiedFrames=qualified_frames,
        rejectedOrTransitionalFrames=rejected_frames,
        qualificationRate=round(qualified_frames / max(1, attempted_frames), 4),
        pixelTolerancePx=pixel_tolerance_px,
        minIoU=min_iou,
        totals=totals,
        rows=rows,
    )
    q.save(out_dir / 'composition-qual-report.json', report, replace=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=q.ROOT / 'reports/work/RESET604/comp-qual-v1')
    parser.add_argument('--examples', type=Path, default=DEFAULT_TTR_EXAMPLES)
    parser.add_argument('--suite', choices=('starter', 'second-layout', 'custom'), default='starter')
    parser.add_argument('--recipe', action='append', default=[], help='label=path for --suite custom')
    parser.add_argument('--pixel-tolerance-px', type=float, default=8.0)
    parser.add_argument('--min-iou', type=float, default=0.90)
    parser.add_argument('--no-capture', action='store_true')
    args = parser.parse_args()
    if args.suite == 'starter':
        recipes = {k: args.examples / rel for k, rel in STARTER_RECIPES.items()}
    elif args.suite == 'second-layout':
        recipes = {k: args.examples / rel for k, rel in SECOND_LAYOUT_RECIPES.items()}
    else:
        recipes = {}
        for spec in args.recipe:
            label, path_str = spec.split('=', 1)
            recipes[label] = Path(path_str)
    report = qualify_recipes(recipes, args.out, args.pixel_tolerance_px, args.min_iou, capture=not args.no_capture)
    summary = {k: v for k, v in report.items() if k != 'rows'}
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
