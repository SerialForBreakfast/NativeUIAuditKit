"""RA557-13: matched evaluation of the shipped tvOS v3 weights and the whole-cell fine-tune.

Both models run through the same PyTorch path (Ultralytics, 640 px, NMS IoU 0.45).
Synthetic: 323 pixel-unique test images, scored with new (whole-cell) and original (artwork) labels, COCO AP per class.
Real app: the 9 NewsTV pilot holdout screens, measured once for this candidate, with the REAL543 matching rules.
No model export, threshold change or promotion.
Usage: ra557_13_evaluate.py --candidate CHECKPOINT --out NEW_JSON
"""
import argparse
import contextlib
import io
import json
import statistics
from pathlib import Path
import research_queue as q
import real_app_benchmark543 as b
from perception_benchmark import _iou

BASELINE = q.ROOT/'NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.pt'
DATA = q.ROOT/'dataset/tvos557'
R = q.ROOT/'reports/work/REALAPP554'
NAMES = [c['name'] for c in sorted(q.load(q.ROOT/'Research/schemas/category_map.json')['categories'], key=lambda c: c['id'])]


def predict(weights, images, conf):
    from ultralytics import YOLO
    model = YOLO(str(weights))
    out = {}
    for start in range(0, len(images), 16):
        part = images[start:start+16]
        for path, res in zip(part, model.predict([str(p) for p in part], imgsz=640, conf=conf, iou=.45, verbose=False, device='mps')):
            boxes = res.boxes
            out[path] = [dict(cls=NAMES[int(c)], box=[float(x1), float(y1), float(x2-x1), float(y2-y1)], score=float(s))
                         for (x1, y1, x2, y2), c, s in zip(boxes.xyxy.tolist(), boxes.cls.tolist(), boxes.conf.tolist())]
    return out


def labels(sidecar):
    d = q.load(sidecar); out = []
    for e in d['elements']:
        if e['elementType'] not in NAMES:
            continue
        p = e['boundsPixels']; x, y = max(p['x'], 0), max(p['y'], 0)
        x2, y2 = min(p['x']+p['width'], 1920), min(p['y']+p['height'], 1080)
        if x2 > x and y2 > y:
            out.append(dict(cls=e['elementType'], box=[x, y, x2-x, y2-y]))
    return out


def coco(images, truth, preds):
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval
    anns, dets = [], []
    for i, path in enumerate(images, 1):
        for t in truth[path]:
            anns.append(dict(id=len(anns)+1, image_id=i, category_id=NAMES.index(t['cls'])+1, bbox=t['box'], area=t['box'][2]*t['box'][3], iscrowd=0))
        for p in preds[path]:
            dets.append(dict(image_id=i, category_id=NAMES.index(p['cls'])+1, bbox=p['box'], score=p['score']))
    with contextlib.redirect_stdout(io.StringIO()):
        gt = COCO(); gt.dataset = dict(images=[dict(id=i) for i in range(1, len(images)+1)], annotations=anns,
                                       categories=[dict(id=i+1, name=n) for i, n in enumerate(NAMES)], info={}); gt.createIndex()
        dt = gt.loadRes(dets)
        ev = COCOeval(gt, dt, 'bbox'); ev.evaluate(); ev.accumulate(); ev.summarize()
    present = sorted({t['cls'] for v in truth.values() for t in v})
    per = {}
    for name in present:
        k = NAMES.index(name)
        prec = ev.eval['precision'][0, :, k, 0, 2]  # IoU 0.5, all areas, 100 detections
        per[name] = float(prec[prec > -1].mean()) if (prec > -1).any() else None
    return dict(AP50=float(ev.stats[1]), AP75=float(ev.stats[2]), AP50_95=float(ev.stats[0]), perClassAP50=per)


def newstv(weights):
    manifest = q.load(R/'pilot-v2/manifest.json')
    cases = [c for c in manifest['cases'] if c['status'] == 'captured']
    images = [q.ROOT/c['image']['path'] for c in cases]
    preds = predict(weights, images, .5)
    rows, ious = [], []
    for case, path in zip(cases, images):
        label = q.load(q.ROOT/case['labels']['path'])
        dets = [{'class': p['cls'], 'box': p['box'], 'score': p['score']} for p in preds[path]]
        known, found, extra, wrong, loc = b.match(label, dets, .5)
        for o in known:
            if o['class'] == 'collectionItem':
                ious.append(max((_iou(o['box'], d['box']) for d in dets if d['class'] == o['class']), default=0))
        rows.append(dict(id=case['id'], status='ok', complete=label['complete'], unresolved=len(label['objects'])-len(known),
                         objects=known, allDetections=dets, found=found))
    per = {}
    for name in ('collectionItem', 'secondaryButton'):
        truth = sum(o['class'] == name for r in rows for o in r['objects'])
        per[name] = f"{sum(o['class'] == name and o['id'] in r['found'] for r in rows for o in r['objects'])}/{truth}"
    matched = [v for v in ious if v >= .5]
    return dict(recall=f"{sum(len(r['found']) for r in rows)}/{sum(len(r['objects']) for r in rows)}", perClass=per,
                cardMedianIoU=statistics.median(ious) if ious else None, cardMedianMatchedIoU=statistics.median(matched) if matched else None,
                cardIoUAtLeast075=sum(v >= .75 for v in ious), coco=b.official_ap(rows, manifest['classes']).get('metrics'))


def build(candidate, out):
    test = [DATA/'wholecell/test'/f'{n}.png' for n in q.load(q.ROOT/'reports/work/REALAPP557/ra557-13/test-unique.json')['images']]
    new = {p: labels(p.with_suffix('.json')) for p in test}
    old = {p: labels(DATA/'orig/test'/p.with_suffix('.json').name) for p in test}
    result = dict(version='ra557-13-evaluation-v1', testImages=len(test), candidate=dict(path=str(Path(candidate).relative_to(q.ROOT)), sha256=q.digest(candidate)),
                  baseline=dict(path=str(BASELINE.relative_to(q.ROOT)), sha256=q.digest(BASELINE)), models={})
    for name, weights in (('baseline', BASELINE), ('candidate', Path(candidate))):
        preds = predict(weights, test, .001)
        result['models'][name] = dict(syntheticNewLabels=coco(test, new, preds), syntheticOriginalLabels=coco(test, old, preds), newstvPilot=newstv(weights))
    q.save(out, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--candidate', type=Path, required=True); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    r = build(args.candidate.resolve(), args.out)
    for name, m in r['models'].items():
        print(name, 'new', round(m['syntheticNewLabels']['AP50'], 4), 'orig', round(m['syntheticOriginalLabels']['AP50'], 4),
              'newstv', m['newstvPilot']['recall'], m['newstvPilot']['perClass'], 'cardIoU', m['newstvPilot']['cardMedianIoU'], m['newstvPilot']['coco'])


if __name__ == '__main__':
    main()
