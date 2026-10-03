# Reference45 — new layouts expose a specific focus-ranking failure

Update October2: maintainer approved all12review samples without corrections
(“They were perfect.”). [Bound confirmation](human-sample-approval.json).
Sample review is complete; role assignment remains separate. Pending-review wording
below describes the original benchmark execution, not current sample-review status.

The fixed full-screen candidate has not transferred to these reference layouts.
We now have a concrete next experiment, working grouped review, and executable native
coverage plans rather than another unchanged fit.

## Measured results

72source frames reduce to61distinct decoded images. Native annotations remain
provisional while human review is open; both families retain calibration roles.

| Measure | FSF001 full-screen | Shipped detector/focus |
|---|---:|---:|
| Focused body localized, IoU≥.50 | 0/61 | 13/61 |
| Focused body localized, IoU≥.70 | 0/61 | 2/61 |
| Focused body localized, IoU≥.90 | 0/61 | 1/61 |
| Selected boxes matching known unfocused controls | 73 | 2 |
| Selected boxes with unreviewed geometry | 37 | 39 |

Those last two rows count predictions, not frames. Unmatched predictions are not
automatically false positives on these partial visible inventories. Distinct known
control localization is72/398vs65/398, regardless of focus. Source-entry-weighted
focused-body recall is0/72vs15/72. Different architectures/thresholds make this a
fixed-system diagnostic, not an isolated architecture experiment or real-app benchmark.

**Root-cause narrowing:** visually inspected catalog predictions often cover a
roughly square upper patch of a tall card. Full-card geometry therefore matters.
But a relaxed diagnostic associates candidates with a known body when≥80%of the
prediction lies inside exactly that body. This finds a focused-card candidate in
all30catalog images at the retained.001floor; only4are above the fixed.25operating
threshold, and28/30score a known unfocused card higher. Thus geometry alone cannot
explain the failure. Guide31images have no contained focused candidates at that floor.
Containment is diagnostic only; annotations, thresholds and scoring remain unchanged.
It does not establish which learned visual feature caused the wrong ranking.

## Completed implementation and companion work

- Removed transitive OpenCV evaluation imports from the real annotation-validation
  path. A review-interpreter regression test blocks model/analysis imports explicitly.
  The annotator launched with all12prefilled images in one queue; human edits remain
  separate from the immutable native-label benchmark.
- Added frozen model/input/runtime protocol, decoded-image deduplication with label
  conflict rejection, retained predictions, strict replay and interrupted-run resume.
- Verified six native UIButton recipe cases spanning3×3buttons,3vertical row-styled
  buttons and3horizontal tab-styled buttons across dark/light backgrounds:30target
  intentions. ID mapping follows producer ceil(sqrt(count)), not visual canvas columns.
- Current TTR helper validated the exact manifest and planned eight grid-density cases.
  All states remain unattempted. Native labels/actual spatial coverage require captures.
  Rows/tabs here are styled UIButton, not UITableViewCell/UITabBar; grid planning
  targets one interior control per case and does not itself solve position coverage.
- Exact membership choices preserve aliases, all61pixel hashes, source-family grouping
  and shared renderer ancestry. Recommendation: retain both families as a development
  challenge. Alternative all61training use requires explicit assignment and fresh
  held-out families; current diagnostics already informed development.

Source: Developer/TVTestRig87e59be5; matching helper SHA81be8412…f54b. This is on-disk
source/helper verification, not loaded-image attestation. Old source-absence notes in
Tasks33/37are corrected; capture/export qualification remains separate.

## Verification and operational incident

- 28reference/diagnostic tests,84fixture tests and14transition tests pass:126total.
  Earlier direct benchmark/import runs also passed, but are not added to this count.
- Offline Swift build and14XCTest+120SwiftTesting checks pass.
- Complete benchmark replay matches retained results. Per-image times sum6.2704s
  candidate and28.5556s production, excluding initialization/validation.
- Initial inference was stopped after Ultralytics created a fallback /tmp settings
  cache. The configured project parent was absent. Cache precreation/writeability
  checks now precede import, with regression coverage.29complete prediction pairs
  were reused; PID77862generated32remaining pairs in18.2346s. That resumed wall time
  is not the total experiment duration. Initial warning/interrupt evidence is retained;
  no external cleanup was attempted.
- Initial annotator failure and its fix are recorded separately from model performance.

## Evidence

- [Fixed benchmark](benchmark/scorecard.json), [protocol](benchmark/protocol.json),
  [containment diagnosis](containment.json), [replay](replay.log)
- [Exact membership choices](membership-options.json)
- [Native manifest](planner/native-manifest.json), [native validation](planner/native-response.json),
  [grid plan](planner/grid-response.json), [source qualification](planner/verified-source.json)
- [Grouped review instructions](../REFERENCE-IMPORT-44/ReviewGuide.md)

## Next substantial tranche

1. Finish the single12-image review and record corrections/approval; retain source
   calibration unless the maintainer explicitly assigns training membership.
2. Repair/resume export of the already captured smoke data, then qualify the planned
   native spatial sweep. Add varied tall/wide artwork geometry and matched-content
   focused/unfocused contrasts; actual native Settings/tab widgets remain producer work.
3. Run a defined data comparison using approved grouped training membership, fixed
   existing synthetic/real challenges and newly held-out renderer/layout families.
   Measure wrong-control ranking and body localization separately. This is the next
   justified fit; extending the unchanged dataset is not supported by these results.

Blockers are specific: human review/data-use decision for admission; producer writer
repair for retained smoke export; native widget coverage beyond styled buttons.
