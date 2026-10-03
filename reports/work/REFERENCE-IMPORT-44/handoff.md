# REFERENCE-IMPORT-44 — importer and review ready

## Completed

- Added closed referencePack v1/v2 recipe identity, including pinned upstream
  revisions and Swift canonical viewport formatting; retained legacy hash behavior.
- Validated reference planned controls against visible records plus explicit
  clipped/offscreen exclusions. Semantic anchor focusability is kept separate from
  the observed native focus inventory. Navigation keeps initial request and observed
  result separate; unknown modes still fail. Both ancestry fields are retained.
- Integrated reference delivery through the existing batch-review entrypoint,
  production cropper and grouped annotation queue. Intake appends accepted sources
  only after their required contract fields validate.
- All36accepted cases validate:12appearance,12scroll_moved,12scroll_unchanged.
  72PNG entries have66byte-distinct encodings and61distinct decoded images.
  All468visible-control crops passed production16%/256x256 QA. Explicit producer
  exclusions account for1,476planned control observations across frames; that is
  different from the producer's72missing/clipped comparison windows.
- One12-image random review, seed42, covers both families and all3conditions;
  all12selected images have distinct pixels. No additional exception images were
  added just for expected calibration/partial-inventory notices.
- Companion executable `reference_diversity44.py` pins candidate membership,
  original2,000training/500evaluation membership and unchanged model/configuration.
  It reports positional coverage, duplicate groups, common controls and growth,
  and explicit prerequisites for a data-addition comparison.

## Actionable findings

Catalog native focused bodies have median area ratio1.2279 (~23%larger,12observed
focus-changing common-control comparisons). Guide rows have ratio1.0 (24comparisons):
custom highlighting, not native image growth. This verifies geometry variation,
not model recognition of the effect.

All36catalog focused screenshots fall in the middle/middle position bin; guide
has30middle/middle and6top/middle. No bottom or side coverage. These data cannot
by themselves address the prior full-screen model's position failure. Both families
retain shared Fixture renderer ancestry; variants/seeds are not independent tests.
Source taxonomy is primaryButton for both families; preserve it pending explicit
detector-role mapping. Native Settings, native tabs and dialog-button coverage remain.

## Evidence and verification

- [Accepted batch and all468crops](review-final/report.json)
- [Review instructions](ReviewGuide.md)
- [Coverage and fixed-comparison preflight](diversity-final.json)
- Python:84fixture tests,10legacy sidecar,14transition,7integrity,41harvest and5diversity
  tests passed (161test executions across suites; generated fixtures are software evidence).
- Offline Swift build passed;14XCTest+120SwiftTesting checks passed.
- Native Qt startup doctor passed with desktop access. Restricted probe could not
  connect to macOS UI services; isolated failure and host-success receipts retained.
- Inspected representative guide/catalog overlays; human sample approval remains open.
- Earlier `review/` attempt contains successful crops but an intake summary rejected
  a missing adapter coverage field. Use `review-final/`; the adapter and append order
  are corrected. Earlier evidence is retained, not a second review assignment.

Outcomes: software verified; reference36diagnostic integration qualified; training
admission pending human review/data-role decision; model improvement not assessed.

## Next substantial tranche

1. Complete the single12-image review and designate exact source-family training and
   new-family development membership. Preserve the existing500evaluation images.
2. Qualify native Settings/tab/dialog renderers and distribute focused positions
   across top/middle/bottom and left/center/right, with ordinary appearance captures.
3. Execute the approved fixed-model data comparison, report synthetic and retained
   real-screen changes separately, and investigate specific failures before scaling.

TTR43retained smoke export remains a separate producer writer failure. The earlier
request is still open; this tranche imports the already delivered archive.
