"""Retained development-only brightness/paired-state diagnostic; never loads a model."""
import argparse
from collections import Counter, defaultdict
import math
import time

import numpy as np
from PIL import Image
import human_annotation_review as h
import focus_representative_experiment as metrics

VERSION = 'focus-brightness-spike-v1'
POLICY = dict(luma=.60, neutral=.45, delta=.08, model=.85,
              sizes=[16, 32, 64, 192], body=[32, 32, 224, 224])
SETTINGS = frozenset(('settings', 'settings-apps', 'voiceover-settings',
                      'accessibility', 'settings-accessibility'))


def features(image):
    h.require(image.size == (256, 256), 'production_crop_dimensions')
    rgb = np.asarray(image.convert('RGB'), dtype=np.float64)
    body = rgb[32:224, 32:224]
    luma = rgb @ np.array([.2126, .7152, .0722]) / 255
    mask = np.ones((256, 256), dtype=bool)
    mask[32:224, 32:224] = False
    result = dict(luma=float(luma[32:224, 32:224].mean()),
                  neutral=float(((body.min(2) > 220) &
                                 (body.max(2)-body.min(2) < 25)).mean()),
                  contrast=float(luma[32:224, 32:224].mean()-luma[mask].mean()))
    body_image = Image.fromarray(body.astype(np.uint8))
    result['downsample'] = {}
    for size in POLICY['sizes']:
        small = np.asarray(body_image.resize((size, size), Image.Resampling.BOX), dtype=float)
        result['downsample'][str(size)] = dict(
            luma=float((small @ np.array([.2126, .7152, .0722]) / 255).mean()),
            neutral=float(((small.min(2) > 220) & (small.max(2)-small.min(2) < 25)).mean()))
    return result


def bright(value):
    return value['luma'] >= POLICY['luma'] and value['neutral'] >= POLICY['neutral']


def direction(before, after, *, settled, matched, stable_context):
    if not (settled and matched and stable_context):
        return 'unavailable'
    delta = after['luma']-before['luma']
    h.require(math.isfinite(delta), 'invalid_luma')
    return 'arrival' if delta >= POLICY['delta'] else 'departure' if delta <= -POLICY['delta'] else 'unknown'


def membership(rows, predictions):
    h.require(bool(rows), 'empty_supported_subset')
    h.require(len(rows) == len({r['id'] for r in rows}), 'duplicate_sample')
    h.require(len(predictions) == len({p['id'] for p in predictions}), 'duplicate_prediction')
    h.require({r['id'] for r in rows} == {p['id'] for p in predictions}, 'prediction_membership')
    index = {p['id']: p for p in predictions}
    for r in rows:
        p = index[r['id']]
        h.require(r['split'] == 'validation' and r['use'] in
                  ('representative-selection', 'retention-validation'), 'protected_or_unsupported_role')
        h.require(type(r['label']) is int and r['label'] in (0, 1) and p['label'] == r['label'], 'label_mismatch')
        q = p['probability']
        h.require(type(q) in (int, float) and math.isfinite(q) and 0 <= q <= 1, 'invalid_score')
    return index


def arm_predictions(rows, scores, values, arm):
    h.require(arm in ('model', 'brightness', 'settings-oracle-hybrid', 'agreement-only'), 'unsupported_arm')
    result = []
    for r in rows:
        q = scores[r['id']]['probability']
        b = bright(values[r['id']])
        family = r.get('family', r.get('sourceID'))
        if arm == 'brightness' or (arm == 'settings-oracle-hybrid' and family in SETTINGS):
            q = float(b)
        elif arm == 'agreement-only':
            q = q if b else 0.
        result.append(dict(id=r['id'], label=r['label'], probability=q))
    return result


def counts(rows, predictions):
    result = Counter()
    for r, p in zip(rows, predictions):
        result[('tp' if p['probability'] >= .85 else 'fn') if r['label'] else
               ('fp' if p['probability'] >= .85 else 'tn')] += 1
    return dict(result)


def run(protocol, baseline, growth, output):
    out = h.fresh(output)
    doc = h.read(h.local(protocol), limit=32*1024*1024)
    h.require(doc.get('version') == 'focus-visual-experiment-v1' and
              doc['protocolSHA256'] == h.digest({k:v for k,v in doc.items() if k != 'protocolSHA256'}),
              'changed_protocol')
    h.require(all(r['split'] in ('train','validation') for r in doc['samples']), 'protected_or_unsupported_role')
    rows = [r for r in doc['samples'] if r['split'] == 'validation']
    old = h.read(h.local(baseline), limit=32*1024*1024)
    selected = [s for s in old['history'] if s['update'] == old['selectedUpdate']]
    h.require(len(selected) == 1, 'selected_checkpoint_missing')
    scores = membership(rows, selected[0]['validation']['predictions'])
    samples = {r['id']: r for r in doc['samples']}
    pairs = h.read(h.local(growth))['comparisons']
    pair_ids = {p[k] for p in pairs for k in ('focused', 'unfocused')}
    h.require(pair_ids <= samples.keys(), 'missing_pair_member')
    for sid in pair_ids:
        h.require(samples[sid]['split'] == 'train', 'pair_role_changed')
    values = {}
    refs = {}
    start = time.monotonic()
    for sid in sorted(pair_ids | {r['id'] for r in rows}):
        ref = samples[sid]['crop']
        path = h.checked(h.ROOT, ref)
        refs[sid] = ref
        with Image.open(path) as im:
            values[sid] = features(im)
    elapsed = time.monotonic()-start
    arms = {}
    for arm in ('model', 'brightness', 'settings-oracle-hybrid', 'agreement-only'):
        preds = arm_predictions(rows, scores, values, arm)
        replay = metrics.selection_metrics(preds, rows, doc['selection'])
        # Binary heuristic outputs use the existing counts, never probabilistic calibration claims.
        strata = {}
        for family in sorted({r.get('family', r.get('sourceID')) for r in rows}):
            indices = [i for i,r in enumerate(rows) if r.get('family', r.get('sourceID')) == family]
            strata[family] = counts([rows[i] for i in indices], [preds[i] for i in indices])
        arms[arm] = dict(counts=counts(rows,preds), families=strata,
                         frames=replay['real']['metrics']['completeFrameSelection'],
                         real=replay['real']['metrics']['candidate']['groups']['overall'],
                         retention=replay['retention']['retentionCorrect'], predictions=preds)
    h.require(arms['model']['real'] == selected[0]['validation']['real']['metrics']['candidate']['groups']['overall'],
              'baseline_counts_changed')
    paired = []
    # Static native same-control pairs: both directions are diagnostics, not recorded actions.
    for pair in pairs:
        f,u = (samples[pair[k]] for k in ('focused','unfocused'))
        h.require(f['label']==1 and u['label']==0 and f['sourceID']==u['sourceID'] and
                  f['sourceElementID']==u['sourceElementID'], 'pair_identity_or_label')
        paired.append(dict(focused=f['id'],unfocused=u['id'],source=f['sourceID'],
            delta=values[f['id']]['luma']-values[u['id']]['luma'],growth=pair['raw'],
            arrival=direction(values[u['id']],values[f['id']],settled=True,matched=True,stable_context=True),
            departure=direction(values[f['id']],values[u['id']],settled=True,matched=True,stable_context=True),
            noOp=direction(values[u['id']],values[u['id']],settled=True,matched=True,stable_context=True)))
    retained=defaultdict(dict)
    for r in rows:
        if r['use']=='retention-validation':retained[r['elementID']][r['label']]=r
    settings_pairs=[]
    for element,states in sorted(retained.items()):
        h.require(set(states)=={0,1}, 'incomplete_retention_pair')
        u,f=states[0],states[1]
        settings_pairs.append(dict(element=element,focused=f['id'],unfocused=u['id'],
            delta=values[f['id']]['luma']-values[u['id']]['luma'],
            arrival=direction(values[u['id']],values[f['id']],settled=True,matched=True,stable_context=True),
            modelPositive=scores[f['id']]['probability']>=.85,
            combinedPositive=scores[f['id']]['probability']>=.85 and
                direction(values[u['id']],values[f['id']],settled=True,matched=True,stable_context=True)=='arrival'))
    sensitivity={str(n):dict(
        changedDecisions=sum(bright(v)!=bright(v['downsample'][str(n)]) for v in values.values()),
        maxLumaError=max(abs(v['luma']-v['downsample'][str(n)]['luma']) for v in values.values()))
        for n in POLICY['sizes']}
    report=dict(version=VERSION,policy=POLICY,inputs=[h.ref(h.local(p)) for p in (protocol,baseline,growth)],
        scope='development-exposed oracle bounds/context; static pairs are NOT qualified transitions',
        modelExecution=False,trainingAdmission=False,releaseEligible=False,
        evaluationControls=len(rows),featureControls=len(values),featureSeconds=elapsed,
        arms=arms,features=values,cropReferences=refs,downsampleSensitivity=sensitivity,
        staticPairs=paired,settingsPairs=settings_pairs,
        pairCounts=dict(Counter(p['arrival'] for p in paired)),
        settingsPairCounts=dict(Counter(p['arrival'] for p in settings_pairs)),
        unavailable=['runtime Settings recognizer','detector-box end-to-end result',
                     'qualified genuine transition accuracy','untouched independent test'])
    out.mkdir(parents=True)
    h.write(out/'result.json',report)
    print({k:report[k] for k in ('evaluationControls','featureControls','featureSeconds','pairCounts','settingsPairCounts','downsampleSensitivity')})
    for arm,r in arms.items():print(arm, r['real'], r['frames']['counts'],r['retention'])
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('protocol','baseline','growth','output'):p.add_argument('--'+name,required=True)
    a=p.parse_args();run(a.protocol,a.baseline,a.growth,a.output)
