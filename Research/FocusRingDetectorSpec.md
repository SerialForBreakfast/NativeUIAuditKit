# FocusRingDetector — Stage 2 tvOS Focus Classifier

**Status:** Phase B harvest + fdr001 train complete (2026-09-18). Torch test 270/270. No shipped `.mlmodelc`.  
**Audience:** NativeUIAuditKit maintainers  
**Related:** [`NativeUIElementDetection.md`](NativeUIElementDetection.md), [`ExperimentLog.md`](ExperimentLog.md) Run FDR-001, [`tvOSTrainingStrategy.md`](tvOSTrainingStrategy.md)

Stage 2 sits *after* YOLO. YOLO answers *what is on screen*; FocusRingDetector answers *which crop is focused*. YOLO weights and the detection pipeline are independent of this classifier.

```
Screenshot (1920×1080)
  └─► YOLO11 (Stage 1): focusable element boxes
        └─► expand 16%, crop 256×256 → FocusRingDetector
              ├─ is_focused_prob ≥ 0.85  →  isFocused = true
              ├─ 0.70 ≤ prob < 0.85      →  isAmbiguousFocus = true, isFocused = nil
              └─ prob < 0.70             →  isFocused = false
```

`NativeUIDetectionRequest.resolveTVOSFocus` (brightness / geometry heuristic) remains the fallback when `FocusRingDetector.mlmodelc` is absent or `useFocusClassifier == false`.

---

## 1. Architecture choice (v1.0)

| Decision | Choice | Why |
|---|---|---|
| Backbone | MobileNetV4-Conv-Small (vendored `scripts/focus_ring_backbone.py`) | ≤5 MB FP16 CoreML budget; proven ANE path. Matches timm 1.0.29 `mobilenetv4_conv_small` topology, trained from scratch |
| Alternative deferred | FastViT-T8 | Attention ANE compatibility less certain |
| Framework | PyTorch only (no `import timm` — BP-47) | `.venv-yolo` torch; timm package init hangs |
| Export | ONNX → coremltools FP16 `.mlpackage` | Same chain as YOLO exports; compile to `.mlmodelc` for the models package |
| Dataset v0.1 | Plan A: harvest real TVTestRigFixture pairs (1,500–2,500) | `POST /v1/scene/render` (FIX-SYNTH-06) does not exist yet |
| Dataset v1.0 | 6,000+ pairs once RPC or Plan A scale completes | Quality gates below |

Do not fold this head into the YOLO detector. Extra heads scramble the frozen 41-class ID map (BP-28).

---

## 2. Input contract

| Field | Value |
|---|---|
| Spatial | 256×256 |
| Layout | BGRA8 `CVPixelBuffer` at inference; training uses RGB `[0, 1]` |
| Color | sRGB |
| Normalization | ÷255 (no ImageNet mean/std) |
| Expansion | 16% on each side of the YOLO box, then clamp to screenshot bounds, then scale to 256×256 |

`FocusRingClassifier.makeCrop(from:bbox:expansionFactor:)` is the Swift implementation of this crop.

---

## 3. Output contract

Both outputs are `Float32` tensors of shape `(1,)`:

| Name | Meaning |
|---|---|
| `is_focused_prob` | Sigmoid probability that the crop shows active tvOS focus |
| `confidence` | `abs(is_focused_prob - 0.5) * 2` — distance from the decision boundary |

Thresholds are **not** baked into weights. They live in CoreML `user_defined_metadata` with Swift fallbacks:

| Key | Default |
|---|---|
| `focusThreshold` | `0.85` |
| `ambiguityThreshold` | `0.70` |

Required metadata:

| Key | Value |
|---|---|
| `modelID` | `focus-ring-detector-v1.0` |
| `versionString` | `1.0.0` |
| `short_description` | Binary classifier: tvOS UI element focus state |
| `author` | NativeUIAuditKit |

Package size gate: FP16 `.mlpackage` **≤ 5.0 MB**.

---

## 4. Dataset

Crops and the manifest live **outside** this package (filesystem-boundary + dataset location rules):

```
NativeUIAuditKit-Dataset/focus_ring/
  crops/
  focus_dataset_manifest.json
```

Default harvest input is the in-tree fixture cache `dataset/tvos_fixture_captures/` (gitignored). Harvest never lists `dataset/dataset/train`.

### Manifest entry

```json
{
  "pair_id": "gridMatrix_0042",
  "recipe_seed": 42,
  "fixture_scene": "gridMatrix",
  "theme": "system",
  "element_type": "collectionItem",
  "unfocused_crop": "crops/gridMatrix_0042_unfocused.png",
  "focused_crop": "crops/gridMatrix_0042_focused.png",
  "bbox_normalized": [0.12, 0.33, 0.28, 0.22],
  "split": "train"
}
```

`split` is assigned from `recipe_seed` (not from filename) so a focused/unfocused pair cannot straddle train/test.

Labels come from, in order:

1. Sidecar `elements[].state.isFocused` or `elements[].isFocused` (Schema v1.0 ground truth)
2. YOLO sidecar `isFocused` when present
3. Otherwise the crop is unlabeled and excluded from train/val/test unless `--include-unlabeled`

Current `dataset/tvos_fixture_captures/*.json` files have empty `elements` arrays. Phase A extraction therefore reports unlabeled counts; live `--live` capture (Phase B) is required for paired labels.

---

## 5. Quality gates (held-out test)

| Gate | Required |
|---|---|
| Accuracy | ≥ 99.0% |
| FPR (unfocused) | ≤ 0.5% |
| FNR (focused) | ≤ 1.0% |
| Precision @ 0.85 | ≥ 0.98 |
| Recall @ 0.85 | ≥ 0.98 |
| Hard-negative FPR (`light` + `highContrast`, `imageView` / `collectionItem`) | ≤ 0.5% independently |

Do not copy `.mlmodelc` into `NativeUIAuditKitModels` resources until these gates pass.

---

## 6. Training

| Parameter | Value |
|---|---|
| Model | `mobilenetv4_conv_small` |
| Input | 256 |
| Classes | 1 (sigmoid) |
| Batch | 64 |
| Epochs | 30 |
| LR | 3e-4 |
| Augment (train only) | HFlip 0.5, ColorJitter, ±5° rotation, GaussianBlur p=0.3 |
| Forbidden | Vertical flip (tvOS glow is orientation-sensitive) |

Checkpoints: `NativeUITrainer/focus_ring_runs/<run_id>/weights/best.pt`

Scripts:

```bash
.venv-yolo/bin/python scripts/harvest_focus_pairs.py --dry-run
.venv-yolo/bin/python scripts/train_focus_ring_detector.py --dry-run
.venv-coreml/bin/python scripts/export_focus_ring_coreml.py --weights NativeUITrainer/focus_ring_runs/<run>/weights/best.pt
.venv-yolo/bin/python scripts/eval_focus_ring_detector.py --mlpackage NativeUITrainer/focus_ring_runs/<run>/export/FocusRingDetector.mlpackage
```

---

## 7. Swift integration

- `FocusRingClassifier` — crop + `MLModel` predict
- `NativeUIDetectionConfiguration.useFocusClassifier` — default `true`; heuristic used when the compiled model is missing
- `NativeUIModelAsset.focusRingDetectorURL` / `loadFocusRingDetector()` — return `nil` when the resource is absent (never `fatalError`)
- Compiled `FocusRingDetector.mlmodelc` is **not** committed until gates pass. When an uncompiled `.mlpackage` is dropped next to the other model sources, add it to the NativeUIAuditKitModels target `exclude:` list (same pattern as `NativeUIModel_tvOS.mlpackage`). Do not add `.copy("Resources/FocusRingDetector.mlmodelc")` until the compiled resource exists — SPM fails planning if the path is missing.
