# IOS-ROI-194 — Run025 completed; retain as experimental

2026-10-05 / Codex. Started from clean `f8514fc`. No Git writes, capture, TTR
operations, CoreML export or promotion. Run022 and shipped models are unchanged.

| Outcome | Result |
|---|---|
| Software verified | 17 focused tests; offline Swift build and 142 tests passed |
| Data eligible | Existing 802 unique crops from 216 admitted training images; no role changes |
| Local integration qualified | All 568 crop outputs validated and merged into all 2,712 original records |
| Model gate passed | No: eight of 14 gates fail; retained fine geometry also regresses |

## Measured outcome

Run025 finished 10 epochs and exactly 130 planned optimizer updates in 2,731.612s
(45.5 minutes), PID76719, exit0. Fresh Run022-last initialization, 640 input,
batch8, AdamW1e-4, warmup.25, fixed terminal checkpoint; in-sample monitoring only.
This is not equal compute to Run022's69 updates and not independent final qualification.

| Page-control result | Run022 | ROI pipeline |
|---|---:|---:|
| Training-fit true positives /216 |185|199|
| Training-fit false positives |38|24|
| Trailing fit hits /72 |45|59|
| Fit AP50:95 |0.474462|0.763265|
| Development TP / FP |58 /14|58 /14|
| Development AP50:95 |0.321576|0.380124|
| Retained TP / FP |249 /24|249 /24|
| Retained page AP50:95 |0.494261|0.461604|

All 14 recovered fit cases were prior localization misses; all185 prior hits remain.
Leading/center remain68/72 and72/72. Count-based ceilings are68/72/59: this candidate
reaches the optimistic fit ceiling of its fixed proposals. It cannot repair17fit
images without eligible proposals. Development ceiling58TP/≥14FP cannot satisfy
59TP/≤4FP, and five non-page gates are immutable failures. This ceiling should have
been quantified before training; the lesson is recorded in BestPractices.

Retained aggregate AP50 stays0.899967; aggregate AP50:95 changes0.858373→0.857513.
Every non-page class metric is exactly unchanged. Better fit/development localization
does not establish transfer: retained page AP90 also falls0.008497→0.000929.
No promotion or automatic extra epochs. Next195diagnoses source/size transfer and
training-only coverage before proposing another comparison.

## Integration and cost

Actual strict exporter produced223fit,72development and273retained crop results in
33.268s including export work. Merge validates source artifacts independently,
crop IDs, proposal indices, exact windows/dimensions, successful inference and
conservation. No-proposal originals remain17/38/2148, respectively. Crop labels
never choose evaluation windows. Derived results have their own format and both
model references; they are not misrepresented as a single-model inference export.

Fixed-rule diagnostics count179/48/213 replaced boxes. Other proposals remain
unchanged through missing detections, ambiguous/shared matches or failed overlap.
The evaluation `accounting.changedBoxes` field counts changed original-image rows,
not individual boxes; use diagnosis.json for box-level totals.

Warm batch-one MPS diagnostic: proposal-frame median105.46ms total,56.33ms added;
no-proposal median47.02ms total. First cold pipeline frame1.194s; model loading
separately65.6ms. Sample is source-ordered8proposal+8no-proposal frames, selected
without labels; not population-weighted or CoreML/device qualification. CPU scoring
ran concurrently, so report these as local diagnostic timings, not controlled
latency guarantees. Both raw passes and stage timings are retained.

## Evidence and reproduction

All commands used resident `.venv-yolo/bin/python`, `PYTHONDONTWRITEBYTECODE=1`;
inference/evaluation also set `YOLO_OFFLINE=true`. No dependencies changed.

- `scripts/roi194.py prepare`: source/data/dependency pins and isolated output checks.
  Initial preliminary protocol retained; attempt02corrected the unexecuted scoring
  adapter before training. No candidate retry.
- `scripts/roi194.py train`: exit0; all10 finite CSV epochs, exact saved args and
  optimizer schedule verified before model use.
- `scripts/roi194.py infer` and `report`: exit0; actual prediction/merge/scoring paths.
- `scripts/roi194_ceiling.py`, `roi194_diagnose.py`, `roi194_latency.py`: exit0.
- `python -m unittest discover -s scripts -p 'test_roi19*.py'`:17passed; source
  conservation, missing/extra/duplicate outputs, bad geometry, failed inference,
  no-proposal fallback, coordinate mapping and alias-label conflicts.
- Required offline Swift build/test with known scoped host access: exit0,142tests.
  Logs `.build/roi194-build.log`, `.build/roi194-test.log`. Final `git diff --check` passed.

Sealed machine reports under `artifacts/attempt02/`: protocol, execution, completion,
inference, evaluation, ceiling, diagnosis, latency and all three derived exports.
Candidate outputs are about77MB after normal trainer stripping; reports about17MB,
within budget. Raw outputs remain ignored; only this summary and source are reviewable.

- Protocol file SHA256: `b846b6115e834b2f06b91b9db4fa10a13ffc272aeab35ab3f1c7326f846b0c6c`
- Fixed-last checkpoint: `bf26cec4daf2f194066a832f1ffc7601d5fe6639102a77ca241decf4c83aff3b`
- Evaluation seal: `cfd6577bf85a81a5640f0ba6793cd2cbbdd5caa61b4647821ecf4582fe8b95a5`
- Latency seal: `5b8c8941df97921c32da187c26f226b39949714ffebc1b87692b92e9e8e784d2`

Assigned tranche complete for review. SMB coordination is not applicable: this local
iOS experiment changes no TTR interface/model delivery or outstanding peer action.
