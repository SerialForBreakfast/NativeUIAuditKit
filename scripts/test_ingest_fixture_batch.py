#!/usr/bin/env python3
"""
test_ingest_fixture_batch.py — Offline self-test for `scripts/ingest_fixture_batch.py`.

No real `aatv fixture batch --output-dir` sample exists yet (TVTestRig has implemented and
offline-tested FIX-SYNTH-01..06, but `Docs/Testing/2026-09-18-nua-harvest-unblock.md` in the
TVTestRig repo is explicit: "Live office harvest: not run"), so this exercises the conversion/
validation logic against hand-built fixtures matching the *verified* on-disk format read
directly from TVTestRig's `FixtureBatchHarvestEngine.swift` source: `<id>_unfocused.png` /
`<id>_focused.png` / `<id>_metadata.json` triples plus `manifest.json` split assignment. It
proves the script's logic is correct against that verified format — it does not prove a real
harvest run won't surface something the source reading missed. Re-run against a real
`--output-dir` the moment one exists.

All output goes under `.build/debug-output/` (ephemeral, in-project) per AGENTS.md.

Usage:
  .venv-yolo/bin/python scripts/test_ingest_fixture_batch.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import ingest_fixture_batch as ifb  # noqa: E402

WORK_DIR = PROJECT_ROOT / ".build" / "debug-output" / "ingest_fixture_batch_test"
INPUT_DIR = WORK_DIR / "input"
OUTPUT_DIR = WORK_DIR / "output"

UNFOCUSED_PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"baseline frame, geometry-only test fixture"
FOCUSED_PNG_BYTES_TMPL = b"\x89PNG\r\n\x1a\n" + b"focused frame %d, geometry-only test fixture"


def write_row(
    row_id: str,
    elements: list,
    recipe: dict,
    focused_element_id: str | None,
    unfocused_png_bytes: bytes,
    focused_png_bytes: bytes,
) -> None:
    (INPUT_DIR / f"{row_id}_unfocused.png").write_bytes(unfocused_png_bytes)
    (INPUT_DIR / f"{row_id}_focused.png").write_bytes(focused_png_bytes)
    metadata = {
        "id": row_id,
        "unfocused_png": f"{row_id}_unfocused.png",
        "focused_png": f"{row_id}_focused.png",
        "focused_element_id": focused_element_id,
        "is_settled": True,
        "elements": elements,
        "recipe": recipe,
    }
    (INPUT_DIR / f"{row_id}_metadata.json").write_text(json.dumps(metadata))


def write_manifest(rows: list) -> None:
    (INPUT_DIR / "manifest.json").write_text(json.dumps(rows))


def reset_workdir() -> None:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)


def approx(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) < tol


def run_checks() -> int:
    failures = []

    def check(label: str, condition: bool) -> None:
        status = "PASS" if condition else "FAIL"
        print(f"[{status}] {label}")
        if not condition:
            failures.append(label)

    # --- unit-level: coordinate conversion ---
    vision = ifb.normalized_bounds_to_vision([0.0, 0.10, 0.25, 0.40])
    check(
        "normalized_bounds_to_vision: top-left -> Vision bottom-left conversion",
        vision is not None
        and approx(vision["x"], 0.0)
        and approx(vision["y"], 0.6)
        and approx(vision["width"], 0.25)
        and approx(vision["height"], 0.30),
    )

    degenerate = ifb.normalized_bounds_to_vision([0.5, 0.5, 0.5, 0.5])
    check("normalized_bounds_to_vision: zero-area box rejected", degenerate is None)

    # --- unit-level: BP-28 class rejection + force_unfocused ---
    known = ifb.load_category_names(ifb.CATEGORY_MAP)
    dropped = __import__("collections").Counter()
    focused_elem = ifb.build_element(
        {
            "element_id": "e1",
            "taxonomy_class": "primaryButton",
            "normalized_bounds": [0.1, 0.1, 0.3, 0.2],
            "pixel_bounds": [192, 108, 384, 108],
            "is_focused": True,
        },
        known, dropped, force_unfocused=False,
    )
    check("build_element: known class kept, is_focused honored", focused_elem is not None and focused_elem["state"]["isFocused"] is True)

    forced_unfocused_elem = ifb.build_element(
        {
            "element_id": "e1",
            "taxonomy_class": "primaryButton",
            "normalized_bounds": [0.1, 0.1, 0.3, 0.2],
            "is_focused": True,  # source says focused...
        },
        known, dropped, force_unfocused=True,  # ...but this is the shared baseline frame
    )
    check(
        "build_element: force_unfocused overrides is_focused=True for the baseline frame",
        forced_unfocused_elem is not None and forced_unfocused_elem["state"]["isFocused"] is False,
    )

    unknown_elem = ifb.build_element(
        {"element_id": "e2", "taxonomy_class": "tabBarItem", "normalized_bounds": [0.4, 0.4, 0.6, 0.5]},
        known, dropped, force_unfocused=False,
    )
    check("build_element: unknown class ('tabBarItem') is dropped, not remapped (BP-28)", unknown_elem is None)
    check("build_element: dropped class is counted", dropped["tabBarItem"] == 1)

    # --- integration: full CLI run against synthetic fixtures matching the verified format ---
    reset_workdir()
    recipe_a = {"recipe_hash": "aaaa1111", "seed": 1, "archetype": "gridMatrix", "step_index": 1}
    recipe_b = {"recipe_hash": "bbbb2222", "seed": 2, "archetype": "settingsList", "step_index": 1}

    shared_unfocused_a = UNFOCUSED_PNG_BYTES + b"-recipeA"

    # Recipe A, two focus steps -> two rows (synth-0, synth-1) SHARING one unfocused baseline.
    write_row(
        "synth-0",
        [
            {"element_id": "card_0", "taxonomy_class": "collectionItem", "is_focused": True,
             "normalized_bounds": [0.05, 0.10, 0.30, 0.40], "pixel_bounds": [96, 108, 480, 324]},
            {"element_id": "card_1", "taxonomy_class": "collectionItem", "is_focused": False,
             "normalized_bounds": [0.35, 0.10, 0.60, 0.40], "pixel_bounds": [672, 108, 480, 324]},
            {"element_id": "bad_label", "taxonomy_class": "tabBarItem", "is_focused": False,
             "normalized_bounds": [0.05, 0.42, 0.30, 0.46]},  # deliberately invalid
        ],
        recipe_a, "card_0", shared_unfocused_a, FOCUSED_PNG_BYTES_TMPL % 0,
    )
    write_row(
        "synth-1",
        [
            {"element_id": "card_0", "taxonomy_class": "collectionItem", "is_focused": False,
             "normalized_bounds": [0.05, 0.10, 0.30, 0.40], "pixel_bounds": [96, 108, 480, 324]},
            {"element_id": "card_1", "taxonomy_class": "collectionItem", "is_focused": True,
             "normalized_bounds": [0.35, 0.10, 0.60, 0.40], "pixel_bounds": [672, 108, 480, 324]},
        ],
        recipe_a, "card_1", shared_unfocused_a, FOCUSED_PNG_BYTES_TMPL % 1,
    )
    # Recipe B, one focus step -> one row (synth-2), different split bucket.
    write_row(
        "synth-2",
        [
            {"element_id": "row_0", "taxonomy_class": "listRow", "is_focused": True,
             "normalized_bounds": [0.10, 0.10, 0.90, 0.16], "pixel_bounds": [192, 108, 1536, 65]},
        ],
        recipe_b, "row_0", UNFOCUSED_PNG_BYTES + b"-recipeB", FOCUSED_PNG_BYTES_TMPL % 2,
    )
    write_manifest(
        [
            {"id": "synth-0", "path": "synth-0_focused.png", "split": "training"},
            {"id": "synth-1", "path": "synth-1_focused.png", "split": "training"},
            {"id": "synth-2", "path": "synth-2_focused.png", "split": "held-out"},
        ]
    )

    dry_run = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "ingest_fixture_batch.py"),
         "--input", str(INPUT_DIR), "--output", str(OUTPUT_DIR), "--dry-run", "--legacy-fixture-mode"],
        capture_output=True, text=True,
    )
    check("CLI --dry-run exits 0", dry_run.returncode == 0)
    check("CLI --dry-run writes nothing", not OUTPUT_DIR.exists())
    check("CLI --dry-run reports the dropped class", "tabBarItem" in dry_run.stdout)
    # 2 focused (recipe A) + 1 deduped unfocused (recipe A) + 1 focused (recipe B) + 1 unfocused (B) = 5
    check("CLI --dry-run dedupes the shared recipe-A baseline (5 images, not 6)", "Ingesting 5 images" in dry_run.stdout)

    real_run = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "ingest_fixture_batch.py"),
         "--input", str(INPUT_DIR), "--output", str(OUTPUT_DIR), "--legacy-fixture-mode"],
        capture_output=True, text=True,
    )
    check("CLI real run exits 0", real_run.returncode == 0)

    train_pngs = list((OUTPUT_DIR / "train").glob("*.png")) if (OUTPUT_DIR / "train").exists() else []
    holdout_pngs = list((OUTPUT_DIR / "fixture_holdout").glob("*.png")) if (OUTPUT_DIR / "fixture_holdout").exists() else []
    # train: synth-0_focused, synth-1_focused, one deduped recipe-A unfocused = 3
    # fixture_holdout: synth-2_focused, synth-2_unfocused = 2
    check("CLI real run: manifest split honored with baseline dedup (3 train, 2 held-out)", len(train_pngs) == 3 and len(holdout_pngs) == 2)

    unfocused_sidecars = [p for p in train_pngs if "_unfocused" in p.name]
    if unfocused_sidecars:
        sidecar = json.loads((OUTPUT_DIR / "train" / f"{unfocused_sidecars[0].stem}.json").read_text())
        all_unfocused = all(not e["state"]["isFocused"] for e in sidecar["elements"])
        check("Deduped baseline sidecar: every element forced isFocused=False", all_unfocused)

    if train_pngs:
        sample = json.loads((OUTPUT_DIR / "train" / f"{train_pngs[0].stem}.json").read_text())
        required_top_level = {"schemaVersion", "imageSHA256", "image", "generatorProfile", "elements"}
        check("Written sidecar has all annotation.schema.json v1.0 required top-level keys", required_top_level.issubset(sample.keys()))
        check("Written sidecar: schemaVersion is '1.1' for tvOS scale 1", sample.get("schemaVersion") == "1.1")

    focused_sidecars = [p for p in train_pngs if "_focused" in p.name]
    if focused_sidecars:
        sample = json.loads((OUTPUT_DIR / "train" / f"{focused_sidecars[0].stem}.json").read_text())
        elem_types = {e["elementType"] for e in sample["elements"]}
        check("Written focused sidecar: no dropped class leaked through", "tabBarItem" not in elem_types)
        check("Written focused sidecar: kept element carried through", "collectionItem" in elem_types)

    print()
    if failures:
        print(f"{len(failures)} check(s) FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
