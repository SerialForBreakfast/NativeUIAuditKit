#!/usr/bin/env python3
"""
export_coco.py — Native annotation JSON → YOLO labels + COCO JSON (Phase 6a).

Reads the generator dataset (PNG + sidecar JSON) and writes an in-package
Ultralytics dataset. Images are symlinked; labels are rewritten.

Coordinate conversion (Vision bottom-left → YOLO/COCO top-left, center-anchored):
    cx = vn.x + vn.w / 2
    cy = 1.0 - vn.y - vn.h / 2
    w, h unchanged
Same formula as CreateMLExporter (BP-10).

Family holdout (BP-27): images from DEFAULT_HOLDOUT_FAMILIES go to test/
regardless of the generator's 8:1:1-within-family split. Remaining images
keep their original train assignment; original validation+test → val.

tabBarItem is dropped (not in the frozen 41-class taxonomy, BP-28).

Usage:
  .venv-yolo/bin/python scripts/export_coco.py --dataset /path/to/NativeUIAuditKit-Dataset
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = PROJECT_ROOT / "NativeUITrainer" / "yolo_dataset_41class"
CATEGORY_MAP = PROJECT_ROOT / "Research" / "schemas" / "category_map.json"

# Families that are NOT unique sources of rare classes (BP-27).
DEFAULT_HOLDOUT_FAMILIES = [
    "CardDetail",
    "WizardStepFlow",
    "NotificationCenter",
    "GalleryPage",
    "MultiSectionForm",
    "SettingsToggleDense",
    "EmptyState",
    "OnboardingPage",
]

DROP_TYPES = {"tabBarItem"}
SPLIT_DIRS = ("train", "validation", "test")


def load_category_map(path: Path) -> tuple[dict[str, int], list[str]]:
    data = json.loads(path.read_text())
    cats = sorted(data["categories"], key=lambda c: c["id"])
    name_to_id = {c["name"]: int(c["id"]) for c in cats}
    names = [c["name"] for c in cats]
    return name_to_id, names


def discover_dataset(explicit: str | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    env = os.environ.get("NATIVEUI_DATASET")
    if env:
        candidates.append(Path(env).expanduser())
    candidates.extend(
        [
            PROJECT_ROOT / "dataset" / "dataset",
            PROJECT_ROOT / "dataset",
            PROJECT_ROOT.parent / "NativeUIAuditKit-Dataset",
            Path.home() / "NativeUIAuditKit-Dataset",
            PROJECT_ROOT / "NativeUITrainer" / "source_dataset",
        ]
    )
    for c in candidates:
        if (c / "manifest.json").exists() or (c / "train").is_dir():
            return c.resolve()
    print("ERROR: native dataset not found. Pass --dataset <root>.")
    print("Looked at:")
    for c in candidates:
        print(f"  {c}")
    sys.exit(1)


def vision_to_yolo(vn: dict) -> tuple[float, float, float, float] | None:
    """Vision-normalized xywh (bottom-left) → YOLO cxcywh (top-left)."""
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


def vision_to_coco_xywh(vn: dict, pixel_w: int, pixel_h: int) -> list[float] | None:
    yolo = vision_to_yolo(vn)
    if yolo is None:
        return None
    cx, cy, w, h = yolo
    x_min = (cx - w / 2.0) * pixel_w
    y_min = (cy - h / 2.0) * pixel_h
    return [x_min, y_min, w * pixel_w, h * pixel_h]


def element_type(el: dict) -> str | None:
    return el.get("elementType") or el.get("type")


def bounds_vision(el: dict) -> dict | None:
    return (
        el.get("boundsVisionNormalized")
        or el.get("boundsVisionNormalized")
        or el.get("visionNormalizedBounds")
    )


def template_family(ann: dict, manifest_family: str | None) -> str:
    profile = ann.get("generatorProfile") or ann.get("generatorProfile") or {}
    return (
        profile.get("templateFamily")
        or manifest_family
        or "unknown"
    )


def image_size(ann: dict, png: Path) -> tuple[int, int]:
    info = ann.get("image") or {}
    w = info.get("pixelWidth") or info.get("pixelWidth") or info.get("width")
    h = info.get("pixelHeight") or info.get("pixelHeight") or info.get("height")
    if w and h:
        return int(w), int(h)
    try:
        import struct

        with png.open("rb") as f:
            if f.read(8) != b"\x89PNG\r\n\x1a\n":
                raise ValueError("not a png")
            f.read(4)
            if f.read(4) != b"IHDR":
                raise ValueError("no IHDR")
            pw, ph = struct.unpack(">II", f.read(8))
            return int(pw), int(ph)
    except Exception:
        return 0, 0


def load_manifest_families(dataset: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    man = dataset / "manifest.json"
    if not man.exists():
        return out
    data = json.loads(man.read_text())
    entries = data.get("entries") or data.get("images") or []
    if isinstance(data, list):
        entries = data
    for e in entries:
        fam = e.get("templateFamily")
        fn = e.get("fileName") or ""
        if fam and fn:
            out[fn] = fam
            out[Path(fn).name] = fam
    return out


def iter_pairs(dataset: Path):
    for split in SPLIT_DIRS:
        d = dataset / split
        if not d.is_dir():
            continue
        for png in sorted(d.glob("*.png")):
            js = png.with_suffix(".json")
            if js.exists():
                yield split, png, js


def target_split(original: str, family: str, holdout: set[str]) -> str:
    if family in holdout:
        return "test"
    if original == "train":
        return "train"
    return "val"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default=None, help="Native dataset root (PNG+JSON splits)")
    p.add_argument("--output", default=str(DEFAULT_OUT), help="In-package YOLO/COCO output")
    p.add_argument(
        "--holdout-families",
        nargs="*",
        default=DEFAULT_HOLDOUT_FAMILIES,
        help="Template families assigned entirely to test/",
    )
    p.add_argument("--dry-run", action="store_true", help="Count only; write nothing")
    return p.parse_args()


def main():
    args = parse_args()
    dataset = discover_dataset(args.dataset)
    out_dir = Path(args.output).expanduser().resolve()
    name_to_id, names = load_category_map(CATEGORY_MAP)
    holdout = set(args.holdout_families)
    manifest_fam = load_manifest_families(dataset)

    print(f"Dataset : {dataset}")
    print(f"Output  : {out_dir}")
    print(f"Classes : {len(names)}")
    print(f"Holdout : {sorted(holdout)}")
    if args.dry_run:
        print("DRY RUN — no files written\n")

    coco = {
        "train": {"images": [], "annotations": [], "categories": []},
        "val": {"images": [], "annotations": [], "categories": []},
        "test": {"images": [], "annotations": [], "categories": []},
    }
    cats = [{"id": i, "name": n, "supercategory": "ui"} for i, n in enumerate(names)]
    for split in coco:
        coco[split]["categories"] = cats

    box_counts: Counter[str] = Counter()
    dropped: Counter[str] = Counter()
    unknown_types: Counter[str] = Counter()
    family_split: dict[str, Counter] = defaultdict(Counter)
    images_written = {"train": 0, "val": 0, "test": 0}
    ann_id = 1
    image_id = 1

    if not args.dry_run:
        for split in ("train", "val", "test"):
            (out_dir / split / "images").mkdir(parents=True, exist_ok=True)
            (out_dir / split / "labels").mkdir(parents=True, exist_ok=True)
        (out_dir / "annotations").mkdir(parents=True, exist_ok=True)

    n_pairs = 0
    for original, png, js in iter_pairs(dataset):
        n_pairs += 1
        try:
            ann = json.loads(js.read_text())
        except json.JSONDecodeError:
            print(f"  SKIP unreadable JSON: {js.name}")
            continue

        rel = f"{original}/{png.name}"
        family = template_family(ann, manifest_fam.get(rel) or manifest_fam.get(png.name))
        dest = target_split(original, family, holdout)
        family_split[family][dest] += 1

        pw, ph = image_size(ann, png)
        yolo_lines: list[str] = []
        coco_anns: list[dict] = []

        for el in ann.get("elements") or []:
            if el.get("excluded") is True:
                continue
            et = element_type(el)
            if not et:
                continue
            if et in DROP_TYPES:
                dropped[et] += 1
                continue
            if et not in name_to_id:
                unknown_types[et] += 1
                continue
            vn = bounds_vision(el)
            if not vn:
                continue
            yolo = vision_to_yolo(vn)
            if yolo is None:
                continue
            cid = name_to_id[et]
            cx, cy, w, h = yolo
            yolo_lines.append(f"{cid} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
            box_counts[et] += 1
            if pw > 0 and ph > 0:
                bbox = vision_to_coco_xywh(vn, pw, ph)
                if bbox:
                    coco_anns.append(
                        {
                            "id": ann_id,
                            "image_id": image_id,
                            "category_id": cid,
                            "bbox": [round(v, 2) for v in bbox],
                            "area": round(bbox[2] * bbox[3], 2),
                            "iscrowd": 0,
                        }
                    )
                    ann_id += 1

        if not args.dry_run:
            img_dst = out_dir / dest / "images" / png.name
            lbl_dst = out_dir / dest / "labels" / (png.stem + ".txt")
            if img_dst.exists() or img_dst.is_symlink():
                img_dst.unlink()
            os.symlink(png.resolve(), img_dst)
            lbl_dst.write_text("\n".join(yolo_lines) + ("\n" if yolo_lines else ""))

        coco[dest]["images"].append(
            {
                "id": image_id,
                "file_name": png.name,
                "width": pw,
                "height": ph,
            }
        )
        coco[dest]["annotations"].extend(coco_anns)
        images_written[dest] += 1
        image_id += 1

    yaml_lines = [
        f"path: {out_dir}",
        "train: train/images",
        "val: val/images",
        "test: test/images",
        "",
        f"nc: {len(names)}",
        "names:",
    ]
    for i, n in enumerate(names):
        yaml_lines.append(f"  {i}: {n}")
    yaml_text = "\n".join(yaml_lines) + "\n"

    report = {
        "source": str(dataset),
        "pairs": n_pairs,
        "images": images_written,
        "boxes_per_class": dict(box_counts),
        "dropped": dict(dropped),
        "unknown_types": dict(unknown_types),
        "holdout_families": sorted(holdout),
        "family_split": {k: dict(v) for k, v in sorted(family_split.items())},
        "empty_taxonomy_classes": [n for n in names if box_counts[n] == 0],
    }

    if not args.dry_run:
        (out_dir / "dataset.yaml").write_text(yaml_text)
        for split, blob in coco.items():
            (out_dir / "annotations" / f"instances_{split}.json").write_text(
                json.dumps(blob)
            )
        (out_dir / "export_report.json").write_text(json.dumps(report, indent=2))

    print(f"\nPairs scanned          : {n_pairs}")
    print(
        f"Images train/val/test  : "
        f"{images_written['train']}/{images_written['val']}/{images_written['test']}"
    )
    print(f"Boxes written          : {sum(box_counts.values())}")
    print(f"Dropped (BP-28)        : {dict(dropped)}")
    if unknown_types:
        print(f"Unknown types          : {dict(unknown_types)}")
    empty = report["empty_taxonomy_classes"]
    print(f"Empty classes ({len(empty)}): {empty}")
    print(f"Present classes        : {len(names) - len(empty)} / {len(names)}")
    if not args.dry_run:
        print(f"\nWrote {out_dir / 'dataset.yaml'}")
        print("Next:")
        print("  .venv-yolo/bin/python scripts/compute_class_weights.py")
        print("  .venv-yolo/bin/python scripts/train_ios_model.py --dry-run")


if __name__ == "__main__":
    main()
