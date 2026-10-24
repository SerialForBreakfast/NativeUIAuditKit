# Matched detector and focus repairs

Owner: Maximum-mini-NUIAK. Date: October 24, 2026.

## Decisions from completed work

The active USB checkout passes a write check. The mounted drive has about 1,600 GiB free.
The review verifies retained output hashes before using results.
Evidence lives in `reports/work/MATCHED499/review.json` and `coverage-review.json`.

| Comparison | Measured result | Decision |
|---|---|---|
| IOS494 original-only frozen fit against Run013 | 25 gained detections; 22 lost successes across 2,030 labels | Reject replacement. Original-only retraining also causes drift. |
| NATIVE494 frozen fit against matched full training | 24 lost Standard known-box successes across 72 observations | Reject replacement. Freezing does not preserve this capability. |
| TEACHER496 against retained Standard | 6 gained known-box successes; 6 previous consumer negatives become false positives | Reject replacement. Teacher preservation does not solve consumer retention. |
| COVERAGE498 iOS confidence 0.25 versus 0.5 | 14 recovered labels; 0 lost successes across 2,030 labels | Keep as a diagnostic candidate. Unmatched predictions require separate review. |
| COVERAGE498 tvOS confidence 0.25 versus 0.5 | 5 recovered buttons and 1 row; 0 lost successes | Lower confidence alone leaves substantial proposal gaps. |

Counts from separate input types are not independent trials. Do not combine crops, frames, and related profiles into one accuracy percentage.
Incomplete detector labels prevent precision claims from unmatched predictions.

At confidence 0.25, the scoped detector supports 10 correct Standard selections across 24 native observations.
Both completed crop models have this result. Known boxes produce 24 correct selections.
The native groups contain 8 button, 8 row, and 8 tab observations.
Rows produce 2 wrong selections. This separates proposal problems from the known-box crop result.

PROPOSAL497 uses the scoped DETECTOR422 checkpoint. Earlier text calls these general-detector boxes.
That description is incorrect. MATCHED499 compares the general tvOS checkpoint against the scoped checkpoint directly.

## Three controlled questions

The batch has 26 jobs. These jobs answer 3 questions, rather than 26 independent scientific questions.
The existing compiler and detached runner own registration and execution.
No execution module changes are needed.

1. **tvOS proposals:** Does the general detector recover bodies that the scoped detector misses?
   Eight T56 jobs change only weights. Eight T42 jobs separate geometry from class assignment.
   Keep images, labels, confidence 0.25, resolution 1280, NMS 0.45, and development groups fixed.
   Compare class-aware results with class-agnostic overlap at IoU 0.5.
2. **iOS data effect:** Does native-data adaptation damage localization or class assignment?
   Six T42 jobs compare cached frozen mixed-data and frozen original-only predictions.
   Keep confidence 0.5, labels, groups, and prediction bytes fixed.
   Compare these geometry results with the completed class-aware IOS494 comparisons.
3. **Focus selection:** Does changing the proposal detector improve native focus selection?
   Three T57 jobs hold both crop models, thresholds, mapping, and captures fixed.
   One T58 report groups buttons, rows, and tabs. Compare each model with its COVERAGE498 counterpart.
   Standard results lead the decision. HCF remains a separate optional profile.

All 26 descriptions are registered and approved. Descriptions and pinned inputs: `reports/work/MATCHED499/batch.json`.
Registration receipts: `reports/work/MATCHED499/registered.json`.
Approval receipts: `reports/work/MATCHED499/admission.json`.
Admission uses cycles of 9, 9, and 8 jobs. Existing jobs and specifications remain intact.
The handoff snapshot verifies all 26 approvals: 3 complete, 13 pending, and 10 waiting on dependencies.
No new job has exhausted its attempt. Completion still requires scientific review.
The snapshot is saved in `reports/work/MATCHED499/handoff-snapshot.json`.

## Result rules and prepared repairs

| Result | Next action | Required input and owner |
|---|---|---|
| General detector improves focused-body coverage without lost successes | Prepare a bounded integration comparison using that detector | Maximum-mini-NUIAK verifies per-frame focus outcomes and the retained consumer suite. |
| General detector adds losses | Identify the exact lost bodies before selecting a detector | Maximum-mini-NUIAK uses cached geometry and class results. |
| Both detectors miss bodies | Prepare targeted detector training for the missing families | Maximum-mini-NUIAK supplies complete training-only labels and preserved development exclusions. |
| Geometry passes but classes fail | Prepare a class repair with fixed geometry and membership | Maximum-mini-NUIAK identifies confused classes and sufficient training examples. |
| iOS geometry also regresses | Address localization drift before another class-focused fit | Maximum-mini-NUIAK supplies the lost-box list and a justified changed factor. |
| iOS geometry survives while class-aware results regress | Prepare class-preservation training | Maximum-mini-NUIAK pins training-only anchors for the affected classes. |
| Proposal coverage improves but focus selection does not | Inspect competing crop scores and actual proposal crops | Maximum-mini-NUIAK uses the fixed-model T57 results. |
| Evidence remains inconclusive | Keep current models and request only the missing evidence | The task names the missing group, label, or consumer result before another run. |

Any replacement must preserve previous successes and avoid new wrong Standard selections.
Training must use training-only groups. Development images remain excluded.
The scoped native-control labels do not establish exhaustive general UI annotations.
Do not repeat the rejected frozen or teacher fits with unchanged membership and settings.

The next justified fit uses the qualified T89 path and a matched control.
Record the changed factor, membership, initialization, fixed 30 epochs, and storage limit before admission.
Reuse completed controls only when membership and settings match.
Use the retained iOS 6-group suite and the tvOS native, hard-case, no-focus, and consumer suites as applicable.
Checkpoint restoration remains a separate qualification requirement.

## Training qualification and runtime

All 36 focused tests pass in 27.302 s through the resident unittest runner.
The environment lacks pytest. The suites use unittest and need no dependency installation.
Verified fits complete in 192.6 s for DETECTOR422, 689.5 s for IOS493, and 698.6 s for IOS494.
These timings qualify observed execution, not model acceptance.

The 26 diagnostic jobs each retain the 800 s and 100 MB ceilings.
The aggregate ceiling is 20,800 s and 2.6 GB. This is a reservation, not a duration estimate.
Prior 14 inference jobs total 60.5 s. Plan approximately 5–15 min for this diagnostic graph, excluding admission and contention.
This queue does not represent an overnight training workload.

## Independent Fixture finding

Retained recovery completes with verified cleanup and preserved failed evidence.
The first session comparison then fails during label import with `artwork_geometry_fields`.
The captured sidecars add a `presentation` object. The legacy validator accepts only nominal artwork fields.
The inspected after-sidecars contain 52 such objects. This is an import compatibility failure, not evidence of incorrect annotations.
Preserve exported images and the failed attempt. Repair import against the current producer contract before any replacement capture.
The remaining 3 session comparisons depend on this failure. Maximum-mini-NUIAK owns the compatibility repair.
Any shared execution change requires tests and activation at an idle boundary.

## Coordination

The review reads TTR messages through cursor 1316.
TTR reports SDK setup, layout inspection, and UIKit checks. Those changes remain uncommitted.
The reported callback p95 of 0.226 ms exceeds its 0.2 ms target.
User-selected sidecars remain unaligned evidence. They cannot supply automatic screenshot annotations.
These findings do not block the retained detector and focus graph.
The coordinator stores the feedback as request `nuiak-matched499-sdk-review-20261024-v1` at cursor 1317.
Readback confirms storage. Forwarding and recipient acknowledgment remain unconfirmed.
