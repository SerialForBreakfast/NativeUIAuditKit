# Corroborated-alias precision result — October 6

Software verified; existing data roles unchanged; retained replay integrated;
overall model gate failed. No capture, inference, training or promotion.

## What changed

`precision211.py prepare|fit|report` uses existing validated raw predictions and
crop geometry. For an operating page proposal with exactly one admitted crop donor,
resolve overlaps with other uniquely corroborated donors by descending original
confidence, stable original-index ties, IoU>=0.5. Refine survivors and remove aliases.
Uncorroborated predictions and non-page classes remain unchanged. The extra-proposal
composition stays unchanged. No label-dependent selection or threshold search.

The old rule left conflicting originals untouched. Diagnosis found38conflicting
proposals in18fit frames and17in7development frames. All24fit/14development treatment
false positives originated in first-pass proposals; not unrelated-class hallucinations.

## Frozen evaluation

Fit passed before retained scoring. Custom existing AP implementation; original
confidence0.25/IoU0.5 operating point. Retained data is not a new independent final set.

| Treatment028 population | Previous composition TP/FP | New TP/FP | AP50:95 before→after |
|---|---:|---:|---:|
| Training-fit216 |216/24|216/4|.861796→.929248|
| Development96 |75/14|75/4|.604146→.629974|
| Retained600 |543/24|543/7|.655860→.661776|

Control027 also improves: fit216/4, development72/6, retained533/7. Its AP50:95 is
.937932/.589978/.662630 respectively. Treatment is not uniformly better: control's
retained AP50:95 remains slightly higher, while treatment has higher recall.
All non-page metrics match original first-pass metrics exactly.

Treatment now passes the existing pageFP gate. Five inherited gates still fail:
sheetAP,scrollIndicatorAP,sheetFP,cancelActionFP,mapViewFP. Do not promote the detector
or claim DS-G8. Both candidates remain separate experimental artifacts.

Suppressed aliases20fit/10development/17retained per arm. Treatment also refines54
development versus51control, so its FP14→4 is not solely the number of removed
boxes; corrected geometry matters. No extra-donor count changes. Synthetic tests
exercise nearby separate controls, overlap chains, stable ties, invalid geometry,
failed crops, no corroboration and failed-fit gating. Overlapping genuine controls
remain a deployment risk requiring independent scene evidence.

## Verification and cost

22focused tests pass0.004seconds. Real prepare, fit and report exit0. Fit3.23seconds;
full CPU report30.55seconds. Offline build2.71seconds and139tests/19suites4.116seconds
pass using the documented Apple runtime permission context, no exclusions/downloads.
No GPU compute or new pixel files. Same crop workload as composition; fresh inference
and runtime cost remain unmeasured, not free. No old source/report changed.

Hashes under `artifacts/comparison01`:

- protocol.json: `a5bbb7b1b7a81e6ee9dd9b6db4014308e7a2c0bbf19cbafe6c3f5d13b7861e8e`
- fit-screen.json: `1b87ba6dd36e8afe8a366f627de9cf3f2e822682dcaa4f9e84d673df0f8f04e0`
- evaluation.json: `2201df77e798395365546ea6669efd4e03ecff702672d0219bf84d950b21897b`

Logs `.build/precision211-{build,test,evaluation}.log`; source/tests are new files.
Pre-existing dirty changes preserved. No Git writes. Worker CPU paired report remains
pending; no duplicate scoring assignment. Native-focus work still depends on TTR's
capture-source binding, not this iOS result.

Published/read back `nuiak/responses/nuiak-20261006-worker198-precision211-feedback.json`,
1,653bytes, SHA256 `9bc7f5817227093f22a9484b674a600e12ce3097a42f72dd9c6d77a5a5366500`.
The message keeps the existing CPU report assignment and distinguishes raw ROI,
hybrid, composed and alias-resolved metrics; no additional GPU job. Peer
acknowledgment remains unobserved. No unrelated local iOS status sent to TTR.

Next tranche: review worker's case-linked report; use training/development evidence
to diagnose inherited sheet/scrollIndicator/cancelAction/mapView errors and select
one bounded intervention. Keep the precision rule frozen, and measure execution cost
on independent scenes before any production routing. Resume native-focus205/206first
when eligible producer evidence becomes available.
