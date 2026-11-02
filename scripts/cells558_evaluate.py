"""CELLS558 S6: compare the tvOS v3 baseline with C1 and C2 on development and synthetic sets.

Development (no holdout): NewsTV development frames with SDK rectangles (cards, main tabs, categories),
and focused-control coverage on the 21 focus development frames. The NewsTV pilot holdout is not read.
Synthetic retention: clean test images from tvos557 (original and whole-cell labels) and tvos558 (new generator labels).
All models use the same PyTorch path (640 px, NMS IoU 0.45). No export, threshold change or promotion.
Usage: cells558_evaluate.py --model NAME=CHECKPOINT ... --out NEW_JSON
"""
import argparse
import json
import statistics
from pathlib import Path
import research_queue as q
import ra557_13_evaluate as ev
from perception_benchmark import _iou

R = q.ROOT/'reports/work/REALAPP554'
BUTTONS = {'primaryButton', 'secondaryButton'}
PILL = ('category.', 'main-tab.')


def newstv_development():
    """SDK rectangles of the 10 NewsTV development frames, in 4K pixels."""
    frames = []
    for case in q.load(R/'capture-newstv-dev/session.json')['cases']:
        if case['status'] != 'captured':
            continue
        refs = []
        for sdk_id, bounds, _ in case['sdkBefore']['elements']:
            b = json.loads(bounds)
            kind = 'card' if sdk_id.startswith('article.') else ('pill' if sdk_id.startswith(PILL) else None)
            if kind:
                refs.append(dict(kind=kind, id=sdk_id, box=[b['x']*2, b['y']*2, b['width']*2, b['height']*2]))
        frames.append(dict(id=case['id'], image=Path(case['image']), refs=refs))
    return frames


def focus_frames():
    out = []
    for path in (R/'capture-newstv-dev/session.json', R/'capture-photo-dev/session.json'):
        for case in q.load(path)['cases']:
            label = q.load(R/'review-dev/labels'/f"{case['id']}.json")
            if case['status'] == 'captured' and label['focus']['state'] == 'focused':
                out.append(dict(id=case['id'], image=Path(case['image']), box=label['focus']['box']))
    return out


def development(weights, frames, focus):
    preds = ev.predict(weights, [f['image'] for f in frames] + [f['image'] for f in focus], .5)
    cards, pills, card_ious, pill_classes = [0, 0], [0, 0], [], {}
    for f in frames:
        dets = preds[f['image']]
        for ref in f['refs']:
            if ref['kind'] == 'card':
                best = max((_iou(ref['box'], d['box']) for d in dets if d['cls'] == 'collectionItem'), default=0)
                card_ious.append(best); cards[1] += 1; cards[0] += best >= .5
            else:
                hit = [d for d in dets if d['cls'] in BUTTONS and _iou(ref['box'], d['box']) >= .5]
                pills[1] += 1; pills[0] += bool(hit)
                for d in hit[:1]:
                    pill_classes[d['cls']] = pill_classes.get(d['cls'], 0) + 1
    covered = sum(any(d['cls'] != 'label' and _iou(f['box'], d['box']) >= .5 for d in preds[f['image']]) for f in focus)
    matched = [v for v in card_ious if v >= .5]
    return dict(cardRecall=f'{cards[0]}/{cards[1]}', cardMedianIoU=round(statistics.median(card_ious), 3) if card_ious else None,
                cardMedianMatchedIoU=round(statistics.median(matched), 3) if matched else None,
                pillRecallButtonClasses=f'{pills[0]}/{pills[1]}', pillClasses=pill_classes,
                focusedCoverage=f'{covered}/{len(focus)}')


def synthetic(weights, sets):
    out = {}
    for name, (images, labels) in sets.items():
        out[name] = ev.coco(images, labels, ev.predict(weights, images, .001))
    return out


def build(models, out):
    frames, focus = newstv_development(), focus_frames()
    t557 = [q.ROOT/'dataset/tvos557/wholecell/test'/f'{n}.png' for n in q.load(q.ROOT/'reports/work/REALAPP557/ra557-13/test-unique.json')['images']]
    t558 = [q.ROOT/'dataset/tvos558/cells/test'/f'{n}.png' for n in q.load(q.ROOT/'reports/work/REALAPP557/cells558/test-unique.json')['images']]
    sets = {'tvos557Original': (t557, {p: ev.labels(q.ROOT/'dataset/tvos557/orig/test'/p.with_suffix('.json').name) for p in t557}),
            'tvos557WholeCell': (t557, {p: ev.labels(p.with_suffix('.json')) for p in t557}),
            'tvos558': (t558, {p: ev.labels(p.with_suffix('.json')) for p in t558})}
    result = dict(version='cells558-evaluation-v1', developmentFrames=len(frames), focusFrames=len(focus),
                  syntheticImages={k: len(v[0]) for k, v in sets.items()}, models={})
    for name, weights in models.items():
        result['models'][name] = dict(checkpoint=dict(path=str(weights.relative_to(q.ROOT)), sha256=q.digest(weights)),
                                      development=development(weights, frames, focus), synthetic=synthetic(weights, sets))
    base = result['models'].get('baseline')
    if base:
        for name, m in result['models'].items():
            losses = {}
            for s, metrics in m['synthetic'].items():
                ref = base['synthetic'][s]['perClassAP50']
                deltas = {k: v - ref[k] for k, v in metrics['perClassAP50'].items() if v is not None and ref.get(k) is not None}
                worst = min(deltas, key=deltas.get) if deltas else None
                losses[s] = dict(worstClass=worst, worstDelta=round(deltas[worst], 3) if worst else None,
                                 labelDelta=round(deltas.get('label', 0), 3))
            m['retention'] = losses
    q.save(out, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--model', action='append', required=True, help='NAME=CHECKPOINT')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    models = {m.split('=', 1)[0]: Path(m.split('=', 1)[1]).resolve() for m in args.model}
    r = build(models, args.out)
    for name, m in r['models'].items():
        print(name, json.dumps(m['development']), json.dumps(m.get('retention')),
              {k: round(v['AP50'], 4) for k, v in m['synthetic'].items()})


if __name__ == '__main__':
    main()
