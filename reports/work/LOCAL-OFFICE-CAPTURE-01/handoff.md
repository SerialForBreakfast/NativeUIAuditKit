# Max-local Office connection and capture — completed bounded test

2026-09-28; owner: current NUIAK TTR consumer worker. Authority: maintainer reported
Office free, requested current Max TTR connection/capture, then approved permission
prompts. One still, no navigation, model execution, training or app activation.

## Result

**Local connection → owned capture → original-byte delivery → visual inspection →
cleanup passed.** Max can be the primary local capture host for the next approved
Focus collection. Sillycon pairing/SMB is not a prerequisite for this local path.
This is one bounded live test, not reliability or remote-transport qualification.

The captured Home screen visibly shows the enlarged Photos tile and Photos caption.
This is an agent visual observation, not native focus telemetry, human-confirmed
training annotation, or a new Photos-in-app pair. Some other tiles appear blank;
the frame is not black and is usable for capture-path proof, not full rendering QA.

## Runtime and evidence

Running TTR PID61937 and its matching `Contents/Helpers/aatv` were used from
`/Users/josephmccraw/Library/Developer/Xcode/DerivedData/TVTestRig-fssavpzkujakgqggjglqjvvrtyoo/Build/Products/Debug/TVTestRig.app`.
No rebuild, restart, re-signing or producer edits. Host-context signature verification
passed; restricted execution previously aborted the helper. Existing component
identity evidence is in [EXT-CAP-02](../EXT-CAP-02/handoff.md); exact source binding
remains unverified. All files below are relative to this directory and remain local.

| Check | Observed result / evidence |
| --- | --- |
| Target | Fresh discovery bound Office to `8D80F616-6C12-49A6-9015-8F594EE5F24E`; `devices.json`. |
| First attempt | `connect.json`: commandTimedOut,22,153ms. `capture.json`: connectionLost,7ms. Both owned resources released/disconnected before retry. |
| Changed circumstance | Maintainer approved permissions. Exact permission category/root cause is not established; preflight had already reported camera authorization. |
| Fresh connection | `connect-after-permission.json`: success,124ms; request E7F2A524-5021-459A-A72B-33870DA657A1. |
| Owned lease | `acquire-after-permission.json`: owner nuiak-local-office-20260928-02; lease FA92EC16-955A-447E-A9EE-AFB8C93C73E9, video/control. |
| Fresh capture | `capture-after-permission.json`: success,5,708ms total;61ms capture duration; estimated age56ms/current. Source matches Office; avfoundation-video; connectionGeneration1. Observation AECA85EC-FF75-4D97-8584-CA61D6388B85; request0B5C0C57-EAB9-4023-BB54-403FD9DEAD43. |
| Pixels received | Base64 payload decoded without image transformation to `office-after-permission.png`;650,958bytes;1920×1080;SHA256 `73c3d086c85afb44ff8a415eff81ae71362554e51f5f539cf42b1cf8957985b5`. Inspected with local image viewer. |
| Cleanup | `release-after-permission.json`: video/control released. `disconnect-after-permission.json`: disconnected. `status-final.json`: disconnected, no active command/observation, queue0. `lease-final-targeted.json`: no active lease, acquire/release counts3/3. `observation-final.json`: provider idle,not warm. |

`outputWritten:false` in the successful capture means the app did not write an
output path; inline image bytes were delivered and saved by the consumer. It is
not missing evidence. Raw JSON contains the image and is gitignored, as is the PNG.
Capture time uses Foundation seconds since2001; do not interpret as Unix seconds.

## Friction / producer feedback

- Connection failure was initially a generic timeout; after user permission approval
  a fresh connection succeeded. Preserve the chronology, but do not claim a proved
  permission root cause. Surface pending consent/readiness distinctly where possible.
- Helper repeatedly reports `diagnostic_file_sink_failed`/persistenceFailed code24
  even when the actual command succeeds. Review diagnostic persistence separately.
- `capture status` without explicit device ID returned invalidArgument even though
  coordinator status retained a selected Office ID. The explicit-target check passed.
- Local inline delivery removes manual terminal relay and app output-folder grants
  from this one still workflow. It does not validate packaged remote MCP registration.

## Acceptance and next step

- Software: no implementation changes; existing installed commands exercised, full
  software suite not rerun/not assessed.
- Data: one retained diagnostic frame; no reviewed pair, bounds or training admission.
- Integration: passed for this exact local Office still/receipt/cleanup scope only.
- Model gate: not assessed; NUIAK feature remained disabled.

Recommend Max-local for the next supervised session. Before collecting the proposed
20–30 screen situations, qualify human-operated **TTR** input recording with correlated
before/after frames, command outcomes, timestamps and settling. Then use existing
review/import/crop tooling with explicit roles and human labels. This follow-up is
not executed by the connection test. Existing two Sillycon Photos originals still
await receipt; do not replace or relabel them with this Home screenshot.

Shared publication and peer acknowledgment are recorded in [coordination.md](coordination.md).
