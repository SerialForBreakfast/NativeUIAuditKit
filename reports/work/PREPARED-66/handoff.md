# GENERALIZATION-65 / PREPARED-66 — admission and reusable experiment inputs

## Delivered

- Approved32train/5development admission, with original29records and old artifacts
  unchanged. Native negative labels, hashes and lineage rebuilt and verified.
- Frozen generalization diagnostics completed; [results](../GENERALIZATION-65/handoff.md).
- Existing direct trainer now accepts optional `preparedInputs`; old protocols keep
  their original intake path. No separate trainer or replacement cropper introduced.
- Cold preparation verifies raw sources and admission, then builds the existing
  deterministic translation bank. Warm use rechecks hashes, roles, pins, membership,
  bounded non-pickle arrays and source references without raw case decoding.
- Preflight checks array integrity before model launch. Cached input cannot bypass
  model gates or run approval. Missing/changed inputs fail closed, no hidden rebuild.

## Measured actual 32-pair preparation

| Stage | Time |
|---|---:|
| Cold preparation |30.082s|
| Warm verification/loading |0.214s|
| Actual trainer preflight to expected model-gate rejection |0.394s|

160 variants,23,598,720 tensor bytes. Exact tensors and schedule match the existing
path. This is preparation savings, not measured end-to-end training acceleration.
Final cache lives in `.build/prepared66-final-bank/`; it is disposable, not a backup.
Manifest SHA256 `8e35c31222b7708ab867104e97ae35636fbd9d6d29628320c1c3a4e06a14c96c`.
The earlier cache remains preserved but is stale after the final preflight change.

The real expanded-corpus preflight rejects `full_fit_gate_binding`: historical fit
evidence covers24pairs, not32. This is expected, not a producer/runtime blocker.
DATA-67 must validate the unchanged original subset and exact eight additions.

## Verification

- Actual `admit_negatives65.py --base reports/work/EXPOSURE-64/ready/protocol.json
  --proposal reports/work/GENERALIZATION-65/negative-admission-proposal-verified.json
  --decision reports/work/GENERALIZATION-65/data-role-decision.json
  --output reports/work/GENERALIZATION-65/admission`: exit0.
- Actual `prepare_transition_inputs.py --corpus
  reports/work/GENERALIZATION-65/admission/corpus.json --admission
  reports/work/GENERALIZATION-65/admission/admission.json --output
  .build/prepared66-final-bank`: exit0. Verification receipt in that directory.
-75focused Python tests pass3.592s, including real trainer input/preflight boundaries,
  admission/seal safety, source/role/code changes, corrupt/missing arrays, unsupported
  version, wrong shapes, collision, exact tensors and deterministic schedules.
  `.build/prepared66-all-tests-final.log`.
- Required offline Swift build/test exit0:14XCTest+120Swift Testing. Project-local
  caches, scoped host compiler execution. `.build/prepared66-swift-{build,test}.log`.
- Real gate check receipt: `check/receipt.json`; no run directory/model was launched.
- `git diff --check` passes. No Git writes, downloads, external edits or devices.
  Prior Geometry58–Exposure64 changes remain intact; no raw evidence removed.

Software: verified. Data: exact32training/5development admitted; no independent final
evaluation. Integration: offline trainer/preparer verified, producer runtime not
assessed. Model gates: unchanged, no new candidate. SMB: not applicable to local
cache/admission results; existing producer compatibility request remains separate.

## Next substantial tranche

DATA-67: explicit expanded-data compatibility gate, one DTM011-config600epoch
candidate under the applicable experiment authority, then batched comparison on
original24, added8, exposed Settings and counterfactuals. Preserve class-balance and
data-role reporting; no architecture change, capture or promotion. Acquisition
campaign batching is a separate runtime-authorized implementation, not delivered
or assumed by this software tranche.
