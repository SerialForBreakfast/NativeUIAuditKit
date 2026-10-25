# STREAM514 — Preserve selections across detector resolutions

Owner: Maximum-mini-NUIAK. Date: October 24, 2026.

## Completed comparisons

STREAM512 completes 16 tvOS jobs and 17 iOS jobs.
The campaigns answer separate questions. Their completion does not qualify a model replacement.

The 960-pixel tvOS detector improves Standard selection from 3/19 to 6/19 in the broader regression set.
It gains 4 selections, loses 1 edge-clearance success, and adds no wrong selections.
Both resolutions preserve 3 no-focus abstentions.
Optional HCF loses 5 successes and adds 2 wrong selections.
Reject a global resolution replacement. Preserve the earlier native-control gain as development evidence.

Additive iOS rehearsal gains 14 detections and loses 20 against coverage-selection rehearsal.
It gains 14 and loses 30 against original-only frozen training.
It gains 18 and loses 31 against Run013.
Reject the candidate. These are matched development observations, not independent deployment accuracy.
The conditional diagnostic reports contain localization and missed-detection failures, without class-confusion errors.
Do not assume more images alone resolve retention. Keep iOS separate from tvOS focus.

## Next experiment

Test one fixed rule: preserve a unique 1280-pixel selection; otherwise use the retained 960-pixel result.
Branch selection uses scores only. Ground truth measures the outcome after selection.
A wrong unique baseline selection stays wrong. No-focus false selections remain visible failures.

The graph contains 8 comparisons and 1 combined decision.
It covers buttons, rows, tabs, no-focus, tall controls, edge clearance, small decoration, and diamond decoration.
All jobs reuse completed inference. No capture, training, threshold change, or model promotion occurs.
The combined report checks Standard candidate selections and retains every model, arm, and profile in its detailed rows.
Reject any lost Standard success or new wrong selection.
A passing development result still needs independent consumer and latency qualification.

Each diagnostic has an 800 s ceiling and a 100 MB output ceiling.
Cached comparison work should take seconds, plus queue overhead. This is not overnight training work.
The runner owns execution. New jobs do not alter its active code or restart its service.

## Software qualification

All 31 focused tests pass. Two campaigns use the same adapter through isolated queues.
Changed weights, invalid receipts, duplicate cases, and no-focus failures have explicit checks.
The offline Swift build and all 177 Swift tests pass.

## SDK dependency

Sillycon-TTR reply 1400 supplies source repair f8cdd641. The standalone retained audit now passes under Ruby 2.6.10.
No eligible independent SDK training delivery is available.
The existing 6 pairs remain review-only. Do not train on those inspected test cases.
Missing independent groups and observed profiles block native crop training, not retained-data comparisons.
The corrected audit returns zero candidates across 6 pairs, 1 group, and 5 images.
Sillycon-TTR reports a new matching-host freshness check. Its pixels remain calibration evidence, not independent training groups.

## Next priorities

1. Review the complete fallback report before requesting consumer changes.
2. Qualify independent SDK groups for crop and temporal training through SDK513.
3. Use matched iOS localization evidence to select a bounded training correction.

Keep Standard and shipped models unchanged. Preserve every prior success and failed attempt.
Private graph specifications, test logs, and receipts reside under `reports/work/STREAM514/`.
