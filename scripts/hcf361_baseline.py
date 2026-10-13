"""Score retained reported-HCF crops with existing models. Do not admit training data."""
import base64
import math
import os
import time
from pathlib import Path
import research_queue as q
import focus_runtime
from eval_focus_ring_detector import predict_torch

OUT = None


def summarize(rows, scores, threshold=.85):
    q.require(len(rows) == len(scores) and rows, 'incomplete_predictions')
    q.require(all(type(s) in (float, int) and math.isfinite(s) and 0 <= s <= 1 for s in scores), 'invalid_probability')
    q.require(len({r['id'] for r in rows}) == len(rows), 'duplicate_prediction')
    q.require(all(type(r['label']) is int and r['label'] in (0, 1) for r in rows), 'invalid_label')
    results = [dict(id=r['id'], reportedLabel=r['label'], profile=r['profile'], probability=s,
                    decision='focused' if s >= threshold else 'unfocused', agreement=int(s >= threshold) == r['label'])
               for r, s in zip(rows, scores)]
    return dict(predictions=results, threshold=threshold,
        reportedLabelAgreement=sum(r['agreement'] for r in results), cases=len(rows),
        reportedFocusedMisses=sum(r['reportedLabel'] == 1 and not r['agreement'] for r in results),
        reportedUnfocusedFalsePositives=sum(r['reportedLabel'] == 0 and not r['agreement'] for r in results),
        measuredQualifiedAccuracy=None, modelAccepted=False, trainingEligible=False,
        limitation='Reported labels and oracle boxes support diagnosis only. OS HCF benefit, proposal recall, and app accuracy remain unqualified.')


def run():
    config = q.load(OUT/'config.json')
    for ref in config['inputs']:
        q.require(q.digest(q.local_path(q.ROOT, ref['path'])) == ref['sha256'], 'input_changed')
    os.environ.setdefault('TORCH_HOME', str(q.ROOT/'NativeUITrainer/.torch'))
    import torch
    torch.set_num_threads(2)
    rows = []; items = []
    for profile, ref in config['metadata'].items():
        path = q.ROOT/ref['path']; doc = q.load(path)
        for state, scene in (('focused', 'focused_scene'), ('unfocused', 'baseline_scene')):
            target = doc['focused_element_id']
            elements = [e for e in doc[scene]['elements'] if e['element_id'] == target]
            q.require(len(elements) == 1, 'missing_control')
            geometry = elements[0]['rendered_body_geometry']
            q.require(geometry['availability'] == 'measured', 'unmeasured_body')
            name = doc[state+'_png']; q.require(Path(name).name == name, 'unsafe_image_name')
            image = path.parent/name; ident = profile+'-'+state
            items.append(dict(id=ident, path=str(image), sha256=doc[state+'_sha256'], bounds=geometry['visible_pixel_bounds']))
            rows.append(dict(id=ident, profile=profile, label=int(state == 'focused'), path=OUT/(ident+'.png')))
    started = time.monotonic()
    reply = focus_runtime.invoke(items)
    for row, result in zip(rows, reply['results']):
        q.require(row['id'] == result['id'], 'crop_membership')
        payload = base64.b64decode(result['png'], validate=True)
        q.require(len(payload) <= 1_000_000, 'crop_budget')
        with row['path'].open('xb') as stream: stream.write(payload)
    preprocessing_seconds = time.monotonic()-started
    started = time.monotonic()
    scores = predict_torch(q.ROOT/config['weights']['path'], rows)
    result = summarize(rows, scores)
    result.update(model=config['weights'], runtime=focus_runtime.identity(),
                  preprocessingSeconds=preprocessing_seconds, inferenceSeconds=time.monotonic()-started,
                  crops=[dict(id=r['id'], sha256=q.digest(r['path'])) for r in rows])
    q.save(OUT/'summary.json', result)
