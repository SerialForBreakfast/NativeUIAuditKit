# COEFFICIENT-REPLAY-144 — feasible native fit; robustness still fails

One DTM043 equivalent LP now preserves every nonzero solver coefficient above the
resident1e-9threshold. Row and rhs amplification leaves the original problem and
norm objective unchanged. Maximum amplification458300.55, smallest retained
coefficient~1e-8. No changed labels or weakened acceptance gates.

## Result

PID35829,41iterations,5.037130seconds solve/7.239766total; original maximum residual
1.364242e-12 passes. Finite diagnostic checkpoint saved and exact reload replay
passed through the actual float32 transition head on all retained views.

- All9admitted native cases correct:5within-screen,2screen transitions,2identical.
- All207original cases and226identity cases retained; prior correct contrast subsets retained.
- Actual .85/.15decision margins pass all993constraints.
- Extra margin TARGET=logit(.85)+.001 fails narrowly in float32: minimum1.73558044.
- Contrast-negative correctness219/226both; global8correct220/226 (4false changes,2abstentions).
- Localized-left correct34/226 (191false changes,1abstention); center correct9/226
  (207false changes,10abstentions). These failures prevent replacement.

This proves the existing features can fit the exposed native cases jointly with
the retained constraints; it does not prove independent native generalization or
complete nuisance robustness. No promotion/export or new TTR artifact.

## Evidence and checks

Command: resident Python `scripts/conditioned142.py --strict --preserve-coefficients
--ready reports/work/COEFFICIENT-REPLAY-144/artifacts/ready`; bytecode disabled,
project-local TMPDIR, two BLAS threads. Result:
`NativeUITrainer/focus_ring_runs/coefficient144-dtm043/result.json`.
Checkpoint SHA25615e57c83a8da8973ed9c972a31d72474bf1f84de76efcb53935091b71f156ca3.
Protocol SHA2566b3776044900163403d0ff0b2157415f66f13002e0bc187a1c462e7145af1452.
Prior143source preserved at its ready directory as `conditioned142-source.py`.

43Python tests pass in0.560s; equivalent row/rhs scaling, coefficient retention,
unsafe amplification rejection, original objective and all prior regression checks.
Offline Swift build and explicit serial tests pass:14XCTest+128SwiftTesting checks.
Logs `.build/coefficient144-{build,test}.log`; established project-local cache paths
and scoped native-test host permission. No source changes after verification.

Software verified; existing data eligible only for this scoped exposed diagnostic;
no fresh producer integration; model gate failed. Model-workflow skill kept real
decision success separate from extra-margin failure and independent qualification.
All pre-existing work, rejected evidence and shipped models preserved. No Git write.

## Next substantial tranche

Freeze an explicit nuisance-data role decision and verify generated transformations
preserve focus before fitting them; retain all existing native/old constraints.
Quantify float32 cancellation to set a preregistered safety margin, not relax the
runtime gate after seeing results. Execute one joint constrained comparison and
report all family-level false changes/abstentions. Independent real native-motion
coverage remains a separate TTR qualification need, not a blocker to local diagnosis.

TTR snapshot unchanged18:46:20Z/expired19:46:20Z. Worker141 still awaits environment
authority. Peer consequence: exposed native fit is possible; no replacement model
is available, keep passive DTM030/DTM025 use unchanged. Publication tracked separately.

Published/read back `packets.COEFFICIENT-REPLAY-144` in verified
`/Volumes/SharedStatusFile/nuiak/status.yaml` at21:40:08Z, with all other semantic
fields preserved. Peer acknowledgment not observed. Metadata only, no artifact
transfer and no new TTR execution request.

Read-only follow-up before worker redirection measured maximum float32 weight
rounding logit error8.486e-6, accumulation error4.671e-5, combined5.372e-5 on993cases.
17rows miss the extra target; worst deficit2.061e-5. Existing226identity pairs
are exactly equal at source; all three lighting transforms leave first frame and
padding unchanged. This mechanical check does NOT admit localized transformations
as semantically valid training negatives. No further role change or fit occurred.

## Batch-size precision audit

Read-only actual `net.change` replay on the same993source-bound constraints, CPU
two threads, no optimization. Reconstructed float64 reference uses the preserved
solver weights; float32 model uses the saved checkpoint. All five tested batches
retain993/993correct decisions with zero abstentions:

| Batch | Max logit error vs float64 | Min signed margin | Extra-margin failures | Max delta vs batch993 |
|---|---:|---:|---:|---:|
| 1 | 8.34972e-5 | 1.73555565 | 16 | 1.22070e-4 |
| 8 | 7.13400e-5 | 1.73555374 | 16 | 9.15527e-5 |
| 16 | 5.37244e-5 | 1.73558044 | 17 | 0 |
| 32 | 5.37244e-5 | 1.73558044 | 17 | 0 |
| 993 | 5.37244e-5 | 1.73558044 | 17 | 0 |

This demonstrates batching-sensitive floating-point arithmetic without observed
decision changes on this exposed set. It is not a bound for arbitrary unseen
features or CUDA/CoreML. Preserve the failed extra-margin gate; future comparisons
must record batch/backend and verify decisions separately from exact same-backend
checkpoint replay. No universal cross-backend exact-logit equality requirement.
