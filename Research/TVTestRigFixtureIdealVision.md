# TVTestRigFixture: Next-Generation On-Device Synthetic UI Generator & Training Rig

**Document Status:** Architectural Vision & Feature Specification  
**Target Platform:** tvOS 18+ / physical Apple TV 4K & tvOS Simulator  
**Audience:** NativeUIAuditKit Core Team, TVTestRig Maintainers, Computer Vision Engineers  
**Related Documents:** `Research/tvOSTrainingStrategy.md`, `Research/BestPractices.md`, `Research/NativeUIElementDetection.md`  
**Date:** 2026-09-17  

---

## 1. Executive Vision: The Paradigm Shift

Historically, training computer vision models for Apple platforms has relied on two compromised extremes:

1. **Offline Synthetic Generation (macOS Simulator / Mock Renders):**  
   Fast and scalable, but visually impoverished. Simulators run on macOS Intel/Apple Silicon software renderers that do not replicate real Apple TV Metal shaders, hardware parallax tilt, dynamic drop shadows, specular glare on focused cards, or true HDR/SDR display pipeline characteristics.
2. **Real-World Crawling (Live Apps & Settings):**  
   Visually authentic, but extremely fragile, dangerous (state mutation, display reset countdowns, account logins), and missing ground-truth bounding box labels (relying on imperfect OCR heuristics).

### The New Architecture: On-Device Programmable Synthetic Generation
With `TVTestRigFixture`, we can invert this paradigm. Because the fixture is a native app running directly on physical Apple TV hardware inside its own sandbox, we can transform it into a **programmable, on-device synthetic UI generation engine and ground-truth oracle**:

```
+---------------------------------------------------------------------------------------------------------+
|                                    MAC HOST ORCHESTRATOR (aatv / Python)                                |
|   - Training Loop Scheduler                                                                             |
|   - Parametric Scene Generator (Density, Taxonomy, ColorScheme, Seed)                                   |
|   - Model Retraining Pipeline (YOLO11 / CoreML)                                                         |
+---------------------------------------------------------------------------------------------------------+
                                 │ HTTP / WebSocket RPC
                                 ▼
+---------------------------------------------------------------------------------------------------------+
|                             PHYSICAL APPLE TV: TVTestRigFixture.app                                     |
|                                                                                                         |
|   ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐   |
|   │ 1. Declarative Scene Engine (SwiftUI / UIKit)                                                   │   |
|   │    Instantiates parametric UI layouts on the fly (Grids, Shelves, Sidebars, Forms, Media)       │   |
|   └─────────────────────────────────────────────────────────────────────────────────────────────────┘   |
|   ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐   |
|   │ 2. Automated Focus Sweep Controller (UIFocusSystem)                                             │   |
|   │    Cycles focus programmatically across every element on screen (Capturing Focus Variations)    │   |
|   └─────────────────────────────────────────────────────────────────────────────────────────────────┘   |
|   ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐   |
|   │ 3. Ground-Truth Telemetry Oracle (Window Coordinate Introspection)                              │   |
|   │    Extracts exact pixel rects, active focus, text strings, and traits with 100% accuracy        │   |
|   └─────────────────────────────────────────────────────────────────────────────────────────────────┘   |
|   ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐   |
|   │ 4. Deterministic Frame Capture & Event Handshake                                                │   |
|   │    Direct uncompressed frame grab + Schema v1.0 JSON sidecar broadcast (zero OCR guessing!)     │   |
|   └─────────────────────────────────────────────────────────────────────────────────────────────────┘   |
+---------------------------------------------------------------------------------------------------------+
```

This delivers the **holy grail of training data**: **100% authentic hardware rendering** (native Apple TV GPU shaders, parallax focus, specular highlights) combined with **100% mathematically exact ground-truth bounding boxes and state labels** generated directly from the UI window hierarchy.

---

## 2. Core Pillars of the Ideal Fixture Architecture

### Pillar A: Declarative Dynamic Scene Engine (On-the-Fly UI Synthesis)

Instead of relying on static, pre-compiled screens, the fixture should host a **Dynamic Scene Engine** capable of rendering arbitrary UI hierarchies described via declarative JSON recipes.

#### 1. Parametric Layout Archetypes
The engine should natively synthesize all major tvOS layout paradigms:
- **Top Shelf & Hero Carousel:** Expanding banner cards, badge overlays, call-to-action buttons.
- **Media Browsing Grids & Shelves:** Horizontal scrolling collection rows (poster art, 16:9 thumbnails, circular avatars, square albums) with focus zoom.
- **Split-View & Sidebar Navigation:** Left sidebar icon rails (collapsed and expanded) paired with right detail content cards.
- **Settings & Preference Tables:** Grouped table views with headers, footers, disclosure indicators (`>`), in-place value readouts, and toggle switches.
- **AVKit Media Player Chrome:** Full transport overlay with progress bar scrubbers, chapter cards, audio/subtitle popovers, and "Skip Intro" floating chips.
- **Modal Sheets, Alerts & Prompts:** Destructive confirmations, PIN entry pads, search keyboards, and multi-action dialogs.

#### 2. Seeded Combinatorial Variation
Every scene is driven by a random seed that controls:
- **Element Density:** Sparse (1–3 elements) vs Medium (4–12 elements) vs Extreme (15–40 elements).
- **Color Scheme & Contrast:** Light mode, Dark mode, High Contrast mode, Reduce Transparency.
- **Typography Scales:** Standard large, accessibility extra-large, bold text enabled.
- **Safe Area Insets:** Standard 90px horizontal / 60px vertical margin variations.
- **Content Realism:** Procedurally generated localized titles, ratings badges (`4K`, `HDR10`, `Dolby Atmos`), timecodes, and placeholder asset shapes.

---

### Pillar B: Ground-Truth Geometry & State Oracle

The single largest bottleneck in computer vision training is human labeling or noisy OCR heuristics. Inside `TVTestRigFixture`, the exact truth already exists in memory.

#### 1. Frame-Perfect Window Introspection
The fixture attaches an introspection coordinator to every rendered view:
```swift
// Direct Window Coordinate Extraction
let windowRect = view.convert(view.bounds, to: view.window)
let pixelRect = [
    windowRect.minX * scale,
    windowRect.minY * scale,
    windowRect.maxX * scale,
    windowRect.maxY * scale
]
```
This guarantees **zero coordinate drift**, zero IoU annotation error, and eliminates all discrepancies between normalized coordinates, points, and pixels.

#### 2. Native State Introspection
The fixture directly interrogates the operating system for every element:
- `isFocused`: `UIFocusSystem.active(for: window)?.focusedItem === view` (true ground truth on whether the element has system focus ring/glow).
- `elementText`: Raw string from `UILabel.text`, `UIButton.configuration?.title`, or `accessibilityLabel`.
- `elementType`: Authoritative 41-class taxonomy enum assigned directly by the generator template.
- `interactiveState`: Toggle value (`true`/`false`), slider percentage (`0.0`–`1.0`), segmented index (`0`–`N`), loading spinner state (`animating`).

#### 3. Instant Schema v1.0 Sidecar Emission
The fixture generates and pairs the exact `annotation.schema.json` sidecar synchronously with the screenshot:
```json
{
  "schemaVersion": "1.0",
  "imageSHA256": "4a18f9e...",
  "captureSource": "realAppleTVFixtureEngine",
  "image": {
    "pixelWidth": 1920,
    "pixelHeight": 1080,
    "scale": 1,
    "platform": "tvOS",
    "osVersion": "tvOS 18.x"
  },
  "elements": [
    {
      "id": "btn_play_01",
      "type": "primaryButton",
      "box": [450.0, 680.0, 750.0, 760.0],
      "text": "Play Episode 1",
      "state": {
        "isFocused": true,
        "isEnabled": true
      }
    }
  ]
}
```

---

### Pillar C: Automated Focus Sweep & Shader Training

On Apple TV, focused elements are not simply highlighted—they **scale up by 10%–15%, cast intense radial drop shadows, emit a bloom glow, and shift layer parallax on tilt**.

Standard models frequently hallucinate or miscalculate bounding boxes because they only see focused items or only see unfocused items.

#### The N-Way Focus Sweep Protocol
For any synthesized scene with $N$ interactive elements:
1. **Frame 0 (Unfocused Baseline):** Fixture moves focus to a non-interactive invisible anchor. Captures all $N$ elements in their resting, unfocused state.
2. **Frames $1 \dots N$ (Individual Focus Passes):**  
   The fixture programmatically moves focus to element $i$ using `UIFocusSystem.requestFocusUpdate(to: element)`:
   - Settle 150ms for Metal glow shaders and parallax spring animations to finish.
   - Capture frame and emit sidecar where element $i$ has `isFocused: true` and all others have `isFocused: false`.

**Impact:** A single synthesized scene of 10 controls immediately yields **11 perfectly calibrated training images** showing both the resting state and the exact focus glow distortion for every single control!

---

### Pillar D: Comprehensive 41-Class Component Kitchen Sink

The fixture must implement reference implementations of **all 41 classes** in the `NativeUIAuditKit` taxonomy, guaranteeing 100% class balance on hardware:

| Taxonomy Class Group | Specific tvOS Implementations in Fixture |
|---|---|
| **Buttons (5 classes)** | `primaryButton` (prominent pill), `secondaryButton` (tinted card), `destructiveButton` (red alert action), `borderlessButton` (flat icon), `cancelAction` (standard dismiss). |
| **Pickers & Inputs (8 classes)** | `segmentedControl` (pill selector), `picker` (wheel / vertical stack), `slider` (scrubber bar), `stepper` (numeric incrementor), `toggle` (switch), `textField`, `searchField`, `secureField` (PIN grid). |
| **Navigation & Chrome (6 classes)** | `tabBar` (top navigation rail), `sidebar` (split view navigation), `navigationBar`, `toolbar`, `pageControl` (dots), `segmentedControl`. |
| **Collections & Rows (5 classes)** | `collectionItem` (parallax poster art / card), `listRow` (settings row with chevron), `cardContainer`, `headerView`, `footerView`. |
| **Modals & Containers (5 classes)** | `sheet` (slide-up dialog), `alert` (tvOS modal prompt), `popover` (contextual bubble), `splitView`, `dockTile`. |
| **Indicators & Status (6 classes)** | `progressView` (determinate loading bar), `activityIndicator` (spinning gear), `badge` (`4K`, `CC`, `AD`), `ratingControl` (star bar), `toast` / HUD, `statusIndicator`. |
| **Content & Chrome (6 classes)** | `label` (title/body), `imageView`, `icon`, `divider`, `handle` (focus guide indicator), `placeholder` (skeleton card). |

---

### Pillar E: Defect & Accessibility Oracle (Seeded Audit Training)

Beyond object detection, NativeUIAuditKit's mission includes **UI and accessibility auditing (Phase 7)**. The fixture is the ideal vehicle to train and evaluate audit heuristics:

1. **Text Truncation & Clipping:**
   - Programmatically constrain label widths to trigger hard text clipping or premature ellipsis.
   - The sidecar marks `hasAuditDefect: true`, `defectType: "clippedText"`.
2. **Focus Traps & Unreachable Controls:**
   - Place elements in layout configurations that violate tvOS focus guide projection (e.g. diagonal gaps without `UIFocusGuide`).
   - Ground truth records `isFocusable: false`.
3. **Contrast Ratio Violations:**
   - Inject text colors that fail WCAG 2.1 AA contrast requirements (< 3:1 for large text, < 4.5:1 for body).
   - Ground truth records `contrastRatio: 2.1`, `auditDefect: "lowContrast"`.
4. **VoiceOver Label Omission:**
   - Programmatically strip `accessibilityLabel` or set misleading `accessibilityTraits`.
   - Ground truth marks element for accessibility lint failure.

---

## 3. Production Control Protocol: The Fixture RPC Interface

To operate this at scale (thousands of training frames per hour), the host machine (`aatv` / Python runner) requires a clean, zero-latency RPC interface to the fixture.

### 1. Transport Options
- **Primary: High-Speed Local HTTP / WebSocket Server:**
  - `TVTestRigFixture` hosts a lightweight, embedded Swift NIO / `NWListener` server on port `8080` (Bonjour advertised as `_tvtr-fixture._tcp`).
  - Completely bypasses the macOS App Sandbox limitations of `TVTestRig.app`!
- **Secondary: Shared Container Volume / Memory-Mapped Exchange:**
  - Used when running in tvOS Simulator environments.

### 2. The RPC Command Set

#### `POST /v1/scene/render`
Instructs the fixture to assemble and display a parametric scene.
```json
{
  "template": "SettingsTableView",
  "seed": 10482,
  "density": "high",
  "colorScheme": "dark",
  "insets": "standard",
  "components": [
    {"type": "listRow", "label": "Network", "hasChevron": true},
    {"type": "toggle", "label": "AirPlay", "state": "on"},
    {"type": "slider", "label": "Volume", "value": 0.75}
  ]
}
```
**Response:**
```json
{
  "status": "ready",
  "renderTimeMs": 14,
  "elementCount": 3,
  "sceneHash": "a82b9..."
}
```

#### `POST /v1/focus/set`
Moves focus to a specific element ID deterministically.
```json
{
  "elementId": "elem_toggle_02",
  "settleTimeMs": 150
}
```
**Response:** Confirms focus shift and returns updated `UIFocusSystem` bounding box.

#### `GET /v1/telemetry/ground-truth`
Returns the authoritative Schema v1.0 annotation sidecar for the currently visible screen:
- Exact pixel coordinates.
- Active focus state.
- Authoritative taxonomy labels.
- Text content and accessibility traits.

#### `POST /v1/batch/generate`
Orchestrates an autonomous on-device sweep:
- Generates $M$ scenes across specified template families.
- Automatically executes the $N$-way focus sweep on each.
- Streams compressed frames and sidecars directly to the host over HTTP chunked transfer.
- Throughput: **~5–10 frames per second** on physical Apple TV 4K!

---

## 4. Adversarial Focus Navigation & Diagnostic Stress-Testing (Hardening TVTestRig)

The fixture’s mission extends beyond generating passive training imagery for NativeUIAuditKit’s computer vision model. It serves as an **active training gymnasium and diagnostic proving ground for TVTestRig’s own automated navigation engine**.

Just as flight simulators subject autopilots to extreme turbulence, wind shear, and system failures, `TVTestRigFixture` can programmatically inject **pathological, broken, and hostile UI/UX patterns**. This allows TVTestRig to discover its own algorithmic blind spots, harden its pathfinding logic, and master navigation in a 100% safe, non-destructive sandbox before ever touching complex production apps or system settings.

```
+───────────────────────────────────────────────────────────────────────────────────+
|                  TVTESTRIG NAVIGATION DIAGNOSTIC GYMNASIUM                         |
+───────────────────────────────────────────────────────────────────────────────────+
|                                                                                   |
|   1. True Focus Traps         --> Tests automatic stall detection & escape macro  |
|   2. Diagonal Focus Gaps      --> Tests multi-step compound path planning         |
|   3. Asymmetric Graphs        --> Forces non-Euclidean directed graph memory      |
|   4. Dynamic Momentum Jitter  --> Calibrates velocity-aware settling heuristics   |
|   5. Redirection Loops        --> Tests cycle detection & backtracking recovery   |
|                                                                                   |
+───────────────────────────────────────────────────────────────────────────────────+
```

### Pathological Focus Archetypes Injected by the Fixture

#### 1. True Focus Traps (Dead Ends & Isolation)
- **The Defect:** A container, modal sheet, or sub-view where entering via a directional pulse is easy, but standard directional rays cannot escape back to the rest of the UI (e.g. nested views lacking focus restoration, or container views without escape focus guides).
- **How TVTestRig Learns:** 
  - TVTestRig must detect state stalls: *"I sent `navigate up` 3 times, but the focused bounding box has not changed. I am trapped."*
  - TVTestRig tests and refines **self-healing recovery maneuvers**: synthesizing a single `back` pulse, testing corner-exit escapes, or triggering an emergency return to root.
  - **Diagnostic Output:** TVTestRig automatically flags and generates a formal **Focus Trap Defect Report** with reproducing key sequences for third-party developers.

#### 2. Discontinuous & Diagonal Focus Gaps (Missing `UIFocusGuide`)
- **The Defect:** Buttons or interactive tiles arranged with diagonal offsets or separated by wide gaps lacking horizontal/vertical coordinate overlap. In native tvOS, standard 2D Euclidean raycasting fails to find a neighbor unless a developer manually bridges the gap with a `UIFocusGuide`.
- **How TVTestRig Learns:**
  - Standard linear counting (`navigate down 1`) completely halts.
  - TVTestRig develops **multi-step compound pathfinding**: recognizing that to reach an element at bottom-right, it must execute `right 1 -> down 1` through an intermediate element rather than attempting a direct diagonal ray.

#### 3. Asymmetric & Non-Reciprocal Navigation Paths
- **The Defect:** In complex carousels or split-screen layouts, moving `down` from Element $A$ lands on Element $B$, but moving `up` from Element $B$ lands on Element $C$ (or nowhere at all).
- **How TVTestRig Learns:**
  - Prevents the naive assumption of spatial symmetry (assuming that reversing the arrow key reverses the focus step).
  - TVTestRig builds an **internal directed state graph $G = (V, E)$**, recording actual transition edges $(u \xrightarrow{\text{dir}} v)$ rather than Euclidean approximations.

#### 4. Redirection Loops & Ping-Pong Traps
- **The Defect:** A container with an explicit `preferredFocusEnvironments` override that automatically bounces focus back to a default child whenever any edge is entered, creating an infinite oscillation when an automated crawler attempts to traverse out.
- **How TVTestRig Learns:**
  - TVTestRig implements **cycle detection algorithms** (Tarjan's or Floyd's cycle-finding) in its traversal stack.
  - When a focus cycle is detected, TVTestRig marks the edge as a loop, aborts re-entry, and backtracks along a proven safe ancestor edge.

#### 5. Dynamic Scrolling & Momentum Overshoot Traps
- **The Defect:** Long vertical lists or infinite horizontal shelves where cells are recycled dynamically and list momentum causes focus to jump past the intended target or stick to a header.
- **How TVTestRig Learns:**
  - Stress-tests TVTestRig’s closed-loop `wait-stable` and visual diffing thresholds against fast-moving content.
  - Calibrates single-step pulse timing to prevent momentum overrun.

#### 6. Intermittent Responders & Async UI Latency
- **The Defect:** Buttons that temporarily disable themselves (`isEnabled = false`) during simulated network fetches, or views that delay becoming focusable (`canBecomeFocused = false`) for 300–800ms after rendering.
- **How TVTestRig Learns:**
  - Hardens TVTestRig against timing out or misidentifying disabled elements as static labels.
  - Teaches the test runner when to wait for async state transitions versus when to classify an element as permanently non-interactive.

---

### Transformational Value for TVTestRig as a Product

By using `TVTestRigFixture` as an adversarial diagnostic testbed:
1. **Self-Validating Automation Engine:** We can run automated regression test suites *on TVTestRig itself*, proving that TVTestRig’s navigation engine can successfully explore and escape 100 randomly generated pathological focus mazes with 0% failure rate.
2. **First-in-Class Focus Accessibility Linter:** TVTestRig evolves from a simple remote-control runner into an **authoritative Focus Accessibility Auditor**. When running against customer apps, TVTestRig can automatically detect, visualize, and report broken focus guides, trapped containers, and unreachable elements.
3. **Bulletproof Real-World Crawling:** Once TVTestRig’s navigation engine can master the fixture’s most extreme adversarial focus traps, navigating real-world commercial apps (Netflix, YouTube, Peacock, Hulu) and native OS Settings becomes trivial, robust, and completely fail-safe.

---

## 5. Best Practices Applied from Previous Hard Lessons

| Past Pain Point / Bug | How the Fixture Architecture Solves It |
|---|---|
| **BP-25 / Coordinate ScaleFit Bug** | The fixture generates screenshots strictly at native display resolution (1920x1080 @ 1x or 3840x2160 @ 2x) and reports pixel coordinates directly. No aspect-ratio distortion. |
| **BP-01 / BP-02 SwiftUI Offset & Safe Area** | Layout templates use pure SwiftUI layout containers (`VStack`, `HStack`, `Grid`) with explicit `.safeAreaPadding()` rather than `.offset()` hacks, ensuring GeometryReader captures match visual bounds. |
| **BP-04 / Focus Glow Animation Settle** | The RPC server enforces an explicit post-render settling interval (150ms) before signaling frame readiness, eliminating blurred or mid-transition captures. |
| **BP-10 Vision Y-Flip & Inversion** | Telemetry exports window-native coordinates `[x_min, y_min, x_max, y_max]` with top-left origin (standard Cocoa/CoreGraphics), with helper functions for YOLO `[cx, cy, w, h]` and Vision normalized representations. |
| **TVTestRig Sandbox `persistenceFailed`** | Streaming frame buffers directly over the local network via HTTP/WebSocket completely eliminates macOS sandbox container file permissions. |
| **Open-Loop Traversal Disasters (Peacock/Reset)** | Synthetic generation is 100% programmatic and self-contained inside the fixture. Zero interaction with Springboard or system Settings. |

---

## 6. Phased Implementation Roadmap

```
+───────────────────────────────────────────────────────────────────────────────────+
|                           FIXTURE EMPOWERMENT ROADMAP                             |
+───────────────────────────────────────────────────────────────────────────────────+
| Phase 1: Local HTTP Telemetry & Frame Pipeline                                     |
|          - Embedded Swift NIO server on port 8080                                 |
|          - Direct window coordinate introspection & Schema v1.0 JSON emission     |
+───────────────────────────────────────────────────────────────────────────────────+
| Phase 2: 41-Class Component Kitchen Sink View                                     |
|          - Modular SwiftUI views covering all 41 taxonomy classes                 |
|          - Systematic focus shift controller (UIFocusSystem.requestFocusUpdate)   |
+───────────────────────────────────────────────────────────────────────────────────+
| Phase 3: Declarative Dynamic Scene Engine & Adversarial Focus Mazes               |
|          - JSON-driven layout synthesis (POST /v1/scene/render)                   |
|          - Seeded focus traps, broken focus guides, and non-reciprocal graphs     |
+───────────────────────────────────────────────────────────────────────────────────+
| Phase 4: High-Throughput Autonomous Harvester & Navigation Benchmarking           |
|          - Continuous batch generation loop (5–10 frames/sec)                     |
|          - Automated TVTestRig navigation stress-testing suite                    |
+───────────────────────────────────────────────────────────────────────────────────+
```

---

## 7. Conclusion & Expected Impact

By turning `TVTestRigFixture` into an on-device synthetic generation engine and adversarial navigation proving ground:
1. **Model Quality:** The tvOS detector trains on authentic Metal shaders, real parallax focus dynamics, and hardware drop shadows.
2. **Speed & Scale:** We eliminate slow manual or UI-driven navigation entirely. We can generate **10,000+ perfectly labeled tvOS training frames per hour**.
3. **Audit Readiness:** Ground-truth defect injection provides the exact testbed needed to train and validate NativeUIAuditKit's Phase 7 accessibility audit engine.
4. **Hardened TVTestRig Navigation:** TVTestRig’s navigation engine learns to detect focus stalls, solve broken focus guides, break out of focus traps, and report focus accessibility defects directly.
5. **Zero Production Risk:** Runs inside a safe app sandbox on dedicated test hardware, with zero possibility of touching system accounts, resetting video modes, or drifting into foreign apps.
