#!/usr/bin/env python3
"""
ingest_batch_6a8.py — Import simulator batch into a YOLO file-list dataset.

Does not list dest/train or yolo train/images (those directories hang on glob/
iterdir). Existing images are referenced by name from dest manifest.json.
New PNGs land in yolo_dataset_41class/batch_6a8/ (new empty dirs).

Replaced families (LoginForm, ToolbarActions, ProgressActivity, MediaCardGrid)
are omitted from the old file list and supplied by the batch instead.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from export_coco import (  # noqa: E402
    CATEGORY_MAP,
    DEFAULT_HOLDOUT_FAMILIES,
    DROP_TYPES,
    element_type,
    bounds_vision,
    vision_to_yolo,
    load_category_map,
)

SRC_DEFAULT = Path(
    "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/"
    "50B7A5E5-3114-4525-994F-C7D547D3E5B8/data/Containers/Data/Application/"
    "457433DD-AA66-4EE8-88A1-2A04E7761279/Documents/dataset"
)
DEST_MANIFEST = PROJECT_ROOT / "dataset" / "dataset" / "manifest.json"
YOLO_ROOT = PROJECT_ROOT / "NativeUITrainer" / "yolo_dataset_41class"
BATCH = YOLO_ROOT / "batch_6a8"
SPLITS = ("train", "validation", "test")
IMG_RE = re.compile(r"^img_\d{6}\.(png|json)$")
REPLACE_FAMILIES = {
    "LoginForm",
    "ToolbarActions",
    "ProgressActivity",
    "MediaCardGrid",
}
BATCH_FAMILIES = REPLACE_FAMILIES | {
    "AccountProfileForm",
    "ChromeCoverage",
    "KitchenSink",
}


def scandir_pairs(root: Path) -> list[tuple[str, Path, Path]]:
    pairs: list[tuple[str, Path, Path]] = []
    for split in SPLITS:
        d = root / split
        if not d.is_dir():
            continue
        pngs: dict[str, Path] = {}
        jsons: dict[str, Path] = {}
        with os.scandir(d) as it:
            for ent in it:
                m = IMG_RE.match(ent.name)
                if not m:
                    continue
                stem = Path(ent.name).stem
                path = Path(ent.path)
                if m.group(1) == "png":
                    pngs[stem] = path
                else:
                    jsons[stem] = path
        for stem, png in pngs.items():
            js = jsons.get(stem)
            if js is not None:
                pairs.append((split, png, js))
    return pairs


def family_seed(ann: dict) -> tuple[str, int]:
    gp = ann.get("generatorProfile") or {}
    return str(gp.get("templateFamily") or "unknown"), int(gp.get("seed") or 0)


def yolo_lines(ann: dict, name_to_id: dict[str, int]) -> list[str]:
    lines: list[str] = []
    for el in ann.get("elements") or []:
        if el.get("excluded") is True:
            continue
        et = element_type(el)
        if not et or et in DROP_TYPES or et not in name_to_id:
            continue
        vn = bounds_vision(el)
        if not vn:
            continue
        yolo = vision_to_yolo(vn)
        if yolo is None:
            continue
        cx, cy, w, h = yolo
        lines.append(f"{name_to_id[et]} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
    return lines


def target_split(original: str, family: str, holdout: set[str]) -> str:
    if family in holdout:
        return "test"
    if original == "train":
        return "train"
    return "val"


def main() -> int:
    src = Path(os.environ.get("NATIVEUI_BATCH_SRC") or SRC_DEFAULT)
    if not src.is_dir():
        print(f"ERROR: simulator batch not found: {src}", flush=True)
        return 1
    if not DEST_MANIFEST.exists():
        print(f"ERROR: dest manifest missing: {DEST_MANIFEST}", flush=True)
        return 1

    name_to_id, names = load_category_map(CATEGORY_MAP)
    holdout = set(DEFAULT_HOLDOUT_FAMILIES)
    print("Loading dest manifest…", flush=True)
    manifest = json.loads(DEST_MANIFEST.read_text())
    entries = manifest.get("entries") or []

    print(f"Listing simulator batch {src}…", flush=True)
    pairs = scandir_pairs(src)
    print(f"Batch pairs: {len(pairs)}", flush=True)

    for split in ("train", "val", "test"):
        (BATCH / split / "images").mkdir(parents=True, exist_ok=True)
        (BATCH / split / "labels").mkdir(parents=True, exist_ok=True)

    replaced_keys: set[tuple[str, int]] = set()
    batch_paths: dict[str, list[str]] = {"train": [], "val": [], "test": []}
    box_counts: Counter[str] = Counter()
    n = 0
    for original, png, js in pairs:
        ann = json.loads(js.read_text())
        fam, seed = family_seed(ann)
        if fam not in BATCH_FAMILIES:
            continue
        dest = target_split(original, fam, holdout)
        n += 1
        stem = f"img_6a8_{n:06d}"
        img_dst = BATCH / dest / "images" / f"{stem}.png"
        lbl_dst = BATCH / dest / "labels" / f"{stem}.txt"
        shutil.copy2(png, img_dst)
        lines = yolo_lines(ann, name_to_id)
        lbl_dst.write_text("\n".join(lines) + ("\n" if lines else ""))
        for line in lines:
            cid = int(line.split()[0])
            box_counts[names[cid]] += 1
        batch_paths[dest].append(str(img_dst.resolve()))
        if fam in REPLACE_FAMILIES:
            replaced_keys.add((fam, seed))
        if n % 50 == 0:
            print(f"  ingested {n}/{len(pairs)}", flush=True)
    print(f"Ingested {n} batch images into {BATCH}", flush=True)

    lists: dict[str, list[str]] = {"train": [], "val": [], "test": []}
    skipped_replaced = 0
    missing_old = 0
    for e in entries:
        fam = e.get("templateFamily") or "unknown"
        seed = int(e.get("generatorSeed") or 0)
        if (fam, seed) in replaced_keys:
            skipped_replaced += 1
            continue
        fn = e.get("fileName") or ""
        original = fn.split("/", 1)[0] if "/" in fn else "train"
        if original == "validation":
            original = "validation"
        dest = target_split(original if original != "validation" else "validation", fam, holdout)
        # dest/train/img_X.png → yolo train/images/img_X.png (existing Run 007 export)
        yolo_split = dest
        name = Path(fn).name
        old = YOLO_ROOT / yolo_split / "images" / name
        lists[yolo_split].append(str(old))

    for k, paths in batch_paths.items():
        lists[k].extend(paths)

    for split, paths in lists.items():
        out = YOLO_ROOT / f"{split}.txt"
        out.write_text("\n".join(paths) + "\n")
        print(f"  {split}.txt: {len(paths)} images", flush=True)
    print(f"Omitted replaced seeds: {skipped_replaced}", flush=True)

    yaml_path = YOLO_ROOT / "dataset.yaml"
    yaml_lines = [
        f"path: {YOLO_ROOT}",
        "train: train.txt",
        "val: val.txt",
        "test: test.txt",
        "",
        f"nc: {len(names)}",
        "names:",
    ]
    for i, nme in enumerate(names):
        yaml_lines.append(f"  {i}: {nme}")
    yaml_path.write_text("\n".join(yaml_lines) + "\n")
    print(f"Wrote {yaml_path}", flush=True)

    # Class weights from train.txt label files (open by name, no glob).
    counts = [0] * len(names)
    for img in lists["train"]:
        p = Path(img)
        lbl = p.parent.parent / "labels" / (p.stem + ".txt")
        if not lbl.exists():
            missing_old += 1
            continue
        for line in lbl.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            cid = int(line.split()[0])
            if 0 <= cid < len(names):
                counts[cid] += 1
    print(f"Train labels missing (old path): {missing_old}", flush=True)

    safe = [c if c > 0 else 1 for c in counts]
    total = float(sum(safe))
    raw = [total / c for c in safe]
    s = sum(raw)
    alphas = [a / s for a in raw]
    weights = {
        "source": str(YOLO_ROOT / "train.txt"),
        "n_train_images": len(lists["train"]),
        "counts": {names[i]: counts[i] for i in range(len(names))},
        "alpha": alphas,
        "note": "Inverse-frequency α, empty classes counted as 1, L1-normalized.",
    }
    wpath = PROJECT_ROOT / "scripts" / "class_weights.json"
    wpath.write_text(json.dumps(weights, indent=2) + "\n")
    print(f"Wrote {wpath}", flush=True)
    for k in ("toolbar", "statusBar", "scrollIndicator", "tooltip", "unknown", "pageControl"):
        print(f"  {k}: {weights['counts'].get(k, 0)}", flush=True)

    report = {
        "batch_images": n,
        "skipped_replaced": skipped_replaced,
        "list_sizes": {k: len(v) for k, v in lists.items()},
        "batch_boxes": dict(box_counts),
    }
    rpath = PROJECT_ROOT / "reports" / "batch_6a8_ingest.json"
    rpath.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote {rpath}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
