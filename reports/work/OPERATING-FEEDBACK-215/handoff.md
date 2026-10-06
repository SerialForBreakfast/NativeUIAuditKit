# Operating-case feedback — October 6

Completed a local CPU-only correction to the accepted worker198 paired report's
legacy export-floor ranking. All585cases, support/count sums, per-class totals and
ROI-to-parent mappings reconcile. No new predictions, training, data admission or
model selection. Source hashes and full cases are retained in `artifacts/report01.json`.

Largest **treatment operating** categories at confidence0.25/IoU0.5:

| Role/partition | Category | Count | Relevant denominator | Affected parent frames |
|---|---|---:|---:|---:|
| Retained combined | unmatched FP |1431|2677 operating detections|387|
| Retained combined | localization FN |326|1524 GT boxes|320|
| Retained combined | duplicate FP |166|2677 operating detections|144|
| Training fit | duplicate FP |153|676 operating detections|107|
| Training fit | unmatched FP |101|676 operating detections|62|

Full top ten includes deterministic ROI IDs, original frame IDs and crop windows.
For example, combined-1562 traces to test/images/img_008583.png, window295,395,885,985;
nine unmatched operating FPs. This is raw ROI output, not shipped full-frame output.
Counts do not constitute population prevalence across mixed roles; no ratio blends
training/development/retained sets. Geometric categories are not causal diagnoses.

The actionable low-confidence queue excludes already-matched targets:30fit and29
retained ROIs have unmatched targets with matching below-threshold candidates; page
development has0. These are hypotheses for diagnosis, not permission to lower thresholds.

Regression visibility: retained toggle FP139→166; tabBar44→47; progressView0→4.
Page-development imageView FP17→26, support0: AP stays unavailable, FP remains meaningful.
Fit listRow FP73→114 and one lost toggle TP(19→18). Overall improvements must not hide
these tradeoffs. Existing page-only composition preserves non-page first-pass outputs;
do not mistake raw-ROI errors for regressions in that composed deployment path.

Three focused tests cover operating-floor separation, deterministic parent links,
matched-target exclusion, corrupt membership/counts and class-regression reporting.
Actual report replay completed; offline Swift build/tests also required at handoff.
Next: use the same operating contract for future worker feedback, not rerun198-D.
Current213training remains unchanged. Native tvOS top-ten work still requires qualified
source-bound captures; this iOS report does not close SHADOW-TOPTEN.

Offline Swift build/test exit0:140Swift Testing+14XCTest; logs
`.build/operating215-build.log` and `.build/operating215-test.log`.
Feedback published/read back at
`nuiak/responses/nuiak-20261006-worker215-operating-feedback.json`,2087bytes,
SHA256 `f6c311ba4c5ffc9f117a4075dc3a8e61742662f3bc9cb1122254bdba89b1c865`.
Acknowledgment remains separate. No rerun requested; worker213control completion
is peer-reported10epochs/1430batches/89updates, treatment still pending at this handoff.
