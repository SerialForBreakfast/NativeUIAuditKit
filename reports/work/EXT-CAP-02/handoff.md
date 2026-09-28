# EXT-CAP-02 — consumer discovery and local interface tests

2026-09-28T15:43:24Z · owner: current NUIAK TTR consumer worker  
State: **partial; pairing/live transport blocked on endpoint and human target/grant confirmation**.

## Scope and outcomes

User requested fresh TTR status, testing the producer's pairing/registration/Simulator transport request, and feedback. This report preserves completed checks, not a full EXT-CAP-02 acceptance claim.

| Outcome | Result |
| --- | --- |
| Software verified | Partial: actual remote CLI help/status/register and standalone MCP initialize/tools-list pass. No code changed, no claim of full software qualification. |
| Data eligible | Not assessed: no captures, downloads, annotations or admitted examples. |
| Integration qualified | Blocked: service discovery returned no candidates; pairing, agent-host activation and two-host grant/capture/review/finish unrun. |
| Model gate | Not assessed; no inference/training/export/promotion. |

## Producer update received

Verified mounted SMB endpoint `sillycon.local/SharedStatusFile`. Safely parsed schema1 status with duplicate-key rejection; observed producer update `2026-09-28T15:32:34Z`, valid until `2026-09-29T15:32:34Z`.

Exact metadata verified against the producer's published sizes/hashes:

| File under `tvtestrig/` | Bytes | SHA-256 |
| --- | ---: | --- |
| `ttr-ext-cap-consumer-runbook-20260928T153135Z.md` | 5252 | `64dad7d1a985f84e47eb5157697132cce27a4e4f40de69fc44895ddd17657517` |
| `ttr-external-capture-plan-rev2-20260928T062700Z.md` | 21249 | `99a1f1650c9920a17c127497df8ff37723ea1a0e03d26c95e1ee3181714433cf` |
| `ttr-external-control-response-20260928T012443Z.yaml` | 2088 | `0ab2d34c762ffc91b77485ed7b9d93b78762d3f9f0b5339b71032df76558b1cb` |

New runbook requests a local source build at `c45f3e739386250c0f038f49b7052e7f47704e07`, swift-certificates1.19.3, and reports only Xcode27.0 testing. Producer says this revision is not yet pushed; release builds remain paused. Local adjacent producer checkout HEAD is `46dce7b3a79e4f17af49bc0324d4aeba3cc0958d`; `git cat-file -t c45f3e739386250c0f038f49b7052e7f47704e07` exits128, object unavailable. Existing unrelated producer edits were inspected read-only and preserved. No fetch, checkout, build, dependency install or source change performed.

This source mismatch does **not** establish that the available app is old: an actual development app contains the new helpers and responds successfully. Its exact source-to-binary receipt remains needed.

## Local executable evidence

App observed at:

`/Users/josephmccraw/Library/Developer/Xcode/DerivedData/TVTestRig-fssavpzkujakgqggjglqjvvrtyoo/Build/Products/Debug/TVTestRig.app`

- `Contents/Helpers/tvtestrig-remote` points to `../MacOS/TVTestRig`.
- Executable SHA256: `e97a762a88b11ce27f3264338eccb64607ec3726aff8012c65c74ec9fb4ea815`.
- Debug dylib SHA256: `13ae29d28a80caa270626f26100db5a32cbbde0c6cf9aeda9ac43bdac08c3927`.
- These are component hashes, not the producer's full candidate `51652c05…` hash. Exact build/source equivalence is **unverified**.
- Restricted `help` launch: exit134, no structured response. Identical help-only host-execution check: exit0. This is an execution-context distinction, not evidence of server failure.
- Restricted signature check: `CSSMERR_TP_NOT_TRUSTED`; identical `codesign --verify --deep --strict` with normal host visibility: exit0. No signing/trust configuration changed.
- Restricted `ps` failed `operation not permitted`; no current host-process inventory or server occupancy inferred.

Explicit local client state root:

`reports/work/EXT-CAP-02/client-state/`

All CLI probes supplied its absolute path via `--state-dir`; the standalone MCP probe supplied the same path via `TVTESTRIG_REMOTE_STATE`. No pairing identity was created by these probes.

## Actual checks

| Check | Result | Limit |
| --- | --- | --- |
| Remote CLI `help` | exit0 in approved host context; discovers supported commands and state-dir override | Grant explicitly permits stills only, no navigation/input/audio/inference |
| `status` with explicit project state | exit0; paired=`no`, empty public fingerprints/server/lastGrantID | No usable pairing yet |
| `discover` | exit0 after approximately3s; `candidates: []` | Does not distinguish listener disabled, interface/discovery/network issue or absent advertisement |
| `register --print` | exit0; JSON entry points to matching `tvtestrig-remote-mcp`, empty args | No agent configuration edited; output lacks the CLI's custom state directory |
| Standalone MCP `initialize` | exit0; protocol `2024-11-05`, server `tvtestrig-remote` version1 | Direct stdio probe, not a loaded Codex tool connection |
| Standalone MCP `tools/list` | 12 tool schemas returned | No tool calls or device effects |

Discovered tool names: `remote_pairing_status`, `remote_access_request`, `remote_access_status`, `remote_access_finish`, `remote_access_recover`, `remote_capture_still`, `remote_artifact_describe`, `remote_artifact_retrieve`, `remote_artifacts_resume`, `remote_review_record`, `remote_operation_query`, `remote_events`.

Access request schema requires `targetID`; optional `minutes`, `recipientID` and `waitSeconds`. No remote target-inventory tool is advertised. The required UUID is the **booted simulator on Sillycon**, not a historical/local Maximum-mini UUID. No unsupported command or physical fallback was attempted.

## Actionable feedback

1. **State propagation in registration:** `register --print` was invoked with explicit `--state-dir`, but prints only command/type/empty args. If consumed verbatim without an inherited environment override, MCP may use default storage and miss CLI pairing. Reproduce after pairing; request generated registration preserve `TVTESTRIG_REMOTE_STATE` (or equivalent supported argument). This is an observed omission and a predicted failure mode, not a reproduced lost-pairing incident.
2. **Endpoint discovery:** zero candidates. Operator/producer should supply the actual running listener's service name or host/port and chosen interface, with pairing window opened when both sides are ready. No diagnosis that the server is down or broken.
3. **Build binding:** confirm which source/build produced the observed executable and debug dylib before claiming an exact-candidate pass. Do not require a needless rebuild if the running artifacts are already the intended candidate.
4. **Target discovery:** current remote MCP schema has no inventory tool. Supply a fresh exact Sillycon booted tvOS Simulator UUID; do not infer target availability from stale coordination.
5. **Next collection capability:** current grant is still-only. Human-controlled TTR input/frame correlation is a separate requested design topic; capture transport acceptance must not be reported as action-sequence support.

## Resume conditions and proposed pass

Human question issued in this chat: enable Remote Clients on the intended LAN interface, open pairing, provide service/host-port and booted simulator UUID; confirm a15-minute still-capture transport test to this NUIAK project on Maximum-mini. This is a proposed bounded scope, **not an already granted server lease**.

Once endpoint and identity are established: use actual `pair`, compare both fingerprints with the human in TTR, record explicit confirmation; then configure matching MCP state and verify actual host connection. No fingerprint auto-acceptance.

Before capture, confirm exact target/duration/recipient/interface and runtime approval. Test request → readiness → still delivery → independent hash/decode/source checks → numbered review → finish. Keep each finish dimension separate. No fabricated labels, autonomous input, new training or physical Office pass. Pairing uses login-keychain identity and may require normal macOS consent; scoped permission must cover those effects and agent configuration before mutation.

No active subprocess remains after the probes. No lease/grant was acquired by this worker. Existing Office ownership remains unknown.

## Verification / completion boundary

Documentation-only changes use link/content/YAML checks; no Swift build/test is needed or claimed. CLI/MCP checks above exercised actual installed helpers. Pairing, live capture, artifact/schema mapping, import/crop QA, release and postflight are **not completed**. Missing endpoint/human target confirmation concretely blocks the remaining live work.

See [coordination record](coordination.md) for publication/readback and separate peer-acknowledgment status.
