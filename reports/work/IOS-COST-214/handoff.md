# Actual ROI cost — October 6

Audited both fixed STYLE210 candidates through the existing validated request and
merge paths. No inference, retraining, role changes or metric/threshold tuning.
Report: `artifacts/audit01.json`; source `scripts/cost214.py`.

| Partition | Frames | Extra crop calls | Maximum/frame | No-crop frames | Identical-window redundancy |
|---|---:|---:|---:|---:|---:|
| Training fit |216|358|4|0|9|
| Page development |96|109|4|21|0|
| Retained combined |2400|686|4|1781|0|

Counts are identical across both candidates because proposals originate from the
same frozen Run022 outputs. Retained mean0.286 crops/frame;74.2%need none.
The historical44-window figure described dense-coverage diagnosis, not this pipeline.
Full-frame first-pass inference is additional and not counted as a crop.

Recorded control batch times: refinement32.754s,extra47.215s; treatment31.900s,
47.489s. These cover the recorded batch/export workflows and model loading; extra
timing includes reporting. Do not convert these into cold/warm production navigation
latency or assume GPU parallelism. Total decoded RGB workload:883,610,589bytes per
candidate across all partitions, not peak memory or resident GPU allocation.

Decision: exact-window reuse is not a meaningful retained-data win; a blanket crop
cap lacks a measured need and could damage recall. Prioritize model accuracy and
real end-to-end runtime measurement before adding a scheduler/cache architecture.
This does not qualify production deployment; other model gates still fail.

Verification: twofocused tests pass; real audit verifies all plans/predictions and
geometry in both arms. Offline Swift build/test exit0,140Swift Testing+14XCTest.
Initial audit failed before report creation because its output parent was absent;
fixed local parent creation and reran the CPU-only audit, retaining unchanged inputs.
No capture/training repeated. Existing unrelated edits preserved.
