# Local focus review — Start / Review / Finish

No Docker, server, account or device connection. This batch contains the eight
retained Office screenshots. Originals and receipts are separate from editable
copies. Start with **004 and005**: the two Photos Welcome states.

Visual reference: [all41 labels](visual-reference/LabelCheatSheet.html) ·
[quick illustrated sheet](visual-reference/QuickReference.png).
Home app tile = `collectionItem`; external caption = separate `label`, not part
of the focus target. `homeIndicator` is the phone/tablet gesture pill.

## Start

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 reports/work/HUMAN-REVIEW-01/runtime/venv/bin/python \
  scripts/human_review_editor.py \
  reports/work/HUMAN-REVIEW-01/office-batch/batch.json --frame frame-004
```

Use this launcher, **not bare `labelme`**: it keeps settings/cache files local.
If already open, use that window. One window per batch. Finish review runs inside
that window; close it before using the alternative command-line Finish.
Reopening preserves saved edits. No background service or TTR lease is involved.

## Review

**Fast controls:** use **All frame flags on/off** at the top of Flags to toggle
Reviewed, Settled and Content approved together for the current image. Mixed flags
become all-on; when all are checked the button clears all three. Only turn them
on when those statements are true. Box focus/confirmed flags and other images are
unchanged; Finish review remains the bulk box-confirmation action.

Navigate with **⌘→ / ⌘←** on macOS (Ctrl+Right/Left on other platforms), or the
existing **D / A** keys. Works from the canvas or file list; unsaved edits still
offer Save, Discard or Cancel. Navigation never copies labels and does not wrap
at the first/last image. Save/close/relaunch once to activate an updated launcher.

1. In Photos frame004, inspect the two proposed control boxes. **ID1 = View All
   iCloud Photos; ID2 = View Only Shared Albums.** Frame005 uses the same IDs.
   These are manual proposals, not model/native ground truth. Verify the proposed
   `primaryButton` class too; change it if the taxonomy requires another class.
2. Choose **Edit rectangles** (E), zoom in and drag corners to the actual control bounds,
   not its shadow/glow. Keep each frame's own box: focused controls can grow.
   The cropper will add16% context itself. Do not enlarge the annotation for it.
3. Double-click an entry under **Control boxes**. Keep its Group ID unchanged.
   Check exactly one of `focused` / `unfocused`, then `confirmed` only after
   checking the box, class and state. **Neither = unknown**; `flagged` = needs
   discussion; `rejected` = exclude. Do not delete existing controls to exclude them.
   Label-list visibility checkboxes are **not** review confirmation.
4. At the top-right, check `reviewed`, `settled`, `content_approved` for the frame
   only when true. Save, then use **Next Image** / **Prev Image** (D / A). Review
   frame005 the same way. Save both. The other six context frames may remain pending.
5. For a new rectangle, use **Create rectangle** (R), click opposite corners, and choose a taxonomy class.
   Give it an unused positive Group ID. Matching IDs across different frames mean
   the same control only within a declared screen/pair; pairing new examples needs
an explicit reviewed pair assignment, not just matching integers.

**Already-open older window:** Save and close before relaunching for the new
rectangle-only toolbar; we do not force-restart or auto-convert your annotations.
Until then use **Edit → Create Rectangle** in the current window, not Create Polygons.
Existing polygons must be redrawn as rectangles with the same control Group ID;
they are not silently accepted or automatically converted.

The static [numbered sheets](office-batch/review.html) preserve full-frame context.
The [proposal crop previews](proposal-crops/) contain two side-by-side Photos pairs,
ordered frame004 then005. They are crop QA, not accepted labels. We can discuss the
whole batch after you finish—no chat exchange between edits.

## Copy boxes between Home frames

Save and close the old window, then relaunch with the Start command above
(use `--frame frame-007` to start at your annotated Home image).

1. Choose **Edit → Select all boxes** (⌘A with canvas focus), then **Copy boxes** (⌘C).
   Visibility checkmarks do not select boxes. The same actions are in the toolbar;
   on shorter windows use the Edit menu if lower toolbar buttons are hidden.
2. Copy assigns missing local Group IDs, preserving existing IDs. **Save** the
   source so those IDs survive. They are local review identities, not native labels.
3. Open an unannotated Home frame in the **same window**, then **Paste boxes** (⌘V).
   The clipboard is editor-local, not the system clipboard; it survives frame changes,
   not closing the app. Different screen types/dimensions and ID collisions are rejected
   with an explanation. Existing destination boxes are never overwritten.
4. Adjust the enlarged/shrunken tiles for the new focus state; update focused/unfocused
   flags and explicitly confirm each box. Copied focus states remain proposals;
   pasted `confirmed` and destination `reviewed` are cleared. Other flags, including
   flagged/rejected, remain as copied and must be checked. Save after reviewing.

Copying does not create an approved pair or make the data training-eligible.

## Finish batch

Use **Finish review…** beside Save in the toolbar, or **Edit → Finish review…**.

1. If you have unsaved edits, approve **Save** or cancel without changing anything.
2. Inspect the batch summary. **Needs attention** rows list exact box IDs/reasons.
   Select one and click **Open selected frame to fix/check**. Choose the missing
   focus state yourself, save, then return to Finish review. No focus is inferred.
3. For the **Ready** frames, enter your reviewer name and check the explicit
   statement that you reviewed their bounds/classes/focus states and that their
   images are settled and content-approved. You do not need to tick each box's
   confirmed flag individually. Do not attest frames you have not reviewed.
4. Click **Confirm ready frames and finish**. Missing local IDs on new boxes are
   assigned; existing IDs, boxes, classes and focus states are preserved. Blocked
   frames remain unchanged. The action backs up saved annotations and produces a
   new immutable revision under `office-batch/review-revisions/`, with a receipt.

The dialog can finish the ready subset while other frames remain pending. It
refuses stale previews if saved data changed. Cancel does not confirm anything;
an explicitly approved Save before opening the dialog is retained. If a storage
error interrupts application, stop editing and use the reported `before/` backups
and `failure.json` to reconcile the exact affected frames; do not blindly retry.

Alternative CLI: close the editor after saving, then run this once after review:

```sh
PYTHONDONTWRITEBYTECODE=1 reports/work/HUMAN-REVIEW-01/runtime/venv/bin/python \
  scripts/human_annotation_review.py finish \
  reports/work/HUMAN-REVIEW-01/office-batch/batch.json \
  reports/work/HUMAN-REVIEW-01/human-revision-001 \
  --reviewer Joseph --reference 'Photos004-005 reviewed in local editor' \
  --reviewer-kind human --confirm-batch
```

Finish snapshots edits into a **new immutable revision**, validates identities,
hashes, boxes, flags and pairs, and accounts for pending/rejected controls. It
never marks unchecked examples reviewed. Saving alone is not acceptance. For a
later revision choose a new output name; do not overwrite earlier evidence.

Then run production crop QA against that exact revision:

```sh
PYTHONDONTWRITEBYTECODE=1 reports/work/HUMAN-REVIEW-01/runtime/venv/bin/python \
  scripts/human_annotation_review.py crop-qa \
  reports/work/HUMAN-REVIEW-01/office-batch/batch.json \
  reports/work/HUMAN-REVIEW-01/human-crops-001 \
  --revision reports/work/HUMAN-REVIEW-01/human-revision-001/revision.json
```

All data remains **development diagnostics**, including reviewed pairs. Training
admission is a separate policy decision. No model inference is run by these tools.

## Reinstall only if needed

The tested environment is already installed (~292MiB). The pinned dependency list
is [requirements-human-review.txt](../../../scripts/requirements-human-review.txt).
Use Python3.12 and a non-hidden in-project venv; this host's Qt hides plugins under
dot-directories. Put pip cache and TMPDIR under `.build/human-review/` as recorded
in the handoff. Do not reuse the training environment or install globally.
