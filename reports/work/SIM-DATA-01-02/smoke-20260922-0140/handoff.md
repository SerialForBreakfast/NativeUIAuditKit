# Native reference repaired; screenshot output denied

Authorized single simulator smoke, 2026-09-22 01:38–01:39 UTC.
Job `B699DFCC-2A91-4968-AE8B-387904BB9E4D`; **failed**, no automatic retry.

Same app/Fixture PIDs and exact target as the preceding
[runtime inventory](../readiness-20260922-0134/handoff.md); endpoint PID64284
owns port8080. Fresh preflight can_run=true and persisted ownership clear.
Matching helper, local source fd50a80; no rebuild or binary substitution.

Prepared unchanged action_dialog/high_contrast/regular/seed7/step0 recipe with
two elements through documented inline JSON. storageReady=true; recipe SHA256
`212f35c0395e8482756773652b238acc78ce000af18279370c21e2ea2999ea07`.
One `fixture run-job` invocation with exact simulator
`9026ECA9-77DB-4AE6-8FE6-BB239E9571FA` and `http://127.0.0.1:8080`.
The built-in ten-minute job bound was not reached. Structured start succeeded;
terminal job failed `capture:unclassified`, files=[]; receipt acceptedRowCount=0,
outcome=aborted, stage=capture, code=commandRejected, retryable=false.

## Material progress

Post-scene now has nativeFocusResolved=true, referenceFocused=true,
referenceAttached/referenceFocusable=true, resolution=identifier,
geometrySource=uikit_window_converted_bounds, verified focus observation,
is_settled=true, missingIDs=[], sampleCount409, age88.8ms, stable40800ms.
This positively resolves the reference baseline; both target focus states are
still untested because capture failed first. Do not claim complete focus sweep.
Pixel/normalized boxes now describe a common scaled coordinate space; without a
captured PNG their alignment and screenshot dimensions remain unqualified.

## Concrete capture failure

Read-only retained companion evidence:
`SimulatorDiagnostics/capture-ee4ec697-93ca-4a0c-9d44-2d165b9c6ae0/capture.stderr`
under the app's existing Evidence root. `capture.stdout` is empty, no frame.png.
The screenshot command reports NSCocoaErrorDomain513: permission denied saving
frame.png in that capture folder; underlying NSPOSIXErrorDomain1/EPERM.
It selected display TVOut/screenID2. This identifies output access failure, not
an absent simulator or a diagnosed focus failure. Exact sandbox/security-scope
root cause remains producer investigation; do not weaken permissions speculatively.

Source path: CompanionMain.swift screenshot writes via `simctl io <UUID>
screenshot --type=png <app-managed capture folder>/frame.png`.
FixtureHarvestFailureDiagnostic collapses the surfaced error to unclassified;
request typed stage/cause and retained diagnostic references. Preflight's own
write/readback success does not establish screenshot writer access.

Partial receipt remains untouched in job workspace
`.bundle.partial-0E7C98BD-5187-490E-8B9B-7C73C6A51891/harvest-receipt.json`.
No manual publication, export, intake, baseline inference, training or promotion.

## Postflight and outcomes

Fresh scene/environment respond; instance/run IDs match preflight. Exact-target
readiness passes with persisted ownership clear. No owned resource remains reported;
no restart/reset/cancel of another operation. Recipe remains applied at reference focus.
This is observed responsiveness, not indefinite crash-free health.

- Software: prior offline evidence preserved; not retested in this operation.
- Data eligibility: blocked, zero accepted rows of two expected pairs.
- Integration: failed at screenshot output; native reference admission improved.
- Model gates: not assessed.

Next: TTR repairs authorized screenshot-output access and surfaces actionable
capture errors, with regression coverage of the actual writer boundary. Then one
newly authorized smoke/export/intake; do not rerun unchanged. No external producer
code edits or permission changes are authorized by this report.

Evidence: adjacent prepare/start/status-01 and pre/post JSON/stderr files.
All helper calls returned structured success; job failure is inside status payload,
not a successful capture. JSON parsed and diff checked; no code changes, build/tests
not rerun. Shared result/request publication and acknowledgment tracked separately.
