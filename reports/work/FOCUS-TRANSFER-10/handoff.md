# FOCUS-TRANSFER-10 handoff — complete for review

Assigned: failure audit, isolated emphasis and input experiments, unchanged evaluation,
clear keep/reject decisions and actionable TTR feedback. All included local work
completed; no request for another routine launch approval or human annotation.

| Acceptance | Evidence |
|---|---|
| Compare real failures with synthetic inputs | `audit.md`, ten inspected diagnostic sheets and retained-pixel `artifacts/audit/audit.json` |
| One weight-only test | FDR033100updates; unchanged nonfixture/fixture-label budgets and identical initial predictions; reject4/12artwork with29FP |
| One evidence-selected input test | Native aspect-fit, all1895production inputs replayed exactly; FDR034100updates, original weights; reject7/12artwork with68FP and0/3buttons |
| Same evaluation and prescribed acceptance |333records unchanged;30saved evaluations replay exactly; no eligible/strict-passing update |
| Real caller plus adversarial tests | Both arms wired into existing trainer; actual CLI2positive/6negative checks;46Python tests |
| Repository checks | `swift-build-host.log`, `swift-test.log`: offline build clean;134tests pass; `git diff --check` clean |
| Bounded execution | `artifacts/output-budget.json`:451.909model seconds, about326MB versus1800seconds/2GiB |
| Actionable producer feedback | `ttr-feedback.md`, published coverage request and owned shared packet; readback verified, peer acknowledgment pending |

Software **passed**. Existing data eligibility **passed**, no new admission.
Integration of retained data/native preprocessing/actual training CLI **passed**;
new live TTR generation **not run/not qualified**. Model improvement gate **failed**.
No export, promotion, download, device operation, external dataset write or Git write.
Original captures/annotations andFDR021preserved. Generated outputs remain ignored.

Implementation reuses the native cropper, existing prefix encoder, partial model,
weighted trainer and evaluator; new `scripts/focus_transfer_experiment.py` binds
only the two assigned experimental changes. No parallel training implementation.
Results and next meaningful decisions: [results.md](results.md). Producer follow-up
is a capability/coverage map before structurally different generation, not another
unchanged training run. This follow-up is not required to complete this experiment.
