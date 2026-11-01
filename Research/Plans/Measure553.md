# MEASURE553 — Real metrics first, then model improvement

Date: 2026-10-31. Owner: Maximum-mini-NUIAK. Task authority: Tasks.md, section MEASURE553.
This plan connects the existing REAL543 benchmark to the actual runtime.
It then uses the benchmark as the single gate for model improvement.

## Problem

All current model metrics come from generated or Fixture images:

| Model | Metric | Population |
|---|---|---|
| iOS `nativeui-ios-v2.0` | mAP@0.5 0.935 | Generated layouts from training templates |
| tvOS `nativeui-tvos-v3.0` | mAP@0.5 0.982 | Generated Fixture layouts |
| Run 013, 41 classes | mAP@0.5 0.6322 on 13 classes | Withheld generated templates |
| Standard focus | Selection counts | Retained Fixture development cases |

No real-app metric exists. NewsTV has 1 captured pilot case without accepted labels.
The production path returns no selection on all 3 retained replays.

Recent candidates improve their target and lose previous successes:

- ROW545, RETENTION547, and IOS551 lose 8 to 16 Run 013 detections.
- DEDUP486 and PROFILE425 HCF lose Standard focus successes.

The runner uses 16.58% of the nightly review window and has 0 ready jobs.
Compute is not the limit. Real data, real measurement, and retention are the limits.

## Goals

1. Produce real-app detection and focus metrics through the actual Standard runtime.
2. Use 1 promotion gate: real benchmark improvement, retention, latency, and no new wrong selections.
3. Improve the detector and focus models only against that gate.

## Workstreams

### M1 — Runtime predictions for the benchmark (REAL543-RUNTIME), P0

TTR ac85177b now reports source revision, preprocessing, taxonomy, and loaded model digests.
The loaded digests match the shipped `NativeUIModel_tvOS` and `FocusRingDetector` compiled trees.

- `scripts/real_app_runtime553.py runtime-receipt` makes a `real-app-runtime-v1` receipt only from observed replay fields.
- `scripts/real_app_runtime553.py predictions` converts audited `visual replay` exports into the REAL543 prediction format.
- A partial provider result stays an abstention. The converter does not remove suppression or invent a selection.
- Crop identity remains unavailable. Reports keep that limitation.

Acceptance: the converter and receipt pass offline tests and run on the 3 retained replays.
Those replays are Fixture cases. They test the path, not real-app accuracy.

Result, 2026-10-31: 18 tests pass. The ac85177b receipt binds detector `86c16915…` and FocusRing `1fe0de31…`.
The 3 replays convert to 2, 6, and 4 detections. All 3 stay abstentions. Receipts: `reports/work/MEASURE553/`.
The taxonomy descriptor records the observed manifest digest. NUIAK does not recompute that digest yet.

### M2 — Promotion gate with paired uncertainty, P0

`scripts/real_app_runtime553.py gate` compares a candidate report with the baseline report on the same freeze.
It uses a paired bootstrap over whole flows within apps, with a fixed seed.
The gate passes only if all of these conditions hold:

- 0 lost focus successes and 0 lost detected controls on the benchmark
- 0 new wrong or false selections
- 0 lost previous successes in the declared retention report
- the 95% interval lower bound of at least 1 primary improvement is above 0
- candidate median latency is at most the declared latency ratio of the baseline

The gate never sets `modelAccepted`. Promotion keeps its separate authority.

### M3 — Real-app benchmark population (REAL543-APPS, REVIEW, PILOT), P0

Use the existing REAL543 protocol: a pilot of up to 50 cases, then 200 qualification cases across 5 apps.
The approved apps are NewsTV, Swiftfin, and Photo Guessing Game. WeatherFeels needs the Metal toolchain.
Moonlight is the recommended 5th app, and Provenance is the reserve. See [REAL543 applications](../RealAppApplications543.md).

- Plan all pilot capture points before the session. Capture them in 1 batched session per target.
- Export SDK drafts for blinded human review. The SDK draft is never a final label.
- Human review takes about 2 to 3 min per screen. The pilot needs about 2 h. The qualification set needs about 8 h.

### M4 — Runtime selection repair (REAL550-FOCUS), P0

One off-screen proposal suppresses every selection. Real-app focus metrics are empty until this changes.
Sillycon-TTR owns the correction. Maximum-mini-NUIAK verifies it on the 3 retained replays and the pilot.

### M5 — Detector improvement with full retention, P1

- Train on the full original data plus reviewed new data. Do not fine-tune from a subset.
- Add reviewed real-app screens from apps outside the benchmark.
- Test 1 larger backbone (YOLO11s) for the 41-class model with a fixed budget.
- Use the M2 gate with Run 013 retention and the real benchmark.

### M6 — Focus improvement through 1 batched native capture session, P1

See [CAPTURE553](CaptureSession553.md) for the grouped sessions.

37 records wait on native captures (T03, T47, T37, T07, and T42). 7 are ready on existing Fixture features.
Prepare their recipes and consumer jobs first. Then capture them in 1 or 2 sessions.
Pause unchanged optional HCF variants until Standard measures well on real apps.

## Order and dependencies

| Step | Needs | Owner | Unblocks |
|---|---|---|---|
| M1 | ac85177b replays (done) | Maximum-mini-NUIAK | M2, pilot scoring |
| M2 | M1 | Maximum-mini-NUIAK | Every candidate decision |
| M4 | TTR correction | Sillycon-TTR | Focus metrics |
| M3 | App qualification, batched capture, human review | Maximum-mini-NUIAK and maintainer | Real metrics |
| M5 | M2, M3 pilot | Maximum-mini-NUIAK | Detector candidates |
| M6 | Capture plan | Maximum-mini-NUIAK | Focus candidates |

## Maintainer decisions

1. Done, 2026-10-31: NewsTV, Swiftfin, and Photo Guessing Game are approved and evaluation-only. The 5th app and the training pool stay open.
2. Name the label reviewer, or request an assisted review tool first.
3. Accept the REAL543 sizes: a pilot of 50 cases and 200 qualification cases across 5 apps.

## Limitations

Simulator results describe Simulator behavior. Physical-device qualification remains separate.
After results inform a model change, those cases become development evidence. Use fresh cases for the next qualification.
