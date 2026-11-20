"""ARTPARITY595 step 2: frozen-model baseline on TTR's native-truth development frames.

Sources: the Studio Shelf matched pair (flat, brushed) and the 6 ArtworkEligibility-v1 frames (Field Atlas, Cinema Programme).
For each detector, every non-text proposal and every native truth box get a shipped FocusRing score through the production crop path
(`focus_runtime.invoke`, FocusRingClassifier.makeCrop, 16% expansion, 256 x 256). The runtime scores non-text proposals only.
Consumer rule (focusring-winner-takes-all-v1, observed in ac85177b receipts): exactly 1 scored proposal at >= 0.85 is selected; otherwise abstain.
Truth stays in the evaluator. No threshold is fit; results are provisional development evidence.
Usage: artparity595_baseline.py --out NEW_JSON [--model NAME=CHECKPOINT ...] [--conf 0.25]
"""
import argparse
import json
from pathlib import Path
import research_queue as q
import focus_runtime as fr
import roles559_evaluate as e
from perception_benchmark import _iou

FOCUS_MODEL = q.ROOT/'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc'
THRESHOLD = 0.85
SHELF = q.ROOT/'dataset/tvos_captures/artparity595/shelf-pair-v1'
ELIGIBILITY = q.ROOT/'dataset/tvos_captures/artparity595/eligibility-v1'  # Copied from TTR Docs/Research/ArtworkEligibility-v1 (hash-checked).
DEFAULT_MODELS = {'v3': q.ROOT/'NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.pt',
                  'r5': q.QUEUE/'jobs/pills560-platter-r5/attempts/1/out/final.pt'}


def shelf_frames():
    truth = q.load(SHELF/'truth.json'); out = []
    for f in truth['frames']:
        boxes = {'focused:' + f['before']['elementID']: f['before']['frame'], 'competitor:' + f['copper']['elementID']: f['copper']['frame'],
                 'clipped:' + f['edge']['elementID']: f['edge']['frame']}
        out.append(dict(id='shelf-' + f['material'], path=SHELF/f['image'], sha256=f['sha256'], focus='artwork', focused='focused:' + f['before']['elementID'], boxes=boxes))
    return out


def eligibility_frames():
    root = ELIGIBILITY; out = []
    for i, c in enumerate(q.load(root/'comparison.json')):
        folder = root/f"{c['layout']}-{i % 3}"
        key = 'control-' + c['native_id'].rsplit('.', 1)[1]
        boxes = {('focused:' if k == key else ('decor:' if k == 'decor' else 'other:')) + k: v for k, v in c['native_boxes'].items()}
        out.append(dict(id=f"eligibility-{c['layout']}-{i % 3}", path=folder/'source.png', sha256=c['sha256'], focus=c['focus'],
                        focused='focused:' + key, boxes=boxes, ttrBaseline=c['baseline'], ttrExpanded=c['expanded']))
    return out


def visible(box, width=1920, height=1080):
    """Clip a box to the image. FocusRingTool rejects bounds outside the image; a clipped tile keeps its visible part only."""
    x, y = max(box[0], 0), max(box[1], 0)
    return [float(x), float(y), float(min(box[0]+box[2], width) - x), float(min(box[1]+box[3], height) - y)]


def score(items):
    out = {}
    for batch in fr.bounded_batches(items, shared_images=True):
        for r in fr.invoke(batch, FOCUS_MODEL)['results']:
            out[r['id']] = r
    return out


def probability(result):
    for key in ('probability', 'focusProbability', 'score', 'focused'):
        if isinstance(result.get(key), (int, float)):
            return float(result[key])
    raise ValueError('unknown_runtime_result:' + ','.join(sorted(result)))


def evaluate(frames, models, conf):
    for f in frames:
        q.require(q.digest(f['path']) == f['sha256'], 'artparity595_image_hash:' + f['id'])
    preds = {name: e.predict(w, [f['path'] for f in frames], conf) for name, w in models.items()}
    items = []
    for f in frames:
        for k, b in f['boxes'].items():
            items.append(dict(id=f"{f['id']}|truth|{k}", path=str(f['path']), sha256=f['sha256'], bounds=visible(b)))
        for name in models:
            for j, d in enumerate(preds[name][f['path']]):
                if d['cls'] != 'text':
                    items.append(dict(id=f"{f['id']}|{name}|{j}", path=str(f['path']), sha256=f['sha256'], bounds=visible(d['box'])))
    scores = {k: probability(v) for k, v in score(items).items()}
    report = []
    for f in frames:
        focus_box = f['boxes'][f['focused']]
        row = dict(id=f['id'], focus=f['focus'], suppliedCrops={k: round(scores[f"{f['id']}|truth|{k}"], 4) for k in f['boxes']}, models={})
        for opt in ('ttrBaseline', 'ttrExpanded'):
            if opt in f:
                row[opt] = f[opt]
        for name in models:
            dets = preds[name][f['path']]
            scored = [(scores[f"{f['id']}|{name}|{j}"], d) for j, d in enumerate(dets) if d['cls'] != 'text']
            high = [(s, d) for s, d in scored if s >= THRESHOLD]
            selected = high[0][1] if len(high) == 1 else None
            if selected is None:
                outcome = 'abstain_none' if not high else 'abstain_multiple'
            else:
                hit = {k: _iou(selected['box'], b) for k, b in f['boxes'].items()}
                best = max(hit, key=hit.get)
                outcome = 'correct' if best == f['focused'] and hit[best] >= .5 else ('wrong_decor' if best.startswith('decor') and hit[best] >= .5 else 'wrong_selection')
            row['models'][name] = dict(
                outcome=outcome, aboveThreshold=len(high),
                proposalAtTruth={k: max(((round(_iou(d['box'], b), 3), d['cls']) for d in dets), default=(0, None)) for k, b in f['boxes'].items()},
                bestScoredOnFocused=round(max((s for s, d in scored if _iou(d['box'], focus_box) >= .5), default=0), 4),
                decorAboveThreshold=sum(1 for s, d in high for k, b in f['boxes'].items() if k.startswith('decor') and _iou(d['box'], b) >= .5))
        report.append(row)
    summary = {name: dict(correct=sum(r['models'][name]['outcome'] == 'correct' for r in report), frames=len(report),
                          wrong=sum(r['models'][name]['outcome'].startswith('wrong') for r in report),
                          abstain=sum(r['models'][name]['outcome'].startswith('abstain') for r in report)) for name in models}
    return dict(version='artparity595-baseline-v1', threshold=THRESHOLD, detectorConf=conf, cropBounds='clipped to the 1920 x 1080 image (visible part only)', focusModel=dict(path=str(FOCUS_MODEL.relative_to(q.ROOT))),
                models={n: dict(path=str(Path(w).relative_to(q.ROOT)), sha256=q.digest(w)) for n, w in models.items()},
                summary=summary, frames=report, status='provisional development evidence; no threshold fit; not reviewed by Joe')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--model', action='append', help='NAME=CHECKPOINT (default: v3 and r5)')
    parser.add_argument('--conf', type=float, default=.25)
    args = parser.parse_args()
    models = {m.split('=', 1)[0]: Path(m.split('=', 1)[1]).resolve() for m in args.model} if args.model else DEFAULT_MODELS
    result = evaluate(shelf_frames() + eligibility_frames(), models, args.conf)
    q.save(args.out, result)
    print(json.dumps(result['summary']))
    for r in result['frames']:
        print(r['id'], r['focus'], {n: m['outcome'] for n, m in r['models'].items()}, r['suppliedCrops'])


if __name__ == '__main__':
    main()
