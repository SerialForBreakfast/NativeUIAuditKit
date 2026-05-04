# Coordinate Spike — NativeUIAuditKit Phase 1

**Status:** COMPLETE  
**Phase gate:** Must complete before Phase 2 (taxonomy schema) and Phase 3 (dataset generation at scale)  
**Fixture code:** `CoordinateSpike/` · **Test runner:** `CoordSpikeRunner/CoordSpikeRunner.xcodeproj`  
**Run script:** `CoordinateSpike/Scripts/run_spike.sh`

---

## Purpose

Dataset generation requires knowing the **precise pixel bounding box** of every element in each
generated screenshot. This spike validates that the coordinate pipeline produces annotations that
align with ground truth at ≤2px tolerance on both @2x and @3x Simulator output.

Questions answered by this spike:

| # | Question | Answer |
|---|----------|--------|
| 1 | Does `GeometryReader` (global frame) match declared ground truth? | **Yes — 0 pt delta at both scales** |
| 2 | Do point coordinates × scale factor equal PNG pixel coordinates? | **Confirmed — pixel sampling validates blue tint at exact bounds** |
| 3 | Do @2x and @3x outputs both satisfy ≤2px alignment? | **Yes — 0 px delta at both scales** |
| 4 | Are partially-clipped elements bounded to their visible rect? | **No — GeometryReader reports layout frame; generator must clip manually** |

---

## Fixture Design

The spike uses a single, deterministic SwiftUI scene with **three elements at fixed positions**:

```
┌─────────────────────────────────┐  ← device top (y = 0)
│                                 │
│  [  Primary Button  ]           │  ← A: 200×44pt at (40, 100)
│                                 │
│  [_ Text Field ___________]     │  ← B: 280×44pt at (40, 164)
│                                 │
│  Static Label                   │  ← C: 200×30pt at (40, 228)
│                                 │
└─────────────────────────────────┘
```

The `ZStack` applies `.ignoresSafeArea(.all)` so the coordinate origin is the physical screen
top-left — eliminating safe area as a variable. Elements are positioned with padding (not `.offset()`)
so `GeometryReader` captures the true global frame.

**Ground truth (points, portrait, any device):**

| Element | x | y | width | height |
|---------|---|---|-------|--------|
| Button | 40 | 100 | 200 | 44 |
| TextField | 40 | 164 | 280 | 44 |
| Label | 40 | 228 | 200 | 30 |

**Expected pixel coordinates (@2x):** multiply each value by 2.  
**Expected pixel coordinates (@3x):** multiply each value by 3.

---

## Setup — Option C: UIHostingController Hosted Unit Tests

**Why not XCUITest?** The dataset generator (Phase 3) uses `UIHostingController` + `GeometryReader`
to export frames, not XCUITest accessibility APIs. Testing `XCUIElement.frame` would validate a
different mechanism than the one actually used in production.

**Chosen approach:** Hosted `XCTestCase` methods that render `CoordSpikeView` via
`UIHostingController` in an off-screen `UIWindow`. Frames are captured via the
`onFramesCaptured` callback (SwiftUI `PreferenceKey`). Screenshots are captured via
`UIGraphicsImageRenderer`. No XCUITest APIs used.

### Requirements

- Xcode 16+ (iOS 17+ deployment target)
- Simulators: iPhone 17 Pro @3x + iPhone SE 3rd gen @2x (see UDIDs in `run_spike.sh`)

### Running the spike

```bash
# From the repo root — runs both simulators:
bash CoordinateSpike/Scripts/run_spike.sh

# Single test method:
bash CoordinateSpike/Scripts/run_spike.sh testGeometryReaderAlignment

# Direct xcodebuild (iPhone 17 Pro @3x):
xcodebuild test \
  -project CoordSpikeRunner/CoordSpikeRunner.xcodeproj \
  -scheme CoordSpikeRunner \
  -destination "platform=iOS Simulator,id=812EDC32-DB8D-49D6-B130-2279180CCDEB"

# Direct xcodebuild (iPhone SE 3rd gen @2x):
xcodebuild test \
  -project CoordSpikeRunner/CoordSpikeRunner.xcodeproj \
  -scheme CoordSpikeRunner \
  -destination "platform=iOS Simulator,id=1A331965-FAA7-477E-A1D1-51B2868D6A88"
```

---

## Results

### iPhone 17 Pro Simulator — @3x (393pt wide × 852pt tall, iOS 26.4.1)

Tested: 2026-05-04 · All 6 tests passed

| Element | Declared (pt) | GeometryReader (pt) | Max edge delta |
|---------|--------------|---------------------|----------------|
| Button | 40, 100, 200×44 | 40, 100, 200×44 | 0 pt |
| TextField | 40, 164, 280×44 | 40, 164, 280×44 | 0 pt |
| Label | 40, 228, 200×30 | 40, 228, 200×30 | 0 pt |

**Scale factor:** 3.0  
**Pixel alignment within ≤2px:** ✓ Pass

| Element | Expected pixel (×3) | Measured pixel | Max edge delta |
|---------|---------------------|----------------|----------------|
| Button | 120, 300, 600×132 | 120, 300, 600×132 | 0 px |
| TextField | 120, 492, 840×132 | 120, 492, 840×132 | 0 px |
| Label | 120, 684, 600×90 | 120, 684, 600×90 | 0 px |

**Vision-normalized (button, origin bottom-left, [0,1]):**  
x = 120/1179 ≈ 0.1018 · y = 1 − 432/2556 ≈ 0.8310 · w = 600/1179 ≈ 0.5089 · h = 132/2556 ≈ 0.0516

---

### iPhone SE (3rd gen) Simulator — @2x (375pt wide × 667pt tall, iOS 17.5)

Tested: 2026-05-04 · All 6 tests passed

| Element | Declared (pt) | GeometryReader (pt) | Max edge delta |
|---------|--------------|---------------------|----------------|
| Button | 40, 100, 200×44 | 40, 100, 200×44 | 0 pt |
| TextField | 40, 164, 280×44 | 40, 164, 280×44 | 0 pt |
| Label | 40, 228, 200×30 | 40, 228, 200×30 | 0 pt |

**Scale factor:** 2.0  
**Pixel alignment within ≤2px:** ✓ Pass

| Element | Expected pixel (×2) | Measured pixel | Max edge delta |
|---------|---------------------|----------------|----------------|
| Button | 80, 200, 400×88 | 80, 200, 400×88 | 0 px |
| TextField | 80, 328, 560×88 | 80, 328, 560×88 | 0 px |
| Label | 80, 456, 400×60 | 80, 456, 400×60 | 0 px |

---

## Frame Export Strategy Decision

**Chosen strategy: Option B — `GeometryReader` + `PreferenceKey` in global coordinate space**

| Option | Mechanism | Why rejected / why chosen |
|--------|-----------|--------------------------|
| A | Fixed `.frame()` values + scale factor | Exact by construction but breaks for any dynamic or adaptive sizing; does not validate the actual rendered position |
| **B** | **`GeometryReader` + `PreferenceKey` in `.global` space** | **Confirmed accurate at 0 pt delta. Reports the true rendered position regardless of layout complexity. This is the mechanism already proven here.** |
| C | `XCUIElement.frame` × `UIScreen.main.scale` | Tests the accessibility frame, not the visual bounds. Does not reflect what the PNG pixels contain for UIKit-backed elements. |

**Generator implementation:** Wrap each element in a `.background(GeometryReader { proxy in Color.clear.preference(...) })`. Use `onPreferenceChange` to receive global frames as `CGRect`. Scale by `UIScreen.main.scale` for pixel coordinates.

**Key requirement:** Apply `.ignoresSafeArea(.all)` to the top-level `ZStack` so that `GeometryReader` reports coordinates relative to the physical screen origin. Without it, all y-values are shifted by the safe area inset.

---

## Known Risks — Outcomes

| Risk | Test | Outcome |
|------|------|---------|
| Safe area shifts origin | `testSafeAreaOriginShift` — compare `ignoresSafeArea` vs. without | **Confirmed: dy = 62 pt on iPhone 17 Pro (Dynamic Island + status bar), dy = 20 pt on iPhone SE (status bar only). Fix: apply `.ignoresSafeArea(.all)` to the ZStack, not just the background.** |
| `clipsToBounds` clips reported frame | `testClipToBoundsFrameReporting` — child 240×120 inside 120×60 container | **Confirmed: GeometryReader reports layout frame (240×120), not visible rect (120×60). Generator must intersect each element's frame with parent `.clipped()` container bounds.** |
| SwiftUI animation frame lag | `testAnimationFrameStability` — two layout passes 150ms apart | **Not observed: frames identical between passes at both @2x and @3x. A 150ms RunLoop wait is sufficient before capturing.** |
| `accessibilityFrame` vs `.frame` divergence | Not separately tested — XCUITest approach retired; generator uses GeometryReader, not accessibility frames | **Moot: generator does not use accessibility frames. UITextField's UIKit backing does not affect GeometryReader output.** |

---

## Acceptance Criteria

- [x] ≤2px alignment on all three elements at @3x (0 px delta — 2026-05-04)
- [x] ≤2px alignment on all three elements at @2x (0 px delta — 2026-05-04)
- [x] Frame export strategy decided and documented (Option B: GeometryReader global frame)
- [x] Scale factor conversion formula confirmed (`pointRect × UIScreen.main.scale = pixelRect`)
- [x] All known risks investigated with conclusions

**Phase 1 gate condition met.** Proceed to Phase 2 (taxonomy schema) and Phase 3 (dataset generation).
