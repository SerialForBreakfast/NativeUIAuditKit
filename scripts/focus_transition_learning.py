"""Offline paired-measurement learning; retained diagnostics never imply admission.

Training is dispatched by train_focus_ring_detector.py, not this inventory CLI.
No Torch, inference, crop service or network is imported by preflight.
"""
import argparse
import hashlib
from collections import Counter
import math
import re
import time
from pathlib import Path

import human_annotation_review as h
from focus_dataset_contract import digest
import focus_scene_transition as scene

VERSION = 'focus-transition-learning-v1'
CORPUS = 'focus-transition-measurements-v1'
ARM = 'transition-measurements'
LABELS = ('unchanged', 'arrival', 'departure')
FEATURES = ('lumaDelta', 'scaleX', 'scaleY', 'edgeStrength', 'centerDrift',
            'trackingDx', 'trackingDy', 'correlation', 'peakGap',
            'absoluteMean', 'absoluteP95', 'changedFraction', 'maximum',
            'arrivalCoverage', 'departureCoverage', 'hasAbsoluteMetrics', 'identical')
CONFIG = dict(model=ARM, epochs=30, batch=0, lr=.05, l2=.0001, seed=42,
              confidence=.85, maxSeconds=None, maxOutputBytes=2*1024**3,
              optimizer='full-batch-gradient-descent', selection='fixed-last')


def fresh_run(name):
    path=h.ROOT/'NativeUITrainer/focus_ring_runs'/name
    h.require(not path.exists() and not any(p.is_symlink() for p in (path,*path.parents)), 'output_collision')
    h.require(path.resolve().is_relative_to(h.ROOT/'NativeUITrainer/focus_ring_runs'), 'output_boundary')
    return path


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def decoded_hash(ref):
    return decoded_identity(ref)[1]


def decoded_identity(ref):
    """Return dimensions and the historical RGBA hash from one validated decode."""
    from PIL import Image
    path = h.checked(h.ROOT, ref)
    with Image.open(path) as image:
        h.require(image.format == 'PNG' and image.width * image.height <= 20_000_000,
                  'invalid_endpoint_image')
        image.load()
        pixels = image.convert('RGBA')
        return pixels.size, hashlib.sha256(str(pixels.size).encode() + pixels.tobytes()).hexdigest()


def features(prediction):
    """Prediction-only paired measurements; labels and after truth are forbidden."""
    h.require(not {'expected', 'state', 'afterControl', 'truth'} & set(prediction), 'truth_in_features')
    tracking = prediction['tracking']
    status = tracking['status']
    if status == 'identical':
        return [0., 1., 1., 0., 0., 0., 0., 1., 1., 0., 0., 0., 0., 0., 0., 1., 1.]
    if status != 'matched' or prediction.get('illuminationWarning'):
        return None
    m = prediction.get('measurement', {})
    required = ('lumaDelta', 'edgeStrength', 'centerDrift')
    if not all(k in m for k in required) or len(m.get('ratios', [])) != 2:
        return None
    absolute = prediction.get('stability', {}).get('metrics')
    values = [m['lumaDelta'], *m['ratios'], m['edgeStrength'], m['centerDrift'],
              tracking['dx'], tracking['dy'], tracking['correlation'], tracking['peakGap']]
    if absolute is not None:
        coverage = absolute['directionalCoverage']
        h.require(all(len(coverage[k]) == 4 and all(finite(v) and 0 <= v <= 1 for v in coverage[k])
                      for k in ('arrival', 'departure')), 'invalid_directional_coverage')
        values += [absolute[k] for k in ('mean', 'p95', 'changedFraction', 'maximum')]
        h.require(all(finite(v) and 0 <= v <= 1 for v in values[-4:]), 'invalid_absolute_metrics')
        values += [min(coverage['arrival']), min(coverage['departure']), 1., 0.]
    else:
        values += [0.] * 8  # explicit availability feature is zero, not a stability assertion
    h.require(len(values) == len(FEATURES) and all(finite(v) for v in values), 'nonfinite_features')
    return values


def action_decision(rows, complete):
    """Reuse strict existing scene corroboration; no truth is supplied."""
    request = dict(version=1, context=dict(sameScene=True, settled=True,
        fresh=True, completeCoverage=complete), controls=[dict(id=r['id'],
        decision=r['decision'], identityVerified=r['identityVerified']) for r in rows])
    if not rows:
        return dict(decision='unavailable', reason='no_controls')
    return scene.corroborate(request, True, require_resolved=True)


def expected_action(rows, complete):
    if not complete or not rows or any(r['expected'] not in LABELS for r in rows):
        return None
    arrivals = [r['id'] for r in rows if r['expected'] == 'arrival']
    departures = [r['id'] for r in rows if r['expected'] == 'departure']
    if not arrivals and not departures:
        return dict(decision='unchanged')
    if len(arrivals) == len(departures) == 1:
        return dict(decision='switch', gained=arrivals[0], lost=departures[0])
    return None


def action_score(rows, complete):
    observed = action_decision(rows, complete)
    truth = expected_action(rows, complete)
    correct = None if truth is None else all(observed.get(k) == v for k, v in truth.items())
    return dict(prediction=observed, truth=truth, correct=correct,
                scorable=truth is not None, abstained=observed['decision'] in ('unavailable', 'unknown'))


def collect(sources):
    """Reconcile retained sealed reports, not invented temporal pairs or new labels."""
    h.require(isinstance(sources, list) and 1 <= len(sources) <= 16, 'source_count')
    records, actions, blocked, refs = [], [], [], []
    seen = set()
    for source in sources:
        h.require({'report', 'group'} <= set(source) <= {'report', 'group', 'endpointImages'}, 'source_fields')
        group = source['group']; h.text(group)
        image_refs = source.get('endpointImages', [])
        h.require(isinstance(image_refs, list) and len(image_refs) <= 512, 'endpoint_image_count')
        pixel_hashes = {ref['sha256']: decoded_hash(ref) for ref in image_refs}
        path = h.checked(h.ROOT, source['report'])
        d = h.read(path)
        h.require(d['version'] in ('settings-stability-v1', 'corrected-transition-audit-v1',
                                  'reference-transition-audit-v1'), 'source_version')
        h.sealed(path, d['version'])
        h.require(d.get('tracker','template')=='template','experimental_tracker_not_admitted')
        if d['version']=='settings-stability-v1' and 'baseline' in d:
            comparison=h.read(h.checked(h.ROOT,d['baseline']))
            h.require(comparison.get('tracker','template')=='template','experimental_tracker_not_admitted')
        refs.append(source['report'])
        # Raw report scores are reused, not claimed to be fresh inference or native readiness.
        rows = d.get('actions', d.get('pairs'))
        h.require(isinstance(rows, list) and len(rows) <= 256, 'action_count')
        for row in rows:
            original_id = row.get('actionID', row.get('id'))
            ident = source['report']['sha256'] + ':' + original_id
            h.require(ident not in seen, 'duplicate_action'); seen.add(ident)
            if row.get('status') == 'blocked':
                blocked.append(dict(id=ident, reason=row.get('reason'), condition=row.get('condition')))
                continue
            native = d['version'] in ('corrected-transition-audit-v1','reference-transition-audit-v1')
            if d['version']=='reference-transition-audit-v1':
                h.require(group=='fixture-procedural-renderer-v1' and
                          row['sourceAncestry']['renderer']=='fixture_procedural_renderer_v1',
                          'reference_renderer_group')
            if native:
                endpoint_hashes = [r['sha256'] for r in row['inputs'][:2]]
                for ref in row['inputs']: h.checked(h.ROOT, ref)
                for ref in row['inputs'][:2]:
                    if ref['sha256'] not in pixel_hashes:
                        pixel_hashes[ref['sha256']] = decoded_hash(ref)
                controls = row['controls']
                # Native export completeness isn't equivalent to full detector candidate coverage.
                complete = False
            else:
                endpoint_hashes = [row['endpoints'][k]['sha256'] for k in ('before', 'after')]
                controls = row['guardedControls']
                complete = row['completeEndpoints']
            action_rows = []
            h.require(isinstance(controls, list) and len(controls) <= 256, 'control_count')
            ids = set()
            for control in controls:
                cid = control['id']; h.require(cid not in ids, 'duplicate_control'); ids.add(cid)
                arm = control['arms']['guardedStability' if native else 'combined']
                label = control['expected']
                h.require(label in (*LABELS, None) and arm['expected'] == label, 'changed_label')
                h.require(arm['decision'] in scene.DECISIONS, 'invalid_decision')
                h.require(arm['scorable'] == (label is not None), 'scorable_truth_mismatch')
                h.require(arm['correct'] == (arm['decision'] == label if label is not None else None), 'changed_score')
                prediction = control['prediction']
                values = features(prediction)
                record = dict(id=ident+':'+cid, actionID=ident, controlID=cid,
                    group=group, source=source['report'], endpointHashes=endpoint_hashes,
                    decodedPixelHashes=[pixel_hashes.get(key) for key in endpoint_hashes],
                    sourceRole=row.get('sourceRole',d['partition']), trainingEligible=False,
                    label=label, baseline=arm['decision'], features=values,
                    identityVerified=control['trackingAgreesWithSemanticTarget'],
                    family=row.get('family'),condition=row.get('condition','recorded-settings'),
                    completeEndpoints=complete)
                records.append(record)
                h.require(len(records) <= 4096, 'corpus_record_limit')
                action_rows.append(dict(id=cid, expected=label, decision=arm['decision'],
                    identityVerified=record['identityVerified']))
            actions.append(dict(id=ident, group=group, condition=row.get('condition', 'recorded-settings'),
                endpointHashes=endpoint_hashes, completeEndpoints=complete,
                controlIDs=[r['id'] for r in action_rows],
                reviewedSubset=action_score(action_rows, all(r['expected'] is not None for r in action_rows)),
                fullScene=action_score(action_rows, complete)))
    result = dict(version=CORPUS, sources=sources, featureNames=list(FEATURES), records=records,
        actions=actions, blocked=blocked, sourceReports=refs,
        trainingEligible=False, independentEvaluationEligible=False,
        counts=dict(actions=len(actions), blockedActions=len(blocked), controls=len(records),
            labels=dict(Counter(r['label'] or 'unmatched' for r in records)),
            featureReady=sum(r['features'] is not None and r['label'] is not None for r in records),
            groups=len({r['group'] for r in records})),
        baseline=score_records(records, actions),
        blockers=['no_exact_transition_training_admission', 'no_independent_train_development_assignment'],
        evidenceScope='retained-report replay; native source references hash-checked; no fresh inference')
    result['corpusSHA256'] = digest(result)
    return result


def feasibility(corpus):
    """Whole-source-group support, not a split proposal or an admission decision."""
    groups=[]
    for name in sorted({r['group'] for r in corpus['records']}):
        members=[r for r in corpus['records'] if r['group']==name]
        failures=Counter()
        for row in members:
            if row['features'] is None:failures['no_pixel_features']+=1
            if row['label'] not in LABELS:failures['no_corresponding_label']+=1
            if not row['identityVerified']:failures['pixel_identity_not_supported']+=1
            if not all(row['decodedPixelHashes']):failures['missing_decoded_pixels']+=1
        usable=[r for r in members if r['features'] is not None and r['label'] in LABELS and r['identityVerified']
                and all(r['decodedPixelHashes'])]
        support=Counter(r['label'] for r in usable)
        groups.append(dict(group=name,records=len(members),usable=len(usable),labels=dict(support),
                           exclusionReasons=dict(failures),
                           missingClasses=[k for k in LABELS if not support[k]],
                           sourceRoles=sorted({r['sourceRole'] for r in members}),
                           families=sorted({r['family'] for r in members if r.get('family')})))
    covered=[g['group'] for g in groups if not g['missingClasses']]
    overlap=[]
    for i,a in enumerate(groups):
        for b in groups[i+1:]:
            pixels=lambda group:{p for r in corpus['records'] if r['group']==group for p in r['decodedPixelHashes'] if p}
            shared=pixels(a['group'])&pixels(b['group'])
            if shared:overlap.append(dict(groups=[a['group'],b['group']],sharedPixels=len(shared)))
    return dict(groups=groups,allClassGroups=covered,crossGroupDuplicatePixels=overlap,
        necessaryTwoGroupSupportPresent=len(covered)>=2 and not overlap,
        trainingEligible=False,splitAssigned=False,
        limitation='Necessary support check only; human data admission and independence review still required.')


def score_records(records, actions):
    counts = Counter()
    for r in records:
        if r['label'] is None: counts['unmatched'] += 1; continue
        counts['scorable'] += 1
        if r['baseline'] in ('unknown', 'unavailable'): counts['abstained'] += 1
        elif r['baseline'] == r['label']: counts['correct'] += 1
        else: counts['wrong'] += 1
    return dict(controls={k:counts[k] for k in ('scorable','correct','wrong','abstained','unmatched')},
        actions={kind:dict(total=len(actions), scorable=sum(a[kind]['scorable'] for a in actions),
            correct=sum(a[kind]['correct'] is True for a in actions),
            wrong=sum(a[kind]['correct'] is False and not a[kind]['abstained'] for a in actions),
            abstained=sum(a[kind]['abstained'] for a in actions)) for kind in ('reviewedSubset','fullScene')})


def load_protocol(path, arm, run_name, approval_path=None):
    doc = h.read(h.local(path))
    h.require(doc.get('version') == VERSION and doc.get('configuration') == CONFIG, 'transition_protocol_configuration')
    h.require(arm == ARM and isinstance(run_name, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', run_name), 'transition_arm_or_name')
    h.require(doc.get('protocolSHA256') == digest({k:v for k,v in doc.items() if k != 'protocolSHA256'}), 'transition_protocol_hash')
    corpus = collect(doc['sources'])
    h.require(corpus['corpusSHA256'] == doc['corpusSHA256'], 'transition_corpus_changed')
    out = fresh_run(run_name)
    blockers = []
    assignments = {}
    if doc.get('admission') is None:
        blockers.append('missing_exact_data_role_admission')
    else:
        admission = h.read(h.checked(h.ROOT, doc['admission']))
        h.require(admission.get('version') == 'focus-transition-admission-v1' and
            admission.get('corpusSHA256') == corpus['corpusSHA256'] and
            admission.get('approved') is True and admission.get('reviewer') and
            admission.get('decisionReference'), 'transition_admission_binding')
        assignments = admission['assignments']
        h.require(isinstance(assignments, dict) and set(assignments) == {r['id'] for r in corpus['records']}, 'admission_member_accounting')
        h.require(all(v in ('train', 'development', 'excluded') for v in assignments.values()), 'admission_role')
    rows = []
    group_roles, pixel_roles, action_roles = {}, {}, {}
    for original in corpus['records']:
        split = assignments.get(original['id'], 'excluded')
        if split == 'excluded': continue
        h.require(original['features'] is not None and original['label'] in LABELS and original['identityVerified'], 'unusable_training_member')
        if not all(original['decodedPixelHashes']):
            blockers.append('missing_decoded_pixel_evidence')
        for ledger, keys in ((group_roles, [original['group']]), (pixel_roles, original['endpointHashes']),
                             (pixel_roles, [v for v in original['decodedPixelHashes'] if v]),
                             (action_roles, [original['actionID']])):
            for key in keys:
                h.require(ledger.setdefault(key, split) == split, 'transition_group_or_endpoint_leakage')
        rows.append(dict(original, split=split))
    for split in ('train', 'development'):
        support = Counter(r['label'] for r in rows if r['split'] == split)
        if any(not support[k] for k in LABELS): blockers.append(split+'_missing_transition_classes')
    approval_ref = None
    if approval_path is None: blockers.append('missing_execution_approval')
    else:
        approval_ref = h.ref(h.local(approval_path)); approval = h.read(h.local(approval_path))
        h.require(approval.get('version') == 'focus-transition-approval-v1' and approval.get('approved') is True and
            approval.get('protocolSHA256') == doc['protocolSHA256'] and approval.get('arm') == ARM and
            approval.get('runName') == run_name and approval.get('decisionReference'), 'transition_execution_binding')
    return dict(formatVersion='focus-transition-preflight-v1', protocolVersion=VERSION,
        configurationValid=True, launchEligible=not blockers, blockers=sorted(set(blockers)),
        executionAuthorized=False, releaseEligible=False, configuration=CONFIG,
        protocolSHA256=doc['protocolSHA256'], protocolFile=h.ref(h.local(path)), approval=approval_ref,
        output=str(out.relative_to(h.ROOT)), arm=ARM, counts=corpus['counts'],
        corpusSHA256=corpus['corpusSHA256']), rows


def fit_head(x, y):
    """Small deterministic temporal head. Only training features set normalization."""
    import numpy as np
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.int64)
    h.require(x.ndim == 2 and x.shape[1] == len(FEATURES) and len(x) == len(y) and
        len(x) > 0 and np.isfinite(x).all() and set(y.tolist()) == {0,1,2}, 'invalid_training_tensors')
    mean = x.mean(0); scale = x.std(0); scale[scale < 1e-8] = 1.
    z = (x-mean)/scale
    w = np.random.default_rng(CONFIG['seed']).normal(0,.01,(len(FEATURES),3)); b = np.zeros(3)
    truth = np.eye(3)[y]; history = []
    for epoch in range(CONFIG['epochs']):
        logits = z@w+b; logits -= logits.max(1,keepdims=True)
        p = np.exp(logits); p /= p.sum(1,keepdims=True)
        loss = float(-np.log(np.maximum(p[np.arange(len(y)),y],1e-15)).mean())
        error = (p-truth)/len(y)
        w -= CONFIG['lr']*(z.T@error+CONFIG['l2']*w); b -= CONFIG['lr']*error.sum(0)
        h.require(np.isfinite(w).all() and np.isfinite(b).all(), 'nonfinite_update')
        history.append(dict(epoch=epoch+1, trainingLoss=loss))
    return dict(version='focus-transition-head-v1', labels=list(LABELS), featureNames=list(FEATURES),
        mean=mean.tolist(), scale=scale.tolist(), weights=w.tolist(), bias=b.tolist(),
        configuration=CONFIG, history=history)


def probabilities(model, values):
    import numpy as np
    h.require(model.get('version') == 'focus-transition-head-v1' and model['labels'] == list(LABELS)
        and model['featureNames'] == list(FEATURES), 'transition_head_contract')
    x = np.asarray(values,dtype=float); w = np.asarray(model['weights']); b = np.asarray(model['bias'])
    mean = np.asarray(model['mean']); scale = np.asarray(model['scale'])
    h.require(x.shape == (len(FEATURES),) and w.shape == (len(FEATURES),3) and b.shape == (3,) and
        mean.shape == scale.shape == x.shape and (scale>0).all() and
        all(np.isfinite(v).all() for v in (x,w,b,mean,scale)), 'invalid_head_tensors')
    logits = ((x-mean)/scale)@w+b; logits -= logits.max()
    p = np.exp(logits); p /= p.sum()
    return p.tolist()


def run(report, experiment_id):
    """Called only after existing trainer log/authorization checks; recheck all inputs."""
    start = time.monotonic()
    fresh, rows = load_protocol(h.checked(h.ROOT, report['protocolFile']), ARM,
        report['output'].split('/')[-1], h.checked(h.ROOT,report['approval']))
    h.require(fresh == report and fresh['launchEligible'], 'changed_transition_preflight')
    actions=collect(h.read(h.checked(h.ROOT,report['protocolFile']))['sources'])['actions']
    out = fresh_run(Path(report['output']).name); out.mkdir(parents=True)
    h.write(out/'execution.json', dict(experimentID=experiment_id, protocolSHA256=report['protocolSHA256'],
        configuration=CONFIG, backend='numpy-cpu', status='started'))
    train = [r for r in rows if r['split']=='train']
    model = fit_head([r['features'] for r in train],[LABELS.index(r['label']) for r in train])
    h.write(out/'last.json', model)
    results=[]
    for r in rows:
        if r['split'] != 'development': continue
        p=probabilities(model,r['features']); best=max(range(3),key=lambda i:p[i])
        results.append(dict(r, probabilities=p, rawDecision=LABELS[best],
            baseline=r['baseline'], candidate=LABELS[best] if p[best]>=CONFIG['confidence'] else 'unknown'))
    summaries={}
    for arm in ('baseline','candidate'):
        scored=[dict(r,baseline=r[arm]) for r in results]; action_results=[]
        for action in actions:
            members=[r for r in results if r['actionID']==action['id']]
            if not members: continue
            ar=[dict(id=r['controlID'],expected=r['label'],decision=r[arm],identityVerified=r['identityVerified']) for r in members]
            action_results.append(dict(reviewedSubset=action_score(ar,True),
                fullScene=action_score(ar,action['completeEndpoints'] and
                    {r['controlID'] for r in members}==set(action['controlIDs']))))
        summaries[arm]=score_records(scored,action_results)
    h.write(out/'result.json',dict(version='focus-transition-result-v1',experimentID=experiment_id,
        corpusSHA256=report['corpusSHA256'], model=h.ref(out/'last.json'), results=results,
        summaries=summaries, elapsedSeconds=time.monotonic()-start, releaseEligible=False,
        modelGatePassed=None, evidenceScope='development-only temporal head; no live qualification'))
    return 0


def predict_pair(request, model):
    """Actual two-frame pixel path; no after rectangles, identities or labels accepted."""
    h.require(set(request) == {'version','before','after','controls','context'} and
              request['version'] == 'focus-transition-request-v1', 'transition_request_fields')
    context=request['context']
    h.require(set(context)==scene.CONTEXT and all(type(v)is bool for v in context.values()), 'transition_context')
    controls=request['controls']
    h.require(isinstance(controls,list) and 0<len(controls)<=256 and
        all(set(c)=={'id','bounds'} for c in controls) and
        len({c['id'] for c in controls})==len(controls), 'transition_proposals')
    if not all(context.values()):
        return dict(version='focus-transition-prediction-v1',decision='unavailable',reason='context_unverified',
                    releaseEligible=False,controlIssued=False)
    import focus_recorded_transition_eval as evaluate
    import settings_focus_stability as stability
    predictions,runtime=evaluate.predict(request['before'],request['after'],controls)
    h.require(len(predictions)==len(controls) and {p['id'] for p in predictions}=={c['id'] for c in controls},
              'incomplete_transition_predictions')
    metrics,crop_runtime=stability.crop_metrics(request['before'],request['after'],controls,predictions)
    h.require(runtime is None or runtime==crop_runtime, 'transition_runtime_changed')
    rows=[]
    for p in predictions:
        p=dict(p,stability=dict(metrics=metrics.get(p['id'])))
        values=features(p)
        probs=probabilities(model,values) if values is not None else None
        best=max(range(3),key=lambda i:probs[i]) if probs else None
        decision=LABELS[best] if probs and probs[best]>=CONFIG['confidence'] else 'unknown'
        rows.append(dict(id=p['id'],decision=decision,probabilities=probs,
            identityVerified=p['tracking']['status'] in ('identical','matched'),tracking=p['tracking']))
    return dict(version='focus-transition-prediction-v1',controls=rows,
        scene=action_decision(rows,True),runtime=runtime or crop_runtime,
        releaseEligible=False,controlIssued=False,
        identityScope='pixel correspondence only; not authenticated control identity')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--sources');mode.add_argument('--request')
    p.add_argument('--model');p.add_argument('--output',required=True)
    a=p.parse_args();out=h.fresh(a.output)
    if a.request:
        if not a.model:p.error('--request requires --model')
        model_path=h.local(a.model);model=h.read(model_path)
        result=predict_pair(h.read(h.local(a.request)),model)
        h.write(out,dict(result,model=h.ref(model_path)));return 0
    if a.model:p.error('--model requires --request')
    report=collect(h.read(h.local(a.sources)))
    out.mkdir(parents=True);h.write(out/'audit.json',report)
    h.write(out/'feasibility.json',feasibility(report))
    protocol=dict(version=VERSION,sources=report['sources'],corpusSHA256=report['corpusSHA256'],
                  admission=None,configuration=CONFIG)
    protocol['protocolSHA256']=digest(protocol);h.write(out/'protocol.json',protocol)
    print(report['counts']);print(report['baseline']);return 0


if __name__=='__main__':
    raise SystemExit(main())
