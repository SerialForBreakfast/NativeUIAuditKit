# ADR-0026 — queued, resumable research experiments

## Capture producers — 2026-10-12

The queue now supports bounded Fixture generation as a producer job.
Consumers name the producer specification and required outputs before capture starts.
The queue resolves output hashes only after successful completion and integrity checks.
Failed capture or unresolved cleanup blocks consumers. Failed attempts do not retry automatically.
The [GENERATION352 plan](Plans/Generation352.md) defines the capture contract, recovery marker, tests, and first live result.

## Measured evidence amendment — 2026-10-12

The [RESEARCH340 plan](Plans/MeasuredResearch340.md) supersedes assigned screening scores and automatic retries described below.
The 100 legacy benchmark jobs use placeholder scores. Preserve their files, but exclude those scores from measured results.
Require pinned predictions, labels, inputs, models, preprocessing, and raw counts for measured accuracy.
Keep replay agreement, execution completion, and model acceptance separate.
Report unsupported coverage explicitly. Do not substitute a different theme or rank incompatible tasks together.
Use 800 s and 100 MB diagnostic limits. The approved candidate exception remains 30 epochs, 30 min, and 2 GiB.
Require explicit retry after failure or interruption. Keep completed attempts unchanged.
The optional loopback dashboard controls the existing queue. It does not add remote execution or a second scheduler.
The current-task panel shows actual worker events. It never estimates progress from elapsed time.
Use a launch token, Host and Origin checks, shared execution locks, and cancellation of runner-owned process groups only.
See [results and remaining inputs](RESEARCH340Results.md).

## Exhausted jobs and dashboard operation — EXTENSION408, 2026-10-14

- The dashboard lists exhausted jobs. An exhausted job has used all of its attempts.
- The maintainer can save a restart. A restart is a new successor job with larger limits and its own approval.
- The parent job and its attempts stay unchanged. A restart starts from step 0.
- A limit above the default policy needs a maintainer override for the exact successor specification hash.
- The runner selects ordinary ready work first, then restarts in save order, then approved continuation chunks.
- Capture jobs and `checkpoint-v1` training jobs cannot use restarts. Training stays at 30 epochs or fewer.
- The time estimate uses recorded progress units of the parent attempt. The progress bar still shows only worker events.
- The server builds 1 snapshot at a time and shares it between requests. Unchanged polls get a small reply.
- `scripts/restart_research_dashboard.py` stops the runner after its current job, then restarts the server.
  It refuses to stop a running job unless the maintainer passes `--wait` or `--cancel-running`.

See [EXTENSION408](Plans/Extension408.md).

## Historical decision

Status: accepted. [RESEARCH338](RESEARCH338Results.md) replays 3 FOCUS audits with exact agreement. Diagnostic jobs are qualified.
[RESEARCH339](RESEARCH339Results.md) replays the FOCUS329 30-epoch training run with byte-identical weights. Training jobs are qualified.
Date: 2026-10-11.
Relates to [ADR-0025](ADR-0025-Portable-Experiment-Runner.md), [ADR-0011](ADR-0011-Measured-Training-Efficiency.md),
[LocalExperimentApprovalEnvelope](Plans/LocalExperimentApprovalEnvelope.md), and [FocusImprovementProgram](Plans/FocusImprovementProgram.md).

## Problem

FOCUS302–FOCUS331 test 1 idea at a time. Each idea gets a new hand-written script, a fixed output folder, and a manual report.
This pattern makes 3 problems:

1. Throughput is low. A person or agent must start, watch, and summarize each run.
2. Results are hard to compare. Each script writes its own format, and each decision rule lives in a different file.
3. Provenance is incomplete. A registration records the top script hash, but the FOCUS331 audit imports 131 repository modules.

The maintainer wants many ideas tested as independent, resumable jobs, with analysis that updates as results arrive.

## Decision

Add a NUIAK research queue. It runs declared experiment jobs, records a standard result for each job, and keeps a ranked summary current.

The queue is separate from ADR-0025's `FixtureExperiments` tool. That tool acquires images in TTR and must not launch model sweeps.
The research queue runs NUIAK analysis and, later, training. It reuses ADR-0025's job, receipt, and recovery rules.

The queue is not a service. It runs only when a person, an agent, or the host scheduler starts it.
Each invocation runs a bounded number of jobs, then stops. A later invocation resumes from the recorded state.

## Experiment spec

Each job starts from 1 immutable spec file, `research-spec-v1`. The spec declares these fields:

- Identity: job ID, task ID, owner, and creation time.
- Question: hypothesis, kind (`replay`, `screen`, or `confirm`), and the decision rule. The rule is fixed before execution.
- Authority class: `diagnostic`, `training`, `capture`, `export`, or `promotion`.
- Entry point: an allowlisted adapter with typed parameters. The first adapter is `python-callable`.
- Inputs: each input file with its repository-relative path and SHA-256.
- Outputs: the expected output files, a byte limit, and a wall-time limit.
- Replay section, for `replay` jobs only: the recorded output files and the fields that can differ, each with a reason.

A spec contains no shell command, absolute path, credential, or machine name.

## Authority enforcement

The queue checks authority before it starts a job. It does not ask a person per run when standing approval applies.

| Authority class | Current rule |
| --- | --- |
| diagnostic | Allowed. No training, capture, device use, or data-role change. |
| training | Allowed when the spec carries the standing-approval fields: hypothesis, exact membership, initialization, epochs, storage budget, and acceptance evidence. The experiment-log entry must exist before the run. See [RESEARCH339](Plans/RESEARCH339.md). |
| capture, export, promotion | Refused. These need their own authority. |

Evaluation membership is pinned by hash. A `screen` job cannot use evaluation data to select a variant.

## Execution and recovery

- The runner takes 1 host lock. A second runner on the same host stops with `resource_busy`.
- Each job runs in its own Python process. One job's module changes cannot affect another job.
- The `python-callable` adapter imports the named module and sets its output attribute to a new attempt folder.
  This lets recorded scripts run unchanged. Their fixed output folders stay untouched.
- The adapter records the SHA-256 of every repository module that the process imported.
- Each attempt writes `attempt.json` before it starts and `result.json` after it ends. Both writes are atomic.
- On restart, the runner skips a job when its result exists and its outputs still match the recorded hashes.
  It marks an attempt without a result as interrupted. It starts a new attempt within the job's attempt limit.
- Failed attempts keep their logs and partial outputs.

## Results and analysis

Each `result.json` (`research-result-v1`) records these fields:

- Spec hash, input hashes, module-closure hashes, interpreter, and package versions.
- Exit status, timing, and the output inventory with hashes.
- For replay jobs, the comparison result for each recorded file.
- Metrics extracted by the spec's declared extractor, when one exists.

The `summarize` command reads all result records and writes 1 summary table.
The table groups jobs by task and question. It shows the outcome, the decision rule, and the cost of each job.
A screening result can rank an idea. It cannot promote a model. Promotion still needs the matched gates in FocusImprovementProgram.

## Screening and confirmation

Use 2 stages for broad tests:

1. Screen: many short jobs with small budgets on training-only groups. Report group-level intervals, not frame counts.
2. Confirm: only top-ranked ideas get a full matched run with the existing regression and reserved-group checks.

Short screens on small, grouped data produce false signals. Therefore, the screen only orders the confirmation queue.

## Replay qualification

Before new ideas use the queue, the queue must reproduce finished work.
RESEARCH338 replays 3 training-free FOCUS audits from their recorded source and inputs:

| Job | Recorded output | Original time |
| --- | --- | ---: |
| FOCUS329 boundary audit | `registration.json`, `audit.json` | 163.4 s |
| FOCUS330 detector-centered audit and report | `audit.json`, `report.json` | 85.9 s, plus the report |
| FOCUS331 boundary-region audit and report | `registration.json`, `audit.json`, `report.json` | 98.7 s, plus the report |

Each replay passes only when every recorded field matches, except the declared timing and file-hash fields.
The replays use no training, no device, and about 6 min of CPU time.

## Alternatives

- Keep hand-written scripts: lowest setup cost, but throughput and comparison stay manual.
- Extend `FixtureExperiments`: conflicts with ADR-0025, which keeps model work out of the acquisition tool.
- Adopt an external workflow system: adds a service, dependencies, and a second scheduler before the job contract is proven.

## Limits

The first tranche supports only `diagnostic` jobs and the `python-callable` adapter on local hardware.
RESEARCH339 adds `training` jobs. An interrupted training attempt restarts from epoch 0, because the trainers save weights only at the end.
Distributed execution needs a bundle transfer and a qualified executor.
File times show that the replayed modules predate the original runs. File times do not prove that the code was identical.
# WORKFLOW357 amendment — October 12, 2026

The existing loopback server accepts explicit approved job IDs and canonical specification hashes through `/api/add`.
The runner persists approvals separately and reads them at dispatch boundaries. Adding jobs does not start a stopped runner.
Pre-dispatch checks report missing inputs, dependencies, training registration, storage, and the production interpreter.
Campaign reports preserve measured comparison fields and verify output hashes. Execution completion never grants model acceptance.
The HCF study uses separately recorded training and storage budgets. Backup/restore remain future tasks with exact receipt requirements.
