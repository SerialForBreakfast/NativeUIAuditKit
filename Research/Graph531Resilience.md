# GRAPH531 — Bounded recovery for experiment graphs

Owner: Maximum-mini-NUIAK. Status: implemented and activated at an idle boundary.

## Observed gaps

Normal dependencies require complete producer outputs. A failed producer cannot release a repair through that dependency.
Scientific conditions accept supported and contradicted branches. They reject an explicit inconclusive branch.
A failed job ends the current dispatch cycle, including diagnostic jobs with independent work behind them.
The continuous runner can start another cycle. This is not evidence that every failure stops the service.

## Implemented candidate

1. A failure dependency names the producer specification, exact attempt, and expected failure reason.
2. It exposes the failure receipt. It does not expose failed outputs as successful data.
3. The immediate recovery job must be a diagnostic artifact job with 1 attempt.
4. Normal success dependencies connect its verified qualification output to any approved downstream work.
5. An explicit inconclusive condition selects a predefined follow-up.
6. An opted-in diagnostic artifact failure lets the bounded cycle continue to independent approved jobs.

Default specifications retain their existing behavior.
Cancellation, interrupted attempts, changed identities, and unexpected failures do not select a repair.
A newer producer attempt prevents recovery from silently using an older failure.
Successful producers leave their unused recovery branches unselected.
An unapproved repair does not execute. A failed repair cannot loop automatically.
Capture and training failures do not opt into the new cycle-continuation rule.
Their cleanup, ownership, checkpoint, and approval requirements remain unchanged.

## Simple authoring

Use the existing experiment-batch-v1 compiler and template descriptions.
For a parent within the same batch, the compiler can derive the specification hash.
External parents still require their exact specification hash.

```json
{
  "dependencies": [{
    "job": "prepare-a",
    "outputs": [],
    "failure": {"attempt": 1, "reason": "process_failed"}
  }]
}
```

This dependency belongs to a diagnostic repair or qualification description.
It does not authorize another capture or training attempt.
Add `continueIndependentOnFailure: true` only to bounded diagnostic artifact descriptions.
Use ordinary output dependencies after successful repair qualification.
Conditions can now name `supported`, `contradicted`, or `inconclusive`.
Each action remains an exact approved job with fixed limits and inputs.

## Apply the pattern to current bottlenecks

| Hurdle | Graph response | Remaining requirement |
|---|---|---|
| Missing native profile | Approved profile producer before crop training | Implement the supported producer connection; preserve group exclusions. |
| Incomplete static labels | Prepare valid binary focus labels independently | Do not guess detector classes or admit unknown focus. |
| Diagnostic process failure | Run its predefined diagnostic repair | Exact attempt and expected reason must match. |
| Exhausted training | Inspect checkpoint and qualify restoration | Existing cumulative time, epochs, and storage authority still apply. |
| Inconclusive model comparison | Run a predefined independent comparison | Do not create an arbitrary sweep. |
| Regression | Reject replacement and run the approved diagnosis | Preserve previous successes and shipped models. |
| Unexpected failure | Retain the failed attempt and report the exact requirement | Independent ready branches can continue. |

The graph cannot invent a missing producer or reliable labels.
The author must include that producer as an executable node before claiming an unattended campaign.
A dependency definition alone does not unblock native training.

## Verification and activation

The candidate and integrated suites each pass 67 tests through the actual queue in isolated directories.
The integrated suite takes 28.967 s. No experiment execution is used as a software test.
Two configuration-only batches demonstrate failure, repair, and independent execution without new adapter scripts.
Tests cover changed identities, cancelled attempts, unexpected reasons, failed repairs, approval checks, and duplicate execution.
Tests also verify that failed outputs cannot become training inputs through the failure dependency.
The live sources remain unchanged during candidate qualification.
After qualification, the existing idle-safe tool stops dispatch and restarts the dashboard.
No job is running at activation. No valid pending approvals require refresh.
The queue, existing priority, submitted specifications, and prior attempts remain unchanged.

Activation must preserve the current queue and stop new dispatch only at an idle boundary.
Refresh only existing affected approvals whose specifications and input hashes still pass.
Do not overwrite submitted specifications or restore revoked approvals.
If an explicit source pin changes, create a reviewed successor instead of changing that specification.
The dashboard process retains code. Use its existing idle-safe restart mechanism for activation.

Candidate patch and test logs: reports/work/GRAPH531/.
No scheduler, recurring task, model promotion, or budget extension is added.

Recorded candidate preparation through activation takes 11.2 min, against the 25–40 min estimate.
Initial inspection was not timed. Service 89140 resumes through the existing restart tool.
