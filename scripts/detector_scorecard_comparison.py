"""Compare completed detector scorecards through the existing case matcher."""
import research_queue as q
from template_adapters395 import document, resolve_inputs
import detector_case_match411 as matching

OUT = None


def compare(refs, confidence):
    labels = document(refs['labels'])
    q.require(labels['role'] == 'development' and labels['trainingEligible'] is False, 'comparison_role')
    q.require(type(confidence) in (int, float) and 0 < confidence < 1, 'comparison_confidence')
    cards = [document(refs[k]) for k in ('baseline', 'candidate')]
    q.require(min(c['settings']['confidence'] for c in cards) == confidence, 'comparison_threshold_floor')
    q.require(all(c['settings']['engine'] == 'pytorch' for c in cards), 'comparison_engine')
    expected = {k: refs['labels'][k] for k in ('path', 'sha256')}
    for card in cards:
        q.require(card['inputs'] == expected, 'comparison_labels')
        q.require(card['partition'] == 'development' and card['trainingEligible'] is False, 'comparison_role')
        q.require(card['settings']['confidence'] >= confidence, 'comparison_threshold_floor')
    q.require(cards[0]['identity']['detector']['weightsSHA256'] ==
              cards[1]['identity']['detector']['weightsSHA256'], 'comparison_weights')
    q.require(cards[0]['identity']['detector']['nmsIoU'] ==
              cards[1]['identity']['detector']['nmsIoU'], 'comparison_nms')
    changes = [k for k in ('imageSize', 'confidence') if cards[0]['settings'][k] != cards[1]['settings'][k]]
    q.require(len(changes) <= 1, 'comparison_multiple_changes')
    bundle = dict(version='detector-case-inputs-v1', role='development', platform=labels['platform'],
        format='real-model-scorecard-v1', confidence=confidence, labelReview=labels['labelReview'],
        **{k: {f: refs[k][f] for f in ('path', 'sha256')} for k in ('labels', 'baseline', 'candidate')})
    images, predictions, meta = matching.load_bundle(bundle)
    settings = ('geometry', None, {}, 'class-aware')
    rows, extra = matching.evaluate(images, predictions, settings, confidence)
    report = matching.summarize(rows, extra, settings, meta)
    report.update(changedSettings=changes, settings={k:c['settings'] for k,c in zip(('baseline','candidate'), cards)},
        modelAccepted=False, limitation='Inspected native development data. Unmatched predictions are not verified false positives.')
    return report, dict(rows=rows, unmatchedPredictions=extra), bundle


def run():
    cfg = q.load(OUT.parents[2]/'spec.json')['template']
    report, cases, bundle = compare(resolve_inputs(cfg, OUT), cfg['parameters']['confidence'])
    for name, value in [('benchmark_summary.json', report), ('cases.json', cases), ('bundle.json', bundle)]:
        q.save(OUT/name, value)
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=n, sha256=q.digest(OUT/n)) for n in ('benchmark_summary.json', 'cases.json', 'bundle.json')]))
