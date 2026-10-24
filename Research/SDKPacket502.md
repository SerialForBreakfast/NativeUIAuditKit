# Portable SDK packet intake

Owner: Maximum-mini-NUIAK. Date: October 24, 2026.

## Source findings

Local TTR revision `cf17ed0ed52663994b7019a96d03ead9a4c80abf` contains an SDK packet interface.
The reviewed source files have no local modifications. Their hashes are recorded in the source receipt below.
`SDKInquiryCommands` supports `sdk packet` with endpoint, enrollment, Simulator identity, and a new output directory.
This operation captures an image. Do not invoke it as a read-only query.
`SDKPacketDirectory` exports `frame.png` and `evidence.json`.

`SDKCaptureEvidence` records screenshot hash, dimensions, capture timing, producer identity, registered elements, and observations before and after capture.
It also records explicit issues, `focusKnown`, and optional `focusID`.
Known focus with no ID means observed no focus. Unknown focus remains unavailable.
The packet always declares `review_only`. It does not grant training admission.

This corrects the earlier assumption that explicit no-focus semantics were wholly missing.
They exist in this source. Retained native qualification of NUIAK's consumer remains pending.

## Implemented consumer

### Updated Developer source and request interface

The isolated `Developer/TVTestRig/.local-work/nuiak-sdk-ae310e08` checkout contains revision `ae310e085783717721c9039ccfd4c52d819bf23f`.
The existing `ui-refactor` checkout and its local edits remain unchanged.
`CaptureEvidence.swift` is byte-identical to the reviewed contract. Recorder and inquiry implementations contain additional capabilities.
The update adds focus-decision records, SDK planning, and setup interfaces. These do not change observed focus into preferred focus.
Source compatibility does not establish runtime qualification. No new TTR build or app replacement occurs.

SDK503 adds a small request format to the existing consumer.
Each request specifies pinned packet files, expected app, expected Simulator source, original group, and review or calibration role.
Training roles are rejected. App or source mismatches fail before evidence interpretation.

Compile a saved request with the existing interpreter:

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/sdk_packet502.py \
  --request reports/work/CAMPAIGN/request.json \
  --spec reports/work/CAMPAIGN/spec.json
```

Use actual project-relative paths. Compilation creates an immutable specification; it does not register, approve, or execute it.
The existing queue handles registration, approval, and execution after input qualification.

Example request shape:

```json
{
  "version": "sdk-packet-request-v1",
  "id": "sdk-review-example",
  "evidence": {"path": "reports/work/CAMPAIGN/evidence.json", "sha256": "ACTUAL_SHA256"},
  "image": {"path": "reports/work/CAMPAIGN/frame.png", "sha256": "ACTUAL_SHA256"},
  "expectedAppID": "VERIFIED_APP_ID",
  "expectedSourceID": "VERIFIED_SIMULATOR_ID",
  "group": "ORIGINAL_GROUP",
  "role": "review_only"
}
```

The example contains placeholders and is not executable evidence.

`scripts/sdk_packet502.py` uses the existing queue callable interface.
Inputs are pinned `evidence.json` and `frame.png` files.
Output is `benchmark_summary.json` with an artifact receipt.

The consumer:

1. Checks the packet version, role, image hash, image size, dimensions, and timestamp order.
2. Checks producer identity and source declarations across the capture bracket.
3. Distinguishes focused, observed no-focus, and unavailable observations.
4. Flags changes anywhere in the registered inventory, including nonfocused controls.
5. Keeps pixel geometry separate from window-point geometry.
6. Preserves registered selection as registration evidence, not verified native selection.
7. Leaves detector taxonomy and annotation completeness unknown.
8. Keeps all output in review-only status without training or model admission.

A source declaration is not independent authentication. Exact producer provenance remains required for native qualification.
Navigation `coverageComplete` does not establish complete detector annotations.
The packet schema does not carry per-class coverage or dataset ancestry. Those remain external admission requirements.

## Verification

Eight focused unit tests pass, including the prior retained Fixture adapter tests.
The isolated queue produces these software-only results:

| Case | Queue outcome | Consumer outcome |
|---|---|---|
| Known focused control | Complete | `focused` |
| Known focus with absent ID | Complete | `no_focus` |
| Unavailable focus observation | Complete | `unknown`; no label admission |
| Incorrect image hash | Failed | `sdk_packet_pixels` |

These fixtures test software behavior. They are not native captures or model accuracy evidence.
No software fixture enters the experiment backlog as training data.

SDK503 increases the focused suite to 10 passing tests.
The actual CLI compiles 2 configuration-only requests, and both pass through the isolated queue.
Their outputs preserve `focused` and `no_focus`. A third request fails with `sdk_request_app_mismatch` as expected.
No retained SDK `evidence.json` appears in the checked local SDK repair directory.
The peer packet request remains pending. Do not replace missing native evidence with these software fixtures.

## Exact remaining dependency

### SDK504 native delivery — October 24, 2026

Sillycon-TTR delivers 2 retained native Fixture cases through coordinator reply 1337.
Maximum-mini-NUIAK verifies the 2,663,115-byte archive and its published SHA-256.
The original manifest hash and all 4 data-file hashes match. Six archive members expand to 2,939,615 bytes.
The recording-specific extractor rejects the multiple archive roots before extraction.
The existing archive-member validator then checks every member before exclusive extraction into a new owned directory.
No capture repeats. Original bytes remain preserved.

Both packets pass initial native consumer review with known focused controls, no reported issues, and 4 registered elements each.
Jobs `sdk504-grid-origin` and `sdk504-grid-opposite` complete through the detached runner. Their output hashes verify.
The original group is `fixture-grid-713`; the content group is `synthetic-713`.
The producer requests split `test`, with role `single` and review-only admission. These designations remain unchanged.
The producer declares source and SDK revision `8e4afe5d0127835882d6eb9e9fce1c8469ea4b7e` plus an instrumentation digest.
NUIAK has not independently reconstructed that producer build.

No observed-no-focus packet exists in this delivery. The before/after observations bracket each screenshot; they are not navigation transitions.
Per-class annotation completeness and image-aligned hierarchy export remain unverified.
These packets do not establish cross-app accuracy, training eligibility, or independent evaluation membership.

Exact transfer receipt `nuiak-sdk504-receipt-20261024-v1` is stored at coordinator cursor 1340.
TTR owns deletion of the exact shared copy after receipt verification. Cleanup acknowledgment remains pending.
See [transfer receipt](../reports/work/SDK504/receipt.json) and [native job admission](../reports/work/SDK504/admission.json).
The [completed queue results](../reports/work/SDK504/handoff.json) qualify consumer intake for these 2 focused packets only.

The earlier packet request below is now satisfied for focused examples only.

Sillycon-TTR must identify an existing native SDK packet and its source, runtime, group, and role evidence.
Maximum-mini-NUIAK will verify transfer hashes and run the consumer through the background queue.
Prefer retained focused and no-focus examples. Missing examples remain missing; this request authorizes no new capture.
Request `nuiak-sdk502-retained-packet-20261024-v1` is stored at coordinator cursor 1334.
Forwarding and peer acceptance remain unconfirmed.

Native acceptance requires matching screenshot and Simulator identity, producer revision, clean observation bracket, and unchanged data roles.
Complete detector training additionally requires reviewed taxonomy, coverage exclusions, and training-only ancestry.
Do not infer these requirements from successful software tests or a clean packet.

## Evidence

- [Source hashes](../reports/work/SDK502/source-contract.json)
- [Software queue outcomes](../reports/work/SDK502/qualification.json)
- [Prior retained Fixture audits](SDKEvidence501.md)
- [Producer requirements](TTRSDKTrainingRequirements.md)
- [Updated source hashes](../reports/work/SDK503/source-contract.json)
- [Request compiler qualification](../reports/work/SDK503/qualification.json)
