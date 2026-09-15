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

### 4.1 App-Content Synthetic Track

This track uses generator templates under NativeUIAuditKit control. It should produce deterministic screenshots and sidecar annotations without device automation beyond launching the generator app.

Initial templates:

| Template | Required roles |
|---|---|
| Shelf/card grid | `collectionItem`, `label`, `imageView` |
| Top tab bar | `tabBar`, `label`, `primaryButton` |
| Settings list | `listRow`, `toggle`, `label`, `navigationBar` |
| Search and keyboard | `searchField`, `listRow`, `collectionItem`, `keyboardKey` |
| Alert/dialog | `alert`, `primaryButton`, `cancelAction` |

Each focusable template must render focused and unfocused variants. Focus is state metadata, not a separate element role.

### 4.2 AVKit Playback Track

AVKit chrome is a separate template family because playback state is part of the label semantics.

Initial roles:

- `playPauseButton`
- `scrubber`
- `skipForwardButton`
- `skipBackwardButton`
- `routePickerButton`
- `closedCaptionsButton`
- `transportControlsOverlay`
- `bufferingIndicator`
- `liveBadge`
- `adBreakOverlay`
- `adCountdownLabel`
- `chapterMarker`

Required states before AVKit support can be called complete:

- Playing, paused, buffering, and scrubbing-in-progress.
- Controls visible and controls hidden.
- Live playback vs. video-on-demand.
- Ad break with countdown visible and scrubber disabled or hidden.
- Hard negatives: subtitles, scoreboards, letterboxing, and in-content UI-like shapes.

### 4.3 System-Chrome Capture Track

System chrome is not generator-owned. Control Center, profile switching, Home Screen, Settings, setup/pairing, app switcher, screensaver, and accessibility overlays need capture automation through TVTestRig or manual capture protocols.

This track must keep OS provenance explicit because system chrome changes independently of app code.

Minimum metadata per capture:

- tvOS version and build.
- Device or simulator name.
- Resolution and scale.
- Capture source: TVTestRig automation, simulator screenshot, or manual real-device capture.
- Triggered state, such as Control Center open, profile switcher open, VoiceOver active, or screensaver idle.
- Artifact SHA-256.

## 5. TVTestRig Role

TVTestRig should be used for capture orchestration and real-device coverage, not as a runtime dependency of NativeUIAuditKit.

NativeUIAuditKit owns:

- Taxonomy and schema definitions.
- Coordinate transforms and annotation validation.
- Model training/evaluation scripts.
- Offline inference adapter: screenshot in, versioned JSON out.

TVTestRig owns:

- Driving Apple TV hardware or tvOS Simulator into app/system states.
- Capturing screenshots and any available metadata.
- Providing saved artifacts to the NativeUIAuditKit dataset ingestion path.
- Validating navigation behavior downstream after NativeUIAuditKit emits observations.

The first integration milestone is offline only: saved tvOS screenshot plus optional sidecar in, versioned JSON observations out. No device actions, automatic model download, or production dependency changes are required for milestone one.

## 5.1 Sequencing: Simulator First, Real Device Second

Split tvOS work into two explicit phases.

### Simulator phase

Use the tvOS Simulator for the first trainable model. This phase optimizes for speed, repeatability, and controlled labels.

Simulator phase scope:

- Coordinate validation at 1920x1080.
- App-content generator templates.
- Focused and unfocused synthetic variants for focusable elements.
- First hard-negative set for hidden controls, video-like backgrounds, and decorative highlights.
- First offline adapter contract: saved screenshot in, versioned JSON observations out.
- First model export and held-out simulator-template evaluation.

Simulator phase exclusions:

- No claim of complete tvOS OS-navigation coverage.
- No release qualification for VoiceOver, Switch Control, Zoom, Control Center, Home Screen, profile switching, app switcher, or screensaver classes.
- No production navigation-evidence claims based on simulator-only metrics.

### Real-device phase

Use real Apple TV capture through TVTestRig after the simulator model can already detect app-content roles. This phase is for OS-owned surfaces, accessibility visuals, and qualification.

Real-device phase scope:

- Home Screen, Control Center, profile switcher, App Switcher, Settings, pairing/setup, screensaver, system banners, and Siri/search overlays.
- VoiceOver caption bar and VoiceOver focus visuals.
- Switch Control focus indicator, Zoom magnification indicator, Reduce Motion, Increase Contrast, Button Shapes, and related accessibility visual variants.
- Remote-driven focus/parallax fidelity.
- Held-out qualification set that is never used for training unless explicitly reclassified into a later training split.

Real-device phase gate:

- No OS-chrome or accessibility class is marked supported until it has real-device or explicitly accepted simulator evidence, documented per class with capture source and tvOS version.

## 6. Focus Policy

Focus-related fields must represent uncertainty honestly.

- Visual focus, VoiceOver focus, and selected state are separate concepts.
- Do not populate VoiceOver focus from a visual focus halo.
- Pixel-only outputs may leave focus fields unknown when focus was not evaluated.
- Evaluate a focus estimator before adding custom detector heads.

Candidate approaches:

1. Auxiliary detector head for focus state.
2. Lightweight classifier on detected element crops.
3. Frame-diff or visual-change heuristic using adjacent TVTestRig captures.

The chosen approach must report precision/recall on held-out focus-transition footage before it becomes part of a release model.

## 7. Initial Qualification Gates

The first simulator-trained `NativeUIModel_tvOS` candidate needs:

- tvOS coordinate validation documented at 1920x1080 and, if available, 3840x2160.
- At least 3,000 app-content synthetic screenshots.
- Every role has at least 400 training instances or is explicitly deferred.
- `tabBar` AP at or above 0.80 on the withheld tvOS set.
- Overall mAP@0.5 at or above 0.80 on the withheld tvOS set.
- Separate hard-negative report for hidden playback controls and video-like backgrounds.
- CoreML export parity check against the training runtime on a fixed validation subset.

Real-device qualification then adds:

- At least 500 TVTestRig captured real/system screenshots held out from training.
- Separate hard-negative report for screensaver frames and system chrome.
- Per-accessibility-surface report for VoiceOver, Switch Control, and Zoom visuals.
- Explicit supported/deferred status per OS-navigation class.

## 8. Deferred Until After Milestone One

- Training on system-chrome captures.
- AVKit release qualification.
- Temporal tracking and `trackID`.
- Spatial-neighbor navigation claims.
- Unified multi-platform detector.
- Real-time TVTestRig navigation automation using model output.
