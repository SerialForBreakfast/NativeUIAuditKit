# WORKFLOW441 — Exact-job admission transaction qualification

Date: 2026-10-18. Owner: Maximum-mini-NUIAK.

The dedicated worker account remains postponed. This work uses the existing queue and account.

## Scope

The isolated adapter approves up to 10 explicitly identified jobs with one atomic publication.
Each entry supplies its job ID, specification hash, approver, and reason.
Each job retains the existing input, training, storage, state, and source checks.
The transaction uses the existing approval lock. It preserves individual records and historical events.
It rejects revoked IDs instead of restoring their approvals.
It rechecks specifications, inputs, and source pins before publication.

The adapter refuses the live queue. Capture admission remains outside this pilot.
No active worker module, model, experiment specification, or runner process changes.
This is an admission optimization, not additional execution authority.

## Tests and observed timing

The tests use real resident approval checks in disposable queues.
They cover 5-job and 10-job admission, equivalent checks, repeated requests, and concurrent duplicate requests.
They also cover concurrent revocation, invalid hashes, storage exhaustion, and source changes during checks.
Injected write failures test preservation before atomic replacement and recovery after a lost receipt.
These tests do not establish survival after host power loss.

One small-store timing sample gives:

| Jobs | Individual admission | Transaction |
| --- | ---: | ---: |
| 5 | 1.693 s | 2.348 s |
| 10 | 4.001 s | 3.491 s |

The transaction uses 1 store write instead of 5 or 10.
However, additional final checks have a cost. These samples do not establish a reliable speed improvement.
The live 77.8 MB approval store differs from these small disposable stores.
Do not extrapolate these timings to live admission.

## Decision

Update: [WORKFLOW442](WorkflowTransaction442.md) completes representative-store and process-recovery checks.
It adds an explicit campaign option. The observations below remain the original pilot decision.

Keep live admission unchanged. The safety tests support further qualification, not immediate deployment.
Next, compare repeated samples using a disposable copy of the representative approval store.
Check process termination before and after replacement. Preserve the original store throughout qualification.
Measure complete admission time and lock duration, not only serialization.
If the transaction has no useful benefit, retain the existing per-job path.

No scientific experiment repeats for this qualification.
Standard remains primary. HCF remains optional. Previous successes and checkpoints remain unchanged.

## Reproduction

Run `PYTHONPATH=scripts .venv-yolo/bin/python -B -m unittest test_workflow_transaction441.TransactionTests -v`.
Tests create disposable files inside the project and remove their own fixtures.
The helper has no live admission CLI. Do not remove its live-queue guard for routine use.

## Validation outcome

All 13 transaction checks pass. The first 11 take 32.620 s; 2 additional negative checks take 1.786 s.
Offline Swift validation passes, including 177 Swift Testing cases in 53.916 s.
The first build fails because migrated cache records retain the old checkout path.
The retry uses the existing USB module cache and passes. No cache deletion is required.
Whitespace checks pass. The detached runner retains PID 77776 throughout this work.
