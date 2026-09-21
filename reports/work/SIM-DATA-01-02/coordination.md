# TVTestRig coordination — published

`publication: published` — `SIM-DATA-01` was updated and read back at
`/Volumes/SharedStatusFile/nuiak/status.yaml` on 2026-09-21T04:43:20Z. This confirms
storage publication only; no peer has acknowledged this revised observation.

## Consumer observation

The simulator fixture process is running for UUID
`9026ECA9-77DB-4AE6-8FE6-BB239E9571FA` on tvOS 26.5 and owns its in-simulator
port 8080. The host CoreSimulator control plane is unavailable: `simctl list`
returns connection-invalid/connection-refused, and the per-user launchd service
is absent. Host loopback cannot reach the fixture's in-simulator HTTP listener.

## Cross-repository consequence

No TTR simulator harvesting, explicit-UUID screenshots, or fixture HTTP bridge can
be qualified until the host CoreSimulator service is restored. This is not a request
to restart the fixture, alter settings, or capture data. After maintainer restoration,
the consumer will rerun read-only simulator inventory and fixture scene/environment
probes before any authorized minimal capture.

## Office FR-B preflight, 2026-09-20

The user explicitly authorized Office FR-B capture. The packaged `aatv` helper reached
a stale connected-session snapshot and the fixture HTTP endpoints: Office reports tvOS
26.6, 1920×1080, VoiceOver off, and a settled `media_shelf` scene. However, target-specific
`device get`, `device capabilities`, `capture status`, and `doctor` all returned
`serviceUnavailable`. Fixture HTTP cannot create screenshots; a fixture batch would therefore
produce no qualified capture evidence. No device input, capture lease, batch command, output,
or cleanup action was started. Reopen/restore the TVTestRig coordinator while preserving Office
and fixture state, then rerun the named read-only preflight before capture.

## Corrected simulator readiness observation, 2026-09-21

The later TVTestRig readiness report changes the immediate stop condition: its coordinator
is ready and the Fixture reports telemetry ready on port 8080, but
`SimulatorDiagnosticCompanion` cannot connect because a development-team signing identity
is unavailable. Consequently storage, Xcode, runner, CoreSimulator, runtime, selected-target,
and fixture-diagnostic checks were **not checked** in that run. This does not prove or repair
the prior host CoreSimulator control-plane finding.

Resume condition: configure the companion signing identity, rebuild and reopen TVTestRig, then
run its read-only readiness gate. The user-paused simulator policy remains in force; a passing
readiness gate neither authorizes capture nor training.
