# Execution completion amendment — 2026-09-19

## Scope and evidence

User supplied two consecutive final responses that promised continued P4-B/P2-A
work but stopped after partial helper edits. This amendment addresses premature
turn termination, not a claim that the resulting software has been reviewed.

Changed AGENTS.md, Research/WorkerExecution/SKILL.md, WorkerWorkflow.md,
PlanTemplate.md, ImplementationPlans.md, and BestPractices.md (BP-55).
Removed contradictory smallest-slice/one-packet execution guidance. Packets remain
independent review boundaries within a substantial authorized tranche. No feature,
hardware, training, deployment, or cross-repository execution is authorized here.
Other workers' code, taxonomy, model documentation, and queue changes were preserved.

## Verification

- Skill creator's `quick_validate.py Research/WorkerExecution`: exit 0, valid skill.
- `git diff --check`: exit 0.
- Changed-document local Markdown links checked separately; no external browsing required.
- No Swift checks needed: documentation/instruction changes only.

## Manual instruction scenario review

These are desk checks of the written policy, not independent agent behavior tests.

| Scenario | Required behavior in amended contract |
|---|---|
| Helper finished, assigned comparator and integrated tests remain | Continue in the same turn; commentary only for interim progress |
| One packet review-ready in an assigned multi-packet tranche | Continue other included packets unless a declared dependency prevents it |
| Toy tests pass but required CLI/caller is not connected | Incomplete; integrate and test before review-ready claim |
| Own code causes test failures | Diagnose and fix within scope, then rerun; no false pass |
| Real pixels unavailable, software tests are feasible | Complete software; report real-data qualification separately blocked |
| SMB disconnected | Save local unpublished status; continue authorized local work |
| New hardware authority required, independent assigned docs/tests remain | Stop hardware operation; finish independent work and report exact authority gap |
| User interrupts or actual runtime limit occurs | Honor interruption; checkpoint truthfully, do not claim completion |
| Entire assigned scope verified | Return completed-for-review handoff; do not expand into unassigned backlog |
| User requests review/diagnosis only | Inspect and report; persistence does not authorize implementation |

## Completion boundary

The requested instruction amendment is implemented and structurally checked.
This does not accept the prior workers' software or guarantee future agent behavior.
Active agents need to read the changed instructions; this task did not send prompts
to other tasks or install an enforcement/monitoring system. The architect must use
the stronger criterion-by-criterion review before accepting their deliverables.
