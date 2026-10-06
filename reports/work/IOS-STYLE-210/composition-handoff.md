# Composed detector paths — October 6

Software verified; data roles unchanged; retained-output integration verified;
model gates failed. No new model inference, training, capture or promotion.

Implemented `scripts/compose_style210.py prepare|report` and focused tests. The
protocol freezes source/input/checkpoint identities before evaluation. Each raw
prediction artifact is validated against its original manifest and settings;
existing refinement and extra-proposal merges are reused. Append admitted original
extra donors after refinement, suppressing overlap with refined operating page
boxes atIoU>=0.5. Labels never select donors. All non-page detections and metrics
are preserved. Neither original predictions nor reports are overwritten.

## Measured results

Custom existing metric implementation; not official COCO results. Same images,
fixed-last checkpoints and operating threshold as the previous comparison.

| Population | Control027 AP50:95 extra→composed | Treatment028 extra→composed | Composed TP/FP027→028 |
|---|---:|---:|---:|
| Training-fit216 |.545466→.869329|.546938→.861796|216/24→216/24|
| Development96 |.433172→.563801|.465028→.604146|72/16→75/14|
| Retained600 |.617944→.656555|.625048→.655860|533/24→543/24|

Fit now has72/72hits at all three placements. Development and retained TP/FP are
unchanged from extra-only; their improvement is box localization, not additional
recall. Treatment has slightly lower retained AP50:95 than composed control, despite
higher TP, so it is not uniformly superior. Six gates fail: pageFP, sheetAP,
scrollIndicatorAP, sheetFP, cancelActionFP, mapViewFP. No independent-final or DS-G8
claim. This retained set is reused research evaluation, not an untouched new final.

Fit/page/combined added donors: control17/16/284, treatment17/17/294. Zero overlap
suppressions in actual data; synthetic tests exercise suppression and threshold edge.

## Cost and evidence

CPU report30.954seconds. Reused2,306crop predictions across both arms; no GPU work.
For actual fresh inference, each arm needs358fit,109development,686retained crop
requests before caching, versus135/37/413extra-only. Exact source-window deduplication
could reduce fit358→349; none of the109development or686retained windows duplicate.
Do not describe composition as free runtime work or claim measured deployment latency.
Its one-time retained-output evaluation cost is not a fresh capture/inference cost.

Protocol SHA256 `fe8d12b1b596837865559630c75a2b4acaa3df92c10f05dbc3302c38b2de8888`.
Report SHA256 `05b9161953a3d8a45b61fe14b608ef128ea37467dfcba24bdaa12d48041c6de6`.
Files: `artifacts/composition01/{protocol,evaluation}.json`; logs in
`.build/composition210-{evaluation,build,test,test-authorized}.log`.

Verification:23focused Python tests passed0.026s. Real prepare/report exited0;
real repeat report rejected `output_collision` before scoring, preserving its hash.
Offline Swift build passed. Restricted tests failed15issues with explicit Apple
sandbox-extension/CVPixelBufferPool errors; authorized unchanged command passed
139tests/19suites in4.194seconds. No test exclusions or package changes. Existing
dirty work preserved; only new composition source/tests and scoped docs added here.

## Next substantial tranche

1. Integrate Big Dog's CPU paired error report when delivered, with independent
   case/metric verification and one precise acceptance response.
2. Diagnose the remaining page false positives on training/development sources;
   define one precision intervention, freeze it, and keep retained evaluation out
   of parameter selection. Measure deployment cost before any routing proposal.
3. Resume native-focus205/206when TTR supplies capture-build/source evidence.
   Current artwork/capture integrity alone cannot admit uncertain focus labels.

No additional worker GPU task is needed to reproduce this cached-output result.
