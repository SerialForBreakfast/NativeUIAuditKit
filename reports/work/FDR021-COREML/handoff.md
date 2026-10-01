# FDR021 CoreML export — artifact created, integration blocked

## Deliverable

Complete selected-update775 model: pinned ImageNet MobileNetV3-small encoder,
576-feature linear head, in-graph ImageNet normalization and sigmoid outputs.
Not a head-only export. No retraining, data changes, threshold changes or promotion.

- Preferred conversion artifact: `export-fp32/FocusRingDetector.mlpackage`.
- Compiled experimental artifact: `compiled-fp32/FocusRingDetector.mlmodelc`.
- Package size:3,788,242bytes, below unchanged5,000,000byte gate.
- Exact package/compiled/trace hashes: `artifact-index.json`.
- Frozen head/encoder/protocol/reference bindings: `trace/receipt.json`.
- Failed FP16 artifacts retained in `export/` and `compiled/`; not deployable.

## Evidence and outcomes

| Outcome | Evidence |
|---|---|
| Software |12focused tests pass; offline Swift build and109Swift tests pass. Logs: tests-final.log, swift-build-final.log, swift-test-final.log. Legacy FP16 default preserved; FP32 explicit. |
| Data |333unchanged development/retention crops accounted for, production crop RGB hashes match333/333. No new eligibility or independence claim.63PNGs contain partial alpha. |
| Conversion |Direct FP32 CoreML CPU versus full Torch CPU: max error0.0000340939, mean0.0000014878; all333pass0.01tolerance with zero flips at0.5/0.70/0.85. See direct-parity.json. |
| Integration |FAIL: production CPU path FP32 max error0.418649, mean0.002125; FP16 max0.211059. See parity-fp32.json and parity.json. No TTR load or device/ANE proof. |
| Model gate |Blocked; development improvement is not production qualification. Artwork remains weak. Shipped model unchanged. |

Full trace/reference produced under existing Torch2.13/torchvision0.28environment;
conversion under existing resident Torch2.7/coremltools9. No packages installed.
Each stage has an execution JSON with exact command/PID/timing/exit status and a
600second deadline. No stage timed out. Existing size/parity gates unchanged.

## Concrete blocker and next assignment

`launch.py parity` and `launch.py parity-fp32` exit1 because production predictions
disagree. Direct CoreML RGB predictions pass on the same333images, localizing the
remaining problem to the image/runtime boundary rather than complete-model conversion.
PIL training input drops alpha; production `makePixelBuffer` redraws a CGImage
into an opaque BGRA context. All three largest failures contain partial alpha.
Black-composite diagnostic scores are retained but do not reproduce every production
score exactly; do not claim a fully proven compositing/rounding mechanism yet.

Next scoped work: inspect exact production pixel-buffer RGB bytes on affected crops,
define deterministic alpha semantics compatible with frozen training RGB, implement
and test an explicit candidate path without silently changing shipped-model behavior,
then rerun333production parity and legacy regression tests. This changes production
preprocessing beyond the requested export; it was not silently implemented here.
No new training or annotation needed for diagnosis. Resume integration only after
production parity passes; observer-only TTR deployment still needs explicit scope.

Research, task queue, current state, experiment history and lessons updated.
Shared coordination published/read back; peer acknowledgment not claimed.
