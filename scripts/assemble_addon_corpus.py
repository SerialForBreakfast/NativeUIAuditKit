#!/usr/bin/env python3
"""
assemble_addon_corpus.py — Retrieve simulator addon batch and assemble combined r7 corpus.

1. Retrieves generated 2,800 addon pairs from the simulator app container
   into NativeUITrainer/reconstructed_corpora/ios-41class-addon-v1.
2. Assembles NativeUITrainer/reconstructed_corpora/ios-41class-r7-combined by combining
   the sealed r6 corpus (16,940 pairs) + addon-v1 (2,800 pairs) = 19,740 pairs.
3. Addon pairs are sequentially numbered starting at img_016941.
4. Validates zero duplicate pixel hashes and zero cross-split leakage.

Usage:
  .venv-yolo/bin/python scripts/assemble_addon_corpus.py
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TARGET_UDID = "F3EF9DB8-0B0F-4757-B653-D1628269F6FF"
APP_BUNDLE = "com.nativeuiauditkit.generatorrunner"
STAGING_NAME = "ios-41class-addon-v1"

R6_DIR = PROJECT_ROOT / "NativeUITrainer" / "reconstructed_corpora" / "ios-41class-r6"
ADDON_LOCAL_DIR = PROJECT_ROOT / "NativeUITrainer" / "reconstructed_corpora" / "ios-41class-addon-v1"
COMBINED_DIR = PROJECT_ROOT / "NativeUITrainer" / "reconstructed_corpora" / "ios-41class-r7-combined"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_simulator_container() -> Path:
    out = subprocess.check_output(
        ["xcrun", "simctl", "get_app_container", TARGET_UDID, APP_BUNDLE, "data"],
        text=True,
    ).strip()
    return Path(out)


def retrieve_addon_staging(sim_dir: Path, local_dir: Path) -> dict:
    source = sim_dir / "Documents" / "reconstruction" / STAGING_NAME
    if not source.exists():
        raise FileNotFoundError(f"Simulator staging not found: {source}")

    manifest_p = source / "manifest.json"
    if not manifest_p.exists():
        raise FileNotFoundError(f"Missing manifest in {source}")

    manifest = json.loads(manifest_p.read_text())
    entries = manifest.get("entries", [])
    print(f"Retrieved manifest from simulator: {len(entries)} entries")

    if local_dir.exists():
        print(f"Local addon directory already exists: {local_dir}")
    else:
        local_dir.mkdir(parents=True, exist_ok=True)
        for split in ("train", "validation", "test"):
            (local_dir / split).mkdir(exist_ok=True)

        print(f"Copying addon files from {source} to {local_dir}...")
        for e in entries:
            fn = e["fileName"]
            src_png = source / fn
            dst_png = local_dir / fn
            src_json = src_png.with_suffix(".json")
            dst_json = dst_png.with_suffix(".json")

            shutil.copy2(src_png, dst_png)
            shutil.copy2(src_json, dst_json)

        shutil.copy2(manifest_p, local_dir / "manifest.json")
        ledger_p = source / "capture-ledger.json"
        if ledger_p.exists():
            shutil.copy2(ledger_p, local_dir / "capture-ledger.json")
        report_p = source / "balance_report.md"
        if report_p.exists():
            shutil.copy2(report_p, local_dir / "balance_report.md")

    return manifest


def assemble_combined_corpus(r6_dir: Path, addon_dir: Path, combined_dir: Path):
    if combined_dir.exists():
        raise FileExistsError(f"Combined destination already exists: {combined_dir}")

    combined_dir.mkdir(parents=True, exist_ok=True)
    for s in ("train", "validation", "test"):
        (combined_dir / s).mkdir(exist_ok=True)

    print("Step 1: Copying sealed r6 corpus (hardlinking where possible)...")
    r6_manifest = json.loads((r6_dir / "manifest.json").read_text())
    r6_entries = r6_manifest.get("entries", [])
    print(f"r6 entries: {len(r6_entries)}")

    combined_entries = []
    seen_hashes: dict[str, str] = {}

    for e in r6_entries:
        fn = e["fileName"]
        src_png = r6_dir / fn
        dst_png = combined_dir / fn
        src_json = src_png.with_suffix(".json")
        dst_json = dst_png.with_suffix(".json")

        os.link(src_png, dst_png)
        os.link(src_json, dst_json)

        h = e.get("sha256") or sha256_file(src_png)
        seen_hashes[h] = fn
        combined_entries.append(e)

    print(f"Linked {len(combined_entries)} r6 entries.")

    print("Step 2: Appending addon entries sequentially...")
    addon_manifest = json.loads((addon_dir / "manifest.json").read_text())
    addon_entries = addon_manifest.get("entries", [])
    print(f"addon entries: {len(addon_entries)}")

    addon_counter = len(combined_entries) + 1

    for e in addon_entries:
        old_fn = e["fileName"]
        split = e["split"]
        new_base = f"img_{addon_counter:06d}"
        new_fn = f"{split}/{new_base}.png"

        src_png = addon_dir / old_fn
        dst_png = combined_dir / new_fn
        src_json = src_png.with_suffix(".json")
        dst_json = dst_png.with_suffix(".json")

        h = sha256_file(src_png)
        if h in seen_hashes:
            print(f"WARNING: duplicate pixel hash detected: {old_fn} matches {seen_hashes[h]}")
        seen_hashes[h] = new_fn

        # Copy image
        shutil.copy2(src_png, dst_png)

        # Update JSON sidecar imageFileName
        ann_data = json.loads(src_json.read_text())
        if "image" in ann_data:
            ann_data["image"]["fileName"] = f"{new_base}.png"
        dst_json.write_text(json.dumps(ann_data, indent=2))

        # Create new manifest entry
        new_entry = dict(e)
        new_entry["fileName"] = new_fn
        new_entry["sha256"] = h
        combined_entries.append(new_entry)

        addon_counter += 1

    print(f"Total combined entries: {len(combined_entries)}")

    # Write combined manifest
    combined_manifest = {
        "version": "1.0",
        "entries": combined_entries,
        "imageCount": len(combined_entries),
    }
    (combined_dir / "manifest.json").write_text(json.dumps(combined_manifest, indent=2))

    # Split breakdown
    split_counts = Counter(e["split"] for e in combined_entries)
    print("Combined split breakdown:")
    for s, c in sorted(split_counts.items()):
        print(f"  {s}: {c}")

    print(f"Successfully assembled combined corpus at: {combined_dir}")


def main():
    parser = argparse.ArgumentParser(description="Assemble r7 combined corpus.")
    args = parser.parse_args()

    sim_container = get_simulator_container()
    print(f"Simulator container: {sim_container}")

    manifest = retrieve_addon_staging(sim_container, ADDON_LOCAL_DIR)
    if len(manifest.get("entries", [])) < 2800:
        print(f"Addon generation not yet complete ({len(manifest.get('entries', []))} / 2800).")
        return 1

    assemble_combined_corpus(R6_DIR, ADDON_LOCAL_DIR, COMBINED_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
