# WORKFLOW434 — Reusable model decision batches

Date: 2026-10-18. Owner: Maximum-mini-NUIAK.

## Purpose

Turn a short experiment description into a train, score, compare, decision, and follow-up graph.
Reuse existing T06 training, T37 selection scoring, and T63 consumer scoring.
Keep Standard first. Preserve shipped models and every declared retained success.

## Implementation

`scripts/model_decision_batch434.py` compiles and registers immutable specifications.
`scripts/model_decision434.py` verifies evidence and produces case-linked comparisons and reports.
The existing queue remains the only scheduler. The detached runner owns execution.

A description names its question, controlled comparison, training job, and matched baseline and candidate scoring jobs.
An optional pinned `executionBatch` supplies new T06, T37, and T63 descriptions through the existing compiler.
When `executionBatch` is null, the compiler reuses existing jobs without repeating training or scoring.
Missing outputs remain dependencies. Changed specifications and incompatible inputs fail validation.

Each comparison job handles up to 4 matched pairs.
The merge verifies comparison identities. The decision verifies the complete declared suite and completed training checkpoint.
The reports separate profiles, proposal sources, groups, no-focus support, margins, gains, losses, and new wrong selections.
Training and scoring times come from retained evidence when available.

## Decision rules

- If any retained success is lost, report a contradicted result.
- If any new wrong selection appears, report a contradicted result.
- If Standard raw-proposal selection improves without these regressions, report a supported development result.
- Otherwise, report an inconclusive result.
- If evidence is missing or incompatible, fail the job. Do not accept a model.

The follow-up job selects a fixed analysis report from these outcomes.
A contradiction identifies failures for diagnosis. A supported result requires independent qualification.
An inconclusive result identifies coverage and proposal gaps before more training.
The follow-up does not authorize training, capture, promotion, or navigation.

## Two admitted experiments

| Batch | Comparison | Decision |
| --- | --- | --- |
| `workflow434-standard` | PROFILE425 Standard-only versus the retained mixed-profile baseline | Does Standard-only training improve proposal selection without losing retained successes? |
| `workflow434-without-button` | RESERVE429 without-button training versus PROFILE425 Standard-only | Does omitted-family training transfer to buttons without degrading other retained cases? |

Each batch reuses 17 matched scoring pairs and its existing training job.
Each adds 8 diagnostic jobs: 5 comparisons, 1 merge, 1 decision, and 1 follow-up.
All 16 new jobs have individual approvals. Each permits 800 s, 100 MB, and 1 attempt.
These are conditional diagnostics, not 16 ready training jobs or a measured overnight workload.
Plans and exact specification pins remain under `reports/work/WORKFLOW434/`.

## Qualification

The focused suite passes 27 tests. The integrated Swift suite passes 177 tests in 25 suites.
The isolated queue executes two descriptions through the same adapter without a second experiment script.
Tests cover supported and contradicted outcomes, missing evidence, changed hashes, duplicate pairs, and duplicate dispatch.
Tests also cover no-focus regressions, incompatible settings, and new execution descriptions through existing templates.
Synthetic software fixtures establish workflow correctness, not model accuracy.
The second real experiment remains dependent on its actual training and scoring results.

Logs: `reports/work/WORKFLOW434/focused-tests.log` and `reports/work/WORKFLOW434/swift-tests.log`.

## Remaining work

Review the automatic reports after the background runner completes each graph.
Extend the contract explicitly before using detector templates or different training completion policies.
Do not change active specifications to broaden this version.
Measure preparation and review effort before claiming efficiency gains.
The implementation makes no model improvement claim before the matched results finish.
