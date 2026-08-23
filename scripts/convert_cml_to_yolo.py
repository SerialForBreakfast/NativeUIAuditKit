#!/usr/bin/env python3
"""
convert_cml_to_yolo.py  —  Convert a Create ML export to YOLO dataset format.

Create ML format (input):
  <createml_export>/
    train/
      images/        PNG files (full + strip)
      annotations.json  [{imagefilename, annotation:[{label, coordinates:{x,y,w,h}}]}]
    validation/
      images/
      annotations.json

YOLO format (output):
  <yolo_dataset>/
    dataset.yaml
    train/
      images/   symlinks → <createml_export>/train/images/*.png
      labels/   <stem>.txt  (one line per box: class_id cx cy w h)
    val/
      images/   symlinks → <createml_export>/validation/images/*.png
      labels/   <stem>.txt

Coordinate system:
  Create ML uses top-left origin, center-anchored, normalised [0,1].
  YOLO uses the same convention.  No coordinate transform needed — only
  class names → integer IDs and JSON → per-file .txt serialisation.

Usage:
  .venv-yolo/bin/python scripts/convert_cml_to_yolo.py \\
    --createml-dir /path/to/createml_export \\
    --output-dir   NativeUITrainer/yolo_dataset

  Run with --dry-run to check counts without writing.
"""

import argparse
import json
import os
import sys
from pathlib import Path


CLASSES = [
    "alert",
    "navigationBar",
    "primaryButton",
    "textField",
    "toggle",
]
CLASS_TO_ID = {name: i for i, name in enumerate(CLASSES)}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--createml-dir", required=True,
                   help="Path to createml_export/ directory")
    p.add_argument("--output-dir", required=True,
                   help="Destination for YOLO dataset (will be created)")
    p.add_argument("--classes", nargs="+", default=CLASSES,
                   help="Ordered class list (determines class IDs)")
    p.add_argument("--dry-run", action="store_true",
                   help="Print counts only, write nothing")
    return p.parse_args()


def convert_split(
    cml_split: Path,
    yolo_split: Path,
    class_to_id: dict,
    dry_run: bool,
) -> tuple[int, int, int]:
    """
    Returns (n_images_linked, n_labels_written, n_boxes_written).
    Images are symlinked; labels are written as .txt.
    """
    annot_path = cml_split / "annotations.json"
    cml_images = cml_split / "images"
    yolo_images = yolo_split / "images"
    yolo_labels = yolo_split / "labels"

    if not annot_path.exists():
        print(f"  WARNING: {annot_path} not found — skipping split")
        return 0, 0, 0

    with open(annot_path) as f:
        entries = json.load(f)

    if not dry_run:
        yolo_images.mkdir(parents=True, exist_ok=True)
        yolo_labels.mkdir(parents=True, exist_ok=True)

    n_images = n_labels = n_boxes = 0
    skipped_labels = []

    for entry in entries:
        fname = entry["imagefilename"]
        stem  = Path(fname).stem
        src   = cml_images / fname
        dst   = yolo_images / fname

        if not src.exists():
            continue

        # Symlink image.
        if not dry_run and not dst.exists():
            dst.symlink_to(src.resolve())
        n_images += 1

        # Build label lines.
        lines = []
        for ann in entry.get("annotation", []):
            label = ann["label"]
            if label not in class_to_id:
                skipped_labels.append(label)
                continue
            cid = class_to_id[label]
            c   = ann["coordinates"]
            cx, cy, w, h = c["x"], c["y"], c["width"], c["height"]
            lines.append(f"{cid} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

        # Write .txt (even if empty — YOLO expects a file per image).
        txt_path = yolo_labels / f"{stem}.txt"
        if not dry_run:
            txt_path.write_text("\n".join(lines) + ("\n" if lines else ""))
        n_labels += 1
        n_boxes  += len(lines)

    if skipped_labels:
        from collections import Counter
        skips = Counter(skipped_labels)
        print(f"  NOTE: skipped unknown labels: {dict(skips.most_common())}")

    return n_images, n_labels, n_boxes


def write_dataset_yaml(output_dir: Path, classes: list, dry_run: bool):
    yaml_path = output_dir / "dataset.yaml"
    lines = [
        f"path: {output_dir.resolve()}",
        "train: train/images",
        "val:   val/images",
        "",
        f"nc: {len(classes)}",
        "names:",
    ]
    for i, name in enumerate(classes):
        lines.append(f"  {i}: {name}")
    content = "\n".join(lines) + "\n"
    if dry_run:
        print(f"\n  [dry-run] dataset.yaml would be:\n{content}")
    else:
        yaml_path.write_text(content)
        print(f"  Wrote {yaml_path}")


def main():
    args = parse_args()
    cml_root    = Path(args.createml_dir).expanduser().resolve()
    output_dir  = Path(args.output_dir).expanduser().resolve()
    class_to_id = {name: i for i, name in enumerate(args.classes)}

    if not cml_root.exists():
        print(f"ERROR: --createml-dir not found: {cml_root}")
        sys.exit(1)

    print(f"Create ML export : {cml_root}")
    print(f"YOLO dataset out : {output_dir}")
    print(f"Classes ({len(args.classes)}): {args.classes}")
    if args.dry_run:
        print("DRY RUN — no files will be written\n")

    split_map = [
        ("train",      "train"),
        ("validation", "val"),
    ]

    total_images = total_labels = total_boxes = 0
    for cml_name, yolo_name in split_map:
        cml_split  = cml_root / cml_name
        yolo_split = output_dir / yolo_name
        print(f"\n── {yolo_name} (← {cml_name}/) ──")
        ni, nl, nb = convert_split(cml_split, yolo_split, class_to_id, args.dry_run)
        print(f"  Images symlinked : {ni:>6}")
        print(f"  Label files      : {nl:>6}")
        print(f"  Bounding boxes   : {nb:>6}")
        total_images += ni
        total_labels += nl
        total_boxes  += nb

    write_dataset_yaml(output_dir, args.classes, args.dry_run)

    print(f"\n{'─'*50}")
    print(f"  Total images : {total_images}")
    print(f"  Total labels : {total_labels}")
    print(f"  Total boxes  : {total_boxes}")
    print(f"{'─'*50}")
    if not args.dry_run:
        print(f"\nDone. Train with:")
        print(f"  .venv-yolo/bin/python scripts/train_yolo.py --dataset {output_dir}")


if __name__ == "__main__":
    main()
