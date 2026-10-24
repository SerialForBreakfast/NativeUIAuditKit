# ADR spikes 493: first pass

Date: 2026-10-22. Owner: Maximum-mini-NUIAK.
Standard and shipped models remain unchanged. The detached runner owns execution.

## Latest review: mixed-model scoring and evidence export

### Retained geometry comparison — October 22

The detached runner completes `adr493-ocr-pro-a-geometry` and `adr493-ocr-se-a-geometry`.
Both results pass output hash verification. Each reuses all 30 OCR outputs without capture or inference.
The fixed geometry rule rejects the 2 harmful text-only changes on each device variant.
Both comparisons report 0 gains, 0 lost successes, and 0 new wrong classes against the original detector.
Execution takes 0.036 s and 0.031 s. These are short diagnostics, not overnight capacity.
The device variants share the inspected KitchenSink group. They do not establish independent replication.
The correction preserves baseline results but does not resolve the control class or improve the model.
Keep Standard unchanged. Do not train or promote this rule from incomplete supplied labels.
Next useful evidence is frame-bound semantic role and hierarchy for ambiguous controls, followed by independent annotated groups.
Do not repeat these comparisons with arbitrary geometry thresholds.

Sillycon-TTR reports the export repair pushed at `6e4a55a23932cb8a7c5937c1434a9aed82d4edc6`.
Maximum-mini-TTR remains at `8e4afe5d` during this review. Its matching runtime is not verified.
The supported command is `aatv diagnostics export-recovery RESTART_ID --output NEW_AUTHORIZED_DIRECTORY`.
The next integration step needs a matching source build and the exact retained export receipt.
The 7 remaining cases and 4 session comparisons remain gated. No captures repeat.
Maximum-mini-NUIAK acknowledges messages through cursor 1225 and sends consumer status at cursor 1228.

### Executable OCR comparison connection

`ocr_class_comparison493.py` supplies a reusable request compiler and queue adapter.
The existing Vision OCR helper now offers structured pixel bounds with actual image dimensions.
Legacy text output remains available. No production fusion or detector behavior changes.
The adapter reuses retained detector scores and boxes. It does not rerun the detector.
It divides original groups deterministically before reading OCR results.
A text rule requires one class across at least 2 fitting groups.
Conflicting, absent, low-confidence, or multiple overlapping text regions preserve the baseline class.
Evaluation groups remain separate. Labels never select a correction for an evaluation prediction.
The report includes every supplied label in those evaluation groups, including previous successes.
It records gains, losses, new wrong classes, ambiguous text, group membership, and runtime.
Incomplete native annotations remain explicit. These diagnostics cannot qualify false-positive rates or model release.
This experimental rule is separate from production text association, which does not reclassify elements.

The detached runner receives 2 approved successors: `adr493-ocr-pro-a-r2` and `adr493-ocr-se-a-r2`.
Each uses 30 retained iOS frames, Run013 predictions, and unchanged confidence 0.5.
These are 2 conditions within one investigation, not 2 independent corpora.
Each job retains the 800 s and 100 MB diagnostic limits. Measured runtime is not yet available.
No capture, training, TTR availability, or new dependency is required.
Both jobs use the same adapter with different requests. Neither requires another script.

Focused verification passes 13 tests in 2.673 s.
The actual isolated queue passes a software fixture and rejects an invalid request with `ocr_request_version`.
Software fixtures do not establish real OCR performance. The runner supplies those results separately.
Requests and specifications: `reports/work/ADRSPIKES493/ocr-comparison/`.

The first native executions expose an insufficient 20 s per-image OCR deadline.
They fail after 20.528 s and 34.552 s. The second attempt retains 7 completed OCR outputs.
Both original attempts remain unchanged. Successors verify their receipts and reuse completed outputs.
The per-image deadline becomes 60 s. The total job limit remains 800 s and 100 MB.
The reuse path passes an additional actual isolated queue continuation check.
These failures are OCR runtime failures, not capture failures or negative model results.
The offline Swift suite exits successfully. Its log remains in `ocr-comparison/swift-test.log` beside the requests.

Both corrected jobs complete with verified output hashes: 5.881 s for Pro and 4.197 s for SE.
The SE successor reuses all 7 previously completed OCR outputs.
Each condition learns 1 unambiguous text rule from its fitting groups.
Each rule adds 0 correct detections and loses 2 previous successes in the evaluation groups.
Those losses share the `KitchenSink:13` group across device variants. They are not 4 independent failures.
The same rendered phrase belongs to different control roles across contexts.
Reject this text-only rule. Do not change Standard, production OCR fusion, or detector classes.
The reusable connection is qualified for these development diagnostics, not model release.
The runner finishes this short batch and waits for other approved ready work.
The batch does not provide overnight capacity. No further repetitions of this contradicted rule are justified.

Next useful independent work is a context-aware class diagnostic using these retained OCR outputs and original geometry.
It must define its rule on fitting groups and preserve the newly identified lost cases.
The TTR recovery chain still requires the exact supported evidence export and a delivered source repair.

### Export follow-up

Maximum-mini-NUIAK reads and acknowledges TTR replies through cursor 1209.
Those replies report uncommitted SDK work. The recovery export remains unresolved.
BigDog-Coordinator stores `nuiak-adr493-export-repair-20261022-v3` at cursor 1210.
The message requests an exact app-owned export command, artifact hash, and committed source revision.
It also asks for an existing UI export action, if available, instead of new code.
Storage does not prove forwarding or recipient acceptance. No TTR source changes occur here.

All 6 mixed-model executions finish with verified output hashes.
All 3 pairs have identical scores and identical threshold decisions.
Batch size 8 reduces median total step time from 1.034894 s to 0.891389 s, or 13.9%.
The first size-8 execution is slower than its size-4 partner.
Loading and cache effects remain confounded. The 16 rows include repeated images.
This result supports numerical compatibility on these inputs, not a general speed claim or model improvement.
Production batch settings remain unchanged. Further repetitions of this small test are not useful reserve work.
Evidence: `reports/work/ADRSPIKES493/mixed-efficiency-review.json`.

TTR reply `ttr-sdk-independent-live-20261022-v1` confirms receipt of the export blocker through cursor 1204.
TTR still needs a supported export for the exact persisted restart report.
Its SDK sample supplies app-declared observations, not qualified native focus labels.
The reported SDK changes remain unpushed. They do not unblock the recovery comparison.

The available CLI documents remote-session diagnostics and general cached diagnostics.
Neither documented interface identifies the retained restart operation as an export target.
Do not substitute a remote-session report for the restart report.
The required artifact remains `SimulatorDiagnostics/restart-b838426c-3f16-40bc-8064-f73b584c8d00/report.json`.
Its 4,760 bytes need an authorized app-side export or a human export through permitted access.
The prior marker remains absent. Export must report that absence, not create a replacement.
No capture, restart, resume, TTR source change, or model change occurs during this review.

Before OCR admission, the runner reports healthy continuous operation and waits for approved work that passes readiness checks.
The 4 session comparisons remain approved but dependency-blocked. They are not ready work.
The earlier efficiency-only review admits no new experiment. The OCR successors above supersede that queue status.
Independent preparation remains: observed condition labels for spike 01, context labels for spike 04, and an OCR comparison connection for spike 05.
These missing inputs and capabilities cannot be replaced by more timing repetitions.

## Campaign adapter update

### Approved recovery and comparison successors

The maintainer approves recovery and resume of the 7 unattempted cases on 2026-10-22.
The fresh checkpoint retains 518.902681 s and 1,073,727,860 bytes within its original cumulative budget.
The recovery adapter uses one supported Simulator restart, then resumes the exact manifest.
It preserves the original failed case and refuses duplicate dispatch.
It requires known cleanup, unchanged failed evidence, bounded usage, and verified export before releasing dependent work.
Unknown cleanup or export failure blocks release. Neither failure permits another capture.

`adr493-retained-campaign-recovery` precedes `adr493-session-1-r2` through `adr493-session-4-r2`.
`adr493-session-report-r2` compares all four capture outputs.
The original admissions are revoked. Their specifications, attempts, and dispatch evidence remain preserved.
Each comparison keeps its approved 800 s and 250 MB limits.
The recovery keeps the original producer budget. Its queue allowance includes restart and export overhead.
No source, model, data role, or behavior changes occur in TTR or Standard.

The combined suite passes 50 tests in 12.179 s.
Six recovery tests cover success, duplicate refusal, restart failure, lost resume, failed-case changes, and export failure.
The existing offline Swift result remains unchanged: 177 tests pass across 25 suites.
The idle NUIAK runner reloads the tested adapter. No active execution is interrupted.
Admission is not recovery success. Native results require the runner's completion receipt.

### Recovery execution result

The runner executes recovery attempt 1 in 21.432 s.
The supported restart succeeds with `restart_completed` and `can_run: true`.
The subsequent exact-manifest resume fails with `resourceContended`. Cancellation returns the same error.
A read-only reconciliation confirms that the campaign report remains exactly unchanged.
All 7 cases remain unattempted. The remaining campaign time remains 518.902681 s.
No capture repeats. The four comparison successors remain approved but dependent, not ready.

Source review identifies a recovery contract incompatibility that requires TTR review.
`CampaignRecoveryProof.decode` requires `inventory.count == 1` and the target at index 0.
The companion's restart implementation saves the full fresh host inventory in its restart report.
This restart returns 11 inventory entries. The requested target is present and Booted.
The public restart response also omits cleanup fields required by the proof decoder.
The persisted host report is separate from that response. Its cleanup fields remain unverified.
Do not infer the exact internal rejection branch from the generic error alone.

Required TTR acceptance checks:

- Accept verified restart evidence for the exact target when other Simulators exist in inventory.
- Preserve timestamp, cleanup, target ownership, and manifest checks.
- Test a real companion report, not only a single-target synthetic report.
- Preserve the failed case and resume only the 7 unattempted cases within their remaining budget.
- Return a specific failed recovery condition when proof validation fails.

Sillycon-TTR owns the proposed source repair. Maximum-mini-TTR remains the execution machine.
No TTR repository changes occur here. The repair must arrive through Git and a source build.
Retained evidence: `reports/work/research-queue/jobs/adr493-retained-campaign-recovery/attempts`.
Reconciliation: `reports/work/ADRSPIKES493/recovery-failure-reconciliation/status.json`.
The supported recovery path is blocked. Another restart or resume is not queued.

### Coordinator handoff and independent work

### Efficiency review and confirmed TTR receipt

All six scoring-efficiency executions complete with verified output hashes.
Batch size 8 reduces median total step time from 1.059690 s to 0.921983 s, a 13.0% reduction.
All three paired comparisons have zero score difference and identical 0.15/0.85 decisions.
The first batch-size-4 execution takes 2.379475 s. The median limits its effect but does not remove cache uncertainty.
The evidence covers 16 retained crop rows, one checkpoint, and the CPU backend only.
It does not establish a model improvement, inference-only speedup, or a safe production default change.
Detailed verified measurements: `reports/work/ADRSPIKES493/scoring-efficiency-review.json`.

The next independent comparison uses the frozen mixed checkpoint and reverses the initial order: 8/4, 4/8, 8/4.
One preparation job precedes six scoring jobs. Existing TEMPLATE393 functions supply dependency-aware preparation and scoring.
The newer T07 description compiler refuses unpinned producer outputs. Its restriction remains unchanged.
This comparison needs no new script, capture, training, model installation, or TTR access.
Require the same 0.0001 score tolerance and identical threshold decisions before reviewing median timing.
The previous batch consumes 10.794 s of worker time. This remains short diagnostic work, not overnight capacity.

Sillycon-TTR confirms reading forwarded request 1192 in `ttr-adr493-recovery-evidence-20261022-v2`.
BigDog-Coordinator delivers that reply at cursor 1196. Subsequent replies arrive through cursor 1200.
TTR reports the cardinality repair and 44 final host tests. Source remains uncommitted and not delivered through Git.
NUIAK has not independently qualified that repair. The capture chain remains gated.

TTR requests the persisted restart report and correlated prior marker.
The exact persisted report exists at `SimulatorDiagnostics/restart-b838426c-3f16-40bc-8064-f73b584c8d00/report.json`, with 4,760 bytes.
Normal and scoped-approved content reads both fail with `Operation not permitted`.
The same directory's `prior-recovery-marker.json` returns `No such file or directory`.
NUIAK cannot hash or transfer unread bytes. The public restart response is not a substitute.
Message `nuiak-adr493-proof-access-20261022-v2` reports this requirement through BigDog-Coordinator at cursor 1201.
TTR must identify a supported read-only export, or the maintainer must export the exact report through authorized access.
No restart, resume, capture, TTR source edit, or Standard change occurs during this review.

BigDog-Coordinator stores `nuiak-adr493-recovery-mismatch-20261022-v1` at cursor 1191.
The request names Sillycon-TTR, the exact campaign, remaining budget, receipt hashes, and repair acceptance checks.
Readback verifies the stored message. Forwarding and Sillycon-TTR acceptance remain unconfirmed.
The message does not authorize captures, guard deletion, or Maximum-mini-TTR source changes.

A separate readiness check finds the runner healthy and idle.
The only approved pending independent job is `hcf490r2-native-mixed-parity-7`; its input check fails.
Do not refresh that historical job's pins or repeat it without checking its completed replacements.

The independent ADRSPIKES493-06 batch uses the existing T07 scorer and 16 verified retained production crops.
Its six jobs compare batch sizes 4 and 8 across three paired repetitions: 4/8, 8/4, 4/8.
The CPU backend, 2 Torch threads, model, membership, tensors, and thresholds stay fixed.
The matched retained scorer previously takes 1.465 s. Six runs provide seconds of work, not overnight capacity.
The decision requires maximum score error at most 0.0001 and identical 0.15/0.85 decisions for every pair.
Compare median total step time only after parity passes. Loading and inference times remain combined.
Peak memory and stage timing are unavailable. This small diagnostic cannot establish general throughput gains.
The six executions represent one investigation. They require no capture, training, new script, or TTR access.
All six exact specifications are registered and approved.
At handoff, four executions complete, the runner reports execution five active, and execution six waits on its predecessor.
No comparison outcome or production setting change is claimed before the full batch review.

### Native execution blocker

The follow-up identifies a current blocker through supported `campaign status`.
Campaign `A22DBCB6-F160-4EC1-8FD0-50FA7D801101` remains `cleanup_unknown`.
Its first reference viewport case fails with `cleanupTimedOut`. It has 0 completed cases and 7 unattempted cases.
Fresh evidence is retained under `reports/work/ADRSPIKES493/campaign-owner-review`.
The campaign admission code rejects new work while this retained state exists.
Other campaign blockers cannot be excluded without a supported inventory.

The available `campaign resume` command requires a later verified Simulator restart receipt and fresh readiness.
It preserves failed cases, records recovery evidence, and then starts the old campaign's unattempted cases.
It does not provide recovery-only behavior. `campaign cancel` refuses cleanup-unknown campaigns.
`simulator reconcile` handles Simulator operation markers, not this campaign checkpoint.
Do not use resume merely to clear the blocker while silently admitting the 7 old cases.
The maintainer subsequently approves those additional cases within the remaining budget, as recorded above.
No restart, resume, cancellation, capture retry, or TTR source change occurs during this diagnosis.
The four approved comparisons remain waiting on this explicit boundary.

The diagnostics collector also returns `deliveryFailure: persistenceFailed` with partial cached metadata.
That response remains preserved. It does not establish current ownership or recovery.

The runner attempts `adr493-session-1`. It fails after 2.738 s with TTR `resourceContended` at campaign start.
The three dependent captures and the report remain blocked. No native capture success is claimed.
TTR general status reports no active command or observation. Simulator readiness reports clear ownership.
Those checks do not establish campaign availability.
TTR rejects cancellation and later status for the requested campaign ID with `invalidArgument`.
The adapter preserves its dispatch marker and failure receipts. It does not repeat start.

Source inspection identifies several possible campaign blockers: active work, pending transfer preparation, retained cleanup uncertainty, or a harvest recovery marker.
The returned error does not identify which condition applies. Do not claim a diagnosed stale lock.
macOS denies read access to retained campaign checkpoints, including the scoped permission retry.
Maximum-mini-TTR needs to identify the blocking campaign or transfer and provide its supported recovery action.
This requirement does not authorize a restart, marker deletion, repository change, or new capture.
After reconciliation, use an explicit NUIAK successor. Preserve the failed attempt and all approved limits.

The NUIAK campaign adapter is implemented and integrated with capture approval and execution limits.
The 250 MB exception applies only to the four approved ADRSPIKES493 capture identities.
General capture limits remain unchanged.
The adapter binds the helper hash, Fixture binaries, Simulator, and endpoint before dispatch.
It retains a dispatch marker before starting TTR. A lost reply cannot trigger another capture.
Failed exports preserve producer evidence. They do not cause automatic recapture.
Native intake reuses the existing transition validator for hashes, coordinates, focus, action ordering, and cleanup.
It publishes observed labels with calibration roles. Unknown condition tags remain explicit.

All four jobs and the final report are registered and approved.
The capture order is separate, reused, reused, separate. Each successor requires verified predecessor output.
The report requires matching labels and faster reuse in both paired repetitions before supporting reuse.
Two repetitions provide preliminary timing evidence, not broad performance qualification.
The aggregate capture limit is 3,200 s and 1,000 MB. These limits are not a measured runtime estimate.
Producer capture uses up to 600 s per job. The remaining queue allowance covers export, validation, and cleanup.

The idle NUIAK runner reloads the tested policy with its existing priorities preserved.
No active job is interrupted. Maximum-mini-TTR source and its running app remain unchanged.
The graph service remains unchanged. It uses a different port from the execution runner.

Verification includes 9 adapter tests and the existing queue regression suite.
The combined focused suite passes all 44 tests in 12.624 s.
An isolated actual queue completes the positive software fixture in 0.112 s.
It rejects an invalid configuration in 0.117 s before dispatch.
These fixtures mock TTR. They are not native capture evidence.
The offline Swift suite passes 177 tests across 25 suites in 51.975 s.

See [SDK training requirements](TTRSDKTrainingRequirements.md) for planned capabilities and missing condition evidence.
The sections below preserve the earlier findings and preparation history.

## Delivered

The reusable `failure_review_sampling493` adapter verifies completed comparison receipts and reconstructs outcomes from their original reports.
It verifies matched inputs and original data roles. It rejects changed outcomes and duplicate cases.
It preserves every success in the full report. Sampling changes review membership only.

The admitted job is `adr493-retained-focus-review`.
The background runner completes it in 0.71 s. Its receipt reports success.
It compares retained Standard checkpoints from epochs 30 and 23. These are experimental models, not a shipped-model comparison.
It reuses 456 observations. Proposal methods, profiles, and related frames are not independent trials.
It produces `review.json`, `report.md`, and an artifact receipt.

Private inputs and qualification receipts remain under `reports/work/ADRSPIKES493`.
The submitted job remains under `reports/work/research-queue/jobs/adr493-retained-focus-review`.

## Spike 01: difficult negatives

The retained report supports native no-focus truth and consumer crop labels.
Each native profile includes 4 no-focus observations per proposal method. Both compared checkpoints preserve their correct abstentions.
These observations do not establish broad no-focus accuracy.
The full report preserves gains, lost successes, and newly wrong selections for every method.

Explicit condition labels remain missing for decorative borders, bright artwork, and selected-but-unfocused controls in this input contract.
Do not infer those labels from filenames or requested appearances.
The next data request must identify those conditions and record actual focus, selection state, control bounds, and original ancestry.
No new training is justified by this review alone.

## Spike 03: review sampling

The rule selects unused groups and favors a previously uncovered error category.
Uniform random selection uses the same eligible cases and sample size.
Seeds are 49301, 49302, and 49303.
Categories combine the scoring method and its verified outcome. They are not causal diagnoses.

| Profile | Cases per arm | Diverse categories | Random categories | Diverse groups | Random groups |
|---|---:|---:|---|---:|---|
| Standard | 18 | 4 | 5, 4, 4 | 18 | 10, 9, 12 |
| Optional HCF | 17 | 3 | 3, 3, 3 | 17 | 10, 10, 13 |

Outcome: inconclusive. The rule improves retained group coverage but does not improve category coverage.
Keep random selection as the control. Do not promote this rule as superior.
An iOS detector pool needs its own verified input connection. These are tvOS focus findings only.
No model accuracy or human review-time improvement is claimed.

## Spike 02: session reuse

The maintainer approves 4 Simulator jobs, each within 800 s and 250,000,000 bytes.
No physical devices or settings changes are approved for this comparison.
The active source-built app uses app-managed storage. A project override reaches the wrong coordinator namespace.
The matching helper succeeds without that override. Simulator readiness reports clear ownership and a booted target.
Fixture identity still needs fresh verification before capture.

TTR source revision: `b407305e737badd82d78e4004217cafd50d89c2a`.
The source packet compiler passes its compatibility and rejection tests.
TTR validates all 4 plans. Their order is separate, reused, reused, separate.
Each plan has identical recipe cases: 2 layout variants crossed with unchanged-boundary and moved-scroll transitions.
Each plan requests 4 pairs and 8 endpoint images.
TTR estimates 234,881,024 bytes for capture and export per plan. This is an estimate, not measured storage.
These development measurements retain the producer's calibration role and validation split. They are not admitted training data.

`reuse_runner` supports Simulator transition campaigns only. It does not support ordinary appearance campaigns.
The current NUIAK capture adapter uses its older direct capture path. It cannot execute these campaign plans unchanged.
The TTR Ruby schedule helper also forces project mode and TTR-local output paths.
Do not hide those incompatibilities with a diagnostic job that starts capture outside the capture policy.

Required integration: connect the existing campaign API to the queue's capture policy at a safe activation boundary.
Preserve campaign identity after a lost response. Resume or export existing evidence instead of repeating capture.
Check cancellation, partial export, native annotations, and terminal restoration before reporting throughput.
Keep startup inside elapsed throughput. Do not add nested stage times twice.
The 4 plans are prepared, not executed or counted as ready jobs.
The current capture policy also caps jobs at 100 MB. Activate the approved 250 MB exception only for this bounded comparison.
That integration needs tests before admitting the captures. Do not weaken the general capture policy.

## Verification

- 10 focused Python tests pass.
- An isolated queue completes the real metadata input in 0.55 s.
- An isolated queue rejects an invalid version with `review_input_version` in 0.11 s.
- TTR's source packet test passes incompatible-environment, duplicate-case, budget, and non-transition rejection checks.
- The offline Swift build passes. The serial suite passes 177 tests across 25 suites in 53.69 s.
- The first Swift run stalls. Its process sample remains preserved; only the owned test processes are stopped.
- No capture, training, model promotion, or runner restart occurs in this preparation.

The metadata job adds less than 1 s of measured work. It does not fill an overnight queue.
The useful next tranche is the campaign connection plus separate iOS review support, not repeated metadata runs.
