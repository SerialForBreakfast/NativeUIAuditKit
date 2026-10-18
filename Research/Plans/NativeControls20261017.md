# Native-control crop training — 2026-10-17

Owner: Maximum-mini-NUIAK. Scientific task: B405-177. Parent: GROOM-20261017 decisions 1 and 2.

## Approved scope

The maintainer approves the scoped kernel proposal and native-control training use of B405-042 and B405-167 captures.
The maintainer requires separate development groups. This turn prepares the experiment; the detached runner owns execution.
Decisions 3 and 4 remain pending. No existing specification or original capture changes.

## Kernel handoff

Request `nuiak-native-controls-20261017-kernel-v3` targets Maximum-mini-TTR through the coordinator.
The coordinator stores it at cursor 799. Exact text readback passes.
The coordinator rejects v2 at cursor 796 because `reported_state: review` is invalid. V3 uses `pending`.
It corrects the unstructured v1 message at cursor 793, assigned review `review-969ae6693291c476294a595c`.
The corrected send reports no provider delivery. Forwarding and recipient acceptance remain pending.
Receipts: `reports/work/NATIVE-CONTROLS-20261017/`.

The proposal combines high-quality interpolation, short-side sampling, and an inner search extended by 2 analysis pixels.
Use mapped body boxes before crop classification. Scope remains dark-background artwork posters with optional HCF.
Light backgrounds and native button-style controls remain unsupported. Standard behavior stays unchanged.
Request committed source and regression evidence, not a build. Maximum-mini-NUIAK builds locally.

## Source and role decision

All 4 capture hashes and all 40 image hashes pass verification on 2026-10-17.
Each source is attempt 1, output `artifact.json`, under `reports/work/research-queue/jobs/`.

| Producer | Whole groups approved for training | Frames | Capture SHA-256 |
| --- | --- | ---: | --- |
| b405-042-button | t45-button-group-b042 | 8 | 621805c3a28880f0d1aa8e00d1b3f3af116fc8228a9eb4828d6c9513f3206a5c |
| b405-042-row | t45-row-group-b042 | 8 | bb42cf76de2750b14a04a25797fa1b289fb842a8b0b441a9dab5f997de48d076 |
| b405-042-tab | t45-tab-group-b042 | 8 | aaba61ff44b356ec80fb692d0d2e168e3890f4518619a76423b47c928987519b |
| b405-167-tab-selected | b405-027-tab-group-1; b405-027-tab-group-2 | 16 | 153523bcf2bc6dac65339eb3fb25cd608a391f4c19b8674933d0b8bbd39b215d |

These groups become training sources through a new derived admission record. Original development records remain historical evidence.
The authorization record is `reports/work/NATIVE-CONTROLS-20261017/role-decision.json`.
Exclude these groups and duplicate-connected relatives from future development scores for models trained on them.
Keep profile counterparts, focus positions, content variants, and repeated captures in the same partition.
Deduplicate identical Standard/HCF pixels without losing profile provenance. Use observed focus, not selected state, as the label.
Selected-but-unfocused tabs are negatives. Selection itself is not a focus label.

Only 1 existing group covers buttons and 1 covers rows. A frame-level split cannot provide separate development coverage.
Reserve at least 2 new layout groups per family before training. Include selected and unselected tabs in development.
Change structure, spacing, size, and content; new seeds alone do not establish independence.
Check recipe ancestry, image and crop duplicates, and labels before accepting the split.
These are development comparisons, not an untouched final audit. Existing final-audit membership stays closed.

## Question and controlled comparison

Does adding native-control examples recover native focus selections while preserving artwork and Standard behavior?

Current known-box results: jitter selects 0/24 B405-042 frames and 0/16 selected-tab frames.
The retained model selects 6/24 and 12/16 respectively. Both make 0 wrong selections.
After role conversion, these numbers describe diagnosed training-source failures, not independent evaluation accuracy.

Compare an artwork-only control with artwork plus native-control training.
Use the same initialization, seed 371, batch 16, 30 epochs, fixed-last checkpoint, and production crop preparation.
Keep 0.16 expansion, 256 by 256 stretch, and threshold 0.85.
Preserve existing artwork training and development membership, except duplicate exclusions required by the new admission.
Match actual optimizer updates, sample exposure, learning-rate schedule, and class weighting.
Use repeated sampling after deduplication; do not create duplicate image files to increase exposure.
Freeze family sampling quotas from training counts before registration. Report them in the membership receipt.
Reuse a completed control only when all comparison settings and effective exposure match.
Otherwise plan 2 new fits in a separately recorded tranche; do not silently charge both to the 1 remaining GROOM run.

## Execution graph and blockers

| Step | Template or work | Owner | Unblock condition |
| --- | --- | --- | --- |
| 1 | Native-control admission and crop producer | Maximum-mini-NUIAK | Qualify native-control schema, duplicate handling, role overlay, and crop lineage. |
| 2 | Separate native development recipes | Maximum-mini-NUIAK using Maximum-mini-TTR | Reserve groups and qualify local T45/T03 recipes and target binding. |
| 3 | Frozen membership and exposure report | Maximum-mini-NUIAK | Verify source hashes, labels, group exclusions, sampling, and control compatibility. |
| 4 | Matched control and mixed candidate | T06 | Steps 1–3 pass; compiler accepts exact inputs; ExperimentLog records scope and budgets. |
| 5 | Known-box native selection | T37 | Score both fits and retained baselines on reserved native groups. |
| 6 | Artwork and no-focus regressions | T37/T41 | Score identical retained groups, mapped inner proposals, and fixed box interventions. |
| 7 | Batch review | Existing review/confirm | Apply the rules below and record the next action. |

T04 admission currently requires a localized HCF-versus-Standard pixel difference.
It also treats identical pixels across profiles as conflicting. Native controls can legitimately render identically across those profiles.
Do not weaken the artwork gate. Add a qualified native-control variant with explicit observed-focus and geometry checks.
The native cases also lack the artwork-specific metadata that the existing admission path expects.
T06 needs a verified producer of `crops.json`; capture authorization alone does not supply that producer.

## Decision rules

- Supported: the candidate gains correct selections in each native family against the matched control, with 0 new wrong selections.
- Require 0 lost previous successes on reserved native groups and retained artwork regression groups.
- Require unchanged correct abstention on the fixed no-focus groups and no selected-but-unfocused tab selections.
- Contradicted: any required regression gate fails, or native training gains do not transfer to separate development groups.
- Inconclusive: family support, matched exposure, crop integrity, or a required evaluation arm is missing.
- If supported, plan paired-seed confirmation and actual-proposal evaluation before CoreML qualification.
- If contradicted, separate fitting failure, sampling imbalance, crop representation, and proposal absence before another fit.
- If inconclusive, supply the named missing evidence. Do not promote or repeat unchanged work.

Report correct, wrong, missed, and abstained selections per family and profile.
Report paired case gains/losses, unique groups, crop support, actual updates, runtime, and output size.
Successful known-box classification does not establish detector coverage or navigation reliability.

## Budgets and estimates

Use 800 s and 100 MB per diagnostic or scoped capture job.
Plan at most 2 initial training fits, each 30 epochs, 30 min, and 2 GiB.
Two fits reserve up to 60 min; this is a ceiling, not a runtime prediction.
Retained HCF-only training took 105 s but does not predict the mixed-corpus runtime.
Reserve up to 1 GiB for new captures and derived crops, subject to measured storage checks.
Adapter implementation is an estimated 2–4 h. Capture and scoring estimates follow recipe and membership validation.
## Preparation result and registered execution

T53 admits all 88 frames: 40 training frames in 5 groups and 48 development frames in 6 groups.
The corpus contains 45 unique rendered images. Profile duplicates retain the same label and partition.
All 3 captures finish with cleanup in 344 s. Development includes 2 different structures per native family.
Layout fingerprints exclude content and seed changes when checking separation. Crop checks also reject cross-role pixel duplicates.

T05 creates production crops with 4 seeded jitter variants within 2 px for unique training crops only.
T54 retains 3,075 unique artwork crops and 265 native family-specific crops before repeated sampling.
Both fits use 7,200 samples per epoch, 3,600 per label, and positive weight 1.
Mixed training uses 5,400 artwork samples and 1,800 native samples per epoch.
Each native family supplies 300 samples per label. All unique artwork examples remain in both arms.
Both fits use the same 1,152 development crops and perform 13,500 updates across 30 epochs.

The existing compiler registers 48 jobs under B405-177:

- 3 captures, 1 admission, 1 crop preparation, and 2 membership jobs.
- 3 proposal diagnostics and 6 retained-model baseline evaluations.
- 2 matched fits and 6 native-control evaluations.
- 24 artwork and no-focus regression evaluations, registered in batches of 8.

The detached runner owns execution under the current tranche and standing training approval.
Registered dependencies establish input readiness, not scientific acceptance. Review the complete comparison before any follow-up fit or model qualification.
The native family results are development evidence. They do not establish real-app transfer or an independent final-audit score.

Validation: 57 Python tests pass, including real-source admission and isolated queue execution of both reusable adapters.
Swift validation passes 176 tests with the existing timeout/cancellation test excluded after a sampled stall.
The full Swift gate remains incomplete until that test is repaired or separately qualified.
Evidence and batch descriptions: `reports/work/NATIVE-CONTROLS-20261017/`.

## Queue process changes

The measured 24-hour interval ends at 2026-10-17T19:57:23Z.
It contains 334 finished attempts, including 1 failure, and 12,414 s of execution: 14.4% utilization.
This excludes the active capture duration. Completed attempts do not establish scientific progress.
AGENTS.md now requires complete decision branches, grouped exceptions, and ready duration across qualified tracks.
The iOS track still needs the T46-to-detector bundle adapter. The tvOS track needs qualified detector proposals on retained native frames.
These are implementation priorities, not ready jobs. Do not fill capacity with repeated diagnostics or arbitrary longer runs.
