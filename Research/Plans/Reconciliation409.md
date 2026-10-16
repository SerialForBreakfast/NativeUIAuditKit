# RECONCILE409 — queue inventory, successors, and seed variation result

Owner: Maximum-mini-NUIAK. Date: 2026-10-15.

## Inventory

The live queue has 805 jobs. Before this work, 70 jobs were blocked or pending and 20 were exhausted.
No job was ready. The runner was active but had no approved work that passed readiness checks.

| Cause | Jobs | Disposition |
| --- | ---: | --- |
| Changed code inputs, completed successor exists | 61 | Superseded. See the mapping. |
| Dependency on an exhausted job, completed successor exists | 7 | Superseded (PROGRAM384-D1 v1 graph) |
| Exhausted, completed successor exists | 18 | Superseded |
| Exhausted capture, no successor | 2 | Blocked on Fixture body geometry |
| Blocked on those 2 captures | 4 | Blocked |
| Peer inference receipt | 1 | Blocked on Sillycon-TTR |
| Outdated readiness report | 1 | Withdrawn |

Only `hcf375c-71-detector-train` failed with `timeout`. HCF388 supersedes it. No exhausted job needs only more time.
No EXTENSION408 restart is proposed.

## Reconciliation

The [mapping](../Experiments/reconciliation409.json) adds 66 jobs to the 22 jobs in RECONCILE407.
`scripts/reconcile_research_jobs.py` verifies 66 results against 39 completed successors and their output hashes.
The evidence is `reports/work/RECONCILE409/reconciliation.json`.
The tool now has a `question` comparison for jobs without a template or training section.
It shows the question, authority, and entry points. Inputs can differ for those jobs.

The evidence records these differences:

- Template successors use repaired producer outputs, so their input references differ. Parameters are equal, except for the 2 export rows.
- `hcf396-10-compress` uses weight-only INT8 to meet the size limit. The stale T10 qualification job had no compression.
- The 5 old HCF375 decision jobs ask a narrower question than `hcf388-method-decision`. HCF388 answers it on the same cases.
- `hcf402-native-coverage` failed with HTTP 400. The split focused-r3 and no-focus-r4 pilots replace its recipe.
- `hcf389-proposal-selection` read a dependency from the old checkout path. `hcf397-01-proposals` answers the same question.

Specifications and attempts stay unchanged. The agent `agent:claude-unblock409` revokes 12 stale approvals.
Of these, 11 belong to superseded jobs. The 12th belongs to `hcf389-next-actions`.
Its adapter writes fixed blocker text that HCF396 export and parity results contradict. Tasks.md HCF389 holds the current requirements.
No job fails only the approval code check. Thus no approval renewal is necessary.

## Dashboard

The dashboard now shows a `superseded` state and a filter for it.
A row gets this state only when a reviewed mapping names a completed replacement.
The queue lifecycle and the runner selection do not change.
After a restart, the dashboard shows 715 complete, 82 superseded, 6 blocked, and 2 exhausted jobs.

## Remaining blockers

| Jobs | Missing input | Owner | Resume condition |
| --- | --- | --- | --- |
| `hcf402-factor-small-controls`, `hcf402-factor-wide-controls` | The Fixture reports `rendered_body_geometry` as `unavailable` with `non_affine_transform` for the 72-point and wide controls. This occurs on the first HCF-profile frame. | Sillycon-TTR owns the Fixture source. Maximum-mini-NUIAK verifies it locally. | A Fixture build reports measured body geometry for every planned control in both profiles. Then register `-r2` capture successors. |
| `hcf402-report-r2-small-controls`, `hcf402-report-r2-wide-controls`, `hcf402-measure-small-controls`, `hcf402-measure-wide-controls` | Completed captures from the row above | Maximum-mini-NUIAK | Register report successors that depend on the `-r2` captures. Approve them after a fresh check. |
| `hcf396-14-ttr-verification` | Actual observer inference and a receipt for `nuiak-hcf396-observer-v1` | Sillycon-TTR | Sillycon-TTR runs the consumer check after native Autonav qualification. Maximum-mini-NUIAK pins the receipt in a new successor. |

Do not substitute requested bounds for unavailable native geometry.

## Backlog promotion

No BACKLOG405 task is ready with existing inputs and templates. Thus no batch is registered.

- T37 already covers all 9 completed native captures through `native404-selection-00`–`08`. T40 joins those results.
- 23 tasks need the missing `detector-case-match` adapter (ENG405-02).
- 12 tasks need `temporal-evaluation`, and 11 tasks need `representation-comparison`. Neither adapter exists.
- The T03 and T03-ios tasks need qualified Fixture recipes and focus manifests from Maximum-mini-TTR.
- The T07 and T11 tasks need new native data, a frozen pipeline, or actual Sillycon-TTR inference.
- B405-002 needs a scored box-intervention adapter. Its 74 retained frames are available.

The ready duration is 0 s. Adapter work produces the next ready jobs. A new capture does not.

## Result — PROGRAM384-D1 seed variation

The runner completes the 5 v2 jobs. Each training run takes about 1,037 s. Each evaluation takes 14–16 s.
All 3 seeds use the same initialization, membership, 30 epochs, and thresholds 0.15/0.85.
The comparison uses the same 1,408 retained views.

| Role | Views | Groups | Seed 42 correct | Seed 43 correct | Seed 44 correct | Varied views | Lost baseline successes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Training | 1,392 | 5 | 1,136 | 1,091 | 1,116 | 49 | 0 / 3 / 0 |
| Development | 16 | 1 | 8 | 8 | 8 | 0 | 0 / 0 / 0 |

Seed 43 loses 3 of the 1,005 pinned baseline successes on training views. Seeds 42 and 44 lose none.
The correct count varies by 45 views (3.2 points) on training views. Only the seed changes.
Of the 49 varied views, 44 are in groups s0–s2. Seed 42 is correct on 48 of them.
The development role has 16 views from 1 group. It cannot show seed stability.

Decision:

- A single-seed comparison cannot attribute a difference of 45 training views or fewer to a correction.
- The 0-loss rule can reject a seed of an unchanged recipe. Seed 43 is an example.
- Keep the rule unchanged. A gate change needs the maintainer's decision.
- For a later candidate, compare 2 or more seeds, or require losses outside the measured seed-variation set.
- Model acceptance stays false. Related views are not independent trials.

## Validation

- `test_reconcile_research_jobs`, `test_research_dashboard`, and `test_research_dashboard_descriptions` pass 87 tests in 55 s.
- The reconciliation tool verifies all 66 successor results and output hashes.
- The dashboard restart passes its health check. The runner waits for approved work.
