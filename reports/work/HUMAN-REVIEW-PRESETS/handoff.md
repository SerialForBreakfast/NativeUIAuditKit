# Rectangle presets

## Binary Finish review correction

Finish preview now proposes unfocused=true for unchecked Focused (legacy both-false
flags). Explicit human confirmation is still required before writes, with backups.
Conflicts/flagged items remain blocked; raw legacy parser remains unchanged.
Actual saved eight-frame batch read-only preview:8 ready,0 issues; no human files
changed or completion claimed.59 Python tests,11 Qt tests and offline Swift
build/test pass. Logs: .build/human-review/binary-finish-{qt,build,test}.log.
User editor restart pending save/close; local only, no data/model admission change.

## Focus list indicator follow-up

Explicit FOCUSED/unfocused/unknown/conflict/excluded markers accompany each
control. All active focused controls pin first; dock title counts them and warns
on multiple focus without changing annotations. Multiple-focus qualification still
requires adjudication; recording it remains possible. Drag-reordering disabled;
canvas stacking, saved shape order and selection preserved by tested presentation
sorting.11 Qt tests and offline Swift build/test passed. Logs:
.build/human-review/focus-list-{qt,build,test}.log. User restart awaits save/close.
Software verified; no data admission/model gate change. Local-only coordination.

## Single-focus dialog follow-up

Only `focused` is visible for focus state; explicit OK saves `unfocused` as its
inverse. Opening/canceling never relabels stored proposals. Other review flags stay
separate. Enter/Return accepts from label, list, group ID, description and checkbox;
invalid taxonomy labels cannot be accepted. Description placeholder says optional.
Eight actual Qt tests pass, including new keyboard/default/cancel cases. Offline
Swift build/test pass (focus-dialog logs under .build/human-review). Existing
annotation and Finish review tests also pass. Current user window is not forcibly
closed; save/close/reopen is needed. No annotation migration, device or model work.

Software: six actual offscreen Qt tests pass, covering persistent save/load,
approval stripping, fresh IDs, incompatible dimensions, invalid presets and
existing interactions. Offline Swift build/test pass; logs in
`.build/human-review/presets-build.log` and `presets-test.log`.
Data: no human annotations changed. Model gate: not assessed.
Integration: toolbar/Edit-menu controls tested; running user window must be
saved/closed/reopened to load the new code. Coordination: local only, not applicable.

Select rectangles (or deselect all to save the entire screen), choose Save preset,
and name it Home grid or Settings navigation. Load preset adds unconfirmed boxes;
check geometry and set focus states. Original boxes remain intact. Normally load
once on an empty image; repeated loading adds boxes. Different image dimensions
are rejected; same-size layouts still need human checking. No guessed built-in
coordinates. Revise presets under new names; existing names cannot be overwritten.
Presets persist across batches under the gitignored project-local directory
`reports/work/HUMAN-REVIEW-01/rectangle-presets/`.

Contract: Research/Plans/RectanglePresets.md. Changes: human_review_presets.py,
human_review_editor.py and test_human_review_editor_interactions.py. Prior dirty
work preserved. Next: reopen after operator saves/closes, then save actual layouts.
