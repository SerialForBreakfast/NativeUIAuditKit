# PERMISSION532 — Routine permission audit

Date: 2026-10-25. Owner: Maximum-mini-NUIAK.

## Decision

The maintainer explicitly approves the proposed policy changes after the initial edit was rejected by automatic approval review.
AGENTS.md now records that approval. WorkerWorkflow.md no longer requires a separate packet where existing authority already covers the action.

| Finding | Applied rule |
|---|---|
| Repeated consent for unchanged work | Reuse approval for unchanged actions, targets, and remaining cumulative budgets |
| Tested NUIAK corrections require activation | Permit activation and one supported dashboard restart when idle within requested implementation work |
| Approval requests mix evidence and authority | Missing labels require observations, not consent |
| Older packet wording conflicts with standing authority | Apply current user approval and AGENTS.md amendments first |
| Scope expansion or restricted actions | Request exact consent and identify its source |

Preserve user pauses, running work, queue history, original evidence, and previous successes.
Schedules, destructive actions, physical devices, and unauthorized TTR replacement retain explicit consent requirements.
No new installation, download, release, or external-access permission is granted.
Sandbox review remains a platform control. This audit does not change platform settings or TTR instructions.

## TTR findings

Developer/TVTestRig/AGENTS.md contains standing authority for local builds and tests, ongoing Simulator trials, and supported recovery.
Agents must read the applicable scope before requesting repeated consent.
Those rules do not automatically authorize candidate replacement, downloads, erasure, or unrelated operations.
This audit does not classify every previous sample installation request as unnecessary.

## Remaining technical friction

Campaign-specific validators still create repeated source activation work.
Use reusable configuration checks for supported scenarios instead of adding new campaign identifiers to validators.
Preserve specification identity and source verification.
GRAPH531 provides bounded recovery branches; missing native profile acquisition still requires a qualified producer.
A permission change cannot supply absent observations or make an experiment ready.

## Verification

Reviewed the changed documents and their local links.
This change edits instructions only. It starts no jobs, changes no models, and restarts no service.
Runtime tests are not required for this documentation change.

## Next implementation tranche

1. Connect native profile acquisition to the existing capture and preparation graph.
2. Replace campaign-specific validation with reusable checks for supported scenarios.
3. Apply bounded recovery branches and verify that independent experiments continue after expected failures.
