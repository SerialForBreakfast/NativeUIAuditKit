# Architect acceptance review — 2026-09-19

## Accepted scope

The architect accepted the software-only scopes of H1, P1-A, P2-A, P3-A, P4-A,
P4-B, P5-A, and FR-A after reviewing their contracts, handoffs, actual command-line
entry points, adversarial tests, and integrated offline behavior.

| Packet | Accepted capability | Still not asserted |
|---|---|---|
| H1 | Source-pinned NUIAK offline compatibility contract | Bilateral producer acceptance, genuine bundle, identity/provenance, data eligibility |
| P1-A / P2-A / P3-A | Export, reference comparison, and deterministic regression software | Full-corpus inference or a Run 009 baseline |
| P4-A / P4-B | Fail-closed bundle normalization and split-safe assembly | Genuine producer compatibility or trainable fixture data |
| P5-A | Validation-only launch preflight | Launch eligibility, training, or model gates |
| FR-A | FocusRing quota/pair/split and ADR-0007 alignment contract validation | Capture, producer metadata support, training, or FocusRing v1.0 qualification |

## Review evidence

The current-tree acceptance run passed:

```text
scripts/test_integrated_offline_toolchain.py       1 passed
scripts/test_prediction_artifact.py                6 passed
scripts/test_reference_comparison.py               3 passed
scripts/test_regression_selector.py                2 passed
scripts/test_corpus_assembly.py                    2 passed
scripts/test_training_preflight.py                 3 passed
scripts/test_harvest_bundle_validation.py          7 passed
scripts/test_annotation_schema_versions.py         4 passed
scripts/test_ingest_fixture_batch.py              16 passed
scripts/test_focus_ring_readiness.py               6 passed
scripts/test_harvest_focus_pairs.py                2 passed
swift build                                        passed
swift test                                         14 XCTest + 90 Swift Testing passed
git diff --check                                   passed
```

P0-A was not accepted: its own handoff reports no recoverable originals at the
bounded sources and incomplete label identity finalization. R-A, BADGE-A, DOC-A, and
HIST-A remain review state because no complete handoff/evidence package was available
for this review.

H1, P4-A, and FR-A were published as accepted software-only scopes in the shared
NUIAK status and read back successfully. Peer acknowledgment remains separate from
publication and no device operation was requested.

## Next gates

- P0-B requires a specific backup/archive location; P0-C requires separately authorized
  rendering/reconstruction work.
- P1-B/P2-B/P3-B/P5-B require eligible corpus bytes.
- P4-L requires a genuine completed producer bundle.
- FR-B requires explicit Office capture authority plus producer support for the ADR-0007
  metadata envelope.
