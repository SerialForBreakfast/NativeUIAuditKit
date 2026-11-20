# Maximum-mini-NUIAK nightly review for November 11, 2026

Window: 2026-11-09 07:47:40.449 UTC through 2026-11-12 07:45:37.038 UTC. The last filed review ends at the start of this window. The November 11 partial snapshot contains no completed report or attempt ledger. [Attempt ledger](../reports/work/NIGHTLY-20261112/attempts.json)

## What improved

The comparative selector at threshold 0.50 improves correct focus from 2/36 to 14/36 on matched tvOS development screens with Standard proposals, with 1 previous success lost. The 2 conditions scored 305 proposals on the same 42 screen IDs. Wrong focused selections fell from 31 to 7. Abstentions on focused screens rose from 3 to 15. False selections fell from 6/6 to 0/6 on known no-focus screens. These provisional counts come from saved per-frame outcomes. Joe has not accepted a headline metric or model. [Matched development results](../reports/work/RESET604/comparative-focus-armb-v1.json)

## What we learned

The comparative Python and Swift paths agreed on all 42 winner or abstention decisions. Neither path supplied evidence of matching per-crop input bytes across both implementations. The earlier FocusRing comparison matched 40/42 decisions. Cold CLI timings do not measure in-app latency. [Comparative parity](../reports/work/RESET604/parity-report-armb-v1.md) · [FocusRing parity](../reports/work/RESET604/parity-report-v2.md)

The TVCatalog Description screen reconciled 8/8 expected controls and identified the focused tab. The pilot reported zero static text items classified as controls. This covers one instrumented scene. The Fixture report records 3,214 reconciled frames from 7 non-scrolling layouts. After deduplication and family exclusion, the v3 detector membership adds 1,592 training rows. It contains 6,320 rows including calibration. The source split decision keeps generator-only calibration. [TVCatalog evidence](../reports/work/RESET604/tvcatalog-sdk-pilot/reconciliation-report.json) · [Fixture counts and split decision](../reports/work/RESET604/comp-capture-v1-v2.md)

## What regressed

The comparative selector abstained on 15 focused development screens. On synthetic held-out scenes it still selected a control on 75/188 no-focus frames at threshold 0.50. Those frames share layouts. The first composition batch rejected 56 light-theme recipes. The second preserved source themes and recorded zero rejected recipes. Scrolling and occlusion still need independent coverage. The real-app qualification manifest contains 0 cases. The 20 reviewed Office cases now have development-regression status. [Focus results](../reports/work/RESET604/comparative-focus-armb-v1.md) · [Qualification manifest](../dataset/real_apps/tvbench-v1/sealed-manifest-v2.json)

## What runs next

Maximum-mini-NUIAK should extend the successful SDK annotation check to a second populated route. Verify control completeness, focus, app identity and settlement against independent references. Joe's review of complete controls in a second app releases Gate 2. Missing or contradictory evidence returns the scene to annotation repair.

Four existing T107 specifications compare D1 and focus-as-class on v2 memberships at seeds 371 and 372. Both membership hashes still match the plan. Each fit allows 100 epochs, 12 h and 2 GiB. The plan estimates 564 min per fit. Its primary outcomes are complete-screen recall and official AP50 across NewsTV and the second app. Stop if gains fail to repeat or stay confined to NewsTV. These specifications vary supervision and membership together. To test the added composition training data, prepare a separate immutable v2/v3 comparison with the same detector objective and fixed exposure. Do not substitute v3 into submitted configurations. [Matched plan](../reports/work/RESET604/d1-matched-experiment-plan.json)

## Queue health

The live runner reported continuous mode, no active job, and no error. Cached readiness came from November 11 at 18:21 UTC. It showed 0 ready jobs, 0 ready seconds, 451 blocked and 129 exhausted. Of the 451 blocked jobs, 440 listed a dependency reason. Another 8 awaited approval and 29 branches were unselected. Ready duration for RESET604 is 0 verified hours. The 4 dependent T107 fits represent about 37.6 estimated hours. No job was admitted, released, continued or restarted. [Health](../reports/work/NIGHTLY-20261112/health.json) · [Readiness snapshot](../reports/work/NIGHTLY-20261112/state.json)

The detached queue recorded 0 completed and 0 failed attempts in this window. Their measured occupied intervals were each 0 s. The remaining 259,077 s have no recorded queue execution. Continuous machine idle time cannot be inferred because separate training, capture and parity work produced artifacts. [Attempt ledger](../reports/work/NIGHTLY-20261112/attempts.json)

## Blockers and approvals

BigDog-Coordinator forwarded Sillycon-TTR's published Office target fix. Maximum-mini-TTR HEAD matches the requested revision. The live comparison of Workspace, Remote, preview and recorder identities remains open. BigDog-Coordinator stored the revision receipt at cursor 2066. Peer forwarding of that receipt remains unverified. No repeat Office capture is required. [Coordinator reply](../reports/work/NIGHTLY-20261112/peer.json)

## Priority changes and reasons

Prioritize SDK labels for the second app and a matched no-focus comparison on fresh development flows. These determine whether detector gains transfer and whether focus gains survive new layouts. Additional scoring on the same 6 no-focus screens cannot answer either question. Keep iOS and optional HCF under the maintainer's RESET604 pause. The legacy catalog has no newly selected eligible branch. Preserve existing specifications. [Active tasks](../Tasks.md) · [Catalog check](../reports/work/NIGHTLY-20261112/catalog-check.json)
