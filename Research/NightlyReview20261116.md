# Nightly review · November 16, 2026 Pacific

Reviewed November 16 07:42:13.370 UTC through November 17 07:48:34.487 UTC, starting at the prior report cutoff. The [attempt ledger](../reports/work/NIGHTLY-20261117/window.json) contains 43 attempt IDs and their intervals.

## What improved

No verified model improvement this review period. No D1 seed pair completed. No model was accepted for release.

## What we learned

**tvOS detection.** On the same 42 development screens, shipped Standard localized 404/460 controls and the historical one-epoch probe localized 398/460. NewsTV fell from 393/437 to 376/437, Photo Guessing Game rose from 9/21 to 20/21, and Swiftfin stayed at 2/2. The respective legacy same-role matches were 120/438 and 374/438. This explains why the earlier role-score increase overstated localization gains. The small Swiftfin and Photo denominators limit an equal-app comparison. [Paired development evidence](../reports/work/TRAIN666/development-rescore/)

**tvOS focus.** Only 1/34 supplied human reference crops on the reviewed Settings and Home positives cleared the shipped focus threshold. On the separate Kanopy recording, Standard picked 1/18 focused controls correctly and picked a control on both no-focus frames. These results identify a scoring problem even when reference boxes are available. The reviewed frames share flows. [Stage trace](../reports/work/TRAIN666/ax-development-r1/focus-stages.json) · [Kanopy readback](../reports/work/TRAIN666/development-rescore/Kanopy-Standard-focus.json)

**TTR calibration.** Split Settings delivered six states, three distinct PNGs and one layout. All six passed a same-frame capture reference comparison after normal loader decoding. Disabled Autoplay kept its toggle box and Details kept focus. The loader preserved both intentionally corrupt inputs. Comparing decoded values against capture evidence identified the shifted box and wrong focus owner separately. All eight were refused training. Coordinator stored the readback as 2275. Delivery to Sillycon-TTR remains unconfirmed. [Decoded states](../reports/work/NIGHTLY-20261117/split-readback.json) · [Reference comparison](../reports/work/NIGHTLY-20261117/split-reference-comparison.json) · [Receipt](../reports/work/NIGHTLY-20261117/send-receipt.json)

**iOS detection.** No iOS attempt in this window. No iOS accuracy or release decision.

## What regressed

Across 50 repeated focus appearances on 13 mixed panels, COMP600 seed 371 recovered three, lost two to abstention and added one wrong Store pick. Seed 372 recovered nine, lost none and removed one wrong pick. Both retained the Accessibility success. All 50 had positive references and some supplied only the correct crop. General no-focus performance and whole-screen real-app gains remain unmeasured. On one synthetic parallax layout, the original controls scored 0/4 at both seeds under each brightness condition. Programme scored 4/4 at 371 and 0/4 at 372. The catalog now closes B405-294 as contradicted. Watch Later resolution testing recovered 0/244 child appearances at both seeds. [COMP600 decisions](../reports/work/UNBLOCK665/results.md) · [Parallax](../reports/work/UNBLOCK665/parallax-results.md) · [Catalog](Experiments/backlog405.json)

## What runs next and what each test decides

D1 seed 371-r2 was running at cutoff. Its launch pins differ from two files subsequently changed for TRAIN666 compiler validation. Require the normal post-run authorization and output verification before any scoring. When the runner releases its host lock, use the existing unstarted-job source refresh for seed 372-r2. Its spec and non-code approval checks matched, and reversing the two reviewed validation edits in memory reproduced the approved hashes. Only after verified outputs, score each eligible checkpoint against shipped Standard on the same 42 development screens and 20 Kanopy frames to distinguish localization, role and focus changes. No jobs released, admitted or continued this pass.

## Queue health

One maintenance snapshot found 0 ready, 1 running, 351 dependent, 13 otherwise blocked, 9 awaiting approval, 127 exhausted and 29 unselected. Estimated useful ready duration was zero. The window included 40 completed attempts, 2 failed and 1 still executing. Disjoint runner time was 1 h 4 min 53 s completed, 46 s failed, 7 h 0 min 38 s ongoing and 16 h 0 min 4 s idle. [Queue snapshot](../reports/work/NIGHTLY-20261117/queue.json) · [Runner](../reports/work/NIGHTLY-20261117/health.json) · [Window](../reports/work/NIGHTLY-20261117/window.json)

## Blockers and approvals

Both original D1 attempts failed their output limit. Their restarts already had bounded approval. The seed-372 source refresh returned resource_busy on the active runner lock before any approval mutation. Retry after release. If seed 371 fails post-run checks, preserve the attempt and reconcile cumulative time, storage and restoration before considering a successor. No additional fit approval requested. Watch Later fits remain held.

## Priority changes and reasons

Prioritize a valid D1 comparison and H2 coverage of underrepresented roles. The split layout adds calibration evidence only. Keep H3 tied to the measured focus-stage failures. Close the legacy COMP600, parallax and Watch Later investigations without extending them. The nightly automation now follows the three TRAIN666 hypotheses and no longer targets a queue length.
