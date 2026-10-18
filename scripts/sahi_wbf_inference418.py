"""T73 adapter: Scale-Gated Dual-Resolution SAHI + Weighted Box Fusion (WBF) detector inference."""
from __future__ import annotations

import math
import numpy as np
import research_queue as q
from template_adapters395 import document, resolve_inputs

OUT = None
LAYOUTS = ("full-640-only", "top-band-plus-2x2", "adaptive-row-3x2")
POLICIES = ("ungated-nms", "ungated-wbf", "scale-gated-wbf")


def parameters(values: dict) -> dict:
    q.require(
        isinstance(values, dict)
        and set(values) == {"tileLayout", "scaleGatePolicy", "wbfIouThreshold", "confidence"},
        "sahi_parameters",
    )
    layout = values["tileLayout"]
    policy = values["scaleGatePolicy"]
    iou_thr = values["wbfIouThreshold"]
    conf = values["confidence"]
    q.require(layout in LAYOUTS, "sahi_layout_unknown")
    q.require(policy in POLICIES, "sahi_policy_unknown")
    q.require(
        isinstance(iou_thr, (int, float)) and not isinstance(iou_thr, bool) and math.isfinite(iou_thr) and 0.25 <= iou_thr <= 0.90,
        "sahi_iou_range",
    )
    q.require(
        isinstance(conf, (int, float)) and not isinstance(conf, bool) and math.isfinite(conf) and 0.05 <= conf <= 0.95,
        "sahi_confidence_range",
    )
    return dict(
        tileLayout=layout,
        scaleGatePolicy=policy,
        wbfIouThreshold=float(iou_thr),
        confidence=float(conf),
    )


def box_iou_xyxy(box_a: list[float], box_b: list[float]) -> float:
    ix1 = max(box_a[0], box_b[0])
    iy1 = max(box_a[1], box_b[1])
    ix2 = min(box_a[2], box_b[2])
    iy2 = min(box_a[3], box_b[3])
    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter = iw * ih
    area_a = max(0.0, box_a[2] - box_a[0]) * max(0.0, box_a[3] - box_a[1])
    area_b = max(0.0, box_b[2] - box_b[0]) * max(0.0, box_b[3] - box_b[1])
    return inter / max(area_a + area_b - inter, 1e-7)


def scale_gated_wbf(
    full_frame_preds: list[dict],
    tile_preds: list[dict],
    frame_width: float = 1920.0,
    frame_height: float = 1080.0,
    policy: str = "scale-gated-wbf",
    iou_threshold: float = 0.55,
    confidence: float = 0.25,
) -> list[dict]:
    """Fuses full-frame 640px predictions with high-res tile predictions using receptive-field scale gating + WBF."""
    q.require(policy in POLICIES, "sahi_policy_unknown")
    frame_area = max(frame_width * frame_height, 1.0)
    candidates = []

    for pred in full_frame_preds:
        score = float(pred["score"])
        if score < confidence:
            continue
        box = [float(v) for v in pred["box"]]
        rel_area = ((box[2] - box[0]) * (box[3] - box[1])) / frame_area
        weight = 1.0
        if policy == "scale-gated-wbf" and rel_area < 0.004:
            weight = 0.50  # Down-weight tiny full-frame boxes where high-res tiles excel
        candidates.append({
            "class": pred["class"],
            "box": box,
            "score": score,
            "weight": score * weight,
            "source": "full",
        })

    for pred in tile_preds:
        score = float(pred["score"])
        if score < confidence:
            continue
        box = [float(v) for v in pred["box"]]
        tile_box = [float(v) for v in pred.get("tileBox", [0.0, 0.0, frame_width, frame_height])]
        tile_area = max((tile_box[2] - tile_box[0]) * (tile_box[3] - tile_box[1]), 1.0)
        box_area = max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])
        tile_fill = box_area / tile_area

        # Scale gate: reject truncated large cards/sheets in zoomed tiles (tile_fill > 0.35)
        if policy == "scale-gated-wbf":
            if tile_fill > 0.35:
                continue
            # Reject boxes clipped against an interior tile seam
            touches_seam = (
                (tile_box[0] > 0 and abs(box[0] - tile_box[0]) <= 2.0)
                or (tile_box[1] > 0 and abs(box[1] - tile_box[1]) <= 2.0)
                or (tile_box[2] < frame_width and abs(box[2] - tile_box[2]) <= 2.0)
                or (tile_box[3] < frame_height and abs(box[3] - tile_box[3]) <= 2.0)
            )
            if touches_seam and tile_fill > 0.12:
                continue

        candidates.append({
            "class": pred["class"],
            "box": box,
            "score": score,
            "weight": score,
            "source": "tile",
        })

    candidates.sort(key=lambda c: -c["score"])
    if policy == "ungated-nms":
        kept = []
        for cand in candidates:
            if not any(cand["class"] == k["class"] and box_iou_xyxy(cand["box"], k["box"]) >= iou_threshold for k in kept):
                kept.append(cand)
        return kept

    clusters: list[list[dict]] = []
    for cand in candidates:
        matched = False
        for cluster in clusters:
            if cluster[0]["class"] == cand["class"] and box_iou_xyxy(cand["box"], cluster[0]["box"]) >= iou_threshold:
                cluster.append(cand)
                matched = True
                break
        if not matched:
            clusters.append([cand])

    fused = []
    for cluster in clusters:
        weights = np.array([c["weight"] for c in cluster], dtype=np.float64)
        boxes = np.array([c["box"] for c in cluster], dtype=np.float64)
        w_sum = max(float(np.sum(weights)), 1e-8)
        fused_box = (np.sum(boxes * weights[:, None], axis=0) / w_sum).tolist()
        best_score = float(max(c["score"] for c in cluster))
        fused.append({
            "class": cluster[0]["class"],
            "box": [round(v, 3) for v in fused_box],
            "score": round(best_score, 5),
            "contributors": len(cluster),
            "sources": sorted({c["source"] for c in cluster}),
        })
    return fused


def run() -> None:
    cfg = q.load(OUT.parents[2] / "spec.json")["template"]
    params = parameters(cfg["parameters"])
    refs = resolve_inputs(cfg, OUT)
    model_doc = document(refs["model"])
    labels_doc = document(refs["labels"])
    q.require(labels_doc.get("role") == "development" and not labels_doc.get("trainingEligible", False), "sahi_role_violation")

    frames = labels_doc.get("frames", [])
    rows = []
    for frame in frames:
        fused = scale_gated_wbf(
            frame.get("fullPreds", []),
            frame.get("tilePreds", []) if params["tileLayout"] != "full-640-only" else [],
            frame_width=float(frame.get("width", 1920.0)),
            frame_height=float(frame.get("height", 1080.0)),
            policy=params["scaleGatePolicy"],
            iou_threshold=params["wbfIouThreshold"],
            confidence=params["confidence"],
        )
        rows.append({"id": frame["id"], "detections": fused})

    result = {
        "version": "sahi-wbf-inference-v1",
        "parameters": params,
        "modelIdentity": model_doc.get("identity", "pinned-640"),
        "frames": len(rows),
        "rows": rows,
        "modelAccepted": False,
    }
    result["inputs"] = refs
    q.save(OUT / "benchmark_summary.json", result)
    q.save(
        OUT / "artifact-receipt.json",
        {
            "version": "research-artifact-v1",
            "outputs": [{"path": "benchmark_summary.json", "sha256": q.digest(OUT / "benchmark_summary.json")}],
        },
    )
