# Capture once, review a small batch

This is preparation, not a request to capture now. The action-linked TTR recorder
must first pass its start/stop/export test. Current failure evidence is in
[recorder readiness](../FOCUS-REGRESSION-V2/recorder-readiness/handoff.md).
No chat after each press. The human operates TTR; one recording contains the whole
approved walkthrough, including input events, failures and settled frames.

## First walkthrough: available Apple apps and OS UI only

Choose from already-accessible screens below. Skip anything unavailable, sensitive
or uncertain; record the gap instead of opening accounts or changing settings.

| Family | Suggested safe situation | What to retain |
|---|---|---|
| Artwork grid | Home; an already-accessible Apple media grid | Two adjacent focus states with competitors; Home capped at two situations |
| Shelf/card | TV or Music browse shelf already accessible | Center and edge cards; do not purchase or subscribe |
| Native list | Settings top-level and a safe informational submenu | Focused row, adjacent row, visible neighbors; do not toggle settings |
| Button/detail | Photos Welcome; accessible media information panel | Different action buttons without activating destructive/account/purchase actions |
| Navigation/toolbar | TV/Music tabs or existing Photos navigation | Focus movement between tabs; distinguish active tab from current focus |
| Overlay/search/player | Control Center visible panel; safe search keyboard or existing player overlay | Observe and move only within operator-approved controls; no text/account entry, playback or settings change required |

These are candidate situations, not assertions that every installed version exposes
them. Operator approves the actual screen before interaction. Back/Home transitions
are retained, but do not turn transition frames into settled examples. Stop on wrong
target, another user, black capture, sensitive content or uncertain control state.

Preparer, not annotator: verify target/session and action timestamps; preserve raw
files; select settled states; assign app/layout/family once per screen; prepare the
queue. First batch: six to eight varied frames, ideally one from each available
family. Later batches: eight. Overall 24 situations/48–72 frames remain collection
targets, not accuracy gates. Do not fill gaps with repeated Home or Photos dialogs.

## Fast annotation pass

1. Review only the numbered queue, not every recorded frame. Exact compatible pixel
   repeats stay in sequence evidence with a canonical reference. Near matches stay
   separate; focus enlargement or scrolling can change geometry.
2. Use **⌘A, ⌘C, ⌘V** to reuse boxes on compatible screens. Pasted boxes are proposals:
   adjust changed bounds and focus; confirmation is deliberately cleared.
3. **Double-click a rectangle** to edit its label/focus flags. Draw with R; edit with E.
   Use **⌘→/⌘←** (or D/A) to move between frames. Save normally.
4. Use **Finish review** once per batch. Fix only the listed exceptions. Enter your
   name and confirm the Ready frames after visually checking them. No need to click
   Confirmed on every box or turn on all three flags image by image.
5. Optional, initially unchecked: confirm **all visible focusable controls are
   included** in every Ready frame. If unsure, leave it off; partial review still
   saves. This is not a claim that the model is accurate.

Label the control body using the existing cheat sheet, not its glow. Focus states
must come from the displayed evidence, not button intent or OCR. Empty/missing
controls, ambiguity and unreviewed frames remain pending. Originals are untouched;
Finish review saves a backed-up immutable revision. Crop QA follows the existing
production path after review, not another annotation task.

Measure first-batch elapsed review time and number of corrected boxes once, then
adjust batch size or prefills. No per-box timing form. Existing eight frames remain
a separate smoke set; no reannotation requested by this tranche.
