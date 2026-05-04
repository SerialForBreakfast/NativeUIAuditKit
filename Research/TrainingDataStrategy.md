# NativeUIAuditKit: Training Data Strategy

**Status:** Approved — active reference  
**Decided:** 2026-05-04  
**Audience:** NativeUIAuditKit maintainers; anyone building or expanding the dataset  
**Supersedes:** Sections 6, 7, 8, and 14 of `NativeUIElementDetection.md` for dataset-specific decisions. That document remains authoritative for architecture and API design; this document is authoritative for dataset composition, bias prevention, and training methodology.

---

## Summary of Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Taxonomy size | ~41 classes | Original 27 was missing common native elements (see Section 1) |
| Model architecture | 3 separate models (iOS/iPadOS, tvOS, macOS) | Platforms have distinct visual languages and interaction paradigms; unified model compromises accuracy on all three (see Section 2) |
| Real-world validation | 200 personal-device App Store screenshots | Bias detection only — never in training; clean legal provenance (see Section 3.6) |
| Training data source | Synthetic only (generator-direct annotation) | Eliminates coordinate drift, label inconsistency, and missing metadata that plague manual annotation |
| Train/validation/test split | By template family, not random | Prevents template memorization; tests genuine generalization (see Section 9.2) |

---

## 1. Taxonomy — ~41 Classes

### 1.1 Design principle

Use stable semantic role strings, not private UIKit/AppKit class names. `primaryButton` survives iOS redesigns; `UIButton.ButtonType.system` does not. Every `NativeUIElementType.rawValue` is stable public API from the moment schema v1.0 is tagged. Adding a class after tagging is a minor version bump; renaming is a major version bump.

### 1.2 Full class list

**Chrome (7):** `statusBar`, `navigationBar`, `tabBar`, `toolbar`, `sidebar`, `homeIndicator`, `dynamicIsland`

**Controls (14):** `primaryButton`, `secondaryButton`, `destructiveButton`, `cancelAction`, `textField`, `secureField`, `toggle`, `slider`, `segmentedControl`, `picker`, `stepperControl`, `searchField`, `menuButton`, `colorWell`

**Content (4):** `label`, `imageView`, `link`, `mapView`

**Indicators (5):** `activityIndicator`, `progressView`, `pageControl`, `scrollIndicator`, `refreshControl`

**Containers (9):** `alert`, `actionSheet`, `sheet`, `popover`, `listRow`, `collectionItem`, `disclosureGroup`, `tooltip`, `contextMenu`

**Special (2):** `webContent`, `unknown`

**Total: 41 classes**

### 1.3 Classes deferred to a future expansion (60+ class target)

The following are NOT in v1 and should not be added until schema v2.0:

- macOS window chrome: `titleBar`, `menuBar`, `dock` — macOS model uses `navigationBar` for in-app navigation; window chrome detection serves a different audit use case
- visionOS: `ornament` — deferred until a reliable visionOS screenshot capture workflow exists
- tvOS: `shelfItem` — `collectionItem` covers shelf cards for now; add if shelf-specific metrics are needed

### 1.4 Platform-exclusive classes

| Class | Platforms |
|---|---|
| `homeIndicator` | iOS, iPadOS (iPhone models with Face ID) |
| `dynamicIsland` | iOS (iPhone 14 Pro and later) |
| `tooltip` | iPadOS (pointer-hover), macOS |
| `scrollIndicator` | macOS (always visible by default) |

These classes are present in the model for the platform where they are common; the iOS model includes `homeIndicator` and `dynamicIsland`; the macOS model emphasizes `tooltip` and `scrollIndicator`.

---

## 2. Three-Model Architecture

### 2.1 Model assignments

| Model | Platforms covered | Training dataset origin |
|---|---|---|
| `NativeUIModel_iOS` | iOS, iPadOS | SwiftUI + UIKit generator (Phases 3–5b) |
| `NativeUIModel_tvOS` | tvOS | tvOS generator (Phase 6b) |
| `NativeUIModel_macOS` | macOS | AppKit generator (Phase 6c) |

### 2.2 Rationale for separation

**tvOS:** The tab bar sits at the top of the screen (iOS: bottom). Every interactive element has focused/unfocused states with parallax effects. There is no homeIndicator, no Dynamic Island, no notch. A unified model trained on iOS data would learn "tab bar = bottom element" — a rule that actively mis-classifies tvOS.

**macOS:** AppKit uses a bottom-left Y-axis origin (flipped from iOS). macOS screenshots include window chrome (title bar, traffic lights) with no iOS equivalent. NSToolbar occupies a horizontal band below the title bar with no iOS analog. The pointer paradigm introduces hover states (tooltips, hover highlights) that do not exist on touch screens.

**iOS + iPadOS (combined):** These share almost all visual language. iPad size-class switching (compact = tab bar, regular = sidebar) is modeled within the iOS training data as an explicit variation axis, not as a separate model.

### 2.3 Model selection at inference time

**With sidecar:** Use `sidecar.platform` field. This is always deterministic — the platform is known at capture time.

**Pixel-only (no sidecar):** Apply a heuristic classifier using:
1. Aspect ratio: tvOS screenshots are ~16:9 landscape; iOS is portrait; macOS is landscape (wider)
2. Tab bar position: if a tab bar is detected in the bottom 15% of the image → iOS; in the top 15% → tvOS
3. Menu bar: solid top bar spanning full width with clock and menu items at top-left → macOS
4. Status bar height heuristic: tall status bar with clock/signal icons → iOS/iPadOS

---

## 3. Dataset Composition

### 3.1 Per-class instance minimums (per model, training split)

| Tier | Classes | Min training instances |
|---|---|---|
| High (chrome) | `statusBar`, `navigationBar`, `tabBar` | 2,000 (this is a ceiling, not a floor — cap at 2,000 to prevent loss domination) |
| High (controls) | `primaryButton`, `textField`, `toggle`, `listRow`, `label` | 1,500 |
| Medium | `alert`, `sheet`, `slider`, `segmentedControl`, `searchField`, `picker`, `activityIndicator`, `progressView`, `imageView`, `pageControl` | 800 |
| Low | `menuButton`, `contextMenu`, `disclosureGroup`, `link`, `refreshControl`, `scrollIndicator` | 500 |
| Rare | `stepperControl`, `homeIndicator`, `dynamicIsland`, `actionSheet`, `popover`, `collectionItem`, `sidebar`, `secureField`, `webContent`, `colorWell`, `tooltip`, `mapView` | 400 (active oversampling required) |
| Absorber | `unknown` | 300 |

**Imbalance ceiling rule:** No class may have more than 5× the instance count of the rarest class in the same training split. Subsample over-represented classes (prefer removing same-template images first, then random sample) if exceeded.

### 3.2 Primary stratification axes

These must be balanced across all generated images, not left to chance:

| Axis | Target distribution |
|---|---|
| Platform | iOS 60%, iPadOS 20%, macOS 10%, tvOS 10% |
| Color scheme | 50% light / 50% dark — strict 1:1 |
| Dynamic Type | xSmall 10%, Small 10%, Medium 20%, Large 15%, XLarge 15%, XXLarge 15%, AccessibilityMedium 10%, AccessibilityExtraLarge 5% |
| Framework | SwiftUI 50%, UIKit 40%, AppKit 5%, tvOS-UIKit 5% |
| Layout direction | LTR 85%, RTL 15% |

### 3.3 Secondary axes (sweep within primary strata)

- iOS devices: iPhone SE 10%, standard iPhone 50%, iPhone Pro Max 40%
- iPadOS: iPad Air 40%, iPad Pro 11" 30%, iPad Pro 13" 30% (iPad Pro 13" withheld from training; test set only)
- OS visual profile: iOS 17 30%, iOS 18 40%, iOS 26 30%
- Orientation: iPhone 80/20 portrait/landscape, iPad 50/50

### 3.4 Rare class boost

Build "feature-focused" templates that guarantee the rare class appears in every image. Flag in manifest as `focusedClass: "stepperControl"`. After training, verify the model also detects them in non-focused templates (AP on non-focused test images must be ≥ 80% of focused-template AP).

### 3.5 Template diversity requirements

- Minimum 50 structurally distinct templates for production. "Distinct" means a different element arrangement — two templates that share the same navigation + list structure but differ only in content text are not distinct.
- Screen archetypes: forms, lists, modals, navigation-heavy, content-heavy, empty states, error states, tool-heavy. No archetype may contribute >25% of total images.
- Post-training check: if any single template contributes >15% of per-class validation AP (measured by ablation), it is over-represented.

---

## 4. Systematic Contextual Bias — The Full Audit

The most insidious risk in synthetic datasets is **temporal and environmental correlation**: all images generated in the same session inherit the same simulator state, making those environmental features spuriously predictive of UI elements. If all macOS screenshots are generated on the same day, the menu bar clock shows the same time in every image. The model learns "12:09 Tuesday" → `statusBar` rather than "the horizontal bar with icons at the top of the screen."

There are 16 confirmed sources of this bias, each with a required fix:

### 4.1 Leakage audit table

| Source | Leakage mechanism | Required fix |
|---|---|---|
| **Status bar / menu bar clock** | All images in a session show the same time. | Override via `xcrun simctl status_bar <device> override --time "HH:MM"`. Sweep every hour × 7 days of week × 12 months. |
| **Status bar date (macOS)** | macOS menu bar shows day + date. | Override macOS system date per generation run. Sweep 12 months × 4 weeks. |
| **Battery level** | Simulator shows 100% unless overridden. | Override `--batteryLevel 10/25/50/75/100 --batteryState charging`. Sweep all values. |
| **Cellular/Wi-Fi signal** | Simulator shows full signal unless overridden. | Override `--cellularBars 0/1/3/5`, `--wifiBars 0/1/3`, `--cellularMode notSupported`. |
| **Carrier name** | Simulator shows "Carrier". | Override: empty, "AT&T", "Vodafone", "SoftBank". |
| **Do Not Disturb / Focus icons** | Icon always present or always absent in a session. | Vary: DND on, DND off, Focus mode, alarm active. |
| **Wallpaper behind translucent chrome** | Same wallpaper → model learns "that blurred color = nav bar." | 6 wallpaper archetypes (see Section 4.2). Sweep all translucent chrome templates across all 6. |
| **Date content in date pickers** | All pickers show today's date. | Use `withDate:` API — never `Date()`. Sweep 12 months × 3 years. |
| **Numeric badges** | Badge count same across batch. | Sweep: 1, 5, 9, 12, 99, 100+, no-badge, red dot. |
| **macOS cursor position** | Same coordinates in every screenshot. | `NSCursor.hide()` before capture, or `CGWarpMouseCursorPosition` to randomize. |
| **List/row text content** | Same names repeat. Model may learn "John Smith" → `listRow`. | Seeded content corpus: 500+ names, 200+ places, varied dates/prices. No string in >5% of any class's instances. |
| **iCloud/sync spinner** | Always spinning or always idle. | Vary: upload-in-progress, sync-complete, sync-idle states. |
| **Screen recording indicator** | Orange dot always absent. | Include in 5% of status bar templates. |
| **Locale-specific numerals** | Arabic Eastern numerals ٠١٢٣ could become class features. | Generate Arabic templates; model must learn shape, not numeral encoding. |
| **Subpixel element positions** | Generator always snaps to pixel grid. | Apply ±0.5pt canvas jitter (post-processing) on 10% of images. Do NOT jitter annotation boxes. |
| **Screenshot capture API** | Single API has consistent rendering artifacts. | Vary: `UIGraphicsImageRenderer`, `XCUIScreen.main.screenshot`, `CGDisplayCreateImage` (macOS). |

### 4.2 Wallpaper archetypes for translucent chrome

Pre-generate 6 abstract pattern assets (synthesized — no real photographs):
1. Solid dark
2. Solid light
3. Dark gradient (diagonal, blue-to-purple)
4. Light gradient (diagonal, cream-to-peach)
5. Abstract texture (fine grain, dark)
6. Photography-style abstract (soft bokeh shapes, light)

Render these as the window background layer in the generator app (not via simulator wallpaper — that is not reproducible). Every template that includes a translucent `navigationBar`, `tabBar`, `toolbar`, or `sheet` is run once per wallpaper archetype → 6 image variants per template run.

### 4.3 Simulator state override protocol

Before every generation batch of ≥100 images, run a state sweep. Record active overrides in each image's `generatorProfile.simulatorState` annotation field.

```
for each batch:
  time     ← random [00:00–23:45, 15-min intervals]
  battery  ← random [10, 25, 50, 75, 100, "charging"]
  signal   ← random [0, 1, 3, 5 bars]
  date     ← random [−18 to +6 months from current date]
  carrier  ← random ["", "AT&T", "Vodafone", "SoftBank"]

  xcrun simctl status_bar <device> override \
    --time {time} --batteryLevel {battery} \
    --cellularBars {signal} --wifiBars {signal} \
    --operatorName {carrier}

  [run generation batch]

  xcrun simctl status_bar <device> clear
```

**Temporal spread:** Minimum 4 separate generation runs across different calendar days. Record `generationDate` in manifest per batch.

### 4.4 Content corpus requirements

The text content used in `label`, `listRow`, `textField`, `searchField`, `menuButton`, and `link` elements must be drawn from a structured seeded corpus:

- 500+ unique person names (varied given/family name lengths and origins)
- 200+ place names (cities, countries, street names)
- 100+ company/brand names
- Dates: generated programmatically across all months and years — never `Date()`
- Numbers/prices: 0–9999 range, currency symbols from 5 locales (USD, EUR, GBP, JPY, AED)
- Email/URL patterns: varied format, never repeated "test@example.com"
- No Lorem Ipsum — Latin character frequency distribution differs from real UI strings

Verification: before training, confirm no single string appears in >5% of any class's training instances.

### 4.5 Content-agnostic post-training verification

After training, blur all text in 200 test images and re-run inference. If mAP for non-text-dependent classes (`navigationBar`, `tabBar`, `toggle`, `slider`, `alert`) drops >10 points, the model is using text as a proxy feature. Diagnose and add more structural variation to affected templates.

---

## 5. Bounding Box Standards

### 5.1 Definition

The bounding box for any element is the minimal axis-aligned rectangle fully enclosing the element's rendered visual extent — including background fill and border stroke, but **excluding** drop shadows, blur halos, and glow effects (which have undefined rendered extents that vary by rendering engine version).

### 5.2 Per-class box rules

| Class | Box rule |
|---|---|
| `navigationBar` | Status bar bottom edge → navigation bar bottom edge (including hairline separator). Does NOT include status bar. |
| `tabBar` | Tab bar top edge → device bottom edge (including home indicator safe area region). `homeIndicator` is its own class beneath. |
| `homeIndicator` | The pill itself only (~134×5pt on iPhone 14 Pro). Not the full safe area. |
| `alert`, `sheet`, `popover` | The card boundary only. Never include the dimmed background scrim. |
| `listRow` | Each row independently. Never group all rows into one box. |
| `dynamicIsland` | The pill boundary at its current state. Expanded state annotated separately from rest state. |
| Hidden elements | If `isHidden = true` or `alpha < 0.01`: do not annotate. |
| Partial/clipped elements | See Section 6. |

### 5.3 Chrome adjacency rule

Adjacent chrome elements must have non-overlapping, gap-free boundaries:
- `statusBar` ends exactly where `navigationBar` begins (no gap, no overlap)
- `tabBar` and `homeIndicator` occupy non-overlapping vertical strips
- `toolbar` and `tabBar` annotated independently when both present

---

## 6. Partial Image Captures

### 6.1 Annotation rules

**P1 — Clip to image boundary:** Box coordinates must not exceed `[0, pixelWidth] × [0, pixelHeight]`.

**P2 — Clip to visible rect in scroll views:** Annotate only the visible portion of a partially-scrolled element. Set `"occluded": true, "occlusionType": "scroll"`.

**P3 — Minimum visibility threshold:** Do not annotate elements where less than 20% of the logical area is visible. Set `"excluded": true, "exclusionReason": "insufficient_visible_area"`.

**P4 — Partial chrome:** If a chrome element is fully cropped out of the image, do not annotate it. If partially visible, clip to image boundary and set `"occluded": true, "occlusionType": "imageBoundary"`.

**P5 — Dynamic Island mid-state:** Do not annotate mid-expansion animation states. Capture only stable rest or stable expanded states.

**No separate class for partial elements.** Use the same class with `occluded` metadata. The model should generalize "this is a navigation bar, partially cropped" — not treat partial and full occurrences as different semantic entities.

### 6.2 Required partial element coverage

| Element tier | Min partial instances per class |
|---|---|
| Chrome | 200 |
| Containers (sheet, alert, popover) | 150 |
| Controls | 100 |

**Total:** ~4,000–5,000 partial instances across the full dataset, representing 5–8% of training annotations. Mix organically into existing templates via "cropped screen" variants.

### 6.3 Specific scenarios

- **Status bar cropped (10% of templates):** Image starts at navigation bar top edge. `navigationBar` becomes topmost annotated element.
- **Home indicator cropped (10% of templates):** Image ends above home indicator region.
- **List scroll positions:** 3 variants per list template — top, middle, bottom scroll position.
- **Sheet heights:** full (25%), half-height (40%), custom detent ~1/3 (15%), non-dismissible variant (15%).
- **iPad split view:** 40%-width pane; elements at boundary use `occlusionType: "splitView"`.
- **iPadOS floating keyboard:** 20 templates with keyboard at varied positions; `occlusionType: "keyboard"`.

---

## 7. Platform and OS Version Coverage

### 7.1 OS visual profiles (parameterized, not multi-simulator)

The generator does not need to run on multiple simulator OS versions to produce images representing those versions. Define an `OSVisualProfile` struct with rendering switches:

```swift
struct OSVisualProfile {
    var tabBarStyle: TabBarStyle         // .classic | .floating | .liquidGlass
    var navBarStyle: NavBarStyle         // .classic | .liquidGlass
    var hasDynamicIsland: Bool
    var hasHomeIndicator: Bool
    var hasNotch: Bool
    var navBarIsTranslucent: Bool
    var safeAreaTopInset: CGFloat
    var safeAreaBottomInset: CGFloat
}
```

Predefined profiles correspond to known device/OS pairings. Visual appearance is simulated via SwiftUI modifiers on the build SDK — no need to switch SDK versions for different profile styles.

### 7.2 Coverage matrix (minimum 200 images per cell)

| Platform | OS profile | Chrome variants | Device families |
|---|---|---|---|
| iOS | 17.x | Classic navbar/tabbar, notch | SE, standard, Pro Max |
| iOS | 18.x | Floating tab bar, Dynamic Island | SE, standard, Pro Max |
| iOS | 26.x | Liquid Glass navbar/tabbar, Dynamic Island | standard, Pro Max |
| iPadOS | 17–18 | Sidebar, classic/floating tabbar | Air, Pro 11", Pro 13" |
| iPadOS | 26.x | Liquid Glass, sidebar | Pro 13" |
| tvOS | 17–18 | Focus state, shelf layout | Apple TV 4K |
| macOS | 14–15 | NSToolbar, sidebar, window chrome | MacBook Air, Mac mini |

### 7.3 Liquid Glass (iOS 26)

Liquid Glass is a major visual redesign that changes `navigationBar` and `tabBar` appearance significantly. It requires dedicated treatment:

- 10 Liquid Glass templates minimum (in training set, not held out)
- Target: mAP ≥ 0.80 on Liquid Glass test images (slightly below 0.85 overall bar — acceptable for initial training size)
- No new taxonomy classes — `navigationBar` is still `navigationBar`. The visual change is handled by training diversity.
- Withheld from training: all iOS 26 images go to test set only (validates Liquid Glass generalization)

### 7.4 tvOS specifics

- Tab bar at top of screen — model must not conflate position with class identity
- Focus ring: NOT a separate class; annotate element normally with `state.isFocused: true`
- All focusable elements generate both focused and unfocused variants

### 7.5 macOS specifics

- AppKit Y-axis is flipped (bottom-left origin); generator must convert to top-left before writing annotation JSON
- Requires macOS-specific coordinate spike (analogous to Phase 1) before generating at scale
- Window chrome (title bar, traffic lights) is NOT annotated in v1 taxonomy — use `unknown` or exclude

---

## 8. Chrome and Toolbar Variant Coverage

### 8.1 Tab bar variants (≥100 instances each, all annotated as `tabBar`)

| Variant | Description |
|---|---|
| `tabBar_iphone_classic_3item` | iOS 17, 3 items, icon+label, bottom edge |
| `tabBar_iphone_classic_5item` | iOS 17, 5 items, icon+label |
| `tabBar_iphone_floating_ios18` | iOS 18 elevated pill, 5 items |
| `tabBar_iphone_floating_badge` | iOS 18 floating with badge |
| `tabBar_ipad_compact` | iPad in Slide Over (compact width), bottom |
| `tabBar_tvos_top` | tvOS horizontal top-of-screen |
| `tabBar_liquidglass_ios26` | iOS 26 Liquid Glass pill |

### 8.2 Navigation bar variants (≥100 instances each, all annotated as `navigationBar`)

| Variant | Description |
|---|---|
| `navBar_large_title` | Large title, pre-scroll |
| `navBar_inline` | Compact / scrolled-to-inline |
| `navBar_hidden` | `isHidden = true` → NOT annotated |
| `navBar_search_embedded` | UISearchController extending bar height |
| `navBar_translucent` | Blur-through over image content |
| `navBar_opaque` | Solid background |
| `navBar_liquidglass_ios26` | iOS 26 Liquid Glass |
| `navBar_back_visible` | Back chevron present |
| `navBar_back_absent` | Root screen, no back button |

### 8.3 iPadOS size class switching

The same template must produce two layout families by switching horizontal size class:
- Regular width (full screen landscape) → `sidebar` at leading edge
- Compact width (Slide Over, ~iPhone width) → `tabBar` at bottom

---

## 9. State Coverage

### 9.1 Control state matrix

| Class | State distribution |
|---|---|
| primaryButton / secondaryButton / destructiveButton | normal 45%, disabled 20%, selected 10%, loading (`isLoading: true`) 10%, highlighted 5%, focused-tvOS 10% of tvOS instances |
| textField / secureField | empty/placeholder 30%, filled 40%, first-responder 15%, error state 10%, disabled 5% |
| toggle | on 35%, off 35%, disabled-on 15%, disabled-off 15% |
| slider | left 15%, center 40%, right 15%, arbitrary 25%, disabled 5% — include discrete step-snapped variants |
| alert | 1-button 20%, 2-button 40%, 3-button 15%; with-title+message 30%, with-text-field 20% |
| sheet | expanded 25%, half-height 40%, custom detent 15%, non-dismissible 15%; drag handle visible 60% |
| picker | inline 30%, wheel 30%, date-only 20%, time-only 20%, date+time 20%, compact 10% |
| segmentedControl | 2 segments 30%, 3 segments 40%, 4 segments 20%, 5 segments 10% |
| searchField | unfocused/empty 30%, unfocused/filled 20%, focused 20%, with cancel 30%, with scope bar 20% |

### 9.2 Loading and skeleton states

- Spinner inside button → annotate as `primaryButton`, `state.isLoading: true`
- Skeleton shimmer row → annotate as `listRow`, `state.isSkeleton: true`
- Full-screen loading overlay (all content hidden) → **hard negative**: no annotations, not even `unknown`
- `unknown` is reserved for elements that visually resemble a native Apple control but cannot be confidently classified

---

## 10. Accessibility Settings as Training Variation Axes

These are annotation metadata fields (`image.accessibility.*`), NOT separate classes. The semantic role of an element does not change when accessibility settings change — only the visual presentation does.

| Setting | Target coverage |
|---|---|
| `increaseContrast: true` | 15% of all images |
| `reduceTransparency: true` | 15% of all images (changes navbar/tabbar visually — load-bearing variation) |
| `boldText: true` | 10% of all images |
| `buttonShapes: true` | 10% of all images |
| `onOffLabels: true` (toggles) | 20% of `toggle` instances |
| `smartInvert: true` | 5% of all images |
| `classicInvert: true` | 5% of all images |
| `differentiateWithoutColor: true` | 5% of `destructiveButton` instances |

**Exception for rare classes:** Do not spend accessibility-variant budget on classes with <800 instances. Use base visual settings until 800 instances are reached, then add variants.

### 10.1 VoiceOver focus ring

The VoiceOver focus ring (black rounded rectangle over the focused element) is transparent to the annotation layer — annotate the underlying element normally. Generate VoiceOver ring examples for two purposes:

1. **Robustness training:** 100 examples per major control class with VoiceOver ring present. The model must still detect the underlying element.
2. **False positive prevention:** 50 examples where the ring is the most prominent visual feature. Confirm the model does not emit false positive `alert` or `sheet` detections.

---

## 11. Additional Coverage Areas

### 11.1 RTL layouts

15% of all images use RTL layout direction (locales: `ar-SA`, `he-IL`). Mirror existing templates via `.environment(\.layoutDirection, .rightToLeft)` as a post-generation step. RTL changes element positions and text direction but not semantic class.

### 11.2 Tint color variation

Sweep 8 hue families per template: red, orange, yellow, green, teal, blue, purple, pink. System blue is the default and dominates if not controlled. `toggle` on-state should also sweep (not just system green).

### 11.3 Tab bar badges

20% of tab bar instances with badge on first item, 10% middle, 10% last. Values: "9", "99+", "100+", red dot (no number). Annotate badge within the enclosing `tabBar` box — not a separate class.

### 11.4 Status bar content variation

Vary time, battery level (10%/50%/100%), signal type, airplane mode, carrier across status bar instances. Prevents the model from learning specific clock values or signal icons as `statusBar` features. This is covered by the simulator state override protocol in Section 4.3.

### 11.5 Pixel density

- @3x: iPhone Pro/Pro Max, standard iPhone
- @2x: iPad (all), MacBook Retina, iPhone SE

Model input is resized to 640×640, so @2x and @3x elements appear at different scales within the detector's input window. Both must be present in training.

---

## 12. Dataset Quality and Anti-Overfitting

### 12.1 Train/validation/test split

**Split is by template family — not random.**

| Split | Template families | Images |
|---|---|---|
| Train | 70% of families | ~70% |
| Validation | 20% of families (zero overlap with training) | ~20% |
| Test | 10% of families + 200 real-world screenshots | ~10% |

Additionally withheld from training (go to test only):
- iPad Pro 13" device family
- iOS 26 OS visual profile

The withheld-template mAP is the primary pass/fail metric. A model that achieves mAP 0.90 on random-split validation but 0.65 on withheld-template validation is not ready for production.

### 12.2 Pre-training dataset quality gates

All must pass before any Phase 6 training run:

| Gate | Threshold |
|---|---|
| DS-G1 | Class imbalance ratio ≤5:1 (max/min instance count) |
| DS-G2 | UIKit generator contributes ≥2,000 images |
| DS-G3 | Spot-check pass rate ≥95% (≤3 misaligned boxes in 20 per template) |
| DS-G4 | Zero template families in both train and validation splits |
| DS-G5 | `imageSHA256` match rate = 1.0 |
| DS-G6 | No invalid bounding boxes (width > 0, height > 0, coordinates within image bounds) |
| DS-G7 | All rare classes meet 400-instance floor |
| DS-G8 | No single template contributes >15% of total instances |

### 12.3 Detecting template memorization

Symptom: withheld-template mAP is >15 points below template-split validation mAP.

Diagnostic protocol:
1. Compute per-template AP after training. Flag templates with AP >0.95 when overall mAP <0.85.
2. "Text-blinded" test: blur all text in 200 test images and re-evaluate. AP drop >10 points on non-text-dependent classes indicates the model is reading text layout.
3. Run inference on 50 images with deliberately "broken" templates (swapped element positions, inverted color scheme). AP drop >30 points indicates template dependence.

### 12.4 Real-world validation set

**200 manually-annotated App Store screenshots.** Used only to detect synthetic bias — never in training.

- Sourced by manually screenshotting apps on a personal developer device
- App selection: 20 apps × 10 screens, varied across productivity, social, media, utilities, health, finance
- Avoid heavily custom-UI apps (games with custom controls contaminate the native signal)
- Post-hoc human annotation using the overlay viewer
- Stored in `NativeUIAuditKit-Dataset/golden_real_world/` — never committed to any repository

Interpretation: if synthetic test mAP ≥ 0.85 but real-world mAP <0.70, there is a severe synthetic bias. Diagnose which classes suffer most and add more structural variety to those classes' templates.

---

## 13. Dataset Infrastructure

### 13.1 Annotation format

Use the custom JSON schema (`annotation.schema.json v1.0`), not COCO format natively. COCO does not support:
- Multi-coordinate storage (`boundsPixels`, `boundsPoints`, `boundsVisionNormalized`)
- Per-image accessibility metadata
- Per-element `knownIssues` arrays
- `occluded`, `occlusionType`, `excluded`, `exclusionReason` fields

Provide a COCO export converter for PyTorch/YOLOv8 training pipelines. The converter maps `elementType` to integer category IDs via `schemas/category_map.json` and uses `boundsPixels` as the coordinate system.

### 13.2 Generator-direct annotation (mandatory)

The generator is the sole annotation authority. No human re-draws boxes post-hoc for training data.

Generator pipeline per image:
1. Render scene
2. Stabilize: `CATransaction.flush()` + `RunLoop.main.run(until: Date() + 0.05)`
3. Read element frames from layout engine
4. Convert to all 3 coordinate systems
5. Export annotation JSON
6. Capture PNG screenshot
7. Compute `imageSHA256` and write to annotation

**Exception:** The 200-image real-world validation set requires post-hoc human annotation. These images are stored separately and never used in training.

### 13.3 Reproducibility

- `--seed N` CLI argument → byte-identical PNG + JSON every time
- Eliminate non-determinism sources: seeded UUIDs (UUID v5 namespaced on seed + index), seeded `RandomNumberGenerator`, `UIView.setAnimationsEnabled(false)`, `withAnimation(.none)`, simulator clock override, fixed simulator date
- Determinism CI test: after any generator code change, run 10 seeds from before the change and confirm byte-identical output

### 13.4 Dataset manifest

`manifest.json` at dataset root tracks: `datasetVersion` (semver), `generatorVersion`, `totalImages`, split assignments by template family, `classDistribution`, `withheldDeviceFamily`, `withheldOSVersion`, `generationDate` per batch, per-image entries with `sha256`, `templateFamily`, `generatorSeed`, `simulatorState`.

**Versioning policy:** patch = new images same templates, minor = new template families added, major = taxonomy change or split reassignment.

### 13.5 File naming convention

```
{platform}_{device}_{osVersion}_{scale}_{colorScheme}_{dtSize}_{templateFamily}_{seed:06d}.png
```

Example: `ios_iphone15pro_26_3_light_xl_loginform_000042.png`

---

## 14. Training Milestones and Phase Gates

| Gate | Condition | Enables |
|---|---|---|
| DS-G1–G8 | Pre-training quality gates (Section 12.2) | Phase 6 training |
| Phase 6 gate | mAP@0.5 ≥ 0.70 on withheld-template test (iOS, 5-class) | Phase 7 OCR fusion |
| Phase 6a gate | mAP@0.5 ≥ 0.85 on withheld-template test (iOS, 41-class) | Phase 6b tvOS training |
| Phase 6b gate | mAP@0.5 ≥ 0.80 on tvOS withheld test | Phase 8 device inference |
| Phase 6c gate | mAP@0.5 ≥ 0.80 on macOS withheld test | Phase 9 ScreenAuditKit integration |
| Production gate | All 3 models at mAP ≥ 0.85 on respective withheld-template test sets | Public release of `NativeUIAuditKitModels` |

---

## 15. Continuous Expansion

### 15.1 Triggers for new data generation

- New major iOS/iPadOS release with significant visual changes (Liquid Glass is the model)
- Any class AP on withheld-template test falls below 0.80
- New device form factor (new Dynamic Island shape, new notch configuration)
- Taxonomy extension (new class added to v2.0 schema)
- Real-world mAP <0.70 on any class

### 15.2 Expansion procedure

1. Identify the gap (underperforming classes, new visual changes)
2. Build new templates covering the gap; spot-check 20 samples per template
3. Generate to staging directory; merge into dataset; update manifest version
4. Rerun all DS quality gates
5. Train new model version; compare to prior

### 15.3 Retraining policy

- <20% new images (same templates): fine-tune from prior model weights
- >20% new images or taxonomy change: retrain from scratch on full expanded dataset

### 15.4 Model versioning

Each `.mlpackage` records `calibrationOsRange`, `trainedClasses`, and `trainingDatasetVersion` in its metadata. Every `NativeUIElementObservation` report includes `modelId` for reproducibility. Major Apple visual refreshes require a new model version — never patch an existing model's training data in-place after an OS redesign.
