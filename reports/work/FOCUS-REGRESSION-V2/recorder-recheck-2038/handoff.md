# Recorder repair present; live qualification pending

Observed 2026-09-28T20:38–20:41Z, Max-local TTR. Read-only status assignment;
no connection, capture, navigation, audio recording, restart or producer edits.

## Exact running build

Process97201 started20:37:24Z from the previously matched DerivedData Debug app.
Its debug dylib was modified20:37:23Z. SHA-256:
`2034f92e3095af3fd70b0c4290c3f4a890fade7c37e83805e0bcf0e0147053b9`.
Matching bundled MCP helper SHA-256:
`a522c794f08940fcdfd25b075538bc3008089ecff3fe47ac38247547b9710505`.
`recording-symbols.txt` confirms both coordinator start methods exist, including
`startActionRecording(destination:title:)`, the repair reported by the producer.
This proves the symbol is in the on-disk running-build artifact, not successful
live dispatch or complete capture/export behavior.

Producer shared status observed at19:56:26Z reports the previous failure was a
protocol signature mismatch: IPC called destination/title while the coordinator
implemented sessionName/bundleDirectory, selecting an unsupported default. It reports
an added forwarding overload and a passing offline dispatch test. This explains
the retained failure; producer tests were not independently rerun here. The nearby
TVTestRig checkout differs from this runtime; its old HEAD is not runtime provenance.

## Fresh readiness

- Matching helper help succeeds; MCP initialize/tools/list/status succeed.
- MCP advertises record.start/status/stop; CLI help still omits recorder commands.
- Office discovered with the expected stable ID, but connectionStatus=disconnected.
  PairingStatus=unknown is not proof that re-pairing is needed.
- Recorder target=Office, isRecording=false, actions=0, frames=0, gaps=0.
- No active evidence session or command-controller lease.
- Capture-resource state=available; this is not a human reservation.
- AVFoundation provider idle/not warm; video/audio permission authorized.
- Audio recording inactive, busy=false. No audio was started.

Evidence: `mcp-readiness.jsonl`, `target-status.jsonl` and matching stderr. The first
audio.status probe omitted its required device_id and returned missingField with
no mutation; the schema-correct read-only probe then succeeded. Historical capture
lease events remain in the response and are not current occupied leases.

## Requirements and outcomes

Software: repair present in binary; current read-only interface verified. Data:
no new bundle. Integration: end-to-end unqualified. Model gate: not assessed.
No claim of synchronized pre/after frames, event ordering, settling/gap accounting,
advisory OCR, successful stop/export, hashes or review import until a real bundle
is delivered and inspected. Existing review-preparation tooling is complete.

Next: operator confirms Office is available with non-sensitive content and connects
it through TTR. Then authorize one short human-operated start → several safe TTR
inputs → stop trial. Agent sends no navigation; verify the resulting bundle before
a larger walkthrough. No chat-per-press fallback or new model prerequisite.
Latest request was status checking, so no hardware session was started implicitly.

Shared-status consequence: acknowledge producer diagnosis and update the same
action-linked-recorder request, not another request for the already supplied fix.
Publication/readback recorded separately in coordination.md.
