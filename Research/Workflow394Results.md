# WORKFLOW394 — measured template and DVC comparison

Date: 2026-10-14.
Decision: Keep the existing queue and qualify templates incrementally.
DVC adoption remains a separate review decision.

## What works

The registry defines 14 versioned template contracts.
Three bounded bindings run: existing-crop preparation, crop inference, and measured reporting.
The remaining 11 contracts reject assumptions of executable support. Their catalog entries name the missing implementation.
This is not completion of all HCF templates or HCF389.

A description supplies 8 fields: version, identifier, owner, question, decision, manifest, model, and batch size.
The compiler checks input hashes and produces 3 immutable dependent jobs.
Registration neither approves nor starts execution.
Duplicate descriptions reuse registrations. Conflicting descriptions fail.
Interrupted registration resumes without duplicate jobs.

## Measured comparison

Both arms use the same 16 retained development crops and fixed checkpoint.
All cases belong to 1 group. This sample tests execution, not deployment accuracy.
The comparison does not use final-audit data or start training.

| Measurement | Result |
| --- | --- |
| Matched repetitions | 3 |
| Queue jobs completed | 9 |
| DVC jobs completed | 3 |
| Reports across both arms | Identical bytes in every repetition |
| Second description | Batch size changes from 4 to 2 without new adapter code |
| Second-description results | Identical decisions and scores |
| Queue function time, summed per repetition | 1.102–1.715 s |
| DVC first execution | 1.718–1.799 s |
| DVC unchanged-output reuse | 0.289–0.295 s |

These timings have different boundaries. Queue function time excludes dispatch and process startup.
DVC time includes its orchestration and stage processes, but excludes installation and initialization.
OS caches remain uncontrolled. These numbers do not establish a throughput winner.
Peak memory, authoring effort, and a 30% maintenance reduction remain unmeasured.

The approved isolated environment uses DVC 3.67.1. Dependency checks pass.
The installation record preserves dependency versions and download hashes.
Training environments remain unchanged. No cloud storage or new service is configured.

## Positive and negative checks

- All 14 contracts pass required-field checks and reject missing fields or unknown versions.
- Actual queue execution completes preparation and reports an invalid checkpoint as failed.
- Missing and changed input files fail validation.
- DVC rejects a changed input against its declared hash.
- Invalid scoring produces no downstream report.
- DVC restores missing downstream outputs without changing verified preparation.
- Both arms resume after their test caller stops at the completed preparation boundary.
- Duplicate execution requests do not create new queue attempts.
- A repeated DVC request reuses unchanged outputs.
- RGB conversion matches the existing trainer for RGBA crops.

The first pilot rejects RGBA crops incorrectly. Its failed attempts remain preserved.
The corrected pilot uses the trainer's RGB conversion without changing original images.
Recovery tests cover registration, caller restart, and completed stage outputs. They do not qualify interrupted training resume.
The first restart driver incorrectly expects one dispatch pass to revisit newly ready jobs.
The corrected driver uses dependency order. Both attempts remain preserved; the live runner stays unchanged.

Validation passes 54 focused tests, 14 XCTest checks, and 174 Swift Testing checks.
The isolated test evidence uses about 61 MB. The DVC environment uses about 154 MB.

## Template limits

| Templates | Current support | Next required work |
| --- | --- | --- |
| T05, T07, T08 | Bounded development-crop workflow | Add measured selection comparisons and larger admitted memberships |
| T01, T02, T09 | Named contracts only | Wrap evidence, group checks, and candidate review |
| T03, T04 | Named contracts only | Wrap qualified native capture and label checks |
| T06 | Named contract only | Wrap trainers and test complete checkpoint resume |
| T10, T11, T12 | Named contracts only | Add export authority to the queue, actual Vision parity, and runtime checks |
| T13, T14 | Named contracts only | Validate packaging and returned TTR inference receipts |

The 16-case limit belongs to this qualification binding. It is not a limit on the HCF study.
Current bindings do not support audit data, proposal selection, model promotion, or navigation authority.
Contract checks alone do not qualify the remaining adapters.

## Recommendation

Keep small descriptions and shared adapters. Keep execution ownership in the existing queue.
DVC supplies working caching and dependency tracking, but does not replace label checks, model checks, or execution approvals.
Do not migrate active experiments based on this small comparison.
Next, implement T01/T02/T09 and the export/parity branch using retained HCF evidence.
Keep Standard detection unchanged and HCF optional.

## Local evidence

Ignored evidence lives under `reports/work/WORKFLOW394/`.
It includes installation records, test logs, immutable pilot queues, case reports, failure receipts, and `qualification.json`.
`second-description.json` records the independent reuse check.
`process-restart.json` and `dvc-process-restart.json` record recovery after caller termination.
No original data, active queue specifications, or production models change.
