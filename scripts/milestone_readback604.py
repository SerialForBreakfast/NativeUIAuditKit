"""RESET604 R604-17: NUIAK loader readback for TTR milestone packets (`tvos-framework-projection-v1` + TTR A1).

For every clean frame: production importer (`ingest_framework_frame`) -> dataset writer (`detector_training419.prepare`)
-> Ultralytics `YOLODataset` (LetterBox 640, no augmentation) -> `collate_fn` batch -> inverse transform to source pixels.
Every value is keyed by sidecar SHA-256 and loader-configuration SHA-256.

Also:
- per-object agreement between the NUIAK projection and the producer's embedded `ttr_projection`;
- 2 derived crops (NUIAK-side, recorded provenance): 1 removes the focused object, 1 leaves a target 1 pixel wide;
- twins M1-M10 built from a real clean frame and checked through `qpacket_import604.run_packet`.
Read-only for the packets. Output: reports/work/RESET604/milestone-readback-v1/.
"""
import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path

import detector_training419 as t
import framework_projection604 as fp
import qpacket_import604 as qp
import research_queue as q
import ttr_detector_ingest604 as ingest

PACKETS = (
    q.ROOT / 'reports/work/RESET604/ttr-milestone-v1/tvtestrig-reset604-milestone-navconsumer-20261112-v1',
    q.ROOT / 'reports/work/RESET604/ttr-milestone-v1/tvtestrig-reset604-milestone-presses-20261112-v1',
)
SIDECAR = 'frame.tvos-framework-frame-v1.json'
GROUP = 'ttr-navconsumer-catalog'


def loader_config():
    import ultralytics
    cfg = dict(loader='ultralytics.data.YOLODataset', ultralytics=ultralytics.__version__, task='detect', imgsz=640, augment=False,
               rect=False, cache=False, transform='LetterBox(640, center, pad 114) + Format(xywh normalized)', batch='collate_fn, all frames',
               names=fp.tvos_classes(), writer='detector_training419.prepare (TRAIN_ONLY_VERSION)', importer='ttr_detector_ingest604.ingest_framework_frame')
    return cfg, hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()


def frames_of(packet):
    for d in sorted((Path(packet) / 'frames').iterdir()):
        if (d / SIDECAR).is_file():
            yield f'{Path(packet).name.split("-milestone-")[1].split("-2026")[0]}-{d.name}', d


def compare_with_producer(side, proj):
    """Per-object agreement with the producer's embedded projection (independent implementation)."""
    theirs = {o['id']: o for o in (side.get('ttr_projection') or {}).get('objects') or []}
    rows = []
    for o in proj['objects']:
        t_ = theirs.get(o['id'])
        same = t_ is not None and (t_.get('disposition'), t_.get('class'), t_.get('rule_id'), t_.get('reason')) == (o['disposition'], o['class'], o['rule_id'], o['reason'])
        if not same:
            rows.append(dict(id=o['id'], nuiak=(o['disposition'], o['class'], o['rule_id'], o['reason']),
                             ttr=None if t_ is None else (t_.get('disposition'), t_.get('class'), t_.get('rule_id'), t_.get('reason'))))
    missing = sorted(set(theirs) - {o['id'] for o in proj['objects']})
    return dict(objects=len(proj['objects']), disagreements=rows, producer_only=missing, agree=not rows and not missing)


def decode_batch(dataset_yaml, names):
    """Read the written dataset with the training loader, batch it with collate_fn, invert to source pixels."""
    import yaml
    from ultralytics.data import YOLODataset
    cfg = yaml.safe_load(Path(dataset_yaml).read_text())
    ds = YOLODataset(img_path=str(Path(cfg['path']) / cfg['train']), data={'names': dict(enumerate(names)), 'nc': len(names), 'channels': 3},
                     task='detect', imgsz=640, augment=False, rect=False, cache=False, batch_size=1)
    items = [ds[i] for i in range(len(ds))]
    batch = ds.collate_fn(items)
    out = {}
    for i, item in enumerate(items):
        (ry, rx), (px, py) = item['ratio_pad']  # Ultralytics: ratio = (height, width), pad = (left, top)
        H, W = batch['img'].shape[2:]
        sel = batch['batch_idx'] == i
        boxes = []
        for cls, (cx, cy, bw, bh) in zip(batch['cls'][sel].view(-1).tolist(), batch['bboxes'][sel].tolist()):
            x0 = (cx * W - bw * W / 2 - px) / rx; y0 = (cy * H - bh * H / 2 - py) / ry
            boxes.append(dict(cls=names[int(cls)], box_src_px=[round(x0, 3), round(y0, 3), round(bw * W / rx, 3), round(bh * H / ry, 3)],
                              box_loader_norm=[round(v, 6) for v in (cx, cy, bw, bh)]))
        out[Path(item['im_file']).stem] = dict(boxes=boxes, ori_shape=list(item['ori_shape']), resized_shape=list(item['resized_shape']),
                                               ratio_pad_h_w_left_top=[[ry, rx], [px, py]], batch_shape=list(batch['img'].shape))
    return out


def readback(entries, work, names, cfg_sha):
    """entries: list of (frame_key, sidecar_path, image_path). Returns per-frame readback records."""
    rows, recs = [], {}
    for key, side_path, img_path in entries:
        side = q.load(side_path)
        row, proj = ingest.ingest_framework_frame(side_path, img_path, group=GROUP, row_id=key)
        recs[key] = dict(sidecar=str(Path(side_path).resolve().relative_to(q.ROOT)), sidecar_sha256=q.digest(side_path), image_sha256=q.digest(img_path),
                         loader_config_sha256=cfg_sha, eligible=row is not None, frame_reasons=proj['reasons'],
                         producer_agreement=compare_with_producer(side, proj),
                         focus=dict(state=proj['focus_state'], object_id=proj['focus_id'],
                                    training_effect='not a detector class; row field only; unknown focus never encodes no focus'),
                         no_box=[dict(id=o['id'], disposition=o['disposition'], reason=o['reason'], rule_id=o['rule_id'], parent_id=o['parent_id'],
                                      training_effect='background pixels (no box, no ignore mask)' if o['disposition'] != 'unresolved' else 'frame excluded')
                                 for o in proj['objects'] if o['disposition'] != 'target'],
                         importer_targets=[dict(id=x['objectId'], cls=x['class'], box_src_px=x['bounds'], rule_id=x['ruleId']) for x in (row or {}).get('controls', [])])
        if row is not None:
            rows.append(row)
    out = work / 'prepare'
    if out.exists():
        shutil.rmtree(out)
    doc = dict(version=t.TRAIN_ONLY_VERSION, trainingAdmitted=True, calibrationPolicy='none-fixed-last-training-diagnostics', names=names, rows=rows)
    yaml_path, counts = t.prepare(doc, out)
    decoded = decode_batch(yaml_path, names)
    first_by_sha = {}
    for r in rows:
        first_by_sha.setdefault(r['image']['sha256'], r['id'])
    for key, rec in recs.items():
        if not rec['eligible']:
            continue
        stem = first_by_sha[rec['image_sha256']]
        d = decoded.get(stem, dict(boxes=[]))
        rec['dataset_image'] = stem if stem == key else f'deduplicated to {stem} (identical pixels and labels)'
        rec['loader'] = {k: v for k, v in d.items() if k != 'boxes'}
        matched, errs = [], []
        pool = list(d['boxes'])
        for tgt in rec['importer_targets']:
            best = max(pool, key=lambda b: qp._iou_edge(b['box_src_px'], tgt['box_src_px'])[0], default=None)
            if best is None:
                errs.append(f"missing_in_tensor:{tgt['id']}"); continue
            pool.remove(best)
            iou, edge = qp._iou_edge(best['box_src_px'], tgt['box_src_px'])
            if not qp.geometry_in_tolerance(tgt['box_src_px'], iou, edge):
                errs.append(f"geometry:{tgt['id']}:edge={edge:.4f}:iou={iou:.6f}")
            if best['cls'] != tgt['cls']:
                errs.append(f"class:{tgt['id']}")
            matched.append(dict(tgt, decoded_cls=best['cls'], decoded_box_src_px=best['box_src_px'], box_loader_norm=best['box_loader_norm'],
                                roundtrip_edge_px=round(edge, 4), roundtrip_iou=round(iou, 6)))
        errs += [f"extra_in_tensor:{b['cls']}" for b in pool]
        rec['decoded_targets'] = matched
        rec['roundtrip_errors'] = errs
        rec['max_roundtrip_edge_px'] = max((m['roundtrip_edge_px'] for m in matched), default=0.0)
    return recs, counts


# ---------- derived crops (NUIAK-side augmentation with recorded provenance) ----------

def crop_frame(side_path, img_path, rect, out_dir, name):
    """Crop a canonical TTR frame to rect [x0, y0, x1, y1] (source pixels). Objects outside the crop are not visible
    and leave the frame; clipped objects keep their clipped body. A cropped-out focus owner makes focus `unknown`."""
    from PIL import Image
    side = copy.deepcopy(q.load(side_path))
    x0, y0, x1, y1 = rect
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / f'{name}.png'
    with Image.open(img_path) as im:
        im.crop((x0, y0, x1, y1)).save(png)
    sha = q.digest(png)
    rev = side['frame']['scene_revision'] + f':crop:{x0},{y0},{x1},{y1}'
    kept, dropped = [], []
    for item in side['objects']:
        ob = item['object']
        b = ob['observation']['visible_bounds_px']
        nb = [max(b[0], x0) - x0, max(b[1], y0) - y0, min(b[2], x1) - x0, min(b[3], y1) - y0]
        if nb[2] <= nb[0] or nb[3] <= nb[1]:
            dropped.append(ob['id']); continue
        ob['observation'].update(visible_bounds_px=nb, scene_revision=rev, screenshot_sha256=sha)
        kept.append(item)
    kept_ids = {i['object']['id'] for i in kept}
    for item in kept:
        if item['object'].get('parent_id') not in (None, *kept_ids):
            item['object']['parent_id'] = None; item['object']['owner_relation'] = None
    side['objects'] = kept
    side['frame'].update(png_width=x1 - x0, png_height=y1 - y0, scene_revision=rev, screenshot_sha256=sha)
    focus = side.get('focus') or {}
    if focus.get('object_id') in dropped:
        side['focus'] = dict(state='unknown', object_id=None, scene_revision=rev, screenshot_sha256=sha, reason='focus_owner_outside_crop')
    else:
        side['focus'] = dict(focus, scene_revision=rev, screenshot_sha256=sha)
    side.pop('ttr_projection', None)
    side['derived'] = dict(by='Maximum-mini-NUIAK milestone_readback604.crop_frame', source_sidecar_sha256=q.digest(side_path), crop_px=rect, dropped_objects=dropped)
    sp = out_dir / f'{name}.json'
    q.save(sp, side, replace=True)
    return sp, png, dropped


def crop_cases(packet, out_dir):
    side_path = Path(packet) / 'frames/list_start' / SIDECAR
    img = Path(packet) / 'frames/list_start/frame.png'
    side = q.load(side_path)
    W, H = side['frame']['png_width'], side['frame']['png_height']
    objs = {i['object']['id']: i['object'] for i in side['objects']}
    focus_box = objs[side['focus']['object_id']]['observation']['visible_bounds_px']
    a = crop_frame(side_path, img, [focus_box[2], 0, W, H], out_dir, 'crop-without-focused-object')
    cells = sorted((o for o in objs.values() if o['construction']['primitive'] == 'UICollectionViewCell' and o['id'] != side['focus']['object_id']),
                   key=lambda o: o['observation']['visible_bounds_px'][0])
    victim = cells[1]['observation']['visible_bounds_px']
    b = crop_frame(side_path, img, [victim[2] - 1, 0, W, H], out_dir, 'crop-one-pixel-box')
    return [('crop-without-focused-object', a[0], a[1]), ('crop-one-pixel-box', b[0], b[1])], dict(one_pixel_cell=cells[1]['id'])


# ---------- twins from a real clean frame ----------

def build_twins(packet, other_frame, out_dir):
    """M1-M10 on the real list_start frame, as a tvos-qpacket-v1 packet. Key = clean NUIAK projection, which is
    checked against TTR's independent projection first (agreement required)."""
    src = Path(packet) / 'frames/list_start'
    side0 = q.load(src / SIDECAR)
    flat, _ = ingest.normalize_framework_frame(side0)
    proj = fp.project_frame(flat)
    out_dir = Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / 'keys').mkdir(parents=True)
    key = dict(schema='tvos-framework-key-v1', case='navconsumer-list_start',
               authored_from='NUIAK projection of the clean frame; agrees object by object with TTR embedded projection',
               objects=[dict(id=o['id'], parent_id=o['parent_id'], expected=dict(disposition=o['disposition'], **({'class': o['class']} if o['class'] else {})))
                        for o in proj['objects']])
    q.save(out_dir / 'keys/list_start.json', key)
    ref = {o['id']: o['box'] for o in proj['targets']}
    stop = dict(native_focus=dict(state='focused', id=proj['focus_id']))
    shutil.copy2(src / 'frame.png', out_dir / 'clean.png')
    frames = [dict(frame_id='navconsumer-clean', sidecar='clean.json', image='clean.png', key='keys/list_start.json', reference_geometry=ref,
                   expected='accept', mutation=None, focus_stop=stop)]
    q.save(out_dir / 'clean.json', side0)

    def objs(s):
        return {i['object']['id']: i for i in s['objects']}
    unowned_label = next(o['id'] for o in proj['objects'] if o['rule_id'] == 'text.static' and o['parent_id'] is None)
    cells = [o['id'] for o in proj['targets'] if o['class'] == 'cell']
    owned = next(o['id'] for o in proj['objects'] if o['disposition'] == 'owned_metadata')

    def m1(s):
        ob = objs(s)[unowned_label]['object']; ob['construction'].update(primitive='UIButton', style='bordered', style_source='applied_instance'); ob['observation']['focusable'] = True
    def m2(s):
        s['objects'] = [i for i in s['objects'] if i['object']['id'] != cells[1] and i['object'].get('parent_id') != cells[1]]
    def m3(s):
        s['objects'].append(copy.deepcopy(objs(s)[owned]))
    def m4(s):
        s['focus']['object_id'] = cells[2]
    def m5(s):
        for i in s['objects']:
            b = i['object']['observation']['visible_bounds_px']
            i['object']['observation']['visible_bounds_px'] = [max(b[0] - 600, 0), b[1], max(b[2] - 600, 1), b[3]]
    def m6(s):
        base = copy.deepcopy(objs(s)[cells[0]]); ob = base['object']; ob['id'] = ob['construction']['instance_id'] = ob['observation']['instance_id'] = 'underlay.cell'
        ob['observation']['visible_bounds_px'] = [100, 100, 400, 400]; s['objects'].append(base)
    def m7(s):
        b = objs(s)[cells[0]]['object']['observation']['visible_bounds_px']; objs(s)[cells[0]]['object']['observation']['visible_bounds_px'] = [b[0] + 2, b[1], b[2] + 2, b[3]]
    def m9(s):
        objs(s)[cells[0]]['object']['construction'] = None
    muts = dict(M1=m1, M2=m2, M3=m3, M4=m4, M5=m5, M6=m6, M7=m7, M8=lambda s: None, M9=m9, M10=lambda s: None)
    for mid, fn in muts.items():
        tw = copy.deepcopy(side0); fn(tw); tw.pop('ttr_projection', None)
        tid = f'twin-{mid.lower()}'
        q.save(out_dir / f'{tid}.json', tw)
        image = f'{tid}.png'
        shutil.copy2(other_frame if mid == 'M10' else src / 'frame.png', out_dir / image)
        frames.append(dict(frame_id=f'navconsumer-{tid}', sidecar=f'{tid}.json', image=image, key='keys/list_start.json', reference_geometry=ref,
                           expected={'reject': sorted(qp.MUTATIONS[mid][1])}, mutation=mid, focus_stop=stop,
                           label_mutation='class_index_shift' if mid == 'M8' else None))
    q.save(out_dir / 'manifest.json', dict(schema='tvos-qpacket-v1', source='twins from TTR navconsumer list_start', frames=frames))
    return out_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, default=q.ROOT / 'reports/work/RESET604/milestone-readback-v1')
    parser.add_argument('--work', type=Path, default=q.ROOT / '.build/debug-output/milestone604')
    args = parser.parse_args()
    names = fp.tvos_classes()
    cfg, cfg_sha = loader_config()
    entries = [(k, d / SIDECAR, d / 'frame.png') for p in PACKETS for k, d in frames_of(p)]
    recs, counts = readback(entries, args.work / 'clean', names, cfg_sha)
    crops, crop_info = crop_cases(PACKETS[0], args.work / 'crops')
    crop_recs, _ = readback(crops, args.work / 'crop', names, cfg_sha)
    twin_packet = build_twins(PACKETS[0], PACKETS[0] / 'frames/scrolled/frame.png', args.work / 'twins')
    twins = qp.run_packet(twin_packet, args.work / 'twins-run')
    contract, digest = fp.load_contract()
    summary = dict(
        schema='nuiak-milestone-readback-v1', contract=contract['contract'], mapping_version=contract['mapping_version'], table_sha256=digest,
        loader_config=cfg, loader_config_sha256=cfg_sha, written_counts=counts,
        clean=dict(frames=len(recs), eligible=sum(r['eligible'] for r in recs.values()),
                   producer_agreement=sum(r['producer_agreement']['agree'] for r in recs.values()),
                   targets=sum(len(r.get('decoded_targets', [])) for r in recs.values()),
                   roundtrip_errors=sum(len(r.get('roundtrip_errors', [])) for r in recs.values()),
                   max_roundtrip_edge_px=max(r.get('max_roundtrip_edge_px', 0) for r in recs.values())),
        crops=dict(info=crop_info, frames=crop_recs),
        twins={k: v for k, v in twins.items() if k != 'results'} | dict(results=[{k: r[k] for k in ('frame_id', 'mutation', 'outcome', 'checks', 'passed')} for r in twins['results']]),
        frames=recs)
    args.out.mkdir(parents=True, exist_ok=True)
    q.save(args.out / 'milestone-readback-v1.json', summary, replace=True)
    print(json.dumps(dict(clean=summary['clean'], twins={k: summary['twins'][k] for k in ('frames', 'passed', 'clean_accepted', 'twins_rejected_for_named_reason')}), indent=2))
    for k, r in recs.items():
        print(k, 'eligible' if r['eligible'] else 'REJECTED', 'agree' if r['producer_agreement']['agree'] else 'DISAGREE', len(r.get('decoded_targets', [])), r.get('roundtrip_errors'), r['frame_reasons'][:3])
    for k, r in crop_recs.items():
        print(k, r['eligible'], r['focus'], [(d['id'], d['box_src_px'], d['decoded_box_src_px']) for d in r.get('decoded_targets', []) if d['box_src_px'][2] <= 2], r['frame_reasons'][:4])
    for r in summary['twins']['results']:
        print('PASS' if r['passed'] else 'FAIL', r['frame_id'], r['outcome'], r['checks'])


if __name__ == '__main__':
    main()
