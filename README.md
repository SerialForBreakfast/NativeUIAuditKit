# NativeUIAuditKit

A portable Swift package for detecting native Apple platform UI elements in screenshot PNGs, designed as a drop-in complement to [ScreenAuditKit](../ScreenAuditKit/).

**Current state:** Phase 6 (5-class iOS model) complete. A trained `NativeUIDetector_v1.mlpackage` is live in `NativeUIAuditKitModels/`. The eval pipeline achieves mAP@0.5 = **0.756** across 1,394 validation images, with all five gated classes passing DS-G5 (AP@0.5 ≥ 0.50) and DS-G6 (mAP ≥ 0.70). Physical device latency testing and withheld-template generalization testing are the immediate next steps before declaring Phase 6 complete.

---

## What This Package Does

NativeUIAuditKit builds a custom Vision-style request backed by CoreML object detectors trained on synthetic native Apple UIs. Given a screenshot PNG, it returns structured `NativeUIElementObservation` values with:

- **Semantic element type** — one of ~41 stable role strings: `primaryButton`, `navigationBar`, `toggle`, `dynamicIsland`, etc.
- **Accurate bounding boxes** — in Vision-normalized, pixel, and point coordinate systems
- **Visible text** — from `VNRecognizeTextRequest` OCR fusion (Phase 7, not yet wired)
- **Audit issues** — truncation, clipping, overlapping controls, insufficient touch target, Dynamic Type overflow
- **Device / OS inference** — ranked candidates from visual chrome signals (orphan PNG mode)

**Two operating modes:**
- **Sidecar mode** — highest accuracy; hierarchy metadata exported at capture time is paired with the PNG
- **Pixel-only mode** — moderate accuracy; works on orphan PNGs with no metadata

**Three platform-specific models (iOS model trained; tvOS/macOS planned):**
- `NativeUIModel_iOS` — iOS + iPadOS (shared visual language) — **5-class prototype trained ✓**
- `NativeUIModel_tvOS` — tvOS (focus state paradigm, tab bar at screen top)
- `NativeUIModel_macOS` — macOS (window chrome, NSToolbar, AppKit layout)

---

## Model Performance (NativeUIDetector_v1, trained 2026-05-28)

5-class iOS prototype. Evaluated on 1,394 held-out validation images using a per-class-routed inference pipeline with cross-class conflict suppression.

| Class | AP@0.5 | GT | TP | Pred | Notes |
|---|---|---|---|---|---|
| alert | **1.000** | 40 | 40 | 40 | Full-image pass only |
| toggle | **0.821** | 1,074 | 1,019 | 1,232 | Strip pass, conf ≥ 0.95 |
| navigationBar | **0.775** | 1,186 | 1,176 | 1,508 | Strip pass |
| primaryButton | **0.680** | 761 | 687 | 1,185 | Full-image + strip |
| textField | **0.505** | 315 | 268 | 609 | Strip pass + cross-class suppression |
| **mAP@0.5** | **0.756** | | | | DS-G5 ✓ DS-G6 ✓ |

**Training configuration:** transferLearning (objectPrint revision:1), 25,000 iterations, batch 32, 22%-height strip tiling at 50% overlap, 20,632 training entries (18,563 original + 2,069 UIKitToggleForm hard-negative augmentation).

**Inference pipeline:** per-class pass routing (alert → full-image only; navBar/textField/toggle → strip pass; primaryButton → both), cross-class conflict suppression (textField suppressed if IoU > 0.30 with toggle or primaryButton), NMS IoU threshold 0.30.

Full experiment history: [`Research/ExperimentLog.md`](Research/ExperimentLog.md)

---

## Requirements

- macOS 15+, Xcode 26+
- Swift 6.0+
- iOS 17+ simulator (for `GeneratorRunner` test target)
- Python 3 + Pillow (for `scripts/augment_createml_export.py`)

No external Swift dependencies. Vision, CoreML, CoreGraphics, UIKit only.

---

## Build & Test

**SPM package (macOS):**
```bash
swift build
swift test
```

**Generator smoke test (iOS Simulator):**
```bash
scripts/run-kitchen-sink-test.sh
# Runs KitchenSinkValidationTest, extracts annotated PNGs to .build/debug-output/attachments/
```

**Full dataset generation (iOS Simulator):**
```bash
xcodebuild test \
  -project GeneratorRunner/GeneratorRunner.xcodeproj \
  -scheme GeneratorRunnerTests \
  -destination "platform=iOS Simulator,name=iPhone 17 Pro" \
  -only-testing GeneratorRunnerTests/GenerateDatasetTests
# Writes PNG + JSON pairs to the simulator Documents/dataset/ directory
```

**Train (run in Terminal — ~10h, do not run via agent harness):**
```bash
swift run -c release NativeUITrainer \
  --dataset <simulator-dataset-root> \
  --output NativeUIAuditKitModels/Sources/NativeUIAuditKitModels \
  [--skip-export]   # use when source train/ PNGs have been deleted after a prior run
  2>&1 | tee NativeUITrainer/training.log
```

**Evaluate trained model:**
```bash
swift scripts/eval_map.swift
# Writes reports/eval_results.json
```

**Augment an existing createml_export/ with new images (without full re-export):**
```bash
python3 scripts/augment_createml_export.py \
  --source <new-images-simulator-dataset-root> \
  --target <training-simulator-dataset-root> \
  --template-family UIKitToggleForm \
  --strip-fraction 0.22
```

---

## Package Structure

```
NativeUIAuditKit/
├── Package.swift
├── README.md
├── Tasks.md                               ← phase-structured task list and roadmap
├── AGENTS.md                              ← agent handoff notes
├── Research/
│   ├── ExperimentLog.md                   ← chronological training run history (Runs 001–005)
│   ├── NativeUIElementDetection.md        ← architecture, API design, training approach
│   ├── TrainingDataStrategy.md            ← dataset design, bias prevention, platform coverage
│   ├── BestPractices.md                   ← lessons learned (BP-01 through BP-26+)
│   ├── TrainingRunbook.md                 ← step-by-step training procedure and pre-flight checks
│   ├── LessonsLearned.md                  ← extended write-up of major discoveries
│   ├── OCRFusionPolicy.md                 ← OCR fusion rules and truncation detection
│   └── schemas/
│       ├── annotation.schema.json         ← versioned annotation schema (v1.0)
│       └── category_map.json              ← element type → integer ID for COCO export
├── Sources/
│   └── NativeUIAuditKit/
│       ├── Detection/NativeUIDetectionRequest.swift
│       └── Models/NativeUIElementObservation.swift
├── Tests/
│   └── NativeUIAuditKitTests/
├── NativeUIAuditKitModels/                ← trained model (gitignored binaries)
│   └── Sources/NativeUIAuditKitModels/
│       ├── NativeUIDetector_v1.mlpackage.mlmodel   ← active model (trained 2026-05-28)
│       ├── training_config.json
│       └── ModelRegistry.swift
├── NativeUIDatasetGenerator/
│   ├── Sources/                           ← macOS orchestrator
│   │   ├── SeededRNG.swift
│   │   ├── ContentCorpus.swift
│   │   ├── GeneratorConfig.swift          ← OSVisualProfile, GeneratorRunConfig
│   │   ├── AnnotationWriter.swift
│   │   ├── DatasetManifest.swift
│   │   └── ...
│   └── Templates/                         ← iOS SwiftUI + UIKit templates (40+)
│       ├── ScreenshotCapture.swift
│       ├── KitchenSinkTemplate.swift
│       ├── AlertTemplate.swift            ← + AlertWithTextFieldTemplate
│       ├── LoginFormTemplate.swift
│       ├── SettingsListTemplate.swift     ← + SettingsToggleDenseTemplate, SettingsDisclosureTemplate
│       ├── MultiSectionFormTemplate.swift
│       ├── SheetTemplate.swift
│       ├── SliderPanelTemplate.swift
│       ├── SegmentedFilterTemplate.swift
│       ├── TabViewNavigationTemplate.swift
│       ├── LiquidGlassNavTemplate.swift   ← iOS 26 Liquid Glass variants
│       ├── LiquidGlassTabTemplate.swift
│       ├── UIKitToggleFormViewController.swift  ← hard-negative: zero textField, toggle+button
│       ├── UIKitFormViewController.swift
│       ├── UIKitListViewController.swift
│       ├── UIKitControlsViewController.swift
│       └── KnownBad/                      ← intentional failure case templates
├── GeneratorRunner/                        ← iOS Xcode project
│   └── GeneratorRunnerTests/
│       ├── KitchenSinkValidationTest.swift
│       └── GenerateDatasetTests.swift      ← ~20k image generation across all templates
├── NativeUITrainer/                        ← Swift SPM executable (Create ML training)
│   └── Sources/
│       ├── main.swift                      ← CLI: --dataset --output [--skip-export]
│       ├── CreateMLExporter.swift
│       ├── TrainingConfig.swift
│       └── ExportResult.swift
├── reports/
│   ├── eval_results.json                  ← latest eval output
│   ├── dataset_balance.md
│   └── ...                               ← diagnostic outputs
└── scripts/
    ├── eval_map.swift                     ← custom mAP eval (per-class routing + suppression)
    ├── augment_createml_export.py         ← append new images without full re-export
    ├── diagnose_class_fps.swift           ← per-class FP classification (near-dup vs false-class)
    ├── diagnose_textfield_fps.swift
    ├── diagnose_fp_passes.swift           ← per-pass FP attribution
    ├── analyze_fp_zones.py               ← strip y-zone FP analysis
    ├── confusion_matrix.py
    ├── test_model_predictions.swift       ← single-image spot check
    ├── inspect_model_outputs.swift        ← raw YOLO tensor inspector
    ├── verify_strip_export.swift
    ├── generate_balance_report.py
    └── run-kitchen-sink-test.sh
```

Dataset lives **outside** this repository — gitignored, stored in the simulator container:
```
dataset/
├── manifest.json
├── train/           ← source PNGs + annotation JSONs
├── validation/
├── test/
└── createml_export/ ← Create ML annotatedFiles layout (hard-linked PNGs + annotations.json)
```

---

## Element Taxonomy (~41 classes)

**Chrome:** `statusBar` · `navigationBar` · `tabBar` · `toolbar` · `sidebar` · `homeIndicator` · `dynamicIsland`

**Controls:** `primaryButton` · `secondaryButton` · `destructiveButton` · `cancelAction` · `textField` · `secureField` · `toggle` · `slider` · `segmentedControl` · `picker` · `stepperControl` · `searchField` · `menuButton` · `colorWell`

**Content:** `label` · `imageView` · `link` · `mapView`

**Indicators:** `activityIndicator` · `progressView` · `pageControl` · `scrollIndicator` · `refreshControl`

**Containers:** `alert` · `actionSheet` · `sheet` · `popover` · `listRow` · `collectionItem` · `disclosureGroup` · `tooltip` · `contextMenu`

**Special:** `webContent` · `unknown`

*Phase 6 prototype trains 5 classes: alert, navigationBar, primaryButton, textField, toggle. Full 41-class expansion in Phase 6a requires anchor-free architecture (YOLO11/RT-DETR) — see Key Design Decisions.*

---

## Roadmap

Full task breakdown: [`Tasks.md`](Tasks.md)  
Architecture: [`Research/NativeUIElementDetection.md`](Research/NativeUIElementDetection.md)  
Training history: [`Research/ExperimentLog.md`](Research/ExperimentLog.md)  
Best practices: [`Research/BestPractices.md`](Research/BestPractices.md)

| Phase | Status | Goal | Key Gate |
|---|---|---|---|
| **0: Scaffold** | ✅ Done | Buildable package + research docs | — |
| **1: Coordinate Spike** | ✅ Done | Prove exported coords align with PNG pixels ≤2px | ≤2pt delta on all elements @2x and @3x |
| **2: Taxonomy + Schema v1** | ✅ Done | Expand to ~41 classes; freeze annotation schema | Schema tagged v1.0 |
| **3: Dataset Generator** | ✅ Done | SwiftUI templates + first generation run | 50/50 spot-check pass; imageSHA256 = 1.0 |
| **4: UIKit Generator** | ✅ Done | UIKit-rendered controls (anti-overfitting) | UIKit templates live; ~20k training entries |
| **5: Hard Negatives** | 🔄 In progress | Hard-negative templates targeting known FP zones | UIKitToggleForm ✓; more templates planned |
| **6: iOS Model (5-class)** | 🔄 In progress | Working CoreML detector; mAP ≥ 0.70 | DS-G5 ✓ DS-G6 ✓ (mAP=0.756); device latency TBD |
| **6→6a: Foundation Models eval** | ⬜ | Evaluate Apple Intelligence vision model before full 41-class training | Decision documented |
| **6a: iOS Model (41-class)** | ⬜ | Anchor-free YOLO11 + focal loss; all 41 classes | mAP@0.5 ≥ 0.85 on withheld-template test |
| **6b: tvOS Model** | ⬜ | Focus state, top tab bar | mAP@0.5 ≥ 0.80 |
| **6c: macOS Model** | ⬜ | AppKit, NSToolbar, Y-axis flip | mAP@0.5 ≥ 0.80 |
| **7: OCR Fusion** | ⬜ | Visible text + truncation/clipping rules | Unit tests pass on known-bad fixtures |
| **8: Device/OS Inference** | ⬜ | `NativeUIDeviceInference` from chrome heuristics | Sidecar = exact; orphan PNG = ranked |
| **9: ScreenAuditKit Integration** | ⬜ | Drop-in protocol; contract fields; CLI flag | All ScreenAuditKit tests pass |

**Immediate next steps:**
1. Physical device latency test (iPhone — target < 200ms per image)
2. Withheld-template generalization test (template-family split, not random split)
3. navBar AP regression monitoring (0.845 → 0.775 in Run 005; root cause: UIKitToggleForm section headers creating navBar-like strip patterns)
4. Phase 6→6a evaluation gate: test Apple Foundation Models zero-shot before committing to full 41-class training

---

## Design Principles

1. **Deterministic checks first** — pixel inference augments, it does not replace, rule-based validation
2. **No cloud dependency** — all inference runs locally; screenshots never leave the machine
3. **Semantic roles, not private class names** — `primaryButton` survives OS redesigns; `UIButton` does not
4. **Three models, not one** — iOS/iPadOS, tvOS, and macOS have distinct enough visual languages to warrant separate detectors
5. **Confidence surfaced, not hidden** — every observation declares its `confidenceSource` (`.sidecar`, `.pixelModel`, or `.heuristic`)
6. **Generate, don't annotate** — all training data is synthetic, with ground truth exported at render time
7. **Bias prevention by design** — every environment variable that could leak into the model (clock, battery, wallpaper, text content) is explicitly swept

---

## Key Design Decisions

**Why three models instead of one?** tvOS places the tab bar at the top of the screen; iOS places it at the bottom. tvOS uses focus states that visually transform every element. macOS has window chrome, Y-axis inverted coordinates, and a pointer paradigm with hover states and tooltips. Three targeted models, selected by sidecar platform field or pixel-only heuristic, are more accurate and easier to retrain independently when an OS redesign happens.

**Why anchor-free (YOLO11/RT-DETR) for the full 41-class model?** The element taxonomy spans ~50:1 in aspect ratio — from the homeIndicator (~134×5pt, ratio ~27:1) to a collectionItem (roughly square). Anchor-based detectors (including Create ML objectPrint) cannot cover this range without anchor-to-class mismatch. Create ML is used for the 5-class prototype where the aspect ratio spread is manageable; anchor-free architecture is required for the full taxonomy.

**Why strip tiling?** The 5-class prototype uses Create ML objectPrint (anchor-based). In full 2556×1179px portrait images, a navigationBar has ~16:1 aspect ratio — no anchor matches it, so the model receives zero gradient. Tiling into 22%-height horizontal strips reduces effective aspect ratios to ≤4:1 and makes all classes learnable. This is unnecessary for anchor-free YOLO11.

**Why per-class pass routing?** After strip training, the model learns element features in strip context. Running the same model on full images AND strips creates duplicate predictions across passes. Routing each class to only the pass where it performs well (e.g., alert → full-image only; toggle → strip only) eliminates this FP source. Identified empirically across Runs 003–005.

**Why withhold entire template families from validation, not random 80/20?** A random split from the same generator templates leaks template structure into the validation set. Template-family splits test genuine generalization to unseen screen layouts.

**Why evaluate Apple Foundation Models before Phase 6a?** Apple Intelligence ships a ~3B parameter on-device multimodal vision model. If it achieves strong zero-shot mAP on our 41-class test set, months of custom training effort may be better spent on fine-tuning or distillation rather than training from scratch.

---

## Related

- [`../ScreenAuditKit/`](../ScreenAuditKit/) — screenshot validation engine this package integrates with
- [`../memlog/research/ScreenAuditKit-NativeUIElementDetection-Research.md`](../memlog/research/ScreenAuditKit-NativeUIElementDetection-Research.md) — original feasibility ADR
- [`../memlog/research/ADR-0002-AI-Assisted-Screenshot-Validation.md`](../memlog/research/ADR-0002-AI-Assisted-Screenshot-Validation.md)
