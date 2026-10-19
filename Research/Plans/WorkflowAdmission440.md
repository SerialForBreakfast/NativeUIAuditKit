# WORKFLOW440 — Campaign preflight and measured admission costs

Date: 2026-10-18. Owner: Maximum-mini-NUIAK.

## Delivered behavior

`workflow_admission440.py` checks a compiled campaign without approving or dispatching jobs.
`workflow_campaign439.admit` calls it before publishing the first specification.
Missing training records and insufficient storage therefore fail before partial publication.
Approval and dispatch still repeat their authoritative checks afterward.
Preflight is a snapshot, not a reservation or approval.

Checks cover specification identities, source inputs, immutable conflicts, revocations, training prerequisites, and output storage.
They also cover dependency cycles, changed producer identities, and completed output hashes.
Reports separate normal waits, failed producers, unselected branches, and inconclusive outcomes.
A failed producer needs review and an explicit successor. It is not a normal wait.
Capture ownership remains outside this read-only check. Use the qualified capture admission path.
No TTR setting, model, worker module, or runner process changes.

## Authoring command

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/workflow_admission440.py COMPILED.json --text
```

Exit code 0 permits registration at this snapshot. It does not establish immediate execution readiness.
Exit code 2 identifies blocking requirements. Invalid manifest structure fails before normal inspection.
The report names owners, requirements, next actions, and normal waits.

Use `--profile-sources` to measure source closure checks.
Use `--profile-store reports/work/WORKFLOW440` for a bounded disposable approval-store measurement.
The profiler reads the live store but never locks or writes it.
It removes only its own temporary copies. It does not copy model or image payloads.
Its failure test verifies original bytes remain unchanged when a write fails.

## Measurements

Two retained campaigns pass preflight without new scientific execution.
Their completed attempts and conditional branches remain unchanged.

| Measurement | Observed value |
| --- | ---: |
| Approval store | 77,831,555 bytes |
| Current approvals / historical events | 1,374 / 1,606 |
| Two-job preflight with source profiling | 0.823–0.973 s |
| Source closure checks per two-job campaign | 0.668–0.685 s |
| Approval store byte read, 3 samples | 0.0057–0.0059 s |
| JSON parse, 3 samples | 0.130–0.157 s |
| JSON serialization, 3 samples | 0.184–0.188 s |
| Atomic save of disposable copy, 3 samples | 0.855–0.957 s |
| Uncontended isolated lock | 0.00011–0.00021 s |
| Live lock contention | Not measured |

Atomic save includes serialization. Do not add both as a single-path total.
These are warm-cache measurements from one host, not general USB performance claims.
The profiler does not measure concurrent traffic or the complete live admission path.

## Decision and next tranche

Repeated full-store parsing and publication are credible optimization targets.
The measurements do not justify a new storage format or database yet.
First test a bounded transaction for 5–10 explicitly approved jobs in an isolated queue.
Preserve individual checks, approval records, reasons, timestamps, source pins, and revocation events.
Compare identical specifications against the current per-job path.
Require crash recovery, concurrent revocation checks, duplicate handling, and equivalent authorization results.
Do not activate it before qualification.

Any source-check reuse needs exact identities and strict invalidation.
Do not weaken hashing or use a dashboard cache for execution authority.
This tranche improves preparation failure handling. It does not claim faster live approval or add overnight capacity.
Use these checks for the next compatible Standard proposal comparison.
Preserve previous successes and keep HCF optional.

## Validation

Campaign tests exercise actual isolated queue admission and execution.
Additional tests cover missing training records, storage exhaustion, failed producers, changed evidence, and duplicate IDs.
Profiler tests cover original-store preservation, temporary cleanup, and failed writes.
Evidence remains under `reports/work/WORKFLOW440`.

All 63 focused tests pass in 46.921 s.
Offline checks pass 177 Swift Testing cases and 14 XCTest cases without failures.
The Swift Testing run takes 53.278 s. Diff whitespace checks pass.
