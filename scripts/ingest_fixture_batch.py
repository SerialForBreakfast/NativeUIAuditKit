#!/usr/bin/env python3
"""
ingest_fixture_batch.py — Convert TVTestRig `aatv fixture batch` (FIX-SYNTH-06) output into
NativeUIAuditKit `annotation.schema.json` v1.0 sidecars that `scripts/export_tvos_coco.py`
can consume unchanged.

STATUS (2026-09-18): Written against TVTestRig's *documented* wire schema
(`Docs/Research/2026-09-17-fix-synth-and-meta-specifications.md`, FIX-SYNTH-02 / FIX-SYNTH-06
in the TVTestRig repo), not a verified real sample. FIX-SYNTH-02 (the `GET /scene`
ground-truth telemetry server) is unimplemented and FIX-SYNTH-06 has only been
mock-provider-tested — no live `office` harvest has been run. Every real capture currently in
`dataset/` has `"elements": []` (verified 2026-09-18, zero non-empty sidecars out of 88).
Re-validate every assumption below against a real `aatv fixture batch` output directory before
trusting this for an actual training run.

Assumed on-disk layout per recipe/element pair (FIX-SYNTH-06 step 5):
    <id>_unfocused.png
    <id>_focused.png
    <id>_metadata.json      # one `GET /scene`-shaped payload, applied to both frames

Assumed `<id>_metadata.json` shape (FIX-SYNTH-02 wire schema):
    {
      "schemaVersion": 1,
      "timestampMs": <int>,
      "isSettled": <bool>,
      "activeFocusId": <string|null>,
      "elements": [
        {
          "id": <string>,
          "taxonomyRole": <string>,                    # one of the 41 category_map.json names
          "normalizedRect": [xMin, yMin, xMax, yMax],   # top-left origin, GeometryReader-derived
          "nativePixelRect": [x, y, w, h],               # top-left origin, pixels
          "accessibilityTraits": [<string>, ...],
          "textContent": <string|null>,
          "isFocused": <bool>
        }, ...
      ]
    }

Known open questions (ask TVTestRig once real output exists, do not guess further here):
  - Does one metadata.json really cover both the unfocused and focused frame, or does each
    frame get its own (`<id>_unfocused_metadata.json` / `<id>_focused_metadata.json`)? This
    script accepts either layout (see `_find_metadata_for`).
  - `normalizedRect`'s corner order/origin is inferred from FIX-SYNTH-02's prose
    ("x_min = frame.minX / window.width", GeometryReader default top-left origin) — never
    verified against a real payload.

What this script enforces regardless of the above uncertainty:
  - BP-28: any `taxonomyRole` not in `Research/schemas/category_map.json` is dropped, counted,
    and reported — never trained on, never remapped.
  - Full-frame preservation: every element in a scene is carried into one sidecar per image.
    Nothing here ever crops to a single element's ROI.
  - Held-out fixture split is independent of the synthetic withheld-template holdout — grouped
    by recipe id, never split at the individual-frame level, so a whole recipe stays on one
    side (train vs. fixture_holdout).
  - Never writes outside this package (`--output` defaults inside the repo; refuses to write
    above `PROJECT_ROOT`).

Usage:
  .venv-yolo/bin/python scripts/ingest_fixture_batch.py --dry-run --input <fixture-batch-dir>
  .venv-yolo/bin/python scripts/ingest_fixture_batch.py --input <fixture-batch-dir> \\
      --output dataset/tvos_fixture_batch_ingested
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATEGORY_MAP = PROJECT_ROOT / "Research" / "schemas" / "category_map.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "dataset" / "tvos_fixture_batch_ingested"

# tvOS fixture-batch captures observed so far are 1920x1080 at scale 1 (see dataset/tvos_captures
# sidecars). `annotation.schema.json`'s `image.scale` enum is [2, 3] only (iOS/iPadOS-oriented) —
# every existing tvOS sidecar already violates that enum with scale=1. Not fixed here (a schema
# change is a separate, deliberate version bump); this script matches existing tvOS practice.
DEFAULT_PIXEL_WIDTH = 1920
DEFAULT_PIXEL_HEIGHT = 1080


def load_category_names(path: Path) -> set:
    data = json.loads(path.read_text())
    return {c["name"] for c in data["categories"]}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _find_metadata_for(png_path: Path) -> Optional[Path]:
    """Accept either one shared `<id>_metadata.json`, or a per-frame
    `<id>_unfocused_metadata.json` / `<id>_focused_metadata.json` — the real on-disk
    convention is unverified (see module docstring)."""
    stem = png_path.stem  # "<id>_unfocused" or "<id>_focused"
    per_frame = png_path.with_name(f"{stem}_metadata.json")
    if per_frame.exists():
        return per_frame
    if stem.endswith("_unfocused") or stem.endswith("_focused"):
        recipe_id = stem.rsplit("_", 1)[0]
        shared = png_path.with_name(f"{recipe_id}_metadata.json")
        if shared.exists():
            return shared
    return None


def _recipe_id_for(png_path: Path) -> str:
    stem = png_path.stem
    if stem.endswith("_unfocused") or stem.endswith("_focused"):
        return stem.rsplit("_", 1)[0]
    return stem


def normalized_rect_to_vision(rect: List[float]) -> Optional[Dict[str, float]]:
    """`[xMin, yMin, xMax, yMax]` top-left-origin -> Vision-normalized bottom-left-origin
    `{x, y, width, height}`, matching `boundsVisionNormalized` in annotation.schema.json."""
    if not isinstance(rect, (list, tuple)) or len(rect) != 4:
        return None
    x_min, y_min, x_max, y_max = (float(v) for v in rect)
    width = x_max - x_min
    height = y_max - y_min
    if width <= 0 or height <= 0:
        return None
    vision_x = min(max(x_min, 0.0), 1.0)
    vision_y = min(max(1.0 - y_max, 0.0), 1.0)
    width = min(max(width, 1e-6), 1.0)
    height = min(max(height, 1e-6), 1.0)
    return {"x": vision_x, "y": vision_y, "width": width, "height": height}


def native_pixel_rect_to_bounds(rect: Optional[List[float]]) -> Optional[Dict[str, float]]:
    if not isinstance(rect, (list, tuple)) or len(rect) != 4:
        return None
    x, y, w, h = (float(v) for v in rect)
    if w <= 0 or h <= 0:
        return None
    return {"x": x, "y": y, "width": w, "height": h}


def build_element(
    raw: Dict[str, Any],
    known_classes: set,
    dropped_classes: Counter,
) -> Optional[Dict[str, Any]]:
    role = raw.get("taxonomyRole") or raw.get("elementType")
    if role not in known_classes:
        dropped_classes[str(role)] += 1
        return None  # BP-28: never remap or invent a mapping for an unfrozen class name

    vision_rect = normalized_rect_to_vision(raw.get("normalizedRect"))
    if vision_rect is None:
        return None

    pixel_rect = native_pixel_rect_to_bounds(raw.get("nativePixelRect"))
    if pixel_rect is None:
        # Fall back to deriving pixels from the normalized rect against the assumed frame size.
        x_min, y_min, x_max, y_max = raw["normalizedRect"]
        pixel_rect = {
            "x": x_min * DEFAULT_PIXEL_WIDTH,
            "y": y_min * DEFAULT_PIXEL_HEIGHT,
            "width": (x_max - x_min) * DEFAULT_PIXEL_WIDTH,
            "height": (y_max - y_min) * DEFAULT_PIXEL_HEIGHT,
        }

    return {
        "id": str(raw.get("id", "")),
        "elementType": role,
        "framework": "tvOS-UIKit",
        "boundsPixels": pixel_rect,
        "boundsPoints": pixel_rect,  # tvOS scale=1: points == pixels, matches existing captures
        "boundsVisionNormalized": vision_rect,
        "visibleText": raw.get("textContent"),
        "accessibilityLabel": None,
        "accessibilityHint": None,
        "traits": list(raw.get("accessibilityTraits", [])),
        "state": {
            "isEnabled": True,
            "isSelected": False,
            "isFocused": bool(raw.get("isFocused", False)),
        },
        "occluded": False,
        "excluded": False,
        "knownIssues": [],
    }


def build_sidecar(png_path: Path, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "schemaVersion": "1.0",
        "imageSHA256": sha256_of(png_path),
        "image": {
            "fileName": png_path.name,
            "pixelWidth": DEFAULT_PIXEL_WIDTH,
            "pixelHeight": DEFAULT_PIXEL_HEIGHT,
            "scale": 1,
            "platform": "tvOS",
            "osVersion": "unknown",
            "deviceName": "Apple TV (fixture batch)",
            "interfaceIdiom": "tv",
            "orientation": "landscape",
            "colorScheme": "dark",
            "dynamicTypeSize": "large",
            "locale": "en_US",
            "layoutDirection": "ltr",
            "safeAreaInsets": {"top": 60, "left": 90, "bottom": 60, "right": 90},
            "reduceTransparency": False,
            "increaseContrast": False,
            "boldText": False,
            "buttonShapes": False,
            "onOffLabels": False,
            "smartInvert": False,
        },
        "generatorProfile": {
            "templateFamily": "TVTestRigFixtureBatch",
            "seed": int(sha256_of(png_path)[:8], 16),
            "generatorVersion": "fix-synth-06-ingest-v1",
            "isolationTemplate": False,
            "lowDensity": False,
            # Not meaningful for real/fixture-batch-sourced captures (this field was designed
            # for xcrun simctl status_bar overrides on synthetic simulator renders). Filled with
            # a documented sentinel purely to satisfy the shared sidecar shape.
            "simulatorState": {
                "time": "00:00",
                "batteryLevel": 100,
                "batteryState": "charging",
                "cellularBars": 0,
                "wifiBars": 3,
                "operatorName": "N/A",
            },
        },
        "elements": elements,
    }


def discover_pairs(input_dir: Path) -> List[Tuple[Path, Path]]:
    """Returns (png_path, metadata_path) for every frame with a resolvable metadata file."""
    pairs: List[Tuple[Path, Path]] = []
    for png_path in sorted(input_dir.rglob("*.png")):
        metadata_path = _find_metadata_for(png_path)
        if metadata_path is not None:
            pairs.append((png_path, metadata_path))
    return pairs


def assign_splits(recipe_ids: List[str], holdout_fraction: float) -> Dict[str, str]:
    """Whole-recipe train/fixture_holdout assignment — never splits frames from the same
    recipe across both sides (mirrors BP-32's family-holdout requirement)."""
    unique_recipes = sorted(set(recipe_ids))
    n_holdout = max(1, round(len(unique_recipes) * holdout_fraction)) if unique_recipes else 0
    holdout_set = set(unique_recipes[:n_holdout])
    return {rid: ("fixture_holdout" if rid in holdout_set else "train") for rid in unique_recipes}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, required=True, help="aatv fixture batch output directory")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Ingested sidecar+image output directory (must stay inside the repo)")
    parser.add_argument("--holdout-fraction", type=float, default=0.2, help="Fraction of distinct recipes assigned to the fixture holdout split")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report counts; write nothing")
    args = parser.parse_args()

    output_dir = args.output.resolve()
    try:
        output_dir.relative_to(PROJECT_ROOT)
    except ValueError:
        print(f"Refusing to write outside the project: {output_dir}", file=sys.stderr)
        return 1

    if not args.input.exists():
        print(f"Input directory does not exist: {args.input}", file=sys.stderr)
        print("No real aatv fixture batch output has been produced yet (FIX-SYNTH-02/06 status, "
              "see module docstring) — this is expected until TVTestRig ships it.", file=sys.stderr)
        return 1

    known_classes = load_category_names(CATEGORY_MAP)
    pairs = discover_pairs(args.input)
    if not pairs:
        print(f"No PNG+metadata pairs found under {args.input}", file=sys.stderr)
        return 1

    dropped_classes: Counter = Counter()
    kept_classes: Counter = Counter()
    recipe_ids = [_recipe_id_for(png) for png, _ in pairs]
    splits = assign_splits(recipe_ids, args.holdout_fraction)

    sidecars: List[Tuple[Path, str, Dict[str, Any]]] = []  # (png_path, split, sidecar)
    for png_path, metadata_path in pairs:
        try:
            metadata = json.loads(metadata_path.read_text())
        except json.JSONDecodeError as exc:
            print(f"Skipping {metadata_path}: invalid JSON ({exc})", file=sys.stderr)
            continue

        raw_elements = metadata.get("elements", [])
        if not isinstance(raw_elements, list):
            print(f"Skipping {metadata_path}: 'elements' is not a list", file=sys.stderr)
            continue

        elements = []
        for raw in raw_elements:
            elem = build_element(raw, known_classes, dropped_classes)
            if elem is not None:
                elements.append(elem)
                kept_classes[elem["elementType"]] += 1

        recipe_id = _recipe_id_for(png_path)
        split = splits[recipe_id]
        sidecar = build_sidecar(png_path, elements)
        sidecars.append((png_path, split, sidecar))

    print(f"Discovered {len(pairs)} image+metadata pairs across {len(splits)} recipes")
    print(f"Kept {sum(kept_classes.values())} elements across {len(kept_classes)} classes")
    if dropped_classes:
        print(f"Dropped {sum(dropped_classes.values())} elements with unrecognized taxonomyRole (BP-28):")
        for name, count in dropped_classes.most_common():
            print(f"  {name!r}: {count}")
    split_counts = Counter(split for _, split, _ in sidecars)
    print(f"Split assignment: {dict(split_counts)}")

    if args.dry_run:
        print("--dry-run: nothing written")
        return 0

    for png_path, split, sidecar in sidecars:
        split_dir = output_dir / split
        split_dir.mkdir(parents=True, exist_ok=True)
        dest_png = split_dir / png_path.name
        dest_png.write_bytes(png_path.read_bytes())
        dest_json = split_dir / f"{png_path.stem}.json"
        dest_json.write_text(json.dumps(sidecar, indent=2) + "\n")

    print(f"Wrote {len(sidecars)} sidecar+image pairs to {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
