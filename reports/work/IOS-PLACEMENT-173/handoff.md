# IOS-PLACEMENT-173 — complete, candidate not accepted

Run019 tested264new unique native placement/tint training frames, retaining
Run017's fixed five-epoch configuration and fresh Run013 initialization.
14804train/2800validation/2400test;24duplicate controls excluded. No evaluation
membership changed. Shipped models remain untouched.

## Matched results

Custom all-point AP, not official trainer/COCO metrics:

| Population | Run017 AP50 / AP50:95 | Run019 AP50 / AP50:95 |
|---|---:|---:|
| Combined2400,38supported classes | .887166 / .846356 | .882978 / .841897 |
| Withheld2000,13supported classes | .642493 / .554267 | .643083 / .546074 |
| Addon400 | .983136 / .968149 | .979535 / .966516 |
| Page development96 | .291148 / .177810 | .343791 / .219273 |

At confidence.25/IoU.5, page development TP18→19, FP0→0, FN78→77.
All19candidate hits are centered non-native controls. Left48/native48 each remain
0hits. Native AP50.1875 reflects lower-confidence evidence, not usable operating
recall. Aggregate AP50 regressed. The predeclared development acceptance fails.

CancelAction FP171→73 but TP80→76 of80: reduced false positives are not a clean
retention win. Cancel AP50 .998406→.895769. MapView retains100/100TP and FP1→0.
Combined pageControl AP50 .341570→.452892, TP60→79/600, FP0→2; that gain does
not establish generalization to the exposed native/off-center probes.

No promotion, DS-G8 claim, extra epochs or automatic retraining. Missing class
support remains unavailable, not zero. Exposed evaluation is not newly independent.

## Evidence and verification

- Training exec51642/PID20948 terminal0,11455.514seconds; five finite epoch records.
  Final trainer validation mAP50.86622/mAP50:95.83498 is separate from this report.
- Fixed last.pt SHA256 `ecfb0195250e65d9bbbc0954e9e1714af60685d5e1123d5dd0e0784dcdadb378`.
- [Completion](artifacts/completion.json) seal
  `c932855a83a5e9c6a133b99c7ecbcaee56dbdc9240bedd9ce5d7e457b48caf50`.
- `eval_placement173.py infer` exec43363 and `report` exec53559 both exit0.
  All2400retained and96probe records validated; no missing/duplicate/unexpected
  image IDs and zero rejected post-clipping detections. Run017 artifacts reused.
- [Evaluation](artifacts/evaluation/evaluation.json) file SHA256
  `e350f07970b58cd9de0a00d6b8a8874bcfe2c13e5ed697cada6822b2bd373a45`;
  seal `bff131bba66e14d10f5b28032f2bdfd338d76fa8bca6fedab3efbe3461562ae9`.
- Export wall time143.546s combined/5.390s page; includes input verification,
  loading and inference, not isolated model latency or a timed control comparison.
- Existing14focused tests and offline Swift build/test passed, recorded in
  `.build/placement173-tests.log`, `placement173-timing-tests.log`,
  `placement173-build.log`, `placement173-swift-tests.log`. No code change during
  terminal evaluation; unchanged checks reused rather than rerun.
- Raw telemetry/captures, failed172trials, source labels, checkpoints, prediction
  audits and geometry cases preserved. No Git writes or unrelated-file cleanup.

Software verified; data eligible for this experiment; local training/evaluation
integrated; model acceptance failed. No TTR interface or peer action changed, so
SMB publication is not applicable for this local iOS result.

## Next substantial tranche

IOS-DIAG-174: score all264added training images in two batches (017/019), reuse
existing probe/retained predictions, compare training fit with probe geometry,
scale and confidence, and audit the lost cancelAction hits. Produce one supported
next-experiment proposal rather than assume more placement data or epochs will fix
the gap. Independently resume native24 transition intake when its exact producer
source contract becomes available; no recapture is justified by this iOS result.
