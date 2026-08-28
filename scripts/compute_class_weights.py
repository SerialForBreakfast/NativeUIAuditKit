#!/usr/bin/env python3
"""
compute_class_weights.py — Inverse-frequency focal-loss α for the 41-class taxonomy.

alpha_i = 1 / (count_i / total) = total / count_i
Then normalize so sum(alpha) = 1.0.

Empty classes (count 0) are treated as count=1 so they get a high but finite
weight and the JSON still has exactly 41 entries. They never appear in the
loss (no boxes), so the inflated α is inert until the generator covers them.

Usage:
  .venv-yolo/bin/python scripts/compute_class_weights.py
  .venv-yolo/bin/python scripts/compute_class_weights.py \\
      --labels NativeUITrainer/yolo_dataset_41class/train/labels
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATEGORY_MAP = PROJECT_ROOT / "Research" / "schemas" / "category_map.json"
DEFAULT_LABELS = PROJECT_ROOT / "NativeUITrainer" / "yolo_dataset_41class" / "train" / "labels"
DEFAULT_OUT = PROJECT_ROOT / "scripts" / "class_weights.json"


def load_names(path: Path) -> list[str]:
    data = json.loads(path.read_text())
    cats = sorted(data["categories"], key=lambda c: c["id"])
    return [c["name"] for c in cats]


def count_boxes(labels_dir: Path, n_classes: int) -> list[int]:
    counts = [0] * n_classes
    files = list(labels_dir.glob("*.txt"))
    if not files:
        print(f"ERROR: no label files in {labels_dir}")
        sys.exit(1)
    for f in files:
        for line in f.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            cid = int(line.split()[0])
            if 0 <= cid < n_classes:
                counts[cid] += 1
    return counts


def alphas_from_counts(counts: list[int]) -> list[float]:
    """Inverse frequency, empty classes counted as 1, then L1-normalized."""
    safe = [c if c > 0 else 1 for c in counts]
    total = float(sum(safe))
    raw = [total / c for c in safe]
    s = sum(raw)
    return [a / s for a in raw]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--labels", default=str(DEFAULT_LABELS), help="YOLO train labels dir")
    p.add_argument("--output", default=str(DEFAULT_OUT))
    return p.parse_args()


def main():
    args = parse_args()
    names = load_names(CATEGORY_MAP)
    labels_dir = Path(args.labels).expanduser().resolve()
    counts = count_boxes(labels_dir, len(names))
    alphas = alphas_from_counts(counts)
    if abs(sum(alphas) - 1.0) > 1e-9:
        print("ERROR: alphas do not sum to 1")
        sys.exit(1)

    payload = {
        "formula": "alpha_i = (total/max(count_i,1)); then normalize to sum=1",
        "total_boxes_observed": int(sum(counts)),
        "weights": [
            {
                "id": i,
                "name": names[i],
                "count": counts[i],
                "alpha": alphas[i],
            }
            for i in range(len(names))
        ],
    }
    out = Path(args.output).expanduser().resolve()
    out.write_text(json.dumps(payload, indent=2) + "\n")

    ranked = sorted(payload["weights"], key=lambda w: w["alpha"], reverse=True)
    print(f"Wrote {out}")
    print(f"  classes : {len(names)}")
    print(f"  boxes   : {sum(counts)}")
    print(f"  sum(α)  : {sum(alphas):.6f}")
    print("  highest α (rarest / empty):")
    for w in ranked[:8]:
        print(f"    {w['name']:20s}  count={w['count']:6d}  α={w['alpha']:.6f}")
    print("  lowest α (most frequent):")
    for w in ranked[-5:]:
        print(f"    {w['name']:20s}  count={w['count']:6d}  α={w['alpha']:.6f}")


if __name__ == "__main__":
    main()
