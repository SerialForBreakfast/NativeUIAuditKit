# NativeUIAuditKit

A portable Swift package for detecting native Apple platform UI elements in screenshot PNGs, designed as a drop-in complement to [ScreenAuditKit](../ScreenAuditKit/).

**Product direction:** [MVP, planned features, and proposed features](Research/ProductRoadmap.md).

**Accuracy scope:** Real-app accuracy is **not independently established**. Dataset mAP is not the percentage of screenshots understood. See the [accuracy audit and benchmark](Research/RealAppValidation543.md).

**Current state:** Shipped models and their historical evaluation scopes are:

- iOS 5-class YOLO11n (`nativeui-ios-v2.0`): generated-screen validation mAP@0.5 is **0.935** CoreML and **0.968** PyTorch.
- Historical direct model inference takes about **7.5 ms/image**. This excludes full consumer overhead.
- tvOS 25-class YOLO11n (`nativeui-tvos-v3.0`): synthetic-screen validation mAP@0.5 is **0.9822**.
- FocusRingDetector v0.1 uses a MobileNetV4 crop classifier. Its model size is **4.80 MB**.
- The completed 5-class phase includes withheld generated-template mAP **0.934**.

The 41-class iOS gate remains open. Run013 custom AP50 is **0.6322**, versus Run009 **0.5549**, on identical withheld generated screens.
That comparison supports 13 classes. Its release requirement is at least **0.85**.
FocusRing v1.0 data and macOS work remain open. See [PhaseMap](Research/PhaseMap.md) for dependencies.

---

## Research status and evidence

Standard UI detection, classification, and focus detection remain the primary goals.
iOS research remains independent of tvOS capture work.
High Contrast Focus (HCF) remains an optional research track. It does not replace Standard behavior.

Current experimental results do not change the shipped models listed above.
The [current consumer measurements](Research/Real550ConsumerReplay.md) use the actual Standard screenshot path.
On 3 retained Fixture development screens, proposals cover 5 of 12 registered controls at IoU 0.5, ignoring classes.
All 3 consumer results are partial and select no control. These counts are not independent real-app accuracy.
NewsTV now supplies 1 predetermined pilot case, captured in 2 trials. It still needs reviewed labels and complete runtime provenance.
XCTest reports foreground while the SDK reports inactivity. Focus remains unknown; this is not a verified no-focus example.

### Plan for trustworthy accuracy measurements

1. Pin the loaded Standard models, preprocessing, taxonomy, thresholds, and TTR build evidence before inference.
2. Collect a 50-screen pilot across up to 5 qualified source-built apps. Report the actual qualified scope.
3. Obtain blinded human review of complete visible controls. Keep SDK reference labels outside model inputs.
4. Freeze 200 additional screens across 5 apps, with 8 distinct flows and 5 capture points per flow.
5. Report per-class precision and recall, localization errors, focus outcomes, no-focus false selections, latency, and execution failures.
6. Cross-check AP50, AP75, and AP50–95 with the official COCO evaluator. Preserve historical custom AP definitions separately.
7. Report each app separately, equal-app summaries, denominators, missing coverage, and uncertainty from whole-flow resampling.

The benchmark measures a selected test population. It does not establish deployment-wide accuracy.
Pilot cases become development evidence. Cases used to guide corrections cannot remain independent qualification evidence.
No training, threshold tuning, or model promotion occurs inside the benchmark.
HCF and iOS remain separate from the tvOS Standard headline. Temporal tracking receives a separate benchmark.
See the [frozen protocol and remaining gates](Research/RealAppValidation543.md) and [application qualification status](Research/RealAppApplications543.md).

Use the [experiment workflow guide](docs/experiment-workflow.md) to understand preparation, execution, evidence, and acceptance.
The [batch authoring guide](docs/experiment-batches/README.md) describes reusable experiment definitions.
These internal research tools are not requirements for library consumers.
The [teacher-preservation experiment](Research/TeacherPreservation495.md) tests training-only anchors through the existing comparison workflow.
Its software tests pass, but the first candidate fails Standard retention. The [matched results](Research/Teacher495Results.md) define the next correction.

## Add as a Dependency

For local screenshot inspection without writing Swift, use the
[nativeui-audit CLI and stdio MCP server](Tools/NativeUIAuditCLI/README.md).
It wraps the production pipeline without replacing shipped models.

```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/<org>/NativeUIAuditKit.git", from: "2.0.0")
]
```

Choose the library product that matches the required behavior:

- **`NativeUIAuditKitModels`** — just the trained model + versioned metadata, no Vision
  framework dependency. Use this if you bring your own inference/rendering code (this is
  what [ViewLens](https://github.com/SerialForBreakfast/ViewLens) depends on).
- **`NativeUIAuditKit`** — the full Vision-style detection request API, built on the above.
- **`NativeUIAuditKitRuntime`** — preview runtime with explicit local models and no bundled model resources.
  This unreleased product requires the new source changes. Downloads remain unfinished.
  See the [TTR handoff](Research/TTRModelHandoff.md) for the interface and limits.

```swift
.target(
    name: "YourTarget",
    dependencies: [
        .product(name: "NativeUIAuditKitModels", package: "NativeUIAuditKit")
    ]
)
```

**Quick Start:**

```swift
import NativeUIAuditKitModels

// iOS Model
let model = try await NativeUIModelAsset.loadModel()          // ANE/GPU-configured MLModel
let metadata = NativeUIModelAsset.metadata                    // input size, class order, thresholds
print(metadata.classLabels)  // ["alert", "navigationBar", "primaryButton", "textField", "toggle"]

// tvOS Model (25 active classes)
let tvOSDescriptor = ModelRegistry.tvOS                       // nativeui-tvos-v3.0
let tvOSModel = try await ModelRegistry.loadModel(for: tvOSDescriptor)
```

The model expects a 640×640 letterboxed input with NMS already baked into the CoreML graph.
For the complete, tested letterbox → predict → parse pipeline, see
[`scripts/eval_yolo_map.swift`](scripts/eval_yolo_map.swift) and [`scripts/eval_tvos_model.py`](scripts/eval_tvos_model.py). Full API docs: `swift package generate-documentation`
(DocC), or see the module documentation comments in
[`NativeUIModelAsset.swift`](NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIModelAsset.swift) and [`ModelRegistry.swift`](NativeUIAuditKitModels/Sources/NativeUIModelContracts/ModelRegistry.swift).

`NativeUIDetectionRequest` (the `NativeUIAuditKit` product's higher-level Vision-style
wrapper) supports automatic platform routing for iOS and tvOS screenshots with active focus detection:

```swift
import NativeUIAuditKit

let request = NativeUIDetectionRequest()   // auto-routes to tvOS when 1080p Apple TV image detected
let observations = try await request.perform(on: screenshotCGImage)

for obs in observations {
    print(obs.elementType, obs.confidence, obs.boundingBoxPixels, "focused:", obs.state.isFocused ?? false)
}
```


---

## What This Package Does

NativeUIAuditKit builds a custom Vision-style request backed by CoreML object detectors trained on synthetic native Apple UIs. Given a screenshot PNG, it returns structured `NativeUIElementObservation` values with:

- **Semantic element type** — one of ~41 stable role strings: `primaryButton`, `navigationBar`, `toggle`, `dynamicIsland`, etc.
- **Accurate bounding boxes** — in Vision-normalized, pixel, and point coordinate systems
- **Visible text** — from `VNRecognizeTextRequest` OCR fusion (`ObservationMerger`)
- **Audit issues** — truncation, clipping, overlapping controls, insufficient touch target
- **Device / OS inference** — ranked candidates from visual chrome signals (orphan PNG mode)
- **tvOS focus** — geometric heuristic, plus optional FocusRingDetector Stage 2 on YOLO crops

**Two operating modes:**
- **Sidecar mode** — uses supplied hierarchy; hierarchy metadata exported at capture time is paired with the PNG
- **Pixel-only mode** — uses screenshot pixels; works on orphan PNGs with no metadata

**Three platform-specific models (iOS and tvOS trained; macOS planned):**
- `NativeUIModel_iOS` — iOS + iPadOS (shared visual language) — **YOLO11n v2.0 shipped ✓** (generated-screen validation mAP@0.5 = 0.935)
- `NativeUIModel_tvOS` — tvOS (focus state paradigm, top shelf, carousel) — **YOLO11n v3.0 shipped ✓** (synthetic-screen validation mAP@0.5 = **0.9822**, 25 active classes; historical Apple TV execution checks)
- `NativeUIModel_macOS` — macOS (window chrome, NSToolbar, AppKit layout)

---

## Model Performance

### tvOS Model: YOLO11n v3.0 (Synthetic Validation and Historical Hardware Execution)

25-class tvOS detector trained on 5,000 balanced 1080p synthetic screens (25 UI families) using Ultralytics YOLO11n and exported to CoreML (`NativeUIModel_tvOS.mlmodelc`) with FP16 quantization.

- **Synthetic-screen validation mAP@0.5:** **0.9822** (Precision: 0.983, Recall: 0.983, mAP@0.5:0.95: 0.944).
- **Active classes (25):** `activityIndicator`, `alert`, `cancelAction`, `collectionItem`, `contextMenu`, `destructiveButton`, `imageView`, `label`, `link`, `listRow`, `navigationBar`, `popover`, `primaryButton`, `progressView`, `searchField`, `secondaryButton`, `secureField`, `segmentedControl`, `sheet`, `sidebar`, `slider`, `stepperControl`, `tabBar`, `toggle`, `toolbar`.
- **Dual Focus Engine:** Evaluates active focus via parallax geometric tile expansion (\(301.5 \times 173.2\) pt vs baseline \(247 \times 147\) pt), radiant perimeter glow, inverted high-luminance interior pills (mean brightness 228.9 vs 149.6), and VoiceOver accessibility contrast borders.
- **Historical hardware observations:** The earlier summary reported 23 captures and 586 detections.
  These counts do not establish precision or recall.
  The retained report contains 29 capture entries and lacks complete reference labels.
  Its earlier “zero false positives” claim is not independently supported.
  See `reports/tvos_hardware_qualification.json` and the accuracy audit.

### iOS Model: YOLO11n v2.0 (Trained + Evaluated 2026-08-23)

5-class iOS detector trained via Ultralytics YOLO11n (100 epochs), exported to CoreML with NMS baked into the graph (IoU 0.30, confidence floor 0.001). Evaluated on the **same 1,394 generated-screen validation images** as the Create ML baseline below, so the two are directly comparable.

| Class | AP@0.5 (.pt) | AP@0.5 (CoreML) | GT instances |
|---|---|---|---|
| alert | 0.995 | **1.000** | 40 |
| navigationBar | 0.975 | 0.909 | 1,186 |
| primaryButton | 0.905 | 0.894 | 761 |
| textField | 0.981 | 0.961 | 315 |
| toggle | 0.984 | 0.909 | 1,074 |
| **mAP@0.5** | **0.968** | **0.935** | — |

DS-G5 (every class AP@0.5 ≥ 0.50) and DS-G6 (mAP ≥ 0.70) both pass with wide margin. Every class improved over the Create ML baseline — navigationBar 0.775 → 0.909, textField 0.505 → 0.961 most notably. The observed backend gap is about 3 percentage points. These results do not isolate its cause.

**On-device latency** (physical iPhone, `best.mlpackage` via direct `MLModel` inference — no Vision framework overhead):

| Metric | Result | Gate |
|---|---|---|
| Model size | 5.18 MB | < 15 MB |
| Cold load | 25 ms avg | < 3 s |
| Per-image inference (total) | ~7.5–9 ms avg | < 200 ms |
| — letterbox + `CVPixelBuffer` | 5.9 ms | |
| — `MLModel.prediction` | 3.4 ms | |
| — output parsing | < 0.1 ms | |

Every latency gate clears by more than an order of magnitude — fast enough to run inline during agentic UI iteration with no perceptible delay. Full pipeline and benchmark source: [`scripts/eval_yolo_map.swift`](scripts/eval_yolo_map.swift), [`GeneratorRunner/GeneratorRunnerTests/YOLOBenchmarkTests.swift`](GeneratorRunner/GeneratorRunnerTests/YOLOBenchmarkTests.swift).

Promoted and shipped as of `2.0.0`: the compiled model lives at `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/NativeUIDetector_v2.mlmodelc`, bundled as an SPM resource in the `NativeUIAuditKitModels` product — see [Add as a Dependency](#add-as-a-dependency). (Raw training checkpoints remain gitignored in `NativeUITrainer/yolo_runs/`.)

### FocusRingDetector v0.1 (shipped 2026-09-18)

Stage 2 tvOS focus classifier on 256×256 YOLO crops. MobileNetV4-Conv-Small uses from-scratch training.
FDR-001 scores 270/270 on its historical test set; the required hard-negative coverage remains incomplete.
The inspected source package exceeds the 5,000,000-byte export gate. Public weight distribution needs explicit review.
See [licensing review](Research/LicensingArchitecture.md) and [release preparation](Research/ReleasePreparation.md).

### Superseded: Create ML baseline (NativeUIDetector_v1, trained 2026-05-28)

The original anchor-based Create ML objectPrint model — required strip-tiling and per-class pass routing to handle high-aspect-ratio classes like navigationBar (~16:1). Kept on disk as `ModelRegistry.iOS_v1`; it is **not** the default bundled detector.

| Class | AP@0.5 | GT | TP | Pred | Notes |
|---|---|---|---|---|---|
| alert | 1.000 | 40 | 40 | 40 | Full-image pass only |
| toggle | 0.821 | 1,074 | 1,019 | 1,232 | Strip pass, conf ≥ 0.95 |
| navigationBar | 0.775 | 1,186 | 1,176 | 1,508 | Strip pass |
| primaryButton | 0.680 | 761 | 687 | 1,185 | Full-image + strip |
| textField | 0.505 | 315 | 268 | 609 | Strip pass + cross-class suppression |
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

**Research queue dashboard (local, loopback only):**
```bash
.venv-yolo/bin/python -B scripts/restart_research_dashboard.py --priority-task TEMPLATE395
# Stops any dashboard on port 8765 after its current job, then starts a new one at http://127.0.0.1:8765/
```
The script refuses to stop a running job unless you pass `--wait SECONDS` or `--cancel-running`.
Use `--stop` to stop only and `--dry-run` to preview. See [ADR-0026](Research/ADR-0026-Queued-Research-Experiments.md).

**Inspect exhausted queue jobs and their restart estimates:**
```bash
.venv-yolo/bin/python -B scripts/research_extensions.py inventory
```
The dashboard Inspect dialog saves a restart with larger limits. See [EXTENSION408](Research/Plans/Extension408.md).

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
├── CHANGELOG.md                           ← version history, semver
├── PROVENANCE.md                          ← shipped-model training audit
├── Research/
│   ├── PhaseMap.md                        ← phase dependency map
│   ├── ExperimentLog.md                   ← chronological training run history
│   ├── NativeUIElementDetection.md        ← architecture, API design, training approach
│   ├── TrainingDataStrategy.md            ← dataset design, bias prevention, platform coverage
│   ├── BestPractices.md                   ← lessons learned (BP-01 through BP-47)
│   ├── TrainingRunbook.md                 ← Create ML historical procedure (YOLO is scripts/)
│   ├── FocusRingDetectorSpec.md           ← Stage 2 tvOS crop classifier
│   ├── FixtureBatchIngest.md              ← TVTestRig batch sidecar format + IPC
│   ├── OCRFusionPolicy.md                 ← OCR fusion rules and truncation detection
│   └── schemas/
│       ├── annotation.schema.json         ← versioned annotation schema (v1.0)
│       └── category_map.json              ← element type → integer ID for COCO export
├── Sources/
│   └── NativeUIAuditKit/
│       ├── NativeUIAuditKit.docc/          ← DocC catalog (landing page + Getting Started)
│       ├── Detection/NativeUIDetectionRequest.swift
│       └── Models/NativeUIElementObservation.swift
├── Tests/
│   ├── NativeUIAuditKitTests/
│   └── NativeUIAuditKitModelsTests/        ← model asset smoke tests (resource resolves + loads)
├── NativeUIAuditKitModels/                ← trained model (bundled SPM resource)
│   └── Sources/NativeUIAuditKitModels/
│       ├── NativeUIAuditKitModels.docc/    ← DocC catalog
│       ├── Resources/
│       │   ├── NativeUIDetector_v2.mlmodelc/     ← iOS YOLO11n v2.0
│       │   ├── NativeUIModel_tvOS.mlmodelc/      ← tvOS YOLO11n v3.0
│       │   └── FocusRingDetector.mlmodelc/       ← Stage 2 focus classifier v0.1

│       ├── NativeUIDetector_v1.mlpackage.mlmodel   ← superseded (2026-05-28); on disk, not a bundled resource
│       ├── training_config_v1.json         ← Create ML config (superseded)
│       ├── training_config_v2.json         ← YOLO11n config (current)
│       ├── NativeUIModelAsset.swift        ← zero-config model + metadata accessor
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
│       ├── AccountProfileFormTemplate.swift  ← train Form-in-List clone (TASK-6a-8)
│       ├── ChromeCoverageTemplate.swift      ← statusBar, scrollIndicator, tooltip, unknown
│       ├── NativeUIPageControlView.swift     ← shared UIPageControl + SwiftUI dots
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
├── NativeUITrainer/                        ← Create ML CLI (retired for production; YOLO logs/weights live here)
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
    ├── research_queue.py                  ← queued research jobs (ADR-0026)
    ├── research_dashboard_server.py       ← loopback dashboard for the queue
    ├── restart_research_dashboard.py      ← safe dashboard stop and restart
    ├── research_extensions.py             ← restart exhausted jobs with larger limits
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

*Shipped iOS detector trains 5 classes: alert, navigationBar, primaryButton, textField, toggle. Full 41-class YOLO11m expansion is Phase 6a (not shipped — DS-G8 fail). tvOS ships 25 of these classes as `nativeui-tvos-v3.0`.*

---

## Roadmap

Phase map: [`Research/PhaseMap.md`](Research/PhaseMap.md)  
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
| **5 / 5a / 5b: Hard Negatives + templates** | ✅ Done | Known-bad + extended SwiftUI/UIKit templates | 16,440 images; UIKitToggleForm live |
| **6: iOS Model (5-class)** | ✅ Done | Working CoreML detector; mAP ≥ 0.70 | DS-G5 ✓ DS-G6 ✓ (generated-screen mAP=0.935, YOLO11n); direct inference latency ✓ (~7.5ms); withheld generated-template mAP 0.934 |
| **6d: `NativeUIDetectionRequest` v2 migration** | ✅ Done | Port the Vision-style request API to the v2 model/pipeline | TASK-6d-1 through 6d-7 pass |
| **6→6a: Foundation Models eval** | ✅ Skipped | Confirmed infeasible — `FoundationModels` has no image input API | Decision documented — proceeded to 6a |
| **6a: iOS Model (41-class)** | 🔄 In progress | Anchor-free YOLO11m; family holdout | DS-G8: mAP@0.5 ≥ 0.85 on withheld-template test (historical Run 009 = **0.586**; matched Run 009 **0.5549**, Run 013 **0.6322**; custom AP) |
| **6b: tvOS Model** | ✅ Done (v3.0) | OS UI + FocusRing v0.1 | Synthetic-screen validation mAP@0.5 = 0.9822; remaining: R-1 scale, FOCUS-DET-05, 6b-U |
| **6c: macOS Model** | ⬜ | AppKit, NSToolbar, Y-axis flip | Requires 6a DS-G8; then mAP@0.5 ≥ 0.80 |
| **7: OCR Fusion** | ✅ Done | Visible text + truncation/clipping rules | `ObservationMerger` + audit rules |
| **8: Device/OS Inference** | ✅ Done | `NativeUIDeviceInference` from chrome heuristics | Sidecar = exact; orphan PNG = ranked |
| **9: ScreenAuditKit Integration** | 🔄 Partial | Drop-in protocol; contract fields; CLI flag | 9-1 done; 9-2/9-3 remain in ScreenAuditKit |

**Immediate next steps**:
1. TASK-6a-10 — authorized Office `aatv fixture batch`, then retrain 41-class from Run 009. Do not ship 41-class weights (DS-G8).
2. FOCUS-DET-05 — ≥6,000 pairs with `light`/`highContrast` hard-neg before replacing FocusRing v0.1.

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

- [`PROVENANCE.md`](PROVENANCE.md) — training hardware, hyperparameters, source datasets, and a personal-identifier audit for every shipped model
- [`Research/LicensingArchitecture.md`](Research/LicensingArchitecture.md) — MIT (code) vs. AGPL-3.0 (bundled YOLO11 weights) license boundary
- [`../ScreenAuditKit/`](../ScreenAuditKit/) — screenshot validation engine this package integrates with
- [`../memlog/research/ScreenAuditKit-NativeUIElementDetection-Research.md`](../memlog/research/ScreenAuditKit-NativeUIElementDetection-Research.md) — original feasibility ADR
- [`../memlog/research/ADR-0002-AI-Assisted-Screenshot-Validation.md`](../memlog/research/ADR-0002-AI-Assisted-Screenshot-Validation.md)
