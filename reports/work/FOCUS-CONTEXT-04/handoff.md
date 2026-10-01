# FOCUS-CONTEXT-04 — completed diagnosis, no promotion

October 1, 2026. Implemented and executed all three approved comparisons without
another per-run human approval. FDR021 and shipped models remain unchanged.

## Results

Every new head confidently classifies all 1,550 training controls correctly, but
none produces an eligible checkpoint under the existing selection rules.

| Input/model | Focused hits /27 | False positives /288 | Artwork hits /12 | Unique-correct frames /14 |
|---|---:|---:|---:|---:|
| FDR021 selected baseline |16|3|2|12|
| FDR024 nonlinear local head |14|10|0|7|
| FDR025 +geometry |15|9|1|9|
| FDR026 +geometry+scene |15|24|1|11|

New-run rows are **terminal diagnostics, not selected candidates**. All retain
18/18 retention classifications. Multiple/wrong complete-frame selections are
4/1, 3/1 and 1/1 respectively. Eighteen additional development frames lack complete
candidate-set support; they contribute candidate scores, not invented frame outcomes.

All 34 saved evaluations replay exactly through the existing metric implementation.
All arms have identical initial predictions. Zero snapshots pass either existing
selection eligibility or the stricter FDR021 comparison. Maximum artwork hits
over all snapshots are 0/1/1: this is not just a poor checkpoint selection.
At the latest common saved update 175, artwork is 0/0/1, FP 7/7/24 and unique
7/9/11. Matched-update diagnostics do not change selection. All arms stop through
the unchanged training-fit rule, not a time limit.

## Diagnosis and next decision

1. **Head capacity is not the main remaining explanation.** The nonlinear heads
   fit every training example but transfer poorly. Correct annotations do not
   automatically teach invariance to unfamiliar artwork. This does not prove
   that every annotation is perfect.
2. **Growth normalization was real, but geometry alone did not fix transfer.**
   The prior audit measured that loss. Supplying normalized current bounds still
   failed here; absolute size can also correlate with layout rather than focus.
3. **This frozen scene representation is insufficient.** Adding global and masked
   ImageNet features increased false positives. This rejects this recipe, not all
   contextual architectures. The encoder remained frozen, spatially downsampled
   and pooled; it learned no focus-specific visual features.
4. **Coverage and representation remain interacting hypotheses.** Holding data
   fixed cannot establish whether missing appearance diversity or inadequate
   visual features is the dominant cause. The development set is small and
   repeatedly exposed, not independent production qualification.

Next: a bounded partial-backbone fine-tune against a matched frozen control,
keeping admitted data, evaluation, threshold and selection fixed. Establish
gradient flow, training fit and held-out-source transfer separately. Predeclare
compute/memory limits before execution. Do not simultaneously change data, loss,
preprocessing and threshold and then attribute an improvement to one of them.
If trainable features still fit but fail transfer, prioritize targeted real-artwork
or counterfactual appearance coverage—not broad reannotation or more of the same
synthetic layouts. No additional human annotation is needed to interpret this result.

The three-run envelope is exhausted; no fourth model was launched. Reviewed boxes
were used as inputs. Detector-box sensitivity, CoreML parity and deployment timing
remain future gates; no deployment claim is made.

## Acceptance evidence

- Software: integrated into the real trainer and existing optimizer/selection loop;
  distinct context-MLP checkpoint kinds prevent accidental linear-head export.
  67 focused Python tests pass; offline Swift build and 14 XCTest + 120 Swift
  Testing tests pass. `git diff --check` passes.
- Data: exact 1550 training + 315 development + 18 retention, unchanged weighting,
  fixed 0.85. All crop/frame/scene/mask/geometry bindings verified; protected roles
  rejected. No source annotations changed, new admission or final-challenge access.
- Encoding: 693 scenes / 1883 controls, batches of 8, 11.341 encoder seconds;
  frozen state unchanged. Cache and references retained in artifacts/encoded.
- Runs: FDR024 PID67553, 335 updates / 17.918 training seconds; FDR025 PID67645,
  300 / 15.391; FDR026 PID67759, 198 / 11.070. All completed successfully as
  software executions; all failed the model comparison.
- Budget: receipted processes total 818.998 seconds, including failed startup
  attempts and encoding. With a conservative 180-second protocol-preparation
  allowance, 998.998 < 1800 seconds. Artifacts/run outputs total 193,264,721 bytes,
  below 2 GiB. Actual optimization took 44.379 seconds; input verification dominated.
- Recovery: initial encoding failed before cache creation on MPS non-divisible
  mask resizing. Explicit CPU mask reduction fixed it, with encoder/pooling still
  on MPS. First training launch stopped before model loading because combined log
  headings did not satisfy exact per-run bindings. Both receipts remain; neither
  produced a trained candidate, and both count against the original budget.
- Integration: local pipeline complete; TTR changes/runtime were unnecessary.
  Shared coordination is not applicable: no producer next action changed.
- Model gate: failed; no export, promotion or shipped-model change.

## Reproduce without model execution

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python reports/work/FOCUS-CONTEXT-04/analyze.py
```

[Results](analysis.json), [inputs](inputs.json), [authorization](authorization.md),
[envelope](envelope.json), [contract](../../../Research/Plans/FocusContext04.md).
Protocol: `0399de2a10e8196e489c5bbb6e61650b534e76d8aa5762ef7a17a57d964396db`.
Bulky evidence is gitignored. The inherited configuration string `fresh-linear-head`
is baseline metadata; the actual `context_mlp_64` model, checkpoint metadata and
implementation specify the experimental 1736→64→1 MLP.
