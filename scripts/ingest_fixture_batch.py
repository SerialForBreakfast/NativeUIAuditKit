#!/usr/bin/env python3
"""
ingest_fixture_batch.py — Convert TVTestRig `aatv fixture batch` (FIX-SYNTH-06) output into
NativeUIAuditKit `annotation.schema.json` v1.0 sidecars that `scripts/export_tvos_coco.py`
can consume unchanged.

STATUS (2026-09-18): Written against the REAL Swift implementation in the TVTestRig repo
(`TVTestRig/TVTestRig/SyntheticFactory/FixtureBatchHarvestEngine.swift`, read directly, current
as of TVTestRig commit "Fixture improvement FIX-Synth-02"). This is the SECOND rewrite of this
script in one day — the on-disk layout changed underneath the first correction between reads,
which is exactly why every assumption below is sourced to an exact line range rather than
memory. FIX-SYNTH-01 through 06 are implemented and offline-tested there. **No live hardware
harvest has been run yet** (TVTestRig's own doc: `Docs/Testing/2026-09-18-nua-harvest-unblock.md`
§"Live office harvest" — "Not run... Not claimed: Live office batch output, a trained NUA model,
or token savings."). This script has only been exercised against hand-built fixtures matching
the verified source. Re-run `scripts/test_ingest_fixture_batch.py`'s assumptions against a real
`--output-dir` the moment one exists — a live run can still surface something source-reading
missed.

Verified on-disk layout of `aatv fixture batch --recipes-dir <dir> --output-dir <out>`
(FixtureBatchHarvestEngine.swift:399-468, :487-500):
    <out>/synth-<rowIndex>_unfocused.png   # recipe's baseline frame, duplicated per row
    <out>/synth-<rowIndex>_focused.png     # this row's focused element's frame
    <out>/synth-<rowIndex>_metadata.json   # HarvestPairMetadataFile for this row
    <out>/manifest.json                    # [FixtureHarvestSample] — every accepted row
    <out>/training.json                    # subset where split == "training"
    <out>/calibration.json                 # subset where split == "calibration"
    <out>/held-out.json                    # subset where split == "held-out"

TVTestRig assigns the training/calibration/held-out split itself (bucketed by `recipe_hash`
prefix so a whole recipe family stays on one side — `assignSplits`, line 471) and records it in
`manifest.json`; this script reads that assignment rather than re-deriving one, and treats
`held-out` as the fixture-holdout eval set TASK-6a-10 needs (independent of the synthetic
withheld-template holdout).

`<id>_metadata.json` shape (`HarvestPairMetadataFile.encode`, lines 515-540 — this is what's
actually written; the *decoder* on the TVTestRig side separately accepts NUA-alias key names
too, but that's only relevant to TVTestRig reading `GET /scene`, not to what lands on disk here):
    {
      "id": "synth-<n>",
      "unfocused_png": "synth-<n>_unfocused.png",
      "focused_png": "synth-<n>_focused.png",
      "focused_element_id": <string|null>,
      "is_settled": <bool>,
      "elements": [
        {
          "element_id": <string>,
          "taxonomy_class": <string>,              # validated against category_map.json (BP-28)
          "is_focused": <bool>,                     # reflects the FOCUSED frame's state only
          "normalized_bounds": [xMin, yMin, xMax, yMax],  # top-left origin, [0,1] — confirmed
                                                            # against the GeometryReader-derived
                                                            # producer this time, not just prose
          "pixel_bounds": [?, ?, ?, ?]              # order still not confirmed from a producer
                                                      # (only validated as count==4, [2]>0, [3]>0
                                                      # in the Swift source) — not trusted here;
                                                      # boundsPixels is derived from
                                                      # normalized_bounds x the known 1920x1080
                                                      # frame instead, correct by construction.
        }, ...
      ],
      "recipe": {"recipe_hash": <string>, "seed": <int>, "archetype": <string>, "step_index": <int>}
    }

Known correctness issue this script fixes rather than reproduces: the baseline `_unfocused.png`
is the SAME file content across every row of one recipe (frame 0, captured once, reused), but
each row's `elements` list reflects whichever element is focused in THAT row's focused frame.
Naively ingesting `_unfocused.png` with its row's `elements` list would falsely mark an element
as focused in an image where nothing is glowing. This script ingests each unique
`_unfocused.png` (deduped by its own SHA-256, since content is identical across a recipe's rows)
exactly once, with every element's `is_focused` forced to `False` — the true state of that
baseline frame. `_focused.png` frames are ingested as-is, one per manifest row.

What this script enforces regardless of any remaining uncertainty:
  - BP-28: any `taxonomy_class` not in `Research/schemas/category_map.json` is dropped, counted,
    and reported — never trained on, never remapped.
  - Full-frame preservation: every element in a scene is carried into one sidecar per image.
    Nothing here ever crops to a single element's ROI.
  - Uses TVTestRig's own `held-out` split as the fixture holdout — never blends it into train.
  - Never writes outside this package (`--output` defaults inside the repo; refuses to write
    above `PROJECT_ROOT`).

Usage:
  .venv-yolo/bin/python scripts/ingest_fixture_batch.py --dry-run --input <aatv-output-dir>
  .venv-yolo/bin/python scripts/ingest_fixture_batch.py --input <aatv-output-dir> \\
      --output dataset/tvos_fixture_batch_ingested
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from harvest_bundle_validation import HarvestValidationError, validate_bundle

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATEGORY_MAP = PROJECT_ROOT / "Research" / "schemas" / "category_map.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "dataset" / "tvos_fixture_batch_ingested"

# Every real tvOS capture observed so far (dataset/tvos_captures, dataset/tvos_fixture_captures)
# is 1920x1080 at scale 1; `aatv fixture batch` targets the same fixture app. `annotation.
# schema.json`'s `image.scale` enum is [2, 3] only (iOS/iPadOS-oriented) — existing tvOS
# sidecars already violate that enum with scale=1; this script matches existing tvOS practice
# rather than fixing the schema (a deliberate version bump, out of scope here).
FRAME_PIXEL_WIDTH = 1920
FRAME_PIXEL_HEIGHT = 1080

# TVTestRig's own split names -> this script's output directory names. "calibration" is kept
# distinct from "training" rather than folded in, since its purpose upstream (confidence/
# threshold calibration) is different from what a training split implies.
SPLIT_DIR_NAMES = {"training": "train", "calibration": "calibration", "held-out": "fixture_holdout"}


def load_category_names(path: Path) -> set:
    data = json.loads(path.read_text())
    return {c["name"] for c in data["categories"]}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def load_manifest_rows(input_dir: Path) -> List[Dict[str, Any]]:
    manifest_path = input_dir / "manifest.json"
    if not manifest_path.exists():
        return []
    try:
        rows = json.loads(manifest_path.read_text())
    except json.JSONDecodeError:
        return []
    return [r for r in rows if isinstance(r, dict) and "id" in r]


def normalized_bounds_to_vision(bounds: List[float]) -> Optional[Dict[str, float]]:
    """`[xMin, yMin, xMax, yMax]` top-left-origin -> Vision-normalized bottom-left-origin
    `{x, y, width, height}`, matching `boundsVisionNormalized` in annotation.schema.json."""
    if not isinstance(bounds, (list, tuple)) or len(bounds) != 4:
        return None
    x_min, y_min, x_max, y_max = (float(v) for v in bounds)
    width = x_max - x_min
    height = y_max - y_min
    if width <= 0 or height <= 0:
        return None
    vision_x = min(max(x_min, 0.0), 1.0)
    vision_y = min(max(1.0 - y_max, 0.0), 1.0)
    width = min(max(width, 1e-6), 1.0)
    height = min(max(height, 1e-6), 1.0)
    return {"x": vision_x, "y": vision_y, "width": width, "height": height}


def build_element(
    raw: Dict[str, Any],
    known_classes: set,
    dropped_classes: Counter,
    force_unfocused: bool,
) -> Optional[Dict[str, Any]]:
    role = raw.get("taxonomy_class")
    if role not in known_classes:
        dropped_classes[str(role)] += 1
        return None  # BP-28: never remap or invent a mapping for an unfrozen class name

    vision_rect = normalized_bounds_to_vision(raw.get("normalized_bounds"))
    if vision_rect is None:
        return None

    # boundsPixels derived from the normalized rect against the known frame size — pixel_bounds'
    # own array order was never independently confirmed from a producer (see module docstring),
    # so it is not trusted here even though it's present on the wire.
    pixel_rect = {
        "x": vision_rect["x"] * FRAME_PIXEL_WIDTH,
        "y": (1.0 - vision_rect["y"] - vision_rect["height"]) * FRAME_PIXEL_HEIGHT,
        "width": vision_rect["width"] * FRAME_PIXEL_WIDTH,
        "height": vision_rect["height"] * FRAME_PIXEL_HEIGHT,
    }

    is_focused = False if force_unfocused else bool(raw.get("is_focused", False))

    return {
        "id": str(raw.get("element_id", "")),
        "elementType": role,
        "framework": "tvOS-UIKit",
        "boundsPixels": pixel_rect,
        "boundsPoints": pixel_rect,  # tvOS scale=1: points == pixels, matches existing captures
        "boundsVisionNormalized": vision_rect,
        "visibleText": None,
        "accessibilityLabel": None,
        "accessibilityHint": None,
        "traits": [],
        "state": {
            "isEnabled": True,
            "isSelected": False,
            "isFocused": is_focused,
        },
        "occluded": False,
        "excluded": False,
        "knownIssues": [],
    }


def build_sidecar(png_path: Path, elements: List[Dict[str, Any]], recipe: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schemaVersion": "1.1",
        "imageSHA256": sha256_of(png_path),
        "image": {
            "fileName": png_path.name,
            "pixelWidth": FRAME_PIXEL_WIDTH,
            "pixelHeight": FRAME_PIXEL_HEIGHT,
            "scale": 1,
            "platform": "tvOS",
            "osVersion": "unknown",
            "deviceName": "TVTestRigFixture (aatv fixture batch)",
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
            "templateFamily": f"TVTestRigFixtureBatch.{recipe.get('archetype', 'unknown')}",
            "seed": int(recipe.get("seed", 0)),
            "generatorVersion": "fix-synth-06-ingest-v2",
            "isolationTemplate": False,
            "lowDensity": False,
            # Not meaningful for fixture-batch-sourced captures (this field was designed for
            # xcrun simctl status_bar overrides on synthetic simulator renders). Filled with a
            # documented sentinel purely to satisfy the shared sidecar shape.
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, required=True, help="aatv fixture batch --output-dir directory")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Ingested sidecar+image output directory (must stay inside the repo)")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report counts; write nothing")
    parser.add_argument("--legacy-fixture-mode", action="store_true", help="TEST ONLY: bypass completed-bundle validation for legacy parser fixtures")
    args = parser.parse_args()

    output_dir = args.output.resolve()
    try:
        output_dir.relative_to(PROJECT_ROOT)
    except ValueError:
        print(f"Refusing to write outside the project: {output_dir}", file=sys.stderr)
        return 1

    if not args.input.exists():
        print(f"Input directory does not exist: {args.input}", file=sys.stderr)
        print("No real `aatv fixture batch` output has been produced yet — FIX-SYNTH-01..06 are "
              "implemented in TVTestRig but no live 'office' harvest has been run (see module "
              "docstring). This is expected until that changes.", file=sys.stderr)
        return 1

    if not args.legacy_fixture_mode:
        try:
            contract = validate_bundle(args.input)
        except HarvestValidationError as exc:
            print(f"Harvest bundle validation failed: {exc}", file=sys.stderr)
            return 1
        if not contract["usableRows"]:
            print("Harvest bundle has no usable known-taxonomy annotations; not eligible for ingestion.", file=sys.stderr)
            return 1

    rows = load_manifest_rows(args.input)
    if not rows:
        print(f"No manifest.json (or it was empty) under {args.input} — cannot determine "
              "train/calibration/held-out split assignment or locate metadata files.", file=sys.stderr)
        return 1

    known_classes = load_category_names(CATEGORY_MAP)
    dropped_classes: Counter = Counter()
    kept_classes: Counter = Counter()
    split_counts: Counter = Counter()
    written: List[tuple] = []  # (png_path, split_dir_name, sidecar)
    seen_unfocused_sha256: set = set()

    for row in rows:
        row_id = row["id"]
        metadata_path = args.input / f"{row_id}_metadata.json"
        if not metadata_path.exists():
            print(f"Skipping {row_id}: missing {metadata_path.name}", file=sys.stderr)
            continue
        try:
            pair = json.loads(metadata_path.read_text())
        except json.JSONDecodeError as exc:
            print(f"Skipping {metadata_path}: invalid JSON ({exc})", file=sys.stderr)
            continue

        raw_elements = pair.get("elements", [])
        if not isinstance(raw_elements, list):
            print(f"Skipping {metadata_path}: 'elements' is not a list", file=sys.stderr)
            continue

        recipe = pair.get("recipe") or {}
        tvtestrig_split = row.get("split")
        split_dir_name = SPLIT_DIR_NAMES.get(tvtestrig_split, "train")

        focused_png = args.input / pair.get("focused_png", f"{row_id}_focused.png")
        if focused_png.exists():
            elements = []
            for raw in raw_elements:
                elem = build_element(raw, known_classes, dropped_classes, force_unfocused=False)
                if elem is not None:
                    elements.append(elem)
                    kept_classes[elem["elementType"]] += 1
            split_counts[split_dir_name] += 1
            written.append((focused_png, split_dir_name, build_sidecar(focused_png, elements, recipe)))
        else:
            print(f"Skipping {focused_png.name}: file missing", file=sys.stderr)

        unfocused_png = args.input / pair.get("unfocused_png", f"{row_id}_unfocused.png")
        if unfocused_png.exists():
            unfocused_sha = sha256_of(unfocused_png)
            if unfocused_sha not in seen_unfocused_sha256:
                seen_unfocused_sha256.add(unfocused_sha)
                elements = []
                for raw in raw_elements:
                    elem = build_element(raw, known_classes, dropped_classes, force_unfocused=True)
                    if elem is not None:
                        elements.append(elem)
                        kept_classes[elem["elementType"]] += 1
                split_counts[split_dir_name] += 1
                written.append((unfocused_png, split_dir_name, build_sidecar(unfocused_png, elements, recipe)))

    print(f"Discovered {len(rows)} manifest rows")
    print(f"Ingesting {len(written)} images (focused frames + deduped unfocused baselines)")
    print(f"Kept {sum(kept_classes.values())} elements across {len(kept_classes)} classes")
    if dropped_classes:
        print(f"Dropped {sum(dropped_classes.values())} elements with unrecognized taxonomy_class (BP-28):")
        for name, count in dropped_classes.most_common():
            print(f"  {name!r}: {count}")
    print(f"Split assignment: {dict(split_counts)}")

    if args.dry_run:
        print("--dry-run: nothing written")
        return 0

    for png_path, split_dir_name, sidecar in written:
        split_dir = output_dir / split_dir_name
        split_dir.mkdir(parents=True, exist_ok=True)
        (split_dir / png_path.name).write_bytes(png_path.read_bytes())
        (split_dir / f"{png_path.stem}.json").write_text(json.dumps(sidecar, indent=2) + "\n")

    print(f"Wrote {len(written)} sidecar+image pairs to {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
