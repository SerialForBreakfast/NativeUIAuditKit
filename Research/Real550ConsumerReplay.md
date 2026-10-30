# REAL550 — Standard consumer replay, October 30, 2026

Latest status: NewsTV capture succeeds through NUIAK XCTest. One pilot case awaits human review; runtime provenance remains incomplete.
The sections below preserve the sequence of checks. Earlier activation and dashboard blockers are superseded where stated.

Maximum-mini-NUIAK builds published TTR revision `e8bbdd4a22cfcaf0251e552e3c11b248a86e8821` from isolated Git source.
The build and portable bundle checks pass. The dirty Developer checkout remains preserved.

## Measured outcomes

The fixed diagnostic uses 3 retained Fixture development screenshots: button, row, and tab.
SDK reference data does not enter prediction inputs. These cases do not establish independent real-app accuracy.

| Measure | Result |
|---|---:|
| Requested replays | 3 |
| Completed exports with verified hashes | 3/3 |
| Execution failures | 0/3 |
| Partial provider results | 3/3 |
| Final selected controls | 0/3 |
| Rejected off-screen predictions | 3, one per screen |

The provider returns 2, 6, and 4 valid elements respectively.
Each screen also contains one predicted rectangle below the image boundary.
TTR marks each result partial and returns no final selection.
Raw focused candidates are not final consumer selections. Partial results are not verified no-focus outcomes.
We do not report detection precision or mAP without complete reviewed reference labels.

| Case | Analysis time | Request to durable result |
|---|---:|---:|
| button | 1067.77 ms | 1116.77 ms |
| row | 44.83 ms | 102.06 ms |
| tab | 43.19 ms | 94.20 ms |

Timing excludes completion-receipt writing and IPC return. The first call includes cold model work.
These 3 calls do not establish a latency distribution.

## Provenance and limits

All source, manifest, and result hashes match their completion receipts.
All cases report the same loaded detector and focus digests.
The runtime reports the bundled baseline. The feature returns to its original disabled state after replay.
No capture, training, navigation, model replacement, or promotion occurs.

TTR still reports build source revision, preprocessing identity, taxonomy identity, and crop identity as unavailable.
The external build revision is known. It does not replace missing runtime provenance.
REAL543 baseline freezing remains blocked on the required provenance and reviewed independent application labels.
Real-app accuracy remains **not established**.

## Next decisions

1. Ask Sillycon-TTR to separate invalid proposal diagnostics from valid candidate eligibility, with matched regression evidence.
2. Preserve current conservative selection behavior until that comparison passes. Do not silently ignore rejected geometry.
3. Complete observed runtime provenance for REAL543 through the existing replay contract.
4. Continue SDK539-APPS preparation and blinded label review for the 50-screen pilot.
5. Run frozen full-screen scoring after labels and runtime identities qualify.

## Independent iOS result

IOS549 targeted row rehearsal loses 13 Run013 detections and recovers 16.
It loses 7 ROW545 detections and recovers 5 across the retained comparisons.
The candidate fails preservation. The shipped baseline remains unchanged.
The next training proposal needs a class-preserving objective and training-only anchors before admission.

Detailed local receipts: [verified replay summary](../reports/work/REAL550/verified-replay-summary.json).

## Follow-up: test the proposed correction before changing policy

The native before/after observations agree on focused identity and rendered-body geometry for all 3 retained screenshots.
Source image hashes match the original capture records and replay receipts.
This comparison uses the existing IoU implementation with a fixed 0.5 matching threshold.
It uses native reference geometry only after inference.

| Case | Best focused-body proposal IoU | Outcome if only partial suppression were ignored |
|---|---:|---|
| Button | 0.9870 | Wrong selection; selected-box IoU is 0 |
| Row | 0.9374 | Correct selection |
| Tab | 0.9633 | Abstention |

Removing partial suppression alone would recover 1 selection but introduce 1 wrong selection.
That correction fails preservation. The runtime policy remains unchanged.
Accurate candidate geometry alone does not establish correct focus scoring.
Investigate crop provenance and scoring separately from rejected proposals.
These 3 related development cases do not estimate deployment accuracy.

## Reusable export audit

The existing benchmark CLI now supports `audit-replay INPUT_DIRECTORY --output REPORT`.
It verifies completion, source/manifest/result hashes, image dimensions, upright orientation, and final-selection consistency.
It rejects reference labels in the inference manifest.
It records partial results, observed model identities, missing provenance, and the actual timing scope.
A valid export remains ineligible for accuracy claims until runtime and reference qualification pass.
All 51 Python tests pass, including 6 new replay checks. All 3 actual exports pass the audit.
No queue execution or model inference occurs during this audit.

## Reference review and pilot boundary

The existing review exporter produces 3 prediction-free development reference drafts.
Classes remain unresolved. Visibility and annotation completeness require human review.
The designated reviewer must not have seen model predictions for these cases.
These are retained Fixture cases. They do not increase the independent pilot count.
Private review entry: `reports/work/REAL550/blinded-development-review/index.html`.

No independent pilot screenshot currently meets all required gates.
NewsTV needs supported foreground activation before native focus and image alignment can qualify.
Swiftfin needs controlled content and SDK integration. The game needs SDK integration and runtime qualification.
WeatherFeels needs the missing Metal toolchain. A fifth independent application remains unselected.
No human labels are invented, and no empty benchmark job is admitted.

The coordinator stores the counterfactual findings at cursor 1816.
Forwarding to Sillycon-TTR remains unconfirmed. No new TTR reply is present at this check.

## Verification and remaining operational limits

Offline Swift build passes. Swift Testing reports 177 passing tests; XCTest reports 14 passing tests.
The 51 Python checks pass. No model accuracy claim follows from software checks.
The final coordinator attention check reports no unread reply.
The dashboard health check at port 8766 fails with connection refusal. Runner health remains unverified.
No service restart or new queue admission occurs.
Recorded follow-up work spans approximately 5 min, against the initial 30–60 min estimate.
The larger independent pilot remains incomplete at the documented application, provenance, and human-review gates.

## Dashboard and application follow-up

The dashboard is healthy at http://127.0.0.1:8765/.
The prior probe used stale port 8766 and the wrong endpoint, `/health`.
The supported check reads `.build/dashboard/control.json` and calls authenticated `/api/health` through `restart_research_dashboard.Api`.
Do not publish its authentication token.
The verified process has continuous dispatch enabled, no current job, and no reported error.
It waits for approved work that passes readiness. No restart occurs.
The corrected browser URL is sent to the Codex panel.

TTR requests at cursors 1812 and 1816 remain unread and unaccepted.
The remote source tip remains e8bbdd4. No newer repair is published.
A 25-file source map matches the published Git content byte-for-byte.
It identifies RuntimeSources as the active implementation location, distinct from legacy Sources.
This source evidence helps define preprocessing and taxonomy exports. It does not invent missing runtime fields.

The intended tvOS Simulator reports ready with clear ownership.
The standard Simulator frontend path is absent. Xcode contains DeviceHub instead.
A bounded NewsTV metadata trial still reports 23 controls, inactive state, and unknown focus across 3 observations.
Cleanup passes after 8.68 s. No screenshots or navigation inputs occur.
The unsupported foreground route remains an exact blocker for the independent NewsTV pilot.
No system component is downloaded, no setting changes, and no TTR source edits occur.

### Additional retained coverage measurement

| Family | Registered controls covered at IoU 0.5 | Total registered controls |
|---|---:|---:|
| Button | 2 | 4 |
| Row | 2 | 4 |
| Tab | 1 | 4 |
| Total | 5 | 12 |

This is class-agnostic geometric coverage over known registered controls.
Native rendered-body geometry agrees before and after each capture.
This is not complete detector recall, precision, mAP, or independent real-app accuracy.
The result separates missed control bodies from focus selection failures without new inference.
Evidence: `reports/work/REAL550/registered-control-coverage.json`.

The coordinator stores the updated activation and source request at cursor 1818.
The next owner is BigDog-Coordinator for confirmed routing to Sillycon-TTR.
Maximum-mini-NUIAK can qualify the published correction after it supplies observed runtime identities and a supported arbitrary-app activation route.
The independent pilot and model promotion remain incomplete. Standard remains unchanged.

## Real-app capture unblocked with the existing XCTest target

NUIAK's opt-in NativeOSFocus target now has 2 bounded NewsTV tests.
`testNewsTVPilotInitial` launches controlled content and verifies foreground state before one screenshot.
It records native accessibility observations and verified termination. The test passes in 3.57 s.
`testNewsTVActivateExisting` activates an already enrolled process and holds it for 12 s without navigation.
It records one screenshot and native observations. The test passes; host cleanup succeeds after 15.79 s.

Both trials use the intended tvOS Simulator after TTR reports clear ownership and readiness.
They send zero navigation inputs. They change no settings, model, or TTR source.
Two retained screenshots represent **one pilot case**, not two independent samples.
The second screenshot accompanies 23 authenticated SDK control observations.
The capture manifest now records 1 captured case and 9 planned cases for NewsTV.

XCTest reports runningForeground. SDK observations still report UIKit and scene inactivity with unknown focus.
Do not erase this disagreement or label the image as known no-focus.
Detection-label preparation can proceed while focus qualification remains open.
The draft converts SDK window points to pixels using the observed 2x screenshot/window ratio.
Human review must verify alignment, clipping, semantic classes, and complete visible coverage.
All draft classes remain unresolved. Completeness remains false. No model prediction has been viewed.

Review entry: [NewsTV reference review](../reports/work/REAL550/newstv-blinded-review/index.html).
The reviewer must inspect the actual screenshot before accepting labels.
The screenshot is not yet eligible for benchmark scoring or training.
No independent application is fully qualified yet. Runtime provenance remains incomplete.

The host metadata receipt originally counts only host captures and reports zero.
A separate reconciliation records the XCTest screenshot and total capture count of 1 for that second trial.
Both original receipts remain preserved.

The coordinator stores the proven activation recipe and lifecycle discrepancy at cursor 1820.
No TTR reply or delivery confirmation is present. The TTR source owner still controls its implementation and Git publication.
Next: review this actual screen, reconcile SDK readiness, and complete runtime provenance before frozen inference.
