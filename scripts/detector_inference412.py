"""T43: run pinned detector weights on pinned reviewed frames, then compare with a pinned baseline scorecard.

engine 'production' runs the package CLI with its bundled Core ML model. Only the minimum confidence changes.
engine 'pytorch' runs the source YOLO weights through ultralytics. Confidence and input size can change.
The comparison reuses T42 matching. Frames, labels, and weights stay fixed. No model is accepted.
"""
import os
import shutil
import subprocess
import time
from pathlib import Path

import research_queue as q
from template_inputs398 import checked
from template_adapters395 import document, resolve_inputs

OUT = None
ENGINES = ('production', 'pytorch')
SIZES = (640, 960, 1280)
SLICES = ('class', 'position', 'screen')
# Storage migration (STORAGE-LIVE-01) moved some reviewed frames to this archive. Hashes are always verified.
ARCHIVE = Path('/Volumes/training-drive/data/NUIAK/live')
# Ultralytics Core ML export default for the baked NMS. The production control arm checks the match.
NMS_IOU = 0.45
FRAME_LIMIT = 64


def parameters(value):
    """Return (engine, confidence, image size, slice) or raise."""
    q.require(isinstance(value, dict) and set(value) == {'engine', 'confidence', 'imageSize', 'slice'}, 'inference_parameters')
    engine, confidence, size, kind = value['engine'], value['confidence'], value['imageSize'], value['slice']
    q.require(engine in ENGINES, 'inference_engine')
    q.require(type(confidence) in (int, float) and .01 <= confidence <= .95, 'inference_confidence')
    # The bundled Core ML model has a fixed input size. Only the source weights can change it.
    q.require(size is None if engine == 'production' else size in SIZES, 'inference_image_size')
    q.require(kind in SLICES, 'inference_slice')
    return engine, float(confidence), size, kind


def frame_path(ref):
    """Return the verified local path of 1 reviewed frame."""
    path = q.local_path(q.ROOT, ref['path'])
    if not path.is_file():
        path = ARCHIVE / ref['path']
    q.require(path.is_file() and q.digest(path) == ref['sha256'], 'frame_missing_or_changed:' + ref['path'])
    return path


def staged(path, folder):
    """The CLI refuses inputs outside its root. Copy an archived frame into the root and verify the copy."""
    if path.is_relative_to(q.ROOT):
        return path
    folder.mkdir(parents=True, exist_ok=True)
    copy = folder / path.name
    shutil.copyfile(path, copy)
    q.require(q.digest(copy) == q.digest(path), 'staged_frame_changed')
    return copy


def production(binary, frames, confidence, raw):
    docs = []
    env = {**os.environ, 'TMPDIR': str(q.ROOT / '.build/debug-output/focus-launch/tmp')}
    Path(env['TMPDIR']).mkdir(parents=True, exist_ok=True)
    stage = q.ROOT / '.build/debug-output/inference412' / OUT.parents[2].name
    for i, frame in enumerate(frames):
        path = staged(frame_path(frame['image']), stage)
        command = [str(binary), 'scan', str(path), '--platform', 'tvOS',
                   '--min-confidence', repr(confidence), '--no-ocr', '--strict', '--root', str(q.ROOT)]
        proc = subprocess.run(command, cwd=q.ROOT, capture_output=True, text=True, timeout=90, env=env)
        if path.parent == stage:
            path.unlink()
        q.require(proc.returncode == 0, 'production_scan_failed:%d' % i)
        (raw / ('%03d.json' % i)).write_text(proc.stdout)
        doc = q.load(raw / ('%03d.json' % i))
        q.require(doc['status'] == 'success' and doc['inputSHA256'] == frame['sha256'], 'production_scan_identity')
        q.require(doc['configuration']['minConfidence'] == confidence and doc['configuration']['ocr'] is False,
                  'production_configuration')
        docs.append(doc)
    return docs[0]['runtime']['detector'] if docs else None


def pytorch(weights, frames, confidence, size, raw):
    from PIL import Image
    from ultralytics import YOLO
    model = YOLO(str(weights))
    identity = dict(engine='pytorch', weightsSHA256=q.digest(weights), imageSize=size, nmsIoU=NMS_IOU)
    for i, frame in enumerate(frames):
        path = frame_path(frame['image'])
        with Image.open(path) as image:
            width, height = image.size
        result = model.predict(str(path), imgsz=size, conf=confidence, iou=NMS_IOU, device='mps', verbose=False)[0]
        elements = []
        for (x1, y1, x2, y2), score, cls in zip(result.boxes.xyxy.tolist(), result.boxes.conf.tolist(),
                                                 result.boxes.cls.tolist()):
            elements.append(dict(elementType=result.names[int(cls)], confidence=float(score),
                                 boundingBoxPixels=dict(x=x1, y=y1, width=x2 - x1, height=y2 - y1)))
        q.save(raw / ('%03d.json' % i), dict(status='success', inputSHA256=frame['sha256'], width=width, height=height,
            coordinates='boundingBoxPixels: pixels top-left', configuration=dict(minConfidence=confidence, imageSize=size),
            runtime=dict(detector=identity, result=dict(elements=elements))))
    return identity


def run():
    from detector_case_match411 import load_bundle, evaluate, summarize
    cfg = q.load(OUT.parents[2] / 'spec.json')['template']
    engine, confidence, size, kind = parameters(cfg['parameters'])
    refs = resolve_inputs(cfg, OUT)
    labels = document(refs['labels'])
    frames = labels['frames']
    q.require(0 < len(frames) <= FRAME_LIMIT, 'frame_count')
    baseline = document(refs['baseline'])
    q.require(baseline['inputs'] == {k: refs['labels'][k] for k in ('path', 'sha256')}, 'baseline_labels_changed')
    raw = OUT / 'raw'
    raw.mkdir()
    start = time.monotonic()
    if engine == 'production':
        identity = production(checked(refs['model']), frames, confidence, raw)
        # The bundled model must be the baseline model. A rebuilt CLI is allowed; a changed model is not.
        q.require(identity['treeSHA256'] == baseline['identity']['detector']['treeSHA256'], 'production_model_changed')
    else:
        identity = pytorch(checked(refs['model']), frames, confidence, size, raw)
    seconds = time.monotonic() - start
    raws = [raw / ('%03d.json' % i) for i in range(len(frames))]
    q.save(OUT / 'scorecard.json', dict(version='real-model-scorecard-v1', partition='development',
        trainingEligible=False, inputs={k: refs['labels'][k] for k in ('path', 'sha256')},
        rawPredictions=[dict(path=q.relative(p), sha256=q.digest(p)) for p in raws],
        frames=[f['sha256'] for f in frames], identity=dict(detector=identity)))
    bundle = dict(version='detector-case-inputs-v1', role='development', platform='tvOS', format='real-model-scorecard-v1',
                  confidence=confidence, labelReview='reviewed',
                  baseline={k: refs['baseline'][k] for k in ('path', 'sha256')},
                  candidate=dict(path=q.relative(OUT / 'scorecard.json'), sha256=q.digest(OUT / 'scorecard.json')),
                  labels={k: refs['labels'][k] for k in ('path', 'sha256')})
    images, predictions, meta = load_bundle(bundle)
    rows, unmatched = evaluate(images, predictions, (kind, None, {}, 'class-aware'), confidence)
    report = summarize(rows, unmatched, (kind, None, {}, 'class-aware'), meta)
    report.update(engine=engine, imageSize=size, inferenceSeconds=seconds, frames=len(frames),
                  limitation='Baseline is the stored production scorecard at confidence 0.50. Unmatched boxes are not '
                             'reviewed false positives. Reviewed development frames only. No model is accepted.')
    q.save(OUT / 'benchmark_summary.json', report)
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=name, sha256=q.digest(OUT / name)) for name in ('benchmark_summary.json', 'scorecard.json')]))
