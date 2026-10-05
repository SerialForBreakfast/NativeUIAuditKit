# IOS165 — matched repair experiment complete

Both five-epoch runs and serial evaluation completed with exit0. Each arm accounts
for all2400 retained and96 page-development images, with no inference failures.
No model promoted; preserved Run014 failure and original corpus/checkpoints.

## Results

All figures below use the same custom all-point interpolated AP implementation,
not official Ultralytics/COCO AP. Percentages are comparable within this table.

| Evidence | Run013 |016 prior data|017 repaired data|
|---|---:|---:|---:|
|Withheld2000 AP50,13 supported classes|63.22|63.07|64.25|
|Withheld AP50:95|57.07|54.71|55.43|
|Combined2400 AP50,38 supported classes|87.90|87.84|88.72|
|Combined AP50:95|85.27|84.39|84.64|
|Page96 AP50|0|24.75|29.11|
|Page96 operating TP / FP / FN|0 /48 /96|7 /0 /89|18 /0 /78|

Operating confidence=.25, matching IoU=.5. Zero observed false positives does not
establish reliable detection: repaired recall is only18.75% on the page probe.
Repaired page candidates exist on30/96 images at export threshold versus36/96
prior; better successful boxes coexist with many absent predictions. Oracle
best-IoU width ratios improve from Run0134.53 to prior1.067/repaired1.037, but
oracle geometry is diagnostic, never model-selected accuracy.

Repair versus prior withheld AP50 gains1.175 percentage points; AP50:95 gains.720.
However repaired AP50:95 remains1.647 points below Run013. Combined per-class AP50
gains concentrate in pageControl(+14.95points) and scrollIndicator(+18.34);
label falls1.08points. No uniform improvement or statistical significance claim.
Combined unsupported classes homeIndicator,unknown,webContent remain unavailable;
the withheld corpus supports only13/41 classes. DS-G8 remains unmet.

## Contract and evidence

14540 training members,2800validation,2400test per arm;900 native pixels and labels
changed together, not a label-only causal experiment. Same Run013 initialization,
seed42, five epochs, fixed-last checkpoints,640long edge,batch8,MPS,AdamW1e-4,
bias warmup1e-4, no augmentation. Existing666manual repairs and5200evaluation
members preserved. No tuning against fresh final evaluation.

- [Frozen launch](artifacts/launch-corrected.json): seal/source/membership pins.
- [016 report](artifacts/r016-prior-evaluation.json) and
  [017 report](artifacts/r017-repaired-evaluation.json): sealed exact metrics,
  hashes, per-class support and per-image geometry.
- Checkpoint016 SHA256:22482e54b73a1bf0006f4a9985583e7a72b8d17a9ce322ada7a8e3fe725af077.
- Checkpoint017 SHA256:24b53eee1a383038d0b3c4ffbb60ee30340d6b810c53adf6bb9d601a867c7bd5.
- Training driver71394 and evaluation54635 terminal0. Existing32focused checks
  and integrated offline Swift checks passed; final changes are evidence/docs only.
- Run016 receipt11330.11seconds; Run017 epoch CSV11294.10seconds. Its receipt
  22823.32seconds is cumulative campaign time, not standalone arm time.

Software verified; existing eligible training membership unchanged except accepted
native159 overlay; local training/evaluation integration verified; model gates not
passed. Retained/probe results are development evidence, not independent final proof.

## Next substantial tranche

1. Diagnose the66 page images with no repaired candidate and localization losses
   using these saved predictions: stratify existing recipe/style/size metadata and
   audit matched misses before choosing resolution, coverage or optimization work.
2. Resume native24 transition intake once the exact table-v3 producer source is
   available. Validate callbacks/geometry, then compare050/051/052 on the same
   real move/no-op/artwork cases before any training-role decision.
3. Register at most one targeted detector comparison from that diagnosis, keeping
   evaluation membership fixed and preserving Run013; no automatic epoch sweep.

TTR local checkout remains46dce7b3 and shared status still reports uncommitted v3
source basedb98402df at this handoff. Existing source request is sufficient; no
recapture, duplicate status noise or build-only request. iOS results stay local.
