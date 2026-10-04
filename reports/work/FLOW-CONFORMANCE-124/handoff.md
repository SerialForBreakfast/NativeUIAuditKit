# FLOW-CONFORMANCE-124 — consumer vectors and exposure inventory

2026-10-04. Local deliverable verified; external artifact delivery pending.

Responds to `tvtestrig-20261004-workflow-alignment`. Reuses H1/v2 fixture
constructors and actual `validate_bundle`, not a second implementation. Source
hashes identify seven relevant files, not a complete dependency closure. Synthetic
64×48 fixtures do not establish rendered crop parity or newer producer coverage.

## Evidence

- `artifacts/report.json`: 11 expected outcomes: valid, partial receipt, unsupported
  layout, altered bytes, corrupt PNG, missing member, duplicate index, viewport
  mismatch, stale observed focus, invalid bounds, cross-split shared baseline.
- Valid input remains unverified and training-ineligible. Validation is read-only.
- `artifacts/pack/exposure.json`: 282 known training-exposed hashes/ancestry from
  COVERAGE119. No private images/paths. No independent final membership. Missing
  hashes mean unknown, never clean. Scope is DTM030, not all historical NUIAK data.
- Archive: `artifacts/nuiak-conformance-exposure-v1.zip`, 54,764 bytes, 103 members,
  SHA-256 `32a3a4309e02a2c8a7d68b1234850e3c045a4a9f41029ef9bf158982bac0f419`.
  Exact member/hash inventory verified. Synthetic images only. Not published.

## Verification

All exit 0:

1. `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build" .venv-yolo/bin/python scripts/build_conformance124.py`
2. Same environment: `.venv-yolo/bin/python -m unittest scripts.test_conformance124 scripts.test_ttr_sidecar_v2 scripts.test_harvest_bundle_validation` — 27 tests.
3. Offline `swift build` and `swift test` with existing project-local caches and
   scoped standard Apple cache permission — 14 XCTest + 125 Swift Testing pass.
   Logs: `.build/conformance124-swift-{build,test}.log`.

Artifact-specific tests skip when local gitignored evidence is absent; existing
H1/v2 deterministic tests remain independently executable. Builder deliberately
requires the pinned local COVERAGE119 audit and rejects an existing destination.

## Coordination and boundaries

Published/read back `nuiak/status.yaml` packet `FLOW-CONFORMANCE-124` on the verified
share. Other fields preserved by before/after semantic hash. TTR acknowledged the
earlier alignment request; acknowledgment/replay of this pack remains pending.
Strict exclusive publication remains blocked by SMB ENOTSUP45; no unsafe fallback,
no archive upload or deletion. Receiving an already published peer archive is not
blocked by this outbound limitation.

Software verified: passed. Data eligibility: not applicable (test-only).
Producer integration: pending delivery/replay. Model gates: not assessed.
No capture, training, promotion, Git writes or external-repository edits. Preserved
pre-existing dirty changes. No speedup claim: this is contract evidence, not a
generation-throughput benchmark.

Next substantial tranche: qualify supported immutable publication and peer replay;
intake retained survey26 evidence when delivered, reproduce the three mixed-model
decisions, and diagnose before selecting another candidate. Extend body/outline
geometry vectors and actual crop parity only against the aligned source contract.
