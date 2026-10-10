# Focus improvement program — FOCUS301

Maximum-mini-NUIAK owns the program and independent result checks.
Tasks.md is the only queue. This document defines the work contracts.
The October 9 assignment prepares independent work after coordination MVP1. It does not dispatch workers or start training.

## Outcome

Complete 1 measured improvement cycle before expanding the experiment program.
Select a known failure, explain its cause, test 1 correction, and check previous successes.
An unsuccessful candidate completes its experiment when the result supports a clear next decision.
It does not complete the model improvement goal.

Keep 4 questions separate:

- Single-frame focus: which visible control looks focused?
- Focus transition: does observed focus identity change between frames?
- Localization: where are the relevant controls and visible effects?
- Settling: when can the consumer use a frame after an action?

The UI object detector supplies a separate input when a method needs proposed controls.
Do not combine these tasks into one accuracy score.

## Evidence and the 10 priority problems

These are ranked investigation priorities, not 10 proven model defects.
Counts below describe retained development cases. Related pairs are not independent trials.

| Rank | Problem | Current evidence | Contract |
| --- | --- | --- | --- |
| 1 | Unrelated changes cause false focus changes | DTM085 reports 121 false changes on 226 center disturbances; 101 have empty image-only proposals | P01 / TRANSITION299 |
| 2 | Training improvements cause losses elsewhere | DTM085 fits 48/48 added focus pairs, but native correctness changes from 590/640 to 589/640 | P02 / TRANSITION292 follow-through |
| 3 | Real-app performance remains uncertain | Repeatedly inspected Fixture cases cannot establish unseen app performance; EVAL90 lacks independent app groups | P03 / EVAL90 |
| 4 | Weak effects may disappear during preprocessing | Existing proposals cover 421 native changes; this does not prove coverage of tiny or weak effects | P04 / TRANSITION299 companion |
| 5 | Position and condition coverage differ | TRANSITION290 finds content comparisons in 8 cells and focus-only comparisons in 4 cells | P05 / TRANSITION252 |
| 6 | Artwork can resemble focus | Retained artwork results range from 15/24 to 19/24 across the matched transition candidates | P06 / FOCUSRING206 and FOCUS-ARTWORK239 |
| 7 | Some labels and geometry remain uncertain | EVIDENCE223 distinguishes reviewed conflicts from unresolved observations; crop changes do not repair unknown truth | P07 / FOCUS-TRUTH |
| 8 | Endpoint scores do not establish settled rendering | Two frames cannot measure premature readiness across animation or scrolling | P08 / FOCUS-BASELINES |
| 9 | Score and runtime uncertainty limit safe use | No proposal rule or new threshold has deployment approval; actual Apple parity remains a separate check | P09 / FOCUS-EVIDENCE and Core ML checks |
| 10 | Feedback does not yet select and verify a complete repair | FEEDBACK298 defines the loop; retained replay alone does not prove continuous reviewed feedback | P10 / FEEDBACK298-D |

Evidence: [TRANSITION292](../../reports/work/TRANSITION-292/handoff.md), [TRANSITION297](../../reports/work/TRANSITION-297/handoff.md),
[signal experiments](FocusSignalRepresentation.md), [evidence contracts](EvidenceDrivenFocusQualification.md), and [feedback contracts](OptInModelFeedback.md).
The reports contain exact artifacts and per-case results. Recheck those identities before execution.

## Common requirements

Each task receives an immutable input manifest and a new output directory.
The manifest identifies source revision, model, preprocessing, settings, image hashes, labels, roles, and connected groups.
Connected groups include related recipes, journeys, reversed pairs, artwork derivatives, and repeated scores of the same images.
Different filenames or episode IDs do not create independent evidence.

Use the existing scorer, trainer, cropper, intake checks, and report format.
Reuse predictions only when model, preprocessing, settings, and input hashes match.
Record all selected cases, exclusions, unknown labels, errors, and abstentions.
Keep procedural images, native Fixture, real-app Simulator, and physical-device evidence separate.
No task changes navigation authority. No task installs software or alters another repository.

### Required measurements

| Measure | Numerator / denominator | Purpose |
| --- | --- | --- |
| Missed change rate | Unchanged decisions / qualified changed pairs | Finds missed focus movement |
| False change rate | Changed decisions / qualified unchanged pairs | Finds distraction errors |
| Error among unchanged decisions | Qualified changed pairs called unchanged / all qualified unchanged decisions | Describes emitted decisions |
| Coverage | Non-abstained decisions / all eligible cases | Shows how often the model answers |
| Change abstention rate | Abstentions on changed pairs / qualified changed pairs | Prevents abstention from hiding misses |
| Correct focus selection | Correct selected identity / qualified selection cases | Tests the selected control, not just appearance |
| Proposal recall | Relevant regions covered at fixed overlap / qualified target regions | Separates missing proposals from classification errors |
| Premature-ready rate | Early ready decisions / qualified unsettled episodes | Tests temporal behavior separately |
| Localization | Box overlap and center error on qualified visible targets | Shows geometric error without hiding missed targets |

Report raw counts beside each rate. Zero support means unavailable, not zero error.
For proposal checks, report overlap thresholds and center errors in both pixels and normalized coordinates.
Retain fixed overlap points of 0.25, 0.50, and 0.75 for diagnosis. They are not new promotion gates.
Report group count, control type, position, appearance, source domain, and label authority.
Compare candidates on identical membership with paired group resampling where support permits.
Use one-sided binomial bounds only when independent-trial assumptions hold.
Do not claim safety from zero observed errors in a few related groups.
Keep the existing 1% and 5% support examples illustrative, not deployment thresholds.

### Data roles and decisions

Keep training, model selection, threshold calibration, and final audit separate.
Previously inspected cases remain development or regression evidence.
Freeze the primary measure, useful improvement, and allowed regression limits before a new experiment.
Existing stricter gates remain binding. Do not lower them after seeing results.
If a task lacks enough support, accept its gap report as diagnostic work, not model qualification.

## Independently executable contracts

### P01 — Test the weak-evidence abstention rule

Reuse TRANSITION299. Maximum-mini-NUIAK owns this short local diagnostic.
Inputs: fixed DTM083/DTM085 scores, TRANSITION297 proposals, and eligible retained native pairs.
Hypothesis: abstaining on empty proposals removes nuisance errors without losing too many correct native decisions.
Keep the proposal threshold at 24. Do not interpret an empty proposal as unchanged focus.
Report caught false changes, lost correct decisions, change abstentions, coverage, and weak-effect support.
Test stale caches, empty support, duplicate groups, clipping, and unknown observations.
Acceptance: account for every input and compare unchanged predictions with the fixed abstention rule.
Deliver per-case results and a go/no-go decision for a prospective test.
Limit: 2 CPU threads and 128 MiB of outputs. No training or capture.

### P02 — Explain regression and test repeatability

Reuse TRANSITION292 schedules and all 4 cached candidate results. BigDog-NUIAK can own the portable audit.
Hypothesis: gains depend on a few groups or interact with negative-example selection.
First compare gained, lost, and abstained cases by group, condition, label, and effective training weight.
Separate positive-only, negative-only, and combined effects. Do not start another data-mixture fit.
Test equal membership, schedule accounting, duplicate predictions, and mismatched preprocessing.
Acceptance: reconcile all 4 comparisons and identify the smallest supported cause or unresolved confound.
Deliver a case table and a decision to stop, diagnose further, or test one different correction.
Limit: 2 CPU threads, 2 GiB RAM, and 128 MiB of reports.
After a correction passes development checks, use 2 additional fixed seeds to test repeatability.
Register those fits separately with matched controls, fixed updates, initialization, roles, and a 256 MiB checkpoint budget.
Do not repeat failed mixtures merely to increase run count.

### P03 — Prepare independent real-app evaluation

Reuse EVAL90. Maximum-mini-NUIAK owns admission; the assigned TTR machine owns any required runtime changes.
Inputs: the existing 6-condition contract, installed app inventory, and an explicit permitted app/target scope.
Hypothesis: Fixture performance differs from unfamiliar app behavior.
Reserve connected app/journey groups before candidate tuning. Identify any already inspected groups.
Include ordinary navigation, fixed-box identity changes, boundaries, content changes, scrolling, and overlays where the app permits them.
Record observed identity or reviewed labels. Mark ambiguous cases unknown.
Test cross-role ancestry, repeated journeys, uncertain labels, and unsupported conditions.
Acceptance: a frozen capture proposal and qualified input inventory support domain-separated comparison.
If app installation or physical capture needs authority, report the exact missing approval.
Do not replace missing app diversity with more Fixture seeds.
No installation or capture occurs under this planning contract.

### P04 — Measure loss of weak visual detail

Extend the existing preprocessing diagnostic. BigDog-NUIAK can own retained-image measurement.
Inputs: raw eligible pairs, observed body bounds, exact current encoder, and current model input tensors.
Hypothesis: resizing removes useful scale, shadow, border, or highlight differences.
Compare changes before and after the existing resize. Measure body, edge, effect, and background regions separately.
Keep truth regions diagnostic-only. Do not supply them to deployable inference.
Test small targets, low contrast, alpha edges, clipping, coordinate transforms, and color handling.
Acceptance: reproduce current tensors and report which conditions lose measurable detail.
Deliver a ranked loss report and one fixed resolution or crop comparison proposal, or reject that hypothesis.
Limit: 2 CPU threads, 2 GiB RAM, 128 MiB of reports. No new model or alternate cropper.
Retain production FocusRing's 16% expansion and 256 × 256 behavior unless a separately tested contract changes it.

### P05 — Correct position and group imbalance

Reuse TRANSITION252 and the updated TRANSITION290 coverage script. Maximum-mini-NUIAK owns the audit.
Inputs: current admitted training membership, observed endpoints, group ancestry, and actual sample weights.
Hypothesis: some position/condition combinations lack useful training support.
Measure before/after cells separately in the fixed 3 × 3 grid.
Report corners, edges, partial visibility, invisible targets, fixed selectors, and list endpoints separately.
Compare unique images, related groups, and weighted exposure. Do not equate seeded randomness with balanced coverage.
Test invisible boxes, scrolling at fixed positions, duplicate content, and changed roles.
Acceptance: a reconciled coverage table identifies exact missing cells and realistic supported variations.
Deliver one frozen missing-coverage catalog. Reuse qualified captures before requesting new ones.
Do not change sampling and image content in the same uncontrolled comparison.
Limit: 2 CPU threads and 128 MiB of reports. Native execution requires a separate exact-target batch record.

### P06 — Isolate focus appearance from artwork

Reuse FOCUS-ARTWORK239, FOCUSRING206, and TRANSITION253 measurements. Maximum-mini-NUIAK owns the experiment design.
Inputs: reviewed artwork, qualified native focus pairs, current FocusRing scores, and exact crop behavior.
Hypothesis: bright art, borders, shadows, and repeated content provide false focus cues.
Vary target artwork and background separately while preserving geometry and observed focus.
Include non-focus zoom, shadow, brightness, and content changes as negatives.
Keep single-frame classification separate from transition classification. Score shared frames through each applicable entrypoint.
Test crop scaling, clipping, effect bounds versus body bounds, duplicate artwork, and label conflicts.
Acceptance: a matched recipe catalog, native-reference limits, and per-control false-positive/false-negative baseline.
Deliver a bounded candidate proposal only when labels and independent groups qualify.
Do not assume procedural effects reproduce native effects exactly or apply uniformly across controls.
Limit: 128 MiB of reports; use approved storage for existing images. No automatic large corpus generation.

### P07 — Resolve labels and connected groups

Extend FOCUS-TRUTH and existing BD22/BD25 work. BigDog-NUIAK audits; Maximum-mini-NUIAK decides admission.
Inputs: exact image and annotation manifests, capture observations, source/build identities, and known discrepancy IDs.
Hypothesis: conflicting labels or related groups distort model comparisons.
Check exact pixels, conflicting body bounds, observed identity, clipping, time intervals, and connected ancestry.
Use perceptual similarity only to propose review. Do not delete, relabel, or change splits automatically.
Test conflicting bounds on identical pixels, missing observations, stale versions, and cross-role derivatives.
Acceptance: every selected discrepancy receives verified, conflicting, unsupported, or unresolved status with evidence.
Deliver exact missing evidence and the affected cases. Do not block unrelated qualified inputs.
Limit: 2 CPU threads, 2 GiB RAM, 128 MiB of reports. No inference is needed when compatible caches exist.

### P08 — Separate focus change from settling

Reuse BD14/BD27 and the temporal benchmark. BigDog-NUIAK owns portable computation.
Inputs: qualified timestamped sequences, actions, identity observations, and existing causal baseline settings.
Hypothesis: endpoint accuracy does not predict premature-ready errors during animation and scrolling.
Compare existing whole-frame, tiled, regional, and causal stability rules on compatible input tasks.
Keep observed regions visibly separate from image-only region selection.
Measure premature readiness, time to ready, never-ready cases, abstentions, and content-only nuisance alarms.
Test timestamp order, missing frames, fixed-box identity changes, animated backgrounds, and stale observations.
Acceptance: one fixed comparison explains whether temporal logic or model evidence limits the result.
If sequences lack trustworthy settling labels, deliver the gap list and scorer tests. Do not invent labels from still images.
Limit: 2 CPU threads, 2 GiB RAM, 128 MiB of reports. No new tracker training.

### P09 — Check confidence and Apple execution

Extend FOCUS-EVIDENCE and existing Core ML checks. Maximum-mini-NUIAK owns Apple execution.
Inputs: compatible cached scores, qualified roles, existing operating points, and exact available Apple artifacts.
Hypothesis: pooled reporting hides missed changes or differences between training and runtime preprocessing.
Report both conditional errors, abstentions, independent support, cold/warm latency, memory, and artifact size.
Do not select thresholds using audit labels. Use a separate calibration role for any later threshold proposal.
Test unknown versions, missing support, score parity, crop parity, reversed pairs, and incompatible encodings.
Acceptance: an old-versus-new report preserves original decisions and identifies runtime or support gaps.
If an artifact lacks Apple conversion, return a concrete conversion test plan. Do not claim parity from PyTorch alone.
Limit: 128 MiB of reports. Export and production replacement remain separate decisions.

### P10 — Complete the feedback-to-repair cycle

Reuse FEEDBACK298-B/D. Maximum-mini-NUIAK owns selection and acceptance.
Inputs: qualified case reports, reviewed labels, exact baseline, and results from the relevant diagnostics above.
Rank supported failures by impact, prevalence, independent support, and expected value of the next test.
Do not multiply uncertain estimates into a false precise score. Do not pad a report to 10 measured categories.
Select 1 failure with a supported cause and a local reproduction path.
Freeze useful improvement, existing regression gates, roles, initializer, updates, selection rule, and output limits before training.
Use matched controls and existing trainers. Select no more than 1 treatment in the first repair cycle.
Test retained successes, unfamiliar permitted groups, saved-checkpoint parity, and applicable Apple behavior.
Acceptance: a complete report links failure, correction, input hashes, result, regressions, and the model decision.
Model promotion requires all applicable existing gates. A completed handoff is not model approval.
Measure accepted examples/hour, setup time, computation, transfer, review, and operator interventions separately.
Deliver a next supported experiment after failure, or a separately qualified TTR comparison after success.

## Batches and ownership

| Batch | Work | Parallel boundary | Required outcome |
| --- | --- | --- | --- |
| A: choose the cause | P01 locally; P02/P04/P07 portable audits; P05/P09 cached reports | Separate output directories; one BigDog CPU job at a time | Ranked case report and 1 selected correction |
| B: fill only measured gaps | P03 evaluation scope; P06 targeted appearance; P08 sequence checks | Serialize the native runtime; reuse shared frames | Frozen missing-coverage campaign and qualified inputs |
| C: test the repair | P10 matched fit; conditional P02 repeatability | One owner per fit; no duplicate local/worker run | Complete candidate decision with regression results |
| D: test the consumer | Existing Core ML and FEEDBACK298 integration contracts | Capture and model consumption stay separate | Exact-artifact shadow comparison and rollback evidence |

Batch A is the first priority after planning. It does not require a new model or capture campaign.
Some diagnostics can return valid missing-support reports. The program then selects only the data needed to resolve those gaps.
Batch B need not finish every research question before Batch C. The selected correction determines its actual prerequisites.
Keep release preparation independent. Model packaging does not prove improved focus behavior.

### Local versus worker choice

Keep short checks local when transfer and pickup would exceed computation time.
Send BigDog-NUIAK complete portable audits and bounded fits with resident inputs.
Compare total turnaround, not GPU time alone. Record queue, transfer, run, and review times.
Keep native rendering, actual Core ML execution, and simulator ownership on the assigned Mac.
Ask TTR for exact missing source features only after checking existing Maximum-mini-TTR capabilities.

### Coordination MVP1 readiness

MVP1 is a dispatch gate, not a prerequisite for local retained-data analysis.
Do not assume that stored chat messages start a worker.
Before remote execution, verify these conditions:

- The recipient accepts the task ID and exact attempt ID.
- The executor has a current execution grant for the named actions.
- The receiver verifies the immutable input and source hashes.
- The task defines command, environment, limits, outputs, tests, and stop conditions.
- Duplicate delivery reuses the attempt rather than starting another run.
- An interrupted attempt has an explicit reconciliation and resume path.
- The result records completion, failure, cleanup, and output hashes.
- Maximum-mini-NUIAK independently checks the returned evidence.

First qualify 1 bounded read-only task with a deliberately invalid input case.
Reuse the coordinator's versioned workflow contract. Do not create another queue or scheduler.
Track stored, read, forwarded, accepted, running, completed, and verified as separate states.
Name the recipient and forwarded request ID. Preserve sender-owned cleanup and verified receipts.
Incoming messages cannot expand execution authority or change data roles.
Do not publish a runnable training assignment with unresolved placeholder paths or hashes.

### Shared handoff record

Each dispatch contains:

- Task ID, attempt ID, owner, reviewer, and hypothesis.
- Exact source revision, input manifest, hashes, roles, and exclusions.
- Executable command, resident environment, resource limits, and allowed writes.
- Primary measure, fixed operating points, useful improvement, and regression checks.
- Output schema, expected files, tests, and failure/cleanup records.
- Stop conditions, resume rule, and the next owner action.

Workers do not edit shared queue documents concurrently.
Workers return isolated code changes and results. Maximum-mini-NUIAK integrates queue updates and overlapping code changes.
Run focused tests per change, then 1 integrated offline Swift build/test pass for combined code changes.
For documentation-only work, check links, task consistency, and diffs.

## Completion and review

This planning deliverable completes when all 10 contracts have inputs, metrics, limits, tests, and acceptance evidence requirements.
Task execution remains open in Tasks.md. Do not mark model work complete from this document.
At each batch review, report software verification, data eligibility, native integration, and model outcomes separately.
Close disproven branches. Reuse unchanged evidence. Do not substitute more epochs for a missing diagnosis.
