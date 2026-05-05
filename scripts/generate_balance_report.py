"""
generate_balance_report.py — Dataset class-distribution health dashboard.

Reads manifest.json and produces:
  - reports/class_distribution.json   (per-class instance counts)
  - reports/class_distribution.png    (horizontal bar histogram via matplotlib)

Usage:
    python scripts/generate_balance_report.py \\
        --manifest NativeUIAuditKit-Dataset/manifest.json \\
        --reports-dir reports \\
        --floor 100 \\
        --version 1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_manifest(path: Path) -> dict:
    """Load and parse manifest.json. Exits 1 on missing or malformed file."""
    if not path.exists():
        print(f"ERROR: manifest not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(f"ERROR: manifest is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def compute_distribution(manifest: dict) -> dict[str, int]:
    """Return {class_name: instance_count} from the manifest's classDistribution field."""
    dist = manifest.get("classDistribution", {})
    if not isinstance(dist, dict):
        print("ERROR: manifest.classDistribution is missing or not an object.", file=sys.stderr)
        sys.exit(1)
    return {k: int(v) for k, v in dist.items()}


def flag_classes(distribution: dict[str, int], floor: int) -> list[str]:
    """Return sorted list of class names with count < floor."""
    return sorted(k for k, v in distribution.items() if v < floor)


def imbalance_ratio(distribution: dict[str, int]) -> float | None:
    """max_count / min_count across classes with > 0 instances. None if < 2 classes."""
    counts = [v for v in distribution.values() if v > 0]
    if len(counts) < 2:
        return None
    return max(counts) / min(counts)


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def write_json(distribution: dict[str, int], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "classDistribution": distribution,
        "totalInstances": sum(distribution.values()),
        "classCount": len(distribution),
    }
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"Saved class distribution JSON: {output_path}")


def write_histogram(
    distribution: dict[str, int],
    output_path: Path,
    floor: int,
    version: int,
) -> None:
    """Save a horizontal bar chart with under-floor classes highlighted in red."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    classes = sorted(distribution.keys())
    counts = [distribution[c] for c in classes]
    colors = ["#e74c3c" if c < floor else "#3498db" for c in counts]

    fig, ax = plt.subplots(figsize=(10, max(6, len(classes) * 0.28)))
    y_pos = np.arange(len(classes))
    ax.barh(y_pos, counts, color=colors, height=0.7)

    # Floor reference line
    ax.axvline(x=floor, color="#e74c3c", linestyle="--", linewidth=1,
               label=f"Floor = {floor}")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(classes, fontsize=8)
    ax.set_xlabel("Instance count")
    ax.set_title(f"Class Distribution v{version}", fontsize=13)
    ax.legend(fontsize=8)
    ax.invert_yaxis()

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved class distribution histogram: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate dataset balance report from manifest.json."
    )
    parser.add_argument(
        "--manifest",
        required=True,
        type=Path,
        help="Path to manifest.json.",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("reports"),
        help="Directory to write output files (default: reports/).",
    )
    parser.add_argument(
        "--floor",
        type=int,
        default=100,
        help="Minimum instance count per class before flagging (default: 100).",
    )
    parser.add_argument(
        "--version",
        type=int,
        default=1,
        help="Version number appended to output filenames (default: 1).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    manifest = load_manifest(args.manifest)
    distribution = compute_distribution(manifest)

    image_count = manifest.get("imageCount", len(manifest.get("entries", [])))
    print(f"Manifest: {image_count} images, {len(distribution)} classes")

    ratio = imbalance_ratio(distribution)
    if ratio is not None:
        flag = " ⚠️" if ratio > 5.0 else ""
        print(f"Imbalance ratio (max/min): {ratio:.1f}{flag}")

    flagged = flag_classes(distribution, args.floor)
    if flagged:
        print(f"Under-represented classes (< {args.floor} instances): {', '.join(flagged)}")
    else:
        print(f"All classes meet the floor of {args.floor} instances.")

    v = args.version
    write_json(distribution, args.reports_dir / f"class_distribution_v{v}.json")
    write_histogram(distribution, args.reports_dir / f"class_distribution_v{v}.png",
                    args.floor, v)


if __name__ == "__main__":
    main()
