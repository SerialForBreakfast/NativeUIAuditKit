# FLOW479 — Reject regressions and repair automatic follow-ups

Date: 2026-10-20.
Owner: Maximum-mini-NUIAK.

## Model decision

Neither native-only iOS correction replaces Run 013.

| Candidate | Completed epochs | Training time | Gained detections | Lost retained detections |
|---|---:|---:|---:|---:|
| Controls | 30 | 165.77 s | 13 | 69 |
| Toggles | 30 | 145.72 s | 8 | 316 |

Each candidate uses the same 6 retained development evaluation sets as its control.
These counts describe label detections, not independent scenes or release accuracy.
Unmatched predictions are not verified false positives.
These detector reports do not establish focus selection or no-focus accuracy.
The shipped models and Standard behavior remain unchanged.

The next comparison should test preservation of previous training coverage.
Do not repeat native-only training with more epochs.
First use the approved class-agnostic diagnostics to separate classification losses from missing boxes.
Then qualify a rehearsal membership containing eligible original training examples and the new native examples.
Do not use retained evaluation frames for rehearsal.
Compare against the completed native-only candidate without repeating it.

## Reporting repairs

The original reports fail because they declare a request file but do not read it.
The repaired worker reads and validates that pinned request.
It also checks the required number of comparisons.

The first reporting successor exposes a second contract defect.
Its conditional result lacks the required reason field.
The worker now supplies that field.
The regression test passes the output through the runner's condition validator.
Explicit successors preserve every prior attempt.
Neither repair repeats training or scoring.

The final report jobs are `ios479r-controls-decision` and `ios479r-toggles-decision`.
Each has 6 conditional class-agnostic diagnostics.
The diagnostics execute only for a contradicted result.
The controls decision completes and automatically releases its diagnostics.
Five controls diagnostics complete at this check.
The remaining diagnostics stay with the runner.

## No-focus capture review

The capture contains both expected frames.
The final HCF check stops at the evidence budget before sending input.
Standard restoration succeeds and records HCF as its original setting.
The original failed receipt remains unchanged.

The queued evidence-only review checks that exact failure and the successful restoration observation.
It also checks membership, image hashes, original profile, and native admission requirements.
Any uncertain observation rejects the review.
The review performs no navigation or capture.
Eight unchanged comparisons depend on its success.
The review does not admit training data or promote a model.

## Scheduler bottleneck

The existing scheduler calls full state verification for historical completed jobs during each scan.
This includes reading and hashing their output artifacts.
The prepared filter skips jobs with an existing attempt before full readiness checks.
Normal execution starts only unstarted pending jobs.
Retries still require their existing lifecycle or an explicit successor.

The measured filter processes 2,286 approved records in 0.055 s.
It returns 428 unstarted records, not 428 ready jobs.
This measurement does not establish overall dispatch latency.
The existing readiness, approval, dependency, and execution checks remain unchanged.

The dashboard loads this change after the approved reload on 2026-10-20 at 20:17 UTC.
Both reloads reach an idle boundary without cancelling an experiment.
The second reload preserves the existing B405-220 and B405-124 priority settings.
Continuous execution resumes with approved jobs. Live dispatch latency remains unmeasured.

## Evidence

Detailed receipts remain in ignored local records under `reports/work/REPORT479`.
The report and diagnostic jobs retain case-linked comparison evidence.
The offline Swift build passes.
All 177 serial Swift tests pass in 52.82 s.
Focused tests cover report pins, comparison counts, condition validity, zero-input recovery, and dispatch filtering.
The combined focused and dashboard run passes 93 tests in 50.84 s.

The four-week program remains in [ResearchProgram478](Plans/ResearchProgram478.md).
Multi-day ready capacity remains unmet.
