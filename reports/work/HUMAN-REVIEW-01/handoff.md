# HUMAN-REVIEW-01 — lightweight local review handoff

## Actual human completion and production crop QA

2026-09-28 supersedes earlier operator-pending notes below. Joe explicitly finished
all8 frames/113 controls at18:47:53Z. Verified immutable revision
`office-batch/review-revisions/20260928T184752Z-15f34d37/revision/revision.json`
matches the saved editor JSON; both defined Photos pairs reviewed. Actual production
crop QA completed113/113 at `human-crops-joe-20260928/crop-qa.json`, with no model.
All113 crops visually inspected during [HR2 audit](../HUMAN-REVIEW-02/handoff.md).
Human diagnostics are ready; training/development-evaluation admission still requires
the separate policy decision. No labels were silently changed during crop/audit.

## Follow-up: frame-flag toggle and fast image navigation

2026-09-28. Added All frame flags on/off in the Flags panel and Edit menu. It
only toggles the current frame's reviewed/settled/content_approved assertions;
mixed states become all-on. No box flags, other frames or acceptance policy change.
Added Command-Left/Right (Qt Ctrl-Left/Right) alongside A/D. Removed stock
Ctrl-Shift-A/D navigation aliases that implicitly enable previous-label propagation;
ordinary navigation never copies labels. Stock Save/Discard/Cancel remains.
Known absolute image paths are normalized to file-list entries so Next/Previous
also works after Finish review's Open frame action.

Software and local integration verified: `speed-ui-accepted/verification.json`
tests real on/off/mixed toggles, unchanged box flags, current-frame isolation,
Command arrows from canvas/file list, A/D, first/last boundaries, unsaved Cancel/
Save, no implicit copy, disabled controls without an image and saved reopen.
`speed-controls.png` was visually inspected. `speed-finish-regression`,
`speed-rectangle-regression`, `speed-clipboard-regression`, `speed-roundtrip`
retain passing integrated regressions (8 image save/reopens,4 production crops).
`speed-python-tests.log`:136 pass; `speed-swift-build.log`:build passed without
warnings; `speed-swift-test.log`:14 XCTest +109 Swift Testing pass. Source hashes:
`speed-source-sha256.txt`.

The first isolated test stalled because its response timer ran before the Save
dialog; only that identified test process was stopped (PID83699), not the user
editor. Bounded watchdog and corrected timer ordering now prevent this. A second
test assertion was corrected to compare annotation fields rather than reject the
stock serializer's additional optional description field. Failed evidence remains
in `speed-ui-check*`/`speed-ui-verified.log`; final tests pass.

Data: no human labels changed or admitted by this implementation. Model gate:
unassessed. Shared coordination: not applicable. Operator confirmed saving and
closing; updated editor launched at frame001 (`editor-speed-live.log`). This
follow-up is complete for review; human use/confirmation remains operator-owned.

## Follow-up: Finish review with explicit bulk attestation

2026-09-28. Completed the maintainer-assigned Finish review action, not a new
annotation application. Toolbar (beside Save) and Edit menu open a read-only batch
preview with ready/exception rows, exact control IDs/reasons and Open frame.
Unsaved current edits require explicit Save or Cancel. Reviewer name plus an
unchecked attestation authorize bulk confirmed/reviewed/settled/content-approved
flags only for ready frames. Missing IDs on new controls are allocated locally;
original proposal identity cannot be guessed. Unknown/conflicting focus, flagged
rows, bad geometry/IDs or integrity/provenance failures are not auto-approved.

The helper reuses the importer's document validation and finish implementation.
It rechecks the preview against saved hashes, backs up exact JSON, stages atomic
per-file replacements and saves an immutable revision plus receipt. Blocked frames
stay untouched. Partial I/O failure preserves before files and applied-frame
membership; no rollback over potential concurrent user edits. One editor per batch
remains required; cross-process writes are detected optimistically, not locked.

| Outcome | State | Evidence |
| --- | --- | --- |
| Software | Verified |13 new generated-fixture tests;136 total Python tests pass; offline Swift build and14 XCTest +109 Swift Testing pass |
| Data | Real operator completion still pending |Read-only actual saved audit:113 rectangles;004/005/006/008 ready (17 boxes,13 missing IDs proposed);001/002/003/007 blocked on unknown focus for IDs6/9. No real confirmation/revision created by the agent |
| Integration | Verified on isolated/generated inputs |Actual Qt dialog cancel, explicit checkbox/name, jump-to-frame, stale preview, unsaved Save-cancel and software-test revision; rectangle/clipboard regressions and8-frame save/reopen with4 production crops pass |
| Model gate | Unassessed |No model inference, training, capture, export, promotion or admission-policy changes |

Evidence: `finish-ui-verified/finish-ui-verification.json` and visually inspected
`finish-dialog.png`; `finish-focused-tests.log`, `finish-python-tests.log`,
`finish-swift-build.log`, `finish-swift-test.log`; `finish-rectangle-regression`,
`finish-clipboard-regression`, `finish-roundtrip`. Reproduce the GUI test using
`scripts/verify_review_finish_ui.py <fresh-project-output>`; it creates synthetic
source fixtures and forces software-test revision provenance. The tests do not
touch the active Office batch or attest human labels. Source hashes are in
`finish-source-sha256.txt`.

Operator confirmed save/close; updated editor launched at frame001 via the existing
launcher (`editor-finish-live.log`). Next: operator uses Finish review, resolves
remaining focus exceptions, confirms ready frames, then revision-bound crop QA.
No TTR next-action change; shared coordination not applicable. All implementation,
integration, verification and documentation for this assigned follow-up are complete
for review; actual human attestation remains intentionally operator-owned.

## Follow-up: Select all and safe cross-frame paste

2026-09-28. Implemented in the pinned launcher, not vendor files. The operator's
visibility checkmarks were not shape selection; stock copy/paste lacked main
Edit-menu entries and reused clipboard objects on paste. Explicit Select all,
Copy and Paste now have main-menu actions, toolbar buttons and platform-native
shortcuts. Actual former operator failure cannot be reconstructed from a screenshot;
selection/shortcut exposure and object reuse are verified implementation findings.

Copy assigns missing positive local IDs without changing existing ones, marks the
source dirty and requires a normal save. Paste deep-copies, retains destination
image binding, rejects screen/dimension mismatches and ID collisions, and clears
pasted confirmation plus destination reviewed. Focus flags are proposals; existing
destination boxes and source confirmations are preserved. No autosave, no new pair
assignment, no model/native-label claim. The current editor/workspace was untouched;
operator save/close/relaunch was required for activation. The operator subsequently
confirmed saving and closing; the updated launcher was started at frame007
(`editor-clipboard-live.log`). Human testing of the new workflow remains pending.

Evidence (all under this directory):

- `clipboard-final/clipboard-verification.json`: real Qt SelectAll/Copy/Paste
  keyboard sequences, toolbar paste, missing-ID allocation, preserved IDs and
  existing boxes, independent repeated pastes, fresh confirmation and five warning
  paths (empty clipboard, collision, invalid IDs, wrong screen, wrong dimensions).
  Saved JSON parsed by the importer stays blocked pending human confirmation;
  close/new-window reopen preserves edited coordinates and flags; originals unchanged.
- `clipboard-final/clipboard-editor.png`: visually inspected software-test UI,
  not human annotation evidence. `verify_review_clipboard.py` reproduces this from
  `input-index.json` into a fresh output directory. The initial test-harness return
  type mismatch is retained in `clipboard-ui-check.log`; corrected runs pass.
- `clipboard-rectangle-regression`: actual two-click rectangle creation, forbidden
  modes and all8 loads pass. `clipboard-roundtrip`:8 saved/reopened,4 production crops.
- `clipboard-python-tests.log`:123 passed. `clipboard-swift-build.log`: success,
  no warnings. `clipboard-swift-test.log`:14 XCTest plus109 Swift Testing passed.

Outcomes: software verified; local editor/import/crop integration verified in
isolated copies; operator data review remains pending; model gate unassessed.
No TTR next-action change, so shared coordination is not applicable.

## Follow-up: visual labels and rectangle-only controls

2026-09-28 maintainer requested an illustrated label reference and rectangle-only
annotation. [Visual guide](visual-reference/LabelCheatSheet.html) contains all41
current editor labels; [quick sheet](visual-reference/QuickReference.png) covers
common tvOS decisions. [Source-backed rules](../../../Research/HumanReviewLabelGuide.md)
explain app tile=`collectionItem`, external caption=separate `label`, and why
`homeIndicator` does not mean Home-screen icon. Diagrams are schematic, never
native geometry or human-confirmed training annotations.

The pinned launcher now exposes Create rectangle (R), Edit rectangles (E), and
Control boxes. Polygon/circle/line/point/linestrip actions and shortcuts are hidden,
the drawing entrypoint rejects those modes, and polygon vertex removal is hidden.
Existing annotations are not rewritten; the user's current window was left alone.
**Save, close, then relaunch** to activate the revised controls.

Verification: `rectangle-ui-verified/rectangle-verification.json` exercises real
two-click canvas rectangle creation, visible toolbar captions, five forbidden
modes, and persistence across all8 image loads. `rectangle-roundtrip` rechecks
stock dialog/save/reopen plus4 production crops on an isolated re-import, not the
active user workspace.123 Python tests pass (`rectangle-python-tests.log`);
offline Swift build plus14 XCTest/109 Swift Testing tests pass (`rectangle-swift-*`).
The quick sheet and editor screenshot were visually inspected. HTML membership
is checked against the exact41-class map; browser preview of local file URLs was
blocked by browser policy and not bypassed, so browser layout is not claimed
verified. Local schematic PNG rendering is the inspected preview.

Software and local integration verified; human data confirmation still pending;
model gate unassessed; shared coordination not applicable. Runtime/content hashes
for this refinement are in `rectangle-reference-evidence.json`. Original handoff
and earlier runtime evidence below remain historical, not silently replaced.

## Original tranche handoff

2026-09-28. Owner: current NUIAK review-tool worker.
**Software ready for review; operator annotation session pending.** Maintainer
rejected Docker/CVAT; no container, server, database or second annotation app was
created. Scope is the eight retained frames, not new capture or training.

## Independent outcomes

| Outcome | State | Evidence |
| --- | --- | --- |
| Software | Verified | Import/validate/finish/crop CLI, pinned stock Labelme launcher,27 new adversarial tests plus96 legacy tests; all123 pass |
| Data | Raw intake verified; human bounds/class/state confirmation pending |8/8 originals imported,8 distinct pixel hashes,0 blocked intake rows;4 Photos control proposals and2 explicit pair candidates;0 accepted human labels |
| Integration | Local stock-editor round trip and production crop path verified | All8 loaded/saved/closed/reopened; real checkbox-dialog edits; fractional box edits survive;4/4 production crops; working review copy unchanged |
| Model gate | Not assessed | No training, model inference, export, promotion, threshold or admission-policy changes |

The worker-execution skill's completion contract required the installed editor
round trip and real production crop check, not just schema/unit tests. Human
approval cannot be manufactured by those tests. HR1.6 remains pending until the
maintainer reviews the actual Photos controls; it does not block this handoff.

## Acceptance mapping

| Criterion | Actual evidence |
| --- | --- |
| HR1.1 isolated local runtime | Python3.12, Labelme5.2.1, PyQt5.15.11/Qt5.15.19, NumPy1.26.4; full dependency pins in `scripts/requirements-human-review.txt`; install logs and `runtime-evidence.json` |
| HR1.2 start/close/reopen | Stock MainWindow8-frame membership verified, project-local INI settings, saved JSON reopened in a new window; no service or listener |
| HR1.3 frozen intake | `input-index.json`, `office-batch/batch.json`, `office-batch/raw/`; exact inline PNG/receipt identity, target/session/generation/timeline checks, every row accounted for, idempotent import |
| HR1.4 editable review | `editor-dialog-verified/verification.json`, window and dialog PNGs; stock rectangles, classes, Group IDs and focus/review flags; numbered editor entries and static full-frame sheets |
| HR1.5 exact round trip/crops | Unchanged coordinates identical; first box shifted0.25px/0.5px and focus edited through checkbox dialog in isolated software-test copy;4/4 crops via `FocusRingClassifier.makeCrop`,16%/256×256; originals unchanged |
| HR1.6 human handoff | [Start / Review / Finish](OperatorGuide.md); untouched user workspace `office-batch/editor/`; actual human confirmation and reviewed revision pending |

The numbered sheets and paired previews supplement the editor, not another
annotation interface. Proposal boxes are manually assessed and explicitly marked
as proposals. Existing chat state confirmations do not confirm geometry/class.
Six non-Photos frames deliberately have no speculative boxes; they remain
available for review and blocked from accepted control labels.

## Verification

- `focused-tests.log`:27 new generated-fixture tests pass, including missing/corrupt
  images, changed bytes/binding/index, wrong target/generation/inline pixels/time,
  duplicate pixels/membership, native-unresolved evidence, unknown/conflicting
  states, invalid geometry, deleted controls, interrupted output, explicit finish,
  unsupported/final-challenge/training-role rejection, actual CLI/crop integration,
  and incomplete crop accounting.
- `legacy-and-focused-tests.log`:123 tests pass (`test_human_annotation_review`,
  `test_photos_focus_pilot`, `test_focus_retained_review`, `test_native_os_focus_dataset`,
  `test_focus_surface_evaluation`, `test_focus_appearance_experiment`,
  `test_focus_visual_comparison`, `test_focus_runtime_batching`).
- `editor-dialog-verified.log`: installed stock Qt window/checkbox dialog,8
  load/save/reopen checks and4 crops pass. Explicitly `software-test`, never human.
  Geometry edit exercises the stock shape/save path; a human drag/review session
  has not been claimed. `editor-roundtrip*` are earlier successful serialization
  passes; `editor-dialog-roundtrip` retains the first failed simulated checkbox hit.
- `proposal-crops/crop-qa.json`:4/4 proposal crops,2 paired previews, pinned production
  helper/source/runtime. No inference argument is supplied.
- `swift-build.log`: offline build succeeds, zero warnings.
- `swift-test.log`:14 XCTest plus109 Swift Testing tests pass,123 total.
- `git diff --check`: passes. No Swift/public API/taxonomy/evaluator changes.
- Dedicated runtime `pip check`: no broken requirements. Native Cocoa editor
  launched with `--frame frame-004`; foreground process remains running without
  startup errors (`editor-live.log`). This is the human review window, intentionally
  left open; close that window normally after saving. Visible operator interaction
  has not yet been confirmed.

Python runs set `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=scripts`, project-local
TMPDIR. Swift build/test used `--disable-automatic-resolution --manifest-cache local`
and cache/config/security/module-cache/TMPDIR under `.build/human-review/`, in the
established host execution context. No package resolution or device requirement.

Repeat the actual editor integration independently with a fresh output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 reports/work/HUMAN-REVIEW-01/runtime/venv/bin/python \
  scripts/verify_human_review_editor.py \
  reports/work/HUMAN-REVIEW-01/office-batch/batch.json \
  reports/work/HUMAN-REVIEW-01/editor-verification-new
```

## Evidence limitations and next action

Input timeline has9 commands but8 captures. Right/Up/Select before Settings has
uncaptured intermediate states; the importer explicitly records that transition
gap. No input intent is converted into a focus label. No native focus observations
or OCR receipt were added. Repeated Home/boundary states do not establish source
independence. Full-frame candidate coverage remains unknown, so no unique-selection
accuracy claim or training eligibility follows.

Next: maintainer reviews Photos004/005 in the local window, then explicit Finish
and revision-bound crop QA. Unknown/flagged/rejected examples stay excluded. Later
HUMAN-REVIEW-02–04 remain separately assigned: defect triage, exact TTR recorder
bundle integration, and a human-label admission policy. This tranche changes no
TTR producer contract; shared coordination is **not applicable**.

## Runtime setup findings

- Initial restricted pip download failed DNS; scoped host download succeeded.
- `.venv-review` installed but Qt5.15.19 treats its plugins as hidden, confirmed
  both restricted and host-side. No permission weakening solved or was used for it.
  Correct runtime is the non-hidden ignored `runtime/venv`; old ignored environment
  is retained (~292MiB) but unused. Total two envs ~584MiB; no storage pressure.
- Bare Labelme writes `~/.labelmerc` despite `--config`; our launcher supplies the
  stock bundled configuration directly. macOS organization/app QSettings ignored
  default INI settings, so the pinned constructor receives an explicit project INI
  object. No HOME override, vendor patch, system settings or certificate change.
- The selected classic editor has no AI downloads or inference imports in this
  path. Help can open external documentation if explicitly clicked; screenshots
  are not uploaded. No network service runs. This is a local-only tested pin, not
  a security qualification of old Labelme for arbitrary/untrusted projects.
