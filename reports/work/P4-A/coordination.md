# P4-A coordination update

**Observed:** 2026-09-19. **State:** working.

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
  versions have no fallback. Maintainer reports shared-status publication and
  readback; this worker did not perform the external write.
- **Completed since decision:** Added strict `annotation.schema.v1.1.json`, a
  dependency-free declared-version selector, and parity tests. v1.0 SHA-256 is
  `68f41f4e5988a43d4c3f0582efffbc552c424d15599626a14cf1c6c262aa9e2c`;
  v1.1 SHA-256 is
  `5d0b897bd44510bfa5f9e560f170213273a15162c61547ddbae2cfe2ee1f1d34`.
  Four tests pass: structural parity, no fallback, incomplete/v1.0-scale-1
  rejection, and v1.1 scales 1/2/3 acceptance.
- **Next:** Complete the receipt/index/pair validator and normalizer tests, then
  publish the P4-A handoff.

This worker update is for the NUA shared-status coordinator. No external
`nuiak/status.yaml` write was attempted: AGENTS.md assigns that writer role to
the coordinator, and this update neither claims delivery nor peer acknowledgment.
