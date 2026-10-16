# EXTENSION408 — inspect exhausted jobs and restart them with larger limits

## Problem

A job is exhausted when its attempts reach `limits.maxAttempts`. All live jobs use 1 attempt.
[CONTINUATION403](Continuation403.md) resumes only timed-out jobs with a qualified checkpoint.
It also limits each chunk to 800 s. Most exhausted jobs have no qualified checkpoint.
The runtime limit for each job comes from a hardcoded table in `research_execution_policy.py`.
The dashboard cannot set a larger limit, restart a job, or estimate the remaining time.

## Behavior

The maintainer opens an exhausted job in the dashboard and saves a restart with new limits.
The save action does these steps:

1. It copies the parent specification to a new successor job ID, such as `parent-r2`.
2. It changes only the `limits` fields and, for training, `storageBudgetBytes`.
3. It records a limit override for the exact successor specification hash if a limit is above the default policy.
4. It writes an immutable extension record with the parent, the parent result pin, the reason, and the save time.
5. It approves that 1 successor job as `maintainer`, through the normal approval checks.

The parent job and its attempt stay unchanged as history. Specifications stay immutable.
A restart starts from step 0. It does not claim checkpoint resume.
Use a CONTINUATION403 successor for a qualified checkpoint resume.

## Queue order

The runner selects ordinary ready work first, as before.
Then it selects extension jobs in the order of their save time. A saved restart goes to the end of this list.
Then it selects approved continuation chunks.
The runner checks the order again after each job. It does not stop running work to change the order.

## Limits

- The new timeout and output limits must be equal to or larger than the parent limits.
- The maximum timeout is 86400 s. The maximum output is 16 GiB. The spec validator sets these values.
- If a limit is above the default policy, only `maintainer` can record the override.
- An override applies to 1 exact specification hash. A changed specification needs a new override.
- The runner uses the larger of the default policy and the override.
- The 30-epoch training limit does not change. More epochs change the experiment, not the budget.
- Capture jobs are not supported. Capture limits stay at 800 s and 100 MB.
- Training jobs with `checkpoint-v1` resume are not supported. Use a continuation for them.
- Only 1 successor can exist for each parent. To extend again, extend the exhausted successor.

If the parent failure is not `timeout` or `output_limit`, more resources do not fix it.
The dashboard shows this warning. A restart with the same limits is permitted after a repair.
The reason text must name the repair or the unresolved question.

## Time estimate

The estimate uses the last attempt of the parent:

- `attempt.json` gives the start time.
- `progress.json` gives the completed units, the total units, and the time of the last update.

The rate is the elapsed time to the last update divided by the completed units.
The rate includes setup time, so the estimate is conservative.
The restart estimate is the total units multiplied by this rate.
The suggested timeout is 125 % of that estimate, rounded up to 1 min.
If the attempt has no completed units, no estimate is shown. The suggestion is 2 times the old timeout.

While a job runs, the dashboard shows a live estimate from its own progress.
If 3 or more comparable completed runs exist, the history estimate takes priority.
A linear estimate does not include slower later epochs or evaluation steps at the end.

## Commands

- `scripts/research_extensions.py inventory` lists exhausted jobs, reasons, estimates, and suggested limits.
- `scripts/research_extensions.py save JOB --timeout-seconds N --max-output-bytes N --reason TEXT` saves a restart.
- The dashboard server supplies the same save action at `/api/extend`.

The `save` command acts as `maintainer`. Agents do not run it. Agents can run `inventory` and propose limits.
A running dashboard server keeps its old code. Restart the server to show the new controls.

## Restart the dashboard server

Use `scripts/restart_research_dashboard.py` from the package folder:

```bash
.venv-yolo/bin/python -B scripts/restart_research_dashboard.py --priority-task TEMPLATE395
```

The script does these steps:

1. It imports the new server code first. If the import fails, the old server stays running.
2. It refuses if a program that is not a dashboard holds the port.
3. It refuses if a job holds an active lease. Use `--wait SECONDS` or `--cancel-running` to continue.
4. It asks the runner to stop after its current job. Then it sends SIGINT, and SIGTERM or SIGKILL only if needed.
5. It starts a detached server with `--resume-approved`. It checks the light `/api/health` endpoint.

Other options are `--stop`, `--dry-run`, `--no-resume`, and `--port`.
Exit code 2 means a safety check refused the action. Exit code 1 means an operating system error.
The server writes `.build/dashboard/server.log` and `server.pid`.
It also writes `.build/dashboard/control.json`, which holds the control token. Only the current user can read this file.
An older server has no control file. Its token comes from the full page, which took 2.5 min on the live queue.

## Validation

Tests use an isolated queue and synthetic progress files. They are not model evidence.
Tests cover the estimate, the order after ordinary work, the policy override, refusals, and the real execution of a successor.

## Dashboard snapshot cost

A profile of the live queue (805 jobs) shows a 29 s snapshot. Several open tabs increase it to 2.5 min.
These changes reduce the cost:

- `summarize` and the readiness labels load the 11.7 MB approval file once per snapshot, not once per job.
- The display hash cache holds 200,000 entries. The old limit of 10,000 cleared the cache during each snapshot.
- The server builds 1 snapshot at a time and shares it between requests.
- A cached snapshot is used until it is older than 5 s, or 2 times its build time if that is longer.
- An action or a change of the running job forces a new snapshot.
- A poll with `?since=ID` gets a 176-byte reply when nothing changed. A full reply is about 1.1 MB.
- The page sends no new poll while a reply is still pending.

Measured on the live queue: the first snapshot takes 8.8 s, and the next one takes 1.3 s.
The runner and the approval checks still hash files in full. Only the display path uses cached hashes.
