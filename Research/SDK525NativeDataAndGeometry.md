# SDK525 — Native data intake and detector recovery

October 25, 2026. Owner: Maximum-mini-NUIAK.

## Delivered

The exact TTR source revision is `e4c693c5237b8498a23e60d51c104ee5f7600a16`.
The Developer checkout contains this revision on `master`, not a branch named `main`.
NUIAK pins all 30 portable Ruby files directly from Git objects.
No TTR source, personal Xcode files, services, or Simulator state change.

Portable checks pass: 26 continuity checks, 19 training intake checks, and 10 scoped crop checks.
Their imported pair, profile, and provenance checks also pass.
This verifies portable source behavior. It does not qualify a native build or admit training data.

## Native training remains blocked by evidence

The current source audits all 48 retained pairs across 8 groups and 56 unique images.
No cohort leakage appears. Zero pairs qualify as training review candidates.
All 48 lack observed profiles, profile timestamps, and supervisor timing.
Another 16 carry unverified content motion.
The update cannot reconstruct missing historical observations.

Coordinator message 1460 stores the exact source receipt and remaining requirements for Sillycon-TTR.
Forwarding and acceptance are not yet confirmed.
The request asks for existing eligible exports before any new producer work.
No capture repeats. Historical roles and unknown fields remain unchanged.

For crop training, require observed profiles and independent training/development groups.
For temporal training, require actual action timing and observed transitions.
Visible-control no-focus cases remain necessary for distractor regression tests.
Empty-box no-focus scenes do not establish this safety property.

## Eight detector misses

The misses involve 4 controls across 3 groups:

| Control | Misses | Evidence |
|---|---:|---|
| t1 control2 | 4 | No overlapping proposal. Another endpoint succeeds at confidence 0.315. |
| t5 control0 | 1 | No overlapping proposal. Other endpoints succeed at confidence 0.252 and 0.266. |
| t5 control1 | 2 | Centered text proposals cover only 0.109 and 0.087 of the control by IoU. |
| t6 control0 | 1 | A centered text proposal has IoU 0.057. Other endpoints recover the body. |

All bounds fit the image. These results do not support a global coordinate correction.
The comparison ignores classes. It does not establish taxonomy accuracy.

## Executable comparison

SDK506 now permits one explicit threshold comparison: 0.10 against cached 0.25 outputs.
The adapter requires identical model pins, image size 1280, and unchanged NMS.
The default detector comparison remains unchanged.
Reports include proposal counts, threshold identities, candidate gains, and lost previous successes.
The adapter also removes duplicate evidence paths when both arms use identical weights.

All 9 jobs have exact approvals:

- `sdk525-geometry-01-r2` through `sdk525-geometry-08-r2`
- `sdk525-geometry-report-r2`

The first handoff snapshot has 3 complete jobs, 5 pending scoring jobs, and 1 dependent report.
The health check then confirms the same runner executing group 4.
The first completed receipt verifies the corrected adapter and thresholds.
No service restart occurs.

This is 1 investigation across 8 groups, not 9 independent investigations.
A comparable group takes 4.63 s. The batch is short diagnostic work, not an overnight workload.
Each job retains the 800 s and 100 MB limits.
All 112 previous coverage successes remain in the comparison.
Reject any lost success. More boxes alone do not establish improved focus selection.
Before adoption, require wrong-selection and no-focus regression results on the additional proposals.

## Validation and readiness

All 15 focused Python tests pass. The offline Swift suite passes all 177 tests.
The initial Swift attempt finds a cache containing the parked checkout path.
A new project-local module cache resolves the problem without deleting existing evidence.
The passing Swift test run takes 51.564 s.

The completed `tvos511-size-r2-decision` receipt verifies.
Its obsolete predecessor now has an explicit reconciliation link.
No producer or inference job repeats for this cleanup.

## Next steps

1. Review the combined threshold report and its additional proposals.
2. Use qualified native training groups when the producer supplies the missing evidence.
3. Keep crop, temporal, and detector eligibility separate.
4. Investigate the slow global readiness snapshot as independent workflow work.

Standard, shipped models, and previous success records remain unchanged.
No model is promoted.

Compact qualification, source pins, audit results, approvals, and logs remain in `reports/work/SDK525/`.
