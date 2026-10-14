# Focus learning priorities and implementation plans

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

This plan turns the methodology review into bounded work that can improve focus models.
Start with qualified native examples and useful comparisons. Add a new model only when a defined test supports it.
`Tasks.md` remains the only work queue. This document defines requirements and implementation, not live execution status.

[ADR-0027](../ADR-0027-Evidence-Guided-Experiment-Graphs.md) proposes how these packages form a graph of evidence and decisions.
Its conditional execution changes remain proposals. Existing queue behavior stays unchanged.

## Scope and authority

The maintainer approves project planning and technical plans in this turn.
No new experiment starts, queue specification changes, downloads, or worker dispatches occur here.
Existing approved execution continues unchanged.
Existing HCF work keeps its 48 GPU-hour, 50,000-frame, and 250 GiB study limits.
New model and optimization proposals require a frozen run contract and applicable approval before submission.
Do not charge unrelated transition experiments against the HCF budget without an explicit allocation.

## Evidence that sets priorities

- FOCUS348 reduces authored false changes from 587 to 26 but loses 72 correct movement decisions against its control.
- GENERATION354 retains essentially all measured movement evidence in the original detail windows, yet every model misses the tested movements.
- FOCUS355 already tests trainable whole-frame features. It does not justify repeating that comparison unchanged.
- FOCUS358 extends training to 30 epochs without gaining native movement successes.
- HCF362 verifies native setting restoration but finds a clipped Settings text mismatch during queued capture.

Sources: [FOCUS348](../Focus348Results.md), [GENERATION354](../Generation354Results.md),
[FOCUS355](Focus355.md), [FOCUS360 review](../Focus360LocalAnswers.md), and [HCF362](../HCF362Results.md).
These results support better native comparisons. They do not prove that one new architecture will work.

## Work packages and order

| Priority | Package | Question | Owner | Required input | Deliverable |
| --- | --- | --- | --- | --- | --- |
| P0 | A: Native capture reliability | Can we make repeatable examples with the actual OS HCF setting? | research-host-NUIAK; TTR repair owner requires confirmation | Repaired observation handling and fresh target checks | Qualified producer and repeatability report |
| P0 | B: Balanced benchmark | Can our evaluation expose movement misses and misleading appearance separately? | research-host-NUIAK | Existing manifests first; qualified new capture for gaps | Frozen roles, coverage table, and scoring contract |
| P0 | C: HCF baseline and learning | Does a learned detector improve on rules under native HCF? | research-host-NUIAK; worker-host-NUIAK for accepted training handoffs | A and B; admitted HCF frames | Matched rules, crop, and detector comparison |
| P1 | D: Transition model restriction | Does training on qualified native examples resolve the existing branch failure? | research-host-NUIAK; worker-host-NUIAK for accepted training handoffs | B and training-eligible paired examples | One justified comparison with full regressions |
| P1 | E: Pretrained visual features | Does a pretrained encoder separate cases our current features cannot? | research-host-NUIAK; worker-host-NUIAK for accepted feature extraction | B; approved weights, license, memory, and adapter | Frozen-feature comparison and feasibility decision |
| P2 | F: Weak-group learning | Does group-aware training help without hiding movement losses? | research-host-NUIAK | B and a useful C or D baseline | Balanced-sampling versus group-aware comparison |

B can begin its retained-data audit while A waits for repair.
C and D answer different tasks: single-frame selection and paired focus change.
E starts with one task and fixed membership, not a combined leaderboard.
F waits for reliable group labels and a useful baseline.
Temporal segmentation, SAM 2, and model distillation remain future proposals. Do not add their compute to this tranche.

## Completion and decision rules

Software completion means tests and the real queue entrypoint pass.
Research completion means the comparison answers its question or records a specific evidence limit.
Replacement acceptance requires existing gates, including no lost successes on the frozen retained suite.
A failed replacement can still complete its research task.
Do not relax deployment thresholds or label requirements to obtain a passing result.

Report correct selections, wrong selections, movement recall, false changes, abstentions, and coverage where each metric applies.
Report localization separately from selection. Report settling only when timed labels support it.
Count independent groups separately from frames, reversals, crops, seeds, and execution jobs.
Use paired group comparisons where support permits them. Report uncertainty and insufficient support explicitly.
Do not use repeatedly inspected development cases as untouched final evaluation.

## Technical plan A

Reuse HCF361 qualification and the HCF362 producer. Do not create a second capture service.

1. Reproduce the saved clipped-row disagreement using TTR's observation tests.
2. Require the repair to retain page, focused-row, value, and restoration checks.
3. Qualify the exact signed TTR build and installed Fixture identity.
4. Check the exact Simulator target and existing recovery records.
5. Verify native Standard/HCF/Standard behavior and restoration.
6. Register new immutable successors for the 3 pilot captures and their comparisons.
7. Let the background runner execute the accepted batch.

Never clear the recovery guard solely because no process runs.
Require verified state, closed session, restored scene, and the recorded recovery decision.
Preserve failed attempts and original specifications.

Acceptance requires repeat captures under both observed profiles, correct focus observations, valid geometry, and verified restoration.
Compare visible effects against within-profile variation before qualifying a control family.
Unsupported families remain explicit. An enabled setting alone does not prove a useful visible cue.

The current pilot limits remain 800 s and 100 MB per job, with separate bounded TTR receipt storage.
Larger capture jobs use the explicit HCF study contract, not repeated diagnostic limits.
Add tests for clipped text, actual row changes, wrong focus, missing observations, interruption, and restoration failure.

## Technical plan B

Extend existing manifests, evidence reports, and comparison scripts.
Reuse HCF361 group design and FOCUS360 E04 rather than duplicating their queues.

1. Inventory existing cases by source domain, data role, family, control size, position, and observed focus state.
2. Identify missing positive and negative cases within each supported family.
3. Freeze related template, artwork, profile, and journey groups before selection.
4. Define matched movement-only, content-only, combined-change, and unchanged comparisons.
5. Register producer dependencies only for missing eligible coverage.
6. Freeze the development selection rule before inspecting new model scores.
7. Reserve separate calibration and final-audit groups before training.

Use modest content edits as well as complete artwork changes.
Measure change area and strength; do not let all content negatives dwarf every focus movement.
Requested parameters are not labels. Retain observed focus, per-frame bounds, timestamps, and capture brackets.
Keep Office as inspected real-device development evidence. Unknown labels do not enter accuracy totals.

Acceptance requires a coverage table with both outcomes, explicit unsupported cells, and a successful group-overlap audit.
Zero-support metrics remain unavailable. A benchmark with only unchanged pairs cannot accept a transition model.
Test duplicate predictions, conflicting labels, cross-role ancestry, stale frames, and unsupported themes.

## Technical plan C

Implement the existing HCF361 blocks rather than registering a second HCF study.
Start with its 1,000 accepted HCF training frames and separate development, calibration, and audit groups.
Keep paired Standard images as comparisons with their own recorded roles.

1. Pin the TTR rules and existing NUIAK models.
2. Score identical eligible screenshots and record proposal recall.
3. Train the resident FocusRing architecture with production crop preprocessing.
4. Train resident YOLO11n to detect the focused control body.
5. Compare deployable proposals separately from known-box diagnostic crops.
6. Run the complete retained suite and per-condition reports.
7. Repeat useful configurations with 3 seeds total before claiming repeatability.

Use HCF361 limits: at most 100 epochs and 4 GPU-hours per run, with patience 10 on development loss.
All runs count against the existing 48 GPU-hour study ledger.
Preserve full resume state and verify checkpoint reload predictions.
Expand to the next data stage only when the existing study decision rule supports it.

Acceptance requires more correct target selections without more wrong selections and no lost frozen retained successes.
If rules match or beat the model, record that result. Do not require a learned model to justify the study.
Core ML conversion follows model selection and the existing export checks.
Measure Apple runtime decisions, numerical parity, package size, and cold/warm latency before optional TTR shadow use.

## Technical plan D

First read the completed FOCUS355 branch comparison and FOCUS356 audits.
Link their exact results in the new contract. Do not repeat frozen-versus-trainable training on unchanged authored inputs.

The proposed new question is whether qualified native training examples correct the branch failure.
Keep previously inspected native development cases outside training.

1. Use B to define new training-eligible native pairs and matched content negatives.
2. Run the existing gradient diagnostic from FOCUS360 E01 without updating weights.
3. Check whether a tiny verified training subset fits before spending the full budget.
4. Select one comparison: frozen versus trainable branches, or inherited versus fresh initialization.
5. Hold membership, preprocessing, update count, and selection rules constant within that comparison.
6. Measure target changes and every previous-success set automatically.

Do not change initialization and trainable layers together when attributing the result to one factor.
A reused control needs identical settings and verified inputs. Otherwise, budget a matched control.
Use existing trainers and branch reports. Preserve original-resolution crops.
Set exact epochs, time, memory, output, and aggregate compute before submission; this plan grants no new run budget.

Acceptance is a decision about the tested restriction, even when neither candidate qualifies for replacement.
If verified examples do not fit, inspect labels, preprocessing, and optimization before adding more data.
If training fits but separate families fail, prioritize coverage or representation rather than more epochs alone.

## Technical plan E

DINOv3 is a candidate feature extractor, not a proven focus detector.
Its dense features preserve spatial information. Test that benefit before planning a production integration.

1. Inventory resident weights and approved licenses before proposing any download.
2. Select one small encoder and one task from B.
3. Record the exact source, weight hash, license, preprocessing, and output feature shape.
4. Measure peak memory and extraction time on a bounded representative sample.
5. Cache features using image, crop, model, and preprocessing hashes.
6. Train a small output layer on frozen features.
7. Compare with the current encoder under the same role assignments and output-layer protocol.

Use original task-appropriate crops. Do not stretch images or remove small cues merely to fit a default encoder input.
Report compute cost and pixel-resolution differences when equal representation budgets are impossible.
Choose the development metric and minimum useful gain before scoring.
Do not tune feature layers repeatedly against final-audit data.

Acceptance requires reproducible features, complete comparisons, and a justified continue-or-stop decision.
A measured representation gain can justify later fine-tuning or distillation. It does not authorize either automatically.
Downloads, installation, export, and exact execution budgets remain explicit prerequisites.

## Technical plan F

Group-aware training gives more influence to poorly performing groups.
It can also emphasize incorrect labels or tiny groups. Check those cases first.

1. Reuse training-only group definitions from B.
2. Compare ordinary balanced sampling with one specified group-aware loss.
3. Hold initialization, examples, preprocessing, optimizer updates, and model structure constant.
4. Report each group's exposure and contribution during training.
5. Compare worst-supported-group performance and aggregate performance separately.
6. Include movement, false-change, abstention, and retained-success reports.

Do not define groups using final-audit failures or inferred model labels.
Freeze regularization and group-weight limits before execution.
Set a minimum supported group size from the available independent data before selecting this experiment.
If support is inadequate, complete the diagnostic and keep training blocked.

Acceptance requires an evidence-backed sampling decision, not merely lower average loss.
Keep this below native capture, baseline learning, and the representation comparison.

## Queue and worker handoffs

Use existing producer, validation, scoring, training, regression, and report stages.
Submit the complete dependency chain together. Do not wait for a chat turn between training and its regression report.
Keep completed attempts immutable. Explicitly reconcile failed target operations before retry.
Do not add placeholder jobs or repeat finished work to fill idle time.

Each accepted handoff contains these fields:

- Task ID, owner, decision question, and existing authority.
- Named immutable inputs, hashes, data roles, and group exclusions.
- Entrypoint, resident environment, resource limits, and storage reservation.
- Expected outputs, raw counts, tests, and acceptance checks.
- Stop conditions, recovery owner, receipt rules, and next consumer.

research-host-NUIAK owns data admission and model acceptance.
worker-host-NUIAK receives bounded training or cached-feature work after input and capacity checks.
TTR owners supply native capture behavior and repair evidence for their assigned targets.
worker-host-Coordinator tracks delivery and missing dependencies, not repository task ownership.
LittleDog can prepare manifests and assemble reports after its existing preparation qualification passes.
Stored, forwarded, accepted, completed, and independently verified remain separate states.
These are planned responsibilities, not messages sent or accepted assignments.

## Program measurements

For each completed comparison, report elapsed time from approved question to usable decision.
Also report capture hours, accepted unique examples, independent groups, GPU-hours, transfer bytes, and manual interventions.
Record previous successes lost and new successes gained beside every model comparison.
Record why a rejected model still changes the next decision, or why the experiment was inconclusive.
Review these measurements after 3 completed comparisons before changing workflow targets.

Keep a rolling estimate of ready work under the existing queue policy.
Do not treat producer-dependent work as ready capacity.
When inputs block compute, prioritize the specific producer or a different unanswered question with resident inputs.

## Research references and limits

[Shortcut learning](https://arxiv.org/abs/2004.07780) supports testing misleading appearance and position cues.
[DINOv3](https://arxiv.org/abs/2508.10104) supports a dense-feature experiment, not a claim of focus accuracy.
[Group DRO](https://arxiv.org/abs/1911.08731) supports testing weak-group performance with appropriate regularization.
These NUIAK applications remain hypotheses. Existing measured results determine priority over paper popularity.
