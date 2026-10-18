"""Prepare matched exposure without changing source crops or evaluation membership."""
from collections import Counter
from pathlib import Path
import hashlib
from PIL import Image
import research_queue as q

OUT = None
VERSION = 'native-control-membership-v1'


def validate_rows(rows):
    groups, pixels, cache = {}, {}, {}
    unique = {'artwork': {0: [], 1: []}, 'native': {0: [], 1: []}}
    seen = set()
    for row in rows:
        role, label = row['role'], row['label']
        q.require(role in ('train', 'development') and type(label) is int and label in (0, 1), 'membership_role_label')
        q.require(groups.setdefault(row['group'], role) == role, 'membership_group_leak')
        path = Path(row['path'])
        q.require(q.digest(path) == row['sha256'], 'membership_crop_changed')
        if row['sha256'] not in cache:
            with Image.open(path) as im:
                q.require(im.size == (256, 256), 'membership_crop_size')
                cache[row['sha256']] = hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
        pixel = cache[row['sha256']]
        old = pixels.setdefault(pixel, (role, label))
        q.require(old[0] == role, 'membership_pixel_leak')
        q.require(old[1] == label, 'membership_label_conflict')
        kind = 'native' if row['family'] in ('button', 'row', 'tab') else 'artwork'
        key = (kind, row['family'] if kind == 'native' else '', pixel)
        if role == 'train' and key not in seen:
            seen.add(key)
            unique[kind][label].append(row)
    return unique


def repeat_rows(rows, count, prefix):
    q.require(rows and count >= len(rows), 'membership_insufficient_exposure')
    ordered = sorted(rows, key=lambda r: r['id'])
    return [dict(ordered[i % len(ordered)], id=f'{prefix}-{i:06d}', sourceID=ordered[i % len(ordered)]['id'])
            for i in range(count)]


def select(unique, development, per_label, native_per_label, arm):
    q.require(arm in ('control', 'mixed'), 'membership_arm')
    q.require(type(per_label) is int and per_label > 0 and per_label % 16 == 0, 'membership_exposure')
    q.require(type(native_per_label) is int and 0 < native_per_label < per_label and native_per_label % 3 == 0,
              'membership_native_quota')
    rows = []
    for label in (0, 1):
        count = per_label if arm == 'control' else per_label - native_per_label
        rows += repeat_rows(unique['artwork'][label], count, f'{arm}-artwork-{label}')
        if arm == 'mixed':
            for family in ('button', 'row', 'tab'):
                members = [r for r in unique['native'][label] if r['family'] == family]
                rows += repeat_rows(members, native_per_label // 3, f'{arm}-{family}-{label}')
    return rows + development


def run():
    from template_adapters395 import resolve_inputs, document
    cfg = q.load(OUT.parents[2]/'spec.json')['template']
    refs = resolve_inputs(cfg, OUT)
    config = document(refs['configuration'])
    q.require(set(config) == {'version', 'arm', 'perLabel', 'nativePerLabel'}, 'membership_config_fields')
    q.require(config['version'] == VERSION, 'membership_version')
    artwork, native = document(refs['artwork']), document(refs['native'])
    q.require(artwork['preprocessing'] == native['preprocessing'], 'membership_preprocessing')
    q.require(artwork['runtime'] == native['runtime'], 'membership_runtime')
    original = artwork['rows'] + native['rows']
    q.require(len({r['id'] for r in original}) == len(original), 'membership_duplicate_id')
    unique = validate_rows(original)
    development = [r for r in original if r['role'] == 'development']
    q.require(development and {r['family'] for r in development} >= {'button', 'row', 'tab'},
              'membership_development_missing')
    rows = select(unique, development, config['perLabel'], config['nativePerLabel'], config['arm'])
    training = [r for r in rows if r['role'] == 'train']
    q.save(OUT/'crops.json', dict(artwork, rows=rows, frames=artwork['frames'] + native['frames'],
                               sampling=config, sources=refs))
    q.save(OUT/'summary.json', dict(configuration=config, trainRows=len(training), developmentRows=len(development),
        classCounts=dict(Counter(r['label'] for r in training)), updatesPerEpoch=len(training)//16,
        epochs=30, fixedLast=True, positiveWeight=1, uniqueTraining={kind: {str(k): len(v) for k,v in classes.items()}
        for kind,classes in unique.items()}, modelAccepted=False))
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=name, sha256=q.digest(OUT/name)) for name in ('crops.json','summary.json')]))
