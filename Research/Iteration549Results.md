# ITERATION549 — Coverage and profile-transfer decisions

Owner: Maximum-mini-NUIAK. October 30, 2026.

## Completed longer iOS fits

Both fits finish their fixed 30 epochs. The control takes 98.3 min. The additive arm takes 102.2 min.
Together they take 200.4 min, within the prior 3.5–4 h estimate.
The additive arm detects 24/24 new development rows. The control detects 8/24.
Across six retained conditions, the additive arm gains 20 Run013 detections and loses 8.
The original-only control gains 19 and loses 9.
Both fail replacement gates. These counts describe development evidence, not independent real-app accuracy.

The additive arm loses 6 old rows, 1 label, and 1 navigation bar against Run013.
Three Run013 losses are shared between the two arms. Five additive-only losses are rows.
Broader coverage reduces forgetting, but does not resolve the conflict between old and new rows.
Do not expand the corpus again without testing a different correction.

## Standard transfer

Standard-only training loses 3 supplied-box Standard tab successes against joint-profile training.
It also introduces false positives on retained consumer crops.
The full report keeps Standard and HCF separate. Related frames do not count as independent trials.
Do not replace the joint-profile control with this Standard-only candidate.
HCF-only transfer remains unanswered because its fit stopped before epoch 30.

## Admitted checkpoint comparison

Ten jobs compare the retained additive checkpoint against the final additive checkpoint and Run013.
Seven T56 jobs use identical screenshots, labels, taxonomy, preprocessing, and thresholds.
Two retained reports and one aggregate report enforce previous-success checks.
The checkpoint was selected by training diagnostics, not these development results.
Its weights differ from the final model. The control checkpoint has identical weights, so its completed scores are reused.
These jobs perform inference and reporting only. They do not retrain or promote a model.
Each job permits 800 s and 100 MB. Expected execution is minutes, not overnight training.
If the checkpoint preserves more old rows without losing new rows, test stopping behavior in a separate fixed experiment.
If it fails, prioritize a class-preserving training objective with training-only anchors.

## HCF continuation

The exact historical trainer exists in Git revision d04a1702b5debb8a287f2292c6013a042ee11e0a.
Its SHA256 matches the exhausted checkpoint contract.
This removes the missing-source question. Runtime restoration parity remains unverified.
The next adapter must use this trainer and deduplication=False, not the current forced deduplication setting.
Do not restart the original fit or bypass its contract.

## TTR and runner

TTR reports new save/reopen, enrollment, and readiness checks. These remain unverified peer results.
Its new source remains unpublished. Maximum-mini-NUIAK requests the fetchable revision through BigDog-Coordinator.
The reply also confirms the retained padding arithmetic. This does not establish raw-tensor correctness.
The coordinator stores the response at cursor 1802. Forwarding is not confirmed.

The existing runner remains continuous and reports no error. No service restart occurs.
An initial health request used stale port 8766. The existing private control record resolves the correct endpoint.
Standard, previous successes, original evidence, and shipped models remain unchanged.

## Evidence and next tranche

Local receipts are in reports/work/ITERATION549/.
Catalog B405-268 is closed as contradicted. Full result files remain in the original queue attempts.

1. Review the admitted checkpoint comparison and choose the next fixed iOS correction.
2. Qualify the historical HCF continuation and finish only its remaining original epochs.
3. Obtain TTR source publication and qualify the actual Standard consumer replay.
4. Build a detector objective that preserves old classes if checkpoint selection still fails.

## Checkpoint result and admitted training correction

All 10 checkpoint jobs complete. The earlier additive checkpoint still loses 8 Run013 detections.
It exchanges one gain and one loss against the final checkpoint. Checkpoint selection does not resolve retention.
The frozen geometry review places 6 of its 10 ROW545 losses in controls 32–64 pixels high and under half-screen width.
That supports focused class and geometry work, not another arbitrary scale sweep.

A new graph tests targeted original-row rehearsal with 221 qualified training images.
It preserves all 157 ROW545 images and adds 64 original row-containing images from the qualified wider training pool.
Selection uses family round-robin and hashed image IDs. Evaluation predictions do not select training members.
Preflight verifies images, complete annotations, and class mapping. The batch compiler verifies the seven evaluation memberships.
Initialization, learning rates, seed, and 30 epochs remain unchanged. Sampling changes exposure; this is not an equal-update experiment.
The fit permits 1800 s and 2 GiB. Estimated runtime is 24 min from the measured 157-frame fit.
Nineteen jobs include training, seven scores, a decision, seven conditional diagnostics, and three retention reports.
Require all 24 new development rows and no lost Run013 or ROW545 successes. No model promotion follows automatically.
If this targeted rehearsal also fails, implement an explicit class-preserving detector objective with training-only anchors.

## Latest completed review

The targeted rehearsal graph completes. It gains 16 Run013 detections but loses 13.
Against ROW545, it gains 5 detections and loses 7. It fails preservation and cannot replace either baseline.
TTR source publication and bounded consumer replay now pass. See [REAL550](Real550ConsumerReplay.md) for the current measurement limits.
The next training correction needs a class-preserving objective with training-only anchors. Repeating corpus expansion is not justified by these results.
