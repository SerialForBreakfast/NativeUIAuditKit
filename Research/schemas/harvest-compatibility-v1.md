# Harvest bundle compatibility v1

**Status:** Source-pinned NUA consumer contract. It describes the read-only
producer snapshot below and does not constitute producer acceptance, live-device
qualification, provenance attestation, corpus eligibility, or a model gate.

**Producer snapshot:** TVTestRig commit
`586050e043bddd742c701963650e2fc5815afe36`, clean working tree, inspected
2026-09-19. The source paths are
`TVTestRig/TVTestRig/TVTestRig/SyntheticFactory/FixtureBatchHarvestEngine.swift`,
`HarvestDatasetIndex.swift`, `FixtureHarvestReceipt.swift`,
`HarvestBundleValidator.swift`, and `HarvestIdentity.swift`. The producer's
offline instructions are `Docs/Testing/harvest-bundle-validation.md` at the
same revision.

## Scope and compatibility result

This defines exactly the offline format that the future P4-A consumer must
support as **harvest-compatibility-v1**. That consumer must fail closed for a
bundle that does not meet every required condition below. This is a
source-pinned local agreement only; a genuine completed bundle plus identity
evidence is still required by P4-L before integration is qualified.

| Item | v1 requirement | NUA support / outcome |
|---|---|---|
| Producer revision | `586050e043bddd742c701963650e2fc5815afe36` | Source-pinned; other revisions require a new compatibility case. |
| Dataset index | `datasetLayoutVersion == 1`; `telemetryContract == "harvest-canonical-v1; source-version-unverified"`; `provenance == "unverified-pixel-telemetry-binding"` | Supported only with these exact identifiers. Unsupported identifier/version is a consumer `unsupported_version` rejection. |
| Coordinate identifiers | `normalizedCoordinates == "xyxy-top-left-unit"`; `pixelCoordinates == "xywh-top-left-pixels"` | Supported. Convert the normalized top-left `xyxy` value to NUA/Vision representation only after validation. |
| Receipt | `schemaVersion == 1`, `outcome == "completed"`, `failure == null`, and `acceptedRowCount > 0` | Required. Partial/aborted output is `incomplete_run`, never manually promoted. |
| Publication | Completed directory only; names containing `.partial-` are rejected | Required. Producer stages `.NAME.partial-UUID` then exclusively renames completion. |
| Integrity index | Every indexed artifact has unique flat filename, exact `byteCount`, and SHA-256 | Required. Any digest/path/count failure is `integrity_failed`. |
| Required artifact set | `manifest.json`, `training.json`, `calibration.json`, `held-out.json`, and the three per-row artifacts | Required; no missing, duplicate, or extra *indexed* artifact. |
| Sample split | Each row uses exactly `training`, `calibration`, or `held-out`; each split file equals its manifest subset | Required. Preserve names; do not fold calibration into training. |
| Pair metadata | `id`, `unfocused_png`, `focused_png`, `focused_element_id`, `is_settled`, `elements`, and optional `recipe`, `unfocused_provenance`, `focused_provenance` | Required fields are validated as listed below. Optional provenance objects do not create a trusted identity claim. |
| Taxonomy | `taxonomy_class` is producer text; no producer taxonomy version exists in v1 | Preserve losslessly through validation. P4-A must map only against NUA's frozen category map and reject/report unmapped classes—never silently remap. |
| Identity | `HarvestIdentity(deviceID, runID, captureGeneration)` is an in-memory adapter gate, not an exported v1 bundle field | Not proven by an offline bundle. Positive fixture remains `unverified` and ineligible; actual shared attestation is P4-L/TV-I1 work. |

The producer validator permits Codable's default unknown-key behavior while it
requires all decoded non-optional fields. NUA v1 therefore may ignore unknown
additive keys only when every required v1 semantic remains unchanged. A new
required meaning, changed identifier, coordinate convention, split vocabulary,
or provenance claim is incompatible until a new versioned case is reviewed.

## Exact layout and required fields

A completed bundle has flat artifact names. The index controls which files are
read; an unindexed directory entry is not part of ingestion.

```text
bundle/
  dataset-index.json
  harvest-receipt.json
  manifest.json
  training.json
  calibration.json
  held-out.json
  synth-0_unfocused.png
  synth-0_focused.png
  synth-0_metadata.json
```

`dataset-index.json` contains `datasetLayoutVersion`, `telemetryContract`,
`producer`, optional `producerBuild`, `provenance`, `normalizedCoordinates`,
`pixelCoordinates`, and `artifacts`. Each artifact has `path`, `sha256`, and
`byteCount`.

`harvest-receipt.json` contains `schemaVersion`, `outcome`,
`acceptedRowCount`, `rejections`, and optional `failure`. A completed receipt
requires `failure` to be absent/null. It is a diagnostic receipt, not proof of
sample authenticity.

Every manifest and split row is `FixtureHarvestSample`:

```text
id, path, sha256, expectedFocus, box,
optional category, optional metadata, optional split
```

For a valid row, `split` is required in practice and one of the three values
above. `metadata` must include `unfocusedPath`, `focusedPath`, and
`metadataPath`; producer output also writes `recipeFile`, `recipeHash`, `seed`,
`stepIndex`, and `taxonomyClass`. `path` is a legacy relative path whose final
component equals `focusedPath`; it must not be absolute, empty, `.`/`..`, or
contain a backslash or NUL.

The metadata sidecar's `elements` entries require `element_id`,
`taxonomy_class`, `is_focused`, `normalized_bounds`, and `pixel_bounds`.
`normalized_bounds` is `[xMin, yMin, xMax, yMax]`, top-left-origin and unit
bounded. `pixel_bounds` is `[x, y, width, height]`, top-left-origin pixels.
Exactly one element is focused; its ID equals `focused_element_id` and
`expectedFocus`, and its pixel bounds equal the manifest row's `box`.

## Validator-derived limits and rejection behavior

The compatibility test must use the producer limits as observed, rather than
approximating them: at most 10,000 indexed artifacts; at most 32 MiB per file;
at most 256 MiB total bytes read; decoded PNG dimensions at most 8192 by 8192
and at most 16,777,216 pixels. PNG pair dimensions must match. Bounds must be
finite, positive, and within both image and normalized-unit extents.

Expected normalized NUA result codes are consumer-owned summaries of the
producer behavior, not producer wire values:

| Condition | Expected result code |
|---|---|
| Unknown index/receipt/coordinate contract | `unsupported_version` |
| Partial directory or incomplete/aborted receipt | `incomplete_run` |
| Traversal, symlink, special file, duplicate/extra/missing index artifact | `unsafe_or_invalid_manifest` |
| Byte count or SHA-256 mismatch | `integrity_failed` |
| Invalid/oversized PNG or mismatched pair | `invalid_image` |
| Stale/multiple/missing focused element, bad split, or invalid bounds | `invalid_metadata` |
| Unmapped taxonomy after otherwise-valid producer bundle parsing | `unsupported_taxonomy` |

## Deterministic offline case definitions

These are definitions for P4-A's consumer fixture builder, not a claim that
files already constitute a genuine harvest. All positive bytes must be a
deterministic non-user 1x1 PNG and the index hashes/byte counts must be
recomputed from those exact bytes.

| Case ID | Construction | Expected integrity result | Eligibility |
|---|---|---|---|
| `H1-positive-v1` | One completed row and all required indexed files; matching bytes/hashes; a real decodable 1x1 pair; one settled focused element with unit-valid bounds and a known NUA taxonomy. | pass | false: `unverified-pixel-telemetry-binding`, test-only fixture, no live identity attestation |
| `H1-unknown-version` | Change an index identifier or receipt schema version. | `unsupported_version` | false |
| `H1-aborted-receipt` | Set receipt outcome to `aborted` or set a failure. | `incomplete_run` | false |
| `H1-altered-bytes` | Change one indexed file without updating its index digest/count. | `integrity_failed` | false |
| `H1-traversal-or-symlink` | Reference a traversal path or symlinked indexed artifact. | `unsafe_or_invalid_manifest` | false |
| `H1-malformed-png` | Keep hashes consistent but use non-decodable PNG bytes. | `invalid_image` | false |
| `H1-stale-focus` | Make focus ID, focused flags, or row box disagree. | `invalid_metadata` | false |
| `H1-split-conflict` | Make a split file differ from the manifest subset. | `invalid_metadata` | false |
| `H1-missing-or-duplicate-artifact` | Omit a required pair member or duplicate an index path. | `unsafe_or_invalid_manifest` | false |
| `H1-invalid-bounds` | Use non-finite, empty, out-of-image, or out-of-unit bounds. | `invalid_metadata` | false |
| `H1-unknown-taxonomy` | Use a producer-valid but NUA-unmapped `taxonomy_class`. | integrity pass then `unsupported_taxonomy` | false |

Existing `Scripts/test_ingest_fixture_batch.py` uses PNG-signature-only,
geometry-oriented mock bytes and checks legacy conversion behavior. It is not a
v1-positive compatibility fixture because it has no receipt/index and its bytes
are not decodable PNGs. Keep it useful for its own parser tests, but do not use
it to assert harvest-bundle integrity, provenance, or training eligibility.

## NUA test-result envelope

P4-A tests should emit this consumer-owned envelope; it is not written into a
producer bundle:

```json
{
  "caseID": "H1-positive-v1",
  "producerRevision": "586050e043bddd742c701963650e2fc5815afe36",
  "contractVersion": "harvest-compatibility-v1",
  "consumerRevision": "<NUA revision or dirty-worktree marker>",
  "integrity": { "passed": true, "resultCode": "pass" },
  "provenanceState": "unverified-pixel-telemetry-binding",
  "eligibleForTraining": false,
  "eligibilityReasons": ["offline test fixture", "no shared identity attestation"],
  "evidencePath": "reports/work/P4-A/<case-id>.json"
}
```

`evidencePath` is repository-relative. Do not include host paths, device IDs,
run IDs, secrets, or invented attestation values in fixtures or reports.

## Producer-owner brief

Please preserve the current completed-bundle layout and the exact v1 index,
receipt, coordinate, and provenance identifiers when publishing a consumer
candidate. With a format change, provide the producer revision, a minimal
offline positive and the affected negative cases, expected validator result,
and a migration note. A positive offline result must continue to state
unverified provenance and `approvedForTraining: false`. Identity lifecycle and
wire evidence remain TV-I1; a genuine-bundle check remains P4-L.

Open questions that do not block P4-A parser work: the producer has no exported
taxonomy version, and `HarvestIdentity` is not serialized into v1 artifacts.
Those questions constrain `H1-unknown-taxonomy` and all eligibility assertions,
respectively; they do not authorize a fabricated field or fallback identity.
