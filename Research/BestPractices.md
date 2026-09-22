# NativeUIAuditKit — Best Practices

Lessons learned from building and running the spike experiments. Each entry describes a mistake or inefficiency encountered, the correct approach, and why it matters.

---

## SwiftUI Layout & Coordinate Capture

### BP-01: Use padding-based layout, never `.offset()`, when coordinates must be measured

**Wrong:**
```swift
Button("Label") {}
    .frame(width: 200, height: 44)
    .offset(x: 40, y: 100)               // shifts visual position only
    .background(frameReader(id: "btn"))   // reads pre-offset layout frame → (0, 0, 200, 44)
```

**Correct:**
```swift
Button("Label") {}
    .frame(width: 200, height: 44)
    .background(frameReader(id: "btn"))   // reads layout frame
    .padding(.top, 100)
    .padding(.leading, 40)                // layout frame shifts to (40, 100, 200, 44) ✓
```

**Why:** `.offset()` repositions the view visually without changing its layout frame. `GeometryReader` reads the layout frame, not the visual position. This means a view placed with `.offset()` reports its origin as `(0, 0)` regardless of where it appears on screen.

**Impact:** If the generator uses `.offset()` for any element placement, every exported coordinate will be wrong by exactly the offset amount.

---

### BP-02: Apply `.ignoresSafeArea(.all)` to the top-level ZStack, not just the background Color

**Wrong:**
```swift
ZStack(alignment: .topLeading) {
    Color.white.ignoresSafeArea()  // only the Color ignores safe area
    // elements...
}
// ZStack still respects safe area — all y-values shift by status bar height
```

**Correct:**
```swift
ZStack(alignment: .topLeading) {
    Color.white
    // elements...
}
.ignoresSafeArea(.all)  // ZStack itself ignores safe area → origin = screen top-left
```

**Why:** `.ignoresSafeArea()` on a child view only affects that child's layout. The parent `ZStack` still clips its layout to the safe area boundary, so all padding-based positions start below the status bar. Applying `.ignoresSafeArea(.all)` to the container pins the coordinate origin to the physical screen top-left.

**Measured safe area insets (2026):**
- iPhone 17 Pro (Dynamic Island): **62 pt**
- iPhone SE 3rd gen (home button): **20 pt**

**Impact:** Without this fix, all exported y-coordinates are off by the device's status bar height — a systematic bias that would corrupt every annotation in the dataset.

---

### BP-03: GeometryReader reports layout frame, not visible clipped rect

**Behavior:** When a child element overflows a `.clipped()` container, `GeometryReader` on the child reports the child's full layout frame, not the visible cropped area.

**Example:** Child 240×120 pt inside a 120×60 pt `.clipped()` container → `GeometryReader` returns `(x, y, 240, 120)`, not `(x, y, 120, 60)`.

**Generator requirement:** After reading `GeometryReader` frames, intersect each element's rect with its parent container's bounds when the container uses `.clipped()` or `clipsToBounds = true`. The visible annotation is the intersection, not the raw layout frame.

```swift
let visibleRect = elementFrame.intersection(containerFrame)
```

---

### BP-04: Wait at least 150ms (one RunLoop pass) after layout before capturing frames

**Why:** SwiftUI's preference propagation (`onPreferenceChange`) runs during the layout pass, but the actual draw pass that writes pixels can lag behind. `GeometryReader` values are stable after one RunLoop cycle.

**Correct pattern (async context):**
```swift
hostingController.view.layoutIfNeeded()
try await Task.sleep(for: .milliseconds(150))
// Now safe to read frames and capture screenshot
```

**Verified:** Frames are identical between two consecutive layout passes 150ms apart at both @2x and @3x. No animation frame lag observed in static layouts.

---

## Testing Strategy

### BP-05: Test the actual generator mechanism, not a proxy

**Wrong:** Using `XCUIElement.frame` (accessibility frame) as ground truth for the generator, when the generator will use `UIHostingController` + `GeometryReader`.

**Why it's wrong:**
- `XCUIElement.frame` reads the accessibility frame, which can differ from the visual bounding box for UIKit-backed elements
- It validates a proxy — if the proxy is accurate, that doesn't prove the real mechanism is accurate
- XCUITest introduces a separate process and process-boundary serialization that adds latency and potential for frame-read timing issues
- It relies on private APIs for screen scale (`app.value(forKey: "screenScale")`) that can break across OS updates

**Correct:** Use hosted unit tests that render with `UIHostingController` and capture with `UIGraphicsImageRenderer` — exactly the mechanism the generator will use in production.

```swift
@MainActor
final class MyGeneratorTests: XCTestCase {
    func testCoordinates() async throws {
        let hc = UIHostingController(rootView: MyView(onFramesCaptured: { ... }))
        // set up off-screen window, wait for preference propagation
        // assert GeometryReader values match declared positions
    }
}
```

---

### BP-06: Use `fulfillment(of:timeout:)` not `RunLoop.main.run(until:)` in async test contexts

**Wrong (causes Swift 6 compiler error in async context):**
```swift
func testSomething() async throws {
    // ...
    RunLoop.main.run(until: Date(timeIntervalSinceNow: 0.15))  // ❌ unavailable in async
}
```

**Correct:**
```swift
func testSomething() async throws {
    let expectation = XCTestExpectation(description: "frames")
    // ...
    await fulfillment(of: [expectation], timeout: 2.0)  // non-blocking async wait ✓
}
```

`RunLoop.main.run(until:)` is only valid in synchronous test methods. In `async` test methods (including `@MainActor` classes), use `fulfillment(of:timeout:)` or `Task.sleep(for:)`.

---

### BP-07: Mark test classes `@MainActor` when they interact with UIKit/SwiftUI

UIKit and SwiftUI rendering must happen on the main thread. Instead of sprinkling `DispatchQueue.main.async` throughout tests, mark the entire test class:

```swift
@MainActor
final class CoordSpikeHostedTests: XCTestCase { ... }
```

This ensures every test method, setup, and teardown runs on the main actor automatically, eliminating a class of threading bugs in test infrastructure.

---

## Xcode Project Structure

### BP-08: Hand-authored `.xcodeproj` is viable for minimal spike projects

When `xcodegen` is unavailable, a minimal `project.pbxproj` can be hand-authored with:
- `objectVersion = 60` (Xcode 15+ compatible)
- `LastUpgradeCheck = 2640` (Xcode 26.4)
- No explicit framework references needed — system frameworks (UIKit, SwiftUI) link automatically via `SDKROOT = iphoneos`
- `GENERATE_INFOPLIST_FILE = YES` for test targets eliminates the need for a manual Info.plist
- `CODE_SIGNING_ALLOWED = NO` + `CODE_SIGN_STYLE = Manual` enables simulator-only builds without a provisioning profile

**Key test target settings for `@testable import`:**
```
TEST_HOST = "$(BUILT_PRODUCTS_DIR)/CoordSpikeRunner.app/$(BUNDLE_EXECUTABLE_FOLDER_PATH)/CoordSpikeRunner"
BUNDLE_LOADER = "$(TEST_HOST)"
```

---

### BP-09: Nested class in a generic function is a Swift compiler error

**Wrong:**
```swift
private func captureFrames<V: View>(_ view: V) async throws -> [String: CGRect] {
    final class Box<T>: @unchecked Sendable { ... }  // ❌ cannot nest generic class in generic func
}
```

**Correct:** Hoist the helper class to file scope, or restructure to avoid it entirely. For the coordinator pattern, `@Sendable` closures with captured `var` values work in simple `@MainActor` contexts without a `Box` wrapper.

---

## Coordinate System Conversions

### BP-10: Always carry all three coordinate representations in annotations

Every annotation must store all three forms. Do not derive on demand — derivation at read-time risks wrong scale assumptions.

| Field | Formula | Origin |
|-------|---------|--------|
| `boundsPoints` | `GeometryReader` output | Top-left |
| `boundsPixels` | `boundsPoints × UIScreen.main.scale` | Top-left |
| `boundsVisionNormalized` | See below | Bottom-left |

**Vision-normalized formula:**
```
x_norm = x_px / screenWidth_px
y_norm = 1.0 - (y_px + height_px) / screenHeight_px
w_norm = width_px  / screenWidth_px
h_norm = height_px / screenHeight_px
```

The y-axis flip (`1.0 - ...`) is the most common source of annotation bugs when integrating with Vision. Test this formula explicitly (see `testVisionNormalizedConversion`).

---

### BP-11: `UIScreen.main.scale` is the only scale source to use in the generator

Do not hardcode `2.0` or `3.0`. Do not read scale from `UITraitCollection`. Use `UIScreen.main.scale` at capture time.

`UIGraphicsImageRenderer` uses `UIScreen.main.scale` by default — this means rendered PNG pixel dimensions equal `view.bounds.size × UIScreen.main.scale` automatically. No manual scale management is needed for rendering; only for coordinate conversion.

---

## Process & Research

### BP-12: Run the simplest possible test first — the spike revealed a critical design flaw before any data was generated

The `.offset()` layout bug and the safe area origin shift would have corrupted every annotation in the dataset if discovered during Phase 3 rather than Phase 1. The coordinate spike's value is not the tests themselves — it is forcing the design to be proven correct before automation.

**Lesson:** When building a coordinate-dependent pipeline, instrument the coordinate capture mechanism with a fixture that has ground truth by construction (fixed layout, known values), and run it before writing any generation code.

---

### BP-13: Document findings immediately in `Research/` — don't rely on test output

Test output is transient. The `.xcresult` bundle is not committed. The `Research/CoordinateSpike.md` results tables are the permanent record. Fill them in as soon as tests pass, before moving on.

**Minimum to capture per run:**
- Simulator: model, OS version, scale factor, screen size in pt and px
- Max edge delta across all elements (or individual deltas if any are non-zero)
- Any behavioral finding (safe area shift amount, clipping behavior, animation stability window)
- Test pass/fail status

---

### BP-14: Retire code that tests the wrong thing rather than fixing it

`CoordSpikeUITests.swift` was not broken — it was testing the wrong mechanism. The correct action was to retire it and replace it with `CoordSpikeHostedTests.swift`, which tests the actual production path.

**Principle:** A test that passes but validates a proxy for the real behavior gives false confidence. It is more dangerous than no test. When a test's mechanism diverges from the production mechanism, retire it.

---

### BP-15: Never use compiler flags to paper over a platform mismatch in view code


**Problem:** SwiftUI templates written for iOS were placed in the macOS SPM target. The resulting `#if canImport(UIKit)` / `#if os(iOS)` guards spread through every view file, obscuring intent and creating permanent maintenance debt.

**Root cause:** Putting iOS-only files in a multi-platform SPM target forces every iOS API call to be guarded individually. Method chaining breaks at guard boundaries. `EmptyView()` stubs must be maintained as false alternatives.

**Rule:** Platform-specific view code belongs in a platform-specific target. Shared data types belong in a platform-agnostic module.

**Applied architecture for the dataset generator:**

| Layer | Location | Platform | Content |
|-------|----------|----------|---------|
| Shared types | `NativeUIDatasetGenerator/Sources/CaptureTypes.swift` | macOS SPM | `AnnotatedElement`, `CaptureResult`, `ScreenshotCaptureError` |
| macOS orchestrator | `NativeUIDatasetGenerator/Sources/` | macOS SPM | `AnnotationWriter`, `DatasetManifest`, `BalanceReport`, `GeneratorConfig`, etc. |
| iOS capture + templates | `NativeUIDatasetGenerator/Templates/` | iOS Xcode project | `ScreenshotCapture`, `FramePreference`, all `*Template` views |

The iOS Xcode project (`GeneratorRunner`) references the shared `Sources/` Swift files by relative path — the same pattern `CoordSpikeRunner` uses. The SPM target declares `exclude: ["Templates"]` so it never sees the iOS-only files.

**Result:** Zero `#if` guards in any view file. Each file compiles cleanly in its intended context.

---

## XCTest Artifact Extraction

### BP-16: Use `xcresulttool` object-graph traversal, not SQLite, to extract XCTAttachments

The `.xcresult` bundle format changed in Xcode 16. Prior to Xcode 16, bundles contained a `database.sqlite3` file with an `Attachments` table that could be queried directly. From Xcode 16 onward, the bundle uses an opaque `Data/` blob store — no SQLite file is present.

**Wrong (breaks on Xcode 16+):**
```bash
sqlite3 "$XCRESULT/database.sqlite3" \
  "SELECT filenameOverride || '|' || xcResultKitPayloadRefId FROM Attachments WHERE uniformTypeIdentifier = 'public.png';"
```

**Correct (works across all versions):**
```bash
# 1. Get the root JSON
xcrun xcresulttool get --legacy --path "$XCRESULT" --format json

# 2. Navigate: root → ActionRecord.actionResult.testsRef
# 3. For each ActionTestMetadata, follow summaryRef
# 4. Collect ActionTestAttachment.payloadRef.id values
# 5. Export each:
xcrun xcresulttool export object --legacy \
    --path "$XCRESULT" --id "$REF_ID" \
    --output-path out.png --type file
```

**Key path through the object graph:**
```
ActionsInvocationRecord
  └─ actions[]
       └─ ActionRecord.actionResult.testsRef     → (fetch with --id)
            └─ ActionTestPlanRunSummaries
                 └─ summaries[].testableSummaries[].tests[]
                      └─ ActionTestMetadata.summaryRef   → (fetch with --id)
                           └─ ActionTestSummary
                                └─ activitySummaries[].attachments[]
                                     └─ ActionTestAttachment.payloadRef.id
```

See `scripts/_xcresult_attachments.py` for the full implementation. The `--legacy` flag is required in Xcode 16+; omitting it causes the command to exit 64.

---

## Bounding Box Capture

### BP-17: Capture chrome element frames via UIKit hierarchy scan, not `.captureFrame` on container views

**Problem:** Attaching `.captureFrame(id: "navigationBar")` to a `NavigationStack` or `.captureFrame(id: "tabBar")` to a `TabView` produces a frame covering the entire container (essentially the full screen height), not the chrome strip.

**Why it happens:** `.captureFrame` uses a `background(GeometryReader)` that reads the view's layout frame. `NavigationStack` and `TabView` fill their entire allocated space — the nav bar and tab bar chrome are *rendered inside* these containers by UIKit, not exposed as discrete SwiftUI views.

**Correct approach:** After layout stabilises, walk the UIKit view hierarchy from `hosting.view` to locate `UINavigationBar` and `UITabBar` instances, then convert their bounds to the hosting view's coordinate space:

```swift
private static func detectChromeFrames(in hostingView: UIView) -> [String: CGRect] {
    var result: [String: CGRect] = [:]
    func walk(_ view: UIView) {
        guard !view.isHidden, view.alpha > 0.01 else { return }
        switch view {
        case let navBar as UINavigationBar:
            if result["navigationBar"] == nil {
                result["navigationBar"] = navBar.convert(navBar.bounds, to: hostingView)
            }
        case let tabBar as UITabBar:
            if result["tabBar"] == nil {
                result["tabBar"] = tabBar.convert(tabBar.bounds, to: hostingView)
            }
            // Divide the bar width evenly using UITabBar.items?.count.
            // iOS always distributes tab items uniformly, so this gives accurate
            // bounding boxes without navigating private UIKit view hierarchies.
            // Note: On iOS 26 Liquid Glass, UITabBarButton subviews are no longer
            // UIControl instances — class-based subview filtering is unreliable.
            // UITabBar.items is a stable public API that works across all versions.
            let tabBarGlobalFrame = result["tabBar"]!
            let itemCount = tabBar.items?.count ?? 0
            if itemCount > 0 {
                let itemWidth = tabBarGlobalFrame.width / CGFloat(itemCount)
                for i in 0..<itemCount {
                    result["tabBarItem_\(i)"] = CGRect(
                        x: tabBarGlobalFrame.minX + CGFloat(i) * itemWidth,
                        y: tabBarGlobalFrame.minY,
                        width: itemWidth,
                        height: tabBarGlobalFrame.height
                    )
                }
            }
        default: break
        }
        view.subviews.forEach { walk($0) }
    }
    walk(hostingView)
    return result
}
```

`detectChromeFrames` is called after the 150 ms stabilisation wait and its results are merged into `capturedFrames`, overwriting any template-level `.captureFrame` values for the same keys.

**Do not place `.captureFrame(id: "navigationBar")` or `.captureFrame(id: "tabBar")` in templates** — those keys are now owned by the UIKit scan.

---

### BP-18: Place `.captureFrame` before layout-spacing padding, not after

`.captureFrame` adds a `background(GeometryReader)` that reads the frame of the view it wraps. Applying it *outside* a `.padding()` modifier means the GeometryReader measures the padded container (including the whitespace), not the element's visual boundary.

**Wrong — captures frame including the 16 pt margins:**
```swift
Slider(value: $v)
    .padding(.horizontal, 16)
    .captureFrame(id: "slider_0")   // reads padded container → x ≈ 0, w ≈ 393
```

**Correct — captures the slider's own visual frame:**
```swift
Slider(value: $v)
    .captureFrame(id: "slider_0")   // reads slider frame → x = 16, w = 361
    .padding(.horizontal, 16)
```

**Rule:** `.captureFrame` is always the innermost annotation modifier. Any `.padding`, `.clipShape`, or other layout modifier that adds space *around* the element goes outside it.

---

### BP-19: Use the OSVisualProfile's canonical screen size for the rendering window, not `UIScreen.main.bounds`

**Problem:** In a hosted `XCTest` context, `UIScreen.main.bounds` returns the simulator's *reported* logical resolution, which can differ from the device's specification. On the iPhone 17 Pro simulator running iOS 26, `UIScreen.main.bounds` was observed to return `320×480pt` instead of the expected `393×852pt`. This caused UIKit chrome (UINavigationBar, UITabBar) to be positioned incorrectly relative to the off-screen rendering window, producing wrong frame coordinates for `detectChromeFrames`.

**Symptoms:**
- `navigationBar` reported with an unrealistically large height (e.g. 335pt for a 480pt-tall canvas)
- `tabBar` positioned at the top of the screen (y ≈ 62pt) instead of the bottom

**Correct approach:** Store a `screenSize: CGSize` on `OSVisualProfile` and pass it explicitly to `ScreenshotCapture.capture` via `windowSize`. Never rely on `UIScreen.main.bounds` for the off-screen rendering window:

```swift
// OSVisualProfile predefined profile:
public static let ios26 = OSVisualProfile(
    ...
    screenSize: CGSize(width: 393, height: 852)   // iPhone 17 Pro logical resolution
)

// ScreenshotCapture.capture:
let canonicalSize = windowSize ?? config.osProfile.screenSize
let bounds = CGRect(origin: .zero, size: canonicalSize)
```

**Also:** use `config.pixelScale` (from `GeneratorRunConfig`) for `UIGraphicsImageRendererFormat.scale` rather than `UIScreen.main.scale`. This ensures images rendered with an ios17-profile config come out @2x (750×1334px) even when the simulator hardware is @3x.

**Verified canonical sizes:**

| Profile | Logical size | Scale | Output pixels |
|---|---|---|---|
| ios17 (iPhone SE 3rd gen) | 375×667pt | @2x | 750×1334px |
| ios26 (iPhone 17 Pro) | 393×852pt | @3x | 1179×2556px |

---

### BP-20: Never use the capture-frame ID as the element type — always derive `elementType` from the ID prefix

**Problem discovered:** `ScreenshotCapture.swift` originally passed `elementType: id` when constructing `AnnotatedElement` from SwiftUI `captureFrame` results:

```swift
// WRONG — stores full ID ("cancelAction_alert", "label_title") as the class
let elements = capturedFrames.map { id, frame in
    AnnotatedElement(id: id, elementType: id, frame: frame)
}
```

Templates use descriptive IDs like `cancelAction_alert`, `label_title`, `slider_0`, `imageView_hero`. When `elementType` is set to the full ID, the manifest's `classDistribution` accumulates hundreds of spurious keys (`cancelAction_alert`, `cancelAction_0`, `label_title`, `label_section_header` …) instead of the 41 canonical class names. This corrupts training labels and makes dataset balance analysis meaningless.

**Root cause:** The element ID and the element type serve different purposes. The ID is a unique locator within a template render; the type is the canonical model class. Templates should (and do) follow the convention `{elementType}_{descriptor}` — the type is always the camelCase prefix before the first underscore.

**Correct approach:** Strip the suffix at the single point where `AnnotatedElement` is constructed in the SwiftUI capture path:

```swift
// CORRECT — extracts canonical class from the ID convention
let elements = capturedFrames.map { id, frame in
    let elementType = id.components(separatedBy: "_").first ?? id
    return AnnotatedElement(id: id, elementType: elementType, frame: frame)
}
```

**ID naming convention (mandatory for all templates):**

| ID pattern | Derived `elementType` | Notes |
|---|---|---|
| `slider_0`, `slider_1` | `slider` | Numeric suffix for multiple instances |
| `label_title`, `label_body` | `label` | Descriptive suffix to distinguish roles |
| `cancelAction_alert` | `cancelAction` | Context suffix |
| `primaryButton_alertOK` | `primaryButton` | Role suffix |
| `navigationBar`, `tabBar` | `navigationBar`, `tabBar` | Pure class names (no suffix) — still correct after split |
| `imageView_hero` | `imageView` | Named region |

IDs that do not start with a canonical class name will produce incorrect element types. All template authors must prefix the ID with the exact canonical class string.

**Detection:** After any generation run, verify `manifest.classDistribution` has ≤ 41 keys and none contain a `_` (except `tabBarItem` which is a canonical class name). A classDistribution with hundreds of keys is diagnostic of this bug.

**Impact of getting this wrong:** If an entire generation run completes with the bug active, all annotation JSONs have wrong `elementType` values. The only safe recovery is to fix the source and re-run — post-hoc patching of thousands of JSON files outside the project is error-prone and not reproducible.

---

### BP-21: Clamp all four Vision-normalized coordinates to [0,1] and shrink dimensions to keep the far edge ≤ 1

**Problem discovered:** `AnnotationWriter.swift` applied `max(0, yNorm)` to clamp the Vision y-coordinate but left `xNorm` unclamped. When `ToolbarActionsTemplate` placed toolbar buttons near the left screen edge, UIKit's auto-centering produced frames with `minX` slightly less than zero (e.g., -3.8pt for a 393pt-wide screen), yielding `xNorm ≈ -0.038`. These negative x values failed the QG-4 bounding-box validity gate.

**Root cause:** Elements that span the screen boundary (toolbar items, status bar corners, Dynamic Island at extreme seeds) produce frames whose logical coordinates extend slightly outside [0, screenWidth] × [0, screenHeight]. This is correct UIKit geometry — the element is physically there — but Vision-normalized coordinates are defined on [0,1]×[0,1] and must be clipped.

**Correct approach:** After computing raw normalized values, clamp origin to [0,1] and then shrink the dimension so the far edge also stays ≤ 1:

```swift
let xNorm = max(0.0, min(1.0, xNormRaw))
let yNorm = max(0.0, min(1.0, yNormRaw))
// Shrink so far edge stays within bounds after origin clamp
let wNorm = max(0.0, min(wNormRaw, 1.0 - xNorm))
let hNorm = max(0.0, min(hNormRaw, 1.0 - yNorm))
```

**Do not** clamp only `y` and leave `x` unclamped. Do not clamp `x` without also adjusting `width`.

**Detection:** Run `DatasetQualityAuditTests/testQG4_boundingBoxValidity` — it checks `x < 0`, `y < 0`, `x+w > 1`, `y+h > 1` with a 0.001 tolerance. Any generation run should produce zero QG-4 violations. The template most likely to trigger this is any template that uses `UIToolbar` with tightly-packed items (e.g., `ToolbarActionsTemplate`).

---

### BP-22: `MLObjectDetector` uses `objectPrint`, NOT `scenePrint`

**Problem discovered:** The training plan specified `scenePrint(revision: 2)` as the feature extractor for object detection. This is wrong — `scenePrint` belongs to `MLImageClassifier`. `MLObjectDetector` has its own `FeatureExtractorType` enum with only one case: `.objectPrint(revision: Int = 1)`.

**Correct types:**
- Image classification: `MLImageClassifier.ModelParameters` → `featureExtractor: .scenePrint(revision: 1|2)`
- Object detection: `MLObjectDetector.ModelParameters` → `algorithm: .transferLearning(.objectPrint(revision: 1))`

**Correct `ModelParameters` init for MLObjectDetector (macOS 11+):**
```swift
let parameters = MLObjectDetector.ModelParameters(
    validation: .dataSource(valSource),
    batchSize: 32,
    maxIterations: 10_000,
    gridSize: CGSize(width: 13, height: 13),
    algorithm: .transferLearning(.objectPrint(revision: 1))
)
```

**Note:** The older 2-param init `init(validation:batchSize:maxIterations:)` exists but lacks `gridSize` and `algorithm` — use the full macOS 11 init instead.

---

### BP-23: `MLObjectDetector.DataSource` uses a single consolidated JSON, not per-image JSONs

**Problem discovered:** The first draft of `CreateMLExporter` wrote one JSON file per image (e.g., `img001.json` alongside `img001.png`). This matches what some third-party Create ML tutorials show, but the actual `MLObjectDetector.DataSource` cases are:
- `.directoryWithImagesAndJsonAnnotation(at:)` — ONE JSON file in the directory for ALL images
- `.directoryWithImages(at:annotationFile:)` — images in one dir, single JSON path passed explicitly

Using per-image JSONs with `.directoryWithImagesAndJsonAnnotation` causes a fatal crash at load time:
```
Fatal error: Expecting one JSON file with object annotations, found 4509.
```

**Correct approach:** Write a single `annotations.json` using `directoryWithImages(at:annotationFile:)`:
```json
[
  {
    "imagefilename": "img001.png",
    "annotation": [
      {"label": "button", "coordinates": {"x": 100, "y": 100, "width": 50, "height": 30}}
    ]
  }
]
```
Key names are `imagefilename` (not `image`) and `annotation` (not `annotations`).

**Annotation type:** coordinates are center-based pixels, top-left origin — match with:
```swift
.boundingBox(units: .pixel, origin: .topLeft, anchor: .center)
```

---

### BP-24: `MLObjectDetector` evaluation requires NORMALIZED annotation coordinates

**Problem discovered:** `MLObjectDetector.evaluation(on:)` does not accept an `annotationType` parameter. It reads coordinates from the annotation JSON and compares them against model predictions in normalized [0,1] space. If the annotation JSON contains raw **pixel** coordinates (e.g., `cx=590` for a 1179px-wide image), `evaluation(on:)` treats them as normalized values (`cx=590`), which are wildly out of bounds. The resulting IoU against the model's normalized predictions (e.g., `cx=0.5`) is effectively 0 for every box → mAP ≈ 0.

**Evidence:** Training with pixel coordinates, 10,000 iterations of objectPrint transfer learning, mAP@0.5 = 0.0018. Switching to normalized coordinates → retraining.

**Root cause:** `MLObjectDetector.init(trainingData:parameters:annotationType:)` uses `annotationType` to convert training annotation coordinates internally. But `evaluation(on:dataSource)` has no `annotationType` parameter — it assumes the annotation JSON uses the same coordinate format as the model output (normalized [0,1]).

**Correct approach:** Always export annotation JSON with **normalized [0,1]** coordinates. Use:
```swift
annotationType: .boundingBox(units: .normalized, origin: .topLeft, anchor: .center)
```

**Coordinate conversion (from our dataset's `boundsVisionNormalized`):**
```swift
// Vision: x=left, y=bottom (bottom-left origin, [0,1])
// Create ML normalized: cx, cy center-based top-left origin [0,1]
let cx = vn.x + vn.width  / 2
let cy = 1.0 - vn.y - vn.height / 2    // flip y-axis
```

**Note:** `boundsVisionNormalized` is already clamped to [0,1] (BP-21), making it the safest source for normalized coordinates. Do NOT compute normalized coords from pixel values + image dimensions — that requires reading PNG dimensions for every image.

---

### BP-25: Use `.scaleFill` for VNCoreMLRequest on objectPrint portrait images — `.scaleFit` causes ~2× width blowup

**Wrong:**
```swift
let req = VNCoreMLRequest(model: vnModel)
req.imageCropAndScaleOption = .scaleFit   // default — letterboxes portrait images
```

**Correct:**
```swift
let req = VNCoreMLRequest(model: vnModel)
req.imageCropAndScaleOption = .scaleFill  // matches Create ML training preprocessing
```

**Why it matters:** Create ML trains objectPrint models by stretching images to fill 299×299 (scale fill). When you run inference with `.scaleFit` instead, Vision letterboxes portrait images (e.g., 1179×2556 fills only 138px of the 299-wide input), but the model's predicted widths are still in the 299-wide training coordinate space. When Vision maps those predicted widths back to the original image, they appear ~2.17× too large (299/138 ≈ 2.17). This pushes IoU from 0.992 down to 0.457 — just below the 0.5 AP threshold — so every detection is a false positive and mAP@0.5 ≈ 0.

**Empirical verification (img_000409.png, alert class):**
- `.scaleFit` → predicted w=1.500, IoU=0.457 (miss)
- `.scaleFill` → predicted w=0.688, IoU=0.992 (TP)

**Corollary:** `MLObjectDetector.evaluation(on:)` uses `.scaleFit` internally and cannot be overridden — reported mAP is meaningless for non-square portrait screenshots. Use a custom eval loop with `.scaleFill` for accurate metrics.

**SAHI tiles:** Square 640×640 tiles are unaffected (both options are equivalent when aspect ratio = 1:1). Still, default to `.scaleFill` everywhere for consistency.

---

### BP-26: objectPrint YOLO anchors cannot regress extreme-aspect-ratio boxes — use horizontal strip tiling

**Symptom:** Per-class AP = 0.00 for `navigationBar` (w≈1.0, h≈0.063, ratio 16:1) and `textField` (w≈0.69, h≈0.032, ratio 21:1), even with 3,700+ training instances. The model emits 14,661 candidates for a pure-navigationBar validation image, but max confidence across all classes is 0.0024 — effectively zero. Classes with more typical aspect ratios train well: `alert` (2.7:1 → AP 0.91), `toggle` (3.6:1 → AP 0.60).

**Root cause:** Create ML's objectPrint uses a YOLO-style 13×13 detection grid with learned anchor boxes. Anchor assignment matches each GT box to the anchor with the highest center-IoU. For a 16:1 box (w=1.0, h=0.063), even a (0.5, 0.5) anchor gives center-IoU ≈ 0.11 — well below the ~0.4–0.5 assignment threshold. No anchor is ever matched → no gradient → the class is never learned, regardless of how many training instances exist.

**Fix — horizontal strip tiling (what was actually implemented):**

NOT square tiles. The actual fix uses overlapping horizontal strips at 22% of image height with 50% overlap stride. For a 1179×2556 image, each strip is 1179×562px. Parameters: `stripFraction = 0.22`, `stride = stripH / 2`.

For navigationBar (full width, near top of screen), in the strip's normalized coordinate space:
- width = 1.0 (unchanged — strip uses full image width)
- height = h_full × (imageH / stripH) = 0.063 × (2556/562) ≈ 0.286
- **Aspect ratio in strip space: ~3.5:1** (down from 16:1) — achieves anchor-assignment IoU > 0.4

For textField: **~2.5:1** in strip space. For primaryButton: **~2.0:1**.

Verified by `scripts/verify_strip_export.swift` (run smoke test before every training run):
- navigationBar strip AR: 1.83:1 ✓
- textField strip AR:      2.46:1 ✓
- primaryButton strip AR:  1.96:1 ✓

Full images are also included alongside strips (for alert and toggle coverage, which don't need strip treatment). Validation uses full images only — strips are a training-time augmentation only.

**Training data impact:** 18,563 total training records (4,509 full images + 14,054 strips) vs 4,509 without stripping.

**Inference impact:** Add a matching strip pass at inference time. The model was trained on strips, so it must also be evaluated on strips. Both `scripts/eval_map.swift` and `NativeUIDetectionRequest` run a dedicated horizontal strip pass (same parameters: 22% height, 50% overlap).

**Implemented in:** `NativeUITrainer/Sources/CreateMLExporter.swift` (`stripFraction` parameter), `Sources/NativeUIAuditKit/Detection/NativeUIDetectionRequest.swift` (`stripPass`), `scripts/eval_map.swift` (`stripPass` function).

**Do NOT evaluate a strip-trained model with only a full-image VNCoreMLRequest.** That will still show AP=0 for navigationBar and textField because the full-image pass suffers from the same anchor-assignment problem that training fixed. You must run the strip pass at eval time too.

---

### BP-27: Phase 6a splits must withhold entire template families — the generator 8:1:1 split is not a holdout

**Wrong:** Train YOLO11 on the generator's `train/` folder and report mAP on `test/`. Those folders are an 8:1:1 split *within each family* (QG-5). Every layout the model sees at test time was also seen at train time.

**Correct:** Move every image from a chosen set of families into `test/`, regardless of the original split. Train and validate only on the remaining families. Default holdout (Run 007): `CardDetail`, `WizardStepFlow`, `NotificationCenter`, `GalleryPage`, `MultiSectionForm`, `SettingsToggleDense`, `EmptyState`, `OnboardingPage`. Never withhold a family that is the unique source of a rare class (`ColorPicker` / colorWell, `MenuButton` / menuButton, `iPadSidebar` / sidebar, `MapOverlays` / mapView). `HardNegative_2` / WKWebView was retired from P0-C; do not claim `webContent` coverage from it.

**Why:** Phase 6a's gate is mAP on a withheld-template test. Measuring on the generator test split repeats Run 006's in-distribution number and does not answer the gate.

---

### BP-28: Drop generator labels that are not in the frozen 41-class taxonomy

**Wrong:** Train on every `elementType` string in the annotation JSON, including `tabBarItem`.

**Correct:** Keep only names in `Research/schemas/category_map.json`. `tabBarItem` is a chrome auto-detect artifact (parent `tabBar` is already labeled). Five taxonomy classes currently have 0 iOS instances (`statusBar`, `toolbar`, `scrollIndicator`, `tooltip`, `unknown`) — they stay in the 41-slot name list so IDs remain frozen, but they contribute no boxes until the generator covers them.

**Why:** Extra heads waste capacity and scramble the frozen ID map. Empty classes with reserved IDs are cheaper to fill later than a remapped taxonomy.

---

### BP-29: OHEM must keep YOLO dataset length constant — never append to `im_files` without resizing `ims`

**Wrong:** At `on_train_epoch_end`, append extra copies of hard images onto `dataset.im_files` and `dataset.labels` (11,504 → 13,804).

**Correct:** Replace easy-image slots with extra copies of the hard images so `len(im_files)` stays equal to the original `ni`. Reset `ims` / `im_hw0` / `im_hw` / `npy_files` to match. Call `train_loader.reset()` so workers pick up the new list.

**Why:** Ultralytics `BaseDataset.load_image` indexes `self.ims[i]` (sized once at init). `nb = len(train_loader)` is captured *once* before the epoch loop, but `SequentialSampler` (used with `rect=True`) uses live `len(dataset)`. After OHEM grows `labels`, epoch 2's loader yields more batches than `nb`. tqdm shows `2876/2876`, then the next index is `>= ni` → `IndexError: list index out of range`. Run 007 died at the end of epoch 2 this way. Same-length replacement keeps the sampler, `nb`, and `ims` aligned.

---

### BP-30: Resume Phase 6a from `last.pt` after a power cut; do not restart from `yolo11m.pt`

**Wrong:** After a reboot, run `train_ios_model.py` without `--resume`. That starts epoch 1 again and overwrites the run directory.

**Correct:** `last.pt` is only valid at epoch boundaries. Mid-epoch progress is lost. Resume with `--resume NativeUITrainer/yolo_runs/phase6a_r008/weights/last.pt` (script resolves this to an absolute path *before* `chdir` into `NativeUITrainer/weights`). If `last.pt` is unreadable (cut during the write), use `last.prev.pt`. Keep the machine awake with `caffeinate` and run `scripts/watch_phase6a.py` so a crash or logout restarts the resume loop until Ultralytics exits 0 (100 epochs or patience).

**Why:** Run 007 lost power mid-epoch 46. `results.csv` and `last.pt` had finished epoch 45 (best mAP50 = 0.984 at epoch 39). A fresh start would throw that away. The watchdog is how the run actually finishes unattended.

---

### BP-31: CoreML INT8 is linear weight quantize of the FP16 package — do not pass `data=` or `int8=True` to Ultralytics CoreML export

**Wrong:** `YOLO.export(format="coreml", int8=True, data="dataset.yaml")`. Ultralytics 8.4 rejects `data` for `format='coreml'`. `quantize=8` runs k-means palettization (`palettize_weights`) which SIGKILL'd YOLO11m at 0/227 ops. `int8=True` is deprecated.

**Correct:** Export FP16+NMS for on-device shipping (`nms=True` → pipeline). For INT8, export a second `nms=False` FP16 *mlprogram*, then `coremltools.optimize.coreml.linear_quantize_weights`. Do not quantize the NMS pipeline (`linear_quantize_weights` rejects type pipeline). Do not use Ultralytics `quantize=8` palettization on YOLO11m (SIGKILL at `palettize_weights` 0/227). Compare small-element AP on the two nms=False packages (Python NMS) for TASK-6a-5.

**Why:** CoreML INT8 is weight-only. Calibration `data` is an ONNX/OpenVINO concern. The shipped detector still uses the NMS FP16 package if INT8 drops small-element AP >5 pt or if FP16 is already under 50 MB.

---

### BP-32: Family holdout is a style test — non-zero train count is not enough

**Wrong:** Withhold `OnboardingPage` / `GalleryPage` / `WizardStepFlow` / `MultiSectionForm` because those families are not the unique *count* source of `pageControl` / `secondaryButton` / `textField`. KitchenSink still has 700 `pageControl` boxes; LoginForm still has `secondaryButton`.

**Correct:** Before withholding a family, every class it contains must appear in a **train family with similar chrome** (size, isolation, container). Run 007 holdout diagnosis (`reports/holdout_diagnosis_phase6a.json`):

| Class | Train+val | Test | What happened |
|---|---|---|---|
| `pageControl` | 700 | 600 | 97.5% miss. Train: packed 7pt circles + UIKit `UIPageControl`. Holdout: isolated onboarding/gallery dots. |
| `secondaryButton` | 3977 | 341 | 0% miss, 311/341 matched as `cancelAction` (Wizard "Back"). |
| `textField` | 2645 | 500 | 314/500 matched as `listRow` (Form-in-List). |
| `picker` / `secureField` / `stepperControl` | plenty | 200 | listRow confusion or miss on MultiSectionForm chrome. |
| `toolbar` | 0 | 0 | `detectChromeFrames` never saw `UIToolbar` from `.bottomBar`. |

A non-zero box count from a packed kitchen-sink or a toolbar *icon* does not train the holdout *style*.

**Why:** Val mAP 0.981 vs holdout mAP 0.358 is template-texture overfitting plus style zero-shot, not a missing-class unique-source violation (those were none).

---

### BP-33: Disable per-epoch snapshot I/O and metric plotting during MPS training

**Wrong:** Train with `save_period=1` and `plots=True`. This writes ~154 MB weights + optimizer snapshot every epoch (~15.4 GB across 100 epochs) and renders 41x41 confusion matrices and PR curves on CPU at every epoch boundary.

**Correct:** For production runs (Run 009+), set `save_period=-1` (or `5`) and `plots=False`. Keep `last.pt`, `best.pt`, and the `last.prev.pt` backup hook. Rely on `results.csv` for real-time loss/mAP tracking, and generate visual evaluation plots only after training finishes.

**Why:** Saves massive SSD write bandwidth, avoids disk exhaustion crashes (which killed Run 003/007), and eliminates CPU bottlenecks during validation epochs without affecting model accuracy.

---

### BP-34: Never glob or iterate flat directories containing >10k images on APFS — use line-delimited text manifests

**Wrong:** Call `os.listdir()`, `Path.glob("*")`, or `iterdir()` on `dataset/dataset/train` or other large flat export directories.

**Correct:** Generate line-delimited text manifests (`train.txt`, `val.txt`, `test.txt`) and configure YOLO/data pipelines to read directly from text file lists.

**Why:** Flat APFS directories containing >10,000 files cause extreme kernel metadata caching stalls on macOS, hanging Python scripts and blocking terminal execution. Text manifests bypass directory scanning entirely.

---

### BP-35: Reclaim host unified memory and size batches to Apple Silicon memory headroom

**Wrong:** Leave Simulator.app and Xcode open during training runs while keeping `batch=4` on a 24 GB or 32 GB Apple Silicon machine.

**Correct:** Close `Simulator.app` and idle Xcode instances before launching training to release 3–6 GB of unified memory. On machines with ≥24 GB unified memory, scale `batch=8` (and linearly scale `lr0`) or use `--batch -1` AutoBatch.

**Why:** Apple Silicon unified memory is shared between CPU and GPU. Freeing host RAM provides the GPU headroom needed for larger batch sizes, doubling tensor core utilization and cutting wall-clock training time by 25–35%.

---

### BP-36: Guard OpenCV image loading against partial APFS buffer reads and Apple-optimized PNGs

**Wrong:** Rely solely on `np.fromfile()` + `cv2.imdecode()` without a universal PIL fallback. When `im is None`, unconditionally raise `FileNotFoundError`.

**Correct:** If `cv2.imdecode()` returns `None` (which triggers `libpng error: PNG input buffer is incomplete`), re-read the file bytes using Python's signal-safe `open().read()`, and if `cv2.imdecode()` still fails, fall back to Pillow (`PIL.Image.open()`). Never gate the PIL fallback to just `(.avif, .heic, .heif)` extensions.

**Why:** Under concurrent multiprocessing dataloading (`workers=4`) on macOS APFS, C stdio `fread()` in `np.fromfile()` can occasionally suffer interrupted or short buffer reads. Furthermore, Apple screenshots with 16-bit RGBA depth or `iDOT` chunks can cause OpenCV's bundled libpng to fail decoding. Pillow's decoder seamlessly handles these images and prevents a fatal training crash after dozens of hours of compute.

---

### BP-37: Confine Matplotlib and PyTorch caches to package directory for strict filesystem boundaries

**Wrong:** Import `matplotlib.pyplot` or `torch` without setting cache environment variables. Matplotlib defaults to `~/.matplotlib` or `/var/folders/.../T/matplotlib-*`, and PyTorch defaults to `~/.cache/torch`. In restricted sandboxes or automated pipelines, this triggers `is not a writable directory` warnings or fatal sandbox permission rejections, violating the filesystem boundary rule.

**Correct:** Explicitly configure `MPLCONFIGDIR`, `TORCH_HOME`, and `YOLO_CONFIG_DIR` at the very top of Python scripts before any heavy third-party library imports:
```python
os_env_defaults = {
    "YOLO_CONFIG_DIR": str(PROJECT_ROOT / "NativeUITrainer" / ".ultralytics"),
    "MPLCONFIGDIR": str(PROJECT_ROOT / "NativeUITrainer" / ".mplconfig"),
    "TORCH_HOME": str(PROJECT_ROOT / "NativeUITrainer" / ".torch"),
}
for k, v in os_env_defaults.items():
    os.environ[k] = v
    Path(v).mkdir(parents=True, exist_ok=True)
```

**Why:** Guarantees 100% self-containment inside the package boundary, ensures zero user-directory pollution, and prevents sandbox access violations during headless runs.

---

### BP-38: Specify in-project module cache when running standalone Swift scripts

**Wrong:** Run standalone Swift scripts with bare `swift scripts/myscript.swift`. The Swift interpreter attempts to write Clang precompiled module caches to `/var/folders/.../C/clang/ModuleCache/`, which errors with `Operation not permitted` under strict sandbox isolation.

**Correct:** Pass `-module-cache-path .build/clang-cache` to the `swift` invocation:
```bash
swift -module-cache-path .build/clang-cache scripts/myscript.swift [args]
```

**Why:** Confines all compiled module caches to `.build/`, eliminating sandbox permission failures and adhering strictly to the filesystem boundary rule.

---

### BP-39: macOS Vision OCR and IOSurface Allocation Depend on Host Session Context (Mach Bootstrap / WindowServer)

**What went wrong:** During initial physical Apple TV qualification, `VNRecognizeTextRequest` consistently failed on valid screenshots with `kCVReturnAllocationFailed` (-6662) under `com.apple.Vision` / `Foundation._GenericObjCError`. However, running the identical code on the identical reviewed screenshot and identical OS build (`Build 25F84`) inside an interactive user shell session succeeded 7/7 times (`surfaceAllocationCode: 0`, 13 text regions detected).

**Root Cause:** Apple's Vision framework allocates hardware-accelerated memory buffers via `IOSurface`. `IOSurfaceCreate` requires access to the system WindowServer and graphics daemons via Mach bootstrap service ports (`bootstrap_port`). In certain non-interactive or restricted execution contexts (e.g. headless SSH sessions without GUI login context, LaunchDaemon background processes lacking Aqua session type, or restricted subshells), Mach lookup fails and CoreVideo returns `kCVReturnAllocationFailed` (-6662).

**Correct Approach:**
1. **Library Level:** Always treat OCR as a fallible modality. Use `ModalityHealth` (WP1-1) to report `.failed(reason: ..., domain: "com.apple.Vision", code: -6662)` without swallowing the error or crashing the detection pipeline.
2. **CI / Automation Level:** Ensure automated test runners and inspection harnesses (such as TVTestRig) execute inside an active Aqua user session (or with `launchctl asuser <uid>`), rather than a disconnected background launchd daemon.
3. **Diagnostics:** When diagnosing OCR failures, verify whether `IOSurface` can be allocated in the target shell before assuming image corruption.

---

## tvOS Automated Navigation & Physical Hardware Testing

### BP-40: Never navigate Apple TV interfaces with open-loop key counting (`navigate down --count N`)

**Wrong:**
```python
# Assuming item 4 is "Audio Output"
navigate("up", 20)
navigate("down", 4)
press("select") # DANGER: hits "Reset Video Settings" or "Erase All Content"
```

**Correct:**
```python
# Closed-loop single-stepping with focus confirmation
while not target_reached:
    navigate("down", 1)
    wait_stable()
    current_focus = get_focused_element_ocr()
    if current_focus.text == target_label:
        break
# Verify focus before select
assert current_focus.text == target_label
press("select")
```

**Why:** tvOS list views contain non-selectable section headers (`VIDEO`, `AUDIO`, `INFO`, `MAINTENANCE`), descriptive footers, and dynamic off-screen paging. Open-loop multi-step counts drift unpredictably, causing blind clicks to land on adjacent destructive actions (`Reset Video Settings`, `Add New Profile`, `Erase All Content`).

---

### BP-41: Mandatory Disclosure Chevron (`>`) Gate Before Sending `select`

**Wrong:** Treating every row or highlighted item as a sub-menu to be clicked with `press select`.

**Correct:** A row may only be clicked for sub-view navigation if OCR or Vision confirms a trailing disclosure chevron (`>`) on the right margin of that row. Rows lacking chevrons must be classified as **in-place value toggles, steppers, or direct action buttons**:
- Record their labels and values into the hierarchy tree as **read-only leaf nodes**.
- **Never send `select`** to rows lacking chevrons during navigation sweeps.

**Why:** In Apple's Human Interface Guidelines for tvOS, rows without chevrons either mutate the setting immediately in place (e.g. changing 1080p to 720p, toggling Wi-Fi off) or trigger modal setup wizards.

---

### BP-42: Traversal Boundary Lock ("Settings Jail" / App Context Lock)

**Wrong:** Unconditionally calling `press("back")` or `press("home")` to escape deep menus.

**Correct:** 
1. Maintain an explicit DFS navigation stack: `[Root, Category, Subview]`.
2. When backtracking, send a single `press("back")` pulse, then capture and assert that the screen title matches the parent node on the stack.
3. If the screen does not match, or if an unexpected modal dialog ("Cancel / OK") appears, halt immediately.
4. **Never send `press("home")` during active menu traversal.** If the app escapes to Springboard, subsequent clicks will enter the app grid, launch random third-party apps (e.g. Peacock), and pop modal Terms of Use dialogs.

**Why:** Prevents automation drift from escaping the target application into Springboard and contaminating dataset captures with third-party app interfaces.

---

### BP-43: Strict Destructive Keyword Blacklist

**Rule:** Traversal scripts must maintain an active keyword blacklist that unconditionally forbids `select` even if a button or chevron is visually present:

```python
FORBIDDEN_KEYWORDS = re.compile(
    r"\b(Reset|Erase|Format|Update|Delete|Remove|Sign Out|Add Profile|Add New|"
    r"Purchase|Restore|Terms|Agree|Offload|Restart|Sleep|Calibrate|Check HDMI)\b",
    re.IGNORECASE
)
```

If the focused element's label or accessibility text matches any term in this pattern:
- Immediately record the element as `type: "destructive_blacklisted"`.
- **Do not send `select`**.
- Advance focus to the next safe row.

---

### BP-44: On-Device Fixture Synthetic Generation over Fragile OS Crawling

**Wrong:** Relying on live system Settings or third-party apps to gather training data for native tvOS controls.

**Correct:** Use `TVTestRigFixture` running on physical hardware to generate and render native UI components inside a safe, dedicated test sandbox:
1. **Zero Mutation Risk:** Actions inside the fixture cannot wipe credentials, reset video modes, or reboot the Apple TV.
2. **Authentic Hardware Rendering:** Employs real Apple TV Metal shaders, parallax tilt, specular highlights, and dynamic drop shadows that simulators cannot replicate.
3. **Exact Ground Truth:** The fixture introspects native window coordinates (`view.convert(bounds, to: window)`), `UIFocusSystem.focusedItem`, and accessibility traits directly in memory, outputting Schema v1.0 JSON sidecars with zero OCR annotation noise.

---

### BP-45: Local HTTP/WebSocket Frame Pipeline over App Sandbox Disk Scraping

**Wrong:** Relying on `aatv observe capture --output <path>`, which fails with `persistenceFailed` outside `TVTestRig.app`'s sandboxed container directory, forcing scripts to crawl internal UUID paths and triggering macOS permission dialogs.

**Correct:** Stream uncompressed frame buffers and Schema v1.0 JSON sidecars directly from `TVTestRigFixture` over a local lightweight HTTP/WebSocket server on port `8080` (or pipe via `--stdout`).

**Why:** Eliminates macOS App Sandbox container friction, avoids disk thrashing, eliminates permission prompts, and increases capture throughput from ~0.2 fps to ~5–10 fps.

---

### BP-46: Do not use `CGImage.cropping(to:)` on YOLO top-left pixel boxes

**Wrong:** Crop a Stage 2 focus patch with `image.cropping(to: boundingBoxPixels.cgRect)`. `CGImage` bitmap space has its origin at the **bottom-left**; YOLO / `boundingBoxPixels` use **top-left**. The crop is vertically mirrored relative to the on-screen element.

**Correct:** Draw the screenshot into a `CGContext` that has been flipped to top-left (`translateBy(x:0, y:height); scaleBy(x:1, y:-1)`), offset by the pixel box origin, then scale to 256×256. That is `FocusRingClassifier.makeCrop`.

**Why:** A flipped crop trains and infers on the wrong pixels. Focus glow lives on the *top* of a tvOS tile; a y-flipped patch shows the bottom shadow instead.

---

### BP-47: Do not `import timm` (or `timm.layers`) in the FocusRing train path

**Wrong:** `import timm` then `timm.create_model("mobilenetv4_conv_small", ...)`. In `.venv-yolo` on this Mac, `timm.models.__init__` star-imports 100+ architectures and `timm.layers.__init__` pulls torchvision FX. The process sits at ~0% CPU / ~200 MB RSS for many minutes with no epoch output. `pip install timm` also hangs.

**Correct:** Construct MobileNetV4-Conv-Small from `scripts/focus_ring_backbone.py` (torch.nn only). Train, eval, and CoreML export all use that factory. ImageNet pretrained weights are skipped (`pretrained=False`). Export is `torch.jit.trace` → coremltools — do not go through ONNX (`onnx` is not installed; that path was a dead end).

---

### BP-48: `CGContext.fill(_:)` on a freshly created context is bottom-left origin — even when you're only drawing test fixtures, not production crops

**Wrong:** In a test helper, create a bitmap `CGContext(data: nil, ...)`, draw an existing image into the full canvas with `context.draw(image, in: CGRect(x:0,y:0,width:w,height:h))`, then call `context.fill(CGRect(x:0,y:0,width:patchSide,height:patchSide))` expecting the fill to land at the visual top-left corner.

**Correct:** The full-canvas `draw(image, in:)` call is origin-agnostic (it fills the entire context either way), but a **partial** fill or draw is not — `y` must be `height - patchSide` to land near the visual top, because `CGContext` defaults to bottom-left-origin coordinates. `ChangeRegionLocalizerTests.withLocalizedChange` first drew a "top-left" patch at `y: 0` and got a top-left assertion failure with the region reported near the *bottom* of the image (`minY ≈ 828` of `1080`) — the ChangeRegionLocalizer's own top-left-origin `CGRect` output was correct; the test fixture was wrong.

**Why:** This is the same root cause as BP-46 (`CGImage`/`CGContext` bottom-left origin vs. this project's top-left convention), but it bites in test-fixture construction, not just production cropping — anywhere a test synthesizes a "changed region at position X" fixture via direct `CGContext` fills, verify the assertion against where the fill *actually* lands, not where the call site's `(x, y)` naively suggests.

---

### BP-49: Always check booted simulator state before booting another

**Wrong:** Seeing a simulator is "Shutdown" in a plan and immediately calling `xcrun simctl boot <UDID>` without checking what is currently running.

**Correct:**
```bash
# Always run this first — do not assume the state from a plan written earlier
xcrun simctl list devices | grep Booted
```
Only boot a new simulator after confirming no conflicting instance is already running. Booting a second tvOS simulator (especially across major OS versions) while one is already open can cause Simulator.app conflicts, resource contention, or the newly booted device to not reach a usable state.

**Why:** In a prior session, two tvOS 26.5 simulators were already Booted when the plan called for booting tvOS 17.2 — the plan was written from an earlier `simctl list` snapshot, not the live state. Always re-check the live state immediately before any `simctl boot` or `simctl install` command. Treating the plan's captured state as current is a class of bug that causes unnecessary simulator restarts and potential data loss in already-running sessions.

---

### BP-50: An evaluation script's default checkpoint is not the current baseline

**Wrong:** Plan a Run 009 baseline evaluation using `eval_phase6a.py` defaults. Inspection on 2026-09-19 found `WEIGHTS_DIR` still points at Run 007.

**Correct:** Resolve the intended checkpoint explicitly, record its hash in the evaluation manifest, and tie metrics and predictions to that identity. Recheck the script before execution; prose titles do not establish provenance.

**Why:** A valid evaluation of older weights can silently become mislabeled baseline evidence, invalidating candidate comparisons. Evidence: `scripts/eval_phase6a.py:WEIGHTS_DIR`; worker packet P1 addresses the interface.

---

### BP-51: Separate configuration preflight from training smoke execution

**Wrong:** The initial offline plan described `train_ios_model.py --dry-run` as preparation without recognizing that it executes training. Source inspection shows two epochs on 5% of data with warmup disabled and other settings changed.

**Correct:** Use a dedicated validation-only mode for configuration readiness. Treat the existing dry-run as a real, separately logged smoke experiment. Verify inactive schedule features through configuration tests rather than claiming the smoke run exercised them.

**Why:** Option names do not establish side effects or test coverage. Conflating these modes can start unplanned compute and create false confidence in the full-run schedule. Evidence: `scripts/train_ios_model.py:parse_args/main`; worker packet P5 specifies the separation.

---

### BP-52: A symlink export and surviving metrics do not preserve an evaluation corpus

**Wrong:** Mark the Run 009 baseline runnable because `test.txt`, all labels, and a historical metric report exist. On 2026-09-19, all 2,000 test image entries were broken symlinks; train/validation were also substantially incomplete. The earlier planning readiness check had not verified the image targets. This finding does not establish who removed or moved the source files.

**Correct:** Resolve and validate image/annotation members from manifests before data-dependent work. Record content hashes and source dependencies; preserve source pixels or a verified recoverable copy independently of disposable exports. Missing inputs trigger a recovery assessment, not a silent reduced holdout or regeneration into old paths. If historical corpus identity cannot be established, version the replacement and evaluate both baseline and candidate on it; retain original metrics as historical, non-comparable evidence.

**Why:** Labels, symlinks, and cached metrics cannot reconstruct pixels. Reusing the old corpus name after regeneration can hide changed geometry/rendering and invalidate comparisons. Evidence: `reports/dataset_availability_2026-09-19.md`; operational recovery contract: `Research/DatasetRecoveryPlan.md`.

---

### BP-53: Separate software acceptance from unavailable-data qualification

**Wrong:** Revision-2 planning grouped serializers/comparators/suite builders with full Run 009 execution, leaving combined packets blocked by missing image pixels even though their software could be tested independently. Downstream work waited on whole upstream outcomes when only an interface was needed.

**Correct:** Assign software slices with deterministic fixture-based acceptance and separate real-data/live qualification slices. Review schemas/examples early, pin producer versions, and test compatibility as each side evolves. Explicitly label evidence as synthetic or real and preserve independent integrity/provenance/model gates.

**Why:** This removes unnecessary planning dependencies without treating mocks as production evidence. It is a workflow correction, not a claim of measured throughput improvement. Evidence: ImplementationPlans revisions 2–3 and IterationRoadmap.md; TVTestRig's documented offline validator supports the immediate compatibility workstream.

---

### BP-54: Keep offline consumer validation dependency-free and provenance-preserving

**Wrong:** Let an offline compatibility validator depend on an undeclared image library, or fill in missing producer identity while normalizing a structurally valid bundle.

**Correct:** Use a built-in, strict PNG parser for the declared artifact format; preserve producer fields when present, represent missing identity evidence explicitly as `null`, and keep unverified bundles ineligible for training.

**Why:** A host-dependent validator creates a false green path in one environment and an outage in another. Invented identity would turn an integrity check into an unsupported provenance claim. Evidence: P4-A H1 contract suite, 2026-09-19.

---

### BP-55: A progress checkpoint is not a completed execution tranche

**Wrong:** After a user explicitly requested a much larger P4-B/P2-A tranche,
the worker ended consecutive turns after small helper edits, saying it was
"continuing" and would verify next. That required repeated user prompts for
already authorized work. Evidence: user-supplied transcript, 2026-09-19,
12:48–12:49 PM; this observation does not establish the helpers' eventual quality.

**Correct:** Define the integrated completion boundary up front, then implement,
connect, verify, fix, and hand off the whole authorized tranche in the active turn.
Use commentary for interim progress and continue execution. Keep packet-specific
evidence without treating every packet as a stop. Finalize only on completion,
concrete blockage of all remaining authorized work, user interruption, or a real
runtime limit; report incomplete work truthfully.

**Why:** Small reviewable contracts aid verification, but artificial turn boundaries
shift execution management onto the user. Token efficiency means concise context
and evidence, not omitting integration/tests or ending work prematurely. These
rules address the observed failure; they do not guarantee future agent compliance.

---

### BP-56: Exercise the producer's actual artifact layout and envelope

**Wrong:** Unit-test export, readiness, corpus assembly, prediction serialization,
and comparison with hand-written lookalike paths or documents. This hid that the
exporter emitted `train|val|test/{images,labels}` while readiness expected a
different directory shape, and that P2 expected obsolete top-level prediction
hashes rather than P1's nested v1 envelope.

**Correct:** In a project-local synthetic integration test, invoke the exporter
CLI into a fresh output directory, feed that exact output to validation-only
training preflight, and pass a real-format prediction artifact through the
consumer. Corrupt/truncated pixels, cross-split content and family reuse, stale
output paths, failed prediction rows, and absent metrics must fail or report an
explicit unavailable state.

**Why:** Interface drift is most likely at producer/consumer boundaries. Testing
the actual emitted layout and schema catches it without misrepresenting toy data
as an eligible corpus or starting a model run. Evidence: integrated offline
toolchain review, 2026-09-19.

---

### BP-57: Make large preservation inventories resumable without rewriting sources

**Wrong:** Treat a split-level cache hash as every label's identity after a
large-file inventory stalls, or rerun a report generator that overwrites prior
recovery evidence just to resume an interrupted scan.

**Correct:** Derive rows only from the frozen manifests, keep every source path
read-only, write uniquely named in-project chunks with no-overwrite behavior,
and finalize only after exact membership and duplicate-content validation. Report partial
coverage and measured filesystem limits plainly; do not substitute cache hashes
or filename claims for missing content hashes.

**Why:** Recovery decisions require durable evidence while preserving the
historical corpus. Resumable additive chunks allow bounded progress without
converting an I/O limitation into a false identity claim. Evidence: P0-A label
identity review, 2026-09-19.

---

### BP-64: Preserve a bounded settling anchor across cadence changes

**Wrong:** Require a fixed-size trailing frame window to span a settling duration,
or compare only consecutive frames. At high cadence the window never spans the
duration; gradual per-frame motion can also look stable while accumulating drift.

**Correct:** Retain the stable-run anchor plus bounded recent history, compare
current pixels against that anchor and recent frames, and reset on change, stale
observations, missing focus or cadence gaps. Keep observation-time deadlines
separate from host execution timeouts. Readiness remains a candidate, not action
permission; an ROI can miss changes outside it.

**Why:** PER-05 deterministic high-cadence and cumulative-drift tests reproduce
both errors; the anchor-based policy passes them without unbounded frame storage.
Evidence: `scripts/test_transition_benchmark.py`, PER-05 handoff. Synthetic tests
do not calibrate real-world thresholds or establish live navigation reliability.

### BP-63: Seed separation is not pixel or journey independence

**2026-09-22 integration:** enforce decoded-content isolation at both perception
byte verification and shared FocusRing intake, not only a separate audit script.
Regression tests re-encode identical pixels with different PNG metadata/hashes;
cross-partition reuse still fails. See `reports/work/PERCEPTION-INTAKE/handoff.md`.

**Wrong:** The legacy FocusRing audit reported zero shared seeds as clean partition
leakage, and file existence as complete image verification. The old evaluator also
reported a passing hard-negative gate when no hard negatives existed.

**Correct:** Decode and dimension-check every member; hash both bytes and normalized
pixels, then check content across partitions independently of seeds. Keep related
journeys/near-duplicates grouped too; exact hash checks alone cannot establish that.
Report empty support as unavailable/failing, never zero-error evidence. Separate a
test-only unavailable-adapter report from an actual model baseline.

**Why:** On 2026-09-21 the reproducible audit found 84 cross-partition identical-pixel
groups (386 crop references) in 1,500 legacy pairs despite zero seed overlap, and
one duplicate-pixel group with conflicting focused/unfocused labels. Historical
metrics remain historical, not independent quality evidence. See
`reports/work/EVIDENCE-AUDIT/handoff.md`; original crops/reports were preserved.

### BP-62: Test crop contents and orientation, not only tensor dimensions

**Wrong:** A 256×256 crop and correct box arithmetic were treated as evidence that
CoreGraphics selected the intended source pixels. A flipped draw context actually
sampled the opposite vertical region and inverted it.

**Correct:** On a known RGB coordinate gradient, assert pixel location/orientation
for integer, fractional, edge, tiny and expanded focus boxes. The unflipped crop
canvas draws the source at y = canvasHeight - imageHeight + bbox.minY. Share the
actual production crop with dataset tooling; record backend hashes and re-baseline
after changing preprocessing. Pillow interpolation is not exact CoreGraphics parity.

**Why:** A model can run successfully on the wrong pixels. The production regression
and exact runtime recrop checks now test content, not just shape. Evidence:
`reports/work/FOCUS-LAUNCH/handoff.md`, 2026-09-21. Model quality remains unassessed.

### BP-61: Validate the real candidate path without consuming its holdout

**Wrong:** Treat a one-epoch training run as a dry run, evaluate held-out hard
negatives every epoch, or calculate theme quotas from minimum scene sizes.

**Correct:** Preflight the actual trainer without Torch/model loading or writes;
reject missing membership, preserve validation/test isolation, and calculate
theme shares against actual counts. Derive hard-negative support from verified
unfocused test frames. Multiple elements sharing one recipe seed are valid
within a partition; crossing partitions is not.

**Why:** Repeated test inspection leaks evaluation information, and a corpus can
pass minimum-denominator checks while becoming less representative as it grows.
Evidence: `reports/work/FOCUS-CONSUMER/handoff.md`, adversarial tests, 2026-09-21.

### BP-60: Shell cwd is not the signed helper's output authority

**Observed extension (2026-09-22):** `fixture prepare --recipe FILE` returned
`serviceUnavailable` even while readiness passed before and after. The documented
`--recipe-json` import of the same recipe succeeded without permission changes.
Inspect the failure stage before diagnosing a stopped app: this producer maps
untyped local file-read exceptions to serviceUnavailable. Inline recipe bytes are
a supported import route, not a reason to manually write the container or relax
capture admission. Capture subsequently failed independently at native focus.
Evidence: `reports/work/SIM-DATA-01-02/smoke-20260922-0031/handoff.md`.

**Wrong:** Assume launching TVTestRig's signed CLI from NUIAK makes NUIAK its
harvest workspace, or blame a missing parent directory for an earlier containment error.

**Correct:** Verify the effective root and validation stage. In the observed build,
the helper saw its container Data directory as cwd even with an explicit launcher cwd.
Container output passed containment in a guaranteed no-capture negative control.
Use an explicitly approved staging/export route; never bypass containment or broaden
permissions merely to finish a harvest.

**Why:** Process/container boundaries can differ from shell expectations. Distinguishing
containment, parent readiness and actual file access avoids ineffective retries.
Evidence: reports/work/OFFICE-FOCUS-SMOKE/output-path-rca.md, 2026-09-21.

### BP-59: Verify the running TTR entrypoint before routing execution elsewhere

**Wrong:** Treat a missing standalone aatv binary or an old Sillycon setup as proof
that local capture must be dispatched to another machine.

**Correct:** Inspect the running app and matching documented CLI entrypoint first.
This build uses the app executable with --tvtr-stable-cli. Verify session/control,
capture and Fixture state separately; discovery's disconnected record did not match
the connected coordinator session. Validate output boundaries without changing hosts.

**Why:** Wrong-host handoffs add needless approval loops and risk duplicate operators.
Evidence: reports/work/OFFICE-FOCUS-SMOKE/local-attempt.md, 2026-09-20.

### BP-58: Retire nondeterministic renderer-dependent corpus routes

**Wrong:** Keep a `WKWebView` capture route in a deterministic offline corpus after the target simulator repeatedly loses its web process and entitlement checks. A structurally valid PNG/JSON pair cannot prove that the claimed web content rendered.

**Correct:** Remove the failed route from the active capture and validation flow, document any now-uncovered legacy class, and preserve taxonomy/model identifiers unless an explicit compatibility decision changes them. A future replacement requires its own deterministic rendering and architecture approval.

**Why:** Retrying a renderer with unavailable processes wastes capture time and can create semantically false labels. Evidence: P0-C `HardNegative_2` retirement, 2026-09-19.
