"""RESET604 T2.5: production-path Q-packet importer check (`tvos-framework-projection-v1`).

Path under test, for every frame in a packet:
  sidecar -> ttr_detector_ingest604.ingest_framework_frame -> detector_training419.prepare
  -> Ultralytics YOLODataset tensor -> decoded class names and screenshot pixels
  -> compared with the hand-written answer key and the reference geometry.

Packet layout (`manifest.json`):
  {"schema": "tvos-qpacket-v1", "frames": [{"frame_id", "sidecar", "image", "key", "reference_geometry",
    "expected": "accept" | {"reject": "<check>"}, "label_mutation": null | "class_index_shift"}]}
Each corrupted twin must fail with its named check. A generic failure does not count.
`--synthetic` builds a packet from the NUIAK keys with drawn images, M1-M9 twins and a frame-identity twin,
so the importer is proven before TTR delivers real frames.
"""
import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path

import detector_training419 as t
import framework_projection604 as fp
import research_queue as q
import ttr_detector_ingest604 as ingest

KEYS = q.ROOT / 'reports/work/RESET604/contract/keys'
RELEASE_EDGE_PX, RELEASE_IOU, SMALL_SIDE_PX = 1.78, 0.9722, 48
FOCUSABLE = {'UIButton', 'Button', 'Link', 'Menu', 'UIAlertAction', 'UICollectionViewCell', 'UICollectionViewListCell',
             'UITableViewCell', 'ListRow', 'UITextField', 'TextField', 'SecureField', 'Toggle', 'UITabBarItem', 'Segment'}
# Named checks that each mutation must trigger (TTR manifest r5 names, mapped to NUIAK checks).
MUTATIONS = {
    'M1': ('synopsis line relabelled as a button', {'answer_key.roles'}),
    'M2': ('visible target removed from export', {'answer_key.counts'}),
    'M3': ('duplicate child label', {'answer_key.relationships'}),
    'M4': ('focus id from the previous frame', {'answer_key.focus'}),
    'M5': ('pre-scroll coordinates', {'geometry'}),
    'M6': ('underlay control visible through an opaque overlay', {'answer_key.roles'}),
    'M7': ('box shifted just beyond release tolerance', {'geometry'}),
    'M8': ('class index shifted by 1 in the label file', {'tensor.class'}),
    'M9': ('class claim without matching framework facts', {'importer.framework_facts_missing'}),
    'M10': ('valid screenshot with the previous frame sidecar', {'importer.frame_identity_mismatch'}),
}


# ---------- checks ----------

def geometry_in_tolerance(reference_box, iou, edge):
    """Apply the contract's source-pixel limits after projection or tensor decoding."""
    small = min(reference_box[2:]) < SMALL_SIDE_PX
    return edge <= RELEASE_EDGE_PX and (small or iou >= RELEASE_IOU)


def _iou_edge(a, b):
    ax0, ay0, aw, ah = a; bx0, by0, bw, bh = b
    ax1, ay1, bx1, by1 = ax0 + aw, ay0 + ah, bx0 + bw, by0 + bh
    iw, ih = max(0, min(ax1, bx1) - max(ax0, bx0)), max(0, min(ay1, by1) - max(ay0, by0))
    inter = iw * ih
    iou = inter / (aw * ah + bw * bh - inter) if inter else 0.0
    edge = max(abs(ax0 - bx0), abs(ay0 - by0), abs(ax1 - bx1), abs(ay1 - by1))
    return iou, edge


def check_key(proj, key, focus_stop=None):
    """Compare 1 projected frame with its key. Returns a list of failed check names with detail."""
    fails = []
    exp = {o['id']: o['expected'] for o in key['objects']}
    got = {o['id']: o for o in proj['objects']}
    seen = [o['id'] for o in proj['objects']]
    if len(seen) != len(set(seen)):
        fails.append('answer_key.relationships:duplicate_object_id')
    for oid, o in got.items():
        e = exp.get(oid)
        if e is None:
            if o['disposition'] == 'target':
                fails.append(f'answer_key.roles:unexpected_target:{oid}')
            continue
        if o['disposition'] != e['disposition'] or o['class'] != e.get('class'):
            fails.append(f"answer_key.roles:{oid}:{o['disposition']}/{o['class']}!={e['disposition']}/{e.get('class')}")
        k_parent = next((k.get('parent_id') for k in key['objects'] if k['id'] == oid), None)
        if o['parent_id'] != k_parent:
            fails.append(f'answer_key.relationships:parent:{oid}')
    for oid, e in exp.items():
        if oid not in got and e['disposition'] == 'target':
            fails.append(f'answer_key.counts:missing_target:{oid}')
    if focus_stop is not None:
        want = focus_stop['native_focus']
        if proj['focus_state'] != want['state'] or proj['focus_id'] != want.get('id'):
            fails.append(f"answer_key.focus:{proj['focus_state']}/{proj['focus_id']}!={want['state']}/{want.get('id')}")
    return fails


def check_geometry(row, reference):
    """Compare importer boxes with independent reference geometry (TTR mask, or the clean synthetic frame)."""
    fails = []
    boxes = {c['objectId']: c['bounds'] for c in row['controls']}
    for oid, ref in reference.items():
        box = boxes.get(oid)
        if box is None:
            continue
        iou, edge = _iou_edge(box, ref)
        if not geometry_in_tolerance(ref, iou, edge):
            fails.append(f'geometry:{oid}:edge={edge:.2f}:iou={iou:.4f}')
    return fails


def decode_tensors(dataset_yaml, names):
    """Load the written dataset with the training loader and decode tensors to classes and screenshot pixels."""
    import yaml
    from ultralytics.data import YOLODataset
    cfg = yaml.safe_load(Path(dataset_yaml).read_text())
    img_dir = Path(cfg['path']) / cfg['train']
    ds = YOLODataset(img_path=str(img_dir), data={'names': dict(enumerate(names)), 'nc': len(names), 'channels': 3},
                     task='detect', imgsz=640, augment=False, rect=False, cache=False, batch_size=1)
    out = {}
    for i in range(len(ds)):
        item = ds[i]
        (ry, rx), (px, py) = item['ratio_pad']  # Ultralytics: ratio = (height, width), pad = (left, top)
        H, W = item['img'].shape[1:]
        boxes = []
        for cls, (cx, cy, bw, bh) in zip(item['cls'].view(-1).tolist(), item['bboxes'].tolist()):
            x0 = (cx * W - bw * W / 2 - px) / rx; y0 = (cy * H - bh * H / 2 - py) / ry
            boxes.append(dict(cls=names[int(cls)], box=[x0, y0, bw * W / rx, bh * H / ry]))
        out[Path(item['im_file']).stem] = boxes
    return out


def check_tensor(row, decoded):
    """Every importer control must come back from the loader tensor with its class and box (<= 1 px)."""
    from scipy.optimize import linear_sum_assignment

    got = decoded.get(row['id'], [])
    want = row['controls']
    if len(got) != len(want):
        return [f'tensor.count:{len(got)}!={len(want)}']
    if not want:
        return []

    # Prefer the maximum number of valid pairs. Among failed pairs, align
    # coincident boxes first so a changed class reports the named class failure.
    penalty = len(want) + 1
    costs = []
    for target in want:
        row_costs = []
        for box in got:
            within = _iou_edge(box['box'], target['bounds'])[1] <= 1.0
            valid = within and box['cls'] == target['class']
            row_costs.append(0 if valid else penalty + int(not within))
        costs.append(row_costs)

    targets, boxes = linear_sum_assignment(costs)
    fails = []
    for target_index, box_index in zip(targets, boxes):
        w, g = want[target_index], got[box_index]
        if g['cls'] != w['class']:
            fails.append(f"tensor.class:{w['objectId']}:{g['cls']}!={w['class']}")
        if _iou_edge(g['box'], w['bounds'])[1] > 1.0:
            fails.append(f"tensor.geometry:{w['objectId']}")
    return fails


# ---------- runner ----------

def run_packet(packet_dir, work_dir):
    packet_dir, work_dir = Path(packet_dir), Path(work_dir)
    manifest = q.load(packet_dir / 'manifest.json')
    q.require(manifest.get('schema') == 'tvos-qpacket-v1', 'qpacket_schema')
    names = fp.tvos_classes()
    results, rows = [], []
    for f in manifest['frames']:
        key = q.load(packet_dir / f['key'])
        side = q.load(packet_dir / f['sidecar'])
        focus_stop = f.get('focus_stop') or next((s for s in key.get('focus_stops', []) if s['native_focus'].get('id') == (side.get('expected_focus_id') or '')), None)
        row, proj = ingest.ingest_framework_frame(packet_dir / f['sidecar'], packet_dir / f['image'], group=f['frame_id'], row_id=f['frame_id'])
        fails = [f'importer.{r.split(":")[0]}' + (':' + r.split(':', 1)[1] if ':' in r else '') for r in proj['reasons']]
        fails += check_key(proj, key, focus_stop)
        if row is not None:
            fails += check_geometry(row, {k: v for k, v in (f.get('reference_geometry') or {}).items()})
        results.append(dict(frame=f, row=row, fails=fails))
        if row is not None:
            rows.append((f, row))
    # Write each importer-accepted row with the production dataset writer, then read it with the training loader.
    # 1 frame per dataset: a twin can share pixels with its clean frame, which the writer correctly refuses to mix.
    decoded = {}
    for f, row in rows:
        out = work_dir / 'prepare' / f['frame_id']
        if out.exists():
            shutil.rmtree(out)
        doc = dict(version=t.TRAIN_ONLY_VERSION, trainingAdmitted=True, calibrationPolicy='none-fixed-last-training-diagnostics',
                   names=names, rows=[row])
        yaml_path, _ = t.prepare(doc, out)
        if f.get('label_mutation') == 'class_index_shift':
            lab = out / 'dataset/labels/train' / (row['id'] + '.txt')
            lines = [ln.split() for ln in lab.read_text().splitlines()]
            lab.write_text(''.join(f"{(int(p[0]) + 1) % len(names)} {' '.join(p[1:])}\n" for p in lines))
        decoded.update(decode_tensors(yaml_path, names))
    report = []
    for r in results:
        fails = list(r['fails'])
        if r['row'] is not None:
            fails += check_tensor(r['row'], decoded)
        exp = r['frame']['expected']
        checks = {x.split(':')[0] for x in fails}
        if exp == 'accept':
            ok = not fails
        else:
            want = set(exp['reject']) if isinstance(exp['reject'], list) else {exp['reject']}
            ok = bool(checks & want)
        report.append(dict(frame_id=r['frame']['frame_id'], mutation=r['frame'].get('mutation'), expected=exp,
                           outcome='accepted' if not fails else 'rejected', checks=sorted(checks), fails=fails, passed=ok))
    summary = dict(schema='tvos-qpacket-result-v1', mapping_version=fp.load_contract()[0]['mapping_version'],
                   contract_sha256=fp.load_contract()[1], frames=len(report), passed=sum(r['passed'] for r in report),
                   clean_accepted=sum(r['expected'] == 'accept' and r['outcome'] == 'accepted' for r in report),
                   twins_rejected_for_named_reason=sum(r['expected'] != 'accept' and r['passed'] for r in report), results=report)
    q.save(work_dir / 'qpacket-result.json', summary, replace=True)
    return summary


# ---------- synthetic packet ----------

def _layout(key):
    """Deterministic boxes: targets on a row; owned objects inside their parent; others on a lower row."""
    boxes, x = {}, 80
    for o in key['objects']:
        if o.get('parent_id') is None:
            boxes[o['id']] = [x, 120, x + 300, 200] if o['expected']['disposition'] == 'target' else [x, 600, x + 280, 650]
            x += 330 if x < 1500 else -1400
    for o in key['objects']:
        p = o.get('parent_id')
        if p is not None:
            px0, py0, px1, py1 = boxes[p]
            boxes[o['id']] = [px0 + 10, py0 + 10, px1 - 10, py0 + 40]
    return boxes


def _sidecar(key, frame_id, png_sha, boxes, focus_id):
    objects = []
    for o in key['objects']:
        c = dict(o['construction'], instance_id=o['id'], source='synthetic-key')
        objects.append(dict(id=o['id'], construction=c, parent_id=o.get('parent_id'), owner_relation=o.get('owner_relation'),
                            observation=dict(instance_id=o['id'], uikit_class='synthetic', visible_bounds_px=boxes[o['id']],
                                             focusable=c['primitive'] in FOCUSABLE, scene_revision=frame_id, screenshot_sha256=png_sha)))
    focus = dict(state='focused', id=focus_id, source='native_focus_observation') if focus_id else dict(state='unknown')
    return dict(schema=ingest.FRAME_SCHEMA, frame_id=frame_id, scene_revision=frame_id, screenshot_sha256=png_sha,
                width=1920, height=1080, family=key['case'], focus=focus, expected_focus_id=focus_id, objects=objects)


def build_synthetic(out_dir, keys=('q1-office-details', 'q5-button-classes')):
    """Write a synthetic packet: 1 clean frame per key plus twins M1-M10 on Q1 (M8 uses Q5)."""
    from PIL import Image, ImageDraw
    out_dir = Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / 'keys').mkdir(parents=True)
    frames, clean = [], {}

    def png(name, boxes, tone):
        im = Image.new('RGB', (1920, 1080), (30, 30, 30 + tone)); d = ImageDraw.Draw(im)
        for b in boxes.values():
            d.rectangle([b[0], b[1], b[2] - 1, b[3] - 1], outline=(200, 200, 200))
        p = out_dir / f'{name}.png'; im.save(p)
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def add(frame_id, key_name, side, image, ref, expected, mutation=None, label_mutation=None):
        q.save(out_dir / f'{frame_id}.json', side)
        frames.append(dict(frame_id=frame_id, sidecar=f'{frame_id}.json', image=image, key=f'keys/{key_name}.json',
                           reference_geometry=ref, expected=expected, mutation=mutation, label_mutation=label_mutation))

    for i, name in enumerate(keys):
        key = q.load(KEYS / f'{name}.json'); shutil.copy2(KEYS / f'{name}.json', out_dir / 'keys' / f'{name}.json')
        boxes = _layout(key)
        focus_id = key['focus_stops'][0]['native_focus']['id']
        fid = f'clean-{name}'
        sha = png(fid, boxes, i * 20)
        side = _sidecar(key, fid, sha, boxes, focus_id)
        ref = {o['id']: [b[0], b[1], b[2] - b[0], b[3] - b[1]] for o, b in ((o, boxes[o['id']]) for o in key['objects'])}
        add(fid, name, side, f'{fid}.png', ref, 'accept')
        clean[name] = (key, boxes, side, ref, fid)

    key, boxes, side, ref, fid = clean['q1-office-details']

    def twin(mid, mutate, key_name='q1-office-details', label_mutation=None, image=None):
        k, b, s, r, cf = clean[key_name]
        tw = copy.deepcopy(s); mutate(tw)
        tid = f'twin-{mid.lower()}'
        if image is None:
            shutil.copy2(out_dir / f'{cf}.png', out_dir / f'{tid}.png'); image = f'{tid}.png'
        add(tid, key_name, tw, image, r, {'reject': sorted(MUTATIONS[mid][1])}, mutation=mid, label_mutation=label_mutation)

    def by_id(s, oid):
        return next(o for o in s['objects'] if o['id'] == oid)

    def m1(s):
        by_id(s, 'synopsis_line_0')['construction'].update(primitive='UIButton', style='bordered', style_source='applied_instance', framework='UIKit')
        by_id(s, 'synopsis_line_0')['observation']['focusable'] = True
    twin('M1', m1)
    twin('M2', lambda s: s['objects'].remove(by_id(s, 'action_watchlist')))

    def m3(s):
        s['objects'].append(copy.deepcopy(by_id(s, 'hero_title')))
    twin('M3', m3)

    def m4(s):
        s['focus'] = dict(state='focused', id='action_watchlist', source='native_focus_observation')
    twin('M4', m4)

    def m5(s):
        for o in s['objects']:
            b = o['observation']['visible_bounds_px']; o['observation']['visible_bounds_px'] = [b[0] - 120, b[1], b[2] - 120, b[3]]
    twin('M5', m5)

    def m6(s):
        s['objects'].append(dict(id='underlay_card', construction=dict(framework='UIKit', primitive='UICollectionViewCell', instance_id='underlay_card', source='synthetic-key'),
                                 parent_id=None, owner_relation=None,
                                 observation=dict(instance_id='underlay_card', uikit_class='synthetic', visible_bounds_px=[80, 800, 380, 1000],
                                                  focusable=True, scene_revision=s['scene_revision'], screenshot_sha256=s['screenshot_sha256'])))
    twin('M6', m6)

    def m7(s):
        b = by_id(s, 'action_watch')['observation']['visible_bounds_px']; by_id(s, 'action_watch')['observation']['visible_bounds_px'] = [b[0] + 2, b[1], b[2] + 2, b[3]]
    twin('M7', m7)
    twin('M8', lambda s: None, key_name='q5-button-classes', label_mutation='class_index_shift')

    def m9(s):
        o = by_id(s, 'action_watchlist'); o['construction'] = None; o['declared_class'] = 'button'
    twin('M9', m9)
    # M10: the clean Q5 screenshot paired with the Q1 sidecar (a different frame).
    twin('M10', lambda s: None, image=f"{clean['q5-button-classes'][4]}.png")
    q.save(out_dir / 'manifest.json', dict(schema='tvos-qpacket-v1', source='synthetic from NUIAK keys', frames=frames))
    return out_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--packet', type=Path)
    parser.add_argument('--synthetic', action='store_true', help='Build and run the synthetic packet from the NUIAK keys')
    parser.add_argument('--work', type=Path, default=q.ROOT / '.build/debug-output/qpacket604')
    args = parser.parse_args()
    packet = build_synthetic(args.work / 'packet') if args.synthetic else args.packet
    q.require(packet is not None, 'qpacket_missing_packet')
    summary = run_packet(packet, args.work)
    print(json.dumps({k: v for k, v in summary.items() if k != 'results'}, indent=2))
    for r in summary['results']:
        print(('PASS' if r['passed'] else 'FAIL'), r['frame_id'], r['mutation'] or '', r['outcome'], ','.join(r['checks']))


if __name__ == '__main__':
    main()
