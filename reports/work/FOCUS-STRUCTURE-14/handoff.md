# Structural-v3 consumer — completed for review

October 1, 2026 PDT. No device operations, new captured data, data admission,
encoding, training, export or model promotion. FDR021 unchanged.

## Delivered

- Received the exact175,879-byte TTR source checkpoint; archive SHA256
  `3bffa1d60bf614afc2d4b3ff44b9b5a1f2b040a6320ecf677e638ae2f8b78c33`.
  All81manifest files verified. Tar extraction includes179entries; those are not
  179corpus examples. [Receipt](artifacts/received/receipt.json).
- Existing consumer now handles composition-v3 composite cards, ranked rows, home
  icons and hero controls, retaining collectionItem labels and measured-body bounds.
  Bounded scroll declarations and optional hidden/alpha/scroll observations validated.
  Missing observations are not defaulted to false. Legacy contracts remain supported.
- Reusable source-checkpoint audit verifies manifest integrity, full matrix coverage,
  recipe hashes, targets/competitors and existing consumer recipe identities. Actual
  delivered48appearance+16transition recipes pass. [Audit](artifacts/source-audit.json).
  These are planned cases, not captured or admitted examples.36appearance recipes
  use custom focus;12use native_image. Their performance must be reported separately.
- Four generated-family tests exercise the actual bundle validator, native crop QA
  and prefilled review preparation, not only the recipe parser. Tampered manifests,
  traversal, incomplete matrices, invalid geometry/focus/version/scroll metadata fail.

## Verification

`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build/tmp" .venv-yolo/bin/python -m unittest test_fixture_structure test_fixture_composition test_fixture_semantic_inventory test_ttr_sidecar_v2 test_fixture_rendered_body test_fixture_batch_review test_focus_artwork_readiness -q`

61tests passed: [log](artifacts/python-tests-full.log).

`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python scripts/audit_fixture_structure.py --checkpoint reports/work/FOCUS-STRUCTURE-14/artifacts/received/ttr-structural-source-evidence-20261002-r1 --output <fresh-project-local-output.json>`

Offline Swift build passes without warnings. Swift test passes14XCTest+120Swift
Testing tests: [build](artifacts/swift-build.log), [tests](artifacts/swift-test.log).
Project-local TMPDIR/module/cache/config/security paths used. `git diff --check` passes.

## Next producer evidence, not another unchanged training run

1. One measured focus pair per family, preserving whole-control, artwork and child
   geometry separately with original pixels and native focus/capture brackets.
2. Producer recipe/composition hash vectors, including optional-scroll cases.
3. A clipped scrolling inventory example: current strict membership is intentionally
   unchanged until the actual representation is established. Transition requests and
   expected outcomes are not labels; retain observed focus and mutation receipts.

TTR's self-service request/campaign/resume/export implementation stays independent.
Continue using deterministic coverage/seed/source-role requests and immutable
archive/manifest/hash/receipt output; no consumer dependency on live peer availability.
The four proofs should precede48-pair expansion and sampled annotation review.

## Independent outcomes

Software verified: pass. Data eligible: not admitted. Integration: source/offline
passed; live v3 pending. Model gate: not assessed. No user annotation needed now.

Receipt and actionable request `nuiak-20261002-structure14-proof-contract` published
to `/Volumes/SharedStatusFile/nuiak/status.yaml`, packetFOCUS-STRUCTURE-14.
Unique-key YAML and readback passed; unrelated entries preserved. This is publication,
not peer acknowledgment. Only sender may clean up its exact shared archive.
