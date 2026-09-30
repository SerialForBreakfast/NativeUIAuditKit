# Auto-detect annotation rectangles

| Outcome | Result |
|---|---|
| Software verified |Passed110Python tests, offline Swift build and123Swift tests|
| Data eligible |Not applicable; proposals are unconfirmed, no admission changes|
| Integration qualified |Actual pinned Qt editor preview/add/cancel/undo/save/reload tested offscreen; operator relaunch pending|
| Model gate passed |Not assessed; no model execution/training/export|

## Use

In the updated annotator, click **Auto-detect boxes…** in the toolbar or Edit menu.
It scans only the current image. The numbered preview lets you uncheck unwanted
rectangles, select all/none and choose one initial label (last-used label by default).
Click **Add N boxes**, then adjust individual bounds/labels and mark focus normally.
Cancel leaves annotations unchanged. Undo reverses the added group; nothing is
automatically saved. Existing boxes are retained and overlapping proposals skipped.
All added boxes start unfocused and unconfirmed; frame Reviewed is cleared while
Settled/Content approved are preserved. Finish review still requires human review.

This optional local Pillow/NumPy geometry aid has no new dependencies, downloads,
uploads, model inference, OCR or focus prediction.640pixel bounded analysis,
40proposal/100total-box caps. Existing manual drawing, click suggestions and presets
remain unchanged. The annotator must be relaunched to load the new toolbar action;
the current window has not been closed or its human edits modified.

## Evidence and limits

- `human-tests.log`:110tests, including18actual Qt interaction tests and4detector
  tests; existing click suggestion, review/confirmation and annotation integrity
  behavior preserved. Preview cancel, last label, partial selection, defaults,
  existing flags/IDs, undo, save/reload, empty/error/manual-mode handling tested.
- `swift-build.log`, `swift-test.log`: offline build,14XCTest+109Swift Testing pass.
- `.build/human-review/gui-tests/auto-detect.png`: actual Qt preview inspected.
- `final-pass/retained-proposals.json` and overlays:3previously exposed development
  screenshots inspected,7/6/9proposals at0.118/0.185/0.120seconds on this host.
  Source image hashes unchanged; annotations never opened for writing.
- Flat Home tiles are useful proposals. Featured/search screens also produce
  containers, partial card regions and internal logos. Borderless tabs/rows and
  keyboard letters can be missed; clipped elements intentionally abstain. This
  is not measured semantic detection accuracy or complete focus-candidate coverage.
  The preview explicitly warns about containers/partial regions; do not accept all
  merely because the tool drew them. No precision/recall claim is made.

The initial Qt launch failure was investigated rather than retried blindly.
Installed plugin dylibs were BSD-hidden; Qt's discovery omitted them even though
their bytes were readable. Byte-identical, hash-verified project-local runtime
copies restore discovery. Only the hidden bit on owned cache copies is cleared;
installed binaries, system flags/permissions and signatures remain unchanged.
Initial failure logs are retained; repeated fixed launches pass.

Changed reusable code: `scripts/human_auto_boxes.py`, `human_review_editor.py`,
`test_human_auto_boxes.py`, `test_human_review_editor_interactions.py`.
Existing dirty geometry/model work was preserved. No git writes.

## Next

Save/close the running annotator before reopening the same batch with this version.
Try it first on a Home grid; review mixed artwork screens more selectively. User
feedback should decide whether to keep this lightweight aid or separately add
semantic detector proposals. No extra annotation batch or training run started.
TTR coordination is not applicable to this local editor-only change.
