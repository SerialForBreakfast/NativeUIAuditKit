# NativeUIAuditKit — Tasks

## Status Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Done
- `[!]` Blocked — see note

Full architecture: [`Research/NativeUIElementDetection.md`](Research/NativeUIElementDetection.md)  
Training data strategy: [`Research/TrainingDataStrategy.md`](Research/TrainingDataStrategy.md)

---

## Phase 0: Scaffold ✅

*Goal: A buildable Swift package with research documentation and task structure.*

- [x] Create `NativeUIAuditKit` Swift package (`Package.swift`, Swift 6, macOS 15+)
- [x] Write `Sources/NativeUIAuditKit/NativeUIAuditKit.swift` — entry point and version constant
- [x] Write `Sources/NativeUIAuditKit/Detection/NativeUIDetectionRequest.swift` — API shape (stub, throws `modelUnavailable`)
- [x] Write `Sources/NativeUIAuditKit/Models/NativeUIElementObservation.swift` — full data type hierarchy
- [x] Write `Tests/NativeUIAuditKitTests/NativeUIAuditKitTests.swift` — smoke tests (build, API shape, Codable round-trip)
- [x] Write `Research/NativeUIElementDetection.md` — synthesized 20-section research document
- [x] Write `Research/References.md` — Apple docs, prior art, related tools
- [x] Write `Tasks.md` (this file)
- [x] Write `README.md`
- [x] Verify `swift build` and `swift test` pass — 6/6 tests pass (2026-05-03)

---

## Phase 1: Coordinate Spike (P0 blocker) [~]

*Goal: Prove that exported element coordinates align with PNG pixels before any dataset generation. Nothing downstream of this phase is reliable until it completes.*

Full spike protocol and results template: [`Research/CoordinateSpike.md`](Research/CoordinateSpike.md)  
Fixture code (copy into Xcode project): [`CoordinateSpike/`](CoordinateSpike/)

- [x] Write `Research/CoordinateSpike.md` — methodology, protocol, results template, acceptance criteria
- [x] Write `CoordinateSpike/CoordSpikeView.swift` — SwiftUI fixture: Button + TextField + Label at fixed positions
- [x] Write `CoordinateSpike/CoordSpikeUITests.swift` — XCTest UI test measuring XCUIElement.frame vs declared ground truth at @2x and @3x
- [ ] **Run on iPhone 14 Pro Simulator (@3x)** — fill in Results section of `Research/CoordinateSpike.md`
- [ ] **Run on iPhone SE Simulator (@2x)** — fill in Results section of `Research/CoordinateSpike.md`
- [ ] Resolve SwiftUI frame export strategy (GeometryReader preference keys vs `XCUIElement.frame`) — document decision in `Research/CoordinateSpike.md`
- [ ] Investigate known risks (safe area shift, `clipsToBounds` frame vs `accessibilityFrame`, transform divergence) — document outcome
- [ ] Confirm ≤2px alignment at both scale factors — mark acceptance criteria checked in `Research/CoordinateSpike.md`
- [ ] Update `Research/NativeUIElementDetection.md` Section 6 with chosen coordinate strategy

**Gate:** Do not begin Phase 2 until all acceptance criteria in `Research/CoordinateSpike.md` are checked.

---

## Phase 2: Taxonomy Expansion & Schema v1

*Goal: Expand the element taxonomy to ~41 classes and freeze the annotation schema before generating data at scale. This phase has a hard deadline: the `NativeUIElementType` rawValues become stable public API the moment the schema is tagged v1.0. Any addition after tagging is a minor version bump; any rename is a major version bump.*

**Note on ordering:** Taxonomy expansion (2a) must complete before schema freeze (2b). Do not freeze the schema until the full class list is final.

### Phase 2a: Taxonomy Expansion

The original 27-class taxonomy is extended to ~41 classes. New additions address common native Apple elements that were absent.

- [ ] Add 14 new cases to `NativeUIElementType` in `Sources/NativeUIAuditKit/Models/NativeUIElementObservation.swift`:
  - `activityIndicator` — UIActivityIndicatorView / SwiftUI ProgressView (spinning)
  - `progressView` — UIProgressView / SwiftUI ProgressView (linear bar)
  - `pageControl` — UIPageControl (pager dot indicators)
  - `label` — UILabel / SwiftUI Text (standalone non-interactive text)
  - `imageView` — UIImageView / SwiftUI Image (standalone image/media)
  - `menuButton` — UIButton with `.menu` / SwiftUI Menu (pull-down trigger)
  - `contextMenu` — UIContextMenuInteraction preview + action list (long-press popup)
  - `colorWell` — UIColorWell / SwiftUI ColorPicker
  - `disclosureGroup` — SwiftUI DisclosureGroup / UIKit disclosure cell
  - `tooltip` — pointer-hover tooltip (iPadOS/macOS)
  - `refreshControl` — UIRefreshControl (pull-to-refresh)
  - `link` — tappable URL link within text
  - `scrollIndicator` — scroll position indicator bar
  - `mapView` — MKMapView embedded in a screen
- [ ] Add `isLoading` and `isSkeleton` to `NativeUIElementState`
- [ ] Add `isFocused` to `NativeUIElementState` (for tvOS focus state)
- [ ] Update all Codable round-trip tests to cover new element types
- [ ] Update `Research/NativeUIElementDetection.md` Section 5 with expanded taxonomy

### Phase 2b: Schema Freeze

- [ ] Write `Research/schemas/annotation.schema.json` v1.0 — versioned JSON schema with all required fields
- [ ] Confirm multi-coordinate storage: `boundsPixels`, `boundsPoints`, `boundsVisionNormalized`
- [ ] Confirm `imageSHA256` checksum linkage in annotation files
- [ ] Document `generatorProfile.simulatorState` metadata fields (see Phase 3a)
- [ ] Document `image.accessibility` metadata fields (increaseContrast, reduceTransparency, boldText, buttonShapes, onOffLabels, smartInvert)
- [ ] Document `occluded`, `occlusionType`, `excluded`, `exclusionReason` fields (see Section 3 of `Research/TrainingDataStrategy.md`)
- [ ] Write `Research/OCRFusionPolicy.md` — when OCR text overrides or contradicts detector bounds
- [ ] Tag schema as v1.0 — this is the freeze point

**Gate:** Schema tagged v1.0. All 41 `NativeUIElementType` cases present. `swift test` passes.

---

## Phase 3: Dataset Generator Foundation

*Goal: The infrastructure every subsequent generation phase depends on — simulator state control, content corpus, and the overlay validation tool. This is a one-time investment that makes all future data generation reliable.*

### Phase 3a: Simulator State Infrastructure

*Prevents systematic contextual bias — every environment variable that could leak into the model as a spurious feature must be explicitly swept. See `Research/TrainingDataStrategy.md` Section 2b for the full audit.*

- [ ] Write `NativeUIDatasetGenerator/GeneratorConfig.swift` — `OSVisualProfile`, `SimulatorStateOverride` structs
- [ ] Implement `SimulatorStateManager` — wraps `xcrun simctl status_bar override` calls with all override parameters: `--time`, `--batteryLevel`, `--batteryState`, `--cellularBars`, `--wifiBars`, `--cellularMode`, `--operatorName`
- [ ] Implement sweep scheduler: assigns random-but-recorded override combinations before each batch of ≥100 images; records the active override in each image's `generatorProfile.simulatorState` annotation field
- [ ] Implement macOS cursor management: `NSCursor.hide()` before capture, cursor position randomization via `CGWarpMouseCursorPosition`
- [ ] Create 6 wallpaper archetype assets (synthesized abstract patterns — no photos): solid-dark, solid-light, dark-gradient, light-gradient, abstract-texture, photography-style-abstract; store as generator assets
- [ ] Write `ContentCorpus.swift` — seeded realistic UI string generator: 500+ person names, 200+ place names, 100+ company names, date spans (12 months × 3 years), price ranges, email/URL format variants; ensure no string exceeds 5% frequency in any class's instances
- [ ] Write determinism test: given the same `--seed N`, generator produces byte-identical PNG + JSON every time (CI gate)
- [ ] Implement `xcrun simctl status_bar clear` teardown after each batch

### Phase 3b: Generator App Target

- [ ] Create `NativeUIDatasetGenerator` app target in `Package.swift`
- [ ] Implement screenshot capture pipeline: render → `CATransaction.flush()` → `RunLoop.main.run(until: Date() + 0.05)` → read frames → export JSON → capture PNG → compute `imageSHA256`
- [ ] Implement `--seed N` CLI argument for deterministic reproduction
- [ ] Implement manifest writer: records `datasetVersion`, `generatorVersion`, `totalImages`, split assignments, `generationDate`, and per-image entries
- [ ] Implement dataset balance report generator: `reports/dataset_balance.md` and `reports/class_distribution.json`

### Phase 3c: SwiftUI Templates (First 3)

- [ ] Template: Login / signup form (navigationBar, primaryButton, textField, secureField, label)
- [ ] Template: Settings screen grouped list (navigationBar, tabBar, toggle, listRow, disclosureGroup)
- [ ] Template: Alert (alert, primaryButton, cancelAction, label)
- [ ] Sweep: light/dark × 3 Dynamic Type sizes × 2 device sizes = 12 variants per template minimum
- [ ] Sweep wallpaper archetypes for templates with translucent chrome (6 variants per template run)
- [ ] Confirm `xcrun simctl status_bar` overrides are active during generation

### Phase 3d: Overlay Viewer

- [ ] Build overlay viewer app (or Xcode preview target): loads PNG + annotation JSON, draws bounding boxes at `boundsPixels` coordinates in a contrasting color with element type labels
- [ ] Implement spot-check report: random 50-sample viewer that flags misaligned boxes for manual review

### Phase 3e: First Generation Run

- [ ] Generate ≥500 annotated images across the 3 templates
- [ ] Manually spot-check 50 random samples using the overlay viewer — confirm ≤3 misaligned boxes in 50
- [ ] Run dataset balance report; confirm class distribution, Dynamic Type distribution, device distribution
- [ ] Confirm every PNG has a matching annotation with valid `imageSHA256`
- [ ] Record `generationDate` in manifest; confirm spread across ≥4 generation sessions

**Gate:** Overlay viewer shows correct element bounds across 50 random samples. `imageSHA256` match rate = 1.0. Simulator state sweep confirmed in annotation metadata.

---

## Phase 4: UIKit Generator (Anti-Overfitting Requirement)

*Goal: Supplement SwiftUI data with UIKit-rendered controls before any model training. SwiftUI-only training causes the model to learn SwiftUI rendering artifacts rather than native Apple UI semantics. This phase must complete before Phase 6.*

- [ ] Build `UIKitGeneratorViewController` with controls: `UIButton` (4 styles: default, filled, tinted, gray), `UILabel`, `UITextField`, `UITextView`, `UISwitch`, `UISlider`, `UISegmentedControl`, `UITableViewCell` (plain, subtitle, value1, value2), `UIAlertController`, `UISheetPresentationController`, `UITabBar`, `UINavigationBar`
- [ ] Add new Phase 3a/2b class targets: `UIActivityIndicatorView`, `UIProgressView`, `UIPageControl`, `UIImageView`, `UIDatePicker`, `UIContextMenuInteraction`
- [ ] Export matching sidecar JSON from UIKit view hierarchy using `convert(_:to:nil)` to window coordinates
- [ ] Verify coordinate alignment for UIKit frames using the same ±2px standard as Phase 1
- [ ] Apply simulator state sweep (same protocol as Phase 3a) during UIKit generation
- [ ] Generate ≥2,000 annotated UIKit images
- [ ] Merge into dataset; run balance report; confirm imbalance ratio ≤5:1 across all classes
- [ ] Verify no single UIKit template contributes >15% of any class's total instances

**Gate:** UIKit generator contributes ≥2,000 images. Class imbalance ≤5:1.

---

## Phase 5: Known-Bad UI Generator

*Goal: Intentional failure cases labeled so audit rules can detect them. Hard negatives for false-positive prevention.*

- [ ] Implement truncated label generation: constrained width, `.lineBreakMode = .byTruncatingTail`, confirm `…` character present
- [ ] Implement clipped content generation: `clipsToBounds = true` with overflowing content
- [ ] Implement overlapping controls generation: two controls with IoU > 0.1
- [ ] Implement small hit-target generation: <44×44pt buttons
- [ ] Implement Dynamic Type overflow generation: fixed-height container + `accessibilityExtraExtraExtraLarge`
- [ ] Implement RTL mirroring failure generation: LTR-ordered controls in `.rightToLeft` layout
- [ ] Implement off-screen element generation: content below fold in `UIScrollView`
- [ ] Implement occluded element generation: sheet partially covering a target control
- [ ] Implement hard negatives: full-screen loading overlay (no annotations), WKWebView with native-looking controls (labeled `webContent`), decorative image fills
- [ ] Tag all known-bad images with `knownIssues` array in annotation JSON
- [ ] Generate ≥500 known-bad images
- [ ] Verify these images split across train/validation/test by template family (same split rule as all other images)

---

## Phase 5b: Extended SwiftUI Templates

*Goal: Expand SwiftUI template coverage before training. Diversity of screen archetypes is the primary defense against template-memorization bias.*

- [ ] Template: Tab view with navigation (tabBar, navigationBar, homeIndicator, dynamicIsland)
- [ ] Template: Sheet / half-sheet (sheet, primaryButton, cancelAction, label)
- [ ] Template: Search results (searchField, navigationBar, listRow, label)
- [ ] Template: Form with validation (textField, secureField, toggle, primaryButton, label)
- [ ] Template: Empty state (primaryButton, imageView, label)
- [ ] Template: Loading / skeleton state (activityIndicator, progressView, listRow with `isSkeleton: true`)
- [ ] Template: Media card grid (collectionItem, imageView, label)
- [ ] Template: Onboarding page (pageControl, primaryButton, imageView, label)
- [ ] Template: Picker / date entry (picker, navigationBar, primaryButton, cancelAction)
- [ ] Template: Action sheet (actionSheet, destructiveButton, cancelAction)
- [ ] Template: Popover (popover, label, secondaryButton)
- [ ] Template: RTL mirror of login form (all Phase 3c templates mirrored via `.environment(\.layoutDirection, .rightToLeft)`)
- [ ] Add Liquid Glass (iOS 26) visual profile to the 5 highest-coverage templates
- [ ] Add `reduceTransparency`, `increaseContrast`, `boldText` variants to all navigation/tab bar templates (15% of images per setting per `Research/TrainingDataStrategy.md` Section 8)
- [ ] Spot-check 20 samples from each new template before adding to training set
- [ ] Generate to target: ≥8,000 SwiftUI images total across all templates

**Gate:** ≥50 structurally distinct templates. No archetype contributes >25% of total images.

---

## Phase 6: iOS + iPadOS Model — 5-Class Vertical Slice

*Goal: A working iOS/iPadOS CoreML detector for 5 classes, integrated into `NativeUIDetectionRequest`. Validates the full pipeline before expanding to all 41 classes.*

**Prerequisite:** Phases 3a–5 complete. DS-G1 through DS-G4 quality gates pass (see `Research/TrainingDataStrategy.md` Section 12).

- [ ] Run pre-training dataset quality report: imbalance ≤5:1, SHA256 match rate = 1.0, no invalid boxes, zero split contamination, all 5 classes meet instance floors
- [ ] Prepare 5-class training split: `primaryButton`, `navigationBar`, `alert`, `textField`, `toggle`
- [ ] Apply template-family–aware split: 70/20/10 train/validation/test — zero template family overlap between splits; withhold iPad Pro 13" device family from training
- [ ] Train Create ML `MLObjectDetector` (10,000 iterations, `scenePrint` revision 2 feature extractor)
- [ ] Export `.mlpackage` to `NativeUIAuditKitModels/` (separate package, not committed to this repo)
- [ ] Wire `VNCoreMLRequest` into `NativeUIDetectionRequest.perform(on:sidecar:)`; implement tiling strategy (2–3 overlapping 640×640 crops, NMS across crops)
- [ ] Implement model selection routing: `sidecar.platform` → choose model; pixel-only → heuristic classifier (aspect ratio, tab bar position, status bar presence)
- [ ] Run evaluation: mAP@0.5, mAP@0.75, per-class AP, small-object recall
- [ ] Run content-agnostic test: blur all text in 200 test images; verify mAP for non-text-dependent classes drops <10 points
- [ ] Run on 10 real App Store screenshots (personal device); document failure modes in `Research/TrainingDataStrategy.md`
- [ ] Adjust confidence thresholds from precision/recall tradeoff analysis
- [ ] Write `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/ModelRegistry.swift` — version manifest with `calibrationOsRange`, `trainedClasses`, `trainingDatasetVersion`

**Gate (DS-G6):** mAP@0.5 ≥ 0.70 on withheld-template validation set (prototype bar). Document gap between synthetic mAP and real-app mAP.

---

## Phase 6a: iOS + iPadOS Model — Full 41-Class

*Goal: Expand the iOS model to all 41 element classes.*

**Prerequisite:** Phase 5b complete. All 41 classes meet per-class instance floors.

- [ ] Run DS-G7 quality gate: all 41 classes meet instance floors
- [ ] Confirm no class pair has co-occurrence >95% (flag in pre-training report)
- [ ] Train full 41-class model (increase iterations to 20,000 minimum; consider YOLO/DETR if Create ML plateaus below 0.80)
- [ ] Run per-template AP analysis — flag any template with AP >0.95 when overall mAP <0.85
- [ ] Run confusion matrix report; confirm high-risk pairs (alert/sheet, listRow/collectionItem, toolbar/tabBar)
- [ ] Run INT8 quantization benchmark: compare quantized vs FP16 on small-element test subset; document mAP delta
- [ ] Verify model binary <50MB; inference latency <200ms on M1 via tiling strategy
- [ ] Collect 200-image real-world validation set: personal device App Store screenshots, manual annotation via overlay viewer, stored in `NativeUIAuditKit-Dataset/golden_real_world/` (never committed)
- [ ] Report real-world mAP separately from synthetic test mAP; document gap

**Gate (DS-G8):** withheld-template mAP ≥ 0.85 across all 41 classes.

---

## Phase 6b: tvOS Model

*Goal: Dedicated tvOS detector. tvOS has a fundamentally different interaction paradigm — focus state, tab bar at screen top, no homeIndicator — that cannot share weights with the iOS model.*

**Prerequisite:** Phase 6a complete (validates training pipeline before investing in additional platforms).

- [ ] Build tvOS generator templates: focused/unfocused shelf card layout, top-of-screen tab bar, collection row, playback controls, alert
- [ ] Annotate focus ring state via `state.isFocused: true` (NOT a separate class)
- [ ] Apply simulator state sweep adapted for tvOS (no cellular/battery overrides needed; vary time and content)
- [ ] Generate ≥3,000 tvOS images
- [ ] Run tvOS-specific quality gates (same DS-G1 through DS-G4 criteria)
- [ ] Train `NativeUIModel_tvOS` — Create ML or YOLO depending on Phase 6a outcome
- [ ] Verify: `tabBar` detected at top of screen (not confused with toolbar); `isFocused: true` state does not create false positive detections
- [ ] Export `.mlpackage` to `NativeUIAuditKitModels/`

---

## Phase 6c: macOS Model

*Goal: Dedicated macOS detector. macOS introduces window chrome, NSToolbar, pointer-hover tooltips, and AppKit's Y-axis flip — all distinct from iOS.*

**Prerequisite:** Phase 6a complete. macOS coordinate spike completed (Y-axis flip validated — analogous to Phase 1 for AppKit).

- [ ] Complete macOS coordinate spike: validate AppKit Y-axis flip, confirm ±2px alignment on macOS Simulator
- [ ] Build AppKit generator templates: document window with NSToolbar, settings panel, two-column split view with sidebar, NSAlert
- [ ] Apply simulator state sweep adapted for macOS: vary system clock, hide cursor, vary wallpaper behind translucent toolbar
- [ ] Generate ≥2,000 macOS images
- [ ] Run macOS-specific quality gates
- [ ] Train `NativeUIModel_macOS`
- [ ] Export `.mlpackage` to `NativeUIAuditKitModels/`

---

## Phase 7: OCR Fusion & Audit Rules

*Goal: Visible text associated to detected elements; truncation and clipping audit rules active. Works across all three model platforms.*

**Prerequisite:** Phase 6 complete (`NativeUIDetectionRequest` returns live observations).

- [ ] Add `VNRecognizeTextRequest` pass after detector
- [ ] Implement observation merger: associate OCR text regions to nearest element bounds (by IoU and centroid proximity)
- [ ] Surface `visibleText` in `NativeUIElementObservation`
- [ ] Implement `NativeUIIssue(.truncatedText)`: OCR bounding box narrower than element bounds + `…` character
- [ ] Implement `NativeUIIssue(.clippedElement)`: element bounds extend past image edge
- [ ] Implement `NativeUIIssue(.tappableTargetTooSmall)`: `boundingBoxPixels.width * scale < 44` or height < 44
- [ ] Implement `NativeUIIssue(.overlappingElements)`: IoU > 0.1 between two observations
- [ ] Write unit tests for each rule using known-bad fixture images from Phase 5

---

## Phase 8: Device & OS Inference

*Goal: `NativeUIDeviceInference` from dimension/chrome heuristics; pixel classifier for orphan PNGs that lack a sidecar.*

- [ ] Build dimension/safe-area heuristic database: device candidates indexed by screenshot pixel dimensions
- [ ] Implement `NativeUIDeviceInference` from dimensions + safe area inset detection
- [ ] Return ranked candidates with per-candidate confidence — never a single hard-coded guess
- [ ] Train optional visual classifier for: Dynamic Island vs. notch vs. no-notch (small binary/ternary classifier)
- [ ] Implement pixel-only platform heuristic: aspect ratio (tvOS ~16:9 landscape, iOS portrait, macOS landscape), tab bar position (bottom = iOS, top = tvOS), menu bar at top-left = macOS
- [ ] Verify: sidecar screenshots return exact metadata; orphan PNGs return ranked candidates

---

## Phase 9: ScreenAuditKit Integration

*Goal: `NativeUIRecognizing` protocol wired into ScreenAuditKit; `--native-ui coreml` CLI flag.*

- [ ] Define `NativeUIRecognizing` protocol (parallel to `ScreenAuditOCRRecognizing` in ScreenAuditKit)
- [ ] Implement `NativeUINoOpRecognizer` for test determinism
- [ ] Extend `ScreenAuditScreenContract` with `uiElements.required/forbidden/minConfidence`
- [ ] Implement rule IDs: `missingUIElement`, `unexpectedUIElement`, `uiElementBoundsViolation`, `uiElementTruncated`, `uiElementClipped`, `uiElementTargetTooSmall`, `inferredOSMismatch`
- [ ] Add `--native-ui none|coreml` flag to `screenaudit validate` CLI
- [ ] Add clear error message and installation instructions when `NativeUIAuditKitModels` is absent
- [ ] Update ScreenAuditKit integration tests

---

## Extraction Readiness Checklist

Before moving `NativeUIAuditKit` to its own public repository:

- [ ] No RA11y-specific code, paths, or terminology in `Sources/NativeUIAuditKit/`
- [ ] Package builds standalone (`swift build` from `NativeUIAuditKit/` with no workspace)
- [ ] `README.md` includes a minimal integration guide for a project that is not RA11y
- [ ] License decision made and `LICENSE` file added
- [ ] Dataset folder structure documented in `README.md`
- [ ] `NativeUIAuditKitModels` package structure defined
- [ ] At least one non-RA11y test scenario documented in `Research/` or `README.md`
- [ ] `AGENTS.md`-compatible (no prohibited commands, no filesystem boundary violations)
- [ ] `Research/TrainingDataStrategy.md` reviewed and current
