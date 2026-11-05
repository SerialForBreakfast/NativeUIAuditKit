"""Reusable immutable FocusRing surgery, dataset preparation, scoring and comparison."""
import base64
import hashlib
import math
from pathlib import Path
import torch
import research_queue as q
from template_adapters395 import resolve_inputs, document
from template_inputs398 import checked, pin
from weight_surgery import edit_parameters
from focus_ring_backbone import mobilenetv4_conv_small

OUT = None
ARMS = {'baseline': ('classifier', 0., 0.), 'bias': ('classifier', 0., .5),
        'classifier': ('classifier', .5, 0.), 'head': ('head', .5, 0.)}


def ancestry(base, donor, preflight, completion):
    """Verify retained initialization records; do not infer ancestry from tensor shapes."""
    p, c = document(preflight), document(completion)
    q.require(p.get('arm') == c.get('arm') == 'warm-stretch', 'ancestry_arm')
    q.require(p.get('launchEligible') is True and c.get('status') == 'completed', 'ancestry_completion')
    q.require(p.get('protocolSHA256') and p['protocolSHA256'] == c.get('protocolSHA256'), 'ancestry_protocol')
    q.require(p.get('warmCheckpoint') == base, 'ancestry_parent')
    q.require(c.get('bestSHA256') == donor['sha256'], 'ancestry_donor')
    q.require(p.get('configuration', {}).get('model') == 'mobilenetv4_conv_small', 'ancestry_architecture')
    q.require(c.get('experimentID') == 'FDR-006', 'ancestry_experiment')
    q.require(p.get('configuration', {}).get('augmentation') == 'none', 'ancestry_preprocessing')
    q.require(p.get('support') == {'train': {'0': 37, '1': 37}, 'validation': {'0': 9, '1': 9}}, 'ancestry_membership')
    for ref in (base, donor):
        state = torch.load(checked(ref), map_location='cpu', weights_only=True)
        q.require(state.get('model_name') == 'mobilenetv4_conv_small', 'ancestry_model_name')
    return dict(verified=True, evidenceKind='retained-preflight-and-completion',
                base=base, donor=donor, preflight=preflight, completion=completion,
                protocolSHA256=p['protocolSHA256'],
                limitation='Historical records bind initialization; no execution attestation is claimed.')


def receipt(names):
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=name, sha256=q.digest(OUT/name)) for name in names]))


def refs():
    return resolve_inputs(q.load(OUT.parents[2]/'spec.json')['template'], OUT)


def produce():
    r = refs()
    config = document(r['recipe'])
    q.require(config.get('version') == 'weight-surgery-recipe-v1' and config.get('arm') in ARMS, 'surgery_recipe')
    proof = ancestry(r['base'], r['donor'], r['preflight'], r['completion'])
    base = torch.load(checked(r['base']), map_location='cpu', weights_only=True)
    donor = torch.load(checked(r['donor']), map_location='cpu', weights_only=True)
    model = mobilenetv4_conv_small()
    group, coefficient, offset = ARMS[config['arm']]
    prefixes = ('classifier', 'conv_head') if group == 'head' else ('classifier',)
    allowed = [k for k, _ in model.named_parameters() if k.split('.')[0] in prefixes]
    state, edit = edit_parameters(model, base['state_dict'], donor['state_dict'], allowed, coefficient, offset)
    model.load_state_dict(state, strict=True)
    target = OUT/'candidate.pt'
    q.require(not target.exists(), 'candidate_collision')
    torch.save(dict(state_dict=state, model_name='mobilenetv4_conv_small', surgery=dict(config, ancestry=proof)), target)
    reloaded = torch.load(target, map_location='cpu', weights_only=True)['state_dict']
    q.require(all(torch.equal(state[k], reloaded[k]) for k in state), 'candidate_roundtrip')
    edit.update(ancestryVerified=True, ancestry=proof, arm=config['arm'], modelAccepted=False)
    q.save(OUT/'edit.json', edit)
    q.save(OUT/'model.json', dict(version='weight-surgery-model-v1', checkpoint=pin(target),
                               arm=config['arm'], edit=pin(OUT/'edit.json'), threshold=.85, modelAccepted=False))
    receipt(['candidate.pt', 'model.json', 'edit.json'])


def validate_reference(label):
    review = label.get('review', {})
    q.require(review.get('blinded') is True and review.get('status') == 'accepted'
              and review.get('reviewer') and not any(t in review['reviewer'].lower() for t in ('agent', 'nuiak', 'model')), 'independent_focus_review')
    focus = label.get('focus', {})
    q.require(focus.get('state') == 'focused', 'focus_reference_unknown')
    box = focus.get('box')
    q.require(isinstance(box, list) and len(box) == 4 and all(type(x) in (int, float) and math.isfinite(x) for x in box)
              and box[2] > 0 and box[3] > 0, 'focus_reference_box')
    for obj in label.get('objects', []):
        q.require(not any(t in str(obj.get('provenance', '')).lower() for t in ('prediction', 'model-output', 'candidate')), 'prediction_as_reference')


def prepare():
    from PIL import Image
    import focus_runtime as runtime
    from perception_benchmark import _iou
    r = refs(); plan = document(r['plan'])
    q.require(plan.get('version') == 'weight-surgery-suite-plan-v1', 'surgery_suite_plan')
    q.require(runtime.identity() == plan['runtime'], 'crop_runtime_changed')
    frames, batch, pixels = [], [], set()
    for case in plan['frames']:
        label = document(case['label']); validate_reference(label)
        image = checked(case['image'])
        from PIL import Image
        with Image.open(image) as decoded:
            rgb = decoded.convert('RGB')
            pixel = hashlib.sha256(str(rgb.size).encode()+rgb.tobytes()).hexdigest()
        q.require(pixel not in pixels, 'duplicate_development_pixels')
        pixels.add(pixel)
        q.require(label['imageSHA256'] == case['image']['sha256'], 'reference_image_changed')
        frame = dict(id=case['id'], app=case['app'], group=case['group'], candidates=[], truthKey=case['id']+'|truth')
        for candidate in case['candidates']:
            key = case['id']+'|'+candidate['id']
            frame['candidates'].append(dict(key=key, iou=_iou(candidate['bounds'], label['focus']['box'])))
            batch.append(dict(id=key, path=str(image.relative_to(q.ROOT)), sha256=case['image']['sha256'], bounds=candidate['bounds']))
        batch.append(dict(id=frame['truthKey'], path=str(image.relative_to(q.ROOT)), sha256=case['image']['sha256'], bounds=label['focus']['box']))
        frames.append(frame)
    q.require(len(frames) == len({f['id'] for f in frames}) > 0, 'duplicate_frames')
    crops = {}; (OUT/'crops').mkdir()
    for part in runtime.bounded_batches(batch, shared_images=True):
        reply = runtime.invoke(part)
        q.require({v['id'] for v in reply['results']} == {v['id'] for v in part}, 'incomplete_crops')
        for row in reply['results']:
            path = OUT/'crops'/(hashlib.sha256(row['id'].encode()).hexdigest()+'.png')
            path.write_bytes(base64.b64decode(row['png'], validate=True))
            with Image.open(path) as image:
                q.require(image.size == (256, 256), 'crop_dimensions')
                image.verify()
            crops[row['id']] = pin(path)
    legacy = plan['legacy']
    legacy_manifest = document(plan['legacyManifest'])
    from eval_focus_ring_detector import load_split
    actual_legacy = [dict(image=pin(row['path']), label=row['label']) for row in load_split(q.ROOT/'dataset/focus_ring', 'test')]
    q.require(actual_legacy == legacy, 'legacy_manifest_changed')
    original_ancillary = document(plan['ancillarySource'])
    for scope in ('reserved', 'calibration'):
        expected = [dict(image=row['crop'], label=row['label']) for row in original_ancillary['rows'] if row['scope'] == scope]
        q.require(expected == plan['ancillary'][scope], 'ancillary_source_changed')
    for group, count in (('reserved', 16), ('calibration', 8)):
        q.require(len(plan['ancillary'][group]) == count, 'ancillary_membership')
        for row in plan['ancillary'][group]:
            checked(row['image']); q.require(row['label'] in (0, 1), 'ancillary_label')
    q.require(len(legacy) == 270, 'legacy_membership_count')
    for row in legacy:
        checked(row['image']); q.require(row['label'] in (0, 1), 'legacy_label')
    q.save(OUT/'suite.json', dict(version='weight-surgery-suite-v1', threshold=.85, frames=frames, crops=crops,
                               legacy=legacy, ancillary=plan['ancillary'], referenceRole='reviewed-development',
                               limitations=['Legacy is retained regression evidence.',
                                            'D3 uses retained non-text proposals and approximates selection.',
                                            'No independent qualification or no-focus population is included.']))
    receipt(['suite.json'])


def validate_scores(scores, expected):
    q.require(set(scores) == set(expected), 'prediction_membership')
    q.require(all(type(v) in (int, float) and math.isfinite(v) and 0 <= v <= 1 for v in scores.values()), 'invalid_probability')


def score():
    from eval_focus_ring_detector import predict_torch, metrics
    from focus_candidates556 import measure
    r = refs(); model = document(r['model']); suite = document(r['suite'])
    q.require(model.get('version') == 'weight-surgery-model-v1' and suite.get('version') == 'weight-surgery-suite-v1', 'surgery_score_contract')
    q.require(model['threshold'] == suite['threshold'] == .85, 'threshold_changed')
    edit = document(model['edit']); q.require(edit.get('ancestryVerified') is True, 'unverified_ancestry')
    checkpoint = checked(model['checkpoint'])
    torch.set_num_threads(4)
    keys = list(suite['crops']); paths = [dict(path=checked(suite['crops'][key])) for key in keys]
    values = predict_torch(checkpoint, paths)
    if model['arm'] == 'baseline':
        original = checked(edit['ancestry']['base'])
        q.require(values == predict_torch(original, paths), 'noop_prediction_parity')
    scores = dict(zip(keys, values))
    validate_scores(scores, keys)
    legacy_rows = [dict(path=checked(row['image']), label=row['label']) for row in suite['legacy']]
    legacy_prob = predict_torch(checkpoint, legacy_rows)
    legacy_metrics = metrics(legacy_rows, legacy_prob, thr=.85)
    ancillary = {}
    for group, members in suite['ancillary'].items():
        samples = [dict(path=checked(row['image']), label=row['label']) for row in members]
        ancillary[group] = metrics(samples, predict_torch(checkpoint, samples), thr=.85)
    outcomes = []
    for f in suite['frames']:
        high = [c for c in f['candidates'] if scores[c['key']] >= .85]
        outcomes.append(dict(id=f['id'], app=f['app'], group=f['group'],
                             selection=high[0]['key'] if len(high) == 1 else None,
                             correct=len(high) == 1 and high[0]['iou'] >= .5,
                             wrong=len(high) == 1 and high[0]['iou'] < .5,
                             abstained=len(high) != 1))
    summary = dict(version='weight-surgery-score-v1', arm=model['arm'], model=model['checkpoint'],
                   suiteSHA256=r['suite']['sha256'], threshold=.85, development=measure(suite['frames'], scores),
                   retention=legacy_metrics, ancillary=ancillary, outcomes=outcomes, legacyProbabilities=legacy_prob,
                   legacyLabels=[r['label'] for r in legacy_rows], scores=scores,
                   perApplication={app: dict(frames=sum(o['app']==app for o in outcomes),
                       correct=sum(o['correct'] for o in outcomes if o['app']==app),
                       wrong=sum(o['wrong'] for o in outcomes if o['app']==app),
                       abstained=sum(o['abstained'] for o in outcomes if o['app']==app))
                       for app in sorted({o['app'] for o in outcomes})},
                   unmeasuredGates=['full-screen TTR replay', 'fresh independent qualification'],
                   modelAccepted=False)
    q.save(OUT/'benchmark_summary.json', summary)
    receipt(['benchmark_summary.json'])


def compare_reports(reports):
    baseline = reports['baseline']
    q.require(set(reports) == set(ARMS), 'comparison_arms')
    q.require(len({r['suiteSHA256'] for r in reports.values()}) == 1 and all(r['threshold'] == .85 for r in reports.values()), 'comparison_membership')
    rows = []
    old = {r['id']: r for r in baseline['outcomes']}
    for arm in ARMS:
        r = reports[arm]; now = {v['id']: v for v in r['outcomes']}
        q.require(set(old) == set(now), 'comparison_cases')
        q.require(r['legacyLabels'] == baseline['legacyLabels'] and len(r['legacyProbabilities']) == len(r['legacyLabels']), 'comparison_legacy')
        gained = [k for k in old if not old[k]['correct'] and now[k]['correct']]
        lost = [k for k in old if old[k]['correct'] and not now[k]['correct']]
        wrong = [k for k in old if not old[k]['wrong'] and now[k]['wrong']]
        legacy_lost = [i for i, (b, c, y) in enumerate(zip(baseline['legacyProbabilities'], r['legacyProbabilities'], r['legacyLabels']))
                       if (b >= .85) == bool(y) and (c >= .85) != bool(y)]
        d = r['development']; pass_measured = (d['D1'] >= 12 and d['D2'] <= 8 and d['D3'] >= 5
                       and r['retention']['tp'] + r['retention']['tn'] == 270 and not lost and not wrong and not legacy_lost
                       and all(name in r.get('ancillary', {}) for name in ('reserved', 'calibration'))
                       and r['ancillary']['reserved']['tp'] + r['ancillary']['reserved']['tn'] >= 14
                       and r['ancillary']['calibration']['tp'] + r['ancillary']['calibration']['tn'] >= 3)
        status = 'contradicted' if legacy_lost or lost or wrong or not pass_measured else 'inconclusive'
        rows.append(dict(arm=arm, outcome=status, measuredGatesPass=pass_measured, gained=gained, lost=lost,
                         newWrong=wrong, lostLegacy=legacy_lost, development=d, retention=r['retention'],
                         missingGates=r['unmeasuredGates']))
    return dict(version='weight-surgery-comparison-v1', arms=rows, modelAccepted=False,
                selectedForPromotion=None, nextAction='Diagnose failed gates. If measured gates pass, qualify missing gates before candidate selection.')


def compare():
    r = refs(); result = compare_reports({key: document(ref) for key, ref in r.items()})
    q.save(OUT/'benchmark_summary.json', result)
    q.save(OUT/'report.md', '# Matched weight surgery comparison\n\n'+ '\n'.join(
        f"- {row['arm']}: {row['outcome']}; gained {len(row['gained'])}, lost {len(row['lost'])}, new wrong {len(row['newWrong'])}."
        for row in result['arms'])+'\n\nNo promotion. Missing qualification gates remain explicit.\n')
    receipt(['benchmark_summary.json', 'report.md'])


def detector_initializations():
    import copy
    import os
    os.environ.setdefault('YOLO_CONFIG_DIR', str(q.ROOT/'NativeUITrainer/.ultralytics'))
    os.environ.setdefault('MPLCONFIGDIR', str(q.ROOT/'NativeUITrainer/.mplconfig'))
    from ultralytics import YOLO
    from roles559 import ROLES, CLASS_ROLE
    from role_head_projection import initialize_pair
    r = refs()
    source = checked(r['source'])
    original = YOLO(str(source))
    q.require(len(original.model.names) == 41, 'source_taxonomy_count')
    first, second, report = initialize_pair(original.model, original.model.names, ROLES, CLASS_ROLE, seed=42)
    for name, model in (('random', first), ('projected', second)):
        checkpoint = copy.deepcopy(original.ckpt)
        checkpoint.update(model=model.cpu().float(), ema=None, optimizer=None, epoch=-1,
                          surgery=dict(report, source=r['source'], arm=name))
        path = OUT/(name+'.pt'); q.require(not path.exists(), 'initialization_collision')
        torch.save(checkpoint, path)
        reloaded = YOLO(str(path))
        q.require(reloaded.model.names == dict(enumerate(ROLES)), 'initialization_taxonomy_roundtrip')
        q.require(all(torch.equal(v.cpu(), reloaded.model.state_dict()[k].cpu()) for k,v in model.state_dict().items()), 'initialization_roundtrip')
    q.save(OUT/'initializations.json',dict(report, source=r['source'],random=pin(OUT/'random.pt'),projected=pin(OUT/'projected.pt'),
        trainingReady=False, blocker='T89 fixes seed 371 and its trainer rebuilds the model; seed 42 and retained initializer preservation need qualification.'))
    receipt(['random.pt','projected.pt','initializations.json'])
