# ROI197: recall improved, candidate rejected for promotion

October6,2026. Frozen022base plus026ROI candidate; no training or threshold tuning.

| Partition | Page TP before → after | FP before → after | AP50 before → after |
|---|---:|---:|---:|
| Fit216 |185→202|38→38|.8560→.9208|
| Development96 |58→72|14→15|.6193→.7395|
| Retained2400images/600page targets |249→519|24→24|.8584→.9241|

Fit screen:135crops,10negative/52partial-target regions,17new detections,17matches,
zero negative false admissions. Passed frozen gate to run retained comparison.
All2712originals accounted for including absent/duplicate/abstained proposals. Existing
detections unchanged; only page donors added. Non-page metrics asserted unchanged
against022. Custom matched metrics, not official Ultralytics or untouched-final evaluation.

Development failure: `gallery-inspector-true-false-5-false-19`, confidence.9090,
IoU.3166; predicted height24.4pixels versus truth77pixels. No label correction or
threshold tuning. Negative-region rejection does not guarantee full-box geometry.
No-additional-FP condition and seven of14existing gates fail. No promotion or TTR
delivery. Latency qualification was not launched after rejection; throughput below
is not deployment latency.

## Execution and verification

`roi197_screen.py` and `roi197_compare.py` prepare/infer/report completed with existing
export/scoring and193cropper. Exact sources/manifests/settings sealed in ignored
`artifacts/screen01` and `artifacts/comparison01`.026SHA256
`de3ffdeec3c4767edc2d4bea0059294a26d87b6c9fc03b9d684de769ed3dd638`.
Fit inference10.32seconds;37development+413retained crops26.13seconds. Fit reused;
approximately30MiBoutputs within budgets. No recapture/training. Evaluation seal
`41a23b911c0bdbc2dfde96ad91bb5336413dab04ca53340ce8b99102fd93e152`.

37focused tests and offline Swift build/test pass; logs `.build/roi197-screen-{build,test}.log`.
Tests cover missing crop membership, empty/error distinction, confidence/overlap,
ambiguous donors, duplicate suppression, preserved original boxes and zero-candidate
frames. Software verified; source roles preserved; local PyTorch integration verified;
model gates failed. Next: training-derived height/context diagnosis with retained
regression checks. Dense44crop scans and more epochs are not justified by this result.

Companion:32Big Dog originals match exact requested hashes/sizes/decodes/dimensions and
proposed ancestry; zero within-return pixel duplicates. Return02archive SHA256
`c342c710e61639aa9e6fe71b366cf87d42005abb949e9b4d55c100ce609ec002`,45,110,413bytes.
Receipt published/read back as `nuiak/responses/nuiak-20261006-artwork204-receipt02.json`;
sender cleanup pending. Native focus source/import gap remains, not missing artwork.
Worker confirms both77-token encoders dropped state instructions in203; no regeneration.

## Follow-up geometry diagnosis

Read-only audit of all1,173page labels in the actual026training crop membership:
minimum16.9994, median22.9989, maximum29.9998pixels; none exceed30pixels. The216fit
subset similarly tops out at23.001pixels. This establishes a missing geometry regime,
not proof that adding that regime alone fixes generalization.

The retained failure image visibly contains a prominent capsule around five dots.
`KitchenSinkValidationTest.swift`'s PageComposition155Controller requests native
UIPageControl `.prominent` for seed19. `compose155.py` derives its visible bounds from
the visible/hidden render difference; measured25.6667points at scale3 gives77pixels.
The predicted24.4pixel height mainly covers dots. Do not shrink the visible-body truth
or admit this development example into training to improve its score.

Image SHA256 `214a3db5a779d283cfa2b38620d0e8a13524af40ba0458614a0c8aa8317412ef`;
hidden reference `38d548284540a3ed8d71739d205a3502fe164497fff250a1e3b825d96201adcf`.
Source, retained image and all training label heights were inspected without recapture,
inference or training. Next: inventory native background styles in training sources and
propose fresh training-family coverage, preserving the manual-dot/native-body distinction.
