# SHADOW121 and WORKFLOW122 — receipt, regression signals and process alignment

DTM030v1 receipt matches exact request,207304bytes and SHA256
977c938617007eec8f6caf5c2d122241a5717c13e6d3bfc0d0dfdf2dae7f8d65.
Reverified shared bytes and local original; removed only shared v1 duplicate under
receipt protocol. Local original remains recoverable; consumer-v2 untouched.
Receiver reports18manifest members verified (19archive entries includes manifest
itself), portable build and synthetic parity; no live subscription claim.

## Evidence and software

Preserved two original producer YAML reports with hashes in derived
survey24-inspection.json and survey26-inspection.json. Existing feedback CLI now
supports `--peer-report`, bounded1MiB/20000events/32levels, rejecting aliases,
duplicate keys, malformed YAML, unsupported versions, unknown or mixed model/tree/
contract/manifest identities, source mismatch, count/availability mismatch and
invalid/duplicate case hashes/IDs/decisions. It never turns summaries into accuracy,
training admission or execution attestation. Original normalized feedback mode
unchanged; producer owns original wire schema.

Actual two CLI invocations and16Python tests pass; offline build and139Swift tests
pass using approved Apple cache access. Logs .build/shadow121-{tests-final,build,
swift-tests}.log. Focused tests cover both actual reports and invalid variants.
No device operation, model inference/training/export/promotion or Git writes.

Survey24 reports4/8DTM025vs5/8DTM030native agreements. Survey26 reports6/6vs3/6,
plus2unavailable hints. Eight case rows identify7unique image hashes and three
changed→unchanged differences:5:6,7:8,8:9 in operation
21BC8868-A77A-47B1-929A-E55F4A0B3EB0. These are regression signals, not reviewed
false negatives. Original pixels, probabilities, case-level hint availability and
reviewed identity are missing. No broad replacement or further fitting justified yet.

Requested retained8intervals/7original images, exact two-model inputs/replies,
observation/action/hint/review/ancestry bindings and explanation of8sampled versus
9survey intervals. Reuse source, no recapture. Preserve both models and current roles.

## Process improvements

Maintainer's process proposal adopted as scoped contracts in
Research/Plans/ProducerConsumerWorkflow.md and Tasks.md. Four workstreams include
shared validators, existing resumable generation, exact-receipt reconciliation,
compact owned status/read-only source handoff. Source-backed capability inventory
comes before duplicate implementation. Global ancestry needs NUIAK registry;
FocusRing and transition preprocessing differ; headless cannot bypass coordinator;
receipts, not expiry, govern cleanup. No estimated throughput/token savings accepted.
Qualification requires invalid corpus, genuine authorized generation, interrupted
resume, receipt mismatch, concurrency preservation and measured accepted throughput.
Planning/alignment is complete; these workflow implementations are not claimed done.

Published/read back on verified SMB:
- nuiak/responses/nuiak-20261004-survey26-review-request.yaml
- nuiak/requests/nuiak-20261004-workflow-alignment.yaml
- own SHADOW-FEEDBACK-121 and WORKFLOW-ALIGN-122status entries; duplicate-key parsing
  and unrelated semantic-content hash preservation pass.
New requests await peer acknowledgment; v1copy receipt is separately reconciled.

Outcomes: feedback software verified; data/truth not admitted; producer retained
execution reported but not locally replayed; no independent/model qualification.
Next substantial tranche: receive/replay/review the exact retained cases and define
one justified comparison if warranted, alongside source-pinned shared validation
vectors and deterministic receipt tooling. No unchanged training reruns or capture
while retained bytes can answer the current question.
