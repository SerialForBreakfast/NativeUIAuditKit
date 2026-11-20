"""RESET604 Correction 5: Compare shipping Swift `nativeui-audit` vs Python `tvbench.py` on retained dev frames.

Checks per-frame parity across:
- input SHA-256 and model identities/digests
- Stage 1 detections (counts, matched IoU, score diffs, unmatched counts)
- Stage 2 FocusRing eligible proposals, dispositions, probabilities, crop hashes, winners, abstentions, failures
- Execution timings per frame

Usage:
  .venv-coreml/bin/python scripts/tvbench_parity604.py [--manifest dataset/real_apps/tvbench-v1/dev-manifest.json]
"""
import argparse
import json
import statistics
import subprocess
import time
from pathlib import Path

import real_app_benchmark543 as r543
import research_queue as q
import tvbench

VERSION = 'tvbench-parity-v1'
DEFAULT_MANIFEST = q.ROOT / 'dataset/real_apps/tvbench-v1/dev-manifest.json'
DEFAULT_AUDIT_BIN = q.ROOT / '.build/swift-check/debug/nativeui-audit'
DEFAULT_MLPACKAGE = q.ROOT / 'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIModel_tvOS.mlpackage'
DEFAULT_FOCUSRING = q.ROOT / 'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc'
DEFAULT_JSON_OUT = q.ROOT / 'reports/work/RESET604/parity-report-v1.json'
DEFAULT_MD_OUT = q.ROOT / 'reports/work/RESET604/parity-report-v1.md'


def _compiled_digest(path):
    from observer_identity398 import compiled_digest
    p = Path(path)
    return compiled_digest(p) if p.is_dir() else q.digest(p)


def run_swift_scan(audit_bin, image_rel_path, conf=0.25, comparative_focus_dir=None, comparative_gate_threshold=0.28):
    """Execute Swift `nativeui-audit scan` with explicit tvOS platform, conf, and --no-ocr."""
    cmd = [
        str(audit_bin), 'scan', str(image_rel_path),
        '--root', str(q.ROOT),
        '--platform', 'tvOS',
        '--min-confidence', str(conf),
        '--no-ocr',
        '--format', 'json',
    ]
    if comparative_focus_dir is not None:
        cmd.extend(['--comparative-focus-dir', str(comparative_focus_dir), '--comparative-gate-threshold', str(comparative_gate_threshold)])
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    q.require(res.returncode == 0 and res.stdout.strip().startswith('{'), f'swift_audit_failed:{image_rel_path}:{res.stderr[-300:]}')
    return json.loads(res.stdout)


def extract_swift_case(swift_doc):
    """Normalize Swift `nativeui-audit` JSON payload for structured comparison."""
    rt = swift_doc['runtime']
    res = rt['result']
    elements = res['elements']
    focus_exec = res.get('focusExecution') or {}
    cands_by_id = {c['observationID']: c for c in focus_exec.get('candidates', [])}
    dets = []
    focused_boxes = []
    for el in elements:
        bp = el['boundingBoxPixels']
        box = [float(bp['x']), float(bp['y']), float(bp['width']), float(bp['height'])]
        dets.append(dict(cls=el['elementType'], box=box, score=float(el['confidence']), id=el['id']))
        if (el.get('state') or {}).get('isFocused') is True:
            focused_boxes.append((box, (el.get('state') or {}).get('focusScore')))
    winner_box = focused_boxes[0][0] if focused_boxes else None
    winner_prob = focused_boxes[0][1] if focused_boxes else None
    disps = [c.get('disposition') for c in focus_exec.get('candidates', [])]
    probs = [c.get('probability') for c in focus_exec.get('candidates', []) if isinstance(c.get('probability'), (int, float))]
    return dict(
        inputSHA256=swift_doc['inputSHA256'],
        status=swift_doc['status'],
        detectorDigest=(rt.get('detector') or {}).get('treeSHA256'),
        focusDigest=focus_exec.get('modelDigest'),
        focusBackend=focus_exec.get('backend'),
        threshold=focus_exec.get('threshold'),
        secondaryThreshold=focus_exec.get('secondaryThreshold'),
        detections=dets,
        focusBox=winner_box,
        winnerProbability=winner_prob,
        maxProbability=max(probs) if probs else None,
        eligibleCount=sum(1 for d in disps if d != 'unsupportedRole'),
        scoredCount=sum(1 for d in disps if d == 'scored'),
        unsupportedRoleCount=sum(1 for d in disps if d == 'unsupportedRole'),
        cropRejectedCount=sum(1 for d in disps if d == 'cropRejected'),
        failedCount=sum(1 for d in disps if d == 'predictionFailed'),
        timings=dict(
            totalMs=swift_doc.get('totalMs'),
            modelLoadMs=rt.get('modelLoadMs'),
            timings=res.get('timings'),
        ),
        candidates=[
            dict(
                cls=next((e['elementType'] for e in elements if e['id'] == cid), None),
                disposition=c.get('disposition'),
                probability=c.get('probability'),
                isFocused=c.get('isFocused'),
            )
            for cid, c in cands_by_id.items()
        ],
    )


def compare_detections(swift_dets, py_dets, iou_threshold=0.5):
    """Greedily match same-class detections by score and return alignment statistics."""
    used = set()
    ious, score_diffs = [], []
    for sd in sorted(swift_dets, key=lambda d: -d['score']):
        best_iou, best_idx = 0.0, None
        for idx, pd in enumerate(py_dets):
            if idx not in used and pd['cls'] == sd['cls']:
                iou = r543._iou(sd['box'], pd['box'])
                if iou > best_iou:
                    best_iou, best_idx = iou, idx
        if best_idx is not None and best_iou >= iou_threshold:
            used.add(best_idx)
            ious.append(best_iou)
            score_diffs.append(abs(sd['score'] - py_dets[best_idx]['score']))
    return dict(
        swiftCount=len(swift_dets),
        pythonCount=len(py_dets),
        matched=len(ious),
        swiftUnmatched=len(swift_dets) - len(ious),
        pythonUnmatched=len(py_dets) - len(ious),
        medianIoU=round(statistics.median(ious), 6) if ious else None,
        minIoU=round(min(ious), 6) if ious else None,
        maxScoreDiff=round(max(score_diffs), 6) if score_diffs else None,
    )


def compare_frame_pair(case_id, swift_rec, py_rec):
    """Compare one frame across Swift and Python Stage 1 + Stage 2 paths."""
    det_cmp = compare_detections(swift_rec['detections'], py_rec['detections'])
    py_fx = py_rec.get('focusExecution') or {}
    s_box = swift_rec.get('focusBox')
    p_box = py_rec.get('focusBox')
    if s_box is None and p_box is None:
        winner_match = True
        winner_iou = None
    elif s_box is not None and p_box is not None:
        winner_iou = round(r543._iou(s_box, p_box), 6)
        winner_match = winner_iou >= 0.99
    else:
        winner_iou = 0.0
        winner_match = False

    s_prob = swift_rec.get('maxProbability')
    p_prob = py_fx.get('maxProbability')
    max_prob_diff = round(abs(s_prob - p_prob), 6) if (s_prob is not None and p_prob is not None) else None

    return dict(
        id=case_id,
        inputHashMatch=(swift_rec['inputSHA256'] == py_rec['imageSHA256']),
        detections=det_cmp,
        eligibleCountMatch=(swift_rec['eligibleCount'] == py_fx.get('eligibleCount')),
        swiftEligible=swift_rec['eligibleCount'],
        pythonEligible=py_fx.get('eligibleCount'),
        swiftScored=swift_rec['scoredCount'],
        pythonScored=py_fx.get('scoredCount'),
        swiftUnsupported=swift_rec['unsupportedRoleCount'],
        pythonUnsupported=py_fx.get('unsupportedRoleCount'),
        swiftCropRejected=swift_rec['cropRejectedCount'],
        pythonCropRejected=py_fx.get('cropRejectedCount'),
        swiftFailed=swift_rec['failedCount'],
        pythonFailed=py_fx.get('failedCount'),
        winnerMatch=winner_match,
        winnerIoU=winner_iou,
        swiftWinner=(s_box is not None),
        pythonWinner=(p_box is not None),
        swiftMaxProb=s_prob,
        pythonMaxProb=p_prob,
        maxProbDiff=max_prob_diff,
        pythonCropHashesPresent=sum(
            1 for c in py_fx.get('candidates', []) if c.get('disposition') == 'scored' and c.get('modelInputRGBSHA256')
        ),
        swiftMs=swift_rec['timings'].get('totalMs'),
    )


def run_parity(
    manifest_path=DEFAULT_MANIFEST,
    audit_bin=DEFAULT_AUDIT_BIN,
    mlpackage=DEFAULT_MLPACKAGE,
    focusring_model=DEFAULT_FOCUSRING,
    conf=0.25,
    nms_iou=tvbench.NMS_IOU,
    comparative_focus_dir=None,
    comparative_gate_threshold=0.28,
    json_out=DEFAULT_JSON_OUT,
    md_out=DEFAULT_MD_OUT,
):
    manifest = q.load(manifest_path)
    q.require(not manifest.get('sealed'), 'parity_must_run_on_dev_only')
    cases = [c for c in manifest['cases'] if c.get('status', 'captured') == 'captured']

    t0 = time.monotonic()
    if comparative_focus_dir is not None:
        import coremltools as ct
        import comparative_focus604 as cf
        comp_dir = Path(comparative_focus_dir)
        model = ct.models.MLModel(str(mlpackage))
        cnames = tvbench.model_class_names(model)
        dets_by_id = tvbench._coreml_predict_preproc_keyed(model, cnames, cases, conf=conf, nms_iou=nms_iou)
        coreml_paths = dict(
            scorerPackage=str(comp_dir / 'ComparativeFocusScorer.mlpackage'),
            gatePackage=str(comp_dir / 'ComparativeFocusGate.mlpackage'),
        )
        py_preds = cf.predict_comparative_on_detections(
            dict(gateThreshold=comparative_gate_threshold),
            cases, dets_by_id, class_names=cnames, use_gate=True, coreml_paths=coreml_paths,
            gate_threshold=comparative_gate_threshold,
        )
    else:
        py_preds = tvbench.predict_coreml(
            mlpackage, cases, conf=conf, focusring_model=focusring_model, nms_iou=nms_iou,
        )
    py_total_s = round(time.monotonic() - t0, 3)

    t1 = time.monotonic()
    swift_recs = {}
    for c in cases:
        raw = run_swift_scan(
            audit_bin, c['image']['path'], conf=conf,
            comparative_focus_dir=comparative_focus_dir,
            comparative_gate_threshold=comparative_gate_threshold,
        )
        swift_recs[c['id']] = extract_swift_case(raw)
    swift_total_s = round(time.monotonic() - t1, 3)

    rows = [compare_frame_pair(c['id'], swift_recs[c['id']], py_preds[c['id']]) for c in cases]
    summary = dict(
        frames=len(rows),
        inputHashMatches=sum(r['inputHashMatch'] for r in rows),
        exactDetectionCountMatches=sum(r['detections']['swiftCount'] == r['detections']['pythonCount'] for r in rows),
        zeroUnmatchedDetectionFrames=sum(
            r['detections']['swiftUnmatched'] == 0 and r['detections']['pythonUnmatched'] == 0 for r in rows
        ),
        eligibleCountMatches=sum(r['eligibleCountMatch'] for r in rows),
        winnerMatches=sum(r['winnerMatch'] for r in rows),
        swiftWinners=sum(r['swiftWinner'] for r in rows),
        pythonWinners=sum(r['pythonWinner'] for r in rows),
        totalSwiftScoredCrops=sum(r['swiftScored'] for r in rows),
        totalPythonScoredCrops=sum(r['pythonScored'] for r in rows),
        totalPythonCropHashesPresent=sum(r['pythonCropHashesPresent'] for r in rows),
        totalSwiftUnsupported=sum(r['swiftUnsupported'] for r in rows),
        totalPythonUnsupported=sum(r['pythonUnsupported'] for r in rows),
        totalSwiftCropRejected=sum(r['swiftCropRejected'] for r in rows),
        totalPythonCropRejected=sum(r['pythonCropRejected'] for r in rows),
        totalSwiftFailed=sum(r['swiftFailed'] for r in rows),
        totalPythonFailed=sum(r['pythonFailed'] for r in rows),
        maxFocusProbDiff=max((r['maxProbDiff'] for r in rows if r['maxProbDiff'] is not None), default=None),
        pythonWallSeconds=py_total_s,
        swiftWallSeconds=swift_total_s,
    )

    first_swift = next(iter(swift_recs.values()))
    report = dict(
        version=VERSION,
        manifest=dict(path=str(manifest_path), sha256=q.digest(manifest_path)),
        models=dict(
            swiftDetectorDigest=first_swift['detectorDigest'],
            swiftFocusDigest=first_swift['focusDigest'],
            pythonMlpackageSHA256=_compiled_digest(mlpackage),
            pythonFocusModelSHA256=_compiled_digest(focusring_model),
            pythonSubmittedCropHashing='FocusRingTool modelInputRGBSHA256',
            swiftSubmittedCropHashing='unavailable_in_nativeui_audit_json',
        ),
        thresholds=dict(confidence=conf, nmsIoU=nms_iou, focusThreshold=tvbench.DEFAULT_FOCUS_THRESHOLD, ambiguityThreshold=tvbench.DEFAULT_AMBIGUITY_THRESHOLD),
        summary=summary,
        divergentFrames=[r for r in rows if not r['winnerMatch'] or not r['eligibleCountMatch'] or r['detections']['swiftUnmatched'] or r['detections']['pythonUnmatched']],
        rows=rows,
    )
    if json_out:
        Path(json_out).parent.mkdir(parents=True, exist_ok=True)
        q.save(json_out, report, replace=True)
    if md_out:
        lines = [
            '# RESET604 Retained-Frame Parity Report (`tvbench-parity-v1`)',
            '',
            f"- Manifest: `{manifest_path}` (`{summary['frames']}` development frames)",
            f"- Swift `nativeui-audit` (`--platform tvOS --min-confidence {conf} --no-ocr`) vs Python `tvbench.py` (`nmsIoU={nms_iou}`)",
            f"- Input SHA-256 matches: **{summary['inputHashMatches']} / {summary['frames']}**",
            f"- Zero-unmatched Stage 1 frames: **{summary['zeroUnmatchedDetectionFrames']} / {summary['frames']}**",
            f"- Stage 2 eligible proposal count matches: **{summary['eligibleCountMatches']} / {summary['frames']}** (Swift scored `{summary['totalSwiftScoredCrops']}`, Python scored `{summary['totalPythonScoredCrops']}`, unsupported skipped: Swift `{summary['totalSwiftUnsupported']}` vs Python `{summary['totalPythonUnsupported']}`)",
            f"- Focus winner/abstention parity: **{summary['winnerMatches']} / {summary['frames']}** (Swift winners `{summary['swiftWinners']}`, Python winners `{summary['pythonWinners']}`, max focus prob diff `{summary['maxFocusProbDiff']}`)",
            f"- Failures: Swift `{summary['totalSwiftFailed']}`, Python `{summary['totalPythonFailed']}`; crop rejections: Swift `{summary['totalSwiftCropRejected']}`, Python `{summary['totalPythonCropRejected']}`",
            f"- Python `FocusRingTool` recorded `modelInputRGBSHA256` on `{summary['totalPythonCropHashesPresent']} / {summary['totalPythonScoredCrops']}` scored crops (`nativeui-audit` JSON omits per-crop buffer digests).",
            f"- Timings: Python `{py_total_s} s`, Swift CLI (42 cold/warm invocations) `{swift_total_s} s`.",
        ]
        Path(md_out).parent.mkdir(parents=True, exist_ok=True)
        Path(md_out).write_text('\n'.join(lines) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument('--audit-bin', type=Path, default=DEFAULT_AUDIT_BIN)
    parser.add_argument('--mlpackage', type=Path, default=DEFAULT_MLPACKAGE)
    parser.add_argument('--focusring', type=Path, default=DEFAULT_FOCUSRING)
    parser.add_argument('--conf', type=float, default=0.25)
    parser.add_argument('--nms-iou', type=float, default=tvbench.NMS_IOU)
    parser.add_argument('--comparative-focus-dir', type=Path, default=None)
    parser.add_argument('--comparative-gate-threshold', type=float, default=0.28)
    parser.add_argument('--json-out', type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument('--md-out', type=Path, default=DEFAULT_MD_OUT)
    args = parser.parse_args()
    rep = run_parity(
        manifest_path=args.manifest,
        audit_bin=args.audit_bin,
        mlpackage=args.mlpackage,
        focusring_model=args.focusring,
        conf=args.conf,
        nms_iou=args.nms_iou,
        comparative_focus_dir=args.comparative_focus_dir,
        comparative_gate_threshold=args.comparative_gate_threshold,
        json_out=args.json_out,
        md_out=args.md_out,
    )
    print(json.dumps(rep['summary'], indent=2))


if __name__ == '__main__':
    main()
