# IOS-ROI-195 — transfer diagnosed; training-only coverage proposed

2026-10-05 / Codex. Preserved all194changes and artifacts. No Git writes,
inference, training, capture, export, promotion or role changes. SMB not applicable:
local iOS diagnosis does not change TTR's next action.

All2712original image records and cached predictions reconcile exactly with194.
Diagnostic associations fix each prediction's original overlapping truth; these
are not AP matching or independent examples. Actual audit20.575s, no external wait.

| Changed page boxes | Improved | Regressed | Median height/truth before→after |
|---|---:|---:|---:|
| KitchenSink fit |78|0|1.483→1.016|
| UIKitControls fit |80|21|1.105→.996|
| Native development (family unknown) |36|12|1.321→.890|
| GalleryPage retained |8|148|1.107→.780|
| OnboardingPage retained |56|1|1.263→.837|

Gallery truth heights20–30pixels versus fit17–23pixels; this supports a coverage
hypothesis, not proof. Width/center and original-image records remain in sealed
diagnosis. Missing family provenance stays unknown. No labels were corrected using
candidate predictions. Unchanged/no-proposal examples remain in accounting.

Training audit:1830page-positive frames:330KitchenSink,834UIKitControls,
266MediaCardGrid,400ProgressActivity. Proposed24additional frames/family,96total,
74distinctgroups (12/14/24/24 respectively). All96page annotations are contained
in the source image, with no recorded occlusion. That is not visual confirmation
or crop admission: all-class clipping and full native-evaluation ancestry remain
required during196materialization. MediaCardGrid and ProgressActivity heights20–30
pixels provide source diversity absent from193's crop parents. Renderer inspection
shows dot-group capture before padding; historical bytes retain original lineage.

## Evidence and verification

- `scripts/roi195.py`: strict cached merge reproduction, family joins by image+label
  hashes, conservation, geometry/crossings, full training-label audit and bounded selection.
- `scripts/roi195_geometry.py`: actual selected sidecar geometry and support audit.
- Focused `test_roi19*.py`:23tests,exit0. Offline Swift build and142tests,exit0;
  project-local `.build/roi195-{build,test}.log`. No new model result.
- Diagnosis seal `5f230baa55fdeffeb08ce32816de1c1ddbb3ab0f16ea2e935ffff38f4ab993d9`.
- Proposal seal `bf627d97217e22a7fdd1849b168767f5d8b75f397cd5597d6907a87b2ca4b2bc`.
- Raw sealed artifacts under ignored `reports/work/IOS-ROI-195/artifacts/`;
  no image copies. Prior194evidence unchanged.

Software verified; source proposal uses admitted train roles but new crop membership
is not yet qualified; cached local integration verified; model gates unchanged/failed.
Next substantial tranche196: materialize/qualify coverage, register one comparison,
and independently diagnose proposal recall. Fixed proposals still cap development
at58TP/≥14FP, and non-page gates cannot change through geometry-only refinement.
