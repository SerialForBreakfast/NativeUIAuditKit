"""Frozen real-app evaluation. References are never inference inputs; no model execution."""
import argparse
from collections import Counter, defaultdict
import contextlib
import hashlib
import html
import io
import json
import math
from pathlib import Path
import random
import statistics
import research_queue as q
from experiment_templates import checked, pin
from perception_benchmark import _box, _iou

OUT = None
VERSION = 'real-app-benchmark-v1'


def require(value, reason):
    q.require(value, 'real543_' + reason)


def read(ref):
    return q.load(checked(ref))


def ratio(n, d):
    return dict(numerator=n, denominator=d, value=n / d if d else None)


def save_new(path, value):
    path = Path(path).absolute()
    require(path.resolve().is_relative_to(q.ROOT), 'output_scope')
    require(not path.exists(), 'immutable_output')
    path.parent.mkdir(parents=True, exist_ok=True)
    q.save(path, value)


def model_identity(ref):
    path=checked(ref)
    if path.suffix == '.json':
        doc=q.load(path)
        if doc.get('version') == 'compiled-model-reference-v1':
            from observer_identity398 import compiled_digest
            root=q.local_path(q.ROOT,doc['root'])
            actual=compiled_digest(root)
            require(actual==doc['compiledSHA256'], 'compiled_model_changed')
            return actual, [pin(p) for p in sorted(root.rglob('*')) if p.is_file()]
    return ref['sha256'], [ref]


def validate(manifest, assets=True):
    require(manifest['version'] == VERSION, 'version')
    require(manifest['platform'] in ('tvOS', 'iOS') and manifest['profile'] == 'standard', 'track')
    require(manifest['phase'] in ('pilot', 'qualification'), 'phase')
    require(manifest['trainingEligible'] is False, 'training_role')
    names = manifest['classes']; require(names and len(names) == len(set(names)), 'taxonomy')
    baseline = manifest['baseline']
    for candidate in manifest.get('candidates', []):
        copy = dict(manifest, baseline=candidate, candidates=[])
        validate(copy, assets=assets)
    require(len({q.text_digest(c) for c in [baseline, *manifest.get('candidates', [])]}) == 1 + len(manifest.get('candidates', [])), 'duplicate_candidate')
    require(baseline['inputMode'] == 'screenshots-only', 'reference_leakage')
    require(baseline['coordinates'] == 'xywh-top-left-pixels' and baseline['orientation'] == 'upright', 'coordinates')
    require(0 <= baseline['confidence'] <= 1 and baseline['matchingIoU'] == .5, 'thresholds')
    require(len(baseline['ttrRevision']) == 40 and all(c in '0123456789abcdef' for c in baseline['ttrRevision']), 'revision')
    for key in ('detector', 'focus', 'runtimeReceipt', 'preprocessing', 'taxonomy'):
        if assets: checked(baseline[key])
    if assets:
        runtime=read(baseline['runtimeReceipt'])
        require(runtime.get('version') == 'real-app-runtime-v1' and runtime.get('observedLoaded') is True, 'runtime_observation')
        require(runtime.get('inputMode') == 'screenshots-only' and runtime.get('ttrRevision') == baseline['ttrRevision'], 'runtime_contract')
        for key in ('detector','focus','preprocessing','taxonomy'):
            expected=model_identity(baseline[key])[0] if key in ('detector','focus') else baseline[key]['sha256']
            require(runtime.get(key+'SHA256') == expected, 'runtime_'+key)
    apps = {a['id']: a for a in manifest['apps']}
    require(len(apps) == len(manifest['apps']) and apps, 'apps')
    ancestry = [a['ancestry'] for a in apps.values()]
    require(len(ancestry) == len(set(ancestry)), 'app_ancestry')
    for app in apps.values():
        require(app['kind'] == 'independent-app' and app['trainingExposure'] == 'excluded', 'app_qualification')
        require(app['sourceRevision'] and app['qualification'], 'app_receipt')
        if assets:
            qualification=read(app['qualification'])
            require(qualification.get('version') == 'real-app-qualification-v1', 'app_receipt_version')
            require(all(qualification.get(k)==app[k] for k in ('id','ancestry','sourceRevision','trainingExposure')), 'app_receipt_identity')
            require(all(qualification.get(k) is True for k in ('independent','controlledContent','sdkObservationsVerified')), 'app_receipt_evidence')
        require(app['id'].lower() not in ('fixture','navigationconsumer','tvtestrigfixture'), 'sample_not_independent')
    excluded = manifest['exclusions']
    ids = set(); pixels = set(); groups = defaultdict(set)
    for c in manifest['cases']:
        require(c['id'] not in ids and c['app'] in apps and c['flow'] and c['group'], 'case_identity')
        ids.add(c['id']); groups[c['app']].add(c['flow'])
        require(c['status'] in ('planned', 'captured', 'rejected', 'missing'), 'case_status')
        require(c['group'] not in excluded['groups'] and [c['app'], c['flow']] not in excluded['flows'], 'flow_leakage')
        if c['status'] != 'captured':
            require(c.get('reason'), 'missing_reason'); continue
        require(c['image']['sha256'] not in excluded['images'], 'image_leakage')
        require(c['pixelSHA256'] not in excluded['pixels'] and c['pixelSHA256'] not in pixels, 'pixel_leakage')
        pixels.add(c['pixelSHA256'])
        if assets:
            from PIL import Image
            path = checked(c['image'])
            with Image.open(path) as im:
                require(im.size == (c['width'], c['height']) and im.getexif().get(274, 1) == 1, 'image_geometry')
                require(hashlib.sha256(im.convert('RGB').tobytes()).hexdigest() == c['pixelSHA256'], 'pixel_hash')
            labels = read(c['labels']); checked(c['sdkEvidence'])
            validate_labels(labels, c, names)
    require(ids, 'empty_cases')
    if manifest['phase'] == 'qualification':
        require(len(apps) == 5 and len(ids) == 200, 'qualification_membership')
        for app in apps:
            rows = [c for c in manifest['cases'] if c['app'] == app]
            require(len(rows) == 40 and len(groups[app]) == 8 and all(n == 5 for n in Counter(c['flow'] for c in rows).values()), 'qualification_flows')
    else:
        require(len(ids) <= 50 and all(sum(c['app'] == a for c in manifest['cases']) <= 10 for a in apps), 'pilot_scope')
    return manifest


def validate_labels(labels, case, names):
    require(labels['imageSHA256'] == case['image']['sha256'], 'label_image')
    require(labels['review']['blinded'] is True and labels['review']['reviewer'] and labels['review']['status'] == 'accepted', 'human_review')
    require(type(labels['complete']) is bool, 'completeness')
    seen = set()
    for obj in labels['objects']:
        require(obj['id'] not in seen and obj['class'] in [None, *names], 'label_class')
        seen.add(obj['id']); _box(obj['box'], case['width'], case['height'])
        require(obj['visibility'] in ('visible', 'clipped', 'occluded', 'unknown'), 'visibility')
        require(obj['provenance'], 'label_provenance')
    focus = labels['focus']; require(focus['state'] in ('focused', 'no_focus', 'unknown'), 'focus_state')
    if focus['state'] == 'focused': _box(focus['box'], case['width'], case['height'])
    else: require(focus.get('box') is None, 'focus_box')


def evaluator_identity():
    from importlib.metadata import version, PackageNotFoundError
    packages={}
    for name in ('numpy','Pillow','pycocotools'):
        try: packages[name]=version(name)
        except PackageNotFoundError: packages[name]=None
    return dict(packages=packages,helpers=[pin(Path(__file__).parent/name) for name in ('perception_benchmark.py','eval_ios_r6_baseline.py','observer_identity398.py')])


def freeze(path, out):
    manifest = validate(q.load(path))
    require(all(c['status'] != 'planned' for c in manifest['cases']), 'planned_cases')
    frozen = dict(version='real-app-freeze-v1', manifest=pin(path), baselineSHA256=q.text_digest(manifest['baseline']),
                  evaluator=pin(Path(__file__)), evaluatorIdentity=evaluator_identity(), modelAccepted=False)
    save_new(out, frozen)
    # Deliberately exclude labels, SDK evidence, focus truth, and app hierarchy.
    inference = dict(version='real-app-pixels-v1', freeze=pin(out), baseline=manifest['baseline'], candidates=manifest.get('candidates', []),
                     cases=[dict(id=c['id'], image=c['image']) for c in manifest['cases'] if c['status'] == 'captured'])
    save_new(Path(out).with_name(Path(out).stem + '-pixels.json'), inference)
    return frozen


def blind_review(path, out):
    """Export draft references only. Never read a prediction artifact."""
    m = q.load(path); dest = Path(out).absolute()
    require(dest.resolve().is_relative_to(q.ROOT) and not dest.exists(), 'review_output')
    dest.mkdir(parents=True)
    cards = []
    for c in m['cases']:
        if c['status'] != 'captured': continue
        image = checked(c['image']); labels = read(c['labels']); checked(c['sdkEvidence'])
        draft = dict(imageSHA256=c['image']['sha256'], complete=False, objects=labels['objects'], focus=labels['focus'],
                     review=dict(blinded=True, reviewer='', status='pending'))
        require(q.ID.fullmatch(c['id']), 'review_id')
        save_new(dest / (c['id'] + '.json'), draft)
        cards.append('<h2>' + html.escape(c['id']) + '</h2><img style="max-width:100%" src="' + html.escape(image.as_uri(), quote=True) + '"><pre>' + html.escape(json.dumps(draft, indent=2)) + '</pre>')
    (dest / 'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Blinded reference review</title><h1>Review references before model predictions</h1><p>Check all visible controls, clipping, class uncertainty, and focus. Edit the adjacent JSON. Do not accept incomplete coverage as complete.</p>' + ''.join(cards))


def match(labels, detections, threshold):
    known = [o for o in labels['objects'] if o['class'] is not None and o['visibility'] != 'unknown']
    used = set(); found = set(); extra = []
    for d in sorted(detections, key=lambda x: -x['score']):
        eligible = [(i, _iou(d['box'], o['box'])) for i, o in enumerate(known) if i not in used and o['class'] == d['class']]
        best = max(eligible, key=lambda x: x[1], default=(None, 0))
        if best[1] >= threshold: used.add(best[0]); found.add(known[best[0]]['id'])
        else: extra.append(d)
    wrong = localized = 0
    for i, o in enumerate(known):
        if i in used: continue
        same = max((_iou(o['box'], d['box']) for d in detections if d['class'] == o['class']), default=0)
        other = max((_iou(o['box'], d['box']) for d in detections if d['class'] != o['class']), default=0)
        wrong += other >= threshold
        localized += other < threshold and 0.1 <= same < threshold
    return known, found, extra, wrong, localized


def official_ap(rows, classes):
    eligible = [r for r in rows if r.get('complete') and r['status'] == 'ok' and not r['unresolved']]
    if not eligible: return dict(status='unavailable', reason='no_complete_successful_screens', screens=0)
    try:
        from pycocotools.coco import COCO
        from pycocotools.cocoeval import COCOeval
    except ImportError:
        return dict(status='unavailable', reason='pycocotools_not_installed', screens=len(eligible))
    anns = []; preds = []; images = []
    for index, row in enumerate(eligible, 1):
        images.append(dict(id=index))
        for obj in row['objects']:
            anns.append(dict(id=len(anns)+1, image_id=index, category_id=classes.index(obj['class'])+1,
                             bbox=obj['box'], area=obj['box'][2]*obj['box'][3], iscrowd=0))
        for d in sorted(row['allDetections'], key=lambda d: -d['score']):
            preds.append(dict(image_id=index, category_id=classes.index(d['class'])+1, bbox=d['box'], score=d['score']))
    with contextlib.redirect_stdout(io.StringIO()):
        gt = COCO(); gt.dataset = dict(images=images, annotations=anns, categories=[dict(id=i+1, name=n) for i,n in enumerate(classes)], info={}); gt.createIndex()
        if preds: dt = gt.loadRes(preds)
        else:
            dt = COCO(); dt.dataset = dict(images=images, annotations=[], categories=gt.dataset['categories']); dt.createIndex()
        ev = COCOeval(gt, dt, 'bbox'); ev.evaluate(); ev.accumulate(); ev.summarize()
    values = {name: None if ev.stats[i] < 0 else float(ev.stats[i]) for name,i in [('AP50',1),('AP75',2),('AP50_95',0)]}
    return dict(status='available', evaluator='official pycocotools COCOeval', screens=len(eligible), metrics=values,
                customCrossCheck=custom_ap(eligible, classes, values),
                limitation='Complete successful screens only; execution failures remain in overall denominators. Maximum 100 detections per image and category.')


def custom_ap(rows, classes, official=None):
    """Preserve the historical all-point AP definition; COCO uses 101 recall points."""
    from eval_ios_r6_baseline import compute_ap_at_iou
    gt=defaultdict(lambda:defaultdict(list)); predictions=defaultdict(list)
    xyxy=lambda b:(b[0],b[1],b[0]+b[2],b[1]+b[3])
    for row in rows:
        for o in row['objects']: gt[classes.index(o['class'])][row['id']].append(xyxy(o['box']))
        # COCO maxDets=100 applies per image and category.
        for name in classes:
            ds=sorted((d for d in row['allDetections'] if d['class']==name),key=lambda d:-d['score'])[:100]
            predictions[classes.index(name)].extend((row['id'],d['score'],xyxy(d['box'])) for d in ds)
    for values in predictions.values(): values.sort(key=lambda d:-d[1])
    thresholds=[.5+i*.05 for i in range(10)]
    per_class={classes[c]:[compute_ap_at_iou(gt,predictions,c,t) for t in thresholds] for c in gt}
    mean=lambda values:sum(values)/len(values) if values else None
    values=dict(AP50=mean([v[0] for v in per_class.values()]),AP75=mean([v[5] for v in per_class.values()]),AP50_95=mean([mean(v) for v in per_class.values()]))
    return dict(name='historical all-point interpolated AP',metrics=values,perClass=per_class,
                officialMinusCustom={k:official[k]-v if official and official[k] is not None and v is not None else None for k,v in values.items()},
                interpretation='Identical eligible annotations and predictions. Interpolation and matching definitions differ; disagreement requires review.')


TIMING_SCOPES = {
    'end-to-end-consumer': 'Caller request through returned durable result, including transport.',
    'request-to-result-durable': 'Consumer entry through result-file durability; excludes completion receipt and IPC return.',
}


def timing_summary(values):
    values = sorted(values)
    return dict(count=len(values), median=statistics.median(values) if values else None,
                p95=values[max(0, math.ceil(.95 * len(values)) - 1)] if values else None)


def aggregate(rows, classes):
    captured = [r for r in rows if 'focusOutcome' in r]
    focus = Counter(r['focusOutcome'] for r in captured)
    per_class = {}
    for name in classes:
        truth = sum(sum(o['class']==name for o in r['objects']) for r in captured)
        tp = sum(sum(o['class']==name and o['id'] in r['detected'] for o in r['objects']) for r in captured)
        complete = [r for r in captured if r['complete'] and not r['unresolved'] and r['status']=='ok']
        ctp = sum(sum(o['class']==name and o['id'] in r['detected'] for o in r['objects']) for r in complete)
        fp = sum(sum(d['class']==name for d in r['unmatched']) for r in complete)
        per_class[name] = dict(recall=ratio(tp,truth), precision=ratio(ctp,ctp+fp), falseDetections=fp)
    known = sum(r['focusState'] != 'unknown' for r in captured)
    nofocus = [r for r in captured if r['focusState']=='no_focus']
    latency = sorted(r['latencyMs'] for r in captured if r['latencyMs'] is not None)
    return dict(planned=len(rows), captured=len(captured), executionFailures=sum(r['status']=='failed' for r in captured),
                missing=sum(r['status']=='missing' for r in rows), rejected=sum(r['status']=='rejected' for r in rows),
                focusCounts=dict(focus), correctFocus=ratio(focus['correct']+focus['correct-abstention'],known),
                falseNoFocusSelection=ratio(sum(r['focusOutcome']=='false-selection' for r in nofocus),len(nofocus)),
                noFocusExecutionFailures=sum(r['status']=='failed' for r in nofocus), perClass=per_class,
                unresolvedAnnotations=sum(r['unresolved'] for r in captured),
                missedControls=sum(len(r['objects'])-len(r['detected']) for r in captured),
                unmatchedDetections=sum(len(r['unmatched']) for r in captured),
                wrongClasses=sum(r['wrongClass'] for r in captured), localizationErrors=sum(r['localization'] for r in captured),
                latencyMs=dict(**timing_summary(latency), scope='end-to-end-consumer',
                               missing=len(captured)-len(latency)),
                timingByScope={scope: dict(**timing_summary(r['measuredLatencyMs'] for r in captured
                    if r.get('latencyScope') == scope and r.get('measuredLatencyMs') is not None),
                    definition=definition) for scope, definition in TIMING_SCOPES.items()},
                unavailableTiming=sum(r.get('latencyScope') == 'unavailable' for r in captured))


def uncertainty(rows, apps, samples=2000):
    rng = random.Random(543); draws = []
    grouped = {a: defaultdict(list) for a in apps}
    for row in rows: grouped[row['app']][row['flow']].append(row)
    for _ in range(samples):
        rates=[]
        for app in apps:
            flows=list(grouped[app].values()); sampled=[r for flow in rng.choices(flows,k=len(flows)) for r in flow] if flows else []
            known=[r for r in sampled if r.get('focusState','unknown')!='unknown']
            if known: rates.append(sum(r.get('focusOutcome') in ('correct','correct-abstention') for r in known)/len(known))
        if rates: draws.append(sum(rates)/len(rates))
    draws.sort()
    return dict(method='stratified whole-flow bootstrap within apps', samples=samples, seed=543,
                interval95=[draws[int(.025*len(draws))],draws[min(len(draws)-1,int(.975*len(draws)))]] if draws else None,
                limitation='Exploratory uncertainty within selected apps. Few apps do not establish population generalization.')


def score(frozen_ref, predictions):
    frozen=read(frozen_ref); require(frozen['version']=='real-app-freeze-v1','freeze')
    require(frozen['evaluator']==pin(Path(__file__)) and frozen['evaluatorIdentity']==evaluator_identity(), 'evaluator_changed')
    m=validate(read(frozen['manifest'])); baseline=frozen['baselineSHA256']
    require(baseline==q.text_digest(m['baseline']), 'baseline_changed')
    configurations={q.text_digest(c):c for c in [m['baseline'], *m.get('candidates', [])]}
    baseline=predictions['baselineSHA256']; require(baseline in configurations, 'undeclared_candidate')
    configuration=configurations[baseline]
    require(predictions['freeze']==frozen_ref and predictions['inputMode']=='screenshots-only', 'prediction_binding')
    byid={r['id']:r for r in predictions['cases']};expected={c['id'] for c in m['cases'] if c['status']=='captured'}
    require(len(byid)==len(predictions['cases']) and set(byid)==expected,'prediction_membership')
    rows=[]
    for c in m['cases']:
        row=dict(id=c['id'],app=c['app'],flow=c['flow'],status=c['status'])
        if c['status']!='captured':rows.append(row);continue
        labels=read(c['labels']);p=byid[c['id']]
        require(p['imageSHA256']==c['image']['sha256'] and p['baselineSHA256']==baseline,'runtime_identity')
        require(p.get('pixelSHA256') == c['pixelSHA256'], 'runtime_pixels')
        for crop in p.get('crops', []):
            checked(crop['image']); require(crop['sourceSHA256'] == c['image']['sha256'], 'crop_source')
            _box(crop['sourceBox'],c['width'],c['height'])
        require(p['status'] in ('ok','failed'),'execution_status')
        require(p.get('runtimeReceipt') == configuration['runtimeReceipt'], 'loaded_runtime')
        detections=p.get('detections',[]); selected=p.get('focusBox');latency=p.get('latencyMs')
        if p['status']=='failed':require(p.get('error') and not detections and selected is None,'failed_payload')
        else:
            require(p.get('latencyScope') in (*TIMING_SCOPES, 'unavailable'), 'latency_scope')
            if p['latencyScope'] == 'unavailable':
                require(latency is None and isinstance(p.get('latencyUnavailableReason'), str)
                        and p['latencyUnavailableReason'].strip(), 'latency_unavailable_reason')
            else:
                require(type(latency) in (int,float) and math.isfinite(latency) and latency>=0,'latency')
            for d in detections:
                _box(d['box'],c['width'],c['height']);require(d['class'] in m['classes'] and type(d['score']) in (int,float) and math.isfinite(d['score']) and 0<=d['score']<=1,'prediction_values')
            if selected is not None:_box(selected,c['width'],c['height'])
        above=[d for d in detections if d['score']>=configuration['confidence']]
        known,found,extra,wrong,loc=match(labels,above,.5)
        f=labels['focus'];outcome='unknown'
        if f['state']!='unknown':
            if p['status']=='failed':outcome='execution-failure'
            elif f['state']=='no_focus':outcome='correct-abstention' if selected is None else 'false-selection'
            elif selected is None:outcome='abstention'
            else:outcome='correct' if _iou(selected,f['box'])>=.5 else 'wrong-selection'
        row.update(missedControls=len(known)-len(found),unmatchedDetectionCount=len(extra),status=p['status'],objects=known,detected=sorted(found),unmatched=extra,wrongClass=wrong,localization=loc,
                   allDetections=detections,complete=labels['complete'],unresolved=len(labels['objects'])-len(known),
                   focusState=f['state'],focusOutcome=outcome,
                   latencyMs=latency if p['status']=='ok' and p.get('latencyScope')=='end-to-end-consumer' else None,
                   measuredLatencyMs=latency if p['status']=='ok' else None,
                   latencyScope=p.get('latencyScope') if p['status']=='ok' else 'execution-failed',
                   latencyUnavailableReason=p.get('latencyUnavailableReason') if p.get('latencyScope')=='unavailable' else None)
        rows.append(row)
    apps={a['id']:aggregate([r for r in rows if r['app']==a['id']],m['classes']) for a in m['apps']}
    for app, report in apps.items():
        report['officialCOCO']=official_ap([r for r in rows if r['app']==app],m['classes'])
    macro={}
    for name in m['classes']:
        macro[name]={}
        for metric in ('recall','precision'):
            values=[a['perClass'][name][metric]['value'] for a in apps.values() if a['perClass'][name][metric]['value'] is not None]
            macro[name][metric]=dict(value=sum(values)/len(values) if values else None,supportedApps=len(values),plannedApps=len(apps))
    rates=[a['correctFocus']['value'] for a in apps.values() if a['correctFocus']['value'] is not None]
    return dict(version='real-app-report-v1',freeze=frozen_ref,baselineSHA256=baseline,phase=m['phase'],platform=m['platform'],profile=m['profile'],
                configuration=configuration,scope='Selected real-app test population; not deployment-wide accuracy',dataRole='development' if m['phase']=='pilot' else 'independent-qualification',modelAccepted=False,rows=rows,
                overall=aggregate(rows,m['classes']),perApplication=apps,equalApplicationPerClass=macro,
                equalApplicationCorrectFocus=dict(value=sum(rates)/len(rates) if rates else None,supportedApps=len(rates),plannedApps=len(apps)),
                uncertainty=uncertainty(rows,apps),officialCOCO=official_ap(rows,m['classes']),
                historicalCustomAP='Unchanged. Not interchangeable with official COCO AP.')


def compare(left,right):
    require(left['freeze']==right['freeze'],'comparison_membership')
    a={r['id']:r for r in left['rows']};b={r['id']:r for r in right['rows']};require(a.keys()==b.keys(),'comparison_cases')
    good={'correct','correct-abstention'};bad={'wrong-selection','false-selection'}
    controls=lambda rows: {(k, control) for k,r in rows.items() for control in r.get('detected', [])}
    return dict(recoveredControls=sorted(controls(b)-controls(a)), lostControls=sorted(controls(a)-controls(b)), recovered=[k for k in a if a[k].get('focusOutcome') not in good and b[k].get('focusOutcome') in good],
                lost=[k for k in a if a[k].get('focusOutcome') in good and b[k].get('focusOutcome') not in good],
                newWrong=[k for k in a if a[k].get('focusOutcome') not in bad and b[k].get('focusOutcome') in bad],modelAccepted=False)


def build(request_path):
    r=q.load(request_path); result=score(r['freeze'],read(r['predictions']))
    frozen=read(r['freeze']);m=read(frozen['manifest'])
    if result['baselineSHA256'] != frozen['baselineSHA256']:
        prior=read(r['baselineReport'])
        require(prior['baselineSHA256']==frozen['baselineSHA256'], 'baseline_first')
        compare(prior,result)
    refs=[pin(request_path),r['freeze'],r['predictions'],frozen['manifest'],pin(Path(__file__))]
    refs += [ref for config in [m['baseline'], *m.get('candidates', [])] for ref in config.values() if isinstance(ref,dict) and 'sha256' in ref]
    if 'baselineReport' in r: refs.append(r['baselineReport'])
    for config in [m['baseline'], *m.get('candidates', [])]:
        for key in ('detector','focus'): refs.extend(model_identity(config[key])[1])
    refs += [a['qualification'] for a in m['apps']]
    refs += [c[k] for c in m['cases'] if c['status']=='captured' for k in ('image','labels','sdkEvidence')]
    refs=list({r['path']:r for r in refs}.values())
    return dict(version='research-spec-v2',id=r['id'],task='REAL543',owner='Maximum-mini-NUIAK',kind='screen',jobKind='artifact',authority='diagnostic',dependencies=[],inputs=refs,
                adapter=dict(type='python-callable',steps=['real_app_benchmark543.run'],outputAttributes=['real_app_benchmark543.OUT']),
                limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),evidence=dict(reads=[r['path'] for r in refs],artifactReceipt='artifact-receipt.json'),
                question='How well does the frozen consumer perform on blinded real-app references?',hypothesis='Independent labels expose consumer errors hidden by generated-screen metrics.',controlledComparison='Fixed screenshots, native references, models and runtime. No training or tuning.',decisionRule='Report every planned case, failures and unavailable metrics. Do not promote.',nextActionByOutcome=dict(supported='Review case-linked failures before separate development work.',contradicted='Repair invalid evidence without removing failed cases.'))


def run():
    spec=q.load(OUT.parents[2]/'spec.json');r=read(spec['inputs'][0]);report=score(r['freeze'],read(r['predictions']))
    if 'baselineReport' in r: report['comparison']=compare(read(r['baselineReport']),report)
    q.save(OUT/'benchmark_summary.json',report)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))


def audit_replay(path, out):
    """Check retained TTR exports. This does not qualify labels or model accuracy."""
    from PIL import Image
    root = Path(path).resolve()
    require(root.is_relative_to(q.ROOT), 'replay_scope')
    completion = q.load(root / 'completion.json')
    require(completion.get('completed') is True, 'replay_incomplete')
    for filename, key in (('source.png', 'source_sha256'), ('input-manifest.json', 'input_manifest_sha256'), ('result.json', 'result_sha256')):
        file = root / filename
        require(file.resolve().is_relative_to(root) and file.is_file(), 'replay_file')
        require(q.digest(file) == completion.get(key), 'replay_hash')
    result = q.load(root / 'result.json')
    receipt = result['receipt']
    manifest = q.load(root / 'input-manifest.json')
    require(manifest.get('source_sha256') == completion['source_sha256'] == receipt.get('image_sha256'), 'replay_source')
    require(set(manifest) <= {'source_sha256', 'declared_provenance'}, 'replay_reference_leakage')
    require(result.get('action_authorized') is False and receipt.get('action_authorized') is False, 'replay_action')
    with Image.open(root / 'source.png') as image:
        require(image.size == (receipt['width'], receipt['height']) and image.getexif().get(274, 1) == 1, 'replay_geometry')
    provider = receipt.get('provider') or {}
    selection = result.get('predictionSelection', {})
    elements = provider.get('elements', [])
    selected = selection.get('id')
    if selected is not None:
        matching = [e for e in elements if e.get('id') == selected]
        require(selection.get('status') == 'selected' and len(matching) == 1, 'replay_selection')
        require(provider.get('partial') is False and provider.get('focus_execution', {}).get('model_scoring_complete') is True, 'replay_selection')
        require(matching[0].get('focused') is True and matching[0].get('ambiguous') is False, 'replay_selection')
    else:
        require(selection.get('status') != 'selected', 'replay_selection')
    report = dict(version='real-app-replay-audit-v1', exportIntegrityVerified=True, accuracyEligible=False,
                  accuracyLimitation='Requires frozen runtime, application qualification, and reviewed reference labels.',
                  sourceSHA256=completion['source_sha256'], providerPartial=provider.get('partial'), selection=selection,
                  validElements=len(elements), rejectedGeometry=len(provider.get('rejected_geometry') or {}),
                  observedDetector=provider.get('detector_artifact_digest'), observedFocus=provider.get('focus_model'),
                  observedTTR=result.get('ttr_observed'), unavailableProvenance=result.get('unavailable_provenance', []),
                  latencyScope='request-to-result-durable', latencyMs=completion.get('request_to_result_durable_ms'),
                  timingExcludes=completion.get('timing_excludes', []), receipt=pin(root / 'result.json'))
    save_new(out, report)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['freeze','review','report','compile','audit-replay']);parser.add_argument('input',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.command=='audit-replay':audit_replay(args.input,args.output)
    elif args.command=='freeze':freeze(args.input,args.output)
    elif args.command=='review':blind_review(args.input,args.output)
    elif args.command=='compile':save_new(args.output,build(args.input))
    else:
        r=q.load(args.input);save_new(args.output,score(r['freeze'],read(r['predictions'])))

if __name__=='__main__':main()
