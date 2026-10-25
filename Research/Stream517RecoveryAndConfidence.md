# STREAM517 — Retained recovery and iOS confidence diagnosis

## Verified results

Session 2 completes capture, export, labels, and cleanup. The queue rejects publication because one required dependency receipt was unread.
Its failed attempt remains unchanged. Retained recovery verifies all output hashes and repeats label validation without TTR calls.
The live import completes. Original captures and data roles remain unchanged.

IOS516 loses 21 prior detections and gains 19 against the higher-rate additive control.
Against Run013, it gains 20 detections and loses 35. Reject model replacement.
Against original-only training, it gains 13 and loses 31. Against native-only training, it gains 61 and loses 20.
These are related development observations, not independent release evidence. Standard and shipped models remain unchanged.

## Repair and execution

The campaign adapter now reads each required dependency receipt before dispatch. It rejects failed cleanup before any producer call.
Immutable r7 successors use the verified session 2 import. Only sessions 3 and 4 remain unattempted.
The dashboard restarts once after explicit approval and an idle check. Thirteen pending iOS approvals are refreshed without specification changes.
The runner starts adr493-session-3-r7. Session 4 and the combined report wait on dependencies.
Timing remains confounded by the helper change after session 1. Label parity and cleanup remain useful outcomes.

## Independent iOS experiment

The existing T56 and T65 templates compile 24 jobs for one matched confidence investigation.
Twelve jobs score Run013 and IOS516 at confidence 0.25 across all 6 retained conditions.
Twelve reports compare these outputs with the same models at confidence 0.5.
Candidate scoring also compares the two models at the same lower threshold.
Weights, image size, NMS, labels, and evaluation exclusions remain fixed.
Report missed boxes, class errors, localization errors, gains, losses, and unmatched predictions.
Unmatched predictions do not establish false-positive rates. No production threshold or model changes follow automatically.
If lower confidence recovers boxes without losses, prioritize independent negative coverage and calibration qualification.
If misses persist, prioritize localization or training coverage instead of another rate sweep.

At handoff, this tranche has 1 running job, 4 ready jobs, 11 dependent jobs, and 11 completed jobs.
These counts cover the 3 capture/report successors and 24 iOS jobs. Dependent jobs are not actionable failures.
This is a short diagnostic batch. It does not meet the overnight-work target.
The completed session 2 took approximately 49 s. Each remaining capture retains the approved 800 s and 250 MB ceiling.

## TTR coordination

Canonical manifest SHA256 matches: df9c88c2ac9b6a22a9563a98a3277fb98d432aa74c80ee51f437db027eaa2d64.
The prior byte difference is whitespace. Preserve original hashes.
The proposed session bracket is acceptable for bounded qualification with its external-change limitation explicit.
Require matching observed Focus Style, exact target and capture identities, ordered brackets, exclusive ownership, and a complete action ledger.
Reject missing or conflicting evidence. Do not backfill old unknown profiles or treat inferred profile continuity as observed control focus.
Coordinator request 1425 returns these requirements. Storage is confirmed; forwarding remains unconfirmed.
The new TTR source remains uncommitted according to the peer. Obtain a pushed Git revision before source qualification.
No new 48-pair capture is authorized by this review.

## Validation

Positive retained recovery completes through an isolated queue. An unsupported failure is rejected through the same queue.
Fifty-one focused tests pass. Two additional tests verify dependency consumption and rejection before dispatch.
The prior broad Swift suite stalls in Vision; it remains incomplete. No Swift source changes in this tranche.
Git diff whitespace checks pass.

## Next priority

Review both completed capture arms and the iOS threshold reports together.
Qualify the pushed TTR continuity implementation and its positive and negative evidence.
Prepare independent SDK training groups only after profile and role requirements pass.
Do not extend rejected training recipes merely to occupy the runner.

Evidence: reports/work/STREAM517/verified-results.json, activation-admission.json, handoff-state.json, and ios/compiled.json.
