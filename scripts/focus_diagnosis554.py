"""REALAPP554 focus diagnosis: find where focus selection fails on the 21 reviewed real-app frames.

Scores every detector proposal and every reviewed focus box with the shipped FocusRing model,
through the production crop path (`FocusRingClassifier.makeCrop`, 16% expansion, 256 x 256).
Read-only for models and policies. Reviewed labels are evaluation data: report sensitivity, do not select a threshold here.
Usage: focus_diagnosis554.py --labels REVIEWED_LABEL_DIR --out NEW_JSON [--replays REPLAYS_JSON --sessions SESSION_JSON ...]
"""
import argparse
import json
from collections import Counter
from pathlib import Path
import research_queue as q
import focus_runtime as fr
from perception_benchmark import _iou

R = q.ROOT/'reports/work/REALAPP554'
MODEL = q.ROOT/'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc'
THRESHOLD, SECONDARY = 0.85, 0.70  # Observed in the ac85177b receipts (focusring-winner-takes-all-v1).


PILOT = dict(replays=R/'replays/replays.json', sessions=[R/p for p in ('capture-newstv/session.json', 'capture-photo/session.json', 'capture-swiftfin-2/session.json')])


def frames(replays=PILOT['replays'], sessions=PILOT['sessions']):
    replays = q.load(replays)
    sessions = [q.load(p) for p in sessions]
    images = {c['id']: c for s in sessions for c in s['cases'] if c['status'] == 'captured'}
    return [(f['cases'][0], images[f['cases'][0]], q.ROOT/f['export']) for f in replays['frames']]


def score(items):
    out = {}
    for start in range(0, len(items), 100):
        reply = fr.invoke(items[start:start+100], MODEL)
        for r in reply['results']:
            out[r['id']] = r
    return out


def probability(result):
    for key in ('probability', 'focusProbability', 'score', 'focused'):
        if isinstance(result.get(key), (int, float)):
            return float(result[key])
    raise ValueError('unknown_runtime_result:'+','.join(sorted(result)))


def cause(row):
    """Name the first failing stage for a focused frame."""
    if row['partial']:
        return 'suppressed_by_invalid_proposal'
    if row['truthScore'] is not None and row['truthScore'] < SECONDARY:
        return 'focus_effect_not_recognized'
    if row['bestOverlap'] is None:
        return 'no_proposal_on_focused_control'
    if not row['overlapScored']:
        return 'overlapping_proposal_not_scored'
    if row['overlapScore'] < THRESHOLD:
        return 'proposal_below_threshold'
    if row['selectionStatus'] == 'selected':
        return 'selected_other' if row['outcome'] != 'correct' else 'correct'
    return 'competing_candidates'


def build(labels, out, replays=PILOT['replays'], sessions=PILOT['sessions']):
    items, rows = [], []
    for case_id, record, export in frames(replays, sessions):
        label = q.load(Path(labels)/f'{case_id}.json')
        result = q.load(export/'result.json')
        provider = result['receipt']['provider']
        elements = provider['elements']
        for e in elements:
            items.append(dict(id=f"{case_id}|{e['id']}", path=record['image'], sha256=record['sha256'], bounds=list(e['pixels'])))
        if label['focus']['state'] == 'focused':
            items.append(dict(id=f'{case_id}|truth', path=record['image'], sha256=record['sha256'], bounds=label['focus']['box']))
        rows.append(dict(id=case_id, label=label, provider=provider, selection=result['predictionSelection']))
    scores = score(items)
    report = []
    for row in rows:
        label, provider, selection = row['label'], row['provider'], row['selection']
        elements = provider['elements']
        ranked = sorted(((probability(scores[f"{row['id']}|{e['id']}"]), e) for e in elements), key=lambda x: -x[0])
        focus = label['focus']
        entry = dict(id=row['id'], truth=focus['state'], selectionStatus=selection.get('status'), partial=bool(provider.get('partial')),
                     attempted=provider['focus_execution']['attempted_predictions'], candidates=len(elements),
                     topScores=[dict(role=e['role'], score=round(s, 3), iouWithTruth=round(_iou(e['pixels'], focus['box']), 3) if focus['box'] else None)
                                for s, e in ranked[:3]],
                     aboveThreshold=sum(s >= THRESHOLD for s, _ in ranked), aboveSecondary=sum(s >= SECONDARY for s, _ in ranked))
        scored = [(s, e) for s, e in ranked if e['role'] != 'label']  # The runtime scores non-text proposals only.
        entry.update(scoredCandidates=len(scored), attemptedMatchesNonText=len(scored) == entry['attempted'],
                     scoredAboveThreshold=sum(s >= THRESHOLD for s, _ in scored), scoredAboveSecondary=sum(s >= SECONDARY for s, _ in scored),
                     scoredTop=[dict(role=e['role'], score=round(s, 3), iouWithTruth=round(_iou(e['pixels'], focus['box']), 3) if focus['box'] else None) for s, e in scored[:3]],
                     truthRankAmongScored=next((i+1 for i, (_, e) in enumerate(scored) if focus['box'] and _iou(e['pixels'], focus['box']) >= .5), None))
        selected = [e for e in elements if e['id'] == selection.get('id')]
        if focus['state'] == 'focused':
            overlaps = sorted(((_iou(e['pixels'], focus['box']), e) for e in elements), key=lambda x: -x[0])
            best = overlaps[0] if overlaps and overlaps[0][0] >= .5 else None
            entry.update(truthScore=round(probability(scores[f"{row['id']}|truth"]), 3),
                         bestOverlap=round(best[0], 3) if best else None, overlapRole=best[1]['role'] if best else None,
                         overlapScore=round(probability(scores[f"{row['id']}|{best[1]['id']}"]), 3) if best else None,
                         overlapScored=best[1]['role'] != 'label' if best else False,
                         outcome='correct' if selected and _iou(selected[0]['pixels'], focus['box']) >= .5 else 'other')
            entry['cause'] = cause(entry)
        else:
            entry['cause'] = 'false_selection' if selected else 'correct_abstention'
        report.append(entry)
    focused = [r for r in report if r['truth'] == 'focused']
    doc = dict(version='realapp554-focus-diagnosis-v1', labels=str(labels), replays=str(replays),
               correctSelections=sum(r.get('outcome') == 'correct' for r in focused), model=str(MODEL.relative_to(q.ROOT)), threshold=THRESHOLD,
               secondaryThreshold=SECONDARY, causes=dict(Counter(r['cause'] for r in report)),
               truthScoreAtLeast=dict((str(t), sum(r['truthScore'] >= t for r in focused)) for t in (0.5, 0.7, 0.85)),
               focusedFrames=len(focused), rows=report,
               limitation='Role "label" proposals are assumed unscored by the runtime (7 of 40 attempted). Sensitivity only; no threshold is chosen on evaluation data.')
    q.save(out, doc)
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--labels', type=Path, required=True); parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--replays', type=Path, default=PILOT['replays']); parser.add_argument('--sessions', type=Path, nargs='+', default=PILOT['sessions'])
    args = parser.parse_args()
    doc = build(args.labels, args.out, args.replays, args.sessions)
    print(json.dumps({k: doc[k] for k in ('causes', 'truthScoreAtLeast', 'focusedFrames', 'correctSelections')}, indent=1))
    for r in doc['rows']:
        print(r['id'], r['truth'], r['cause'], 'truth', r.get('truthScore'), 'overlap', r.get('overlapRole'), r.get('overlapScore'),
              'scored', r['scoredCandidates'], '=att' if r['attemptedMatchesNonText'] else f"!=att {r['attempted']}", '>=0.85', r['scoredAboveThreshold'], '>=0.70', r['scoredAboveSecondary'])


if __name__ == '__main__':
    main()
