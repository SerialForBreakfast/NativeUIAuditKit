#!/usr/bin/env python3
"""
export_tvos_coco.py — Export tvOS annotations to YOLO format (Phase 6b).

Reads tvOS screenshots and sidecar JSONs (synthetic templates and TVTestRig captures)
and prepares a YOLO11 dataset directory (images + text labels + dataset.yaml).

Coordinate conversion (Vision bottom-left -> YOLO top-left center-anchored):
    cx = vn.x + vn.w / 2.0
    cy = 1.0 - vn.y - vn.h / 2.0
    w, h unchanged

Usage:
    .venv-yolo/bin/python scripts/export_tvos_coco.py \
        --input dataset/tvos_captures \
        --output NativeUITrainer/yolo_dataset_tvos
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IN = PROJECT_ROOT / "dataset" / "tvos_captures"
DEFAULT_OUT = PROJECT_ROOT / "NativeUITrainer" / "yolo_dataset_tvos"
CATEGORY_MAP = PROJECT_ROOT / "Research" / "schemas" / "category_map.json"


def load_category_map(path: Path) -> Tuple[Dict[str, int], List[str]]:
    data = json.loads(path.read_text())
    cats = sorted(data["categories"], key=lambda c: c["id"])
    name_to_id = {c["name"]: int(c["id"]) for c in cats}
    names = [c["name"] for c in cats]
    return name_to_id, names


def vision_to_yolo(vn: dict) -> Tuple[float, float, float, float] | None:
    try:
        x = float(vn["x"])
        y = float(vn["y"])
        w = float(vn["width"])
        h = float(vn["height"])
    except (KeyError, TypeError, ValueError):
        return None
    if w <= 0 or h <= 0:
        return None
    cx = min(max(x + w / 2.0, 1e-6), 1.0 - 1e-6)
    cy = min(max(1.0 - y - h / 2.0, 1e-6), 1.0 - 1e-6)
    w = min(max(w, 1e-6), 1.0)
    h = min(max(h, 1e-6), 1.0)
    return cx, cy, w, h


def main() -> int:
    parser = argparse.ArgumentParser(description="Export tvOS annotations to YOLO dataset")
    parser.add_argument("--input", type=Path, default=DEFAULT_IN, help="Input directory containing PNGs and JSONs")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT, help="Output YOLO dataset directory")
    args = parser.parse_args()

    name_to_id, names = load_category_map(CATEGORY_MAP)
    out_dir = args.output
    out_dir.mkdir(parents=True, exist_ok=True)

    images_dir = out_dir / "images"
    labels_dir = out_dir / "labels"
    for split in ["train", "val", "test"]:
        (images_dir / split).mkdir(parents=True, exist_ok=True)
        (labels_dir / split).mkdir(parents=True, exist_ok=True)

    input_dir = args.input
    if not input_dir.exists():
        print(f"Input directory does not exist: {input_dir}. Creating empty placeholder.", file=sys.stderr)
        input_dir.mkdir(parents=True, exist_ok=True)

    json_files = [p for p in input_dir.rglob("*.json") if p.name != "manifest.json"]
    print(f"Found {len(json_files)} sidecar JSON files in {input_dir}")

    exported_count = 0
    for i, jf in enumerate(json_files):
        png_path = jf.with_suffix(".png")
        if not png_path.exists():
            continue

        try:
            data = json.loads(jf.read_text())
        except Exception:
            continue

        # Check if file was already inside a split directory
        parent_name = jf.parent.name
        if parent_name in ["train", "validation", "val", "test"]:
            split = "val" if parent_name == "validation" else parent_name
        else:
            # Fallback 80/10/10 split
            split = "train"
            if i % 10 == 9:
                split = "test"
            elif i % 10 == 8:
                split = "val"

        # Copy image or create relative symlink
        dest_img = images_dir / split / png_path.name
        if not dest_img.exists():
            shutil.copy(png_path, dest_img)

        # Convert elements to YOLO lines
        yolo_lines = []
        for elem in data.get("elements", []):
            etype = elem.get("elementType")
            if etype not in name_to_id:
                continue
            cat_id = name_to_id[etype]
            vn = elem.get("boundsVisionNormalized")
            if not vn:
                continue
            coords = vision_to_yolo(vn)
            if not coords:
                continue
            cx, cy, w, h = coords
            yolo_lines.append(f"{cat_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

        dest_label = labels_dir / split / f"{png_path.stem}.txt"
        dest_label.write_text("\n".join(yolo_lines) + ("\n" if yolo_lines else ""))
        exported_count += 1

    # Write dataset.yaml
    yaml_lines = [
        f"path: {out_dir.resolve()}",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        f"nc: {len(names)}",
        f"names: {names}",
    ]
    (out_dir / "dataset.yaml").write_text("\n".join(yaml_lines) + "\n")

    print(f"Successfully exported {exported_count} images to YOLO dataset at {out_dir}")
    print(f"dataset.yaml written with {len(names)} classes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
