"""REALAPP554 RA554-07: provisional real-app report against SDK-registered rectangles.

This is a diagnostic, not an accuracy result. SDK rectangles are unreviewed: they can miss controls and can be misaligned.
Only apps with SDK instrumentation get a reference comparison. Other apps report detection counts only.
Usage: real_app_provisional554.py --replays REPLAYS_JSON --sessions SESSION_JSON ... --output NEW_PREFIX
"""
import argparse
from collections import Counter
from pathlib import Path
import json
import research_queue as q

TEXT = {'label'}
IOU = 0.5


def iou(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    w = max(0.0, min(ax+aw, bx+bw)-max(ax, bx)); h = max(0.0, min(ay+ah, by+bh)-max(ay, by))
    union = aw*ah+bw*bh-w*h
    return w*h/union if union else 0.0


def greedy(references, detections):
    """Match 1 to 1 by descending IoU at or above IOU. Return matched pairs."""
    pairs = sorted(((iou(r['box'], d['box']), i, j) for i, r in enumerate(references) for j, d in enumerate(detections)), reverse=True)
    used_r, used_d, matched = set(), set(), []
    for value, i, j in pairs:
        if value < IOU:
            break
        if i not in used_r and j not in used_d:
            used_r.add(i); used_d.add(j); matched.append((i, j, value))
    return matched


def sdk_references(record, width):
    """SDK bounds are window points. Scale them to screenshot pixels."""
    elements = record['sdkBefore']['elements']
    scale = width/1920
    return [dict(id=e[0], box=[v*scale for v in (lambda b: (b['x'], b['y'], b['width'], b['height']))(json.loads(e[1]))]) for e in elements]


def case_row(record, replay):
    result = q.load(q.ROOT/replay['export']/'result.json')
    receipt = result['receipt']
    elements = receipt['provider']['elements']
    detections = [dict(role=e['role'], box=e['pixels'], score=e['confidence'], id=e['id']) for e in elements]
    controls = [d for d in detections if d['role'] not in TEXT]
    selection = result['predictionSelection']
    row = dict(id=record['id'], app=record['app'], flow=record['flow'], sha256=record['sha256'], duplicateOf=replay['cases'][0] if replay['cases'][0] != record['id'] else None,
               detections=len(detections), controlDetections=len(controls), textDetections=len(detections)-len(controls),
               roles=dict(Counter(d['role'] for d in detections)), selectionStatus=selection.get('status'),
               partial=receipt['provider'].get('partial'), latencyMs=replay.get('requestToResultDurableMS'))
    if record.get('sdkBefore'):
        references = sdk_references(record, receipt['width'])
        matched = greedy(references, controls)
        hit = {references[i]['id'] for i, _, _ in matched}
        # Text detections often cover tab and category pills. Count them separately; they are not control evidence.
        any_role = greedy(references, detections)
        row.update(matchedSDKAnyRole=len(any_role), matchedAnyRoleByDetectionRole=dict(Counter(detections[j]['role'] for _, j, _ in any_role)),
                   matchedAnyRoleByPrefix=dict(Counter(references[i]['id'].split('.')[0] for i, _, _ in any_role)),
                   matchedRoles=dict(Counter(controls[j]['role'] for _, j, _ in matched)))
        row.update(sdkControls=len(references), matchedSDK=len(matched), unmatchedSDK=sorted(r['id'] for r in references if r['id'] not in hit),
                   unmatchedControlDetections=len(controls)-len(matched), meanMatchedIoU=round(sum(v for _, _, v in matched)/len(matched), 3) if matched else None,
                   matchedByPrefix=dict(Counter(references[i]['id'].split('.')[0] for i, _, _ in matched)),
                   sdkByPrefix=dict(Counter(r['id'].split('.')[0] for r in references)))
        selected = [d for d in detections if d['id'] == selection.get('id')]
        if selected:
            best = max(((iou(selected[0]['box'], r['box']), r['id']) for r in references), default=(0, None))
            row['selectedMatchesSDK'] = best[1] if best[0] >= IOU else None
    return row


def build(replays_path, sessions, prefix):
    replays = q.load(replays_path)
    by_case = {c: f for f in replays['frames'] for c in f['cases']}
    rows = []
    for path in sessions:
        session = q.load(path)
        app = session['bundle']
        for record in session['cases']:
            if record['status'] != 'captured':
                continue
            rows.append(case_row(dict(record, app=app), by_case[record['id']]))
    apps = {}
    for app in sorted({r['app'] for r in rows}):
        group = [r for r in rows if r['app'] == app]
        distinct = [r for r in group if r['duplicateOf'] is None]
        summary = dict(cases=len(group), distinctFrames=len(distinct), detections=sum(r['detections'] for r in distinct),
                       controlDetections=sum(r['controlDetections'] for r in distinct), textDetections=sum(r['textDetections'] for r in distinct),
                       selection=dict(Counter(r['selectionStatus'] for r in distinct)),
                       latencyMs=sorted(r['latencyMs'] for r in distinct if r['latencyMs'] is not None))
        if any('sdkControls' in r for r in distinct):
            summary.update(sdkControls=sum(r['sdkControls'] for r in distinct), matchedSDK=sum(r['matchedSDK'] for r in distinct),
                           unmatchedControlDetections=sum(r['unmatchedControlDetections'] for r in distinct),
                           matchedByPrefix=dict(sum((Counter(r['matchedByPrefix']) for r in distinct), Counter())),
                           sdkByPrefix=dict(sum((Counter(r['sdkByPrefix']) for r in distinct), Counter())),
                           selectedMatchesSDK=sum(1 for r in distinct if r.get('selectedMatchesSDK')),
                           matchedSDKAnyRole=sum(r['matchedSDKAnyRole'] for r in distinct),
                           matchedAnyRoleByPrefix=dict(sum((Counter(r['matchedAnyRoleByPrefix']) for r in distinct), Counter())),
                           matchedAnyRoleByDetectionRole=dict(sum((Counter(r['matchedAnyRoleByDetectionRole']) for r in distinct), Counter())),
                           matchedRoles=dict(sum((Counter(r['matchedRoles']) for r in distinct), Counter())),
                           unmatchedSDKByPrefix=dict(Counter(i.split('.')[0] for r in distinct for i in r['unmatchedSDK'])))
        apps[app] = summary
    doc = dict(version='realapp554-provisional-v1', label='SDK-registered, unreviewed', iou=IOU, textRoles=sorted(TEXT),
               replays=replays_path and str(replays_path), sessions=[str(p) for p in sessions], apps=apps, cases=rows,
               accuracyEligible=False, modelAccepted=False,
               limitations=['SDK rectangles are unreviewed and can miss controls.', 'Duplicate frames count once in app totals.',
                            'Native focus truth is unknown. Focus selections are not scored.',
                            'Photo Guessing Game and Swiftfin have no SDK reference. Their counts are not accuracy.'])
    q.save(Path(str(prefix)+'.json'), doc)
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--replays', type=Path, required=True); parser.add_argument('--sessions', type=Path, nargs='+', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    doc = build(args.replays, args.sessions, args.output)
    print(json.dumps(doc['apps'], indent=1))


if __name__ == '__main__':
    main()
