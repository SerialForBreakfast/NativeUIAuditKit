# TTR-EXTERNAL-CONTROL-01 — Human-approved external control and capture

Revision 1 — 2026-09-27. Priority: **P0 / highest next TTR–NUIAK integration priority**,
explicitly requested by the maintainer after the Office Photos pilot.
Request ID: `nuiak-20260927T182937Z-supervised-external-control`.
Consumer owner: current NUIAK Photos/coordination worker. Proposed producer owner:
TTR maintainer/agent, assignment and implementation acknowledgment pending.

## Decision and authority

Replace the manual terminal-and-chat relay with a supported, authenticated external
client paired through a human approval in the running TTR app. The approval must
bind an exact target, capabilities, evidence destination/recipient and bounded
lease. The operator should drive Photos and review labels, not orchestrate TTR's
internal connection/session/storage state.

This assignment produces a formal request and status update, **not an implementation
or deployment of remote control**. No new listener, SSH bridge, tunnel, agent service,
installation, producer edit, permission change, restart, capture or model operation
is authorized by publishing it. TTR must propose its implementation/security scope
and obtain its own execution assignment. Existing Office work must not be interrupted.
A request/acknowledgment is neither a hardware reservation nor a lease.

## Outcome already achieved, and what remains

Two physical Office captures succeeded at18:21:09Z and18:24:42Z on September27.
Both responses identify the exact authorized target, generation1,1920x1080 up PNG,
current freshness and outputWritten=true. The maintainer subsequently confirmed
both captures are correct and show different focus states on Photos Welcome.
This is a successful supervised capture proof, and useful diagnostic evidence.

Neither image has yet been received/hash-verified in NUIAK. The confirmation does
not supply exact per-frame bounds, native focus telemetry, duplicate-pixel checking
or production-crop QA. Record **one human-confirmed candidate pair, zero
consumer-admitted pairs**. Do not mark the complete10-pair pilot, independent-source
qualification, training admission or a model gate complete.

## Evidence and elapsed workflow

Times below are producer terminal timestamps, not a measured service SLA.

| UTC | Observed event | Consequence |
| --- | --- | --- |
| 17:46:00–02 | Copied app-bundled helper runs help/status/device list on Sillycon; socket round-trip succeeds. Office listed but disconnected. | Local helper-to-app transport works. It does not connect this NUIAK chat remotely. |
| 17:55:24–26 | Separate capture/session/provider/audio checks; video provider idle/cold, permissions authorized, audio recording inactive. No active lease/session reported. | Operator manually relays several state fragments; GUI captures are not automatically enrolled. |
| 17:57:37 | Capture acquire returns deviceNotFound, retryable=false, for the previously listed Office ID. | No lease obtained. Agent stops; error does not identify the selection prerequisite. |
| 18:02:53–18:03:28 | Device list/get still resolve Office; doctor reports no_device_selected/control_disconnected. | Read-only source inspection needed to explain discovery versus selection. |
| 18:08:50 | Explicit device connect succeeds. | Selection/control prerequisite satisfied. No Apple TV re-pairing was needed. |
| 18:08:58 /18:09:06 | Pilot acquires video/control lease; repeated acquire returns the same lease/activity timestamp. | Correct ownership established, but repetition is not proof of renewal. |
| 18:13:02 | Exact Office selected/connected, epoch1; no sessionID, provider still idle. | Connected is not capturing. |
| 18:17:03 | Evidence session starts; expected Screenshots directory is absent. | Session metadata is not a live video stream. Storage path had to be resolved manually. |
| 18:21:09 | First still capture/export succeeds into existing app-owned Evidence storage. | 9,745ms whole command;136ms reported capture;104ms estimated frame age. |
| 18:24:42 | Second still succeeds with same target/generation/resolution. | 208ms whole command;127ms reported capture;112ms estimated frame age. |
| After second capture | Maintainer confirms correct images/different focus states and calls workflow unusable. | Reliability/usability of iteration is now the highest integration priority. |

From the first helper invocation to first successful export: **35m09s**; to second:
**38m42s**. These include agent analysis, documentation, copy/paste and operator
response time. They are **not TTR execution time or model inference latency**.
Two successful backend captures do not establish repeatability or a latency distribution.

Local evidence: reports/work/PHOTOS-PILOT-01/coordination.md and first/second-capture-response.json.
Those JSON files are transcribed from user-provided terminal results, not original
sender-file hash receipts. First request CAC8B187-CD19-4C57-AB6B-E86F9CF92D59;
second B78B2DAB-21F0-4AF7-8F19-9E60F38FA62F. Raw pixels are not in this request.

## Findings: observed failure versus inference

| Area | What happened | Attribution and requested correction |
| --- | --- | --- |
| Execution host / connection | Sillycon ran TTR; this chat had no usable approved remote TTR transport. SMB worked only as a metadata board. | Provide an approved external-client connection. Do not equate local IPC, MCP availability or an SMB mount with cross-host reachability. |
| App/helper identity | Operator copied a DerivedData helper path; installed help was pasted manually. Exact app/helper binary identity was not pinned. | Return matched app/helper/runtime/protocol identity and negotiated capabilities in one handshake. No path archaeology. |
| Authentication and pairing | Local helper/app IPC worked. Device inventory said pairing unknown; explicit control connection later succeeded without a new pairing procedure. | No demonstrated bad credentials or Apple TV pairing failure. Distinguish client-to-TTR trust pairing, Apple TV control authentication, lease consent and Photos labels. |
| Target selection / lease | Agent incorrectly required capture lease before control connection. Inspected coordinator requires selectedDevice equality; connect(to:) establishes selection. | Agent sequencing error plus weak prerequisite diagnostics. Expose the ordered workflow and targetNotSelected/next step, rather than misleading rediscovery advice. |
| Split ownership | Command-control and capture-resource leases, evidence sessions and streams are distinct. Status lacked a simple human-approved overall grant; GUI capture occupancy is separately incomplete. | One human-facing workflow must coordinate these mechanisms and report actual owner/target/expiry without treating silence as availability. |
| Session / video / red border | Control connected and evidence session started while provider was idle; user saw no red border. | Display control, evidence session, live video, recording and delivery separately. A border is not a readiness contract. |
| Storage / export | Agent assumed Screenshots existed; it did not. Existing app-owned Evidence storage worked. Output JSON did not name/hash the saved PNG. | App allocates safe destinations, checks its own writer permissions and returns immutable artifact descriptors. No manual container paths/mkdir/re-signing. |
| Diagnostics | Every helper launch emitted diagnostic_file_sink_failed/persistenceFailed code24, yet IPC and both exports succeeded. | Classify logging degradation separately; investigate persistence without making it a capture/auth failure or prescribing restart. |
| Human relay | Repeated command batches, full debug log pastes, manual paths and repeated status documentation delayed the actual task. | Agent also contributed excessive round trips. Batch passive checks, use compact authoritative receipts, publish only actionable transitions. |
| Review / labels | Correct focused/unfocused images confirmed by the maintainer; image bytes/bounds/crops still not admitted locally. | Pair review is a separate evidence step. Never infer labels from a capture filename, requested direction or model prediction. |
| Completion | Owned lease and evidence session were established; no teardown receipt has been observed. | Completion must finalize evidence and return separate resource-release and health outcomes. No claim of current availability from old receipts. |

The inspected local TTR source HEAD was46dce7b3a79e4f17af49bc0324d4aeba3cc0958d;
source-to-Sillycon-binary match was not verified. The later successful connect→acquire
sequence supports the prerequisite diagnosis. Do not call it a broken lease implementation.

TTR peer status updated18:10:33Z reports MCP-COMPAT-01 and a live local Claude Code
listing of94 tools, plus some environment-limited test failures. Reuse and assess
that interface; this is **not** a request to reinvent MCP or a claim that TTR has
no automation support. Local MCP qualification does not prove a cross-host consumer
path, its authorization model or end-to-end Photos evidence delivery.

## Required workflow

Conceptual states, not currently implemented command names:

Unpaired → pairing requested → human approval in TTR → scoped client paired →
human-approved target lease → setup/qualification → ready → capture/review →
finalize evidence → release owned resources → complete.

Denied/expired/revoked/contended/uncertain states must be explicit. Pairing alone
does not grant a perpetual device lease; a lease alone does not prove working pixels.
All transitions must identify the failing stage and next safe actor/action.

### R1 — Pair the external client through TTR

- Give the external consumer a supported entrypoint/discovery/bootstrap flow with
  advertised protocol version and exact host/app identity. Prefer existing CLI/MCP
  integration where applicable; document the additional cross-host transport.
- Human on TTR sees the verified requester identity, consumer host, requested target,
  capabilities, duration and evidence destination before approving or denying.
  Display names supplied by a client are not authenticated identities.
- Use short-lived, single-use pairing initiation protected against interception,
  replay and brute-force attempts. Authenticate and encrypt cross-host traffic with
  a reviewed standard protocol; no custom cryptographic scheme, plaintext LAN token,
  public unauthenticated endpoint or credentials in chat/SMB/logs/URLs.
- Securely retain revocable trust if explicitly chosen. A returning trusted client
  avoids repeated path/token copying but must obtain the required current grant.
  Show paired clients, scope and revoke/disconnect controls in TTR.
- TTR design must specify binding/listener exposure, credential storage/rotation,
  trust-change behavior, audit redaction and version compatibility. Deployment
  approval remains separate; no new service is implied by this document.

### R2 — Human-validated and runtime-qualified lease

- Bind approval to client identity, exact physical target, allowed resources/actions,
  output/recipient scope, start/expiry, idle policy, request identity and current
  connection generation. Return a lease/session reference usable by that client,
  not a bearer secret published to the share.
- Default Photos grant: status, explicitly initiated still capture, session/evidence
  management and bounded delivery/review. Human retains remote navigation.
  Remote button/text/app control, audio recording, model inference, settings/account
  mutation and other targets remain disallowed unless separately and visibly approved.
  Required control-connection setup is not authorization to send navigation.
- TTR coordinates selection→control connection→resource ownership→session→storage
  qualification internally. Do not make the external client guess prerequisite order.
  A grant is accepted before setup; ready is asserted only after applicable checks.
  Any qualification image needs explicit image-capture consent and stays accounted for.
- Admit or reject cross-host/GUI contention without stealing. Report unregistered
  capture limitations honestly; do not treat absent records as exclusive use.
- Renewal may proceed within an explicitly approved ceiling without repeated prompts.
  Longer duration, expanded scope, target/identity/generation changes and trust loss
  require revalidation and, where scope changes, fresh human approval. No indefinite
  keepalive. Expiry/revocation promptly blocks new operations and reconciles in-flight
  work without replay; cleanup affects only owned resources.
- Distinguish human-consent proof from runtime qualification and genuine native labels.

### R3 — One readiness response; operation-safe recovery

A single versioned readiness response should include authenticated client/build/
protocol identity, exact control target and observed image-source mapping, control
authentication, lease holder/scopes/expiry, session ID, provider/frame freshness,
storage writer result, audio-recording and inference states, limitations and
typed blocker/next action. Unknown must remain unknown.

Use operation/request IDs and queryable completion, bounded event delivery and
deduplication. A lost reply must permit reconciliation without a second capture,
button press or overwrite. Reconnect of the client transport must not silently
reconnect hardware, change target or replay mutations. Reuse warm state only after
fresh target/epoch/ownership validation. Keep raw technical evidence available
on demand, with compact normal responses and separate degraded-log notices.

### R4 — Capture, export and review as one reliable transaction

- One request for a settled still creates immutable pixels plus observation/session/
  lease/target/source/generation/timestamp context and SHA-256/size/dimensions.
  The producer allocates app-writable paths; the external client uses artifact IDs.
- Do not falsely claim atomic native-focus/frame correlation. Record actual
  correlation guarantees, uncertainty, human declarations and any genuine native
  observations separately. Unknown/mismatched source fails qualification.
- Deliver a thumbnail/review reference and supported original-byte retrieval to the
  authorized recipient. Retrieval is bounded, integrity-checked and resumable;
  partial transfers are not complete receipts. Retain originals after export failure.
- Current SMB fallback continues the existing named-file size/hash receipt protocol:
  files over10,000,000bytes need explicit per-file approval; sender owns cleanup.
  This request changes neither those limits nor private-data restrictions.
  A future direct API must define and receive approval for its data-egress policy.
- A small paired-capture interaction records two explicit operator-ready states,
  stable control identity and per-frame bounds, preserves visible competitors,
  shows both frames for human confirmation, and accounts for duplicate/missing/
  corrupt/ambiguous examples. Human labels stay human-reviewed diagnostics.
- Integrate with NUIAK's existing diagnostic importer/cropper; negotiate any new
  envelope through a separately reviewed adapter version. No training/eval admission,
  native-journey schema, public Swift API or taxonomy change in this request.
- Reject private/wrong-target/black/stale or unsettled frames appropriately; do not
  silently substitute a cached frame or infer unfocused state from the requested action.

### R5 — TTR owns lifecycle visibility and bounded completion

Show the approved client/target, remaining lease, session, live preview versus
recording state, approved actions, saved/delivered count and stop/revoke control.
Never force a user to use the TV's red border as the only indicator.

Finish must report session-finalized, artifacts-retained/delivered, capture-released,
control connection disposition and postflight health independently. Ownership
enforcement prevents cleanup of another client's resources. On client disconnect,
expiry or crash, bounded cleanup and recoverable partial evidence are required;
unknown cleanup blocks target reuse. Release is not deletion of evidence.

## Acceptance criteria — proposed release gates, not measured achievements

TTR should accept or explicitly counter-propose these gates before implementation;
do not silently replace them with a help/list-tools demonstration.

1. **End-to-end real consumer:** on the approved two-host topology, the actual external
   consumer pairs through TTR, receives a scoped human-approved grant, captures two
   stills and obtains byte-verified originals/metadata, reviews the pair, then
   finalizes/releases. Show real client/app/build identities and receipts. A same-host
   CLI demo or94-tool listing alone does not pass this gate.
2. **Interaction budget:** zero terminal commands, debug-log pastes, helper-path copying,
   manual container paths or SMB-file juggling in the supported happy path. At most
   one initial pairing approval and one lease approval (may be combined with both
   meanings visible). Per-frame readiness/label review are legitimate human work,
   not infrastructure prompts. No repeated approval within unchanged granted scope.
3. **Proposed timing targets:** on a preconfigured available target, first readable
   capture delivered within60s of approval; a renewed/returning approved session
   ready within15s; warm captures delivered within2s p95. Report setup, capture,
   encode/export and transport timings separately, across at least3 cold starts,
   5 returning sessions and20 warm captures in separately approved qualification.
   Publish failures and percentiles; one208ms CLI result does not establish this SLA.
4. **Security/ownership negative cases:** deny/unpaired client, expired/replayed pairing,
   wrong requester/target/scope, revoked/expired lease, concurrent client/GUI capture,
   scope escalation, generation change and credential rotation. No image or remote
   action before required approval; no token leakage or lease stealing.
5. **Reliability negative cases:** absent target/selection, lost response after commit,
   cold-provider timeout, no frame/black/stale/wrong-source image, unwritable storage,
   interrupted transfer/hash mismatch, consumer disconnect, app restart and cleanup
   failure. No blind replay, overwrites, silent partial success or orphaned ownership.
6. **Scope checks:** the Photos capture-only grant cannot navigate, activate controls,
   record audio or run inference. Explicitly broader future grants are tested
   separately. Human-reviewed data is rejected by training/eval admission by default.
7. **Evidence completeness:** all attempted frames accounted for; exact delivered bytes,
   immutable manifest, actual source provenance, human reviews and cleanup results
   are consumable by NUIAK. Missing native telemetry remains unavailable, not blocking
   this diagnostic mode or being substituted by observe focus.
8. **Honest reporting:** software/security, data eligibility, integration qualification
   and model gates are reported separately. Integration is not qualified until actual
   consumer delivery and cleanup pass. No model gate is exercised here.

## Prioritized producer assignment and dependencies

**First / P0:** acknowledge this exact request, name an owner and provide a capability
gap map against existing MCP/IPC/lease/storage work. Propose the minimal secure
human-pairing/grant contract, transport exposure and end-to-end vertical slice,
with estimate, acceptance targets and exact extra approvals needed. Do not request
new Photos recordings just to prove the need; retain the successful pair.

**Next, after separately assigned implementation:** deliver the integrated client
pairing, grant/readiness, single-still capture/delivery and finish path with
positive/adversarial tests. Add paired review through existing components rather
than building a broad annotation platform. Offline fixtures can qualify software;
a separately approved physical Office run qualifies real integration.

**Then:** use the improved path to complete the bounded Photos pilot and plan broader
coverage. Do not launch training, change model thresholds or promote anything.

There is no need to wait for new FocusRing weights, native Photos telemetry, VoiceOver
alignment, iOS DS-G8, independent-source review or a new dataset to implement this
transport/ownership slice. Evaluate the workflow with retained or synthetic data
offline; validate capture with separately authorized images. Training still waits
for eligible data/evaluation and separate approval. This breaks the circular demand
for better models to collect the data needed for better models.

The earlier artificial cycle “need lease before connect / need selected target
before lease” is resolved by producer-managed setup under the human grant; it is not
a reason to remove exclusivity or authorization gates. Do not wait for shared-status
acknowledgment to do already assigned local work, and do not mistake an acknowledgment
for permission to deploy or operate a device.

## Immediate handoff and cleanup caveat

Current request is documentation/coordination only. Preserve both saved Office PNGs,
their original session and metadata. Session65AF215E-05C6-48F1-AB28-5217C4DE047D and
lease544C001D-0312-4C37-9A54-5A5D953DAE7B were last observed owned by
nuiak-photos-pilot-20260927-01; **no finalization/release receipt has been supplied**.
Their present live status is unknown, not perpetually held or free. Do not interrupt
TTR or assume cleanup from elapsed time. The operator should finish only this owned
session through supported cleanup; no cleanup was remotely performed by NUIAK.

This consumer asks for acknowledgment of the formal request, not a restart or
capture job. The older read-only readiness request is superseded for next-action
purposes by the maintainer-supplied receipts, with no fabricated peer acknowledgment.

