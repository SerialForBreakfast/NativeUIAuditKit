# NativeUIAuditKit

A portable Swift package for detecting native Apple platform UI elements in screenshot PNGs, designed as a drop-in complement to [ScreenAuditKit](../ScreenAuditKit/).

**Current state:** Scaffold only — `0.1.0-scaffold`. The API shape is fully defined and buildable. `NativeUIDetectionRequest.perform(on:sidecar:)` throws `NativeUIDetectionError.modelUnavailable` until the `NativeUIAuditKitModels` package ships. The dataset generator and model training pipeline are under active development.

---

## What This Package Does

NativeUIAuditKit builds a custom Vision-style request backed by CoreML object detectors trained on synthetic native Apple UIs. Given a screenshot PNG, it returns structured `NativeUIElementObservation` values with:

- **Semantic element type** — one of ~41 stable role strings: `primaryButton`, `navigationBar`, `toggle`, `dynamicIsland`, etc.
- **Accurate bounding boxes** — in Vision-normalized, pixel, and point coordinate systems
- **Visible text** — from `VNRecognizeTextRequest` OCR fusion
- **Audit issues** — truncation, clipping, overlapping controls, insufficient touch target, Dynamic Type overflow
- **Device / OS inference** — ranked candidates from visual chrome signals (orphan PNG mode)

**Two operating modes:**
- **Sidecar mode** — highest accuracy; hierarchy metadata exported at capture time is paired with the PNG
- **Pixel-only mode** — moderate accuracy; works on orphan PNGs with no metadata

**Three platform-specific models (when trained):**
- `NativeUIModel_iOS` — iOS + iPadOS (shared visual language)
- `NativeUIModel_tvOS` — tvOS (focus state paradigm, tab bar at screen top)
- `NativeUIModel_macOS` — macOS (window chrome, NSToolbar, AppKit layout)

---

## Requirements

- macOS 15+
- Swift 6.0+
- Xcode 16+

No external dependencies. Vision, CoreML, and CoreGraphics only.

---

## Build & Test

```bash
swift build
swift test
```

All tests pass on the scaffold. `perform(on:sidecar:)` throws `modelUnavailable` until `NativeUIAuditKitModels` is installed — this is expected and tested.

---

## Package Structure

```
NativeUIAuditKit/
├── Package.swift
├── README.md
├── Tasks.md                           ← phase-structured task list and roadmap
├── Research/
│   ├── NativeUIElementDetection.md    ← architecture, API design, training approach
│   ├── TrainingDataStrategy.md        ← dataset design, bias prevention, platform coverage
│   ├── CoordinateSpike.md             ← Phase 1 coordinate alignment validation protocol
│   ├── References.md                  ← Apple docs, prior art, related tools
│   └── schemas/
│       └── annotation.schema.json     ← versioned annotation schema (v1.0, post-Phase 2)
├── Sources/
│   └── NativeUIAuditKit/
│       ├── NativeUIAuditKit.swift
│       ├── Detection/
│       │   └── NativeUIDetectionRequest.swift
│       └── Models/
│           └── NativeUIElementObservation.swift
├── Tests/
│   └── NativeUIAuditKitTests/
│       └── NativeUIAuditKitTests.swift
└── CoordinateSpike/                   ← Phase 1 fixture (copy into Xcode project to run)
    ├── CoordSpikeView.swift
    └── CoordSpikeUITests.swift
```

Dataset lives **outside** this repository — gitignored, stored separately:
```
NativeUIAuditKit-Dataset/
├── manifest.json
├── train/images/ & annotations/
├── validation/images/ & annotations/
├── test/images/ & annotations/
└── golden_real_world/                 ← 200 manually-annotated App Store screenshots (never in training)
```

---

## Element Taxonomy (~41 classes)

**Chrome:** `statusBar` · `navigationBar` · `tabBar` · `toolbar` · `sidebar` · `homeIndicator` · `dynamicIsland`

**Controls:** `primaryButton` · `secondaryButton` · `destructiveButton` · `cancelAction` · `textField` · `secureField` · `toggle` · `slider` · `segmentedControl` · `picker` · `stepperControl` · `searchField` · `menuButton` · `colorWell`

**Content:** `label` · `imageView` · `link` · `mapView`

**Indicators:** `activityIndicator` · `progressView` · `pageControl` · `scrollIndicator` · `refreshControl`

**Containers:** `alert` · `actionSheet` · `sheet` · `popover` · `listRow` · `collectionItem` · `disclosureGroup` · `tooltip` · `contextMenu`

**Special:** `webContent` · `unknown`

---

## Roadmap

Full task breakdown: [`Tasks.md`](Tasks.md)  
Architecture: [`Research/NativeUIElementDetection.md`](Research/NativeUIElementDetection.md)  
Training data strategy: [`Research/TrainingDataStrategy.md`](Research/TrainingDataStrategy.md)

| Phase | Status | Goal | Key Gate |
|-------|--------|------|----------|
| **0: Scaffold** | ✅ Done | Buildable package + research docs | — |
| **1: Coordinate Spike** | 🔄 In progress | Prove exported coords align with PNG pixels ≤2px | `CoordinateSpike.md` acceptance criteria checked |
| **2: Taxonomy + Schema v1** | ⬜ Next | Expand to ~41 classes; freeze annotation schema | Schema tagged v1.0; all new types in `swift test` |
| **3: Dataset Generator** | ⬜ | Simulator state infrastructure + 3 SwiftUI templates + overlay viewer | Overlay spot-check passes; `imageSHA256` match = 1.0 |
| **4: UIKit Generator** | ⬜ | UIKit-rendered controls (anti-overfitting requirement) | ≥2,000 UIKit images; class imbalance ≤5:1 |
| **5: Known-Bad UI** | ⬜ | Intentional failure cases + hard negatives | ≥500 known-bad images; `knownIssues` tagged |
| **5b: Extended Templates** | ⬜ | ≥50 distinct SwiftUI templates; full state/accessibility sweep | No archetype >25% of images |
| **6: iOS Model (5-class)** | ⬜ | First working CoreML detector; validates full pipeline | mAP@0.5 ≥ 0.70 on withheld-template test; physical device < 200ms |
| **6→6a gate: Foundation Models eval** | ⬜ | Run Apple Intelligence vision model against 41-class test set before committing to full custom training | Decision documented; see `TrainingDataStrategy.md` §16.5 |
| **6a: iOS Model (41-class)** | ⬜ | Anchor-free YOLO11 + focal loss + OHEM; real-world validation gap documented | mAP@0.5 ≥ 0.85 on withheld-template test; physical device < 200ms |
| **6b: tvOS Model** | ⬜ | Focus state, top-of-screen tab bar | mAP@0.5 ≥ 0.80 on tvOS withheld test |
| **6c: macOS Model** | ⬜ | AppKit, NSToolbar, Y-axis flip | mAP@0.5 ≥ 0.80 on macOS withheld test |
| **7: OCR Fusion** | ⬜ | Visible text + truncation/clipping rules | Unit tests pass on known-bad fixtures |
| **8: Device/OS Inference** | ⬜ | `NativeUIDeviceInference` from chrome heuristics | Sidecar = exact; orphan PNG = ranked candidates |
| **9: ScreenAuditKit Integration** | ⬜ | Drop-in protocol; contract fields; CLI flag | All ScreenAuditKit tests pass |

---

## Design Principles

1. **Deterministic checks first** — pixel inference augments, it does not replace, rule-based validation
2. **No cloud dependency** — all inference runs locally; screenshots never leave the machine
3. **Semantic roles, not private class names** — `primaryButton` survives OS redesigns; `UIButton` does not
4. **Three models, not one** — iOS/iPadOS, tvOS, and macOS have distinct enough visual languages to warrant separate detectors; one unified model would compromise accuracy on all three
5. **Confidence surfaced, not hidden** — every observation declares its `confidenceSource` (`.sidecar`, `.pixelModel`, or `.heuristic`)
6. **Generate, don't annotate** — all training data is synthetic, with ground truth exported at render time; manual annotation introduces coordinate drift, label inconsistency, and missing metadata
7. **Bias prevention by design** — every environment variable that could leak into the model (clock, battery, wallpaper, text content) is explicitly swept across values

---

## Key Design Decisions

**Why three models instead of one?** tvOS places the tab bar at the top of the screen; iOS places it at the bottom. tvOS uses focus states that visually transform every element. macOS has window chrome, Y-axis inverted coordinates, and a pointer paradigm with hover states and tooltips. Training a single model across all three would require it to learn platform context from visual cues alone — which is ambiguous and reduces accuracy across the board. Three targeted models, selected by sidecar platform field or pixel-only heuristic, are more accurate and easier to retrain independently when an OS redesign happens.

**Why ~41 classes and not more?** The taxonomy covers every common native Apple UI element that can be reliably bounded from a screenshot. Window chrome (macOS title bar, dock, menu bar) is excluded in v1 — the macOS model uses `navigationBar` for in-app navigation; window chrome detection requires a separate use case that is not part of the ScreenAuditKit contract validation goal. visionOS ornaments are deferred until a reliable screenshot capture workflow exists.

**Why withhold entire template families from validation, not random 80/20?** A random split of images from the same generator templates leaks template structure into the validation set. The model memorizes generator patterns rather than generalizing to new screens. Template-family splits test genuine generalization.

**Why anchor-free (YOLO11/RT-DETR) for the full 41-class model?** The element taxonomy spans ~50:1 in aspect ratio — from the homeIndicator (~134×5pt, ratio ~27:1) to a collectionItem (roughly square). Anchor-based detectors use k-means priors that cannot cover this range without severe anchor-to-class mismatch. Create ML's `MLObjectDetector` (anchor-based) is used for the 5-class prototype where the aspect ratio spread is manageable; anchor-free architecture is required for the full taxonomy.

**Why evaluate Apple Foundation Models before Phase 6a?** Apple Intelligence ships a ~3B parameter on-device multimodal vision model. If it achieves strong zero-shot mAP on our test set, months of custom training effort may be better spent on fine-tuning or distillation rather than full training from scratch. This is a one-day evaluation that gates a multi-month commitment.

---

## Related

- [`../ScreenAuditKit/`](../ScreenAuditKit/) — screenshot validation engine this package integrates with
- [`../memlog/research/ScreenAuditKit-NativeUIElementDetection-Research.md`](../memlog/research/ScreenAuditKit-NativeUIElementDetection-Research.md) — original feasibility ADR
- [`../memlog/research/ADR-0002-AI-Assisted-Screenshot-Validation.md`](../memlog/research/ADR-0002-AI-Assisted-Screenshot-Validation.md)
