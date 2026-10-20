# DETECTOR469 — Expanded native control training

## Question

Does qualified native training coverage recover missed proposals and improve full-screen Standard focus without losing previous successes?

## Evidence and scope

Standard-only recovery passes in 61.80 s. No capture repeats.
The evidence review initially rejects a differently formatted copy of the original guard.
The successor reconstructs the original serialization and verifies its exact recorded SHA-256 before review.
It reuses the completed restoration and preserves the failed review.

Combined qualification checks 328 capture events across 23 training groups and 10 development groups.
Training contains 184 events and 97 distinct decoded images. The complete partition contains 171 distinct images.
Related events do not establish independent evidence. All results remain development evidence.

## Execution graph

1. Admit exact sources with T53 after native integrity and partition checks.
2. Prepare each control family with T87.
3. Verify complete canonical control labels using the existing label mapper.
4. Train the expanded detector through T89 with pinned initialization and settings.
5. Score matched proposals and full-screen focus through T56 and T57.
6. Compare native families, no-focus scenes, edges, decoration, and new position groups.

Use the completed DETECTOR422-v2 model as the matched training baseline.
Keep the retained original detector reports available. Do not repeat completed baseline scoring.
Freeze crop models, confidence thresholds, proposal matching, and evaluation membership.
Keep known Standard row and tab regressions explicit. A successful fit does not qualify a replacement.

## Budget and decision

Training permits 30 epochs, 2 h, 2 GiB, and 1 attempt.
Each diagnostic permits 800 s and 100 MB.
The existing compiler checks total graph limits before admission.
Use fixed-last selection. Trainer validation is not held-out accuracy.
Reject replacement on lost Standard successes or added wrong selections.
Report uncertain or unsupported conditions rather than inventing accuracy.

Standard and iOS remain unchanged. HCF stays optional. The background runner owns execution.
Compact evidence and configurations reside in `reports/work/QUALIFY469/`.
