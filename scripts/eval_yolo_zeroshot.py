#!/usr/bin/env python3
"""
Test B — YOLO11n COCO pre-trained zero-shot inference on iOS UI strips.

Purpose:
  1. Validate the YOLO11 pipeline end-to-end (download weights, run, parse output).
  2. Measure per-image inference time on this Mac (M-series baseline).
  3. Inspect what COCO classes fire on rendered iOS UI strips (spatial coherence check).

Usage:
  .venv-yolo/bin/python scripts/eval_yolo_zeroshot.py

Outputs:
  - Console report (timing + top detections per image)
  - reports/yolo_zeroshot/<image_name>.jpg  — annotated with COCO boxes
  - reports/yolo_zeroshot/summary.json      — machine-readable results
"""

import json
import os
import sys
import time
from pathlib import Path

# Resolve project root from this script's location.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR   = PROJECT_ROOT / "scripts"
IMAGE_DIR    = PROJECT_ROOT / "NativeUITrainer" / "strip_smoke_test" / "images"
OUTPUT_DIR   = PROJECT_ROOT / "reports" / "yolo_zeroshot"
MODEL_PATH   = SCRIPT_DIR / "yolo11n.pt"   # cached here if present; falls back to ~/.cache/ultralytics/

# Suppress ultralytics telemetry and auto-update noise.
os.environ["YOLO_VERBOSE"] = "False"
os.environ["ULTRALYTICS_DISABLE_MSG"] = "1"

def main():
    try:
        from ultralytics import YOLO
    except ImportError:
        print("ERROR: ultralytics not found. Run from the project-local venv:")
        print("  .venv-yolo/bin/python scripts/eval_yolo_zeroshot.py")
        sys.exit(1)

    # Collect images.
    images = sorted(IMAGE_DIR.glob("*.png"))
    if not images:
        print(f"ERROR: No PNG images found in {IMAGE_DIR}")
        sys.exit(1)

    print(f"Found {len(images)} strip images in {IMAGE_DIR.relative_to(PROJECT_ROOT)}")

    # Load YOLO11n: use local project copy if present; otherwise ultralytics
    # downloads to ~/.cache/ultralytics/ automatically (library behavior).
    model_arg = str(MODEL_PATH) if MODEL_PATH.exists() else "yolo11n.pt"
    print(f"\nLoading YOLO11n (source: {'project cache' if MODEL_PATH.exists() else '~/.cache/ultralytics'}) …")
    t0 = time.perf_counter()
    model = YOLO(model_arg)
    load_ms = (time.perf_counter() - t0) * 1000
    print(f"  Model loaded in {load_ms:.0f} ms")

    # Copy weights into project scripts/ so future runs stay local.
    if not MODEL_PATH.exists():
        import shutil
        downloaded = Path(model.model.pt_path) if hasattr(model.model, "pt_path") else None
        if downloaded and downloaded.exists() and downloaded != MODEL_PATH:
            shutil.copy2(downloaded, MODEL_PATH)
            print(f"  Weights cached → {MODEL_PATH.relative_to(PROJECT_ROOT)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results_list = []
    inference_times_ms = []

    print(f"\n{'─'*60}")
    print(f"{'Image':<35}  {'ms':>5}  Top detections (COCO class, conf)")
    print(f"{'─'*60}")

    for img_path in images:
        t1 = time.perf_counter()
        results = model.predict(
            source=str(img_path),
            conf=0.25,          # COCO default threshold
            iou=0.45,
            verbose=False,
            save=False,
        )
        inf_ms = (time.perf_counter() - t1) * 1000
        inference_times_ms.append(inf_ms)

        r = results[0]
        boxes = r.boxes

        detections = []
        if boxes is not None and len(boxes):
            for box in boxes:
                cls_id = int(box.cls[0].item())
                conf   = float(box.conf[0].item())
                xyxy   = box.xyxy[0].tolist()
                label  = model.names[cls_id]
                detections.append({
                    "class": label,
                    "conf": round(conf, 3),
                    "xyxy": [round(v, 1) for v in xyxy],
                })

        # Sort by conf descending, show top 3 in console.
        detections.sort(key=lambda d: d["conf"], reverse=True)
        top3 = ", ".join(f"{d['class']} {d['conf']:.2f}" for d in detections[:3]) or "—"
        print(f"  {img_path.name:<33}  {inf_ms:>5.0f}  {top3}")

        # Save annotated image (YOLO plot API).
        annotated = r.plot()   # numpy HWC BGR
        import cv2
        out_path = OUTPUT_DIR / (img_path.stem + ".jpg")
        cv2.imwrite(str(out_path), annotated)

        results_list.append({
            "image": img_path.name,
            "inference_ms": round(inf_ms, 1),
            "n_detections": len(detections),
            "detections": detections,
        })

    print(f"{'─'*60}")

    # Summary stats.
    p50 = sorted(inference_times_ms)[len(inference_times_ms)//2]
    p95 = sorted(inference_times_ms)[int(len(inference_times_ms)*0.95)]
    total_dets = sum(r["n_detections"] for r in results_list)

    # Class frequency across all images.
    from collections import Counter
    cls_counts = Counter(
        d["class"]
        for r in results_list
        for d in r["detections"]
    )

    print(f"\n{'─'*60}")
    print(f"  Images:              {len(results_list)}")
    print(f"  Total detections:    {total_dets}")
    print(f"  Inference p50:       {p50:.0f} ms")
    print(f"  Inference p95:       {p95:.0f} ms")
    print(f"\n  COCO class hits (across all images):")
    for cls, cnt in cls_counts.most_common(15):
        print(f"    {cls:<22}  {cnt:>3}")
    print(f"{'─'*60}")

    # Write machine-readable summary.
    summary = {
        "model": "yolo11n",
        "weights": "COCO pretrained (zero-shot)",
        "n_images": len(results_list),
        "inference_p50_ms": round(p50, 1),
        "inference_p95_ms": round(p95, 1),
        "total_detections": total_dets,
        "class_freq": dict(cls_counts.most_common()),
        "per_image": results_list,
    }
    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\n  Annotated images → {OUTPUT_DIR.relative_to(PROJECT_ROOT)}/")
    print(f"  Summary JSON     → {summary_path.relative_to(PROJECT_ROOT)}")

if __name__ == "__main__":
    main()
