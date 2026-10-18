# REVIEW426 — matched detector and crop findings

Owner: Maximum-mini-NUIAK. Date: 2026-10-18.

Standard remains primary. HCF stays optional. No model passes replacement gates in this review.
Case-linked detector evidence is in `reports/work/REVIEW426/detector-matched.json`.
Completed output hashes and matched frame identities are verified before comparison.

## Detector comparison

Hold the low-dose crop classifier, frames, thresholds, and preprocessing fixed. Change only the proposal detector.
These are development frames. Related profiles and repeated layouts are not independent trials.

| Condition | Standard correct selections, old → new | HCF correct selections, old → new | Important outcome |
| --- | --- | --- | --- |
| Buttons | 8/8 → 8/8 | 8/8 → 8/8 | Better boxes do not add selection gains here. |
| Rows | 3/8 → 8/8 | 3/8 → 8/8 | Recover 5 selections per profile without losses. |
| Tabs | 8/8 → 8/8 | 8/8 → 8/8 | All 32 geometrically matched tab labels receive the wrong class. |
| Diamond decoration | 4/4 → 4/4 | 0/4 → 0/4 | Add 2 wrong HCF selections. |
| Edge clearance | 4/4 → 1/4 | 0/4 → 0/4 | Lose 3 Standard successes. |
| Small decoration | 3/4 → 3/4 | 0/4 → 0/4 | Add 3 wrong HCF selections. |
| Tall controls | 3/4 → 0/4 | 0/4 → 0/4 | Lose 3 Standard successes. |
| No focus | 3/3 correct abstentions remain | 3/3 correct abstentions remain | This small set does not establish general no-focus safety. |

Class-agnostic matched boxes improve from 14 to 32 of 32 button labels, and 19 to 29 of 32 row labels.
Tab box matches improve from 25 to 32 of 32, but the candidate calls all 32 `primaryButton`, not `menuButton`.
Do not treat this geometry result as classification accuracy. Unmatched predictions are not reviewed false positives.
The candidate loses Standard coverage outside its narrow native training scope. Reject it as a general detector replacement.

## Crop comparison

The generic-jitter fit completes all 17 scoring jobs. Its measured-box counterpart still trains at this review.
Fifteen T37 conditions use identical boxes and the retained mixed model as baseline.
Jitter recovers 3 known-box tab selections per profile and 1 raw-proposal HCF tall-control selection.
These 15 conditions show no lost selections or new wrong selections. Known-box gains do not establish deployable gains.
Job `review426-jitter-retention` queues the existing T64 report with verified inputs for these comparisons.

The 2 TTR consumer sets add a different result:

- Original set: false-positive crops fall from 8 to 5, but true-positive crops fall from 2 to 1.
- V5 set: false-positive crops fall from 8 to 4, while true-positive crops remain 2.
- The lost positive is `stingray-catalog-breadthfirst-1-ref-6`.

Crop counts are not full-screen selection accuracy. Both sets use known boxes and inspected development groups.
Do not promote jitter from the 15-condition report alone. Preserve this consumer failure in every next comparison.
Wait for matched measured-box scoring before choosing another crop-training correction.

## Preparation and next work

PROFILE425 producers remain pending behind running training. No producer receipt exists yet; do not claim publication success.
Their approved consumers remain dependency-blocked, not failed or exhausted. Do not interrupt training to run them first.

Prioritize a supplemental-proposal comparison before more detector training:

1. Keep the shipped detector and both pinned crop classifiers as controls.
2. Compare baseline proposals, supplemental proposals, and a frozen combination on all 8 conditions.
3. Use scores and geometry for selection. Never choose the branch from labels or control-family truth.
4. Report every gained selection, lost success, new wrong selection, and no-focus outcome separately.
5. Reject any replacement that loses retained successes or adds wrong selections.

The existing T66 adapter requires the same detector at 2 confidence thresholds. It cannot compare these different detector models.
Create a bounded cached-report adapter task. Do not mislabel a detector change as a threshold comparison or bypass T66 checks.
Audit the tab class error separately against training labels and the checkpoint class map before assuming more data fixes it.

## TTR repair

Sillycon-TTR verifies the prior 4,940-byte archive in forwarded message 865.
Maximum-mini-NUIAK supplies the requested retained app logs through the verified share, with a bounded time window and sanitized user paths.
The response is stored at cursor 866. No repaired revision is delivered yet.
The old verified shared archive is removed after the exact receipt. Its project-local original remains available.
No new capture, navigation, build, or recovery attempt occurs in this review. The recovery guard remains.
