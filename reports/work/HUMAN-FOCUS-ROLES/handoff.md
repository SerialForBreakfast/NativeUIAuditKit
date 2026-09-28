# Focus-only annotation roles

| Outcome | Evidence |
|---|---|
| Software verified |77 Python tests,9 actual offscreen Qt tests, offline Swift build/test pass |
| Data eligible |No admission change; original user annotations untouched |
| Integration qualified |Generated editor→revision/completeness→production crop→audit path passes; user saved/closed, actual batch reopened at recorded-656 |
| Model gate passed |Not assessed; no model run, export or training |

User-requested gap addressed: choose `focus:tabItem` for each tab destination;
`focus:otherFocusable` for an accurately observed focusable control without a
matching class. No taxonomy IDs added or renamed. Version2 revisions store role
separately with null detector class; legacy revisions remain v1. New-role presets
are version2; legacy presets remain readable. Original source images/annotations
are not migrated. No extra per-box mapping form or required description.

Acceptance evidence in test_human_focus_roles.py includes real production crops,
Finish-review integration, complete-frame receipts, role-based coverage, legacy
compatibility, role mismatch, unsettled blocking, invalid mappings, preset
persistence and explicit training/evaluation rejection. Qt test verifies selecting
the new label, accepting with Enter and saving/reloading the rectangle. Existing
model-evaluation tests use test doubles; no actual model inference was launched.
Swift logs: .build/human-review/focus-roles-build.log and focus-roles-test.log.

User confirmed saved/closed. Reopened existing office-trial-02/review-batch/batch.json
at App Store frame recorded-656 with the new roles; process remained running without error.
No new capture or repeated annotation required. Software ready for review; user
annotation and separately approved model admission remain follow-ups. Shared
coordination not applicable: this is a local annotation issue, no TTR action change.
