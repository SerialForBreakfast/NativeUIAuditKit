#!/usr/bin/env python3
"""Read-only, bounded intake for iOS visual probes; never grants training eligibility."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys
import uuid

from PIL import Image
from validate_reconstructed_corpus import check_schema, member, read_json, require, sha256

ROOT = Path(__file__).resolve().parents[1]


def bounded(path, limit):
    require(path.stat().st_size <= limit, "oversized_file:" + path.name)
    return path


def validate(batch, catalog_path, selected, target):
    batch = Path(batch).absolute()
    require(batch.resolve() == batch and batch.is_dir(), "unsafe_batch")
    require(str(uuid.UUID(target)).lower() == target.lower(), "invalid_target")
    require(0 < len(selected) <= 48 and len(set(selected)) == len(selected), "invalid_selection")
    catalog_path = Path(catalog_path).absolute()
    require(catalog_path.resolve() == catalog_path and catalog_path.is_file(), "unsafe_expected_catalog")
    catalog = read_json(bounded(catalog_path, 1024 * 1024))
    require(isinstance(catalog, dict), "invalid_catalog_root")
    require(catalog.get("version") == "visual-probe-catalog-v2" and
            catalog.get("partition") == "development" and catalog.get("planningOnly") is True,
            "unsupported_catalog")
    rows = {row["id"]: row for row in catalog["cases"]}
    require(len(rows) == len(catalog["cases"]) and set(selected) <= rows.keys(), "unknown_or_duplicate_case")
    receipt = read_json(bounded(member(batch, "capture.json"), 1024 * 1024))
    require(isinstance(receipt, dict), "invalid_receipt_root")
    require(set(receipt) == {"version", "completion", "trainingEligible", "partition",
            "catalogSHA256", "simulatorUUID", "runtimeOS", "expectedCount", "actualCount",
            "members", "unsupportedIntersections"}, "receipt_fields")
    require(receipt["version"] == "visual-probe-capture-v1" and
            receipt["completion"] == "captured_pending_visual_review" and
            receipt["trainingEligible"] is False and receipt["partition"] == "development", "ineligible_receipt")
    require(receipt["simulatorUUID"] == target, "target_mismatch")
    require(isinstance(receipt["runtimeOS"], str) and receipt["runtimeOS"] not in ("", "unknown"), "missing_runtime")
    require(receipt["catalogSHA256"] == sha256(catalog_path) ==
            sha256(bounded(member(batch, "catalog.json"), 1024 * 1024)), "catalog_hash_mismatch")
    require(receipt["unsupportedIntersections"] == catalog["unsupportedIntersections"], "unsupported_axes_changed")
    require(type(receipt["expectedCount"]) is int and type(receipt["actualCount"]) is int and
            receipt["expectedCount"] == receipt["actualCount"] == len(selected) == len(receipt["members"]), "count_mismatch")
    require([m["id"] for m in receipt["members"]] == selected, "membership_mismatch")
    schema = read_json(ROOT / "Research/schemas/annotation.schema.v1.2.json")
    expected_files = {"capture.json", "catalog.json"}
    pixels = defaultdict(list)
    coverage = Counter()
    total_pixels = 0
    for entry in receipt["members"]:
        require(set(entry) == {"id", "group", "image", "annotation", "imageSHA256", "annotationSHA256"}, "member_fields")
        row = rows[entry["id"]]; config = row["config"]
        require(entry["group"] == row["group"], "group_mismatch")
        for key, limit in (("image", 32 * 1024 * 1024), ("annotation", 4 * 1024 * 1024)):
            name = entry[key]
            require(isinstance(name, str) and Path(name).name == name and name not in expected_files, "duplicate_or_unsafe_path")
            expected_files.add(name)
            path = bounded(member(batch, name), limit)
            require(sha256(path) == entry[key + "SHA256"], "hash_mismatch:" + key)
        ann = read_json(batch / entry["annotation"])
        check_schema(ann, schema, schema)
        meta, profile = ann["image"], ann["generatorProfile"]
        require(ann["imageSHA256"] == entry["imageSHA256"] and meta["fileName"] == entry["image"], "sidecar_identity")
        require(meta["platform"] == "iOS" and meta["interfaceIdiom"] == "phone" and meta["orientation"] == "portrait", "platform_mismatch")
        for key in ("colorScheme", "dynamicTypeSize", "locale", "layoutDirection", "deviceName"):
            require(meta[key] == config[key], "config_mismatch:" + key)
        require(meta["scale"] == config["pixelScale"], "scale_mismatch")
        require(meta["safeAreaInsets"] == dict(top=config["osProfile"]["safeAreaTopInset"],
            bottom=config["osProfile"]["safeAreaBottomInset"], left=0, right=0), "safe_area_mismatch")
        for key in ("templateFamily", "seed", "isolationTemplate", "lowDensity"):
            require(profile[key] == config[key], "profile_mismatch:" + key)
        require(profile["generatorVersion"] == "visual-probe-1", "generator_version")
        require(profile["simulatorState"] == {k: config["simulatorOverride"][k] for k in profile["simulatorState"]}, "status_mismatch")
        for key in ("reduceTransparency", "increaseContrast", "boldText", "buttonShapes", "onOffLabels", "smartInvert"):
            require(meta[key] == config["accessibilityFlags"][key], "trait_mismatch:" + key)
        w, h, scale = meta["pixelWidth"], meta["pixelHeight"], meta["scale"]
        require([w, h] == [int(n * scale) for n in config["osProfile"]["screenSize"]], "profile_dimensions")
        require(0 < w * h <= 16_000_000, "image_pixel_limit")
        total_pixels += w * h
        require(total_pixels <= 384_000_000, "batch_pixel_limit")
        with Image.open(batch / entry["image"]) as image:
            require(image.format == "PNG" and image.size == (w, h), "png_dimensions_or_format")
            image.load()
            digest = hashlib.sha256(f"{w}x{h}:RGBA:".encode() + image.convert("RGBA").tobytes()).hexdigest()
        pixels[digest].append(entry["id"])
        require(ann["elements"] and len({e["id"] for e in ann["elements"]}) == len(ann["elements"]), "empty_or_duplicate_elements")
        for e in ann["elements"]:
            p, b, v = e["boundsPoints"], e["boundsPixels"], e["boundsVisionNormalized"]
            require(all(math.isfinite(n) for rect in (p, b, v) for n in rect.values()), "nonfinite_geometry")
            require(p["width"] >= 0 and p["height"] >= 0, "negative_geometry")
            require(all(abs(b[k] - p[k] * scale) <= 0.500001 for k in p), "pixel_geometry")
            left, right = max(0, min(w / scale, p["x"])), max(0, min(w / scale, p["x"] + p["width"]))
            top, bottom = max(0, min(h / scale, p["y"])), max(0, min(h / scale, p["y"] + p["height"]))
            normalized = dict(x=left * scale / w, y=1 - bottom * scale / h,
                              width=(right - left) * scale / w, height=(bottom - top) * scale / h)
            require(all(abs(v[k] - normalized[k]) < 1e-8 for k in normalized), "normalized_geometry")
            invisible = right == left or bottom == top
            clipped = (left, top, right, bottom) != (p["x"], p["y"], p["x"] + p["width"], p["y"] + p["height"])
            require(e["excluded"] == invisible and e["occluded"] == clipped, "visibility_mismatch")
            require(e.get("occlusionType") == ("imageBoundary" if clipped else None) and
                    e.get("exclusionReason") == ("outsideImage" if invisible else None), "visibility_reason_mismatch")
        coverage[(config["templateFamily"], config["colorScheme"], row["profile"], config["dynamicTypeSize"]) ] += 1
    require({p.name for p in batch.iterdir()} == expected_files, "unexpected_or_partial_output")
    return dict(version="visual-probe-intake-v1", integrity="passed", partition="development",
                trainingEligible=False, visualReview="pending", runtimeOSReported=receipt["runtimeOS"],
                catalogSHA256=receipt["catalogSHA256"], acceptedCount=len(selected),
                requestedCoverage=[dict(family=k[0], theme=k[1], profile=k[2], typeSize=k[3], count=n) for k, n in sorted(coverage.items())],
                duplicatePixelGroups=[ids for ids in pixels.values() if len(ids) > 1],
                unsupportedIntersections=receipt["unsupportedIntersections"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--case-id", action="append", required=True)
    parser.add_argument("--target", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.batch, args.catalog, args.case_id, args.target), sort_keys=True, indent=2))
    except (ValueError, OSError, KeyError, TypeError, Image.DecompressionBombError) as error:
        print(json.dumps(dict(integrity="failed", trainingEligible=False, error=str(error))), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
