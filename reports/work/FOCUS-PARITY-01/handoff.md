# Focus integration replay: concrete preprocessing mismatch

Superseding continuation: user approved the native runner. The genuine Settings
recording and 16-case replay completed; see
[live handoff](../OS-FOCUS-01/live-20260922-0712/handoff.md). Approval-pending notes
below are retained as the historical offline checkpoint, not current blockers.

2026-09-22 UTC. NUIAK architect. Offline slice complete; live recording not run.

| Outcome | Result |
|---|---|
| Software verified | Source-bound replay succeeds; four safety tests and required Swift build/92 tests pass |
| Data eligible | Development-only historical images and synthetic calibration; no training admission |
| Integration qualified | Offline crop mismatch reproduced; live TTR/NUA integration not qualified |
| Model gate passed | Not assessed; no training or replacement |

## Results

[Final report](replay-03/report.json) binds TTR revision/source hashes, model digest,
runtime helper, harness and historical input manifest. Four historical source
images verified against producer hashes; three asymmetric synthetic probes added.
Actual unmodified TTR FocusDetectorService/FocusScoring compiled with mechanically
extracted crop/rectangle dependencies; only a minimal error enum is stubbed.
No app IPC, OCR proposal generation or live control is included. Standalone Swift 5
matches producer language mode, not all of its target isolation/build configuration.

| Historical expected-focused example | Same CPU classifier: NUA crop | Same CPU classifier: TTR crop |
|---|---:|---:|
| Home tile | 1.000000 | 0.567383 |
| Settings VoiceOver row | 0.007092 | 0.000079 |
| Fixture tone button | 0.265625 | 0.031433 |
| Fixture Record button | 0.002890 | 0.000588 |

All four historical crops differ. Home crosses the fixed 0.85 threshold; other
three remain below it. Historical approximate boxes were visually reviewed as
development leads, not independently annotated test membership. These scores do
not measure navigation or full-frame candidate detection accuracy.

Original TTR `.all` backend gives Home 0.580566, repeat identical; NUA `.cpuOnly`
gives 1.0. The controlled comparison above scores both saved crop variants through
the same NUA CPU classifier. Its wrapper recrop is verified decoded-pixel identical
on all 14 saved crops. This isolates preprocessing from backend and weights.
Two uniform synthetic crops are identical; one asymmetric probe differs. Do not
infer parity from uniform images. No TTR zero-score/failure sentinel occurred.

Visual inspection of both Home crops confirms tight icon crop versus retained
surrounding context; inspected Settings variants and expanded Fixture tone/Record
crops too. This proves input mismatch, not which training distribution causes each
remaining miss. Privacy-sensitive raw images remain local.

## Verification / attempts

- `replay-01`: retained compile failure, exit 1; producer actor code failed under
  Swift 6 isolation. Read producer project: Swift 5. No external code changed.
- `replay-02`: exit 0; seven cases, original backend comparison.
- `replay-03`: exit 0; adds controlled same-backend inference and pixel-preservation
  assertions. Report includes elapsed build/replay time. No downloads or training.
- `.venv-yolo/bin/python -m unittest discover -s scripts -p test_focus_integration_replay.py`:
  four pass: exact nested extraction, ambiguous/truncated extraction rejection,
  existing-output and outside-root rejection before peer access.
- `swift build` and `swift test`, offline/project-local caches: exit 0; logs alongside
  this report. 92 Swift tests pass. Peer standalone final build log has no warnings.
- Runtime/model/source hashes rechecked after replay; external inputs unchanged.

Existing .agents changes, TVGEN review, ADR-0010 and iOS reconstruction preserved.
New code: scripts/focus_integration_replay.py, focus_peer_probe.swift,
test_focus_integration_replay.py. Research contract precedes code. No public API,
model weights, producer repository or runtime was changed.

## Remaining test boundary and next actions

Recording portion needs the outstanding explicit approval for the independent
runner install, simulator runtime writes, Settings activation and six directional
inputs on 9026ECA9-77DB-4AE6-8FE6-BB239E9571FA. No answer received during this slice.
Process inventory in restricted execution returned operation-not-permitted; that
is not evidence of occupancy or a simulator failure. Fresh approved target/ownership
checks are still required before recording. Historical screenshots are not a journey.

After approval: bounded recording → review native labels against pixels → ordered
replay and coverage report. Broader Home matrix traversal remains OS-FOCUS-03,
not something this Settings-only probe implements. No training authority inferred.

Producer action: under TTR's own assignment, align actual focus crop geometry with
NUA's 16% expanded top-left/256 contract and add source-bound parity cases before
retraining; preserve abstentions and report loaded artifact identity. Then compare
real OCR/detector candidate boxes separately from these manually injected boxes.
Do not assume parity will fix the remaining three cases or withdraw the independent
Fixture native-identity repair. See coordination.md for delivery/readback status.
