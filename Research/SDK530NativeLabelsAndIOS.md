# SDK530 — Native focus labels and iOS correction

Owner: Maximum-mini-NUIAK. Date: October 25, 2026.

## Verified findings

All 6 iOS geometry reports complete and their output hashes verify.
Class-aware matching finds 12 gains and 13 losses against the matched original-only control.
Class-agnostic matching finds 13 gains and 13 losses.
Five class-aware losses have another-class boxes with IoU above 0.96.
Each has an overlapping label that competes for the same prediction.
One-to-one assignment explains why removing class matching does not recover every such case.
Do not describe these as 13 pure localization failures.
The other 8 losses lack any candidate box with IoU of at least 0.5.
Do not change reviewed labels or remove those losses from acceptance.
The candidate also retains its separate 14 losses against Run013.

## Native focus preparation

The new episode adapter connects native labels to the existing production crop helper.
Binary focus labels use observed focus and registered bounds.
They do not require primaryButton or secondaryButton detector roles.
Unknown frame focus and unstable geometry remain excluded.
Visible unfocused controls supply negative crops. Empty frames supply no crop.
Repeated identical images produce one crop set. Conflicting labels on identical pixels fail.
The adapter preserves source groups and source roles. Its outputs remain review-only.
This completes the missing episode-to-crop connection. It does not complete training admission.

The removal episode has 2 unique images: 1 control-bearing frame and 1 empty frame.
The visible-negative episode has 2 unique control-bearing images.
Both share the existing scene ancestry. They are not independent training and validation groups.

## Admitted graph

Two native crop jobs use the same adapter with different configurations.
Six T56 jobs compare iOS inference at 960 pixels against the same weights at 640 pixels.
Six reports and one aggregate also check Run013 preservation.
Confidence, NMS, images, labels, and model weights remain fixed.
Reject losses against either baseline. Do not promote automatically.
These jobs reuse existing templates and comparisons. They require no new capture or training.

All 15 jobs are approved. The detached runner starts the graph without interruption or restart.
At the saved batch review, 9 jobs complete with verified hashes, 4 are pending, and 2 wait for dependencies.
These counts describe this tranche, not the whole historical queue.
The 6 comparable resolution jobs previously used about 35 s in total.
The remaining tranche is short work, approximately less than 1 min of execution if those runtimes hold.
It does not fill an overnight window. No filler or repeated fit is added.

## Remaining native training blocker

Current captures lack observed Focus Style with continuity to their endpoints.
Their existing review roles and group exclusions remain unchanged.
A new eligible producer needs independent training and development groups.
Use the existing native Focus Style collector and continuity verifier.
The missing connection is the supported campaign producer for bracketed profile reads and its complete session ledger.
Do not substitute contrast metadata, preferred focus, or visual appearance.
The next producer must preserve original review groups and prove train/development separation.
It must emit verified focus states, registered bounds, profile continuity, and exact image/source identities.

BigDog-Coordinator stores request 1498 for Sillycon-TTR's supported producer interface.
Storage does not confirm forwarding or acceptance.
TTR's new type-metadata tests pass according to its reply. That does not certify our capture profiles.
No new TTR build, installation, or capture occurs in this tranche.

## Verification

The focused suite passes 22 tests in 4.206 s.
The offline existing Swift build passes 177 Swift Testing tests and 14 XCTest tests.
No rebuild changes the helper used by the runner.
Two isolated queue jobs produce real production crops with positive and negative labels.
Tests cover unknown focus, missing geometry, conflicting repeated pixels, and prohibited training admission.
An initial output-receipt path failure was repaired before live admission.
TTR confirms the exact source archive receipt. Its verified shared copy is removed; the USB original remains.
Swift verification uses the existing build without rebuilding the queued crop helper.
The first attempt detects a stale module cache from the parked checkout. A fresh project-local cache avoids that conflict.
Standard, shipped models, previous successes, and original captures remain unchanged.

Evidence: reports/work/SDK530/ios-loss-review.json, tests.log, admission-receipts.json, batch-review.json, and coordination-receipt.json.

## Next priority

1. Finish the bracketed native profile producer using the supported TTR interface.
2. Produce independent eligible focus groups and queue matched rehearsal with retained-success and no-focus checks.
3. Use the complete iOS resolution decision to accept or reject this correction.
4. Review the 5 overlapping-label cases before changing annotation geometry or class training.

Adapter implementation and qualification take about 10 min, against the 20–30 min estimate.
This duration excludes the preceding result review. Native capture and model training do not run in this preparation session.
