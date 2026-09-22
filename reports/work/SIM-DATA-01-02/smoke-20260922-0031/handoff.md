# Updated-build smoke — 2026-09-22 00:31–00:35 UTC

Outcome: one authorized simulator smoke executed and failed native-focus admission.
No completed bundle, export, intake, training or promotion. No automatic capture retry.

## Verified runtime and scope

- TTR source checkout `0ee5cc88b2f5a198e3f1537a4aeaa7379e5745a4`.
- GUI PID57885; installed Fixture PID57715 owns port8080 and belongs to simulator
  `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`. Same runtime as preceding readiness report.
- Matching bundled `aatv` SHA256 `0dbce8198286e964643535737ec88f2f2bf56eec0a3895d88d087c766f14b748`.
- Installed Fixture dylib SHA256 `6dff813cf01c2519db32e8aeb3234103a5c408a77eaef4e46cb01eb02f38aed1`.
- Existing action_dialog recipe: two elements, high_contrast, regular, seed7, step0.
  Prepared recipe SHA256 `212f35c0395e8482756773652b238acc78ce000af18279370c21e2ea2999ea07`.
- App-owned recipe/job staging only; no manual container write, permission change,
  Office operation, restart, Settings navigation or external-repository modification.

## Actual commands and results

All commands used the verified running app's `Contents/Helpers/aatv`, `--json
--timeout-ms 10000`, approved host execution, and local stdout/stderr evidence here.

1. `simulator readiness --simulator-udid <exact UUID>`: exit0, can_run=true,
   ownership clear; request `EF46C1EB-A266-4B34-95A1-AB8C8849C690`.
2. `fixture prepare --recipe <TTR>/Scripts/fixture-recipes/live-smoke/action-dialog.json`:
   exit69, serviceUnavailable, duration0ms, request `DE3F99B7-1D5A-4D75-AD0B-AB5F53C4E07A`.
   No capture command had been sent. Same processes/hash persisted; subsequent
   readiness passed. Job-status for that request returned commandRejected (exit1).
3. Documented `fixture prepare --recipe-json <same recipe values>`: exit0,
   storageReady=true, job `EE995A3A-AB6F-42A4-9765-1D347BEF8CC7`.
   This is a file-import workaround, not a repeated capture. Source inspection:
   StableCLIRunner.readJobRecipe reads the caller file before IPC; untyped file
   errors collapse to serviceUnavailable. File-access failure is the leading
   hypothesis, not a proven OS error: the original exception is not exposed.
4. `fixture run-job EE995A3A-AB6F-42A4-9765-1D347BEF8CC7 --simulator-udid <exact UUID>
   --fixture-url http://127.0.0.1:8080`: exit0, running, 00:33:57Z or earlier.
5. `fixture job-status <job>`: exit0 envelope, **failed job**, request
   `9C222545-7B88-44FF-9202-E64011D17E36`. Failure:
   `native_focus_or_geometry_unavailable:sceneNotSettled; inspect retained evidence`.
   No completed members (`files=[]`); expected two pairs remain unfulfilled.

## Failure narrowed by genuine diagnostics

Terminal observation: generation2/sampleGeneration2, sampleCount36, sample age
100.929ms, both required buttons and container measured, missingIDs=[],
nativeFocusResolved=false, reason=unresolved_focus, stableMilliseconds0 against
required150. This is not no_sample, missing geometry, or a reason to loosen settling.
Fixture baseline must positively resolve its reference focus; requested focus or
all-false element labels cannot substitute for native ground truth.

Postflight scene: sampleCount485, age12.744ms, same unresolved_focus and measured IDs;
HTTP still responsive. Final environment has the same Fixture instance/run IDs.
Readiness request `A6E4F145-6FC5-495D-AB21-3DFEEB7ACD87`: exit0, can_run=true,
persisted ownership clear. No manual cleanup/reset necessary; recipe remains applied.
This establishes observed postflight responsiveness, not indefinite crash-free health.

Secondary geometry concern for producer review: scene declares1920x1080 but
dialog_btn_0 pixel bounds `[650,442.75,220,72]` and normalized xyxy bounds
`[0.369318...,0.701108...,0.494318...,0.815122...]` do not correspond under those
dimensions. There is no captured image to decide the correct transform. Require
actual screenshot/window/content-origin/scale validation, not guessed conversion.

## Resume and independent outcomes

TTR needs a bounded native-reference/item-resolution fix or source-backed diagnosis,
plus actionable file-read errors with documented inline import. Preserve native
focus and geometry admission, no timeout inflation or synthetic success labels.
Return deployment identity and regressions; then separately authorize a new smoke.

- Software verified: not assessed by this operational run; prior offline evidence preserved.
- Data eligible: blocked; no completed corpus.
- Integration qualified: failed for this exact smoke.
- Model gate passed: not assessed.

No code changed; Swift build/test not rerun for diagnostic/report edits. All retained
JSON is parsed and local diff checked. Shared publication/readback tracked in
`coordination.md`; peer acknowledgment is separate.
