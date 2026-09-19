# P4-A coordination update

**Observed:** 2026-09-19. **State:** review-ready.

- **Packet:** P4-A — consumer bundle validation and normalization.
- **Evidence so far:** H1 pins the offline producer contract to TVTestRig
  `586050e043bddd742c701963650e2fc5815afe36`. Existing fixture ingestion
  lacks receipt/index validation and emits scale-1 tvOS sidecars against a
  v1.0 schema that permits only scale 2/3; both are in P4-A scope.
- **Current action:** Implement source-pinned offline validation and a separate
  scale-1 annotation schema version with deterministic fixtures/tests.
- **Decision received:** Maintainer confirmed complete v1.1 duplication. Keep
  v1.0 byte-for-byte unchanged; only v1.1's declared version and scale set
  differ, with distinct identity/descriptions. Missing/unsupported declared
  versions have no fallback.
- **Completed since decision:** Added strict `annotation.schema.v1.1.json`, a
  dependency-free declared-version selector, and parity tests. v1.0 SHA-256 is
  `68f41f4e5988a43d4c3f0582efffbc552c424d15599626a14cf1c6c262aa9e2c`;
  v1.1 SHA-256 is
  `5d0b897bd44510bfa5f9e560f170213273a15162c61547ddbae2cfe2ee1f1d34`.
  Four tests pass: structural parity, no fallback, incomplete/v1.0-scale-1
  rejection, and v1.1 scales 1/2/3 acceptance.
- **Completed since last coordination update:** Added the fail-closed offline
  `harvest_bundle_validation.py` implementation. Its import check passes. It
  validates H1 receipt/index identifiers, bounded flat files, hashes, split
  equality, decoded pair dimensions, focused-element/bounds consistency,
  unknown taxonomy counting, cross-split baseline reuse, and explicitly keeps
  `eligibleForTraining: false` for unverified provenance.
- **Completed:** The adversarial suite now covers valid/source-unchanged,
  unsupported version, incomplete receipt, altered bytes, partial output,
  missing/duplicate/symlink artifact, malformed PNG, stale focus, split
  conflict, invalid bounds, unknown/empty annotations, and cross-split baseline
  reuse. The validator no longer needs Pillow and explicitly preserves absent
  identity as `null` rather than fabricating it.
- **Current source reconciliation:** TVTestRig layout-v1 source now reports
  additive `sourceDescription` with `reported-source; not-attested` assurance
  for production fixture batches. The validator preserves a well-formed object,
  rejects malformed/changed assurance, and still keeps every result unverified
  and training-ineligible. The internal identity challenge is not a NUA
  production prerequisite.
- **Verification:** 6 H1 validator tests, 4 schema-version tests, 16 legacy
  ingestion checks, `swift build`, and `swift test` pass offline. Full acceptance
  evidence is in `handoff.md`.
- **Publication:** The worker published only `packets.P4-A` directly to the
  permitted SMB status file and verified readback. Peer acknowledgment remains
  absent; publication does not establish live compatibility.
