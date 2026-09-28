# TTR external control — P0 formal request delivered

2026-09-27 · TTR-EXTERNAL-CONTROL-01 · current NUIAK Photos/coordination worker.
Documentation/coordination assignment complete for review; producer implementation
and end-to-end qualification remain unassigned/pending acknowledgment.

## Outcome and next owner

The maintainer confirms both Office Photos images are correct with different focus
states. Successful capture does not make the manual workflow usable. The
[formal request](../../../Research/Plans/TTRSupervisedExternalControl.md) documents
the observed connection, auth/pairing, prerequisite order, ownership, storage,
diagnostics, delivery/review and cleanup gaps, including agent-caused friction.
The observed38m42s includes human/agent delay, not backend execution latency.

**Next: TTR acknowledges request
`nuiak-20260927T182937Z-supervised-external-control`, names an owner, maps existing
MCP/lease/storage capabilities, and proposes the secure implementation scope,
estimate and actual two-host qualification plan.** Reuse existing MCP work.
No new Photos capture or repeat setup is requested. No producer edits, new service,
deployment, restart, device action, training or model evaluation occurred here.

| Outcome | Current result |
| --- | --- |
| Software | Request/documentation verified below. No new external-control implementation. Existing pilot adapter's96 Python/123 Swift test results are prior evidence, not tests rerun here. |
| Data | One human-confirmed candidate pair; zero consumer-admitted pairs. Original image bytes/hashes, bounds, duplicates and production-crop QA remain pending. Human diagnostics are not native labels or training admission. |
| Integration | Full request and owned status published/read back. Capture proof achieved; external-client workflow not qualified. Peer acknowledgment unobserved. |
| Model gate | Not assessed; no inference, training, export, promotion or threshold changes. |

## Acceptance evidence for this assignment

| Assigned deliverable | Evidence |
| --- | --- |
| Detailed issues from this connection/session | Canonical request chronology and findings table; request/observation identities preserved; uncertainty separated from demonstrated failures. |
| Formal approved-pairing / qualified-lease request | R1–R5 cover authenticated client pairing, human-scoped grant, readiness, immutable artifact delivery/review and owned cleanup. |
| Reduce infrastructure work without dropping consent | Happy-path acceptance: no terminal/log/path juggling; initial pairing plus scoped lease approval; retain human frame-ready and label-review steps. |
| Testable release criteria | Real two-host consumer test; proposed timing/intervention budgets; auth, contention, stale/wrong pixels, partial transfers, lost replies and lifecycle negative cases. Targets remain proposals, not measured achievements. |
| Prioritize and break dependency cycles | P0 in Tasks/current state; producer-managed selection before lease qualification; implementation does not wait for models/native Photos/VoiceOver/DS-G8/source review. |
| Status and delivery | Immutable full-message YAML and targeted PHOTOS-PILOT-01 update on verified share; readback/hash/parse checks below. |

## Publication receipt

- Expected endpoint independently verified from OS mount record:
  `smbfs`, `sillycon.local/SharedStatusFile`, `/Volumes/SharedStatusFile`.
  This does not verify server permission/encryption configuration.
- Mounted operating guides equal the repository copies; no guide change.
- Full immutable request destination:
  `/Volumes/SharedStatusFile/nuiak/requests/nuiak-20260927T182937Z-supervised-external-control.yaml`.
  **23,660 bytes**, SHA-256
  `1edbc34b2a8eb5bbe129aa18129ba65267fa40d3992667b99da107eb7ada94f0`.
- Local request mirror:
  `reports/coordination/nuiak/requests/nuiak-20260927T182937Z-supervised-external-control.yaml`.
  Exact byte equality passed; parsed message equals canonical request text.
- Status destination: `/Volumes/SharedStatusFile/nuiak/status.yaml`, only owned
  `packets.PHOTOS-PILOT-01` changed. Packet updated18:42:00Z, expires19:12:00Z;
  these are coordination times, not renewed device readiness/ownership.
- Readback completed by18:43:02Z. Shared status SHA-256:
  `adcdb5a08006bfc45fd270c1c24f1a34294f2b6bc8239f1d343a238cc17d53fa`.
  Local and shared owned packets equal. All other packet/top-level values preserved,
  including unknown fields and the different local-only APPEAR draft.
- Canonical unrelated-content SHA-256 before/after: shared
  `31929921617b0ff9dcaf012c4391eefabf248678d10d48ddad88cf7beb18c47d`;
  local `97ce4699b4a08ddbd1197a519dee4c4fb9e0bf6360661f43151f5c5d51a361e2`.
- Prior readiness request retained and marked closed/superseded by operator evidence;
  no invented peer acknowledgment. Peer status inspected at18:40:29Z was updated
 18:10:33Z and contains no acknowledgment of this new request. Readback is delivery,
  not peer acceptance. No monitoring or automatic retry is scheduled.

## Verification and residual boundaries

Bounded safe YAML parsing with duplicate-key rejection passed for request and both
status documents. Schema version1, exact request identity, canonical-message equality,
owned-packet equality and unrelated-content preservation passed. Local Markdown
links and whitespace checks are recorded in [coordination.md](coordination.md).
Swift build/test not rerun: this tranche changes documentation/metadata only.

The prior Office session and lease have no finalization/release receipt. Current
occupancy is unknown; this report does not release resources or authorize interruption.
The full10-pair Photos pilot and consumer intake remain incomplete. Human-reviewed
diagnostic collection does not wait for native telemetry; training still requires
eligible data/evaluation and separate approval. TTR acknowledgment is needed for
producer coordination, not a reason to block already assigned independent local work.

The worker/TTR guidance shaped the explicit authority boundary, owner-only cleanup,
source-identity checks and separate software/data/integration/model outcomes.
