"""T50: add resident Vision rectangle proposals to cached tvOS detector predictions, then match both arms per object.

The baseline arm is the stored production scorecard. The candidate arm adds VNDetectRectanglesRequest boxes
from the compiled scripts/vision_annotation_probe.swift tool with its fixed settings. Rectangles have no class,
so matching is class-agnostic in both arms. Frames, labels, and detector predictions stay fixed. No model is accepted.
"""
import json
import subprocess
import time
from pathlib import Path

import research_queue as q
from template_inputs398 import checked
from template_adapters395 import document, resolve_inputs

OUT = None
PROPOSALS = ('none', 'rectangles')
SLICES = ('class', 'position', 'screen', 'state')
# The probe accepts at most 40 frames per call.
CHUNK = 40
FRAME_LIMIT = 64
CLASS = 'visionRectangle'


def parameters(value):
    """Return (proposals, slice) or raise. 'none' is the control arm and must reproduce the stored scorecard."""
    q.require(isinstance(value, dict) and set(value) == {'proposals', 'slice'}, 'proposal_parameters')
    q.require(value['proposals'] in PROPOSALS, 'proposal_source')
    q.require(value['slice'] in SLICES, 'proposal_slice')
    return value['proposals'], value['slice']


def rectangles(tool, frames, stage):
    """Run the probe on verified frame copies inside the project. Return 1 list of [x, y, w, h] boxes with scores per frame."""
    from detector_inference412 import frame_path, staged
    found = []
    for start in range(0, len(frames), CHUNK):
        chunk = frames[start:start + CHUNK]
        items = []
        for i, frame in enumerate(chunk):
            path = staged(frame_path(frame['image']), stage)
            items.append(dict(id=str(start + i), path=str(path), sha256=frame['sha256']))
        request = dict(version=1, root=str(q.ROOT), frames=items, rectanglesOnly=True)
        proc = subprocess.run([str(tool)], input=json.dumps(request), cwd=q.ROOT, capture_output=True, text=True, timeout=300)
        q.require(proc.returncode == 0, 'probe_failed:' + proc.stderr[-300:])
        (OUT / 'raw' / ('rectangles-%03d.json' % start)).write_text(proc.stdout)
        receipt = json.loads(proc.stdout)
        q.require([r['id'] for r in receipt['results']] == [i['id'] for i in items], 'probe_membership')
        for result, item in zip(receipt['results'], items):
            q.require(result['sha256'] == item['sha256'] and not result['errors'], 'probe_result')
            found.append([dict(bounds=p['bounds'], confidence=p['confidence']) for p in result['rectangles']])
    return found


def run():
    from detector_case_match411 import load_bundle, evaluate, summarize
    cfg = q.load(OUT.parents[2] / 'spec.json')['template']
    source, kind = parameters(cfg['parameters'])
    refs = resolve_inputs(cfg, OUT)
    labels = document(refs['labels'])
    frames = labels['frames']
    q.require(0 < len(frames) <= FRAME_LIMIT, 'frame_count')
    card = document(refs['baseline'])
    pins = lambda ref: {k: ref[k] for k in ('path', 'sha256')}
    q.require(card['inputs'] == pins(refs['labels']), 'baseline_labels_changed')
    raws = [document(ref) for ref in card['rawPredictions']]
    q.require(len(raws) == len(frames), 'baseline_membership')
    (OUT / 'raw').mkdir()
    start = time.monotonic()
    added = [[] for _ in frames]
    if source == 'rectangles':
        stage = q.ROOT / '.build/debug-output/vision415' / OUT.parents[2].name
        added = rectangles(checked(refs['tool']), frames, stage)
        for path in stage.glob('*'):
            path.unlink()
    seconds = time.monotonic() - start
    paths = []
    for i, (raw, extra) in enumerate(zip(raws, added)):
        elements = list(raw['runtime']['result']['elements']) + [
            dict(elementType=CLASS, confidence=p['confidence'],
                 boundingBoxPixels=dict(x=p['bounds'][0], y=p['bounds'][1], width=p['bounds'][2], height=p['bounds'][3]))
            for p in extra]
        path = OUT / 'raw' / ('%03d.json' % i)
        q.save(path, dict(status='success', inputSHA256=raw['inputSHA256'], width=raw['width'], height=raw['height'],
                          coordinates='boundingBoxPixels: pixels top-left',
                          runtime=dict(detector=dict(card['identity']['detector'], proposals=source),
                                       result=dict(elements=elements))))
        paths.append(path)
    q.save(OUT / 'scorecard.json', dict(version='real-model-scorecard-v1', partition='development', trainingEligible=False,
        inputs=pins(refs['labels']), rawPredictions=[dict(path=q.relative(p), sha256=q.digest(p)) for p in paths],
        frames=[f['sha256'] for f in frames],
        identity=dict(detector=dict(card['identity']['detector'], proposals=source, tool=pins(refs['tool'])))))
    # Detector boxes were stored at confidence 0.50. Probe rectangles have confidence 0.50 or more.
    bundle = dict(version='detector-case-inputs-v1', role='development', platform='tvOS', format='real-model-scorecard-v1',
                  confidence=0.5, labelReview='reviewed',
                  baseline=pins(refs['baseline']),
                  candidate=dict(path=q.relative(OUT / 'scorecard.json'), sha256=q.digest(OUT / 'scorecard.json')),
                  labels=pins(refs['labels']))
    images, predictions, meta = load_bundle(bundle)
    settings = (kind, None, {}, 'class-agnostic')
    rows, unmatched = evaluate(images, predictions, settings, bundle['confidence'])
    report = summarize(rows, unmatched, settings, meta)
    if source == 'none':
        # The control arm must reproduce the stored predictions exactly.
        q.require(not report['gains'] and not report['lostPriorSuccesses'], 'control_changed')
    report.update(proposals=source, proposalSeconds=seconds, frames=len(frames),
                  addedProposals=sum(len(a) for a in added),
                  addedUnmatched=sum(1 for u in unmatched if u['model'] == 'candidate' and u['predictedClass'] == CLASS),
                  limitation='Class-agnostic matching only: rectangles carry no class. Unmatched boxes are not reviewed '
                             'false positives. Reviewed development frames only. No model is accepted.')
    q.save(OUT / 'benchmark_summary.json', report)
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=name, sha256=q.digest(OUT / name)) for name in ('benchmark_summary.json', 'scorecard.json')]))
