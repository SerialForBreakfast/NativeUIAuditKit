#!/usr/bin/env python3
"""
eval_tvos_model.py — Evaluate NativeUIModel_tvOS on held-out OS UI test set.

Evaluates:
  1. Object detection metrics (Precision, Recall, mAP@0.5, mAP@0.5:0.95) across all OS UI classes.
  2. Active focus identification accuracy against ground truth sidecar annotations.
  3. Writes JSON evaluation report to reports/eval_results_tvos_v0.json.

Usage:
  .venv-yolo/bin/python scripts/eval_tvos_model.py
  .venv-yolo/bin/python scripts/eval_tvos_model.py --weights NativeUITrainer/yolo_runs/phase6b_tvos_v0/weights/best.pt
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WEIGHTS = PROJECT_ROOT / "NativeUITrainer" / "yolo_runs" / "phase6b_tvos_v0" / "weights" / "best.pt"
DEFAULT_YAML = PROJECT_ROOT / "NativeUITrainer" / "yolo_dataset_tvos" / "dataset.yaml"
TEST_DATASET_DIR = PROJECT_ROOT / "dataset" / "tvos_dataset" / "test"
REPORTS_DIR = PROJECT_ROOT / "reports"

os_env_defaults = {
    "YOLO_CONFIG_DIR": str(PROJECT_ROOT / "NativeUITrainer" / ".ultralytics"),
    "MPLCONFIGDIR": str(PROJECT_ROOT / "NativeUITrainer" / ".mplconfig"),
    "TORCH_HOME": str(PROJECT_ROOT / "NativeUITrainer" / ".torch"),
}
for k, v in os_env_defaults.items():
    os.environ[k] = v
    Path(v).mkdir(parents=True, exist_ok=True)


def parse_args():
    p = argparse.ArgumentParser(description="Evaluate tvOS OS UI detector")
    p.add_argument("--weights", default=str(DEFAULT_WEIGHTS), help="Path to best.pt")
    p.add_argument("--dataset", default=str(DEFAULT_YAML), help="Path to dataset.yaml")
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--device", default="mps")
    p.add_argument("--report", default=str(REPORTS_DIR / "eval_results_tvos_v0.json"))
    return p.parse_args()


def evaluate_focus_accuracy(model, test_dir: Path):
    """
    Check if the model's highest-luminance interactive detection correctly matches
    the ground truth element marked with isFocused: true.
    """
    json_files = sorted(test_dir.glob("*.json"))
    if not json_files:
        print(f"No sidecar JSON files found in {test_dir}")
        return None

    total_with_focus = 0
    correct_focus = 0

    for jf in json_files:
        with open(jf, "r", encoding="utf-8") as f:
            sidecar = json.load(f)

        gt_focused = None
        for elem in sidecar.get("elements", []):
            if elem.get("state", {}).get("isFocused") is True:
                gt_focused = elem
                break

        if not gt_focused:
            continue

        total_with_focus += 1
        img_name = sidecar.get("image", {}).get("fileName") or (jf.stem + ".png")
        img_path = test_dir / img_name
        if not img_path.exists():
            continue

        im = Image.open(img_path).convert("RGB")
        w, h = im.size

        results = model.predict(source=str(img_path), imgsz=640, device="mps", verbose=False)
        if not results or len(results[0].boxes) == 0:
            continue

        boxes = results[0].boxes
        candidate_boxes = []
        im_arr = np.array(im)
        for i in range(len(boxes)):
            cls_id = int(boxes.cls[i].item())
            cls_name = model.names[cls_id]
            conf = float(boxes.conf[i].item())
            xyxy = boxes.xyxy[i].tolist()
            if cls_name in ["collectionItem", "listRow", "primaryButton", "tabBar", "cancelAction"]:
                x1 = max(0, int(xyxy[0]))
                y1 = max(0, int(xyxy[1]))
                x2 = min(w, int(xyxy[2]))
                y2 = min(h, int(xyxy[3]))
                cw, ch = x2 - x1, y2 - y1
                if cw < 4 or ch < 4:
                    continue
                crop = im_arr[y1:y2, x1:x2]

                if cls_name == "collectionItem":
                    mask = np.zeros((ch, cw), dtype=bool)
                    t = min(6, min(ch, cw) // 4)
                    mask[:t, :] = True
                    mask[-t:, :] = True
                    mask[:, :t] = True
                    mask[:, -t:] = True
                    border_pts = crop[mask]
                    white_count = np.sum((border_pts[:, 0] > 200) & (border_pts[:, 1] > 200) & (border_pts[:, 2] > 200))
                    score = float(white_count / len(border_pts)) if len(border_pts) > 0 else 0.0
                else:
                    in_x1, in_y1 = int(cw * 0.15), int(ch * 0.15)
                    in_x2, in_y2 = int(cw * 0.85), int(ch * 0.85)
                    interior = crop[in_y1:in_y2, in_x1:in_x2]
                    if interior.size > 0:
                        lum = 0.2126 * interior[:, :, 0] + 0.7152 * interior[:, :, 1] + 0.0722 * interior[:, :, 2]
                        score = float(np.mean(lum) / 255.0)
                    else:
                        score = 0.0
                candidate_boxes.append((cls_name, xyxy, conf, score))

        if not candidate_boxes:
            continue

        winner = max(candidate_boxes, key=lambda c: c[3])
        gt_rect = gt_focused.get("boundsPixels") or gt_focused.get("rect", {})
        gt_x = gt_rect.get("x", 0.0)
        gt_y = gt_rect.get("y", 0.0)
        gt_w = gt_rect.get("width", 0.0)
        gt_h = gt_rect.get("height", 0.0)
        gt_xyxy = [gt_x, gt_y, gt_x + gt_w, gt_y + gt_h]

        pred_xyxy = winner[1]
        ix1 = max(pred_xyxy[0], gt_xyxy[0])
        iy1 = max(pred_xyxy[1], gt_xyxy[1])
        ix2 = min(pred_xyxy[2], gt_xyxy[2])
        iy2 = min(pred_xyxy[3], gt_xyxy[3])
        iw = max(0.0, ix2 - ix1)
        ih = max(0.0, iy2 - iy1)
        inter = iw * ih
        area_p = (pred_xyxy[2] - pred_xyxy[0]) * (pred_xyxy[3] - pred_xyxy[1])
        area_g = gt_w * gt_h
        union = area_p + area_g - inter
        iou = inter / union if union > 0 else 0.0

        if iou >= 0.50:
            correct_focus += 1

    accuracy = (correct_focus / total_with_focus) if total_with_focus > 0 else 0.0
    return {
        "totalImagesWithFocus": total_with_focus,
        "correctFocusIdentified": correct_focus,
        "focusAccuracy": round(accuracy, 4),
    }


def main():
    args = parse_args()
    weights_path = Path(args.weights).resolve()
    yaml_path = Path(args.dataset).resolve()

    if not weights_path.exists():
        print(f"ERROR: Weights not found at {weights_path}", file=sys.stderr)
        sys.exit(1)
    if not yaml_path.exists():
        print(f"ERROR: Dataset YAML not found at {yaml_path}", file=sys.stderr)
        sys.exit(1)

    from ultralytics import YOLO

    print(f"Loading weights: {weights_path}")
    model = YOLO(str(weights_path))

    print(f"Running validation on test split...")
    metrics = model.val(
        data=str(yaml_path),
        split="test",
        imgsz=args.imgsz,
        batch=8,
        device=args.device,
        rect=True,
        verbose=True,
    )

    per_class_map50 = {}
    per_class_map50_95 = {}
    if hasattr(metrics.box, "ap_class_index"):
        for idx, cls_id in enumerate(metrics.box.ap_class_index):
            name = model.names[int(cls_id)]
            if hasattr(metrics.box, "ap50") and idx < len(metrics.box.ap50):
                per_class_map50[name] = round(float(metrics.box.ap50[idx]), 4)
            if hasattr(metrics.box, "ap") and idx < len(metrics.box.ap):
                per_class_map50_95[name] = round(float(metrics.box.ap[idx]), 4)
    else:
        for i, name in enumerate(model.names.values()):
            if i < len(metrics.box.maps):
                per_class_map50_95[name] = round(float(metrics.box.maps[i]), 4)
            if hasattr(metrics.box, "ap50") and i < len(metrics.box.ap50):
                per_class_map50[name] = round(float(metrics.box.ap50[i]), 4)

    all_map50 = round(float(metrics.box.map50), 4)
    all_map50_95 = round(float(metrics.box.map), 4)
    precision = round(float(metrics.box.mp), 4)
    recall = round(float(metrics.box.mr), 4)

    print(f"\n--- Held-out Test Set Results ---")
    print(f"Overall mAP@0.5      : {all_map50}")
    print(f"Overall mAP@0.5:0.95 : {all_map50_95}")
    print(f"Mean Precision       : {precision}")
    print(f"Mean Recall          : {recall}")

    focus_eval = None
    if TEST_DATASET_DIR.exists():
        print("\nEvaluating visual focus determination accuracy on test set...")
        focus_eval = evaluate_focus_accuracy(model, TEST_DATASET_DIR)
        if focus_eval:
            print(f"Focus Accuracy: {focus_eval['focusAccuracy'] * 100:.1f}% ({focus_eval['correctFocusIdentified']}/{focus_eval['totalImagesWithFocus']})")

    report_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "modelWeights": str(weights_path),
        "datasetYaml": str(yaml_path),
        "testMetrics": {
            "mAP50": all_map50,
            "mAP50_95": all_map50_95,
            "precision": precision,
            "recall": recall,
            "perClass_mAP50": per_class_map50,
            "perClass_mAP50_95": per_class_map50_95,
        },
        "focusEvaluation": focus_eval,
        "gates": {
            "overall_mAP50_ge_0_80": all_map50 >= 0.80,
            "tabBar_AP50_ge_0_80": per_class_map50.get("tabBar", 0.0) >= 0.80,
            "focus_accuracy_ge_0_85": (focus_eval["focusAccuracy"] >= 0.85) if focus_eval else False,
        }
    }

    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    print(f"\nEvaluation report saved to: {report_path}")
    print(f"Gates Pass: {all(report_data['gates'].values())}")


if __name__ == "__main__":
    main()
