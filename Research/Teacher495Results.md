# Teacher preservation: results and next comparison

Owner: Maximum-mini-NUIAK. Reviewed October 23, 2026.

## Decision

### October 23 follow-up: TEACHER496

Reject TEACHER496 as a replacement. Both terminal reports complete with verified outputs.
Compared with TEACHER495, Standard known-box results remain 68 correct selections and 4 correct abstentions.
The consumer slice recovers 1 true positive but retains all 16 false positives.
Compared with retained Standard, the candidate still loses 6 negative successes.
Optional HCF raw-proposal scoring adds 2 wrong selections. Mapped-proposal results remain unchanged.
Stop this teacher sequence. Do not add another weight or seed trial without a different measured cause.

PROPOSAL497 tests both completed models on identical resolution454 detector boxes across 8 retained families.
The T57 comparisons separate proposal coverage from crop scoring. The T58 report summarizes button, row, and tab results.
All 9 jobs are approved. The runner completes the first comparison without new capture or training.
The 800 s diagnostic limit is a ceiling, not a duration estimate. This batch does not fill the overnight gap.

The independent Standard batch test preserves all decisions across batch sizes 4 and 8.
The maximum score difference is 4.45e-16 across the 6 executions.
Only 16 crops from 3 groups are tested. Timing does not establish a general throughput improvement.

Maximum-mini-TTR coordinator readiness passes after opening the existing qualified source-built app.
Fixture scene access still fails because its HTTP server is absent. No captures repeat and no TTR sources change.
The supported Simulator launch request is stored with BigDog-Coordinator at cursor 1299. Forwarding remains unconfirmed.

### Prior TEACHER495 result

Reject TEACHER495 as a replacement. Preserve Standard, shipped models, and the optional observer.
Both terminal reports complete with verified output hashes. The fit takes 1,321.74 s.
The teacher remains unchanged and detached across 162,000 anchor presentations and 13,500 updates.
This verifies execution, not model acceptance.

| Development slice | Matched native fit | TEACHER495 | Retained Standard | Decision |
|---|---:|---:|---:|---|
| Standard known-box correct selections | 65 | 68 | 62 | Gains without losses on this slice. |
| Standard consumer false positives, 20 crops | 16 | 16 | 10 | Six retained negative successes are lost. |
| Standard consumer true positives | 4 | 3 | 3 | One success is lost against native adaptation. |
| Standard full-screen proposal selections | 0 | 0 | 0 | Better crop scoring does not recover missing proposals. |

Known-box testing includes 68 focused observations and 4 no-focus observations across 21 recorded groups.
All 4 no-focus outcomes remain correct. Related frames and profiles are not independent trials.
The consumer slice contains 1 retained group. Its limitations do not permit ignoring observed regressions.
The lost native-control comparison case is `stingray-catalog-breadthfirst-1-ref-6`.
The Standard retention report identifies all 6 new false positives by case ID.

Optional HCF known-box selections improve from 65 to 68 against native adaptation, without losses.
HCF mapped-proposal selections remain 44. Do not combine these results with Standard accuracy.

## Next useful correction

TEACHER496 changes only the teacher checkpoint to the retained PROFILE425 Standard model.
The first teacher does not preserve the required consumer decisions. This motivates testing teacher choice, not a weight sweep.
Keep the same training membership, anchors, initialization, seed, epochs, penalty weight, and thresholds.
The graph compares the new candidate against TEACHER495 and retained Standard outputs on all 17 conditions.
Thirty-six jobs are registered and approved. Only 1 is a training job.
The training limit remains 1,800 s and 2 GiB. The prior fit suggests approximately 22 min plus scoring.
Reject any lost Standard success or new wrong selection. If retention still fails, inspect training coverage before further fits.

## Independent reserve

Seven approved jobs test CPU batch efficiency on 16 unique retained Standard crops across 3 groups.
The existing preparation and scoring templates compare batch sizes 4 and 8 in paired order: 4/8, 8/4, 4/8.
Require score error at most 0.0001 and unchanged 0.15/0.85 decisions before interpreting timing.
The images retain their development role. Copied image bytes verify against the source hashes.
The initial preparation rejects external paths. Project-local verified copies resolve that template constraint.
The initial ordering dependency lacks an output name. Explicit prediction dependencies resolve the definition error before submission.
This reserve takes seconds to minutes. It does not fill an overnight window or establish model improvement.
The template currently permits at most 16 crops. Broader throughput qualification needs a separately tested bounded extension.

## TTR reply and actionable blocker

Maximum-mini-NUIAK reads and acknowledges coordinator messages through cursor 1277.
Sillycon-TTR reports SDK observer, alias, coverage, and journal improvements through pushed source `39b8a9b4`.
The later real generator sample remains local-only in its report. These claims are not independently qualified native labels.
Useful intake fields remain frame-aligned observed focus, visible bounds, hierarchy, selection state, settling, and explicit missing values.
App declarations and preferred focus do not replace observed focus.

Recovery v3 fails at `export_staging_create` with `access_denied`, `NSCocoaErrorDomain/513`, and writer `cli_caller`.
This is not a time-budget failure. More training time cannot fix it.
The original evidence remains preserved. No capture repeats, TTR source edits, or app restarts occur.
The 4 session comparisons still require verified export and cleanup evidence.
BigDog-Coordinator stores the exact failure and intake feedback at cursor 1278.
Sillycon-TTR acknowledges forwarded message 1279 and returns supported export guidance through cursor 1281.
No shared artifact is offered. No artifact download or shared-copy cleanup is pending.

### Export resolved; Fixture connection remains blocked

The supported source chunk exporter succeeds from the authorized agent caller. All 9 files and 26,143 bytes verify.
Checkpoint: `ff29ab346e1da60a3956df8941e8a0bf2e480c7b0e18296d167b713a8017f2cb`.
No recapture, restart, source edit, or permission change occurs.
The retained campaign reports 2 failed cases, 6 unattempted cases, and 0 accepted image pairs.
Its cumulative time is 81.155284 s. This is not budget exhaustion.
The original cleanup failure remains unchanged. The next case fails Fixture connection with `serviceUnavailable` and `urlError:-1004`.
An exported report is not a usable image corpus. Keep the comparisons gated and request the supported bounded connection repair.
BigDog-Coordinator stores the caller export receipt and exact connection failure at cursor 1282.
Forwarding of this final receipt remains unconfirmed at handoff.

## Handoff snapshot

The same runner executes `teacher496-standard-train`. One independent preparation job is ready behind it.
Forty-one remaining jobs wait on dependencies or result conditions. They are not independent investigations.
The fit plus reserve provides approximately 22 min and short diagnostics, not overnight coverage.
Preparation and admission remain within the estimated 15–25 min window. No full Swift rerun is required for configuration-only changes.

## Evidence

- `teacher495-native-decision`, attempt 1: verified native-control comparison.
- `teacher495-standard-retention-decision`, attempt 1: verified Standard retention comparison.
- `teacher495-native-train`, attempt 1: verified training and teacher-integrity outputs.
- `reports/work/TEACHER496/admission.json`: exact new graph approvals.
- `reports/work/TEACHER496/efficiency-admission.json`: independent reserve approvals.
- `reports/work/TEACHER495/peer-review.json`: received coordinator messages.

The next review checks these terminal reports in a batch. The background runner retains execution ownership.
