#!/usr/bin/env python3
"""
test_ingest_fixture_batch.py — Offline self-test for `scripts/ingest_fixture_batch.py`.

No real `aatv fixture batch` output exists yet (FIX-SYNTH-02 unimplemented in TVTestRig, see
`ingest_fixture_batch.py`'s module docstring), so this exercises the conversion/validation logic
against hand-built fixtures matching the *documented* FIX-SYNTH-02 wire schema. It proves the
script's logic is correct against that documented contract — it does NOT prove the contract
matches what TVTestRig will actually write to disk. Re-run against a real sample once one exists.

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

FAKE_PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"not a real png, geometry-only test fixture"


def write_recipe(recipe_id: str, elements: list) -> None:
    metadata = {
        "schemaVersion": 1,
        "timestampMs": 0,
        "isSettled": True,
        "activeFocusId": elements[0]["id"] if elements else None,
        "elements": elements,
    }
    (INPUT_DIR / f"{recipe_id}_metadata.json").write_text(json.dumps(metadata))
    (INPUT_DIR / f"{recipe_id}_unfocused.png").write_bytes(FAKE_PNG_BYTES)
    (INPUT_DIR / f"{recipe_id}_focused.png").write_bytes(FAKE_PNG_BYTES)


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
    # A box spanning the left 25% width, top 10%-40% height (top-left origin) should become
    # Vision bottom-left-origin x=0.0, y=1-0.4=0.6, width=0.25, height=0.3.
    vision = ifb.normalized_rect_to_vision([0.0, 0.10, 0.25, 0.40])
    check(
        "normalized_rect_to_vision: top-left -> Vision bottom-left conversion",
        vision is not None
        and approx(vision["x"], 0.0)
        and approx(vision["y"], 0.6)
        and approx(vision["width"], 0.25)
        and approx(vision["height"], 0.30),
    )

    degenerate = ifb.normalized_rect_to_vision([0.5, 0.5, 0.5, 0.5])
    check("normalized_rect_to_vision: zero-area box rejected", degenerate is None)

    # --- unit-level: BP-28 class rejection ---
    known = ifb.load_category_names(ifb.CATEGORY_MAP)
    dropped = __import__("collections").Counter()
    kept_elem = ifb.build_element(
        {
            "id": "e1",
            "taxonomyRole": "primaryButton",
            "normalizedRect": [0.1, 0.1, 0.3, 0.2],
            "nativePixelRect": [192, 108, 384, 108],
            "isFocused": True,
        },
        known,
        dropped,
    )
    check("build_element: known class ('primaryButton') is kept", kept_elem is not None and kept_elem["elementType"] == "primaryButton")
    check("build_element: kept element is marked focused", kept_elem is not None and kept_elem["state"]["isFocused"] is True)

    unknown_elem = ifb.build_element(
        {
            "id": "e2",
            "taxonomyRole": "tabBarItem",  # not in the frozen 41-class taxonomy (BP-28 example)
            "normalizedRect": [0.4, 0.4, 0.6, 0.5],
        },
        known,
        dropped,
    )
    check("build_element: unknown class ('tabBarItem') is dropped, not remapped (BP-28)", unknown_elem is None)
    check("build_element: dropped class is counted", dropped["tabBarItem"] == 1)

    # --- integration: full CLI run against synthetic fixtures ---
    reset_workdir()
    write_recipe(
        "gridMatrix_001",
        [
            {
                "id": "card_0",
                "taxonomyRole": "collectionItem",
                "normalizedRect": [0.05, 0.10, 0.30, 0.40],
                "nativePixelRect": [96, 108, 480, 324],
                "accessibilityTraits": ["button"],
                "isFocused": True,
            },
            {
                "id": "card_0_label",
                "taxonomyRole": "tabBarItem",  # deliberately invalid, must be dropped
                "normalizedRect": [0.05, 0.42, 0.30, 0.46],
            },
        ],
    )
    write_recipe(
        "settingsList_002",
        [
            {
                "id": "row_0",
                "taxonomyRole": "listRow",
                "normalizedRect": [0.10, 0.10, 0.90, 0.16],
                "nativePixelRect": [192, 108, 1536, 65],
                "isFocused": False,
            }
        ],
    )

    dry_run = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "ingest_fixture_batch.py"),
         "--input", str(INPUT_DIR), "--output", str(OUTPUT_DIR), "--dry-run"],
        capture_output=True, text=True,
    )
    check("CLI --dry-run exits 0", dry_run.returncode == 0)
    check("CLI --dry-run writes nothing", not OUTPUT_DIR.exists())
    check("CLI --dry-run reports the dropped class", "tabBarItem" in dry_run.stdout)

    real_run = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "ingest_fixture_batch.py"),
         "--input", str(INPUT_DIR), "--output", str(OUTPUT_DIR), "--holdout-fraction", "0.5"],
        capture_output=True, text=True,
    )
    check("CLI real run exits 0", real_run.returncode == 0)

    train_jsons = list((OUTPUT_DIR / "train").glob("*.json")) if (OUTPUT_DIR / "train").exists() else []
    holdout_jsons = list((OUTPUT_DIR / "fixture_holdout").glob("*.json")) if (OUTPUT_DIR / "fixture_holdout").exists() else []
    check("CLI real run: both splits populated (2 recipes, 50% holdout)", len(train_jsons) == 2 and len(holdout_jsons) == 2)

    if train_jsons or holdout_jsons:
        sample = json.loads((train_jsons + holdout_jsons)[0].read_text())
        required_top_level = {"schemaVersion", "imageSHA256", "image", "generatorProfile", "elements"}
        check(
            "Written sidecar has all annotation.schema.json v1.0 required top-level keys",
            required_top_level.issubset(sample.keys()),
        )
        check("Written sidecar: schemaVersion is '1.0'", sample.get("schemaVersion") == "1.0")
        elem_types = {e["elementType"] for e in sample["elements"]}
        check("Written sidecar: no dropped class leaked through", "tabBarItem" not in elem_types)

    # A recipe's two frames (unfocused/focused) must land on the same side of the split.
    same_recipe_split_pngs = list(OUTPUT_DIR.rglob("gridMatrix_001_*.png"))
    parents = {p.parent.name for p in same_recipe_split_pngs}
    check("Both frames of one recipe stay on the same split side", len(parents) == 1)

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
