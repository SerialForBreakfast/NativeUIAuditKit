---
name: nativeui-model-workflow
description: >-
  Use this skill when training, evaluating, exporting, or diagnosing YOLO11
  and CoreML models in NativeUIAuditKit.
---

# NativeUIAuditKit Model Training & Evaluation Workflow

Current snapshot: [`Research/CurrentState.md`](../../../Research/CurrentState.md). Remaining work: [`Tasks.md`](../../../Tasks.md). Archive: [`CompletedTasks.md`](../../../CompletedTasks.md).

This skill covers the end-to-end workflow for training, evaluating, exporting, and debugging object detection models in NativeUIAuditKit across iOS and tvOS (YOLO11) plus FocusRing (MobileNetV4, not YOLO).

---

## Environment & Filesystem Boundary Setup

All training and evaluation runs must strictly respect package filesystem boundaries:

```python
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Confine all third-party caches to the package directory
os_env_defaults = {
    "YOLO_CONFIG_DIR": str(PROJECT_ROOT / "NativeUITrainer" / ".ultralytics"),
    "MPLCONFIGDIR": str(PROJECT_ROOT / "NativeUITrainer" / ".mplconfig"),
    "TORCH_HOME": str(PROJECT_ROOT / "NativeUITrainer" / ".torch"),
}
for k, v in os_env_defaults.items():
    os.environ[k] = v
    Path(v).mkdir(parents=True, exist_ok=True)
```

**Python Virtual Environment:**
Always use `.venv-yolo/bin/python` from the package root:
```bash
.venv-yolo/bin/python --version
```

---

## Training Pipeline Commands

### 1. Export Native JSON Sidecars to YOLO / COCO Format
```bash
# Exports sidecars to YOLO-formatted dataset with family-based holdouts
.venv-yolo/bin/python scripts/export_coco.py --dataset ../NativeUIAuditKit-Dataset
```

### 2. Compute Class Weights
```bash
.venv-yolo/bin/python scripts/compute_class_weights.py
```

### 3. Dry-Run Verification
Always run a dry run before launching an overnight or long training job:
```bash
.venv-yolo/bin/python scripts/train_ios_model.py --dry-run
```

### 4. Full Training Execution (Backgrounded)
```bash
nohup .venv-yolo/bin/python scripts/train_ios_model.py >> NativeUITrainer/training.log 2>&1 &
echo "PID: $!"
```

To monitor progress:
```bash
tail -30 NativeUITrainer/training.log
```

---

## Critical Inference & Evaluation Rules

### 1. Always Use `.scaleFill` for Portrait / Landscape Screenshots (BP-25)
- **Rule:** Set `request.imageCropAndScaleOption = .scaleFill` on `VNCoreMLRequest`.
- **Why:** `.scaleFit` pads the image with black bars. For non-square aspect ratios (e.g. 9:16 portrait or 16:9 tvOS), this causes ~2× coordinate blowup → IoU drops below 0.5 → all detections are false positives.

### 2. Never Use `MLObjectDetector.evaluation(on:)` (BP-25)
- Apple's built-in Create ML evaluation API has a hardcoded `.scaleFit` bug that yields mAP ≈ 0 for portrait screenshots.
- **Always use `swift scripts/eval_map.swift`** for full dataset mAP evaluation.

### 3. Coordinate System Conversions (BP-10)
- **Vision Coordinates:** Origin at bottom-left, normalized `[0, 1]`.
- **Create ML / YOLO:** Origin at top-left, normalized center `(cx, cy, w, h)`.
- **Conversion:**
  ```python
  cx = vn_x + vn_w / 2.0
  cy = 1.0 - vn_y - vn_h / 2.0
  ```

---

## Exporting & Packaging CoreML Weights

When a training run converges and passes holdout gates:

1. **Export to CoreML:**
   ```bash
   .venv-yolo/bin/python scripts/export_yolo_coreml.py --weights NativeUITrainer/yolo_runs/<run_id>/weights/best.pt
   ```
2. **Model Package Location:**
   - Promote a compiled `.mlmodelc` into `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/` only after holdout gates pass.
   - iOS: `NativeUIDetector_v2.mlmodelc`. tvOS: `NativeUIModel_tvOS.mlmodelc`. FocusRing: `FocusRingDetector.mlmodelc`.
   - Never commit raw YOLO `.pt` checkpoints or unpromoted `.mlpackage` dumps to the core repo.

---

## What Works vs What Doesn't

| What Works | What Fails (Do Not Repeat) |
|---|---|
| Setting cache environment variables (`MPLCONFIGDIR`, `TORCH_HOME`). | Letting Matplotlib or Torch write to `~/.matplotlib` or `/tmp`. |
| Running `scripts/eval_map.swift` with `.scaleFill`. | Using `MLObjectDetector.evaluation(on:)` (returns mAP≈0). |
| Logging every run in `Research/ExperimentLog.md`. | Running ad-hoc training runs without recording configuration and outcome. |
| Using `.venv-yolo/bin/python` directly. | Invoking global system python or creating unpinned venvs. |
| Running smoke tests with `swift test` before changes. | Committing code without running local tests. |
