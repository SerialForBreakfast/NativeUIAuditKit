# CLI and MCP differences

**Current policy, user decision 2026-09-19:** normal `fixture batch` uses reported
source context, not attestation. Neither physical nor Simulator factory issues a
pixel challenge. The challenge notes below describe retained optional/internal
machinery, not a required operator step. Use the additive dataset-index
`sourceDescription` and pair provenance to understand the collected source;
missing diagnostics are unknown, not a reason to block NUIAK. Keep fresh office
status, exclusive access and explicit runtime authorization. Unknown cleanup from
an earlier challenge remains a separate operational obligation.

Harvest now receives inline image bytes and provenance in one bounded coordinator
response; it no longer needs GUI write access to helper temporary-frame paths.
Per-frame metadata and telemetry-before/after checks describe the reported
source and scene. They are not authenticated hardware identity, and this
workflow does not require that stronger assurance.

Production fixture batch does not invoke the retained challenge protocol.
An older build may still fail at `identity_preflight`; use matching updated
app/helper builds, not re-pairing or a new identity investigation.
Failed runs after staging retain `.NAME.partial-UUID` siblings; never
promote those manually. A final destination appears only after exclusive atomic
publication, and existing destinations are not overwritten.

Every identity-required batch starts with fresh local identity state. Challenge
and clean-frame provenance are checked; HTTP revalidation reads fixture identity
and current run rather than trusting only cached values. This is not yet qualified
requested-hardware identity mapping. On failure inspect optional `cleanupCause`
alongside the primary cause: it means nonce cleanup was not confirmed. Do not
retry over an unresolved overlay or release another client's session. A missing
cleanup cause does not prove cleanup after abrupt termination or a lost issue
response. Offline tests are not signed-runtime or hardware qualification.

Before issue the helper records an owner in project-root
`.harvest-recovery-required.json`. An ambiguous issue response triggers one
bounded owner-revocation request, followed by clean-frame/scene checks. Unknown
cleanup retains this marker and an aborted diagnostic receipt; subsequent batches
in that workspace return `recoveryRequired`. Do not delete the marker, switch
workspaces, or retry to bypass recovery. Retained markers need maintainer
reconciliation under current device authorization; there is no automatic recovery
CLI yet. This is not a distributed lock: office requires fresh permitting shared
status, one machine at a time, and explicit user authorization.

In a TVTestRig source checkout, the offline repository script
`bash Scripts/validate-harvest-bundle.sh BUNDLE_DIR` checks bundle integrity without
contacting devices. It is not an installed CLI/MCP command. Exit 0 is integrity
only; its JSON explicitly says unverified provenance and no training approval.
Its result does not decide data-use eligibility or model promotion.

Harvest consumers should use `dataset-index.json` for output-relative artifact
paths/hashes when available, but still check the completion receipt. Layout v1
explicitly marks image/telemetry identity unverified; hashes prove byte integrity,
not the correct device or focus. Do not silently accept unknown layout versions.
Conflicting telemetry aliases now fail instead of preferring the canonical value;
do not strip conflicting fields to force acceptance.

New harvest builds run a read-only coordinator status preflight before fixture
mutation. Reachability is not proof of capture readiness or matching telemetry.
Read batch `error.stage`, `error.cause`, domain code and retryability; a path error
is not an unsupported provider. Infrastructure failures stop without automatic
retry and retain partial output. Inspect that evidence before choosing a fresh
destination. This is CLI-only; do not invent an MCP batch tool.
After output creation, inspect `harvest-receipt.json` for rejected recipes/steps
and terminal errors, including zero-row runs. Missing receipt can mean preflight
failure, abrupt termination or a write failure—not success. `completed` is not
proof of dataset provenance. Socket endpointMissing/accessDenied/refused causes
describe the connection attempt, not whether the GUI process is running.

These mappings were checked against the repository contract/catalog on 2026-09-14.
Runtime discovery takes precedence if the installed build differs. Check returned
capabilities and errors even when a command exists.

| Intent | CLI | MCP |
| --- | --- | --- |
| Discover | `device list` | `device.list` |
| Inspect capabilities | `device capabilities` | `device.capabilities` |
| Connect/disconnect | `device connect`, `device disconnect` | `device.connect`, `device.disconnect` |
| Press | `remote press right` | `remote.press` with `button: right` |
| Fixed remote macro | `remote macro NAME` | No direct macro tool |
| App inventory/launch | `app list`, `app launch BUNDLE_ID` | `application.list`, `application.launch` |
| Latest/fresh observation | `observe latest`, `observe capture` | `observation.latest`, `observation.capture` |
| Observation readiness | `observe status` | `observation.status` |
| Compact screen candidate | `observe inspect --device-id ID` | `observation.inspect` with `device_id: ID` |
| Focus classification | `observe focus --device-id ID` | `observation.focus` with `device_id: ID` |
| Wait for stability | `observe wait-stable` | `observation.wait_stable` |
| Fixture `/scene` probe | `fixture scene [--fixture-url URL]` | No MCP tool (CLI-only). GET `/scene` and print the payload. Office needs the TV HTTP origin, not `127.0.0.1`. |
| Fixture synthetic harvest | `fixture batch --recipes-dir DIR --output-dir DIR [--fixture-url URL] [--simulator-udid UUID]` | No MCP tool (CLI-only). Writes `<id>_unfocused.png` / `<id>_focused.png` / `<id>_metadata.json`. `--simulator-udid` is public simctl on that UUID only, not `booted`, and does not use the GUI socket. Office still needs the TV HTTP origin and IPC capture. |
| Read recipe/plan | `recipe get ID`, `recipe plan ID` | `recipe.get`, `recipe.plan` |
| Stop session | `session stop` | `session.end` |
| Audio status | `audio status` | `audio.status` |
| Capture-start evidence | `doctor` | `diagnostics.summary` |
| Capture-resource lease | `capture acquire`, `capture status`, `capture events`, `capture keepalive`, `capture release`, `capture complete` | `capture.acquire`, `capture.status`, `capture.events`, `capture.keepalive`, `capture.release`, `capture.task_complete` |

New builds include optional `captureStartup` in diagnostic summaries and MCP
diagnostic exports. It shares the clipboard's allowlisted operation history and
historical timeout guidance. Missing means an older producer, not a clean capture;
an empty history means no retained events in this app process. It is bounded to
8 operations × 64 events and resets on app restart. Historical timeout guidance
does not prove a current failure, a competing receiver, or that capture stopped.
Gather evidence before retrying; do not change permissions or restart an occupied
session automatically. These diagnostic commands can refresh discovery but do not
connect, start capture, or send remote input.

CLI global options include `--json`, `--device-id`, and `--timeout-ms`.
Installed builds with app-managed storage need no project argument. Explicit
development mode uses matching `--project` / `TVTESTRIG_PROJECT` and GUI workspace.
New GUI builds accept `--project PATH` at initial launch; it overrides the
environment just as in CLI. MCP uses the environment. Prefer the same absolute
path on both sides. Existing running apps are not retargeted by launching again;
do not restart an occupied app to fix a mismatch. The override does not grant
sandbox folder access or bypass the socket path-length limit.
Use bundled helpers from the same signed app; do not mix default and project modes.
Automated outputs stay in the active workspace. The GUI's optional Save/Export
action does not grant CLI/MCP permission to write outside it. Apply the user's
storage policy before capturing; do not assume app-storage permission for agent
build artifacts or other tasks.
Check `success` and typed `error`, not just process output. Diagnostics may appear
on stderr while the result envelope is on stdout. Preserve both where useful.

MCP uses schema fields such as `device_id`, `timeout_ms`, and, where supported,
`idempotency_key`. It is not mechanical space-to-dot conversion. Use published
`control.status`, `control.acquire`, and `control.release` for ownership; respect
lease duration and current holder. Do not assume CLI accepts MCP lease commands.

Observation calls can initiate capture or write artifacts. They are not neutral
inventory operations. CLI observations support `--output`, raw PNG `--stdout`,
or JSON `--base64`; either inline mode may also be combined with `--output`.
MCP observation schemas here do not accept an `output_path`, and MCP's default
inline-image limit remains zero. Use returned artifact references, not fabricated
local paths or presumed MCP image bytes.
Use `observe status` / `observation.status` before diagnosing readiness. An empty
current-epoch cache is `noObservationRecorded`, not provider failure. Explicit
`--auto-capture` / `auto_capture: true` permits `latest` to capture once only
when that cache is empty; without it, `latest` remains cache-only.

Compact inspection requires an already-active evidence session and the selected
authorized `office` device. It captures once, retains evidence in the session and
returns candidate screen/focus text without image bytes or raw OCR. The current
profile covers English dark 1080p Settings only. `unrecognized` is not a failure
to capture; `candidate` is not verified focus, a setting value or permission to
execute cached navigation. Use image evidence for ambiguity, not repeated blind
inspection. Do not start or take over another session just to use this command.
Its deadline is capped at five seconds; stale/reconnected context is rejected.

Control authentication, video delivery and audio capture are distinct states.
Connected control does not imply an active video stream or the TV's red recording
border. Audio `stop` can finalize a file without tearing down preview. Verify the
actual lifecycle status rather than treating these labels as interchangeable.
`resourceContended` on observe/capture/lease acquire means wait (`suggestedAction:
wait`); it is not permission to steal the stream or a failed camera that should be
reacquired. `aatv capture acquire --wait --wait-timeout-ms N` (MCP `wait` /
`wait_timeout_ms`) holds the request until a peer unpublish or local release.
Capture-lease commands are listed in the table above and are
independent of `control.acquire`. An unexpired `_tvtr-lease._tcp` peer record
marks the device busy (`crossHostPeerLease`); do not treat lease ads as extra
Apple TVs.
