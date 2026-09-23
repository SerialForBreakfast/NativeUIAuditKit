# Updated TTR validation — 2026-09-22 18:08 UTC

**Still blocked for Fixture training data, but the previous bracket blocker is
passed on this bounded dialog path.** No completed bundle, export or intake.

## Fresh identity and operation

Running local TTR PID90478 has changed debug-dylib SHA256
`42c4a8b07ed8c671ef0c2f6837ba2cb03e527944238fbd76681afc5304621d9a`.
Fixture PID90498 is a fresh install/process/instance; code hash remains
`d2c0af65803bfc86f8b905259e316d3480198392982391115645e0382b8c81d1`.
Listener8080 belongs to that exact process on simulator
`9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`, tvOS26.5,3840×2160 pixels.
Instance `2B29D23B-E85E-4EE6-9E68-9985D9218B7B`,
run `74D06ACD-62B7-4E7C-A5A0-3EA33AD8005E`.
Eight infrastructure checks ready, ownershipclear, coordinator idle before start.
Shared producer snapshots were expired; they did not grant execution authority.

One same-recipe action_dialog/two buttons/high_contrast/regular/seed7/step0 job:
`E5BCE43B-D60E-467B-93D3-7771D20A649F`.
RecipeSHA256 `212f35c0395e8482756773652b238acc78ce000af18279370c21e2ea2999ea07`.
Used matching bundled helper and advertised inline recipe preparation, app-owned
storage, exact UUID/HTTP endpoint. Initial CLI invocation incorrectly passed600000
to the CLI timeout (help allows1…30000). It returned invalidArgument before start;
job-status confirmed prepared. Corrected supported async start executed once.
The job's established ten-minute operation bound applies separately from CLI timeout.
Preserved both start receipts; no uncertain replay.

## Actual failure and improvement

Terminal failure: `native_focus_or_geometry_unavailable:sceneNotSettled`.
Generation3, requested`dialog_btn_0`, native reference still focused,
reason`focus_mismatch`, stableMilliseconds0. Native view/identifier resolves and
all three geometry IDs are measured; missingIDs empty. Failure sampleCount37,
age63.94ms; passive postflight sampleCount422, age85.07ms shows the same mismatch.
Focus sweep advanced to index0: the reference bracket no longer stopped execution.
Neither target's focused capture or a completed bundle is qualified.

Source now uses `validateCaptureBracket` rather than entire-scene equality and
independently checks endpoint freshness/settling. The remaining request is native
focus handoff from reference to actual UIKit dialog button, **not another storage,
timer-equality, missing-geometry, signing or CoreML dependency repair**.

Read-only producer source shows `ProceduralDialogButton.NativeButton` calls
`requestFocusUpdate(to:)`/`updateFocusIfNeeded()` behind a once-per-generation
request guard; reference control and SwiftUI focus/defaultFocus participate too.
Investigate request consumption/lifecycle, focus-environment preference and
reference competition as hypotheses. Telemetry alone does not establish which
one prevents handoff; NUA did not modify producer source or bypass validation.

Ask producer to demonstrate reference→button0→button1 with actual native callbacks,
fresh settled telemetry, aligned PNGs and healthy cleanup. Do not replace observed
focus with requested IDs, lengthen delays blindly, or loop the unchanged smoke.

## Postflight and outcomes

HTTP/device/scene responsive, same instance/run, readiness8/8 and ownershipclear.
Coordinator idle with no queued command or observation. Partial output retained
producer-side; no manual publication or caller container access. No Office,
settings change, simulator restart, new training or promotion.

- Software: source repair observed; no claim to have rerun producer unit tests.
- Data eligibility: blocked; zero completed bundles/pairs admitted.
- Integration: this exact job failed at first target handoff; reference progress
  is narrower than full producer/consumer qualification.
- Model gates: not assessed.

Commands and outputs are retained beside this report; JSON parsing and diff checks
used for this diagnostic-only handoff, not another irrelevant Swift suite.
Next: producer-owned native focus-handoff repair, then one changed-build smoke
through completed export/intake. Independent NUIAK model work stays unblocked.
