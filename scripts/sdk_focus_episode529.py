"""Compare matched image-model outputs against native focus episodes without navigation claims."""
import math
from pathlib import Path
from collections import Counter
import research_queue as q
from experiment_templates import checked, pin
from cached_selection405 import verified_report
from sdk_episode529 import intake
from detector_case_match411 import iou

OUT = None
SUCCESS = {'correct', 'correct-abstention'}


def overlap(a, b):
    return iou([a[0], a[1], a[0]+a[2], a[1]+a[3]], [b[0], b[1], b[0]+b[2], b[1]+b[3]])


def selection(arm):
    boxes, scores = arm['boxes'], arm['scores']
    q.require(len(boxes) == len(scores) <= 128, 'episode_focus_predictions')
    for box, score in zip(boxes, scores):
        q.require(len(box) == 4 and all(type(v) in (int, float) and math.isfinite(v) for v in box) and box[2] > 0 and box[3] > 0, 'episode_focus_box')
        q.require(type(score) in (int, float) and math.isfinite(score) and 0 <= score <= 1, 'episode_focus_score')
    positive = [b for b, s in zip(boxes, scores) if s >= .85]
    return positive[0] if len(positive) == 1 else None


def visible(control):
    state = control.get('observedState') or (control.get('semanticEvidence') or {}).get('observedState') or {}
    return (state.get('hidden') is False and type(state.get('effectiveAlpha')) in (float, int) and state['effectiveAlpha'] > 0
            and control.get('geometryAvailable') is True)


def identity(control):
    return control['identity']['id'], control['identity'].get('lifetime')


def analyze(episode, predictions):
    rows = []; prior_controls = {}; retired_controls = {}; prior_truth = None; origin = None
    recovery = {name: [] for name in ('baseline', 'candidate')}
    recovered = set()
    temporal = episode['eligibility']['temporalReview']
    for index, frame in enumerate(episode['frames']):
        digest = frame['image']['sha256']
        q.require(digest in predictions, 'episode_focus_missing_prediction')
        native = {identity(c): c for c in frame['controls'] if visible(c)}
        focused = [c for c in frame['controls'] if c['identity']['id'] == frame['focusID']]
        known = frame['frameReviewable'] and frame['frameFocusState'] in ('focused', 'no_focus')
        if frame['frameFocusState'] == 'focused':
            known = known and len(focused) == 1 and visible(focused[0])
        truth = focused[0]['pixelBounds'] if known and frame['frameFocusState'] == 'focused' else None
        truth_id = identity(focused[0]) if truth is not None else None
        if known and truth_id != prior_truth:
            origin = frame['producerIntervalNS']; recovered = set()
        if known:
            retired_controls.update({key: c for key, c in prior_controls.items() if key not in native})
            retired_controls = {key: c for key, c in retired_controls.items() if key not in native}
        arms = {}
        for name in ('baseline', 'candidate'):
            chosen = selection(predictions[digest]['models'][name])
            if not known:
                outcome = 'unknown'
            elif truth is None:
                outcome = 'correct-abstention' if chosen is None else 'false-selection'
            elif chosen is None:
                outcome = 'miss'
            else:
                outcome = 'correct' if overlap(chosen, truth) >= .5 else 'wrong'
            # A box does not expose a model's internal identity. Report only unambiguous stale locations.
            departed = list(retired_controls.values())
            stale = bool(known and chosen is not None and any(overlap(chosen, c['pixelBounds']) >= .5 for c in departed)
                         and not any(overlap(chosen, c['pixelBounds']) >= .5 for c in native.values()))
            arms[name] = dict(outcome=outcome, selectedBox=chosen, staleLocationSelection=stale,
                              falseNoFocus=outcome == 'miss', falseSelection=outcome == 'false-selection')
            if temporal and known and truth_id is not None and outcome == 'correct' and name not in recovered and origin is not None:
                interval = frame['producerIntervalNS']
                if interval is not None:
                    recovery[name].append(dict(frame=index, identity=list(truth_id),
                        earliestMS=max(0, interval[0]-origin[1])/1e6,
                        latestMS=max(0, interval[1]-origin[0])/1e6))
                    recovered.add(name)
        old, new = arms['baseline']['outcome'], arms['candidate']['outcome']
        rows.append(dict(frame=index, image=frame['image'], truthIdentity=truth_id, truthKnown=known, models=arms,
                         gain=known and old not in SUCCESS and new in SUCCESS,
                         loss=known and old in SUCCESS and new not in SUCCESS,
                         newWrong=known and old not in ('wrong', 'false-selection') and new in ('wrong', 'false-selection')))
        if known:
            prior_controls = native; prior_truth = truth_id
        else:
            prior_controls = {}; retired_controls = {}; prior_truth = None; origin = None; recovered = set()
    return dict(id=episode['id'], group=episode['group'], scenario=episode['scenario'], role=episode['role'], rows=rows,
        temporalQualified=temporal, timingReasons=episode['reasons'], sampledReacquisition=recovery,
        counts={name: dict(Counter(r['models'][name]['outcome'] for r in rows)) for name in ('baseline', 'candidate')},
        gains=[r['frame'] for r in rows if r['gain']], losses=[r['frame'] for r in rows if r['loss']],
        newWrong=[r['frame'] for r in rows if r['newWrong']],
        modelAccepted=False, trainingAdmitted=False,
        limitation='Reacquisition intervals start at the first sampled new native focus, not action dispatch. Stale locations do not prove internal identity. Registered truth does not establish complete-screen coverage.')


def evaluate(request):
    q.require(set(request) == {'version', 'id', 'episodes', 'scores'} and request['version'] == 'sdk-focus-episode-v1' and q.ID.fullmatch(request['id']), 'episode_focus_request')
    source = intake(q.load(checked(request['episodes']))); predictions = {}; settings = None
    q.require(0 < len(request['scores']) <= 64, 'episode_focus_source_count')
    for ref in request['scores']:
        report = verified_report(ref)
        q.require(report['version'] == 'sdk-endpoint-focus-results-v1', 'episode_focus_source_version')
        config = q.load(checked(report['request']))
        current = dict(models=config['models'], tool=config['tool'], comparison=report.get('comparison', 'known-box'))
        for model in config['models'].values(): checked(model)
        checked(config['tool'])
        if settings is None: settings = current
        q.require(settings == current, 'episode_focus_model_or_pipeline_changed')
        for row in report['rows']:
            checked(row['image']); digest = row['image']['sha256']
            previous = predictions.setdefault(digest, row)
            q.require(previous['models'] == row['models'], 'episode_focus_conflicting_prediction')
    return dict(version='sdk-focus-episode-report-v1', episodes=[analyze(e, predictions) for e in source['episodes']],
                settings=settings, modelAccepted=False, trainingAdmitted=False)


def build(path):
    request = q.load(path); evaluate(request)
    episodes = q.load(checked(request['episodes']))
    refs = [pin(path), request['episodes']] + [r for e in episodes['episodes'] for f in e['frames'] for r in f.values()]
    refs += [r for score in request['scores'] for r in score.values()]
    refs = list({r['path']: r for r in refs}.values())
    return dict(version='research-spec-v2', id=request['id'], task='SDK529', owner='Maximum-mini-NUIAK', kind='screen', jobKind='artifact', authority='diagnostic', dependencies=[],
        inputs=refs+[pin(Path(__file__))], adapter=dict(type='python-callable', steps=['sdk_focus_episode529.run'], outputAttributes=['sdk_focus_episode529.OUT']),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100000000, maxAttempts=1), evidence=dict(reads=[r['path'] for r in refs], artifactReceipt='artifact-receipt.json'),
        question='Do matched image models preserve native focus through disappearance and return?',
        hypothesis='Native episode identity distinguishes false no-focus, wrong selections, and stale locations.',
        controlledComparison='Same images, native observations, pinned model outputs, threshold, and timing intervals.',
        decisionRule='Reject lost successes and new wrong selections. Report unavailable timing separately from frame outcomes.',
        nextActionByOutcome=dict(supported='Qualify independent dismissal and moving-background episodes.', contradicted='Use exact stale or missed frames for one matched correction.'))


def run():
    spec=q.load(OUT.parents[2]/'spec.json'); result=evaluate(q.load(checked(spec['inputs'][0])))
    q.save(OUT/'benchmark_summary.json', result)
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[dict(path='benchmark_summary.json', sha256=q.digest(OUT/'benchmark_summary.json'))]))
