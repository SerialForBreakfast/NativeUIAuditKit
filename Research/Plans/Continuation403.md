# CONTINUATION403 — useful continuations when priority work finishes

## Behavior

The existing runner selects ordinary ready work before reviewed continuation jobs.
The runner checks priorities after every job. It does not kill training to change priorities.
Each continuation uses a new immutable job and a new output directory.
The parent attempt, checkpoint, and results remain unchanged.
Registration does not approve a job or start the runner.
Stopping the runner prevents further continuation dispatch.

## Admission

Use `scripts/research_continuations.py register RECORD.json` with an existing successor specification.
Then approve that exact job through the existing approval checks.
The record supplies these fields:

- `version`: `research-continuation-v1`.
- `job` and `specSHA256`: the immutable successor identity.
- `parent` and `parentAttempt`: the exhausted attempt.
- `parentResult`: a verified file pin for the timeout result.
- `checkpoint`: a verified file pin within that attempt.
- `qualification`: a verified resume test report, also pinned in the successor inputs.
- `reason`: the unresolved question that justifies more work.
- `budget`: total seconds, total output bytes, and maximum seconds per chunk.

The qualification report uses `resume-qualification-v1` and records these fields:

- `passed`: true only after an actual interrupted-versus-uninterrupted comparison.
- `checkpoint` and `parentResult`: exact file pins.
- `adapter`: the tested executable adapter contract.
- `preservesControls`: the reviewed comparison result.
- `budget`: the approved cumulative limits.

The runner verifies pins, unchanged parent inputs, experiment controls, and current approval before selection.
It reserves worst-case time and output size for every registered sibling.
The reservation includes the original attempt's measured duration and retained output bytes.
Chunks cannot exceed 800 s. Each adapter must finish its chunk with durable outputs.
Nested continuation budgets are unsupported. Do not split a budget into independent chains.
Completed, cancelled, and failed successor attempts never retry automatically.

## Current limitations

The training contract permits restart and one qualified crop restore adapter.
[CHECKPOINT404](Checkpoint404.md) measures restoration for fixed-last crop training on retained inputs.
Other trainers and configurations remain unqualified.
A saved optimizer or random state does not establish correct restoration.
Each continuation still needs a useful unresolved question, matching inputs, and its own approved budget.
Do not turn a restart into a claimed resume or change existing training approvals.
Capture failures need diagnosis and restoration checks, not extra time.
[EXTENSION408](Extension408.md) restarts an exhausted job from step 0 with larger limits when no checkpoint is qualified.

## Retained attempt review

The review finds 697 completed jobs and 19 failed jobs.
Only 1 failed job records a timeout with a checkpoint.
Its HCF388 successor completes the required 30 epochs and has verified outputs.
The timeout is superseded. More work on that old attempt would duplicate an answered comparison.
The other 18 failures need repairs rather than more execution time.
There are no qualified useful continuation jobs in this reviewed set.
The runner remains available for ordinary approved work and future qualified continuations.

## Validation

Test actual successor execution in an isolated queue.
Test priority arrival between chunks, restart, duplicate registration, revocation, altered checkpoints, and cumulative limits.
Use synthetic checkpoints only for software tests. They do not qualify model resume.
Display continuation status separately from execution completion and model acceptance.
Keep Standard models and optional HCF models unchanged.
