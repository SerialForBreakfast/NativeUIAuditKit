# tvOS framework projection contract v1

- **Contract:** `tvos-framework-projection-v1`, mapping version `tvos-framework-projection-v1.0`.
- **Machine table:** [tvos-framework-projection-v1.json](tvos-framework-projection-v1.json). Every derived manifest and model receipt records its SHA-256.
- **Owner:** Maximum-mini-NUIAK. **Counterpart:** Sillycon-TTR (TTR task R604-16).
- **Status:** accepted by Sillycon-TTR under amendments A1. The v1.0 machine table is frozen. After the first capture under this contract, a change creates v2.

## Purpose

Joe's direction, 2026-11-12: detector labels must come from real UIKit and SwiftUI construction.
Invented categories must not enter data generation or training.
This contract defines which visible object gets which training box, and why.
1 question must have an auditable answer: why did this patch of pixels get this label?

TTR records framework facts. NUIAK projects those facts to detector classes with this table.
NUIAK can change the projection without TTR changing what it records.

## Decisions (Joe, 2026-11-12)

- The tvOS detector has 10 classes, in this fixed order: `button`, `cell`, `picture`, `textField`, `toggle`, `segmentedControl`, `pageControl`, `bar`, `dialog`, `indicator`.
- D3 roles `adjustable` and `container` are removed for tvOS. No tvOS framework type produces them (section E).
- There is 1 `button` class. Style (`bordered`, `borderedProminent`, …) and semantic role are attributes, not classes.
- A SwiftUI `Button` with `.card` style projects to `cell`.
- TTR custom `UIControl` and `UIView` controls (`ttr_convention`) are not admitted for training. TTR rebuilds them with native primitives.

The iOS 41-class schema (`NativeUIElementType`) stays unchanged as stable public API. Shipped model contracts do not change.
`scripts/roles559.py` stays unchanged, so historical results stay reproducible. For tvOS training under this contract, schema names are not labels.

## A. Dispositions

Every in-scope visible object gets exactly 1 disposition with a reason.

| Disposition | Example | Training effect |
|---|---|---|
| `target` | A visible card action with a measured body | 1 detector box with object ID, class, box, and `rule_id` |
| `owned_metadata` | The card's image, title, subtitle, or focus halo | Keep `parent_id` and bounds. No extra detector box. |
| `out_of_scope` | Static synopsis text or a declared decorative background | Record the reason. The frame can still be complete. |
| `unresolved` | A visible custom control with no admissible framework evidence | Exclude the frame from full-frame detector training. Keep verified observations for other uses, such as focus. |

A frame is eligible for full-frame detector training only when it has 0 `unresolved` objects.

### Worked examples (also in the answer keys)

1. **Kanopy synopsis.** A synopsis line is a `UILabel` or SwiftUI `Text` with no owner. It is `out_of_scope` (`static_text`). It is never a button.
2. **Watch button with icon and caption.** The `UIButton` is 1 `button` target. The icon and the caption are `owned_metadata` with `parent_id` = the button.
3. **Poster.** A poster is `picture` only when it is standalone artwork: a `UIImageView` or SwiftUI `Image` with no owning target and its own measured body.
   A poster inside a cell is `owned_metadata` of that cell. A poster drawn by a plain `UIView` is `unresolved`.

## B. Projection rules

Each rule has a stable `rule_id`. The full table is in the JSON file. Summary:

| Rule | Framework construction | Result |
|---|---|---|
| `cell.swiftui-card` | SwiftUI `Button` with applied `.card` style | `cell` target |
| `button.swiftui` | SwiftUI `Button` with a known non-card style | `button` target |
| `button.uikit` | `UIButton`, any `UIButton.Configuration` | `button` target |
| `button.link`, `button.menu` | SwiftUI `Link`, `Menu` (the visible trigger) | `button` target |
| `button.alert-action` | `UIAlertAction` button | `button` target, role = `UIAlertAction.Style` |
| `cell.collection`, `cell.table`, `cell.list` | `UICollectionViewCell`, `UICollectionViewListCell`, `UITableViewCell`, SwiftUI `List` row | `cell` target |
| `picture.image` | `UIImageView` or `Image` | `picture` target when standalone, or `owned_metadata` when owned |
| `textField.input` | `UITextField`, `TextField`, `SecureField` | `textField` target |
| `textField.search` | `UISearchBar` field or `.searchable` field, visible | `textField` target |
| `toggle.swiftui` | SwiftUI `Toggle` | `toggle` target |
| `segmentedControl.uikit`, `segmentedControl.swiftui` | `UISegmentedControl`, `Picker` + `.segmented` | `segmentedControl` target |
| `segment.item` | 1 segment | `owned_metadata`, `focus_destination` |
| `pageControl.uikit`, `pageControl.page` | `UIPageControl`, visible `TabView` + `.page` index | `pageControl` target |
| `bar.tab`, `bar.navigation` | `UITabBar`, `UINavigationBar` | `bar` target |
| `bar.tab-item` | 1 tab item | `owned_metadata`, `focus_destination` |
| `dialog.alert`, `dialog.sheet` | `UIAlertController`, `.alert`, `.confirmationDialog`, presented `.sheet` or menu surface | `dialog` target |
| `indicator.progress` | `UIProgressView`, `UIActivityIndicatorView`, `ProgressView` | `indicator` target |
| `text.static` | `UILabel`, `Text` | `out_of_scope` (`static_text`), or `owned_metadata` when owned |
| `view.decorative` | plain `UIView` with declared decorative purpose | `out_of_scope` (`declared_decoration`) |
| `custom.ttr-convention` | custom `UIControl` or plain `UIView` without declared purpose | `unresolved` (`ttr_convention_not_admitted`) |
| no rule | any other fact set | `unresolved` (`unprojected_framework_facts`) |

### Rule resolution

- The rule with the highest specificity wins. `cell.swiftui-card` (3) beats `button.swiftui` (2).
- 2 matching rules with equal specificity and different outcomes give `unresolved` (`conflicting_rules`). There is no silent first match.
- `button.swiftui` needs a known style. A SwiftUI `Button` without style evidence is `unresolved` (`style_evidence_missing`).
  The importer cannot tell a card from a plain button without that evidence.
- Ownership applies after matching. `parent_id` must name an object in the same frame (else `missing_parent`). `owner_relation` must be set (else `ownership_relation_missing`).
  - A child with `owner_relation: same_action` is `owned_metadata` of its parent.
  - A child with `owner_relation: separate_action` keeps its own target.
  - So a wrapper and a child that are 1 action give 1 target.
- Rules that need a visible affordance (`textField.search`, `pageControl.page`, `dialog.sheet`) use `observation.affordance_visible`:
  - `true`: target.
  - `false`: `out_of_scope` (`affordance_hidden`).
  - Missing: `unresolved` (`affordance_evidence_missing`).
  - A modifier on a screen is not evidence of a visible object.
- Tab items and segments keep their own identity and geometry. Focus truth names the item, not the bar. The 10-class detector has no tab-item class.
- Semantic role is recorded only when construction supplies it (`Button(role:)`, `UIAlertAction.Style`). `UIButton` has no role. Titles never supply a role.
- Keyboard and PIN keys have no special rule. A key that is a collection cell is `cell` through `cell.collection`. This resolves the §5.2.1 conflict for this contract only.
- Invariance: the ID prefix, title, language, tint, and Fixture family never take part in matching.

## C. Evidence model

TTR (or an instrumented app) exports 3 parts for each object, and records the source of each:

1. **Construction fact:** `instance_id`, `framework` (`UIKit` or `SwiftUI`), `primitive`, `style`, `style_source`, `role`, `purpose`, and `source`.
   `style_source` is `applied_instance` when the style was read from the built instance, or `declared_recipe` when it was only declared.
   Rules that need a specific style (`.card`, `.segmented`, `.page`) need `applied_instance`.
2. **Runtime observation:** `instance_id`, the nearest public `uikit_class`, `visible_bounds_px`, `traits`, `focusable`, `selected`, `affordance_visible`, `scene_revision`, and `screenshot_sha256`.
3. **Join:** the same `instance_id` in both parts. The observation's `scene_revision` and `screenshot_sha256` must equal the frame's values.

Rejections:
- A missing join gives `unresolved` (`join_mismatch`). A frame whose sidecar names another screenshot or scene revision gives `frame_identity_mismatch`.
- A UIKit backing view alone cannot establish a SwiftUI construction.
- Accessibility traits are observations. If observations disagree with the rule's expectation (for example, a `button` target that is not focusable), the object is `unresolved` (`fact_conflict`).

NUIAK writes these values for each object: `rule_id`, `mapping_version`, class, disposition, reason, and the evidence hashes.

## D. Geometry and focus

- **Pixel convention** (TTR r5): half-open integer rects, edges on pixel boundaries, PNG top-left origin, `floor(min × scale)` and `ceil(max × scale)`.
  Scale and transform come from the frame's `captureGeometry`.
- **Box semantics:**
  - `button`, `cell`, and other focusable controls use the clipped interactive body.
  - `picture` uses the visible artwork body.
  - `bar` uses the bar body. Tab items and segments use their own item bodies.
  - For TVCatalog’s floating tab bar, the detector target encloses the visible group background. Clip to the viewport. Exclude transparent host margins and the selected-item highlight. Keep the full UIKit layout frame and item focus ID as separate evidence. A full-width painted bar can have a full-width target.
  - Maximum-mini-NUIAK verified one such body from stable before/after SDK layout rectangles and an independent PNG outline. If the body is hidden, ambiguous, or lacks a matching visible extent, withhold automatic geometry for that instance. This interpretation uses the existing bar_body rule. [Development readback](../../reports/work/RESET604/bar-boundary-v1/description.json)
  - `dialog` uses the presented surface, without the dimming layer.
  - Focus effects (scale, glow, shadow) never change a box.
- **Release gate:** worst edge error 1.78 px and minimum IoU 0.9722.
  - Source: the starter qualification of 64 frames (`comp-qual-v1`).
  - Stretch target: 1 px / 0.98. Controls with a short side under 48 px use edge error only.
  - The gate counts as qualified only after it passes on small tabs, large cards, scrolling, and overlays.
- **Separate recorded criterion:** the composition capture audit (3,214 frames) passed at 8 px / 0.90 IoU. It is a different test and does not show the release gate.
- **Focus** has 3 states: `focused` (1 object ID), `known_no_focus`, and `unknown`.
  An empty registry does not prove `known_no_focus`. Focus is valid only for the same scene revision and screenshot as the frame.

## E. Platform availability matrix

Pinned to Xcode 27.0 (27A266a), the AppleTVSimulator 27.0 SDK (24J360), and deployment target tvOS 17.0 (TTR Fixture).
Each type has 1 status:
- `unavailable_on_target`: the SDK marks it unavailable on tvOS.
- `available_outside_10_roles`: it exists on tvOS but has no target rule.
- `projected`: a rule maps it.

After an SDK update, re-check `unavailable_on_target` rows first. A newly available type is a reason to revisit the removed roles.

| Type | Status | Evidence |
|---|---|---|
| `UISwitch`, `UISlider`, `UIStepper`, `UIDatePicker`, `UIPickerView`, `UIColorWell`, `UIRefreshControl`, `UIToolbar` | unavailable_on_target | UIKit headers `API_UNAVAILABLE(tvos)` |
| WebKit (`WKWebView`) | unavailable_on_target | framework absent from the tvOS SDK |
| SwiftUI `Slider`, `Stepper`, `DatePicker`, `ColorPicker`, `Gauge` | unavailable_on_target | `@available(tvOS, unavailable)` |
| SwiftUI `Picker` (non-segmented styles), `UILabel`, `Text` | available_outside_10_roles | no target rule |
| All types in section B | projected | see the JSON `availability` list for each header line |

## F. Qualification (both teams)

- Keep TTR cases Q1–Q5 and mutations M1–M9.
- Revised keys: Q1 and Q5 project to `button` with `style` as an attribute. Q5 expects 4 `button` targets and 0 roles.
- New case Q6: a real cancel and destructive role, built with SwiftUI `Button(role:)` and `UIAlertController` with `UIAlertAction.Style`.
- **Tensor round-trip:** the production importer, dataset writer, and training loader produce a tensor.
  NUIAK decodes it back to class names and screenshot coordinates and compares the result with the independently written key.
- **Invariance pairs:**
  - Change tint, text, locale, or selection with construction fixed. The label must not change.
  - Change construction or applied style with appearance fixed. The label must follow the rule.
  - Put the same title and artwork on a plain `Button` and a `.card` `Button`. The labels must be `button` and `cell`.
- **Frame identity:** a valid screenshot paired with the previous frame's valid sidecar must be rejected (`frame_identity_mismatch`).
- Each corrupted case must fail for its named reason. A generic parse failure does not count as a pass.

## Agreed interpretations (TTR amendment A1, 2026-11-12)

Sillycon-TTR accepted the table unchanged (same SHA-256) and vendored it by hash. Both evaluators now apply these readings.
They clarify the table. They do not change any rule outcome.

1. `owned: true` means the object has a `parent_id`.
2. A missing `style` fails `style_required` and a `style` match, and passes `style_not`.
   If no rule matches, and a rule fails only because style evidence is missing or only declared, the result is `style_evidence_missing`.
   A different known style gives `unprojected_framework_facts`. A `.card` known only from the recipe does not fall back to `button.swiftui`.
3. `button.swiftui` admits a declared non-card style in v1.0. (Proposed for v1.1: require `applied_instance`.)
4. A construction without an observation gives `join_mismatch`. An observation without a construction gives `framework_facts_missing`.
5. The affordance check runs before ownership. An `unresolved` object stays `unresolved` under `same_action`. An `owned_metadata` object has `reason: null`.
6. `expect` checks only `focusable`.

- **Frame layout:** the canonical `tvos-framework-frame-v1` layout is TTR's live layout: a `frame` block, `focus.object_id`, and objects wrapped as `{"object", "content_id", "reuse_generation"}`.
- **Focus states:** `transition` and `unavailable` count as `unknown` for training.
- **`applied_instance`:** a value stored on the built instance by the exact code that applied it, read back at observation time, and cleared on reconfiguration.
- **Tensor effect:**
  - `target`: 1 box.
  - `owned_metadata` and `out_of_scope`: no box (background pixels; there is no ignore mask).
  - `unresolved`: the frame is excluded.
  - Focus: never a tensor class. Unknown focus is never a no-focus negative.

Proposed for v1.1, which needs both teams to accept a new hash:
- `applied_instance` on `button.swiftui`;
- `covered_by_presentation` for dialog underlays (A1.4);
- a minimum visible target size (the loader keeps a 1-pixel box);
- per-task eligibility for detection and focus (A1.5).

## Native-primitive requests to TTR

These make Fixture frames admissible under this contract:

- **Cards:** `UICollectionViewCell` in `UICollectionView`. The Fixture has `FixtureNativeCollection`.
- **Rows:** `UICollectionViewListCell` or `UITableViewCell`. The Fixture has native table cells.
- **Tabs:** `UITabBar` items through `UITabBarController`, or `UISegmentedControl` when the intent is a segment.
- **Standalone artwork:** `UIImageView`. A plain `UIView` that draws artwork is `unresolved`. The Q1 `hero_artwork` needs this change.
- **Text:** `UILabel`. The observation must include the `UILabel` instance.
- **Roles:** SwiftUI `Button(role:)` in a hosted view, and a real `UIAlertController`. The system decides the appearance.
- **Decoration:** declare `purpose: decorative` on plain background views.

## Delivery order

1. **Freeze 1 contract.** Maximum-mini-NUIAK and Sillycon-TTR freeze this table, the class order, dispositions, evidence fields, focus states, geometry rules, and revised keys.
2. **Prove the importer.** Maximum-mini-NUIAK runs the clean and corrupted packets through the production importer, writer, and loader.
3. **Prove 2 routes.** Sillycon-TTR builds and pushes the features. Maximum-mini-TTR builds them from source and proves 2 routes:
   - 1 native Fixture route.
   - 1 instrumented real-app route with nested artwork and text, several focus destinations, and a scroll or overlay.
   Then the same importer runs a second layout with only configuration changes.
4. **First strict membership.** Maximum-mini-NUIAK publishes it with a coverage report.
   - v2 and v3 inputs and original human reviews stay preserved.
   - TVBench labels get their own version.
   - Candidates are compared on identical images under 1 mapping version. A score change from relabeling counts as an evaluator change.
5. **Matched training comparison** starts when the corpus supports the stated question. Unsupported classes are reported explicitly.

## First milestone

1 real-app screen where every emitted training box traces to its visible owner, measured geometry, framework evidence, and projection rule.
The same report explains every visible item that produced no box.

## Coverage reporting

Every result states its denominator. The report for each app and layout lists:
- attempted frames and admitted frames;
- visible targets by class;
- unresolved objects, geometry failures, and focus failures;
- excluded custom controls, counted separately.

A claim such as "all admitted labels matched" is valid only with these counts.
For example, 8 / 8 targets on 1 TVCatalog screen is a valid result. It leaves the other classes, screens, and apps unqualified.
