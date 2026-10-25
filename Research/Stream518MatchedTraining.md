# STREAM518 — Capture closure and longer matched training

Owner: Maximum-mini-NUIAK. Date: October 24, 2026.

## Completed capture comparison

All 4 session arms complete with matching labels and verified cleanup. Each arm supplies 8 endpoint images.
The retained first and second sessions are reused. No captures repeat during recovery.
Separate sessions total 62.08 s. Reused sessions total 55.99 s.
Do not claim a speedup: the helper changes after the first arm, and the paired repetitions disagree.
The report remains inconclusive for timing. Label parity and cleanup pass.
Original captures, data roles, and failed attempts remain preserved.

## iOS confidence results

Lowering confidence from 0.5 to 0.25 recovers 21 Run013 detections with zero lost detections.
The same change recovers 27 IOS516 detections with zero lost detections.
At confidence 0.25, IOS516 still gains 19 and loses 28 against Run013.
Run013 has 241 unmatched predictions; IOS516 has 297. These are not verified false-positive counts.
These findings show partial threshold suppression, but they do not qualify a threshold change or candidate replacement.
Keep Standard and shipped models unchanged. Require independent negative coverage before threshold promotion.
All 28 completed capture and iOS results pass specification and output-hash checks.

## Longer work admitted

Two independently runnable training arms use the existing T89 compiler and matched comparison templates.

1. Additive arm: unfreeze the backbone while retaining learning rate 0.0001 and all 144 qualified images.
2. Original-only arm: use the same settings and the original 128 images, excluding the 16 native additions.

Both initialize from Run013. Both preserve the fixed seed and 30 epochs.
Each fit permits 1800 s, 2 GiB, and 1 attempt. Total training ceilings are 3600 s and 4 GiB.
The frozen control takes 747.95 s. Estimate 15–25 min per full-backbone fit; actual runtime remains unmeasured.
The original-only membership exactly matches 128 images in the additive membership. Only 16 native images differ.
Different image counts also change optimizer updates. This is a practical membership comparison, not an exposure-controlled causal test.

The complete graph contains 34 jobs: 2 fits, 12 scoring jobs, 8 reports, and 12 conditional class diagnostics.
Compare against the frozen control, Run013, original-only training, and native-only training.
The paired reports compare both new arms directly. Reject every lost previous success.
Conditional diagnostics run only after regression. No automatic retraining or model promotion follows.
Training validation remains training diagnostics, not held-out accuracy.

At handoff, ios518-unfrozen-train runs. ios518-control-train is ready independently.
The other 32 jobs wait for dependencies or outcome conditions. They are not 32 actionable failures.
This gives approximately 30–50 min of useful training, plus comparisons. It does not fill an overnight window.
The detached runner retains execution ownership. No restart occurs in this tranche.

## TTR reply and next data step

Sillycon-TTR reports 48 retained action pairs across 8 groups and 56 unique images.
Old timing and profile gaps remain explicit. These pairs are review-only, not training data.
TTR reports cleanup recovery, but a fresh after-profile check still refuses an unconfirmed foreground app.
Its next producer work concerns supported activation and measured freshness/IPC latency. No NUIAK runtime retry is requested.
New source remains uncommitted. NUIAK requires a pushed Git revision for qualification.

Coordinator request 1431 asks for one named retained archive, size, SHA256, member manifest, roles, exclusions, and source revision.
The request asks for existing evidence only. It authorizes no new captures or training admission.
The coordinator confirms storage. Forwarding remains unconfirmed.

## Next decisions

- If both new fits regress similarly, prioritize general fine-tuning preservation rather than native-data generation as the sole correction.
- If only the additive arm regresses, investigate native membership, label compatibility, and exposure effects.
- If a candidate preserves all successes, qualify independent coverage and consumer behavior before promotion.
- Use the retained 48 pairs to broaden native layout diagnosis after archive verification. Preserve all unknown labels.

## Evidence and validation

Receipts: reports/work/STREAM518/verified-results.json and handoff-state.json.
Graphs: reports/work/STREAM518/ios/ and reports/work/STREAM518/control/.
Existing template preflight, input hashes, label checks, membership exclusions, and exact approval checks pass.
No execution code changes. The earlier broad Swift test stall remains unresolved; no new Swift test pass is claimed.
Measured preparation from the first saved training request: 3.1 min. Initial review is not timed separately.
The initial estimate was 15–30 min for preparation, excluding runner execution.
