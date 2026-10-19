# WORKFLOW437 — Complete Standard graphs and repair recovery admission

Owner: Maximum-mini-NUIAK. Date: 2026-10-18.

## Scope and result

This tranche completes the missing decision graphs for omitted-row and omitted-tab training.
Each graph reuses 17 existing scoring pairs and its existing training job.
Each graph adds 5 comparisons, 1 merge, 1 decision, and 1 follow-up.
All 16 new specifications have individual approvals. The runner owns execution.
No new training, capture, threshold change, or model promotion occurs during preparation.

The requests use the existing `workflow_batch435.py prepare` command without a new scientific adapter.
Requests and immutable manifests remain under `reports/work/WORKFLOW437/row` and `reports/work/WORKFLOW437/tab`.
The request files sit beside those directories.

## Review several graphs

`workflow_review437.py` reads up to 12 pinned compiled manifests.
It uses existing graph inspection and never writes queue records.
Shared generated jobs count once. Conflicting specification hashes produce an explicit blocker.
A missing or changed manifest does not hide other batches.
An incomplete review returns exit code 2. Invalid request structure fails before inspection.

The current review request covers Standard-only training and all 3 family-exclusion comparisons.
Its snapshot contains 32 generated jobs: 6 eligible pending runner checks and 26 normal dependency waits.
These counts do not describe all queue jobs. No verified decision is complete in this snapshot.
The report shows unavailable duration explicitly. Budget ceilings do not estimate useful queue duration.

Use this command for a requested batch review:

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/workflow_review437.py reports/work/WORKFLOW437/review-request.json --text
```

Do not schedule repeated reviews without explicit consent.

## Recovery gate repair

`recovery_capture_gate437.py` replaces the old comparison of serialized marker bytes.
The original guard remains pinned by its original byte hash.
Preserve that guard in an immutable copy before recovery can remove the active guard.
The gate compares the complete saved JSON value with that original marker.
This permits formatting changes from serialization. It rejects changed fields or changed original bytes.
The new plan version is `recovery-capture-admission-v2`. It requires an `originalMarker` pin.
Target identity, restoration, ownership, screenshot, and immutable capture checks remain required.

The old gate and failed recovery attempt remain unchanged.
The successor gate is qualified in isolation but is not registered against the failed recovery.
Registration needs an explicit recovery successor after the storage requirement passes.

## Exact native capture blocker

Maximum-mini-TTR reports 33,622,715,462 bytes against a 536,870,912-byte HCF evidence quota.
The check stops before input. Restoration does not start.
USB free capacity does not satisfy this separate producer quota.
Maximum-mini-NUIAK requests a supported offload and resume procedure through the existing coordinator channel.
The coordinator stores the request at cursor 887. Forwarding and recipient acknowledgment are not confirmed.
The final attention check contains no unread reply.

Do not raise the quota blindly, remove peer evidence, or bypass the capture guard.
The resume condition requires verified retention, a passing producer budget check, and a new recovery specification.
Then bind the corrected gate to that recovery. The gate can admit the 6 frozen captures after restoration passes.

## Validation

All 46 focused tests pass in 32.050 s.
Tests include real isolated queue execution, immutable repeated admission, marker tampering, and failure paths.
Review tests cover unavailable batches, changed manifests, conflicting specifications, and duplicate counting.
The live read-only review verifies all 4 admitted graphs without dispatching work.
Logs and the review remain under `reports/work/WORKFLOW437`.

The first integrated Swift check fails because a module cache contains the old internal checkout path.
A separate module cache preserves the original cache during the offline retry.
The retry passes all 177 tests in 25 suites in 53.388 s of test execution.
The detached runner remains alive. Neither dashboard server receives a restart.

## Next decision

Review the completed Standard comparisons before selecting a correction.
Reject lost previous successes and new wrong selections.
Keep HCF optional and shipped Standard models unchanged.
Do not count conditional jobs as ready overnight work.
Admission performance remains a separate task. This tranche does not change the per-job approval contract.

## Admission performance sample

The approval file contains 77,636,013 bytes, 1,370 records, and 1,602 events in one local snapshot.
Loading takes 0.1603 s. JSON serialization takes 0.1877 s.
This read-only sample excludes file writes, source checks, input checks, and lock time.
It does not explain the entire preparation cost or prove that bulk approval is safe.
Measure those stages before changing approval storage. Preserve individual job authority and revocation history.
