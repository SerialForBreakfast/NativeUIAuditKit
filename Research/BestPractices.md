# NativeUIAuditKit — Best Practices

## Separate missing data from unusable correspondence — October3, transition50

Wrong: a two-report inventory concluded native movement evidence was missing while
the accepted reference36 corpus already contained24transitions/12actual moves.
Correct: reconcile accepted corpus inventories before requesting new capture. Then
measure labels, corresponding visible controls and usable pixel features separately.
Here12scorable arrival/departure controls all failed pixel identity; collecting more
unchanged examples or fitting the same head cannot resolve that tracking limitation.
Retain native labels for scoring, never inject after-state geometry into a predictor
while claiming it inferred the transition. Source: REFERENCE-TRANSITION-50 replay.

## Score focus transitions at action level, not only per control — October 3

Wrong: interpreting55correct/76control comparisons and no wrong predictions as a
qualified navigation model. Most retained controls were unchanged;21abstentions and
incomplete endpoints leave zero eligible full-screen action scores.

Correct: report correct departure AND arrival identities together, unchanged actions,
abstentions and full candidate coverage separately. Keep adjacent actions/shared
endpoints/journey ancestry together; two moves from one exposed journey cannot provide
independent train/development support. File hashes check bytes; decoded-pixel hashes
also guard duplicate pixels across partitions. Missing evidence blocks admission.

Why: plentiful unchanged controls can hide complete failure to recognize actual focus
movement. Evidence: FOCUS-TRANSITION-49 retained Settings23/native34 audit.

## Page-dot supervision must measure the dots before layout expansion — October2

Wrong: MediaCardGrid and ProgressActivity applied `.frame(maxWidth: .infinity)`
before `captureFrame`, producing666whole-row training labels for small centered
SwiftUI dot groups. Evaluation used intrinsic dots. Train aspect ratios37–39 versus
test4–7 created different localization targets despite the same class/style.

Correct: fix the intrinsic dot group size, capture it, then align/pad its container.
Preserve prior labels for replay; regenerate a new version and verify real rendered
bounds before admission. Native UIPageControl container semantics remain separately
reviewed. Class presence alone does not establish geometry/style coverage; validation
also needs representative page-control support.

Why: increasing resolution cannot reliably correct contradictory target extents.
Source capture-order checks guard regression, but cannot replace rendered geometry QA.
Evidence: CONTROL-ELIGIBILITY-39 page audit and666hash-verified affected training frames.

## Diagnostic proposal eligibility and crop-edge parity — October2, local38

What went wrong: untyped rectangle union recovered focused bodies but introduced
text fragments and enclosing panels into a classifier trained on control crops.
35/46frames saturated at1.0; preserving known role exclusions still underperformed
production on the7complete screens. Proposal recall is not selector improvement.
Preserve semantic eligibility and evaluate whole-control proposals separately.

The strict crop probe also rejected detector boxes crossing the image edge,
including boxes whose bodies were outside but expanded regions overlapped.
Production expands the original body then clamps; pre-clamping changes pixels.
Use explicit diagnostic opt-in for bounded expanded-region overlap, preserving
strict default and rejecting crops with no overlap. Match the real preprocessing
before attributing a failure to model quality.

### Positive-pair brightness ordering is not transition detection (October2,2026)

**Wrong:** Infer a navigation detector from8/8known focused/unfocused pairs ordered
by brightness. In the retained sequence, signed mean correctly found4changing
controls but falsely called41unchanged controls arrival/departure.
**Correct:** Include unchanged rows, noise/content/illumination/scroll negatives,
preserve absolute-pixel stability and broad-highlight guards, and keep whole-screen
completeness distinct. Guarded mean matches existing33correct/0wrong/15abstained;
it does not improve coverage. **Why:** tiny nonzero differences have a direction
without representing focus. Positive-only pair tests hide that failure boundary.

### Row overlap is not precise pixel registration (2026-10-02)

**Wrong:** Treat a tracker box that overlaps the right row as sufficiently aligned
for a strict pixel-difference rule, or assume rounding fractional coordinates fixes it.
**Correct:** Diagnose position error separately from arithmetic and focus labels.
Tracking30 raw and rounded Vision each score2/48; human-center geometry yields36/48
but is an oracle, not an inference gain. One accepted track follows the adjacent row;
median error is3.11source pixels among33review-corresponded tracks. Preserve fixed
scale and ambiguity guards, and distinguish wrong correspondence from crop jitter.
**Why:** Small source offsets amplify in a short256px crop; overlap alone can hide
the failure. Better alignment still leaves12abstentions, so do not blame every
remaining error on tracking or relax stability thresholds without counterexamples.

### Separate arithmetic parity from tracking replacement (2026-10-02)

**Wrong:** Attribute a native pipeline regression to the focus rule without testing
identical crop pixels, or assume Vision tracking improves an OpenCV diagnostic.
**Correct:** Settings25 first reproduced45crop decisions in Swift (metric error below
3.21e-13); only then substituted tracking. Scored decisions fell33→2with unchanged
thresholds. Preserve tracking failures, semantic-target IoU and abstentions separately.
**Why:** Correct arithmetic cannot recover a misaligned row. Changing both components
at once hides which one failed. See ADR-0018; this result is candidate-specific.

## Preserve scene scale separately from accurate control bounds (FOCUS-GROWTH-02)

**Wrong:** Expect a larger rendered-body box to create a larger model input body
after resizing its proportional crop to a fixed size, or use intentionally smaller
annotations to force that effect.
**Correct:** Keep accurate bounds and the production detail crop. An experimental
context branch uses one viewport transform for every candidate and a separate
candidate mask/normalized geometry. Pixel tests must verify growth and global
resolution invariance; label/state metadata must not supply prediction inputs.
**Why:** All 32 retained growing pairs retain enlargement in common-scale masks,
where proportional crops almost erase it. Preserved information is necessary,
not proof a model has learned focus. See FOCUS-GROWTH-02 retained audit.

## Preserve effective sub-source weights when testing added data (SYN-13)

**Wrong:** Report unchanged80/20native-human loss as an unchanged sampling policy
without checking native subgroups. FDR022switched from preserved baseline native
weights to an equal-OS/fixture recomputation:80OScontrols rose9.3%→40%of total loss,
old fixture fell70.7%→27%, new fixture received13%. Even recomputing the old corpus
alone changed all790native weights.
**Correct:** Pin/version the actual weighting policy; require empty-addition
identity and explicit source/label mass plus member-weight delta reports. Preserve
baseline source budgets for the controlled data comparison or separately approve
and name the policy change as another intervention.
**Why:** Normalized totals and outer80/20balance passed while the intended data-only
comparison was confounded. Failed transfer does not isolate bad data or inadequate
features. [Diagnostic evidence](../reports/work/SYN-13-DIAGNOSIS/handoff.md).

## Match producer geometry tolerances before rejecting native annotations (SYN-02)

**Wrong:** Require full and projected visible rectangles to agree to machine precision
when the producer deliberately allows one-pixel rounding before marking clipping.
**Correct:** Inspect the pinned projection implementation, retain full and visible
bounds separately and match that tolerance, while still checking normalized geometry,
frame bounds and scene binding. Keep unknown anchor focusability unknown.
**Why:** Otherwise good native observations are rejected as clipping defects. A
fractional-pixel fixture now passes; a larger unmarked shift still fails. Neither
tolerance nor accessibility text proves complete annotations or visual focus.

## CLI timing and strict health are not UI qualification (LOCAL-TOOLS-02)

**Wrong:** Interpret session-internal modelLoadMs=0 as zero cold startup, or fail CI
on every heuristic issue exposed through the screenshot API.

**Correct:** Measure wrapper load/identity and end-to-end time separately. Report
first-in-process versus warmed calls and actual modality/focus failures. Keep inferred
scale and heuristic clipping/overlap/truncation as review warnings, not strict defects.

**Why:** The real cold iOS smoke took about 1.03s while its warmed repeat took 0.19s;
the preloaded session reported zero inner load time for both. AuditRules also infers
scale without a sidecar. See LOCAL-TOOLS-02 evidence; these timings are observations,
not a performance guarantee. Preserve protocol-only stdout when wrapping native APIs.

## Batch-import Undo must include the empty-image baseline

**Observed:** FOCUS-REPAIR-INTAKE-04 real-sidecar editor check found first import on
an unannotated image stores only the19-box post-state. Undo leaves all19; tests with
an existing box passed and missed this boundary. **Correct approach:** record the
pre-import state even when empty, then the batch post-state; test empty and populated
images independently. Undo after reopening is a separate persistence contract, not
assumed. **Why:** disposable suggestions must be reversible without deleting each
box manually. Fixed by ANNOTATOR-UNDO-01; actual QAction tested on blank/prefilled
images and a real supplied sidecar. Source images were not modified.

## Artwork pair count is not native focus-effect coverage

**Observed:** FDR015's150artwork training pairs contain only24explicit native-image
effect pairs, covering three procedural motifs/two backgrounds. All150report equal
target box area across states; inspected older examples mostly add rings/outlines.
Two real Home failures instead involve enlarged icon bodies and visible titles.
**Correct:** Audit actual effect/content/target-box conventions and sampling mass,
not only taxonomy counts. Keep unknown effect metadata unknown; inspect native
and legacy representatives. Match measured wrapper/body/transform semantics before
adding geometry features or assuming more seeds add missing native appearances.
**Why:** A class bucket can mix different focus mechanisms and crop conventions;
scaling it may reinforce shortcuts rather than cover the measured failure.
Evidence: FOCUS-ARTWORK-AUDIT-01/audit.json and findings.md. This is a demonstrated
coverage mismatch, not proof of the model's sole failure cause.

## Synthetic aggregate gains can hide both mechanism gaps and real transfer failure

**Observed:** FOCUS-REPRESENTATIVE-01 gives FDR-01075% four-stratum macro recall
on SYNTH05, but artwork is0/32 while native-button controls are18/18. Real buttons
and tabs remain0/3each. Background,content,native effect,geometry and label visibility
are coupled in existing recipes, so attributing failure to one axis is unsupported.
**Correct approach:** report every stratum and real-source cohort separately; retain
fixed production preprocessing and use matched single-axis contrasts before scale.
Count admitted source/scene coverage, not seed count or requested elements; a theme
label with unchanged explicit background does not diversify background luminance.
**Why:** high aggregate scores or thousands of correlated examples can conceal the
exact missing behavior needed for deployment. Evidence: `reports/work/FOCUS-REPRESENTATIVE-01/handoff.md`.

## Retention-only selection can preserve a narrow domain while transfer collapses

**Observed:** FDR-010's30 epochs all retain18/18 Settings/Accessibility crop decisions,
yet its selected epoch finds only3/19 real benchmark positives and0/8 in the separate
Home/Photos/Settings regression. Lower false positives inflate overall accuracy.
**Correct approach:** retain these nine pairs as a forgetting floor; use separately
reserved representative source/control validation for checkpoint selection, and
untouched qualification for release. Report positive recall and complete-frame
outcomes, not retention accuracy as transfer evidence. Do not auto-retrain or tune
against the final test to repair this failure.
**Why:** a narrow retention set cannot distinguish broadly useful epochs, even when
every label and checkpoint-selection calculation is correct.
Evidence: `reports/work/FDR-010/handoff.md`, `verification.json`, `comparison-summary.json`.

Lessons learned from building and running the spike experiments. Each entry describes a mistake or inefficiency encountered, the correct approach, and why it matters.

2026-09-23 identifier repair: historical duplicate IDs are disambiguated by title.
Seed independence (old63) is100; crop-content/orientation (old62) is101; real-candidate
holdout isolation (old61) is102; signed-helper output authority (old60) is103;
crop/backend parity (old68) is104; wire diagnostics (old95) is97. Historical reports
retain their original numbering; resolve by topic, not the ambiguous old number.
New skill routing lives in Research/WorkerExecution/references/operational-lessons.md.

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

**Scope correction (P0-C, 2026-09-22):** This applies to manually positioned
fullscreen canvases. Native navigation content must respect the enclosing
NavigationStack/TabView safe area. Applying this rule to their inner List/Form
containers drew ordinary rows under navigation titles on iOS 26.5. Global frame
measurement still works without ignoring those insets; verify actual rendered
geometry. The native-navigation probe covers thirteen families at both profiles.

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

**Run013 correction (2026-09-27):** r7 appends four addon families with500/100/100
train/validation/test members each. Calling their400 novel images "holdout"
mistook new image identity for withheld-family independence. Preserve these useful
within-family diagnostics, but report them separately from the2,000 original
withheld-family members. A combined38-supported-class average cannot certify
41-class generalization;25 added supported classes are not28. Freeze and test the
population union/disjointness and report missing support as unavailable. Repeatedly
used r6 tests also remain diagnostic, not a freshly untouched release challenge.

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

**Why:** Confines these configurable caches, not every framework or subprocess write. Declare unavoidable platform storage separately; these variables cannot guarantee full self-containment (BP-67).

---

### BP-38: Specify in-project module cache when running standalone Swift scripts

**Wrong:** Run standalone Swift scripts with bare `swift scripts/myscript.swift`. The Swift interpreter attempts to write Clang precompiled module caches to `/var/folders/.../C/clang/ModuleCache/`, which errors with `Operation not permitted` under strict sandbox isolation.

**Correct:** Pass `-module-cache-path .build/clang-cache` to the `swift` invocation:
```bash
swift -module-cache-path .build/clang-cache scripts/myscript.swift [args]
```

**Why:** Confines the selected module cache. Other tool caches, service access and execution restrictions remain separate; this option cannot eliminate all permission failures (BP-67).

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

### BP-66: Filename intent and decodable pixels are not reviewed screen truth

**Wrong:** Infer the visible app or target from a capture filename, or promote decoded
images with empty sidecars into labeled evidence. During the 44-image review,
`office_pluto_loaded.png` showed Photos and `office_settings_target.png` showed Home.

**Correct:** Preserve byte hashes, visually review actual content, record uncertain
source/journey/focus separately and quarantine unannotated inputs from qualification.
Keep prediction JSONs out of truth; classify an explicit unknown relation as abstention,
not a claimed wrong association, and reject absent prediction modalities.

**Why:** Intent-derived labels can make benchmark results misleading before training
begins. The [acceptance review](../reports/work/PERCEPTION-ACCEPTANCE/handoff.md) records
all 44 dispositions and regression tests without overwriting original evidence.

### BP-65: Text-anchor verification is not navigation identity verification

**Wrong:** Promote `TextAnchorVerifier`'s verified substring match directly into a
screen/node identity, or use row y-position to disambiguate repeated labels.

**Correct:** Preserve the primitive's documented substring behavior, but evaluate
identity through explicit registered locale/title/row evidence. Reject tied screen
candidates and duplicate row labels; ignore mutable value text and tolerate vertical
scrolling only when unique label plus horizontal geometry support the match. Keep
unknown as an explicit result and leave action/route authority with the consumer.

**Why:** PER-06's General/General Information case produces a false screen match
under the actual anchor-only primitive. The conservative wrapper abstains; duplicate
rows/tied screens also remain unresolved. This improves the synthetic failure case,
not proof of general recognition accuracy. Evidence: `reports/work/PER-06/handoff.md`.

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

### BP-100: Seed separation is not pixel or journey independence

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

### BP-101: Test crop contents and orientation, not only tensor dimensions

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

### BP-102: Validate the real candidate path without consuming its holdout

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

### BP-103: Shell cwd is not the signed helper's output authority

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

### BP-60: Validate real generated sidecars before scaling a capture

**Wrong:** Assume a successful rendering test proves schema compatibility. P0-C's
first replacement run rendered images but serialized `leading/trailing` safe-area
keys and emitted unsupported `tabBarItem` annotations; all 1,150 manifested sidecars
failed the frozen schema. Independent clamping also mis-sized top/left-clipped boxes.

**Correct:** Test the actual writer's encoded JSON, taxonomy filtering and visible
intersection geometry. Audit early real output with full PNG decoding, paired hashes,
schema and coordinate checks, then repeat across the complete corpus. Preserve failed
attempts rather than relabeling their pixels after the fact.

**Why:** Rendering success and schema-valid, image-bound labels are different gates.
Evidence: [P0-C resumption](../reports/work/P0-C/resumption-20260922.md), failed-capture
validation report, and `testAnnotationWriterFrozenSchemaAndVisibleIntersection`.

### BP-61: Prove rendered variation, not just different seeds or metadata

**Wrong:** Count different generator seeds as different screenshots, or claim
connectivity/battery coverage because sidecars rotate values while the painted
status bar still uses fixed icons. P0-C exposed both failures.

**Correct:** Hash decoded pixels, retain duplicate/rejection evidence, and use a
bounded deterministic variant policy without reducing frozen quotas. For appearance
axes, hold unrelated content and clock fixed, render each supported value, verify
pixel differences, and validate emitted sidecars against the frozen schema. Preserve
the distinction between synthetic painted states and actual simulator/device state.

**Why:** Duplicate samples inflate apparent support; false metadata hides gaps.
Different-looking images can still have invalid metadata (r3's cellular value 4
was outside the frozen `[0,1,3,5]` enum). Evidence: P0-C r2/r3 rejection reports,
`testPaintedStatusAxesChangePixelsWithFixedClock`, and r4 preflight validation.

### BP-62: Fail closed after a generation batch error

Related planning rule: [IterationEfficiency.md](IterationEfficiency.md) keeps a
prioritized inventory of controllable visible states. Exhaustive variation is a
long-term goal, not a new gate for every corpus. Independent deterministic schedules
avoid accidentally tying battery/network appearance to clock values. Verify pixels
and sidecars together; metadata variation alone is not visual coverage (BP-61).

**Wrong:** Let XCTest continue generating after a family fails while its accepted
files are not yet in the manifest. P0-C r4 exhausted MenuButton's visual variants;
the next test reused uncommitted image indices, leaving ledger and files inconsistent.

**Correct:** Persist the original generation failure before throwing and block
subsequent batches before any writes. Preserve the entire failed attempt. A new
continuation may reuse only completely manifested, independently verified batches,
with copied byte hashes, exact source/build lineage and recipe-slot reconciliation.
Keep uncommitted output out of membership without deleting its evidence. Test the
actual requested batch size when a family's visual variation space is limited.

**Why:** A green early audit cannot make a later failed corpus atomic or complete.
Evidence: [r4 diagnosis and r5 continuation](../reports/work/P0-C/resumption-20260922.md),
`testGenerationFailurePreventsFollowingBatchWrites`, the 200-image MenuButton probe,
and `stage_reconstruction_prefix.py` regression tests.

### BP-63: Independent capture still requires independent native label evidence

**Wrong:** Treat a successful reference screenshot as proof that a new acquisition
adapter can produce labeled focused pairs, or replace unmapped native focus with
the requested element ID.

**Correct:** Exercise an actual focused target before scaling. Keep reference and
focused-state acceptance separate. If a non-UIView native focus item cannot be
mapped independently to a fixture element, retain diagnostics and reject the pair.
An alternative screenshot transport does not repair a shared Fixture label defect.

**Why:** Both direct simctl and TTR paths reached `non_view` / `unmapped_item`
despite valid button geometry. Guessing would create false ground truth.
Evidence: [parallel acquisition smoke](../reports/work/TVGEN/handoff.md).

Admission follow-up: do not let the observed target list define expected coverage.
The direct-runner review found this could silently admit an omitted control.
Pin expectations from source separately: recipe element_count can differ from
focusable count (hero2, maze8, kitchen18 for this catalog). Test omission and full
execution publication, not only early rejection. [Review](../reports/work/TVGEN-REVIEW/handoff.md).

### BP-58: Retire nondeterministic renderer-dependent corpus routes

**Wrong:** Keep a `WKWebView` capture route in a deterministic offline corpus after the target simulator repeatedly loses its web process and entitlement checks. A structurally valid PNG/JSON pair cannot prove that the claimed web content rendered.

**Correct:** Remove the failed route from the active capture and validation flow, document any now-uncovered legacy class, and preserve taxonomy/model identifiers unless an explicit compatibility decision changes them. A future replacement requires its own deterministic rendering and architecture approval.

**Why:** Retrying a renderer with unavailable processes wastes capture time and can create semantically false labels. Evidence: P0-C `HardNegative_2` retirement, 2026-09-19.

---

### BP-104: Separate crop parity from model and backend quality

**Wrong:** Assuming identical weights imply equivalent focus behavior, or attributing
different scores to training while consumer crops omit the training-time context.

**Correct:** Replay identical image bytes and boxes through the actual source-bound
crop implementations, inspect the crops, and score both through one unchanged
classifier/backend. Record separate original-path results; label oracle/manual-box
replay separately from actual detector proposals and end-to-end navigation.

**Why:** [FOCUS-PARITY-01](../reports/work/FOCUS-PARITY-01/handoff.md) found different
crops on all four historical images. Holding CPU inference constant, Home scored
1.0 with production expansion versus 0.567 with the tight producer crop. Three
other expected-focused examples remained below threshold: parity is necessary,
not proof of adequate model quality. Uniform synthetic crops can appear equal
despite incompatible crop geometry, so include asymmetric and real cases.

### BP-67: Decouple Developer / Automation Tools from the Mac App Store Sandbox

**Wrong:** Treating every permission error as a reason to remove App Sandbox,
re-sign installed apps or reset services. Earlier guidance overstated unsandboxed
distribution as a universal fix and confused local build and release requirements.

**Correct:**
Use the sourced [SandboxOperations guide](SandboxOperations.md). Distinguish agent
execution policy, App Sandbox/bookmarks, privacy protection, ordinary permissions,
signing metadata and service reachability. Scope platform-storage authority with
the operation; reuse proven execution context and retained captures. Distribution
or entitlement changes are separately reviewed producer decisions, never an
operator workaround. Neither notarization nor an unsandboxed binary grants all
filesystem or privacy access.

**Why:** OS-FOCUS-01 capture passed but restricted result export failed; approved
export recovered the evidence without repeating navigation or changing TTR.
Classifying the actual failure avoids repeated prompts and unrelated rebuilds.

### BP-68: Native focus settling and duplicate observations

**Wrong:** Failing immediately on the first focusless AX snapshot after activation,
or treating any changed decorative AX subtree as contradictory pixel labels.

**Correct:** Use bounded observation-only settling (no input retries). For exact
decoded-pixel duplicates require matching native focused identity/geometry and
viewport; retain the first complete observation and preserve all raw evidence.
Do not merge contradictory focus labels. AX may omit decorative chevrons after
return navigation, so whole-tree equality across different visits is not needed
for deduplication. Within each capture interval unchanged observations remain required.

**Why:** OS-FOCUS-02's first attempt sent zero inputs and failed on a transient
focusless snapshot. The bounded fix completed 25 inputs. Return frames had identical
pixels/focus but omitted decorative subtrees. [Evidence](../reports/work/OS-FOCUS-02/handoff.md).

### BP-69: Time the complete training runtime, not just `import torch`

**Wrong:** Treating a quick warmed PyTorch import as proof that a timed training
arm can initialize promptly. Optimizer creation can lazily import substantial
additional dependencies, even without using `torch.compile`.

**Correct:** Use a separately bounded runtime-readiness check covering imports,
the real optimizer and a tiny forward/backward operation before allocating a
timed model run. Record startup separately from epoch compute. Enforce an external
process deadline as well as batch-level checks; an import cannot reach those
checks. Diagnose owned-process stacks/open files before reinstalling dependencies
or changing devices. Explicitly authorize unavoidable platform-managed caches;
keep configured caches, evidence and checkpoints inside the project.

**Why:** FOCUS-EXP-01's first cold import consumed600s without an epoch. A subsequent
import-only probe took0.717s, but AdamW startup still read cold SymPy dependencies.
FDR-006 completed in419s wall time while the following scratch arm took20s.
These timings describe runtime overhead, not an architecture-speed comparison.
The original attempt remains failed evidence; no model-quality-triggered retry.

Export extension, FOCUS-EXPORT-01: fast Torch loading does not establish CoreML
export readiness either. A60s import-only traceback identified coremltools importing
scikit-learn→SciPy; conversion had not started after the612s stopped attempt.
Record import/trace/conversion stages separately. This evidence does not establish
a permission denial, bad weights, deadlock, or a FileProvider root cause.

Follow-up RCA: a later full import exited1/57.119s with OS errno60 in importlib
file reads; four relevant modules were explicitly `dataless`. Check dependency
residency before blaming native imports or retrying conversion. Keep the entire
environment resident through its identified storage provider, or separately
authorize a reproducible local export environment. Do not delete/reinstall
dependencies or alter global security settings as an implicit repair. Apple
documents materialization stalls/ETIMEDOUT in [TN3150](https://developer.apple.com/documentation/technotes/tn3150-getting-ready-for-data-less-files).
Follow-up identifies iCloud Drive: its download API accepted the request while
the file remained dataless/errno60. Verify actual bytes, not request acceptance.
The concurrent account upload-quota error does not prove download causality.
[Evidence](../reports/work/FOCUS-EXPORT-01/residency-repair.md).

Approved follow-through: a separate pinned non-cloud export environment restored
imports in8.90s and export in3.47s, followed by successful real CoreML parity.
Child evaluation commands must use the approved invoking interpreter, not silently
fall back to the old cloud-managed environment. Dependency-version changes require
actual frozen-reference comparison; successful import alone is not acceptance.
[Qualification](../reports/work/FOCUS-EXPORT-01/qualification.md).

Size-gate correction: dividing bytes by1024² while labeling MB accepted a
5,038,123-byte package against a5MB specification. Enforce an integer5,000,000-byte
limit across all package files; report MB and MiB separately. Preserve failed
artifacts with nonzero exit and a failed versioned report. Regression tests cover
the exact boundary and one extra metadata byte; do not round before comparison.

### BP-70: Bound inference batches by decoded pixels

**Wrong:** Assuming18 valid images fit a helper merely because its item limit is128.

**Correct:** Account for summed decoded pixels against the helper's existing80M
limit. Preserve membership/order across batches and report cold starts per batch.
Do not weaken the limit or misclassify the dataset as corrupt.

**Why:** FOCUS-EXP-01's18 4K frames exceeded the pixel budget. Two9-frame batches
passed with identical source membership. A focused regression test covers this
real entrypoint batching mechanism.

### BP-71: Native Home process presence is not labeled-frame readiness

**Wrong:** Assuming the tvOS Home shell's anonymous focus identifies a visible
tile, or treating repeated `AppCell` identifiers as unique elements.

**Correct:** Bind the observed tile-tree host and verify stable foreground,
viewport, nonempty native tile identity and actual screenshot alignment. Retain
the native label alongside repeated container identifiers; reject ambiguities.
Bound transient settling, preserve failed evidence, and do not turn blank images
or requested navigation into ground truth. Continue unrelated qualified acquisition.

**Why:** OS-FOCUS-03 observed PineBoard's anonymous shell and HeadBoard's actual
tile tree, but three bounded trials still failed before any directional inputs.
Home admitted zero pairs while separate Settings journeys delivered nine reviewed
pairs and one training candidate. This is a local observation gap, not TTR dependence.

### BP-72: Compression size wins do not establish speed or broad accuracy wins

**Wrong:** Treating a smaller package and perfect saturated-score parity as proof
of faster runtime or general model qualification.

**Correct:** Preserve the floating-weight baseline and compare identical membership,
probabilities, threshold decisions, cold loads, warm inference and preprocessing
separately. Keep review-only focus labels distinct from native observed callbacks.

**Why:** FOCUS-COMPRESS-01 reduced package bytes48.14% while warm CPU inference
remained1.36–1.37ms and crop work remained about69ms. All12 scores were far from
decision thresholds. PER-DATA's two Photos visual labels add a different appearance
lead but do not create callback-grounded pairs or an independent test partition.
See the [compression](../reports/work/FOCUS-COMPRESS-01/handoff.md) and
[review](../reports/work/PER-DATA/handoff.md) evidence before generalizing results.

### BP-74: Test producer serialization, not an invented equivalent fixture

**What went wrong:** genuine TTR job697018C6 used Swift Date's numeric JSON encoding,
while NUA's positive fixtures used only strings. After correcting that consumer bug,
intake exposed a second mismatch: resolved recipe theme existed in live telemetry but
was omitted by the producer's narrowed sidecar type.
**Correct approach:** preserve source-backed numeric dates (excluding boolean/nonfinite
values), test actual serialized field shapes, and keep missing theme a fail-closed
normalization error. Retained capture bytes remain unchanged. Inspect live-to-sidecar
field loss before requesting another capture or guessing absent metadata.
**Why:** transport/integrity success is not semantic compatibility, and toy fixtures
must not conceal producer/consumer disagreement. See
[real intake evidence](../reports/work/TTR-SMOKE-20260922-2119/continuation.md).

### BP-73: Freeze appearance and box-sensitivity regressions before tuning

**Wrong:** Extrapolating perfect native Settings challenge scores to other focus
treatments, or repairing misses by selecting the best crop/threshold after scoring.

**Correct:** Evaluate separate reviewed appearances and declared small box variants
using the production cropper. Count base examples separately from correlated variants;
report unique, missing and multiple-focus decisions. Preserve failures before planning
new training-only jitter or appearance expansion; never make them untouched test data.

**Why:** FOCUS-VISUAL-01 candidates missed both Photos focused buttons despite12/12
Settings challenge decisions. A4px inset made both buttons positive; compression
drift reached0.04346 despite no threshold disagreement. Correctly rendered crops
and fixed thresholds made the coverage problem visible instead of hiding it.
[Evidence](../reports/work/FOCUS-VISUAL-01/handoff.md).

### BP-75: Preserve the predicate behind a settling timeout

**Wrong:** The direct pilot reported only `settle_timeout` and a truncated telemetry
tail, hiding a stable coordinate mismatch despite healthy native focus.
**Correct:** Retain the last validation predicate and affected element while keeping
the same bounded settling window. Audit retained evidence before considering another
capture. A prefix audit is planning evidence, not permission to mark failed data complete.
**Why:** The real failure was `coordinate_conflict: header_shelf`; focus resets or
longer delays cannot fix mismatched coordinate frames. [Evidence](../reports/work/TVGEN-RESUME-01/handoff.md).

### BP-76: Recheck staged bundle metadata immediately before installation

**Wrong:** Treating a successful staging-time signature check as proof the same
bundle will remain installable in a filesystem that adds metadata asynchronously.
**Correct:** Preserve the original; with explicit authority, inspect a separate
copy and remove only signature-prohibited FinderInfo/ResourceFork attributes.
Verify the existing signature immediately before install. A recurring failure
requires a new diagnosis, not re-signing or blanket attribute/security removal.
**Why:** The Fixture copy passed initially, then FinderInfo reappeared and blocked
the pre-install check. One observed-metadata correction followed immediately by
verification/install succeeded without changing signed bytes. Attribution to a
specific filesystem service remains unproven. [Evidence](../reports/work/TVGEN-SETUP-20260923/install-receipt-2.json).

### BP-77: Dispatch declared sidecar versions before accepting flat aliases

**Wrong:** An older consumer checked only flat focused-element fields and ignored
the new `schema_version`, allowing malformed v2 brackets to look like legacy metadata.
**Correct:** Absent version retains legacy inspection semantics; declared v2 must
validate every required bracket, recipe/hash, native observation and compatibility
alias. Unknown versions fail. Preserve interval correlation rather than inventing
callback-frame IDs to fit the older crop contract.
**Why:** V2 adversarial tests now reject missing/stale endpoints, altered frame hashes
and alias contradictions while valid legacy behavior stays separate.
[Evidence](../reports/work/SIM-DATA-02-V2/handoff.md).

### BP-78: Report focus decisions beside imbalanced tile accuracy

**Wrong:** Calling a Home focus candidate better because tile accuracy increased
while it classified every tile as unfocused.
**Correct:** Report positive recall, negative false positives, and per-frame
unique-correct/wrong/no-focus/multiple-focus decisions with exact support. Retain
whole journeys and box variants as correlated development evidence. Keep the
all-negative baseline visible; do not tune thresholds on this diagnostic set.
**Why:** FDR-007's Home accuracy was91.7% (66/72) with zero of six focused tiles
recognized at0.85, while the shipped model made two correct unique selections.
The aggregate number concealed the failure needed by navigation.
[Evidence](../reports/work/FOCUS-VISUAL-02/handoff.md).

Follow-up: FDR-008 attained100% Fixture training fit and preserved Settings checks,
yet retained Home/Photos remained0/8 correct unique decisions; Home false positives
increased0→5. Retention on one familiar style plus training fit must not substitute
for appearance-transfer evaluation. Prioritize independent visual support before
another same-data run. [Evidence](../reports/work/FOCUS-VISUAL-03/handoff.md).

### BP-82: Trace appearance axes through the actual renderer

**Wrong:** Counting a randomization pack field or descriptor attribute as visual
coverage. APPEAR-A found badgeCount/usesGradient/fontWeight copied by the builder
but not consumed by the procedural view; the native media renderer uses a fixed
gradient. High-contrast naming likewise does not prove distinct rendered contrast.
**Correct:** Trace recipe → descriptor → active native renderer → measured pixels;
record unimplemented axes explicitly and request bounded rendering support. Keep
valid existing native focus/geometry and metadata-only flags separately labeled.
**Why:** More seeded metadata cannot resolve an uncovered appearance distribution.
[Source audit](../reports/work/APPEAR-A/handoff.md).

### BP-81: Equal strata are not equal source totals

The mixed-appearance development assembly uses equal source/scene/style/control
strata. Interpreting that as a 50/50 source mixture would be wrong: its frozen 252
training examples imply 88.89% Fixture / 11.11% native sampling probability because
Fixture contributes more strata. Compute and report aggregate weight mass before
launch, not just raw counts or a policy name. A different source allocation requires
an explicit configuration revision; do not silently change approved sampling.
This matters for native retention and interpretable comparisons, not a claim that
one ratio is optimal. [Evidence](../reports/work/FOCUS-DEV-01/launch-review.md).

### BP-80: Seed differences do not prove independent visual examples

The retained Fixture pilot's seeds 7 and 19 share exact decoded crop pixels,
including non-maze scenes. Splitting by seed alone would leak evidence across
training and validation. Join related recipe groups whenever source/crop pixels
repeat; preserve paired focus states and deduplicate complete pair repetitions
without erasing lineage. Distinct crops may still be near-duplicates, so exact
checks are a minimum, not proof of semantic independence. Report absent independent
validation rather than relabeling training fit as generalization.
[Observed evidence](../reports/work/FOCUS-RETAINED-01/handoff.md).

### BP-79: Revalidate retained crop-runtime bindings before assembly

**Wrong:** Assuming all reviewed native datasets use today's preprocessing because
their source screenshots and pair labels remain valid.
**Correct:** Check the cropper source/helper identities and actual crop pixels.
Preserve stale derived data; regenerate through the existing production adapter
from unchanged sources and review the new crops before issuing a new manifest.
Keep the original journey/split identity; new crops are not new independent data.
**Why:** The mixed-source integration found older Settings-root crop identities
beside current General/Accessibility/Apps data. Offline recropping and24-crop review
restored a compatible49-pair native assembly without a device recapture.
[Evidence](../reports/work/OS-FOCUS-04-ASSEMBLY/handoff.md).

### BP-83: Bound production crop batches by decoded pixels, not just item count

**Wrong:** Sending16 full4K frames to a helper capped at80 million decoded pixels;
small offline fixtures passed while APPEAR-A2 real intake failed `invalidImage`.
**Correct:** Partition ordered requests by actual width×height and item limits;
reject a single oversized source. Preserve successful captures and re-run intake
into a new output, without changing crop geometry or weakening helper limits.
**Why:** Compressed PNG size and frame count do not bound decoded memory. The
4K limit is nine such inputs per request, not sixteen. Evidence: APPEAR-A2 intake.log.

### BP-84: A theme name is not distinct rendered coverage

**Wrong:** Counting dark and high_contrast recipe metadata as independent visual
styles without inspecting their rendered members.
**Correct:** Compare decoded pixels and source consumption of the theme; keep
related variants together and report aliases explicitly. Preserve paired focus
states and raw evidence, but do not inflate unique examples or split aliases.
**Why:** APPEAR-C's three catalog themes yielded12 pairs but only8 distinct pairs:
all four high_contrast pairs were pixel-identical to dark. Metadata and successful
capture did not supply the missing contrast treatment or independent holdout.
Evidence: reports/work/APPEAR-C/reservation.json and handoff.md.

### BP-86: Balance and isolate by data source, not capture adapter

**Wrong:** treat direct-generator and TTR Fixture captures as different sampling
sources or unrelated seed namespaces. Merely adding a transport could otherwise
change a50/50 native/Fixture proposal into thirds and let related Fixture seeds
cross evaluation partitions.

**Correct:** retain original sourceKind/provenance, but use an explicit logical
Fixture bucket for sampling and seed-component joins across both adapters. Build
one graph containing pixel, original lineage and reserved-family edges together;
separate graph checks can miss transitive leakage combining different edge kinds.

**Why:** APPEAR-B1 includes both direct v1.4 and TTR v1.5 samples. Its actual442-row
assembly retains50% native/50% Fixture mass; regression tests reject cross-adapter
seed leakage and combined family/original-lineage paths. Independent family names
are reviewed evidence, not permission to relabel development crops as untouched.

### BP-85: Pin producer hash vectors when additive rendering fields arrive

**Wrong:** Assume unchanged sidecar version means unchanged recipe identity. TTR's
appearance-v1 recipes all collapsed to the same legacy NUIAK hash, rejecting all
three valid producer vectors despite healthy runtime readiness.
**Correct:** Validate the closed rendering extension, mirror its source-backed
canonical suffix, and pin independent producer vectors plus legacy/null cases.
Bind it across both capture brackets, aliases and derived lineage; do not bypass
hash validation or request a producer rebuild for consumer drift.
**Why:** Metadata parsing and byte integrity can pass while cross-repository
semantic identity fails. Real intake/crop CLI tests retain development-only gates.
Evidence: reports/work/APPEAR-C/appearance-v1/compatibility.json and handoff.md.

### BP-87: Replay the current scoring crop, not a retired diagnostic path

**Wrong:** Continue extracting an OCR crop for a parity harness after the producer
scorer switches to its dedicated expanded focus patch. This tests obsolete behavior.
**Correct:** Invoke the source-pinned scorer's actual `focusPatch`, record its
preprocessing version, compare decoded pixels, then isolate same-backend scores
from deployment-backend differences. Include fractional, clipped and asymmetric cases.
**Why:** The corrected producer now matches all ten NUIAK crops exactly; an old
harness would misdiagnose a repaired integration. Matching preprocessing does not
repair the shipped model's remaining focus misses.
Evidence: reports/work/FOCUS-PARITY-01/corrected-20260923/replay/report.json.

### BP-88: Bind evaluation reservations to the members actually reviewed

**Wrong:** Accept a hash-verified reservation containing only family/role/stratum:
the declaration can still be reused against another source or revised membership.
**Correct:** Bind the exact source manifest/review references and canonical source-row
digest before assigning an evaluation role. Reordering alone is not a membership change.
Keep untouched-use, lineage and independent-support checks separate.
**Why:** A file hash proves unchanged declaration bytes, not which dataset those
bytes approve. APPEAR-B1 reservation-v2 tests reject reused or stale bindings while
the complete synthetic assembly/preflight path still passes. No historical corpus
has been relabeled or re-admitted by this correction.

### BP-89: Check the pinned local Git object before declaring source unavailable

**Wrong:** Treat an old producer working-tree HEAD as proof that the requested
revision is unavailable. This unnecessarily made APPEAR family intake wait on TTR.
**Correct:** Check `git cat-file -t <exact-revision>` and read its files with
`git show <revision>:<path>`. Pin content hashes; do not fetch, checkout or modify
the producer just to inspect an already-present immutable object.
**Why:** cda0a32 was locally available while checkout0e43ab3 remained old. That
source resolved all three new-preset intake failures without a producer action.

### BP-90: Diagnostic filenames must not shadow Python standard modules

**Wrong:** Put an executable `inspect.py` alongside a model-comparison script.
NumPy imported that file instead of stdlib inspect and reran diagnostic setup.
**Correct:** Use a specific name such as inspect_bundles.py, and retain completed
model-stage evidence before starting the next backend. Preserve failed trials.
**Why:** The first family comparison failed on a safe output-collision guard;
renaming the diagnostic resolved the import failure. This was not a model defect.

### BP-91: Reconcile remaining recipes with split totals before resuming generation

**Wrong:** Verify only the grand total and a valid prefix, then assume the frozen
split counts match the continuation. P0-C's14,340 prefix plus2,600 planned members
reaches16,940 but yields12,540/2,400/2,000 rather than12,340/2,400/2,200.
**Correct:** Sum source-defined remaining families by frozen split, join the actual
prefix counts and compare every declared partition before mutation. Resolve the
count/allocation decision explicitly; never move retained members to make it pass.
**Why:** This prevents another expensive capture ending at a predictable admission
failure. The IOS-COV20260923 audit also exposes class support beyond the grand total.

### BP-92: Separate mutable Finder metadata from immutable corpus content explicitly

**Wrong:** Treat a changing`.DS_Store` as corrupted training pixels or delete it
while preparing retention evidence. It changed between inventory and recovery check.
**Correct:** Preserve strict failed evidence; optionally create a new sealed inventory
with an explicit `.DS_Store`-only auxiliary exclusion. Continue verifying every image,
annotation, manifest and rejected-trial member; unknown files and symlinks still fail.
**Why:** A recorded metadata exception avoids repeated copy failures without hiding
corpus changes or pretending a same-volume recovery drill is an independent backup.

### BP-94: Marginal diversity and default state labels do not prove joint visual coverage

**Observed:** DATA-VIS-20260923 found balanced light/dark totals across14,340 sidecars,
but no dark/2x-SE combination and theme-coupled ordinary text sizes. Five status
tuples coupled every clock with one charge level. All136,671 element states were
enabled=true/selected=false, matching writer defaults rather than measured state.

**Correct:** Audit important axis intersections, not only distinct values; use
independent deterministic schedules and bounded pairwise probes in versioned additions.
Separate requested metadata, rendered evidence and measured state. Never train state
classification from default labels or retroactively invent missing measurements.

**Why:** A balanced marginal can hide systematic shortcuts and absent combinations.
Coverage improvements must preserve existing membership and cannot establish model
improvement without evaluation. See reports/work/DATA-VIS-20260923/handoff.md.

### BP-95: Native test dispatch needs a real xctestrun file and positive execution evidence

**Observed:** The r6 driver supplied valid test-run plist contents with a `.plist`
suffix; Xcode rejected it before launching any test. Ordinary plist validation did
not expose this entrypoint requirement.
**Correct:** Preserve the generated `.xctestrun` format and suffix when injecting
test environment variables. Retain the pre-launch failure, test the actual dispatch
arguments offline, and require the named native test to pass—not merely exit0 or
an XCTest skip. Reuse unchanged compiled artifacts with their original build hashes.
**Why:** This separates a host dispatch defect from failed rendering and prevents
either an unnecessary rebuild or a skipped generation being reported as capture.

### BP-93: Reference-to-focus success does not establish focus-switch recognition

**Wrong:** Generalize successful localization against an unfocused baseline to
directional navigation. Both the departing and arriving controls change during
a focus switch, and change rectangles do not identify which gained focus.
**Correct:** Report reference arrivals, genuine ordered switches, constructed
switch replays and no-op cases separately. Keep semantic/current-frame boxes,
native truth and model decisions distinct; abstain on ambiguous changes.
**Why:** TEMP-FOCUS-DEV localized9/9 reference arrivals but only2/18 constructed
switches correctly, with2 wrong and14 abstentions. The shipped+diff guardrail
improved reference arrivals but did not solve focus switches. No live action
policy should be inferred from this favorable baseline-only result.

### BP-97: Verify execution diagnostics on the wire, not only in Swift

Renumbered from the duplicate BP-95 on2026-09-23; native test dispatch retains BP-95.

**Wrong:** Assume synthesized Codable includes computed receipt counts because
Swift callers can read them. FOCUS-RECEIPT-01 review found its initial computed
counts/completeness absent from JSON, leaving cross-process consumers without the
promised fields despite an ordinary Swift roundtrip passing.
**Correct:** Encode derived wire fields explicitly, validate them against candidate
dispositions when decoding, and assert actual JSON keys plus contradictory payload
rejection. Keep legacy outer results without the new optional receipt decodable.
**Why:** Cross-repository consumers see serialized bytes, not computed Swift
properties. See FocusExecutionReceiptTests.wireCountsAndTamperedEvidence.

### BP-96: Missing class metrics are not zero measurements

**Wrong:** P2 comparison used dict.get(key,0) over the union of metric keys. When
only one artifact reported a class AP, this fabricated a delta against zero.
**Correct:** Compare finite numeric values present on both sides only; explicitly
report missing/null sides and partial availability. Reject booleans/nonfinite
values and nonfinite subtraction results. Keep unsupported-class AP unavailable.
**Why:** IOS-COV found only12/41 classes supported in the current test prefix.
Invented zeroes conceal absent evaluation evidence and misstate improvement or
regression. Regression coverage: scripts/test_reference_comparison.py and the
actual exported-corpus offline toolchain integration test.

### BP-98: Reconcile skill examples with the qualified implementation

**Wrong:** A model skill retained blanket Create ML `.scaleFill`/eval_map advice
after production moved to YOLO letterboxing; older TTR guidance also described
Office-only jobs after simulator app-managed jobs had passed a genuine smoke.
**Correct:** Route workers to the current assigned contract and exact installed
capabilities, label historical examples, and update the operational entrypoint when
an interface changes. Preserve source/build/runtime and adoption as separate facts.
Keep detailed incident evidence in the learning log, not copied into every skill.
**Why:** Stale instructions can undo a repaired path or fabricate a new blocker.
The2026-09-23 skill audit corrects the model entrypoint and adds the TTR local overlay;
the original producer reference remains versioned, not represented as a new release.

### BP-99: SMB delivery has distinct publication, transfer and intake boundaries

**Wrong:** Treat a producer's filename/hash announcement as a delivered archive,
or an acknowledgment as successful intake. The first APPEAR family check found no
published archive despite having its expected identity; later copy verification
completed before semantic intake.
**Correct:** Verify the actual expected SMB mount, read only relevant metadata,
copy separately approved final artifacts to new local storage, verify bytes, and
publish an exact request/file/size/hash/receiver/time receipt. Review archive safety
and consumer eligibility separately; sender verifies receipt before its owned cleanup.
Reconcile offline guide copies with approved protocol amendments without deriving
new operation authority from peer text. Keep unrelated local progress off the share.
**Why:** This avoids premature cleanup, duplicate transfers, false training approval
and repeated coordinator handoffs. Evidence:
[family transfer](../reports/work/APPEAR-FAMILY-HANDOFF-20260923/coordination.md).

### BP-100: Requalify runtime drift explicitly; never rewrite historical crop identity

**Wrong:** A current helper can reject retained assembly because its classifier
source/helper hashes changed, even when the source change only adds artifact metadata.
Treating that as missing pixels, rewriting old manifest identities, or globally
ignoring hashes would respectively trigger needless recapture or erase provenance.
**Correct:** Retain the failure and old manifests. Bind a complete production-crop
pixel replay to the exact old assembly and current runtime; accept that transition
only through an explicit appearance-assembly `runtimeReplay` reference. Default
validators remain strict. Reconstruct native labels, frame geometry and crops using
the existing validators, reject membership/sampling/selection drift, and record the
actual execution runtime separately. New coverage and training approvals remain gates.
**Why:** The September27 focus tranche reproduced all460 retained crops exactly,
then rebuilt the unchanged candidate through the real CLI without bypassing its
independent-evaluation requirements. [Evidence](../reports/work/APPEAR-EVAL-RESERVE-20260927/handoff.md).

### BP-101: Namespace imported frame files separately from evidence metadata

**Wrong:** Even a path-safe frame ID such as `index` or `session` can overwrite
retained metadata when its observation JSON shares the same raw directory and
suffix. A native sidecar suffix can also collide with another valid frame ID.
**Correct:** Validate IDs and place each frame's PNG/observation/native evidence
in its own directory under `raw/frames/<id>/`; keep capture-index/session metadata
outside that namespace. Reject duplicate IDs and existing destinations, and test
reserved-looking names through the actual importer.
**Why:** Path-traversal rejection alone does not preserve original evidence.
The Photos pilot review caught and corrected this collision before live intake;
its regression verifies the original index bytes survive. [Evidence](../reports/work/PHOTOS-PILOT-01/handoff.md).

### BP-102: Discovering a TTR device does not select it for capture ownership

**Wrong:** Require capture-lease acquisition before control connection when the
coordinator has no selected target. The Photos pilot returned deviceNotFound despite
successful list/get of the same Office ID, creating an artificial setup loop.
**Correct:** Inspect actual runtime status and matching source where available.
The inspected coordinator requires selectedDevice equality for acquireCaptureLease;
connect(to:) selects the discovered target before control connection. After fresh
occupancy checks and human exclusivity, deliberately connect the authorized target,
acquire its owned capture lease, then start separately authorized image capture.
Stop on uncertain outcomes; no automatic pairing, restart or takeover. Distinguish
local source diagnosis from verified identity of a remote installed binary.
**Why:** Discovery, selection, control connection and capture ownership are separate
states. Conflating them wastes supervised time and can prompt unnecessary repair.
[Evidence](../reports/work/PHOTOS-PILOT-01/coordination.md).

### BP-105: Qualify the operator workflow, not just individual TTR primitives

**Wrong:** Treat successful IPC, lease acquisition or capture as proof that a
supervised collection flow is usable. The Photos proof took38m42s from initial
helper invocation to two exports, including agent/operator delay and manual relay.
**Correct:** Batch passive readiness checks, preserve exact operation/artifact
identities, and qualify approval → capture → verified delivery → review → owned
cleanup with the actual consumer. Measure human interventions and end-to-end time
separately from backend execution. Do not remove human consent or label review to
meet a speed target, or launch new transport outside approved scope.
**Why:** Repeated setup and status round trips consume the supervised collection
window even when backend primitives work. The requested contract is in
[TTRSupervisedExternalControl.md](Plans/TTRSupervisedExternalControl.md).

**September28 follow-up:** Logging human TTR inputs does not mean every input has
an image. The local session retained9 commands but only8 checkpoint observations;
Right/Up/Select occurred without intermediate images. Never scale supervised
collection through chat-per-press or describe final-frame command references as
complete trajectories. Qualify action-triggered original-frame retention and explicit
overlap/gap accounting first; batch human label review afterward. This prevents
losing the very transitions the operator is demonstrating. [Repair contract](Plans/TTRActionLinkedCapture.md).

### BP-106: Cached-score diagnosis must not invoke a full runtime/corpus validator

**Wrong:** Reuse inference preparation for offline analysis when it also traverses
protected challenge pixels or requires the original runtime. Treat fewer false
positives/high imbalanced accuracy as proof of improved focus selection.
**Correct:** Pin retained protocol/predictions and only authorized membership;
verify byte/pixel identity, complete paired/frame relationships and cached-score
accounting, then reuse the metric-only implementation. Keep ties and unsupported
subsets explicit. Ranks explain failure; they do not replace the fixed selector.
**Why:** FDR-008's299→23 competition false-positive reduction still leaves1/48
unique-correct frames. The full surface runtime validator traverses challenge crop
dependencies, which this offline tranche must not inspect.
[Evidence](../reports/work/FOCUS-OFFLINE-DIAG-01/diagnosis.md).

### BP-107: Separate training-data admission from independent model qualification

**Wrong:** Treat every development-purpose Fixture manifest as permanently unusable
for training, or rewrite its original split to make a trainer accept it. Conversely,
do not let useful training pixels silently satisfy independent validation gates.
**Correct:** Preserve source manifests and native observations. Bind explicit source
reviews to immutable membership, validate production crops, exclude duplicates and
protected-data overlap, and assign training roles in a separate versioned assembly.
Keep original candidate/retention membership and launch gates intact. A narrower
checkpoint-selection policy requires an explicit decision, not a validator bypass.
**Why:** The local TTR expansion supplies usable native-bracket Fixture examples
without native Photos or independent appearance-validation coverage. Data collection
can advance while those separate qualification dependencies remain unresolved.
[Admission contract](Plans/LocalSimulatorFocusDevelopment.md).

### BP-108: Verify a local annotation tool's actual settings and plugin paths

**Wrong:** Assume `--config` or `QSettings.setDefaultFormat(IniFormat)` keeps all
Labelme5.2.1 settings project-local, or mistake every Qt plugin failure for a
sandbox denial. Its default-config loader still attempts `~/.labelmerc`; the
organization/application QSettings overload still selected native preferences.
Qt5.15.19 on this host also omitted plugin files below a hidden `.venv-review`.
**Correct:** Inspect the installed pin, supply its complete bundled config to the
stock window, scope an explicit project-file QSettings object to construction,
and assert the actual settings filename. Use a non-hidden project-local venv
for this Qt build. Verify real load/edit/save/close/reopen and JSON identity,
not merely successful pip installation. Do not change HOME or system permissions.
**Why:** A lightweight tool can still violate storage assumptions or fail at
startup. Integration evidence must include the actual editor, while automated
GUI edits remain software tests—not human confirmation of labels.
[Evidence](../reports/work/HUMAN-REVIEW-01/handoff.md).

**Rectangle-only follow-up:** stock Labelme's tool buttons wrap QAction in
QWidgetAction and retain a separate iconText. Verify the actual visible button
and canvas, not only QAction.text()/toolbar.actions(). Hide non-rectangle actions
and shortcuts, guard the draw-mode entrypoint across file loads, and update both
text and iconText. A rectangle-only importer does not by itself prevent users
from drawing incompatible polygons in an unmodified generic editor.

**Clipboard follow-up:** visibility checkmarks are not selected shapes. The pinned
editor exposes copy/paste primarily through the canvas context menu and its stock
paste loads clipboard shape instances directly. Put explicit Select all/Copy/Paste
in the main menu, verify actual platform shortcuts, and deep-copy on every paste
so destination edits cannot change the next paste. Preserve local identities,
reject collisions, and clear copied confirmation/destination review. Reusing boxes
is a geometry proposal, never evidence that another frame has been reviewed.

**Bulk completion follow-up:** requiring individual confirmation clicks after a
human has reviewed a batch adds friction without supplying a better audit trail.
Offer an explicit, named-reviewer attestation for an exact previewed ready subset;
reuse the importer checks and leave unknown/conflicting/flagged rows pending.
Hash-bind the preview, back up saved JSON before updates, and record partial I/O
failure membership rather than rolling back over possible concurrent edits.
Allocation of missing local IDs is bookkeeping; it must never guess original
proposal/native identity. A Cancel path and stale-preview test are required in
the actual editor, not just the backend. Software tests remain nonhuman evidence.

**Navigation follow-up:** stock next/previous indexes `filename` verbatim against
its file list. Normalize a known absolute path (such as Finish review's Open frame)
to the matching relative list entry before load; a successful load alone does not
prove subsequent navigation. Test actual navigation after that entrypoint, and
schedule modal-test responses after focus/event setup so a test timer cannot fire
before the Save dialog exists. A frame-wide flag toggle must leave all box flags
and other frames untouched; mutually exclusive focused/unfocused cannot use all-on.

### BP-109: Invalid model scores must not prevent failure receipts

**Wrong:** Catch an invalid/NaN score in metric validation, then serialize the raw
non-finite prediction into strict JSON. Receipt writing fails, hiding the accounted
partial result precisely when the evaluator needs it most.
**Correct:** Reject metrics for incomplete/invalid predictions; retain invalid IDs
and diagnostic values as strings, valid scores separately, and every unscored ID.
Test the real runner's failure receipt, not only a metric helper's exception.
**Why:** HUMAN-REVIEW-04's injected non-finite engine test verifies a serializable
failure report with all expected samples accounted. Actual226 predictions were
finite; the fix required no repeated model execution. See
[handoff](../reports/work/HUMAN-REVIEW-04/handoff.md).

### BP-110: Filtered review queues must scope bulk confirmation too

**Wrong:** Filter the editor file list for convenience but let Finish review confirm
every Ready frame in the source batch, including images the reviewer never saw.
**Correct:** Freeze the exact queue membership, use it for navigation and Finish
review, hash-check it before confirmation, and preserve hidden annotations unchanged.
Keep completeness as a separate unchecked, revision-bound human assertion.
**Why:** Faster review must not silently expand consent. FOCUS-REVIEW-PREP-01 tests
the actual Qt Finish button and proves a hidden generated frame remains unchanged.

### BP-111: Focus candidates are not constrained to detector container classes

**Wrong:** Force each App Store tab into `tabBar` because the frozen detector
taxonomy lacks a tab-item class, or omit it and claim complete focus coverage.
**Correct:** Keep versioned diagnostic focus roles separate from detector class
IDs. Preserve nullable mappings, explicit admission gates and per-control bounds.
**Why:** A focused child is not its containing bar. The role extension unblocks
annotation without silently changing the meaning of41-class training labels.
See human-focus-roles-v1 and HUMAN-FOCUS-ROLES integration tests.

### BP-112: Clear transient canvas state across image navigation

**Wrong:** Assume the pinned Labelme canvas reset clears selected objects and
keyboard movement state. A delayed key release can index an old shape in the new
image and abort through an uncaught PyQt callback.
**Correct:** Clear transient selection/movement at reset, guard stale release and
test actual key-release events after navigation as well as legitimate movement/undo.
**Why:** The observed batch02 crash retained saved JSON but could lose unsaved work;
ordinary loadFile tests alone did not cover the delayed event boundary.

### BP-113: Action completion and a post-frame tag do not establish a transition

**Wrong:** Count completed remote dispatches as successful UI transitions, or use
every action-associated image as a settled after-state. Trial02 has165 completed
dispatches but only15 bounded declared-settled associations; some post associations
precede command completion or follow another input.
**Correct:** Join explicit IDs/hashes, retain raw timestamps/generations, separate
dispatch outcome from visual outcome, and bound after-states by the next input.
Report conservative exclusions and producer settlement as attributed evidence,
not native focus truth. Equal or unequal pixels alone cannot label a no-op.
**Why:** A temporal learner needs defensible action/state correspondence; otherwise
faster collection can teach another action's result. See REVIEW-PARALLEL-01.

### Harvest target coverage is not the accepted-row count

**Observed:** SYNTH-01 exports accepted rows separately from excluded, interrupted,
unattempted or rejected targets. Legacy receipts have no complete inventory.
**Correct:** Bind accepted recipe/target identities to rows and native planned IDs;
preserve incomplete dispositions through crop export. Compare the expected campaign
recipe list separately; absent legacy coverage stays unavailable.
**Why:** A valid partial dataset must not masquerade as an exhaustive sweep simply
because every retained row passed validation. See canvas-consumer.md handoff.

### Producer floating-point identity is not Python JSON identity

**Nullable-field follow-up:** Actual v2 neutral-reference exports omit
focused_element_id rather than serializing null. Validation accepted this, but a
new crop adapter indexed the key directly and failed eight real pairs. Consumers
must preserve the declared optional-field semantics through every layer; test
omission as well as explicit null through the actual CLI. Competitor-v3 identity
is still mandatory and must never be defaulted from a missing value.

**Observed:** The focus-style producer encodes integral Double values as integers
and negative zero as `-0`; ordinary Python JSON uses decimal suffixes. Equivalent
render settings can therefore produce different recipe hashes.
**Correct:** Verify canonicalization against emitted producer vectors, including
fractions, optional fields and signed zero. Preserve that spelling in the closed
contract; never strip a new style or pairing field to make an older hash pass.
**Why:** Identity mismatch blocks valid evidence, while dropping fields incorrectly
merges distinct recipes. See SYNTH-FOCUS-FACTORY-01/competitor-consumer.md.

### Annotation dialog defaults: retain labels, reset per-box evidence

**Preview follow-up:** Labelme paints both current and its transient line guide.
Setting current for a complete suggested rectangle without clearing line resurrects
the last manual guide. Reset the transient guide, not saved shapes; test actual
painting plus zero/one annotation counts on Cancel/Accept.

**Observed:** Suggested rectangles passed an empty label to Labelme, clearing its
existing repeat-label workflow on every click. Canceled text can also remain in
the dialog even though it was never accepted.
**Correct:** Reuse the accepted label and restore it on cancellation; independently
reset focus, confirmation and notes. Test the actual modal dialog with Enter.
**Why:** Efficient repetitive labeling should not copy another control's focus or
review evidence. See HUMAN-CLICK-BOX last-label follow-up.

### A recipe hash does not pin renderer semantics

**Observed:** SYNTH-05 exports native-button grid controls as primaryButton; the
prior source exported the same appearance recipes as collectionItem. The frozen
older collection plan therefore cannot silently become the current contract.
**Correct:** Bind producer build/source evidence alongside recipe hashes, validate
actual emitted taxonomy and geometry, and create a separate capture/admission
record when renderer semantics change. Keep old plans and receipts unchanged.
**Why:** Configuration identity alone cannot establish identical labels or pixels
across builds. See FOCUS-GAP-LIVE-20260929 and its emitted row/tab hash vectors.

### Persistent outlines are not proof of current focus

**Observed:** In HUMAN-REAL10-01 recorded-742, the agent suggested Watch Now was
focused from its outline. The maintainer confirmed the first Top Stories item was
focused and Watch Now was unfocused; the saved human annotation was correct.
**Correct:** Treat outlines as candidate visual cues, not focus truth. Preserve
explicit human confirmation and distinguish persistent button styling from current
focus. Do not repeatedly request correction after that ambiguity is resolved.
**Why:** Styling-based assumptions can turn valid hard negatives into wrong labels.

### Review selection must add coverage, not merely different pixels

**Observed:** HUMAN-REAL10-01 selected ten distinct decoded images but repeated
Home, Photos Welcome and Settings contexts already in32 reviewed frames. Exact
deduplication alone did not protect human annotation time.
**Correct:** Compare proposed screens against completed review membership and
control/context coverage. State the incremental value per example; distinguish
new content within one app from new layout, focus treatment and source diversity.
Keep a smaller useful supplement when the recording lacks broader coverage.
**Why:** Different hashes, titles or focused items can consume review effort without
addressing generalization gaps. See HUMAN-REAL10-01/coverage-correction.json.

### Selected parent is not focused parent

**Observed:** SYNTH05 Browse remains bright/selected while Home or a nested child
has native focus. Interpreting brightness as focus would corrupt hard-negative labels.
**Correct:** Preserve `isSelected`, `parent_element_id` and observed focus separately;
check all bracket scenes and cross-pair relationships. Resolve logical IDs using
the source descriptor, not visual canvas columns or an assumed array order.
**Why:** Selected-unfocused examples are essential to distinguish navigation context
from the one current focus target. A synthetic Selected subtitle is not a general
real-app cue. See SYNTH05-HIERARCHY-INTAKE-01 visual review and tests.

### Related synthetic evaluation is narrower evidence, not automatically invalid data

**Observed:** BULK12 admission was held because new seed29001 variants shared
renderer/motif ancestry with SYNTH05 development evidence. Calling every related
score improvement artificial confused training utility with independent transfer.
**Correct:** Under the explicit2026-09-29 member-bound amendment, admit reviewed
new variants for development training while excluding exact evaluation members and
decoded frame/crop overlap. Report related-synthetic interpolation separately from
real-app development transfer and untouched source-separated qualification. Do not
silently alter original reservations or count a new seed as a new independent source.
**Why:** This permits useful iterative training without overclaiming generalization
or contaminating the independent exam. See Plans/FocusRelatedSyntheticAdmission.md.

### Verify training backend in the actual launch context before weight updates

**Wrong:** FDR-011 reused the interpreter and configuration but launched in a
restricted context. PyTorch reported MPS unavailable and the trainer silently
selected CPU, unlike the FDR-010 MPS baseline. Three epochs completed before stop.
**Correct:** Assert the intended accelerator is available in the same process
context that launches training; use scoped host approval when required. Pin the
actual backend as well as package versions. Preserve interrupted outputs and use
fresh output/approval for a replacement, not an unrecorded retry or partial selection.
**Why:** Matching interpreter versions does not guarantee hardware access. Silent
fallback can waste the budget and confound an intended data-only comparison.
Evidence: reports/work/FDR-011/backend-interruption.json and execution.json.

### Native-label integrity does not establish visible-body geometry fidelity

**Finding:** QUALIFIED44 passed mechanical native identity/bounds checks, but three
Library examples reported100/101px heights for visible bodies around160px tall.
Even the production16% expansion cut off body pixels; schema validity alone missed it.
**Correct:** Inspect original-frame context and production crops before admitting a
new geometry recipe. Quarantine exact affected members and ask the producer to
reconcile layout/native observations; do not enlarge consumer bounds by guesswork.
Keep unaffected members moving. The renderer cause is not established by this review.
**Why:** Trustworthy focus identity can coexist with incomplete geometry, teaching
unintended crop cues if scaled unchecked. Evidence: QUALIFIED44-INTAKE-01/geometry-review.json.

### Retention-only checkpoint selection cannot establish transfer improvement

**Observed:** FDR012 preserved18/18 familiar retention classifications while real
development TP fell3→1 and FP rose9→15. Minimum retention BCE selected an epoch
that did not satisfy the intended transfer goal.
**Correct:** Explicitly assign representative development selection data, keep it
out of training, and freeze per-stratum/complete-frame regression guards before
execution. Only eligible epochs compete on a balanced objective; none eligible
means no selected checkpoint. Preserve a separate untouched qualification set.
**Why:** More training or lower familiar-set loss is not evidence of broader focus
recognition. Reused selection screens cannot also support independent qualification.
Evidence: FOCUS-SELECTION-01/qualified-audit.json and Plans/FocusRepresentativeSelection.md.

### Audit effective sampling probabilities, not only corpus counts

**Wrong:** FDR013 preserved source-first50/50 sampling while adding artwork and tab
examples.40native Settings pairs received50% of draws;150collection-item pairs
7.4%; tab-source examples under1%. Generic gridMatrix/primaryButton strata hid
native tab presentations. Equal selection weights do not change training draws.
**Correct:** Inspect actual training probabilities and deterministic sampler draws;
use hash-bound recipe presentation to distinguish focus appearances. Keep nested
child buttons separate from parent tabs. Freeze the change as a controlled
experiment, not a retroactive claim of improvement or a public taxonomy change.
**Why:** Adding examples need not meaningfully expose the optimizer to them.
Evidence: FDR014 sampler-draw-verification.json; efficacy remains measured by the run.

### Separate focus ranking, ambiguity gates and actual runtime choice

**Wrong:** Reporting exactly-one-crop-above0.85 as if it were the shipped runtime's
winner-above0.85 behavior, or interpreting failure at one threshold as no ranking
signal. FDR014 epoch1 ranks focus first11/13 but actual winner-style thresholding
gives2correct/2wrong/9none; the strict gate reports2multiple instead of2wrong.
**Correct:** Report forced ranking, strict independent-crop positives and actual
selection policy separately, with explicit incomplete/tied cases and simple baselines.
Keep fixed release gates intact. Label native/human-box diagnostics separately from
end-to-end detector geometry, role support and CoreML parity.
**Why:** A policy discrepancy can conceal dangerous wrong selections, while headline
recall can hide useful ranking information. Neither justifies post-hoc promotion.
Evidence: FOCUS-RESET-01/final-evidence/report.json and findings.md.

### Preserve virtual-environment executable identity without dataset admission checks

**Wrong:** Resolving a project-local Python venv executable through the dataset
containment helper rejects a normal symlink to the installed interpreter. FDR015
assembly stopped before any model execution for this metadata-only reason.
**Correct:** Record `sys.executable` as runtime metadata; keep strict resolved-path
containment for actual datasets, weights and outputs. Test the venv symlink case.
**Why:** Runtime provenance and artifact admission are different contracts; sharing
the wrong validator can block valid runs without improving data safety.

### Equal wrapper bounds are not evidence of an absent native focus effect

**Wrong:** Comparing equal native-image wrapper rectangles with enlarged real icon
body rectangles and concluding the native focus effect was absent or mislabeled.
**Correct:** Keep measured wrapper, artwork layout and presentation geometry distinct.
Inspect actual paired pixels; match the selected geometry role to the detector's
annotation convention before making a transfer claim. Preserve originals and version
any new crop-role selection. Native112 review shows visible image enlargement and
caption overlap despite constant wrapper bounds; three separate short-control
geometry defects remain held while twelve repaired examples pass crop enclosure.
**Why:** Correct focus identity and valid measured view bounds can still produce a
different visual training distribution. More volume does not resolve that mismatch.

**Consumer implementation follow-up:** Validate optional artwork geometry at every
native bracket endpoint, not just the flat export. Reuse the producer's1pixel
artwork-coordinate tolerance rather than the wrapper's1.5pixel tolerance. Missing
or explicitly unavailable geometry blocks only the requested diagnostic role;
do not fall back silently. Bind role in crop identity even if two roles happen to
produce identical pixels. FOCUS-GEOMETRY-ADAPTER-01 tests preserve legacy byte parity
and reject altered brackets and rehashed wrong crops.

### Qt can ignore readable platform plugins marked hidden

**Wrong:** Treating “platform plugin not found” as proof the dependency is missing
or as a reason to reinstall or widen permissions. In ANNOTATOR-AUTO-DETECT-01,
both restricted and host launches failed; all4dylibs existed and were readable.
Qt QDir.Files returned zero while Files|Hidden returned all4.
**Correct:** Inspect the actual plugin directory/flags. Keep the wheel unchanged;
use hash-verified byte-identical copies in the project-local runtime, clearing only
the hidden display bit on owned cache files before loading. Test repeated startup.
**Why:** Discovery failure and binary/loading permissions differ. This repair
restored actual Qt tests without system permission changes or package installation.

**SYN-11 follow-up:** discovery is not binary loadability. Relocating only
`platforms/libqcocoa.dylib` broke its`../../lib`framework lookup (QtDBus followed by
QtPrintSupport); the installed original loaded. Cache a matching
`plugins/platforms`layout and a validated link to the existing in-project Qt5/lib.
Preserve the wheel, reject conflicting links/changed cache bytes, and verify the
actual Cocoa loader in a fresh process before GUI startup. No reinstall or global
DYLD override is needed.

**REVIEW-QT-01 prevention:** the supported editor CLI now runs that loadability and
QApplication check automatically in a bounded child before loading annotations.
Reuse the shared verified cache; preserve structured failure receipts. Native aborts,
timeouts and missing/invalid receipts block launch without opening a review window.
Use `human_review_editor.py --doctor`, not another ad-hoc Qt investigation. See
[the canonical startup guide](AnnotationStartup.md). A runtime check catches startup
failures; it does not guarantee future callbacks or remove the need for GUI tests.

### Native rectangle observations are proposals, not control geometry

**Wrong:** Assuming Vision rectangles are whole UI controls or always inside the
image. The fixed eight-screen trial produced one out-of-frame rectangle and many
text/logo/internal-artwork rectangles; OCR grouped keyboard letters into a line.
**Correct:** Preserve raw observations, reject invalid bounds explicitly, keep OCR
separate, and compare proposals to reviewed controls with one-to-one matching.
Do not count unmatched proposals as false positives when review is incomplete.
**Why:** More proposals can increase matching coverage while increasing human
cleanup. Validate annotation effort before promoting a proposal engine.

### Qualify actual proposed recipes before waiting for new captures

**Wrong:** Treating a geometry adapter's passing tests as proof it accepts every
new producer recipe. The matched proposal used v2 card/fillViewport and bright
palette fields outside the previously qualified consumer subset.
**Correct:** Run the exact producer-emitted recipe hashes through consumer identity
validation first; extend only source-backed fields, preserve absent/null identity,
and test original intake/crops with those recipes plus legacy negative cases.
**Why:** This found and fixed a predictable intake rejection before live capture.
Software compatibility is still separate from visible crop correctness and training
admission. Evidence: FOCUS-OFFLINE-PREP-03, eight producer identity vectors.

### Preserve and validate additive producer views

**Wrong:** Removing newly indexed derived views to make a strict legacy intake pass.
**Correct:** Preserve exports and receipts; validate known additive summaries against
canonical rows exactly, retaining native observations as the label authority.
**Why:** FOCUS-GEOMETRY-LIVE-02 introduced derived views before artwork geometry
was present. Accepting views is compatibility, not geometry evidence.

### Stop storage troubleshooting when retries do not distinguish causes

**Wrong:** Recommending repeated Finder/share recreation or filesystem/privacy
changes after authentication and internal-versus-external behavior were established.
**Correct:** Separate session authentication, share enumeration, tree connection and
actual file read/write. Require a falsifiable boundary check before another retry;
redacted paths and UI toggles do not prove the cause. A new remote-access service
requires explicit scope and explanation of its broader access, not a silent fallback.
**Why:** DATA-EXTERNAL-01 was cancelled after these approaches did not qualify a
remote write. Storage must not become a dependency of independent focus work.

### Matched compute does not isolate the source-domain effect

**Wrong:** Treating an equal-budget real-versus-baseline auxiliary comparison as
proof that real examples alone caused a quality change, without reporting label mass.
**Correct:** Record effective positive/negative loss mass alongside source/frame
weights. FDR017/018 matched initialization, feature vectors, genuine-pair draws,
updates and crop counts, but auxiliary positive mass changed from roughly50% to6.68%.
Report the whole tested mixture, not an isolated causal effect; keep checkpoint gates.
**Why:** The approved human mix reduced focused hits1→0 and increased artwork false
positives5→15. Neither “real data always helps” nor “negative-heavy data merely
reduces confidence” explains these observations. Evidence: HUMAN-STATIC-ADMISSION.

### Establish training fit before blaming transfer or replacing the encoder

**Wrong:** Interpreting poor development focus scores as a data-diversity or encoder
failure without measuring predictions on the actual training examples.
**Correct:** Report per-source/class training loss and scores, then run a bounded,
training-only tiny-set fit diagnostic when needed. FDR017/018 detected only32/395
and27/395 native training positives at0.85. FDR019 fitted48/48 balanced samples with
the same frozen features, proving learnability of that subset, not the whole corpus.
**Why:** Fit, calibration and transfer are distinct problems. The diagnostic improved
development hits but produced38false positives; changing several optimization/data
settings together cannot establish which change caused improvement. Keep release
gates unchanged and do not promote an intentionally overfit diagnostic.

### Distinguish crop clipping from floating-point rectangle differences

**Wrong:** Using exact rectangle inequality before/after intersection to label an
image-edge clamp. The retained TTR audit reported64clamps where all windows fit.
**Correct:** Test expanded boundaries against image dimensions, or use an explicit
coordinate tolerance; retain raw rectangles for diagnosis. Consumer64/64PNGparity
passed despite all64incorrect flags, with differences<=3.41e-13pixels.
**Why:** Diagnostic metadata can be wrong while crop pixels are correct. Do not
recapture data or change production preprocessing based on the flag alone.
Evidence: FOCUS-FIT-PREP-02; producer correction requested, not applied locally.

### Report fitting, confidence and transfer separately

**Wrong:** Calling a run simply “failed to learn” because an all-confident criterion
fails, or calling it successful because training classification reaches100%.
**Correct:** FDR020classifies928/928training examples correctly at0.5 but only901
meet the predefined.85positive/.15negative separation. Development artwork detects
1/12positives despite low training loss. Report these as separate observations.
**Why:** Full-corpus optimization now demonstrates fitting capacity, while the
remaining transfer weakness needs a targeted investigation; neither more unchanged
epochs nor lowering the decision threshold is justified by this result alone.

### Preserve rectangular-batch semantics when replacing training images

**Wrong:** Assuming equal dataset length and synchronized file/label/cache lists
make OHEM replacement equivalent under rectangular batching.
**Correct:** Audit batch/aspect grouping and batch_shapes as well. The current
callback fixture demonstrates a tall-image slot can be replaced without rebuilding
its original rectangular batch metadata. Resolve the grouping policy before a
performance comparison; do not silently change the trainer during a source audit.
**Why:** Padding/resize work and learning semantics can change even when labels
remain aligned. Batch-average loss proxies and synchronous scalar extraction also
need separate interpretation/timing; they are not measured per-image difficulty.
Evidence: FOCUS-OFFLINE-PRODUCTIVITY-11 actual callback tests and source audit.

**Resolution, TRAIN-OHEM-TIMING-12:** the callback now restricts replacements to
equal original rectangular output shapes and reports any shortfall. Calling
Ultralytics `set_rectangle()` again would fail because its first call consumes
label `shape`; do not assume that metadata remains available. Reset augmentation
buffer indexes along with decoded caches. Refuse changed dataset identity/geometry
instead of applying an old snapshot after an automatic loader rebuild.

**Timing lesson:** Ultralytics8.4.124 emits teardown after, not inside, the training
`finally` block. Preserve failure timing in the calling trainer's `finally` instead.
Monotonic host intervals overlap and may contain synchronization costs; they are
not pure GPU execution times or pure data-loader times.

**Measured follow-up, TRAIN-MPS-DIAG-13 attempt02:** OHEM's batch callbacks took
0.039s and epoch replacements0.022s across two epochs, while training batch
intervals took133.759s. Do not attribute historical slowness to scalar extraction
from source inspection alone: earlier operations may already synchronize. Likewise,
seed42with warn-only deterministic algorithms produced MPS nondeterminism warnings;
record this limitation rather than promising identical reruns.

**Batch-size follow-up, TRAIN-MPS-COMPARE-14:** do not treat twice the batch as
twice the speed or equal optimizer work. Four early-training trials found7.67%
higher throughput at16versus8, but MPS allocations10.60versus5.62GiB and different
warmup update counts15versus19in epoch1. Compare matching source membership before
OHEM changes it, record update counts and memory headroom, and keep later epochs
supplementary. This prevents a modest resource tradeoff being called a quality-
equivalent or pure-GPU improvement. Batch8remains the default.

### Focus input-audit follow-up — presentation strata are not control-name buckets

**Wrong:** Audit native training coverage using only the evaluator's control-name
mapping. Native tabs or rows implemented as buttons/toggles then appear absent or
misclassified, despite correct presentation-aware sampling. Also, a different
recording/session ID is not evidence of a different UI family.

**Correct:** Trace the actual frozen sampler's appearance support and loss mass,
and name any alternate control-based grouping explicitly. Inspect retained session
context before extending admission. FOCUS-RETAINED-NEXT-15 verified four native
appearance strata each receive20%total loss, whereas the human subset has6focused
artwork examples and no focused buttons. The same recording contains OS families
related to development; no independent-test claim follows from its session ID.

**Why:** Prevents a false missing-stratum diagnosis or an accidental independence
claim while choosing additions that address the actual human coverage gaps.

### Simulator scene and campaign export boundaries — 2026-09-30

**Wrong:** Treat a booted/headless Fixture process or successful capture as proof
of native layout readiness or caller-path export access.

**Correct:** Correlate endpoint to the exact Simulator process and inspect settled
native scene. In FOCUS-R2-LIVE-11, opening the Simulator display changed no_sample
to settled geometry without restart/reinstall. Completed3pairs survived failed
project export; app-owned export and hash-verified local receipt succeeded.

**Why:** Separates rendering readiness and writer access from capture integrity,
avoiding unnecessary recapture or broad permission changes. This observation does
not establish a universal no_sample cause or qualify arbitrary export destinations.

### CoreML parity — test the final pixel-buffer boundary

**Wrong:** Assume matching saved RGB crop hashes establish the input consumed by
CoreML. FDR021 direct RGB parity passed while production inference disagreed;
63retained PNGs contain partial alpha, discarded by PIL RGB but redrawn by Swift.

**Correct:** Check complete-model conversion independently, then production crop
and pixel-buffer handling on opaque and partial-alpha cases. Preserve failed
evidence; scope compatibility changes explicitly rather than adjusting thresholds
or overwriting training pixels. FP32 may fix precision errors but not image handling.

**Why:** Separates model conversion from preprocessing drift and prevents shipping
a model whose runtime decisions differ from its development evaluation.

**Verified repair,2026-10-01:** candidate-only `png-straight-rgb-v1` performs a
lossless in-memory PNG roundtrip followed by explicit RGB→BGRA copy, matching
333/333model input hashes and scores. A generic premultiply/unpremultiply formula
or black composite was not assumed equivalent. Preserve legacy behavior via
absent metadata; require explicit consumer support before handing off new weights.

### Reviewed-data continuation — static labels are not transition pairs

**Wrong:** Reuse a paired test fixture for independently reviewed frames whose
focus labels no longer represent an observed switch. This produced an unresolved
pair issue even though each individual static crop had a valid reviewed label.

**Correct:** Keep static human samples pair-free; reserve pair membership for
verified same-control transitions. Test the complete review/crop/admission/trainer
path, not just a mocked readiness report. Ordered new-feature receipts must bind
exact control IDs, labels, crop hashes and the original frozen encoder state.

**Why:** Avoids blocking valid static supervision or silently inventing temporal
evidence, while ensuring a changed-data comparison really reuses the same encoder.

### Corpus coverage — distinguish detector labels from rendered control roles

**Wrong:** Treat zero `focus:tabItem` training rows as proof that no tab examples
exist, or demand artwork-body geometry for every native button. FOCUS-CORPUS-03
found12 retained tab/nested-tab pairs exported as `primaryButton`, and a producer
matrix of32 native-button pairs with an inapplicable artwork role.

**Correct:** Report label support and source-pinned recipe/presentation support
separately. Join retained native sidecars by exact hashes, not filename guesses.
Use observed control-wrapper geometry for native buttons; missing native-image
body geometry remains a distinct gap. Preserve existing admissions and holds.

**Why:** Prevents redundant capture requests and misleading diversity counts without
inventing semantic labels or promoting diagnostic data. See FOCUS-CORPUS-03.

### Intake audits: separate random sampling from exception yield (2026-10-01)

**Wrong:** Count deliberately suspicious frames as a random defect estimate, or
copy old reviewed/confirmed flags when making a new annotation audit workspace.
**Correct:** Freeze the eligible population and seed, report exclusions and sampling
probabilities, keep flagged exceptions separately counted, and review overlapping
selections only once. Prefill immutable labels but reset approvals in an isolated
workspace. Never infer independent sources from a count of frames.
**Why:** Reduces duplicate human work without falsely claiming independent quality
evidence. INTAKE-AUDIT-01 tests real queue/Finish/crop entrypoints and source preservation.

### Keep invalid lineage bridges in split checks (2026-10-01)

**Wrong:** Drop a recipe from a source graph when its file hash or review fails,
then declare remaining training and validation recipes unrelated.
**Correct:** Preserve already validated source/layout links for that blocked recipe
and propagate the hold through its connected component. Missing or invalid evidence
cannot establish independence by removing a known relationship.
**Why:** SYN-04's corrupt-bridge test demonstrates that deleting a bad node can hide
cross-role ancestry. No reservation proposal or metadata check substitutes for
source review, pixel/native QA or explicit corpus admission.

### Install review membership before loading images (2026-10-01)

**Wrong:** Construct Labelme with a directory, then filter its file list. Its queued
startup callback still loads the original first image after filtering; Next crashes
when that filename is absent from the review queue.
**Correct:** Construct without a filename, populate the directory synchronously,
then install queue membership and load its first frame. Test event-loop startup
with a queue that excludes the directory's first image, not only a first-frame queue.
**Why:** The SYN-03 human review hit `openNextImg` ValueError despite the prior
offscreen smoke passing. File-list membership and the loaded image must agree.

### Preserve corrected producer taxonomy without weakening hierarchy (2026-10-01)

**Wrong:** Require primaryButton for every nested-tab native control simply because
the first fixture exported that class. The corrected bordered-button export then
fails intake despite valid parent, selection and focus evidence.
**Correct:** Accept the explicitly supported historical/current button labels without
rewriting either; retain parent membership, selected-state and semantic checks.
**Why:** SYN-03's real tab delivery exposed this stale consumer assumption. Source
compatibility tests now cover both labels, unsupported container classes and bad parents.
### Version geometry projections; crop execution is not visual acceptance (2026-10-01)

**Wrong:** Reinterpret old wrapper boxes as rendered-body bounds, or silently change
the projection used to validate an already sealed review batch. Successful crop
generation cannot establish that the solid focused body was enclosed.
**Correct:** Keep v1 wrapper reviews reproducible; opt into v2 measured-body reviews.
Validate source, identity, generation, clipping and normalization inside native
capture brackets. Preserve layout/full/visible geometry separately. Missing native
body measurements stay unresolved, without a guessed scale or layout fallback.
**Why:** SYN-06-BODY's focused image measures520×496 against440×420layout, while
native buttons/rows remain unavailable in that delivery. The same fix cannot be assumed for every renderer.

### Quarantine protected source bundles without rejecting unrelated batch members (2026-10-01)

**Wrong:** Decode an entire combined review batch to validate it before checking
reserved frame identities, or let a protected member make unrelated bundles unusable.
**Correct:** Compare exact source/frame metadata with protected and reserved ledgers
first. Quarantine the whole affected source bundle, retain its declared member IDs,
and reconstruct safe source projections with the existing validator. Preserve geometry
and labels exactly; subset numbering and cross-source alias summaries may differ.
**Why:** SYN-08-ASSEMBLY found four reserved frame-pixel matches in the earlier
image-body delivery. Geometry QA and sampled human approval had never admitted those
frames for training. Source-level quarantine preserves that boundary while allowing
independent native-control and palette data to continue through assembly checks.

### Compare annotation content, not capture generations (2026-10-01)

**Wrong:** Treat identical pixels and labels from separate captures as contradictory
because a rendered-body generation counter changed.
**Correct:** Validate generation against its own native bracket, retain original
evidence, then exclude only that counter when comparing annotation content. Keep
all geometry, focus and semantic differences significant; preserve old review seals.
**Why:** Retained SYN-08 assembly exposed generation-only false conflicts that would
discard useful corpus members without improving label quality.

### Reconcile every native focus target before calling a review exhaustive (2026-10-01)

**Wrong:** Reuse the detector-oriented harvest allowlist as the complete focus
annotation vocabulary. D1's two `menuButton` tabs per screen were silently omitted
from a24-control projection of26 native focus targets.
**Correct:** Bind composition instance kind and native focusability, map tabs to
the existing `focus:tabItem` diagnostic role, preserve producer taxonomy, and test
the actual intake/crop caller. Account for nonfocusable content separately. Do not
repair this by adding an untrained detector class or asking the human to redraw tabs.
**Why:** Correct image hashes and body boxes cannot compensate for missing controls;
complete-frame focus selection would otherwise be evaluated against incomplete labels.

### Audit appearance by control role, not just box quality or corpus size (2026-10-01)

**Wrong:** Treat corrected rendered bounds and hundreds of added crops as evidence
that real-app appearance coverage is sufficient, or treat white button examples as
equivalent to white artwork negatives.
**Correct:** Audit retained failures against role × appearance × focus-state coverage;
use explicit descriptive rules and reviewer observations, then request matched
same-asset/layout positives and negatives without moving evaluation into training.
**Why:** FOCUS-VISUAL-05 found0/554 mostly-white unfocused training collection items
versus57/181 development artwork negatives;21/24 FDR029 false positives matched
that descriptor. This motivates targeted data, not a causal claim or new threshold.

### Bound aggregate corpus manifests separately from per-frame documents (2026-10-01)

**Wrong:** Assume a generic8MiB JSON limit can read a complete multi-delivery candidate
ledger merely because every constituent batch is valid.
**Correct:** Give the native-body aggregate reader an explicit32MiB bound, retain
seal/reassembly validation, and test both above-old-limit acceptance and above-new-
limit rejection. Do not raise all JSON or image limits globally.
**Why:** SYN-09's8,455,778-byte valid combined assembly otherwise failed at the actual
trainer caller after all crop/data checks passed; capacity is not data admission.

FOCUS-READY-07 follow-up: do not duplicate a full composition recipe on every control.
The first4,056-control readiness report grew to84.6MB and failed the actual32MiB
preflight reader. Store each exact recipe once by canonical identity and reference
it from controls; the integrated15.3MB report passes the same bounded reader without
raising limits. Preserve per-control identity and reconstruct native evidence.

### Preserve diagnostic export boundaries instead of manufacturing campaign evidence (2026-10-01)

**Wrong:** Convert a direct screenshot/native-endpoint pair into a completed harvest
receipt, or treat its index's recipe-file hash as the canonical recipe identity.
**Correct:** Verify archive membership and canonical recipes independently, retain
declared-versus-observed file identities, and use an explicit diagnostic adapter.
Stable native endpoints and matching pixels support review; missing screenshot
time/hash correlation remains an admission gap, not invented telemetry. Request
retained metadata repairs rather than recapturing unchanged correct geometry.
**Why:** FOCUS-ARTWORK-08 found48 index recipe-file mismatches despite valid archive
and canonical recipe hashes. All96 original/crop/RGB-input matches with TTR's
observer pass independently of those missing capture claims.

### Balance a small focus review by state without pretending it is independent (2026-10-01)

**Wrong:** Assume two random frames per artwork family will exercise both focus
states. The first eight-frame draw contained six unfocused targets and omitted
focused examples in three families.
**Correct:** Optionally stratify by an explicitly named native target's observed
focused/unfocused state, retain seeded selections and stratum denominators, and
leave unsupported states empty. Preserve the original draw as superseded evidence.
**Why:** Eight prefilled frames can inspect both enlargement and hard negatives
without requesting sixteen manual redraws or claiming a population confidence bound.

### Reuse the complete feature-cache chain when adding native controls (2026-10-01)

**Wrong:** Treat FDR021's986 training controls as a single historical cache, or send
its native extension through a path that recognizes only human `added:` IDs.
**Correct:** Join the original928-control cache and reviewed58-control extension
with the existing validator, then append exact native admission members. Test all
three segments and unchanged333 evaluation tensors; training never re-encodes a
missing segment. Encoding and run approvals bind different protocols.
**Why:** SYN-10's caller inspection found both assumptions would misroute the new
native corpus. Generated tensor tests now verify the complete join without another
real training run or fabricated human/pair labels.

### Composition competitor intake is not legacy canvas intake (2026-10-01)

**What went wrong:** a valid new standard campaign failed `pairing_recipe` because
the consumer assumed all competitor scenes have `appearance.canvas.pairing`.
After correcting that, targeted coverage failed on `excluded_by_selection`.
**Correct approach:** validate the actual composition identity and focusable
competitor membership, while preserving native before/frame/after, PNG, observed
focus and legacy-canvas downgrade checks. Account selection exclusions without
counting them as accepted or complete coverage. Exercise the real bundle importer
and negative hash/timing cases, not only the composition decoder.
**Why:** source schema support alone does not establish compatibility through
the full import path. These consumer failures require neither recapture nor
fabricated producer metadata. Evidence: FOCUS-CAMPAIGN-09, six delivered pairs.

### Broad continuation means an integrated outcome, not receipt checkpoints (2026-10-01)

**Wrong:** Repeatedly end at a status refresh, archive receipt or prepared helper and
ask the maintainer to authorize the next already-implied step. The maintainer again
reported this regression after TEMP-FOCUS-02 and the campaign status update.
**Correct:** For a broad implementation continuation, name an integrated tranche
covering intake, evidence checks, review readiness, eligible experiments and parallel
unblocked work. Track remaining work to concrete input/authority dependencies.
A status-only request remains status-only; it does not itself dispatch execution.
**Why:** Useful evidence boundaries should not become repeated conversational gates.
Human review and actual data eligibility still cannot be silently manufactured.

### Brightness rules and compression need scoped evidence (2026-10-01)

**Wrong:** Generalize a white Settings highlight rule to artwork, or assume preserved
mean brightness after downsampling preserves thresholded pixel evidence.
**Correct:** TEMP-FOCUS-02matches109Settings controls but produces58FP on315mixed
development controls and48FP on48white-artwork negatives. Gate any future rule by
validated screen context; do not use annotation family as a deployed recognizer.
16/32pixel body summaries changed7of557rule decisions despite nearly identical mean
luma. Test the actual thresholded feature and thin cues, not just average error.
**Why:** A useful Settings-specific heuristic is not a universal focus detector;
compression can erase the signal while an aggregate similarity measure stays stable.

### Qualify actual MPS mask-pooling dimensions before encoding (2026-10-01)

**Wrong:** Assume CPU success for area resizing a432pixel mask to14feature cells
establishes MPS support. MPS adaptive-average-pooling rejects non-divisible sizes.
**Correct:** Test the actual dimensions on the intended device. Resize the small,
label-free mask explicitly on CPU and transfer the reduced mask to MPS; retain
encoder features and weighted pooling on MPS. Do not silently switch the encoder
or enable global fallback. Preserve the failed receipt and account for its time.
**Why:** FOCUS-CONTEXT-04's first encoding failed before cache creation. The exact
432→14smoke test and corrected full693scene pass succeeded; this was a backend
compatibility failure, not evidence against the representation hypothesis.

### Audit actual failure structures before scaling a successful annotation flow (2026-10-01)

**What went wrong:** Correct automatic boxes and twelve confidently learned white
artwork crops were treated as likely to fix real artwork failures. The new examples
shared a target slot/layout, while failures included composite heroes, artwork/text
footers and4:1ranked rows. Different recipe hashes did not imply different layouts.
**Correct:** Compare failed original screens, actual model inputs and added examples;
separate structural coverage, weighting and preprocessing hypotheses. In
FOCUS-TRANSFER-10 all1895production crops replayed pixel-exact. A10×relative
emphasis test preserved fixture label budgets and nonfixture weights, yet moved
artwork3→4/12 while increasing false positives25→29; reject that setting rather
than report the extra hit as a win. Native aspect-fit tests distortion separately;
proportional aspect-fit still does not preserve absolute focus enlargement.
**Why:** A reliable annotation pipeline proves label delivery, not transfer learning.
Scale a specified missing visual distinction, not merely the number of valid files.

### Preserve growth without confusing scrolling with focus (2026-10-01)

**Wrong:** Independently resize both focus states and expect absolute enlargement
to remain; or fix a crop in screen coordinates while the control scrolls away.
**Correct:** Shared-scale windows preserve growth (Paired11Home6/6versus0/6normalized),
but track translation independently or abstain. The retained Accessibility Shortcut
moves161px; its old window becomes dark background and incorrectly looks unfocused.
Do not count geometry-only matches after row removal as stable identities. Separate
clipped context eligibility for edge probes from same-window brightness availability;
keep the original experiment when testing that correction.
**Why:** Growth is useful evidence, not a universal rule. Content replacement and
lighting can imitate focus. Reversed/reused pairs are not independent trials, and
externally supplied context flags do not prove a runtime safety detector.

### Shared visible support preserves scale at viewport edges (2026-10-01)

**Wrong:** Reject every translated crop that clips a different amount, or silently
resize each clipped window independently. Alignment12's first rule rejected seven
forward retention rows even after finding their texture correspondence.
**Correct:** Trim equal context from both windows using the intersection of their
visible support; preserve equal dimensions and reject if that removes the nominal
body. Keep translated control bounds separate from proxy native-crop request bounds.
The isolated correction recovered18/18retention directions, including the161pxscroll,
without changing matching thresholds. Native edge tests have one-code-value border
rounding differences: do not claim bit equality merely from identical geometry.
**Why:** Translation recovery and growth preservation are compatible, but rigid
texture matching still rejects enlarging artwork and content changes can mimic focus.
Neither improved retention nor caller-supplied flags proves safe autonomous control.

### Visibility metadata must reach annotation projection (2026-10-01)

**Wrong:** Validate optional native hidden/alpha fields but still emit every focusable
rectangle as an annotation. A hidden or transparent view can retain valid geometry.
**Correct:** New sealed review projections exclude explicit hidden/zero-alpha views;
focused/invisible conflicts block their frame/pairs. Keep partial alpha reviewable,
missing fields unknown, and original observations intact. Pin projection behavior so
existing sealed batches replay with their original policy. FOCUS-VISIBILITY-16 tests
exercise real intake/crops and replay the retained50frame batch unchanged.
**Why:** An invisible control is not an unfocused visual training example. Schema
acceptance alone does not mean new observations are respected downstream.

### Opposing visual changes are corroboration, not focus causality (2026-10-01)

**Wrong:** Treat one brightening and one dimming control as proof that focus moved.
**Correct:** Require complete candidate coverage and persistent identity, but still
label the result a candidate. FOCUS-INTAKE-13's actual two-row pixel counterexample
changes only content colors and yields departure/arrival plus a false scene switch.
Requiring both directions reduced retained correct results11→7of12; resolving every
background control rejected all12. The four additional abstentions were caused by
unavailable background matches despite a valid gain/loss pair, not by missing the
departing focus itself. Preserve abstention causes and false-change counts.
**Why:** Aggregating correlated visual evidence cannot distinguish identical pixels
with different causes. Test content-only transitions before adding another safety
rule or declaring model improvement; input receipts alone do not supply focus truth.

### Interruption focus and settling are separate from underlay targets (2026-10-01)

**Wrong:** Treat a stable modal screenshot as a verified underlay-focus training
frame, or convert covered/removed controls into ordinary unfocused examples.
**Correct:** Preserve native and overlay focus independently, exclude covered bodies,
retain missing settling/verification, and keep diagnostic crops separate from admission.
FOCUS-INTERRUPTIONS-17 has stable brackets but8not-settled frames; removal correctly
leaves the requested target unavailable. Its20files are only6unique screenshots.
**Why:** Geometric stability, requested-target success, current focus and sample
diversity are different facts. Repeated interruption controls are not new independent
training coverage, and archive hashes alone do not bind screenshot capture timing.

### Campaign intake must preserve geometry and reduce review fragmentation (2026-10-01)

**Wrong:** Run the old default wrapper-bound reviewer once per newly captured bundle,
then call the resulting collection a balanced campaign review. It repeats human work
and may hide missing planned cases or focused-growth geometry.
**Correct:** Match complete recipe/target membership first, explicitly select measured
body bounds and visibility, crop every usable control, then make one seeded
family-by-focus review. Deduplicate matching pixel/annotation pairs and expose
contradictory labels. Preserve existing seals and human edits on resume; verify the
immutable output membership, not only whichever file hashes a marker happens to list.
FOCUS-CAMPAIGN-INTAKE-19 verifies this with48generated cases and a single8frame editor
queue, plus unchanged retained50frame review. This is software evidence, not live
annotation acceptance or independent-corpus confidence.
**Why:** An efficient review is a representative selection from an explicitly known
population, not an arbitrary concatenation of packet-sized approval requests.

### Carry projection policy through comparison preparation (2026-10-01)

**Wrong:** Validate visibility-aware native reviews, then reconstruct candidates
with the old default projection; or filter to targets before checking whether a
competitor assigns an opposite label to the same pixels.
**Correct:** Replay the batch's declared visibility policy (including legacy absence),
detect conflicts across all candidates, then choose duplicate representatives among
the intended training targets. Keep complete pair membership and unique pixel-pair
counts distinct. FOCUS-READINESS-20's48case software fixture contains only one unique
target pair; its plan correctly proposes two controls rather than96.
**Why:** A successful intake does not prove downstream assembly uses the same geometry,
and filtering/alias ownership must not hide contradictions or manufacture diversity.

### Bind reviewed endpoint images separately from reviewed rectangles (2026-10-01)

**Wrong:** Treat a sealed review or verified editor snapshot as sufficient to attach
its frame-level image/context fields to recorded-action scoring. Snapshot control
validation alone does not prove those separate fields still match the original batch.
**Correct:** Verify exact batch, frame membership, image reference and screen label,
then parse immutable snapshots. Keep pending working edits separate and detect
conflicts with frozen accepted labels. Test a re-sealed revision with a substituted
frame image, as FOCUS-REVIEWED-TRANSITIONS-21 does.
**Why:** Correct rectangles attached to the wrong recorded endpoint produce plausible
but invalid transition scores; a checksum is integrity evidence, not semantic binding.

### Keep harvest-plan membership distinct from visible transition membership (2026-10-02)

**Wrong:** Assume a strict harvest scene validator also qualifies scrolling transition
records, or remove its membership check when planned off-screen IDs are absent from
visible elements. DATA64's scroll records exposed exactly this mismatch.
**Correct:** Record the actual planned/visible disagreement, obtain an explicit
visibility/exclusion contract, and test transition-specific validation separately.
Repeated child labels or asset names such as `film` must also have scene-unique IDs;
parent association does not make a duplicate global ID unique automatically.
**Why:** Valid scrolling can change visibility while identity remains stable. Quietly
dropping checks or guessing scoped identities would conceal genuine correspondence
errors and contaminate before/after labels.

### Brightness change needs spatial support; stability needs absolute differences (2026-10-02)

**Wrong:** Treat mean brightness increase as sufficient focus arrival, or near-zero
signed change as unchanged focus. SETTINGS-STABILITY-23's content replacement caused
a false arrival in the previous rule; positive/negative changes can also cancel.
**Correct:** For the narrow Settings experiment, measure absolute differences for
stability and require distributed same-direction change for highlight evidence.
Retain ambiguous tracking, illumination and incomplete-scene abstentions. Test both
content-only changes and actual focus changes; keep thin-outline/growth-only styles
outside this guard's qualified scope.
**Why:** Content and focus both alter pixels. More decisions are useful only with
explicit false-positive checks and coverage, not a conditional accuracy headline.

### Removing context can remove focus evidence (2026-10-02)

**Wrong:** Promote body-only stability because it resolves more unchanged Settings
rows. SETTINGS-CONTEXT-24 improved33→37correct decisions on retained examples, but
masked away a generated focus outline and falsely declared unchanged.
**Correct:** Keep actual production crops and compare measurement regions explicitly;
test neighboring-control changes and outside-body focus effects as separate cases.
Scope any region-specific rule to demonstrated focus styles. Preserve counterexamples
even when the small retained development score improves.
**Why:** Neighbor contamination and legitimate focus decoration occupy the same
surrounding region. Removing both improves apparent stability but can hide a real
focus change; geometry alone does not distinguish their meaning.

### Updated host does not imply updated Fixture annotations (2026-10-02)

**Wrong:** Infer repaired rendered-body annotations from a new host CLI, passing
planner or a successful native capture. Spike26's host compiled a structural-v3
plan, while the installed Fixture still reported native-effect geometry unmeasured;
a legacy native-image capture nevertheless completed successfully.
**Correct:** Check actual Fixture geometry source/status on the captured scene before
scale-up. Pin host/helper and installed Fixture separately. An accepted pair with
layout-only geometry remains unsuitable for measured-body training. Obtain the
matching source and build locally rather than repeatedly regenerating legacy labels.
**Why:** Host and Simulator app can be updated independently. Planning, capture and
annotation-contract compatibility are separate boundaries.

### Common-scale focus crops can include the competitor (2026-10-02)

**Wrong:** Increase crop context to35% to preserve native growth/shadow without
checking nearby controls. Native26's first25pairs included a neighbouring focused
body in17/50common-window images, providing an unintended alternate focus signal.
**Correct:** Measure context overlap against observed bodies in both frames before
encoding. A fixed before-anchored20%window passed the first150pairs while retaining
visible growth; continue checks across every layout rather than treating20%as universal.
Keep production per-body crops separate and preserve the failed preprocessing evidence.
**Why:** Accurate boxes alone do not ensure that the model sees only the intended
focus cue. A neighbour can change state during the same pair and become a shortcut.

### Campaign resume does not necessarily retry failed cases (2026-10-02)

**Wrong:** Wait forever on `completed_with_failures`, or assume resume retries a
failed case. Native26 encountered a pre-capture Xcode probe timeout; resume finished
the unattempted cases but preserved the failed case as failed.
**Correct:** Recognize all documented terminal states, reconcile individual cases
and fresh ownership/readiness, then use a separately receipted exact-case recovery
only when the failed boundary makes retry safe. Preserve original failures and count
recovery separately. Do not replay an uncertain input or recapture successful cases.
**Why:** Terminal partial success and resumability are different contracts. Aggregate
"completed" claims can conceal a missing example or duplicate already captured data.

### Native-effect synthetic accuracy is not broad focus qualification (2026-10-02)

**Wrong:** Replace the general focus model because a native-effect specialist scores
highly on held-out synthetic controls. Native26 standard crops improved56.6%→86.6%
synthetically, while real complete-frame decisions regressed12/14→0/14.
**Correct:** Report synthetic recognition and retained real-screen transfer separately.
Common-window100%accuracy requires a known unfocused reference, and may exploit body
occupancy rather than subtle shading. Qualify reference acquisition and held-out real
pairs before integration; compare same-scale context/size ablations before attributing
the gain to any one cue. Preserve the broad model until its scope is independently met.
**Why:** Clean labels and a learnable native effect do not eliminate renderer/domain
shift. Narrow training can learn a useful specialist while producing a bad replacement.

### Cue masking diagnoses sensitivity, not a unique learned mechanism (2026-10-02)

**Wrong:** Interpret Native28's500→398correct after equal-size cropping as proof
that enlargement alone explains focus, or500→250after body masking as proof that
the network learned shading. Both transformations change multiple input properties.
**Correct:** Preserve the exact baseline and replay parity; report scale/context and
mask/distribution confounds. Test negative-only brightness/content changes separately.
Require real paired transfer before choosing an operational cue or confidence policy.
**Why:** A classifier can fail on an artificial mask because it is unfamiliar, and a
resized crop changes both occupancy and surrounding pixels. A useful sensitivity
result is narrower than causal attribution or deployment readiness.
# Retrospective reference matching — October2,2026

Spatial overlap is not control identity. In challenge31, a0.901IoU Settings
candidate paired Automatically Install Apps with Profiles and Accounts after
screen content moved. Keep spatial matches as proposals; inspect content and
viewport before scoring, preserve negative examples, and never convert highIoU
into automatic pair admission. This prevents false before/after labels even when
each original frame's boxes and focus annotations were correctly reviewed.

### Coverage names are not rendered control coverage — diagnosis32

The native-effect training corpus's `row` layout meant a row of artwork tiles,
not native Settings list rows: all1,000training body aspects were1.084–1.761,
while five reviewed controls were7.140–11.049. Audit actual measured geometry and
control rendering, not layout names, before claiming coverage. Also separate
context clipped at the screenshot edge from body clipping: four reference windows
lost context while both target bodies remained fully visible. Preserve production
clamping for labeled offline diagnostics without weakening live eligibility gates.

### A repaired identity contract does not prove action-driven readiness (2026-10-02)

**Wrong:** Accept a delivered scroll/focus case as settled because duplicate child
IDs and off-screen membership were repaired. In transition34, all four movement
endpoints still report observed item-2 against requested item-1, verified=false and
zero stable time. **Correct:** Separate declared/visible/excluded membership with
explicit validation, then independently require consistent native readiness and
image brackets. Preserve the mismatch and ask the producer to clarify/repair the
action-linked readiness contract; never rewrite requested focus in the consumer.
**Why:** Twelve valid unchanged cases can test false-change behavior, but cannot
substitute for the four rejected actual moves or qualify navigation reliability.

### Score selected focus independently of duplicate proposal assignment (2026-10-02)

**Wrong:** Grade focus by whether the selected prediction is the exact index chosen
by a one-to-one box-recall matcher. Two overlapping predictions can represent the
same reviewed row; scorecard36 initially reported 3/7 instead of 4/7 because the
matcher assigned its unselected duplicate. **Correct:** Retain one-to-one matching
for localization recall; independently check the actual selected box against the
focused body and flag ambiguous overlap with multiple truths. Test duplicate boxes
and raw probability versus final selection. **Why:** Bookkeeping must not turn a
correct runtime selection into a false failure. Retain old reports and replay the
same predictions when fixing a metric; never imply new inference or model gains.

### Proposal recovery is not final focus accuracy (2026-10-02)

**Wrong:** Treat ensemble42/46 focused-body coverage as42/46 correct focus selections.
**Correct:** Report candidate recall alongside candidate burden (1,084→2,289 here),
duplicate suppression, and then independently score the actual selector on those
boxes. Unmatched proposals on partial annotations remain unreviewed, not false positives.
**Why:** Vision rectangles recovered useful bodies but also increased competing
regions; proposal improvement can coexist with unchanged or worse final selection.

### Dataset switches are not isolation guarantees (2026-10-02)

**Wrong:** Assume Ultralytics `cache=False` prevents adjacent `.npy` reads/deletion,
or `val=False` prevents final-epoch and final-checkpoint validation.
**Correct:** For immutable USB corpora use an in-memory-label dataset that disables
the adjacent cache path. For final-only evaluation, exclude evaluation membership
from both trainer loaders, override validation hooks, and explicitly score fixed
last-epoch weights after completion. Test the resident implementation, not only flags.
**Why:** Both default behaviors survive the apparently disabling switches. They
can mutate originals or allow held-out evaluation to influence checkpoint selection.

### Avoid decoding the corpus twice inside the training budget (2026-10-02)

**Wrong:** Repeat the complete image decode/pixel-duplicate check inside the owned
training child after the parent has just verified the same originals.
**Correct:** Bind the parent's validated result by hash, then recheck source bytes,
annotations, admission, runtime and code in the child. Reuse decoded dimensions and
pixel identities only when original byte hashes still match. Changed inputs fail.
**Why:** The2500-frame read/decode check took211seconds before any training;
duplicating it would consume most of a300second run envelope.

### Preserve completed fitting when terminal scoring is interrupted (2026-10-02)

**Wrong:** Treat a combined training/scoring timeout as a failed model fit and
restart training, or report quality from only the frames scored before interruption.
**Correct:** Save the completed epoch count and fixed checkpoint hash before scoring;
time scoring separately and retain per-frame predictions. Finish evaluation against
that exact checkpoint and complete membership, preserving the original partial receipt.
**Why:** FSF001 finished fitting in238.57seconds but exhausted its old300second
envelope during scoring. Reusing the completed fit produced the full500frame result
without another training run or selecting a different checkpoint.

### Separate reviewed negatives from unlabeled regions (2026-10-02)

**Wrong:** Classify every non-target prediction on a partially annotated frame as
unreviewed, hiding predictions that overlap explicitly reviewed unfocused controls.
**Correct:** Match predictions against reviewed focused and unfocused bodies first;
reserve unknown status for genuinely unreviewed regions. Restrict whole-frame AP and
exhaustive selection scoring to completeness-confirmed frames.
**Why:** REAL-TRANSFER-42 contains46known-unfocused overlaps and11unreviewed predictions.
Combining those obscured a real failure mode even though partial labels cannot support
a blanket false-positive judgment for every unmatched box.

### Identify the running build's source workspace before declaring a feature missing (2026-10-02)

**Wrong:** Inspect the familiar Documents/TVTestRig checkout and conclude the newly
running app lacks reference generation because that checkout is old.
**Correct:** Discover the actual running executable, its matching helper and build
workspace; test its advertised contract. Record checkout revision separately from
loaded-image attestation, and preserve other checkouts unchanged.
**Why:** TTR43 ran from Developer/TVTestRig87e59be5 while Documents remained46dce7b.
The new app successfully generated native controls and rich catalog/guide pairs.

### Reference measurement anchors are not focusable controls (2026-10-02)

**Wrong:** Require each UIKit measurement anchor to report focusable=true, or require
the planned native control inventory to equal only the fully visible controls.
Both rejected valid reference exports; scroll navigation also need not retain a
requestedID equal to the newly observed focus.
**Correct:** Validate the versioned reference recipe, exact visible-plus-excluded
membership, semantic exclusion evidence and measured bodies. Use observed native
focus and planned identities; keep an anchor's unknown focusability unknown. Allow
the explicit native-navigation mode only in its transition contract, preserving
initialRequestedID separately. Keep older contracts strict.
**Why:** Reference44validated36real deliveries and468crops without inventing focus,
including1476clipped/offscreen planned-control observations across72frames.

### Review validation must not import the model-analysis dependency tree (2026-10-02)

**Wrong:** Import OpenCV evaluation helpers at module scope in a file also used for
reference contract validation. The isolated Qt review interpreter then crashes before
opening even though no pixel analysis is requested.
**Correct:** Keep contract validation lightweight; import analysis dependencies inside
the execution function. Test actual review-environment imports with cv2, torch,
ultralytics and coremltools explicitly blocked.
**Why:** Reference45's first real annotator launch failed on a transitive cv2 import
despite earlier startup-doctor success. The repaired actual caller opened all12samples.

### Cache paths must exist before importing inference libraries (2026-10-02)

**Wrong:** Set YOLO_CONFIG_DIR to an absent project directory and assume the library
will create it there. Ultralytics fell back to /tmp and created settings outside the
allowed project boundary in the first reference45attempt.
**Correct:** Create and verify project-owned cache parents and the expected library
subdirectory before import. Preserve an interrupted run and reuse only complete,
input/configuration-bound prediction pairs after fixing setup.
**Why:** Environment variables alone do not enforce output placement. Reference45
retained29complete pairs and resumed32without repeating inference or hiding the incident.

### Separate pixel-grid alignment from absolute position sensitivity (2026-10-02)

**Wrong:** Attribute a fixed-content translation failure directly to learned screen
position, or assume higher-resolution inference must preserve focus performance.
**Correct:** Hold resized content and canvas dimensions fixed, translate boxes exactly,
and compare both stride-aligned and unaligned offsets. Check training translation/
scale variation and independently replay baseline predictions before proposing a fix.
**Why:** Priority46native localization fell15/18→0/18with140px shifts but returned
15/18and16/18with128px shifts. Both move content; only the latter preserve32px-grid
phase. Higher-resolution inference also fell to0/18. This supports testing training
invariance first, not blaming clean annotations or merely requesting more central data.

### Record effective data-loader settings, not just trainer arguments (2026-10-02)

**Wrong:** Infer rectangular training from `args.yaml` when a custom dataset constructor
overrides that setting, or treat batch count as optimizer-update count.
**Correct:** Inspect and test the actual dataset caller; record effective geometry,
training-frame count, batches and optimizer steps in the completion receipt. Keep the
same effective preprocessing when isolating augmentation changes.
**Why:** Augmentation47 found historical `rect=true` arguments but an actual square
`rect=False` read-through dataset. Its first one-epoch run processed250batches but
made31optimizer updates because of accumulation. These are different measurements.

### Audit correspondence before trusting guarded transition accuracy (2026-10-03)

**Wrong:** Treat zero wrong guarded decisions as proof that a pixel tracker is safe.
Scoring can discard matches using known after-state identity unavailable at runtime.
**Correct:** Report correct, wrong, abstained and unscorable pixel correspondences
separately from classification; report arrival/departure support explicitly. Keep
experimental tracker features out of a learner whose inference uses another tracker.
**Why:** Correspondence51 doubled correct unchanged decisions15→30, but also doubled
wrong native identity matches5→10 and still recovered none of12positive transitions.
The wider template was therefore not adopted despite zero wrong guarded decisions.

### Preserve layered motion and report transition-class regressions (2026-10-03)

**Wrong:** Assume every feature inside a UI control moves with that control, or
accept an aggregate accuracy gain when departure/arrival coverage disappears.
**Correct:** Separate stationary/background and foreground motion diagnostics from
runtime identity decisions; report each transition class. Keep difficult layered
examples rather than silently simplifying data to accommodate the tracker.
**Why:** Correspondence52 finds6/12native positive boxes with both stationary and
scrolling feature evidence. Zero wrong native matches still recovers0positive
controls; improved Settings aggregate scores hide losing both departures. Consider
paired-image learning instead of requiring successful tracking for every label.
### Do not make label admission depend on a failing baseline (2026-10-03)

**Wrong:** Treat failed pixel correspondence as proof that genuine before/after labels
are unavailable, or feed native after boxes to inference to work around that failure.
**Correct:** Reconstruct source-bound labels independently, keeping geometry/identity
as training targets only; a direct paired-image model may consume those pixels without
tracking. Data-role permission, source grouping and final evaluation remain separate.
**Why:** Direct53recovers29valid known-focus pairs, including14changes, while native
positive tracking remained0/12. This enables a development experiment without new
capture, but does not itself authorize using calibration data for training.
### Score each direct-transition head against its task metric (2026-10-03)

**Wrong:** Interpret low combined BCE/normalized-box-MSE as successful localization,
or explain all development failures as domain transfer without checking training fit.
**Correct:** Report change accuracy and both endpoint box IoUs independently on train
and development, plus joint confident success. Keep training rescoring diagnostic.
**Why:** DTM001loss reached0.009214and training change24/24, but only2/24training pairs
and0/5Settings pairs localized both boxes atIoU0.5. This supports localization-first
diagnosis rather than automatically adding epochs or promoting a fast model.

### Validate an overlap-loss change instead of assuming it fixes localization (2026-10-03)

**Wrong:** Assume GIoU necessarily improves a multi-head regressor, or compare raw
loss magnitudes across different objectives as model-quality evidence.
**Correct:** Freeze membership, seed, architecture, epochs and inference thresholds;
compare per-endpoint IoU, size/center errors and confident joint outcomes. Preserve
the failed comparison before proposing another representation or optimization budget.
**Why:** DTM002's GIoU+L1 objective reduced train paired localization2/24→0/24 and
increased width error despite correct raw change labels. Settings5/5raw classification
still yielded0confident decisions. Neither result establishes navigation readiness.

### Preserve logical identity when relocating evidence (2026-10-03)

**Wrong:** Replace artifact directories with symlinks or assume a verified copy
means every reader can use it. Physical external paths can break repo-relative
image bindings even when every byte is intact.
**Correct:** Resolve approved logical prefixes explicitly, convert physical inputs
back to logical references, and keep output routing separate. Verify real consumer
results before reclamation; retain tracked files and fail closed without the SSD.
**Why:** STORAGE-LIVE-01 first exposed a human-editor `relative_to(ROOT)` failure.
After fixing it and adding regression coverage, the29pair corpus retained its exact
hash before and after local-copy removal. Generic shell tools still need resolved paths.

### Frozen exports must follow manifest membership, not directory contents (2026-10-03)

**Wrong:** Re-export a qualified corpus by globbing all PNGs and assume copied files
have the same membership. Ignore rules also do not remove previously tracked exports.
**Correct:** Use `export_coco.py --manifest-members-only` for frozen corpora. Reject
missing/changed/duplicate manifest members and compare split membership plus label
bytes before accepting a replacement export. Preserve unmanifested evidence separately.
**Why:** STORAGE-LIVE-03 found5,171extra duplicate-named pairs in the retained r7 tree;
the default exporter produced24,911instead of19,740images. Parity checks caught the
error before training. The old r7 export also has39,487tracked files, so its symlinks
and local targets must stay intact until maintainer-directed untracking.

### Check spatial context before scaling a failed localization head (2026-10-03)

**Wrong:** Assume a dense spatial head automatically localizes wide controls, or read
an admitted training-partition score as the fit score of a smaller diagnostic subset.
**Correct:** Record exact fitted IDs; require a tiny memorization gate before scale-up.
Decompose row/column selection, geometry and change loss, and inspect receptive field.
Keep ground-truth-cell/oracle decompositions clearly separate from actual predictions.
**Why:** Spatial56 fitted4pairs: change4/4, vertical cells8/8, but horizontal0/8 and
paired boxes0/4. Its local head sees15×15input pixels; wider context is a hypothesis,
not proof of cause. The failed gate correctly prevented the full candidate launch.

### Correct center cells do not establish usable boxes (2026-10-03)

**Wrong:** Accept total-loss reduction or correct cells as localization success, or
interpret high change confidence as confidence in geometry.
**Correct:** Measure cells, offsets, width/height and paired IoU separately. Inspect
sigmoid outputs near0/1 and their vanishing derivatives before adding epochs. Keep
the full-box gate and separately evaluate abstention/localization reliability.
**Why:** DTM004 learned8/8center cells but0/4paired boxes; heights collapsed while
change remained4/4. All5Settings pairs emitted decisions despite0/5paired boxes.
More context solved one fitted-subset error, not the task.

### Inventory native scroll telemetry before requesting recapture (2026-10-03)

**Wrong:** Label scrolling from box displacement, or assume an earlier coverage
summary exhausts retained evidence. A focused control can stay fixed while content scrolls.
**Correct:** Inspect hash-bound native semantic inventories for consistent per-container
offsets across both capture brackets. Missing or conflicting offsets stay unknown.
Record mutation receipts separately from optional navigation-action receipts.
**Why:** GEOMETRY-58 found observed scrolling in all24Fixture pairs, including pairs
whose focus boxes did not move. Settings5lacks equivalent bound scroll telemetry.
The inventory avoided both fabricated no-scroll labels and unnecessary recapture.

### Pass tiny fit before scale, then measure full fit separately (2026-10-03)

**Wrong:** Treat a4pair diagnostic pass as proof the full training corpus fits, or
attribute every later development failure to domain shift.
**Correct:** Evaluate the exact fitted membership, full-corpus change/localization and
abstention separately. Diagnose training failure before concluding transfer failure.
**Why:** DTM007fit4/4pairs at120epochs, butDTM00830epoch24pair candidate fit only8/24
paired boxes and12/24change labels. All24abstained. Capacity on a tiny set removed
one blocker, not the full optimization/data-coverage problem.

Follow-up: DTM009120epochs fits24/24paired boxes/change but Settings remains0/5
localization with3false changes. Once fit is established, prioritize transfer/coverage
diagnostics instead of treating more epochs as evidence of generalization.

### Retire stale whole-file status writers (2026-10-03)

**Wrong:** Run a historical sync helper containing hardcoded run metrics and a
whole-file status replacement. Directory existence alone does not verify an SMB mount.
**Correct:** The old update/sync entrypoints now fail without writes. Follow the
shared-status guide: verified mount, fresh bounded unique-key YAML read, one owned
packet patch, validation/readback and preservation of unrelated entries.
**Why:** TRANSFER-62 found both helpers could republish September24facts and erase
concurrent packets. Retaining an executable stale snapshot is not useful compatibility.

### Fit is not position robustness (2026-10-03)

**Wrong:** Treat24/24training localization as proof the model follows visual targets.
**Correct:** Freeze the checkpoint and test paired translations with analytically
transformed boxes; reject off-frame truth rather than clipping it. Report rejected
cells separately and keep transformed examples diagnostic-only.
**Why:** DTM009retained24/24boxes on reversal but only11–12/24under4%translations.
This suggests position sensitivity; black-fill/domain changes prevent causal certainty.

### Equal epochs can hide unequal view exposure (2026-10-03)

**Wrong:** Compare120epochs with and without5-way augmentation as equal memorization
opportunity for each view, or call improved synthetic-shift accuracy real-UI transfer.
**Correct:** Record sampled variant counts, model updates and original/shifted/domain
results separately. Test an explicit fixed matched-exposure hypothesis if fit regresses.
**Why:** DTM010saw~24samples per variant versusDTM009120per original. Shifts improved
47/96→82/96while original24/24→18/24 and Settings stayed0/5. Exposure is a hypothesis,
not a proven explanation or permission for an automatic convergence loop.

Follow-up: DTM011600epochs restored24/24original and96/96trained-shift fit, while
Settings stayed0/5and all3frozen models localized0/8retained native negatives. The
matched-exposure test resolves the fitting question, not the transfer question.
Do not repeatedly extend epochs after this gate; test unseen transformations,
appearance shortcuts and missing data coverage instead.

### Reuse verified preparation, not unchecked cached labels (2026-10-03)

**Wrong:** Rebuild native intake and decode the same pixels before every tiny model
comparison, or skip validation entirely to save that overhead.
**Correct:** Cold-validate an admitted corpus once and cache deterministic encoded
inputs. Bind content, labels, roles, preprocessing, code/dependencies and array hashes;
warm use checks those bindings without re-decoding every case. Retain execution gates
and fail closed on changes or missing cache. Measure cold and warm stages separately.
**Why:** DTM011 spent17.4s on intake versus11.5s fit/setup. PREPARED-66 measured30.08s
cold preparation versus0.214s warm verification with exact tensors, without training.
This measures preparation savings, not a claimed end-to-end training speedup.

### Zero-difference probes expose appearance shortcuts (2026-10-03)

**Wrong:** Treat successful training change classification as proof of temporal
reasoning, or treat a duplicated-frame probe as a genuine no-op action label.
**Correct:** Probe identical-frame inputs separately and preserve semantic uncertainty.
Count true native no-ops and content mutations as distinct source conditions. Derive
theme coverage from resolved native recipes, not case names or light-colored artwork.
**Why:** All three frozen models called18/48 duplicated training inputs and10/10
Settings inputs changed. All eight retained negative cases use native dark theme,
even when a case ID includes a light composition palette.

Follow-up DATA-67: admitting those eight native negatives yields32/32training fit
but leaves original duplicated-frame raw change18/48 and Settings10/10. Always pair
fitting improvements with retained counterfactual/domain diagnostics; improved fit
on additions alone does not establish better temporal reasoning. Batch those probes
over shared decoded inputs instead of repeating intake for each model.

Follow-up TEMPORAL-68: an explicit difference-only change branch raises exposed
Settings raw change2/5→5/5 and removes duplicated-frame raw false changes, but boxes
remain0/5. Both true moves still abstain on invalid geometry. Report raw classification,
geometry and usable combined decisions separately; a correct scalar score is not a
usable focus target.315kversus882kparameters did not materially reduce observed
~15mspair latency, so measure preprocessing/forward separately before claiming speed.

### Inspect joint geometry support, not only marginal ranges (2026-10-03)

**Wrong:** Conclude that Settings boxes are represented because their widths and
heights individually lie near the training min/max, or immediately increase resolution.
**Correct:** Inspect actual width×height combinations, position support and error
decomposition. Keep oracle substitutions explicitly scoring-only and reject invalid
predictions rather than clipping them into apparent success.
**Why:** LOCALIZE-69 found only three training shapes and no center pastx48.23on a
96pixel input, versus Settings39×~4boxes atx72.5. Center and extent both fail; marginal
ranges hide that gap. Shared encoding also showed resize9.49s versus forward/decode
0.68s in a two-model replay, explaining why smaller weights did not improve pair latency.

### Batch preparation without equating coverage with transfer (2026-10-03)

**Wrong:** Revalidate/decode the same corpus for every augmentation arm, or assume
covering missing box shapes guarantees native transfer.
**Correct:** Validate once, construct separately identified policy banks from shared
decoded sources, then compare models on identical encoded evaluation inputs. Keep
rejected views and unequal per-view exposure explicit. Measure transfer separately.
**Why:** COVERAGE-70 prepared two banks in32.76s, warm-loaded in~0.2s and fit both
completely, yet both still localized0/5Settings pairs. Batched input reuse is useful;
repeating successful fitting is not evidence that the real detection problem is solved.

### Separate reusable input identity from model identity (2026-10-03)

**Wrong:** Invalidate decoded/encoded inputs whenever unrelated model layers change,
or treat a lost running-job observation as permission to recapture a case.
**Correct:** Pin preprocessing, labels, membership and relevant source-validation code
separately from full training-code pins. Maintain append-only campaign state with
expected revision, immutable evidence and explicit interrupted-job reconciliation.
Rehash reused source members; do not repeatedly decode unchanged accepted captures.
**Why:** CAMPAIGN-71 reuses exact160-view tensors across two model configurations
in~0.17s each. Its interrupted-batch tests preserve accepted work and refuse stale
writers, mismatched recipes, uncertain cleanup and changed pixels. Runtime identity
checks and final full audits remain necessary; journal receipts are not authority.

### Reconcile semantic names before requesting producer features (2026-10-03)

**Wrong:** Assume a feature is absent because the producer does not use our local
condition name, or build another lifecycle controller without checking current source.
**Correct:** Map source-backed wire names explicitly, preserve original bytes and
retain the stronger consumer evidence requirements. Inspect actual planner and runtime
paths separately; model a capability gap at the boundary that actually lacks support.
**Why:** COMPATIBILITY-72 found existing focus_moved and campaign-scoped session reuse.
The real remaining gap is stationary reference planning/qualification, not generic
directional transitions. A focus_moved receipt still needs unchanged-offset checks
to qualify as no-scroll evidence; a light backdrop is not a native light theme.

### Audit retained raw outputs before rerunning proposal generation (2026-10-03)

**Wrong:** Treat empty editor proposal lists as evidence that no automatic geometry
exists, or treat high candidate recall as solved focus selection.
**Correct:** Follow pinned raw artifacts and identify every retained output field.
Measure geometry recall, candidate ambiguity and ranking accuracy separately; keep
human-box pools explicitly oracle-only.
**Why:** PROPOSALS-73 recovered rectangle proposals from an existing native-ocr.json:
10/10focus endpoints were covered, despite empty/missing editor lists. No fresh
Vision run was necessary. Coordinate snapping still failed paired localization,
supporting a visual-ranking test rather than more coordinate-regression epochs.

### Test proposal coverage on both sides of the domain boundary (2026-10-03)

**Wrong:** Choose a proposal generator because it covers all training examples, or
force a single positive when several overlapping boxes satisfy the geometry target.
**Correct:** Measure automatic recall by source/domain before training a ranker, keep
multi-positive supervision, and preserve missing examples. Reuse fixed alternatives
without feeding them human boxes or tuning against exposed development labels.
**Why:** PROPOSAL-RANK-74 raster covered64/64Fixture endpoints but0/10Settings;
Vision covered40/64Fixture and10/10Settings. Their union covers all74 but has40
multi-positive training endpoints. Recall establishes feasibility, not focus accuracy.
One deduplicated batch and retained development outputs avoided repeated native setup.

### Batch by source image, not by candidate box (2026-10-03)

**Wrong:** Decode the same screenshot for every box or invalidate all input work
after a dispatcher/model-only edit. Treat successful training fit as transfer proof.
**Correct:** Cache decoded sources within one bounded crop request, reject conflicting
hashes for a path, retain per-box validation, and budget distinct decoded images.
Keep prepared image encodings separate from labels and model pins; reuse only with
matching source hashes, encoding/runtime and original preparation dependencies.
**Why:** RANK75prepared2,141crops from59images once in29.64s; warm verification took
0.130s and600epoch fit1.014s. Dispatcher repair reused the bank without recropping.
Despite64/64training endpoint fit, all10Settings endpoints failed. Faster preparation
supports controlled experiments; it does not remove the need for native domain data.

### Consume retained improvements before scheduling another acquisition (2026-10-03)

**Wrong:** Treat a stale local producer capability inventory as proof no usable
data exists, or infer no scrolling from an observed focus move. Assume overlapping
export is faster because it is concurrent.
**Correct:** Check named peer handoffs, receive exact immutable artifacts and audit
new source contracts. Preserve unknown offset evidence. Reuse campaign runners and
measure complete wall time; export only terminal checkpoints and keep serial default
until overlap has a workload-specific measured benefit.
**Why:** NATIVE-INTAKE76 recovered36pairs without simulator setup;12older native-table
pairs pass inspection but cannot prove no scroll, while newer rich data reports8
stationary moves and needs source uptake. TTR's reported reuse trial cut collection
time62.8%; its separate small grouped trial found overlap25.8%slower than serial.
These are producer-reported scopes, not NUIAK runtime measurements or multiplicative gains.

### Pixel identity requires a pinned decoding convention (2026-10-03)

**Wrong:** Compare two fields called decoded hash without checking RGB/RGBA, size
prefix and separators. A mismatch need not indicate changed pixels; a comparison
across conventions cannot establish duplicate exclusion.
**Correct:** Bind original file SHA256 first, then recompute all compared pixel IDs
under the existing corpus convention. Preserve original intake hashes separately.
**Why:** NATIVE77caught RGB-with-separator intake hashes versus RGBA training hashes
before admission. Rebuilding12pairs with the training convention established zero
overlap against existing train/development without rewriting source evidence.

### Image derivative reuse must not imply data admission (2026-10-03)

**Wrong:** Recompute unchanged crops for each model/role change, or treat a cached
tensor as permission to train on the associated calibration image.
**Correct:** Bind immutable image derivatives to byte identity, geometry and actual
preprocessing/runtime/dependencies. Bind supervision, roles and model authorization
separately. Reject corrupt/partial entries; never rewrite old seals to obtain reuse.
**Why:** BATCH79's actual83image inspection reused59entries while preparing24new ones;
the next pass made zero crop calls. Original2141tensors/crop hashes remained exact.
All calibration data stayed training-ineligible. Generated NumPy arrays also need
artifact ignore coverage; report JSON ignore rules alone do not protect them.

### Native virtualization needs measured exclusions (2026-10-03)

**Wrong:** Require every planned native cell to have a visible wrapper, or treat
clipped wrappers as conflicting merely because they also have exclusion records.
**Correct:** Source-pin planned identity, visible measurements and typed exclusions.
Offscreen virtualized cells may lack wrappers; hidden/clipped exclusions require
matching wrapper evidence. Focused targets must remain visible and measured.
**Why:** NATIVE84 qualifies 60 retained rich/collection pairs without dropping
labels or recapturing. Source presence and passing inspection still do not grant
training roles or establish runtime health.

### Single-decode validation without changing identity (2026-10-03)

**Appearance-head identity invariant (RESOLUTION96):** paired RGB context increased
joint training fit to67/68but predicted35confident changes when an identical training
frame appeared on both sides. Test same-frame pairs before trusting improved aggregate
fit, especially when a source appears only with one label. Keep constructed probes
separate from genuine navigation and training admission; they do not test moving
backgrounds or prove the cause of the shortcut. DTM018difference-only reference passed.

CHANGE92 follow-up: semantic preparation was rebuilding the same reviewed baseline
immediately after readiness had validated it. Return the audit and validated frames
together and reuse within that call; do not add a global stale cache. Full73record
parity holds; baseline traversals2→1 and source checks9031→4661. Keep raw accuracy,
confidence-gated decisions and joint correctness separate: DTM021's extra raw
correct decision concealed six new no-op abstentions, so it was rejected.

**Wrong:** Decode an endpoint to get dimensions, then reopen it to compute its
decoded hash; or optimize by hashing RGB and silently dropping alpha.
**Correct:** Verify source bytes and decode once, returning dimensions and the
existing RGBA pixel hash together. Pin the shared helper in new execution protocols;
preserve historical seals. Profile full preparation separately from this stage.
**Why:** PREP91 preserved all73 records while reducing146-endpoint validation from
11.88s to7.02–7.21s. Full source traversal still dominates, so this is not a40%
end-to-end improvement. Reuse must not remove integrity or role checks.

### Export byte identity and portable admission tests (2026-10-03)

**Wrong:** Locate a manifest beside a receipt without reading the receipt, or let
admission regression tests skip entirely when a developer lacks private corpora.
**Correct:** Bind completed receipt/case identity, exact selected inventory and the
original manifest's input_manifest_sha256/byte count. Do not confuse the producer's
semantic manifest_sha256 with its byte hash. Generate small regression fixtures;
retain real corpus replay as separate integration evidence.
**Why:** INTAKE82 found selection validation never read source_receipt, despite
using its directory. The strengthened check passes all24 retained selections and
rejects missing/partial/mismatched evidence. Five admission tests now run without
retained files; this does not make generated tests proof of real-data eligibility.

### Candidate scale is not control identity (2026-10-03, RANKING-97)

**Wrong:** Treat five erroneous endpoint occurrences as five independent scenes,
or propose a minimum-size rule because exposed Settings errors select text fragments.
**Correct:** Group by source image, normalize geometry by actual image dimensions,
inspect both small-fragment and enclosing-region failures, and audit small positive
support before any size intervention. Check whether normalized size is already an
input before proposing it as a new feature. Logit margins are not probabilities.
**Why:** RANKING-97's five errors are four images; the frozen ranker already receives
size. Training has no sub100px positive candidates, and errors include both tiny
disjoint fragments and a large multi-row region. A size cutoff could conceal missing
coverage instead of teaching complete-control selection. See
[review](../reports/work/RANKING-97/handoff.md); no causal feature attribution is claimed.

### Inspect completed cases without rewriting failed campaign history (2026-10-03, INTAKE101)

**Wrong:** Reject every completed case in a mixed-outcome campaign, or rename the
campaign completed to reuse them. Count PNG byte hashes as unique visual examples.
**Correct:** An explicit case-level intake may select only completed cases with
original receipt/manifest/member byte binding. Preserve the failed accounting and
separate repair receipt; require complete expected membership and reject duplicate
selected IDs. Report decoded-pixel duplicates separately and retain intentional
no-change endpoints, linking their ancestry for all later split decisions.
**Why:** Context60 contains61attempts,60completed cases,96unique PNG byte hashes
but86decoded images. Discarding no-change duplicates would erase useful negative
evidence; treating them as independent examples would overstate support. No parser
pass changes calibration membership into training or final evaluation authority.

### Identity negatives are a sanity check, not real no-op coverage (2026-10-03, CALIBRATION102)

**Wrong:** Interpret zero errors on constructed same-frame pairs as robustness to
content animation, artwork changes or other visual changes without focus movement.
**Correct:** Evaluate observed focus moves, boundary no-ops and content-only no-ops
separately; retain confidence errors and candidate coverage versus selection metrics.
Use real action-linked negatives before claiming transition reliability.
**Why:** DTM024 passed122identical-frame negatives but falsely reported focus changes
on all12new content-only negatives. In the same40pair replay, proposals covered
80/80targets while the ranker selected only10correct endpoints. These are distinct
learning failures, not a reason to recapture already verified evidence or inject
ground-truth boxes into inference. [Evidence](../reports/work/CALIBRATION-102/handoff.md).

### Keep component and domain retention gates when adding data (2026-10-03, COLLECTION104)

**Wrong:** Call a combined model improved solely because it fits newly admitted data,
or count a low-confidence correct class as a successful joint decision.
**Correct:** Compare each changed component against the frozen other component;
report old training, new training and exposed development separately. Joint success
requires correct change, confidence admission and both correct boxes. Preserve
failed candidates and the prior component; do not train on the development set to
erase its regression. Reuse byte-bound tensors/crops, not new native capture.
**Why:** DTM025 removed12content-only false changes without retention loss; DTM026
fit80/80new endpoints yet regressed Settings5/10→0/10. The combination's40/40new
joint score therefore did not justify deployment. Cached binding took1.94s with
zero native calls. [Evidence](../reports/work/COLLECTION-104/handoff.md).

### Native transition delivery needs input parity and whole-path timing (2026-10-03, TRANSITION-SHADOW106)

**Wrong:** Treat successful Core ML conversion as native inference qualification,
or substitute an approximate resize and report model-only latency as caller cost.
**Correct:** Independently verify conversion, load, exact native encoded tensors,
scores/decisions, and a clean portable consumer. Pin resampling/color/letterbox
semantics; preserve unsupported-image failures and a true no-model off mode.
Measure preprocessing separately and keep passive inference off navigation's path.
**Why:** DTM025's model runs at0.326ms median locally but validated full-frame
preprocessing takes169ms.240pair byte/decision parity and a separate extracted
source build establish compatibility, not unseen-app accuracy. A sandbox-cache
load denial was distinct from successful package conversion. Deliver the qualified
change component without bundling the regressed localization ranker.

### Retention means preserving previous successes, not just an aggregate count (2026-10-03, RANK-RETENTION105)

**Wrong:** Count repeated endpoints as independent scenes, infer missing proposals
from ranking errors, or assume freezing the final layer preserves the decision rule
when upstream features can change.
**Correct:** Deduplicate source frames, measure proposal coverage separately, and
track exactly which formerly correct frames were lost. Verify frozen tensors from
the saved checkpoint as well as in-loop assertions; receipt fields can have bugs.
**Why:** All9Settings frames had correct proposals; DTM027 kept its final layer
exact but lost all5previous correct selections. Its1new success did not constitute
retention.108training pairs fitting correctly did not establish transfer. A reused
variable corrupted frozen-parameter names in the first receipt; independent tensor
comparison caught the reporting discrepancy without rerunning training.

### Diagnose the scoring rule before blaming representation resolution (2026-10-03, RANK107)

**Wrong:** Infer that small encoded crops cannot represent focus solely because a
trained head fails, or declare a post-hoc distance rule generalized because it fits
the same exposed development failures that motivated it.
**Correct:** Check opposite-label collisions, training-only reference neighborhoods,
query-frame exclusions and reference-cohort sensitivity. Separate information-loss
evidence from a poor learned decision boundary and inadequate source coverage.
**Why:** No exact conflicts appeared among5022candidate encodings. A fixed distance
contrast selected9/9Settings controls using older training references but0/9using
new-only references. It still lost one old training-frame success; this supports
another bounded scoring hypothesis, not production readiness or proof that16×16
is universally sufficient. Full training references share Fixture ancestry.

### Separate reference replay from extent retention (2026-10-04, RANK108)

**Wrong:** Count nearest-neighbor self-matches as generalization, or call a correct
row location a correct box when its extent misses the IoU gate.
**Correct:** Exclude same-frame references for the diagnostic, report self-allowed
replay separately, and inspect extent/IoU against unchanged labels. Use direct
float64 differences with bounded blocks; verify all scores against the naive
oracle before optimizing distance arithmetic. Keep related recipes labeled as
training diagnostics, not independent tests.
**Why:** Self replay122/122old became121/122without self references. The failing
guide row had a correct available proposal at0.516IoU, but the chosen sub-row was
0.419. Successful Settings replay did not waive that regression. The full bank
also costs14.78MB before metadata and preprocessing, unlike the small learned head.

### Binary supervision can hide inconsistent precise geometry (2026-10-04, RANK109)

**Wrong:** Assume that consistent positive proposal IDs imply one valid continuous
box target per image, or use last-write-wins when deduplicating supervision.
**Correct:** Before geometry regression/ranking, group exact image identities,
retain all endpoint annotations, and reject conflicting precise targets. Trace
back to original bracket telemetry, not only derived manifests. Diagnostic IoU
ranges may describe uncertainty but are not automatic relabeling authority.
**Why:** Eleven context60 images had two extents with identical binary-positive
sets. Each before/after bracket was internally consistent, but separate captures
of identical bytes differed. Existing binary metrics remain reproducible while
the new continuous objective requires source correction/review. Settled bracket
telemetry alone does not prove consistent image-to-geometry binding across runs.

### Name the transition target before scoring peer feedback (2026-10-04, SHADOW110)

**Wrong:** Treat "focus changed" as interchangeable with moving highlight geometry,
or count native-ID disagreements as reviewed model accuracy.
**Correct:** Keep focus-owner identity, highlight geometry and content motion as
separate fields. Join independent labels after inference through exact action,
observation and image hashes. Report native-hint disagreements separately; reviewed
abstentions and execution failures must remain visible outside selective accuracy.
**Why:** TTR reported eight identity-changing scrolling pairs with stationary focus
boxes and unchanged DTM025 decisions. The intended identity target makes these
potential misses, not successes; source/review evidence is still required to confirm
them. Changing the target post hoc would conceal a real coverage limitation.

### Review the complete journey without turning strips into training crops (2026-10-04)

**Wrong:** Admit native focus hints from a few representative screenshots, or treat
a focus-strip review as precise body-box ground truth and independent evaluation.
**Correct:** Review every candidate label in sequence with hash-bound visual context;
use fixed inspection strips only for identity confirmation. Keep original full frames
for the existing encoder, separately record reviewer type, and exclude the entire
related journey/layout ancestry from final evaluation after failure-driven selection.
**Why:** Region12's95selected row texts corroborated94identity changes despite a
stationary highlight. This enables change-only training without pretending AX bounds
are rendered-body labels. Its all-positive traversal still lacks genuine same-focus
motion negatives; derived identical pairs do not fill that coverage gap.

### Counterfactual improvements need negative controls (2026-10-04, REGION113)

FOCUS116: restricting differences to even oracle focus boxes repaired reflow but
lost13previous positive successes. Do not deploy an input mask solely because it
fixes one reviewed failure; evaluate positive retention and label-free localization
separately. Explicit supervised admission of exposed cases is distinct from an
inference shortcut and cannot supply independent evaluation evidence.

REFLOW115 further showed similar pixel-difference magnitude for a failed real
unchanged-focus reflow and successful existing negatives. Match negative examples
by renderer/layout and semantic event, not just aggregate change magnitude. A
focused item's identity can remain unchanged while many other rows are inserted,
removed or moved; those are important separate negative controls.

Follow-up IDENTITY114: exact identity cancellation preserved217identical negatives
while a real unchanged-focus Settings transition became confidently wrong. An
algebraic no-op guarantee does not protect scrolling, animated content or other
nonidentical-frame negatives. Evaluate genuine motion negatives separately; never
use the perfect identical-frame score as evidence of real-world no-change safety.

**Wrong:** Remove context at deployment because a difference-only intervention
increased responses on positive scrolling examples.
**Correct:** Compare identical and real negative cases, retain original baseline
replay, and label channel/spatial ablations as sensitivity experiments rather than
accuracy or proof of causality. Gradients alone also do not establish semantic use.
**Why:** DTM028's difference-only Region responses rose26→79, but all217identical
checks became uncertain at~0.645. Outside-focus motion retained20of26responses.
Positive-only improvement concealed a worse no-change decision surface.

### Optimize the measured inference pipeline, not only the network (2026-10-04, SHADOW120)

**Wrong:** Treat0.5ms network inference as end-to-end cost, or cache pixels by a
filename/timestamp and skip integrity checks on later accesses.
**Correct:** Measure decode/resize/hash preprocessing separately. Use bounded
request-owned encoded-frame reuse only after freshly validating path/size/current
bytes hash; retain no full-resolution cache. Preserve integer filter coefficients,
rounding order and exact tensor hashes when optimizing resize loops.
**Why:** DTM030preprocessing dominated. Combined integer-loop optimization and
8frame encoded reuse reduced identical438pair replay86.159→53.436s and median
preprocessing183.869→120.219ms without changing any input tensor or decision.
Consecutive local measurements are not a universal throughput guarantee, and
2359296cached tensor bytes is a payload bound—not total process peak memory.
