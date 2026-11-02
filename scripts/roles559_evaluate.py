"""ROLES559: score 41-class and role-trained detectors on the same 13 roles.

41-class outputs map to roles through `roles559.role`, then get per-role NMS (IoU 0.45), because 2 merged classes can predict the same box.
Development (no holdout): NewsTV development SDK cards (`cell`) and pills (`button`), and focused-control coverage (any role except `text`).
Synthetic: clean test images of tvos557 (whole-cell labels) and tvos558, with role labels from the sidecars (keys are buttons).
All models use the same PyTorch path (640 px, NMS IoU 0.45). No export, threshold change or promotion.
Rule B (--rule-b): truth drops `text` inside `button` boxes; each model is also scored with the same rule applied to its predictions (suffix `+B`).
Usage: roles559_evaluate.py --model NAME=CHECKPOINT ... --out NEW_JSON [--rule-b]
"""
import argparse
import contextlib
import io
import json
import statistics
from pathlib import Path
import research_queue as q
import cells558_evaluate as cells
from perception_benchmark import _iou
from roles559 import ROLES, role, sidecar_roles, without_button_text


def predict(weights, images, conf):
    from ultralytics import YOLO
    model = YOLO(str(weights)); names = model.names; mapped = set(names.values()) != set(ROLES)
    out = {}
    for start in range(0, len(images), 16):
        part = images[start:start+16]
        for path, res in zip(part, model.predict([str(p) for p in part], imgsz=640, conf=conf, iou=.45, verbose=False, device='mps')):
            dets = []
            for (x1, y1, x2, y2), c, s in zip(res.boxes.xyxy.tolist(), res.boxes.cls.tolist(), res.boxes.conf.tolist()):
                r = role(names[int(c)]) if mapped else names[int(c)]
                if r:
                    dets.append(dict(cls=r, box=[x1, y1, x2-x1, y2-y1], score=s))
            out[path] = nms(dets) if mapped else dets
    return out


def rule_b(preds):
    """Apply rule B to predictions: drop `text` predictions inside `button` predictions."""
    out = {}
    for path, dets in preds.items():
        kept = without_button_text(dict(enumerate(dets)))
        out[path] = [d for i, d in enumerate(dets) if i in kept]
    return out


def nms(dets):
    keep = []
    for d in sorted(dets, key=lambda d: -d['score']):
        if all(k['cls'] != d['cls'] or _iou(k['box'], d['box']) < .45 for k in keep):
            keep.append(d)
    return keep


def coco(images, truth, preds):
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval
    anns, dets = [], []
    for i, path in enumerate(images, 1):
        for t in truth[path]:
            anns.append(dict(id=len(anns)+1, image_id=i, category_id=ROLES.index(t['cls'])+1, bbox=t['box'], area=t['box'][2]*t['box'][3], iscrowd=0))
        for p in preds[path]:
            dets.append(dict(image_id=i, category_id=ROLES.index(p['cls'])+1, bbox=p['box'], score=p['score']))
    with contextlib.redirect_stdout(io.StringIO()):
        gt = COCO(); gt.dataset = dict(images=[dict(id=i) for i in range(1, len(images)+1)], annotations=anns,
                                       categories=[dict(id=i+1, name=n) for i, n in enumerate(ROLES)], info={}); gt.createIndex()
        ev = COCOeval(gt, gt.loadRes(dets), 'bbox'); ev.evaluate(); ev.accumulate(); ev.summarize()
    per = {}
    for name in sorted({t['cls'] for v in truth.values() for t in v}):
        prec = ev.eval['precision'][0, :, ROLES.index(name), 0, 2]  # IoU 0.5, all areas, 100 detections
        per[name] = float(prec[prec > -1].mean()) if (prec > -1).any() else None
    return dict(AP50=float(ev.stats[1]), AP75=float(ev.stats[2]), AP50_95=float(ev.stats[0]), perRoleAP50=per)


def development(weights, frames, focus):
    preds = predict(weights, [f['image'] for f in frames] + [f['image'] for f in focus], .5)
    cards, pills, ious = [0, 0], [0, 0], []
    for f in frames:
        dets = preds[f['image']]
        for ref in f['refs']:
            want = 'cell' if ref['kind'] == 'card' else 'button'
            best = max((_iou(ref['box'], d['box']) for d in dets if d['cls'] == want), default=0)
            if want == 'cell':
                ious.append(best); cards[1] += 1; cards[0] += best >= .5
            else:
                pills[1] += 1; pills[0] += best >= .5
    covered = sum(any(d['cls'] != 'text' and _iou(f['box'], d['box']) >= .5 for d in preds[f['image']]) for f in focus)
    # Box fit on focused NewsTV pills (reference: SDK frame). Best non-text IoU per frame, score >= 0.5.
    news = [max((_iou(f['box'], d['box']) for d in preds[f['image']] if d['cls'] != 'text'), default=0) for f in focus if f['id'].startswith('newstv')]
    matched = [v for v in ious if v >= .5]
    return dict(cardRecall=f'{cards[0]}/{cards[1]}', cardMedianIoU=round(statistics.median(ious), 3) if ious else None,
                cardMedianMatchedIoU=round(statistics.median(matched), 3) if matched else None,
                pillRecall=f'{pills[0]}/{pills[1]}', focusedCoverage=f'{covered}/{len(focus)}',
                newsFocusMedianIoU=round(statistics.median(news), 3) if news else None)


def build(models, out, button_text=True):
    frames, focus = cells.newstv_development(), cells.focus_frames()
    t557 = [q.ROOT/'dataset/tvos557/wholecell/test'/f'{n}.png' for n in q.load(q.ROOT/'reports/work/REALAPP557/ra557-13/test-unique.json')['images']]
    t558 = [q.ROOT/'dataset/tvos558/cells/test'/f'{n}.png' for n in q.load(q.ROOT/'reports/work/REALAPP557/cells558/test-unique.json')['images']]
    sets = {name: (images, {p: list(sidecar_roles(p.with_suffix('.json'), button_text).values()) for p in images})
            for name, images in (('tvos557WholeCell', t557), ('tvos558', t558))}
    result = dict(version='roles559-evaluation-v1', roles=ROLES, developmentFrames=len(frames), focusFrames=len(focus),
                  syntheticImages={k: len(v[0]) for k, v in sets.items()}, models={})
    result['ruleB'] = not button_text
    for name, weights in models.items():
        preds = {s: predict(weights, images, .001) for s, (images, _) in sets.items()}
        result['models'][name] = dict(checkpoint=dict(path=str(weights.relative_to(q.ROOT)), sha256=q.digest(weights)),
                                      development=development(weights, frames, focus),
                                      synthetic={s: coco(images, truth, preds[s]) for s, (images, truth) in sets.items()})
        if not button_text:
            result['models'][name + '+B'] = dict(result['models'][name], synthetic={s: coco(images, truth, rule_b(preds[s])) for s, (images, truth) in sets.items()})
    q.save(out, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--model', action='append', required=True, help='NAME=CHECKPOINT')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--rule-b', action='store_true', help='Score against truth without text inside buttons')
    args = parser.parse_args()
    r = build({m.split('=', 1)[0]: Path(m.split('=', 1)[1]).resolve() for m in args.model}, args.out, not args.rule_b)
    for name, m in r['models'].items():
        print(name, json.dumps(m['development']), {k: round(v['AP50'], 4) for k, v in m['synthetic'].items()})


if __name__ == '__main__':
    main()
