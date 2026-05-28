#!/usr/bin/env python3
"""
augment_createml_export.py
NativeUIAuditKit — Run 005 dataset augmentation

Appends new images from a separate generator run into an existing
createml_export/ directory without touching or re-exporting the
original training data.

WHY THIS EXISTS
  After Run 003 training the source train/ PNGs were deleted from the
  812EDC32 simulator dataset to reclaim disk space. The createml_export/
  still holds 18 563 train entries. This script appends the 240 new
  UIKitToggleForm train images (+ their strips) and 30 validation images
  so the trainer can be called with --skip-export.

USAGE
  python3 scripts/augment_createml_export.py \
    --source <new-images-simulator-dataset-root>  \
    --target <training-simulator-dataset-root>    \
    --template-family UIKitToggleForm             \
    --strip-fraction 0.22

  After this script succeeds, run the trainer:
    swift run -c release NativeUITrainer \
      --dataset <training-simulator-dataset-root> \
      --output  <NativeUIAuditKitModels/Sources/NativeUIAuditKitModels> \
      --skip-export

STRIP LOGIC (mirrors CreateMLExporter.swift)
  stripH  = int(imageHeight * stripFraction)
  stride  = stripH // 2
  Strips: y = 0, stride, 2*stride, ... while y + stripH <= imageHeight
  Each strip: keep elements whose Create-ML-norm cy falls in [yTopNorm, yBottomNorm].
  Remap cy and h into strip-local normalised coords.

COORDINATE SYSTEMS
  Source JSON: boundsVisionNormalized (Vision, bottom-left origin, [0,1])
  Create ML:   top-left origin, centre-anchored, normalised
    cx_cml = vn.x + vn.width  / 2
    cy_cml = 1.0 - vn.y - vn.height / 2   # y-axis flip
  Strip:
    cy_strip = (cy_cml - yTopNorm) * scaleY
    h_strip  = h_cml * scaleY
    clamp both to [0, 1]; discard if h_strip < 0.01
"""

import argparse
import glob
import json
import os
import sys
from pathlib import Path

from PIL import Image


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Append new images to an existing createml_export/")
    p.add_argument("--source",          required=True, help="New-images dataset root (train/val/test subdirs)")
    p.add_argument("--target",          required=True, help="Existing training dataset root (has createml_export/)")
    p.add_argument("--template-family", required=True, help="Template family string to filter (e.g. UIKitToggleForm)")
    p.add_argument("--strip-fraction",  type=float, default=0.22, help="Strip height as fraction of image height (default 0.22)")
    p.add_argument("--target-classes",  nargs="+",
                   default=["alert", "navigationBar", "primaryButton", "textField", "toggle"],
                   help="Element types to include in annotations")
    p.add_argument("--dry-run",         action="store_true", help="Print what would be done without writing files")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_annotations_json(path: Path) -> list:
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def save_annotations_json(path: Path, entries: list, dry_run: bool):
    if dry_run:
        print(f"  [dry-run] Would write {len(entries)} entries → {path}")
        return
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)
    print(f"  Wrote {len(entries)} entries → {path}")


def vn_to_cml(vn_x, vn_y, vn_w, vn_h):
    """Convert Vision-normalised box to Create ML normalised (top-left origin, centre-anchored)."""
    cx = vn_x + vn_w / 2.0
    cy = 1.0 - vn_y - vn_h / 2.0
    return cx, cy, vn_w, vn_h


# ---------------------------------------------------------------------------
# Per-image annotation loading
# ---------------------------------------------------------------------------

def load_image_elements(json_path: Path, target_classes: set) -> list:
    """Load elements from our annotation JSON, return list of (label, cx, cy, w, h) in CML coords."""
    with open(json_path) as f:
        data = json.load(f)
    results = []
    for elem in data.get("elements", []):
        if elem["elementType"] not in target_classes:
            continue
        vn = elem.get("boundsVisionNormalized", {})
        vn_x = vn.get("x", 0)
        vn_y = vn.get("y", 0)
        vn_w = vn.get("width", 0)
        vn_h = vn.get("height", 0)
        if vn_w <= 0 or vn_h <= 0:
            continue
        cx, cy, w, h = vn_to_cml(vn_x, vn_y, vn_w, vn_h)
        results.append({"label": elem["elementType"], "cx": cx, "cy": cy, "w": w, "h": h})
    return results


# ---------------------------------------------------------------------------
# Strip generation
# ---------------------------------------------------------------------------

def generate_strips(
    png_path: Path,
    elements: list,       # list of {label, cx, cy, w, h} in CML full-image coords
    images_dir: Path,
    base_name: str,       # e.g. "img_016441" — no extension
    strip_fraction: float,
    dry_run: bool,
) -> list:
    """
    Crop image into overlapping horizontal strips, write PNGs (unless dry_run),
    return list of CreateML annotation entries for each non-empty strip.
    """
    img = Image.open(png_path)
    img_w, img_h = img.size
    strip_h = max(1, int(img_h * strip_fraction))
    stride  = max(1, strip_h // 2)

    entries = []
    strip_index = 0
    strip_y = 0

    while strip_y + strip_h <= img_h:
        y_top_norm    = strip_y / img_h
        y_bottom_norm = (strip_y + strip_h) / img_h
        scale_y       = img_h / strip_h

        strip_elems = []
        for e in elements:
            if e["cy"] < y_top_norm or e["cy"] > y_bottom_norm:
                continue
            cy_s = (e["cy"] - y_top_norm) * scale_y
            h_s  = e["h"] * scale_y
            cy_s = max(0.0, min(1.0, cy_s))
            h_s  = max(0.0, min(1.0, h_s))
            if h_s < 0.01:
                continue
            strip_elems.append({
                "label": e["label"],
                "coordinates": {"x": e["cx"], "y": cy_s, "width": e["w"], "height": h_s}
            })

        if strip_elems:
            strip_name = f"{base_name}_s{strip_index:02d}.png"
            strip_dest = images_dir / strip_name
            if not dry_run and not strip_dest.exists():
                strip_img = img.crop((0, strip_y, img_w, strip_y + strip_h))
                strip_img.save(strip_dest, "PNG")
            entries.append({"imagefilename": strip_name, "annotation": strip_elems})

        strip_y += stride
        strip_index += 1

    return entries


# ---------------------------------------------------------------------------
# Main per-split processing
# ---------------------------------------------------------------------------

def process_split(
    source_split_dir: Path,
    images_dir: Path,
    annot_path: Path,
    template_family: str,
    target_classes: set,
    strip_fraction: float,
    include_strips: bool,
    start_index: int,
    dry_run: bool,
) -> int:
    """
    Copy/process images from source_split_dir into images_dir and append
    to the annotations JSON at annot_path. Returns count of images processed.
    """
    existing = load_annotations_json(annot_path)
    existing_filenames = {e["imagefilename"] for e in existing}

    source_pngs = sorted(source_split_dir.glob("*.png"))
    new_entries = []
    idx = start_index
    processed = 0

    for src_png in source_pngs:
        src_json = src_png.with_suffix(".json")
        if not src_json.exists():
            continue

        # Filter by template family
        with open(src_json) as f:
            ann_data = json.load(f)
        gp = ann_data.get("generatorProfile", {})
        if gp.get("templateFamily", "") != template_family:
            continue

        # Load and convert element annotations
        elements = load_image_elements(src_json, target_classes)
        if not elements:
            # No target-class elements — skip (would produce empty annotation entry)
            idx += 1
            continue

        # Assign a renumbered filename that doesn't conflict with existing images
        new_name = f"img_{idx:06d}.png"
        dest_png  = images_dir / new_name

        # Skip if already present (idempotent re-runs)
        if new_name in existing_filenames:
            print(f"  [skip] {new_name} already in annotations.json")
            idx += 1
            continue

        # Hard-link the full image
        if not dry_run:
            if not dest_png.exists():
                os.link(src_png, dest_png)
        else:
            print(f"  [dry-run] link {src_png.name} → {new_name}")

        # Full-image annotation entry
        full_annot = [
            {"label": e["label"],
             "coordinates": {"x": e["cx"], "y": e["cy"], "width": e["w"], "height": e["h"]}}
            for e in elements
        ]
        new_entries.append({"imagefilename": new_name, "annotation": full_annot})

        # Strip entries (train only)
        if include_strips:
            strip_entries = generate_strips(
                png_path=src_png,
                elements=elements,
                images_dir=images_dir,
                base_name=f"img_{idx:06d}",
                strip_fraction=strip_fraction,
                dry_run=dry_run,
            )
            new_entries.extend(strip_entries)

        idx += 1
        processed += 1

    if new_entries:
        combined = existing + new_entries
        save_annotations_json(annot_path, combined, dry_run)
        print(f"  +{len(new_entries)} new entries ({processed} source images, "
              f"{len(new_entries) - processed} strips)")
    else:
        print(f"  Nothing to add (all images already present or no target-class elements)")

    return processed


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    source_root = Path(args.source)
    target_root = Path(args.target)
    export_root = target_root / "createml_export"
    target_classes = set(args.target_classes)
    template_family = args.template_family

    print(f"Source dataset : {source_root}")
    print(f"Target export  : {export_root}")
    print(f"Template family: {template_family}")
    print(f"Strip fraction : {args.strip_fraction}")
    print(f"Target classes : {sorted(target_classes)}")
    if args.dry_run:
        print("DRY RUN — no files will be written")
    print()

    # Validate paths
    for split, has_strips in [("train", True), ("validation", False)]:
        src_split = source_root / split
        if not src_split.exists():
            print(f"WARNING: source {split}/ not found at {src_split}")
            continue

        export_split  = export_root / split
        images_dir    = export_split / "images"
        annot_path    = export_split / "annotations.json"

        if not images_dir.exists():
            print(f"ERROR: {images_dir} does not exist — is this the right target?")
            sys.exit(1)

        # Determine start index: one past the highest img_NNNNNN in images_dir
        existing_imgs = list(images_dir.glob("img_*.png"))
        if existing_imgs:
            # Extract number from img_NNNNNN.png (not strips like img_016441_s02.png)
            full_imgs = [p for p in existing_imgs if "_s" not in p.stem]
            max_num = max(int(p.stem.split("_")[1]) for p in full_imgs) if full_imgs else 0
        else:
            max_num = 0
        start_index = max_num + 1

        print(f"── {split} (strip={has_strips}) ──")
        print(f"  Existing images in images/: {len(existing_imgs)}")
        print(f"  Next image index: {start_index}")

        n = process_split(
            source_split_dir=src_split,
            images_dir=images_dir,
            annot_path=annot_path,
            template_family=template_family,
            target_classes=target_classes,
            strip_fraction=args.strip_fraction,
            include_strips=has_strips,
            start_index=start_index,
            dry_run=args.dry_run,
        )
        print(f"  Processed {n} source images")
        print()

    print("Done. Run the trainer with --skip-export to use the augmented export.")


if __name__ == "__main__":
    main()
