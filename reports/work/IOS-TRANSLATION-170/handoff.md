# IOS170 — completed experiment and matched evaluation

Run018 tested one change: resident spatial translation0→.35 on both axes, retaining
Run017's repaired14540/2800/2400 membership, Run013 initialization and five-epoch
configuration. No data roles, captures, training budget or production model changed.

## Result and decision

Custom all-point interpolated AP, not official COCO/Ultralytics validation metrics:

| Frozen population | Run017 AP50 / AP50:95 | Run018 AP50 / AP50:95 |
|---|---:|---:|
| Combined2400,38supported classes | .887166 / .846356 | .897897 / .860292 |
| Withheld2000,13supported classes | .642493 / .554267 | .687904 / .609954 |
| Addon400 | .983136 / .968149 | .982645 / .967638 |
| Page development96 | .291148 / .177810 | .399426 / .272804 |

At confidence.25/IoU.5, page hits18→34, false positives0→4, misses78→62.
Native hits0/48→10/48; non-native18/48→24/48. All34candidate hits are centered;
left-position hits remain0/48 despite left AP50 increasing0→.086574 at lower
confidence. Spatial augmentation helps some generalization but does not solve the
predeclared operating-point position failure. Combined class AP50 changes include
pageControl+28.076pp, imageView+16.248pp, label+12.056pp, but cancelAction−15.416pp
and mapView−5.406pp. Reject promotion; no automatic epoch extension/retraining.
DS-G8 remains unmet and coverage incomplete. All these exposed groups are retained
development evidence, not a newly independent release qualification.

## Geometry repair and complete accounting

Initial exports retained1426ok/974failed combined records,96ok probes. A one-image
raw diagnostic found zero-width class14 boxes at x=0 after Ultralytics clipping,
with correct original dimensions. They were not valid artifact detections.

The opt-in `discard-zero-area-after-native-clipping-v1` policy retains raw rejected
detections and counts, filters only finite ordered in-bounds zero-area boxes and
leaves strict artifact geometry unchanged. Nonfinite, inverted, out-of-bounds,
invalid-score/class detections still fail. New settings hash, new destination and
both arms re-inferred; first failed exports were not altered or replaced.

All4992records (2496per arm) passed semantic validation. Run018 rejected1719
zero-area detections across974retained images; Run017 rejected0; both probe sets
rejected0. No image was dropped. Metrics describe this explicit filtered pipeline,
not proof of unchanged historical settings or CoreML behavior.
Run017 replay has identical image/detection counts and class order; numerical MPS
differences exist: max score difference1.961e-5, max pixel difference.388184 on
combined inputs; probe maxima8.285e-6/.020142px. Do not claim byte-identical replay.

## Evidence and verification

- Training driver91179 exit0,11412.904s; fixed-last SHA256
  `3ab45129317e988626c6581196701b074c3d4c72dfd8c5fbd923096e81f50be4`.
- Initial infer/report session63128 exit1 at strict report admission; diagnostic78750 exit0.
- Corrected infer/report session80224 exit0; no training retry.
- Candidate/control combined inference120.7s initial and117.6s corrected control;
  full progress timings retained in `.build/translation170-positive-area-infer.log`.
-22focused tests exit0: `.build/translation170-positive-area-tests.log`.
- Offline Swift build/test session37473 exit0; corresponding `positive-area-*` logs.
- [Evaluation](attempt02/artifacts/matched-positive-area-v1/evaluation.json)
  SHA256 `f4a9fa1f66d60f2d61a953f9d293eb7298a1da9dd9f340a84857988d3a42d906`.
- [Evaluation protocol](attempt02/artifacts/matched-positive-area-v1/protocol.json)
  SHA256 `fa675becfc2d02571037b5490e7ea588869d4f4246d8e575ea6ca0c9f2665198`.
- Original training protocol, receipts, failed exports, all raw rejection lists and
  all13page strata remain under `attempt02/artifacts/` (gitignored bulk evidence).

Software verified; data eligible for this bounded experiment only; local training
and evaluation integrated; model goal/gates not passed. No TTR-facing interface,
artifact request or efficacy decision changed, so SMB publication is not applicable.
Existing broad worktree changes and shipped models preserved; no Git writes.

## Next substantial tranche

Prioritize a source-backed placement/style coverage tranche: analyze all retained
left misses and native centered successes, distinguish confidence/localization from
style failures, and freeze renderer-realistic left/center/right training compositions
without using these probe images or related final-evaluation groups as training.
Validate labels and duplicate/split lineage in a batched generator pass, then run
one bounded matched candidate only when that new membership is admitted. Include
cancelAction/mapView regression evidence; retain translation as a diagnostic option,
not an automatic production default. Independently resume native24 transition intake
once TTR's nativeTablev3 source is available locally; no recapture is yet justified.
