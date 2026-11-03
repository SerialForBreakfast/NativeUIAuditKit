"""PILLS560 R6: Core ML parity of a role detector against its PyTorch checkpoint.

Core ML runs as the Swift library does (`NativeUIDetectionRequest`): 640 × 640 letterbox (centered, gray 114), then the
pipeline with explicit `iouThreshold` 0.45 and `confidenceThreshold`. Ultralytics calls the pipeline without thresholds,
so it gets the export defaults (IoU 0.7, confidence 0.25); this script does not use that path.
1. Backend parity: both backends get the same 640 × 640 letterboxed pixels. Detections match by role and IoU >= 0.5
   (greedy, highest score first). Reports matched IoU, score differences and unmatched counts.
2. Development measures (`roles559_evaluate.development`) from PyTorch and from Core ML on the same frames. No promotion.
Run with .venv-coreml (coremltools). Usage: coreml_parity562.py --pt FINAL.pt --mlpackage FINAL.mlpackage --out NEW_JSON
"""
import argparse
import os
import statistics
from pathlib import Path
import research_queue as q

for k, v in {'YOLO_CONFIG_DIR': '.ultralytics', 'MPLCONFIGDIR': '.mplconfig', 'TORCH_HOME': '.torch'}.items():
    os.environ[k] = str(q.ROOT/'NativeUITrainer'/v); Path(os.environ[k]).mkdir(parents=True, exist_ok=True)

import roles559_evaluate as e
import cells558_evaluate as cells
from perception_benchmark import _iou

SIZE, FOLDER = 640, q.ROOT/'.build/debug-output/parity562'


def letterbox(path):
    """Square letterbox as in the Swift library. Returns the cached image path, scale and padding."""
    from PIL import Image
    im = Image.open(path).convert('RGB'); s = min(SIZE/im.width, SIZE/im.height)
    w, h = int(im.width*s), int(im.height*s); px, py = (SIZE-w)//2, (SIZE-h)//2
    FOLDER.mkdir(parents=True, exist_ok=True); dst = FOLDER/(q.digest(path)[:16] + '.png')
    if not dst.exists():
        canvas = Image.new('RGB', (SIZE, SIZE), (114, 114, 114)); canvas.paste(im.resize((w, h), Image.BILINEAR), (px, py)); canvas.save(dst)
    return dst, s, px, py


def coreml_predict(model, names, images, conf, original=True):
    """Core ML detections per image. Boxes in original-frame pixels, or in 640 × 640 pixels when `original` is False."""
    from PIL import Image
    out = {}
    for p in images:
        sq, s, px, py = letterbox(p) if original else (p, 1, 0, 0)
        y = model.predict({'image': Image.open(sq).convert('RGB'), 'iouThreshold': .45, 'confidenceThreshold': conf})
        dets = []
        for c, (cx, cy, w, h) in zip(y['confidence'], y['coordinates']):
            i = int(c.argmax()); x1, y1 = (cx - w/2)*SIZE, (cy - h/2)*SIZE
            dets.append(dict(cls=names[i], box=[float(v) for v in ((x1-px)/s, (y1-py)/s, w*SIZE/s, h*SIZE/s)], score=float(c[i])))
        out[p] = dets
    return out


def compare(a, b):
    """Match detections of 1 image; a and b are lists of dict(cls, box, score)."""
    used, pairs = set(), []
    for d in sorted(a, key=lambda d: -d['score']):
        best, j = 0, None
        for i, o in enumerate(b):
            if i not in used and o['cls'] == d['cls'] and _iou(d['box'], o['box']) > best:
                best, j = _iou(d['box'], o['box']), i
        if j is not None and best >= .5:
            used.add(j); pairs.append((best, abs(d['score'] - b[j]['score'])))
    return pairs, len(a) - len(pairs), len(b) - len(used)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--pt', type=Path, required=True); parser.add_argument('--mlpackage', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True); parser.add_argument('--synthetic', type=int, default=100)
    parser.add_argument('--conf', type=float, default=.25)
    args = parser.parse_args()
    import coremltools as ct
    from ultralytics import YOLO
    model = ct.models.MLModel(str(args.mlpackage)); names = YOLO(str(args.pt)).names
    frames, focus = cells.newstv_development(), cells.focus_frames()
    t558 = [q.ROOT/'dataset/tvos558/cells/test'/f'{n}.png' for n in q.load(q.ROOT/'reports/work/REALAPP557/cells558/test-unique.json')['images']]
    sets = {'development': sorted({f['image'] for f in frames} | {f['image'] for f in focus}), 'tvos558': t558[:args.synthetic]}
    result = dict(version='coreml-parity562-v3', pt=dict(path=str(args.pt), sha256=q.digest(args.pt)), mlpackage=str(args.mlpackage),
                  conf=args.conf, nmsIoU=.45, letterbox='640 square, centered, gray 114, PIL bilinear', sets={})
    for name, images in sets.items():
        square = [letterbox(p)[0] for p in images]  # Same pixels for both backends.
        pt, ml = e.predict(args.pt, square, args.conf), coreml_predict(model, names, square, args.conf, original=False)
        pairs, only_pt, only_ml = [], 0, 0
        for p in square:
            r = compare(pt[p], ml[p]); pairs += r[0]; only_pt += r[1]; only_ml += r[2]
        ious, diffs = [v for v, _ in pairs], [d for _, d in pairs]
        result['sets'][name] = dict(images=len(images), matched=len(pairs), onlyPyTorch=only_pt, onlyCoreML=only_ml,
                                    medianIoU=round(statistics.median(ious), 4), minIoU=round(min(ious), 4),
                                    medianScoreDiff=round(statistics.median(diffs), 4), maxScoreDiff=round(max(diffs), 4))
        print(name, result['sets'][name])
    result['pytorchDevelopment'] = e.development(args.pt, frames, focus)
    pytorch_predict = e.predict
    e.predict = lambda weights, images, conf: coreml_predict(model, names, images, conf)
    try:
        result['coremlDevelopment'] = e.development(args.mlpackage, frames, focus)
    finally:
        e.predict = pytorch_predict
    print('pytorch', result['pytorchDevelopment']); print('coreml', result['coremlDevelopment'])
    q.save(args.out, result)


if __name__ == '__main__':
    main()
