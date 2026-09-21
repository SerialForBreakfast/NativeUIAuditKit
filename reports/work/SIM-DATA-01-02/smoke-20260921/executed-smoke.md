# Updated Fixture: genuine smoke executed, failed native observation

**Validity correction:** User subsequently reported touching the simulator during
this run. Preserve the observed failure but classify the trial as interrupted /
confounded, not a controlled reproduction or proof of a producer defect. User
explicitly authorized one clean retry and agreed not to interact.

2026-09-21 23:06Z. Continues the user-authorized two-element simulator smoke.
Prior preflight-only failure is retained in handoff.md; it is not this attempt.

New Fixture PID48871 listens on8080, executable path binds it to exact simulator
9026ECA9-77DB-4AE6-8FE6-BB239E9571FA. Installed Debug dylib SHA256:
`7d1014c5b22552f7d99401f7c99badf39e4c3ee05c13192eff16142ba98d076c`.
GUI PID47684 unchanged. New Fixture reports unsettled rather than legacy settled;
missing observation before recipe setup was not treated as an installation failure.
Fresh readiness passed with clear persisted ownership (`new-readiness.json`).

## Actual execution

- Prepared one action_dialog/two-element/high_contrast/regular/seed7/step0 recipe
  via inline job API; storageReady true. Job:
  `F3B3C1B4-A6B0-4161-A007-CC2DC5178D87`.
- Imported recipe SHA256:
  `212f35c0395e8482756773652b238acc78ce000af18279370c21e2ea2999ea07`.
- Started once with explicit simulator UUID and http://127.0.0.1:8080;
  request `95D836DD-7C93-4D05-A0DE-3E0B58032B98`, exit0/running.
- Terminal job-status request `321A63A2-34AD-4FD6-AC47-F9F1AD1AC118`:
  **failed**, `native_focus_or_geometry_unavailable:sceneNotSettled`.
  Transport exit0 means the status was retrieved, not capture success.
- No completed files advertised, no export attempted, no intake/data approval.
  TTR retains the failed app-owned job; no container access, deletion or manual
  publication of partial output was performed.

## Postflight and diagnosis boundary

Fresh scene request `923D4BD0-4071-4E57-8E9F-8665A3A024C5` succeeds and confirms
the requested action_dialog recipe (scene recipe hash
`f4585d933d70dd313b52c403ffeda620e6eea0896be56d9794bc9c5c5fca1216`), sweep index
-1, count3, is_settled false, no focus_observation. The import-byte hash and scene
recipe hash are distinct producer contracts, not claimed interchangeable.
Fixture is HTTP-responsive, not visually/focus-qualified. Recipe remains applied;
no restoration is claimed. Postflight readiness request
`6F231005-8078-46B4-8AC0-F7982045B676` returns ready and persisted ownership clear.
No lease was separately acquired by NUA and none was released on another owner's behalf.

Source inspection shows FixtureCoordinator only publishes focusObservation after
its native gate succeeds, and expires it after one second. Absence alone does not
distinguish missing callbacks, unresolved focus identity, incomplete measured
geometry, generation mismatch, instability or staleness. TTR must expose/diagnose
that gate with this exact recipe; no evidence supports a reset, added delay or
weakening ground-truth requirements. Do not repeat the same job blindly.

## Outcome and next action

Runtime/storage and job dispatch passed. Genuine smoke failed before usable
paired capture; data eligibility and complete integration remain blocked, model
gates not assessed. Retained JSON/stderr files contain commands' full replies.
No training, broad harvest, Office operation, restart or installation occurred.

TTR-owned next assignment: reproduce this two-element baseline/reference-focus
failure, identify the native observation gate reason, fix under its instructions,
and return one genuine completed bundle plus postflight evidence—not only unit
tests. NUA then validates export, separate frame geometry/crops and intake. The
roadmap's pilot+baseline → frozen quota corpus → one candidate remains unchanged.

Shared status: NUA readiness entry updated and YAML read back successfully with
request `nuiak-20260921T230610Z-native-observation-smoke-failure`; deployment
request closed, other requests preserved. Peer acknowledgment pending.
Local queue updated; `git diff --check` passed.

## Explicitly authorized clean retry — 23:09Z

User confirmed no interaction and authorized one retry. Fresh readiness/ownership
passed before a new job; no failed job was replayed. Prepared job
`F996B28B-43B6-4B6D-8B37-7DB45D5E0340`, identical imported recipe hash, started
once (request `B9D07E1C-8B9F-4388-9C10-C4C44953FD88`). Terminal status request
`E0027EBF-1E4D-42C9-8DA5-A7CA6D346350` returned failed with the identical
`native_focus_or_geometry_unavailable:sceneNotSettled` error and no completed files.
Commands returned exit0 for successful API exchanges, not successful capture.
All replies/stderr retained as `retry-*` files alongside this report.

Postflight HTTP succeeds; scene remains unsettled without focus_observation.
Readiness again reports can_run true and persisted ownership clear. Recipe remains
applied. No additional retry, export, training or cleanup mutation performed.
The first run remains confounded; the second reproduces the symptom under the
user's no-interaction agreement. Root cause is still unresolved, not proven to
be any particular callback/geometry issue. TTR should use this new job as its
primary reproduction. No usable data or model-quality evidence was produced.
