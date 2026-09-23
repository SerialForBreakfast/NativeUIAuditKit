# APPEAR-A2 — Authorized live pilot and reference comparison

| Outcome | Evidence |
|---|---|
| Software verified | Pixel-budget batching repair;119 FocusRing +37 direct tests pass; Swift build,14 XCTest and93 Swift Testing pass. |
| Data eligible |76 genuine paired examples admitted by v1.4 for development only. Not training approval or an independent holdout. |
| Integration qualified | Exact installed Fixture → direct screenshot runner → production crops passed for all24 recipes. TTR desktop export not exercised. |
| Model gates | Not assessed. No training, export or promotion. |

## Results at frozen0.85 threshold

| Reference | Focused detected /76 | False positives /76 | Crop accuracy |
|---|---:|---:|---:|
| Shipped CoreML |11|9|51.32%|
| FDR-007 Torch |22|0|64.47%|
| FDR-008 Torch |73|0|98.03%|

FDR-008's misses are dark/compact media: seed101 card1(.846389), seed101
card3(.828927), seed211 card3(.691837). Its grid/dialog/hero examples all classify
correctly. No thresholds were tuned. Ambiguity-band counts [.70,.85): shipped2,
FDR-0072, FDR-0083. Binary misses and abstentions are distinct categories.
See [comparison](comparison.json), [frozen protocol](protocol.json) and
[visual review](visual-review.md). Ground-truth boxes are supplied; this does not
test detector localization, unique-focus navigation decisions or physical devices.

76 unique decoded crop pairs /145 unique individual crops /152 crops; no opposite-
label pixel contradictions. Six individual crops from six pairs exactly overlap
prior mixed-training inputs. Related renderer families also remain shared. This
is development evidence, not proof of novel appearance generalization. The prior
Home/Photos failures remain open; white-outline gradients are not Home artwork.

## Operation and retained evidence

- Authorized target9026ECA9-77DB-4AE6-8FE6-BB239E9571FA, tvOS26.5,
  Apple TV4K3rd generation, Xcode26.6/17F113; listener127.0.0.1:8080 bound to
  FixturePID66851. Installed dylib46011bb0a95cb007325a64baaab643ad913e0bf46c250a7198caab7b9f31a095
  matches retained setup evidence. Source pins matched APPEAR-A1; source and
  binary identities are separately recorded, not asserted reproducible-build proof.
- New `dataset/tvos_captures/appearance-a2-pilot/direct-capture.json`:24/24 recipes,
  100/1004K frames,76/76 target pairs. Canonical capture hash
  50d6f9d4be91a34d832273b32127be5de6e4b197f7a92ed871d438d58ff0f29b.
  Capture exit0; first-to-last screenshot span106.780s. No recipe retry.
- Reviewed all76 crop pairs and reference/first/last overlays for all24 recipes;
  no frame-edge cases. Actual focused geometry retained; media neighbor/chrome
  context and wide-control anisotropic crops explicitly documented.
- First intake failed `invalidImage` before manifest publication. Root cause:
 16×3840×2160 exceeds helper80MP. Preserved initial output; repaired local caller
  batching by actual dimensions, keeping existing16-item cap and helper limits.
  Regression tests cover4K batches9/9/1, small inputs16/3, oversized rejection,
  ordered actual rendering and inference entrypoints. BP-83 records the lesson.
- New `dataset/focus_ring/appearance-a2-pilot-intake2/focus_dataset_manifest.json`:
  intake exit0,76 pairs, production16%/256px crops, trainingApproval false.
- [Fresh postflight](postflight.json) confirms same PID/instance, responsive HTTP
  and settled final hero recipe. No resource/process acquired remains running.
  Fixture left on last authorized recipe; no false claim of prior-scene restoration.

## Verification and timing

Exact operational flags: [runbook](../APPEAR-A1/runbook.md), [authorization](authorization.md).
`capture.log`, `intake.log`, `intake2.log` retain operation results. `review_capture.py`
is diagnostic-only and uses production cropper; `compare.py` pins artifacts before
inference and rechecks hashes afterward. Comparison exit0/55.572s including source
validation and inference; Torch batch timings and CoreML load timings retained.
Individual CoreML cold/warm prediction latency was not retained by this diagnostic
comparison; do not infer it from total time. No target-device latency claim.

`python -m unittest discover -s scripts -p 'test_focus*.py'`:119 tests,4.533s,exit0.
`python -m unittest discover -s scripts -p 'test_direct*.py'`:37 tests,18.603s,exit0.
Swift offline build2.39s/exit0; tests14 XCTest +93 Swift Testing/exit0.
Logs in this directory. All explicit outputs/caches local; standard simulator
storage was declared. No source producer edits, installations, restarts or Git writes.
Pre-existing code/data/report changes preserved. No independent timing measurement
of intake or approval waits; do not fabricate those durations.

## Next substantial tranche

APPEAR-B: audit full lineage/pixel overlap before adding these examples to any
training manifest, define source-balanced replay and untouched evaluation membership,
then propose one candidate—not an automatic run. Prioritize dark/compact thin-ring
media and bright negative context; keep Home/dock/artwork challenge separate.
Known pilot errors remain development examples, never final holdout. Current
renderer cannot provide the missing Home artwork axes; TTR request stays open.
Offline sampling/coverage/protocol work is unblocked; new capture/training needs
its own bounded authorization. Do not expand to6000 pairs of the same appearance.

Assigned capture/review/intake/comparison tranche complete for review. Worker and
Fixture skills kept observed labels and operation boundaries; model-workflow kept
reference artifacts, production preprocessing and shipped models unchanged.
Shared status [published and read back](coordination.md); acknowledgment separate.
