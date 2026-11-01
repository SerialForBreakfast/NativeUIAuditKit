# REALAPP554 — First real-app measurements

Date: 2026-10-31. Owner: Maximum-mini-NUIAK. Priority: P0, highest.
Parent: [MEASURE553](Measure553.md) workstream M3. Protocol: [RealAppValidation543](../RealAppValidation543.md).
Task authority: Tasks.md, section REALAPP554.

## Current state

No real-app metric exists. The table shows the evidence today.

| Item | State |
|---|---|
| Benchmark apps | NewsTV, Swiftfin, and Photo Guessing Game are approved, evaluation-only |
| Source builds | All 3 pass |
| Captured cases | NewsTV: 1 case, captured while a system alert covered the app |
| Human-reviewed labels | 0 |
| Runtime bridge (M1) and gate (M2) | Implemented and tested |
| Standard focus selection | 0 selections on all retained replays (REAL550-FOCUS) |

## Status — 2026-11-01

RA554-01 to 09 are done. RA554-10 is counted; the message to Sillycon-TTR is not sent.
First baseline, rechecked: [baseline report](../../reports/work/REALAPP554/pilot-v2/baseline-report.md).
Provisional numbers: [provisional report](../../reports/work/REALAPP554/provisional-report.md).
The notification prompt caused the NewsTV inactive state. The patched build is active on 62DA0048.

## New finding: the NewsTV inactive state

NewsTV requests notification permission at launch.
The Simulator log shows the request on 2026-10-29 at 18:17:33 and "Show notification user authorization prompt".
PineBoard then sets deactivation reason `systemModalAlert` for the app scene.
The alert stays in all NewsTV trials on Oct 29, Oct 30, and Oct 31 on Simulator 9026ECA9.
This explains the REAL550-SDK-STATE findings: SwiftUI `inactive`, focused item nil, and the interruption flag.
The cause is local app state, not an SDK defect. Task RA554-01 tests this explanation.

## Tasks

Each task names the owner, inputs, steps, acceptance, and estimate.
Tasks RA554-01 to RA554-07 need no new authority. RA554-08 and later need decisions or peer work.

### RA554-01 — Remove the NewsTV notification prompt from the benchmark build (P0, 30–45 min)

Owner: Maximum-mini-NUIAK. Input: the controlled-content patch in `scripts/sdk539/newstv/`.

1. Add a controlled-content condition that skips the notification authorization request.
2. Record the change in the NewsTV source receipt. Keep all other app behavior unchanged.
3. Build NewsTV from the pinned source with the patch.
4. Install it on clean Simulator 62DA0048 (RA554-03).
5. Repeat the bounded scene diagnostic from `reports/work/REAL543/news-scene-diagnostic/`.

Acceptance: the log has no `systemModalAlert` for NewsTV.
The scene state is active, the focused item is not nil, and the SDK reports no interruption.
If all checks pass, close REAL550-SDK-STATE and tell Sillycon-TTR that the cause was local.
If a check fails, keep the receipts and report the exact disagreement.

### RA554-02 — Check for system alerts before each capture session (P0, 20 min)

Owner: Maximum-mini-NUIAK.

1. Add a preflight check that queries the Simulator log for `systemModalAlert` since the app launch.
2. Fail the session start when an alert is present. Report the alert text through Vision OCR, not a displayed image.
3. Add the check to the batching section of the `tvtestrig` skill.
4. Add offline tests for alert present, alert absent, and log unavailable.

Acceptance: the check finds the retained NewsTV alert on 9026ECA9 and passes on 62DA0048.

### RA554-03 — Set up the benchmark Simulator (P0, 15 min)

Owner: Maximum-mini-NUIAK. Target: 62DA0048 (Apple TV 4K 3rd generation, tvOS 26.5).

1. Record the target binding: runtime, device type, Xcode version, and installed apps.
2. Install the 3 benchmark apps from their source builds. Do not install Fixture data apps here.
3. Run RA554-02 after each first launch. Record any prompt and the decision for it.

Acceptance: 3 apps launch with an active scene and no modal alert.
Simulator 9026ECA9 keeps the NewsTV alert. Do not use it for real-app capture until someone answers the alert.

### RA554-04 — Freeze the pilot case plans (P0, 30 min)

Owner: Maximum-mini-NUIAK. Freeze plans before any model output is viewed.

| App | Cases | Flows | Note |
|---|---|---|---|
| NewsTV | 10 | 3 existing planned flows | The existing captured case stays as a failed attempt; capture it again as a new attempt |
| Photo Guessing Game | 10 | Player setup, date game, location game, feedback, completion | Use the controlled-content mode in `scripts/sdk539/photo-game/` |
| Swiftfin | 2–4 | Server selection and sign-in only | Other flows need a Jellyfin server (RA554-11) |

For each case, record the flow, the remote input path from launch, the expected screen, and the group.
Record planned, missing, and rejected cases. Do not replace a failed case.

Acceptance: 1 frozen plan file for each app, with hashes, in `reports/work/REALAPP554/`.

### RA554-05 — Capture all pilot cases in 1 session per app (P0, about 15 min per app)

Owner: Maximum-mini-NUIAK. Uses standing Simulator authority, within the frozen plans.

1. Launch each app once. Run RA554-02.
2. For each case, send the planned remote inputs through the supported TTR Simulator remote route.
3. Wait for settled native focus. Record the scene state, the SDK snapshot, and the screenshot.
4. Keep each failed case with its reason.
5. Clean up: end the app process and check the Simulator state.

Acceptance: each captured case has an active scene, observed or explicitly unknown focus, an SDK snapshot, and a hashed screenshot.

### RA554-06 — Replay every case through the actual Standard runtime (P0, about 1 s per case)

Owner: Maximum-mini-NUIAK. Runtime: Maximum-mini-TTR ac85177b.

1. Run `aatv visual replay` for each screenshot. Keep the output inside the TTR project.
2. Copy the exports to `reports/work/REALAPP554/replays/` and run `real_app_benchmark543.py audit-replay`.
3. Run `real_app_runtime553.py runtime-receipt` and `predictions`.

Acceptance: 1 audited replay, 1 runtime receipt, and 1 prediction record for each case.
Partial provider results stay abstentions.

### RA554-07 — Publish a provisional report against SDK rectangles (P0, 30 min)

Owner: Maximum-mini-NUIAK. This is a diagnostic, not an accuracy result.

1. Match detections to SDK-registered rectangles at IoU 0.5 for each case.
2. Report matched SDK controls, unmatched SDK controls, unmatched detections, and focus outcomes.
3. Label every number "SDK-registered, unreviewed". SDK rectangles can miss controls and can be misaligned.

Acceptance: a report in `reports/work/REALAPP554/provisional-report.md` with numerators and denominators per app.
It gives the first real-app numbers. It does not replace RA554-09.

### RA554-08 — Blinded human review (P0, maintainer, 2–3 min per screen)

Owner: the maintainer or a named reviewer. Input: blinded drafts from `real_app_benchmark543.py blind_review`.
About 25 screens need 50 to 75 min.
Review every visible control, including controls the SDK does not register. Mark class, bounds, clipping, occlusion, and focus.
Acceptance: every scored case has reviewed labels. Unknown labels stay unknown.

### RA554-09 — Freeze and score the pilot (P0, 30 min)

Owner: Maximum-mini-NUIAK. Depends on RA554-06 and RA554-08.

1. Run `validate`, `freeze`, and `score` in `real_app_benchmark543.py` with the reviewed labels.
2. Report per-class precision and recall, AP50, AP75, AP50–95, and localization errors.
3. Report focus selections, wrong selections, abstentions, latency, and execution failures.
4. Report per app, and the smaller pilot scope honestly.

Acceptance: the first real-app baseline report for the shipped tvOS models. This baseline feeds the M2 gate.

### RA554-10 — Size the focus suppression problem on real apps (P0, 20 min)

Owner: Maximum-mini-NUIAK. The correction belongs to Sillycon-TTR (REAL550-FOCUS, requests at cursors 1836 and 1838).
Count the real-app cases in which 1 off-screen or invalid proposal suppresses the whole selection.
Send the count and case IDs in 1 message. Do not send a duplicate request.

### RA554-11 — Swiftfin content decision (decision)

Swiftfin needs a Jellyfin server with controlled media for home, library, and detail flows.
A local Jellyfin server is an installation and needs maintainer approval.
Without it, Swiftfin supplies only server selection and sign-in cases.

### RA554-12 — Fourth and fifth apps (decision)

- Moonlight: clone the source with submodules and try a tvOS Simulator build. Cloning is a download.
- WeatherFeels: install the Apple Metal toolchain. This is a system download.
- Provenance stays the reserve.

### RA554-13 — Qualification set (P1, after the pilot)

Freeze 40 more cases per qualified app across 8 flows, as REAL543-QUALIFY describes.
Start only after RA554-09 shows that the pipeline scores without evaluation defects.

## Order and time

| Step | Tasks | Estimate |
|---|---|---|
| 1 | RA554-01, 02, 03 | 1–1.5 h |
| 2 | RA554-04, 05 for NewsTV and Photo Guessing Game, Swiftfin pre-login | 1.5 h |
| 3 | RA554-06, 07, 10 | 1 h |
| 4 | RA554-08 (maintainer) | 50–75 min |
| 5 | RA554-09 | 30 min |

Slow steps: the app builds, the capture sessions, and the human review.
These estimates assume that remote navigation works on the first session. Navigation faults add time.

## Maintainer decisions

1. Name the label reviewer for RA554-08.
2. Approve or decline a local Jellyfin server for Swiftfin (RA554-11).
3. Approve or decline the Moonlight clone and the Metal toolchain (RA554-12).

## Limitations

Simulator results describe Simulator behavior. Physical-device results remain separate.
Three apps do not establish general accuracy. Report the scope with each number.
