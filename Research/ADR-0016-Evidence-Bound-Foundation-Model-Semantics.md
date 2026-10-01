# ADR-0016: Evidence-Bound Foundation-Model Semantics for UI Audit Reports

- Date: 2026-10-01
- Status: Proposed architecture direction; no Foundation Models runtime, TTR change,
  model training, export, navigation, or cloud use is authorized.
- Related: [ADR-0013](ADR-0013-NativeUI-CLI-and-MCP-Server.md),
  [ADR-0014](ADR-0014-Hierarchical-Detection-and-OCR-Fusion.md),
  [ADR-0015](ADR-0015-Context-Aware-Focus-Detection.md),
  [TTR perception](Plans/TTRPerception.md), and
  [screen/row identity](Plans/TTRPerception.md#per-06--screen-and-row-identity-under-change).

## Context

NativeUIAuditKit already produces bounded evidence: detector observations, OCR tied
to observations where supported, focus receipts, audit warnings, image identity and
timing. TVTestRig separately owns capture, native accessibility observations,
settlement/action policy and any remote-control input. Raw screenshot inspection by
an agent is costly and does not make an inferred description authoritative.

Apple's Foundation Models framework can generate text, constrained Swift data
structures and tool calls. Current capability discovery also lists vision as a beta
capability. Capability and availability must be checked at runtime; neither can be
assumed from the OS version or this ADR. See Apple's
[framework overview](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models),
[guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation),
and [capabilities](https://developer.apple.com/documentation/foundationmodels/languagemodelcapabilities/capability/vision).

The useful role is semantic interpretation of verified, structured evidence: an
explanation of what is visible, likely screen role, candidate screen identity and
why a proposed action should stop. It is not pixel measurement, native-state
recovery, ground-truth labeling or autonomous control.

## Decision

When separately implemented and available, use a Foundation Model as an **optional,
evidence-bound semantic reporter**. It receives a versioned, size-bounded UI evidence
envelope, not unbounded project files or a default screenshot stream. It returns a
guided typed report whose every conclusion is marked as one of:

- `verified` — established by deterministic/native evidence supplied in the envelope;
- `candidate` — selected from a supplied screen catalog with stated matching evidence;
- `inference` — a model interpretation that requires no action and may be wrong;
- `unknown` or `ambiguous` — insufficient or conflicting evidence.

The report is advisory. A model cannot promote an `inference` into `verified`, fill a
missing native focus identifier, invent a bounding box, alter annotations, create
training labels, or authorize a TTR input. Missing, stale, contradictory or
unsupported evidence returns `unknown`/`ambiguous` and preserves the existing
fail-closed behavior.

## Input and output boundary

The input envelope must bind one observation by source ID, byte hash, dimensions,
capture time, producer/model versions and freshness state. Its optional fields are:

- NUIAK element class, pixel bounds, confidence and geometry provenance;
- OCR text, OCR bounds/confidence and the association to an element or `unassociated`;
- TTR native focus/state, expected transition and settlement information, when
  actually present;
- deterministic screen/row-matcher candidates and their evidence; and
- explicit unavailable, corrupt, stale and uncertainty fields.

The output is a guided typed structure, not free-form control text. It may contain a
screen role (`settings_list`, `dialog`, `media_grid`, `search`, `unknown`), an
evidence-cited summary, catalog candidates, visible actions as descriptions,
contradictions and recommended **non-mutating** disposition (`continue_observation`,
`ask_user`, `stop_and_report`, or `unknown`). It must include evidence IDs and an
uncertainty reason for every screen identity claim.

An exact name such as `App > Settings > Playback` is permitted only when a supplied,
versioned screen catalog and deterministic matcher establish a candidate according to
their frozen policy. The model may explain or rank those candidates; it cannot
recognize an arbitrary app screen from general knowledge and call it verified.

Vision-capable prompts, if available and separately authorized, are supplementary
context only. Vision output cannot override the evidence envelope's image identity,
detector geometry, OCR, native focus or deterministic candidate result. No raw image,
personal text, account state, credentials or dataset content goes to an external
provider by default.

## Responsibility split with TVTestRig

| Concern | Owner / authority |
|---|---|
| Capture, image identity, native accessibility state, settle/timeout policy, remote input | TVTestRig |
| Detector boxes, OCR association, focus receipt, deterministic identity matching, audit evidence | NativeUIAuditKit |
| Plain-language explanation, bounded semantic role/candidate interpretation, uncertainty narration | Optional Foundation Model |
| Whether an input is safe and permitted | TTR's existing deterministic policy and user authority |

TTR may consume an NUIAK semantic report as an additional read-only observer signal.
It must retain native state as action authority and stop/report on disagreement or
uncertainty. Agreement from a Foundation Model never bypasses a TTR policy gate.
NUIAK's existing CLI/MCP output remains useful without Foundation Models; this ADR
does not require a new MCP server, an agent registration, or a TTR adoption.

## Delivery and evaluation sequence

1. Define the versioned evidence and guided-report schemas with explicit limits,
   source fields and `unknown` states. Use deterministic local fixtures only.
2. Implement an offline reporter behind capability discovery. Test valid summaries,
   missing/stale observations, unknown catalog entries, conflicting native/visual
   evidence, prompt-size limits and typed-output rejection. No navigation or capture.
3. Evaluate semantic usefulness on held-out, reviewed evidence. Measure unsupported
   claims, false catalog matches, correct abstentions, latency and disclosure of
   evidence. Do not score model prose as detector/focus accuracy or training quality.
4. Only after the offline contract passes, propose a TTR-owned observer integration
   using the same canonical capture receipt. It returns compact structured findings,
   not image bytes or an instruction to press a button.

Any action-linked use requires a separate TTR decision and live-safety assignment.
The temporal, chevron/dialog, focus and screen-identity contracts retain their own
evidence gates; this ADR does not merge or weaken them.

## Consequences and non-goals

- This can make verified scan receipts understandable and searchable without sending
  an agent raw screenshots or asking it to reconstruct UI semantics from prose.
- It can explain why a screen is unknown, why a catalog candidate is ambiguous, or why
  an expected dialog/control does not appear to match the observed evidence.
- It does not improve YOLO localization, OCR accuracy, focus classification or native
  accessibility telemetry. Those remain separately measured components.
- It does not establish a model's general knowledge of a consuming app, calibrated
  confidence, deterministic output, privacy consent, offline availability or a
  screenshot-vision capability on every supported device.
- It does not create a semantic UI taxonomy, alter stable `NativeUIElementType` raw
  values, add a training corpus, or permit automatic app navigation.

Revisit this decision after a separately assigned offline evidence/report evaluation
or if Foundation Models capability, privacy or availability constraints materially
change. Until then, structured NUIAK/TTR receipts and deterministic matching remain
the complete supported path.
