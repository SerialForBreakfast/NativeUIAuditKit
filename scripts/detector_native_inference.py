"""Run existing detector inference on native development labels, without a prior scorecard."""
import time
import research_queue as q
from template_inputs398 import checked, pin
import detector_inference412 as inference
import detector_case_match411 as matching
from detector_native_inputs import VERSION, bounds

OUT = None


def validate(labels):
    q.require(labels.get('version') == VERSION and labels.get('role') == 'development'
              and labels.get('trainingEligible') is False, 'detector_role')
    q.require(labels.get('platform') in ('iOS','tvOS'), 'detector_platform')
    frames=labels['frames']
    q.require(0 < len(frames) <= 64 and len({r['sha256'] for r in frames}) == len(frames), 'detector_membership')
    for row in frames:
        q.require(row['image']['sha256'] == row['sha256'] and row['group'], 'detector_identity')
        checked(row['image'])
        q.require(len({c['id'] for c in row['controls']}) == len(row['controls']), 'detector_control_ids')
        for control in row['controls']:
            bounds(control['bounds'],row['width'],row['height'])
            q.require(isinstance(control['class'],str) and control['class'], 'detector_class')
    return frames


def run():
    from template_adapters395 import resolve_inputs, document
    cfg=q.load(OUT.parents[2]/'spec.json')['template']
    engine,confidence,size,kind=inference.parameters(cfg['parameters'])
    refs=resolve_inputs(cfg,OUT)
    labels=document(refs['labels']);frames=validate(labels)
    if 'baseline' in refs:
        baseline=document(refs['baseline'])
        q.require(baseline['inputs'] == {k:refs['labels'][k] for k in ('path','sha256')}, 'detector_baseline_labels')
        prior=baseline['identity']['detector']
        q.require(engine == prior.get('engine') == 'pytorch' and prior['imageSize'] == size
                  and prior['nmsIoU'] == inference.NMS_IOU, 'detector_baseline_settings')
        q.require(baseline.get('settings') == cfg['parameters'], 'detector_baseline_settings')
    q.require(engine == 'pytorch' or labels['platform'] == 'tvOS', 'detector_production_platform')
    raw=OUT/'raw';raw.mkdir()
    start=time.monotonic()
    inference.OUT=OUT
    if engine == 'pytorch':
        identity=inference.pytorch(checked(refs['model']),frames,confidence,size,raw)
    else:
        identity=inference.production(checked(refs['model']),frames,confidence,raw)
    seconds=time.monotonic()-start
    raws=[raw/('%03d.json'%i) for i in range(len(frames))]
    for path,row in zip(raws,frames):
        doc=q.load(path)
        q.require(doc['inputSHA256'] == row['sha256'] and
                  (doc['width'],doc['height']) == (row['width'],row['height']), 'detector_prediction_identity')
        q.require(doc['runtime']['detector'] == identity, 'detector_model_changed')
    q.save(OUT/'scorecard.json',dict(version='real-model-scorecard-v1',partition='development',trainingEligible=False,
        inputs={k:refs['labels'][k] for k in ('path','sha256')},rawPredictions=[pin(p) for p in raws],
        frames=[r['sha256'] for r in frames],identity=dict(detector=identity),settings=cfg['parameters']))
    bundle=dict(version='detector-case-inputs-v1',role='development',platform=labels['platform'],
        format='real-model-scorecard-v1',confidence=confidence,labelReview=labels['labelReview'],
        baseline={k:refs['baseline'][k] for k in ('path','sha256')} if 'baseline' in refs else pin(OUT/'scorecard.json'),
        candidate=pin(OUT/'scorecard.json'),
        labels={k:refs['labels'][k] for k in ('path','sha256')})
    images,predictions,meta=matching.load_bundle(bundle)
    settings=(kind,None,{},'class-aware')
    rows,extra=matching.evaluate(images,predictions,settings,confidence)
    report=matching.summarize(rows,extra,settings,meta)
    report.update(inferenceSeconds=seconds,engine=engine,imageSize=size,
        limitation='New native development baseline. Unmatched predictions are not verified false positives. No model acceptance.')
    q.save(OUT/'bundle.json',bundle)
    q.save(OUT/'benchmark_summary.json',report)
    q.save(OUT/'cases.json',dict(rows=rows,unmatchedPredictions=extra))
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in
        [OUT/n for n in ('scorecard.json','bundle.json','benchmark_summary.json','cases.json')]+raws]))
