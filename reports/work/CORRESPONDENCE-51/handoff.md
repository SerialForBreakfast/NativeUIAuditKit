# Correspondence51 — controlled replay complete

October3,2026. No capture, training, export, default replacement or Git write.
Preserved prior49/50 changes and all raw evidence. One fixed experiment, no sweep.

## Decision

Do not adopt `wide-template-v1`: peripheral-text retention improves unchanged rows,
but native positive identity remains0/12 and wrong matches increase. Keep opt-in
diagnostics reproducible; default70%/256px tracker remains unchanged. Experimental
reports are explicitly rejected by the default temporal learner, including nested
Settings baseline tracker metadata. No native positive examples became trainable.

| Evidence | Original | Wide90%/512px |
|---|---:|---:|
| Reference correct identity |43|89|
| Reference wrong identity |5|10|
| Reference tracking abstentions |98|46|
| Reference matched without truth |10|11|
| Reference arrival/departure correct |0/12|0/12|
| Reference guarded correct/wrong |15/0|30/0|
| Settings correct identity |45|48|
| Settings wrong identity |0|0|
| Settings guarded correct/wrong |33/0|36/0|
| Reference replay seconds |35.884|43.124|
| Settings replay seconds |18.706|24.364|

Same24reference actions/156controls and5Settings actions/50controls;120and48have
scorable truth. Reference36appearance-only cases remain excluded (12captures).
Native wrong departure matches3→6; arrival wrong0→1. No whole-screen qualification.
Scoring uses after truth to reject wrong matches; this is not a runtime safety gate.
Runtime comparisons reuse historical baselines, not controlled system-load benchmarks.

## Evidence and acceptance

- Actual audit CLI: `scripts/focus_corrected_transition_audit.py --reference-delivery
  --tracker wide-template-v1 --root reports/work/TTR-UPDATE-43/received/ttr-rich-reference36-20261002-r1
  --output reports/work/CORRESPONDENCE-51/wide-replay` — exit0,24diagnostic pairs,
  all581manifest files verified before/after.
- Actual Settings CLI: `scripts/settings_focus_stability.py --semantics
  reports/work/FOCUS-RECORDED-STRUCTURAL-22/artifacts/settings-ocr/semantics.json
  --tracker wide-template-v1 --output reports/work/CORRESPONDENCE-51/settings-wide` — exit0.
- Comparison CLI `scripts/focus_correspondence_comparison.py --baseline <sealed-original>
  --candidate <sealed-replay> --output <new-json>` — both exit0. Exact control/label/
  endpoint membership and data roles checked; no native after boxes enter prediction.
- New offline tests cover peripheral text, duplicate texture, low texture, viewport,
  fixed crop dimensions, wrong-match accounting, changed truth/pixels/roles/membership,
  prediction boundary and experimental-feature admission rejection.
-101Python tests pass1.818s; `.build/correspondence51-python-tests.log`.
  Offline Swift build exit0(2.79s),14XCTest+120SwiftTesting pass;
  `.build/correspondence51-swift-{build,test}.log`. No model-performance claim from tests.
- Settings output predates the added top-level tracker metadata; its sealed nested
  comparison already records `wide-template-v1`, which admission now checks. Original
  evidence retained rather than rewriting or needlessly replaying it.

SHA256:

- reference comparison: `601a2bc335c97ca8e242324c4458f5a12ea688c8fc30c12a46845a9562878841`
- Settings comparison: `e5dd6115c149f733dd24803ff07947f5bf5b23b63a92ef6ce417bc4627fab8cf`
- reference replay: `73244e02e2e431fb9acccd258e150283d4a639bbd1a27d4450cb44e9c9423853`
- Settings replay: `82a1df4279e0efd1af980091547cdb5e6284a76a8f339db50b64d8f1fe86d2d4`

## Independent outcomes and next tranche

Software verified: passed. Data: retained calibration/development only, no new
training admission. Integration: retained consumer replay passed; live TTR readiness
not reassessed. Model gates: not assessed, no candidate trained.

Next: one pixel-only feature-consensus correspondence experiment covering native
growth/scroll and repeated rows, plus matched Settings regression and training-feature
readiness. Preserve crop scale and score identity separately. TTR independently
resolves50cleanup; no duplicate producer request or unchanged live retry. Once safe,
resume authorized8cases, validate exact new membership and fit the30epoch temporal
head if all states have features. Existing calibration evidence stays calibration.

Coordination: verified `smb://sillycon.local/SharedStatusFile` mount, published
`/Volumes/SharedStatusFile/nuiak/status.yaml` packet `CORRESPONDENCE-51` at08:08:51UTC,
validated duplicate-free YAML and read back. Parsed unrelated status SHA256 stayed
`502e989ee0a3696ae6d42a77e629c927840f2289dbf333c2ba3f3be9556b0601`.
Existing request `nuiak-20261003-transition50-cleanup` preserved; no new request,
peer acknowledgment or live readiness claim. No external wait this tranche.
