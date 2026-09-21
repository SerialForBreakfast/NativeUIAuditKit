# Local simulator smoke preflight — 2026-09-21

## App-managed repair accepted on this host — 21:03 UTC

New GUI PID 37440; matching helper SHA256
`25fc417aac660d4df9d5d5531c0bcc213c669d05911007e1d4d3605c5cb0dd6e`.
Producer 20:59 report identifies a repaired private-container path handoff, preserving
OS access and cleanup guards. One supported refresh on this changed build returned
outcome=ready, stage=companion_write_readback, workspace_mode=app_managed, exit 0,
609 ms, request 2B2A31E3-012D-4310-BD38-9D1A171FC8C4.

Exact-target readiness then passed: outcome=ready, can_run=true, can_restart=true;
all eight prerequisite checks ready, ownership source=persisted/state=clear.
Request 2DF19F2F-802F-40DE-9282-583449AE9B99, exit 0, 239 ms, 21:03:20 UTC.
Same booted UUID/runtime and Xcode 26.6 as below. Fixture remains not_checked.
The app-owned diagnostic references include
SimulatorDiagnostics/readiness-0ac8466b-411a-4797-b86c-287bfe8ba033/report.json.

This accepts storage/companion/readiness integration for the observed build only.
It is not a completed SIM-DATA-01 smoke, control baseline, capture/export or model
qualification. No Simulator input, restart, Office action or training occurred.
Next: verify exact Fixture endpoint and approved recipe/output access, then the
already-scoped one bounded smoke and intake/postflight. Do not infer arbitrary
project export permission from app-managed evidence access. Historical failures below
remain preserved and are superseded only for the passing prerequisite checks.

## Supported renewal failed — 20:35 UTC

Ran matching helper `--json --timeout-ms 30000 workspace refresh-access` once
under scoped approval. Exit 0 / transport success, but workspaceAccess outcome=failed,
stage=evidence_bookmark_stale, workspace_mode=app_managed. Request
E1228B68-5350-4332-B73A-EA0A8B5B466F, duration 468 ms, observed 20:35:28 UTC.
Producer message: companion access still failed after renewal; do not repeatedly
reselect folder or clear cleanup records.

Subsequent exact-target readiness request CD4D20C3-A7FC-4AC3-856F-AD278C35B284
(252 ms, exit 0) confirms can_run=false/can_restart=false, evidence_bookmark_stale,
cleanup_status_unavailable (ownership source storage). Toolchain checks still pass.
No capture, navigation, restart, signing change or repeated renewal. Remaining
producer defect is the failed app-managed renewal; the quoted TTR guidance routes
this case to producer investigation, not another user folder prompt. Smoke remains
unrun until storage and then exact-target readiness pass.

## Updated-build check — 20:33 UTC

New GUI PID 34812; matching helper SHA256
`4baf033dfe41ff01368cb53cee0212b54cddad14801d2e1a30718ab5e93d0a05`
differs from the earlier artifact. Exact-target readiness succeeded as a diagnostic
(exit 0, request E2A8F946-851B-4045-B2EC-7DE2BF2E7F43, 1063 ms).
Coordinator/companion/Xcode/runner/CoreSimulator/runtime remain ready. Storage is
still evidence_bookmark_stale. Target now explicitly reports cleanup_status_unavailable;
ownership entry source=storage, state=cleanup_status_unavailable. This is inaccessible
records, not evidence of an active runner. can_run/can_restart remain false; Fixture
not checked. No control, refresh, capture, restart or marker manipulation performed.

TTR NUIAK-STORAGE snapshot 20:21 reports repair implementation and producer-local
CLI/MCP qualification, not NUIAK acceptance. Current source exposes Repair Folder
Access and workspace refresh-access for the existing root. Next operation is a scoped
same-root grant refresh, inspecting ready/user_selection_required/busy/failed, followed
by fresh readiness. Human selection may be required. No alternate root or permission
weakening. This check-only request did not authorize a storage mutation outside NUA.

## Follow-up control-baseline check — 19:57 UTC

Same running GUI PID 30190 and matching helper. Exact-target readiness returned
success/exit 0, request `C9D54F46-76DF-4A74-8CE1-2E4BD932A09A`, duration 521 ms.
Coordinator/companion/toolchain/runtime checks still pass, but `can_run=false` and
`can_restart=false`: evidence_bookmark_stale and target_busy_or_cleanup_unknown.
No control, screenshot or Fixture operation was issued across the blocked gate.

TTR acknowledged our request at 19:48:48 UTC (NUIAK-STORAGE r1; producer-owned
NUIAK-ACCESS-01/03 and SIM-REL-01/02). Their source diagnosis says evidence-access
failure marks cleanup globally unknown: these two warnings may share one storage
cause. A stuck runner is NOT established. Planned repair is same-root bounded
grant/handoff renewal, explicit human selection if necessary, plus read-only
operation/marker/inaccessible-record details. Producer reports implementation not
dispatched. Its plan has not been transferred; this paragraph attributes their report,
not independent implementation verification. Sillycon's cancellation is unrelated.

Baseline ledger: discovery/IPC/toolchain availability evidenced; control transitions,
capture/labels, cleanup health and model accuracy NOT assessed. After storage repair,
refresh exact-target readiness before deciding whether cleanup reconciliation is even
needed. Then verify endpoint and one two-element Fixture smoke, validate receipt/index,
hashes and actual focus/box alignment, and check postflight. Only qualified pilot data
can support a separately assigned shipped-model baseline; no training baseline exists yet.

User authorized readiness and one bounded Fixture smoke, not Office, training,
Settings mapping, restarts or cleanup overrides. Broader simulator work remains paused.
Used current tvtestrig revision-7 skill and fixture supplement.

## Evidence

Running GUI PID 30190, matching helper:
`/Users/josephmccraw/Library/Developer/Xcode/DerivedData/TVTestRig-bfjtodidumtdyagsgxcmwrmheuxr/Build/Products/Debug/TVTestRig.app/Contents/Helpers/aatv`.
Helper SHA256: `22fa3ce64143533303872b4befef6f0e39cea13f38ab163bf9fceb542693ce86`.
Source checkout HEAD `8fe72fedfa52553d3d015b4b1ebde1163f37317c`; not asserted
byte-equivalent to the running app. No app rebuild, restart or signing changes.

Normal-host scoped execution: helper `--help`, `--json --timeout-ms 10000 simulator list`,
`simulator readiness`, `simulator readiness --simulator-udid
9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`, and `settings-map checkpoints
--simulator-udid 9026ECA9-77DB-4AE6-8FE6-BB239E9571FA` all exited 0.
JSON success means the check executed, not operational readiness.

19:37:45 UTC inventory: nine available tvOS simulators; exactly one booted:
Apple TV 4K (3rd generation), UUID above, runtime tvOS-26-5.
19:38:05 UTC exact-target readiness request `0A651F30-60C3-487E-926A-655D8F4FEDCD`:

- coordinator, companion, Xcode, runner, CoreSimulator and tvOS runtime ready.
- host macOS 26.4.1 (25E253); Xcode 26.6 (17F113), /Applications/Xcode.app.
- storage blocked: `evidence_bookmark_stale`; producer asks to refresh existing grant.
- target blocked: `target_busy_or_cleanup_unknown`; no specific operation ID returned.
- `can_run=false`, `can_restart=false`; Fixture not checked.
- Checkpoint query `D63832A8-6A1D-4136-BB88-A4F36B1F366A` returned an empty list.
  Empty checkpoints do not clear an active/unknown-cleanup guard.
- Diagnostic sink persistence warnings remain on stderr; structured commands succeeded.

## Result and resume

No smoke launched: explicit producer readiness blocks capture. No Simulator input,
Fixture mutation, capture lease, Office action or new output bundle. Nothing owned
by this attempt requires runtime cleanup. Fixture responsiveness remains unverified.

TTR needs to identify the stale grant's supported refresh path and the exact local
active operation/recovery guard, with safe reconciliation instructions. Do not assume
Sillycon's separately reported cancelled map explains this host's guard. Do not delete
markers, change workspaces to bypass checks, kill services or weaken permissions.
Resume with valid approved storage, reconciled local ownership/cleanup, ready exact
target and verified Fixture endpoint. One smoke remains the authorized scope; recheck
current availability before any mutation. Source presence does not qualify data.

Outcomes: software not assessed beyond successful runtime checks; data not assessed;
integration blocked; model not assessed. This supersedes historical local signing/
CoreSimulator failures only for the fresh checks above, not all SIM-DATA-01 acceptance.
