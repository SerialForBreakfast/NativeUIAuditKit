# NativeUIAuditKit: tvOS Training Strategy

**Status:** v3.0 shipped (`nativeui-tvos-v3.0`, mAP@0.5 = 0.9822). FocusRingDetector v0.1 shipped. Remaining: TASK-6b-R-1 scale, FOCUS-DET-05, Phase 6b-U.  
**As of:** 2026-09-18  
**Audience:** NativeUIAuditKit maintainers and TVTestRig integrators  
**Depends on:** [`NativeUIElementDetection.md`](NativeUIElementDetection.md), [`CurrentState.md`](CurrentState.md), [`../Tasks.md`](../Tasks.md)

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

### 4.1 Prototype OS UI Track (Phase 6b-S — Milestone One Baseline)

Milestone One delivered an initial baseline (`NativeUIModel_tvOS_sim_v0` / `nativeui-tvos-v1.0`, Run 010):
- **Scope**: Basic Home Screen app tiles, simple Settings list rows, modal alerts, and top tab bar.
- **Limitation**: Trained on only 200 synthetic images across 10 active classes (`alert`, `cancelAction`, `collectionItem`, `imageView`, `label`, `listRow`, `navigationBar`, `primaryButton`, `tabBar`, `toggle`). 31 of 41 taxonomy classes had zero instances.

---

### 4.2 Exhaustive tvOS UI Track (Phase 6b-E — Production Coverage)

To achieve unconstrained Apple TV automation and comprehensive QA qualification in TVTestRig, the training scope expands to all native tvOS UI surfaces:

| Surface Module | Key UI Components | Taxonomy Mappings | Visual Focus Characteristic |
|---|---|---|---|
| **E1: All Menus & Contextual Overlays** | Context pop-up menus, Top Shelf hero banners, slide-out navigation sidebars, category filter chips | `contextMenu`, `sidebar`, `segmentedControl`, `picker`, `primaryButton`, `secondaryButton`, `destructiveButton` | Focused action pill turns bright white with drop shadow; sidebar icons highlight with white background tile. |
| **E2: Control Center & System Panels** | Top-right slide-in panel, user profile switcher, AirPods audio routing, Spatial Audio, HomeKit cameras/scenes, sleep timer | `sheet`, `popover`, `collectionItem`, `slider`, `toggle`, `listRow`, `primaryButton` | Focused tile expands with radiant perimeter; volume slider thumb glows white; profile avatar displays focus ring. |
| **E3: Advanced Settings Navigation** | Multi-column navigation split view, deep submenus (Accounts, Video/Audio, Remotes, Network), calibration test pattern cards, legal agreements | `sidebar`, `listRow`, `toggle`, `progressView`, `sheet`, `imageView` | Left sidebar retains selected indicator; right detail rows invert to white focus pill; calibration cards highlight active action button. |
| **E4: AVKit & Media Playback** | Transport timeline scrubber, elapsed/remaining time, play/pause/skip, audio/subtitle modal picker, chapter markers, PiP window, info metadata sheet, "Skip Intro" overlay, live stream badges | `slider`, `progressView`, `primaryButton`, `secondaryButton`, `sheet`, `collectionItem`, `label`, `segmentedControl` | Scrubber thumb enlarges and shows preview thumbnail bubble; action buttons turn solid white with glow; playback speed chips highlight. |
| **E5: SharePlay & Collaboration** | Group FaceTime call status pill, SharePlay prompt dialogs, synchronized playback HUD, floating participant video grid | `collectionItem`, `alert`, `label`, `imageView`, `primaryButton`, `cancelAction` | Call pill glows green/purple at top-right; modal prompt buttons follow standard focus pill glow. |
| **E6: OS-Specific Chrome & Interaction** | Dynamic Siri listening orb & dictation bubble, linear single-row keyboard, grid keyboard, dictation button, AirPlay PIN overlay, proximity auth cards, Game Center HUD, aerial screensaver badge | `primaryButton`, `searchField`, `alert`, `sheet`, `label`, `imageView` | Focused keyboard key inverts to bright white square with dark letter; proximity prompt displays action button focus. |

---

## 5. TVTestRig Role & Integration Contract

TVTestRig is used for capture orchestration, remote automation, and verification. It is not a compile-time or runtime binary dependency of NativeUIAuditKit.

NativeUIAuditKit owns:
- Taxonomy, schema, and coordinate transformations.
- Synthetic OS UI generator templates (`Templates/tvOS/`).
- Model training (`NativeUIModel_tvOS_v2.0`) and evaluation scripts.
- Offline inference CLI / adapter (`scripts/tvos_detect.swift`) and session API (`NativeUIDetectionSession`).

TVTestRig owns:
- Driving physical Apple TV hardware or tvOS Simulator via `aatv` or `tvtestrig-mcp`.
- Capturing screenshots and calling `NativeUIDetectionSession` / `tvos_detect`.
- Automated remote navigation verification (d-pad steps, target acquisition, focus confirmation).

---

## 6. Phasing Roadmap

1. **Phase 6b-S (Milestone One Prototype):** Coordinate spike, initial 10-class OS UI generator, and Run 010 baseline. ✅
2. **Phase 6b-WP1 (Trustworthy Result Contract):** Modality health, calibrated focus confidence & abstention, verified model manifest, actor-backed detection session, and licensing documentation. ✅
3. **Phase 6b-E (Exhaustive tvOS UI Coverage & Retraining):**
   - E1: All Menus & Contextual Overlays (ContextMenu, TopShelfHero, SidebarMenu) ✅
   - E2: Control Center & System Panels (ControlCenter drawer, User Switcher, Audio, HomeKit) ✅
   - E3: Advanced Settings Navigation & Submenus (SplitSettings, Stepper, SegmentedControl) ✅
   - E4: AVKit & Media Playback Overlays (AVKitPlayback scrubber, Audio & Subtitles panel) ✅
   - E5: SharePlay & Collaborative Experiences (FaceTime banner, speaking halos, group controls) ✅
   - E6: OS-Specific Chrome & Keyboards (Linear/grid keyboard, Siri voice dictation card) ✅
   - E7: Synthetic dataset generator updated (15 families, 3,000 images generated, 39,520 instances across 21 classes), YOLO export validated, and dry-run training verified on Apple Silicon MPS. 🟡
4. **Phase 6b-R (Real Hardware Qualification):** Qualify on physical Apple TV captures from TVTestRig across all surfaces.
5. **Phase 6b-U (Multi-Platform Unified Detector):** Evaluate unified model once tvOS real-device qualification passes.
