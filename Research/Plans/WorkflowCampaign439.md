# WORKFLOW439 — Bounded experiment campaigns

Owner: Maximum-mini-NUIAK. Date: 2026-10-18.

## Contract

`workflow_campaign439.py` compiles one request through the existing queue and template compiler.
The request has `version`, `id`, `decision`, and `branches`.
Use version `workflow-campaign-v1`.

The `decision` field contains exactly one of these choices:

- `plan`: an embedded `model-decision-batch-v1` plan.
- `reuse`: a pin for an existing compiled decision graph.

An embedded plan can include T05 preparation, T06 training, and T37/T63 scoring in one execution batch.
The compiler does not repeat reused training, scoring, or decisions.
Preparation must satisfy the selected template's current binding contract.
T03, T05, T06, and T07 still require pinned inputs at binding time.
Use a pinned `crop-membership-plan-v1` for pending preparation.
Its ordered rows freeze `id`, `role`, `profile`, `group`, and `label` before execution.
The training dependency names the preparation specification and `crops.json` output.
The existing bridge checks every produced row against this plan before calling the trainer.
Crop paths and hashes come from the verified producer output, not invented future pins.
Unknown membership remains blocked. This contract does not approve unknown labels or change data roles.

Each branch has `when` and `jobs`. Supported conditions are `supported` and `contradicted`.
An inconclusive decision releases neither branch. Evidence failures also release neither branch.
Each job uses an existing template description or the fixed `decision-audit` action.
The audit action requires only `id`, `kind`, and `question`.
It separates absent proposals, retained regressions, and regressions with positive maximum scores.
It does not infer that a positive maximum score proves correct ranking.

The request permits up to 8 branches and 32 follow-up jobs.
Template follow-ups permit diagnostics and training only. Existing training contracts and approval checks still apply.
Capture, export, promotion, arbitrary commands, recursive expansion, and automatic retries are not part of this contract.

## Admission and recovery

Compilation writes immutable metadata, not live jobs.
The compiler uses a metadata-only binding directory to resolve references through the existing template compiler.
No runner executes that directory.
Registration validates all specifications, source pins, existing dependencies, and immutable conflicts before writing live jobs.
Each approval names an explicit job ID. Registration alone grants no authority.
Revoked IDs cannot be restored through this command.
Interrupted registration resumes with the same identities. Completed attempts remain unchanged.
The existing runner checks conditions, approval, inputs, and resources before execution.

## Two real descriptions

Both requests remain under `reports/work/WORKFLOW439`.
They reuse the completed Standard-only and omitted-tab graphs.
Each registers a contradicted audit and a supported audit with individual approvals.
The detached runner completes both contradicted audits. Both supported branches remain unexecuted.
No training or scoring repeats occur.

The Standard audit finds 68 focused observations without proposals in each Standard proposal arm.
Its 3 lost known-box selections have positive maximum margins.
These cases need competing-score inspection, not an assumed threshold correction.
The consumer comparison also loses 1 positive crop.
The omitted-tab audit preserves the recorded 2 lost consumer successes.
These observations reuse development evidence. They do not qualify a model replacement.

## Graph metadata and duration

The read-only companion reads owner and condition fields from exact matching job specifications.
Changed hashes, invalid paths, missing files, and oversized specifications produce explicit metadata gaps.
The companion does not import worker modules or change execution authority.

Duration samples come from completed queue records with matching execution, input, template, training, capture, staging, and dependency identities.
Failed runs and nonfinite durations do not supply samples.
The UI reports ready work and conditional waits separately.
If any job lacks a comparable sample, that category's duration remains unavailable.
Summed durations describe serial work, not a promised completion time.
Runtime samples do not verify model quality or artifact validity.

The companion reload changes port 8766 only. The runner on port 8765 keeps its process and state.

## Validation and limits

Isolated queue tests cover two descriptions, both selected outcomes, failed producers, interrupted registration, repeated admission, and revocation.
Other checks cover changed inputs, immutable conflicts, existing-template branches, duplicate cases, and metadata integrity.
The real queue proves both audit executions and closed alternative branches.
Logs remain under `reports/work/WORKFLOW439`.

The final Python suite passes 63 tests in 37.9 s.
Offline Swift checks pass 177 Swift Testing cases and 14 XCTest cases without failures.
The Swift Testing run takes 53.4 s. `git diff --check` also passes.
JavaScript checks cover graph projection, layouts, branches, blockers, and incomplete duration history.
The 2 real audit jobs complete through the detached runner. Their alternatives have no attempts.
Preparation tests compile pending jobs without crop bytes and verify the existing training bridge with a stub trainer.
Those tests do not claim a new real training run or new model quality.

The initial estimate is 60–90 min. Total active implementation time was not instrumented.
The report records measured validation time instead of inventing an elapsed total.

This tranche does not create overnight capacity. Its useful diagnostics are short.
The compiler supports one T05 producer per decision batch with frozen training and development membership.
It rejects duplicate identities, group leakage, unknown roles, and unrelated preparation jobs.
The existing queue resolves produced crops after preparation completes.
The bridge rejects changed labels, groups, profiles, roles, or missing rows before training.
This simpler contract avoids automatic publication of newly invented training specifications.
Do not claim that every template supports future inputs or unknown membership.

## Next priority

Use these descriptions for a justified Standard proposal comparison before another classifier fit.
Keep preparation separate from the native storage recovery requirement.
If a producer cannot declare its membership, add a separate admission review before training.
Do not invent future labels to make a graph ready.
