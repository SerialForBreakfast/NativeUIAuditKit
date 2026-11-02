"""PILLS560: build the R2 role membership from the R1 (ROLES559) rows.

Unchanged families keep their R1 rows; each row must have the same pixels (SHA-256) in the regenerated dataset.
`tvOSTopTabBar` rows point to the regenerated images at the same index. `tvOSTabRows` adds stratified train and calibration rows (seed 560).
Pixel-unique rows only, as in CELLS558. Labels map to roles through `roles559.sidecar_roles`.
R3 (PIN repair): --r1 membership-r2.json --extend-family tvOSPINEntry --train 20 --calibration 2 --name r3.
R4 (rule B, no text boxes inside buttons): --r1 membership-r3.json --rule-b --name r4.
R5 (plain focus platter): --r1 membership-r4.json --dataset dataset/tvos560/platter --replace tvOSTopTabBar,tvOSTabRows --name r5.
Usage: pills560_membership.py --r1 reports/work/REALAPP557/roles559/membership-roles-c2.json --dataset dataset/tvos560/pills --out reports/work/REALAPP557/pills560
"""
import argparse
import random
from pathlib import Path
import research_queue as q
import detector_training419 as t
from template_inputs398 import pin
from roles559 import sidecar_roles

CHANGED, NEW = 'tvOSTopTabBar', 'tvOSTabRows'


def controls(sidecar, button_text=True):
    return [dict(id=k, bounds=[round(v, 3) for v in b['box']], **{'class': b['cls']}) for k, b in sidecar_roles(sidecar, button_text).items()]


def row(image, role, split, button_text=True):
    d = q.load(image.with_suffix('.json'))
    return dict(id=f'tvos560-{split}-{image.stem}', group='px-'+d['imageSHA256'][:16], role=role, sourceRole=split,
                trainingEligible=role == 'train', labelsComplete=True, width=1920, height=1080, image=pin(image), controls=controls(image.with_suffix('.json'), button_text))


def build(r1, root, out, train, calibration):
    doc = q.load(r1); rows, seen, changed = [], set(), 0
    for old in doc['rows']:
        src = q.ROOT/old['image']['path']; split = src.parent.name; image = root/split/src.name
        family = q.load(image.with_suffix('.json'))['generatorProfile']['templateFamily']
        if family == CHANGED:
            new = row(image, old['role'], split); changed += 1
        else:
            q.require(q.digest(image) == old['image']['sha256'], 'pills560_unchanged_pixels:' + image.name)
            new = dict(old, id=old['id'].replace('tvos558', 'tvos560'), image=pin(image))
        q.require(new['group'] not in seen, 'pills560_duplicate_pixels'); seen.add(new['group']); rows.append(new)
    rng = random.Random(560); added = {}
    for split, role, quota in (('train', 'train', train), ('validation', 'calibration', calibration)):
        pool = sorted(p for p in (root/split).glob('*.png') if q.load(p.with_suffix('.json'))['generatorProfile']['templateFamily'] == NEW)
        rng.shuffle(pool); n = 0
        for image in pool:
            if n == quota:
                break
            item = row(image, role, split)
            if item['group'] in seen:
                continue
            seen.add(item['group']); rows.append(item); n += 1
        added[role] = n
    new = dict(doc, rows=rows, calibrationGroups=sorted({r['group'] for r in rows if r['role'] == 'calibration'}),
               targetScope=doc['targetScope'] + ' PILLS560: TabRow pills with nested labels, tvOSTabRows family.',
               limitation=doc['limitation'] + f' {CHANGED} regenerated; {NEW} added (seed 560).')
    path = Path(out)/'membership-r2.json'; q.save(path, new, replace=True)
    check = q.ROOT/f'.build/debug-output/pills560-prepare-{q.digest(path)[:8]}'; check.mkdir(parents=True, exist_ok=True)
    counts = t.prepare(new, check)[1] if not (check/'dataset').exists() else 'checked earlier'
    return dict(path=str(path), sha256=q.digest(path), rows=len(rows), changedRows=changed, added=added, counts=counts)


def extend(base, root, out, family, train, calibration, name):
    """Add pixel-unique rows of 1 family to an existing role membership (seed 561). Existing rows stay unchanged."""
    doc = q.load(base); rows = list(doc['rows']); seen = {r['group'] for r in rows}
    rng = random.Random(561); added = {}
    for split, role, quota in (('train', 'train', train), ('validation', 'calibration', calibration)):
        pool = sorted(p for p in (root/split).glob('*.png') if q.load(p.with_suffix('.json'))['generatorProfile']['templateFamily'] == family)
        rng.shuffle(pool); n = 0
        for image in pool:
            if n == quota:
                break
            item = row(image, role, split)
            if item['group'] not in seen:
                seen.add(item['group']); rows.append(item); n += 1
        added[role] = n
    new = dict(doc, rows=rows, calibrationGroups=sorted({r['group'] for r in rows if r['role'] == 'calibration'}),
               limitation=doc['limitation'] + f' {family}: +{added["train"]} train, +{added["calibration"]} calibration (seed 561).')
    path = Path(out)/f'membership-{name}.json'; q.save(path, new, replace=True)
    check = q.ROOT/f'.build/debug-output/pills560-prepare-{q.digest(path)[:8]}'; check.mkdir(parents=True, exist_ok=True)
    counts = t.prepare(new, check)[1] if not (check/'dataset').exists() else 'checked earlier'
    return dict(path=str(path), sha256=q.digest(path), rows=len(rows), added=added, counts=counts)


def rule_b(base, out, name):
    """Remove `text` controls inside `button` controls (roles559 rule B). Rows, groups, roles and images stay unchanged."""
    doc = q.load(base); rows, removed = [], 0
    for r in doc['rows']:
        keep = sidecar_roles(q.ROOT/Path(r['image']['path']).with_suffix('.json'), button_text=False)
        controls = [c for c in r['controls'] if c['id'] in keep]
        removed += len(r['controls']) - len(controls); rows.append(dict(r, controls=controls))
    new = dict(doc, rows=rows, targetScope=doc['targetScope'] + ' Rule B: text inside a button is part of the button.',
               limitation=doc['limitation'] + f' Rule B removed {removed} text boxes inside buttons.')
    path = Path(out)/f'membership-{name}.json'; q.save(path, new, replace=True)
    check = q.ROOT/f'.build/debug-output/pills560-prepare-{q.digest(path)[:8]}'; check.mkdir(parents=True, exist_ok=True)
    counts = t.prepare(new, check)[1] if not (check/'dataset').exists() else 'checked earlier'
    return dict(path=str(path), sha256=q.digest(path), rows=len(rows), removedTextBoxes=removed, counts=counts)


def replace(base, root, out, families, name):
    """Point rows of `families` at regenerated images (same split and index) with rule-B labels. Other rows must keep identical pixels."""
    doc = q.load(base); rows, seen, changed = [], set(), 0
    for old in doc['rows']:
        src = q.ROOT/old['image']['path']; split = src.parent.name; image = root/split/src.name
        if q.load(image.with_suffix('.json'))['generatorProfile']['templateFamily'] in families:
            new = row(image, old['role'], split, button_text=False); new['id'] = old['id']; changed += 1
        else:
            new = old  # Keep the original pin: regenerated unchanged families can differ by ±2 levels of rendering noise.
        q.require(new['group'] not in seen, 'pills560_duplicate_pixels'); seen.add(new['group']); rows.append(new)
    new = dict(doc, rows=rows, calibrationGroups=sorted({r['group'] for r in rows if r['role'] == 'calibration'}),
               targetScope=doc['targetScope'] + ' R5: focused tabs may show a .plain platter beyond the labeled frame.',
               limitation=doc['limitation'] + f' {",".join(families)} regenerated with the plain focus platter ({changed} rows).')
    path = Path(out)/f'membership-{name}.json'; q.save(path, new, replace=True)
    check = q.ROOT/f'.build/debug-output/pills560-prepare-{q.digest(path)[:8]}'; check.mkdir(parents=True, exist_ok=True)
    counts = t.prepare(new, check)[1] if not (check/'dataset').exists() else 'checked earlier'
    return dict(path=str(path), sha256=q.digest(path), rows=len(rows), changedRows=changed, counts=counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--r1', type=Path, required=True); parser.add_argument('--dataset', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--train', type=int, default=120); parser.add_argument('--calibration', type=int, default=16)
    parser.add_argument('--extend-family', help='Add rows of this family to --r1 instead of building R2, for example tvOSPINEntry')
    parser.add_argument('--name', default='r3', help='Membership name for --extend-family or --rule-b')
    parser.add_argument('--rule-b', action='store_true', help='Remove text boxes inside buttons from --r1 (R4)')
    parser.add_argument('--replace', help='Comma-separated families to point at --dataset (R5)')
    args = parser.parse_args()
    if args.replace:
        print(replace(args.r1, args.dataset.resolve(), args.out, set(args.replace.split(',')), args.name))
    elif args.rule_b:
        print(rule_b(args.r1, args.out, args.name))
    elif args.extend_family:
        print(extend(args.r1, args.dataset.resolve(), args.out, args.extend_family, args.train, args.calibration, args.name))
    else:
        print(build(args.r1, args.dataset.resolve(), args.out, args.train, args.calibration))


if __name__ == '__main__':
    main()
