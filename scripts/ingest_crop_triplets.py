#!/usr/bin/env python3
"""Ingest and validate bulk crop triplets for FocusRing contrastive learning (ASD-STE100)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import struct
import sys
import time

def compute_sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def check_png_dimensions(path):
    with Path(path).open("rb") as f:
        header = f.read(24)
        if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
            return None, None
        w, h = struct.unpack(">II", header[16:24])
        return w, h

def ingest_triplets(dataset_dir, output_manifest_path=None, seed=42):
    root = Path(dataset_dir)
    manifest_file = root / "bulk_crop_triplets_manifest.json"
    if not manifest_file.exists():
        raise FileNotFoundError(f"Manifest missing at {manifest_file}")

    raw_manifest = json.loads(manifest_file.read_text())
    cases = raw_manifest.get("cases", [])
    if not cases:
        raise ValueError("No cases found in manifest")

    crops_dir = root / "crops"
    validated_cases = []
    failed_cases = []

    random.seed(seed)
    
    # Shuffle deterministically before split
    shuffled_cases = list(cases)
    random.shuffle(shuffled_cases)

    # 70% train, 15% val, 15% test
    n_total = len(shuffled_cases)
    n_train = int(n_total * 0.70)
    n_val = int(n_total * 0.15)

    for idx, c in enumerate(shuffled_cases):
        case_id = c["case_id"]
        case_folder = crops_dir / case_id

        anchor_png = case_folder / "crop_anchor.png"
        pos_png = case_folder / "crop_positive.png"
        neg_png = case_folder / "crop_negative.png"
        item_manifest = case_folder / "crop_manifest.json"

        # Check file existence
        missing = [f.name for f in [anchor_png, pos_png, neg_png, item_manifest] if not f.exists()]
        if missing:
            failed_cases.append({"case_id": case_id, "error": f"missing files: {missing}"})
            continue

        # Check PNG dimensions
        dimension_error = False
        for img in [anchor_png, pos_png, neg_png]:
            w, h = check_png_dimensions(img)
            if (w, h) != (256, 256):
                failed_cases.append({"case_id": case_id, "error": f"{img.name} has invalid size {w}x{h}"})
                dimension_error = True
                break
        if dimension_error:
            continue

        # Assign split
        if idx < n_train:
            split = "train"
        elif idx < n_train + n_val:
            split = "val"
        else:
            split = "test"

        validated_cases.append({
            "case_id": case_id,
            "split": split,
            "layout": c.get("layout"),
            "focus_bias": c.get("focus_bias"),
            "interruption": c.get("interruption"),
            "focused_node_id": c.get("focused_node_id"),
            "anchor_path": str(anchor_png.relative_to(root)),
            "positive_path": str(pos_png.relative_to(root)),
            "negative_path": str(neg_png.relative_to(root)),
            "anchor_sha256": c.get("crop_anchor_sha256"),
            "positive_sha256": c.get("crop_positive_sha256"),
            "negative_sha256": c.get("crop_negative_sha256")
        })

    summary = {
        "dataset_name": "NUIAK-Bulk-Anchored-Crop-Triplets-200-v1",
        "total_cases_found": n_total,
        "validated_cases": len(validated_cases),
        "failed_cases": len(failed_cases),
        "splits": {
            "train": sum(1 for c in validated_cases if c["split"] == "train"),
            "val": sum(1 for c in validated_cases if c["split"] == "val"),
            "test": sum(1 for c in validated_cases if c["split"] == "test")
        },
        "archetypes": {},
        "biases": {},
        "cases": validated_cases,
        "failures": failed_cases,
        "indexed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    for c in validated_cases:
        arch = c["layout"]
        bias = c["focus_bias"]
        summary["archetypes"][arch] = summary["archetypes"].get(arch, 0) + 1
        summary["biases"][bias] = summary["biases"].get(bias, 0) + 1

    if output_manifest_path:
        out = Path(output_manifest_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    return summary

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Ingest and validate crop triplets dataset.")
    p.add_argument("dataset_dir", help="Path to uncompressed dataset directory")
    p.add_argument("--output", "-o", default=None, help="Output JSON manifest path")
    args = p.parse_args()
    res = ingest_triplets(args.dataset_dir, args.output)
    print(json.dumps({k: v for k, v in res.items() if k != "cases"}, indent=2))
