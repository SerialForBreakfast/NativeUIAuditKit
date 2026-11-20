"""RESET604 T2.5: read-only compliance audit of existing tvOS data against `tvos-framework-projection-v1`.

For each source family and construction path, count frames that are:
- `reprojectable`: every visible inventory object resolves under the contract from existing evidence;
- `needs_recapture`: the frame has an unresolved object (for example a custom UIControl card) or no construction evidence;
- `focus_only`: not detector-eligible, but it carries verified native focus truth;
- `excluded`: not settled, or the screenshot hash does not match its metadata.

Fixture evidence: the semantic inventory `native_class` is mapped to its public UIKit superclass, resolved in the
TTR source at the revision in CLASS_MAP_REVISION. Audit assumption A1: a non-focusable inventory child whose
`declared_parent_id` or view-hierarchy path (`<control>/view:<path>`) names a focusable control is owned by it (`same_action`). Legacy metadata has no
construction-to-observation join, so `reprojectable` means "resolves; TTR must still re-export with the join".
No data is changed. Output: reports/work/RESET604/compliance-audit-v1.{json,md}.
"""
import argparse
import collections
import json
from pathlib import Path

import fixture_recipes604 as fr
import framework_projection604 as fp
import research_queue as q

CLASS_MAP_REVISION = 'TVTestRig 25110d7a (Maximum-mini-TTR checkout)'
# Swift class (substring) -> (framework, public primitive). Source lines at CLASS_MAP_REVISION.
CLASS_MAP = (
    ('NativeMazeButton', ('UIKit', 'UIButton')),          # ProceduralSceneView.swift:2316, subclass of NativeProceduralButton
    ('NativeProceduralButton', ('UIKit', 'UIButton')),    # ProceduralSceneView.swift:1514
    ('FixtureSemanticLabel', ('UIKit', 'UILabel')),       # ProceduralSceneView.swift:1357
    ('NativeMediaCardView', ('UIKit', 'UIControl')),      # ProceduralSceneView.swift:1817
    ('FixtureArtworkView', ('UIKit', 'UIView')),          # ProceduralSceneView.swift:2584 -> FixtureSemanticArtworkView: UIView
    ('FixtureBoundsAnchorView', ('UIKit', 'UIView')),     # ProceduralSceneView.swift:1501
    ('FixtureRatingBadge', ('UIKit', 'UIView')),          # FixtureComponentCatalog.swift:8
    ('CompositionBackdrop', ('UIKit', 'UIView')),         # SwiftUI backdrop hosted view
)
PUBLIC = {'UILabel', 'UIImageView', 'UIButton', 'UICollectionViewCell', 'UITableViewCell', 'UIView', 'UIControl'}
DECLARED_DECORATION = {'decorative_background', 'layout_region'}
FIXTURE_BATCHES = ('pilot-d', 'batch-v1', 'comp-v1', 'comp-v2')


def primitive_of(native_class):
    for needle, value in CLASS_MAP:
        if needle in native_class:
            return value
    name = native_class.split('.')[-1]
    return ('UIKit', name) if name in PUBLIC else (None, None)


def _rect(b):
    if not (isinstance(b, (list, tuple)) and len(b) == 4):
        return None
    x, y, w, h = b
    return [int(x), int(y), int(-(-(x + w) // 1)), int(-(-(y + h) // 1))]


def inventory_frame(inv, width, height, focus):
    """Convert 1 legacy semantic inventory to a contract frame (audit assumptions A1/A2)."""
    els = [e for e in inv.get('elements') or [] if not e.get('is_hidden') and (e.get('effective_alpha', 1) or 0) > 0 and e.get('visible_pixel_bounds')]
    ids = {e['id'] for e in els}
    focusable = {e['id'] for e in els if e.get('focusable')}
    objects = []
    for e in els:
        fw, prim = primitive_of(e.get('native_class', ''))
        c = dict(instance_id=e['id'], framework=fw, primitive=prim, source='legacy_semantic_inventory') if prim else None
        if c is not None and e.get('role') in DECLARED_DECORATION:
            c['purpose'] = 'decorative'
        # A1: ownership from declared_parent_id, or from the view-hierarchy path `<control>/view:<index path>`.
        parent = e.get('declared_parent_id') or (e['id'].split('/view:')[0] if '/view:' in e['id'] else None)
        rel = None
        if parent in focusable and parent in ids and not e.get('focusable'):
            rel = 'same_action'                                 # A1
        elif parent not in ids:
            parent = None
        elif parent is not None:
            rel = 'separate_action' if e.get('focusable') else None
        objects.append(dict(id=e['id'], construction=c, parent_id=parent, owner_relation=rel,
                            observation=dict(instance_id=e['id'], uikit_class=e.get('native_class'), visible_bounds_px=_rect(e['visible_pixel_bounds']),
                                             focusable=bool(e.get('focusable')), selected=e.get('selected'), scene_revision='legacy', screenshot_sha256='legacy')))
    return dict(scene_revision='legacy', screenshot_sha256='legacy', width=width, height=height, objects=objects, focus=focus)


def audit_fixture(batch_root):
    """Yield 1 record per Fixture frame (focused and baseline) under a batch root."""
    for meta_path in sorted(Path(batch_root).rglob('*_metadata.json')):
        meta = q.load(meta_path)
        recipe = meta.get('recipe') or {}
        fam = fr.family(recipe) if 'archetype' in recipe else 'unknown'
        w, h = int(meta.get('scene_width', 0)), int(meta.get('scene_height', 0))
        for kind, scene_key, png_key, sha_key in (('foc', 'focused_scene', 'focused_png', 'focused_sha256'),
                                                  ('unf', 'baseline_scene', 'unfocused_png', 'unfocused_sha256')):
            png = meta.get(png_key)
            if not png:
                continue
            rec = dict(source=f'fixture:{Path(batch_root).name}', family=fam, frame=f'{meta_path.parent.name}/{png}')
            img = meta_path.parent / png
            if not meta.get('is_settled') or not img.is_file() or (meta.get(sha_key) and q.digest(img) != meta.get(sha_key)):
                yield dict(rec, status='excluded', reasons=['not_settled_or_hash'])
                continue
            inv = (meta.get(scene_key) or {}).get('semantic_inventory') or {}
            if kind == 'foc':
                focus = dict(state='focused', id=meta.get('focused_element_id'), source='native_focus_observation') if meta.get('focused_element_id') else dict(state='unknown')
            else:
                focus = dict(state='known_no_focus', source='paired_baseline')
            if not inv.get('elements'):
                yield dict(rec, status='needs_recapture', reasons=['no_semantic_inventory'], focus_verified=focus['state'] != 'unknown')
                continue
            proj = fp.project_frame(inventory_frame(inv, w, h, focus))
            unresolved = collections.Counter(o['reason'] for o in proj['objects'] if o['disposition'] == 'unresolved')
            targets = collections.Counter(t['class'] for t in proj['targets'])
            custom = sum(1 for o in proj['objects'] if o['reason'] == 'ttr_convention_not_admitted' and (o['attributes'].get('focusable')))
            # Focus-only use relies on TTR's verified native focus, not on the detector projection of the focused object.
            focus_ok = focus['state'] in ('focused', 'known_no_focus')
            status = 'reprojectable' if proj['eligible'] else ('focus_only' if focus_ok else 'needs_recapture')
            yield dict(rec, status=status, reasons=sorted(unresolved), unresolved=dict(unresolved), targets=dict(targets),
                       custom_controls=custom, focus_verified=focus_ok)


def audit_membership_sources():
    """Generator, programme and native-focus rows: construction evidence is absent by construction path."""
    seen, out = set(), []
    base = q.ROOT / 'reports/work/RESET604/membership'
    for m in ('v3-d1', 'v3-focus-supervision'):
        doc = q.load(base / m / 'membership.json')
        held = q.load(base / m / 'held-out.json')['rows']
        for r in doc['rows'] + held:
            src = r.get('sourceRole')
            if src == 'fixture-batch' or r['image']['sha256'] in seen:
                continue
            seen.add(r['image']['sha256'])
            if src in ('train', 'validation'):
                out.append(dict(source='generator:tvos560/cells6', family='generator', frame=r['id'], status='needs_recapture',
                                reasons=['class_from_id_prefix'], targets=dict(collections.Counter(c['class'] for c in r['controls']))))
            else:
                ok = r.get('focusState') in ('focused', 'no_focus')
                out.append(dict(source=f'ttr:{src}', family=src, frame=r['id'], status='focus_only' if ok else 'needs_recapture',
                                reasons=['partial_labels_role_only'], focus_verified=ok))
    return out


def audit_tvbench():
    """TVBench development labels: SDK drafts with legacy classes and no construction facts."""
    rows = []
    for d in ('dev-labels-v2', 'dev-regression-labels-v2'):
        for p in sorted((q.ROOT / 'dataset/real_apps/tvbench-v1' / d).glob('*.json')):
            lab = q.load(p)
            app = p.stem.split('-')[0]
            objs = lab.get('objects') or []
            rows.append(dict(source=f'tvbench:{d}', app=app, frame=p.stem, objects=len(objs),
                             legacy_classes=dict(collections.Counter(o.get('class') or 'none' for o in objs)),
                             construction_facts=sum(1 for o in objs if o.get('construction'))))
    return rows


def summarize(records):
    table = collections.defaultdict(lambda: collections.Counter())
    reasons = collections.defaultdict(collections.Counter)
    targets = collections.defaultdict(collections.Counter)
    custom = collections.Counter()
    for r in records:
        key = (r['source'], r['family'])
        table[key][r['status']] += 1
        table[key]['frames'] += 1
        for k, v in (r.get('unresolved') or {}).items():
            reasons[key][k] += v
        for k in r.get('reasons') or []:
            if not r.get('unresolved'):
                reasons[key][k] += 1
        if r['status'] == 'reprojectable':
            targets[key].update(r.get('targets') or {})
        custom[key] += r.get('custom_controls', 0)
    return table, reasons, targets, custom


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, default=q.ROOT / 'reports/work/RESET604')
    args = parser.parse_args()
    records = []
    for b in FIXTURE_BATCHES:
        records.extend(audit_fixture(q.ROOT / 'dataset/tvos_captures/reset604' / b))
    records.extend(audit_membership_sources())
    tvbench = audit_tvbench()
    table, reasons, targets, custom = summarize(records)
    contract, digest = fp.load_contract()
    doc = dict(version='compliance-audit604-v1', contract=contract['contract'], mapping_version=contract['mapping_version'], contract_sha256=digest,
               class_map_revision=CLASS_MAP_REVISION, assumptions=['A1: a non-focusable inventory child of a focusable control (declared_parent_id or view-hierarchy path) is same_action owned',
               'A2: legacy metadata has no construction-observation join; reprojectable frames still need a contract re-export'],
               families=[dict(source=s, family=f, **dict(c), unresolved_reasons=dict(reasons[(s, f)]), reprojectable_targets=dict(targets[(s, f)]),
                              custom_focusable_controls=custom[(s, f)]) for (s, f), c in sorted(table.items())],
               tvbench=tvbench)
    q.save(args.out / 'compliance-audit-v1.json', doc, replace=True)
    totals = collections.Counter()
    for c in table.values():
        totals.update(c)
    lines = ['# Compliance audit v1 — existing tvOS data against tvos-framework-projection-v1', '',
             f"Contract SHA-256 `{digest}`. Class map from {CLASS_MAP_REVISION}. Read-only; no data changed.",
             'No current membership has demonstrated compliance with the new contract. This audit counts what existing evidence can recover.', '',
             f"Totals: {totals['frames']} frames; reprojectable {totals['reprojectable']}, needs recapture {totals['needs_recapture']}, "
             f"focus only {totals['focus_only']}, excluded {totals['excluded']}.", '',
             '| Source | Family | Frames | Reprojectable | Needs recapture | Focus only | Excluded | Custom focusable controls | Top unresolved reasons |',
             '|---|---|---|---|---|---|---|---|---|']
    for f in doc['families']:
        top = ', '.join(f'{k} {v}' for k, v in sorted(f['unresolved_reasons'].items(), key=lambda x: -x[1])[:3])
        lines.append(f"| {f['source']} | {f['family']} | {f.get('frames', 0)} | {f.get('reprojectable', 0)} | {f.get('needs_recapture', 0)} | "
                     f"{f.get('focus_only', 0)} | {f.get('excluded', 0)} | {f['custom_focusable_controls']} | {top} |")
    lines += ['', '## TVBench development labels', '',
              '| App | Frames | Objects | Objects with construction facts | Legacy classes |', '|---|---|---|---|---|']
    apps = collections.defaultdict(lambda: [0, 0, 0, collections.Counter()])
    for r in tvbench:
        a = apps[r['app']]; a[0] += 1; a[1] += r['objects']; a[2] += r['construction_facts']; a[3].update(r['legacy_classes'])
    for app, (n, o, c, cl) in sorted(apps.items()):
        lines.append(f"| {app} | {n} | {o} | {c} | {', '.join(f'{k} {v}' for k, v in cl.most_common())} |")
    lines += ['', 'TVBench objects carry no construction facts, so custom controls cannot be counted from these labels.',
              'They need an SDK re-capture that records construction facts (TTR R604-07, R604-14).',
              'Assumptions: ' + ' '.join(doc['assumptions'])]
    (args.out / 'compliance-audit-v1.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines[:6 + len(doc['families']) + 4]))


if __name__ == '__main__':
    main()
