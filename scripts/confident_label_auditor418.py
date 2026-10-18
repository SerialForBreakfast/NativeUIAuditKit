"""T76 adapter: Confident Learning & Tri-Modal (Consensus + Rendered-Body + OCR) Label-Completeness Auditor."""
from __future__ import annotations

import math
from collections import Counter
import research_queue as q
from sahi_wbf_inference418 import box_iou_xyxy
from template_adapters395 import document, resolve_inputs

OUT = None


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"minConfidence", "iouMatchThreshold"},
        "auditor_parameters",
    )
    conf = values["minConfidence"]
    iou = values["iouMatchThreshold"]
    q.require(
        isinstance(conf, (int, float)) and not isinstance(conf, bool) and math.isfinite(conf) and 0.10 <= conf <= 0.95,
        "auditor_confidence_range",
    )
    q.require(
        isinstance(iou, (int, float)) and not isinstance(iou, bool) and math.isfinite(iou) and 0.25 <= iou <= 0.90,
        "auditor_iou_range",
    )
    return dict(minConfidence=float(conf), iouMatchThreshold=float(iou))


def audit_unmatched_predictions_trimodal(
    primary_preds: list[dict],
    secondary_preds: list[dict],
    ground_truth: list[dict],
    rendered_bodies: list[dict],
    ocr_boxes: list[dict] | None = None,
    min_confidence: float = 0.25,
    iou_match_threshold: float = 0.50,
) -> dict[str, object]:
    """Classifies unmatched detector predictions into Tier-A missing GT labels, Tier-B review candidates, or Tier-C hallucinations."""
    ocr_boxes = ocr_boxes or []
    records = []
    for pred in primary_preds:
        score = float(pred["score"])
        if score < min_confidence:
            continue
        box = [float(v) for v in pred["box"]]
        frame_id = pred["frameId"]
        cls_name = pred["class"]

        gt_matches = [
            g for g in ground_truth
            if g["frameId"] == frame_id and box_iou_xyxy(box, g["box"]) >= iou_match_threshold
        ]
        if gt_matches:
            continue  # Already matched to ground truth

        sec_agreed = any(
            s["frameId"] == frame_id
            and s["class"] == cls_name
            and float(s.get("score", 0.0)) >= min_confidence
            and box_iou_xyxy(box, s["box"]) >= iou_match_threshold
            for s in secondary_preds
        )
        body_agreed = any(
            b["frameId"] == frame_id and box_iou_xyxy(box, b["box"]) >= iou_match_threshold
            for b in rendered_bodies
        )
        ocr_agreed = any(
            o["frameId"] == frame_id and box_iou_xyxy(box, o["box"]) >= 0.20
            for o in ocr_boxes
        )

        support_count = int(sec_agreed) + int(body_agreed) + int(ocr_agreed)
        if sec_agreed and (body_agreed or ocr_agreed):
            tier = "tier-a-missing-ground-truth"
        elif support_count >= 1:
            tier = "tier-b-ambiguous-review-queue"
        else:
            tier = "tier-c-confirmed-hallucination"

        records.append({
            "frameId": frame_id,
            "class": cls_name,
            "box": box,
            "score": score,
            "secondaryConsensus": sec_agreed,
            "renderedBodyMatch": body_agreed,
            "ocrSupport": ocr_agreed,
            "tier": tier,
            "autoRelabelApplied": False,  # Never auto-relabel evaluation data without human review
        })

    counts = Counter(r["tier"] for r in records)
    return {
        "version": "confident-label-auditor-v1",
        "unmatchedTotal": len(records),
        "tierCounts": dict(counts),
        "records": records,
        "autoRelabelApplied": False,
        "modelAccepted": False,
    }


def run() -> None:
    cfg = q.load(OUT.parents[2] / "spec.json")["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    prim = document(refs["primaryPreds"])
    sec = document(refs["secondaryPreds"])
    gt = document(refs["groundTruth"])
    bodies = document(refs["renderedBodies"])

    q.require(gt.get("role") in ("development", "calibration") and not gt.get("trainingEligible", False), "auditor_role_violation")
    result = audit_unmatched_predictions_trimodal(
        prim.get("predictions", []),
        sec.get("predictions", []),
        gt.get("labels", []),
        bodies.get("bodies", []),
        ocr_boxes=bodies.get("ocrBoxes", []),
        min_confidence=params["minConfidence"],
        iou_match_threshold=params["iouMatchThreshold"],
    )
    result["parameters"] = params
    result["inputs"] = refs
    q.save(OUT / "benchmark_summary.json", result)
    q.save(
        OUT / "artifact-receipt.json",
        {
            "version": "research-artifact-v1",
            "outputs": [{"path": "benchmark_summary.json", "sha256": q.digest(OUT / "benchmark_summary.json")}],
        },
    )
