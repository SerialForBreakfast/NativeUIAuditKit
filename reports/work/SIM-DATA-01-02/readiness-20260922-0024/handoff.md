# New TTR build: read-only readiness check

2026-09-22 00:24–00:25 UTC. User authorized checking updated TTR and publishing
status, not a new smoke, recipe mutation, capture, training or deployment.

## Verified

- Running GUI PID 57885, matching bundled helper in the same DerivedData app.
- Helper SHA-256 `0dbce8198286e964643535737ec88f2f2bf56eec0a3895d88d087c766f14b748`.
- App debug dylib SHA-256 `80e3972f3b03c62d2170ef8d99983593f1d87661d4e8b2c066b9bde7e01c89fc`.
- TTR source checkout `0ee5cc88b2f5a198e3f1537a4aeaa7379e5745a4`, clean.
  Source presence alone does not identify every compiled dependency.
- Running Fixture PID 57715 belongs to exact simulator
  `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`; lsof confirms that PID owns TCP 8080.
- Installed Fixture debug dylib SHA-256
  `6dff813cf01c2519db32e8aeb3234103a5c408a77eaef4e46cb01eb02f38aed1`
  matches the local Debug-appletvsimulator build artifact.
- Readiness request `5D52E3AA-E82D-490A-8415-B77BCAA1EBF4`: success,
  can_run=true, persisted ownership clear. Coordinator, companion, storage, Xcode,
  packaged runner, CoreSimulator, tvOS runtime and selected target ready.
- Target is booted tvOS 26.5, Xcode 26.6 (17F113).
- Fixture scene request `990AEE6A-DBAC-424A-B33B-F6AE3F2C1ED5` succeeds and
  includes new `observation_diagnostics`. Current media_shelf seed1042 scene:
  is_settled=false, reason=no_sample, sampleCount=0, measuredIDs=[],
  nativeFocusResolved=false, eight required IDs missing. No focus_observation.

This confirms updated diagnostic capability and runtime availability, **not**
successful native observation/capture. The idle scene differs from the two-element
smoke recipe; it is not a controlled reproduction or proof that a new smoke will fail.
Only a newly authorized bounded capture/intake can resolve that qualification.

## Commands and retained evidence

Process/port checks were read-only host commands. Restricted process inspection
was denied; restricted helper --help exited134. The identical approved host help
exited0, so no rebuild/re-sign/restart was attempted. Runtime checks used that same
helper with --json --timeout-ms 10000 in approved host execution:

- `simulator readiness --simulator-udid <exact UUID>`: exit0, readiness.json/stderr.
- `fixture scene --fixture-url http://127.0.0.1:8080`: exit0, scene.json/stderr.
- `fixture env --fixture-url http://127.0.0.1:8080`: exit0, environment.json/stderr.

The helper diagnostic-file sink warning persists; structured calls succeeded.
Only reports in this NUIAK folder were explicitly written. No session/lease acquired,
recipe prepared/applied, screenshot taken, job started, restart, Office input or model run.

## Outcome and next action

Runtime readiness passed; software-wide verification not rerun. Data eligible:
not established. Genuine integration: not qualified. Model gates: not assessed.
Ready to attempt a separately authorized exact-target smoke, not ready to train.
Fresh readiness/ownership must be checked again when that operation is assigned.

Peer packet NUIAK-CAPTURE-CROP updated 00:16:36Z reports source85ffddc+dirty
producer fixes and tests, not consumer qualification. Its request
`tvtestrig-20260922T001254Z-capture-crop-qualification` is received for coordination,
not execution authority. Peer acknowledgment of our crop notice was observed.
Published under `packets.SIM-CHECK-20260922` and refreshed the architect summary
in `/Volumes/SharedStatusFile/nuiak/status.yaml` on the verified sillycon.local mount.
Safe YAML readback and exact readiness-request checks passed; other workers' packet
entries were preserved. Our crop notice is now marked acknowledged using the peer's
00:12:54Z receipt. Acknowledgment of this new status update remains pending.
