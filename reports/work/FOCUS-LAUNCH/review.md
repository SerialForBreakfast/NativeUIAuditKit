# Delivered-packet review — 2026-09-21

This review compares existing handoffs/code against `Research/Plans/TTRPerception.md`
and `FocusRingConsumerReadiness.md`; Tasks.md is the only ownership/state queue.
No worker files were taken over. Tests demonstrate existing scope, not omitted criteria.

## FOCUS-CONSUMER — accept offline foundation

Actual validator/extractor/preflight and score-protocol integration has deterministic
positive/negative coverage. Frame-specific geometry, observed callbacks, recipe-group
splits, actual-denominator quotas and held-out isolation are implemented. The disclosed
Pillow/CoreGraphics parity limitation is addressed additively in FOCUS-LAUNCH: old
v1.2 crops remain inspectable but cannot launch training; new v1.3 calls production
Swift crops. This accepts software only, not a real corpus or SIM-DATA-03/FR-B.

## PER-01 — changes required, preserve existing inventory/schema

`perception_benchmark.verify_evidence` hashes bytes without decoding pixels or checking
dimensions; CLI verification is optional. Correct-hash corrupt files can therefore
pass that check. Original PER-01 acceptance explicitly requires corrupt-image rejection.

Bounded correction: make byte/decode/dimension checks mandatory before reporting
eligible real evidence; separate schema-only test cases and unavailable pixels. Test
correct-hash nonimages, truncated PNGs, dimension mismatch, missing paths and output
collisions through the CLI. Preserve journey grouping/inventory. No new captures needed.

## PER-02 — changes required, preserve relation scorer

The scorer is useful and existing tests pass. It consumes predictions but does not
implement the original deterministic geometry/OCR baseline comparison. Real adapters
may stay unavailable, but the offline contract and deterministic baseline must exist.
Per-slice evaluation and artifact/settings/metric hash binding need completion; do not
represent externally asserted predictions as observed model execution. Latency is
unavailable until measured; fake timing cannot qualify deployment performance.

Concrete semantic bug: `semantic != destructive` increments destructiveAsBenign,
including `unknown`. Unknown is abstention, not a benign claim. Separate destructive-
as-informational from abstention/missed detection and report both with support.
Test ambiguous/localized confirmations, zero support, duplicate proposals, wrong-row
links, missing adapter vs empty success, deterministic equality and slice/hash drift.
Keep no-training recommendation while real evidence/gates are absent.

## PER-04 — changes required, metadata helper only

`physical_focus_readiness.validate` checks crop filenames/size/expansion as supplied
strings, not files or frame geometry. Its `_sha` accepts any 64 characters; it can
return `eligible: true` without pixels. This is not actual ingest/extraction readiness.

Bounded correction: integrate physical observed-frame evidence into the shared strict
dataset contract and runtime crop path, retain physical source identity, validate
actual PNG hashes/geometry/callback alignment, and call the existing baseline adapter.
Report inspection, data eligibility and operation authority separately. Tests must
reject missing/changed/corrupt pixels, nonhex hashes, requested-only focus, stale
callbacks, forged crops, cross-split duplicates and prediction truth. Exercise actual
entrypoints with physical test fixtures, not merely metadata dictionaries. No live
Office operation or independent training pipeline is needed for this correction.

## Verification and next action

Existing perception tests: 5 pass; physical metadata tests: 3 pass. Their success is
not acceptance of omitted integration. Focus suites now cover actual production
crop/CoreML integration, with explicitly test-only pixels. See the tranche handoff
for complete verification. Assign the bounded corrections to existing owners; do
not restart completed work or launch real inference from this review alone.
