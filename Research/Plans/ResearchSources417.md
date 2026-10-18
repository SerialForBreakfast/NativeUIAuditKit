# Research sources and 70 ideas for NUIAK

Owner: Maximum-mini-NUIAK. Review date: 2026-10-17.

## Main recommendation

Prioritize proposal quality, small controls, native coverage, and preservation of previous successes.
Test data selection and training changes against equal-budget controls.
Do not replace the model architecture before these tests explain the remaining failures.
Standard detection and focus remain primary. HCF remains optional.

This review selects 10 relevant ideas from each of 7 discovery sources.
It does not claim 70 new papers or 70 independent experiments.
Several sources suggest different tests from the same paper. Many ideas extend existing backlog entries.
Older work remains relevant when it addresses a measured failure better than a recent method.

The recommendations below are proposed NUIAK adaptations, not reported NUIAK improvements.
No queue specifications, approvals, models, or running processes change through this review.

## Evidence and effort

- **Paper:** an author or publisher source supports the method. Local transfer remains untested.
- **Lead:** a community discussion suggests a question. Its performance claims do not establish evidence.
- **Analogy:** a method from another field suggests a test. It does not establish that the method transfers.
- **Now:** prepare the test using current evidence or existing adapters.
- **Next:** resolve the named input or adapter requirement first.
- **Defer:** expected value does not yet justify the implementation cost.

Effort describes implementation scope, not a promised duration.
**Small** means cached scoring or an existing adapter variant.
**Medium** means one producer or trainer extension.
**Large** means a new model, outside dependency, or substantial data preparation.
Readiness still requires verified inputs and an executable contract.

Backlog numbers below use the `B405-` prefix. They identify related work, not new execution authority.
See [the retained-result audit](ExperimentAudit20261017.md) and [the existing discovery plan](ResearchDiscovery417.md).

## What our results make important

The retained iOS comparison records 228 gains and 66 losses across 180 native development frames.
Of those losses, 48 involve controls between 32 and 64 px high.
The position counts have unequal support. They do not establish position as the cause.

The retained native-control comparison improves known-box selection from 12/48 to 42/48.
Both candidates score 0/48 with the tested mapped proposals.
These results make proposal correspondence and geometry higher priorities than another broad classifier fit.
The raw-proposal comparison also loses a previous success. The candidate does not meet replacement acceptance.

These are development findings from the linked audit. They are not untouched audit results or deployment accuracy.

## 1 OpenReview

OpenReview is useful for methods, revisions, and reviewer concerns.
Some forum pages blocked direct access. Linked author copies supply the method summaries where available.
The first 9 rows use published method descriptions. The final row remains a lower-confidence submission lead.

| ID | Idea and source basis | Proposed test and decision | Recommendation and existing work |
| --- | --- | --- | --- |
| OR01 | [Group DRO](https://arxiv.org/abs/1911.08731) optimizes difficult groups rather than only average loss. | Compare fixed family-balanced sampling with group-weighted loss. Report worst-family errors and lost successes. Decide whether weighting adds value. | Next; Medium. Extend 192 after groups and training controls qualify. Small groups can make weights unstable. |
| OR02 | The same [Group DRO study](https://arxiv.org/abs/1911.08731) finds regularization important for group generalization. | Hold sampling fixed. Compare the current stopping rule with a frozen development selection rule. Decide whether overfitting explains weak families. | Now; Small for retained checkpoints. Extend 192. Do not tune against final audit groups. |
| OR03 | [LP-FT](https://arxiv.org/abs/2202.10054) first fits the output layer, then updates the encoder. | Compare frozen encoder, full fine-tuning, and staged fine-tuning on identical native groups. Count recovered cases and old losses. | Next; Medium. Reuse 191 and 195. The paper does not prove benefits for FocusRing. |
| OR04 | [DomainBed](https://openreview.net/references/pdf?id=HbkNISWzO2) emphasizes controlled comparisons against ordinary training. | Match data exposure and selection budgets before comparing a new loss. Decide whether the method beats a fair baseline. | Now; Small. Apply to 181, 189, and 191. This is a comparison requirement, not another model. |
| OR05 | [DomainBed](https://openreview.net/references/pdf?id=HbkNISWzO2) treats model selection as part of the method. | Rescore retained checkpoints using average versus worst-family development performance. Freeze the rule before a new fit. | Now; Small. Extend 192. Report support so one tiny family does not silently determine selection. |
| OR06 | [AugMix](https://arxiv.org/abs/1912.02781) trains consistency under image corruptions. | Apply bounded appearance changes that preserve focus labels. Compare errors on unchanged controls and real dim controls. | Next; Medium. Extend 043 and 118. Exclude transformations that erase or manufacture the focus effect. |
| OR07 | [mixup](https://openreview.net/references/pdf?id=S1-xmzWCW) combines training inputs and labels. | First inspect whether blended UI images retain meaningful focus labels. Reject ambiguous mixtures before training. | Defer; Medium. Thin borders and overlapping focused items make direct use risky. Do not add a fit yet. |
| OR08 | [BADGE](https://arxiv.org/abs/1906.03671) combines gradient information with batch diversity for active learning. | Compare its selected groups with random and balanced groups at equal capture and fit budgets. Include selection overhead. | Next; Medium. Extend 181 and 184. Avoid selecting many derivatives from one scene. |
| OR09 | [Outlier Exposure](https://github.com/hendrycks/outlier-exposure) uses auxiliary outliers during training. | Compare unfamiliar-screen rejection with verified no-focus recognition. Report both separately. Decide whether one score confuses these states. | Next; Medium. Extend 182 and 058. Unknown appearance does not mean no focus. |
| OR10 | [MonoSoup submission](https://openreview.net/forum?id=ICANwnoGgN) proposes reweighting components of a checkpoint update. | Only after simple controls fail, compare the proposed update transformation with an unchanged checkpoint and simple interpolation. | Defer; Large. Submission evidence is not local validation. Resolve 191 and previous-success retention first. |

## 2 PMLR

PMLR provides stable proceedings and concise author abstracts.
Its strongest contributions here concern evaluation, sampling, and inexpensive training controls.

| ID | Idea and source basis | Proposed test and decision | Recommendation and existing work |
| --- | --- | --- | --- |
| PM01 | [Temperature scaling](https://proceedings.mlr.press/v70/guo17a.html) adjusts confidence after training. | Fit on calibration groups only. Compare wrong selections at matched coverage. Decide whether confidence needs correction. | Next; Small. Extend 009 and 115. Scaling cannot restore missing boxes or change class ranking by itself. |
| PM02 | [Just Train Twice](https://proceedings.mlr.press/v139/liu21f.html) emphasizes mistakes from an initial training pass. | Compare reviewed training-error emphasis with balanced sampling. Measure rare-family recovery and label-conflict exposure. | Next; Medium. Extend 181. Do not mine the frozen audit or amplify uncertain labels. |
| PM03 | [WILDS](https://proceedings.mlr.press/v139/koh21a.html) evaluates real distribution changes. | Reserve native families, app layouts, or capture domains rather than random nearby frames. Report transfer separately. | Now; Small for manifests. Extend 190, 088, and 089. Do not label Fixture variation as real-app transfer. |
| PM04 | [GRAD-MATCH](https://proceedings.mlr.press/v139/killamsetty21a.html) selects data through gradient matching. | Compare selected training groups with random groups at equal exposure. Measure selection time and retained performance. | Defer until 181; Medium. A complex selector needs to beat the simple control including preparation cost. |
| PM05 | [Distilling the Knowledge in Data Pruning](https://proceedings.mlr.press/v267/ben-baruch25a.html) finds strong random-subset controls with teacher guidance. | Compare the same subset with and without a pinned teacher penalty. Measure previous-success retention and new-family gains. | Next; Medium. Extend 195. Teacher errors remain possible; teacher predictions do not replace labels. |
| PM06 | [Geometric Median Matching](https://proceedings.mlr.press/v267/acharya25b.html) targets robust subset selection. | Compare a representative subset with reviewed random selection under documented label conflicts. Decide whether robustness beats simpler filtering. | Defer; Medium. Extend 113 and 184 after label review. Do not introduce noise into audit data. |
| PM07 | [Data Shapley](https://proceedings.mlr.press/v97/ghorbani19c.html) estimates individual data value. | Start with leave-one-training-group-out tests on a small frozen fit. Decide whether expensive attribution is warranted. | Defer; Large for full attribution. Reuse 190 and 197 for cheaper group-level answers first. |
| PM08 | [Model soups](https://proceedings.mlr.press/v162/wortsman22a.html) average compatible fine-tuned weights. | Check common initialization and architecture. Compare a fixed blend with both endpoints on all retained conditions. | Next; Small if compatible checkpoints exist. Preserve failures. Weight compatibility is a prerequisite, not an assumption. |
| PM09 | [Lowering the Pre-training Tax](https://proceedings.mlr.press/v202/ro23a.html) considers overhead in gradient-based selection. | Include feature extraction, selection, and repeated reads in the data-selection cost. Decide whether a selector saves total time. | Now; Small instrumentation extension. Pair with 181 and the existing workflow comparison. |
| PM10 | [SelMatch](https://proceedings.mlr.press/v235/lee24g.html) combines selected examples with dataset distillation. | Compare ordinary selected UI scenes before considering optimized synthetic pixels. Require valid geometry and labels throughout. | Defer; Large. Its classification results do not establish valid focus synthesis. TTR rendering is the simpler current producer. |

## 3 Hugging Face Papers

Use Hugging Face for discovery, then read the original paper.
These 10 ideas come from 5 papers. The paired rows ask different questions.
Do not treat generated summaries, votes, or downloadable weights as qualification.

| ID | Idea and primary source | Proposed test and decision | Recommendation and existing work |
| --- | --- | --- | --- |
| HF01 | [OmniParser](https://arxiv.org/abs/2408.00203) separates screen parsing from downstream actions. | Compare class-free control proposals with class-aware boxes before focus scoring. Measure proposal recall separately. | Now; Small. Reuse 188 and 023. Do not import a full GUI agent to test this principle. |
| HF02 | [OmniParser](https://arxiv.org/abs/2408.00203) associates detected regions with element semantics. | Add OCR association to fixed proposals. Test whether tabs and rows become easier to classify without changing geometry. | Next; Medium. Extend 019 and 093. Text is supporting evidence, not proof of focus. |
| HF03 | [ScreenSpot-Pro](https://arxiv.org/abs/2504.07981) finds benefits from reducing the search area in high-resolution GUI grounding. | Compare full-frame inference with fixed native-resolution regions. Count recovered small controls and new duplicate boxes. | Next; Medium. Extend 007, 075, and 077. Keep the original view as the control. |
| HF04 | [ScreenSpot-Pro](https://arxiv.org/abs/2504.07981) exposes difficult professional applications and small targets. | Hold out complete native layout families. Compare known-family and unseen-family results by target size. | Now; Small when labels qualify. Extend 190 and 039. Grounding a requested target differs from finding focus. |
| HF05 | [DINOv2](https://arxiv.org/abs/2304.07193) supplies general visual features without task-specific supervision. | First test a frozen resident encoder against full fine-tuning. Consider an outside encoder only if representation remains the measured limit. | Next; Medium with resident models; Large with new weights. Extend 191 and 079. |
| HF06 | [DINOv2](https://arxiv.org/abs/2304.07193) includes large-scale data curation. Our adaptation concerns diversity. | Compare feature-diverse scene selection with exact deduplication and random groups. Preserve distinct events even when pixels match. | Next; Medium. Extend 184 and 197. Feature distance is not semantic identity. |
| HF07 | [Segment Anything](https://arxiv.org/abs/2304.02643) supports prompted segmentation. | On reviewed controls, test masks as a diagnostic for body boundaries. Compare against existing geometry before changing proposals. | Defer; Large unless resident tooling qualifies. Extend 186. A segmentation mask does not identify focus. |
| HF08 | [Segment Anything](https://arxiv.org/abs/2304.02643) enables interactive annotation workflows. | Compare human review time and correction quality with and without mask suggestions. Keep reviewer decisions authoritative. | Defer; Medium or Large. Extend 113. Do not admit generated masks as automatic truth. |
| HF09 | [InstaGen](https://arxiv.org/abs/2402.05937) explores synthetic images for object detection. | Test whether exported TTR geometry matches rendered pixels across effect strengths. Reject label-render mismatches before fitting. | Now; Small using retained captures. Extend 110 and 113. This adaptation uses TTR, not diffusion generation. |
| HF10 | [InstaGen](https://arxiv.org/abs/2402.05937) motivates testing synthetic detection data. | Compare native-only with a fixed native/synthetic mixture at equal exposures. Measure native gains and retained losses. | Next; Medium. Extend 189 and 040. Do not equate realistic appearance with native-domain accuracy. |

Discovery pages: [OmniParser](https://huggingface.co/papers/2408.00203), [ScreenSpot-Pro](https://huggingface.co/papers/2504.07981), [DINOv2](https://huggingface.co/papers/2304.07193), [SAM](https://huggingface.co/papers/2304.02643), and [InstaGen](https://huggingface.co/papers/2402.05937).

## 4 Reddit

Treat these discussions as practical questions, not validated methods.
Some threads were available only through indexed excerpts. No recommendation depends on their claimed numerical gains.
The controlled tests below are our proposals. Primary support comes from the related paper rows where noted.

| ID | Discovery lead | Proposed test and decision | Recommendation and existing work |
| --- | --- | --- | --- |
| RD01 | [Synthetic versus real YOLO data](https://www.reddit.com/r/computervision/comments/1qcldia/synthetic_data_vs_realonly_training_for_yolo_on/) raises comparison fairness. | Hold frame exposure and training steps fixed when adding synthetic scenes. Decide whether diversity, rather than extra work, produces gains. | Now; Small design correction. Extend 189. See HF10 for primary research. |
| RD02 | The same [synthetic-data discussion](https://www.reddit.com/r/computervision/comments/1qcldia/synthetic_data_vs_realonly_training_for_yolo_on/) mixes confidence and performance claims. | Report raw correct and wrong selections beside confidence changes. Reject improvements based only on higher confidence. | Now; Small. Extend 115. See PM01. |
| RD03 | [YOLO false-positive discussion](https://www.reddit.com/r/computervision/comments/1gv3q0y) suggests reviewing difficult negatives. | Generate decorative borders and selected-but-unfocused tabs with verified focus elsewhere. Measure wrong picks at matched recall. | Next; Medium. Extend 109 and 194. Confirm labels before emphasizing mistakes. |
| RD04 | The [false-positive discussion](https://www.reddit.com/r/computervision/comments/1gv3q0y) also raises low-confidence collection. | Compare uncertain, diverse, and random scene selection at equal budgets. Decide whether uncertainty just repeats ambiguous scenes. | Next; Medium. Reuse 181 rather than adding a duplicate. See OR08. |
| RD05 | [Hidden dataset failures](https://www.reddit.com/r/computervision/comments/1ptm7wh/what_are_the_biggest_hidden_failure_modes_in/) raises aggregate-metric blind spots. | Separate recall by control height and native pixel size. Test whether resizing explains the 32–64 px failures. | Now; Small. Extend 007 and 077. Do not infer causation from the size slice alone. |
| RD06 | [Hidden dataset failures](https://www.reddit.com/r/computervision/comments/1ptm7wh/what_are_the_biggest_hidden_failure_modes_in/) suggests missing negative conditions. | Separate verified no-focus, unknown focus, and missing proposals. Measure false selections for each state. | Now for retained evidence; Medium for missing capture. Extend 182 and 058. |
| RD07 | [Copy-paste synthesis discussion](https://www.reddit.com/r/computervision/comments/1bnhhki) raises visual seams. | Hold focus constant while changing compositing seams and background boundaries. Decide whether synthetic artifacts drive predictions. | Next; Medium. Extend 043 and 198. Preserve control pixels where possible. |
| RD08 | [Small custom detector discussion](https://www.reddit.com/r/computervision/comments/1w4ijvy/yolxo_smalltiny_custom_model_training/) raises preprocessing errors. | Compare decoded tensors and outputs across training, export, and Vision. Check channel order, scaling, and coordinates independently. | Now; Small when artifacts exist. Reuse 081 and 087. An anecdote does not establish our pipeline is wrong. |
| RD09 | The same [custom detector discussion](https://www.reddit.com/r/computervision/comments/1w4ijvy/yolxo_smalltiny_custom_model_training/) suggests checking minimal training behavior. | Fit a tiny qualified training set as a software check. Fail on incorrect label indexing or unreachable low training error. | Next; Small bounded template test. This does not measure generalization or justify promotion. |
| RD10 | [Domain generalization discussion](https://www.reddit.com/r/MachineLearning/comments/hvc0uh) points back to DomainBed. | Compare ordinary training before adding domain-adaptation machinery. Match selection budgets and held-out families. | Now; Small planning requirement. Reuse OR04 and 190. Do not create another domain-generalization job. |

## 5 Hacker News

Hacker News is more useful for operational costs and failure reports than for choosing focus models.
The proposed tests use official documentation where a tool contract matters.
Community comments do not establish current tool defects.

| ID | Discovery lead and evidence | Proposed test and decision | Recommendation and existing work |
| --- | --- | --- | --- |
| HN01 | [DVC discussion](https://news.ycombinator.com/item?id=41888937); [official pipeline documentation](https://doc.dvc.org/user-guide/pipelines/running-pipelines). | Repeat a preparation stage with identical inputs. Verify output hashes and avoided work. Decide whether caching removes maintenance. | Now; Small. Reuse WORKFLOW394. Do not introduce a second scheduler. |
| HN02 | [DVC discussion](https://news.ycombinator.com/item?id=41888937); [official fetch contract](https://doc.dvc.org/command-reference/fetch). | Restore one named dataset shard and checkpoint into an isolated destination. Verify hashes and dependent scoring. | Next; Medium. Reuse storage recovery work. An execution copy is not automatically a retained backup. |
| HN03 | [Older DVC discussion](https://news.ycombinator.com/item?id=33047634) raises costs with many files. | Compare original files and packed shards on USB using identical decoded tensors. Measure cold and warm reads separately. | Next; Medium. Existing workflow audit. Do not assume an old complaint applies to our installed version. |
| HN04 | [Older DVC discussion](https://news.ycombinator.com/item?id=33047634); [official user guide](https://doc.dvc.org/user-guide). | Compare custom code, recovery steps, and operator actions across our adapter and DVC. Decide whether migration actually reduces work. | Now; Small review of WORKFLOW394 results. Keep framework adoption separate from model work. |
| HN05 | [Leakage discussion](https://news.ycombinator.com/item?id=32111697); [primary paper](https://arxiv.org/abs/2207.07048). | Test that derivatives, reversals, and profile counterparts stay in one group. Fail cross-role ancestry. | Now; Small. Reuse existing split checks. Add cases only where the current checks lack coverage. |
| HN06 | [Leakage discussion](https://news.ycombinator.com/item?id=32111697); [primary paper](https://arxiv.org/abs/2207.07048). | Verify that normalization, selection, and threshold fitting exclude final audit membership. Decide whether reported gains need reclassification. | Now; Small. Extend 009 and 010. Reading audit errors already removes their untouched status. |
| HN07 | [Continuous ML discussion](https://news.ycombinator.com/item?id=23759332) suggests automatic comparison reports. | Remove one required output from an isolated report test. Require an incomplete decision, not model acceptance. | Now; Small. Reuse decision-report templates. This is our reliability proposal, not a claim about a CI product. |
| HN08 | [Continuous ML discussion](https://news.ycombinator.com/item?id=23759332) suggests repeatable automation. | Replay a completion event and interrupt receipt delivery. Require one recorded attempt and no duplicate execution. | Now; Small. Extend existing reporting tests. Keep execution ownership with the NUIAK runner. |
| HN09 | [Procedural visual training discussion](https://news.ycombinator.com/item?id=29496829) offers a non-photographic data lead. | Compare owned procedural textures with varied artwork while holding geometry fixed. Measure native transfer and artwork dependence. | Next; Medium. Extend 043 and 110. Do not replace native qualification with procedural accuracy. |
| HN10 | [More data discussion](https://news.ycombinator.com/item?id=18916542) motivates testing data value rather than volume alone. | Compare new scene groups with repeated views at equal frame counts. Include capture and preprocessing cost. | Next; Medium. Reuse 197. See PM04–PM09 for primary methods and stronger controls. |

## 6 Two Minute Papers

These are 10 questions inspired by 5 video topics, not 10 verified video claims.
Video metadata and linked research are available; the videos themselves were not reviewed frame by frame.
The strongest uses are bounded robustness tests. Rendering and camera papers do not directly solve native UI focus.

| ID | Video topic and primary basis | Proposed test and decision | Recommendation and existing work |
| --- | --- | --- | --- |
| TP01 | [Adversarial policies video](https://www.youtube.com/watch?v=QFu0vZgMcqk); [paper](https://arxiv.org/abs/1702.02284). | Apply bounded, label-preserving pixel changes to retained UI frames. Measure decision flips and margin changes. | Next; Medium. Extend 118. A policy attack paper supplies motivation, not a NUIAK robustness guarantee. |
| TP02 | The same [policy study](https://arxiv.org/abs/1702.02284) motivates sequence-level failure analysis. | Replay a wrong focus observation inside a recorded sequence. Measure stale-state persistence without sending navigation inputs. | Next; Medium. Extend 068 and 090. Offline replay does not establish safe live navigation. |
| TP03 | [Optical-flow video](https://www.youtube.com/watch?v=7aLda2E0Yyg) suggests motion evidence. | Compare existing frame differences with a qualified flow baseline on scrolling and focus movement. Measure confusion between those conditions. | Next; Medium. Extend 064 and 070. Flow is motion evidence, not a focus label. |
| TP04 | The same [optical-flow topic](https://www.youtube.com/watch?v=7aLda2E0Yyg) suggests correspondence checks. | Insert occlusion, repeated frames, and scene cuts into replay. Require invalid motion evidence rather than confident continuity. | Next; Medium. Extend 068 and 069. This is a proposed hardening test, not a video result. |
| TP05 | [Resampling video](https://www.youtube.com/watch?v=W1UDzxtrhes); [NVIDIA presentation](https://research.nvidia.com/publication/2021-07_rearchitecting-spatiotemporal-resampling-production). | Compare cached feature reuse with fresh scoring after a scene change. Require invalidation when inputs change. | Now; Small. Analogy only. Rendering reuse does not establish a correct ML cache key. |
| TP06 | The same [rendering presentation](https://research.nvidia.com/publication/2021-07_rearchitecting-spatiotemporal-resampling-production) motivates separating reusable work. | Batch compatible scoring jobs with shared decoding. Require identical predictions and measure total time saved. | Now; Small or Medium. Reuse workflow templates. Do not share mutable model state without isolation checks. |
| TP07 | [Low-light video](https://www.youtube.com/watch?v=bcZFQ3f26pA); [Learning to See in the Dark](https://arxiv.org/abs/1805.01934). | Vary UI contrast while preserving focus geometry. Find the native contrast range where decisions fail. | Next; Medium. Extend 035 and 052. Camera RAW reconstruction is not the same problem as dark screenshots. |
| TP08 | The same [low-light study](https://arxiv.org/abs/1805.01934) raises the risk of preprocessing mismatch. | Compare original screenshots with bounded normalization. Check whether enhancement invents borders or removes shadows. | Next; Small. Extend 087. Defer importing the camera model; preserve original evidence. |
| TP09 | [Super-resolution video](https://www.youtube.com/watch?v=HvH0b9K_Iro); [ProSR project](https://igl.ethz.ch/projects/prosr/). | Compare original-resolution crops with resized crops before testing learned enlargement. Measure small-control recovery. | Now; Small. Extend 007 and 077. Learned enlargement cannot be assumed to recover truthful focus details. |
| TP10 | [ProSR](https://arxiv.org/abs/1804.02900) uses progressive architecture and training for image reconstruction. | If resolution remains limiting, compare a fixed coarse-to-fine training schedule with native-resolution training at equal budgets. | Defer; Medium. Cross-task analogy only. Do not change architecture and schedule together. |

## 7 Slashdot

Slashdot has the lowest direct yield for this project.
Its useful topics concern data provenance, similarity limits, and robustness.
The following questions are adaptations from those topics, not endorsements of headline claims.

| ID | Discovery lead | Proposed test and decision | Recommendation and existing work |
| --- | --- | --- | --- |
| SD01 | [Synthetic-data article](https://tech.slashdot.org/story/23/07/19/1413237/why-synthetic-data-is-being-used-to-train-ai-models). | Distinguish procedural rendering, native Fixture capture, and model-generated images in manifests. Reject missing provenance. | Now; Small. Extend intake checks. Native rendering does not establish real-app generalization. |
| SD02 | The same [synthetic-data topic](https://tech.slashdot.org/story/23/07/19/1413237/why-synthetic-data-is-being-used-to-train-ai-models) motivates coverage checks. | Compare requested factors with accepted capture counts. Find missing families, positions, and themes before training. | Now; Small. Extend 031 and 110. A recipe does not prove the capture contains the requested variation. |
| SD03 | [Model-collapse coverage](https://tech.slashdot.org/story/24/07/26/0016252/ai-models-face-collapse-if-they-overdose-on-their-own-output); [Nature study](https://www.nature.com/articles/s41586-024-07566-y). | Check that self-generated predictions never silently replace observed labels. Preserve original captures and corrections. | Now; Small. Extend 113. The study concerns recursive generative training, not proof that Fixture data is harmful. |
| SD04 | The same [Nature study](https://www.nature.com/articles/s41586-024-07566-y) motivates preserving rare conditions. | Measure whether pruning removes rare native families. Compare coverage-preserving selection with ordinary random selection. | Next; Medium. Reuse 184. This application is an inference, not a result from the generative study. |
| SD05 | [NeuralHash coverage](https://apple.slashdot.org/story/21/08/18/1755223/apples-neuralhash-algorithm-has-been-reverse-engineered) raises similarity limits. | Compare exact hashes and perceptual review candidates on duplicate captures. Never delete from perceptual similarity alone. | Now; Small. Extend 024. NeuralHash is not Apple's Vision feature-print method. |
| SD06 | The same [hashing topic](https://apple.slashdot.org/story/21/08/18/1755223/apples-neuralhash-algorithm-has-been-reverse-engineered) suggests collision checks. | Keep distinct capture events with identical bytes. Verify storage deduplication does not collapse labels, timing, or group membership. | Now; Small. Extend 024 and reporting checks. Payload identity and event identity answer different questions. |
| SD07 | [Visual attack coverage](https://tech.slashdot.org/story/19/04/02/0347232/researchers-trick-tesla-autopilot-into-steering-into-oncoming-traffic) suggests competing patterns. | Add decorative outlines to unfocused controls. Measure wrong selections without changing the actual focused control. | Next; Medium. Extend 005 and 194. This is not a claim that vehicle attacks transfer to NUIAK. |
| SD08 | The same [attack topic](https://tech.slashdot.org/story/19/04/02/0347232/researchers-trick-tesla-autopilot-into-steering-into-oncoming-traffic) suggests limiting action from uncertain perception. | Replay ambiguous decisions through observation-only integration. Require explicit abstention and no navigation authority. | Now; Small integration check. Extend 090. Do not add live device actions for this review. |
| SD09 | [Neural-network failure coverage](https://slashdot.org/story/14/05/27/1326219/the-flaw-lurking-in-every-deep-neural-net); [primary paper](https://arxiv.org/abs/1312.6199). | Measure decision stability under bounded translations and rasterization changes. Separate genuine effect removal from incidental sensitivity. | Next; Medium. Extend 118 and 076. A finite stress test does not certify general robustness. |
| SD10 | The same [primary paper](https://arxiv.org/abs/1312.6199) motivates checking mistakes beyond average accuracy. | Compare confidence on clean errors and perturbed errors. Decide whether abstention catches failures at usable coverage. | Next; Small. Reuse 115 and PM01. Do not assume confidence detects adversarial or unfamiliar inputs. |

## Consolidated implementation priorities

Do not create 70 jobs from these rows. Several rows strengthen one shared comparison.
The following order follows our retained failures rather than source popularity.

| Order | Combined investigation | Smallest useful deliverable | Dependency and next decision |
| --- | --- | --- | --- |
| 1 | Proposal correspondence and class-free recall: HF01, RD08. | Case-linked comparison of known boxes, raw proposals, and mapped proposals. | Reuse 188 and 193. Fix geometry or proposal coverage before another broad crop fit. |
| 2 | Small-control resolution: HF03, RD05, TP09. | Native-resolution comparison with unchanged original views and per-size support. | Reuse 007 and 077. Add a detail path only if it recovers cases without previous losses. |
| 3 | Realistic proposal-error training: related 196. | Measured box-error distribution from training groups, plus a matched random-jitter control. | Requires correct proposal correspondence. Decide whether robustness training is justified. |
| 4 | Frozen versus updated features: OR03, HF05. | Fixed-membership comparison of output-only, staged, and full updates. | Extend 191 after trainer qualification. Count new gains and previous successes lost. |
| 5 | Equal-budget data selection: OR08, PM02, RD04, HN10. | Shared subset manifests for random, balanced, and targeted selection. | Reuse 181 and 197. Include preparation cost and independent groups. |
| 6 | No-focus and competing decoration: RD03, RD06, SD07. | Qualified negative states and separate unknown-state reporting. | Reuse 182 and 194. Capture only missing conditions through the approved producer. |
| 7 | Preserve old behavior: PM05 and OR03. | Teacher-penalty comparison on old training examples, not inspected audit examples. | Reuse 195. Proceed only if the simpler correction still loses previous successes. |
| 8 | Family-aware selection: OR02, OR05, PM03. | Retained-checkpoint report with average and worst-family outcomes. | Reuse 190 and 192. Freeze the selection rule before new training. |
| 9 | Cache, restore, and reporting correctness: HN01–HN08, TP05–TP06. | One reusable positive/negative template suite with measured saved work. | Reuse WORKFLOW394 and existing adapters. Do not add another framework. |
| 10 | Confidence at matched coverage: PM01, SD10. | Calibration-only comparison with wrong selections, abstentions, and support. | Correct proposals first. Calibration does not fix missing evidence. |

## Template requirements

Prefer variants of existing adapters over new experiment scripts.
These are proposed requirements to verify against the current templates, not claims that every variant already exists.

| Shared operation | Required additions when absent | Positive and negative qualification |
| --- | --- | --- |
| Score fixed proposals | Preserve raw, mapped, and known-box identities. Record proposal recall before selection. | Valid mapping reproduces reference scores. Missing correspondence fails explicitly. |
| Build controlled subsets | Fix group membership, seed, exposure, and selection policy. | Same specification reproduces hashes. Cross-role ancestry fails. |
| Fit a controlled variant | Declare frozen layers, teacher identity, and checkpoint selection rule. | Resume matches the declared tolerance. Incompatible weights fail before training. |
| Apply a diagnostic change | Preserve original pixels and record changed coordinates or appearance factors. | A zero-change control reproduces outputs. Invalid geometry or labels fail. |
| Report a comparison | Separate task metrics, support, costs, and acceptance. | Complete evidence produces a decision. Missing baseline or labels prevents acceptance. |
| Test workflow efficiency | Separate first-read cost, repeated-read cost, setup, and scoring. | Reuse preserves outputs. Changed inputs invalidate reuse. |

Keep 800 s and 100 MB defaults for diagnostics.
Training, capture, outside dependencies, and bulk storage need their existing explicit contracts.
Keep final evaluation exclusions unchanged. Use development groups for diagnosis and calibration groups for thresholds.
Do not treat zero observed errors on related frames as proof of safety.

## How to use these sources efficiently

Use OpenReview, PMLR, CVF, Apple documentation, and author repositories for technical decisions.
Use Hugging Face to find those primary sources.
Use Reddit and Hacker News to find failure modes and operational questions.
Use Two Minute Papers for visual ideas that need a careful transfer check.
Use Slashdot occasionally; it does not justify a dedicated high-volume research stream for this project.

Require one observed local failure and one decision-changing test before adding an experiment.
Reject duplicated questions unless a new control, domain, or qualified input changes the answer.
Check code and weight licenses separately before any download or redistribution.
Do not send private captures to outside services during discovery.

The next substantial tranche should prepare priorities 1–3 and the shared subset producer for priority 5.
This gives immediate diagnostics plus the inputs needed for controlled training.
Keep larger encoders, optimized synthetic pixels, and expensive data attribution deferred until simpler comparisons justify them.
