# Updated TTR capability check — 2026-09-21 21:40 UTC

Scope: read-only diagnosis and coordination. No capture, recipe/job creation,
restart, Office operation, source change or training.

## Observed runtime

- GUI PID 40739, still present at 21:39:43; matching app under
  `TVTestRig-bfjtodidumtdyagsgxcmwrmheuxr/Build/Products/Debug/TVTestRig.app`.
- Matching `Contents/Helpers/aatv` SHA-256:
  `efabf490b83d3d57c60ef735677e7909f7a8725be29e74c8b68d110d82515b71`.
- Clean producer source HEAD `1feaeac69d03a8bee0704064cbfb229866be2c6b`.
  This is source identity, not proof of all running binary contents.
- Help exits 0 and advertises recipe-json import, explicit-UUID simulator run-job,
  job status, manifest/read chunks and export. Producer revision-8 guidance supplies
  caller-side hash-verified transfer; repository-local installed skill remains v7.
  No protected skill files were modified. Help's generic assertion that --project
  is required remains inconsistent with documented app-managed support; no override used.

## Results

| Check | Result |
| --- | --- |
| Exact simulator readiness | Failed before target inspection: exit 69, serviceUnavailable, 1 ms; request A88EB10B-9799-402D-9166-7B643BABD0AD at 21:39:13 |
| GUI Unix socket inventory | `lsof -nP -a -p 40739 -U` returned no socket entries; GUI process still exists. Coordinator listener unavailable/not observed, not proof the app is absent |
| Fixture endpoint | Existing PID 37989 listens on 8080; executable path binds it to simulator 9026ECA9-77DB-4AE6-8FE6-BB239E9571FA |
| Fixture env | Exit 0, 11 ms; request DF8DCA5A-386B-4910-8EE1-5A40EC55A5FD at 21:39:56; tvOS 26.5, bounds 1920x1080, scale 2, Fixture 1.0/build 1 |
| Source contract changes | No changes since c2b1bc4 in batch engine, Fixture telemetry server or coordinator; requested-focus and baseline-geometry findings remain |

Helper stderr also reports `diagnostic_file_sink_failed/persistenceFailed`.
Its relation to coordinator startup is not proven. Fixture env succeeds through
HTTP despite the failed optional coordinator exchange; returned captureBinding
is unverified and endpointCorrelation is fixture_only_unverified. OS process/port
correlation is diagnostic evidence, not authenticated image identity.

## Interpretation / next action

The export capability gap has a producer implementation and is visible in the
matching helper's help. It is **not yet consumer-qualified**: no job/export ran.
The current immediate blocker is GUI coordinator startup/listener availability,
not simulator discovery, Fixture installation or a demonstrated signing failure.
Inspect TTR's local startup/storage diagnostics or any pending UI/debugger state;
do not infer which is responsible from process presence alone. No automatic
restart, root switch, permission weakening or repeated refresh was attempted.

After coordinator access is restored: exact-target readiness, then the previously
bounded smoke/job/export/intake. Preserve the separate ground-truth contract
request before scaling/training. Producer handoff's “observed focus” wording is
not accepted as proof because the inspected engine/telemetry code is unchanged.

Software: new CLI surface observed; full software verification not assessed.
Data eligibility: blocked. Integration qualification: blocked. Model gates:
not assessed. Prior readiness passes are historical, not current passes.

Coordination: NUIAK-EXPORT acknowledged our export request at 21:34:33, reporting
170 tests/18 suites and project-mode checks on the producer host. Those are peer
reports, not tests rerun here; app-managed consumer qualification remains open.
