"""Configurable crop-context and temporal-order diagnostics on retained evidence."""
from collections import Counter
from pathlib import Path
from contextlib import contextmanager
import base64
import hashlib
import io

import research_queue as q
from experiment_templates import pin, checked

OUT = None
SUCCESS = {'correct', 'correct-abstention'}


def completed(ref):
    path = checked(ref)
    result = q.load(path.parent.parent / 'result.json')
    q.require(result['status'] == 'complete', 'diagnostic_source_incomplete')
    entry = next((r for r in result['outputs'] if r['path'] == path.name), None)
    q.require(entry and entry['sha256'] == ref['sha256'], 'diagnostic_source_receipt')
    return q.load(path)


def crop_frames(request):
    frames = []
    for source in request['sources']:
        doc = completed(source)
        if doc['version'] == 'sdk-model-comparison-v1':
            for f in doc['rows']:
                frames.append(dict(id=f['id'], image=f['image'], truth=f['truth'], group=f['group'],
                    role='review_only', split=f['split'], profile=f['profile'],
                    arms={n: f['arms'][n] for n in ('known', 'union')}))
        else:
            q.require(doc.get('view') == 'geometry' and not doc['trainingEligible'], 'diagnostic_source_kind')
            for f in doc['frames']:
                controls = [e for e in f['elements'] if e['body'].get('availability') == 'measured']
                boxes = [e['body']['visible_pixel_bounds'] for e in controls]
                truths = [b for e, b in zip(controls, boxes) if e['focused']]
                q.require(len(truths) == 1 and f['role'] == 'calibration', 'diagnostic_fixture_truth')
                frames.append(dict(id=f['case'] + ':' + f['endpoint'], image=f['image'], truth=truths[0],
                    group=f['group'], role=f['role'], split='calibration', profile='unknown', arms={'known': dict(boxes=boxes)}))
    q.require(0 < len(frames) <= 32 and len({f['id'] for f in frames}) == len(frames), 'diagnostic_frame_scope')
    for f in frames:
        checked(f['image'])
    return frames


def temporal_rows(request):
    if request['sourceKind'] == 'sdk':
        from sdk_temporal508 import rows
        return rows(q.load(checked(request['source'])))
    from temporal_pairs414 import manifest
    doc = q.load(checked(request['source']))
    result = manifest(doc)
    q.require(all(r['role'] in ('development', 'calibration', 'test') for r in result), 'diagnostic_temporal_role')
    q.require(len(result) <= 512, 'diagnostic_temporal_scope')
    for r in result:
        checked(r['action']['evidence'])
        for ref in r['images']:
            checked(ref)
    return result


def expanded(box, factor, size=None):
    x, y, w, h = box
    q.require(factor in (1., 1.5) and w > 0 and h > 0, 'diagnostic_context_scale')
    result = [x - w * (factor - 1) / 2, y - h * (factor - 1) / 2, w * factor, h * factor]
    if size is not None:
        # Clip context before the unchanged production expansion. Proposal boxes stay unchanged.
        left, top = max(0, result[0]), max(0, result[1])
        right, bottom = min(size[0], result[0]+result[2]), min(size[1], result[1]+result[3])
        q.require(right > left and bottom > top, 'diagnostic_context_outside_image')
        result = [left, top, right-left, bottom-top]
    return result


def comparison(old, new):
    return dict(baseline=old, candidate=new, gain=old not in SUCCESS and new in SUCCESS,
                loss=old in SUCCESS and new not in SUCCESS,
                newWrong=old not in ('wrong', 'false-selection', 'false-change') and new in ('wrong', 'false-selection', 'false-change'))


@contextmanager
def grayscale_inputs(module):
    """Transform both full-frame and detail reads inside one isolated scoring process."""
    original = module.image
    def converted(*args, **kwargs):
        # The original reader verifies the original image hash before conversion.
        return original(*args, **kwargs).convert('L').convert('RGB')
    module.image = converted
    try:
        yield
    finally:
        module.image = original


def build(path):
    r = q.load(path)
    q.require(r['version'] == 'sdk-diagnostic-v1' and q.ID.fullmatch(r['id']), 'diagnostic_contract')
    refs = [pin(path), *r['models'].values()]
    if r['kind'] == 'crop':
        q.require(set(r['models']) == {'hcf', 'mixed'}, 'diagnostic_crop_models')
        crop_frames(r)
        refs += [*r['sources'], r['tool']]
        question = 'Do wider context or aspect-preserving crops recover native focus without losing retained successes?'
    else:
        q.require(r['kind'] == 'temporal' and r['sourceKind'] in ('sdk', 'manifest'), 'diagnostic_kind')
        temporal_rows(r)
        refs += [r['source']]
        question = 'Does symmetric temporal scoring recover departure without new false changes on retained cases?'
        q.require(r.get('operation', 'symmetric-max') in ('symmetric-max', 'grayscale'), 'diagnostic_operation')
        if r.get('operation') == 'grayscale':
            refs += [r['prior']]
            question = 'Does removing color sensitivity recover departure without losing retained temporal successes?'
    for ref in refs:
        checked(ref)
    refs += [pin(Path(__file__).resolve())]
    return dict(version='research-spec-v2', id=r['id'], task='SDK509', owner='Maximum-mini-NUIAK', kind='screen',
        jobKind='artifact', authority='diagnostic', dependencies=[], inputs=refs,
        adapter=dict(type='python-callable', steps=['sdk_diagnostics509.run'], outputAttributes=['sdk_diagnostics509.OUT']),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100000000, maxAttempts=1),
        evidence=dict(artifactReceipt='artifact-receipt.json', reads=[x['path'] for x in refs[:-1]]),
        question=question, hypothesis=question,
        controlledComparison='Keep original pixels, models, labels, roles, and thresholds. Change one declared inference operation at a time.',
        decisionRule='Reject any correction with lost successes or new wrong outcomes. Keep native and authored results separate.',
        nextActionByOutcome=dict(supported='Request independent validation of the fixed correction. Do not promote.',
                                 contradicted='Reject the correction and retain failure evidence for separate training data requirements.'))


def crop_run(r):
    import numpy as np
    import torch
    from PIL import Image
    import focus_runtime
    from native_selection404 import outcome
    from train_focus_ring_detector import load_mobilenetv4_conv_small
    from sdk_campaign508 import fallback
    frames = crop_frames(r)
    torch.set_num_threads(2)
    focus_runtime.TOOL = checked(r['tool'])
    nets = {}
    for name, ref in r['models'].items():
        net = load_mobilenetv4_conv_small()(pretrained=False, num_classes=1).eval()
        net.load_state_dict(torch.load(checked(ref), map_location='cpu', weights_only=True)['state_dict'], strict=True)
        nets[name] = net
    results, cache = [], {}
    for f in frames:
        with Image.open(checked(f['image'])) as source_image:
            image_size = source_image.size
        for arm, old in f['arms'].items():
            variants = {}
            for mode, factor, fit in (('baseline', 1., False), ('wide-context', 1.5, False), ('aspect-fit', 1., True)):
                boxes = [expanded(b, factor, image_size) for b in old['boxes']]
                key = (f['image']['sha256'], tuple(tuple(b) for b in boxes), fit)
                if key not in cache:
                    scores = {m: [] for m in nets}; hashes = []
                    if boxes:
                        items = [dict(id=str(i), path=str(checked(f['image'])), sha256=f['image']['sha256'], bounds=b) for i, b in enumerate(boxes)]
                        arrays = []
                        for batch in focus_runtime.bounded_batches(items, shared_images=True):
                            reply = focus_runtime.invoke(batch, experimental_aspect_fit=fit, image_root=Path('/Volumes/training-drive/data/NUIAK'))
                            for item in reply['results']:
                                with Image.open(io.BytesIO(base64.b64decode(item['png'], validate=True))) as image:
                                    q.require(image.size == (256, 256), 'diagnostic_crop_shape')
                                    array = np.array(image.convert('RGB'), copy=True)
                                arrays.append(array)
                                hashes.append(hashlib.sha256(b'(256, 256)\0' + array.tobytes()).hexdigest())
                        tensor = torch.from_numpy(np.stack(arrays)).permute(0, 3, 1, 2).float() / 255
                        with torch.no_grad():
                            scores = {m: torch.sigmoid(net(tensor)).reshape(-1).tolist() for m, net in nets.items()}
                    scores['fallback'] = fallback(scores['hcf'], scores['mixed'])
                    cache[key] = (scores, hashes)
                scores, hashes = cache[key]
                if mode == 'baseline' and 'cropRGBSHA256' in old:
                    q.require(hashes == old['cropRGBSHA256'], 'diagnostic_crop_parity')
                    for m in nets:
                        q.require(len(scores[m]) == len(old['models'][m]['scores']) and
                                  all(abs(a-b) <= 1e-6 for a,b in zip(scores[m], old['models'][m]['scores'])), 'diagnostic_score_parity')
                variants[mode] = dict(cropBounds=boxes, hashes=hashes,
                    models={m: dict(scores=s, outcome=outcome(s, old['boxes'], f['truth'])) for m,s in scores.items()})
            for mode in ('wide-context', 'aspect-fit'):
                for m in ('hcf', 'mixed', 'fallback'):
                    results.append(dict(id=f['id'], image=f['image'], group=f['group'], role=f['role'], split=f['split'],
                        profile=f['profile'], noFocus=f['truth'] is None, arm=arm, model=m, intervention=mode,
                        **comparison(variants['baseline']['models'][m]['outcome'], variants[mode]['models'][m]['outcome']),
                        proposalBoxes=old['boxes'], candidateCropBounds=variants[mode]['cropBounds'],
                        baselineScores=variants['baseline']['models'][m]['scores'], candidateScores=variants[mode]['models'][m]['scores']))
    return dict(rows=results, frames=len(frames), groups=len({f['group'] for f in frames}), uniqueImages=len({f['image']['sha256'] for f in frames}),
        baselineParity='verified_where_prior_scores_exist', limitation='Crop interventions do not change proposal boxes or labels. Unknown visual profile stays unknown.')


def temporal_run(r):
    import additive341 as a
    import report_additive341 as scoring
    from temporal_pairs414 import decision, outcome
    data = temporal_rows(r)
    reverse = [dict(row, images=row['images'][::-1]) for row in data]
    a.t.set_num_threads(2)
    results = []
    operation = r.get('operation', 'symmetric-max')
    prior = None
    if operation == 'grayscale':
        prior = completed(r['prior'])
        previous_request = q.load(checked(prior['request']))
        q.require(previous_request['source'] == r['source'] and previous_request['sourceKind'] == r['sourceKind'] and
                  previous_request.get('operation', 'symmetric-max') == 'symmetric-max' and
                  all(previous_request['models'][k] == v for k,v in r['models'].items()), 'diagnostic_prior_mismatch')
    for name, ref in r['models'].items():
        net = a.e.load_candidate(checked(ref)); net.eval()
        with a.t.inference_mode():
            if operation == 'grayscale':
                previous = [row for row in prior['rows'] if row['model'] == name]
                q.require([row['id'] for row in previous] == [row['id'] for row in data], 'diagnostic_prior_membership')
                forward = [row['forward'] for row in previous]
                with grayscale_inputs(a.r.s):
                    backward = scoring.score_rows(net, data, False).tolist()
            else:
                forward = scoring.score_rows(net, data, False).tolist()
                backward = scoring.score_rows(net, reverse, False).tolist()
        q.require(len(forward) == len(backward) == len(data), 'diagnostic_temporal_count')
        for row, p, rev in zip(data, forward, backward):
            candidate = rev if operation == 'grayscale' else max(p, rev)
            old = outcome(decision(p), row['changed']); new = outcome(decision(candidate), row['changed'])
            results.append(dict(id=row['id'], group=row['group'], role=row['role'], model=name,
                condition=row.get('observed', row.get('condition')), label=row['changed'], forward=p, reverse=rev,
                intervention=operation, candidateProbability=candidate,
                scoreMeaning='reverse contains grayscale forward probability' if operation == 'grayscale' else 'reverse contains reverse-order probability',
                **comparison(old, new)))
    return dict(rows=results, pairs=len(data), groups=len({row['group'] for row in data}),
        limitation='Inference interventions can add false changes. Grayscale uses original hash-verified images in memory. Neither operation locates the focused control.')


def run():
    spec = q.load(OUT.parents[2] / 'spec.json'); request = q.load(checked(spec['inputs'][0]))
    report = crop_run(request) if request['kind'] == 'crop' else temporal_run(request)
    report.update(version='sdk-diagnostic-results-v1', request=spec['inputs'][0], kind=request['kind'], modelAccepted=False, trainingEligible=False)
    report['gains'] = sum(row['gain'] for row in report['rows'])
    report['losses'] = sum(row['loss'] for row in report['rows'])
    report['newWrong'] = sum(row['newWrong'] for row in report['rows'])
    q.save(OUT / 'benchmark_summary.json', report)
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[dict(path='benchmark_summary.json', sha256=q.digest(OUT / 'benchmark_summary.json'))]))


def report_spec(specs, ident):
    q.require(len({s['id'] for s in specs}) == len(specs) and q.ID.fullmatch(ident), 'diagnostic_report_ids')
    return dict(version='research-spec-v2', id=ident, task='SDK509', owner='Maximum-mini-NUIAK', kind='screen',
        jobKind='artifact', authority='diagnostic', inputs=[],
        dependencies=[dict(job=s['id'], specSHA256=q.text_digest(s), outputs=['benchmark_summary.json']) for s in specs],
        adapter=dict(type='python-callable', steps=['sdk_diagnostics509.report_run'], outputAttributes=['sdk_diagnostics509.OUT']),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100000000, maxAttempts=1),
        evidence=dict(artifactReceipt='artifact-receipt.json', reads=[]),
        question='Which correction recovers native failures without losing retained successes?',
        hypothesis='Independent regression reports can reject a local gain that breaks prior outcomes.',
        controlledComparison='Join completed native and retained comparisons without additional inference.',
        decisionRule='Reject corrections with losses or new wrong outcomes. Do not promote from this diagnostic set.',
        nextActionByOutcome=dict(supported='Qualify independent evidence before adoption.', contradicted='Keep models and reject failing corrections.'))


def report_run():
    spec = q.load(OUT.parents[2] / 'spec.json'); sources = []; results = []
    for dep in spec['dependencies']:
        job = OUT.parents[4] / 'jobs' / dep['job']; state, attempts = q.state(job)
        q.require(state == 'complete', 'diagnostic_dependency_incomplete')
        result = q.load(attempts[-1] / 'result.json')
        q.require(result['specSHA256'] == dep['specSHA256'], 'diagnostic_dependency_spec')
        ref = pin(attempts[-1] / 'out/benchmark_summary.json'); doc = completed(ref); sources.append(ref)
        for row in doc['rows']:
            results.append(dict(**row, job=dep['job'], kind=doc['kind']))
    gates = {}
    for row in results:
        key = '/'.join([row['kind'], row['model'], row.get('intervention', 'symmetric-max'), row.get('arm', 'pair')])
        gate = gates.setdefault(key, dict(gains=[], losses=[], newWrong=[], jobs=[]))
        case = row['job'] + ':' + row['id']
        for field, target in [('gain', 'gains'), ('loss', 'losses'), ('newWrong', 'newWrong')]:
            if row[field]: gate[target].append(case)
        if row['job'] not in gate['jobs']: gate['jobs'].append(row['job'])
    for gate in gates.values():
        gate['decision'] = 'reject' if gate['losses'] or gate['newWrong'] else 'independent_validation_required' if gate['gains'] else 'no_gain'
    q.save(OUT / 'benchmark_summary.json', dict(version='sdk509-decision-v1', sources=sources, gates=gates,
        modelAccepted=False, trainingEligible=False, limitation='Counts across related endpoints are not independent accuracy. No source-role changes.'))
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[dict(path='benchmark_summary.json', sha256=q.digest(OUT / 'benchmark_summary.json'))]))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('requests', nargs='+')
    parser.add_argument('--output', required=True)
    parser.add_argument('--report-id', required=True)
    args = parser.parse_args()
    destination = Path(args.output).resolve()
    q.require(destination.is_relative_to(q.ROOT.resolve()) and not destination.exists(), 'diagnostic_output_collision_or_boundary')
    specs = [build(Path(p)) for p in args.requests]
    specs.append(report_spec(specs, args.report_id))
    for spec in specs: q.validate(spec)
    destination.mkdir(parents=True)
    for spec in specs:
        q.save(destination / (spec['id'] + '.json'), spec)
        print(spec['id'])
