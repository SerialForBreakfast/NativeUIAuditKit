"""PILLS560: role AP50 on synthetic sets that do not depend on the tab-label convention.

tvos558NoTabBar: tvos558 clean test images without `tvOSTopTabBar` (old tab labels put the underline in the box and have no nested label).
tvos560Tabs: tvos560 test images of `tvOSTopTabBar` and `tvOSTabRows` (new labels).
Also reports `textField` recall and median score on PIN entry slots, the R2 loss (PILLS560 report).
Rule B (--rule-b): as in roles559_evaluate; models are also scored with rule B on predictions (suffix `+B`).
Usage: pills560_retention.py --model NAME=CHECKPOINT ... --out NEW_JSON [--rule-b]
"""
import argparse
import json
import statistics
from pathlib import Path
import research_queue as q
import roles559_evaluate as e
from roles559 import sidecar_roles
from perception_benchmark import _iou


def family(image):
    return q.load(image.with_suffix('.json'))['generatorProfile']['templateFamily']


def sets():
    t558 = [q.ROOT/'dataset/tvos558/cells/test'/f'{n}.png' for n in q.load(q.ROOT/'reports/work/REALAPP557/cells558/test-unique.json')['images']]
    t560 = [p for p in sorted((q.ROOT/'dataset/tvos560/pills/test').glob('*.png')) if family(p) in ('tvOSTopTabBar', 'tvOSTabRows')]
    return {'tvos558NoTabBar': [p for p in t558 if family(p) != 'tvOSTopTabBar'], 'tvos560Tabs': t560}


def pin_slots(weights, images):
    images = [p for p in images if family(p) == 'tvOSPINEntry']
    preds = e.predict(weights, images, .01); hits, scores, total = 0, [], 0
    for p in images:
        for t in sidecar_roles(p.with_suffix('.json')).values():
            if t['cls'] != 'textField':
                continue
            total += 1
            best = max((d['score'] for d in preds[p] if d['cls'] == 'textField' and _iou(t['box'], d['box']) >= .5), default=0)
            hits += best >= .25; scores.append(best)
    return dict(recallAt025=f'{hits}/{total}', medianScore=round(statistics.median(scores), 3) if scores else None)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--model', action='append', required=True, help='NAME=CHECKPOINT')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--rule-b', action='store_true', help='Score against truth without text inside buttons')
    args = parser.parse_args()
    models = {m.split('=', 1)[0]: Path(m.split('=', 1)[1]).resolve() for m in args.model}
    groups = sets(); keep = not args.rule_b
    result = dict(version='pills560-retention-v1', ruleB=args.rule_b, images={k: len(v) for k, v in groups.items()}, models={})
    for name, weights in models.items():
        m, mb = {}, {}
        for s, images in groups.items():
            truth = {p: list(sidecar_roles(p.with_suffix('.json'), keep).values()) for p in images}
            preds = e.predict(weights, images, .001)
            m[s] = e.coco(images, truth, preds)
            if args.rule_b:
                mb[s] = e.coco(images, truth, e.rule_b(preds))
        m['pinSlots'] = pin_slots(weights, groups['tvos558NoTabBar'])
        result['models'][name] = m
        if mb:
            result['models'][name + '+B'] = dict(mb, pinSlots=m['pinSlots'])
        for n, v in ((name, m), (name + '+B', mb)):
            if v:
                print(n, {s: round(v[s]['AP50'], 4) for s in groups}, 'textField', round(v['tvos558NoTabBar']['perRoleAP50'].get('textField') or 0, 3), m['pinSlots'])
    q.save(args.out, result)


if __name__ == '__main__':
    main()
