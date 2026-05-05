# NativeUIAuditKit — Tasks

## Status Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Done
- `[!]` Blocked — see note

Full architecture: [`Research/NativeUIElementDetection.md`](Research/NativeUIElementDetection.md)  
Training data strategy: [`Research/TrainingDataStrategy.md`](Research/TrainingDataStrategy.md)

---

## Parallel Work Map

The following streams are independent and can be handed to separate agents or engineers simultaneously once their phase prerequisites are met.

```
Phase 2 unlocks:
  ┌─ STREAM A: Swift type expansion (2a-1, 2a-2, 2a-3, 2a-4)
  └─ STREAM B: Schema + policy docs (2b-1, 2b-2, 2b-3)        ← no Swift needed

Phase 2 gate unlocks:
  ┌─ STREAM C: Generator infrastructure (3a-*, 3b-*)
  ├─ STREAM D: Evaluation scripts (5e-1, 5e-2)                 ← only needs schema format
  └─ STREAM E: Overlay viewer (3d-1, 3d-2)                     ← only needs annotation format

Phase 3 gate unlocks:
  ┌─ STREAM F: UIKit generator (Phase 4)
  ├─ STREAM G: Known-bad generator (Phase 5a)
  └─ STREAM H: Extended SwiftUI templates (Phase 5b)           ← F, G, H are independent

Phase 6 gate unlocks:
  └─ Foundation Models evaluation (6-gate)                     ← blocks Phase 6a

Phase 6a gate unlocks:
  ┌─ STREAM I: tvOS generator + model (Phase 6b)
  └─ STREAM J: macOS coordinate spike + model (Phase 6c)       ← I and J are independent
```

---

## Phase 0: Scaffold ✅

*Complete 2026-05-03. Buildable package, API shape, research docs, 6/6 tests passing.*

---

## Phase 1: Coordinate Spike ✅

*Complete 2026-05-04. All 5 acceptance criteria met on iPhone 17 Pro @3x and iPhone SE @2x.*

**Key findings that govern all generator work:**

| Finding | Rule for all generators |
|---|---|
| GeometryReader global frame = declared position at 0 pt delta | Use `GeometryReader` + `PreferenceKey` as the ground truth source in all SwiftUI templates |
| ZStack must apply `.ignoresSafeArea(.all)` — not just background | Every generator template's root ZStack must carry `.ignoresSafeArea(.all)` |
| `.offset()` does not move the layout frame | All generator templates must use padding-based layout, never `.offset()` |
| GeometryReader reports layout frame, not clipped visible rect | Generator must intersect element frame with any enclosing `.clipped()` container |
| 150ms RunLoop wait is sufficient for frame stability | Use `RunLoop.main.run(until: Date() + 0.15)` before every screenshot capture |

See [`Research/CoordinateSpike.md`](Research/CoordinateSpike.md) for full results.

---

## Phase 2: Taxonomy Expansion & Schema v1 ✅

*Complete 2026-05-04. All 41 types in enum, schema v1.0 written, category_map frozen (alphabetical), OCRFusionPolicy documented. 9/9 tests pass.*

**Hard deadline:** `NativeUIElementType.rawValue` strings become stable public API the moment the schema is tagged v1.0. Additions after tagging = minor version bump. Renames = major version bump. Do not freeze until all 41 classes are final.

**Phase gate:** All tasks in 2a and 2b complete. `swift test` passes. Schema JSON validated against a sample annotation.

---

### STREAM A — Swift type changes (no schema file dependency)

---

#### TASK-2a-1: Add 14 new `NativeUIElementType` cases ✅

**File:** `Sources/NativeUIAuditKit/Models/NativeUIElementObservation.swift`  
**Requires:** Nothing — unblocked immediately  
**Parallel with:** All of Stream B

Add the following 14 cases to the `NativeUIElementType` enum. `rawValue` must exactly match the string shown (these become the stable annotation format strings):

| Case | rawValue | Maps to |
|---|---|---|
| `activityIndicator` | `"activityIndicator"` | UIActivityIndicatorView / SwiftUI ProgressView (spinning) |
| `progressView` | `"progressView"` | UIProgressView / SwiftUI ProgressView (linear bar) |
| `pageControl` | `"pageControl"` | UIPageControl (carousel/pager dots) |
| `label` | `"label"` | UILabel / SwiftUI Text (standalone, non-interactive) |
| `imageView` | `"imageView"` | UIImageView / SwiftUI Image (standalone image/media) |
| `menuButton` | `"menuButton"` | UIButton with `.menu` / SwiftUI Menu (pull-down trigger) |
| `contextMenu` | `"contextMenu"` | UIContextMenuInteraction preview + action list |
| `colorWell` | `"colorWell"` | UIColorWell / SwiftUI ColorPicker |
| `disclosureGroup` | `"disclosureGroup"` | SwiftUI DisclosureGroup / UIKit disclosure cell |
| `tooltip` | `"tooltip"` | Pointer-hover tooltip (iPadOS/macOS) |
| `refreshControl` | `"refreshControl"` | UIRefreshControl (pull-to-refresh spinner) |
| `link` | `"link"` | Tappable URL link within text |
| `scrollIndicator` | `"scrollIndicator"` | Scroll position indicator bar |
| `mapView` | `"mapView"` | MKMapView embedded in a screen |

**AC:**
- `NativeUIElementType.allCases.count == 41`
- Every new case's `rawValue` exactly matches the string in the table above
- `swift build` passes with zero warnings
- No existing rawValues changed

---

#### TASK-2a-2: Extend `NativeUIElementState` ✅

**File:** `Sources/NativeUIAuditKit/Models/NativeUIElementObservation.swift`  
**Requires:** Nothing — unblocked immediately  
**Parallel with:** TASK-2a-1 (different struct, no conflict)

Add three new optional `Bool?` fields to `NativeUIElementState`:

```swift
public var isLoading: Bool?    // true when element displays an in-progress spinner
public var isSkeleton: Bool?   // true when element is a shimmer/placeholder (loading state)
public var isFocused: Bool?    // true when element holds tvOS focus ring
```

All three must be optional (nil = state not applicable or not observed), `Codable`, and `Sendable`.

**AC:**
- All three fields present in `NativeUIElementState`
- `NativeUIElementState()` default-initializes all three to `nil`
- Round-trip Codable test: encode state with all three set to `true`, decode, values preserved
- Round-trip Codable test: encode state with all three `nil`, decoded JSON omits the keys (use `encodeIfPresent`)
- `swift test` passes

---

#### TASK-2a-3: Update Codable round-trip tests ✅

**File:** `Tests/NativeUIAuditKitTests/NativeUIAuditKitTests.swift`  
**Requires:** TASK-2a-1 and TASK-2a-2 complete  
**Parallel with:** Stream B tasks

Extend the existing Codable round-trip tests to cover all 14 new element types and the 3 new state fields.

**Specific tests to add or extend:**
1. `testAllElementTypesRoundTrip` — encode and decode each of the 41 `NativeUIElementType` cases; verify rawValue survives the round-trip without mutation
2. `testNewStateFieldsRoundTrip` — create an observation with `isLoading: true`, `isSkeleton: true`, `isFocused: true`; encode to JSON; decode; assert all three values match
3. `testNilStateFieldsOmittedFromJSON` — create an observation with all state fields nil; encode; confirm the JSON string does not contain the keys `"isLoading"`, `"isSkeleton"`, `"isFocused"`

**AC:**
- All 3 new tests present and passing
- `NativeUIElementType.allCases.count == 41` asserted in `testAllElementTypesRoundTrip`
- `swift test` reports 9+ passing tests (was 6)

---

#### TASK-2a-4: Update `NativeUIElementDetection.md` Section 5 ✅

**File:** `Research/NativeUIElementDetection.md`  
**Requires:** TASK-2a-1 complete  
**Parallel with:** TASK-2b-1, 2b-2

Replace the class list in Section 5.2 with the full 41-class taxonomy. Preserve the existing structure and prose around it. Add a table row for each new class with: case name, description, platform scope (all platforms / iOS only / macOS only / etc.).

**AC:**
- Section 5.2 shows all 41 classes organized by the same 6 groups (Chrome, Controls, Content, Indicators, Containers, Special)
- All 14 new classes have a description and platform scope entry
- No existing class entries removed or renamed

---

### STREAM B — Schema and policy documents (no Swift dependency)

---

#### TASK-2b-1: Write `Research/schemas/annotation.schema.json` v1.0 ✅

**File:** `Research/schemas/annotation.schema.json` (new file)  
**Requires:** Nothing — unblocked immediately  
**Parallel with:** All of Stream A

Write a JSON Schema (draft-07) that validates a single annotation file. The schema must enforce all fields documented in `Research/TrainingDataStrategy.md` Section 13.1 and the sample in `Research/NativeUIElementDetection.md` Section 6.3.

**Required top-level fields in the schema:**
- `schemaVersion` (string, const "1.0")
- `imageSHA256` (string, pattern `^[a-f0-9]{64}$`)
- `image` object with required sub-fields: `fileName`, `pixelWidth`, `pixelHeight`, `scale` (2 or 3), `platform` (enum: iOS/iPadOS/tvOS/macOS), `osVersion`, `deviceName`, `interfaceIdiom`, `orientation`, `colorScheme` (enum: light/dark), `dynamicTypeSize`, `locale`, `layoutDirection` (enum: ltr/rtl), `safeAreaInsets`, `reduceTransparency`, `increaseContrast`, `boldText`, `buttonShapes`, `onOffLabels`, `smartInvert`
- `generatorProfile` object: `templateFamily`, `seed`, `generatorVersion`, `isolationTemplate` (bool), `lowDensity` (bool), `simulatorState` (object with `time`, `batteryLevel`, `batteryState`, `cellularBars`, `wifiBars`, `operatorName`)
- `elements` array, each element with: `id`, `elementType` (enum of all 41 rawValues), `framework`, `boundsPixels`, `boundsPoints`, `boundsVisionNormalized` (all as `{x, y, width, height}` objects), `visibleText` (nullable string), `accessibilityLabel` (nullable string), `traits` (array of strings), `state` object, `occluded` (bool), `occlusionType` (nullable enum: scroll/imageBoundary/splitView/keyboard), `excluded` (bool), `exclusionReason` (nullable string), `knownIssues` (array of strings)

**AC:**
- `Research/schemas/annotation.schema.json` exists and is valid JSON Schema draft-07
- Running `jsonschema --instance` against the sample annotation in `NativeUIElementDetection.md` Section 6.3 passes with no errors
- All 41 element type rawValues present in the `elementType` enum
- `schemaVersion` is a const `"1.0"`
- `imageSHA256` pattern rejects strings shorter than 64 chars and non-hex chars

---

#### TASK-2b-2: Write `Research/schemas/category_map.json` ✅

**File:** `Research/schemas/category_map.json` (new file)  
**Requires:** TASK-2a-1 complete (need final list of all 41 rawValues)  
**Parallel with:** TASK-2b-1

Create a deterministic mapping from `NativeUIElementType.rawValue` string to an integer category ID for COCO-format export and YOLO training. Integer IDs must be stable — do not change them after this file is tagged.

Format:
```json
{
  "version": "1.0",
  "categories": [
    { "id": 0, "name": "primaryButton", "supercategory": "controls" },
    ...
  ]
}
```

Assign IDs 0–40 in alphabetical order of rawValue string. Use `supercategory` groups: chrome, controls, content, indicators, containers, special.

**AC:**
- 41 entries, IDs 0–40, no gaps, no duplicates
- Every entry's `name` matches a `NativeUIElementType.rawValue` exactly
- Alphabetical order verified: running `jq '[.categories[].name] | sort'` on the file produces the same order as the IDs

---

#### TASK-2b-3: Write `Research/OCRFusionPolicy.md` ✅

**File:** `Research/OCRFusionPolicy.md` (new file)  
**Requires:** Nothing — unblocked immediately  
**Parallel with:** Everything in Phase 2

Document the rules for associating `VNRecognizeTextRequest` output to detected element observations. This document governs Phase 7 implementation.

**Required sections:**
1. Association algorithm: for each OCR text observation, find the element whose `boundingBox` has the highest IoU with the text observation's bounding box, subject to minimum IoU ≥ 0.1 and same centroid quadrant. Ties broken by centroid distance.
2. `visibleText` field: the concatenated (space-joined) text of all associated OCR observations, in reading order (top-to-bottom, LTR or RTL per layout direction).
3. Truncation detection rule: OCR bounding box width < element `boundsPixels.width × 0.85` AND the last character of `visibleText` is `…` (U+2026) or the text ends mid-word → emit `NativeUIIssue(.truncatedText)`.
4. Conflict policy: if sidecar provides `visibleText` and OCR disagrees by more than 2 characters, prefer OCR (pixel truth) and log the conflict with both values.
5. Elements that should never have associated text: `toggle`, `slider`, `imageView`, `mapView`, `activityIndicator`, `progressView`, `pageControl`, `scrollIndicator`, `colorWell`.

**AC:**
- All 5 sections present
- Truncation detection rule states the exact threshold (0.85× width) and the U+2026 character check
- The no-text-element list exactly matches the 9 classes listed above
- No implementation code in this document — policy only

---

## Phase 3: Dataset Generator Foundation

*Goal: The infrastructure that all subsequent generation depends on. This phase produces no training images — only the machinery that generates them. Several components are fully independent and can be built in parallel.*

**Phase gate:** Overlay viewer shows correct element bounds on 50 random samples. `imageSHA256` match rate = 1.0. Simulator state overrides confirmed in annotation metadata of generated images.

---

### STREAM C-1 — Generator data types and configuration (no app target needed)

These tasks only require a Swift file and have no Xcode/Simulator dependency. They can be written and tested with `swift build` alone.

---

#### TASK-3a-1: `GeneratorConfig.swift` — core data types ✅

**File:** `NativeUIDatasetGenerator/Sources/GeneratorConfig.swift` (new)  
**Requires:** TASK-2b-1 complete (schema defines the metadata fields)  
**Parallel with:** TASK-3a-3, TASK-3a-4, TASK-3d-1

Define the data types that govern every generator run. All types `Codable`, `Sendable`.

```swift
// Controls which platform/OS visual appearance is rendered
struct OSVisualProfile: Codable, Sendable {
    var tabBarStyle: TabBarStyle      // .classic | .floating | .liquidGlass
    var navBarStyle: NavBarStyle      // .classic | .liquidGlass
    var hasDynamicIsland: Bool
    var hasHomeIndicator: Bool
    var hasNotch: Bool
    var navBarIsTranslucent: Bool
    var safeAreaTopInset: CGFloat
    var safeAreaBottomInset: CGFloat
}

// Simulator status bar state to apply before each batch
struct SimulatorStateOverride: Codable, Sendable {
    var time: String           // "HH:MM" format
    var batteryLevel: Int      // 10, 25, 50, 75, 100
    var batteryState: String   // "charging" | "discharging"
    var cellularBars: Int      // 0, 1, 3, 5
    var wifiBars: Int          // 0, 1, 3
    var cellularMode: String   // "active" | "notSupported"
    var operatorName: String   // "", "AT&T", "Vodafone", "SoftBank"
}

// Top-level configuration for a generator run
struct GeneratorRunConfig: Codable, Sendable {
    var seed: UInt64
    var templateFamily: String
    var osProfile: OSVisualProfile
    var simulatorOverride: SimulatorStateOverride
    var colorScheme: ColorScheme
    var dynamicTypeSize: DynamicTypeSize
    var deviceName: String
    var pixelScale: Int          // 2 or 3
    var locale: String
    var layoutDirection: LayoutDirection
    var accessibilityFlags: AccessibilityFlags
}

struct AccessibilityFlags: Codable, Sendable {
    var reduceTransparency: Bool = false
    var increaseContrast: Bool = false
    var boldText: Bool = false
    var buttonShapes: Bool = false
    var onOffLabels: Bool = false
    var smartInvert: Bool = false
    var classicInvert: Bool = false
}
```

Include 5 predefined `OSVisualProfile` static instances: `ios17`, `ios18`, `ios26`, `tvOS17`, `macOS15`.

**AC:**
- All types compile under Swift 6 strict concurrency with no warnings
- `GeneratorRunConfig` round-trips through `JSONEncoder`/`JSONDecoder` without data loss
- Each `OSVisualProfile` static instance has non-zero `safeAreaTopInset` appropriate for the device family it represents
- `swift build` in the generator target passes

---

#### TASK-3a-2: `ContentCorpus.swift` — seeded text generation ✅

**File:** `NativeUIDatasetGenerator/Sources/ContentCorpus.swift` (new)  
**Requires:** Nothing — unblocked immediately  
**Parallel with:** Everything in Phase 3

Write a deterministic, seeded text generator for realistic UI strings. Must be reproducible: same seed → same sequence every time.

**Required content pools:**
- 500+ person names (varied cultural origins, first+last)
- 200+ place names (cities, countries, street names, venues)
- 100+ company/brand names
- Date generator: spans 2023-01-01 to 2027-12-31 in `MMM d, yyyy` / `d MMM yyyy` / `yyyy-MM-dd` formats
- Price generator: `$0.99–$9,999.99`, `€`, `£`, `¥`, `AED` currency variants
- Email format: `[name]@[domain].[tld]` with varied components
- URL format: `https://[subdomain].[domain].[tld]/[path]`
- Button labels corpus: 50+ action verbs appropriate for primary buttons (Continue, Save, Submit, etc.)
- Navigation titles corpus: 50+ screen names appropriate for navigation bar titles

**Key API:**
```swift
struct ContentCorpus {
    init(seed: UInt64)
    func personName() -> String
    func placeName() -> String
    func companyName() -> String
    func date(format: DateFormat) -> String
    func price(currency: Currency) -> String
    func email() -> String
    func buttonLabel() -> String
    func navigationTitle() -> String
    func listRowTitle() -> String
    func listRowSubtitle() -> String
}
```

**AC:**
- `ContentCorpus(seed: 42).personName()` returns the same string every time it is called (test this 3× in a unit test)
- No single string appears in the output of 100 consecutive `personName()` calls more than once (diversity check)
- All 10 content types produce non-empty strings
- Strings from `buttonLabel()` are title-case single words or short phrases (≤4 words)
- `swift test` passes on a unit test covering the above

---

#### TASK-3a-3: Wallpaper archetype assets ✅

**Files:** `NativeUIDatasetGenerator/Assets/Wallpapers/` (6 PNG files, new directory)  
**Requires:** Nothing — unblocked immediately  
**Parallel with:** Everything

Create 6 abstract wallpaper PNG assets at 1290×2796px (iPhone 15 Pro Max native resolution — scale down as needed). No real photographs. These are used as background layers behind translucent chrome elements to prevent the model from learning a specific blurred color as a chrome feature.

| Filename | Description |
|---|---|
| `wallpaper_solid_dark.png` | Uniform `#1C1C1E` (iOS dark system background) |
| `wallpaper_solid_light.png` | Uniform `#F2F2F7` (iOS light system background) |
| `wallpaper_gradient_dark.png` | Diagonal linear gradient `#0D0D1A` → `#1A0D2E` (dark indigo) |
| `wallpaper_gradient_light.png` | Diagonal linear gradient `#E8F4FD` → `#FDE8F0` (light blue → pink) |
| `wallpaper_texture_abstract.png` | Noise/grain texture, neutral mid-grey base |
| `wallpaper_bokeh_light.png` | Soft circular gradient blobs (no recognizable objects) |

**AC:**
- All 6 files exist as valid PNG files at ≥ 390×844px (minimum useful size)
- No file contains any text, logos, faces, or recognizable real-world objects
- All 6 PNG files load without error via `UIImage(named:)` in the generator target

---

#### TASK-3a-4: `SimulatorStateManager.swift` ✅

**File:** `NativeUIDatasetGenerator/Sources/SimulatorStateManager.swift` (new)  
**Requires:** TASK-3a-1 complete (`SimulatorStateOverride` type)  
**Parallel with:** TASK-3a-2, TASK-3a-3, TASK-3d-1

Implement the manager that calls `xcrun simctl status_bar` before and after each generation batch.

```swift
actor SimulatorStateManager {
    let deviceUDID: String

    // Apply overrides to simulator status bar. Throws if xcrun fails.
    func apply(_ override: SimulatorStateOverride) async throws

    // Clear all overrides (call after each batch)
    func clear() async throws

    // Generate a randomized override using seeded RNG
    static func randomOverride(seed: UInt64, batchIndex: Int) -> SimulatorStateOverride
}
```

`randomOverride` must sweep these ranges deterministically:
- `time`: one of 96 values (every 15-minute slot in 24h)
- `batteryLevel`: one of [10, 25, 50, 75, 100]
- `batteryState`: cycling "charging"/"discharging" alternately
- `cellularBars`: one of [0, 1, 3, 5]
- `wifiBars`: one of [0, 1, 3]
- `operatorName`: one of ["", "AT\&T", "Vodafone", "SoftBank"]

The `xcrun simctl status_bar <udid> override` command arguments must map exactly: `--time HH:MM --batteryLevel N --batteryState S --cellularBars N --wifiBars N --operatorName S`.

**AC:**
- `apply(_:)` constructs the correct `xcrun simctl status_bar override` command string (verify with a unit test that captures the process arguments without actually running xcrun)
- `clear()` calls `xcrun simctl status_bar <udid> clear`
- `randomOverride(seed: 42, batchIndex: 0)` returns the same value every time
- `randomOverride(seed: 42, batchIndex: 0)` and `randomOverride(seed: 42, batchIndex: 1)` return different values
- Swift 6 actor isolation — `apply` and `clear` must be `async`

---

### STREAM C-2 — Generator app target and capture pipeline

These tasks require an Xcode app target and must run on Simulator.

---

#### TASK-3b-1: Add `NativeUIDatasetGenerator` app target to `Package.swift` ✅

**File:** `Package.swift`  
**Requires:** Nothing for the Package.swift edit itself  
**Blocks:** TASK-3b-2, TASK-3b-3, TASK-3c-1

macOS orchestrator executable. Drives `xcrun simctl`, writes annotation JSON, manages the manifest.
`Templates/` is excluded from this target — it lives in the iOS GeneratorRunner Xcode project only.

**AC:**
- `swift build --target NativeUIDatasetGenerator` succeeds with zero warnings
- `swift run NativeUIDatasetGenerator --help` prints usage (even if bare-bones)
- No iOS-only `#if` guards in any `Sources/` file

---

#### TASK-3b-1a: Create `GeneratorRunner` iOS Xcode project ✅

**File:** `GeneratorRunner/GeneratorRunner.xcodeproj` (new)  
**Requires:** TASK-3b-1, TASK-3b-2 complete  
**Blocks:** TASK-3c first runs on a real simulator

iOS app target (iPhone deployment target: iOS 17+) that:
- Compiles all files in `NativeUIDatasetGenerator/Templates/` (including `ScreenshotCapture.swift`)
- References shared files from `NativeUIDatasetGenerator/Sources/` by relative path (same pattern as `CoordSpikeRunner`)
- Runs in the simulator via `xcrun simctl install` + `xcrun simctl launch`

**Pattern:** Mirror `CoordSpikeRunner/` directory layout: minimal `xcodeproj`, no storyboard, `@main` Swift entry point.

**AC:**
- `xcodebuild -project GeneratorRunner/GeneratorRunner.xcodeproj -scheme GeneratorRunner -destination 'platform=iOS Simulator,...' build` succeeds
- No `#if canImport(UIKit)` or `#if os(iOS)` guards in any template file
- `ScreenshotCapture.capture` compiles without guards because UIKit is always available in this target

---

#### TASK-3b-2: Screenshot capture pipeline ✅

**Files:** `NativeUIDatasetGenerator/Templates/ScreenshotCapture.swift` (iOS-only, no guards),  
`NativeUIDatasetGenerator/Sources/CaptureTypes.swift` (shared types, macOS + iOS)  
**Requires:** TASK-3b-1 complete, Phase 1 findings (150ms stabilization, `.ignoresSafeArea`, padding layout)  
**Parallel with:** TASK-3a-4 (different files)

Implement the per-image capture pipeline. This is the most critical infrastructure task — every annotation's accuracy depends on it.

```swift
struct CaptureResult {
    let png: Data
    let sha256: String         // hex SHA-256 of png bytes
    let elements: [AnnotatedElement]  // frames from GeometryReader PreferenceKeys
}

struct ScreenshotCapture {
    // Renders the given SwiftUI view in a UIHostingController,
    // waits 150ms for layout stability, reads frames via PreferenceKey,
    // captures PNG via UIGraphicsImageRenderer at the current screen scale.
    static func capture<V: View>(
        _ view: V,
        config: GeneratorRunConfig
    ) async throws -> CaptureResult
}
```

**Critical implementation requirements from Phase 1:**
1. Root container must be `ZStack { ... }.ignoresSafeArea(.all)` — not just the background
2. All element positioning uses padding, never `.offset()`
3. Frame reading uses `GeometryReader` inside a `PreferenceKey` propagation chain, reading `.global` frame in the CoordinateSpace of the hosting window
4. Stabilization: `RunLoop.main.run(until: Date() + 0.15)` after `setNeedsLayout`/`layoutIfNeeded` cycle
5. PNG capture: `UIGraphicsImageRenderer(bounds: hostingController.view.bounds, format: format)` where `format.scale = UIScreen.main.scale`
6. SHA-256 computation: `SHA256.hash(data: pngData)` via CryptoKit

**AC:**
- Given a view with a `Button` at known padding position (40pt from top, 40pt from left, 200pt wide, 44pt tall), `capture` returns an element with `boundsPoints` within ±2pt of the declared frame — verified by a unit test using `UIHostingController` (same mechanism as Phase 1 tests)
- `sha256` is a valid 64-character lowercase hex string
- `sha256` changes if the PNG bytes change (test by modifying one pixel)
- Running `capture` twice with the same seed and config returns byte-identical PNGs (determinism)

---

#### TASK-3b-3: Annotation JSON writer and manifest ✅

**Files:** `NativeUIDatasetGenerator/Sources/AnnotationWriter.swift`, `NativeUIDatasetGenerator/Sources/DatasetManifest.swift` (new)  
**Requires:** TASK-3b-2 complete, TASK-2b-1 complete (schema defines the format)  
**Parallel with:** TASK-3d-1

Implement two writers:

**`AnnotationWriter`:** Converts a `CaptureResult` + `GeneratorRunConfig` into the annotation JSON format defined by `annotation.schema.json v1.0`. Output must validate against the schema.

Key coordinate conversions:
- `boundsPixels`: `element.frame × config.pixelScale` (already in CGPoint, multiply x/y/w/h by scale)
- `boundsPoints`: `element.frame` as-is from GeometryReader
- `boundsVisionNormalized`: `x_norm = x_pt / imageWidthPt`, `y_norm = 1.0 - (y_pt + height_pt) / imageHeightPt` (Vision uses bottom-left origin)

**`DatasetManifest`:** Maintains the top-level `manifest.json`. Appends one record per generated image. Computes and updates the `classDistribution` map after each image.

```swift
struct ManifestEntry: Codable {
    let fileName: String
    let split: DatasetSplit       // .train | .validation | .test
    let sha256: String
    let templateFamily: String
    let generatorSeed: UInt64
    let generationDate: Date
    let simulatorState: SimulatorStateOverride
    let isolationTemplate: Bool
    let lowDensity: Bool          // true if element count < 2
}
```

**AC:**
- A generated annotation JSON file passes `jsonschema --instance` validation against `Research/schemas/annotation.schema.json`
- `boundsVisionNormalized.y + boundsVisionNormalized.height ≤ 1.0` for every element (no out-of-bounds Vision coords)
- `boundsPixels.x == round(boundsPoints.x × config.pixelScale)` to within 1px for every element
- Manifest `sha256` field for each entry matches the actual SHA-256 of the PNG file on disk
- `DatasetManifest.classDistribution` correctly counts instances across all 41 classes

---

#### TASK-3b-4: Dataset balance report ✅

**File:** `NativeUIDatasetGenerator/Sources/BalanceReport.swift` and `scripts/generate_balance_report.py` (new)  
**Requires:** TASK-3b-3 complete (needs manifest format)  
**Parallel with:** TASK-3d-1

Two complementary tools:

**Swift:** `BalanceReport.generate(from manifest: DatasetManifest) -> String` — produces `reports/dataset_balance.md` with a Markdown table of instance counts per class, imbalance ratio, and a flagged list of classes below their minimum floor.

**Python:** `scripts/generate_balance_report.py` — reads `manifest.json` and produces `reports/class_distribution.json` plus a histogram saved to `reports/class_distribution.png` (using matplotlib). This is the human-readable dataset health dashboard.

**AC:**
- Running the Python script on a sample `manifest.json` with 3 classes and known counts produces a `class_distribution.json` with exactly those counts
- The Markdown report flags any class with imbalance ratio > 5.0 with a `⚠️` prefix
- Both tools exit non-zero and print a useful error if `manifest.json` is missing or malformed

---

### STREAM D — Evaluation scripts (unblocked after schema freeze)

These are pure Python scripts. They only need to know the annotation JSON format and YOLO prediction format. They can be written entirely before any training occurs.

---

#### TASK-5e-1: `scripts/confusion_matrix.py` ✅

**File:** `scripts/confusion_matrix.py` (new)  
**Requires:** TASK-2b-1 complete (needs category_map for class names), TASK-2b-2 complete  
**Parallel with:** Everything in Phase 3, 4, 5

Write a Python evaluation script using the `supervision` library that:
1. Reads ground-truth annotation JSON files from a specified directory
2. Reads YOLO prediction files (`.txt` format, one line per detection: `class_id cx cy w h conf`)
3. Converts both to `supervision.Detections` objects using `category_map.json` for class name mapping
4. Computes `supervision.ConfusionMatrix` at IoU threshold 0.5
5. Outputs:
   - `reports/confusion_matrix_v{N}.png` — heatmap with class names on axes
   - `reports/per_class_metrics_v{N}.csv` — precision, recall, F1 per class
   - stdout summary: overall mAP@0.5, top-5 most-confused pairs

```
Usage: python scripts/confusion_matrix.py \
    --gt-dir NativeUIAuditKit-Dataset/test/annotations \
    --pred-dir runs/detect/predict/labels \
    --version 1
```

**AC:**
- Script runs to completion on a toy dataset (10 images, 3 classes, mixed correct/incorrect predictions) without errors
- Output PNG is a valid image file with class names on both axes
- CSV has a row per class with numeric precision/recall/F1 values
- If `--gt-dir` is missing, script exits 1 with a clear error message
- A unit test (pytest) verifies that a known perfect prediction set produces a diagonal confusion matrix

---

#### TASK-5e-2: `scripts/centroid_distribution.py` ✅

**File:** `scripts/centroid_distribution.py` (new)  
**Requires:** TASK-2b-1 complete  
**Parallel with:** Everything in Phase 3, 4, 5

Write a Python script that detects spatial prior bias — whether predicted bounding box centroids cluster too tightly compared to the training distribution.

For each class:
1. Load all training annotation centroids from `manifest.json` + annotation files
2. Load all predicted centroids from YOLO prediction files
3. Compute 2D spatial entropy of both distributions using a 10×10 grid
4. Flag the class if >80% of predicted centroids fall within a 30% image area square (spatial prior bias)

```
Usage: python scripts/centroid_distribution.py \
    --manifest NativeUIAuditKit-Dataset/manifest.json \
    --pred-dir runs/detect/predict/labels \
    --output reports/centroid_bias_v{N}.json
```

**AC:**
- Outputs a JSON file with one entry per class: `{class_name: str, training_entropy: float, prediction_entropy: float, bias_flag: bool, bias_region: {x, y, w, h} | null}`
- A synthetic test case where all predictions for one class cluster in the bottom-right 30% of the image correctly sets `bias_flag: true` for that class
- Classes with <50 predictions are skipped with a warning (insufficient data)

---

### STREAM E — Overlay viewer (unblocked after schema freeze)

---

#### TASK-3d-1: Overlay viewer ✅

**File:** `NativeUIDatasetGeneratorOverlay/` (new Xcode app or SPM executable target)  
**Requires:** TASK-2b-1 complete (needs annotation format), TASK-3b-3 complete (needs the annotation files it reads)  
**Parallel with:** TASK-3a-4, TASK-3b-4

Build a macOS SwiftUI app (or command-line tool) for manual spot-checking. Given a PNG + its annotation JSON, renders the PNG with colored bounding boxes and element type labels overlaid at `boundsPixels` coordinates.

**Required capabilities:**
- Load any PNG + matching annotation JSON by drag-and-drop or file picker
- Draw each element's `boundsPixels` as a colored rounded-rect stroke (1pt line width, colors per class group: blue=chrome, green=controls, orange=containers, purple=indicators, grey=special)
- Display element type label and confidence (if present) as a small tag above each box
- "Spot check mode": loads 50 random images from a dataset directory, presents them one-by-one with Pass/Fail buttons, writes results to `reports/spotcheck_v{N}.json`
- Keyboard shortcut: `→` = Pass (next image), `←` = Fail (flag for review), `ESC` = quit

**AC:**
- Loading the annotation from `NativeUIElementDetection.md` Section 6.3 (the sample) renders one blue box at the correct pixel position for the `primaryButton` element
- "Spot check mode" produces a valid JSON report with `{passed: N, failed: N, failedImages: [...]}`
- The viewer correctly handles annotations where `occluded: true` (render box with dashed stroke instead of solid)
- App compiles and runs on macOS 15+

---

### Phase 3c: First 3 SwiftUI Templates

*Requires TASK-3b-2 complete (capture pipeline). These 3 templates can be built in parallel by different engineers.*

**Platform note:** All templates in this phase are **iOS-only**. They live in `NativeUIDatasetGenerator/Templates/` and are compiled exclusively by the `GeneratorRunner` iOS Xcode project (TASK-3b-1a). No `#if canImport(UIKit)` or `#if os(iOS)` guards are permitted in any template file — see BP-15.

---

#### TASK-3c-1: Login/signup form template ✅

**File:** `NativeUIDatasetGenerator/Templates/LoginFormTemplate.swift` (new)  
**Requires:** TASK-3b-2, TASK-3a-1 (GeneratorConfig), TASK-3a-2 (ContentCorpus)  
**Parallel with:** TASK-3c-2, TASK-3c-3

**Elements to annotate:** `navigationBar`, `primaryButton`, `secondaryButton`, `textField`, `secureField`, `label`, `link`

**Parameterized inputs (all drawn from `ContentCorpus` using the run seed):**
- Navigation title: `corpus.navigationTitle()`
- Email field placeholder: `corpus.email()`
- Button label: `corpus.buttonLabel()`
- "Forgot password" link present: randomized bool
- Secondary button ("Sign up instead") present: randomized bool
- Error state on email field: randomized bool (triggers red border + error label)

**Layout rules (from Phase 1 findings):**
- Root ZStack with `.ignoresSafeArea(.all)`
- All spacing via padding, never `.offset()`
- Navigation bar rendered via `NavigationStack`/`NavigationView`; annotated as `navigationBar`
- Primary button: full-width, bottom section, 44pt minimum height

**Parameter sweep for the first generation run:**
- 2 color schemes × 3 Dynamic Type sizes × 2 device sizes (iPhone SE, iPhone 15 Pro) = 12 variants minimum

**AC:**
- Running with `--seed 42` produces exactly 12 PNG + JSON pairs with no errors
- Overlay viewer shows all annotated elements aligned to their rendered counterparts (spot-check 5 images manually before marking done)
- All 7 element types appear at least once across the 12 variants
- No element box extends outside the image boundary
- `imageSHA256` matches for all 12 annotation files

---

#### TASK-3c-2: Settings grouped list template ✅

**File:** `NativeUIDatasetGenerator/Templates/SettingsListTemplate.swift` (new)  
**Requires:** TASK-3b-2, TASK-3a-1, TASK-3a-2  
**Parallel with:** TASK-3c-1, TASK-3c-3

**Elements to annotate:** `navigationBar`, `tabBar`, `toggle`, `listRow`, `disclosureGroup`, `label`, `homeIndicator` (when device has one)

**Parameterized inputs:**
- Number of toggle rows: 2–5 (randomized)
- Number of plain list rows: 3–8 (randomized)
- Disclosure group expanded: randomized bool
- Tab bar items: 3 or 5 items (randomized)
- Home indicator: present if device profile has `hasHomeIndicator: true`

**Parameter sweep:** 2 color schemes × 3 Dynamic Type sizes × 2 device sizes = 12 variants minimum

**AC:** Same structure as TASK-3c-1 AC, with elements: all 7 types appear across the 12 variants.

---

#### TASK-3c-3: Alert template ✅

**File:** `NativeUIDatasetGenerator/Templates/AlertTemplate.swift` (new)  
**Requires:** TASK-3b-2, TASK-3a-1, TASK-3a-2  
**Parallel with:** TASK-3c-1, TASK-3c-2

**Elements to annotate:** `alert`, `primaryButton`, `cancelAction`, `destructiveButton`, `label`

**Parameterized inputs:**
- Button count: 1, 2, or 3 (must generate all three variants across a run)
- Has title: randomized bool (when false, message only)
- Has message body: randomized bool
- Has text field (UIAlertController text field style): randomized bool (only valid for ≤2 buttons)
- Destructive button: present when button count = 3

**Alert background:** Must render a partially-visible screen behind the alert (alert is a modal overlay). The background elements are NOT annotated — only the `alert` card and its buttons are annotated.

**AC:** Same structure as TASK-3c-1. All 5 element types appear. All 3 button-count variants appear across the run.

---

### Phase 3e: First Generation Run and Validation

*Requires TASK-3c-1, 3c-2, 3c-3 complete and TASK-3a-4 (SimulatorStateManager) integrated.*

---

#### TASK-3e-1: First generation run

**Requires:** All of Phase 3a, 3b, 3c complete  
**Produces:** ≥500 annotated images in `NativeUIAuditKit-Dataset/train/` and `validation/`

Run the generator across all 3 templates with the full parameter sweep including simulator state overrides.

**AC:**
- ≥500 PNG files with matching annotation JSON files
- `imageSHA256` match rate = 1.0 (every annotation's SHA matches its PNG)
- `manifest.json` contains an entry for every image
- `generationDate` values in the manifest span at least 2 calendar days (minimum 2 separate sessions)
- Simulator state overrides confirmed in annotation metadata: at least 5 distinct `time` values across 100 random images

---

#### TASK-3e-2: Spot-check validation

**Requires:** TASK-3e-1 complete, TASK-3d-1 (overlay viewer) complete

Run the overlay viewer's spot-check mode on 50 random samples from the Phase 3e-1 output.

**AC:**
- ≤3 images flagged as "Fail" (misaligned boxes) in the spot-check report
- Any failure triggers investigation: if a generator bug is found, halt generation, fix, and re-run TASK-3e-1
- `reports/spotcheck_v1.json` exists and shows ≥47/50 Pass

**Phase 3 gate:** TASK-3e-2 passes. `imageSHA256` rate = 1.0. Simulator state sweep confirmed.

---

## Phase 4: UIKit Generator

*Goal: Supplement SwiftUI data with UIKit-rendered controls to prevent SwiftUI rendering artifact overfitting. Must complete before Phase 6.*

**Requires:** Phase 3 gate passed (generator infrastructure stable)  
**Parallel with:** Phase 5 (Known-Bad), Phase 5b (Extended Templates)

---

#### TASK-4-1: UIKit coordinate export validation

**File:** `NativeUIDatasetGenerator/Tests/UIKitCoordTests.swift` (new)  
**Requires:** TASK-3b-2 (capture pipeline)

Before generating at scale, verify UIKit frame export. Create a `UIViewController` with 3 subviews at known frames. Export via `view.convert(subview.bounds, to: nil)`. Assert ±2pt alignment with declared frames.

**AC:**
- Test passes on iPhone 14 Pro Simulator (@3x) and iPhone SE Simulator (@2x)
- Verifies that `UITableViewCell` frames (the most complex case) are exported correctly within a `UITableView`
- Confirms that `clipsToBounds = true` on a parent does NOT change the reported frame (matches Phase 1 finding — report layout frame, not clipped rect)

---

#### TASK-4-2: `UIKitGeneratorViewController`

**File:** `NativeUIDatasetGenerator/Templates/UIKit/UIKitGeneratorViewController.swift` (new)  
**Requires:** TASK-4-1 passing, TASK-3b-2 (capture pipeline), TASK-3a-2 (ContentCorpus)

Build a `UIViewController` that renders a configurable combination of UIKit controls and exports their frames. Supports all UIKit equivalents of the SwiftUI taxonomy.

**Required controls and annotation class mapping:**

| UIKit control | Annotated as |
|---|---|
| `UIButton` (4 styles: default, filled, tinted, gray) | `primaryButton` / `secondaryButton` |
| `UIButton` with `.menu` | `menuButton` |
| `UILabel` (standalone) | `label` |
| `UITextField` | `textField` |
| `UITextView` | `label` (multiline text) |
| `UISwitch` | `toggle` |
| `UISlider` | `slider` |
| `UISegmentedControl` | `segmentedControl` |
| `UITableViewCell` (plain/subtitle/value1/value2 styles) | `listRow` |
| `UIAlertController` | `alert` |
| `UISheetPresentationController` | `sheet` |
| `UITabBar` (standalone, not in UITabBarController) | `tabBar` |
| `UINavigationBar` (standalone) | `navigationBar` |
| `UIActivityIndicatorView` | `activityIndicator` |
| `UIProgressView` | `progressView` |
| `UIPageControl` | `pageControl` |
| `UIImageView` (non-decorative) | `imageView` |
| `UIDatePicker` (inline style) | `picker` |
| `UIContextMenuInteraction` (in a preview state) | `contextMenu` |

Frame export: `view.convert(subview.bounds, to: nil)` for all subviews. Hidden or alpha < 0.01 views are NOT annotated.

**AC:**
- Generates a valid annotation JSON for a test layout with ≥8 different control types
- All exported frames pass the ±2pt alignment test from TASK-4-1
- `UITableViewCell` frames exported correctly in a scrolled `UITableView` (mid-table position, not just row 0)
- No `UIButton` with `isHidden = true` appears in the annotation output

---

#### TASK-4-3: UIKit generation run

**Requires:** TASK-4-2 complete, TASK-3a-4 (SimulatorStateManager)

Run the UIKit generator with the same simulator state sweep as Phase 3.

**AC:**
- ≥2,000 annotated UIKit images generated
- Simulator state overrides confirmed in annotation metadata
- After merging with SwiftUI dataset: class imbalance ratio ≤5:1 across all classes represented in both frameworks
- No single UIKit template contributes >15% of any class's total instance count
- `imageSHA256` match rate = 1.0

---

## Phase 5: Known-Bad UI Generator and Evaluation Tooling

*Goal: Intentional failure cases for audit rule training + the Python evaluation scripts needed in Phase 6+.*

**Requires:** Phase 3 gate passed  
**Parallel with:** Phase 4, Phase 5b

---

### Known-Bad Generator

*TASK-5a-1 through 5a-9 are largely independent of each other — each failure mode can be built and tested separately.*

---

#### TASK-5a-1: Truncated label generator

**File:** `NativeUIDatasetGenerator/Templates/KnownBad/TruncatedLabelTemplate.swift`  
**Requires:** TASK-3b-2

Render a `UILabel` (or SwiftUI `Text`) whose content is wider than its container. Force `.lineBreakMode = .byTruncatingTail` / `.truncationMode(.tail)`. Confirm the `…` (U+2026) character appears in the rendered text using `VNRecognizeTextRequest`.

Annotate as: `label` with `knownIssues: ["truncatedText"]`. The bounding box covers the visible element bounds (not the full text extent).

**AC:**
- Generated images visually show truncated text with `…` character (verified by spot-check)
- `knownIssues` array in annotation contains `"truncatedText"` for every truncated element
- A `VNRecognizeTextRequest` run on the generated image detects the `…` character within the element bounds
- Generate ≥50 images in this category

---

#### TASK-5a-2: Clipped content generator

**Requires:** TASK-3b-2

Render a `UIView`/`View` with `clipsToBounds = true` / `.clipped()` where child content overflows the parent bounds. The parent bounds = the annotated box. The overflow is NOT annotated.

**AC:**
- `knownIssues: ["clippedElement"]` on affected elements
- ≥50 images

---

#### TASK-5a-3: Overlapping controls generator

**Requires:** TASK-3b-2

Render two controls (e.g., two `UIButton`) whose frames overlap with IoU > 0.1. Both are annotated normally. The overlap is flagged at the observation-merge layer (Phase 7), not in the generator itself.

**AC:**
- Both overlapping controls annotated with correct classes and frames
- At least 5 distinct overlap configurations (different element pairs, different overlap amounts: 10–50% IoU)
- ≥50 images

---

#### TASK-5a-4: Small hit-target generator

**Requires:** TASK-3b-2

Render `UIButton` controls at sizes below the 44×44pt minimum: specifically at 20×20pt, 30×30pt, 32×44pt (narrow but tall), 44×20pt (wide but short).

**AC:**
- `knownIssues: ["tappableTargetTooSmall"]` for every button with either dimension < 44pt
- `boundsPoints.width < 44 || boundsPoints.height < 44` verifiable from annotation data
- ≥50 images

---

#### TASK-5a-5: Dynamic Type overflow generator

**Requires:** TASK-3b-2

Render fixed-height containers (explicit `frame(height: N)`) with `AccessibilityExtraExtraExtraLarge` Dynamic Type. Text overflows the container, either clipping or pushing sibling elements.

**AC:**
- `knownIssues: ["dynamicTypeOverflow"]` on affected containers
- Generated at `dynamicTypeSize: "accessibilityExtraExtraExtraLarge"` — confirmed in annotation metadata
- ≥50 images

---

#### TASK-5a-6: RTL mirroring failure generator

**Requires:** TASK-3b-2

Render layouts with `layoutDirection: .rightToLeft` but elements that are intentionally LTR-pinned (e.g., hardcoded `.leading` alignment instead of `.listRowInsets`, or a back button on the left in an RTL layout).

**AC:**
- `knownIssues: ["rtlMirroringFailure"]` on the mis-mirrored element
- `image.layoutDirection: "rtl"` in annotation metadata
- ≥30 images

---

#### TASK-5a-7: Off-screen element generator

**Requires:** TASK-3b-2

Render a `UIScrollView` or `ScrollView` where a target element is below the fold. The element IS in the view hierarchy but NOT visible in the screenshot.

**Annotation rule:** Elements where the computed `boundsPixels` rect has `y > imageHeight` (entirely off-screen) receive `excluded: true, exclusionReason: "insufficient_visible_area"` per Phase 1's P3 rule.

**AC:**
- Off-screen elements are excluded from annotation (not present in `elements` array)
- Partially visible elements (bottom row peeking into frame) are annotated with `occluded: true, occlusionType: "scroll"` and a clipped bounding box
- ≥50 images

---

#### TASK-5a-8: Occluded element generator

**Requires:** TASK-3b-2

Render a sheet partially covering underlying controls. The covered controls annotated with `occluded: true, occlusionType: "imageBoundary"` or left unannotated if <20% visible (P3 rule).

**AC:**
- Partially covered controls (20–80% visible): annotated with clipped box + `occluded: true`
- Mostly covered controls (<20% visible): `excluded: true`
- Sheet itself annotated normally as `sheet`
- ≥50 images

---

#### TASK-5a-9: Hard negatives generator

**Requires:** TASK-3b-2

Three hard negative template types — images where the model should produce *no* detections or specifically `webContent`:

1. **Full-screen loading overlay:** `UIActivityIndicatorView` centered on a dimmed `UIView` covering the entire screen. The loading overlay has NO annotations — the underlying UI elements are hidden.
2. **WKWebView with native-looking controls:** A `WKWebView` rendering a simple HTML page that visually mimics a button, text field, and navigation bar. All annotated as `webContent` (one box for the entire WKWebView region), NOT as `primaryButton`/`textField`/`navigationBar`.
3. **Decorative image fill:** A `UIImageView` with a gradient image taking up >80% of the screen, no interactive elements. Zero annotations.

**AC:**
- Loading overlay images have `elements: []` (empty array) in annotation
- WKWebView images have exactly one element annotated as `webContent`, encompassing the WKWebView bounds
- Decorative fill images have `elements: []`
- ≥30 images per hard negative type (≥90 total)

---

#### TASK-5a-10: Generation run and tagging

**Requires:** TASK-5a-1 through 5a-9 complete

Run all known-bad templates. Verify `knownIssues` population and total count.

**AC:**
- ≥500 known-bad images total across all failure types
- Every image with a known failure has a non-empty `knownIssues` array
- Images split across train/validation/test by template family (same rule as all other images)
- Hard negatives are distributed evenly: 30% in validation, 70% in train

---

## Phase 5b: Extended SwiftUI Templates

*Goal: Expand to ≥50 structurally distinct templates before Phase 6 training. Templates can be built and tested independently.*

**Requires:** Phase 3 gate passed  
**Parallel with:** Phase 4, Phase 5  
**Each template task is independent of the others**

For each template below, the AC is the same pattern as TASK-3c-1: correct spot-check (≤1 misaligned box in 5 spot-checked images), all listed element types appear across the parameter sweep, `imageSHA256` match = 1.0.

| Task | Template name | Elements to annotate |
|---|---|---|
| TASK-5b-1 | Tab view with navigation | `tabBar`, `navigationBar`, `homeIndicator`, `dynamicIsland` |
| TASK-5b-2 | Sheet / half-sheet | `sheet`, `primaryButton`, `cancelAction`, `label` |
| TASK-5b-3 | Search results | `searchField`, `navigationBar`, `listRow`, `label` |
| TASK-5b-4 | Form with validation | `textField`, `secureField`, `toggle`, `primaryButton`, `label` |
| TASK-5b-5 | Empty state screen | `primaryButton`, `imageView`, `label` |
| TASK-5b-6 | Loading / skeleton state | `activityIndicator`, `progressView`, `listRow` (`isSkeleton: true`) |
| TASK-5b-7 | Media card grid | `collectionItem`, `imageView`, `label` |
| TASK-5b-8 | Onboarding page | `pageControl`, `primaryButton`, `imageView`, `label` |
| TASK-5b-9 | Picker / date entry | `picker`, `navigationBar`, `primaryButton`, `cancelAction` |
| TASK-5b-10 | Action sheet | `actionSheet`, `destructiveButton`, `cancelAction` |
| TASK-5b-11 | Popover | `popover`, `label`, `secondaryButton` |
| TASK-5b-12 | RTL mirrors (all Phase 3c) | All same elements, `layoutDirection: .rightToLeft` |
| TASK-5b-13 | Liquid Glass iOS 26 navbar | `navigationBar` (liquidGlass profile), `primaryButton`, `label` |
| TASK-5b-14 | Liquid Glass iOS 26 tabbar | `tabBar` (liquidGlass), `navigationBar`, `homeIndicator` |
| TASK-5b-15 | Settings with disclosure groups | `navigationBar`, `disclosureGroup`, `listRow`, `toggle`, `label` |
| TASK-5b-16 | Refresh control in list | `navigationBar`, `listRow`, `refreshControl` |
| TASK-5b-17 | Context menu preview | `contextMenu`, `listRow`, `label` |
| TASK-5b-18 | Map with overlays | `mapView`, `navigationBar`, `primaryButton` |
| TASK-5b-19 | stepper + quantity controls | `stepperControl`, `label`, `navigationBar` |
| TASK-5b-20 | Progress + activity combined | `progressView`, `activityIndicator`, `label`, `cancelAction` |

**Additional sweep tasks (apply to all templates):**

#### TASK-5b-21: Accessibility variant sweep

**Requires:** All TASK-5b-1 through 5b-20 complete  
For every template that includes `navigationBar` or `tabBar`, generate variants with `reduceTransparency: true` (15% of images), `increaseContrast: true` (15%), `boldText: true` (10%), and `buttonShapes: true` (10%) per `Research/TrainingDataStrategy.md` Section 10.

**AC:** Annotation metadata shows the correct accessibility flags. Total images across all accessibility variants ≥2,000.

#### TASK-5b-22: Phase 5b generation run

**Requires:** All TASK-5b-1 through 5b-21 complete

**AC:**
- ≥8,000 SwiftUI images total across all templates (Phase 3c + Phase 5b)
- ≥50 structurally distinct templates counted in manifest
- No archetype group (forms/lists/modals/etc.) contributes >25% of total images
- `reports/dataset_balance.md` generated and reviewed

---

## Phase 6: iOS + iPadOS Model — 5-Class Vertical Slice

*Goal: A working CoreML detector for 5 classes in `NativeUIDetectionRequest`. Validates the full training pipeline end-to-end before the 41-class investment.*

**Prerequisite:** Phases 4, 5, 5b complete. Pre-training quality gates DS-G1 through DS-G8 pass.

---

#### TASK-6-1: Pre-training dataset quality audit

**File:** `scripts/dataset_quality_check.py` (new)  
**Requires:** Phase 4 and Phase 5 generation complete

Write a Python script that enforces all pre-training quality gates. Must exit non-zero if any gate fails.

**Gates checked:**
- Imbalance ratio ≤5:1 (max class instance count / min class instance count across the 5 training classes)
- `imageSHA256` match rate = 1.0 (check every PNG in dataset vs annotation)
- Zero invalid bounding boxes (width > 0, height > 0, all normalized coords in [0,1])
- Zero split contamination (no template family appears in both train and validation)
- All 5 classes meet their minimum instance floors
- Isolation template cap: no class has >10% of instances with `isolationTemplate: true`

```
Usage: python scripts/dataset_quality_check.py \
    --manifest NativeUIAuditKit-Dataset/manifest.json \
    --dataset-dir NativeUIAuditKit-Dataset \
    --classes primaryButton navigationBar alert textField toggle
```

**AC:**
- On a clean dataset the script exits 0
- Injecting a synthetic violation (e.g., one annotation with a mis-matched SHA256) causes the script to exit 1 with the specific failed gate named in the output
- All 6 gate checks implemented and individually testable

---

#### TASK-6-2: Train 5-class Create ML model

**Requires:** TASK-6-1 passes (all gates green)

Train `MLObjectDetector` with `scenePrint(revision: 2)` feature extractor, 10,000 iterations, batch size 32, on the 5-class (primaryButton, navigationBar, alert, textField, toggle) training split.

Training configuration to document in `NativeUIAuditKitModels/` alongside the model:
```json
{
  "algorithm": "transferLearning",
  "featureExtractor": "scenePrint_v2",
  "maxIterations": 10000,
  "batchSize": 32,
  "trainingClasses": ["primaryButton", "navigationBar", "alert", "textField", "toggle"],
  "datasetVersion": "<from manifest>",
  "trainedAt": "<ISO date>"
}
```

**AC:**
- Training completes without error
- `.mlpackage` exports successfully to `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIDetector_v1.mlpackage`
- Model metadata includes `calibrationOsRange`, `trainedClasses`, `trainingDatasetVersion`

---

#### TASK-6-3: Implement SAHI inference in `NativeUIDetectionRequest`

**File:** `Sources/NativeUIAuditKit/Detection/NativeUIDetectionRequest.swift`  
**Requires:** TASK-6-2 complete (need a model to test against)

Replace the placeholder inference stub with a real implementation using SAHI (Slicing Aided Hyper Inference). Do NOT use a custom ad-hoc tiling scheme.

**SAHI implementation in Swift:**
1. Resize input `CGImage` to 2× native resolution (preserve aspect ratio)
2. Generate overlapping 640×640 crop grid: step size = 480px (25% overlap) in both axes
3. For each crop: run `VNCoreMLRequest`, collect observations with their crop-local coordinates
4. Convert crop-local coordinates back to full-image Vision-normalized coordinates
5. Merge all observations using Non-Maximum Suppression: IoU threshold 0.45, confidence threshold from `configuration.minimumConfidence`
6. Return merged `[NativeUIElementObservation]` sorted by confidence descending

**Model selection routing (pixel-only mode heuristics):**
- Image aspect ratio > 1.5 AND width > height: check for macOS indicators (no status bar at top, possible menu bar)
- Tab bar detectable in top 15% of image → tvOS model
- Default: iOS model

**AC:**
- Running on the 5 test images from the Phase 1 spike returns at least the 3 annotated elements
- Confidence values are in [0.0, 1.0] for all returned observations
- `VNCoreMLRequest` runs off the main actor (verified by `XCTAssertFalse(Thread.isMainThread)` in a test)
- When `NativeUIAuditKitModels` is not linked, `perform(on:sidecar:)` throws `NativeUIDetectionError.modelUnavailable` (existing behavior preserved)
- `swift test` passes (all existing tests still pass)

---

#### TASK-6-4: Implement `ModelRegistry`

**File:** `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/ModelRegistry.swift` (new)  
**Requires:** TASK-6-2 (need the model file)  
**Parallel with:** TASK-6-3

```swift
public struct ModelRegistry: Sendable {
    public static let iOS = ModelDescriptor(
        modelId: "nativeui-ios-v1.0",
        calibrationOsRange: ClosedRange(uncheckedBounds: ("iOS 17.0", "iOS 26.x")),
        trainedClasses: ["primaryButton", "navigationBar", "alert", "textField", "toggle"],
        trainingDatasetVersion: "<from manifest>",
        minimumDeploymentTarget: "iOS 17.0"
    )
}

public struct ModelDescriptor: Sendable, Codable {
    public let modelId: String
    public let calibrationOsRange: (String, String)
    public let trainedClasses: [String]
    public let trainingDatasetVersion: String
    public let minimumDeploymentTarget: String
}
```

**AC:**
- `ModelRegistry.iOS.trainedClasses.count == 5`
- `ModelDescriptor` round-trips through `JSONEncoder`
- `swift build` on the `NativeUIAuditKitModels` target passes

---

#### TASK-6-5: Evaluation run

**Requires:** TASK-6-3 complete, TASK-5e-1 complete (confusion matrix script)

Run the full evaluation suite on the withheld-template test set.

**AC (all must pass before Phase 6 gate):**
- mAP@0.5 ≥ 0.70 on withheld-template test set
- mAP@0.75 ≥ 0.45 (looser bound — bounding box precision is less critical at prototype stage)
- No individual class AP < 0.50 (a class below 0.50 indicates a training data gap, not a threshold tuning issue)
- Content-agnostic test: blur all text in 200 test images, re-run inference; mAP for `navigationBar`, `tabBar`, `toggle`, `alert` drops <10 points from the unblurred baseline
- `reports/confusion_matrix_v1.png` generated; no confusion pair exceeds 30% false positive rate
- Run on 10 real App Store screenshots (personal device); document failure modes

---

#### TASK-6-6: Physical device benchmark

**Requires:** TASK-6-3 complete  
**Parallel with:** TASK-6-5

Write an `XCTest` performance test that loads the model cold, then runs inference on 10 test images, measuring with `XCTClockMetric` and `XCTMemoryMetric`. Run on a physical iPhone (not simulator).

**AC:**
- Median inference time per image < 200ms (measured on iPhone 14 or later)
- Cold model load time < 3s
- Model file size < 50MB (measured via `FileManager.default.attributesOfItem`)
- Peak memory delta during inference < 200MB
- ANE utilization > 0% (verify via Instruments → Core ML Instrument during manual test)

**Phase 6 gate:** TASK-6-5 and TASK-6-6 both pass.

---

## Phase 6 Gate: Foundation Models Baseline Evaluation

*One mandatory evaluation day before committing to 41-class custom training. No "skip" option.*

**Requires:** Phase 6 gate passed  
**Time estimate:** 1 day

---

#### TASK-6g-1: Foundation Models evaluation harness

**File:** `scripts/foundation_model_eval.py` or a Swift `XCTest` target  
**Requires:** TASK-6-5 complete (have the withheld-template test set ready)

Build an evaluation harness that sends each test image to Apple's Foundation Models framework with a zero-shot prompt and records predictions.

Prompt template:
```
Identify all visible native Apple UI elements in this screenshot. 
For each element, provide: the element type (from this list: {41 class names}), 
and its bounding box as [x_min, y_min, x_max, y_max] normalized to [0,1].
Return JSON array.
```

Parse the JSON response, convert to the same format as YOLO predictions, run through `confusion_matrix.py`.

**AC:**
- Harness runs on all images in the withheld-template test set
- Records per-class AP and overall mAP@0.5
- Records median inference latency on physical device
- Output: `reports/foundation_model_baseline.json` with the full results

---

#### TASK-6g-2: Architecture decision

**Requires:** TASK-6g-1 complete

Apply the decision matrix from `Research/TrainingDataStrategy.md` Section 16.5:

| Foundation Model mAP | Decision |
|---|---|
| < 0.50 | Proceed with YOLO11 custom training (Phase 6a as planned) |
| 0.50–0.75 | Evaluate as distillation teacher; custom training still required |
| > 0.75 zero-shot | Evaluate LoRA adapter fine-tuning before committing to full custom training |

Document the decision and mAP result in `Research/TrainingDataStrategy.md` under Section 16.5.

**AC:**
- `Research/TrainingDataStrategy.md` updated with actual measured mAP and the chosen path
- Decision rationale is one paragraph, not just a number

---

## Phase 6a: iOS + iPadOS Model — Full 41-Class

*Goal: Production-quality iOS model across all 41 classes using anchor-free YOLO11 with focal loss and OHEM.*

**Requires:** Phase 6 gate passed, Phase 6 Gate evaluation complete, Phase 5b complete, all 41 classes meet instance floors

---

#### TASK-6a-1: YOLO11 training configuration

**File:** `scripts/train_ios_model.py` (new)  
**Requires:** TASK-2b-2 complete (category_map.json), Phase 5b generation complete

Configure YOLO11 training via Ultralytics API:

```python
from ultralytics import YOLO
model = YOLO("yolo11m.pt")  # medium size; downsize to nano via distillation if >50MB
model.train(
    data="NativeUIAuditKit-Dataset/dataset.yaml",   # COCO-format via export converter
    epochs=100,
    imgsz=640,
    batch=16,
    loss="focal",           # focal loss (gamma=2.0, alpha=per-class from class_weights.json)
    patience=15,            # early stopping
    workers=4,
    project="runs/ios",
    name="v1",
    # OHEM: implemented via custom loss weighting callback
)
```

Write `scripts/export_coco.py` — converts our custom JSON annotations to COCO format using `category_map.json`, outputs `NativeUIAuditKit-Dataset/dataset.yaml` + `annotations/instances_train.json` + `annotations/instances_val.json`.

**AC:**
- `export_coco.py` produces COCO-valid JSON (validates with `pycocotools`)
- `category_map.json` integer IDs exactly match the COCO category IDs in the export
- Training script runs to completion without errors in a dry-run mode (`--epochs 2 --batch 4`)

---

#### TASK-6a-2: Focal loss alpha calibration

**File:** `scripts/compute_class_weights.py` (new)  
**Requires:** TASK-6-1 (dataset quality check), Phase 5b generation complete

Compute per-class focal loss alpha weights from inverse class frequency in the training split. Output `scripts/class_weights.json`.

```python
# alpha_i = 1 / (count_i / total_instances)
# Then normalize so sum(alpha) = 1
```

**AC:**
- `class_weights.json` has 41 entries, one per class
- Rare classes (stepperControl, colorWell, mapView) have the highest alpha values
- High-frequency classes (navigationBar, tabBar) have the lowest alpha values
- All weights sum to 1.0

---

#### TASK-6a-3: OHEM callback

**File:** `scripts/ohem_callback.py` (new)  
**Requires:** Nothing beyond YOLO knowledge — unblocked

Implement Online Hard Example Mining as a Ultralytics training callback. Each epoch, compute per-image loss from the validation batch. In the next epoch, oversample the top-K highest-loss images by doubling their frequency in the DataLoader.

```python
class OHEMCallback:
    def on_train_epoch_end(self, trainer):
        losses = compute_per_image_loss(trainer)
        top_k_indices = get_top_k_hard_examples(losses, k=int(len(losses) * 0.2))
        trainer.train_loader.sampler.oversample(top_k_indices, factor=2.0)
```

**AC:**
- Callback integrates into YOLO training without errors
- After 2 training epochs, the `top_k_indices` set is non-empty and changes between epochs (not static)
- A unit test verifies that oversampled images appear ~2× more frequently than baseline in the next epoch's batch

---

#### TASK-6a-4: CoreML export pipeline

**File:** `scripts/export_to_coreml.py` (new)  
**Requires:** Successful YOLO11 training run

Convert the trained `.pt` model to CoreML `.mlpackage` via `coremltools`:

```python
import coremltools as ct
from ultralytics import YOLO

yolo = YOLO("runs/ios/v1/weights/best.pt")
yolo.export(
    format="coreml",
    imgsz=640,
    nms=True,           # include NMS in the model
    half=True,          # FP16
    int8=False,         # benchmark separately (TASK-6a-5) before committing
    minimum_deployment_target=ct.target.iOS17
)
```

**AC:**
- Export produces a `.mlpackage` file
- The package loads without error in Swift via `try MLModel(contentsOf: packageURL)`
- FP16 and INT8 versions both exported (for benchmarking in TASK-6a-5)

---

#### TASK-6a-5: Quantization benchmark

**Requires:** TASK-6a-4 complete

Run the FP16 vs INT8 comparison on the small-element test subset (elements with `boundsPixels.width < 100` OR `boundsPixels.height < 100` — covers homeIndicator, stepperControl, pageControl, scrollIndicator, link).

**AC:**
- Both FP16 and INT8 model AP values recorded per class in `reports/quantization_benchmark.json`
- Decision rule: if small-element class AP drops >5 points in INT8 vs FP16, ship FP16
- FP16 model size measured and recorded; if >50MB, proceed to TASK-6a-6 distillation

---

#### TASK-6a-6: Knowledge distillation (conditional)

*Run only if FP16 model exceeds 50MB after TASK-6a-5.*

**Requires:** TASK-6a-4 complete

Train a YOLO11-Nano student model using the YOLO11-Medium as teacher via response-based distillation (match output logits). Target: student model < 50MB while maintaining mAP within 5 points of the teacher.

**AC:**
- Student model < 50MB
- Student mAP@0.5 ≥ teacher mAP - 5 points on withheld-template test
- Student model passes the same physical device benchmark targets as Phase 6 (< 200ms inference)

---

#### TASK-6a-7: Full evaluation and real-world validation

**Requires:** TASK-6a-4 or TASK-6a-6 complete

**AC (all must pass):**
- mAP@0.5 ≥ 0.85 on withheld-template test set (41 classes)
- No individual class AP < 0.65
- Content-agnostic test (blurred text): mAP for non-text classes drops < 10 points
- Centroid bias check (`centroid_distribution.py`): no class has `bias_flag: true`
- Per-template AP: no template AP > 0.95 when overall mAP < 0.85
- 200-image real-world validation set annotated; real-world mAP reported (not required to pass, but gap documented)
- Active learning loop: run prediction entropy on 1,000 new unlabeled generated images; identify top-5 high-uncertainty template families; document them for Phase 5b expansion if mAP gate not met
- Physical device benchmark: < 200ms inference, < 3s cold load, < 50MB

**Phase 6a gate (DS-G8):** All AC above pass.

---

## Phase 6b: tvOS Model

*Goal: Dedicated tvOS detector. Focus state paradigm and top-of-screen tab bar require separate training.*

**Requires:** Phase 6a gate passed  
**Parallel with:** Phase 6c

---

#### TASK-6b-1: tvOS coordinate validation

Before generating at scale, validate that the Phase 1 coordinate approach works correctly in tvOS Simulator. tvOS uses a different screen resolution (1920×1080 at @2x effective) and no safe area insets in the traditional sense.

**AC:**
- A simple tvOS SwiftUI fixture (Button + Label + focused card) passes the same ±2pt alignment test as Phase 1
- `isFocused: true` state is reflected in the annotation when the tvOS focus engine is on the element

---

#### TASK-6b-2: tvOS generator templates

**Files:** `NativeUIDatasetGenerator/Templates/tvOS/` (new directory, 5 templates)

| Template | Elements |
|---|---|
| tvOS shelf/card grid | `collectionItem` (focused + unfocused), `label`, `imageView` |
| tvOS top tab bar | `tabBar` (at top of screen), `label` |
| tvOS settings | `listRow`, `toggle`, `label`, `navigationBar` |
| tvOS playback controls | `slider`, `primaryButton`, `secondaryButton`, `label` |
| tvOS alert | `alert`, `primaryButton`, `cancelAction` |

Focus state sweep: each template generates one variant with `isFocused: true` on the primary interactive element.

**AC:**
- `tabBar` annotations appear in the **top 15% of image height** (not bottom) in all tvOS images
- `isFocused: true` set on the correct element; focus ring visible in spot-check
- ≥3,000 tvOS images generated
- `reports/tvos_balance.md` shows all tvOS classes present with ≥400 instances each

---

#### TASK-6b-3: Train and export `NativeUIModel_tvOS`

**Requires:** TASK-6b-2 complete

Train using the same YOLO11 approach as Phase 6a (same scripts, different dataset split).

**AC:**
- mAP@0.5 ≥ 0.80 on tvOS withheld-template test set
- `tabBar` AP ≥ 0.80 (critical: must not confuse top-of-screen tab bar with toolbar)
- Model < 50MB, inference < 200ms on Apple TV 4K hardware (or tvOS Simulator as proxy)
- Exported to `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIDetector_tvOS_v1.mlpackage`

---

## Phase 6c: macOS Model

*Goal: Dedicated macOS detector, including AppKit coordinate flip validation.*

**Requires:** Phase 6a gate passed  
**Parallel with:** Phase 6b

---

#### TASK-6c-1: macOS coordinate spike

**File:** `CoordinateSpike/macOS/MacCoordSpikeView.swift` (new)

Validate AppKit coordinate handling. AppKit uses bottom-left origin; the generator must flip Y before writing annotation JSON.

Spike fixture: an `NSViewController` with 3 `NSView` subviews at known frames. Export via `view.convert(subview.frame, to: nil)` and apply Y-flip: `y_flipped = window.contentView.bounds.height - frame.origin.y - frame.height`.

**AC:**
- Y-flipped coordinates match top-left pixel positions in a PNG rendered via `NSBitmapImageRep` within ±2pt
- `testMacOSCoordinateFlip` test passes on macOS 15 Simulator

---

#### TASK-6c-2: macOS generator templates + training

**Files:** `NativeUIDatasetGenerator/Templates/macOS/` (new)

Templates: document window with NSToolbar, settings panel (`NSOutlineView`-style), two-column split view with sidebar, NSAlert.

**AC:**
- ≥2,000 macOS images with Y-axis flipped coordinates
- mAP@0.5 ≥ 0.80 on macOS withheld-template test set
- `tooltip` AP ≥ 0.70 (pointer-hover tooltips are macOS-specific)
- Exported to `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIDetector_macOS_v1.mlpackage`

---

## Phase 7: OCR Fusion & Audit Rules

*Goal: Visible text in `NativeUIElementObservation`, and 4 audit issue rules active.*

**Requires:** Phase 6 gate passed (live model returning observations)

---

#### TASK-7-1: `VNRecognizeTextRequest` pass

**File:** `Sources/NativeUIAuditKit/Detection/NativeUIDetectionRequest.swift`

Add a second Vision request running after the CoreML detector, using `.accurate` recognition level and `.english` + device locale languages.

**AC:**
- `testOCRFusionSmoke`: a screenshot of a button labeled "Continue" returns an observation with `visibleText == "Continue"` (or close match)
- OCR runs off the main actor
- When `NativeUIDetectionConfiguration.recognizesText == false`, OCR pass is skipped and `visibleText` is nil on all observations

---

#### TASK-7-2: Observation merger

**File:** `Sources/NativeUIAuditKit/Detection/ObservationMerger.swift` (new)

Implement the text-to-element association algorithm from `Research/OCRFusionPolicy.md`:
- For each OCR text observation, find the element with highest IoU ≥ 0.10
- Concatenate associated text in reading order → `visibleText`
- 9 element types that never receive text association: toggle, slider, imageView, mapView, activityIndicator, progressView, pageControl, scrollIndicator, colorWell

**AC:**
- `testMergerMultipleTextRegions`: 3 OCR text regions, 2 elements → correct assignment based on IoU
- `testMergerNoTextElements`: toggle and slider observations never receive `visibleText` even when OCR text is nearby
- `testMergerReadingOrder`: text regions merged in top-to-bottom order for LTR layout

---

#### TASK-7-3: Audit rules implementation

**File:** `Sources/NativeUIAuditKit/Audit/AuditRules.swift` (new)

Implement 4 `NativeUIIssue` detection rules, each as a pure function `(NativeUIElementObservation, CGSize) -> NativeUIIssue?`:

| Rule | Condition |
|---|---|
| `.truncatedText` | `visibleText` ends with `…` (U+2026) AND OCR box width < element `boundsPixels.width × 0.85` |
| `.clippedElement` | Any edge of `boundsPixels` is within 2px of the image boundary |
| `.tappableTargetTooSmall` | `boundsPoints.width < 44 \|\| boundsPoints.height < 44` — only for interactive classes (primaryButton, secondaryButton, destructiveButton, cancelAction, toggle, textField, secureField, searchField, menuButton, link, colorWell) |
| `.overlappingElements` | IoU > 0.10 between this observation and any other observation in the result set |

**AC:**
- Each rule has at least 2 unit tests: one that fires the rule, one that does not
- `.tappableTargetTooSmall` does NOT fire on `label`, `imageView`, `statusBar`, or any chrome element
- `.overlappingElements` is symmetric: if A overlaps B, both A and B receive the issue
- All 4 rules use the known-bad fixture images from Phase 5 as integration test inputs

---

## Phase 8: Device & OS Inference

*Goal: `NativeUIDeviceInference` from heuristics for sidecar-less screenshots.*

**Requires:** Phase 7 complete  
**Note:** Phases 8 and 7 can be developed in parallel for the heuristic rules (Phase 8 has no ML dependency)

---

#### TASK-8-1: Device dimension database

**File:** `Sources/NativeUIAuditKit/Detection/DeviceDimensionDatabase.swift` (new)

Build a lookup table of known device screenshot dimensions → device candidates. Sourced from Apple's human interface guidelines and public device specs.

```swift
struct DeviceDimension {
    let widthPx: Int    // portrait width in pixels
    let heightPx: Int
    let scale: Int      // 2 or 3
    let candidates: [String]   // device model names
    let platform: NativeUIPlatform
}
```

Must include: all iPhone models from SE (1st gen) to current, all iPad models, Apple TV (1920×1080), MacBook common resolutions.

**AC:**
- An iPhone 15 Pro screenshot (1179×2556 @3x) resolves to candidates containing "iPhone 15 Pro" and "iPhone 15 Pro Max"
- An iPhone SE (750×1334 @2x) resolves to candidates for SE models only
- An Apple TV screenshot (1920×1080 @2x) resolves to tvOS candidates
- A 1440×900 macOS screenshot resolves to macOS candidates
- Ambiguous dimensions (shared between multiple models) return multiple candidates, not a single guess

---

#### TASK-8-2: `NativeUIDeviceInference` implementation

**File:** `Sources/NativeUIAuditKit/Detection/DeviceInference.swift` (new)

```swift
public func inferDevice(from image: CGImage, sidecar: NativeUISidecar?) -> NativeUIDeviceInference
```

If sidecar is present and `imageSHA256` matches: return exact device/platform from sidecar metadata.

If pixel-only:
1. Dimension lookup → initial candidate list
2. Status bar height detection (Vision rectangle detector on top 10% of image) → refine candidates
3. Home indicator presence (scan bottom 5% of image for pill shape) → filter to face-ID devices
4. Dynamic Island presence (scan top 5% for pill cutout) → filter to Pro devices with Dynamic Island

Return `NativeUIDeviceInference` with ranked candidates sorted by confidence descending.

**AC:**
- Sidecar path: `inferDevice(from:, sidecar: validSidecar).platform == .iOS` and `candidates[0].confidence == 1.0`
- Pixel-only path for an iPhone 15 Pro screenshot: top candidate is an iPhone with Dynamic Island
- Never returns a single hard guess — always returns `candidates` array with ≥1 element
- All returned `confidence` values sum to ≤1.0

---

## Phase 9: ScreenAuditKit Integration

*Goal: `NativeUIRecognizing` protocol wired into ScreenAuditKit.*

**Requires:** Phase 7 complete

---

#### TASK-9-1: `NativeUIRecognizing` protocol

**File:** `Sources/NativeUIAuditKit/Integration/NativeUIRecognizing.swift` (new)

```swift
public protocol NativeUIRecognizing: Sendable {
    func recognizeNativeUI(
        inPNGData data: Data,
        path: String,
        sidecar: NativeUISidecar?
    ) throws -> NativeUIObservations
}

public struct NativeUIObservations: Sendable {
    public let elements: [NativeUIElementObservation]
    public let status: NativeUIRecognitionStatus
}

public enum NativeUIRecognitionStatus: Sendable {
    case success
    case notRequested
    case notAvailable   // model not installed
    case failed(Error)
}

public struct NativeUINoOpRecognizer: NativeUIRecognizing {
    public init() {}
    public func recognizeNativeUI(inPNGData:path:sidecar:) throws -> NativeUIObservations {
        NativeUIObservations(elements: [], status: .notRequested)
    }
}
```

**AC:**
- Protocol, `NativeUIObservations`, `NativeUIRecognitionStatus`, and `NativeUINoOpRecognizer` all compile under Swift 6 strict concurrency
- `NativeUINoOpRecognizer` always returns `status: .notRequested` — never throws
- All types are `Sendable`, `Codable` where appropriate

---

#### TASK-9-2: ScreenAuditKit contract extension

*Implementation details depend on ScreenAuditKit's existing contract structure — see `../ScreenAuditKit/` for current API.*

Add to `ScreenAuditScreenContract`:
```json
{
  "uiElements": {
    "required": [{ "label": "primaryButton", "region": "bottomCTA" }],
    "forbidden": [{ "label": "alert" }],
    "minConfidence": 0.75
  }
}
```

New rule IDs: `missingUIElement`, `unexpectedUIElement`, `uiElementBoundsViolation`, `uiElementTruncated`, `uiElementClipped`, `uiElementTargetTooSmall`, `inferredOSMismatch`.

**AC:**
- All 7 rule IDs appear in a validation report when the corresponding conditions are met
- `NativeUINoOpRecognizer` causes all `uiElements` contract fields to be skipped silently (no false failures)
- Existing ScreenAuditKit tests continue to pass

---

#### TASK-9-3: CLI flag

Add `--native-ui none|coreml` to `screenaudit validate`. Default: `none`. When `coreml` is specified and `NativeUIAuditKitModels` is not installed, print a clear error with installation instructions and exit 1.

**AC:**
- `screenaudit validate --native-ui none` behaves identically to current behavior
- `screenaudit validate --native-ui coreml` without model package installed prints: `NativeUIAuditKitModels is not installed. Run: ...` and exits 1
- `--help` output documents both values

---

## Extraction Readiness Checklist

Before moving `NativeUIAuditKit` to its own public repository:

- [ ] No RA11y-specific code, paths, or terminology in `Sources/NativeUIAuditKit/`
- [ ] `swift build` and `swift test` pass standalone (no workspace)
- [ ] `README.md` includes integration guide for a non-RA11y project
- [ ] `LICENSE` file added (license decision made)
- [ ] `NativeUIAuditKitModels` package structure fully defined
- [ ] At least one non-RA11y test scenario documented
- [ ] `AGENTS.md`-compatible
- [ ] `Research/TrainingDataStrategy.md` current and reviewed
- [ ] `Research/schemas/annotation.schema.json` tagged v1.0
- [ ] `Research/schemas/category_map.json` stable (IDs frozen)
