#!/usr/bin/env python3
"""Ingest and validate crop triplets for FocusRing training (ASD-STE100).

Contract (TTR `render-headless-screen.swift`): `crop_anchor.png` is the focused crop,
`crop_positive.png` is the same element unfocused, and `crop_negative.png` is another element.
Each case must state this polarity in its `crop_manifest.json`. Every file must match its manifest hash.
Splits are assigned by group, so identical pixels never cross train, validation, and test.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import time
import re
from PIL import Image

FILES = {"anchor": "crop_anchor.png", "positive": "crop_positive.png", "negative": "crop_negative.png"}
POLARITY = {"anchor": True, "positive": False, "negative": False}
SPLITS = (("train", 0.70), ("val", 0.15), ("test", 0.15))


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
        return struct.unpack(">II", header[16:24])


def check_case(case, case_folder):
    """Return (validated fields, None) or (None, error)."""
    item_path = case_folder / "crop_manifest.json"
    paths = {role: case_folder / name for role, name in FILES.items()}
    missing = [p.name for p in [*paths.values(), item_path] if not p.exists()]
    if missing:
        return None, f"missing files: {missing}"
    item = json.loads(item_path.read_text())
    hashes = {}
    for role, path in paths.items():
        if check_png_dimensions(path) != (256, 256):
            return None, f"{path.name} has invalid size"
        flag = item.get(role, {}).get("is_focused") if isinstance(item.get(role), dict) else None
        if flag is not POLARITY[role]:
            return None, f"polarity_unknown_or_wrong: {role}.is_focused={flag!r}"
        expected = case.get(f"crop_{role}_sha256")
        actual = compute_sha256(path)
        if expected != actual:
            return None, f"hash_mismatch: {path.name}"
        hashes[role] = actual
    return hashes, None


def assign_splits(groups, seed):
    """Assign whole groups to splits in a seeded hash order."""
    order = sorted(groups, key=lambda g: hashlib.sha256(f"{seed}:{g}".encode()).hexdigest())
    result, start = {}, 0
    for index, (split, fraction) in enumerate(SPLITS):
        end = len(order) if index == len(SPLITS) - 1 else start + round(len(order) * fraction)
        for group in order[start:end]:
            result[group] = split
        start = end
    return result


def pixel_groups(checked):
    """Keep connected ancestry and identical decoded crops in one group."""
    parents, pixels, labels, identities = {}, {}, {}, {}
    def root(group):
        parents.setdefault(group, group)
        while parents[group] != group:
            group = parents[group]
        return group
    def join(left, right):
        left, right = root(left), root(right)
        if left != right:
            parents[max(left, right)] = min(left, right)
    for case, folder, hashes, group in checked:
        root(group)
        identities[case['case_id']] = {}
        for role, name in FILES.items():
            with Image.open(folder / name) as image:
                image.load()
                value = hashlib.sha256(image.convert('RGBA').tobytes()).hexdigest()
            identities[case['case_id']][role] = value
            if value in labels and labels[value] != POLARITY[role]:
                raise ValueError('duplicate_pixel_label_conflict')
            labels[value] = POLARITY[role]
            if value in pixels:
                join(group, pixels[value])
            else:
                pixels[value] = group
    return {group: root(group) for *_, group in checked}, identities


def ingest_triplets(dataset_dir, output_manifest_path=None, seed=42):
    root = Path(dataset_dir)
    manifest_file = root / "bulk_crop_triplets_manifest.json"
    if not manifest_file.exists():
        raise FileNotFoundError(f"Manifest missing at {manifest_file}")
    raw_manifest = json.loads(manifest_file.read_text())
    cases = raw_manifest.get("cases", [])
    if not cases:
        raise ValueError("No cases found in manifest")
    if len({case.get('case_id') for case in cases}) != len(cases):
        raise ValueError('duplicate_case_id')

    checked, failed_cases = [], []
    for case in cases:
        if not isinstance(case.get('case_id'), str) or not re.fullmatch(r'[A-Za-z0-9_-]+', case['case_id']):
            raise ValueError('invalid_case_id')
        case_folder = root / "crops" / case["case_id"]
        hashes, error = check_case(case, case_folder)
        if error:
            failed_cases.append({"case_id": case["case_id"], "error": error})
            continue
        # Identical anchor pixels share a group. A declared group also keeps related cases together.
        group = case.get("group") or case.get("lineage_group") or hashes["anchor"]
        checked.append((case, case_folder, hashes, group))

    connected, pixel_hashes = pixel_groups(checked)
    splits = assign_splits(set(connected.values()), seed)
    validated_cases = []
    for case, case_folder, hashes, group in checked:
        group = connected[group]
        validated_cases.append({
            "case_id": case["case_id"],
            "split": splits[group],
            "group": group,
            "layout": case.get("layout"),
            "theme": case.get("theme", "dark_standard"),
            "focus_bias": case.get("focus_bias"),
            "interruption": case.get("interruption"),
            "focused_node_id": case.get("focused_node_id"),
            **{f"{role}_path": str((case_folder / name).relative_to(root)) for role, name in FILES.items()},
            **{f"{role}_sha256": digest for role, digest in hashes.items()},
            'pixel_sha256': pixel_hashes[case['case_id']],
        })

    count = lambda key: {v: sum(1 for c in validated_cases if c[key] == v) for v in sorted({c[key] for c in validated_cases}, key=str)}
    summary = {
        "dataset_name": raw_manifest.get("dataset_name", "NUIAK-Crop-Triplets"),
        "total_cases_found": len(cases),
        "validated_cases": len(validated_cases),
        "failed_cases": len(failed_cases),
        "unique_anchor_images": len({c['pixel_sha256']['anchor'] for c in validated_cases}),
        "groups": len(splits),
        "splits": {name: sum(1 for c in validated_cases if c["split"] == name) for name, _ in SPLITS},
        "archetypes": count("layout"),
        "themes": count("theme"),
        "biases": count("focus_bias"),
        "cases": validated_cases,
        "failures": failed_cases,
        "indexed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    if output_manifest_path:
        out = Path(output_manifest_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    # focus_dataset_manifest.json for eval_focus_ring_detector.py: the anchor is the focused crop.
    focus_manifest = {
        "dataset": summary["dataset_name"],
        "created_at": summary["indexed_at"],
        "pairs": [
            {
                "pair_id": c["case_id"],
                "focused_crop": c["anchor_path"],
                "unfocused_crop": c["positive_path"],
                "negative_crop": c["negative_path"],
                "split": c["split"],
                "group": c["group"],
                "theme": c["theme"],
                "element_type": c["layout"],
            }
            for c in validated_cases
        ],
    }
    (root / "focus_dataset_manifest.json").write_text(json.dumps(focus_manifest, indent=2, sort_keys=True) + "\n")
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Ingest and validate a crop triplet dataset.")
    p.add_argument("dataset_dir", help="Path to the uncompressed dataset directory")
    p.add_argument("--output", "-o", default=None, help="Output JSON manifest path")
    args = p.parse_args()
    res = ingest_triplets(args.dataset_dir, args.output)
    print(json.dumps({k: v for k, v in res.items() if k != "cases"}, indent=2))
