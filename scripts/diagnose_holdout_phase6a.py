#!/usr/bin/env python3
"""diagnose_holdout_phase6a.py — Why Run 007 holdout AP collapsed.

Reads YOLO labels only (no PNG opens). Writes
`reports/holdout_diagnosis_phase6a.json`.

Usage:
  .venv-yolo/bin/python scripts/diagnose_holdout_phase6a.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
YOLO = PROJECT_ROOT / "NativeUITrainer" / "yolo_dataset_41class"
CATS = json.loads((PROJECT_ROOT / "Research" / "schemas" / "category_map.json").read_text())
NAMES = [c["name"] for c in sorted(CATS["categories"], key=lambda x: x["id"])]
PRED_DIR = PROJECT_ROOT / "NativeUITrainer" / "yolo_runs" / "phase6a_r007_test_pred" / "labels"
FAILING = (
    "imageView",
    "listRow",
    "pageControl",
    "picker",
    "secondaryButton",
    "secureField",
    "stepperControl",
    "textField",
    "toggle",
)
IOU = 0.5


def parse_txt(path: Path, has_conf: bool) -> list[tuple[int, float, float, float, float, float]]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        cid = int(float(parts[0]))
        cx, cy, w, h = map(float, parts[1:5])
        conf = float(parts[5]) if has_conf and len(parts) >= 6 else 1.0
        rows.append((cid, cx, cy, w, h, conf))
    return rows


def xyxy(cx: float, cy: float, w: float, h: float) -> tuple[float, float, float, float]:
    return cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2


def iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    if inter <= 0:
        return 0.0
    aa = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    bb = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    u = aa + bb - inter
    return inter / u if u > 0 else 0.0


def count_test() -> Counter:
    """Count boxes on the 2,000-image holdout only. Do not glob train/labels
    (11,504 files hung Path.glob on this volume)."""
    c: Counter = Counter()
    d = YOLO / "test" / "labels"
    for p in d.iterdir():
        if p.suffix != ".txt":
            continue
        for cid, *_rest in parse_txt(p, False):
            if 0 <= cid < len(NAMES):
                c[NAMES[cid]] += 1
    return c


def main() -> None:
    report = json.loads((YOLO / "export_report.json").read_text())
    totals = report.get("boxes_per_class") or {}
    test = count_test()
    per_class = []
    for name in NAMES:
        te = test[name]
        all_n = int(totals.get(name, 0))
        train_val = all_n - te
        per_class.append(
            {
                "class": name,
                "train_plus_val": train_val,
                "test": te,
                "total": all_n,
                "zero_shot_holdout": train_val <= 0 and te > 0,
            }
        )

    # Confusion: for each failing-class GT box, which pred class matches (or miss).
    confusions: dict[str, Counter] = {n: Counter() for n in FAILING}
    misses: Counter = Counter()
    for lab in (YOLO / "test" / "labels").iterdir():
        if lab.suffix != ".txt":
            continue
        gts = parse_txt(lab, False)
        preds = parse_txt(PRED_DIR / lab.name, True)
        pred_boxes = [(cid, xyxy(cx, cy, w, h), conf) for cid, cx, cy, w, h, conf in preds]
        used = [False] * len(pred_boxes)
        for cid, cx, cy, w, h, _ in gts:
            if not (0 <= cid < len(NAMES)):
                continue
            name = NAMES[cid]
            if name not in FAILING:
                continue
            gbox = xyxy(cx, cy, w, h)
            best_i, best_iou, best_cid = -1, 0.0, None
            for i, (pc, pbox, _) in enumerate(pred_boxes):
                if used[i]:
                    continue
                v = iou(gbox, pbox)
                if v > best_iou:
                    best_iou, best_i, best_cid = v, i, pc
            if best_i >= 0 and best_iou >= IOU:
                used[best_i] = True
                confusions[name][NAMES[best_cid] if best_cid is not None and best_cid < len(NAMES) else str(best_cid)] += 1
            else:
                misses[name] += 1
                confusions[name]["__miss__"] += 1

    tv = {r["class"]: r["train_plus_val"] for r in per_class}
    fail_rows = []
    for name in FAILING:
        n_gt = test[name]
        top = confusions[name].most_common(8)
        fail_rows.append(
            {
                "class": name,
                "train_plus_val": tv[name],
                "test": test[name],
                "miss_rate": round(misses[name] / n_gt, 4) if n_gt else None,
                "matched_as": [{"class": k, "n": v} for k, v in top],
            }
        )

    out = {
        "note": (
            "zero_shot_holdout=true means the class appears in the withheld test "
            "split but has 0 train boxes — BP-27 unique-source violation. "
            "Otherwise AP=0 is a visual-style miss (train saw a different chrome)."
        ),
        "splits": {"train_images": 11504, "val_images": 2936, "test_images": 2000},
        "per_class": per_class,
        "failing_holdout_classes": fail_rows,
        "zero_shot": [r["class"] for r in per_class if r["zero_shot_holdout"]],
    }
    dest = PROJECT_ROOT / "reports" / "holdout_diagnosis_phase6a.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"Wrote {dest}")
    print("zero-shot holdout classes:", out["zero_shot"] or "(none)")
    print("\nFailing classes (train / test / miss_rate / top match):")
    for r in fail_rows:
        top = r["matched_as"][:3]
        print(
            f"  {r['class']:18s} train+val={r['train_plus_val']:5d} test={r['test']:4d} "
            f"miss={r['miss_rate']}  {top}"
        )


if __name__ == "__main__":
    main()
