# IOS-PROPOSAL-197 support and next-comparison contract

October6,2026. No capture, inference, training, data-role change or promotion.
Existing artwork feedback changes preserved. Model diagnosis used existing022cached
predictions and216verified training-fit images only; no evaluation-driven design.

## Result

185/216page targets have operating IoU>=.5 support. The fixed single-low-proposal rule
selects135windows, rejects73duplicates, and finds no candidate for8images.17of31missing
targets are completely inside selected windows. This is an upper-support diagnostic,
not17recovered detections.62windows contain no complete target:10retain no page label,
52contain partial targets. Partial targets must not be trained/scored as negatives.

The deterministic50%-overlapping half-width square grid fully contains216/216targets
but costs6714crops, maximum44/frame.5658cropsretain no page labels;564clipped and492full
page-label appearances. These duplicated appearances are not independent examples.
Do not deploy the dense alternative without a different measured cost justification.

## Delivered and verification

`scripts/roi197.py` integrates source-bound prediction validation, training-membership
checks and193crop geometry/label audit. No truth selects proposals or windows. The
sealed `artifacts/support02/support.json` preserves all exact image IDs/windows and
model/input/source hashes. Support01 is retained; support02 corrects the distinction
between absence and incomplete containment, without changing selection.

31focused ROI193–197tests pass. Required offline Swift build/test exited0 using resident
`.build/asset200-offline`; logs `.build/roi197-build.log` and `.build/roi197-test.log`.
New tests cover cap/floor/ties, duplicate rejection without fallback, failed inference,
deterministic edge coverage, invalid/excessive geometry and containment boundaries.

The canonical197plan now freezes a negative-region-first022/026comparison, existing
thresholds, one-crop cap, duplicate rule, retained/full-image accounting and latency
budget.10true negative regions are a narrow falsification screen, not calibration.
No new confidence is authorized for production. Exact selected pixels are not yet
materialized or scored; that is the next substantial model tranche.

Outcomes: software verified; original fit membership verified train; cached integration
verified; candidate/model gates unassessed (prior failed gates unchanged). This work
does not depend on TTR. Native tvOS artwork work remains blocked on current producer
source/import contract, not on the independent iOS diagnostic.

Big Dog sent a native96-frame proposal during this work. Scope alignment response
published/read back at `nuiak/responses/nuiak-20261006-native-artwork-qualification-response01.json`,
SHA256 `248ba8850504db33ff6144318685c35a70b14d27fa2c9aa3f2fcc488ff746a34`.
It reuses the existing importer, requests already selected originals, preserves reserved
families and names the unchanged tvOS source blocker. Peer acknowledgment remains pending.
No iOS-only metrics were sent as general worker status. Support02 audit took2.72seconds.
