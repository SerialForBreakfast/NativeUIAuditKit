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
