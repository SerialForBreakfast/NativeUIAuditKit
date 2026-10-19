# WORKFLOW438 — Reliable graph review and complete outcome summaries

Owner: Maximum-mini-NUIAK. Date: 2026-10-18.

## Implemented changes

- Fixed the browser scope error in completed-history rendering.
- Added a browser initialization test instead of testing only exported graph functions.
- Show root requirements separately from dependent jobs that wait on them.
- Keep changed-source records visible as actionable failures, not completed history.
- Do not treat a superseded failed producer as a successful dependency.
- Distinguish unselected outcome branches from failed execution.
- Keep inconclusive conditions actionable. Do not present them as completed research.
- Show supplied typed conditions in node details. State explicitly when the snapshot omits them.
- Report every comparison slice in the multi-graph review, with Standard first.

The viewer remains read-only. Refreshing the page loads the JavaScript without restarting the runner or companion.
The current snapshot omits owner and condition fields. The viewer does not invent them.
Publishing those fields requires a separate snapshot change at an approved maintenance boundary.

## Standard decisions

The 4 graphs complete all 32 decision jobs. All 4 outcomes are contradicted under their frozen preservation rules.

| Comparison | Standard gains | Standard lost successes | New wrong Standard outcomes |
| --- | --- | --- | --- |
| Standard-only versus retained mixed model | 6 consumer crops | 3 known-box selections and 1 consumer crop | 0 |
| Without button versus Standard-only | 1 consumer crop | 6 consumer crops | 6 |
| Without row versus Standard-only | 1 consumer crop | 6 consumer crops | 6 |
| Without tab versus Standard-only | 1 consumer crop | 2 consumer crops become abstentions | 0 |

Consumer crops and frame selections are different measurements. Do not add these counts as independent trials.
The consumer comparisons cover 20 crop observations from 1 group.
Known-box and proposal comparisons cover 72 observations per profile from 21 groups.
Standard raw proposals show no recovered selections. All 68 focused observations remain misses, with 4 correct no-focus abstentions.
These results do not qualify a replacement. Standard and shipped models remain unchanged.

Case-linked evidence remains in each decision job's `decision.json`.
The combined report is `reports/work/WORKFLOW438/standard-review.md`.
It includes all profile and comparison slices instead of showing only unchanged Standard proposal totals.

## Next useful work

1. Diagnose the 3 lost tab selections and the retained positive consumer crop before another profile-training correction.
2. Use compatible detector proposals for the next full-screen comparison. Empty Standard ring proposals cannot test classifier improvements.
3. Resolve native evidence storage, verify recovery, and admit the frozen capture branch.
4. Add exact owners and typed conditions to snapshots during a maintenance boundary.

The runner is active but has no ready jobs at the browser check.
Do not repeat failed candidates merely to occupy compute. Do not count blocked capture graphs as ready time.
This tranche adds no training, capture, retry, scheduler, or model acceptance.

## Validation

Focused checks cover browser initialization, source drift, root blockers, normal waits, typed conditions, cycles, and invalid ETA evidence.
Both Cytoscape layouts pass headless checks. A 2,500-job workflow projection takes about 19 ms in one local test.
The browser shows the workflow panel and collapsed history without an exception.
Python checks cover read-only transport, hostile text, missing evidence, and losses outside the raw-proposal slice.
Integrated Swift validation uses the separate USB module cache from WORKFLOW437.
All 28 focused Python tests pass in 14.705 s. JavaScript projection and browser-context tests pass.
All 177 integrated Swift tests pass in 53.444 s of test execution.
Logs remain under `reports/work/WORKFLOW438`. No runner or companion restart occurs.
