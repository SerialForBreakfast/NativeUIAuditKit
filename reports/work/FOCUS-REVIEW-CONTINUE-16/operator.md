# Resume the reviewed-data continuation

Run from the repository root with `.venv-yolo/bin/python` and `PYTHONPATH=scripts`.
Every output directory must be new. Preserve the four-frame human review workspace;
this workflow does not edit annotation JSON or infer missing labels.

## 1. Finish the existing review, then production crop QA

The batch is `reports/work/FOCUS-RETAINED-NEXT-15/review-batch-final/batch.json`.
Use its explicit **Finish review** revision, not an automatically chosen older file.
Replace `REVIEW_REVISION` below with that repository-local revision path.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build/debug-output" \
  .venv-yolo/bin/python scripts/focus_review_continuation.py \
  --baseline reports/work/FOCUS-FULL-FIT-03/frozen/protocol.json \
  --batch reports/work/FOCUS-RETAINED-NEXT-15/review-batch-final/batch.json \
  --revision REVIEW_REVISION --crop-qa \
  --output reports/work/FOCUS-REVIEW-CONTINUE-16/reviewed-qa
```

This uses the production cropper, writes a review audit and an **unapproved**
`admission-draft.json`. No training starts. Review all proposed IDs; explicitly
exclude unsuitable controls with reasons. Each admitted frame must retain both
positive and negative examples for the unchanged label-balanced sampling policy.
Hard review issues, uncertain labels, protected overlap or contradictory duplicates
must be resolved or excluded, not overridden. Incomplete frames remain static-crop
examples; they do not establish unique-selection accuracy or transition pairs.

## 2. Membership/source decision

Save the completed admission separately. Bind its revision, crop-QA reference,
baseline seal, session, exact selected/excluded IDs and source-review evidence.
Authorization and source-review evidence use `{path, sha256}` references.
`approved` may become true only following the actual human admission decision.
The relationship decision is `development-exposed-no-independent-claim`; unchanged
development/protected roles must be verified. The recording contains OS families
related to development, so a different recording ID is not an independence claim.

Prepare again with `--revision REVIEW_REVISION --crops reviewed-qa/crops/crop-qa.json`
(use full repository-relative paths), `--admission ADMISSION`, a fresh output,
and the same baseline/batch. No `--crop-qa` is needed when reusing verified crops.
The only data blocker should then be `missing_new_feature_cache`.

## 3. Separately approved feature encoding, then reseal

Encoding approval format:

```json
{
  "version": "focus-addition-encoding-approval-v1",
  "approved": false,
  "protocolSHA256": "EXACT_DATA_READY_PROTOCOL_SEAL",
  "scope": "encode-new-controls-only-no-training",
  "authorizationReference": {"path": "ACTUAL_AUTHORITY", "sha256": "ACTUAL_HASH"}
}
```

After approval, invoke `scripts/focus_review_continuation.py --encode-protocol
PROTOCOL --encoding-approval APPROVAL --output FRESH_ENCODING_DIRECTORY`.
This encodes **only added crops**, MPS, pinned ImageNet weights/normalization,
five-minute internal encoding deadline; no optimizer or model selection.
Use an external bounded supervisor for actual execution. Existing baseline features
and all333development/retention rows are reused, not regenerated.

Re-run preparation with the same review/crops/admission and
`--new-features FRESH_ENCODING_DIRECTORY/features-reference.json`, fresh output.
The new protocol seal binds the ordered feature receipt and cache. Preflight reads
and hashes caches but does not load Torch tensors; execution verifies tensor shapes,
finite values, labels and feature hashes before optimization.

## 4. Actual trainer preflight and later launch decision

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build/debug-output" \
  .venv-yolo/bin/python scripts/train_focus_ring_detector.py \
  --experiment-protocol FINAL_PROTOCOL --experiment-arm reviewed-full-fit \
  --name APPROVED_NEW_RUN_NAME --preflight
```

Without run approval this exits2 with `missing_run_approval`, intentionally.
Run approval must use `focus-reviewed-full-fit-approval-v1`, approved true only
after authorization, exact protocolSHA256/arm/runName, scope
`one-run-no-export-no-promotion`, and a checked authorizationReference.
Pass it through `--experiment-approval`. An actual launch additionally requires
`--execute`, a separately assigned run ID and its exact ExperimentLog entry.
No run ID or training authority is allocated by this tranche.

Keep the same threshold, retention floor, eligible-checkpoint rule and untouched
development membership. If no update is eligible, no checkpoint is selected.
No export or TTR model delivery follows automatically.
