# Growth-preserving preparation and weighting repair

October 1, 2026. Owner: Codex. Base commit `24d2bfb`; pre-existing SYN-12,
SYN-13 and GROWTH-01 research/status changes preserved. No git writes.

| Outcome | Result |
|---|---|
| Software | Explicit continuity policy and context preparation implemented; offline checks below |
| Data | All 1,883 existing controls prepared, no membership/label changes |
| Integration | Existing assembly/experiment/trainer paths support explicit reweighting; context is diagnostic-only |
| Model | Not run; no accuracy, CoreML parity or promotion claim |

## Delivered

- `baseline-fixture-budget-v1` preserves all OS/human weights exactly and divides
  baseline fixture mass separately by label across old+new fixture controls.
  Empty additions return the original weights exactly. Legacy inputs retain their
  policy; this is explicit, not a reinterpretation of FDR022.
- Retained loss budgets verified: fixture **70.6976744%**, OS **9.3023256%**, human
  **20%**. The choice controls comparability, not optimality. Within-fixture weights
  are now equal per label; this policy is documented, not concealed as unchanged.
- `focus_context_inputs.py` provides a real CLI consuming sealed retained protocols.
  Existing 256x256 crops are reused; full scenes share a 768x432 aspect-preserving
  transform. Target masks, normalized bounds and clipping flags retain size.
  No focus labels/native callbacks/reference unfocused size enter prediction records.
- **1,883/1,883 controls, 693 scenes, zero blocked.** Initial preparation lacked
  bounds for 152 appearance-a2 training controls. Their retained v1.4 crop manifest
  supplied bounds matched by pair ID, frame hash and crop hash, not label. Original
  records remain unchanged; recovery provenance is in the new manifest.
- All **32/32** retained growing pairs preserve enlargement on both mask axes.
  Scene geometry preserves original ratios across all 112 same-element comparisons.
  Mask raster rounding yields maximum ratio error 0.031746 across the 112 comparisons;
  masks are not exact continuous geometry. These are not qualified temporal journeys.
- Reweighted protocol prepared from the existing three-cache pipeline, with all
  **1,550 training + 315 development + 18 retention** members unchanged. Encoding
  receipt keeps its original runtime identity; current trainer code is independently
  pinned. No duplicate encoding needed. New objective requires a new run approval.

## Evidence and reproduction

Use project-local `TMPDIR=.build/tmp`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=scripts`
and `.venv-yolo/bin/python`. Outputs must be fresh directories.

```text
scripts/focus_context_inputs.py
  --protocol reports/work/SYN-12-EXECUTION/artifacts/training-protocol/protocol.json
  --geometry-manifest dataset/focus_ring/appearance-a2-pilot-intake2/focus_dataset_manifest.json
  --output reports/work/FOCUS-GROWTH-02/artifacts/context-complete

scripts/audit_focus_growth_inputs.py
  --protocol reports/work/SYN-12-EXECUTION/artifacts/training-protocol/protocol.json
  --context reports/work/FOCUS-GROWTH-02/artifacts/context-complete/manifest.json
  --output reports/work/FOCUS-GROWTH-02/artifacts/audit-complete

scripts/focus_native_body_experiment.py
  --inputs reports/work/FOCUS-GROWTH-02/reweighted-input.json
  --output reports/work/FOCUS-GROWTH-02/artifacts/reweighted-protocol
```

All above passed. Detailed IDs, transforms, masks, source references and exclusions
are in `artifacts/context-complete/manifest.json`; exact weights/deltas and pair
measurements in `artifacts/audit-complete/{weights,audit}.json`. Bulky artifacts
are gitignored. The initial partial result is retained separately, not overwritten.

Focused Python suite: **57 tests passed** (4.248s): growth inputs, native assembly/execution, reviewed continuation,
full-fit and training extension. Tests cover actual growth pixels, no-growth/size
distinctions, resolution invariance, clipping, jitter, invalid geometry, duplicate or
protected roles before decode, missing bounds, hash mismatch, deterministic identity,
label-independent historical recovery, no-addition identity, nonfixture preservation,
real assembly dispatch/cache reuse and refusal of old run approval.
Generated tiny trainer fixtures are software tests, not retained-corpus training.

Offline Swift build passed (4.45s); Swift test passed (14 XCTest + 120 Swift Testing).
The initial restricted build failed at nested `sandbox-exec`; scoped approved build
and test execution succeeded with project-local temp/cache/config/security paths.
Logs: `python-tests.log`, `swift-build-approved.log`, `swift-test.log`.

Real trainer `--dry-run --experiment-arm native-body-full-fit` returned exit2 as
expected: `configurationValid=true`, `launchEligible=false`, sole execution blocker
`missing_run_approval`. See `trainer-preflight.log`. This verifies the real retained
corpus and cached-protocol path, not only mocked dispatch. No run directory created.

## Boundary and next experiment

Context artifacts are **not yet a fusion model**. Current 576-feature head cannot
consume them without an explicit architecture and new encoding/training contract.
No production crop change, new encoder, retained-data inference, training, export,
threshold change or TTR operation occurred. Single-frame relative geometry does not
prove temporal growth, and oracle annotation boxes do not prove detector-box accuracy.
Tests exercise jitter handling, not model robustness to jitter.

Next: approve one cached-feature weight-control comparison (seed 42, existing
optimizer and fixed 0.85 gates, at most 1,000 updates/300 training seconds, no retry,
export or promotion). Then compare a separately specified context-fusion model on
identical membership and source budgets. No further human annotation or TTR build
is needed for this preparation. Swift/CoreML parity belongs to that new model's
export assignment. Coordination not applicable: no producer action changed.
