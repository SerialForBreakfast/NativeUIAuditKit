# TVTestRig layout-v1 reconciliation handoff

**State:** Review-ready (2026-09-19)  
**Parent:** TASK-INTEGRATION-01  
**Scope:** NUA consumer compatibility; no producer, device, dataset, or Git write.

## Outcome

Current TVTestRig source at `3fda3eab1aa7fc944914d0f29cab09a9705655d2`
keeps the existing layout-v1 bundle identifiers and validation boundaries. It
adds optional `dataset-index.json.sourceDescription` for descriptive collection
context. Production/NUIAK `fixture batch` uses the literal assurance
`reported-source; not-attested`; its internal identity challenge is not a
production consumer prerequisite.

NUA now validates the source-description shape when present, preserves it in
the normalized/result records, and keeps `identityEvidence: null`,
`provenance: unverified-pixel-telemetry-binding`, and
`eligibleForTraining: false`. No metadata is fabricated and no integrity pass
is converted into a corpus or model gate.

## Evidence-backed compatibility matrix

| Producer source | Required layout | Additive source context | NUA outcome |
| --- | --- | --- | --- |
| `586050e043bddd742c701963650e2fc5815afe36` | layout-v1 identifiers, receipt v1, flat hash index, canonical coordinates/splits | absent or ignored by historical case | Existing H1 compatibility case remains supported. |
| `3fda3eab1aa7fc944914d0f29cab09a9705655d2` | Same layout-v1 identifiers and integrity/focus limits | optional `sourceDescription`; if present it requires nonempty method/time and `reported-source; not-attested` | Supported; preserved but not trusted. |
| Changed required identifier, coordinate/split vocabulary, or source assurance | Outside this contract | N/A | Reject as `unsupported_version` or `invalid_metadata`, retain a small reproducer, and add a reviewed compatibility case. |

## Changed NUA paths

- `Research/NativeUIElementDetection.md` §6 records the additive metadata and
  separates integrity, source context, eligibility, and model outcomes.
- `Research/TVTestRigIntegrationContract.md` revision 5 replaces the stale
  mandatory-attestation assumption with the inspected producer policy.
- `Research/schemas/harvest-compatibility-v1.md` records both observed source
  revisions and the positive/negative source-description cases.
- `Research/FixtureBatchIngest.md` and `Tasks.md` remove the stale identity
  capture prerequisite without loosening integrity or training rules.
- `scripts/harvest_bundle_validation.py` preserves only well-formed reported
  source descriptions; its result remains training-ineligible.
- `scripts/test_harvest_bundle_validation.py` proves valid context is retained,
  while changed assurance is rejected.

## Verification and remaining gate

Verification passed: 7 harvest-validator tests (including the new
reported-source case), 16 ingest checks, 4 annotation-schema checks,
`swift build`, 14 XCTest cases, 90 Swift Testing cases, and `git diff --check`.
This does not claim a genuine bundle, producer bilateral acceptance, hardware
qualification, eligible corpus, or model gate.

P4-L is now unblocked only by the completed HI-SOURCE-03 bundle being run on
Sillycon and made available at its project-local location. Consumer validation
will report compatibility for that exact producer revision/sample scope only.
