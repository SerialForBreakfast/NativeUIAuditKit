"""RESET604 T2.3 / T2.4: Convert TTR captures and generator sidecars to 12-role detector memberships.

Reuses `pills560_membership.row`, `roles559`, `detector_training419`, `artparity595_ingest`, and `fixture_recipes604`.
Supports:
- TTR Fixture batch captures (`dataset/tvos_captures/reset604/pilot-d` and full batches)
- TTR Programme captures (`dataset/tvos_captures/artparity595/programme`, respecting `dataRole='test'` holdout)
- TTR native focus corpus (`ttr-native-focus-640-v1-data.tar.gz` + verified `first-304` images from `COMP600/sources`)
- Fixed-label generator frames (`dataset/tvos560/cells6` train/validation)
Optional `--include-focused` emits a `focused` box (RESET604 T4.1 Arm A) alongside the 12 detector roles (D3).
"""
import argparse
import hashlib
import json
import statistics
import subprocess
from collections import Counter
from pathlib import Path
from PIL import Image

import detector_training419 as t
import fixture_recipes604 as fr
import pills560_membership as p560
import research_queue as q
from roles559 import ROLES, role as map_role
from template_inputs398 import pin

NATIVE_FOCUS_TAR = q.ROOT / 'reports/work/ART599/ttr-native-focus-640-v1-data.tar.gz'
DEFAULT_UNPACK = q.ROOT / 'dataset/tvos_captures/ttr-native-focus-640'


def _clip_box(x, y, w, h, width, height):
    """Clip [x, y, w, h] strictly inside [0, width] x [0, height]. Returns None if empty."""
    x1 = max(0.0, float(x))
    y1 = max(0.0, float(y))
    x2 = min(float(width), float(x) + float(w))
    y2 = min(float(height), float(y) + float(h))
    if x2 - x1 < 1.0 or y2 - y1 < 1.0:
        return None
    return [round(x1, 3), round(y1, 3), round(x2 - x1, 3), round(y2 - y1, 3)]


def unpack_native_focus(tar_path=NATIVE_FOCUS_TAR, out_dir=DEFAULT_UNPACK):
    """Unpack ttr-native-focus-640-v1 tarball once and verify SHA256SUMS."""
    tar_path, out_dir = Path(tar_path), Path(out_dir)
    marker = out_dir / 'SHA256SUMS'
    if not marker.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(['tar', '-xzf', str(tar_path), '-C', str(out_dir)], check=True)
    sums = [line.strip().split(None, 1) for line in marker.read_text().splitlines() if line.strip()]
    for expected_sha, rel in sums:
        rel = rel.lstrip('*./')
        target = out_dir / rel
        if rel.startswith('training/'):
            q.require(target.is_file(), f'ttr_unpack_missing:{rel}')
            q.require(q.digest(target) == expected_sha, f'ttr_unpack_sha:{rel}')
    return out_dir


def _select_control_box(el, cls, width, height):
    """Select the §5.2.1 role-specific detector training box clipped to the frame.

    Interactive controls (including whole `cell` = artwork + title) keep `pixel_bounds`.
    Standalone `picture` elements prefer `rendered_body_geometry.visible_pixel_bounds` when present.
    """
    pb = None
    if cls == 'picture':
        rbg = el.get('rendered_body_geometry')
        if isinstance(rbg, dict) and rbg.get('visible_pixel_bounds'):
            pb = rbg['visible_pixel_bounds']
    if pb is None:
        pb = el.get('pixel_bounds')
    if not pb:
        return None
    if isinstance(pb, (list, tuple)) and len(pb) == 4:
        return _clip_box(pb[0], pb[1], pb[2], pb[3], width, height)
    return _clip_box(pb['x'], pb['y'], pb['width'], pb['height'], width, height)


def _fixture_controls(elements, width, height, focus_id=None, include_focused=False, is_focus_frame=False, has_paired_focus=False):
    """Extract 12-role controls, explicit focus state, and optional single focused box from Fixture scene."""
    out = []
    focused_boxes = []
    focused_raw_count = 0
    any_focused = False
    for idx, el in enumerate(elements):
        if el.get('is_hidden') or el.get('is_occluded') or el.get('visibility') == 'occluded':
            continue
        eid = el.get('element_id') or f'el_{idx}'
        el_foc = bool(el.get('is_focused') or (is_focus_frame and focus_id and eid == focus_id))
        if el_foc:
            focused_raw_count += 1
            any_focused = True
        cls = map_role(el.get('taxonomy_class', ''), eid)
        box = _select_control_box(el, cls, width, height) if cls else None
        if not cls or not box:
            continue
        out.append(dict(id=f'e{idx:03}_{eid}'[:48], bounds=box, **{'class': cls}))
        if el_foc:
            focused_boxes.append((idx, eid, box))

    if is_focus_frame:
        if focused_raw_count == 1 and len(focused_boxes) == 1:
            focus_state = 'focused'
        elif focused_raw_count > 1:
            focus_state = 'ambiguous'
        else:
            focus_state = 'unknown'
    else:
        if any_focused:
            focus_state = 'ambiguous'
        elif elements and has_paired_focus and all(not el.get('is_focused') for el in elements):
            focus_state = 'no_focus'
        else:
            focus_state = 'unknown'

    if include_focused and focus_state == 'focused':
        idx, eid, box = focused_boxes[0]
        out.append(dict(id=f'f{idx:03}_{eid}'[:48], bounds=box, **{'class': 'focused'}))
    return out, focus_state


def ingest_fixture_batch(batch_dir, prefix='ttr604', include_focused=False, qualified=None):
    """Convert a local TTR `fixture batch` directory preserving completeness and focus truth.

    `qualified` maps entry id -> set of passed frame kinds ('foc', 'unf') from an offline
    composition reconciliation audit. When given, frames without a pass are marked
    `reconciliationFailed` and every supervision mode excludes them.
    """
    batch_dir = Path(batch_dir)
    manifest = q.load(batch_dir / 'manifest.json')
    rows, held_out = [], []
    for entry in manifest:
        meta_rel = entry.get('metadata', {}).get('metadataPath')
        if not meta_rel or not (batch_dir / meta_rel).is_file():
            continue
        meta = q.load(batch_dir / meta_rel)
        if not meta.get('is_settled', False):
            continue
        recipe = meta.get('recipe') or {}
        fam = fr.family(recipe) if 'archetype' in recipe else 'plain:' + entry.get('category', 'unknown')
        # Joe, 2026-11-12 ("Keep current rule"): only NUIAK family hold-out sets roles. `test` is written by
        # fixture_batch_runner604 for HELD_OUT families. TTR advisory splits (`calibration`/`held-out`,
        # consumerSplitRequired) never set roles; calibration stays generator-only.
        is_held = fam in fr.HELD_OUT or entry.get('split') == 'test'
        role = 'held-out' if is_held else 'train'
        group = f"{prefix}-{fam.replace(':', '_')}-{recipe.get('seed', entry['id'])}"
        w, h = int(meta['scene_width']), int(meta['scene_height'])
        sid = entry['id'].replace('/', '-')
        semantic_avail = meta.get('semantic_inventory_availability')
        has_paired_focus = bool(meta.get('focused_png'))

        for kind, img_key, sha_key, scene_key, is_focus_frame in (
            ('foc', 'focused_png', 'focused_sha256', 'focused_scene', True),
            ('unf', 'unfocused_png', 'baseline_scene_png', 'baseline_scene', False),
        ):
            img_name = meta.get(img_key) or (meta.get('unfocused_png') if kind == 'unf' else None)
            if not img_name:
                continue
            img_path = batch_dir / img_name
            if not img_path.is_file():
                continue
            expected_sha = meta.get('focused_sha256' if is_focus_frame else 'unfocused_sha256')
            if expected_sha:
                q.require(q.digest(img_path) == expected_sha, f'fixture_sha:{img_path.name}')
            scene = meta.get(scene_key) or {}
            elements = scene.get('elements') or (meta.get('elements') if is_focus_frame else [])
            si = scene.get('semantic_inventory') or {}
            scene_cov = si.get('coverage')
            scene_exclusions = si.get('exclusions') or {}
            labels_complete = (
                semantic_avail == 'complete_declared_composition'
                and scene_cov == 'complete_declared_composition'
                and not scene_exclusions
            )
            controls, focus_state = _fixture_controls(
                elements, w, h,
                focus_id=meta.get('focused_element_id') if is_focus_frame else None,
                include_focused=include_focused,
                is_focus_frame=is_focus_frame,
                has_paired_focus=has_paired_focus,
            )
            if not controls:
                continue
            row_id = f'{prefix}-{sid}-{kind}'[:60]
            item = dict(
                id=row_id, group=group, role=role, sourceRole='fixture-batch', family=fam,
                trainingEligible=(role == 'train'),
                labelsComplete=labels_complete,
                focusState=focus_state,
                width=w, height=h, image=pin(img_path), controls=controls,
            )
            if qualified is not None and kind not in qualified.get(entry['id'], ()):
                item['reconciliationFailed'] = True
            if not labels_complete:
                item['partialSceneWarning'] = f"availability={semantic_avail or 'unknown'};coverage={scene_cov or 'unknown'}"
            (held_out if is_held else rows).append(item)
    return rows, held_out


FRAME_SCHEMA = 'tvos-framework-frame-v1'


FOCUS_TRAINING_STATE = {'focused': 'focused', 'known_no_focus': 'no_focus'}  # transition, unavailable, unknown -> unknown


def normalize_framework_frame(side):
    """Return the internal flat frame for `framework_projection604.project_frame`, plus frame-level reasons.

    Accepts the canonical TTR layout (`frame` block, `focus.object_id`, objects wrapped as
    `{"object": ..., "content_id", "reuse_generation"}`) and the earlier NUIAK flat layout.
    """
    reasons = []
    fr_ = side.get('frame')
    if isinstance(fr_, dict):
        rev, shot = fr_.get('scene_revision'), fr_.get('screenshot_sha256')
        width, height = fr_.get('png_width'), fr_.get('png_height')
    else:
        rev, shot, width, height = side.get('scene_revision'), side.get('screenshot_sha256'), side.get('width'), side.get('height')
    objects = []
    for item in side.get('objects') or []:
        obj = dict(item['object']) if isinstance(item.get('object'), dict) else dict(item)
        for k in ('content_id', 'reuse_generation'):
            if k in item and k not in obj:
                obj[k] = item[k]
        objects.append(obj)
    focus = dict(side.get('focus') or {'state': 'unknown'})
    if 'object_id' in focus and 'id' not in focus:
        focus['id'] = focus['object_id']
    if focus.get('state') not in ('focused', 'known_no_focus'):
        focus['state'] = 'unknown'
    elif ('scene_revision' in focus and focus['scene_revision'] != rev) or ('screenshot_sha256' in focus and focus['screenshot_sha256'] != shot):
        reasons.append('focus_identity_mismatch')
        focus['state'] = 'unknown'
    if side.get('status', 'settled') != 'settled':
        reasons.append(f"frame_not_settled:{side.get('status')}")
    reasons += [f'withheld:{r}' for r in side.get('withheld_reasons') or []]
    return dict(scene_revision=rev, screenshot_sha256=shot, width=width, height=height, focus=focus, objects=objects,
                frame_id=side.get('frame_id'), family=side.get('family', 'unknown')), reasons


def ingest_framework_frame(sidecar_path, image_path, group, role='train', contract=None, row_id=None):
    """Convert 1 `tvos-framework-frame-v1` sidecar under `tvos-framework-projection-v1`.

    Returns (row or None, projection). A row exists only when the frame is eligible: the table hash and
    mapping version match ours (when the sidecar names them), the frame is settled and not withheld, the
    screenshot hash matches, and no object is unresolved. Classes come from `framework_projection604`,
    never from ids, titles, `taxonomy_class`, or the producer's own projection.
    Focus is a row field, never a tensor class. Unknown focus is never encoded as no focus.
    """
    import framework_projection604 as fp
    side = q.load(sidecar_path)
    q.require(side.get('schema') == FRAME_SCHEMA, 'framework_frame_schema')
    table, digest = (contract, None) if contract else fp.load_contract()
    flat, frame_reasons = normalize_framework_frame(side)
    if side.get('mapping_version') == 'ttr-settings-toggle-v1.1' or table['mapping_version'] == 'ttr-settings-toggle-v1.1':
        pinned, digest = fp.load_contract(fp.CONTRACT_PATH.with_name('ttr-settings-toggle-v1.1.calibration.json'))
        if role != 'diagnostic':
            frame_reasons.append('calibration_only_mapping')
        if contract is not None and contract != pinned:
            frame_reasons.append('calibration_contract_mismatch')
        if side.get('table_sha256') != digest or side.get('mapping_version') != pinned['mapping_version']:
            frame_reasons.append('calibration_contract_identity_mismatch')
        contract = table = pinned
    if side.get('table_sha256') and digest and side['table_sha256'] != digest:
        frame_reasons.append('table_sha256_mismatch')
    if side.get('mapping_version') and side['mapping_version'] != table['mapping_version']:
        frame_reasons.append('mapping_version_mismatch')
    proj = fp.project_frame(flat, contract, diagnostic_covered_children=(role == 'diagnostic'))
    if table['mapping_version'] == 'ttr-settings-toggle-v1.1':
        proj['contract_sha256'] = digest
    image_path = Path(image_path)
    if q.digest(image_path) != flat['screenshot_sha256']:
        frame_reasons.append('frame_identity_mismatch:screenshot')
    if frame_reasons:
        proj = dict(proj, eligible=False, reasons=sorted(proj['reasons'] + frame_reasons))
        if 'focus_identity_mismatch' in frame_reasons:
            proj.update(focus_state='unknown', focus_id=None)
    if not proj['eligible']:
        return None, proj
    w, h = int(flat['width']), int(flat['height'])
    controls = [dict(id=f"t{i:03}", objectId=t['id'], bounds=t['box'], ruleId=t['rule_id'], attributes=t['attributes'], **{'class': t['class']})
                for i, t in enumerate(proj['targets'])]
    row = dict(
        id=str(row_id or flat['frame_id'])[:60], group=group, role=role, sourceRole='framework-frame', family=flat['family'],
        trainingEligible=(role == 'train'), labelsComplete=True,
        focusState=FOCUS_TRAINING_STATE.get(proj['focus_state'], 'unknown'),
        focusObjectId=proj['focus_id'], width=w, height=h, image=pin(image_path), controls=controls,
        mappingVersion=proj['mapping_version'], contractSha256=proj['contract_sha256'],
    )
    return row, proj


def ingest_programme(programme_dir, include_focused=False):
    """Convert `dataset/tvos_captures/artparity595/programme` frames into rows and test holdout."""
    programme_dir = Path(programme_dir)
    rows, held_out = [], []
    for pos_file in sorted(programme_dir.glob('*/position-*.json')):
        d = q.load(pos_file)
        img_path = pos_file.with_suffix('.png')
        if not img_path.is_file():
            continue
        q.require(q.digest(img_path) == d['imageSHA256'], f'programme_sha:{img_path}')
        with Image.open(img_path) as im:
            w, h = im.size
        controls = []
        focused_boxes = []
        raw_focus_count = 0
        for idx, el in enumerate(d['elements']):
            if el.get('focused'):
                raw_focus_count += 1
            cls = map_role(el.get('role', ''), el.get('id', ''))
            bp = el.get('boundsPixels')
            box = _clip_box(bp['x'], bp['y'], bp['width'], bp['height'], w, h) if bp else None
            if not cls or not box:
                continue
            controls.append(dict(id=f'p{idx}_{el["id"]}'[:48], bounds=box, **{'class': cls}))
            if el.get('focused'):
                focused_boxes.append((idx, el['id'], box))
        if raw_focus_count == 1 and len(focused_boxes) == 1:
            focus_state = 'focused'
        elif raw_focus_count > 1:
            focus_state = 'ambiguous'
        else:
            focus_state = 'unknown'
        if include_focused and focus_state == 'focused':
            idx, eid, box = focused_boxes[0]
            controls.append(dict(id=f'pf{idx}_{eid}'[:48], bounds=box, **{'class': 'focused'}))
        if not controls:
            continue
        data_role = d.get('dataRole', 'test')
        is_test = data_role != 'train'
        item = dict(
            id=f"prog-{d['screen']}-p{d['position']}"[:60],
            group=d['group'], role='held-out' if is_test else 'train', sourceRole='artparity595-programme',
            trainingEligible=(not is_test), labelsComplete=True, focusState=focus_state,
            width=w, height=h, image=pin(img_path), controls=controls,
        )
        (held_out if is_test else rows).append(item)
    return rows, held_out


def ingest_native_focus(unpacked_dir, extra_sources_dir=None, include_focused=False):
    """Convert verified TTR native-focus training frames + 3 competitors per frame (partial screen labels)."""
    unpacked_dir = Path(unpacked_dir)
    labels_by_sha = {r['sha256']: r for r in q.load(unpacked_dir / 'training/labels.json')}
    comp_map = {}
    for fname in ('first-304.json', 'next-536.json'):
        p = unpacked_dir / 'training/competitor-index' / fname
        if p.is_file():
            for entry in q.load(p):
                comp_map[entry['sha256']] = entry

    available = {p.stem: p for p in (unpacked_dir / 'training/images').glob('*.png')}
    if extra_sources_dir and Path(extra_sources_dir).is_dir():
        for p in Path(extra_sources_dir).glob('*.png'):
            available.setdefault(p.stem, p)

    rows = []
    for sha, img_path in sorted(available.items()):
        comp = comp_map.get(sha)
        if not comp:
            continue
        q.require(q.digest(img_path) == sha, f'native_focus_sha:{sha}')
        meta = labels_by_sha.get(sha, {})
        scene = comp.get('scene') or meta.get('scene') or sha[:12]
        # Reserved held-out family check (sports scenes must never enter training)
        if 'sports' in scene.lower() or meta.get('family') == 'category-sports' or meta.get('split') != 'training' and meta:
            continue
        with Image.open(img_path) as im:
            w, h = im.size
        # In competitor-index, settings-native_button is button; media/settings rows are cell
        cue = meta.get('cue', '')
        foc_cls = 'button' if cue == 'native_button' else 'cell'
        controls = []
        focus_state = 'unknown'
        if meta.get('bounds'):
            bx = _clip_box(*meta['bounds'], w, h)
            if bx:
                controls.append(dict(id='foc_' + comp['focused'], bounds=bx, **{'class': foc_cls}))
                focus_state = 'focused'
                if include_focused:
                    controls.append(dict(id='focbox_' + comp['focused'], bounds=bx, **{'class': 'focused'}))
        for idx, alt in enumerate(comp.get('observed_unfocused', [])):
            bx = _clip_box(*alt['bounds'], w, h)
            if bx:
                controls.append(dict(id=f'alt{idx}_{alt["control"]}', bounds=bx, **{'class': foc_cls}))
        if not controls:
            continue
        rows.append(dict(
            id=f'ttrnf-{sha[:16]}', group=f'ttrnf-{scene}'[:60], role='train',
            sourceRole='ttr-native-focus-v1', trainingEligible=True,
            labelsComplete=False, focusState=focus_state,
            partialSceneWarning='4-target sweep labels only',
            width=w, height=h, image=pin(img_path), controls=controls,
        ))
    return rows


def ingest_generator(dataset_dir, include_focused=False, max_rows=None):
    """Convert tvos560 generator dataset (train + validation -> calibration) with strict single-focus truth."""
    dataset_dir = Path(dataset_dir)
    rows = []
    for split, role in (('train', 'train'), ('validation', 'calibration')):
        images = sorted((dataset_dir / split).glob('*.png'))
        if max_rows is not None:
            images = images[:max_rows]
        for img_path in images:
            sidecar = img_path.with_suffix('.json')
            d = q.load(sidecar)
            base_row = p560.row(img_path, role, split, button_text=False)
            # Filter any leftover 'text' controls to guarantee strictly 12 D3 roles
            controls = [c for c in base_row['controls'] if c['class'] in ROLES]
            w, h = base_row['width'], base_row['height']
            raw_focused_els = [
                (idx, el) for idx, el in enumerate(d.get('elements', []))
                if (el.get('id') or '').endswith('_focused') or (el.get('state') or {}).get('isFocused') is True
            ]
            if len(raw_focused_els) == 1:
                idx, el = raw_focused_els[0]
                eid = el.get('id', '')
                bp = el.get('boundsPixels')
                box = _clip_box(bp['x'], bp['y'], bp['width'], bp['height'], w, h) if bp else None
                if map_role(el.get('elementType', ''), eid) in ROLES and box:
                    focus_state = 'focused'
                    if include_focused:
                        controls.append(dict(id=f'foc_{idx}', bounds=box, **{'class': 'focused'}))
                else:
                    focus_state = 'unknown'
            elif len(raw_focused_els) > 1:
                focus_state = 'ambiguous'
            else:
                focus_state = 'unknown'
            if not controls:
                continue
            base_row['controls'] = controls
            base_row['id'] = f"gen604-{split[:3]}-{img_path.stem}"[:60]
            base_row['labelsComplete'] = True
            base_row['focusState'] = focus_state
            rows.append(base_row)
    return rows


def audit_membership(doc, held_out=None, tvbench_paths=(), excluded=None):
    """Audit row counts, classes, box geometry, focus states, exclusions, and zero TVBench overlap."""
    forbidden_shas = set()
    for path in tvbench_paths:
        p = Path(path)
        if p.is_file():
            m = q.load(p)
            for c in m.get('cases', []):
                if c.get('image', {}).get('sha256'):
                    forbidden_shas.add(c['image']['sha256'])

    seen_shas = set()
    train_groups, cal_groups = set(), set()
    by_source = Counter()
    by_role = Counter()
    by_class = Counter()
    by_focus_state = Counter()
    widths, heights = [], []
    overlap_violations = []

    for r in doc['rows']:
        sha = r['image']['sha256']
        if sha in forbidden_shas:
            overlap_violations.append(r['id'])
        seen_shas.add(sha)
        by_source[r.get('sourceRole', 'unknown')] += 1
        by_role[r['role']] += 1
        by_focus_state[r.get('focusState', 'unknown')] += 1
        (train_groups if r['role'] == 'train' else cal_groups).add(r['group'])
        for c in r['controls']:
            by_class[c['class']] += 1
            widths.append(c['bounds'][2])
            heights.append(c['bounds'][3])

    q.require(not overlap_violations, f'ttr_ingest_tvbench_overlap:{overlap_violations[:5]}')
    q.require(not (train_groups & cal_groups), f'ttr_ingest_group_leak:{sorted(train_groups & cal_groups)[:5]}')

    excluded_by_source = Counter()
    excluded_by_reason = Counter()
    for ex in (excluded or []):
        excluded_by_source[ex.get('sourceRole', 'unknown')] += 1
        excluded_by_reason[ex.get('reason', 'unknown')] += 1

    return dict(
        version='ttr-ingest-audit-v2',
        totalRows=len(doc['rows']),
        heldOutRows=len(held_out or []),
        uniqueImages=len(seen_shas),
        tvbenchOverlapCount=len(overlap_violations),
        trainCalibrationGroupOverlap=len(train_groups & cal_groups),
        bySource=dict(by_source),
        byRole=dict(by_role),
        byFocusState=dict(by_focus_state),
        byClass=dict(by_class),
        focusBoxCount=by_class.get('focused', 0),
        excludedCount=len(excluded or []),
        excludedBySource=dict(excluded_by_source),
        excludedReasons=dict(excluded_by_reason),
        boxWidth=dict(min=min(widths) if widths else 0, median=round(statistics.median(widths), 2) if widths else 0, max=max(widths) if widths else 0),
        boxHeight=dict(min=min(heights) if heights else 0, median=round(statistics.median(heights), 2) if heights else 0, max=max(heights) if heights else 0),
    )


def _filter_rows_for_mode(rows, mode):
    """Filter candidate rows according to target supervision mode ('d1', 'f1-arma', 'focus-supervision')."""
    kept, excluded = [], []
    for row in rows:
        reason = None
        if row.get('reconciliationFailed'):
            reason = 'composition_reconciliation_failed'
        elif mode == 'd1':
            if not row.get('labelsComplete'):
                reason = 'incomplete_labels'
        elif mode == 'f1-arma':
            if not row.get('labelsComplete'):
                reason = 'incomplete_labels'
            elif row.get('focusState') not in ('focused', 'no_focus'):
                reason = f"focus_state:{row.get('focusState', 'unknown')}"
        elif mode == 'focus-supervision':
            if row.get('focusState') not in ('focused', 'no_focus'):
                reason = f"focus_state:{row.get('focusState', 'unknown')}"
        if reason:
            excluded.append(dict(id=row['id'], sourceRole=row.get('sourceRole', 'unknown'), reason=reason))
        else:
            kept.append(row)
    return kept, excluded


def _collect_all_rows(include_focused=False, include_partial_sweep=True, max_gen=None, extra_fixture_roots=()):
    all_rows, all_held = [], []
    all_rows.extend(ingest_generator(q.ROOT / 'dataset/tvos560/cells6', include_focused=include_focused, max_rows=max_gen))

    pilot_d = q.ROOT / 'dataset/tvos_captures/reset604/pilot-d'
    if pilot_d.is_dir():
        r, h = ingest_fixture_batch(pilot_d, prefix='pilotd', include_focused=include_focused)
        all_rows.extend(r)
        all_held.extend(h)

    batch_v1 = q.ROOT / 'dataset/tvos_captures/reset604/batch-v1'
    if batch_v1.is_dir():
        for chunk in sorted(batch_v1.iterdir()):
            if chunk.is_dir() and (chunk / 'manifest.json').is_file():
                r, h = ingest_fixture_batch(chunk, prefix=f'b1_{chunk.name}', include_focused=include_focused)
                all_rows.extend(r)
                all_held.extend(h)

    for root, prefix, qualified_path in extra_fixture_roots:
        root = Path(root)
        qual_doc = q.load(qualified_path) if qualified_path else None
        for chunk in sorted(root.iterdir()):
            if chunk.is_dir() and (chunk / 'manifest.json').is_file():
                qualified = None
                if qual_doc is not None:
                    passed = qual_doc['chunks'].get(chunk.name, {})
                    qualified = {k: set(v) for k, v in passed.items()}
                r, h = ingest_fixture_batch(chunk, prefix=f'{prefix}_{chunk.name}', include_focused=include_focused, qualified=qualified)
                all_rows.extend(r)
                all_held.extend(h)

    prog = q.ROOT / 'dataset/tvos_captures/artparity595/programme'
    if prog.is_dir():
        r, h = ingest_programme(prog, include_focused=include_focused)
        all_rows.extend(r)
        all_held.extend(h)

    if include_partial_sweep and NATIVE_FOCUS_TAR.is_file():
        unpack_dir = unpack_native_focus()
        all_rows.extend(ingest_native_focus(
            unpack_dir, extra_sources_dir=q.ROOT / 'reports/work/COMP600/sources', include_focused=include_focused,
        ))
    return all_rows, all_held


def _write_membership_bundle(out_dir, rows, held_out, excluded, names, mode, fname='membership.json', audit_fname='audit.json', immutable=False, membership_version=None):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    membership_path = out_dir / fname
    if immutable and membership_path.exists():
        raise ValueError(f'ttr_ingest_immutable_target_exists:{membership_path}')
    doc = dict(
        version=t.VERSION,
        membershipVersion=membership_version or ('v2' if immutable else 'v1'),
        mode=mode,
        trainingAdmitted=(mode in ('d1', 'f1-arma')),
        names=names,
        rows=rows,
        calibrationGroups=sorted({r['group'] for r in rows if r['role'] == 'calibration'}),
        targetScope=f"RESET604 D3 12-role tvOS ({mode})",
        limitation='Mixed 1920x1080 and 3840x2160 images; partial scenes excluded from D1/ArmA detector supervision.',
    )
    tvbench_manifests = [
        q.ROOT / 'reports/work/REALAPP554/pilot-v2/manifest.json',
        q.ROOT / 'dataset/real_apps/tvbench-v1/dev-manifest.json',
        q.ROOT / 'dataset/real_apps/tvbench-v1/dev-manifest-v2.json',
    ]
    audit = audit_membership(doc, held_out=held_out, tvbench_paths=tvbench_manifests, excluded=excluded)
    q.save(membership_path, doc, replace=not immutable)
    q.save(out_dir / 'held-out.json', dict(version='ttr-held-out-v2', rows=held_out), replace=not immutable)
    q.save(out_dir / audit_fname, audit, replace=not immutable)
    return dict(membership=str(membership_path), audit=audit)


def build(out_dir, include_focused=False, include_partial_sweep=True, max_gen=None, mode=None, immutable=False, extra_fixture_roots=(), membership_version=None):
    """Build filtered 12-role (or 12-role + focused) membership from generator + TTR captures."""
    mode = mode or ('f1-arma' if include_focused else 'd1')
    include_focused = include_focused or (mode in ('f1-arma', 'focus-supervision'))
    names = list(ROLES) + (['focused'] if include_focused else [])
    all_rows, all_held = _collect_all_rows(
        include_focused=include_focused,
        include_partial_sweep=include_partial_sweep,
        max_gen=max_gen,
        extra_fixture_roots=extra_fixture_roots,
    )

    # Deduplicate by image SHA-256 and enforce group consistency
    deduped = []
    seen_sha = set()
    group_role = {}
    for row in all_rows:
        sha = row['image']['sha256']
        if sha in seen_sha:
            continue
        grp = row['group']
        if grp in group_role and group_role[grp] != row['role']:
            row['role'] = group_role[grp]
            row['trainingEligible'] = (row['role'] == 'train')
        else:
            group_role[grp] = row['role']
        seen_sha.add(sha)
        deduped.append(row)

    filtered, excluded = _filter_rows_for_mode(deduped, mode)
    filtered_held, _ = _filter_rows_for_mode(all_held, mode if mode != 'focus-supervision' else 'focus-supervision')
    fname = 'membership.json' if immutable else ('membership-f1-arma.json' if include_focused else 'membership-d1.json')
    audit_fname = 'audit.json' if immutable else f'audit-{"f1" if include_focused else "d1"}.json'
    return _write_membership_bundle(
        out_dir, filtered, filtered_held, excluded, names, mode,
        fname=fname, audit_fname=audit_fname, immutable=immutable, membership_version=membership_version,
    )


def build_v2(base_dir=q.ROOT / 'reports/work/RESET604/membership', max_gen=None):
    """Build all three immutable v2 successor memberships cleanly without altering v1 artifacts."""
    base_dir = Path(base_dir)
    results = {}
    for sub, mode, incl_foc, incl_sweep in (
        ('v2-d1', 'd1', False, False),
        ('v2-f1-arma', 'f1-arma', True, False),
        ('v2-focus-supervision', 'focus-supervision', True, True),
    ):
        results[sub] = build(
            base_dir / sub,
            include_focused=incl_foc,
            include_partial_sweep=incl_sweep,
            max_gen=max_gen,
            mode=mode,
            immutable=True,
        )
    return results


COMPOSITION_BATCHES = (
    (q.ROOT / 'dataset/tvos_captures/reset604/comp-v1', 'c1', q.ROOT / 'reports/work/RESET604/comp-capture-v1-qual/qualified-frames.json'),
    (q.ROOT / 'dataset/tvos_captures/reset604/comp-v2', 'c2', q.ROOT / 'reports/work/RESET604/comp-capture-v2-qual/qualified-frames.json'),
)


def build_v3(base_dir=q.ROOT / 'reports/work/RESET604/membership', max_gen=None, composition_batches=COMPOSITION_BATCHES):
    """Build immutable v3 successors: v2 sources plus reconciled `appearance.composition` v5 captures."""
    base_dir = Path(base_dir)
    for root, _, qualified in composition_batches:
        q.require(Path(root).is_dir() and Path(qualified).is_file(), f'ttr_ingest_v3_missing_composition_audit:{root}')
    extra = tuple(composition_batches)
    results = {}
    for sub, mode, incl_foc, incl_sweep in (
        ('v3-d1', 'd1', False, False),
        ('v3-f1-arma', 'f1-arma', True, False),
        ('v3-focus-supervision', 'focus-supervision', True, True),
    ):
        results[sub] = build(
            base_dir / sub, include_focused=incl_foc, include_partial_sweep=incl_sweep, max_gen=max_gen,
            mode=mode, immutable=True, extra_fixture_roots=extra, membership_version='v3',
        )
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, default=q.ROOT / 'reports/work/RESET604/membership')
    parser.add_argument('--include-focused', action='store_true', help='Include `focused` class box (T4.1 Arm A)')
    parser.add_argument('--no-partial-sweep', action='store_true', help='Exclude 4-control partial native-focus frames')
    parser.add_argument('--max-gen', type=int, default=None, help='Cap generator rows per split for fast tests')
    parser.add_argument('--mode', choices=('d1', 'f1-arma', 'focus-supervision'), default=None)
    parser.add_argument('--v2-all', action='store_true', help='Build immutable v2-d1, v2-f1-arma, and v2-focus-supervision under --out')
    parser.add_argument('--v3-all', action='store_true', help='Build immutable v3 successors (v2 sources + reconciled composition captures)')
    args = parser.parse_args()
    if args.v3_all:
        res = build_v3(args.out, max_gen=args.max_gen)
    elif args.v2_all:
        res = build_v2(args.out, max_gen=args.max_gen)
    else:
        res = build(args.out, include_focused=args.include_focused, include_partial_sweep=not args.no_partial_sweep, max_gen=args.max_gen, mode=args.mode)
    print(json.dumps(res, indent=2))


if __name__ == '__main__':
    main()
