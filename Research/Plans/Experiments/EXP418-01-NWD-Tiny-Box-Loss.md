# EXP418-01 — Normalized Wasserstein Distance (NWD) Loss for Tiny UI Controls (`B405-229` / Template `T67`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `iOS detection` (`IOS`). Priority: `P1`.
Parent task: `TASK-6a-10`. Template: `T67` (`nwd_detector_train418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [Backlog410.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Backlog410.md) (`B405-011`, `B405-115`, `B405-116`), `Maximum-mini-NUIAK` measured Run 013 against Run 009 on 2,000 withheld iOS frames (17,862 labels):
- `pageControl` achieves 0 detections at IoU 0.5 across all confidence thresholds from `0.05` to `0.40`. Near-miss boxes appear at low confidence, which proves the failure is bounding-box regression fit rather than objectness blindness.
- Run 013 loses 1,305 `label` detections compared to Run 009. Small labels hold 74 % of all losses, middle-right labels lose 400 of 800, and top-left labels lose 97 of 100.

### SOTA Method: Normalized Wasserstein Distance (NWD)
Standard Complete IoU (CIoU) is highly sensitive to tiny spatial shifts on small objects. For an 8 pt tall `pageControl` or a 10 pt micro-label at `640 px` model scale, a 2 px center offset drops IoU from `1.00` to below `0.15`. This sudden drop causes two failures in YOLO11n:
1. The Task-Aligned Assigner (TAL) rejects positive anchors for tiny controls because the alignment metric depends on $\text{IoU}^\beta$.
2. Box regression gradients become unstable when boxes have near-zero overlap.

**Normalized Wasserstein Distance (NWD)** (Wang et al., *A Normalized Gaussian Wasserstein Distance for Tiny Object Detection*) models bounding boxes $A = (cx_a, cy_a, w_a, h_a)$ and $B = (cx_b, cy_b, w_b, h_b)$ as 2D Gaussian distributions $\mathcal{N}(\mu_a, \Sigma_a)$ and $\mathcal{N}(\mu_b, \Sigma_b)$. The second-order Wasserstein distance is:

$$W_2^2(\mathcal{N}_a, \mathcal{N}_b) = \| (cx_a, cy_a, \tfrac{w_a}{2}, \tfrac{h_a}{2})^\top - (cx_b, cy_b, \tfrac{w_b}{2}, \tfrac{h_b}{2})^\top \|_2^2$$

The normalized similarity metric is:

$$\text{NWD}(A, B) = \exp\left( -\frac{\sqrt{W_2^2(\mathcal{N}_a, \mathcal{N}_b)}}{C} \right) \in (0, 1]$$

Unlike IoU, $\text{NWD}(A, B)$ is smooth, scale-invariant for small boxes, and provides non-zero gradients even when two boxes do not overlap.

---

## 2. Controlled Test and Decision Rules

### Hypothesis
Blending NWD with CIoU (`(1 - w) * L_CIoU + w * L_NWD`) in both the Task-Aligned Assigner and box regression loss for boxes with normalized area `< 0.01` recovers `pageControl` and small-label detections without degrading medium or large control classes.

### Experimental Arms
All arms use the same initialization (`NativeUITrainer/yolo_runs/run_013/weights/best.pt` or common 13-class / 41-class starting weights), seed `371`, 30 epochs, `640 px` image size, and pinned training/calibration membership. Only `nwdWeight` changes:
1. `control` (`nwdWeight = 0.00`, `scaleConstant = 12.0`): Pure CIoU baseline. Must reproduce the standard YOLO11n box loss exactly.
2. `nwd-025` (`nwdWeight = 0.25`, `scaleConstant = 12.0`): 25 % NWD blend on small targets.
3. `nwd-050` (`nwdWeight = 0.50`, `scaleConstant = 12.0`): Equal 50 % NWD and 50 % CIoU blend on small targets.
4. `nwd-075` (`nwdWeight = 0.75`, `scaleConstant = 12.0`): 75 % NWD blend on small targets.

### Mechanical Decision Rule (`gain-without-loss`)
- **Supported**: At least one NWD arm recovers `>= 25` `pageControl` instances and `>= 150` small-label instances on the calibration/development split at IoU `0.5` and confidence `0.25`, with `0` net AP loss (`<= 0.002` jitter tolerance) on medium and large classes (`alert`, `navigationBar`, `sheet`, `collectionItem`).
- **Contradicted**: No NWD arm improves `pageControl` or small-label recall at IoU `0.5`, or every NWD arm degrades large-box localization IoU.
- **Inconclusive**: Training stops early, epoch history is incomplete, or calibration scorecard evaluation fails.

---

## 3. What This Tells TTR and NUIAK

- **If Supported**:
  - `Maximum-mini-NUIAK` proves that `pageControl` and small-label misses come from IoU assignment starvation rather than insufficient image resolution.
  - `Maximum-mini-NUIAK` adopts the winning `nwdWeight` in the Phase 6a detector recipe. This keeps inference at `640 px` on the Apple Neural Engine without the latency cost of `1280 px` inputs.
  - `Sillycon-TTR` and `Maximum-mini-TTR` gain reliable detection of small status badges, pagination dots, and compact top-left navigation labels.
- **If Contradicted**:
  - `Maximum-mini-NUIAK` rules out box-loss assignment starvation as the cause of `pageControl` and small-label failures.
  - Follow-up work pivots immediately to `EXP418-07` (`T73` Scale-Gated Dual-Resolution SAHI) and `GeneratorRunner` intrinsic `pageControl` dot-group annotation review (`B405-115`).

---

## 4. Template `T67` Contract

### Entry in `scripts/hcf_templates395.py`
```python
'T67': (
    {'configuration', 'initialization', 'membership'},
    {'nwdWeight', 'scaleConstant', 'seed'},
    'nwd_detector_train418.run',
    'training',
    'training',
),
```

### Inputs and Parameters
- **Inputs**:
  - `configuration`: Pinned JSON training configuration (`nwd-detector-config-v1`).
  - `initialization`: Pinned starting `.pt` checkpoint.
  - `membership`: Pinned dataset manifest with frozen `train`, `calibration`, and `development` roles.
- **Parameters**:
  - `nwdWeight`: `float` in `{0.0, 0.25, 0.5, 0.75}`.
  - `scaleConstant`: `float` in `{8.0, 12.0, 16.0}` (pixel scale normalization constant $C$).
  - `seed`: `int` in `{371, 372, 373}`.

### Catalog Plan Block Example (`backlog405.json`)
```json
{
  "template": "T67",
  "owner": "Maximum-mini-NUIAK",
  "jobPrefix": "b405-178-nwd",
  "rule": "gain-without-loss",
  "control": "control",
  "question": "On the pinned iOS detector split at 640 px, does blending Normalized Wasserstein Distance (NWD) into box assignment and regression recover pageControl and small-label detections without losing medium or large controls?",
  "decision": "Support the lowest nwdWeight that gains at least 25 pageControl and 150 small-label detections at IoU 0.5 and confidence 0.25 with 0 lost successes on medium and large controls.",
  "outcomes": {
    "supported": "Adopt the winning nwdWeight in the iOS and tvOS detector trainer and run seeds 372 and 373.",
    "contradicted": "Keep pure CIoU (nwdWeight 0.0) and test T73 scale-gated SAHI for small controls.",
    "inconclusive": "Complete all 30 epochs and per-case T42 evaluation on every arm before deciding."
  },
  "shared": {
    "inputs": {
      "configuration": {"file": "Research/ResearchSpecs/EXP418/t55-nwd-config.json"},
      "initialization": {"file": "NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.pt"},
      "membership": {"file": "Research/Experiments/detector-case-ios-r013.json"}
    },
    "parameters": {
      "scaleConstant": 12.0,
      "seed": 371
    }
  },
  "arms": [
    {"id": "control", "label": "CIoU control (nwdWeight 0.0)", "parameters": {"nwdWeight": 0.0}},
    {"id": "nwd-025", "label": "25% NWD + 75% CIoU", "parameters": {"nwdWeight": 0.25}},
    {"id": "nwd-050", "label": "50% NWD + 50% CIoU", "parameters": {"nwdWeight": 0.50}},
    {"id": "nwd-075", "label": "75% NWD + 25% CIoU", "parameters": {"nwdWeight": 0.75}}
  ]
}
```

---

## 5. Implementation Plan and Reference Code

### Step-by-Step Implementation Plan
1. **Create `scripts/nwd_detector_train418.py`**:
   - Implement `parameters(value)` to validate `nwdWeight`, `scaleConstant`, and `seed`.
   - Implement `nwd_box_similarity(box1_xyxy, box2_xyxy, scale_constant)` in PyTorch with numerical stability (`eps = 1e-7`).
   - Subclass the resident Ultralytics v8DetectionLoss / BboxLoss so small ground-truth boxes (`area_norm <= 0.01`) blend `(1 - nwdWeight) * ciou_loss + nwdWeight * (1.0 - nwd)`.
   - After 30 epochs, score `final.pt` against the pinned baseline using `detector_case_match411` (`T42`) and write `fit.json`, `history.json`, `final.pt`, `benchmark_summary.json`, and `artifact-receipt.json`.
2. **Create `scripts/test_nwd_detector_train418.py`**:
   - Verify that `nwdWeight = 0.0` produces byte-identical loss values and gradients to standard CIoU.
   - Verify that non-overlapping tiny boxes (`4x4 px` separated by `6 px`) have non-zero gradients under NWD while standard IoU returns `0.0`.
   - Run an isolated queue test verifying `check_training_report` compliance.
3. **Register Contract at Idle Boundary**:
   - Check `/api/health` on the research dashboard to confirm no job is running.
   - Add `'T67'` to `CONTRACTS` in [hcf_templates395.py](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/scripts/hcf_templates395.py) and `validate_plan` in [backlog_pipeline.py](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/scripts/backlog_pipeline.py).

### Reference Adapter Code (`scripts/nwd_detector_train418.py`)
```python
"""T67: train YOLO11n with blended CIoU + Normalized Wasserstein Distance (NWD) loss for tiny UI controls."""
import math
import torch
import research_queue as q
from template_inputs398 import checked
from template_adapters395 import document, resolve_inputs

OUT = None
WEIGHTS = (0.0, 0.25, 0.50, 0.75)
SCALES = (8.0, 12.0, 16.0)
SEEDS = (371, 372, 373)


def parameters(value):
    """Validate and return (nwdWeight, scaleConstant, seed)."""
    q.require(isinstance(value, dict) and set(value) == {'nwdWeight', 'scaleConstant', 'seed'}, 'nwd_parameters')
    w, c, seed = value['nwdWeight'], value['scaleConstant'], value['seed']
    q.require(w in WEIGHTS, 'nwd_weight_invalid')
    q.require(c in SCALES, 'nwd_scale_invalid')
    q.require(seed in SEEDS, 'nwd_seed_invalid')
    return float(w), float(c), int(seed)


def xyxy_to_cxcywh(boxes: torch.Tensor) -> torch.Tensor:
    """Convert [..., 4] (x1, y1, x2, y2) boxes to (cx, cy, w, h)."""
    x1, y1, x2, y2 = boxes.unbind(dim=-1)
    w = (x2 - x1).clamp(min=1e-6)
    h = (y2 - y1).clamp(min=1e-6)
    return torch.stack([(x1 + x2) * 0.5, (y1 + y2) * 0.5, w, h], dim=-1)


def nwd_similarity(pred_xyxy: torch.Tensor, target_xyxy: torch.Tensor, scale_c: float = 12.0) -> torch.Tensor:
    """Compute 2D Gaussian Wasserstein similarity in (0, 1] between predicted and target boxes."""
    p = xyxy_to_cxcywh(pred_xyxy)
    t = xyxy_to_cxcywh(target_xyxy)
    center_sq = (p[..., :2] - t[..., :2]).pow(2).sum(dim=-1)
    wh_sq = ((p[..., 2:] - t[..., 2:]) * 0.5).pow(2).sum(dim=-1)
    w2_dist = torch.sqrt(center_sq + wh_sq + 1e-7)
    return torch.exp(-w2_dist / scale_c)


def blended_ciou_nwd_loss(
    ciou: torch.Tensor,
    pred_xyxy: torch.Tensor,
    target_xyxy: torch.Tensor,
    nwd_weight: float,
    scale_c: float = 12.0,
    small_area_px: float = 1024.0,
) -> torch.Tensor:
    """Blend CIoU loss and NWD loss for small targets while keeping pure CIoU on large targets."""
    ciou_loss = 1.0 - ciou
    if nwd_weight <= 0.0:
        return ciou_loss
    t_wh = xyxy_to_cxcywh(target_xyxy)[..., 2:]
    area = t_wh[..., 0] * t_wh[..., 1]
    is_small = (area <= small_area_px).float()
    eff_w = nwd_weight * is_small
    nwd_loss = 1.0 - nwd_similarity(pred_xyxy, target_xyxy, scale_c=scale_c)
    return (1.0 - eff_w) * ciou_loss + eff_w * nwd_loss
```

### Resource and Time Budget
- **Preparation**: 45 min to 90 min.
- **Execution**: 4 training jobs at 1,800 s ceiling and 2 GiB output cap each (estimated 18 min to 25 min per run on Apple Silicon MPS).
- **Review**: 15 min via `backlog_pipeline.py review`.
