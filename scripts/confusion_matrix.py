"""
confusion_matrix.py — Evaluate YOLO detections against ground-truth annotations.

Usage:
    python scripts/confusion_matrix.py \
        --gt-dir NativeUIAuditKit-Dataset/test/annotations \
        --pred-dir runs/detect/predict/labels \
        --category-map Research/schemas/category_map.json \
        --version 1

Outputs:
    reports/confusion_matrix_v{N}.png
    reports/per_class_metrics_v{N}.csv
    Stdout: overall mAP@0.5, top-5 most-confused class pairs
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Coordinate conversion helpers
# ---------------------------------------------------------------------------

def vision_to_yolo(x: float, y: float, w: float, h: float) -> tuple[float, float, float, float]:
    """Convert Vision-normalized bbox (bottom-left origin) to YOLO (top-left origin, center).

    Vision:  x = left edge, y = bottom edge, w/h as fractions
    YOLO:    cx = center_x, cy = center_y (measured from top-left)
    """
    cx = x + w / 2.0
    cy = 1.0 - y - h + h / 2.0  # flip y-axis, then center
    return cx, cy, w, h


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_category_map(path: Path) -> tuple[dict[str, int], list[str]]:
    """Return (name_to_id, id_to_name_list) from category_map.json."""
    data = json.loads(path.read_text())
    categories = data["categories"]
    name_to_id: dict[str, int] = {c["name"]: c["id"] for c in categories}
    num_classes = max(c["id"] for c in categories) + 1
    id_to_name: list[str] = [""] * num_classes
    for c in categories:
        id_to_name[c["id"]] = c["name"]
    return name_to_id, id_to_name


def load_gt_annotations(
    gt_dir: Path, name_to_id: dict[str, int]
) -> dict[str, list[tuple[int, float, float, float, float]]]:
    """Load all ground-truth annotation JSONs.

    Returns a mapping of stem -> list of (class_id, cx, cy, w, h).
    Files with zero elements are included with an empty list.
    """
    result: dict[str, list[tuple[int, float, float, float, float]]] = {}
    json_files = sorted(gt_dir.glob("*.json"))
    if not json_files:
        return result
    for jf in json_files:
        data = json.loads(jf.read_text())
        boxes: list[tuple[int, float, float, float, float]] = []
        for elem in data.get("elements", []):
            etype = elem.get("elementType", "")
            if etype not in name_to_id:
                continue
            class_id = name_to_id[etype]
            b = elem.get("boundsVisionNormalized", {})
            x = float(b.get("x", 0.0))
            y = float(b.get("y", 0.0))
            w = float(b.get("width", 0.0))
            h = float(b.get("height", 0.0))
            cx, cy, bw, bh = vision_to_yolo(x, y, w, h)
            boxes.append((class_id, cx, cy, bw, bh))
        result[jf.stem] = boxes
    return result


def load_pred_txt(
    pred_dir: Path, stem: str
) -> list[tuple[int, float, float, float, float, float]]:
    """Load a single YOLO prediction .txt file.

    Each line: class_id cx cy w h conf (already top-left-origin center format).
    Returns list of (class_id, cx, cy, w, h, conf).
    Missing files return an empty list.
    """
    pred_file = pred_dir / f"{stem}.txt"
    if not pred_file.exists():
        return []
    detections: list[tuple[int, float, float, float, float, float]] = []
    for line in pred_file.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 6:
            continue
        class_id = int(parts[0])
        cx, cy, w, h, conf = (float(p) for p in parts[1:6])
        detections.append((class_id, cx, cy, w, h, conf))
    return detections


# ---------------------------------------------------------------------------
# IoU helpers
# ---------------------------------------------------------------------------

def xyxy_from_cxcywh(cx: float, cy: float, w: float, h: float) -> tuple[float, float, float, float]:
    return cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2


def iou(box_a: tuple[float, float, float, float], box_b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


# ---------------------------------------------------------------------------
# Confusion matrix and metrics (pure numpy, no supervision dependency for core)
# ---------------------------------------------------------------------------

def build_confusion_matrix(
    gt_by_stem: dict[str, list[tuple[int, float, float, float, float]]],
    pred_dir: Path,
    num_classes: int,
    iou_threshold: float = 0.5,
) -> np.ndarray:
    """Build an (N+1) x (N+1) confusion matrix.

    Rows = ground-truth class (last row = background/FP source).
    Cols = predicted class (last col = missed/FN destination).
    """
    # +1 for background
    cm = np.zeros((num_classes + 1, num_classes + 1), dtype=np.int64)

    for stem, gt_boxes in gt_by_stem.items():
        preds = load_pred_txt(pred_dir, stem)

        # Sort predictions by confidence descending
        preds_sorted = sorted(preds, key=lambda p: p[5], reverse=True)

        matched_gt: set[int] = set()
        matched_pred: set[int] = set()

        for pi, pred in enumerate(preds_sorted):
            p_cls, pcx, pcy, pw, ph, _ = pred
            p_box = xyxy_from_cxcywh(pcx, pcy, pw, ph)

            best_iou = iou_threshold
            best_gt_idx = -1

            for gi, gt in enumerate(gt_boxes):
                if gi in matched_gt:
                    continue
                g_cls, gcx, gcy, gw, gh = gt
                if g_cls != p_cls:
                    continue
                g_box = xyxy_from_cxcywh(gcx, gcy, gw, gh)
                score = iou(p_box, g_box)
                if score > best_iou:
                    best_iou = score
                    best_gt_idx = gi

            if best_gt_idx >= 0:
                # True positive
                cm[gt_boxes[best_gt_idx][0], p_cls] += 1
                matched_gt.add(best_gt_idx)
                matched_pred.add(pi)

        # False negatives: GT boxes that were never matched
        for gi, gt in enumerate(gt_boxes):
            if gi not in matched_gt:
                g_cls = gt[0]
                cm[g_cls, num_classes] += 1  # FN: GT row, background col

        # False positives: predictions that were never matched
        for pi, pred in enumerate(preds_sorted):
            if pi not in matched_pred:
                p_cls = pred[0]
                cm[num_classes, p_cls] += 1  # FP: background row, pred col

    return cm


def per_class_metrics(
    cm: np.ndarray, num_classes: int
) -> list[dict]:
    """Compute per-class precision, recall, f1, support from confusion matrix."""
    metrics = []
    for c in range(num_classes):
        tp = cm[c, c]
        fp = cm[num_classes, c]       # background row, class col = FP
        fn = cm[c, num_classes]       # class row, background col = FN
        support = tp + fn

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        metrics.append(
            {
                "class_id": c,
                "tp": int(tp),
                "fp": int(fp),
                "fn": int(fn),
                "support": int(support),
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }
        )
    return metrics


def compute_map50(metrics: list[dict]) -> float:
    """Simple macro-averaged AP@0.5 approximated from per-class precision/recall."""
    # For each class, AP ≈ precision * recall (single operating point)
    # Classes with zero support are excluded.
    aps = []
    for m in metrics:
        if m["support"] > 0:
            aps.append(m["precision"] * m["recall"])
    return float(np.mean(aps)) if aps else 0.0


def top_confused_pairs(
    cm: np.ndarray, num_classes: int, id_to_name: list[str], top_n: int = 5
) -> list[tuple[str, str, int]]:
    """Return top-N off-diagonal confusion pairs (gt_name, pred_name, count)."""
    pairs: list[tuple[str, str, int]] = []
    for r in range(num_classes):
        for c in range(num_classes):
            if r != c and cm[r, c] > 0:
                pairs.append((id_to_name[r], id_to_name[c], int(cm[r, c])))
    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs[:top_n]


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_confusion_matrix(
    cm: np.ndarray,
    id_to_name: list[str],
    output_path: Path,
    normalize: bool = True,
) -> None:
    """Save a confusion matrix heatmap (classes only, no background row/col)."""
    num_classes = len(id_to_name)
    cm_classes = cm[:num_classes, :num_classes].astype(float)

    if normalize:
        row_sums = cm_classes.sum(axis=1, keepdims=True)
        cm_plot = np.where(row_sums > 0, cm_classes / row_sums, 0.0)
        fmt_label = "Normalized count"
    else:
        cm_plot = cm_classes
        fmt_label = "Count"

    fig, ax = plt.subplots(figsize=(20, 18))
    im = ax.imshow(cm_plot, interpolation="nearest", cmap="Blues", vmin=0, vmax=1 if normalize else None)
    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label(fmt_label, fontsize=10)

    tick_marks = np.arange(num_classes)
    ax.set_xticks(tick_marks)
    ax.set_yticks(tick_marks)
    ax.set_xticklabels(id_to_name, rotation=90, fontsize=7)
    ax.set_yticklabels(id_to_name, fontsize=7)
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("Ground Truth", fontsize=12)
    ax.set_title("Confusion Matrix (IoU ≥ 0.5)", fontsize=14)

    # Annotate cells with value if nonzero and matrix is small enough
    if num_classes <= 20:
        for r in range(num_classes):
            for c in range(num_classes):
                val = cm_plot[r, c]
                if val > 0:
                    ax.text(
                        c, r, f"{val:.2f}" if normalize else str(int(val)),
                        ha="center", va="center",
                        fontsize=5,
                        color="white" if val > 0.5 else "black",
                    )

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved confusion matrix heatmap: {output_path}")


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------

def write_per_class_csv(
    metrics: list[dict], id_to_name: list[str], output_path: Path
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["class_name", "precision", "recall", "f1", "support"]
        )
        writer.writeheader()
        for m in metrics:
            writer.writerow(
                {
                    "class_name": id_to_name[m["class_id"]],
                    "precision": f"{m['precision']:.4f}",
                    "recall": f"{m['recall']:.4f}",
                    "f1": f"{m['f1']:.4f}",
                    "support": m["support"],
                }
            )
    print(f"Saved per-class metrics: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute confusion matrix and per-class metrics for YOLO detections."
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
        "--version",
        type=int,
        default=1,
        help="Version number appended to output filenames.",
    )
    parser.add_argument(
        "--iou-threshold",
        type=float,
        default=0.5,
        help="IoU threshold for matching (default: 0.5).",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("reports"),
        help="Directory to write report outputs (default: reports/).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    # Validate gt-dir
    if not args.gt_dir.exists() or not args.gt_dir.is_dir():
        print(f"ERROR: --gt-dir does not exist or is not a directory: {args.gt_dir}", file=sys.stderr)
        sys.exit(1)
    json_files = list(args.gt_dir.glob("*.json"))
    if not json_files:
        print(f"ERROR: --gt-dir is empty (no .json files found): {args.gt_dir}", file=sys.stderr)
        sys.exit(1)

    # Load category map
    name_to_id, id_to_name = load_category_map(args.category_map)
    num_classes = len(id_to_name)

    print(f"Loaded {num_classes} classes from {args.category_map}")
    print(f"Found {len(json_files)} ground-truth annotation files in {args.gt_dir}")

    # Load ground truth
    gt_by_stem = load_gt_annotations(args.gt_dir, name_to_id)

    # Count prediction coverage
    missing = sum(1 for stem in gt_by_stem if not (args.pred_dir / f"{stem}.txt").exists())
    if missing:
        print(f"Warning: {missing} GT files have no matching prediction file (treated as zero predictions).", file=sys.stderr)

    # Build confusion matrix
    cm = build_confusion_matrix(gt_by_stem, args.pred_dir, num_classes, args.iou_threshold)

    # Per-class metrics
    metrics = per_class_metrics(cm, num_classes)

    # mAP@0.5
    map50 = compute_map50(metrics)
    print(f"\nmAP@0.5: {map50:.4f}")

    # Top confused pairs
    pairs = top_confused_pairs(cm, num_classes, id_to_name)
    print("\nTop confused class pairs (GT -> Predicted, count):")
    for gt_name, pred_name, count in pairs:
        print(f"  {gt_name:30s} -> {pred_name:30s}  {count}")

    # Output paths
    v = args.version
    cm_path = args.reports_dir / f"confusion_matrix_v{v}.png"
    csv_path = args.reports_dir / f"per_class_metrics_v{v}.csv"

    # Save outputs
    plot_confusion_matrix(cm, id_to_name, cm_path, normalize=True)
    write_per_class_csv(metrics, id_to_name, csv_path)


if __name__ == "__main__":
    main()
