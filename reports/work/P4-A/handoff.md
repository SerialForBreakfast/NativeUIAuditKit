# P4-A handoff — offline consumer compatibility

**State:** review-ready (2026-09-19)  
**Base revision:** `6058676e063d927d27c5387c5ea9896879038a6c`

## Delivered scope

- Complete annotation schema v1.1, selected only by declared version. Version
  1.0 remains byte-for-byte unchanged; v1.1 alone allows scale 1.
- Dependency-free, fail-closed H1 bundle validator and normalizer.
- Ingest preflight that rejects incomplete/invalid completed bundles before
  sidecar creation. `--legacy-fixture-mode` is explicitly test-only.
- Deterministic tests for schema selection and the H1 positive/adversarial
  compatibility matrix.

## Evidence

| Outcome | Result | Evidence |
| --- | --- | --- |
| Software verified | PASS | Schema tests (4), H1 contract tests (6), existing ingest checks (16), `swift build`, and `swift test` pass offline. |
| Data eligible | FAIL (expected) | Fixtures are synthetic. Validator preserves unverified provenance, does not fabricate identity evidence, and always returns `eligibleForTraining: false`. |
| Integration qualified | NOT YET | No genuine completed producer bundle or bilateral acceptance evidence. P4-L remains blocked. |
| Model gate passed | N/A | No training, model export, or model promotion occurred. |

The H1 test suite covers valid/source-byte-preserving input; unsupported
versions; incomplete receipts; altered bytes; partial output; missing,
duplicate, and symlinked artifacts; malformed PNGs; stale focus; split
conflicts; invalid bounds; unknown/empty annotations; and shared baselines
across splits.

## Boundaries retained

- Missing and unsupported schema versions are rejected without fallback.
- Unknown taxonomy values are counted and dropped, never remapped.
- The validator accepts only bounded, flat, indexed artifacts and validates
  hashes, decoded PNG dimensions, split equality, and focus/bounds coherence.
- Normalized records preserve producer/build values when present and express
  absent identity evidence as `null`; they do not imply trusted capture.

## Relevant paths

- `Research/schemas/annotation.schema.v1.1.json`
- `scripts/annotation_schema_validation.py`
- `scripts/harvest_bundle_validation.py`
- `scripts/ingest_fixture_batch.py`
- `scripts/test_annotation_schema_versions.py`
- `scripts/test_harvest_bundle_validation.py`
- `scripts/test_ingest_fixture_batch.py`

## Remaining risks and next work

P4-L needs an authorized genuine TVTestRig export with identity evidence. It
cannot be closed from synthetic fixtures. The next substantial unblocked work
is P5-A: configuration-only training preflight and negative-data tests. It
can consume the strict validation boundary without starting training or using
unavailable corpus pixels.
