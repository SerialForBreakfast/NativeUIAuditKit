# HCF490 — Optional observer delivery

Owner: Maximum-mini-NUIAK. Review date: 2026-10-21.
HCF remains optional. Standard and iOS remain unchanged. Navigation remains disabled.

## Latest review — broader fallback and receiving-Mac verification

### Single-weight conversion correction

The broader HCF palette6 check fails partition 2 at 0.019721 maximum error.
Reject that conversion despite its passing partition 4. Preserve both failed conversion variants.
The correction compresses only the largest weight tensor. Element count and name determine selection, not evaluation scores.
Both exports select `const_90_to_fp16`, with 1,228,800 elements. All other weights retain their source precision.
HCF uses 3,811,992 package bytes. The mixed model uses 3,811,994 package bytes.
Both meet the unchanged 5,000,000-byte limit without retraining.
All 7 HCF partitions pass. Maximum absolute error is 0.002618 across 98 crops.
All 7 mixed-model partitions also pass. Maximum absolute error is 0.002744 across the same 98 crops.
Neither model changes decisions at 0.5, 0.7, or 0.85. All output hashes verify.
The background runner executes these checks through T10 and T11. These are short diagnostics, not overnight training work.

TTR host validation checks all 98 crop RGB hashes against the retained production reference. Every hash matches.
It also verifies each parent image hash before cropping. Original images and source checkpoints remain unchanged.
The retained fallback replay uses screenshot-derived proposals, not ground-truth boxes.
TTR passes this replay on 14 full-frame inputs and 98 proposals with the corrected models.
Selected-model decisions, positive decisions, parent hashes, and crop hashes match the frozen reference.
Thirteen TTR host tests pass. Four historical-input tests remain skipped.
The first replay rejects a reference with the wrong digest format. The corrected reference uses TTR's compiled-tree algorithm.
The rejected reference and failed test remain preserved. No validation gate changes.
It does not establish TTR proposal generation or independent app accuracy.
No fallback resources enter the running application. Standard and navigation remain unchanged.

The 7 cached full-screen policy reports also verify their output hashes.
Low-confidence proposals preserve 16/16 HCF selections across 4 retained conditions.
The Standard-profile research comparison gets 13/16. Neither profile loses previous successes or adds wrong selections.
Both proposal thresholds correctly abstain on 3 retained no-focus scenes per profile.
These related profile observations do not create 6 independent scenes.
This evidence supports retained-input consumer verification, not a shipped detector change.

Software checks pass: 30 Python tests and 12 offline Swift tests.
The first Swift attempt finds an old cache with the parked checkout path.
A fresh project-local module cache repairs that build failure without deleting the old cache.

### October 21 source integration and wider conversion checks

Maximum-mini-TTR uses the verified developer Git checkout.
The maintainer approves scoped fallback and lineage source changes there.
The source adds the frozen two-model selection rule and records parent, crop, model, compiler, and source identities.
Navigation stays disabled. The running app remains unchanged.
Eleven focused host tests pass. Four historical input tests remain skipped.
Sixteen candidate preflight checks pass with system Ruby.
These checks do not establish retained-image consumer acceptance.

The background runner exports the exact mixed checkpoint without retraining.
FP16 produces 5,038,126 bytes and fails the unchanged 5,000,000-byte package limit.
INT8 produces 2,612,938 bytes. The initial 8-crop Vision check passes with maximum error 0.00001145.
The wider comparison covers 98 retained proposals for each model, divided into 7 partitions.
Original captures remain unchanged. Verified copies provide project-relative inputs for the existing parity template.
The rejected external-path attempts remain preserved.

Partition 4 fails the existing 0.01 parity limit for both models.
HCF396 maximum error is 0.017066. The mixed model maximum error is 0.026182.
HCF396 scores proposal `hcf402-edge-clearance-hcf-item-3-0-proposal-6` at 0.839332 in PyTorch and 0.822266 in Vision.
This HCF396 difference does not cross the 0.85 threshold. It still fails score parity.
This is conversion evidence, not an accuracy regression or an exhausted training budget.
Do not resume these failed checks unchanged or enable the fallback resources.

Two approved correction chains reuse T10 and T11 with existing palette6 compression.
Each chain tests its exact failed slice before broader qualification.
Batch files: `reports/work/HCF490/palette-correction-batch.json` and `reports/work/HCF490/mixed-palette-correction-batch.json`.
The runner owns execution. These short diagnostics do not provide overnight training capacity.
Remaining acceptance requires broader parity, actual TTR crop hashes, and the frozen full-screen selection comparison.
Standard, iOS, original checkpoints, and previous success records remain unchanged.

The runner completes both palette6 correction chains with verified output hashes.
HCF396 partition 4 now passes: maximum error falls from 0.017066 to 0.006812, with no threshold disagreements.
Six remaining HCF partitions are submitted as regression checks; partition 4 is not repeated.
The mixed palette6 variant fails: maximum error rises to 0.203428 and one threshold decision changes.
Reject the mixed palette6 variant. Preserve the original checkpoint and INT8 evidence.
The next useful mixed-model investigation is conversion precision on the same failed crop, not additional training.
Full fallback acceptance remains blocked. The inactive TTR source build passes its signed package gate in 97.94 s.
The built application contains the verified source revision, source digest, and compiler fields.

Sillycon-TTR reply 1170 confirms receipt cleanup and a local Ruby compatibility repair.
Maximum-mini-NUIAK acknowledges that reply. No later reply is available during this review.

### Source-only continuation

The maintainer requires TTR from Git and local source builds only. AGENTS.md now records this requirement.
The previously registered TTR folder has no Git metadata.
The app project registry also reports that folder is not a Git repository.
The later source integration above resolves the checkout location. No prebuilt application is substituted and no existing TTR session is restarted.

All 9 proposal-recovery scoring jobs complete. Their recorded output hashes verify.
Seven T60 descriptions now compare the fixed fallback on 5 low-confidence arms and 2 additional high-confidence controls.
They reuse completed scores and pin execution receipts. They do not repeat capture, training, or inference.
Batch: `reports/work/HCF490/proposal-policy-batch.json`.
This is short cached analysis, not an overnight workload. The detached runner owns execution.

All 3 broader fallback jobs complete with verified output hashes.
Frozen fallback improves HCF selections from 10/12 to 12/12 across edge-clearance, tall-control, and diamond-decoration development groups.
It loses no previous successes and adds no wrong selections in these groups.
Combined with the original suite, HCF gets 27/28 focused selections. HCF396 alone gets 13/28.
These related development observations do not establish independent app accuracy.
The original no-focus scene remains correct under both profiles. No new no-focus evidence comes from these 3 groups.

| Broader condition | HCF fallback | HCF396 alone | Standard-profile fallback |
| --- | ---: | ---: | ---: |
| Edge clearance | 4/4 | 4/4 | 1/4 |
| Tall controls | 4/4 | 2/4 | 3/4 |
| Diamond decoration | 4/4 | 4/4 | 3/4 |

Standard-profile fallback gets 7/12 here, without losses or new wrong selections.
Four misses lack a sufficiently overlapping proposal. One diamond-decoration miss has a proposal but scores below threshold.
The mixed comparison model is not shipped Standard. Neither these results nor this research policy changes deployed behavior.

### Receiving-Mac acceptance

Sillycon-TTR replies 1141–1149 supply corrected packaging, paired provenance, and additional host qualification reports.
Both named archives pass exact size, hash, bounded extraction, and manifest verification.
The corrected single-case archive now passes the existing single-root extractor without changes.
The paired archive preserves both original images, 5 primary producer states, and 5 reference states marked `not_recorded`.
The reviewed system-Ruby checker passes on Maximum-mini-NUIAK, with macOS 27.0.1 and arm64.
It performs no inference, navigation, network access, or writes. The app check is not requested.
The pair is a Fixture association, not evidence of a commanded transition or an HCF setting change.
Its recorded interval is 4,229.275875 ms. Predictions remain predictions, not training labels.
Local evidence: `reports/work/HCF490/receiver-review.json` and the preserved `pairs-intake` and `review-v2-intake` directories.
BigDog-Coordinator stores exact transfer receipts and acceptance at cursor 1151. Forwarding is not yet confirmed.

This closes passive receiving-Mac intake and paired export verification for these artifacts.
It does not close native UI behavior, app launch, macOS 14 compatibility, cross-app accuracy, or T23.
Sillycon-TTR still supplies compiled-after identity, per-input RGB hashes, candidate IDs, compiler version, and source revision.
Keep the observer default-off and experimental. The fallback is not installed in TTR.

### Next justified correction

Nine approved T37/T57 jobs reuse retained proposals at confidence 0.25 instead of 0.5.
The detector identity and frame membership match in every comparison. Both crop models and focus thresholds stay fixed.
The batch covers edge clearance, tall controls, diamond decoration, small decoration, and 3 retained no-focus scenes.
Two known-box jobs supply missing HCF396 references. Seven full comparisons supply matched low-confidence scores and additional controls.
Earlier tests with another crop model recover boxes but introduce false selections. Do not assume this correction passes.
Apply the existing fallback after scoring. Reject any lost success, new wrong selection, or no-focus false selection.
Preserve the original suite and broader fallback results as regression evidence. Do not tune on these cases.
Batch: `reports/work/HCF490/proposal-recovery-batch.json`.
All 9 descriptions compile and receive exact approval. The background runner owns execution.
Each diagnostic retains 800 s and 100 MB ceilings. Comparable scoring takes about 10 s per job, not hours.
No new captures, model training, source changes, or runner restart are needed.
Follow-up fallback admission waits for verified scoring receipts. No automatic admission is claimed for this batch.
The admission check verifies 2 completed jobs, 5 ready jobs, and 2 normal dependency waits.
The runner completes the no-focus reference and matched high-confidence comparison without intervention.
Completed jobs are not blockers. The 2 waiting jobs depend on the small-decoration reference.
This snapshot covers this batch only. Expected remaining scoring takes minutes, not an overnight workload.

## Verified progress

The earlier claim that actual TTR crop inference remains missing is stale.
Sillycon-TTR returned `ttr-hcf-observer-20261015-reference.json`.
Job `b405-086-receipt`, attempt 1, completes T14 verification.
This review verifies all 3 output hashes and all 3 data input hashes.
It also verifies 15 pins covering the archive, export, parity, runtime, license, model files, and checkpoint.
No inference, capture, or training is repeated.

The returned 8 scores match the reference within 0.000000178814.
There are zero decision changes at thresholds 0.5, 0.7, and 0.85.
The package contains 2,612,923 bytes. The consumer reports Vision, CPU-only execution, and disabled navigation.
These 8 controls come from 2 development frames. This verifies narrow consumer parity, not broad detection accuracy.
T14 does not establish the stronger T23 compiled-digest and full lineage contract.
Do not rename the v1 receipt as v2 or infer missing fields.

## Frozen candidate for integration

Reuse HCF396 from the HCF375C final checkpoint. Do not substitute a later regressing candidate.

| Item | SHA-256 |
| --- | --- |
| Checkpoint | `dc0a8449523c545820b6ff5c04577fb1d0f31d6c7bcd2715b94beabc8a6a5b05` |
| Bundle manifest | `18aa321c5da28511559e5a9a823b0c79d0bbcd06f93e17011614127bca4f8cea` |
| Model archive | `6705a4cf5a434844bac150b605c1cb51b9706ad2e939aee9fb30ee679631a55d` |
| TTR receipt | `c6d8ad7251f6f6c59a8c905b7e0491174abd3c6e9e7eabab48274e6ae01435b1` |

Keep production cropping at 16% expansion and 256 × 256. Keep the 0.85 selection threshold.
Reuse the original export. A new compilation needs its own identity and parity evidence.
The original 264/264 result uses known boxes. It does not qualify full-screen inference.
Later native-control comparisons expose limitations outside artwork. Preserve those failures in the delivery review.

## Remaining consumer requirement

### TTR reply received on October 21

Sillycon-TTR reply at cursor 1111 confirms HCF396 is research-only, not build13's baseline provider.
It uses caller-supplied body boxes with top-left pixel coordinates. Its observer has no qualified ring-to-body mapping.
Production work remains in TTR's EXP-REVIEW-01/02/03: optional provider selection, proposal provenance, and separate results/export.
Maximum-mini-NUIAK sends the exact T23 fields and existing example reference at cursor 1112.
All 4 offered metadata files pass size/hash verification. Exact transfer receipts are stored at cursor 1114.
Peer forwarding and implementation acceptance remain separate from coordinator storage.
The 7 Fixture families were delivered in 4 FOCUS372 archives. Earlier uncertainty about delivery is resolved by the producer inventory.
Local intake qualification still needs reconciliation. Do not request duplicate captures or treat those families as independent apps.

### Retained comparison batch

The initial batch registers 10 approved T37/T57 diagnostics without new scripts.
Readiness detects stale capture dependencies in 8 jobs. Their approvals are revoked; their specifications remain preserved.
Eight explicit `hcf490r2` successors reuse completed `repair478` outputs. All reused dependencies pass verification before registration.
The original no-focus pair completes and is not repeated.
The candidate is the delivered HCF396 source checkpoint. The comparison model is the retained mixed checkpoint, not the shipped baseline.
These offline PyTorch comparisons cover buttons, rows, tabs, decoration, and no-focus under both profiles.
They compare known boxes, detector boxes, and detector-plus-ring boxes using the existing fixed research mapping.
This mapping is not a qualified TTR production mapping. Results cannot establish current TTR integration or Core ML parity on these cases.
Each job retains 800 s and 100 MB limits. These are ceilings, not runtime estimates.
The batch is short diagnostic work, not an overnight training reserve.

Sillycon-TTR must identify the current observer entrypoint and actual proposal source.
Confirm whether the loaded optional model matches this candidate. Build13's reported execution checks do not establish that identity here.
For screenshot mode, return proposal coordinates, ring-to-body mapping, cropping, selection policy, and case-linked output.
For instrumented mode, identify supplied native bounds explicitly. Do not call that screenshot-only detection.
Reuse the existing HCF396/HCF398 handoff and delivered bytes.
Request existing stronger receipts first. Missing metadata does not justify another capture.

## Next bounded batch

Prepare full-screen comparisons after identifying the exact consumer path.
Use retained artwork, native controls, decorative borders, small controls, light backgrounds, and verified no-focus cases.
Preserve source groups and prior failures. Record missing transition or cross-app evidence explicitly.
Compare the candidate with the existing consumer policy on identical inputs.
Report proposal coverage, correct selections, misses, wrong selections, abstentions, lost successes, and runtime.
Use existing templates and the background runner. Initial diagnostics retain 800 s and 100 MB limits per job.
The initial receipt-only review admitted no jobs. The October 21 follow-up above admits the retained comparison batch.
Repeating the completed T14 job would add no evidence.

## State and evidence

Historical admission snapshot: 3 jobs complete, 4 pending, and 3 dependent jobs.
The 3 waits are normal graph dependencies, not missing data. Eight stale-reference jobs remain revoked and preserved.
The runner completed the button reference job without intervention.
The no-focus comparison correctly abstains in Standard and HCF on 1 retained scene per profile.
These related observations do not establish broad no-focus accuracy.
Comparable button jobs took approximately 4 s for T37 and 10 s for T57. Expect minutes, not overnight occupancy.

Candidate and old-receipt reconciliation pass. Current full-screen integration and cross-app qualification remain open.
No model promotion follows. Standard stays unchanged.
Local evidence: `reports/work/research-queue/jobs/b405-086-receipt/attempts/1/`.
Model evidence: `reports/work/research-queue/jobs/hcf396-10-compress/attempts/1/out/export.json`.
Consumer evidence: `reports/work/TTR-INTAKE-20261016/ttr-hcf-observer-20261015/`.

## Completed comparison and consumer handoff — October 21

All 5 full comparisons complete. Their recorded output hashes pass verification.
The candidate is HCF396's source checkpoint. The comparison model is the retained mixed model, not shipped Standard.
Each profile contains 16 focused frames and 1 no-focus frame across 5 retained groups.
Related profile counterparts are not independent evidence. These are development results, not release accuracy.

| Profile and proposals | Mixed model correct | HCF396 correct | Lost successes | Gains |
| --- | ---: | ---: | ---: | ---: |
| HCF detector | 13/16 | 1/16 | 12 | 0 |
| HCF detector plus ring | 14/16 | 3/16 | 12 | 1 |
| HCF known boxes | 16/16 | 4/16 | 12 | 0 |
| Standard detector | 16/16 | 3/16 | 13 | 0 |
| Standard known boxes | 16/16 | 4/16 | 12 | 0 |

The candidate makes no wrong selections in these comparisons. Its many missed selections still fail replacement acceptance.
Both models correctly abstain on the retained no-focus scene under each profile and proposal arm.
Buttons, rows, and tabs fail even with known boxes. Proposal geometry alone cannot fix this candidate's coverage.
Decoration with known boxes passes 4/4 per profile. Detector geometry remains relevant for that family.
For HCF decoration, the combined arm gains item 0 and loses item 1. Aggregate equality hides this regression.
Exact cases and scores remain in each job's `benchmark_summary.json`.
Jobs: `hcf490r2-full-{button,row,tab,decoration}` and `hcf490-full-nofocus`, attempt 1.

### TTR implementation evidence

Sillycon-TTR reply 1117 reports completed source integration with a default-off provider and a separate observer layer.
It reports 82 passing host tests, export/reopen support, provenance, and failure records.
Maximum-mini-NUIAK verifies all 5 offered metadata files by size and SHA-256.
These checks verify received evidence. They do not independently reproduce the host tests or native UI behavior.
Eight retained adapter references preserve decisions. Their maximum score difference is 0.000000000000448.
The production proposal path returns 9 partial proposals, all unfocused.
The nearest proposal scores 0.01005, versus 1.0 for the reference body box. Their IoU is 0.44359.
This is a measured geometry failure on one retained image, not a general accuracy estimate.
Evidence: `reports/work/HCF490/observer-intake/`.

### Decision and remaining work

Do not replace Standard or the retained mixed model with HCF396.
Continue the default-off experimental observer integration. Do not present it as qualified full-screen focus detection.
Keep navigation and baseline selections unchanged. Show supplied-body and screenshot-proposal modes separately.
Sillycon-TTR still owns native UI review and candidate build qualification.
T23 still needs compiled-after observation, per-row input RGB hashes, candidate IDs, compiler version, and source revision.
Do not repeat captures or fabricate these observations. Reuse the retained inputs for consumer qualification.
The independent cross-app requirement remains open. Fixture families are not independent apps.
The next local diagnostics use T61 for buttons and decoration. They reuse saved scores without new inference or training.
These diagnostics separate geometry failures from native-control model failures. They do not authorize learning from evaluation offsets.
Both definitions pass inspect and preview. Both jobs are submitted and approved for the detached runner.
IDs: `hcf490-geometry-button` and `hcf490-geometry-decoration`. Each retains the diagnostic budget of 800 s and 100 MB.
These cached audits are short diagnostics, not overnight work. No execution completion is claimed here.
The coordinator stores the exact transfer receipt at cursor 1118 and the consumer decision at cursor 1119.
Forwarding and recipient acceptance remain unconfirmed. No peer files are removed by Maximum-mini-NUIAK.

## Geometry follow-up — receipt binding repair

Both original T61 jobs fail before geometry analysis with `KeyError: status`.
Their runtimes are 0.508 s for buttons and 0.376 s for decoration.
The batch supplies artifact receipts. T61 requires the producer execution receipt, including completion state and output hashes.
This is Maximum-mini-NUIAK's configuration error, not a model failure or TTR failure.
Preserve both failed attempts. Do not repeat capture, crop scoring, or training.
`geometry-batch-r2.json` uses explicit successors with pinned producer `result.json` files.
Inspect and preview pass. The actual receipt reader also verifies both corrected report bindings.
Both successors are submitted and approved. Each retains the 800 s and 100 MB diagnostic ceilings.
The runner owns geometry execution. No geometry result is available from the failed attempts.

The coordinator returns no new messages after cursor 1119 at this review.
Observer qualification still needs Sillycon-TTR's native UI/build evidence and the missing T23 fields listed above.
The existing consumer handoff already names these requirements. Do not duplicate that request.
The next model correction remains conditional: isolate decoration geometry losses before changing box handling.
Do not apply a blanket inset to native controls. Their known-box failures require separate coverage work.
No threshold change, model replacement, or observer activation is justified by these failed diagnostic attempts.

## Corrected geometry results and selected correction

Both corrected T61 jobs complete. Recorded output hashes verify.
Button analysis takes 0.558 s. Decoration analysis takes 0.507 s.
These timings describe cached diagnostics, not inference performance.

| Family | Profile | Matched control observations | Unmatched control observations | Candidate known-box selections | Candidate detector selections |
| --- | --- | ---: | ---: | ---: | ---: |
| Button | Standard | 16 | 0 | 0/4 | 1/4 |
| Button | HCF | 16 | 0 | 0/4 | 1/4 |
| Decoration | Standard | 7 | 9 | 4/4 | 2/4 |
| Decoration | HCF | 5 | 11 | 4/4 | 0/4 |

Each family contains 1 original group. Repeated control observations and profile counterparts are not independent samples.
No ambiguous matches occur. Button overlaps range from 0.9532 to 0.9778.
Button failures therefore do not justify another proposal-recovery correction.
Decoration has both missing proposals and crop sensitivity. Unmatched controls include nonfocused controls.
Do not equate the 20 unmatched decoration observations with 20 missing focused targets.
HCF decoration items 1 and 2 have overlapping proposals but lose approximately 0.723 and 0.878 in candidate scores.
Their proposal widths are approximately 1.257 times the body widths. Their heights are approximately 1.396 and 1.334 times the body heights.
These findings do not support one inset across all controls. Preserve the existing mapping and evaluation exclusions.

### Next bounded correction

Test the existing T60 abstention fallback across buttons, rows, tabs, decoration, and no-focus.
Use the retained mixed model only when HCF396 lacks a unique selection and the mixed model has one.
Use the existing 0.85 threshold. Keep all boxes, model scores, images, and labels fixed.
Reject the policy on any lost candidate success, lost mixed-model success, new wrong selection, or no-focus regression.
This tests a possible research policy. It does not install another model in TTR or change Standard.
The mixed model is not the shipped Standard baseline. Consumer model packaging and qualification remain separate.
All 5 descriptions pass inspect and preview. The background runner owns their execution.
All 5 jobs are submitted and approved. The actual receipt reader verifies their retained report and capture bindings.
Each job retains 800 s and 100 MB ceilings. No worker restart, new capture, inference, or training occurs during admission.
Batch: `reports/work/HCF490/fallback-batch.json`. These are short cached diagnostics, not overnight training.

### Observer acceptance remains incomplete

The coordinator returns no new messages after cursor 1119 at this review.
The existing TTR source integration report supports an experimental default-off observer, not activation or full-screen acceptance.
Sillycon-TTR must return native UI/build qualification and the missing T23 observations before those checks can close.
Maximum-mini-NUIAK cannot infer or manufacture observations from another machine.
No new captures are required for those retained-input integration checks.
Keep native controls explicitly unsupported by HCF396's current accuracy evidence. Do not hide their failed cases.

## Fallback results and runtime evidence review

All 5 T60 jobs complete. Their recorded output hashes verify.
Total execution takes approximately 2.69 s. This is cached analysis, not model inference time.
Abstention fallback improves HCF correct selections from 3/16 to 15/16 on retained development frames, without lost successes or new wrong selections.
The retained mixed model alone gets 14/16. The fallback adds 1 success against that model without losing its successes.
Standard diagnostic selections improve from 3/16 to 16/16. Deployed Standard remains unchanged.
Both retained no-focus observations still abstain correctly. They represent 1 scene under 2 profiles, not broad coverage.
The remaining HCF decoration miss stays recorded. There are 5 original groups across this suite.
Evidence: `hcf490-fallback-{button,row,tab,decoration,nofocus}`, attempt 1.

Select the fallback for broader regression and consumer feasibility review.
Stop blanket geometry tuning for this tranche. Do not retrain solely to repeat these answered comparisons.
The mixed model is not shipped Standard. Do not silently install it in TTR.
The current observer can remain a separate experimental layer while this policy receives qualification.

### Runtime evidence received from Sillycon-TTR

Reply 1125 reports 115 host tests passing and 1 explicitly excluded live-capture test.
It reports 9 app-process checks across normal, network-restricted, and restarted execution on 3 retained synthetic images.
Both offered metadata files pass size and SHA-256 verification.
Maximum-mini-NUIAK verifies 45 annotation counts, case hashes, partial flags, and disabled navigation fields against the summary.
Normal, offline, and restart phase summaries match exactly.
The evidence reports reopening 3 exports with models disabled and no new inference.
These are bounded producer runtime checks. They do not establish native UI acceptance, second-host behavior, accuracy, or T23.
Evidence: `reports/work/HCF490/runtime-intake/`.

### Exact remaining qualification gap

The meaning of `model_confidence` does not establish the focus probability used for decisions.
Case 0, annotation 5 reports 0.99951171875 with an unfocused decision.
Case 0, annotation 1 reports 0.638671875 with an abstain decision.
These conflict with the displayed thresholds if the field means focus probability.
They may instead represent class confidence. Do not infer a conversion or declare an inference bug without the producer contract.
Sillycon-TTR must identify the field semantics and return the actual decision score, class mapping, and threshold rules.
Case 0 contains 3 focused annotations. Confirm that this remains an ambiguous observer result, not a unique navigation selection.
Native UI review and the previously listed T23 observations remain open.
Accept the received runtime evidence for its declared scope. Do not mark the full optional observer qualified yet.
Request a successor receipt using retained evidence. No new capture or training is needed for this clarification.

## Score semantics resolved and portable intake accepted

Replies 1131, 1133, and 1135 provide the score contract and a portable five-producer review case.
`annotation.confidence` is `is_focused_prob`. The new export also names this value `focus_probability`.
Below 0.7 means unfocused. Values from 0.7 to below 0.85 mean abstain. Values at least 0.85 mean focused.
All 45 prior annotations match this contract without changing their original values or decisions.
All 9 HCF396 annotations in the portable case also pass.
The earlier apparent score conflict is resolved. It was not evidence of incorrect inference.

The pinned compiled model defines auxiliary `confidence` as `2 * abs(is_focused_prob - 0.5)` with FP16 operations.
The compiled MIL file hash matches the export manifest: `bf17718c1835f0a1479fee3ac9cb4fff17b200fd5ad5d6cee06bfa222d19adb6`.
This value measures distance from 0.5. It is not focus probability or calibrated correctness.
TTR receives this authoritative definition. No score conversion is needed for its decision path.

### Portable review case

The 2,097,161-byte archive passes its offered hash and bounded member checks.
It contains 15 files with 2,167,317 expanded bytes. No member script is executed.
The existing recorder extractor rejects multiple root entries before writing extracted files.
Read-only inspection inside the validated archive completes the intake without changing that extractor.
All 8 manifest inventory hashes verify, including the original 3,840 × 2,160 image and its 2,124,863 bytes.

| Producer | Preserved state | Annotations |
| --- | --- | ---: |
| OCR | Complete | 4 |
| Rectangles | Complete | 13 |
| Baseline model | Partial | 9 |
| HCF rules | Complete | 1 |
| HCF396 | Partial | 9 |

All producer identities match the review manifest. Partial states remain partial.
The review issue says `expectedFocus=not_assessed`. Training-label and navigation flags remain false.
HCF396 elapsed time is unavailable. Missing source and profile fields remain unknown, not inferred.
Multiple positive boxes do not establish a unique focused control. The observer has no navigation authority.
Semantic intake is accepted for passive review. It does not admit training labels or qualify accuracy.
The coordinator stores the exact transfer receipt at 1136 and semantic acceptance at 1137.
Forwarding of this acceptance remains unconfirmed.

### Broader fallback regression

Use retained edge-clearance, tall-control, and diamond-decoration groups beyond the initial 5-condition suite.
Keep HCF396, the mixed comparison model, thresholds, mapping, and original data roles unchanged.
Six approved T37/T57 jobs generate the missing matched scores through the background runner.
Reuse the completed detector outputs and original captures. Do not repeat captures or train.
Then apply the same T60 abstention fallback to each group without tuning.
Reject on any lost success from either model, new wrong selection, or failure in retained no-focus checks.
Keep the initial suite's failures and successes in the decision. Additional groups do not establish independent app coverage.
These are short scoring comparisons, not overnight training. Each diagnostic retains 800 s and 100 MB ceilings.
All 6 scoring jobs complete. The 3 full-score jobs pass recorded output checks and receipt validation.
Their runtimes are 10.22 s, 10.86 s, and 9.99 s respectively.
The follow-up descriptions pass inspect and preview. They retain the initial suite as regression evidence without repeating it.
All 3 fallback jobs are submitted and approved for the detached runner. Their results are not claimed in this handoff.
Portable intake checks are recorded in `reports/work/HCF490/portable-intake-review.json`.
This is a one-time semantic audit, not a newly installed production importer.

### Remaining delivery boundary

Score interpretation and passive portable intake are now closed requirements.
Sillycon-TTR still owns native UI review and qualification of the new normal candidate.
T23 still lacks compiled-after observation, per-input RGB hashes, candidate IDs, compiler version, and source revision.
Second-host behavior and broad paired-case provenance remain unverified.
The optional observer is not fully qualified. Preserve the default-off experimental scope and unchanged Standard/navigation behavior.

## Source-built receiver and lower-confidence proposals — 2026-10-21

Maximum-mini-TTR uses Git revision `dd40d8bf802a0e55c5596be24f6e5f44e8d7b331` from the maintainer-supplied Developer checkout.
The signed candidate builds in 77.19 s, below the provisional 15–25 min estimate.
The exact build receipt, package signatures, compiled HCF396 hash, and retained paired case checks pass.
The app starts without replacing an existing TTR process. Passive coordinator status passes.
The feature inventory reports HCF396 available, disabled, and ineligible for navigation.
No capture, inference, device operation, or restart test occurs during these receiver checks.
System Ruby lacks `Array.filter_map` in candidate preflight. An in-memory compatibility shim permits the passive check without source edits.
Native UI review and T23 input lineage remain open. Source build success does not close them.

Seven cached fallback comparisons complete with verified outputs.
Across 4 retained focused conditions, lower-confidence proposals improve Standard-profile selections from 10/16 to 13/16.
The 3 gains are edge-clearance items 0, 1, and 2. No previous success is lost, and no wrong selection appears.
HCF remains 16/16 across those conditions. All 3 retained no-focus scenes remain correct under each profile.
Profile counterparts are not independent scenes. These results are development evidence, not release qualification.
The frozen fallback differs from the current TTR observer. Standard and shipped models remain unchanged.
Next consumer work must verify the frozen policy on retained inputs through TTR before any adoption claim.
