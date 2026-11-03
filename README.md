# NativeUIAuditKit

A Swift package that finds native Apple UI elements in screenshots. It returns each element's role, box, visible text and tvOS focus state.
It complements [ScreenAuditKit](../ScreenAuditKit/). All inference runs on the device; screenshots never leave the machine.

---

## Accuracy at a glance

**Synthetic scores do not predict real-app accuracy.** Read the real-app rows first.

### Shipped models

| Model | What it detects | Synthetic test | Real apps |
|---|---|---|---|
| `nativeui-ios-v2.0` | iOS, 5 classes | mAP@0.5 **0.935** (Core ML) | not measured |
| `nativeui-tvos-v3.0` | tvOS, 25 classes | mAP@0.5 **0.982** | **23 of 207** controls found (11%), AP50 0.206 |
| FocusRingDetector v0.1 | tvOS focused control | 270 of 270 (historical test) | **0 of 15** focused controls found |

Real-app scope: 9 human-reviewed NewsTV screens (controls) and 21 screens from 3 apps (focus), November 1, 2026. Source: [RealAppValidation543](Research/RealAppValidation543.md).

### tvOS candidate in development (not shipped)

R5 (`pills560-platter-r5`) detects 13 roles, such as button, text, cell and bar. It is not shipped.

| Real-app measure | Role baseline (R1) | Candidate R5 |
|---|---|---|
| Tab and category pills found | 20 of 170 | **168 of 170** |
| Focused control found | 5 of 21 | **18 of 21** |
| Content cards found | 56 of 60 | **60 of 60** |
| Box fit on focused pills (median IoU) | 0.37 | **0.60** |

How to read this table:
- Both models run the shipping input path: Core ML (R5) or matched PyTorch (R1), 640 × 640 letterbox. Source: [PILLS560 results](Research/Plans/Pills560.md#results-summary).
- The screens come from 2 apps (NewsTV, Photo Guessing Game). They guided the tuning, so they are development data, not an independent test.
- A frozen multi-app holdout must confirm these results before any release ([REALCORPUS561](Research/Plans/RealCorpus561.md)).

---

## Status

- **Shipped:** iOS 5-class detector, tvOS 25-class detector, FocusRingDetector v0.1. See [Model details](#model-details).
- **In progress:**
  - tvOS real-app accuracy. R5 is the candidate; holdout scoring is next.
  - FocusRing real-app correction ([FOCUS556](Research/Plans/FocusRealApp556.md)).
  - iOS 41-class detector. Gate DS-G8 needs withheld mAP@0.5 ≥ 0.85; Run 013 reaches 0.632 on 13 supported classes.
- **Planned:** macOS detector (waits on DS-G8).

Dependencies: [PhaseMap](Research/PhaseMap.md). Direction: [ProductRoadmap](Research/ProductRoadmap.md).

---

## Add as a dependency

```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/<org>/NativeUIAuditKit.git", from: "2.0.0")
]
```

Choose 1 library product:

| Product | Use it when |
|---|---|
| `NativeUIAuditKitModels` | You need only the trained models and metadata, and you run your own inference. [ViewLens](https://github.com/SerialForBreakfast/ViewLens) uses this. |
| `NativeUIAuditKit` | You want the Vision-style detection request with OCR, audit rules and tvOS focus. |
| `NativeUIAuditKitRuntime` | Preview only: explicit local models, no bundled resources. Unreleased; see the [TTR handoff](Research/TTRModelHandoff.md). |

For screenshot checks without Swift code, use the [nativeui-audit CLI and stdio MCP server](Tools/NativeUIAuditCLI/README.md).

### Quick start

```swift
import NativeUIAuditKit

let request = NativeUIDetectionRequest()   // routes 1080p Apple TV images to the tvOS model
let observations = try await request.perform(on: screenshotCGImage)

for obs in observations {
    print(obs.elementType, obs.confidence, obs.boundingBoxPixels, "focused:", obs.state.isFocused ?? false)
}
```

Models only:

```swift
import NativeUIAuditKitModels

let model = try await NativeUIModelAsset.loadModel()                    // iOS, ANE/GPU-configured MLModel
let tvOSModel = try await ModelRegistry.loadModel(for: ModelRegistry.tvOS)   // nativeui-tvos-v3.0
```

The models expect a 640 × 640 letterboxed input. NMS is in the Core ML graph.
Pass `iouThreshold` and `confidenceThreshold` explicitly; the export defaults differ (IoU 0.7).
Reference pipelines: [`scripts/eval_yolo_map.swift`](scripts/eval_yolo_map.swift) and [`scripts/eval_tvos_model.py`](scripts/eval_tvos_model.py).
API documentation: `swift package generate-documentation`.

---

## What the package does

For each screenshot, `NativeUIDetectionRequest` returns `NativeUIElementObservation` values with:

- **Role:** 1 of about 41 stable role strings, such as `primaryButton`, `navigationBar` or `toggle`.
- **Box:** in Vision-normalized, pixel and point coordinates.
- **Visible text:** from `VNRecognizeTextRequest` (OCR fusion, `ObservationMerger`).
- **Audit issues:** truncation, clipping, overlapping controls, small touch targets.
- **Device and OS:** ranked candidates from visual chrome.
- **tvOS focus:** a geometric heuristic, plus the optional FocusRingDetector on detector crops.

It works in 2 modes:
- **Sidecar mode:** uses a view hierarchy exported with the screenshot.
- **Pixel-only mode:** uses only the screenshot pixels.

---

## Model details

### iOS: YOLO11n v2.0 (shipped)

5 classes, trained with Ultralytics YOLO11n for 100 epochs. Evaluated on 1,394 generated validation screens.

| Class | AP@0.5 PyTorch | AP@0.5 Core ML | Instances |
|---|---|---|---|
| alert | 0.995 | 1.000 | 40 |
| navigationBar | 0.975 | 0.909 | 1,186 |
| primaryButton | 0.905 | 0.894 | 761 |
| textField | 0.981 | 0.961 | 315 |
| toggle | 0.984 | 0.909 | 1,074 |
| **mAP@0.5** | **0.968** | **0.935** | — |

Withheld generated-template mAP is 0.934. On a physical iPhone, direct model inference takes about 7.5–9 ms per image (size 5.18 MB, cold load 25 ms).
This excludes Vision and consumer overhead. Benchmark source: [`YOLOBenchmarkTests.swift`](GeneratorRunner/GeneratorRunnerTests/YOLOBenchmarkTests.swift).

### tvOS: YOLO11n v3.0 (shipped)

25 classes, trained on 5,000 synthetic 1080p screens from 25 UI families. Exported to Core ML with FP16.
Synthetic validation: mAP@0.5 0.982, precision 0.983, recall 0.983, mAP@0.5:0.95 0.944.
Real apps (pilot): 23 of 207 NewsTV controls found. Tab pills are the largest gap: 1 of 153 found, 106 detected as `label`.

### FocusRingDetector v0.1 (shipped)

A MobileNetV4-Conv-Small classifier on 256 × 256 detector crops. It scores 270 of 270 on its historical test set.
On real apps it finds 0 of 15 focused controls (pilot) and 0 of 21 (development set). See [FOCUS556](Research/Plans/FocusRealApp556.md).
Public weight distribution needs review: [licensing](Research/LicensingArchitecture.md), [release preparation](Research/ReleasePreparation.md).

### History

The Create ML baseline (`NativeUIDetector_v1`, mAP@0.5 0.756) is superseded and not bundled.
Training history is recorded in the research plans and [PROVENANCE.md](PROVENANCE.md).

---

## How accuracy is measured

- **Synthetic tests** use generated screens with labels made at render time. They show training fit, not real-app accuracy.
- **Real-app tests** use source-built apps on the Apple TV Simulator. A person reviews every screen without seeing model output.
- **Development and holdout data stay separate.** Screens that guide a correction cannot later be independent test evidence.
- **Scores use the shipping path:** Core ML, 640 × 640 letterbox, explicit thresholds.
- **Reports show each app separately,** with denominators, missing coverage and uncertainty.

Protocol: [RealAppValidation543](Research/RealAppValidation543.md). App qualification: [RealAppApplications543](Research/RealAppApplications543.md).

---

## Build and test

```bash
swift build
swift test
```

Tests run offline. They do not need Xcode, a Simulator or network access.

Generator smoke test (iOS Simulator):

```bash
scripts/run-kitchen-sink-test.sh
```

Full iOS dataset generation (iOS Simulator):

```bash
xcodebuild test -project GeneratorRunner/GeneratorRunner.xcodeproj -scheme GeneratorRunnerTests -destination "platform=iOS Simulator,name=iPhone 17 Pro" -only-testing GeneratorRunnerTests/GenerateDatasetTests
```

tvOS synthetic dataset:

```bash
swift scripts/generate_tvos_dataset.swift --count 5000 --output dataset/<name>
```

Requirements: macOS 15+, Xcode 26+, Swift 6.0+. No external Swift dependencies.

### For contributors: research queue

```bash
.venv-yolo/bin/python -B scripts/restart_research_dashboard.py --priority-task <TASK>
```

This starts the loopback dashboard at http://127.0.0.1:8765/. It does not stop a running job unless you pass `--wait SECONDS` or `--cancel-running`.
Guides: [experiment workflow](docs/experiment-workflow.md), [batch authoring](docs/experiment-batches/README.md), [queue design (ADR-0026)](Research/ADR-0026-Queued-Research-Experiments.md), [job restarts (EXTENSION408)](Research/Plans/Extension408.md).

---

## Repository layout

```
NativeUIAuditKit/
├── Sources/NativeUIAuditKit/       ← detection request, observations, OCR fusion, audit rules
├── NativeUIAuditKitModels/         ← bundled Core ML models (iOS v2.0, tvOS v3.0, FocusRing v0.1) and metadata
├── NativeUIDatasetGenerator/       ← iOS synthetic data generator (SwiftUI and UIKit templates)
├── GeneratorRunner/                ← iOS Xcode project that renders the templates
├── Tools/NativeUIAuditCLI/         ← command-line tool and MCP server
├── Tests/                          ← offline package tests
├── scripts/                        ← training, evaluation and diagnostic tools
├── Research/                       ← architecture, plans, experiment log, best practices
└── reports/                        ← evaluation outputs and work reports
```

Datasets and training checkpoints are not in the repository.

---

## Element taxonomy (about 41 roles)

| Group | Roles |
|---|---|
| Chrome | `statusBar` `navigationBar` `tabBar` `toolbar` `sidebar` `homeIndicator` `dynamicIsland` |
| Controls | `primaryButton` `secondaryButton` `destructiveButton` `cancelAction` `textField` `secureField` `toggle` `slider` `segmentedControl` `picker` `stepperControl` `searchField` `menuButton` `colorWell` |
| Content | `label` `imageView` `link` `mapView` |
| Indicators | `activityIndicator` `progressView` `pageControl` `scrollIndicator` `refreshControl` |
| Containers | `alert` `actionSheet` `sheet` `popover` `listRow` `collectionItem` `disclosureGroup` `tooltip` `contextMenu` |
| Special | `webContent` `unknown` |

The shipped iOS model detects 5 of these roles. The shipped tvOS model detects 25.
The tvOS candidate groups them into 13 detector roles, after Apple Screen Recognition ([ROLES559](Research/Plans/Roles559.md)). The public role strings do not change.

---

## Roadmap

| Phase | Status | Goal | Gate |
|---|---|---|---|
| 0–5b: scaffold, schema, generators, hard negatives | ✅ Done | Buildable package and synthetic data | — |
| 6: iOS model, 5 classes | ✅ Done | Working Core ML detector | mAP ≥ 0.70: 0.935 |
| 6a: iOS model, 41 classes | 🔄 In progress | Full taxonomy | DS-G8: withheld mAP@0.5 ≥ 0.85 (Run 013: 0.632) |
| 6b: tvOS model and focus | ✅ v3.0 shipped; 🔄 real-app work | Real-app accuracy | Frozen multi-app holdout |
| 6c: macOS model | ⬜ Planned | AppKit detector | Waits on DS-G8 |
| 7: OCR fusion | ✅ Done | Visible text and truncation rules | — |
| 8: Device and OS inference | ✅ Done | Device candidates from chrome | — |
| 9: ScreenAuditKit integration | 🔄 Partial | Drop-in protocol | 9-2 and 9-3 remain in ScreenAuditKit |

Next steps:
1. Score R5 on a frozen multi-app tvOS holdout ([REALCORPUS561](Research/Plans/RealCorpus561.md), RA554-13).
2. Fix FocusRing on real apps without loss on its 270-image retention test ([FOCUS556](Research/Plans/FocusRealApp556.md)).
3. Continue the iOS 41-class work toward DS-G8. Do not ship 41-class weights before the gate passes.

---

## Design principles

1. **Deterministic checks first.** Pixel inference adds to rule-based checks; it does not replace them.
2. **No cloud dependency.** All inference runs locally.
3. **Semantic roles, not private class names.** `primaryButton` survives OS redesigns; `UIButton` does not.
4. **Separate models per platform.** iOS, tvOS and macOS look different enough to need separate detectors.
5. **Visible confidence.** Every observation states its source: `.sidecar`, `.pixelModel` or `.heuristic`.
6. **Generate, then verify on real apps.** Training data is synthetic, with labels made at render time. Real apps measure accuracy.
7. **Prevent bias by design.** The generator varies clock, battery, wallpaper and text content.

More design decisions: [NativeUIElementDetection](Research/NativeUIElementDetection.md). Lessons learned: [BestPractices](Research/BestPractices.md).

---

## Related

- [`PROVENANCE.md`](PROVENANCE.md): training hardware, settings, data sources and a personal-identifier audit for each shipped model.
- [`CHANGELOG.md`](CHANGELOG.md): version history.
- [`Research/LicensingArchitecture.md`](Research/LicensingArchitecture.md): MIT code and AGPL-3.0 YOLO11 weights.
- [`../ScreenAuditKit/`](../ScreenAuditKit/): the screenshot validation engine that uses this package.
