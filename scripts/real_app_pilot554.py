"""REALAPP554 RA554-09: freeze and score the first real-app pilot.

Official benchmark: NewsTV only. It is the only app with reviewed SDK observations.
Focus diagnostic: all 21 reviewed frames, with the benchmark focus outcome rule.
Label conversion rules (reviewer validate-and-flag mode, 2026-11-01):
- An unflagged draft box in an accepted frame is reviewer-confirmed and becomes `visible`.
- A flagged box keeps its reviewer class; `not-control` and `wrong-box` stay unclassified and do not score.
- Photo Guessing Game and Swiftfin frames hold focus boxes only. They are not detection references.
Usage: real_app_pilot554.py --out NEW_DIR [--labels REVIEWED_LABEL_DIR]
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image
import research_queue as q
from experiment_templates import pin
import real_app_benchmark543 as b
import real_app_runtime553 as rt
from perception_benchmark import _iou

R = q.ROOT/'reports/work/REALAPP554'
SESSIONS = {'com.jordankoch.NewsTV': R/'capture-newstv/session.json', 'com.geoffmyers.PhotoGuessingGame': R/'capture-photo/session.json',
            'org.jellyfin.swiftfin': R/'capture-swiftfin-2/session.json'}
MODEL_MANIFEST = q.ROOT/'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/model_manifest_tvos_v1.json'
CLASSES = [m['label'] for m in q.load(MODEL_MANIFEST)['tensorChannelMapping'] if m['type'] == 'taxonomyClass']


LABELS = R/'review/labels'


def reviewed(case_id):
    label = q.load(LABELS/f'{case_id}.json')
    q.require(label['review']['status'] == 'accepted' and label['review']['blinded'] is True, 'review_not_accepted:'+case_id)
    return label


def benchmark_label(label, detection_reference):
    objects = []
    for o in label['objects']:
        flag = o.get('flag')
        visibility = 'visible' if flag is None and o['visibility'] == 'unknown' else o['visibility']
        objects.append({'id': o['id'], 'class': o['class'] if flag not in ('not-control', 'wrong-box') else None, 'box': o['box'],
                        'visibility': visibility, 'provenance': o['provenance']+('' if flag else ';reviewer:confirmed')})
    return dict(imageSHA256=label['imageSHA256'], complete=label['complete'] if detection_reference else False, objects=objects,
                focus=label['focus'], review=label['review'])


def pixels(path):
    with Image.open(path) as image:
        return hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()


def build(out):
    out = Path(out); (out/'labels').mkdir(parents=True, exist_ok=False)
    binding = q.load(R/'setup/binding.json')
    request = q.load(R/'runtime-request.json')
    runtime = R/'runtime-ac85177b.json'
    receipt = q.load(runtime)
    app = binding['apps']['com.jordankoch.NewsTV']
    qualification = out/'newstv-qualification.json'
    q.save(qualification, dict(version='real-app-qualification-v1', id='NewsTV', ancestry='github:NewsTV', sourceRevision=app['sourceRevision'],
        trainingExposure='excluded', independent=True, controlledContent=True, sdkObservationsVerified=True,
        evidence=dict(build=app, review='reports/work/REALAPP554/review/labels', scene='reports/work/REALAPP554/news-scene-ra554/trial.json'),
        note='The maintainer confirmed all 207 SDK rectangles in a blinded review on 2026-11-01. No NewsTV image is in any training set.'))
    session = q.load(SESSIONS['com.jordankoch.NewsTV'])
    replays = q.load(R/'replays/replays.json')
    first = {c: f['cases'][0] for f in replays['frames'] for c in f['cases']}
    cases = []
    for record in session['cases']:
        case = dict(id=record['id'], app='NewsTV', flow=record['flow'], group=record['group'])
        if first[record['id']] != record['id']:
            cases.append(dict(case, status='rejected', reason='duplicate pixels of '+first[record['id']])); continue
        label = benchmark_label(reviewed(record['id']), True)
        path = out/'labels'/f"{record['id']}.json"; q.save(path, label)
        image = Path(record['image'])
        with Image.open(image) as im:
            width, height = im.size
        cases.append(dict(case, status='captured', width=width, height=height, image=pin(image), pixelSHA256=pixels(image), labels=pin(path),
                          sdkEvidence=pin(R/'capture-newstv'/record['sdkBefore']['file'])))
    baseline = dict(inputMode='screenshots-only', coordinates='xywh-top-left-pixels', orientation='upright', confidence=.5, matchingIoU=.5,
                    ttrRevision=receipt['ttrRevision'], detector=request['detector'], focus=request['focus'], runtimeReceipt=pin(runtime),
                    preprocessing=request['preprocessing'], taxonomy=request['taxonomy'])
    manifest = dict(version=b.VERSION, platform='tvOS', profile='standard', phase='pilot', trainingEligible=False, classes=CLASSES,
                    baseline=baseline, apps=[dict(id='NewsTV', ancestry='github:NewsTV', kind='independent-app', trainingExposure='excluded',
                    sourceRevision=app['sourceRevision'], qualification=pin(qualification))],
                    exclusions=dict(groups=[], flows=[], images=[], pixels=[]), cases=cases)
    mp = out/'manifest.json'; q.save(mp, manifest)
    frozen = out/'freeze.json'; b.freeze(mp, frozen)
    configuration = q.text_digest(baseline)
    captured = [c for c in cases if c['status'] == 'captured']
    pr = out/'predictions-request.json'
    q.save(pr, dict(freeze=pin(frozen), configuration=configuration,
                    replays={c['id']: next(f['export'] for f in replays['frames'] if c['id'] in f['cases']) for c in captured}, failed={}))
    predictions = out/'predictions.json'; rt.predictions(pr, predictions)
    report = b.score(pin(frozen), q.load(predictions))
    q.save(out/'report.json', report)
    focus = focus_all(replays)
    q.save(out/'focus-all.json', focus)
    return report, focus


def focus_all(replays):
    """Focus diagnostic on all 21 reviewed frames. The rule matches `real_app_benchmark543.score`."""
    rows = []
    for frame in replays['frames']:
        case_id = frame['cases'][0]
        label = reviewed(case_id)
        result = q.load(q.ROOT/frame['export']/'result.json')
        selection = result['predictionSelection']
        match = [e for e in result['receipt']['provider']['elements'] if e['id'] == selection.get('id')]
        selected = list(match[0]['pixels']) if match else None
        f = label['focus']
        if f['state'] == 'unknown':
            outcome = 'unknown'
        elif f['state'] == 'no_focus':
            outcome = 'correct-abstention' if selected is None else 'false-selection'
        elif selected is None:
            outcome = 'abstention'
        else:
            outcome = 'correct' if _iou(selected, f['box']) >= .5 else 'wrong-selection'
        app = next(a for a, p in SESSIONS.items() if any(c['id'] == case_id for c in q.load(p)['cases']))
        rows.append(dict(id=case_id, app=app, truth=f['state'], selectionStatus=selection.get('status'), outcome=outcome,
                         iou=round(_iou(selected, f['box']), 3) if selected and f['state'] == 'focused' else None))
    summary = {}
    for app in sorted({r['app'] for r in rows}) + ['all']:
        group = [r for r in rows if app in ('all', r['app'])]
        known = [r for r in group if r['truth'] != 'unknown']
        counts = {k: sum(r['outcome'] == k for r in group) for k in ('correct', 'correct-abstention', 'wrong-selection', 'false-selection', 'abstention', 'unknown')}
        summary[app] = dict(frames=len(group), known=len(known), correct=counts['correct']+counts['correct-abstention'], outcomes=counts,
                            focusedFrames=sum(r['truth'] == 'focused' for r in group),
                            selectedOnFocused=sum(r['truth'] == 'focused' and r['outcome'] in ('correct', 'wrong-selection') for r in group))
    return dict(version='realapp554-focus-v1', rule='real_app_benchmark543.score focus outcome, IoU 0.5', rows=rows, summary=summary,
                limitation='Reviewer focus truth is visible focus. Partial provider results count as abstentions.')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--labels', type=Path, default=LABELS, help='Reviewed label folder (default: first review)')
    args = parser.parse_args()
    globals()['LABELS'] = args.labels.resolve()
    report, focus = build(args.out)
    o = report['overall']
    print(json.dumps(dict(captured=o['captured'], rejected=o['rejected'], missed=o['missedControls'], unmatched=o['unmatchedDetections'],
                          wrongClass=o['wrongClasses'], localization=o['localizationErrors'], focus=o['focusCounts'],
                          perClass={k: v for k, v in o['perClass'].items() if v['recall']['denominator'] or v['falseDetections']},
                          coco=report['officialCOCO'].get('metrics'), focusAll=focus['summary']), indent=1, default=str))


if __name__ == '__main__':
    main()
