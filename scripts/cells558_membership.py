"""CELLS558: build matched T89 memberships C1 (variation only) and C2 (plus content cells).

1 row per unique image (pixel SHA-256); images in train never enter calibration; stratified per family (seed 558).
Keyboard and PIN keys are capped at 25% of `collectionItem` boxes in train (Research §5.2.1), keeping ≥ 8 images per key family.
Writes membership-c1.json, membership-c2.json and test-unique.json, and validates each with the T89 `prepare` rules.
Usage: cells558_membership.py --dataset dataset/tvos558/cells --out reports/work/REALAPP557/cells558
"""
import argparse
import collections
import random
from pathlib import Path
import research_queue as q
import detector_training419 as t
from template_inputs398 import pin

NAMES = [c['name'] for c in sorted(q.load(q.ROOT/'Research/schemas/category_map.json')['categories'], key=lambda c: c['id'])]
KEY_FAMILIES = ('tvOSKeyboard', 'tvOSPINEntry')
CAP, MIN_KEY_IMAGES = .25, 8


def row(f, split, role):
    d = q.load(f); controls = []; keys = 0
    for i, e in enumerate(d['elements']):
        if e['elementType'] not in NAMES:
            continue
        b = e['boundsPixels']; x, y = max(b['x'], 0), max(b['y'], 0)
        x2, y2 = min(b['x']+b['width'], 1920), min(b['y']+b['height'], 1080)
        if x2 <= x or y2 <= y:
            continue
        controls.append({'id': f'e{i:03}', 'class': e['elementType'], 'bounds': [x, y, x2-x, y2-y]})
        keys += e['id'].startswith(('collectionItem_key_', 'collectionItem_keypad_'))
    rid = f'tvos558-{split}-{f.stem}'
    return dict(row=dict(id=rid, group='px-'+d['imageSHA256'][:16], role=role, sourceRole=split, trainingEligible=role == 'train',
                         labelsComplete=True, width=1920, height=1080, image=pin(f.with_suffix('.png')), controls=controls),
                family=d['generatorProfile']['templateFamily'], keys=keys, sha=d['imageSHA256'])


def pools(root):
    pool, seen = {'train': [], 'calibration': []}, {}
    for split, role in (('train', 'train'), ('validation', 'calibration')):
        for f in sorted((root/split).glob('*.json')):
            item = row(f, split, role)
            if item['sha'] not in seen:
                seen[item['sha']] = role; pool[role].append(item)
    test = []
    for f in sorted((root/'test').glob('*.png')):
        sha = q.digest(f)
        if sha not in seen:
            test.append(f.stem); seen[sha] = 'test'
    return pool, test


def cap_keys(rows):
    """Drop key images, alternating between key families, until keys are ≤ CAP of collectionItem boxes."""
    def share():
        train = [x for x in rows if x['row']['role'] == 'train']
        keys = sum(x['keys'] for x in train)
        cards = sum(sum(c['class'] == 'collectionItem' for c in x['row']['controls']) for x in train)
        return keys, cards
    turn = 0
    while True:
        keys, cards = share()
        if keys <= CAP * cards:
            return keys, cards
        family = KEY_FAMILIES[turn % 2]; turn += 1
        candidates = [x for x in rows if x['row']['role'] == 'train' and x['family'] == family and x['keys'] > 0]
        if len(candidates) <= MIN_KEY_IMAGES:
            other = KEY_FAMILIES[turn % 2]
            if len([x for x in rows if x['row']['role'] == 'train' and x['family'] == other and x['keys'] > 0]) <= MIN_KEY_IMAGES:
                return keys, cards  # Both key families at their minimum; report the share.
            continue
        rows.remove(candidates[-1])


def build(pool, name, families, quota, out):
    rng = random.Random(558); rows = []
    for role in ('train', 'calibration'):
        by = collections.defaultdict(list)
        for item in pool[role]:
            if item['family'] in families:
                by[item['family']].append(item)
        for family in sorted(by):
            items = sorted(by[family], key=lambda x: x['row']['id']); rng.shuffle(items)
            rows += items[:quota(family, role)]
    keys, cards = cap_keys(rows)
    doc = dict(version='detector-training-membership-v1', trainingAdmitted=True, names=NAMES, rows=[x['row'] for x in rows],
               selection='fixed-last', modelAccepted=False, generalUILabelsComplete=True,
               calibrationGroups=sorted({x['row']['group'] for x in rows if x['row']['role'] == 'calibration'}),
               targetScope=f'CELLS558 {name}: synthetic tvOS generator, whole-cell labels, S2 variation'
                           + (', content cells' if 'tvOSContentCells' in families else '') + '.',
               limitation='One row per unique image; no pixels shared by train and calibration. Stratified per family (seed 558). '
                          f'Keys capped at {CAP:.0%} of collectionItem boxes in train, at least {MIN_KEY_IMAGES} images per key family.')
    path = Path(out)/f'membership-{name}.json'; q.save(path, doc, replace=True)
    check = q.ROOT/f'.build/debug-output/cells558-prepare-{name}-{q.digest(path)[:8]}'; check.mkdir(parents=True, exist_ok=True)
    counts = t.prepare(doc, check)[1] if not (check/'dataset').exists() else 'checked earlier'
    train = [x for x in rows if x['row']['role'] == 'train']
    per = collections.Counter(x['family'] for x in train)
    return dict(name=name, counts=counts, keys=keys, cards=cards, keyShare=round(keys/cards, 3), families=len(per), minPerFamily=min(per.values()),
                keyFamilies={f: per.get(f, 0) for f in KEY_FAMILIES}, contentCells=per.get('tvOSContentCells', 0), sha256=q.digest(path))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--dataset', type=Path, required=True); parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--train-per-family', type=int, default=32, help='C1 train images per family; C2 uses 2 fewer')
    parser.add_argument('--cells-train', type=int, default=60, help='C2 content-cell train images')
    parser.add_argument('--suffix', default='', help='Name suffix for successor memberships, for example b')
    args = parser.parse_args()
    n, cells = args.train_per_family, args.cells_train
    pool, test = pools(args.dataset)
    q.save(args.out/'test-unique.json', dict(version='cells558-test-v1', images=test), replace=True)
    families = {x['family'] for x in pool['train']}
    base = families - {'tvOSContentCells'}
    cal = max(3, n // 8)
    c1 = build(pool, 'c1'+args.suffix, base, lambda f, r: n if r == 'train' else cal, args.out)
    c2 = build(pool, 'c2'+args.suffix, families,
               lambda f, r: (cells if r == 'train' else 2*cal) if f == 'tvOSContentCells' else (n-2 if r == 'train' else cal), args.out)
    print(c1); print(c2); print('clean test images', len(test))


if __name__ == '__main__':
    main()
