"""RESET604 Stage 2 Focus Diagnostic: compare identical FocusRing v0.1 across detector proposals and supplied reference boxes."""
import argparse
import json
import statistics
from pathlib import Path

import real_app_benchmark543 as r543
import research_queue as q
import tvbench
from roles559 import ROLES

VERSION = 'focus-compare-604-v1'
DEFAULT_MANIFEST = q.ROOT / 'dataset/real_apps/tvbench-v1/dev-manifest-v2.json'
DEFAULT_FOCUSRING = q.ROOT / 'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc'
DEFAULT_MODELS = {
    'phase6b_tvos_v3': q.ROOT / 'NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.mlpackage',
    'pills560_r5': q.ROOT / 'NativeUITrainer/pills560-r5/final.mlpackage',
    'd1_e1_probe': q.ROOT / 'reports/work/RESET604/runs/d1-e1-probe/coreml/best.mlpackage',
}
DEFAULT_JSON_OUT = q.ROOT / 'reports/work/RESET604/focus-proposal-vs-supplied-v1.json'
DEFAULT_MD_OUT = q.ROOT / 'reports/work/RESET604/focus-proposal-vs-supplied-v1.md'


def supplied_detections(manifest, focusable_only=True):
    """Build deterministic detections dictionary from human-reviewed reference boxes only."""
    dets_by_id = {}
    for c in manifest['cases']:
        lbl = q.load(q.ROOT / c['labels']['path'])
        r543.validate_labels(lbl, c, manifest['classes'])
        dets = []
        for o in lbl['objects']:
            cls = o.get('class')
            if cls is None or o.get('visibility') == 'occluded':
                continue
            if focusable_only and not tvbench._is_focusable_class(cls, class_names=manifest['classes']):
                continue
            dets.append(dict(cls=cls, box=[float(v) for v in o['box']], score=1.0))
        dets_by_id[c['id']] = dets
    return dets_by_id


def summarize_focus_condition(name, manifest, preds, labels_by_id, control_outcomes=None):
    """Compute Stage 1 focus-box coverage and Stage 2 FocusRing outcomes by app and completeness."""
    per_app = {}
    frames = []
    recovered, lost = [], []
    scored_crops = 0
    ge_thresh = 0
    ge_999 = 0
    true_focus_probs = []
    wrong_max_probs = []

    for c in manifest['cases']:
        cid = c['id']
        app = c['app']
        lbl = labels_by_id[cid]
        f = lbl['focus']
        p = preds[cid]
        dets = p.get('detections', [])
        fexec = p.get('focusExecution') or {}
        cands = fexec.get('candidates') or []
        sel = p.get('focusBox')

        covers_any = False
        covers_focusable = False
        best_true_prob = None
        best_wrong_prob = None
        for d in dets:
            if f['state'] == 'focused' and f.get('box') and r543._iou(d['box'], f['box']) >= tvbench.MATCH_IOU:
                covers_any = True
        for cand in cands:
            prob = cand.get('probability')
            if cand.get('disposition') == 'scored' and isinstance(prob, (int, float)):
                scored_crops += 1
                if prob >= fexec.get('threshold', tvbench.DEFAULT_FOCUS_THRESHOLD):
                    ge_thresh += 1
                if prob >= 0.999:
                    ge_999 += 1
                if f['state'] == 'focused' and f.get('box') and r543._iou(cand['box'], f['box']) >= tvbench.MATCH_IOU:
                    covers_focusable = True
                    best_true_prob = prob if best_true_prob is None else max(best_true_prob, prob)
                else:
                    best_wrong_prob = prob if best_wrong_prob is None else max(best_wrong_prob, prob)
        if best_true_prob is not None:
            true_focus_probs.append(best_true_prob)
        if best_wrong_prob is not None:
            wrong_max_probs.append(best_wrong_prob)

        outcome = 'unknown'
        if f['state'] == 'no_focus':
            outcome = 'correct-abstention' if sel is None else 'false-selection'
        elif f['state'] == 'focused':
            if sel is None:
                outcome = 'abstention'
            elif r543._iou(sel, f['box']) >= tvbench.MATCH_IOU:
                outcome = 'correct'
            else:
                outcome = 'wrong-selection'

        is_win = outcome in ('correct', 'correct-abstention')
        if control_outcomes is not None and cid in control_outcomes:
            prev_win = control_outcomes[cid]
            if is_win and not prev_win:
                recovered.append(cid)
            elif prev_win and not is_win:
                lost.append(cid)

        frames.append(dict(
            id=cid,
            app=app,
            complete=bool(lbl['complete']),
            focusState=f['state'],
            outcome=outcome,
            coversTrueFocusAny=covers_any,
            coversTrueFocusFocusable=covers_focusable,
            scoredCount=len([x for x in cands if x.get('disposition') == 'scored']),
            winnerProbability=fexec.get('winnerProbability'),
        ))
        agg = per_app.setdefault(app, dict(
            frames=0, completeFrames=0, focusedFrames=0, noFocusFrames=0,
            coversTrueFocusAny=0, coversTrueFocusFocusable=0,
            correctFocused=0, wrongSelection=0, abstention=0,
            noFocusCorrectAbstention=0, noFocusFalseSelections=0,
        ))
        agg['frames'] += 1
        agg['completeFrames'] += int(bool(lbl['complete']))
        if f['state'] == 'focused':
            agg['focusedFrames'] += 1
            agg['coversTrueFocusAny'] += int(covers_any)
            agg['coversTrueFocusFocusable'] += int(covers_focusable)
            if outcome == 'correct':
                agg['correctFocused'] += 1
            elif outcome == 'wrong-selection':
                agg['wrongSelection'] += 1
            elif outcome == 'abstention':
                agg['abstention'] += 1
        elif f['state'] == 'no_focus':
            agg['noFocusFrames'] += 1
            if outcome == 'correct-abstention':
                agg['noFocusCorrectAbstention'] += 1
            else:
                agg['noFocusFalseSelections'] += 1

    def _sum_group(subset):
        return dict(
            frames=len(subset),
            focusedFrames=sum(1 for x in subset if x['focusState'] == 'focused'),
            noFocusFrames=sum(1 for x in subset if x['focusState'] == 'no_focus'),
            coversTrueFocusAny=sum(1 for x in subset if x['focusState'] == 'focused' and x['coversTrueFocusAny']),
            coversTrueFocusFocusable=sum(1 for x in subset if x['focusState'] == 'focused' and x['coversTrueFocusFocusable']),
            correctFocused=sum(1 for x in subset if x['focusState'] == 'focused' and x['outcome'] == 'correct'),
            wrongSelection=sum(1 for x in subset if x['focusState'] == 'focused' and x['outcome'] == 'wrong-selection'),
            abstention=sum(1 for x in subset if x['focusState'] == 'focused' and x['outcome'] == 'abstention'),
            noFocusCorrectAbstention=sum(1 for x in subset if x['focusState'] == 'no_focus' and x['outcome'] == 'correct-abstention'),
            noFocusFalseSelections=sum(1 for x in subset if x['focusState'] == 'no_focus' and x['outcome'] == 'false-selection'),
        )

    return dict(
        condition=name,
        overall=_sum_group(frames),
        completeOnly=_sum_group([x for x in frames if x['complete']]),
        perApp=per_app,
        recoveredVsControl=recovered,
        lostPreviousSuccessesVsControl=lost,
        cropStats=dict(
            scoredCrops=scored_crops,
            geThresholdCrops=ge_thresh,
            ge0999Crops=ge_999,
            trueFocusProbMedian=round(statistics.median(true_focus_probs), 6) if true_focus_probs else None,
            wrongMaxProbMedian=round(statistics.median(wrong_max_probs), 6) if wrong_max_probs else None,
        ),
        outcomesById={x['id']: x['outcome'] in ('correct', 'correct-abstention') for x in frames},
        frames=frames,
    )


def run_comparison(manifest_path=DEFAULT_MANIFEST, models=DEFAULT_MODELS, focusring_path=DEFAULT_FOCUSRING,
                   conf=0.25, threshold=tvbench.DEFAULT_FOCUS_THRESHOLD, nms_iou=tvbench.NMS_IOU,
                   json_out=DEFAULT_JSON_OUT, md_out=DEFAULT_MD_OUT):
    """Run identical Stage 2 FocusRing v0.1 scoring across detector proposals and supplied reference boxes."""
    manifest = q.load(manifest_path)
    labels_by_id = {c['id']: q.load(q.ROOT / c['labels']['path']) for c in manifest['cases']}
    conditions = []
    control_outcomes = None

    for name, mlpkg in models.items():
        if not Path(mlpkg).exists():
            continue
        preds = tvbench.predict_coreml(
            mlpkg, manifest['cases'], conf=conf, focusring_model=focusring_path,
            focusring_threshold=threshold, nms_iou=nms_iou,
        )
        summary = summarize_focus_condition(name, manifest, preds, labels_by_id, control_outcomes=control_outcomes)
        if control_outcomes is None:
            control_outcomes = summary['outcomesById']
        score_rep = tvbench.score_manifest(manifest, preds, map_to_roles=True)
        summary['controlsFound'] = score_rep['overall']['controlsFound']
        conditions.append(summary)

    # Supplied reference boxes (all focusable human labels; and complete-screen subset stays exact)
    sup_dets = supplied_detections(manifest, focusable_only=True)
    fr_sup = tvbench.score_focus_with_focusring(
        manifest['cases'], sup_dets, focusring_path, conf=conf, threshold=threshold, class_names=manifest['classes'],
    )
    sup_preds = {
        c['id']: dict(
            id=c['id'],
            imageSHA256=c['image']['sha256'],
            status='ok',
            detections=sup_dets[c['id']],
            focusBox=fr_sup[c['id']]['focusBox'],
            focusExecution=fr_sup[c['id']],
        )
        for c in manifest['cases']
    }
    conditions.append(summarize_focus_condition(
        'supplied_reference_focusable', manifest, sup_preds, labels_by_id, control_outcomes=control_outcomes,
    ))

    report = dict(
        version=VERSION,
        metricsStatus='provisional',
        manifest=dict(path=str(manifest_path), sha256=q.digest(manifest_path), frames=len(manifest['cases'])),
        focusRingModel=str(focusring_path),
        thresholds=dict(conf=conf, nmsIoU=nms_iou, focusThreshold=threshold),
        conditions=[{k: v for k, v in cond.items() if k != 'outcomesById'} for cond in conditions],
    )
    if json_out:
        Path(json_out).parent.mkdir(parents=True, exist_ok=True)
        q.save(json_out, report, replace=True)
    if md_out:
        lines = [
            '# RESET604 Stage 2 Focus Proposal-vs-Supplied Comparison (`provisional`)',
            '',
            f"- Manifest: `{manifest_path}` (`{len(manifest['cases'])}` frames: `36` focused, `6` `no_focus`; `23` complete frames)",
            f"- Scorer: `FocusRingDetector.mlmodelc` (`threshold={threshold}`, `nmsIoU={nms_iou}`)",
            '',
            '| Condition | Proposal Covers True Focus (Focusable) | Focused Correct | Wrong Selection | Abstention | No-Focus False Sel | Complete Subset Focus | Recovered / Lost vs v3 | Crops >= 0.85 (>= 0.999) |',
            '| --- | --- | --- | --- | --- | --- | --- | --- | --- |',
        ]
        for cond in report['conditions']:
            o = cond['overall']
            co = cond['completeOnly']
            cs = cond['cropStats']
            lines.append(
                f"| `{cond['condition']}` | {o['coversTrueFocusFocusable']} / {o['focusedFrames']} | "
                f"{o['correctFocused']} / {o['focusedFrames']} | {o['wrongSelection']} | {o['abstention']} | "
                f"{o['noFocusFalseSelections']} / {o['noFocusFrames']} | "
                f"{co['correctFocused']} / {co['focusedFrames']} (+{co['noFocusCorrectAbstention']}/{co['noFocusFrames']} nf) | "
                f"+{len(cond['recoveredVsControl'])} / -{len(cond['lostPreviousSuccessesVsControl'])} | "
                f"{cs['geThresholdCrops']} / {cs['scoredCrops']} ({cs['ge0999Crops']}) |"
            )
        Path(md_out).parent.mkdir(parents=True, exist_ok=True)
        Path(md_out).write_text('\n'.join(lines) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument('--json-out', type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument('--md-out', type=Path, default=DEFAULT_MD_OUT)
    args = parser.parse_args()
    rep = run_comparison(manifest_path=args.manifest, json_out=args.json_out, md_out=args.md_out)
    print(json.dumps([
        {k: c[k] for k in ('condition', 'overall', 'completeOnly', 'cropStats', 'recoveredVsControl', 'lostPreviousSuccessesVsControl')}
        for c in rep['conditions']
    ], indent=2))


if __name__ == '__main__':
    main()
