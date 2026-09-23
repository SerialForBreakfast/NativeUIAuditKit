# Updated Fixture qualification — 2026-09-22 18:30 UTC

Still blocked for consumer capture/intake. Changed-build smoke failed at reference
geometry; neither button handoff was reached. Zero completed bundles or admitted
pairs. No automatic retry, training, promotion, Office operation or restart.

## Identity and producer acknowledgment

Producer packet at18:25Z acknowledges the prior handoff request and reports live
reference→button0→button1→reference on its different simulator2BAA6307. Received
request `tvtestrig-20260922T182500Z-native-dialog-candidate`; local source SHA256
`852f341dbd5c4e186d3c905f9d84ebbba74ba833b41d4bf07ffff4d20606b27c` matches.
Source correspondence is not authenticated source-to-binary attestation.

Both running binaries changed: TTR debug-dylib
`80a3605ac40dab255f277079e0699d9bc07d885f2649e95cffa61b7720670407`;
Fixture `de66be0901bf8b235391947079376aa128e98455aecb43489c66db512620d589`.
Fixture PID93023 owns8080 on exact local simulator
`9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`, tvOS26.5,1920×1080points/scale2.
Instance `DFB10D6A-85A8-4EF2-826F-BCE4A9FEA6C2`,
run `B9CC1F40-B458-4869-8E7B-794AB98DC2CA`.

## One bounded real smoke

Job `675C0665-7691-4DD0-9197-ADF1E53D8F85`, same frozen action_dialog recipe:
2 elements/high_contrast/regular/seed7/step0, recipe SHA256
`212f35c0395e8482756773652b238acc78ce000af18279370c21e2ea2999ea07`.
Matching app helper, supported inline prepare and exact-UUID app-managed run-job;
no build/install by NUA. Preflight8 checks ready, ownershipclear, coordinatoridle.

Terminal `native_focus_or_geometry_unavailable:sceneNotSettled`:
generation2, referenceFocusedtrue, native view/identifier resolved; measuredIDs
only`dialog_container`, missing`dialog_btn_0` and`dialog_btn_1`, reason
`missing_geometry`, stableMilliseconds0,36 samples/41.98ms age.
Postflight347 samples/74.51ms age shows the same missing geometry at sweepindex-1.
Scene elements contain only the container. Thus target-handoff repair cannot be
accepted or rejected by this run; it is blocked by a newly observed prerequisite.

Current probe source omits hidden/zero-alpha views, unknown IDs, empty/clipped
bounds and failed coordinate projection. Which branch loses both buttons is
unproven. Request producer diagnostics of attachment/IDs/bounds/clipping/projection
for these controls, not substitute layout/prediction boxes or relaxed admission.
Producer should reproduce the **full recipe→reference geometry→both focused
captures→completed receipt/index** path, not only direct focus commands. Include
exact build/runtime/viewport, native callbacks, PNG alignment and postflight.

## Postflight and outcomes

Fresh HTTP responsive, same Fixture instance/run;8 readiness checks ready,
ownershipclear, coordinator command/observation inactive, queue0. Preserved failed
job/partial evidence producer-side. No completed export or intake attempted.

Software: producer-reported checks and source match, not NUA unit-test execution.
Data eligible: blocked. Integration: failed for this exact job. Model gates:
not assessed. Independent NUA export/model work remains available.

JSON evidence retained alongside this report. Diagnostics-only work uses parsing,
identity checks and diff review; no irrelevant rebuild. Next changed-candidate
smoke only after the reference button-geometry prerequisite is addressed.
