# SDK528 — Independent resolution comparison

October 25, 2026. Owner: Maximum-mini-NUIAK.

## Current results

The iOS additive fit remains running at handoff. The control fit remains pending.
Both retention reports wait for training and scoring. They are dependent work, not unresolved label failures.
The source-built SDK packet remains pending. No new packet or iOS comparison result is available.
No TTR reply appears after coordinator cursor 1466. Forwarding of that request remains unconfirmed.
Standard, shipped models, and prior evidence remain unchanged.

## New independent experiment

Lower proposal confidence recovered geometry but added a wrong focus selection. Do not extend that correction.
The earlier Standard resolution comparison recovered selections on retained native cases.
SDK528 tests whether resolution also changes coverage on the registered SDK control groups.

- Baseline: retained 1280-pixel predictions.
- Candidate: 960-pixel predictions from identical detector weights.
- Fixed factors: source pixels, confidence 0.25, NMS IoU 0.45, groups, and labels.
- Scope: 56 retained frames across 8 related groups.
- Metrics: registered-control coverage at IoU 0.5, gained controls, lost controls, and proposal count.
- Limits: 800 s and 100 MB per job.
- Expected duration: approximately 40 s from comparable group runtimes.

All 8 comparison jobs and the combined report have exact approvals.
This is 1 investigation. It is short independent work, not an overnight workload.
All 112 baseline coverage successes remain in scope.
Incomplete annotations prevent detector precision and taxonomy claims.

If resolution recovers controls without losses, compare actual focus selections before considering a runtime correction.
If it loses controls, reject standalone replacement and inspect case-linked differences.
If it recovers nothing, stop this resolution branch.
No automatic model promotion occurs.

## Native training boundary

SDK packet acquisition must finish before its geometry and observed focus can be verified.
Profile-specific training also requires observed Focus Style evidence and reviewed group membership.
The current SDK sample does not supply those fields by itself.
TTR supplies a supported native Settings readback collector. It needs an owned session and the exact observed Settings row.
A saved historical profile cannot certify a new capture. Contrast does not establish HCF.
Current coordinator request 1466 asks for the supported profile-evidence connection.
The sample enrollment expires after 30 min. Preserve any expiry failure before refreshing enrollment through supported setup.
No application restart, additional capture, or settings change occurs during this review.

## Verification

All 14 geometry adapter tests pass. They cover the 960-pixel runtime path, baseline reuse, and rejection of mixed changes.
All 177 Swift tests pass in 56.101 s. These tests do not establish a model improvement.

## Evidence

- [Approved batch](../reports/work/SDK528/admitted.json)
- [Handoff state](../reports/work/SDK528/handoff-state.json)
- [Geometry tests](../reports/work/SDK528/geometry-tests.log)
- [Swift tests](../reports/work/SDK528/swift-tests.log)

## Next substantial tranche

1. Review both iOS retention graphs and select a correction only from measured gains and losses.
2. Verify the SDK packet, then connect native profile evidence to crop preparation.
3. Use SDK528 coverage results to select a complete focus comparison with retained regressions.

The detached runner owns execution. No schedule, commit, or model promotion is added.
