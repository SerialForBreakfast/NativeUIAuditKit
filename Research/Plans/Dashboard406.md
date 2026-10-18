# DASHBOARD406 — pending job audit

Owner: Maximum-mini-NUIAK. Date: 2026-10-14.

## Findings

The maintainer approves `backlog405-native-failure-analysis`. The existing runner completes it in 0.321 s. Output hashes pass verification.

The remaining 24 jobs are unapproved. Of these, 22 also have changed registered code inputs.
Only `program384-d1-train43-v2` and `program384-d1-train44-v2` pass other current readiness checks.
Each control run has limits of 1,800 s and 2 GiB. This audit grants neither run approval.

| Group | Jobs | Blocking condition | Next action |
| --- | ---: | --- | --- |
| HCF375D training | 3 | Changed registered training and capture code | Reconcile successors and completed evidence before considering replacement |
| HCF376 controls | 9 | Changed registered training and capture code | Reconcile completed controls; do not repeat answered comparisons |
| HCF402 measurements | 6 | Changed `scripts/coverage_reports402.py` | Compare corrected successors before creating any replacement |
| TEMPLATE395 | 4 | Changed compiler and adapter inputs | Reuse qualified successors where they answer the same question |
| PROGRAM384 controls | 2 | Approval only in the current runtime check | Review scientific value and exact approval before execution |

Input identity checks stop at the first failure. Additional runtime failures may appear after that failure is resolved.
The audit checks every explicit pin separately. All 22 failures below concern existing files with changed hashes.
The JSON report preserves expected and current hashes. No registered specification changes.

## Exact jobs and changed inputs

### hcf375d-71-detector-train

Changed registered files:

- `scripts/hcf_study371.py`
- `scripts/hcf_compare371.py`
- `scripts/hcf_training375.py`
- `scripts/hcf_capture362.py`
- `scripts/generation352.py`
- `scripts/native343.py`
- `scripts/direct_tvos_capture.py`
- `scripts/train_focus_ring_detector.py`
- `scripts/train_yolo.py`

### hcf375d-71-detector-train-v2

Changed registered files:

- `scripts/hcf_study371.py`
- `scripts/hcf_compare371.py`
- `scripts/hcf_training375.py`
- `scripts/hcf_capture362.py`
- `scripts/generation352.py`
- `scripts/native343.py`
- `scripts/direct_tvos_capture.py`
- `scripts/train_focus_ring_detector.py`
- `scripts/train_yolo.py`

### hcf375d-71-detector-train-v2-usb

Changed registered files:

- `scripts/hcf_study371.py`
- `scripts/hcf_compare371.py`
- `scripts/hcf_training375.py`
- `scripts/hcf_capture362.py`
- `scripts/generation352.py`
- `scripts/native343.py`
- `scripts/direct_tvos_capture.py`
- `scripts/train_focus_ring_detector.py`
- `scripts/train_yolo.py`
- `scripts/usb_training386.py`

### hcf376-balanced-repeated-train-v1

Changed registered files:

- `scripts/hcf_study371.py`
- `scripts/hcf_compare371.py`
- `scripts/hcf_training375.py`
- `scripts/hcf_capture362.py`
- `scripts/generation352.py`
- `scripts/native343.py`
- `scripts/direct_tvos_capture.py`
- `scripts/train_focus_ring_detector.py`
- `scripts/train_yolo.py`
- `scripts/hcf_factor_train376.py`

### hcf376-balanced-repeated-train-v1-usb

Changed registered files:

- `scripts/hcf_study371.py`
- `scripts/hcf_compare371.py`
- `scripts/hcf_training375.py`
- `scripts/hcf_capture362.py`
- `scripts/generation352.py`
- `scripts/native343.py`
- `scripts/direct_tvos_capture.py`
- `scripts/train_focus_ring_detector.py`
- `scripts/train_yolo.py`
- `scripts/hcf_factor_train376.py`
- `scripts/usb_training386.py`

### hcf376-balanced-repeated-train-v1-usb2

Changed registered files:

- `scripts/hcf_study371.py`
- `scripts/hcf_compare371.py`
- `scripts/hcf_training375.py`
- `scripts/hcf_capture362.py`
- `scripts/generation352.py`
- `scripts/native343.py`
- `scripts/direct_tvos_capture.py`
- `scripts/train_focus_ring_detector.py`
- `scripts/train_yolo.py`
- `scripts/hcf_factor_train376.py`
- `scripts/usb_training386.py`

### hcf376-hcf-repeated-train-v1

Changed registered files:

- `scripts/hcf_study371.py`
- `scripts/hcf_compare371.py`
- `scripts/hcf_training375.py`
- `scripts/hcf_capture362.py`
- `scripts/generation352.py`
- `scripts/native343.py`
- `scripts/direct_tvos_capture.py`
- `scripts/train_focus_ring_detector.py`
- `scripts/train_yolo.py`
- `scripts/hcf_factor_train376.py`

### hcf376-hcf-repeated-train-v1-usb

Changed registered files:

- `scripts/hcf_study371.py`
- `scripts/hcf_compare371.py`
- `scripts/hcf_training375.py`
- `scripts/hcf_capture362.py`
- `scripts/generation352.py`
- `scripts/native343.py`
- `scripts/direct_tvos_capture.py`
- `scripts/train_focus_ring_detector.py`
- `scripts/train_yolo.py`
- `scripts/hcf_factor_train376.py`
- `scripts/usb_training386.py`

### hcf376-hcf-repeated-train-v1-usb2

Changed registered files:

- `scripts/hcf_study371.py`
- `scripts/hcf_compare371.py`
- `scripts/hcf_training375.py`
- `scripts/hcf_capture362.py`
- `scripts/generation352.py`
- `scripts/native343.py`
- `scripts/direct_tvos_capture.py`
- `scripts/train_focus_ring_detector.py`
- `scripts/train_yolo.py`
- `scripts/hcf_factor_train376.py`
- `scripts/usb_training386.py`

### hcf376-hcf-unique-train-v1

Changed registered files:

- `scripts/hcf_study371.py`
- `scripts/hcf_compare371.py`
- `scripts/hcf_training375.py`
- `scripts/hcf_capture362.py`
- `scripts/generation352.py`
- `scripts/native343.py`
- `scripts/direct_tvos_capture.py`
- `scripts/train_focus_ring_detector.py`
- `scripts/train_yolo.py`
- `scripts/hcf_factor_train376.py`

### hcf376-hcf-unique-train-v1-usb

Changed registered files:

- `scripts/hcf_study371.py`
- `scripts/hcf_compare371.py`
- `scripts/hcf_training375.py`
- `scripts/hcf_capture362.py`
- `scripts/generation352.py`
- `scripts/native343.py`
- `scripts/direct_tvos_capture.py`
- `scripts/train_focus_ring_detector.py`
- `scripts/train_yolo.py`
- `scripts/hcf_factor_train376.py`
- `scripts/usb_training386.py`

### hcf376-hcf-unique-train-v1-usb2

Changed registered files:

- `scripts/hcf_study371.py`
- `scripts/hcf_compare371.py`
- `scripts/hcf_training375.py`
- `scripts/hcf_capture362.py`
- `scripts/generation352.py`
- `scripts/native343.py`
- `scripts/direct_tvos_capture.py`
- `scripts/train_focus_ring_detector.py`
- `scripts/train_yolo.py`
- `scripts/hcf_factor_train376.py`
- `scripts/usb_training386.py`

### hcf402-measure-dark-background

Changed registered files:

- `scripts/coverage_reports402.py`

### hcf402-measure-diamond-decoration

Changed registered files:

- `scripts/coverage_reports402.py`

### hcf402-measure-edge-clearance

Changed registered files:

- `scripts/coverage_reports402.py`

### hcf402-measure-neighbor-spacing

Changed registered files:

- `scripts/coverage_reports402.py`

### hcf402-measure-small-decoration

Changed registered files:

- `scripts/coverage_reports402.py`

### hcf402-no-focus-mapping-r4

Changed registered files:

- `scripts/coverage_reports402.py`

### program384-d1-train43-v2

Approval is the only reported runtime blocker.

### program384-d1-train44-v2

Approval is the only reported runtime blocker.

### template395-01-inventory

Changed registered files:

- `scripts/hcf_templates395.py`
- `scripts/template_adapters395.py`
- `scripts/template_bridge395.py`

### template395-02-groups

Changed registered files:

- `scripts/hcf_templates395.py`
- `scripts/template_adapters395.py`
- `scripts/template_bridge395.py`

### template395-04-admission

Changed registered files:

- `scripts/hcf_templates395.py`
- `scripts/template_adapters395.py`
- `scripts/template_bridge395.py`
- `scripts/hcf_study371.py`

### template395-09-candidate

Changed registered files:

- `scripts/hcf_templates395.py`
- `scripts/template_adapters395.py`
- `scripts/template_bridge395.py`

## Dashboard behavior

- Ready means current readiness checks pass, including approval.
- Awaiting approval means approval is the only reported blocker.
- Blocked means a requirement or readiness check fails.
- Pending is a filter for work that has not started.
- Unchecked means the display lacks a readiness result. It never receives a green badge.
- Runner active does not mean a job is running.

The presentation layer leaves execution state and immutable specifications unchanged.
The readiness checker remains authoritative. The runner repeats checks before execution.

## Evidence

[Exact audit](../../reports/work/DASHBOARD406/pending-audit.json).
All 77 dashboard and description tests pass in 48.878 s.
All 174 offline Swift tests pass in 52.714 s.
The first software test attempt fails because its fixture uses the obsolete approval schema. The corrected fixture passes.
The first audit save fails because its output directory is absent. The corrected report setup passes.
Both initial failure logs remain available where produced; the audit save failure is recorded in this report.

The server restarts under the idle queue lock. Its existing resume-approved policy and task priority remain unchanged.
Live browser verification shows 0 ready, 2 awaiting approval, 73 blocked, and 710 completed jobs.
The approval filter displays only the 2 PROGRAM384 controls. Blocked jobs have disabled selection and visible reasons.
The header displays `Runner active — waiting` when no job runs.
The initial page request exceeds the browser navigation timeout. The page subsequently loads and passes DOM verification.

Logs: `.build/dashboard406-tests-final.log`, `.build/dashboard406-swift.log`, and `.build/dashboard406-server.log`.
The estimate is 20–40 min. Total task elapsed time was not instrumented; individual checks have measured times above.

