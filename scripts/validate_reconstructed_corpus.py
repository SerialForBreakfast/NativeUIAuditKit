#!/usr/bin/env python3
"""Fail-closed structural validator for a P0-C reconstructed corpus.

The script validates manifest membership, paired PNG/JSON files, PNG headers,
SHA-256s, content duplication, and family-level split isolation. It reports
coverage facts without inventing missing annotations or style metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SPLITS = {"train", "validation", "test"}
EXPECTED_ENTRY_COUNT = 16_940
RETIRED_TEMPLATE_FAMILIES = {"HardNegative_2"}
RETIRED_ELEMENT_TYPES = {"webContent"}


def parse_png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise ValueError("not a PNG with an IHDR header")
    width, height = struct.unpack(">II", header[16:24])
    if width <= 0 or height <= 0:
        raise ValueError("non-positive PNG dimensions")
    return width, height


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    corpus = args.corpus.resolve()
    report = args.report.resolve()
    manifest_path = corpus / "manifest.json"
    errors: list[str] = []

    if not manifest_path.is_file():
        errors.append(f"missing manifest: {manifest_path}")
        manifest: dict[str, object] = {}
    else:
        try:
            manifest = json.loads(manifest_path.read_text())
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid manifest: {error}")
            manifest = {}

    entries = manifest.get("entries", [])
    if not isinstance(entries, list) or not entries:
        errors.append("manifest entries must be a non-empty array")
        entries = []

    split_counts: Counter[str] = Counter()
    family_splits: dict[str, set[str]] = defaultdict(set)
    hash_paths: dict[str, list[str]] = defaultdict(list)
    dimensions: Counter[str] = Counter()
    missing_classes: list[str] = []
    retired_element_counts: Counter[str] = Counter()

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"entry {index} is not an object")
            continue
        relative = entry.get("fileName")
        split = entry.get("split")
        family = entry.get("templateFamily")
        expected_hash = entry.get("sha256")
        if not isinstance(relative, str) or not isinstance(split, str):
            errors.append(f"entry {index} lacks string fileName/split")
            continue
        if split not in SPLITS or not relative.startswith(f"{split}/"):
            errors.append(f"entry {index} split/path mismatch: {split!r} {relative!r}")
            continue
        png = corpus / relative
        annotation = png.with_suffix(".json")
        if not png.is_file() or not annotation.is_file():
            errors.append(f"entry {index} lacks paired PNG/JSON: {relative}")
            continue
        try:
            width, height = parse_png_dimensions(png)
            dimensions[f"{width}x{height}"] += 1
        except (OSError, ValueError) as error:
            errors.append(f"entry {index} invalid PNG {relative}: {error}")
        parsed_annotation: object = None
        try:
            parsed_annotation = json.loads(annotation.read_text())
            if not isinstance(parsed_annotation, dict):
                raise ValueError("root is not an object")
        except (OSError, json.JSONDecodeError, ValueError) as error:
            errors.append(f"entry {index} invalid annotation {annotation.name}: {error}")
        actual_hash = sha256(png)
        if actual_hash != expected_hash:
            errors.append(f"entry {index} SHA-256 mismatch: {relative}")
        hash_paths[actual_hash].append(relative)
        split_counts[split] += 1
        if isinstance(family, str):
            family_splits[family].add(split)
            if family in RETIRED_TEMPLATE_FAMILIES:
                errors.append(f"entry {index} uses retired template family: {family}")
        else:
            errors.append(f"entry {index} lacks templateFamily")

        if isinstance(parsed_annotation, dict):
            elements = parsed_annotation.get("elements")
            if not isinstance(elements, list):
                errors.append(f"entry {index} annotation elements is not an array")
            else:
                for element in elements:
                    if not isinstance(element, dict):
                        errors.append(f"entry {index} annotation has non-object element")
                        continue
                    element_type = element.get("elementType")
                    if element_type in RETIRED_ELEMENT_TYPES:
                        retired_element_counts[element_type] += 1
                        errors.append(
                            f"entry {index} emits retired element type: {element_type}"
                        )

    duplicate_hashes = {digest: paths for digest, paths in hash_paths.items() if len(paths) > 1}
    if duplicate_hashes:
        errors.append(f"duplicate PNG content hashes: {len(duplicate_hashes)}")
    leaking_families = {family: sorted(splits) for family, splits in family_splits.items() if len(splits) != 1}
    if leaking_families:
        errors.append(f"families crossing splits: {len(leaking_families)}")
    if len(entries) != EXPECTED_ENTRY_COUNT:
        errors.append(
            f"unexpected manifest entry count: {len(entries)} != {EXPECTED_ENTRY_COUNT}"
        )

    distribution = manifest.get("classDistribution", {})
    if isinstance(distribution, dict):
        missing_classes = sorted(key for key, value in distribution.items() if value == 0)
    else:
        errors.append("classDistribution is not an object")

    result = {
        "validator": "p0-c-reconstructed-corpus-v1",
        "corpus": str(corpus),
        "manifestEntries": len(entries),
        "expectedManifestEntries": EXPECTED_ENTRY_COUNT,
        "splitCounts": dict(sorted(split_counts.items())),
        "families": {family: sorted(splits) for family, splits in sorted(family_splits.items())},
        "pngDimensions": dict(sorted(dimensions.items())),
        "duplicateContentHashes": duplicate_hashes,
        "crossSplitFamilies": leaking_families,
        "zeroCountClasses": missing_classes,
        "retiredElementCounts": dict(sorted(retired_element_counts.items())),
        "errors": errors,
        "valid": not errors,
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"valid": result["valid"], "errors": len(errors), "entries": len(entries)}))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
