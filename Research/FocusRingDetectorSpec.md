# FocusRingDetector — Stage 2 tvOS Focus Classifier

**Status:** v0.1 shipped 2026-09-18. FDR-001 trained, CoreML 4.80 MB, `FocusRingDetector.mlmodelc` bundled. Hard-neg n=0 (FOCUS-DET-05).  
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
| Export | `torch.jit.trace` → coremltools 9.0 FP16 `.mlpackage` | No ONNX package in the train venv. Compile to `.mlmodelc` for `NativeUIAuditKitModels` |
| Dataset v0.1 | 1,500 Office TVTestRigFixture pairs (harvested 2026-09-17) | `POST /v1/scene/render` (FIX-SYNTH-06) does not exist; Plan A live harvest |
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

**FR-A metadata reconciliation (2026-09-19):** the bundled resource metadata
matches this table exactly: `modelID` is `focus-ring-detector-v1.0` and
`versionString` is `1.0.0`. FDR-001 is the training-run label, not a model
version. No model resource or qualification claim changes here.

Package size gate: FP16 `.mlpackage` **≤ 5.0 MB**.

---

## 4. Dataset

Crops and the manifest are gitignored. v0.1 Office harvest wrote in-tree:

```
dataset/focus_ring/
  crops/
  focus_dataset_manifest.json
```

The harvest script default remains `NativeUIAuditKit-Dataset/focus_ring/` (outside this package). Do not commit either tree.

Default harvest *input* is the in-tree fixture cache `dataset/tvos_fixture_captures/` (gitignored). Harvest never lists `dataset/dataset/train`.

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

### Separate simulator visual-data milestone

[SIM-DATA-01–05](Plans/SimulatorDatasets.md) defines an independent local simulator
dataset lane. Its visual-only pairs do not require the semantic alignment matrix or
`--require-alignment-matrix` below. Present alignment metadata must still validate.
Simulator-only eligibility does not close physical FR-B/FR-C, qualify Apple TV shader
behavior, authorize training, or change model promotion gates.

### ADR-0007 alignment metadata (FR-A / FR-B)

The visual pair contract remains independent from accessibility semantics. A pair may
omit `alignment` and remain a visual-model example. Every pair deliberately collected
for VoiceOver/navigation policy evaluation instead includes this additive object, which
conforms to [`schemas/focus-ring-alignment.v1.json`](schemas/focus-ring-alignment.v1.json):

```json
"alignment": {
  "version": "1.0",
  "source": "fixtureGroundTruth",
  "interactionMode": "voiceOverExploration",
  "expectedRelation": "expectedDecoupled",
  "navigationFocusElementID": "grid-2-1",
  "voiceOverFocusElementID": "grid-3-1"
}
```

`source` is `fixtureGroundTruth` or `trustedLiveMetadata`; captions, model predictions,
and guessed element IDs are invalid. `notAssessable` uses `interactionMode: "unknown"`,
no source, and a null VoiceOver target. It abstains rather than reporting a failure.
FR-B must validate the complete prospective manifest with:

```bash
.venv-yolo/bin/python scripts/validate_focus_ring_readiness.py \
  --manifest dataset/focus_ring/focus_dataset_manifest.json \
  --require-alignment-matrix
```

That command requires all five [ADR-0007](ADR-0007-VoiceOver-Navigation-Focus-Alignment.md)
matrix rows: normal directional alignment, VoiceOver exploration, VoiceOver traversal,
an intentional fixture fault, and missing producer state. It validates capture metadata
only; it does not train, operate a device, or declare a visual model qualified.

Labels come from, in order:

1. Sidecar `elements[].state.isFocused` or `elements[].isFocused` (Schema v1.0 ground truth)
2. YOLO sidecar `isFocused` when present
3. Otherwise the crop is unlabeled and excluded from train/val/test unless `--include-unlabeled`

Current `dataset/tvos_fixture_captures/*.json` files have empty `elements` arrays, so Phase A extraction reports unlabeled counts. Phase B `--live` harvest (Office, 2026-09-17) produced **1,500** labeled pairs in `dataset/focus_ring/` (train 1,201 / val 164 / test 135; `theme=dark` only).

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

v0.1 shipped after the five torch held-out gates passed (270/270). The hard-negative gate was **vacuous** (`n=0`, all harvest `theme=dark`). Do not replace the bundled `.mlmodelc` until FOCUS-DET-05 records a non-vacuous hard-neg FPR ≤ 0.5%.

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
| Augment (v0.1 train) | HFlip 0.5 only |
| Augment (planned, not in FDR-001) | ColorJitter, ±5° rotation, GaussianBlur p=0.3 |
| Forbidden | Vertical flip (tvOS glow is orientation-sensitive) |

Checkpoints: `NativeUITrainer/focus_ring_runs/<run_id>/weights/best.pt`

Scripts:

```bash
.venv-yolo/bin/python scripts/harvest_focus_pairs.py --dry-run
.venv-yolo/bin/python scripts/train_focus_ring_detector.py --dry-run
python scripts/export_focus_ring_coreml.py \
    --weights NativeUITrainer/focus_ring_runs/fdr001/weights/best.pt
.venv-yolo/bin/python scripts/eval_focus_ring_detector.py \
    --weights NativeUITrainer/focus_ring_runs/fdr001/weights/best.pt
```

---

## 7. Swift integration

## VoiceOver/navigation alignment boundary

`FocusRingClassifier` answers only whether a candidate crop has a visible focus
treatment. It does not infer VoiceOver cursor identity, interaction mode, or whether
VoiceOver and directional-navigation focus should agree. Those are source-backed policy
inputs defined by [ADR-0007](ADR-0007-VoiceOver-Navigation-Focus-Alignment.md). Expected
exploration/traversal decoupling must not become a focus-classifier false positive or an
accessibility finding.

- `FocusRingClassifier` — crop + `MLModel` predict
- `NativeUIDetectionConfiguration.useFocusClassifier` — default `true`; heuristic used when the compiled model is missing or the flag is `false`
- `NativeUIModelAsset.focusRingDetectorURL` / `loadFocusRingDetector()` — return `nil` when the resource is stripped (never `fatalError`)
- v0.1 compiled `FocusRingDetector.mlmodelc` **is** bundled via `.copy("Resources/FocusRingDetector.mlmodelc")`. Tests require URL, load, metadata thresholds, and a unit-interval `classify` on `tvos_home_screen.png`. Keep uncompiled `.mlpackage` sources in the NativeUIAuditKitModels `exclude:` list (same pattern as `NativeUIModel_tvOS.mlpackage`).
