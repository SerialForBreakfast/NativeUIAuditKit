"""
centroid_distribution.py — Analyze spatial centroid distributions for bias detection.

Usage:
    python scripts/centroid_distribution.py \
        --manifest NativeUIAuditKit-Dataset/manifest.json \
        --gt-dir NativeUIAuditKit-Dataset/train/annotations \
        --pred-dir runs/detect/predict/labels \
        --category-map Research/schemas/category_map.json \
        --output reports/centroid_bias_v1.json

Output JSON schema per class entry:
    {
        "class_name": str,
        "training_entropy": float,
        "prediction_entropy": float,
        "bias_flag": bool,
        "bias_region": {"cx": float, "cy": float, "size": 0.3} | null,
        "n_train": int,
        "n_pred": int
    }
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GRID_SIZE = 10          # 10x10 grid for entropy
BIAS_THRESHOLD = 0.80   # fraction of predictions to trigger bias flag
BIAS_WINDOW = 0.30      # window size (fraction of image side)
MIN_PREDICTIONS = 50    # minimum predictions to include a class


# ---------------------------------------------------------------------------
# Coordinate conversion
# ---------------------------------------------------------------------------

def vision_to_yolo_centroid(x: float, y: float, w: float, h: float) -> tuple[float, float]:
    """Return (cx, cy) in YOLO/top-left-origin coordinates."""
    cx = x + w / 2.0
    cy = 1.0 - y - h + h / 2.0
    return cx, cy


# ---------------------------------------------------------------------------
# Entropy
# ---------------------------------------------------------------------------

def spatial_entropy(centroids: list[tuple[float, float]], grid_size: int = GRID_SIZE) -> float:
    """Compute 2D Shannon entropy over a grid_size x grid_size spatial grid.

    H = -sum(p * log2(p + eps))
    """
    if not centroids:
        return 0.0
    xs = np.clip([c[0] for c in centroids], 0.0, 1.0 - 1e-9)
    ys = np.clip([c[1] for c in centroids], 0.0, 1.0 - 1e-9)
    col_idx = (np.array(xs) * grid_size).astype(int)
    row_idx = (np.array(ys) * grid_size).astype(int)
    counts = np.zeros((grid_size, grid_size), dtype=float)
    for r, c in zip(row_idx, col_idx):
        counts[r, c] += 1
    total = counts.sum()
    if total == 0:
        return 0.0
    p = counts / total
    eps = 1e-12
    H = -np.sum(p * np.log2(p + eps))
    return float(H)


# ---------------------------------------------------------------------------
# Bias detection
# ---------------------------------------------------------------------------

def detect_bias(
    centroids: list[tuple[float, float]],
    bias_threshold: float = BIAS_THRESHOLD,
    window: float = BIAS_WINDOW,
) -> tuple[bool, Optional[dict]]:
    """Check if >bias_threshold of centroids fall within any window x window square.

    Scans with a stride of window/2 for overlapping windows.
    Returns (bias_flag, bias_region) where bias_region is {"cx": float, "cy": float, "size": 0.3}.
    """
    if not centroids:
        return False, None

    n = len(centroids)
    xs = np.array([c[0] for c in centroids])
    ys = np.array([c[1] for c in centroids])

    stride = window / 2.0
    best_count = 0
    best_wx: float = 0.0
    best_wy: float = 0.0

    wx = 0.0
    while wx + window <= 1.0 + 1e-9:
        wy = 0.0
        while wy + window <= 1.0 + 1e-9:
            in_window = np.sum((xs >= wx) & (xs < wx + window) & (ys >= wy) & (ys < wy + window))
            if in_window > best_count:
                best_count = in_window
                best_wx = wx
                best_wy = wy
            wy += stride
        wx += stride

    fraction = best_count / n
    if fraction > bias_threshold:
        bias_region = {
            "cx": round(best_wx + window / 2.0, 4),
            "cy": round(best_wy + window / 2.0, 4),
            "size": window,
        }
        return True, bias_region

    return False, None


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_category_map(path: Path) -> tuple[dict[str, int], list[str]]:
    data = json.loads(path.read_text())
    categories = data["categories"]
    name_to_id: dict[str, int] = {c["name"]: c["id"] for c in categories}
    num_classes = max(c["id"] for c in categories) + 1
    id_to_name: list[str] = [""] * num_classes
    for c in categories:
        id_to_name[c["id"]] = c["name"]
    return name_to_id, id_to_name


def load_manifest_stems(manifest_path: Path, split: str = "train") -> set[str]:
    """Return set of file stems for the given split from the manifest JSON.

    Manifest format expected: list of objects with at minimum:
        {"file": "path/to/image.png", "split": "train"}  or
        {"stem": "image_stem", "split": "train"}
    Falls back to loading all JSON files in gt_dir if manifest is absent.
    """
    data = json.loads(manifest_path.read_text())
    stems: set[str] = set()
    entries = data if isinstance(data, list) else data.get("images", [])
    for entry in entries:
        if entry.get("split") != split:
            continue
        # Support "file", "filename", "stem" keys
        for key in ("file", "filename", "image", "stem"):
            val = entry.get(key)
            if val:
                stems.add(Path(val).stem)
                break
    return stems


def load_gt_centroids_for_stems(
    gt_dir: Path,
    stems: set[str],
    name_to_id: dict[str, int],
    num_classes: int,
) -> list[list[tuple[float, float]]]:
    """Return per-class list of (cx, cy) centroids from GT annotation files."""
    centroids: list[list[tuple[float, float]]] = [[] for _ in range(num_classes)]
    for stem in stems:
        ann_file = gt_dir / f"{stem}.json"
        if not ann_file.exists():
            continue
        data = json.loads(ann_file.read_text())
        for elem in data.get("elements", []):
            etype = elem.get("elementType", "")
            if etype not in name_to_id:
                continue
            cid = name_to_id[etype]
            b = elem.get("boundsVisionNormalized", {})
            x = float(b.get("x", 0.0))
            y = float(b.get("y", 0.0))
            w = float(b.get("width", 0.0))
            h = float(b.get("height", 0.0))
            cx, cy = vision_to_yolo_centroid(x, y, w, h)
            centroids[cid].append((cx, cy))
    return centroids


def load_pred_centroids(
    pred_dir: Path, stems: set[str], num_classes: int
) -> list[list[tuple[float, float]]]:
    """Return per-class list of (cx, cy) centroids from YOLO prediction files."""
    centroids: list[list[tuple[float, float]]] = [[] for _ in range(num_classes)]
    for stem in stems:
        pred_file = pred_dir / f"{stem}.txt"
        if not pred_file.exists():
            continue
        for line in pred_file.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 5:
                continue
            cid = int(parts[0])
            cx, cy = float(parts[1]), float(parts[2])
            if 0 <= cid < num_classes:
                centroids[cid].append((cx, cy))
    return centroids


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze centroid spatial distributions and flag position bias."
    )
    parser.add_argument(
        "--manifest",
        required=True,
        type=Path,
        help="Path to dataset manifest JSON.",
    )
    parser.add_argument(
        "--gt-dir",
        required=True,
        type=Path,
        help="Directory containing ground-truth annotation JSON files.",
    )
    parser.add_argument(
        "--pred-dir",
        required=True,
        type=Path,
        help="Directory containing YOLO prediction .txt files.",
    )
    parser.add_argument(
        "--category-map",
        required=True,
        type=Path,
        help="Path to category_map.json.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output path for centroid bias JSON report.",
    )
    parser.add_argument(
        "--split",
        default="train",
        help="Manifest split to load GT centroids from (default: train).",
    )
    parser.add_argument(
        "--min-predictions",
        type=int,
        default=MIN_PREDICTIONS,
        help=f"Minimum predictions required to include a class (default: {MIN_PREDICTIONS}).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    # Validate gt-dir
    if not args.gt_dir.exists() or not args.gt_dir.is_dir():
        print(f"ERROR: --gt-dir does not exist or is not a directory: {args.gt_dir}", file=sys.stderr)
        sys.exit(1)

    # Load category map
    name_to_id, id_to_name = load_category_map(args.category_map)
    num_classes = len(id_to_name)
    print(f"Loaded {num_classes} classes from {args.category_map}")

    # Load manifest stems
    if args.manifest.exists():
        train_stems = load_manifest_stems(args.manifest, split=args.split)
        print(f"Loaded {len(train_stems)} image stems from manifest (split={args.split})")
    else:
        # Fallback: use all JSON files in gt_dir
        print(
            f"Warning: manifest not found at {args.manifest}; using all files in {args.gt_dir}",
            file=sys.stderr,
        )
        train_stems = {f.stem for f in args.gt_dir.glob("*.json")}

    # Collect all stems that have prediction files (for pred centroids)
    pred_stems = {f.stem for f in args.pred_dir.glob("*.txt")} if args.pred_dir.exists() else set()
    print(f"Found {len(pred_stems)} prediction files in {args.pred_dir}")

    # Load centroids
    gt_centroids = load_gt_centroids_for_stems(gt_dir=args.gt_dir, stems=train_stems, name_to_id=name_to_id, num_classes=num_classes)
    pred_centroids = load_pred_centroids(pred_dir=args.pred_dir, stems=pred_stems, num_classes=num_classes)

    # Compute per-class results
    results: list[dict] = []
    skipped = 0

    for cid in range(num_classes):
        class_name = id_to_name[cid]
        n_pred = len(pred_centroids[cid])
        n_train = len(gt_centroids[cid])

        if n_pred < args.min_predictions:
            print(
                f"Warning: class '{class_name}' has {n_pred} predictions (< {args.min_predictions}), skipping.",
                file=sys.stderr,
            )
            skipped += 1
            continue

        train_entropy = spatial_entropy(gt_centroids[cid])
        pred_entropy = spatial_entropy(pred_centroids[cid])
        bias_flag, bias_region = detect_bias(pred_centroids[cid])

        results.append(
            {
                "class_name": class_name,
                "training_entropy": round(train_entropy, 4),
                "prediction_entropy": round(pred_entropy, 4),
                "bias_flag": bias_flag,
                "bias_region": bias_region,
                "n_train": n_train,
                "n_pred": n_pred,
            }
        )

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2))
    print(f"\nWrote {len(results)} class entries to {args.output}")
    print(f"Skipped {skipped} classes with fewer than {args.min_predictions} predictions.")

    # Summary
    biased = [r for r in results if r["bias_flag"]]
    if biased:
        print(f"\nBias detected in {len(biased)} class(es):")
        for r in biased:
            br = r["bias_region"]
            print(f"  {r['class_name']:30s}  bias_region=(cx={br['cx']:.3f}, cy={br['cy']:.3f})")
    else:
        print("\nNo spatial bias detected in any class.")


if __name__ == "__main__":
    main()
