# HUMAN-REVIEW-02 — reviewed Office batch audited

2026-09-28. Assigned continuation completed for review: actual HR1 crop QA and
HR2 deterministic audit/queues/coverage decision on the eight retained frames.

| Outcome | Result |
| --- | --- |
| Software | Verified:9 generated-fixture audit tests,145 total Python tests, offline Swift build and14 XCTest +109 Swift Testing tests pass |
| Data |113 human-reviewed controls on8 frames;2 explicit Photos pairs;113/113 production crops. Still diagnostic-only, not admitted to training/evaluation |
| Integration | Real immutable human revision → production cropper → validated audit → numbered sheets/queues. Generated CLI → correction → new revision → revalidation passes |
| Model gate | Not assessed; no inference, training, export, promotion, capture or device operation |

## Findings

| Screen context | Frames | Controls | Focused / unfocused |
| --- | ---: | ---: | ---: |
| Home |4|96|4 /92|
| Photos Welcome |3|6|3 /3|
| Settings |1|11|1 /10|
| Total |8|113|8 /105|

Zero hard integrity/label-conflict issues.111 distinct crop pixel hashes; two
duplicate groups: Home002/007 local controls20 and23. No exact full-frame pixel
duplicates. Four near-frame heuristic matches:001/003,001/007,003/007,005/006.
All remain preserved; no automatic deduplication or inflated source count.
One physical device/session and three screen contexts do not prove three
independent source groups. Appearance attributes and active reviewer time unknown.

All113 crops were visually inspected in eight sheets, plus full context for Photos
005/006 and Settings008. These are agent QA observations, not new human labels:

- Photos004/005 show the expected opposing white/gray button focus states; both
  explicit pairs remain reviewed. Four original box proposals were retained exactly
  after human review; the other109 controls were newly annotated.
- Photos006 repeats the visible005 focus state but has separately drawn, slightly
  larger boxes. Its crops include neighboring button edges. It is useful no-op
  context, not a third independent Photos example; no correction is required solely
  because the boxes differ. It is not silently added to either explicit pair.
- Home shows Photos focused in001/003/007 and Music in002. Blank white app artwork
  is retained as captured, not filled in or classified from guesses.
- General is the focused Settings row; its ten competitors are unfocused.
-67/113 expanded crops intersect another annotated control's bounds. Context is
  intentional under production preprocessing and supplies adjacent-focus negatives;
  it is not automatically a crop defect. Wide buttons/rows stretch into squares
  under the established cropper. No alternative resize/crop policy was introduced.

An always-unfocused classifier would score105/113 =92.9% accuracy here. A future
comparison must emphasize positive recall, false positives and paired outcomes,
not headline accuracy. No actual model performance was measured in this tranche.

## Reproducible evidence

- [Frozen input index](input-index.md): receipt/revision/crop/audit hashes and runtime.
- [Static review queue](joe-final-20260928/review.html): frame context and crop sheets.
- `joe-final-20260928/audit.json`: every frame/control, crop membership, duplicate
  groups, proposal geometry deltas, neighbor counts, exact issues and limitations.
- Random queue: seed42, one frame per screen; Home001 (1/4), Photos004 (1/3),
  Settings008 (1/1). Denominators retained. Not a random independent population
  sample or a confidence interval. Targeted queue is separate: four heuristic
  matches plus two informational duplicate groups.
- `audit-focused-tests.log`, `python-tests.log`, `swift-build.log`, `swift-test.log`.
  The new tests use generated sources, not the ignored Office evidence. They cover
  changed/missing media, crop membership, snapshot/semantic tampering, wrong roles,
  duplicate-label conflict, wrong pair binding and an actual correction round trip.
  Existing tests cover invalid classes/geometry/IDs, native disagreement and pending
  labels through the reused validator. Source hashes: `source-sha256.txt`.

Run `scripts/human_review_audit.py <revision.json> <crop-qa.json> <new-output>` in
the existing review environment. It never loads models, edits labels or silently
reduces membership. Missing/invalid core inputs produce `failure.json`, not a partial
success report. Hard detected issues remain accounted in a completed diagnostic
report; a report existing does not itself make data eligible.

The static HTML was membership/link checked, not interactively browser-tested
(prior local-file browser policy remains respected). Rendered PNGs were inspected.
Correction uses the existing editor's exact batch and `--frame` ID, followed by
Finish review and a new crop/audit output. Immutable revisions are never edited.

## Decision and remaining boundary

Recommend keeping this entire correlated batch as a **development regression set**,
not training, and collecting separate training groups. See the
[proposed admission/comparison decision](../../../Research/Plans/HumanFocusAdmissionDecision.md)
and [prioritized collection assignment](collection-assignment.md).

Current manifests stay trainingEligible=false and independentEvaluationEligible=false.
Complete-frame candidate coverage remains unknown in v1; no unique-selection
accuracy, detector recall, independent qualification or navigation claim. Cross-
corpus source/role leakage is explicitly not assessed: no external role inventory
was assigned, and no new role has been granted. That audit precedes admission.

Human input is now needed to approve the proposed development-evaluation lane and
one fixed-model comparison. No more annotation clicks are requested for this batch.
Shared coordination is not applicable: no new finding changes TTR's next action.
All independent crop/audit work is complete; model execution/admission remain
deliberately unperformed, not hidden completion claims.
