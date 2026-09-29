# Experimental click-to-box and numeric boundary repair

## Duplicate-preview follow-up

Labelme paintEvent draws both current and line. Suggestion assigned current but
left the previous manual rectangle in line, causing a second green preview.
Reset only that transient guide before repaint; saved annotations are untouched.
Regression seeds a stale rectangle, exercises actual canvas painting in the modal
preview, then checks Cancel adds zero shapes and Accept exactly one.16 Qt tests
and required offline Swift build/test pass. Logs:
.build/human-review/suggestion-guide-{qt,build,test}.log.
Software verified; running window restart awaits save/close. Data unchanged;
model unassessed; shared coordination not applicable.

## Last-label follow-up

Auto-select now reuses the last accepted label from suggestions, manual drawing
or editing; Enter accepts it. Cancel restores the previous label default. Focus,
confirmation and notes are not inherited.15 actual Qt interaction tests pass,
including sequential suggestions, Enter, cancellation and focused/confirmed reset.
Offline Swift build and123 tests pass. Logs:
.build/human-review/last-label-{qt,build-local,swift-test}.log.
Initial default-cache build was denied; rerun used scoped approval/project-local
caches. Annotations unchanged; running editor awaits human save/close to restart.
Software verified; data unchanged; model unassessed; no TTR consequence to publish.

Software:44 Python tests and14 actual offscreen Qt tests pass; offline Swift
build/test pass. Tests cover flat rounded panels, blank/clipped/circular abstention,
invalid clicks, toggle-off behavior, cancel, no-result, proposal creation and manual
mode fallback. No vendor edits/dependency installations/model inference.

Integration: toolbar/Edit menu `Suggest box (experimental)` defaults off on every
launch. Enable, click plain control interior, inspect preview, pick label and OK.
Cancel changes nothing; accepted rectangles are unconfirmed and use fresh local IDs.
Explicit human Focused checkbox selection is honored, default unfocused. Turn off
to drag corners; Create rectangle automatically disables suggestion mode. The
feature never changes existing labels or approvals; current window needs restart.

Algorithm: bounded640px color-region segmentation with fill/size/four-edge checks.
No confidence calibration or semantic recognition. Flat panels are the target;
text/artwork/gradients, invisible boundaries and clipped shapes can fail or abstain.
Conservative abstention does not prove a proposed box correct. No promotion claim.

Retained diagnostic probe, using a plain interior point of4 reviewed positive boxes:
recorded-303,319,416 yielded proposals in47,49,44ms respectively; recorded-656
tab pill abstained in28ms. Coordinates differ from reviewed boxes and still require
human adjustment. This is a small selected probe, not a success-rate benchmark.
Promotion requires broader measured proposal acceptance, edit distance and reviewer
time versus manual/preset workflows on tiles/rows/tabs/negatives.

Boundary repair: diagnostic parsing snaps only <=1e-7-pixel excursions to image
edges; real out-of-bounds rectangles still fail. No original editor/snapshot rewrite.
Actual batch02 read-only Finish preview now8/8 ready; user must explicitly finish
again into a new immutable revision before whole-batch crop QA/audit. Existing
7-frame revision remains unchanged. Model/data admission unchanged.

Logs: .build/human-review/click-box-{python,qt,build,test}.log.
Software verified; human data not newly approved; GUI reopen pending user save/close;
model gate unassessed. Shared coordination not applicable, no TTR next-action change.
