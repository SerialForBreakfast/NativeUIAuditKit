# STREAM516 — Capture readiness, SDK construction, and iOS correction

## Completed work

The intended tvOS Simulator is already booted. Its UDID is `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`.
The matching Maximum-mini-TTR helper passes readiness. Ownership is clear.
The Fixture listener maps to that Simulator. Fixture binary hashes match the approved configuration.

The queued capture configurations use an older helper that cannot connect to the running app.
Three immutable successors now use the matching helpers. They preserve campaign IDs, recipes, target, roles, and budgets.
The completed first session remains retained. No captures repeat.
The r6 validator correction is active after one approved idle restart. Positive and negative scope checks pass.
All 48 queue, capture, report, and approval-refresh tests pass.
It preserves label failures and forbids timing claims across changed runtimes.

## Independent execution

IOS515 resolution increases lose 329 previous successes against the matched 640 baseline, despite 63 gains.
The Run013 comparison loses 344 successes and gains 65. Reject the resolution change.

IOS516 changes learning rate from 0.001 to 0.0001 on the same 144 qualified training images.
Run013 initialization, frozen backbone, seed, and 30 epochs remain fixed.
The runner starts ios516-rate-train. Its budget is 1800 s and 2 GiB.
The graph has 17 approved jobs: 1 fit, 6 scores, 4 reports, and 6 conditional class diagnostics.
This is 1 independent investigation. Comparable training takes approximately 13–16 min. This does not fill an overnight queue.
No model promotion follows automatically. Standard and shipped models remain unchanged.

## SDK construction

Exact TTR source commit: `630969a4371adf96446142e3ed4d20dbfeb1c181`.
The portable construction checker passes for 8 layouts: 6 training constructions and 2 development constructions.
It defines 48 case slots. Training eligibility remains false. Observed focus profiles remain absent.
Generated manifest hashes differ from the producer receipt. Exact manifest parity remains unresolved.
BigDog-Coordinator stores request 1415 with the verified receipt and missing requirements. Forwarding is not yet confirmed.

## Remaining work

Activation is complete. The current fit finished before source changes. Sixteen unstarted iOS approvals were refreshed.
Three unattempted capture sessions and the combined report are approved. The runner starts adr493-session-2-r6.
Sessions 3 and 4 wait for their predecessors. The first session remains retained. The old report is explicitly superseded.
The restarted dashboard uses PID 66464. Standard and shipped models remain unchanged.
The broad Swift suite stalled in Vision semaphore waits. Its stack sample and log are preserved.
That suite is incomplete; it is not counted as passed. No Swift source changed.
The report must mark timing as inconclusive because the retained first arm uses an older helper.
Check observed focus profiles before admitting SDK data for training. Keep fresh 48-pair capture outside this approval.
Review IOS516 retention results before selecting another correction.

## Evidence

Local receipts: `reports/work/STREAM516/`.
Capture successors: `reports/work/STREAM516/capture-successors/`.
Compiled iOS graph: `reports/work/STREAM516/ios/compiled/compiled.json`.
SDK audit: `reports/work/STREAM516/construction-check/construction-audit.json`.
