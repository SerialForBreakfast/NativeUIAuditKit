# Integrated iOS offline toolchain review — handoff

**State:** Review-ready; architect acceptance pending.  
**Scope:** P1-A, P2-A, P3-A, P4-B, and P5-A existing offline software only.  
**Date:** 2026-09-19.

## Outcome separation

| Outcome | Result | Evidence |
|---|---|---|
| Software behavior | Passed | The actual exporter CLI, assembly, validation-only trainer entry point, selector, and comparison consumer completed in one synthetic test. |
| Data eligibility | Failed / not established | The inputs are temporary 1×1 toy PNGs under `.build/debug-output/`; no eligible iOS corpus was created or qualified. |
| Live integration | Not applicable | No TVTestRig bundle, Office control, capture, or external transfer was used. |
| Model gate | Not applicable | Validation-only mode was used; no inference, training, checkpoint promotion, or metric gate ran. |

## Remediated integration defects

1. The exporter emits `train|val|test/{images,labels}`, but P5 preflight only
   recognized the old `images/<split>` shape. Preflight now accepts the exporter
   layout (and the documented legacy layout), decodes PNG chunk/CRC/compressed
   scanline structure, and still requires paired labels.
2. Export previously allowed output outside the package and stale output reuse.
   It now permits only a new in-package output directory and returns a nonzero
   exit on collision or boundary violation.
3. P4-B keyed leakage by the combined `(content, family)` pair. It now rejects
   cross-split repeated content and cross-split repeated family independently.
4. P2-A expected an obsolete top-level prediction shape rather than P1-A's
   nested `prediction-artifact-v1` envelope. It now verifies the real nested
   identity/completeness/results fields, rejects failed records, and reports
   missing numeric metrics as explicitly unavailable rather than zero.

## Acceptance evidence

The integration test is [`scripts/test_integrated_offline_toolchain.py`](../../../scripts/test_integrated_offline_toolchain.py).
It creates a project-local deterministic source, invokes `export_coco.py`, feeds
the emitted layout to `train_ios_model.py --validate-only`, uses exported test
pixels/labels for selector and corpus assembly input, compares an actual-format
P1 artifact, and proves repeat export collision rejection.

The following completed with `.venv-yolo/bin/python` (Python 3.13.2), followed
by `git diff --check`:

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
```

`swift build && swift test && git diff --check` also completed: 14 XCTest and
90 Swift Testing tests passed. No tests write outside the package; temporary
artifacts are removed from `.build/debug-output/` during teardown.

## Deliberate limits and next dependency

This proves interfaces, not P1-B/P2-B inference evidence. The per-image P1
artifact intentionally does not compute evaluation metrics; a controlled caller
may supply numeric metrics to P2. When absent, P2 reports unavailable rather
than inventing a delta. A full Run 009 baseline still requires eligible iOS test
pixels, an assigned inference run, and accepted P1-B artifacts. P5-B remains
blocked on eligible, frozen full corpora and separately authorized execution.
