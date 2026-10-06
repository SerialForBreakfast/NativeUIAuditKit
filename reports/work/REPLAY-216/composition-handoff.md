# Consumer-level retention check — October6

Completed the frozen extra-donor comparison with existing predictions, no inference.
Fixed Run022fullframe,028refinement and211alias rule; only extra pageControl donor
varies. Existing merge validates membership/window geometry; all non-page detections
and metrics remain unchanged. Both candidates pass fit216TP/4FP before retained work.

| Partition | Reference028 TP/FP | Control029 TP/FP | Treatment030 TP/FP |
|---|---:|---:|---:|
| Fit216 |216/4|216/4|216/4|
| Development96 |75/4|72/5|69/8|
| Retained600targets/2400frames |543/7|513/7|437/7|

Reject030as an extra-donor replacement:76fewer retained hits than its matched029
control and106fewer than reference028. The reference has different training/backend
history; it is a replacement benchmark, not a controlled causal experiment. All arms
retain inherited non-page gate failures; candidate arms also fail development pageFP.
Artwork recognition gains do not establish retention or qualify a production model.

`artifacts/composition213-01.json` SHA
`5c0b7855cb64bc4ae7c20188b0ed8d8867aa1a3d70799f951dc52481820e52f5`.
Actual CLI: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python
scripts/compose_worker213.py reports/work/REPLAY-216/artifacts/composition213-01.json`,
exit0. Reuses existing merges, score and gate assessment without new thresholds.

## Source-pin compatibility repair

The prior diagnostic matcher extraction changed eval_run013's source hash, invalidating
historical sealed callers despite identical scores. Restored that file exactly (no Git
diff);45composition references now validate through the actual `collect` entrypoint.
Diagnostic matching lives locally in diagnose_replay216 and must reconcile every class
to the unchanged scorer. Regenerated scale-diagnosis02; all semantic fields exactly
equal diagnosis01 (only diagnostic source hash differs). Old evidence retained.
Earlier claims of a shared matcher describe the superseded implementation, not current
code. No old manifest was resealed and no source verification was bypassed.

53focused tests pass, including actual no-donor merge, non-page mutation rejection,
missing membership and output collision, plus existing composition/alias/scorer suites.
Offline Swift build/test evidence: `.build/composition213-build.log` and
`.build/composition213-swift.log`;140Swift Testing+14XCTest passed. No Git writes.

Software and retained integration checks passed; existing data roles unchanged;
model replacement rejected.216worker acknowledgment remains pending at latest check.
Next substantial work: independent031/032 intake, raw+composed retention comparison,
then decide a new experiment only from those results.205/206native focus remains
waiting for source-bound, geometry-qualified producer evidence, not more artwork.
Actionable feedback published/read back:
`nuiak/responses/nuiak-20261006-worker216-composition-feedback.json`,1828bytes,
SHA `278ffd8d5bb914e9ed9724fd9b61573a45d83b438201b2a127966da908fad0ab`.
Peer acknowledgment is separate and still pending; no extra job requested.
