# NativeUIAuditKit: tvOS Training Strategy

**Status:** Draft / pre-implementation
**As of:** 2026-09-15
**Audience:** NativeUIAuditKit maintainers and TVTestRig integrators
**Depends on:** `Research/NativeUIElementDetection.md`, `Tasks.md`

---

## 1. Decision

Train tvOS as a separate model track first: `NativeUIModel_tvOS`.

Do not fold tvOS screenshots into the iOS/iPadOS detector until a later unification experiment proves that a combined model preserves per-platform precision, recall, coordinate error, and focus-state behavior.

The current working assumption is:

| Model | Platform scope | Primary data source |
|---|---|---|
| `NativeUIModel_iOS` | iOS, iPadOS | NativeUIAuditKit synthetic SwiftUI/UIKit generator |
| `NativeUIModel_tvOS` | tvOS app content + selected system chrome | tvOS generator plus TVTestRig capture |
| `NativeUIModel_macOS` | macOS | Future AppKit generator |

## 2. Why tvOS Starts Separate

tvOS has a different visual and interaction grammar from iOS:

- 16:9 landscape screenshots, commonly 1920x1080 or 3840x2160.
- Top-of-screen navigation and tab chrome rather than bottom tab bars.
- Focus-driven interaction: focused elements scale, shadow, glow, or parallax instead of receiving touch highlights.
- AVKit playback chrome differs from iOS: transport overlays, top info panels, live/ad states, and hidden-controls states need separate coverage.
- System chrome such as Control Center, profile switching, Home Screen, Settings, app switcher, and VoiceOver overlays cannot be rendered by ordinary app templates.

A shared detector can be evaluated later, but it should not be the first artifact. The first tvOS model should optimize for tvOS failure modes without inheriting iOS layout priors such as "tab bar is near the bottom."

## 3. Can We Combine Models Later?

Yes. There are three viable combination paths:

1. **Runtime routing:** Keep separate models and select by sidecar platform, falling back to pixel-only platform heuristics for orphan screenshots.
2. **Ensemble routing:** Run a small platform classifier first, then invoke the platform-specific detector. This keeps detector weights independent while sharing the public API.
3. **Unified detector:** Train one detector across iOS/iPadOS/tvOS/macOS with platform-balanced batches and platform-tagged evaluation.

The unified detector is only acceptable if it passes all of these gates:

- No platform loses more than 2 percentage points mAP@0.5 compared with its dedicated model.
- tvOS `tabBar` AP remains at or above 0.80 and does not regress into toolbar confusion.
- tvOS focus-state precision/recall remains within 2 percentage points of the dedicated model or focus estimator.
- iOS false positives do not increase on bottom chrome, status bar, home indicator, or Dynamic Island classes.
- Latency and model size stay within the published deployment budget.

Until those gates are met, separate models are the safer production shape.

## 4. Dataset Tracks

### 4.1 OS UI Detection Track (Priority 1 — TVTestRig Navigation)

This track is the immediate operational priority for TVTestRig navigation and automation. It models the core Apple TV system navigation surfaces needed to identify target fixture apps, locate active focus, and automate menus:

| OS Surface | Required Roles | Focus Behavior |
|---|---|---|
| **Home Screen** | `collectionItem` (app icon / poster tile), `label` (title), `collectionItem`/`imageView` (Top Shelf) | Focused icon expands ~15% in scale, casts drop shadow, radiant white highlight border |
| **Settings** | `listRow` (item / menu entry), `toggle` (switch), `label` (value/desc), `navigationBar` (header) | Focused row turns into solid white rounded pill with dark text |
| **System Alerts & Dialogs** | `alert` (container), `primaryButton` (action/OK), `cancelAction` (cancel), `destructiveButton` | Focused button is solid white pill with glow |
| **Top Tab Bar** | `tabBar` (top-pinned container), `primaryButton`/`collectionItem` (tabs) | Focused tab has highlight pill / vibrant indicator |

Each focusable template must render focused and unfocused variants. Focus is state metadata (`state.isFocused: Bool?`), not a separate element role.

### 4.2 App-Content Synthetic Track (Priority 2)

General third-party app templates:
- Multi-row content shelves (`collectionItem`, `label`, `imageView`)
- Search grid and on-screen keyboard (`searchField`, `listRow`, `collectionItem`)
- Detail modal cards (`sheet`, `label`, `primaryButton`)

### 4.3 AVKit Playback Track (Priority 3)

AVKit chrome for media players:
- `playPauseButton`, `scrubber`, `skipForwardButton`, `skipBackwardButton`, `transportControlsOverlay`, `bufferingIndicator`, `liveBadge`, `adBreakOverlay`.

### 4.4 TVTestRig Capture & Qualification Track

Real device and simulator captures taken by TVTestRig:
- Physical Apple TV captures from `office` or tvOS Simulator.
- Provides real-world domain ground truth for Home Screen icon layouts, Settings, and alert dialogs.
- Ingestion pipeline (`scripts/ingest_tvos_capture.py`) validates image dimensions and packages metadata.

## 5. TVTestRig Role & Integration Contract

TVTestRig is used for capture orchestration, remote automation, and verification. It is not a compile-time or runtime binary dependency of NativeUIAuditKit.

NativeUIAuditKit owns:
- Taxonomy, schema, and coordinate transformations.
- Synthetic OS UI generator templates.
- Model training (`NativeUIModel_tvOS`) and evaluation scripts.
- Offline inference CLI / adapter (`scripts/tvos_detect.swift`): screenshot PNG in $\rightarrow$ structured JSON observations out.

TVTestRig owns:
- Driving physical Apple TV hardware or tvOS Simulator via `aatv` or `tvtestrig-mcp`.
- Capturing screenshots and calling `tvos_detect`.
- Parsing `NativeUIObservations`:
  1. Identifying target elements by `visibleText` (OCR) and `elementType`.
  2. Finding the current focus location (`state.isFocused == true`).
  3. Calculating remote d-pad step count (Up, Down, Left, Right, Select).
  4. Authoritatively verifying that focus reached the target.

### 5.1 Phasing: OS UI Detection First

1. **Phase 6b-S-1 (tvOS Coordinate & Focus Spike):** Validate coordinate reporting at 1920×1080 and `@FocusState` visual vs. layout frame behavior.
2. **Phase 6b-S-2 (OS UI Synthetic Generator):** Generate synthetic Home Screen, Settings, Alert, and Top Tab Bar images with ground-truth focus labels.
3. **Phase 6b-T (TVTestRig Ingestion & Offline Adapter):** Build `scripts/tvos_detect.swift` and `scripts/ingest_tvos_capture.py`.
4. **Phase 6b-S-3 (Train `NativeUIModel_tvOS_v0`):** Train YOLO11 on the OS UI dataset and export CoreML model.
5. **Phase 6b-R (Real Hardware Qualification):** Qualify on physical Apple TV screenshots from TVTestRig.

## 6. Focus Policy

Focus-related fields must represent uncertainty honestly.

- Visual focus, VoiceOver focus, and selected state are separate concepts.
- Do not populate VoiceOver focus from a visual focus halo.
- In tvOS, visual focus is mutually exclusive: at most one element holds visual focus at any moment.
- The detector pipeline combines:
  1. Trained model detections with `state.isFocused` annotations.
  2. Visual focus feature verification (measuring luminance inversion for Settings/Alert pills and scale/halo for Home Screen app icons) to guarantee 100% authoritative focus reporting for TVTestRig navigation.

## 7. Initial Qualification Gates

The first OS-UI-focused `NativeUIModel_tvOS` candidate needs:

- tvOS coordinate validation documented at 1920×1080.
- At least 2,000 OS UI screenshots (Home Screen, Settings, Alerts, Tab Bar).
- Focus precision/recall $\ge 0.90$ on held-out OS UI test sets.
- `collectionItem` and `listRow` AP@0.5 $\ge 0.85$.
- `tabBar` AP@0.5 $\ge 0.80$ (pinned at screen top).
- TVTestRig offline detection CLI (`scripts/tvos_detect.swift`) verified on sample screenshots.

## 8. Deferred Until After Milestone One

- AVKit playback controls release qualification.
- General complex third-party app templates (KitchenSink, ecommerce, etc.).
- Multi-platform unified detector (Phase 6b-U).
