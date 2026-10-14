# Position and branch corrections

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK. Priority: P1. The user approves queue submission and background execution.

## Immediate experiment

GENERATION354 measures missed movements despite retained detail evidence.
It also measures a strong position effect on content-change scores.
Separate training position coverage from the frozen whole-frame branch.

| Arm | Training examples | Trainable layers |
|---|---|---|
| Control | Existing original and authored examples | Detail and correction |
| Position | Same original examples; translated authored examples | Detail and correction |
| Position plus branch | Same examples as Position | Whole-frame, detail, and correction |

Reuse the completed FOCUS348 control. Verify its initialization, 10 epochs, seed, and checkpoint parity before submission.
Do not repeat unchanged control training.
Both new runs start from FOCUS329. Use 10 epochs, seed 42, the existing learning rate, and 2 CPU threads.
Each run permits 1 attempt, 1,800 s, and 2 GiB of outputs.
Previous matched runs take approximately 457–534 s, including preparation. Full-branch training can take longer.
A timeout remains a failure, not a shorter successful run.

Keep the 1,820 original views and their crops unchanged in the primary loss.
Keep the 1,200 auxiliary labels, order, ancestry, and training roles.
Translate only the 960 examples with declared patches and uniform authored backgrounds.
Keep the remaining 240 auxiliary examples unchanged.
Move both frames and all patches together without interpolation, clipping, or wrapping.
Use 9 placement cells with a fixed mapping independent of labels and frame order.
Recompute normal detail crops from translated source pixels.
Record offsets, patch bounds, cell counts, and tensor hashes.
Placement cells describe patch groups. They do not guarantee uniform focused-control centers.
Reject nonuniform undeclared context, invalid bounds, changed hashes, and non-training rows.
Keep preservation losses and thresholds of 0.15 and 0.85.
The broader branch arm changes no architecture or localization layers.

## Automatic comparisons

Queue 24 comparisons per arm:

- 1 retained appearance comparison.
- 5 regression groups: native, replay, global distractions, left distractions, and center distractions.
- 3 retained neighbor and placeholder comparisons.
- 15 GENERATION354 comparisons across movement, content, and repeated frames.

These are 72 evaluation jobs, not 72 independent hypotheses.
Dependencies release candidate comparisons only after complete training and verified output hashes.
Nine partial reports and 1 final report account for all comparisons.
The final report requires target movement gains and zero lost previous successes.
It does not promote a model automatically.
Keep per-arm results to separate position changes from branch changes.
All native development cases remain outside training and final evaluation.
The queue contains 2 new training jobs, 72 comparisons, and 10 report jobs.
Control comparisons can start now. Candidate comparisons wait on their named training jobs.
The existing runner owns execution, progress, cancellation, and failure handling.

## Top 20 research problems

The table separates measured failures from risks that still need measurement.
Each row defines a bounded comparison, not an open-ended sweep.
Require target gains without lost retained successes. Report misses, false changes, abstentions, support, and compute cost separately.

| Priority / ID | Problem and evidence | Data and controlled experiment | Decision and readiness |
|---|---|---|---|
| 1 / P01 | Position bias is measured. Centered content produces a false change. | Translate approved authored patches across 9 cells. Keep labels and artwork fixed. | FOCUS355 tests equal-budget training now. Report regional errors and coverage gaps. |
| 2 / P02 | Whole-frame scores suppress all 10 tested movements. | Use the same position data. Compare frozen versus trainable whole-frame features. | FOCUS355 queues the branch arm now. Require gains beyond position-only training. |
| 3 / P03 | Content scores exceed movement scores in matched cases. | Exchange artwork while fixing observed focus. Match change magnitude across movement and content pairs. | Test hard-negative training after matching succeeds. Needs a producer for matched magnitudes. |
| 4 / P04 | Stronger growth still misses movement. | Use current scale controls for weak, native-like, and exaggerated effects. Reserve native captures for evaluation. | Compare curriculum training with native-strength-only training. Needs reviewed training membership and equal budgets. |
| 5 / P05 | Small effects lose contrast during resizing. | Vary body size and effect width independently. Keep source-resolution crops and background fixed. | Test targeted examples before changing resolution. Existing authored controls work; validate the new split. |
| 6 / P06 | Effect components may interact incorrectly. | Generate growth-only, shadow-only, border-only, and combined effects with existing controls. | Reserve combinations to test cue composition. Needs a frozen split and rendered-effect checks. |
| 7 / P07 | Identical neighbors can hide selection errors. | Repeat identical posters while moving observed focus. Vary spacing independently. | Measure localization before targeted training. Retained controls exist; qualify a broader native producer. |
| 8 / P08 | Unfocused decoration can resemble focus. | Add bright borders, badges, and shadows to unfocused controls. Keep observed focus fixed. | Measure false selections and changes. Verify decoration separately from actual focus effects. |
| 9 / P09 | Clipping and list endpoints lack coverage. | Move controls toward edges in fixed increments. Record visible and full bounds. | Find where detection becomes unreliable. Needs a bounded clipping producer with observed labels. |
| 10 / P10 | Scrolling can resemble focus movement. | Compare fixed-focus scrolling with stationary-screen focus movement. Match direction and displacement. | Test motion compensation against unchanged inputs. Needs observed scroll and focus identities. |
| 11 / P11 | Focus identity can change inside a fixed box. | Use fixed-selector lists with changing content identity in a stable region. | Separate identity change from visual focus movement before training. Needs explicit semantic labels. |
| 12 / P12 | Sparse frames do not measure readiness. | Sample before, during, and after verified focus transitions at recorded times. | Compare causal settling rules first. Needs timed capture with sufficient cadence. |
| 13 / P13 | Stale frames can appear confidently stable. | Replay retained captures with duplicates, gaps, delays, and mismatched instance metadata. | Verify rejection and recovery. Inputs exist; implement a queued disruption adapter. |
| 14 / P14 | No-focus scenes can force false selections. | Pair no-focus and single-focus states in matched scenes. | Test abstention or a no-focus class. Needs verified native absence, not a missing requested ID. |
| 15 / P15 | Modals and loading overlays can interrupt focus. | Insert observed overlays over unchanged content. Include harmless overlays as controls. | Measure missed interruptions. Needs rendering receipts; earlier no-change exports are unsuitable. |
| 16 / P16 | Dense layouts can merge neighboring effects. | Vary spacing, overlap, count, and effect width with fixed artwork. | Test data coverage versus region selection. Composition controls exist; qualify the density producer. |
| 17 / P17 | HCF may help proposals but reduce transfer. | Use peer-host-TTR's matched HCF pilot with verified restoration. | Compare rules, FocusRing, and transitions per mode. Blocked on qualified delivery; do not duplicate capture. |
| 18 / P18 | Sparse layouts and repeated artwork can teach shortcuts. | Use reviewed artwork in dense media screens with held-out asset families and sparse matched controls. | Test realism at equal budgets. Needs qualified recipes, asset rights, hashes, and ancestry. |
| 19 / P19 | Synthetic success does not establish real-app accuracy. | Evaluate fixed candidates on reviewed Office episodes and separately reserved app groups. | Request targeted TTR cases from real failures. More reviewed labels are needed; preserve private data and holdouts. |
| 20 / P20 | Pooled confidence can hide false-stable risk. | Compare pooled and changed-pair calibration on separate groups. Freeze settings before audit. | Report conditional errors, abstentions, and support. Needs eligible calibration membership; do not lower current gates. |

## Preparing later rows

1. Freeze one question and an equal-budget control.
2. Inspect installed TTR controls before requesting new features.
3. Freeze recipes, seeds, artwork ancestry, roles, and maximum outputs.
4. Add a producer job when inputs are missing.
5. Validate pixels, labels, geometry, and groups before releasing consumers.
6. Add training only when diagnostics support it.
7. Queue regression reports with the candidate, not after manual review of training completion.

Use native observations for native labels. Label authored effects as authored.
Keep unsupported themes and layouts explicit. Do not substitute another theme.
Diagnostic jobs use 800 s and 100 MB. Keep specifications immutable and preserve failed attempts.
Do not create variations solely to maintain a queue count.

## Verification

Test translation bounds, unchanged pairs, preserved pixel differences, and label-independent placement.
Test dependency hashes, partial results, missing comparisons, and regression rejection.
Use the existing queue and dashboard for an evaluation smoke.
Run focused tests and one integrated offline Swift check after integration.
Publish capability needs and measured findings to TTR. Messages do not grant new peer execution authority.

## Handoff

All 43 focused tests pass. The offline Swift build and 187 Swift tests pass.
The real queue completes 27 control comparisons and reports before the first new training job starts.
No candidate outcome is claimed. The final report remains dependent on both new runs and their comparisons.
Coordinator cursor 403 stores the TTR questions. Recipient forwarding remains unconfirmed.
Recorded preparation after the coordinator check takes approximately 11 min, excluding earlier context review.
The initial estimate is 45–90 min. Background training is separate from this preparation time.
