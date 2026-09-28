# Capability inspection — preparation and subsequent live evidence

**Latest, 2026-09-27:** operator receipts verify local helper/app IPC, Office control
connection, owned lease/session and two image exports; the maintainer confirms the
images show the intended different focus states. This does not verify an approved
remote transport from this chat, consumer byte receipt/crop QA, native focus labels
or teardown. The initial matrix below is historical; see [coordination](coordination.md).
The highest next integration priority is the
[human-approved external-control request](../../../Research/Plans/TTRSupervisedExternalControl.md).

2026-09-27. Current repository HEAD63d2ff4; initial working tree clean.
Read-only source inspection, filesystem checks and scoped process inventory only.

**Update17:46:02Z:** maintainer-supplied Sillycon help/status/device-list output
verifies the matching helper reaches the running app. Office discovered but
disconnected; pairing unknown. No active command/observation, NUIAK disabled.
Capture ownership/provider/source binding/export remain unverified. Diagnostic-file
sink code24 is separate from untested image export. Binary identity not pinned.
SMB previously mounted/published/read back. The matrix below records historical
initial preparation; current runtime evidence is in [coordination.md](coordination.md).

| Capability | State | Evidence / next check |
| --- | --- | --- |
| Current-host installed/running TTR coordinator | Not found in inspected locations/process inventory | No TVTestRig.app in /Applications or user Applications, no running coordinator; one existing simulator Fixture extension is unrelated and untouched. Standard prior DerivedData app path absent. This does not establish all possible install locations or the Office Mac's state. |
| Exact Office app/helper build | Unknown | Need running Office host's actual app and Copy Helper Launch Check. No app launched, rebuilt or replaced. |
| PNG export plus target/time/freshness | Source-inspected | StableCLIObservation and AtomicObservationFileWriter; tested offline adapter consumes same envelope shape. Installed/runtime round-trip remains pending. |
| Session/target/source binding | Source-inspected; live unknown | session status uses status._0 and includes selectedDeviceID/sessionID. Observation carries sourceDeviceID but no sessionID; operator binding is explicitly non-atomic. |
| Capture/controller ownership | Source-inspected; live unknown | Existing separate controller/capture lease/session contracts. No lease acquired or device connected. |
| Native Photos focus + geometry | Not established | Inspected observe focus uses OCR/model predictions; Fixture callbacks and the existing Home/Settings native runner do not qualify Photos. No new provider implemented. |
| Human annotation/review | Local adapter implemented | Separate diagnostic version, hash-bound confirmation and production cropper; no native/training qualification. |
| Shared coordination delivery | Unavailable this turn | OS mount inventory reports no SharedStatusFile SMB mount. No reconnect, peer read/write or remote execution attempted. |

Initial restricted `ps` returned operation not permitted. Scoped read-only normal-host
approval succeeded, isolating the inspection boundary without changing TTR or host
permissions. No live helper was invoked because no matching running app was found.
No private Photos frame, native telemetry, Office health or current availability
has been observed in this tranche. No capability requirement should be sent as a
producer defect until the actual installed runtime is inspected.

If capture/export fails in that runtime, retain the exact build/helper/request,
stage/error chain and available artifact. Required producer behavior is one fresh
exact-target PNG with correlatable observation ID, capture time, source and honest
freshness, plus supported byte-preserving export. Missing Photos native labels alone
does not block the selected human-reviewed diagnostic pilot.
