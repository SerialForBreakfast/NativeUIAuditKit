#!/usr/bin/env python3
"""
merge_generator_batch.py — Merge a simulator generation batch into dataset/dataset.

Never list dest/train (iterdir/glob hang on this volume). Dest paths come only
from manifest.json. Source dirs are small (~200 files/split) and are listed
with os.scandir.

Replace families (same seed): overwrite PNG+JSON, keep dest filename/split.
New families: append as img_{max+1}. classDistribution is updated incrementally.

Usage:
  .venv-yolo/bin/python scripts/merge_generator_batch.py \\
    --source <sim Documents/dataset> --dest dataset/dataset
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPLITS = ("train", "validation", "test")
IMG_RE = re.compile(r"img_(\d{6})\.(png|json)$")

REPLACE_FAMILIES = {
    "LoginForm",
    "ToolbarActions",
    "ProgressActivity",
    "MediaCardGrid",
}


def iter_source_pairs(root: Path) -> list[tuple[str, Path, Path]]:
    """List PNG/JSON pairs under source only (small dirs)."""
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
                stem = ent.name[: -len(Path(ent.name).suffix)]
                path = Path(ent.path)
                if m.group(2) == "png":
                    pngs[stem] = path
                else:
                    jsons[stem] = path
        for stem, png in pngs.items():
            js = jsons.get(stem)
            if js is not None:
                pairs.append((split, png, js))
    return pairs


def load_ann(path: Path) -> dict:
    return json.loads(path.read_text())


def family_seed(ann: dict) -> tuple[str, int]:
    gp = ann.get("generatorProfile") or {}
    fam = gp.get("templateFamily") or "unknown"
    seed = int(gp.get("seed") or 0)
    return fam, seed


def element_types(ann: dict) -> list[str]:
    return [e.get("elementType", "") for e in ann.get("elements") or [] if e.get("elementType")]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def next_image_index(manifest: dict) -> int:
    max_n = 0
    for e in manifest.get("entries") or []:
        name = Path(e.get("fileName", "")).name
        m = IMG_RE.match(name)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return max_n + 1


def apply_types(dist: Counter[str], old: list[str], new: list[str]) -> None:
    for t in old:
        dist[t] -= 1
        if dist[t] <= 0:
            del dist[t]
    for t in new:
        dist[t] += 1


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--dest", default=PROJECT_ROOT / "dataset" / "dataset", type=Path)
    p.add_argument(
        "--replace-families",
        default=",".join(sorted(REPLACE_FAMILIES)),
        help="Comma-separated families overwritten in-place by seed",
    )
    p.add_argument(
        "--families",
        default="",
        help="If set, only merge these comma-separated template families",
    )
    args = p.parse_args()
    source = args.source.expanduser().resolve()
    dest = args.dest.expanduser().resolve()
    replace = {s.strip() for s in args.replace_families.split(",") if s.strip()}
    only = {s.strip() for s in args.families.split(",") if s.strip()}

    if not source.is_dir():
        print(f"ERROR: source not found: {source}", flush=True)
        return 1
    dest.mkdir(parents=True, exist_ok=True)
    for split in SPLITS:
        (dest / split).mkdir(parents=True, exist_ok=True)

    man_path = dest / "manifest.json"
    if man_path.exists():
        print("Loading dest manifest.json (no dest dir listing)…", flush=True)
        manifest = json.loads(man_path.read_text())
    else:
        manifest = {"entries": [], "classDistribution": {}}

    dist: Counter[str] = Counter(manifest.get("classDistribution") or {})
    index: dict[tuple[str, int], dict] = {}
    for e in manifest.get("entries") or []:
        fam = e.get("templateFamily")
        seed = e.get("generatorSeed")
        if fam is not None and seed is not None:
            index[(fam, int(seed))] = e

    next_idx = next_image_index(manifest)
    print(f"Listing source pairs under {source}…", flush=True)
    pairs = iter_source_pairs(source)
    print(f"Source pairs: {len(pairs)}  next idx: {next_idx:06d}", flush=True)

    replaced = 0
    appended = 0
    skipped = 0

    for i, (split, png, js) in enumerate(pairs, 1):
        ann = load_ann(js)
        fam, seed = family_seed(ann)
        if only and fam not in only:
            skipped += 1
            continue
        new_types = element_types(ann)
        existing = index.get((fam, seed)) if fam in replace else None
        if existing is not None:
            rel = existing["fileName"]
            dest_png = dest / rel
            dest_json = dest_png.with_suffix(".json")
            old_types: list[str] = []
            if dest_json.exists():
                old_types = element_types(load_ann(dest_json))
            dest_png.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(png, dest_png)
            shutil.copy2(js, dest_json)
            existing["sha256"] = sha256_file(dest_png)
            apply_types(dist, old_types, new_types)
            replaced += 1
        else:
            name = f"img_{next_idx:06d}"
            next_idx += 1
            dest_png = dest / split / f"{name}.png"
            dest_json = dest / split / f"{name}.json"
            shutil.copy2(png, dest_png)
            shutil.copy2(js, dest_json)
            image = ann.get("image") or {}
            gp = ann.get("generatorProfile") or {}
            entry = {
                "fileName": f"{split}/{name}.png",
                "split": split,
                "sha256": sha256_file(dest_png),
                "templateFamily": fam,
                "generatorSeed": seed,
                "isolationTemplate": bool(gp.get("isolationTemplate")),
                "lowDensity": bool(gp.get("lowDensity")),
                "deviceName": image.get("deviceName") or "",
                "pixelScale": int(image.get("scale") or 3),
            }
            manifest.setdefault("entries", []).append(entry)
            index[(fam, seed)] = entry
            apply_types(dist, [], new_types)
            appended += 1
        if i % 50 == 0 or i == len(pairs):
            print(f"  {i}/{len(pairs)} replaced={replaced} appended={appended}", flush=True)

    manifest["classDistribution"] = dict(sorted(dist.items()))
    print("Writing manifest.json…", flush=True)
    man_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"Replaced {replaced}  Appended {appended}  Skipped {skipped}", flush=True)
    print(f"Manifest entries: {len(manifest.get('entries') or [])}", flush=True)
    for k in ("toolbar", "statusBar", "scrollIndicator", "tooltip", "unknown", "pageControl"):
        print(f"  {k}: {dist.get(k, 0)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
