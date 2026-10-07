"""Reuse reviewed native frames for a fixed focus-change comparison."""
import argparse
from collections import Counter
import hashlib
import itertools
from pathlib import Path
import shutil
import time

import numpy as np
from PIL import Image

import harvest_schema4_review as review
import native_adapt152 as n
from diagnose_signal95 import encoded
from diagnose_reflow115 import decisions

h = n.h
OUT = h.ROOT / 'reports/work/TRANSITION-242/artifacts-v2'
CONTROL = h.ROOT / 'NativeUITrainer/focus_ring_runs/residual158-dtm054'
SOURCES = {
    '233': 'reports/work/FOCUS-REPAIR-233/artifacts',
    '234': 'reports/work/FOCUS-RETENTION-234/artifacts',
    '236': 'reports/work/FOCUS-REVIEW-236/artifacts/capture',
    '239': 'reports/work/FOCUS-ARTWORK-239/artifacts/capture-v2',
}


def sha(value):
    return hashlib.sha256(value).hexdigest()


def label(before, after):
    """Use observed native focus, not requested focus or model scores."""
    values = []
    for scene in (before, after):
        obs = scene.get('focus_observation', {})
        identity = obs.get('observedID')
        review.require(obs.get('verified') is True and obs.get('source') == 'uikit_focus_system'
                       and isinstance(identity, str) and identity
                       and scene.get('focused_element_id') == identity
                       and scene.get('is_settled') is True, 'unverified_focus')
        values.append(identity)
    return int(values[0] != values[1])


def check_roles(rows):
    """Reject duplicate IDs and exact images shared with training."""
    ids = set()
    pixels = {}
    for row in rows:
        review.require(row['id'] not in ids, 'duplicate_pair')
        ids.add(row['id'])
        review.require(row['role'] in ('train', 'reserved', 'development'), 'invalid_role')
        for key in row['pixelHashes']:
            roles = pixels.setdefault(key, set())
            roles.add(row['role'])
            review.require(not ('train' in roles and len(roles) > 1), 'cross_role_pixels')


def prepare():
    review.require(not OUT.exists(), 'output_collision')
    started = time.monotonic()
    banks = {}
    pins = []
    raw = {}
    tensors = {}
    expected = {'233': 32, '234': 24, '236': 12, '239': 8}
    for source, relative in SOURCES.items():
        root = h.ROOT / relative
        intake = h.read(root / 'intake.json')
        pins.append(h.ref(root / 'intake.json'))
        reviewed = intake['review']['rows']
        review.require(len(reviewed) == expected[source], 'source_membership')
        for item in reviewed:
            path = root / 'exports' / item['path']
            meta = review.decode(path.read_bytes())
            checked = review.pair(path.parent, path.name, expected_version=meta['schema_version'])
            review.require(checked['metadataSHA256'] == item['metadataSHA256'], 'source_changed')
            recipe = Path(item['path']).parent.as_posix()
            group = source + ':' + recipe
            role = 'development' if source == '239' else 'train'
            if source == '233':
                matching = [s for s in intake['samples']
                            if Path(s['root']).name == recipe and s['metadata'] == path.name]
                roles = {s['role'] for s in matching}
                review.require(len(matching) == 2 and len(roles) == 1, 'source_roles')
                role = roles.pop()
            bank = banks.setdefault(group, dict(source=source, recipe=recipe, role=role, endpoints={}))
            pair_endpoints = []
            for endpoint, scene_key in [('unfocused', 'baseline_scene'), ('focused', 'focused_scene')]:
                image_path = path.parent / meta[endpoint + '_png']
                image_hash = meta[endpoint + '_sha256']
                if image_hash not in raw:
                    with Image.open(image_path) as image:
                        image.load()
                        image = image.convert('RGB')
                        raw[image_hash] = sha(str(image.size).encode() + image.tobytes())
                        tensors[image_hash] = encoded(image, image, (192, 128))[0][:3]
                scene = meta[scene_key]
                label(scene, scene)
                entry = dict(image=h.ref(image_path), pixels=raw[image_hash],
                             observedID=scene['focused_element_id'], metadata=h.ref(path))
                previous = bank['endpoints'].setdefault(image_hash, entry)
                review.require(previous['observedID'] == entry['observedID'], 'conflicting_pixel_focus')
                pair_endpoints.append(image_hash)
            bank.setdefault('originalPairs', []).append(pair_endpoints)

    rows = []
    values = []
    seen = {}

    def add(group, a, b, condition, scope=None):
        ba, ia = a
        bb, ib = b
        ea, eb = banks[ba]['endpoints'][ia], banks[bb]['endpoints'][ib]
        role = banks[ba]['role']
        review.require(role == banks[bb]['role'], 'cross_role_pair')
        changed = int(ea['observedID'] != eb['observedID'])
        value = np.concatenate([tensors[ia], tensors[ib]])
        key = sha(value.tobytes())
        if key in seen:
            old = seen[key]
            review.require(old['changed'] == changed and old['role'] == role, 'encoded_label_or_role_conflict')
            old['conditions'] = sorted(set(old['conditions'] + [condition]))
            return
        row = dict(id=group + ':' + key, group=group, role=role,
                   source=banks[ba]['source'], changed=changed, conditions=[condition],
                   scope=scope or 'constructed_endpoints_not_recorded_actions',
                   images=[ea['image'], eb['image']], metadata=[ea['metadata'], eb['metadata']],
                   pixelHashes=[ea['pixels'], eb['pixels']], observedIDs=[ea['observedID'], eb['observedID']],
                   tensorSHA256=key)
        rows.append(row)
        values.append(value)
        seen[key] = row

    for group, bank in banks.items():
        for a, b in bank['originalPairs']:
            add(group, (group, a), (group, b), 'original_capture', 'bracketed_endpoint_pair_not_settling')
        for a, b in itertools.combinations(bank['endpoints'], 2):
            add(group, (group, a), (group, b), 'within_recipe')
        for a in bank['endpoints']:
            add(group, (group, a), (group, a), 'identity', 'exact_identity_control')

    # The reviewed 239 matrix changes artwork or backdrop within each fixed composition.
    # These comparisons stay outside training and do not claim a recorded action.
    for theme in ('dark', 'light'):
        groups = sorted(k for k in banks if k.startswith('239:' + theme + '-'))
        review.require(len(groups) == 4, 'artwork_matrix')
        for ga, gb in itertools.combinations(groups, 2):
            for a, b in itertools.product(banks[ga]['endpoints'], banks[gb]['endpoints']):
                add('239:' + theme, (ga, a), (gb, b), 'artwork_contrast',
                    'controlled_cross_recipe_focus_state_not_action')
    check_roles(rows)
    native = np.stack(values)
    OUT.mkdir(parents=True)
    shutil.copyfile(__file__, OUT / 'preparation-source.py')
    np.save(OUT / 'native.npy', native, allow_pickle=False)
    doc = dict(version='transition242-v1', rows=rows, sources=pins, tensor=h.ref(OUT / 'native.npy'),
               source=h.ref(__file__), validator=h.ref(review.__file__), encoder=h.ref(h.ROOT / 'scripts/diagnose_signal95.py'),
               admission='Development training only for 233 train, 234, and 236. Reserved and 239 never train.',
               independentEvaluation=False, modelInput='pixels_only', nativePairs=sum(expected.values()),
               uniqueFrames=len(raw), counts=dict(Counter(r['role'] for r in rows)),
               seconds=time.monotonic() - started)
    h.write(OUT / 'inputs.json', doc, sealed=True)
    print({k:doc[k] for k in ('nativePairs', 'uniqueFrames', 'counts', 'seconds')}, flush=True)


def load_inputs():
    doc = h.read(OUT / 'inputs.json')
    review.require(doc['seal'] == h.digest({k:v for k,v in doc.items() if k != 'seal'}), 'input_seal')
    # Keep the preparation source with the cache. Scoring edits need no pixel reload.
    review.require(sha((OUT / 'preparation-source.py').read_bytes()) == doc['source']['sha256'],
                   'preparation_source_changed')
    for ref in [*doc['sources'], doc['validator'], doc['encoder']]:
        h.checked(h.ROOT, ref)
    x = np.load(h.checked(h.ROOT, doc['tensor'], 512 * 1024**2), allow_pickle=False)
    rows = doc['rows']
    review.require(x.shape == (len(rows), 6, 128, 192) and x.dtype == np.float32
                   and np.isfinite(x).all() and ((x >= 0) & (x <= 1)).all(), 'tensor_shape')
    for row, value in zip(rows, x):
        review.require(sha(value.tobytes()) == row['tensorSHA256'], 'tensor_membership')
    check_roles(rows)
    return doc, rows, x


def summaries(p, rows):
    y = np.array([r['changed'] for r in rows])
    masks = {role: [i for i,r in enumerate(rows) if r['role'] == role]
             for role in ('train', 'reserved', 'development')}
    for condition in ('original_capture', 'within_recipe', 'identity', 'artwork_contrast'):
        masks[condition] = [i for i,r in enumerate(rows) if condition in r['conditions']]
    for changed in (0, 1):
        masks['artwork_' + str(changed)] = [i for i,r in enumerate(rows)
            if 'artwork_contrast' in r['conditions'] and r['changed'] == changed]
    return {key:n.w.summary(p[ids], y[ids]) for key,ids in masks.items()}


def run(train):
    started = time.monotonic()
    torch = n.d.torch_runtime()
    torch.set_num_threads(2)
    doc, rows, x = load_inputs()
    prior = h.read(CONTROL / 'result.json')
    checkpoint = h.checked(h.ROOT, prior['model'])
    net = n.make_model(torch, paired_context=True)
    net.load_state_dict(torch.load(checkpoint, weights_only=True, map_location='cpu')['state'])
    net.eval()
    baseline_path = OUT / 'baseline.json'
    if not baseline_path.exists():
        tick = time.monotonic()
        p = n.score(net, torch.from_numpy(x))
        h.write(baseline_path, dict(model=h.ref(checkpoint), inputs=h.ref(OUT / 'inputs.json'),
            probabilities=p.tolist(), summary=summaries(p, rows), seconds=time.monotonic()-tick), sealed=True)
    baseline = h.read(baseline_path)
    review.require(baseline['seal'] == h.digest({k:v for k,v in baseline.items() if k != 'seal'})
                   and baseline['inputs'] == h.ref(OUT / 'inputs.json')
                   and baseline['model'] == h.ref(checkpoint), 'baseline_binding')
    print('baseline', baseline['summary'], flush=True)
    if not train:
        return
    output = OUT / 'candidate'
    review.require(not output.exists(), 'output_collision')
    review.require('DTM061' in (h.ROOT / 'Research/ExperimentLog.md').read_text(), 'unregistered')
    review.require(any(v['correct'] < v['count'] for k,v in baseline['summary'].items()
                       if k in ('reserved', 'development')), 'no_failure_to_repair')
    old_x, old_y, mask, _, _, _, _, _, replay, labels = n.inputs()
    control_protocol = h.read(CONTROL / 'protocol.json')
    review.require(sha(replay.tobytes()) == control_protocol['trainingSHA256']
                   and sha(labels.tobytes()) == control_protocol['labelsSHA256'], 'replay_changed')
    before = n.score(net, torch.from_numpy(replay))
    review.require(np.array_equal(before, np.array(prior['probabilities'], dtype=np.float32)), 'control_replay')
    train_ids = [i for i,r in enumerate(rows) if r['role'] == 'train']
    old_endpoints = {sha(v.tobytes()) for row in replay for v in (row[:3], row[3:])}
    review.require(not any(sha(v.tobytes()) in old_endpoints for i,row in enumerate(x)
                           if rows[i]['role'] != 'train' for v in (row[:3],row[3:])), 'replay_role_overlap')
    extra = x[train_ids]
    extra_y = np.array([rows[i]['changed'] for i in train_ids], dtype=np.float32)
    tx = np.concatenate([replay, extra, np.concatenate([extra[:,3:], extra[:,:3]], axis=1)])
    ty = np.concatenate([labels, extra_y, extra_y])
    output.mkdir()
    protocol = dict(experiment='DTM061', configuration=n.CONFIG, initializer=h.ref(checkpoint),
                    inputs=h.ref(OUT / 'inputs.json'), trainer=h.ref(n.__file__), source=h.ref(__file__),
                    replay=h.ref(CONTROL / 'protocol.json'), trainIDs=[rows[i]['id'] for i in train_ids],
                    trainingSHA256=sha(tx.tobytes()), labelsSHA256=sha(ty.tobytes()),
                    rows=len(tx), independentEvaluation=False, outputCapBytes=2*1024**3)
    h.write(output / 'protocol.json', protocol, sealed=True)
    tick = time.monotonic()
    net, history = n.fit(net, torch.from_numpy(tx), torch.from_numpy(ty), n.CONFIG,
                        lambda row:print('DTM061', row, flush=True))
    train_seconds = time.monotonic() - tick
    torch.save(dict(version='transition242-v1', state=net.state_dict(), protocol=h.ref(output/'protocol.json')),
               output/'last.pt')
    restored = n.make_model(torch, paired_context=True)
    restored.load_state_dict(torch.load(output/'last.pt', weights_only=True, map_location='cpu')['state'])
    restored.eval()
    tick = time.monotonic()
    candidate = n.score(restored, torch.from_numpy(x))
    review.require(np.array_equal(candidate, n.score(net, torch.from_numpy(x))), 'checkpoint_reload')
    after = n.score(restored, torch.from_numpy(replay))
    reverse = n.score(restored, torch.from_numpy(np.concatenate([replay[:,3:], replay[:,:3]], axis=1)))
    summary = summaries(candidate, rows)
    original = np.array(baseline['probabilities'], dtype=np.float32)
    truth = np.array([r['changed'] for r in rows])
    repaired = np.flatnonzero((decisions(original) != truth) & (decisions(candidate) == truth))
    lost = np.flatnonzero((decisions(original) == truth) & (decisions(candidate) != truth))
    replay_lost = int(((decisions(before) == labels) & (decisions(after) != labels)).sum())
    passed = (summary['reserved']['correct'] == baseline['summary']['reserved']['count'] and replay_lost == 0
              and summary['development']['correct'] > baseline['summary']['development']['correct']
              and summary['artwork_contrast']['correct'] >= baseline['summary']['artwork_contrast']['correct'])
    stress = {}
    for mode in ('global8', 'left8', 'center8'):
        values = n.nuisance.localized(old_x[207:], mask[207:], mode)
        q = n.score(restored, torch.from_numpy(values))
        stress[mode] = n.w.summary(q, np.zeros(len(q)))
    result = dict(experiment='DTM061', model=h.ref(output/'last.pt'), summary=summary,
                  probabilities=candidate.tolist(), repaired=[rows[i]['id'] for i in repaired],
                  lost=[rows[i]['id'] for i in lost], replay=n.w.summary(after, labels),
                  reversal=n.w.summary(reverse, labels), replayLost=replay_lost,
                  training=n.w.summary(n.score(net, torch.from_numpy(tx)), ty), history=history, stress=stress,
                  boundedRepairPassed=passed, productionEligible=False, independentEvaluation=False,
                  timings=dict(training=train_seconds, verification=time.monotonic()-tick,
                               total=time.monotonic()-started))
    h.write(output/'result.json', result, sealed=True)
    print({k:result[k] for k in ('summary','replay','reversal','replayLost','boundedRepairPassed','timings')}, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['prepare', 'baseline', 'train'])
    args = parser.parse_args()
    prepare() if args.mode == 'prepare' else run(args.mode == 'train')
