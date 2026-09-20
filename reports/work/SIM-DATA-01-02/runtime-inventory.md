# SIM-DATA-01 local runtime inventory

Observed 2026-09-20 on the NUIAK Mac. This is a read-only inventory attempt;
it did not boot, install, reset, or otherwise mutate a simulator.

| Check | Result |
|---|---|
| Xcode developer directory | `/Applications/Xcode.app/Contents/Developer` was selected by `simctl` |
| Exact tvOS simulator UUID/runtime | Not available: `CoreSimulatorService` refused the connection, so no UUID may be selected or inferred |
| Fixture/helper artifact | No executable `aatv` artifact was found under the checked TVTestRig checkout or DerivedData paths |
| Fixture HTTP endpoint | Not inspected: without a selected simulator and matching helper, an endpoint binding would be ambiguous |
| Capture | Not attempted |

The concrete stop condition was `xcrun simctl list devices available` exiting with
CoreSimulatorService connection-invalid/connection-refused errors. No repair,
restart, or fallback was attempted because SIM-DATA-01 excludes those operations.

Resume only after the user has restored the local simulator service and a matching
TVTestRig helper/Fixture build is available. Re-run the read-only inventory, record
the actual UUID/runtime/build/endpoint, then obtain separate capture authority before
the minimal recipe. This result does not concern Sillycon or Office.
