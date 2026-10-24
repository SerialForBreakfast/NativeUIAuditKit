# Retained SDK and temporal comparisons

Date: October 24, 2026. Owner: Maximum-mini-NUIAK.

## Completed work

The background runner completes 3 independent job specifications across 2 investigations.
All completed output hashes verify. Standard and shipped models remain unchanged.

| Comparison | Result | Decision |
|---|---|---|
| Scoped versus general detector on SDK504 pixels | Scoped covers 7/8 registered boxes. General covers 6/8, with 1 gain and 2 losses. | Keep the scoped source. Test combined proposals before considering replacement. |
| Temporal seed 42, ordered pairs versus repeated after frame | Ordered pairs classify 4/4 correctly. The intervention classifies 2/4 correctly and misses both changes. | Temporal information helps on these retained calibration pairs. |
| Temporal seed 44, same comparison | Same 4/4 versus 2/4 result. No unchanged pair becomes a false change. | The finding repeats across these 2 retained candidates. |

These are small diagnostic results. The 2 SDK frames share 1 ancestry group.
The 4 temporal pairs also share 1 ancestry group. They retain their calibration role.
Repeated-after input is an intervention, not a single-frame classifier.
Scroll observations do not qualify arbitrary moving backgrounds or observed no-focus scenes.
No model qualifies for release from this tranche.

## Geometry correction

The first geometry attempt fails after saving general-detector predictions.
The adapter incorrectly reads `id` instead of `identity.id` from the existing packet consumer.
The corrected successor reuses both verified prediction files. It runs only the remaining scoped inference.
The failed attempt and its outputs remain intact.
Tests now use actual native consumer rows, plus missing, ambiguous, invisible, and invalid geometry cases.
Six focused geometry and transition tests pass after the correction.

The scoped detector misses `grid_cell_0_0` in `grid-opposite`.
The general detector recovers that control but misses `grid_cell_1_1` in both frames.
The union covers all 8 registered boxes at IoU 0.5.
This coverage calculation does not establish precision or correct focus selection.
Next, score combined proposals against retained successes and known negatives before changing any proposal policy.

## Helper diagnosis and TTR reply

The pinned app and helper have sandbox entitlements. The running Developer Tool app and helper do not.
Both app bundles declare the same bundle identifier and version.
TTR's `ProjectEvidenceStorage` uses `NSHomeDirectory()` for its default workspace.
Sandboxing changes that directory. This is a likely connection cause, not a verified repair.
No workspace, security boundary, or pinned comparison specification changes.

TTR reply 1357 reports 9 recovery trials and 10 replays with verified restoration.
Those results remain peer evidence. The source changes remain uncommitted; local qualification waits for exact source availability.
TTR confirms the current collector produces focused single frames only.
Native no-focus, action-linked packets, and complete detector inventory remain producer gaps.
Maximum-mini-NUIAK sends exact executable/helper hashes and confirms the required fields in request `nuiak-sdk506-build-identity-20261024-v1`.
The coordinator stores that request at cursor 1358. Delivery remains unconfirmed.

## Evidence

- [Geometry request](../reports/work/SDK506/request-r2.json)
- [Geometry result](../reports/work/research-queue/jobs/sdk506-matched-geometry-r2/attempts/1/out/benchmark_summary.json)
- [Temporal seed 42](../reports/work/research-queue/jobs/sdk506-temporal-42/attempts/1/out/benchmark_summary.json)
- [Temporal seed 44](../reports/work/research-queue/jobs/sdk506-temporal-44/attempts/1/out/benchmark_summary.json)
- [Build identities](../reports/work/SDK506/build-identities.json)
- [TTR replies](../reports/work/SDK506/ttr-replies.json)

These diagnostics take seconds, not an overnight workload. No ready-duration claim follows from their job count.
