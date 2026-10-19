# WORKFLOW442 — Representative admission and recovery qualification

Date: 2026-10-18. Owner: Maximum-mini-NUIAK.

## Decision

Use the transaction option for explicitly approved campaign groups of 1–10 jobs.
Keep the individual approval path as the default and fallback.
The option reduces repeated store writes without changing execution ownership or approval checks.
No live jobs receive approval during this qualification.

The worker account remains postponed. Standard and shipped models remain unchanged.

## Measurements

The comparison uses a disposable copy of the 77,831,555-byte approval store.
Each arm uses identical specifications and the resident approval checks.
Each arm preserves all existing records and historical events.
Three samples run per arm and size. The order alternates between samples.

| Exact approvals | Individual median | Transaction median | Observed ratio |
| --- | ---: | ---: | ---: |
| 5 | 6.996 s | 2.875 s | 2.43× |
| 10 | 14.231 s | 4.826 s | 2.95× |

Transactions reduce store writes from 5 or 10 to 1.
Transaction lock duration ranges from 2.754 s to 4.827 s.
Individual lock duration is not separately measured.
These are warm-cache observations on one host. Other qualification tests run during part of the measurement.
The result supports opt-in use, not a universal performance guarantee.
The source queue receives no writes. Its concurrent updates are not copied back or overwritten.

Compact evidence: `reports/work/WORKFLOW442/admission-measurements.json`.
Disposable copies contain no image or model payloads and are removed after measurement.

## Recovery checks

The test starts an owned child process against an isolated queue.
It kills that process immediately before or after atomic store replacement.
Before replacement, the prior store remains unchanged. Retry publishes each approval once.
After replacement, retry finds the existing approvals and publishes nothing.
The process lock releases after termination. Interrupted temporary files never become authoritative records.
Tests clean their own disposable queues. They never kill a runner or worker.
These checks establish process recovery, not recovery from power loss or damaged storage.

Existing tests cover concurrent duplicate requests, concurrent revocation, input changes, source changes, and exhausted storage.
A revoked ID cannot receive automatic approval. Use a reviewed successor specification instead.

## Integration

`workflow_campaign439.py` accepts `--approval-transaction` with explicit repeated `--approve JOB_ID` arguments.
The command requires `--register`. It refuses an empty selection or more than 10 selected jobs.
It validates the campaign before registration. Every approval names the exact compiled specification hash.
The transaction repeats input and source checks before publication.
Capture ownership checks remain outside this optimization. Use the existing capture admission path.

Registration and approval remain separate operations. Failed approval can leave registered, unapproved jobs.
Retry uses the same immutable specifications. It does not restart completed attempts.
The background runner retains dispatch authority. The command never starts the runner.
The isolated campaign test runs the selected branch and verifies retry creates no additional attempts.

## Next workflow priority

Use this command for the next approved Standard comparison with compatible detector proposals.
Retain the existing regression cases and automatic decision report.
Measure authoring-to-ready time on that real campaign before adding another workflow abstraction.
Admission optimization does not create useful experiments or establish overnight queue capacity.

## Final validation

The integrated Python run passes 60 tests in 75.246 s.
An additional test passes for rejecting the test actor on the live queue identity, even with explicit opt-in.
Offline Swift validation passes 177 Swift Testing cases and 14 XCTest cases.
The Swift Testing run takes 54.464 s. Whitespace checks pass.
The runner keeps PID 77776. No runner restart or live approval occurs.
Logs remain in `reports/work/WORKFLOW442`.
