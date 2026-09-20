#!/usr/bin/env python3
"""Validate a prospective FocusRing corpus without training or device access."""

import argparse
import json
import sys
from pathlib import Path

from focus_ring_readiness import ReadinessError, validate


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="focus_dataset_manifest.json to validate")
    parser.add_argument(
        "--require-alignment-matrix",
        action="store_true",
        help="require all ADR-0007 matrix rows; use for FR-B capture acceptance",
    )
    return parser.parse_args()


def normalize_pair(pair: object) -> dict:
    if not isinstance(pair, dict):
        raise ReadinessError("invalid_pair")
    result = {
        "focused": pair.get("focused_crop"),
        "unfocused": pair.get("unfocused_crop"),
        "labelSource": pair.get("labelSource", "fixtureGroundTruth"),
        "seed": str(pair.get("recipe_seed", "")),
        "scene": pair.get("fixture_scene"),
        "theme": pair.get("theme"),
        "class": pair.get("element_type"),
        "hardNegative": pair.get("hardNegative", False),
    }
    if "alignment" in pair:
        result["alignment"] = pair["alignment"]
    return result


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = (PROJECT_ROOT / manifest_path).resolve()
    if not manifest_path.is_file():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 2
    try:
        manifest = json.loads(manifest_path.read_text())
        if not isinstance(manifest, dict):
            raise ReadinessError("invalid_manifest")
        rows = [normalize_pair(pair) for pair in manifest.get("pairs", [])]
        report = validate(rows, require_alignment_matrix=args.require_alignment_matrix)
    except (json.JSONDecodeError, OSError, ReadinessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
