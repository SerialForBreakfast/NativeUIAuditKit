"""Source-bound alignment diagnosis; reviewed centers are an oracle, never inference."""
import argparse
import copy
import math
import time
from collections import Counter

from PIL import Image, ImageDraw
import human_annotation_review as h
import focus_recorded_comparison as comparison
import focus_recorded_semantics as semantic
import focus_recorded_transition_eval as evaluate
import focus_transition_verifier as visual
import focus_runtime as native
import settings_focus_stability as stability
import settings_context_probe as context

ARMS = ('visionReplay', 'roundedDisplacement', 'reviewedCenterOracle')
METRICS = ('mean', 'p95', 'changedFraction', 'maximum')


def translated(body, center, size):
    """Keep before size: do not normalize out a focus enlargement."""
    x, y, w, height = body
    out = [center[0]-w/2, center[1]-height/2, w, height]
    if out[0] < 0 or out[1] < 0 or out[0]+w > size[0] or out[1]+height > size[1]:
        return visual.unavailable('translated_body_outside')
    windows = visual.common_support(body, out, size)
    if windows is None:
        return visual.unavailable('clipping_support')
    return dict(status='matched', afterBounds=out, dx=out[0]-x, dy=out[1]-y,
                beforeCropBounds=windows[0], afterCropBounds=windows[1])


def center(box):
    return [box[0]+box[2]/2, box[1]+box[3]/2]


def alignment(body, tracking, target, size, arm):
    h.require(arm in ARMS, 'unknown_alignment_arm')
    if arm == 'visionReplay':
        return copy.deepcopy(tracking)
    if arm == 'reviewedCenterOracle':
        if target is None:
            return visual.unavailable('no_reviewed_correspondence')
        return dict(translated(body, center(target), size), oracleGeometry=True)
    if tracking['status'] != 'matched':
        return copy.deepcopy(tracking)
    actual = tracking['afterBounds']
    # Round displacement, not absolute positions: fractional before boxes stay intact.
    dx, dy = round(actual[0]-body[0]), round(actual[1]-body[1])
    return translated(body, [body[0]+body[2]/2+dx, body[1]+body[3]/2+dy], size)


def predict(before, after, body, tracking, ident, size):
    """No focus truth enters pixel measurements or decisions."""
    p = dict(id=ident, tracking=tracking, decision='unavailable')
    if tracking['status'] == 'identical':
        p['decision'] = 'unchanged'
    if tracking['status'] != 'matched':
        return p, None
    images, _ = context.crops(before, after, body, tracking)
    p.update(visual.compare_crops(*images, clipped=any(visual.footprint(body, size))))
    metrics = stability.measure(*images)
    p['decision'] = stability.guard(stability.extend(p, metrics, settings_context=True), metrics)['decision']
    p['metrics'] = metrics
    p['failedStabilityChecks'] = [k for k in METRICS if metrics[k] > stability.POLICY[k]]
    return p, images


def attribution(row):
    if row['expected'] is None:
        return 'unscorable_identity'
    p = row['prediction']
    if p['tracking']['status'] not in ('matched', 'identical'):
        return 'tracking_unavailable'
    if not row['trackingAgreesWithSemanticTarget']:
        return 'wrong_target_geometry'
    s = row['arms']['combined']
    if s['decision'] in ('unknown', 'unavailable'):
        return 'pixel_rule_abstained'
    return 'correct' if s['correct'] else 'wrong_decision'


def scored(predictions, before, after, matches):
    ps = copy.deepcopy(predictions)
    for p in ps:
        p.update(brightness=p['decision'], growth=p['decision'])
    return comparison.compare(ps, before, after, matches)


def snapshot(images, path):
    canvas = Image.new('RGB', (256*len(images), 280), (30, 30, 30))
    draw = ImageDraw.Draw(canvas)
    for i, (name, im) in enumerate(images.items()):
        draw.text((i*256+4, 4), name, fill='white')
        if im is not None:
            canvas.paste(im, (i*256, 24))
    canvas.save(path)


def select_gallery(candidates, limit=12):
    """Cover actions/failure types; prioritize actual changes, not the first frame."""
    groups = {}
    for c in candidates:
        key = (c['expected'] in ('arrival', 'departure'), c['actionID'], c['attribution'])
        groups.setdefault(key, []).append(c)
    keys = sorted(groups, key=lambda k: (not k[0], k[1], k[2]))
    selected = []
    while len(selected) < limit and any(groups.values()):
        for key in keys:
            if groups[key] and len(selected) < limit:
                selected.append(groups[key].pop(0))
    return selected


def run(previous, output):
    previous = h.local(previous)
    source = h.sealed(previous, 'settings-swift-spike-v1')
    for ref in source['implementation']:
        h.checked(h.ROOT, ref)
    prior = h.sealed(h.checked(h.ROOT, source['source']), 'settings-stability-v1')
    h.checked(h.ROOT, prior['implementation'])
    h.require(prior['policy'] == stability.POLICY and prior['changePolicy'] == stability.CHANGE_POLICY, 'policy_changed')
    baseline = h.sealed(h.checked(h.ROOT, prior['baseline']), 'focus-recorded-comparison-v1')
    for ref in baseline['implementation']:
        h.checked(h.ROOT, ref)
    h.require(source['semantics'] == baseline['semantics'], 'semantic_source_changed')
    sem = h.sealed(h.checked(h.ROOT, source['semantics']), 'focus-recorded-semantics-v1')
    h.checked(h.ROOT, sem['implementation'])
    args = {k: str(h.checked(h.ROOT, v)) for k, v in sem['inputs'].items() if k != 'events'}
    _, truth, _, _ = semantic.inputs(**args)
    eligible = [a for a in baseline['actions'] if a['status'] == 'retrospective-diagnostic']
    h.require([a['actionID'] for a in eligible] == [a['actionID'] for a in source['actions']], 'action_membership')
    out = h.fresh(output); out.mkdir(parents=True)
    runtime = native.identity()
    pins = dict(source=h.ref(previous), runtime=runtime, implementation=[h.ref(h.ROOT/'scripts'/p) for p in
        ('settings_tracking_diagnosis.py', 'settings_context_probe.py', 'settings_focus_stability.py',
         'focus_transition_verifier.py', 'focus_recorded_comparison.py')])
    h.write(out/'execution.json', dict(**pins, policy=stability.POLICY, changePolicy=stability.CHANGE_POLICY,
        maxSeconds=300, maxControls=100, arms=ARMS, annotationGeometryOnlyInOracle=True, training=False))
    start = time.monotonic(); actions = []; errors = []; count = 0; candidates = []
    gallery = ['# Alignment failure review', '',
        'Private retained development images. Reviewed-center is diagnostic truth geometry, not an inference method.',
        'Same fixed full-context crop size and thresholds. Blank panel means unavailable.', '']
    for action, saved in zip(eligible, source['actions']):
        b, a = [truth[action['endpoints'][k]['sha256']] for k in ('before', 'after')]
        with Image.open(h.checked(h.ROOT, b['image'])) as im:
            size = im.size
        after = {c['id']: c for c in a['controls']}
        vr = saved['arms']['swiftVision']; py = saved['arms']['python']
        h.require([r['id'] for r in vr] == [c['id'] for c in b['controls']] == [r['id'] for r in py], 'control_membership')
        predictions = {k: [] for k in ARMS}
        for c, old, op in zip(b['controls'], vr, py):
            count += 1
            h.require(count <= 100 and time.monotonic()-start < 300, 'diagnosis_budget')
            target = after.get(old['afterControl']); body = c['bounds']
            panels = {'Before': None}
            decisions = {}
            for arm in ARMS:
                t = alignment(body, old['prediction']['tracking'], target['bounds'] if target else None, size, arm)
                p, ims = predict(b['image'], a['image'], body, t, c['id'], size)
                predictions[arm].append(p); decisions[arm] = p['decision']
                panels[arm] = ims[1] if ims else None
                if ims: panels['Before'] = ims[0]
            raw = predictions['visionReplay'][-1]
            h.require(raw['decision'] == old['prediction']['decision'], 'saved_vision_replay_changed')
            vb = old['prediction']['tracking'].get('afterBounds')
            pb = op['prediction']['tracking'].get('afterBounds')
            error = dict(actionID=action['actionID'], id=c['id'], expected=old['expected'],
                visionAttribution=attribution(old), decisions=decisions)
            for name, ref in [('reviewedCenter', target['bounds'] if target else None), ('openCVCenter', pb)]:
                if vb and ref:
                    delta = [v-r for v, r in zip(center(vb), center(ref))]
                    error[name] = dict(dx=delta[0], dy=delta[1], distance=math.hypot(*delta),
                        approximateCropPixelDx=delta[0]*256/(1.32*body[2]),
                        approximateCropPixelDy=delta[1]*256/(1.32*body[3]))
            errors.append(error)
            if attribution(old) != 'correct':
                candidates.append(dict(actionID=action['actionID'], id=c['id'], expected=old['expected'],
                    attribution=attribution(old), panels=panels, decisions=decisions, error=error, number=count))
        arms = {k: scored(ps, b['controls'], a['controls'], action['matches']) for k, ps in predictions.items()}
        actions.append(dict(actionID=action['actionID'], arms=arms, endpoints=action['endpoints']))
    summaries = {k: evaluate.summarize([r['arms']['combined'] for a in actions for r in a['arms'][k]]) for k in ARMS}
    h.require(summaries['visionReplay'] == source['summaries']['swiftVision'], 'vision_summary_changed')
    h.require(native.identity() == runtime, 'crop_runtime_changed')
    for c in select_gallery(candidates):
        path = out/f"alignment-{c['number']:03d}.png"; snapshot(c['panels'], path)
        gallery += [f"## Action {c['actionID']} / {c['id']}", '',
            f"Expected: {c['expected']}; decisions: {c['decisions']}",
            f"Vision error: {c['error'].get('reviewedCenter', 'unavailable')}", f'![Alignment panels]({path})', '']
    report = dict(version='settings-tracking-diagnosis-v1', **h.FLAGS, **pins, summaries=summaries,
        historicalBaselines=source['summaries'], actions=actions, errors=errors,
        attribution={k: dict(Counter(attribution(r) for a in actions for r in a['arms'][k])) for k in ARMS},
        exclusions=source['exclusions'], elapsedSeconds=time.monotonic()-start, oracleNotDeployable=True)
    h.write(out/'result.json', report, sealed=True)
    (out/'review.md').write_text('\n'.join(gallery)+'\n')
    print(summaries); return report


def stress(previous, output):
    # Settings25's generated-only stress envelope predates the common diagnostic flags.
    # Verify its exact schema/seal here without weakening normal batch admission.
    previous = h.local(previous); source = h.read(previous)
    h.require(source.get('version') == 'settings-swift-stress-v1' and
        source.get('seal') == h.digest({k:v for k,v in source.items() if k != 'seal'}), 'stress_source_changed')
    out = h.fresh(output); out.mkdir(parents=True)
    inputs = []; source_refs = []
    for name, path, version in [('stability', 'reports/work/SETTINGS-STABILITY-23/stress-final/result.json', 'settings-stability-stress-v1'),
                       ('context', 'reports/work/SETTINGS-CONTEXT-24/stress/result.json', 'settings-context-stress-v1')]:
        path = h.ROOT/path; d = h.sealed(path, version); source_refs.append(h.ref(path))
        for c in d['cases']: inputs.append((name+'-'+c['name'], c))
    h.require([n for n, _ in inputs] == [c['name'] for c in source['cases']], 'stress_membership')
    start = time.monotonic(); rows = []; body = [200, 200, 160, 60]; runtime = native.identity()
    pins = dict(source=h.ref(previous), generatedInputs=source_refs, runtime=runtime,
        implementation=h.ref(h.ROOT/'scripts/settings_tracking_diagnosis.py'))
    h.write(out/'execution.json', dict(**pins,
        maxSeconds=300, arms=ARMS))
    for (name, case), old in zip(inputs, source['cases']):
        h.require(time.monotonic()-start < 300, 'stress_budget')
        before, after = case['inputs']
        with Image.open(h.checked(h.ROOT, before)) as im: size = im.size
        target = None if name.endswith('duplicate') else [200, 100 if 'scroll' in name else 200, 160, 60]
        arms = {}
        for arm in ARMS:
            t = alignment(body, old['vision']['tracking'], target, size, arm)
            p, _ = predict(before, after, body, t, 'row', size); arms[arm] = p
        h.require(arms['visionReplay']['decision'] == old['swiftVision'], 'stress_replay_changed')
        rows.append(dict(name=name, expected=case['expected'], inputs=case['inputs'], arms=arms))
    h.require(native.identity() == runtime, 'crop_runtime_changed')
    report = dict(version='settings-tracking-stress-v1', **h.FLAGS, generatedSoftwareFixture=True,
        **pins, cases=rows, oracleNotDeployable=True,
        exact={k: sum(c['arms'][k]['decision'] == c['expected'] for c in rows) for k in ARMS},
        wrongDecisive={k: sum(c['arms'][k]['decision'] in ('unchanged', 'arrival', 'departure') and
            c['arms'][k]['decision'] != c['expected'] for c in rows) for k in ARMS}, elapsedSeconds=time.monotonic()-start)
    h.write(out/'result.json', report, sealed=True); print(report['exact']); return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--previous', required=True); p.add_argument('--output', required=True)
    p.add_argument('--stress', action='store_true'); a = p.parse_args()
    (stress if a.stress else run)(a.previous, a.output)
