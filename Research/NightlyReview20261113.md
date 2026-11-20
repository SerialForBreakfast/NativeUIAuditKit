# Maximum-mini-NUIAK nightly review for November 13, 2026

The review covers November 13 at 07:48:52.797 UTC through November 14 at 07:45:42.634 UTC. Results remain provisional.

## What improved

Adding R5 button proposals after abstentions improves correct focus picks from 3/13 to 10/13 on reviewed focused NewsTV screens, with 3 wrong picks in both arms. Correct picks also rose from 7/21 to 9/21 on Photo Guessing Game, with 1 wrong pick in both arms. The 9 recoveries span 4 development flows. Five share one NewsTV tab strip. The comparison changes both proposal source and threshold. The fixed-threshold v3 control recovered 4 Photo Guessing Game targets and 0 NewsTV targets. No candidate has qualified for release. [Paired outcomes, control and retention](../reports/work/PROP636/README.md)

## What we learned

The fallback retained both Settings successes and all 11 no-focus abstentions. Kanopy remained at 3 correct, 6 wrong and 9 missed across 18 related frames. Consumer latency remains unmeasured. The 2 approved NewsTV focus boxes match the repaired SDK output on 3 samples per route. Article detail reports known no focus. [SDK readback](../reports/work/NEWS623/verified.json)

For tvOS detection, only Studio Search qualified as a complete training layout among 5 synthetic layouts. Four targets passed the loader. Other layouts still have cell edge or focusability discrepancies. For iOS detection, Settings and Calendar supplied 21 accessibility rectangles across 2 screens. Independent visible-box references remain pending. [tvOS loader](../reports/work/ROLE636/subset/loader/receipt.json) · [iOS references](../reports/work/IOS636/README.md)

## What regressed

The severe-clipping fit lost 4 original text detections and recovered 5 targets across 52 generated retention screens. The full-view control lost 2 and recovered 3. Keep clipping as a regression test. These paired changes do not establish a release gain. [Retention results](../reports/work/PAR616/README.md)

## What runs next

1. Compare the frozen focus fallback with its existing control after the 3 FLOW632 focus decisions arrive. Report every new correct pick, wrong pick and lost abstention. Measure consumer latency before integration. A regression directs work to the first changed proposal. Missing focus evidence leaves a case unresolved.
2. After both independent iOS reviews, admit the 4 approved IOS635 fits once. Control and treatment each use 36 screens, 100 epochs and seeds 371 and 372. Verify transfer and retained UIKit success for both seed pairs. Hold a flat, regressing or inconsistent treatment. Total ceilings are 48 h and 8 GiB. Expected fit duration remains unmeasured. [Exact approval](../reports/work/IOS636/conditional-fit-approval.json)
3. For tvOS detection, resolve visible cell bounds and disabled-button ownership before adding more mixed frames. Use the existing component-removal reference and normal loader. Keep partial frames outside complete training membership. [Evidence and ownership questions](../reports/work/ROLE636/README.md)

## Queue health

The live runner was waiting with 0 running. The readiness response marked its inventory stale. Its last counts were 0 ready, 440 dependency-blocked, 11 otherwise blocked, 129 exhausted, 29 unselected and 8 awaiting approval. Current global counts are unverified. Verified ready duration is 0 h. No job was released, admitted or continued. Catalog validation passed on 293 definitions. No new eligible branch was identified.

The detached runner completed par616-r5-full attempt 1 and par616-r5-severe attempt 1. Completed execution occupied 478.35 s. Failed execution occupied 0 s. The other 85,731.49 s had no recorded runner execution. The intervals do not overlap. [Attempt ledger](../reports/work/NIGHTLY-20261114/attempts.json) · [Catalog validation](../reports/work/NIGHTLY-20261114/catalog-check.json)

## Blockers and approvals

The independent iOS reference reviews are the remaining admission condition for the 4 exact fits. The separate 4 artwork fits remain on hold. BigDog-Coordinator stored the requested 19-slot loader readback metadata and Simulator inventory at cursors 2162 and 2163. Recipient acknowledgment remains unverified. [Per-slot evidence](../reports/work/IOS608/ttr/readback.json)

## Priority changes and reasons

Prioritize prospective focus transfer, mixed-screen detection coverage and independent iOS button references. More shelf fits would address one clipped cell family while risking text retention. Optional HCF has no new qualification evidence in this review.
