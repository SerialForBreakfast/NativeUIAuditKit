# Human review: label names and box boundaries

2026-09-28, HUMAN-REVIEW-01 clarification. Applies to this diagnostic review lane;
not a taxonomy, native geometry, training admission or historical-label rewrite.
Visual companion: `reports/work/HUMAN-REVIEW-01/visual-reference/LabelCheatSheet.html`.

## Home-screen example

The selectable Photos app tile is **collectionItem**. Its separate “Photos”
caption is **label** in a full UI-element annotation pass. Do **not** extend the
tile's box down to include that external caption. Do not use `homeIndicator`:
that means the thin iPhone/iPad gesture pill, not a Home-screen app icon.

Evidence: `tvOSHomeScreenTemplate.swift` records `collectionItem_app_*` on the
card before the caption, then records `label_app_*` separately (lines165–203).
`tvOSTopShelfMenuTemplate.swift` likewise separates shelf cards and title labels
(lines222–245). §5.2 of NativeUIElementDetection.md defines the semantic roles.
These templates support the convention, not native bounds of the supplied image.

For the current **focus review**, annotate focusable targets and visible competing
controls. Do not create a separate focus example for the caption or decorative
flower logo. Those may be `label` / `imageView` in a separately scoped full
detection annotation pass. The legacy generator sometimes annotates nested
image/text content; this focus lane intentionally does not claim exhaustive
detection coverage. No blanket new prohibition on nested detection labels.

## Bounds rules

- Axis-aligned rectangle around the visible control surface, including its internal
  text/artwork. Tight enough to exclude surrounding empty space, shadows/glow and
  unrelated neighbors; do not trace rounded corners or draw a polygon.
- External caption: separate, outside the tile box. Text **inside** a button/row
  belongs inside that control box. A composite row includes its label, value and
  disclosure indicator within the same visible row surface.
- A thin solid border belonging to the control may be included; do not enlarge the
  box to chase a diffuse focus halo. Verified native geometry, when actually
  supplied for that frame, remains separate authoritative evidence. A genuine
  disagreement blocks the example rather than silently changing conventions.
- Use each frame's bounds; focus scale/animation can change them. Use settled
  frames. Do not infer invisible cell extents or copy a focused box blindly.
- Do not add the16% context yourself. The production cropper expands and resizes
  to256×256. That resize can stretch wide controls; no aspect-fit change here.
- Class describes the role; focus is a separate flag. A bright focused secondary
  button does not become a primary button. Color alone does not determine role.
- Ambiguous role/geometry: leave unconfirmed and flag. `unknown` is a legitimate
  taxonomy placeholder, not permission to accept a guessed focus/control label.

## Rectangle-only editor refinement

The pinned launcher exposes Create rectangle / Edit rectangles, with R / E keys;
Ctrl+R remains the stock rectangle shortcut (Command mapping follows Qt/macOS).
Non-rectangle drawing actions and shortcuts are hidden/removed. A small pinned
window subclass guards the actual drawing-mode entrypoint, so menus/load transitions
cannot restore polygon drawing. Existing JSON/ingestion already accepts only
axis-aligned two-corner rectangles. Existing annotations are never auto-converted.
The currently running window must be saved and closed by the operator before
relaunch; no forced restart or second writer against the same review workspace.
