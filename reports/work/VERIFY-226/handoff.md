# VERIFY226 — full-frame retention and native review

Completed both assigned outcomes. No training/capture, production change or Git write.

Published/readback verified `nuiak/verify226.json`,2042bytes,SHA256
`1d4d230b41bed70fe9fb09cb57acc99be2d4084aec6c3385db3e7d80a705a67f`.
Peer acknowledgment remains separate/pending.

## Run035 independent retained evaluation

Existing eval_phase6a exporter/eval_run013 scorer, resident environment,640/MPS,
unchanged letterbox/NMS/settings/thresholds. Explicit manifest and checkpoint hashes
verified before execution; all2400pixels/labels validated. Source hashes and membership
rechecked after inference; prediction artifact completeness/settings validated.
Exit0 in140.848seconds;128MiB output cap respected. Cached022/033/034 reports reused
with matching manifest, class support, metric implementation and operating point.

| Model | mAP50 | mAP50:95 | TP | FP | FN |
|---|---:|---:|---:|---:|---:|
|022|.899967|.858373|16713|4346|7278|
|033|.866455|.827267|17376|8215|6615|
|034|.872356|.839466|17809|7786|6182|
|035|.901047|.861824|18620|6623|5371|

Same2400images/23991labels/38supported classes. This is repeatedly inspected
development evaluation, not untouched final qualification.035improves mAP50 by
2.869percentage points versus034 but only0.108points versus022; not a statistical
significance claim. TP increases1907 versus022 whileFP increases2277. ProgressView,
toggle,pageControl AP50 changes versus022 are−.0994/−.0939/−.0699. More TP at a fixed
threshold does not imply improved ranking AP. Labels/listRows add878/854FP.

Earlier ROI losses remain genuine, but did not predict this whole-screen result.
No promotion: real-domain/complete gate evidence remains absent, with meaningful
per-class and false-positive regressions. Do not launch another blind replay variant.

Artifacts: preflight.json, execution.json, predictions035.json, score035.json and
comparison.json under artifacts/. Comparison SHA256
`f84e0caa1f3881f466b249491366822b509a7c7eeaa3c57ea040e5a38919a5d8`.
Checkpoint `4b28997ba8ab65be589787b23079a480f6b533c061a553827a2553b13af17bca`.

## Native review companion

[Repair09 review](repair09-review.md): representative source/visual inspection,
14overlay-plan/raw-byte/sidecar bindings, eight tab-scan image hash bindings and
14actual production16%-expanded256x256crops. No new cropper/model inference.
Source semantics reviewed, capture-era binary/source binding still missing.
Producer subpixel scan results remain producer measurements, not independent replay.
One diagnostic tab trial remains excluded; no dataset admission.

## Outcomes and next tranche

Software: existing entrypoints completed successfully; no production-code changes,
unchanged offline test evidence reused. Data: existing retained membership only,
repair09 not admitted. Integration: local MPS/crop helper verified, no live TTR run.
Model gates: not passed; shipped models preserved.

Next substantial work: cached per-class error review on035 versus022 (especially
label/listRow FP and progress/toggle/pageControl ranking), paired with EVIDENCE223
native source-binding reconciliation. Freeze one targeted campaign only after this
diagnosis; keep ROI and full-frame objectives separately reported. All inspection
frames and derivatives remain excluded from untouched final audit.
