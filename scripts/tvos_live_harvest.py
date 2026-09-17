#!/usr/bin/env python3
"""
scripts/tvos_live_harvest.py

Automated capture ingestion and detection utility for TVTestRig sessions.
Supports two capture modes:
1. Container scan mode: queries `aatv observe latest` / `wait-stable` and syncs
   the latest session PNG from the TVTestRig app container into `dataset/tvos_captures/`.
2. Direct pipe / stream mode (Wishlist feature): ingests standard output PNG bytes directly
   when invoked via `aatv observe capture --stdout | python3 scripts/tvos_live_harvest.py --pipe`.

Generates Schema v1.0 JSON sidecars and runs the 25-class YOLO11n tvOS detector.
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
CAPTURES_DIR = REPO_ROOT / "dataset" / "tvos_captures"
MODEL_WEIGHTS = REPO_ROOT / "NativeUITrainer" / "yolo_runs" / "phase6b_tvos_v3" / "weights" / "best.pt"
TVTESTRIG_CONTAINER = Path.home() / "Library" / "Containers" / "com.showblender.TVTestRig" / "Data" / ".tvtr" / "Evidence" / "Sessions"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def ingest_image_file(src_path: Path, dest_name: str, source_label: str = "realAppleTVTVTestRig") -> Path:
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    dest_path = CAPTURES_DIR / dest_name
    
    if src_path.resolve() != dest_path.resolve():
        shutil.copy2(src_path, dest_path)

    sha = compute_sha256(dest_path)
    im = Image.open(dest_path)
    width, height = im.size

    sidecar = {
        "schemaVersion": "1.0",
        "captureSource": source_label,
        "device": {
            "model": "AppleTV5,3",
            "platform": "tvOS",
            "screenWidth": width,
            "screenHeight": height,
            "screenScale": 1
        },
        "sha256": sha,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elements": []
    }

    sidecar_path = dest_path.with_suffix(".json")
    with open(sidecar_path, "w") as f:
        json.dump(sidecar, f, indent=2)

    print(f"✅ Ingested: {dest_path.name} (SHA-256: {sha[:12]}...)")
    return dest_path


def run_yolo_detection(image_path: Path, conf: float = 0.25):
    if not MODEL_WEIGHTS.exists():
        print(f"⚠️ Model weights not found at {MODEL_WEIGHTS}. Skipping detection.")
        return

    try:
        from ultralytics import YOLO
    except ImportError:
        print("⚠️ Ultralytics YOLO not installed in current Python environment. Skipping detection.")
        return

    model = YOLO(str(MODEL_WEIGHTS))
    results = model.predict(str(image_path), conf=conf, verbose=False)
    boxes = results[0].boxes
    names = model.names

    detections = []
    for b in boxes:
        cls_id = int(b.cls[0])
        conf_val = float(b.conf[0])
        xyxy = [round(x, 1) for x in b.xyxy[0].tolist()]
        detections.append({
            "class": names[cls_id],
            "confidence": round(conf_val, 3),
            "box": xyxy
        })

    print(f"🎯 Detections for {image_path.name} ({len(detections)} elements):")
    for d in sorted(detections, key=lambda x: (x['box'][1], x['box'][0])):
        print(f"   - {d['class']:18s} conf={d['confidence']:.3f} box={d['box']}")


def main():
    parser = argparse.ArgumentParser(description="TVTestRig automated ingestion and detection adapter")
    parser.add_argument("--pipe", action="store_true", help="Read PNG stream directly from stdin (piped mode)")
    parser.add_argument("--name", type=str, default=None, help="Destination filename base (e.g. 'office_settings')")
    parser.add_argument("--session", type=str, default=None, help="TVTestRig session UUID to scan")
    parser.add_argument("--detect", action="store_true", default=True, help="Run YOLO detection after ingestion")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")

    args = parser.parse_args()

    timestamp = int(time.time())
    dest_name = f"{args.name}.png" if args.name else f"office_capture_{timestamp}.png"

    if args.pipe:
        print("📥 Reading image data from stdin...")
        CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
        dest_path = CAPTURES_DIR / dest_name
        with open(dest_path, "wb") as f:
            f.write(sys.stdin.buffer.read())
        ingest_image_file(dest_path, dest_name)
        if args.detect:
            run_yolo_detection(dest_path, conf=args.conf)
        return

    # Container lookup mode
    if not TVTESTRIG_CONTAINER.exists():
        print(f"❌ TVTestRig container directory not found: {TVTESTRIG_CONTAINER}")
        sys.exit(1)

    # Find active session
    if args.session:
        session_dir = TVTESTRIG_CONTAINER / args.session
    else:
        sessions = sorted([s for s in TVTESTRIG_CONTAINER.iterdir() if s.is_dir()], key=os.path.getmtime, reverse=True)
        if not sessions:
            print("❌ No active sessions found in TVTestRig container.")
            sys.exit(1)
        session_dir = sessions[0]

    screens_dir = session_dir / "screens"
    if not screens_dir.exists():
        print(f"❌ No screens directory found in session: {session_dir.name}")
        sys.exit(1)

    screens = sorted(screens_dir.glob("*.png"), key=os.path.getmtime, reverse=True)
    if not screens:
        print("❌ No screenshots found in session screens directory.")
        sys.exit(1)

    latest_screen = screens[0]
    print(f"Found latest session capture: {latest_screen.name} in session {session_dir.name}")
    dest_path = ingest_image_file(latest_screen, dest_name)
    if args.detect:
        run_yolo_detection(dest_path, conf=args.conf)


if __name__ == "__main__":
    main()
