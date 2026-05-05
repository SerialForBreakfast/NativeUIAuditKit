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
