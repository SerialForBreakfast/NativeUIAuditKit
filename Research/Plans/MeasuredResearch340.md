# RESEARCH340 — measured experiments and local controls

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK. Queue: [Tasks](../../Tasks.md).
Decision: [ADR-0026 amendment](../ADR-0026-Queued-Research-Experiments.md#measured-evidence-amendment--2026-10-12).
Results: [RESEARCH340](../RESEARCH340Results.md).

## Scope and limits

Repair evidence reporting before adding model comparisons. Keep the existing queue and dashboard.
Preserve original specifications, attempts, predictions, models, and data roles.
Do not give model predictions navigation authority.

- Diagnostic limit: 800 s and 100 MB per job.
- Batch limit: 5 jobs normally; up to 10 with shared inputs and sufficient resources.
- Candidate limit: up to 3 justified runs, each with 30 epochs, 30 min, and 2 GiB of outputs.
- Freeze inputs, initialization, comparison settings, thresholds, and membership before execution.
- Keep related scenes, reversed pairs, and artwork derivatives in the same group.
- Keep inspected cases outside untouched final evaluation.
- Stop on failure. Retry only through an explicit request.

## Package 1 — evidence repair

The 100 jobs using `benchmark_evaluator.run` contain assigned scores, not measured accuracy.
Classify these jobs as placeholders without changing their stored files.
Exclude their scores from measured results and rankings. Refuse further execution through that adapter.
Keep replay agreement separate from measured performance.

`research-evidence-v1` requires hashes for the model, preprocessing, settings, predictions, membership, and source images.
Each prediction names its label, data role, group, inputs, theme, and archetype.
The scorer checks hashes, duplicate IDs, complete membership, connected groups, and conflicts between data roles.
Final audit reports also require separate selection membership. Shared groups fail that check.
These checks establish file consistency. They do not establish that a declared label authority is correct.

Report counts, recall, false positives, abstentions, and coverage.
For transition and settling tasks, report missed changes separately from errors among emitted stable decisions.
Report all 21 archetype/theme cells. Unsupported cells stay unsupported.
Do not rank different tasks or memberships together.

Acceptance: altered inputs fail; missing labels fail; placeholder scores never become measured results.
The actual queue and HTTP entrypoints must pass positive and negative tests.

## Package 2 — local dashboard

Use `scripts/research_dashboard_server.py` for live controls. Keep static HTML read-only.
Bind only to `127.0.0.1`. Require a launch token, correct Host, and matching Origin for changes.
Accept existing job IDs only. Reject commands, arbitrary paths, oversized bodies, and unknown fields.
Use the shared runner lock. Child processes retain execution leases after a parent failure.
Cancel only the process group created by the current runner. Never cancel a stored PID.

Place the current task above the table. Show its purpose and decision rule.
Show actual worker progress, current step, completed units, total units, and elapsed time.
Show stop-after-current and cancellation controls. Keep completed attempts unchanged.
Use at least 3 matching measured execution records for an ETA range.
If comparable history is absent, show `ETA unavailable`.
Escape all displayed data. Do not load remote scripts.

Acceptance: HTTP tests cover start, duplicate start, stop, cancellation, authentication, output limits, and changed inputs.
Browser review confirms the real queue can start a qualified diagnostic.

## Package 3 — experiment batches

Immutable specifications live in `Research/ResearchSpecs/RESEARCH340`.
Blocked specifications name missing inputs. They do not execute fabricated comparisons.
When inputs become available, register a new revision. Do not edit an existing submitted specification.

| ID | Measurement | Available work or missing input | Next decision |
| --- | --- | --- | --- |
| A1 | Decision changes after artwork exchange | Cached training precheck; controlled new scenes remain pending | Test appearance bias with fixed geometry |
| A2 | Contribution from each effect | Independent growth, border, shadow, and tint controls | Keep useful components and reject harmful combinations |
| A3 | Errors at matched pixel-change magnitude | Retained pixel audit runs; no matched pairs at frozen tolerance | Generate matched-magnitude controls before fitting |
| A4 | Wrong focus from decoration | Independent decorative controls and explicit focus state | Add difficult negatives if the baseline fails |
| A5 | False selections with no focus | Explicit no-focus authored scenes; verified native no-focus for transfer | Test abstention without treating unknown as no focus |
| B1 | Recall by position | Cached corner precheck; matched center and edge scenes pending | Correct position coverage if differences persist |
| B2 | Error by visible fraction | Clipping control and full/visible bounds | Define supported visible fractions |
| B3 | Decision changes from subpixel shifts | Fractional origins and unchanged focus receipts | Diagnose rasterization sensitivity |
| B4 | Boundary coverage and purity | Retained audit runs; controlled padding and neighbors pending | Preserve original windows; reject harmful replacements |
| B5 | Localization with identical neighbors | Identical-artwork transitions with known control identities | Check artwork shortcuts |
| C1 | Scroll/focus confusion | Scroll offsets, focus IDs, and ordered frames | Separate scene motion from focus movement |
| C2 | Premature readiness and delay | Timestamped sequences and independent settling labels | Check temporal rules before a new model |
| C3 | Forward/reverse decisions and box exchange | Cached decisions run; box exchange is unavailable | Diagnose asymmetric decisions without threshold changes |
| C4 | Missed interruptions | Rendered modal, loading, and overlay sequences | Test interruption handling |
| C5 | Rejection of stale or mismatched frames | A pinned temporal consumer and ordered trace | Verify recovery without false confidence |
| D1 | Native-scale recognition after a curriculum | Effect-strength corpus and equal-budget training arms | Select only if native development failures improve |
| D2 | Error linked to rendering differences | Matched native/authored pairs and aligned body bounds | Correct the renderer before adding volume |
| D3 | Generalization to unseen combinations | Independent components and reserved combinations | Test compositional learning |
| D4 | Interactions among factors | Cached size/width/contrast precheck; theme and spacing coverage pending | Choose the strongest supported interaction |
| D5 | Gain per added example | Eligible pool, exclusions, and equal-budget arms | Compare targeted with uniform sampling |

Cached checks use FOCUS319, FOCUS326, FOCUS329, FOCUS331, and TRANSITION249 records.
They preserve hashes and report missing fields. They do not establish independent native accuracy.
The magnitude check caches at most 4 decoded images. It matches only within an artwork family.
Its fixed tolerance is 10% of the larger magnitude. It does not reuse a negative example within matching.

## Package 4 — candidate decision

Select a candidate only after a supported diagnostic identifies its mechanism.
Use one of these corrections:

1. Correct appearance or position coverage.
2. Preserve missing boundary information without removing previous views.
3. Compare targeted sampling or exaggerated effects against an equal-budget control.

Keep the model, settings, initialization, input roles, and acceptance checks fixed for each comparison.
Report successes gained and previous successes lost on identical membership.
A candidate advances only with a target gain and no lost retained successes.
Current cached results do not justify repeating rejected FOCUS329 or fitting another threshold.
No candidate starts from the placeholder rankings.

## Coordination and ownership

research-host-NUIAK owns scoring, queue controls, admission, and Apple model checks.
TTR owns native observations and capture interfaces. worker-host-NUIAK can run complete portable assignments after qualification.
Worker suggestions do not approve new work.
Request source and controls, not bulk generation when research host can render the required scenes.
Keep authored receipts separate from native observations.
Receive offered files through exact hashes and bounded extraction. The sender owns removal of shared copies.

## Completion checks

- Software: focused tests, browser operation, offline Swift build, and serial Swift tests.
- Data: exact input identities, unchanged roles, explicit unsupported cells, and preserved old files.
- Integration: published receipts and exact-ID message readback; acknowledgment remains separate.
- Model: measured candidate decision, or a precise reason that evidence does not justify training.
- Experiment coverage: account for every requested test. Do not call blocked tests complete.
