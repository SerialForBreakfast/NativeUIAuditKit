# Correspondence52 — feature comparison and motion diagnosis

October3,2026. Preserved previous49–51dirty changes and raw evidence. No live target
operation, model fitting, data admission, export, promotion or Git writes.

| Outcome | Result |
|---|---|
| Software verified |108Python tests and134Swift tests pass; actual replay CLIs exit0|
| Data eligible |Existing development/calibration roles unchanged; no new training data|
| Integration qualified |Retained pixel/crop intake passed; live TTR not reassessed|
| Model gates |Not assessed; no trained candidate/default replacement|

## Delivered and decision

Opt-in `feature-consensus-v1` is integrated into the existing reference/Settings
entrypoints. Gradient ORB descriptors use mutual distinct matching and bounded
translation consensus. It does not invent template correlation values; experimental
reports remain barred from the default measurement learner. Production16%/256px
cropping stays unchanged, with equal-size windows and explicit clipping rejection.

| Metric | Original | Feature candidate |
|---|---:|---:|
| Reference correct identities |43|86|
| Reference wrong identities |5|0|
| Reference tracking abstentions |98|65|
| Reference matched without truth |10|5|
| Reference arrival/departure correct |0/12|0/12|
| Reference guarded correct/wrong |15/0|6/0|
| Settings correct identities |45|45|
| Settings wrong identities |0|0|
| Settings departure correct |2/2|0/2|
| Settings arrival correct |2/2|2/2|
| Settings guarded correct/wrong |33/0|37/0|

Same24reference actions/156controls and5Settings actions/50controls,120/48scorable.
Do not adopt: aggregate Settings improvement conceals losing departures; native
positives remain unavailable. Reference replay34.960s, Settings23.145s; historical
baseline times35.884s/18.706s are not controlled throughput measurements.

## Additional diagnosis

Independently inspected one guide before/after pair and quantified all12scorable
native positives using the same pixel matcher. Six boxes contain at least6matches
near zero motion and6near native scrolling motion. Native center movement is
[0,-162]px. Fixed textured artwork remains in place behind scrolling guide rows;
the control box contains multiple visual layers. This supports, but does not prove
for every failure, a single-motion assumption problem. Other positives have weak
native-motion matches; no universal root cause is claimed.

After-state geometry enters only diagnostic scoring after pixel matches are fixed.
The diagnostic replays and exactly checks all12tracking results against the sealed
candidate after the feature-helper extraction; no changed prediction was hidden.
An initial diagnostic write failed on a NumPy integer before creating the output;
fixed native-integer serialization and added a regression test, then reran successfully.

## Reproduction and evidence

All Python commands use `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python`.

- `scripts/focus_corrected_transition_audit.py --reference-delivery --tracker
  feature-consensus-v1 --root reports/work/TTR-UPDATE-43/received/ttr-rich-reference36-20261002-r1
  --output reports/work/CORRESPONDENCE-52/reference-feature` — exit0.
- `scripts/settings_focus_stability.py --semantics
  reports/work/FOCUS-RECORDED-STRUCTURAL-22/artifacts/settings-ocr/semantics.json
  --tracker feature-consensus-v1 --output reports/work/CORRESPONDENCE-52/settings-feature` — exit0.
- Existing `focus_correspondence_comparison.py` compares sealed originals against
  these reports, identical inputs/truth/roles required; both CLI exits0.
- `scripts/focus_motion_diagnostics.py --report
  reports/work/CORRESPONDENCE-52/reference-feature/audit.json --root <same-source-root>
  --output reports/work/CORRESPONDENCE-52/motion-diagnostics.json` — corrected run exit0.
- Tests: `PYTHONPATH=scripts ... -m unittest test_focus_feature52 test_focus_correspondence51
  test_focus_transition_verifier test_focus_recorded_comparison test_settings_focus_stability
  test_focus_corrected_transition_audit test_focus_transition_learning test_reference_transition50`
  —108pass,1.886s. Log `.build/correspondence52-python-tests.log`.
- Offline Swift build2.22s,14XCTest+120SwiftTesting pass. Project-local49caches reused;
  `.build/correspondence52-swift-{build,test}.log`. No repeated full package checks.

SHA256:

- reference comparison `fdf4bc92573725f9e0dc4e37ae057cadff2bfcbf9470d58a4a1b2ab953b5158a`
- Settings comparison `f1ce7be0a3623835f0ac4b1e7698fd0e01f15a285775c035c386ef6ec1263e1c`
- motion diagnosis `670880983941661e18bd7f6b97d9bc257d2e141a02be025fb2d485e420661d20`
- reference replay `0cbfc25c278ac3a0b1ec6b45db58a551e83bd8258f0720354da740e68b1bbd4e`
- Settings replay `6eb8c49913179208602927ee3e898842b9bea3bccfe54e8b7782c1548d41f426`

## Next substantial tranche

Specify/integrate a direct paired-image baseline so valid labels do not depend on
successful tracking. Define after boxes/identities as targets only, freeze exact
training/development membership, and compare against fixed measurement baselines.
New encoder/backbone execution must be explicitly included in the approved experiment.
Obtain no-scroll focus-switch and scroll-without-switch coverage alongside—not
instead of—the layered examples. Existing50cleanup blocks live target reuse, not
local paired-model work. No unchanged capture retry or calibration relabeling.

Coordination: verified expected SMB mount; published/read back packet52in
`/Volumes/SharedStatusFile/nuiak/status.yaml` at14:13:18UTC. Duplicate-free YAML;
unrelated parsed content preserved at SHA256
`1c2b18f3d701b6269188d0f4d602764be13ed1b9d2c2d0218470d104dd18a9bc`.
Peer snapshot10:03:01UTC contained no matching transition50cleanup acknowledgment
in inspected packet/acknowledgment fields; publication is not peer receipt. No
device availability or repair success inferred from stale/missing coordination.
