"""Run bounded Vision diagnostics through the existing queue and Swift probe."""
import json
import math
import subprocess
from collections import defaultdict
import research_queue as q
from compare351 import validate_capture
from perception_benchmark import _iou

OUT = None
THRESHOLDS = (0, .001, .01, .05, .1, .2, .5, 1, 2)


def pair_report(pairs, measured):
    expected = {p['case']+'-'+p['condition']: p for p in pairs}
    q.require(len(expected) == len(pairs), 'duplicate_labels')
    q.require(len(measured) == len(expected) and {r['id'] for r in measured} == set(expected), 'pair_membership')
    rows = []
    for r in measured:
        p = expected[r['id']]
        q.require(r['before'] == p['before'] and r['after'] == p['after'], 'pair_order')
        value = r['distance']
        q.require(isinstance(value, (float, int)) and math.isfinite(value) and value >= 0, 'distance_invalid')
        rows.append(dict(p, distance=value))
    operating = []
    for threshold in THRESHOLDS:
        positive = [r for r in rows if r['changed']]
        negative = [r for r in rows if not r['changed']]
        operating.append(dict(threshold=threshold, positiveSupport=len(positive), negativeSupport=len(negative),
            missedChange=sum(r['distance'] <= threshold for r in positive),
            falseChange=sum(r['distance'] > threshold for r in negative)))
    return dict(rows=rows, operatingPoints=operating, selectedThreshold=None)


def rectangle_report(frames, results):
    q.require(len(results) == len(frames) and {r['id'] for r in results} == set(frames), 'frame_membership')
    rows = []
    for result in results:
        q.require(not result['errors'], 'vision_request_failed')
        frame = frames[result['id']]
        q.require(result['sha256'] == frame['sha256'], 'result_hash')
        bodies = frame['after']['scene']['elements']
        for body in bodies:
            bounds = body['rendered_body_geometry']['visible_pixel_bounds']
            overlap = max((_iou(p['bounds'], bounds) for p in result['rectangles']), default=0)
            rows.append(dict(frame=result['id'], control=body['element_id'], focused=body['is_focused'], bestIoU=overlap))
    return dict(rows=rows, observedBodies=len(rows), coveredAt50=sum(r['bestIoU'] >= .5 for r in rows),
        coveredAt75=sum(r['bestIoU'] >= .75 for r in rows),
        limitation='Proposal coverage allows reuse of proposals. It is not one-to-one detection accuracy or focus selection.')


def run():
    config = q.load(OUT/'config.json')
    for ref in config['inputs']:
        q.require(q.digest(q.local_path(q.ROOT, ref['path'])) == ref['sha256'], 'changed_input')
    path = q.local_path(q.ROOT, config['capture']['path'])
    doc = q.load(path)
    all_frames = validate_capture(doc, path.parent)
    used = {p[k] for p in doc['pairs'] for k in ('before', 'after')}
    frames = {k: v for k, v in all_frames.items() if k in used}
    request = dict(version=1, root=str(q.ROOT), frames=[dict(id=k, path=str(path.parent/v['path']), sha256=v['sha256']) for k,v in frames.items()])
    if config['mode'] == 'features':
        request.update(featureRevision=config['revision'], featureCrop=config['crop'],
            pairs=[dict(id=p['case']+'-'+p['condition'], before=p['before'], after=p['after']) for p in doc['pairs']])
    else:
        q.require(config['mode'] == 'rectangles', 'mode_invalid')
        request['rectanglesOnly'] = True
    q.save(OUT/'request.json', request)
    with (OUT/'vision.json').open('x') as output, (OUT/'vision.stderr').open('x') as errors:
        result = subprocess.run([str(q.local_path(q.ROOT, config['binary']['path']))],
            input=json.dumps(request), text=True, stdout=output, stderr=errors, timeout=740)
    q.require(result.returncode == 0, 'vision_process_failed')
    receipt = q.load(OUT/'vision.json')
    if config['mode'] == 'features':
        q.require(receipt['revision'] == config['revision'] and receipt['crop'] == config['crop'], 'settings_mismatch')
        report = pair_report(doc['pairs'], receipt['pairs'])
    else:
        report = rectangle_report(frames, receipt['results'])
    q.save(OUT/'diagnostic.json', dict(version='vision353-v1', mode=config['mode'], inputs=config['inputs'],
        role='development', independentGroups=1, modelAccepted=False, trainingEligible=False, report=report,
        limitations=['One related Fixture family, not real-app qualification.',
                    'No threshold selection or model change. Missing archetypes and themes remain unsupported.']))


def summarize():
    deps = q.load(OUT/'dependencies.json')
    q.require(len(deps) == 4, 'dependency_count')
    results = {}
    for dep in deps:
        for ref in [dep['result'], *dep['outputs']]:
            q.require(q.digest(q.local_path(q.ROOT, ref['path'])) == ref['sha256'], 'changed_dependency')
        results[dep['job']] = q.load(q.ROOT/dep['outputs'][0]['path'])
    config = q.load(OUT/'config.json')
    models = {}
    for ref in config['inputs']:
        p = q.local_path(q.ROOT, ref['path']);q.require(q.digest(p) == ref['sha256'], 'changed_cached_predictions')
        d = q.load(p)
        models[d['mode']] = {name: entry['counts'] for name,entry in d['scores'].items()}
    q.save(OUT/'comparison.json', dict(version='vision353-comparison-v1', diagnostics=results,
        retainedModels=models, modelAccepted=False, selectedThreshold=None,
        nextDecision='Assess whether similarity loses edge movement and whether proposals cover observed bodies. Do not promote from this family.'))
