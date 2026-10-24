# Nightly research review — 2026-10-23 UTC

Owner: Maximum-mini-NUIAK.
Window: 2026-10-22 06:49:09 UTC through 2026-10-23 06:41:04 UTC.
The preceding durable report defines the start. The heartbeat defines the cutoff.
Attempt IDs and receipt hashes are in `reports/work/NIGHTLY-20261023/review-window.json`.
The verified USB volume has about 1.6 TiB available.

## What improved

No verified model improvement this review period.
Checkpoint restoration and the approved Standard continuation now complete through the queue.
Readiness reporting now returns counts instead of failing on a metadata file.
These are workflow improvements, not model accuracy improvements.

## What we learned

For iOS, the retained best checkpoint loses 8 detections against the final checkpoint, with 0 gains.
Against Run013, that best checkpoint gains 15 detections but loses 54. Reject replacement.
The catalog now records B405-260 as contradicted through the existing confirmation interface.
The two Standard checkpoint records receive updated reviews. Their manual outcomes remain inconclusive pending family-specific interpretation.

Text-only OCR changes lose 2 supplied-label successes on each iOS device variant.
The geometry rule prevents those changes and preserves the baseline. It adds no correct detections.
The variants share the inspected scene group. They do not provide independent replication.
Incomplete annotations prevent full false-positive or release claims.

Mixed-model scoring shows exact paired score parity and a 13.9 percent lower median step time for batch 8 versus batch 4.
Loading effects limit that timing result. Keep production settings unchanged.
See [spike findings](ADRspikes493Results.md).

## What regressed

The Standard exposure continuation fails acceptance despite successful execution.
Standard known-box scoring gains 2 and loses 2 successes, with 3 new wrong selections.
Standard consumer crops gain 2 and lose 4 successes, with 2 new wrong selections.
Standard fixed-proposal selection has no gains, losses, or new wrong selections.
These are development observations. Related crops and frames are not independent trials.
No candidate replaces Standard or shipped models.

The window contains 5 failed attempts: one continuation evidence failure, two OCR timeouts, one session start, and one recovery attempt.
Successful successors preserve the original failures. TTR recovery remains unresolved.

## What runs next

1. Maximum-mini-NUIAK must qualify the committed TTR export repair through a matching source build.
   Export the retained restart report without another restart or capture. Verify bytes, hashes, and explicit missing-marker state.
   This is an implementation-session task, not a nightly build or installation.
2. If recovery proof passes existing guards, release the 4 approved session comparisons and their report.
   These compare separate sessions with reused sessions on identical recipes.
3. Review iOS missing semantic labels and completeness before another training change.
   The SDK proposal requests stable IDs, observed bounds, semantic roles, and completeness evidence.
   Sillycon-TTR records the proposal, but iOS SDK work remains user-deferred.
4. Prepare independent Standard motion and no-focus membership from qualified retained inputs.
   Existing catalog requirements still lack native unchanged-focus motion and independent no-focus groups.

No jobs are admitted, released, or continued during this review.
Do not repeat completed OCR, checkpoint, or timing comparisons to occupy the runner.

## Queue health

The runner is active, healthy, and waiting. Running: 0. Ready: 0. Awaiting approval: 0.
Useful ready duration: 0 s. The overnight capacity target remains unmet.
Five current session-chain jobs remain dependent on recovery: 4 captures and 1 report.
The global status combines 458 blocked or exhausted entries. It does not establish 458 actionable blockers.
A globally separated dependent, exhausted, and unselected count is unavailable from this summary.
The catalog reports 156 planned records, 94 open records without plans, and 3 comparisons awaiting review before this pass.
The pass reviews all 3 and confirms the iOS result. It does not claim that plans are executable work.

The window contains 98 completed and 5 failed attempts.
Non-overlapping completed execution totals 1965.45 s. Failed execution totals 425.10 s.
Recorded terminal execution occupies 2.78 percent of the 23.87 h window: 2.29 percent complete and 0.49 percent failed.
The remaining 97.22 percent has no terminal queue execution in this inventory.
This is not a measurement of total machine idle time. Builds and attempts without terminal receipts are outside the metric.
Occupancy is not scientific progress.

## Blockers and approvals

Sillycon-TTR supplies export repair commit `6e4a55a23932cb8a7c5937c1434a9aed82d4edc6`.
Maximum-mini-TTR still needs matching runtime qualification and an exact export receipt.
Messages through cursor 1231 are read and acknowledged. New SDK reports do not establish native qualification or recovery success.
The 7 unattempted recovery cases retain their 518.902681 s allowance. Do not repeat captures or expand budgets.
Each of the 4 approved session comparisons retains its 800 s and 250 MB limits.

The catalog identifies 9 T03 data requirements affecting 21 records.
It also identifies 10 unsupported future-model adapter requirements affecting 10 records.
T11 membership and T37 independent no-focus data each affect 9 records.
These counts overlap. They are not independent runnable investigations.

## Priority changes and reasons

Prioritize the source-built export integration because it releases existing approved comparisons without new capture recipes.
Keep Standard and iOS label qualification ahead of more narrow OCR threshold tests.
Stop checkpoint selection and learning-rate repetition that already fails retention requirements.
Keep optional HCF separate. Preserve Standard, previous successes, original inputs, checkpoints, and failed evidence.

No source code, service, schedule, model, Git history, or running process changes during this review.
