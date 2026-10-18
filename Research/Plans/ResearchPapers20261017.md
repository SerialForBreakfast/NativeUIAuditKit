# PAPER417 — research ideas as controlled experiments

Status: planned. No new execution, capture, downloads, or model promotion occurs in this tranche.
Owner: Maximum-mini-NUIAK.
Standard UI detection and focus remain primary. HCF remains an optional, separate evaluation slice.

## Evidence and current work

These papers motivate hypotheses. None establishes NUIAK performance or native tvOS focus accuracy.
The earlier review checked primary abstracts and selected full text. It did not reproduce the papers.
Before implementation, inspect each selected method and its released license, code, and data terms.

Current local evidence changes the order of work:

- DETECTOR417 compares retained iOS and tvOS detections. Reuse its case records before selecting new detector training.
- NCTRL417 compares native-control training with retained artwork. Wait for its complete matched results before selecting a new control checkpoint.
- The corrected HCF kernel covers the inspected artwork groups. Do not repeat the older missing-proposal diagnosis as an unanswered question.
- Native controls and light backgrounds remain distinct problems. Do not transfer artwork conclusions to them.

## Shared experiment contract

Use catalog records and existing templates. Do not add another queue or experiment harness.
Each producer, admission, fit, score, and comparison remains a separate immutable step.
Reuse existing outputs only when membership, source hashes, preprocessing, and settings match.
Store bulk artifacts on the verified USB volume. Check free capacity before production.

Freeze related scene groups, artwork derivatives, and profile counterparts before splitting.
Use inspected cases for development, never a newly named final audit.
Freeze thresholds before comparison. Measure no-focus performance separately from positive recall.
Report missing proposals, wrong selections, abstentions, localization, and supported families separately.
Report gains and lost previous successes using paired case IDs and grouped comparisons.
Do not infer safety from zero errors in a small or correlated sample.

Diagnostics use 800 s and 100 MB per job.
Proposed fits use 30 epochs, 30 min, and 2 GiB per arm unless separately approved.
Match examples, optimizer updates, initialization, and preprocessing when testing a training method.
Measure actual time separately; equal wall time does not guarantee equal training exposure.
Do not convert a timeout into a shorter completed experiment.

## P0: E1 — distinguish focus from convincing distractors

Source: [ConClick, 2026-10-09](https://arxiv.org/html/2610.13268v1).
The paper trains language-guided grounding with target-versus-distractor comparisons.
Our focus-ranking adaptation is an inference, not a reproduced paper result.

Question: Does within-screen ranking reduce wrong focus selections without losing retained successes?

1. Reuse current selection predictions and native labels to identify competing controls.
2. Separate absent proposals from ranking failures. Ranking cannot recover an absent control.
3. Build groups containing the focused control and plausible unfocused controls from the same screen.
4. Use TTR recipes for selected tabs, repeated artwork, decorative borders, and bright unfocused controls only where retained coverage is missing.
5. Train a matched binary-loss control and a binary-plus-pairwise-margin candidate.
6. Keep the encoder, crops, exposure, initialization, and scoring threshold unchanged.
7. Evaluate fixed deployable proposals and known boxes as separate arms.

Freeze the margin on training or calibration data before the comparison.
Do not copy the paper's VLM token loss into the crop classifier.
Test listwise ranking only if pairwise ranking shows a useful effect.

Measurements: wrong selections, recall, abstentions, score margins, proposal recall, and retained gains/losses.
Supported: wrong selections decrease, target recall does not decrease, and retained successes remain intact.
Contradicted: a loss or extra wrong selection blocks advancement. Diagnose the named cases.
Inconclusive: too few competing candidates or missing labels requires more qualified cases, not another fit.

Reuse: T03, T05, T07, T15, T37, T53, and compatible T06 controls.
Gap: a scene-group producer and an optional ranking objective in the crop training adapter.
Owner: Maximum-mini-NUIAK. BigDog-NUIAK may receive a separately approved pinned fit assignment.

## P0: E2 — targeted generation versus balanced generation

Source: [Concentration, Not Uncertainty, 2026-10-07](https://arxiv.org/abs/2610.09807).
The paper concerns camouflage segmentation. Its negative finding does not establish the result for UI detection.
Extend B405-059 rather than duplicate its failure-targeted sampling question.

Question: At equal generation and training budgets, does failure targeting beat random and balanced selection?

Use one qualified recipe population with fixed factor support.
Compare random selection, equal family quotas, and failure-targeted quotas.
Determine failure targets from training/development evidence only. Never use final-audit errors for selection.
Generate one deterministic candidate pool and select matched-sized subsets where practical.
Count unique scene groups, accepted examples, attempted captures, and repeated exposures separately.
A conditional fourth arm concentrates examples on randomly chosen families.
Use that arm only if targeting beats uniform selection; it tests concentration rather than targeting quality.

Begin with a 1,000 accepted-frame planning ceiling per subset, not a required collection volume.
Reuse admitted frames first. Run T44 coverage checks before generating missing groups.
Freeze the final size from qualified support and a measured throughput pilot.
Use one seed for screening. Repeat only a promising comparison with 3 matched seeds total.

Measurements: target-slice recall, wrong selections, retained successes, gains per accepted group, capture time, and training time.
Supported: targeting improves the target slice with no retained losses under equal exposure.
Contradicted: retain the simpler sampler when targeting adds no gain or causes losses.
Inconclusive: unequal coverage or exposure requires a repaired comparison.

Reuse: T03, T44, T53, T54, T55, T56, and existing qualified trainers.
Gap: a general deterministic subset producer and a matched-exposure manifest check.
T54 currently covers a specific native/artwork mixture. Do not claim arbitrary sampler support.
Detector fits wait for DETECTOR417's training adapter qualification.

## P0: E3 — explicit no-target and uncertain-target behavior

Source: [GroundGUI, 2026-10-13](https://arxiv.org/abs/2610.19100).
Its grounding dataset includes refusal scenarios. These are not equivalent to native no-focus labels.
Extend B405-004 and B405-058. Preserve their prior results and exclusions.

Question: Can explicit negative scenes reduce false selections without suppressing valid focus?

Keep these states distinct:

- Native observation confirms no focused control.
- Native observation confirms focus, but the proposal source misses it.
- Observation is stale, conflicting, or incomplete.
- A requested target is absent, although another control may have focus.

Only the first state supplies a no-focus training label.
Keep unknown observations outside supervised focus labels.
Use verified settled native no-focus scenes, decorative borders, selected tabs, and loading/overlay transitions where supported.
Do not label a transition no-focus merely because the detector abstains.

First score the frozen pipeline without retraining.
If false selections occur, compare the current training mixture with a fixed-budget mixture containing verified no-focus negatives.
Keep positive exposure matched or add an exposure-matched control.
Calibrate any rejection threshold separately. Do not combine threshold tuning and data changes in one arm.

Measurements: false selections among no-focus scenes, positive recall, abstentions, unknown-state reporting, and recovery after transitions.
Supported: false selections decrease with no lost positive successes.
Contradicted: reject a change that hides valid focus or converts uncertainty into certainty.
Inconclusive: missing native observations block those cases only.

Reuse: T03, T37, T40, T47, T53, and existing crop scoring.
Gap: a reusable state-evaluation report with explicit truth states and sequence identity.
TTR requirement, if missing: expose observed none versus unknown, timestamps, scene identity, and focus changes in capture receipts.
Acceptance: stale or conflicting observations stay unknown; capture restores the original OS setting; labels reference exact frames.
Do not send a duplicate request before checking existing TTR contracts during implementation.

## P1: E4 — independent mobile UI evaluation

Source: [MUIAnno, 2026-05-17](https://arxiv.org/abs/2605.17656).
Question: Does an independently collected iOS dataset expose failures absent from our generated layouts?

First review availability, license, redistribution terms, annotation guidance, and collection provenance.
Paper availability does not grant dataset reuse or redistribution rights.
Do not download the corpus until its access and storage requirements are approved.

Prepare a class mapping with supported, ambiguous, and unsupported labels.
Keep unsupported labels separate instead of forcing them into current classes.
Audit duplicates and related app screens against existing datasets before role assignment.
Evaluate Run 009 and Run 013 on identical eligible membership using the same inference engine.
Begin with a bounded 100-screen review sample spanning available apps and classes.
Increase coverage only after annotation and license checks pass.

Measurements: matched detection counts, localization, per-class/app support, losses, and disagreement with existing native evaluation.
Supported: distinct trustworthy failures justify a targeted repair plan.
Contradicted: duplication or unusable labels prevents independent-evaluation claims.
Inconclusive: missing license or annotation evidence stops admission, not other research.

Reuse: T42 and T56 after the data adapter qualifies. T55's current native format does not imply MUIAnno compatibility.
Gap: one external-label normalization adapter with an explicit taxonomy and provenance contract.
No training admission follows automatically from an evaluation import.

## P1: E5 — refine training examples before scaling the model

Source: [GoClick, 2026-04-27](https://arxiv.org/abs/2604.23941).
The paper combines a 230M-parameter architecture with data refinement. We test data refinement, not its entire model.

Question: Does removing redundant or irrelevant exposure improve Standard detection at the same update budget?

Reuse E2's subset producer and current detector failures.
Compare uniform eligible sampling against a coverage-preserving refined subset.
Refinement uses label validity, duplicate groups, supported classes, and task relevance.
Do not remove valid hard cases because the current model finds them difficult.
Separate data-quality filtering from failure targeting. E2 tests targeting.
Keep all rare supported classes represented. Report excluded groups and reasons.
Match training updates and initialization. Evaluate the same native development groups and retained successes.

Measurements: per-class recall, false detections, lost successes, unique examples, input wait time, and total training time.
Supported: retain refinement if accuracy improves without losses, or equivalent results use measurably less data-processing time.
Contradicted: reject refinement that removes useful rare-class support or loses retained successes.
Inconclusive: unresolved labels require review before another fit.

Reuse: T44, T42, T55, T56, and E2's new subset producer.
No separate GoClick trainer or Core ML conversion enters this plan.
Model adoption needs a separate cost, license, memory, and conversion review.

## Reusable implementation tasks

These are proposed adapter names, not registered template IDs.
Assign numeric IDs only after checking the current compiler.

| Task | Inputs and outputs | Acceptance and failure checks |
| --- | --- | --- |
| PAPER417-PAIRS | Native labels, crops, groups, and cached predictions → within-scene target/distractor manifest | Preserve crop hashes and roles. Reject cross-scene pairs, unknown focus, and label conflicts. |
| PAPER417-RANK | Pair manifest, initializer, fixed settings → checkpoint, history, exposure and loss reports | Binary-only mode reproduces the control. Missing partners and changed membership fail. Check resume separately for the new loss. |
| PAPER417-SUBSET | Eligible manifest, quotas, seed, selection policy → selected manifest and exclusion report | Same input reproduces the subset. Reject insufficient support, role leakage, and impossible quotas. Reuse for E2 and E5. |
| PAPER417-STATES | Predictions, native truth states, timestamps, groups → state-specific errors and recovery report | Distinguish none, missed proposal, absent target, and unknown. Reject duplicate IDs, stale truth, and missing predictions. |
| PAPER417-IMPORT | Approved source manifest, license decision, taxonomy map → normalized detection labels | Preserve provenance and exclusions. Reject invalid bounds, ambiguous mappings, traversal, altered hashes, and cross-role duplicates. |

Every adapter writes counts, input identities, exclusions, limitations, and `modelAccepted: false`.
Use `benchmark_summary.json` with gains, lost previous successes, and slices when comparison evidence supports them.
Do not fill unsupported metrics with invented values.
Prove each adapter with positive and negative queue tests, then reuse it with a second description.
Do not edit shared execution modules while their pinned jobs run.

## Delivery order

1. Finish the current detector and native-control result review without rerunning completed work.
2. Implement PAIRS and STATES using retained cases. These need no new architecture.
3. Implement SUBSET and qualify equal exposure. Reuse it for both sampling studies.
4. Qualify RANK only when the pair audit finds meaningful distractor errors.
5. Review MUIAnno access and labels before implementing IMPORT or collecting data.
6. Expand approved catalog plans into immutable jobs. Let the detached runner execute them.

Planning acceptance: all 5 ideas have controls, measurements, decisions, budgets, dependencies, and template gaps.
Execution acceptance remains separate. No record is ready merely because this plan exists.
