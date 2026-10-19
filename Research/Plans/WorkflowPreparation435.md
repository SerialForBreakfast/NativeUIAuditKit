# WORKFLOW435 — Simple preparation and visible requirements

Owner: Maximum-mini-NUIAK. Date: 2026-10-18.

## Delivered scope

`workflow_batch435.py` adds short request authoring, preparation, and read-only graph inspection.
It reuses WORKFLOW434 and the existing queue. It does not add a scheduler or change active worker modules.

A request names the question, controlled comparison, training job, and 2 lists of scoring jobs.
The author matches scoring jobs by exact non-model inputs and settings.
List order and job names do not determine the match.
Duplicate matches, missing conditions, changed inputs, and incompatible candidate models fail explicitly.

The `prepare` command writes an immutable plan and compiles comparison, merge, decision, and follow-up jobs.
Registration and approval require explicit command flags and existing task authority.
Repeating an identical preparation preserves identities. Conflicting descriptions fail instead of replacing specifications.
The command does not start execution or retry failed attempts.

## Status report

The `inspect` command reads one compiled graph and its dependency records.
It reports these states separately:

- Eligible pending final runner checks.
- Normal dependency waits.
- Missing approval or changed source checks.
- Failed, exhausted, interrupted, and invalid attempts.
- Completed jobs and verified scientific decisions.

Each requirement shows its recorded owner and the number of dependent generated jobs.
Missing owners remain unknown. An exhausted attempt does not receive an automatic continuation.
Reports preserve Standard gains, losses, and new wrong selections.
Job completion never grants model acceptance.

Inspection does not claim runtime resource availability. The runner performs its existing checks before dispatch.
No qualified duration model exists for these batch reports. They show `ETA unavailable` instead of using budget ceilings.

## Qualification

Isolated queue tests exercise preparation, execution, repeated admission, and immutable conflicts.
Other tests cover missing evidence, duplicate membership, changed hashes, wrong models, path traversal, and read-only inspection.
The suite retains WORKFLOW434's supported and contradicted result checks.
All 34 focused tests pass in 15.836 s. All 177 integrated Swift tests pass in 25 suites.
Logs remain under `reports/work/WORKFLOW434/workflow435-tests.log` and `workflow435-swift-tests.log`.

Both real WORKFLOW434 plans reproduce their 17 matched pairs with the candidate lists reversed.
Measured authoring takes 1.127 s for Standard and 0.062 s for the omitted-button comparison in one local run.
These are preparation measurements, not general throughput estimates or training speed improvements.
The check does not register duplicate scientific experiments.

## Remaining boundaries

This request format uses registered T06, T37, and T63 jobs.
WORKFLOW434 still accepts a pinned execution batch for new training and scoring jobs.
Unsupported model contracts need explicit adapter work. Do not assume these contracts cover every detector or export path.
Follow-up reports select a fixed next analysis. They do not invent or approve new training.
Native recovery still requires its separate storage and restoration checks.
The read-only dashboard now shows batch counts, normal waits, actionable requirements, and collapsed completed records.
It uses existing snapshot records without adding worker imports or queue mutations.
Running-task estimates use existing measured-run or worker-progress records, with their basis shown.
Batch duration remains unavailable until comparable timing support is qualified.

## WORKFLOW436 — Dashboard integration

The companion loads the updated JavaScript on page load. Neither server needs a restart.
The panel highlights the running job and identifies each blocker's recorded owner and dependent job count.
Missing records, cycles, exhausted attempts, and missing approvals remain actionable requirements.
Normal dependency waits do not appear as failed work.
Disconnected or stale snapshots remain visibly stale. Job completion does not grant model acceptance.

Browser inspection confirms the live panel and unchanged list at `http://127.0.0.1:8766/`.
JavaScript checks cover waits, failures, cycles, missing dependencies, and invalid or missing ETA evidence.
All 5 Python rendering and read-only transport tests pass.
All 177 integrated Swift tests pass in 57.748 s.
The log is `reports/work/WORKFLOW434/workflow436-swift-tests.log`.

Tasks.md records remaining work. Standard and shipped models remain unchanged.
