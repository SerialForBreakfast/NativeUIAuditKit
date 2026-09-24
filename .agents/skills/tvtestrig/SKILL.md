---
name: tvtestrig
description: Operate and diagnose Apple TV navigation, screen observation, and audio capture using TVTestRig CLI or MCP. Use for authorized TVTestRig device workflows and evidence collection, not desktop automation.
---

# TVTestRig agent operation

Portable candidate revision 7, 2026-09-21. This folder is the complete skill;
copy it as a unit. The app bundles this package and exposes Export Agent Skill
in Automation. Export does not automatically install it in an agent host.

## Scope and preparation

- Apply the user's current device allowlist and workspace rules first. Discovery
  does not authorize operation. Bind the exact authorized name to its discovered
  stable ID; do not embed one developer's IDs, paths, or credentials in a workflow.
  No target is authorized by this skill: NUIAK's current assignment names either
  an exact simulator or physical device. Prior Office windows are not continuing grants.
- Use TVTestRig CLI/MCP, not desktop control. A skill does not grant permission
  for pairing, system consent, installation, route changes or accessibility changes.
- TVTestRig must be open. Use an available approved app-launch path if permitted;
  do not install login items or restart an occupied app/session to solve availability.
- Discover actual runtime commands, schemas and capabilities before dispatch.
  Read device, provider, audio and ownership state first. Preserve an existing
  session; inventory alone must not start capture or reconnect a device.
- MCP mutations need the controller lease required by their schema. Do not steal
  an occupied station. Use one serialized controller, including when using CLI.
  Capture occupancy is a separate 30-minute resource lease (`capture acquire` /
  `capture.acquire`). `resourceContended` means wait; do not start a colliding
  session. Optional `--wait` / `--wait-timeout-ms` (MCP `wait`, `wait_timeout_ms`)
  queues until a local release or peer `_tvtr-lease._tcp` unpublish. Poll
  `capture events` / `capture.events` for idle warnings; after expiry you must
  acquire again. Unidentified GUI captures are not auto-enrolled.
  `capture complete` / `capture.task_complete` finalizes the evidence session and
  optionally releases capture resources as separate outcomes; `session stop`
  does not imply capture release.

## Choose the interface

NUIAK maintenance overlay2026-09-23: for current build/feature qualification read
[the local repair loop](../../../Research/WorkerExecution/references/operational-lessons.md#ttr-featurerepair-qualification).
The portable revision7 examples below and in interfaces.md are historical source
contracts, not a current capability inventory or authority. In particular, later
simulator app-managed jobs and supported chunk export have qualified recorded
scopes; do not reimpose old Office-only job restrictions or infer fresh readiness.
Use installed help/source and actual exact-build evidence before dispatch.
For cross-machine work use [SMB coordination](../../../reports/coordination/SharedStatusSkill.md),
not SSH; local runtime discovery precedes deciding which host must execute.

For an installed DMG, no development team or source build is required. For an
explicit source-build/launch request or signing setup failure, first read
[building and launching](references/interfaces.md#building-and-launching).
Use the ignored local team configuration, not Xcode target-dropdown edits or
re-signing an installed app. A build/launch request does not authorize device tests.

Use MCP when available for typed discovery and bounded actions. Use CLI for
repeatable local sequences and retained JSON evidence. Both address the same
coordinator, not independent receivers. Do not switch transport to evade a gate.
Use Automation → Copy Helper Launch Check to obtain this app's exact helper path.
For startup aborts, sandbox isolation boundaries, or app-owned recipe staging, read the
[launch and workspace guidance](references/interfaces.md#helper-startup-and-workspace-preflight)
and the NUIAK-local [permission diagnosis guide](../../../Research/SandboxOperations.md)
before retrying. A launch check never authorizes a device operation.

NUIAK-local supplement (not part of the producer's portable skill): identify the
denying process/layer before proposing repair. Reuse approved execution setup for
known tool limitations, but never infer continuing permission. A helper launched
by a restricted parent may inherit restrictions; removing its entitlement is not
a remedy. Preserve completed captures if only export failed. Do not re-sign,
disable sandboxing, reset privacy consent or restart services to fix an unclassified
error. The local guide is repository policy, not a new producer capability.

CLI examples (substitute the authorized discovered ID; executable must be verified):

```sh
aatv --json device list
aatv --json --device-id AUTHORIZED_ID device capabilities
aatv --json --device-id AUTHORIZED_ID recipe plan voiceover-toggle
```

Read [interface differences](references/interfaces.md) before translating between
CLI and MCP. A published recipe or command is not proof its runtime is qualified.
Inspect recipe blockers; do not invent `recipe.run` or approximate an unavailable
atomic gesture using unrelated button presses.

## Navigate and verify

1. Establish current target, observation age/source and focus before input.
   Remembered focus can differ from a historical recipe's starting position.
2. Send bounded inputs whose effects remain within scope. Verify focus immediately
   before Select when it could change a setting, activate playback or exit a test.
3. Reobserve after modal transitions, app launch, disabling the focused button or
   changing VoiceOver. These can move focus; don't reuse the old navigation path.
4. A successful command means accepted/completed input, not that the expected UI
   changed. A stable frame is not proof of correct focus or complete animation.
5. If a timeout leaves completion ambiguous, inspect current state before retrying.
   Reuse an idempotency key only where supported for that same logical request.
   Do not blindly repeat Select or overlap a possibly running operation.

Use logs, structured state and local measurements for repeated checks. Inspect
images when they resolve target/focus, settings, or an unexpected state—not every
poll. Cached `current` metadata must still be checked against its timestamp.

### Navigation lessons to apply

- Wait for focus as well as the screen: two matching focusless snapshots can
  describe a transition, not readiness. Use bounded settling, not arbitrary sleeps.
- Native tvOS accessibility can omit a disclosure chevron when a row gains focus
  and continue omitting it afterwards. Moving away/back is not a reliable repair.
  Treat observed chevrons, native submenu contracts and vision predictions as
  distinct evidence. A chevron alone does not authorize Select or prove no side effect.
- Never infer an intermediate route from its final screen. Verify each entered
  child and each backtrack; direct app activation is setup, not remote navigation.
  Track full path plus observed screen identity so duplicate labels do not merge.
- Keep navigation changes separate from setting changes. Entering a verified
  chooser may be allowed; choosing a value, accepting terms, installing profiles,
  signing in/out, purchasing or resetting needs its own authorization.
- Keep local observation/action loops within qualified bounds; send agents compact
  progress and evidence references. Cached routes need fresh entry checks and
  interruption handling. Do not claim token savings without measurement.
- Preserve failed attempts. After equivalent failures, change the hypothesis or
  use an already-supported safe omission rule; do not repeat ambiguous Selects.
- Report navigation outcome, exclusions, runner cleanup and post-test app health
  separately. A passing XCTest and successful foreground return can precede a crash.
  Verify a fresh target-correlated health response after teardown when available;
  otherwise mark health unverified. Never substitute process presence for health.

### Exhaustive DFS requests

Use one bounded TTR session, not one model/tool turn per remote button. Discover
the installed policy and command schema once, start the authorized broad policy,
then read compact status at 15–30-second intervals when progress is needed. Fetch
the full export at terminal state or a meaningful failure, not every poll. Keep
run/operation IDs and a small ledger of counts, stop reason and evidence paths;
filter base64 checkpoint/image lines from log excerpts. Older Simulator status
may show zero progress until completion—zero is not proof it is stuck.

The local loop is **observe → first eligible row → descend → verify child →
Back/verify parent → next sibling**. Scan mixed lists to their verified boundary;
information/editor/no-navigation leaves return without editing or selecting values.
Skip excluded/disabled rows, but stop on unknown context, dialogs, uncertain input
or cleanup. Never retry Select blindly or restart a service to hide failure.
Resume only a compatible non-pending checkpoint with reconciled cleanup and fresh
context. Do not invent graceful-pause/budget flags absent from the installed schema.

Use OCR/similarity as evidence, not action authority. The current Simulator oracle
is native AX plus raster checks; host Vision substrate is not automatically its
live oracle. A similarity hit can miss a small modal/focus shift; fresh full-context
and policy checks remain required. Exact-image text reuse cannot reuse freshness
or focus. Inspect an image only when it resolves uncertainty; retain full local
evidence and report unmetered token savings as unknown.

First check the advertised policy and driver against the requested coverage. A
complete safe traversal requires deterministic child ordering, scroll-to-end
discovery, stable row/screen identities, cycle detection, verified parent return
and retained progress at budget/interruption boundaries. A clipped viewport, a
budget limit or skipped disclosure leaves coverage incomplete, even if status says
`completed`. Record each candidate as entered, excluded by policy, unresolved,
unavailable or not reached; do not turn blocked rows into successful edges.

Do not equate “all settings” with every state obtainable by account changes,
network setup or toggles. Cover safely reachable screens in the authorized starting
configuration, and explicitly report action-dependent branches. If TTR lacks
required scrolling/policy/identity support, name that capability gap instead of
rerunning the restricted crawl and calling it exhaustive. Do not bypass TTR with
desktop automation, arbitrary scripts or a physical-device fallback.

## Compact inspection (candidate only)

Use compact inspection when an **active evidence session** already exists on the
authorized device, you need a digest-bound screen/focus **candidate**, and you must
not pull inline PNG bytes into the agent context by default.

Prerequisites: TVTestRig open; session started; device connected and selected;
exact authorized target bound. The call does **not** connect, start a session, or
send remote input. MCP requires the controller lease policy for artifact writes.

| Intent | CLI | MCP |
| --- | --- | --- |
| Compact screen candidate | `observe inspect --device-id ID` | `observation.inspect` with `device_id: ID` |
| Focus classification | `observe focus --device-id ID` | `observation.focus` with `device_id: ID` |

Outcomes: `candidate` (heuristic label only), `unrecognized` (valid non-match), or
typed errors for stale/missing session, wrong target, or timeout. Timeout does not
prove capture or OCR finished. **Neither outcome grants route execution authority.**
Profile today: English dark 1080p Settings-oriented screens only—not general apps,
full modal coverage, or qualified navigation graphs.

Prefer [`observe latest`](references/interfaces.md) / `observation.latest` when you
need raw pixels; use compact inspection to reduce payload size when the candidate
envelope is sufficient. Do not claim token savings without measured trials.

For repeated read-only screen delivery, use `observe poll --consumer-id LABEL`
or `observation.poll`. Every poll captures and retains fresh local evidence.
Only echo the returned full observation ID after retaining that image; a later
unchanged receipt omits delivery only when exact canonical pixels match for the
same consumer. It never authorizes navigation or replaces fresh inspection.

## Simulator diagnostic

Start with `aatv simulator readiness [--simulator-udid UUID]` or MCP
`simulator.readiness`. It separates coordinator/companion, evidence access, Xcode,
packaged runner, CoreSimulator service, runtime and target checks. Missing devices
does not mean a runtime is missing. `execution_access_denied` is an execution-context
failure, not evidence a restart will help. Keep the selected Xcode consistent.

TTR may reconnect its own XPC handshake once; it never replays uncertain input.
With explicit permission and exclusive use, `simulator restart --simulator-udid UUID
--confirm-exclusive` / MCP `simulator.restart` with `confirm_exclusive: true` restarts
only a freshly verified booted tvOS target. Active operations/unknown cleanup block
it. It does not erase data or resume navigation. A lost reply is not retryable:
reconcile the target and retained marker. Host-wide recovery remains user-guided;
do not kill services, delete caches or substitute another target. Check Again and
Copy Diagnostics in Setup expose the same readiness information without Xcode.

Use `aatv simulator list` or MCP `simulator.list {}` to find the exact local tvOS
UUID, runtime, availability and boot state. Setup exposes this same inventory.
Missing companion/Xcode access is unknown, not proof that no Simulators exist.
Listing never boots a target, pairs, or authorizes navigation. Do not pass a
Simulator UUID to physical-device controls; the interfaces remain separate.

For an explicitly authorized existing tvOS Simulator, use `aatv simulator diagnose
--simulator-udid UUID` or MCP `simulator.diagnose` with `simulator_udid`. This is
navigation-mutating, not status polling. Require the app's matching embedded
companion/runner and approved runtime storage/setup; never substitute a physical
station or desktop automation. The fixed probe activates Fixture as explicitly
labeled setup if it is not foreground; missing Fixture stops qualification. The probe's
direct Settings activation is not a Home-route test, account `unknown` is not
signed-out, and Fixture reactivation is not restoration of the prior app/focus. Raw evidence
stays local. If cleanup is unknown, preserve its unfinished-operation marker and
reconcile the old runner before retrying; do not reset services or delete the marker
to bypass the block. Compiled/packaged is not live-qualified.

## Bounded Simulator Settings mapping

When explicitly authorized for broader read-only discovery, select
`--policy-version settings-map-disclosure-v1` (Simulator only). It admits observed
disclosure rows across Settings rather than the original branch allowlist, but
unsafe action-text exclusions still veto Select. Terms of Use/Terms and Conditions,
License and Warranty are informational views; agreeing/accepting is a separate
blocked action. This mode uses native accessibility text with the exclusion rules,
not an independently qualified OCR reading. Disabled native cells are unavailable,
even if they display chevrons. The four reviewed native submenu contracts remain
separately labeled; missing evidence elsewhere remains a coverage gap. Discovery
scans mixed disclosure lists downward for newly exposed rows from their top;
pure no-chevron lists are leaves and return without scanning value choices.
Disabled rows still trigger bounded scanning because they may hide disclosures,
with bounds of 30 minutes, 2,000 inputs, 150 screens and depth 12. Only a completed
frontier with accounted-for omissions supports a coverage claim; a budget/ambiguity
stop is partial. Same-session chevron memory requires unchanged row content and
is invalidated by disabled/toggle classification or changed content.
For first/focused rows whose visible chevron is omitted by AX, the fixed runner
also checks the trailing row pixels for a right-chevron shape. This is local raster
evidence, not NUIAK inference. Apply the same text exclusions and fresh-focus checks.
Read-only information overlays are leaves; an entered text editor is also a leaf:
record it and Back without typing, selecting a value, saving or accepting anything.
Retained page captures wait for matching pixels; report settling timeouts explicitly.

With an authorized Simulator scope and ready matched companion, use `settings-map start
--policy-version settings-map-v1 --simulator-udid UUID`, then `settings-map status`,
`cancel`, and `export` with its run ID. The corresponding MCP `settings_map.*`
operations use the same coordinator. This is a separate navigation-mutating request;
`simulator.diagnose` never starts DFS automatically and is not a mandatory
Fixture-launching prerequisite for a qualified Settings-only map. The map runner activates only
Settings as labeled setup and runs the shared DFS with native accessibility as
its oracle. It never launches/returns to Fixture and leaves Settings at the last
observed context; original app/focus restoration is not attempted. This separation
does not change the ordinary Fixture diagnostic. It does not qualify the Home route or
NUIAK vision accuracy. Bounds: 10 minutes, 50 inputs, 20 screens, depth 4.

Earlier Fixture-return maps on tvOS 26.5/Xcode 27 reproduced transitions but also
Fixture teardown crashes. Settings-only maps now collect two timestamped,
exact-Simulator process observations after teardown without launching an app or
starting another XCTest session. `present` is not responsiveness or crash-free
proof; `not_observed` is absence from that listing, not a diagnosed crash;
`unknown` means collection/parsing failed. A changed PID is not uninterrupted
survival. Preserve these results separately from map/runner success and
`post_teardown_health`. Broader runtime/replay qualification remains open.
Native tvOS 26.5 may omit
disclosure decorations even after a row loses focus. The fixed Simulator adapter
can also recognize four reviewed label-only submenu entries (General, Accessibility,
About and VoiceOver on their exact parent paths); this is labeled native contract
evidence, not a detected chevron. Physical/OCR selection still requires a chevron.
Do not assume a complete map: only observed viewport rows are explored. Missing
native disclosure can omit a row with `native_disclosure_unavailable`; it is never
selected or reported as an observed edge. Missing focus or changed screens still
stop with partial evidence. Runtime progress counts are published at
session completion, not per key. Cancellation requests stop the owned launcher;
they do not prove the underlying runner stopped. Unknown cleanup blocks target reuse
until reconciled. Inspect both map stop reason and `simulatorDiagnostics` in exports.

## Audio and accessibility tests

Read [capture protocol](references/capture-protocol.md) before audio, ReplayKit or
VoiceOver testing. Include a named navigation-sound segment in every audio test,
and record VoiceOver state separately. Never silently toggle it.

## Completion and maintenance

Retain failed and invalid trials alongside successes. Report observed outcome,
evidence paths, unresolved limitations, cleanup state and next useful step.
Separate offline/compiled checks from live qualification. Restore authorized
setting changes to their recorded original values and verify restoration; stop
only resources owned by this test. Release its lease and disconnect when owned
and appropriate; don't tear down another user's stream.

When a new incident changes the workflow, update the relevant reference and retain
the incident evidence separately. Keep hypotheses labeled, omit station secrets,
and validate a copied package's relative links and contracts before publishing.
Packaging validation is not an agent-performance or hardware qualification score.
