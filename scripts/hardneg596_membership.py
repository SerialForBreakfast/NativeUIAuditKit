"""HARDNEG596: FocusRing crop memberships with generator hard negatives (ARTPARITY595 follow-up, no capture needed).

Observed failure (reports/work/ARTPARITY595/shelf-pair-report.md): FocusRing scores unfocused bright artwork and plain background as focused.
Source of new crops: the tvos560 synthetic tvOS screens. Every element id ends in `_focused` or `_unfocused`, which gives the label.
Families: tab (tab pills), button (other buttons, not keys), row (listRow), cell (collectionItem cards, not keys), plain (empty background, label 0).
Crops use the production crop path (focus_runtime crop mode, FocusRingClassifier.makeCrop, 16 %, 256 x 256).
Before any mixing, the builder re-crops sample rows of the base artwork document and requires identical pixels (helper builds differ).
Arms reuse `native_control_membership.select` (the T54 selection code): control = artwork only; mixed = artwork + native button/row/tab.
Roles: tvos560 `train` split = train; `test` split = development; images whose pixels also occur in train are skipped. Groups are per image.
Usage: hardneg596_membership.py --base ARTWORK_CROPS_JSON --out reports/work/HARDNEG596 --crops dataset/focus_ring/hardneg596
"""
import argparse
import base64
import hashlib
import random
from collections import Counter
from pathlib import Path
from PIL import Image
import research_queue as q
import focus_runtime as fr
from native_control_membership import validate_rows, select
from template_inputs398 import pin

DATASET = q.ROOT/'dataset/tvos560/pills'
KEYS = ('collectionItem_key_', 'collectionItem_keypad_')
BUTTONS = {'primaryButton', 'secondaryButton', 'cancelAction', 'destructiveButton', 'menuButton'}


def family(element):
    eid, cls = element['id'], element['elementType']
    if eid.startswith(KEYS):
        return None
    if '_tab_' in eid and cls in BUTTONS:
        return 'tab'
    if cls in BUTTONS:
        return 'button'
    if cls == 'listRow':
        return 'row'
    if cls == 'collectionItem':
        return 'cell'
    return None


def label(element):
    return 1 if element['id'].endswith('_focused') else (0 if element['id'].endswith('_unfocused') else None)


def overlaps(a, b):
    return a[0] < b[0]+b[2] and b[0] < a[0]+a[2] and a[1] < b[1]+b[3] and b[1] < a[1]+a[3]


def plain_box(rng, boxes):
    for _ in range(40):
        w, h = rng.randint(220, 420), rng.randint(140, 300)
        box = [rng.randint(0, 1920-w), rng.randint(0, 1080-h), w, h]
        expanded = [box[0]-0.16*w, box[1]-0.16*h, 1.32*w, 1.32*h]
        if not any(overlaps(expanded, b) for b in boxes):
            return box
    return None


def candidates(per_label, dev_per_label, seed=596):
    rng = random.Random(seed); train_pixels = set(); pools = {}
    for split in ('train', 'test'):
        role = 'train' if split == 'train' else 'development'
        for sidecar in sorted((DATASET/split).glob('*.json')):
            d = q.load(sidecar)
            if role == 'development' and d['imageSHA256'] in train_pixels:
                continue
            if role == 'train':
                train_pixels.add(d['imageSHA256'])
            image = sidecar.with_suffix('.png'); boxes = []
            for e in d['elements']:
                b = e['boundsPixels']; box = [b['x'], b['y'], b['width'], b['height']]; boxes.append(box)
                f, y = family(e), label(e)
                if f is None or y is None or box[0] < 0 or box[1] < 0 or box[0]+box[2] > 1920 or box[1]+box[3] > 1080 or box[2] < 24 or box[3] < 16:
                    continue
                pools.setdefault((role, f, y), []).append(dict(image=image, sha=d['imageSHA256'], box=box, family=f, label=y, element=e['id'],
                                                                group='tvos560-' + image.stem, templateFamily=d['generatorProfile']['templateFamily']))
            box = plain_box(rng, boxes)
            if box:
                pools.setdefault((role, 'plain', 0), []).append(dict(image=image, sha=d['imageSHA256'], box=box, family='plain', label=0, element='plain',
                                                                       group='tvos560-' + image.stem, templateFamily=d['generatorProfile']['templateFamily']))
    chosen = []
    for key in sorted(pools):
        items = pools[key]; rng.shuffle(items)
        chosen += items[:per_label if key[0] == 'train' else dev_per_label]
    return chosen, {f'{k[0]}/{k[1]}/{k[2]}': len(v) for k, v in sorted(pools.items())}


def crop_all(items, folder):
    folder.mkdir(parents=True, exist_ok=True); rows = []
    requests = [dict(id=f"{it['group']}|{it['element']}|{i}", path=str(it['image']), sha256=q.digest(it['image']), bounds=[float(v) for v in it['box']])
                for i, it in enumerate(items)]
    by_id = {}
    for batch in fr.bounded_batches(requests, shared_images=True):
        for r in fr.invoke(batch, None)['results']:
            by_id[r['id']] = r
    for req, it in zip(requests, items):
        data = base64.b64decode(by_id[req['id']]['png']); name = hashlib.sha256(data).hexdigest()
        path = folder/f'{name}.png'
        if not path.exists():
            path.write_bytes(data)
        rows.append(dict(id='hardneg596-' + req['id'].replace('|', '-'), group=it['group'], label=it['label'], family=it['family'],
                         role='train' if it['group'] in TRAIN_GROUPS else 'development', path=str(path), sha256=q.digest(path),
                         profile='standard', box=it['box'], control=it['element'], frame=it['group'], source='tvos560-generator',
                         templateFamily=it['templateFamily']))
    return dedupe(rows)


def dedupe(rows):
    """Keep the T54 pixel rules: no crop pixels in both train and development, no pixels with both labels."""
    def pixels(r):
        with Image.open(r['path']) as im:
            return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
    for r in rows:
        r['_pixel'] = pixels(r)
    labels, train = {}, {r['_pixel'] for r in rows if r['role'] == 'train'}
    for r in rows:
        labels.setdefault(r['_pixel'], set()).add(r['label'])
    kept = [r for r in rows if len(labels[r['_pixel']]) == 1 and not (r['role'] == 'development' and r['_pixel'] in train)]
    DEDUPE.update(dropped=len(rows) - len(kept), labelConflicts=sum(len(v) > 1 for v in labels.values()))
    for r in kept:
        r.pop('_pixel')
    return kept


DEDUPE = {}
TRAIN_GROUPS = set()


def check_base_pixels(base, sample=24):
    """Re-crop base rows with the current helper; the crops must be pixel-identical."""
    frames = {f['id']: f for f in base.get('frames', []) if isinstance(f, dict) and 'id' in f}
    rows = [r for r in base['rows'] if r.get('frame') in frames and frames[r['frame']].get('image')][:sample]
    if not rows:
        return dict(checked=0, note='base frames carry no source image paths; pixel check not possible')
    same = 0
    for r in rows:
        f = frames[r['frame']]; image = q.ROOT/f['image']['path'] if isinstance(f['image'], dict) else Path(f['image'])
        reply = fr.invoke([dict(id='x', path=str(image), sha256=q.digest(image), bounds=[float(v) for v in r['box']])], None)['results'][0]
        new = Image.open(__import__('io').BytesIO(base64.b64decode(reply['png']))).convert('RGB').tobytes()
        same += new == Image.open(r['path']).convert('RGB').tobytes()
    return dict(checked=len(rows), identical=same)


def programme_rows(folder, crops):
    """Registered-control crops from ARTPARITY595 Programme train frames: focused control = 1; unfocused controls, illustration, plain patch = 0."""
    rng = random.Random(595); items = []
    for sidecar in sorted(folder.glob('*/position-*.json')):
        d = q.load(sidecar)
        if d['dataRole'] != 'train':
            continue
        image = sidecar.with_suffix('.png'); boxes = []
        for e in d['elements']:
            b = e['boundsPixels']; box = [b['x'], b['y'], b['width'], b['height']]; boxes.append(box)
            items.append(dict(image=image, box=box, family='programme', label=int(e['focused']), element=f"{e['id']}-p{d['position']}",
                              group=d['group'], templateFamily=d['screen']))
        box = plain_box(rng, boxes)
        if box:
            items.append(dict(image=image, box=box, family='programme', label=0, element=f"plain-p{d['position']}", group=d['group'], templateFamily=d['screen']))
    TRAIN_GROUPS.update(it['group'] for it in items)
    rows = crop_all(items, crops)
    for r in rows:
        r['source'] = 'artparity595-programme'
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--base', type=Path, required=True); parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--crops', type=Path, required=True)
    parser.add_argument('--per-label', type=int, default=600); parser.add_argument('--dev-per-label', type=int, default=80)
    parser.add_argument('--exposure', type=int, default=3600); parser.add_argument('--native-exposure', type=int, default=900)
    parser.add_argument('--programme', type=Path, help='ARTPARITY595 Programme folder: write only the hardneg-programme arm (train editions)')
    args = parser.parse_args()
    args.out, args.crops, args.base = args.out.resolve(), args.crops.resolve(), args.base.resolve()
    base = q.load(args.base)
    pixel_check = check_base_pixels(base)
    items, pool_sizes = candidates(args.per_label, args.dev_per_label)
    TRAIN_GROUPS.update(it['group'] for it in items if 'train' in str(it['image'].parent.name))
    rows = crop_all(items, args.crops)
    native = [r for r in rows if r['family'] in ('button', 'row', 'tab')]
    artwork = [r for r in rows if r['family'] in ('cell', 'plain')]
    args.out.mkdir(parents=True, exist_ok=True)
    header = {k: v for k, v in base.items() if k not in ('rows', 'frames')}
    header['runtime'] = fr.identity()
    common = dict(header, frames=[], baseArtwork=pin(args.base), basePixelCheck=pixel_check, poolSizes=pool_sizes, cropDedupe=DEDUPE,
                  limitation='Synthetic generator crops (tvos560). Development rows are generator test-split images, not real apps. Provisional.')
    outputs = {}
    arms = (('control', [], 'control'), ('mixed', [], 'mixed'), ('hardneg', artwork, 'control'), ('hardneg-mixed', artwork, 'mixed'))
    if args.programme:
        arms = (('hardneg-programme', artwork + programme_rows(args.programme.resolve(), args.crops), 'mixed'),)
    for name, artwork_rows, arm in arms:
        original = base['rows'] + artwork_rows + native
        unique = validate_rows(original)
        development = [r for r in original if r['role'] == 'development']
        print(name, {k: {l: len(v) for l, v in c.items()} for k, c in unique.items()}, flush=True)
        chosen = select(unique, development, args.exposure, args.native_exposure, arm)
        doc = dict(common, rows=chosen, sampling=dict(arm=arm, perLabel=args.exposure, nativePerLabel=args.native_exposure, artworkAdditions=len(artwork_rows)))
        path = args.out/f'crops-{name}.json'; q.save(path, doc, replace=True)
        train = [r for r in chosen if r['role'] == 'train']
        outputs[name] = dict(path=str(path.relative_to(q.ROOT)), sha256=q.digest(path), train=len(train), development=len(development),
                             trainByFamily=dict(Counter(f"{r['family']}/{r['label']}" for r in train if r.get('source') == 'tvos560-generator')))
    summary = args.out/('membership-summary-programme.json' if args.programme else 'membership-summary.json')
    q.save(summary, dict(version='hardneg596-memberships-v1', pixelCheck=pixel_check, pools=pool_sizes, outputs=outputs), replace=True)
    print(pixel_check); print(outputs)


if __name__ == '__main__':
    main()
