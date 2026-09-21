# CLI and MCP differences

## Building and launching

**Installed DMG:** use the installed signed app and its own
`Contents/Helpers/aatv` or `tvtestrig-mcp`. Users do not need a development team,
certificate, source checkout or Xcode for core functionality. Simulator functions
add compatible Xcode/runtime prerequisites. Do not ask a DMG user to configure
LocalSigning, rebuild, or re-sign as a generic recovery step.

**Building from source:** use the requested checkout and its repository instructions.
From that checkout's root, run:

```sh
ruby Scripts/configure-signing.rb --list-teams
ruby Scripts/configure-signing.rb --team SELECTED_TEAM_ID
ruby Scripts/configure-signing.rb --check
```

Choose the user's Apple Team ID (ten uppercase letters/digits), not their email.
Do not guess among multiple teams. `--list-teams` reads valid development identities;
it does not create certificates. If none is available, the user manages their
account/development certificate through Xcode Settings → Accounts. No credential
or Keychain changes are performed by the script. A check in restricted execution
may lack Keychain visibility; preserve that context instead of claiming the host
has no certificate or repeatedly rebuilding.

`--team` exclusively creates `TVTestRig/Config/LocalSigning.xcconfig`, already
ignored by Git. Repeating the same selection leaves it unchanged; a different or
custom existing file is preserved and requires deliberate editing. Keep tracked
target settings as `DEVELOPMENT_TEAM = $(TVTR_DEVELOPMENT_TEAM)`. Using Xcode's
Team dropdown can replace that expression with a literal tracked override. The
checker identifies this but never repairs project files or changes Git state.
Commit the template/shared indirection, never local choices or private keys.

The pre-build check validates persisted settings and an available identity, not
every future command-line override or actual code signatures. Do not override
DEVELOPMENT_TEAM elsewhere after it passes. Release signing/notarization remains
the separate explicitly configured release pipeline, not this development setup.

Build in an isolated project-local directory; do not share the user's active
DerivedData or replace a running app. Reuse a verified, locked project-local
package cache; if missing, obtain the repository's dependency-resolution approval.
Example signed Debug build, with the existing cache below verified first:

```sh
build_root="$PWD/.local-work/signed-development"
package_root="$PWD/.local-work/packages"
test -f "$package_root/workspace-state.json" || exit 66
mkdir -p "$build_root/tmp" "$build_root/module-cache"
export DEVELOPER_DIR="${DEVELOPER_DIR:-$(/usr/bin/xcode-select -p)}"
export TMPDIR="$build_root/tmp"
export LLVM_PROFILE_FILE="$build_root/coverage-%p.profraw"
xcodebuild build -project TVTestRig/TVTestRig.xcodeproj -scheme TVTestRig \
  -configuration Debug -destination 'platform=macOS' \
  -derivedDataPath "$build_root/DerivedData" \
  -clonedSourcePackagesDirPath "$package_root" -disableAutomaticPackageResolution \
  CLANG_MODULE_CACHE_PATH="$build_root/module-cache" \
  SWIFT_MODULE_CACHE_PATH="$build_root/module-cache" \
  > "$build_root/build.log" 2>&1 || exit $?
app="$build_root/DerivedData/Build/Products/Debug/TVTestRig.app"
ruby Scripts/configure-signing.rb --check --app "$app" || exit $?
```

Choose a fresh owned build/log directory for each independent candidate. This
command does not disable signing or change the sandbox variant. For Simulator
qualification require `TVTR_REQUIRE_SIMULATOR_RUNNER=YES` on the build and inspect
the bundled runner manifest plus `Scripts/check-portable-simulator-gate.sh --app`
with the absolute app path. A packaged runner is not live-qualified navigation.
Normal Apple-managed caches/logs are distinct from explicit project-local outputs;
follow the user's filesystem policy rather than changing HOME or global Xcode.

After the post-build signature check, launch only with user authorization and no
conflicting running TTR owner. For a project-local development workspace:

```sh
open "$app" --args --project "$PWD"
"$app/Contents/Helpers/aatv" --help
"$app/Contents/Helpers/aatv" --project "$PWD" --json status
```

Do not use `open -n`, kill another instance, or assume `open` changed an existing
process's workspace. Retain any folder-consent requirement; a path is not a grant.
Use this exact app's helper, never one from an older DerivedData folder. Launch,
coordinator JSON, storage readiness and target readiness are separate checks.
Do not connect, capture or navigate as an incidental build smoke. For failures,
use the helper-startup guidance below and copy Setup diagnostics, including a
not-checked/failed result; empty inventory alone does not establish a host outage.

## Helper startup and workspace preflight

Use the running app's matching bundled helper on the same host. Automation's
**Copy Helper Launch Check** copies its quoted absolute path plus `--help`;
copying does not execute it. Keep stdout, stderr, exit status and build identity
when startup fails. Exit 134/SIGABRT with no structured output can occur before
TTR starts under an agent execution sandbox; it is not alone proof of that cause,
an Office connection failure, or a broken package.

Request the agent host's explicit execution approval for one **identical help-only**
invocation in normal host execution. Never auto-escalate, disable app sandboxing,
re-sign, change HOME, or replay the failed device/mutation command. If help works
there, use that approved execution context for separately authorized read-only
preflight. If it still fails, stop and retain the exact artifact's crash/loader
evidence; do not prescribe rebuilding or re-pairing without a diagnosed defect.
If approval is unavailable, report execution blocked; do not seek a workaround.
MCP process startup can encounter the same boundary, but a CLI help pass does
not prove MCP transport readiness.

Then check coordinator/target readiness under current authorization. For the
independent staging gate, discover `fixture prepare` in the installed help:
`aatv --json fixture prepare --recipe FILE` sends recipe bytes to TTR over IPC.
No manual container writes or HOME symlinks. Read `storageReady` and the job ID;
this does not start capture or authorize `run-job`. If the command is unavailable,
report an older build/capability gap, not permission to stage externally. Follow
the job workflow below for authorized execution and hash-verified export.

Both clipboard diagnostic actions include cached Fixture telemetry when available,
with observation time, age, process/source references and stale/unavailable labels.
Copying never refreshes it. Do not equate a recent snapshot with current connection
health or the selected target. Share sanitized diagnostics, not credentials or raw
private crash payloads, with the consumer.

For MCP in a development checkout, set `TVTESTRIG_PROJECT` in the client launch
environment; `tvtestrig-mcp` accepts no positional launch arguments. Keep stdin
open between JSON-RPC requests. Do not pass CLI's `--project` to that executable.

## Simulator map resume and teardown (new builds; live qualification pending)

Settings maps activate only Settings, never Fixture, and leave the terminal
context in place (`return_outcome: notAttempted`). The optional
`settings_process_observations` array in diagnostic exports contains two
post-XCTest observations (`observed_at`, `state`, optional `pid`) from the exact
Simulator. Missing means an older producer. These checks cannot relaunch an app
or send input. They do not establish UI responsiveness or restore original focus.

- `settings-map checkpoints --simulator-udid UUID` / `settings_map.checkpoints`
  reads retained local journals without contacting the Simulator. A
  `resume_candidate` still requires fresh readiness, authorization and context
  verification. Unknown cleanup or pending input blocks resume.
- `settings-map resume OPERATION_ID --policy-version VERSION --simulator-udid UUID`
  / `settings_map.resume` (`operation_id`, `policy_version`, `simulator_udid`)
  starts a new bounded segment. Use the diagnostic **operation ID** from checkpoint
  discovery, not the transient map run ID. Exact target, runtime, OS, locale and
  policy must match; each ancestor is reobserved before Select. Frontier/visited
  state is retained, not old action authorization. Poll/export the new map run ID.
- Journals are versioned, capped at 64 KiB and saved inside the selected evidence
  workspace. Oversized/unwritable journals stop before the next crawl input.
  Old summary-only maps cannot be resumed. Do not edit journals, stage them in an
  app container, delete recovery markers or replay an unconfirmed input.
- `simulator teardown-check --simulator-udid UUID --variant VARIANT` /
  `simulator.teardown_check` (`simulator_udid`, `variant`) is an authorized test,
  not inventory. Fixed variants are `session_only` (Fixture activation),
  `settings` (then Settings, left foreground), and `fixture_return` (then Fixture).
  No remote buttons or settings changes; app activation still changes context.
  `post_teardown_health: not_verified` must not be interpreted as healthy.
  Compare target-correlated logs and a fresh post-session Fixture response before
  attributing a crash or claiming a fix. Unknown cleanup blocks another run.

Focused explanatory text can veto a disclosure row, not just its label. A
destructive confirmation is a stop; automatic Cancel dismissal is not implemented
or authorized by these tools. No physical-device fallback exists.

## App-owned fixture jobs (new builds)

Use `fixture prepare --recipe FILE` when the caller cannot write the app's
workspace. It transfers one JSON recipe through IPC; TTR creates a unique job
directory and returns its UUID, resolved paths, recipe SHA-256 and `storageReady`.
Preparation/status/export never contact Office. Storage readiness is not capture
readiness. Never stage files manually inside another app's container or change HOME.

After separate explicit authorization, fresh permitting coordination status,
exclusive use, connected Office and the correct live Fixture origin, use
`fixture run-job UUID --fixture-url ORIGIN --device-id ID`. It runs the existing
harvest engine asynchronously with an owned capture lease. Poll
`fixture job-status UUID`; never repeat start after a lost reply. Cancel using
`fixture cancel-job UUID`, then inspect terminal state. The ten-minute bound
requests cancellation, not proof of teardown. Failed attempts remain local;
interrupted/unconfirmed cleanup blocks another run pending maintainer reconciliation.

For a `completed` job, `fixture export-job UUID --output-dir NEW_DIRECTORY`
copies bounded IPC chunks and verifies chunk and file SHA-256. The CLI—not the
sandboxed app—writes the approved destination. Its parent must exist and be writable;
existing destinations and symlinks are refused. Failed transfers retain
`.ttr-export-UUID` partial directories beside that destination; never ingest these.
JSON includes file hashes and `exportedPath`. Source paths are informational, not
caller write permissions. Integrity does not confer training eligibility.

Limits: one 256 KiB recipe/job; 64 retained jobs; one active job; 256 KiB chunks;
32 MiB/file, 256 MiB/export, 4,096 files. No automatic deletion. CLI/IPC only—do not
invent MCP job tools. Job execution is Office-only; the legacy explicit-Simulator
`fixture batch` lane remains separate. The packaged Simulator batch now delegates
fixed screenshots to the existing signed companion, never direct developer-tool
execution from the sandboxed CLI. Explicit `--project` is the output boundary and
reuses that project's saved grant; a path alone is not a filesystem permission.
Signed/consumer qualification remains separate.

## Existing harvest interface

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
| Fixture synthetic harvest | `fixture batch --recipes-dir DIR --output-dir DIR [--fixture-url URL] [--simulator-udid UUID]` | No MCP tool (CLI-only). Writes paired PNG/metadata. Simulator screenshots use the signed companion and exact UUID, never `booted`; no physical fallback. Verify the Fixture endpoint belongs to that Simulator before scene mutation. Office needs the TV HTTP origin and IPC capture. |
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
