# P2-METRICS — comparison correctness repair

2026-09-23; NUIAK architect. Targeted correction to accepted P2-A, prompted by
IOS-COV's incomplete per-class support. No corpus, inference or training changes.

Software verified:14 Python tests including actual exporter/preflight/selector/
assembly/comparison integration; offline Swift build/test. Data eligible: not
assessed. Live integration: not applicable. Model gates: not assessed.

## Defect and fix

reference_comparison.py previously substituted zero for keys missing on one side.
It also accepted bool as numeric and NaN/infinity, and classified empty dictionaries
as available. None of these are valid evidence of measured model differences.

Comparison now reports finite shared-key deltas only, unavailableMetrics keyed by
missing/null side, and partial/available/unavailable global availability. It rejects
invalid values even when the other artifact has no metrics; overflowing subtraction
also fails. Explicit null represents unavailable AP, not zero. Stable input hash
and genuine finite shared-key deltas retain their previous meanings. Completion
must be literal true and requested member IDs must be nonempty/unique.

Tests cover identical artifacts, genuine deltas, incompatible labels, failed
predictions, absent/empty/disjoint/partial metrics, null support, invalid values,
overflow, invalid completion and duplicate members. The real offline toolchain test
also compares disjoint/unsupported metrics from its exported-corpus artifact and
asserts no invented delta. No new metric implementation or metric provenance is
inferred; callers still supply matching metric implementation/support evidence.

## Evidence

- PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python -m unittest
  scripts.test_reference_comparison scripts.test_prediction_artifact
  scripts.test_integrated_offline_toolchain -v:14 tests pass, tests-final.log.
- Initial tests.log records an introduced test indentation error; corrected before
  execution, retained as failed evidence rather than claiming a first-attempt pass.
- swift build/test --disable-automatic-resolution --manifest-cache local with
  --cache-path/--config-path/--security-path under .build/ios-retention-check:
  swift-build.log and swift-test.log. TMPDIR and module caches also project-local;
  scoped host permission, no downloads/simulator use.123 Swift tests pass.
- git diff --check passes. Modified only comparator, its two test files, contract,
  Tasks and BP-96. Preserved all unrelated dirty changes.

Next: consume honest supported-class reports when the replacement corpus and inference
are eligible. Current iOS split-count decision and training approvals are unchanged.
This full targeted repair is review-ready, not a model improvement or broader P2
requalification. SMB is not applicable to this local iOS evaluation correction.
