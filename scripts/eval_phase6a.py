#!/usr/bin/env python3
"""eval_phase6a.py — TASK-6a-5 INT8 vs FP16 small-element AP + TASK-6a-7 holdout eval.

Writes in-package reports only:
  reports/quantization_benchmark.json
  reports/eval_results_phase6a.json
  reports/centroid_bias_phase6a.json
  reports/phase6a_eval_summary.json

Usage:
  .venv-yolo/bin/python scripts/eval_phase6a.py
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import shutil
import struct
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("YOLO_CONFIG_DIR", str(PROJECT_ROOT / "NativeUITrainer" / ".ultralytics"))
os.environ.setdefault("TMPDIR", str(PROJECT_ROOT / "NativeUITrainer" / ".tmp"))
(PROJECT_ROOT / "NativeUITrainer" / ".tmp").mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from centroid_distribution import detect_bias, load_pred_centroids, spatial_entropy  # noqa: E402

YOLO_DATA = PROJECT_ROOT / "NativeUITrainer" / "yolo_dataset_41class"
WEIGHTS_DIR = PROJECT_ROOT / "NativeUITrainer" / "yolo_runs" / "phase6a_r007" / "weights"
CATEGORY_MAP = PROJECT_ROOT / "Research" / "schemas" / "category_map.json"
REPORTS = PROJECT_ROOT / "reports"
RUNS = PROJECT_ROOT / "NativeUITrainer" / "yolo_runs"

EMPTY_CLASSES = ("statusBar", "toolbar", "scrollIndicator", "tooltip", "unknown")
FOCUS_SMALL = ("homeIndicator", "stepperControl", "pageControl", "scrollIndicator", "link")
TEXT_CLASSES = ("label", "textField", "secureField", "searchField", "link")
SMALL_PX = 100
IOU_THR = 0.5
DROP_POINTS_LIMIT = 5.0
MAP_GATE = 0.85
CLASS_AP_FLOOR = 0.65
BLUR_DROP_LIMIT = 0.10
ENTROPY_N = 1000
BLUR_N = 200
LATENCY_N = 50

# Classes that TrainingDataStrategy treats as structure-not-text for the blur check.
NON_TEXT_PROBE = ("navigationBar", "tabBar", "toggle", "slider", "alert")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_names() -> list[str]:
    data = json.loads(CATEGORY_MAP.read_text())
    cats = sorted(data["categories"], key=lambda c: c["id"])
    return [c["name"] for c in cats]


def dir_size_mb(path: Path) -> float:
    if not path.exists():
        return 0.0
    if path.is_file():
        return path.stat().st_size / (1024 * 1024)
    total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    return total / (1024 * 1024)


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        if f.read(8) != b"\x89PNG\r\n\x1a\n":
            return 0, 0
        f.read(4)
        if f.read(4) != b"IHDR":
            return 0, 0
        w, h = struct.unpack(">II", f.read(8))
        return int(w), int(h)


def yolo_to_xyxy(cx: float, cy: float, w: float, h: float) -> tuple[float, float, float, float]:
    return cx - w / 2.0, cy - h / 2.0, cx + w / 2.0, cy + h / 2.0


def iou_xyxy(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    if inter <= 0:
        return 0.0
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def voc_ap(rec: list[float], prec: list[float]) -> float:
    """All-point interpolated AP (VOC 2010 / COCO AP@0.5)."""
    mrec = [0.0] + rec + [1.0]
    mpre = [0.0] + prec + [0.0]
    for i in range(len(mpre) - 1, 0, -1):
        mpre[i - 1] = max(mpre[i - 1], mpre[i])
    ap = 0.0
    for i in range(len(mrec) - 1):
        if mrec[i + 1] != mrec[i]:
            ap += (mrec[i + 1] - mrec[i]) * mpre[i + 1]
    return ap


def parse_yolo_txt(path: Path, has_conf: bool) -> list[tuple[int, float, float, float, float, float]]:
    """Return (cls, cx, cy, w, h, conf) rows. Missing conf → 1.0."""
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


def load_size_cache(image_dir: Path) -> dict[str, tuple[int, int]]:
    """Read PNG IHDR only (8-byte header + IHDR). Used for small-box pixel tests."""
    out: dict[str, tuple[int, int]] = {}
    for img in image_dir.glob("*.png"):
        out[img.stem] = png_size(img)
    return out


def load_gt(
    label_dir: Path,
    names: list[str],
    size_cache: dict[str, tuple[int, int]] | None = None,
) -> dict[str, list[dict]]:
    """stem → list of {cls, xyxy, px_w, px_h, small, cx, cy}.

    Pixel size is optional. Centroid analysis only needs cx/cy from the YOLO txt
    and must not open 11k training PNGs (that hung the first eval pass).
    """
    out: dict[str, list[dict]] = {}
    for lab in label_dir.glob("*.txt"):
        stem = lab.stem
        pw, ph = (size_cache or {}).get(stem, (0, 0))
        boxes = []
        for cid, cx, cy, w, h, _ in parse_yolo_txt(lab, has_conf=False):
            if not (0 <= cid < len(names)):
                continue
            px_w = w * pw if pw else 0.0
            px_h = h * ph if ph else 0.0
            boxes.append(
                {
                    "cls": cid,
                    "xyxy": yolo_to_xyxy(cx, cy, w, h),
                    "px_w": px_w,
                    "px_h": px_h,
                    "small": bool(pw and (px_w < SMALL_PX or px_h < SMALL_PX)),
                    "cx": cx,
                    "cy": cy,
                }
            )
        out[stem] = boxes
    return out


def load_preds(pred_dir: Path) -> dict[str, list[tuple[int, float, tuple[float, float, float, float]]]]:
    """stem → list of (cls, conf, xyxy)."""
    out: dict[str, list[tuple[int, float, tuple[float, float, float, float]]]] = {}
    for lab in sorted(pred_dir.glob("*.txt")):
        rows = []
        for cid, cx, cy, w, h, conf in parse_yolo_txt(lab, has_conf=True):
            rows.append((cid, conf, yolo_to_xyxy(cx, cy, w, h)))
        out[lab.stem] = rows
    return out


def ap50(gt: dict[str, list[dict]], preds: dict[str, list], names: list[str], small_only: bool) -> list[dict]:
    rows = []
    for cid, name in enumerate(names):
        gts_by_img: dict[str, list] = {}
        n_gt = 0
        for stem, boxes in gt.items():
            sel = [b["xyxy"] for b in boxes if b["cls"] == cid and (b["small"] if small_only else True)]
            if sel:
                gts_by_img[stem] = sel
                n_gt += len(sel)
        det = []
        for stem, plist in preds.items():
            for pc, conf, xyxy in plist:
                if pc == cid:
                    det.append((stem, conf, xyxy))
        det.sort(key=lambda t: t[1], reverse=True)
        if n_gt == 0:
            rows.append({"class": name, "n_gt": 0, "ap50": 0.0})
            continue
        tp = []
        fp = []
        matched = {s: [False] * len(v) for s, v in gts_by_img.items()}
        for stem, _, xyxy in det:
            gboxes = gts_by_img.get(stem, [])
            best_j, best_iou = -1, 0.0
            for j, gbox in enumerate(gboxes):
                if matched[stem][j]:
                    continue
                v = iou_xyxy(xyxy, gbox)
                if v > best_iou:
                    best_iou, best_j = v, j
            if best_j >= 0 and best_iou >= IOU_THR:
                matched[stem][best_j] = True
                tp.append(1)
                fp.append(0)
            else:
                tp.append(0)
                fp.append(1)
        if not tp:
            rows.append({"class": name, "n_gt": n_gt, "ap50": 0.0})
            continue
        cum_tp = cum_fp = 0
        rec, prec = [], []
        for t, f in zip(tp, fp):
            cum_tp += t
            cum_fp += f
            rec.append(cum_tp / n_gt)
            prec.append(cum_tp / (cum_tp + cum_fp))
        rows.append({"class": name, "n_gt": n_gt, "ap50": round(voc_ap(rec, prec), 6)})
    return rows


def extract_ultralytics_metrics(result, names: list[str]) -> dict:
    """Map Ultralytics per-class rows onto frozen taxonomy IDs.

    `box.class_result(j)` is indexed by the *present-class* list
    (`ap_class_index`), not by taxonomy id. Using `class_result(i)` for i in
    0..40 shifted P/R onto the wrong names and zeroed `nt_per_class`.
    """
    box = result.box
    present = [int(x) for x in getattr(box, "ap_class_index", [])]
    nt = getattr(box, "nt_per_class", None)
    by_cid: dict[int, dict] = {}
    for j, cid in enumerate(present):
        try:
            p, r, ap50_v, ap = box.class_result(j)
            p = 0.0 if p != p else float(p)
            r = 0.0 if r != r else float(r)
            ap50_v = 0.0 if ap50_v != ap50_v else float(ap50_v)
            ap = 0.0 if ap != ap else float(ap)
        except Exception:
            p = r = ap50_v = ap = 0.0
        n = int(nt[cid]) if nt is not None and cid < len(nt) else 0
        by_cid[cid] = {
            "class": names[cid] if cid < len(names) else str(cid),
            "ap50": round(ap50_v, 6),
            "ap50_95": round(ap, 6),
            "precision": round(p, 6),
            "recall": round(r, 6),
            "n": n,
        }
    per = []
    for i, name in enumerate(names):
        per.append(
            by_cid.get(
                i,
                {"class": name, "ap50": 0.0, "ap50_95": 0.0, "precision": 0.0, "recall": 0.0, "n": 0},
            )
        )
    return {
        "mAP50": round(float(box.map50), 6),
        "mAP50_95": round(float(box.map), 6),
        "perClass": per,
    }


def native_json_for_stem(image_dir: Path, stem: str) -> Path | None:
    png = image_dir / f"{stem}.png"
    if not png.exists():
        return None
    js = png.resolve().with_suffix(".json")
    return js if js.exists() else None


def template_family_for_stem(image_dir: Path, stem: str) -> str:
    js = native_json_for_stem(image_dir, stem)
    if js is None:
        return "unknown"
    try:
        ann = json.loads(js.read_text())
    except json.JSONDecodeError:
        return "unknown"
    profile = ann.get("generatorProfile") or {}
    return profile.get("templateFamily") or "unknown"


def ensure_int8(weights: Path, int8_pkg: Path) -> Path | None:
    """Build INT8 CoreML via linear weight quantization of an nms=False FP16 mlprogram.

    The NMS-baked FP16 package is a CoreML *pipeline*; linear_quantize_weights
    only accepts mlprogram. Ultralytics k-means palettize (quantize=8) SIGKILL'd
    YOLO11m. Export nms=False FP16, quantize that, restore the NMS FP16 default.
    """
    if int8_pkg.is_dir():
        print(f"INT8 package already present: {int8_pkg}")
        return int8_pkg
    from ultralytics import YOLO
    import coremltools as ct
    import coremltools.optimize.coreml as cto

    fp16_nms = WEIGHTS_DIR / "best_fp16.mlpackage"
    fp16_nonms = WEIGHTS_DIR / "best_fp16_nonms.mlpackage"
    default = WEIGHTS_DIR / "best.mlpackage"

    if not fp16_nonms.is_dir():
        print("Exporting nms=False FP16 mlprogram for INT8 quantization…")
        model = YOLO(str(weights))
        exported = Path(model.export(format="coreml", imgsz=640, nms=False, quantize=16, verbose=True))
        if fp16_nonms.exists():
            shutil.rmtree(fp16_nonms)
        exported.rename(fp16_nonms)
        if fp16_nms.is_dir():
            if default.exists():
                shutil.rmtree(default)
            shutil.copytree(fp16_nms, default)
            print(f"Restored NMS FP16 → {default.name}")

    print(f"INT8 linear_quantize_weights from {fp16_nonms.name}…")
    mlmodel = ct.models.MLModel(str(fp16_nonms))
    config = cto.OptimizationConfig(
        global_config=cto.OpLinearQuantizerConfig(mode="linear_symmetric")
    )
    quantized = cto.linear_quantize_weights(mlmodel, config)
    if int8_pkg.exists():
        shutil.rmtree(int8_pkg)
    quantized.save(str(int8_pkg))
    print(f"INT8 exported → {int8_pkg} ({dir_size_mb(int8_pkg):.1f} MB)")
    return int8_pkg


def run_val(model_path: Path, split: str, name: str, device: str | None):
    from ultralytics import YOLO

    model = YOLO(str(model_path))
    kwargs = dict(
        data=str(YOLO_DATA / "dataset.yaml"),
        split=split,
        imgsz=640,
        batch=4,
        plots=True,
        project=str(RUNS),
        name=name,
        exist_ok=True,
        verbose=True,
    )
    if device:
        kwargs["device"] = device
    return model.val(**kwargs)


def run_predict(model_path: Path, source: Path, name: str, device: str | None, conf: float) -> Path:
    from ultralytics import YOLO

    model = YOLO(str(model_path))
    kwargs = dict(
        source=str(source),
        imgsz=640,
        conf=conf,
        save_txt=True,
        save_conf=True,
        save=False,
        stream=True,
        project=str(RUNS),
        name=name,
        exist_ok=True,
        verbose=False,
    )
    if device:
        kwargs["device"] = device
    # stream=True so 2,000-image dirs do not accumulate Results in RAM.
    for _ in model.predict(**kwargs):
        pass
    labels = RUNS / name / "labels"
    if not labels.is_dir():
        # Ultralytics sometimes nests predict/labels
        alt = RUNS / name
        found = list(alt.rglob("labels"))
        labels = found[0] if found else labels
    return labels


def blur_text_images(stems: list[str], image_dir: Path, out_dir: Path) -> int:
    from PIL import Image, ImageFilter

    out_dir.mkdir(parents=True, exist_ok=True)
    n_written = 0
    for stem in stems:
        src = image_dir / f"{stem}.png"
        js = native_json_for_stem(image_dir, stem)
        if not src.exists() or js is None:
            continue
        ann = json.loads(js.read_text())
        img = Image.open(src).convert("RGB")
        for el in ann.get("elements") or []:
            if el.get("excluded") is True:
                continue
            et = el.get("elementType") or el.get("type")
            if et not in TEXT_CLASSES:
                continue
            bp = el.get("boundsPixels") or {}
            try:
                x, y = int(bp["x"]), int(bp["y"])
                w, h = int(bp["width"]), int(bp["height"])
            except (KeyError, TypeError, ValueError):
                continue
            if w < 2 or h < 2:
                continue
            x2, y2 = min(img.width, x + w), min(img.height, y + h)
            x, y = max(0, x), max(0, y)
            crop = img.crop((x, y, x2, y2))
            img.paste(crop.filter(ImageFilter.GaussianBlur(radius=12)), (x, y))
        dest = out_dir / f"{stem}.png"
        img.save(dest)
        n_written += 1
    return n_written


def mean_ap(rows: list[dict], classes: tuple[str, ...] | None = None, require_gt: bool = True) -> float:
    sel = rows
    if classes is not None:
        sel = [r for r in rows if r["class"] in classes]
    if require_gt:
        sel = [r for r in sel if r.get("n") or r.get("n_gt")]
    if not sel:
        return 0.0
    key = "ap50" if "ap50" in sel[0] else "ap50"
    return sum(r[key] for r in sel) / len(sel)


def write_quant_report(
    names: list[str],
    fp16_pkg: Path,
    int8_pkg: Path,
    weights: Path,
    small_fp16: list[dict] | None,
    small_int8: list[dict] | None,
    small_fallback: list[dict] | None = None,
) -> dict:
    """Write reports/quantization_benchmark.json and return the payload."""
    fp16_rows = small_fp16 or small_fallback
    if fp16_rows is None:
        raise RuntimeError("no FP16 small-element AP rows")
    int8_rows = small_int8
    quant_per = []
    max_drop = 0.0
    ship = "fp16"
    for name in names:
        a = next(r for r in fp16_rows if r["class"] == name)
        b = next((r for r in (int8_rows or []) if r["class"] == name), None)
        ap_fp = a["ap50"]
        ap_i8 = b["ap50"] if b else None
        delta = None if ap_i8 is None else round((ap_fp - ap_i8) * 100.0, 3)
        drop = bool(delta is not None and delta > DROP_POINTS_LIMIT and a["n_gt"] > 0)
        if delta is not None:
            max_drop = max(max_drop, delta)
        quant_per.append(
            {
                "class": name,
                "n_small_gt": a["n_gt"],
                "ap50_fp16": ap_fp,
                "ap50_int8": ap_i8,
                "delta_points": delta,
                "drop_over_5pt": drop,
                "focus": name in FOCUS_SMALL,
            }
        )
    focus_drops = [r for r in quant_per if r["focus"] and r["drop_over_5pt"]]
    nms_fp16 = weights.parent / "best_fp16.mlpackage"
    if not nms_fp16.is_dir():
        nms_fp16 = weights.parent / "best.mlpackage"
    ship_size = dir_size_mb(nms_fp16) if nms_fp16.is_dir() else dir_size_mb(fp16_pkg)
    if int8_rows is None:
        reason = "INT8 package missing; ship FP16"
    elif focus_drops:
        reason = (
            f"INT8 small-element AP dropped >{DROP_POINTS_LIMIT:g} pt vs FP16 on "
            + ", ".join(r["class"] for r in focus_drops)
        )
    elif ship_size <= 50:
        reason = (
            f"INT8 did not drop >{DROP_POINTS_LIMIT:g} pt, but NMS FP16 is "
            f"{ship_size:.1f} MB < 50 MB — ship FP16 (no distill, no INT8 required)"
        )
    else:
        ship = "int8"
        reason = "FP16 > 50 MB and INT8 small-element drop ≤ 5 pt"
    quant = {
        "date": utc_now(),
        "fp16_model": str(fp16_pkg.relative_to(PROJECT_ROOT)),
        "int8_model": str(int8_pkg.relative_to(PROJECT_ROOT)) if int8_pkg.is_dir() else None,
        "fp16_size_mb": round(dir_size_mb(fp16_pkg), 3),
        "int8_size_mb": round(dir_size_mb(int8_pkg), 3) if int8_pkg.is_dir() else None,
        "nms_fp16_size_mb": round(ship_size, 3),
        "pt_size_mb": round(dir_size_mb(weights), 3),
        "small_element_rule": "boundsPixels.width < 100 OR boundsPixels.height < 100",
        "iou": IOU_THR,
        "focus_classes": list(FOCUS_SMALL),
        "backend": "coreml" if small_fp16 and small_int8 else "pytorch_fp16_proxy" if not small_int8 else "mixed",
        "per_class": quant_per,
        "max_drop_points": round(max_drop, 3),
        "ship": ship,
        "reason": reason,
        "distill_required": ship_size > 50,
    }
    qpath = REPORTS / "quantization_benchmark.json"
    qpath.write_text(json.dumps(quant, indent=2) + "\n")
    print(f"Wrote {qpath}  ship={ship}")
    return quant


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--weights", default=str(WEIGHTS_DIR / "best.pt"))
    p.add_argument("--skip-int8-export", action="store_true")
    p.add_argument("--quant-only", action="store_true", help="TASK-6a-5 only (CoreML FP16 vs INT8 small-element AP)")
    p.add_argument("--skip-coreml-predict", action="store_true", help="Skip CoreML test predict (6a-7 path)")
    p.add_argument("--blur-n", type=int, default=BLUR_N)
    p.add_argument("--entropy-n", type=int, default=ENTROPY_N)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    REPORTS.mkdir(parents=True, exist_ok=True)
    names = load_names()
    weights = Path(args.weights).resolve()
    weights_dir = weights.parent
    run_name = weights.parent.parent.name
    fp16_pkg = weights_dir / "best_fp16_nonms.mlpackage"
    if not fp16_pkg.is_dir() and not args.quant_only:
        # Full eval may still score the NMS FP16 package if the nms=False export is missing.
        fallback_fp16 = weights_dir / "best_fp16.mlpackage"
        fp16_pkg = fallback_fp16 if fallback_fp16.is_dir() else weights_dir / "best.mlpackage"
    int8_pkg = weights_dir / "best_int8_nonms.mlpackage"
    test_images = YOLO_DATA / "test" / "images"
    test_labels = YOLO_DATA / "test" / "labels"
    train_images = YOLO_DATA / "train" / "images"

    print(f"=== Phase 6a eval {utc_now()} ===")
    print(f"weights : {weights}")
    print(f"fp16    : {fp16_pkg} ({dir_size_mb(fp16_pkg):.1f} MB)")

    if not args.skip_int8_export:
        try:
            ensure_int8(weights, int8_pkg)
        except Exception as e:
            print(f"INT8 export failed: {e}")
    print(f"int8    : {int8_pkg} exists={int8_pkg.is_dir()} ({dir_size_mb(int8_pkg):.1f} MB)")

    if args.quant_only:
        print("\n--- TASK-6a-5 quant-only ---")
        gt = load_gt(test_labels, names, load_size_cache(test_images))
        small_fp16_cm = small_int8_cm = None
        if fp16_pkg.is_dir():
            pred_fp16 = run_predict(fp16_pkg, test_images, f"{run_name}_fp16_pred", device=None, conf=0.001)
            small_fp16_cm = ap50(gt, load_preds(pred_fp16), names, small_only=True)
        if int8_pkg.is_dir():
            pred_int8 = run_predict(int8_pkg, test_images, f"{run_name}_int8_pred", device=None, conf=0.001)
            small_int8_cm = ap50(gt, load_preds(pred_int8), names, small_only=True)
        write_quant_report(names, fp16_pkg, int8_pkg, weights, small_fp16_cm, small_int8_cm)
        return

    # --- 6a-7 official holdout val (PyTorch / MPS) ---
    print("\n--- withheld-template test val (best.pt) ---")
    test_result = run_val(weights, "test", f"{run_name}_test", device="mps")
    test_metrics = extract_ultralytics_metrics(test_result, names)
    below_floor = [
        r for r in test_metrics["perClass"] if r["n"] > 0 and r["ap50"] < CLASS_AP_FLOOR
    ]
    print(f"test mAP@0.5={test_metrics['mAP50']:.4f}  classes <0.65: {len(below_floor)}")

    # --- predictions for small-AP / centroid / template / entropy ---
    print("\n--- predict test (best.pt) ---")
    pred_pt = run_predict(weights, test_images, f"{run_name}_test_pred", device="mps", conf=0.001)
    gt = load_gt(test_labels, names, load_size_cache(test_images))
    preds_pt = load_preds(pred_pt)
    small_pt = ap50(gt, preds_pt, names, small_only=True)
    full_pt_custom = ap50(gt, preds_pt, names, small_only=False)

    # CoreML FP16 / INT8 small-element AP (same NMS bake-in on both packages)
    small_fp16_cm = None
    small_int8_cm = None
    if not args.skip_coreml_predict:
        if fp16_pkg.is_dir():
            print("\n--- predict test (CoreML FP16) ---")
            pred_fp16 = run_predict(fp16_pkg, test_images, f"{run_name}_fp16_pred", device=None, conf=0.001)
            small_fp16_cm = ap50(gt, load_preds(pred_fp16), names, small_only=True)
        if int8_pkg.is_dir():
            print("\n--- predict test (CoreML INT8) ---")
            pred_int8 = run_predict(int8_pkg, test_images, f"{run_name}_int8_pred", device=None, conf=0.001)
            small_int8_cm = ap50(gt, load_preds(pred_int8), names, small_only=True)

    quant = write_quant_report(
        names, fp16_pkg, int8_pkg, weights, small_fp16_cm, small_int8_cm, small_pt
    )
    ship = quant["ship"]
    reason = quant["reason"]

    # --- content-agnostic blur (200 images, TrainingDataStrategy) ---
    print(f"\n--- blur text on {args.blur_n} test images ---")
    rng = random.Random(6)
    stems = sorted(p.stem for p in test_images.glob("*.png"))
    blur_stems = stems if len(stems) <= args.blur_n else rng.sample(stems, args.blur_n)
    blur_img_dir = PROJECT_ROOT / "reports" / "blurred_eval_images"
    if blur_img_dir.exists():
        shutil.rmtree(blur_img_dir)
    n_blur = blur_text_images(blur_stems, test_images, blur_img_dir)
    blur_root = PROJECT_ROOT / "NativeUITrainer" / ".tmp" / "blur_eval"
    blur_images = blur_root / "images"
    blur_labels = blur_root / "labels"
    if blur_root.exists():
        shutil.rmtree(blur_root)
    blur_images.mkdir(parents=True)
    blur_labels.mkdir(parents=True)
    for stem in blur_stems:
        src_img = blur_img_dir / f"{stem}.png"
        src_lab = test_labels / f"{stem}.txt"
        if src_img.exists():
            (blur_images / f"{stem}.png").symlink_to(src_img.resolve())
        if src_lab.exists():
            (blur_labels / f"{stem}.txt").symlink_to(src_lab.resolve())
    yaml_names = "\n".join(f"  {i}: {n}" for i, n in enumerate(names))
    blur_yaml = blur_root / "dataset.yaml"
    blur_yaml.write_text(
        f"path: {blur_root}\ntrain: images\nval: images\nnc: {len(names)}\nnames:\n{yaml_names}\n"
    )
    from ultralytics import YOLO

    blur_model = YOLO(str(weights))
    blur_result = blur_model.val(
        data=str(blur_yaml),
        split="val",
        imgsz=640,
        batch=4,
        device="mps",
        plots=False,
        project=str(RUNS),
        name=f"{run_name}_blur",
        exist_ok=True,
        verbose=True,
    )
    blur_metrics = extract_ultralytics_metrics(blur_result, names)
    # Baseline on the same 200 stems from custom AP of full test is not the same subset.
    # Recompute AP on the blur subset from pytorch test preds vs GT (unblurred boxes).
    gt_blur = {s: gt[s] for s in blur_stems if s in gt}
    pred_blur_base = {s: preds_pt.get(s, []) for s in blur_stems}
    base_subset = ap50(gt_blur, pred_blur_base, names, small_only=False)
    probe_drop = {}
    for cls_name in NON_TEXT_PROBE:
        b = next(r for r in base_subset if r["class"] == cls_name)
        a = next((r for r in blur_metrics["perClass"] if r["class"] == cls_name), None)
        blur_ap = a["ap50"] if a else 0.0
        drop = (b["ap50"] - blur_ap) * 100.0
        probe_drop[cls_name] = {
            "ap50_clear": b["ap50"],
            "ap50_blur": blur_ap,
            "drop_points": round(drop, 3),
            "n_gt": b["n_gt"],
        }
    max_probe_drop = max((v["drop_points"] for v in probe_drop.values()), default=0.0)
    nontext_ids = set(names) - set(TEXT_CLASSES)
    base_nt = mean_ap(base_subset, tuple(nontext_ids))
    blur_nt = mean_ap(
        [{"class": r["class"], "ap50": r["ap50"], "n": r["n"]} for r in blur_metrics["perClass"]],
        tuple(nontext_ids),
    )
    print(f"blurred {n_blur} images; non-text probe max drop={max_probe_drop:.2f} pt")

    # --- centroid bias (predictions on holdout test; skip 11k train PNG/label scan) ---
    print("\n--- centroid bias ---")
    pred_cent = load_pred_centroids(pred_pt, set(stems), len(names))
    centroid_rows = []
    any_bias = False
    for cid, name in enumerate(names):
        n_pred = len(pred_cent[cid])
        flag, region = detect_bias(pred_cent[cid]) if n_pred >= 50 else (False, None)
        if flag:
            any_bias = True
        centroid_rows.append(
            {
                "class_name": name,
                "training_entropy": None,
                "prediction_entropy": round(spatial_entropy(pred_cent[cid]), 6),
                "bias_flag": flag,
                "bias_region": region,
                "n_train": None,
                "n_pred": n_pred,
            }
        )
    cpath = REPORTS / "centroid_bias_phase6a.json"
    cpath.write_text(json.dumps({"date": utc_now(), "classes": centroid_rows}, indent=2) + "\n")
    print(f"Wrote {cpath}  any_bias={any_bias}")

    # --- per-template AP ---
    print("\n--- per-template AP ---")
    by_fam: dict[str, list[str]] = defaultdict(list)
    for stem in stems:
        by_fam[template_family_for_stem(test_images, stem)].append(stem)
    template_ap = []
    for fam, fam_stems in sorted(by_fam.items()):
        sub_gt = {s: gt[s] for s in fam_stems if s in gt}
        sub_pr = {s: preds_pt.get(s, []) for s in fam_stems}
        rows = ap50(sub_gt, sub_pr, names, small_only=False)
        present = [r for r in rows if r["n_gt"] > 0]
        fam_map = sum(r["ap50"] for r in present) / len(present) if present else 0.0
        template_ap.append(
            {
                "templateFamily": fam,
                "n_images": len(fam_stems),
                "mAP50": round(fam_map, 6),
                "perClass": present,
            }
        )
    overfit_flag = test_metrics["mAP50"] < MAP_GATE and any(t["mAP50"] > 0.95 for t in template_ap)

    # Entropy on holdout test predictions (no extra 1000-image train glob/predict).
    print("\n--- prediction entropy by holdout template family ---")
    fam_H: dict[str, list[float]] = defaultdict(list)
    for stem in stems:
        plist = preds_pt.get(stem, [])
        masses = [0.0] * len(names)
        for cid, conf, _xy in plist:
            if 0 <= cid < len(names):
                masses[cid] += conf
        total = sum(masses)
        if total <= 0:
            H = 0.0
        else:
            H = 0.0
            for m in masses:
                if m > 0:
                    q = m / total
                    H -= q * math.log2(q)
        fam_H[template_family_for_stem(test_images, stem)].append(H)
    fam_rank = sorted(
        (
            {
                "templateFamily": fam,
                "n": len(hs),
                "mean_entropy": round(sum(hs) / len(hs), 6),
            }
            for fam, hs in fam_H.items()
        ),
        key=lambda d: d["mean_entropy"],
        reverse=True,
    )
    top5 = fam_rank[:5]
    print("top-5 uncertain families:", ", ".join(t["templateFamily"] for t in top5))

    # --- Mac latency proxy ---
    print("\n--- Mac latency (ANE/CPU proxy; not a physical iPhone) ---")
    bench_imgs = stems[:LATENCY_N]
    latency = {"platform": "macOS M4 proxy", "physical_iphone": False, "n": len(bench_imgs)}
    nms_fp16 = WEIGHTS_DIR / "best_fp16.mlpackage"
    pkg_for_lat = nms_fp16 if nms_fp16.is_dir() else (fp16_pkg if fp16_pkg.is_dir() else weights)
    t0 = time.perf_counter()
    lat_model = YOLO(str(pkg_for_lat))
    latency["cold_load_s"] = round(time.perf_counter() - t0, 4)
    # warmup
    if bench_imgs:
        lat_model.predict(source=str(test_images / f"{bench_imgs[0]}.png"), imgsz=640, verbose=False)
    times = []
    for stem in bench_imgs:
        t1 = time.perf_counter()
        lat_model.predict(source=str(test_images / f"{stem}.png"), imgsz=640, verbose=False)
        times.append((time.perf_counter() - t1) * 1000.0)
    latency["inference_ms_mean"] = round(sum(times) / len(times), 2) if times else None
    latency["inference_ms_p95"] = round(sorted(times)[int(0.95 * (len(times) - 1))], 2) if times else None
    latency["size_mb"] = round(dir_size_mb(pkg_for_lat), 3)
    latency["cold_load_pass"] = latency["cold_load_s"] < 3.0
    latency["inference_pass"] = (latency["inference_ms_mean"] or 999) < 200
    latency["size_pass"] = latency["size_mb"] < 50
    print(
        f"cold={latency['cold_load_s']:.2f}s  infer={latency['inference_ms_mean']}ms  "
        f"size={latency['size_mb']:.1f}MB"
    )

    real_world_dir = REPORTS / "real_world_screenshots"
    n_real = len(list(real_world_dir.glob("*.png"))) if real_world_dir.is_dir() else 0

    eval_out = {
        "model": run_name,
        "evalDate": utc_now(),
        "split": "test (family holdout)",
        "n_images": len(stems),
        "mAP50": test_metrics["mAP50"],
        "mAP50_95": test_metrics["mAP50_95"],
        "dsG8_map_pass": test_metrics["mAP50"] >= MAP_GATE,
        "dsG8_class_floor_pass": len(below_floor) == 0,
        "classes_below_0_65": [r["class"] for r in below_floor],
        "empty_classes": list(EMPTY_CLASSES),
        "perClass": test_metrics["perClass"],
        "small_element_ap_pt": small_pt,
        "custom_full_ap_pt": full_pt_custom,
        "blur": {
            "n_images": n_blur,
            "non_text_probe": probe_drop,
            "max_probe_drop_points": max_probe_drop,
            "nontext_mean_ap_clear": round(base_nt, 6),
            "nontext_mean_ap_blur": round(blur_nt, 6),
            "pass": max_probe_drop < (BLUR_DROP_LIMIT * 100),
        },
        "centroid_any_bias": any_bias,
        "per_template_overfit_flag": overfit_flag,
        "per_template": [{"templateFamily": t["templateFamily"], "n_images": t["n_images"], "mAP50": t["mAP50"]} for t in template_ap],
        "entropy_proxy": {
            "n": len(stems),
            "note": "Holdout-test prediction entropy by templateFamily. No unlabeled generator dump exists; 200 real-world images also missing.",
            "top5_uncertain_families": top5,
        },
        "real_world": {
            "n_annotated": n_real,
            "required": 200,
            "mAP50": None,
            "gap": "No real-world screenshot set in reports/real_world_screenshots/",
        },
        "device": latency,
    }
    epath = REPORTS / "eval_results_phase6a.json"
    epath.write_text(json.dumps(eval_out, indent=2) + "\n")

    summary = {
        "date": utc_now(),
        "task_6a_5": {
            "ship": ship,
            "fp16_size_mb": quant["fp16_size_mb"],
            "int8_size_mb": quant["int8_size_mb"],
            "max_drop_points": quant["max_drop_points"],
            "distill_required": quant["distill_required"],
            "reason": reason,
        },
        "task_6a_7": {
            "mAP50": test_metrics["mAP50"],
            "map_gate": test_metrics["mAP50"] >= MAP_GATE,
            "class_floor_gate": len(below_floor) == 0,
            "classes_below_0_65": [r["class"] for r in below_floor],
            "blur_pass": eval_out["blur"]["pass"],
            "centroid_pass": not any_bias,
            "template_overfit_pass": not overfit_flag,
            "real_world_n": n_real,
            "entropy_top5": top5,
            "device_mac_proxy": latency,
            "ds_g8": False,
        },
    }
    # DS-G8 requires every AC, including empty-class floor, real-world set, and physical device.
    summary["task_6a_7"]["ds_g8"] = bool(
        summary["task_6a_7"]["map_gate"]
        and summary["task_6a_7"]["class_floor_gate"]
        and summary["task_6a_7"]["blur_pass"]
        and summary["task_6a_7"]["centroid_pass"]
        and summary["task_6a_7"]["template_overfit_pass"]
        and n_real >= 200
        and latency.get("physical_iphone")
        and latency.get("inference_pass")
        and latency.get("cold_load_pass")
        and latency.get("size_pass")
    )
    spath = REPORTS / "phase6a_eval_summary.json"
    spath.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\nWrote {epath}")
    print(f"Wrote {spath}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
