# EXP418-07 — Scale-Gated Dual-Resolution SAHI + Weighted Box Fusion (`B405-235` / Template `T73`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `tvOS detection` (`TV`) and `iOS detection` (`IOS`). Priority: `P0`.
Parent task: `INFERENCE412` / `B405-130`. Template: `T73` (`sahi_wbf_inference418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [DetectorInference412.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/DetectorInference412.md) (`B405-121`, `B405-130`), `Maximum-mini-NUIAK` discovered a sharp scale trade-off when running the tvOS detector on the 46 reviewed real frames:
- At `640 px` (production default), the model detects `247` controls (PyTorch) / `273` controls (Core ML), missing `124 of 224` `listRow` instances and `24 of 24` `tabItem` instances.
- Increasing full-frame inference size to `960 px` **gains `74` controls** (mostly `listRow`), but **loses `34` prior successes** (mostly large `collectionItem` cards that get misclassified as `imageView` or `sheet`).
- Increasing full-frame inference size to `1280 px` **gains `63` controls**, but **loses `95` prior successes**!
- Furthermore, the bundled Core ML model in `NativeUIAuditKitModels` has a **fixed `640 x 640` input tensor**, so it cannot run full-frame `960 px` or `1280 px` inference without re-exporting and breaking ANE compilation.

### SOTA Method: Scale-Gated Slicing Aided Hyper Inference (SAHI) + Weighted Box Fusion (WBF)
This experiment combines two SOTA inference techniques with a novel **Receptive-Field Scale Gate**:
1. **SAHI (Slicing Aided Hyper Inference)** (Akyon et al., *Slicing Aided Hyper Inference and Fine-Tuning for Small Object Detection*): Run the fixed `640 x 640` detector on (a) the full frame and (b) overlapping high-resolution sub-crops (such as the top tab/navigation band and 2x2 or 3x2 content tiles). Every call uses the exact `640 x 640` input shape that the Core ML model and ANE are optimized for!
2. **Receptive-Field Scale Gating + Weighted Box Fusion (WBF)** (Solovyev et al., *Weighted Boxes Fusion*): Why did `960 px` and `1280 px` lose `collectionItem` detections? Because in a zoomed-in tile, a large poster card occupies `> 50 %` of the tile and looks like a full-screen `imageView` or `sheet`! Conversely, in the full frame, a `tabItem` or small `label` is crushed to `< 12 px`.
   Therefore, **Scale-Gated SAHI** enforces a strict scale partition before WBF merging:
   - From the **full-frame `640 px` pass**, keep all predictions.
   - From the **high-resolution tile passes**, **reject** any prediction whose unmapped full-screen area fraction exceeds $\alpha_{\max}$ (e.g., `0.04` of screen area) or whose predicted class is a large container (`collectionItem`, `sheet`, `alert`, `navigationBar`), and **admit only** small/thin classes (`tabItem`, `listRow`, `primaryButton`, `toggle`, `pageControl`, small `label`) that do not conflict with high-confidence full-frame containers!

---

## 2. Controlled Test and Decision Rules

### Hypothesis
Scale-Gated SAHI + WBF recovers the `listRow`, `tabItem`, and small `label` detections found at high resolution while losing **0** `collectionItem` or large-control successes from the `640 px` baseline.

### Experimental Arms
All arms run on the pinned 46 reviewed tvOS frames (`REAL-MODEL-SCORECARD-36`) or the 2,000 withheld iOS frames at confidence `0.50` (tvOS) / `0.25` (iOS) using fixed `640 x 640` model calls:
1. `control` (`fusionMode = 'full-frame-only'`, `tileLayout = 'none'`): Single `640 x 640` full-frame pass. Must reproduce the baseline scorecard with `0` gains and `0` losses.
2. `naive-sahi-nms` (`fusionMode = 'unfiltered-nms'`, `tileLayout = 'grid-2x2'`): Full frame + 2x2 overlapping `640 x 640` tiles merged with standard greedy NMS (`IoU 0.45`).
3. `scale-gated-bands` (`fusionMode = 'scale-gated-wbf'`, `tileLayout = 'top-band-plus-rows'`): Full frame + 2 horizontal high-resolution bands (top tab/header band + center list band), admitting only small/row classes (`areaFrac <= 0.04`) via WBF.
4. `scale-gated-grid` (`fusionMode = 'scale-gated-wbf'`, `tileLayout = 'grid-2x2'`): Full frame + 2x2 overlapping tiles (`20 %` overlap), admitting only small/row classes (`areaFrac <= 0.04`) via WBF.

### Mechanical Decision Rule (`gain-without-loss`)
- **Supported**: A scale-gated arm gains `>= 35` matched controls on the 46 real tvOS frames (or `>= 250` small labels on iOS), loses `0` prior successes from the `640 px` control (`lostPriorSuccesses == []`), and adds fewer than `1.5` unmatched boxes per gained true positive.
- **Contradicted**: Scale gating still loses prior `640 px` successes or fails to recover `listRow` / `tabItem` / small `label` instances.
- **Inconclusive**: Tile coordinate unmapping or baseline control parity fails.

---

## 3. What This Tells TTR and NUIAK

- **If Supported**:
  - `Maximum-mini-NUIAK` achieves an immediate, training-free accuracy jump on both tvOS (`nativeui-tvos-v3.0`) and iOS (`nativeui-ios-v2.0` / Run 013) while keeping the exact bundled `640 x 640` Core ML `.mlmodelc` packages!
  - `NativeUIDetectionSession` in Swift can execute the full frame plus 2 to 4 `640 x 640` crops in a single batched `VNImageRequestHandler` / `MLBatchProvider` call on the Apple Neural Engine in `< 18 ms`.
  - `Sillycon-TTR` immediately gains `listRow` and `tabItem` proposals for Settings and top-tab navigation without waiting for a new YOLO training run.
- **If Contradicted**:
  - `Maximum-mini-NUIAK` proves that `tabItem` misses on tvOS are due to missing training taxonomy examples rather than resolution, prioritizing `tabItem` annotation admission in Phase 6b v3.1.

---

## 4. Template `T73` Contract

### Entry in `scripts/hcf_templates395.py`
```python
'T73': (
    {'labels', 'baseline', 'model'},
    {'fusionMode', 'tileLayout', 'confidence'},
    'sahi_wbf_inference418.run',
    'artifact',
    'diagnostic',
),
```

### Inputs and Parameters
- **Inputs**:
  - `labels`: Pinned reviewed frame manifest (`real-model-labels-v1`).
  - `baseline`: Pinned baseline scorecard (`real-model-scorecard-v1`).
  - `model`: Pinned detector weights or CLI binary.
- **Parameters**:
  - `fusionMode`: `str` in `{'full-frame-only', 'unfiltered-nms', 'scale-gated-wbf'}`.
  - `tileLayout`: `str` in `{'none', 'top-band-plus-rows', 'grid-2x2'}`.
  - `confidence`: `float` in `{0.25, 0.50}`.

### Catalog Plan Block Example (`backlog405.json`)
```json
{
  "template": "T73",
  "owner": "Maximum-mini-NUIAK",
  "jobPrefix": "b405-184-sahi",
  "rule": "gain-without-loss",
  "control": "control",
  "question": "On the 46 reviewed real tvOS frames at confidence 0.50, does Scale-Gated SAHI + Weighted Box Fusion recover listRow and tabItem misses from 640x640 tiles while losing 0 full-frame 640 px collectionItem detections?",
  "decision": "Support a tileLayout with scale-gated-wbf that gains at least 35 true detections with 0 lostPriorSuccesses against the 640 px control.",
  "outcomes": {
    "supported": "Integrate scale-gated tile fusion into NativeUIDetectionSession and test cold/warm latency under T12.",
    "contradicted": "Keep single-pass 640 px inference and address listRow/tabItem via training corpus expansion.",
    "inconclusive": "Complete all 4 arms and verify control parity before deciding."
  },
  "shared": {
    "inputs": {
      "labels": {"file": "Research/Experiments/detector-case-tvos-sc36.json"},
      "baseline": {"file": "reports/work/REAL-MODEL-SCORECARD-36/scorecard.json"},
      "model": {"file": "NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.pt"}
    },
    "parameters": {"confidence": 0.50}
  },
  "arms": [
    {"id": "control", "label": "Full-frame 640 px only", "parameters": {"fusionMode": "full-frame-only", "tileLayout": "none"}},
    {"id": "naive-sahi", "label": "Unfiltered 2x2 SAHI + NMS", "parameters": {"fusionMode": "unfiltered-nms", "tileLayout": "grid-2x2"}},
    {"id": "gated-bands", "label": "Scale-gated top/row bands + WBF", "parameters": {"fusionMode": "scale-gated-wbf", "tileLayout": "top-band-plus-rows"}},
    {"id": "gated-grid", "label": "Scale-gated 2x2 tiles + WBF", "parameters": {"fusionMode": "scale-gated-wbf", "tileLayout": "grid-2x2"}}
  ]
}
```

---

## 5. Implementation Plan and Reference Code

### Step-by-Step Implementation Plan
1. **Create `scripts/sahi_wbf_inference418.py`**:
   - Reuse frame staging and T42 scorecard evaluation from `detector_inference412.py` (`T43`).
   - Implement `compute_tiles(width, height, layout)` returning pixel crop windows `[x0, y0, w, h]`.
   - Run `640 px` inference on the full image and each tile, unmap tile boxes to full-frame pixel coordinates, clip boxes touching an interior tile seam unless merged, and apply `scale_gated_wbf`.
2. **Create `scripts/test_sahi_wbf_inference418.py`**:
   - Prove that `scale_gated_wbf` is mathematically guaranteed to preserve every full-frame detection of non-small classes (`lostPriorSuccesses == 0` on `collectionItem`, `sheet`, `alert`).
   - Verify coordinate unmapping accuracy and WBF clustering on synthetic overlapping boxes.

### Reference Adapter Code (`scripts/sahi_wbf_inference418.py`)
```python
"""T73: Scale-Gated Dual-Resolution SAHI + Weighted Box Fusion (WBF) detector inference."""
import research_queue as q

OUT = None
MODES = ('full-frame-only', 'unfiltered-nms', 'scale-gated-wbf')
LAYOUTS = ('none', 'top-band-plus-rows', 'grid-2x2')
SMALL_CLASSES = frozenset({'tabItem', 'listRow', 'primaryButton', 'secondaryButton', 'toggle', 'pageControl', 'label', 'badge'})


def parameters(value):
    q.require(isinstance(value, dict) and set(value) == {'fusionMode', 'tileLayout', 'confidence'}, 'sahi_parameters')
    mode, layout, conf = value['fusionMode'], value['tileLayout'], value['confidence']
    q.require(mode in MODES, 'sahi_mode_invalid')
    q.require(layout in LAYOUTS, 'sahi_layout_invalid')
    q.require((mode == 'full-frame-only') == (layout == 'none'), 'sahi_control_layout_mismatch')
    q.require(type(conf) in (int, float) and 0.05 <= conf <= 0.95, 'sahi_confidence_invalid')
    return mode, layout, float(conf)


def tile_windows(width: int, height: int, layout: str) -> list[tuple[int, int, int, int]]:
    """Return [x0, y0, w, h] high-resolution crop windows in full-frame pixels."""
    if layout == 'none':
        return []
    if layout == 'top-band-plus-rows':
        # Top tab bar band + 2 middle list-row bands
        bh = int(round(height * 0.45))
        return [(0, 0, width, int(round(height * 0.28))),
                (0, int(round(height * 0.18)), int(round(width * 0.55)), bh),
                (int(round(width * 0.45)), int(round(height * 0.18)), int(round(width * 0.55)), bh)]
    # grid-2x2 with 20% overlap
    tw, th = int(round(width * 0.60)), int(round(height * 0.60))
    return [(0, 0, tw, th), (width - tw, 0, tw, th), (0, height - th, tw, th), (width - tw, height - th, tw, th)]


def scale_gated_merge(
    full_elements: list[dict],
    tile_elements: list[dict],
    frame_area: float,
    max_small_area_frac: float = 0.045,
) -> list[dict]:
    """Preserve all full-frame detections and merge non-conflicting small/row detections from tiles."""
    from swift_fallback416 import iou
    merged = list(full_elements)
    full_boxes = [
        (e['elementType'], [e['boundingBoxPixels'][k] for k in ('x', 'y', 'width', 'height')])
        for e in full_elements
    ]
    for cand in tile_elements:
        cls = cand['elementType']
        if cls not in SMALL_CLASSES:
            continue
        b = [cand['boundingBoxPixels'][k] for k in ('x', 'y', 'width', 'height')]
        if (b[2] * b[3]) / frame_area > max_small_area_frac:
            continue
        if any(iou(b, fb) >= 0.45 for fcls, fb in full_boxes if fcls == cls):
            continue
        merged.append(cand)
        full_boxes.append((cls, b))
    return merged
```

### Resource and Time Budget
- **Preparation**: 45 min.
- **Execution**: 4 diagnostic inference jobs taking 12 s to 35 s each (within the 800 s and 100 MB diagnostic class).
- **Review**: 10 min via `backlog_pipeline.py review`.
