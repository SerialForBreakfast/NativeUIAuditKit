# PROGRAM384 — level-set and experiment program after native HCF qualification

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Date: 2026-10-13. Status: proposal for maintainer selection. This document registers no job and grants no execution authority.
Relates to [ADR-0026](../ADR-0026-Queued-Research-Experiments.md), [ADR-0027](../ADR-0027-Evidence-Guided-Experiment-Graphs.md),
[HCF369](../HCF369Results.md), [HCF371](HCF371.md), [HCF374](../HCF374Duplicates.md), and [RCA-20261013-01](../RCA-20261013-Mock-Experiment-Generation.md).

## 1. Current state

### Native HCF
- HCF368–HCF370 show a visible HCF cue for native image cards.
  - 48 frames and 12 focused states.
  - 98.61%–99.68% of the Standard/HCF difference falls within 64 px of the observed focused control. Unfocused windows show 0 difference.
  - All 48 frames form 1 related development group.
- HCF371 captures 4 focus positions × 2 profiles for each scene. The first 2,000 frames come from 250 scene groups (HCF374).
- HCF371 development comparison on 264 frames (`hcf371r5-92-decision`):

| Method | Correct | Wrong | Misses | Precision | Recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| Outline rule `bright-closed-stroke-v1` | 62 | 25 | 177 | 0.713 | 0.235 |
| Retained crop model | 63 | 5 | 196 | 0.926 | 0.239 |
| HCF crop candidate (known boxes) | 137 | 0 | 127 | 1.000 | 0.519 |
| HCF full-screen detector | 134 | 0 | 130 | 1.000 | 0.508 |

- The decision records `modelAccepted: false`, `productionChanged: false`, and `auditOpened: false`.
  Both learned candidates gain over 100 cases and lose 35 against the retained crop model.
- HCF375 (balanced HCF and Standard training) is pending. Its log entry needs 2 corrections before its result is read:
  - The crop counts conflict: "2,000 training crops" against "4,000 HCF + 4,000 Standard".
  - It calls the 264 development frames "withheld". They are inspected development data.
- Visibility depends on the control family. TTR's button counterparts are pixel-identical across profiles.
  Other families, no-focus scenes, and physical devices remain unmeasured.

### Delivered model needs review
Commit `e890fb79` adds `NativeUIFocusDetector_tvOS.mlmodelc` to the models package and changes `NativeUIModelAsset`.
The HCF371 decision says no model is accepted. The HCF371 plan keeps Core ML conversion, deployable proposals, and the final audit as open gates.
The model metadata names 1 class (`focused_control`), but its Core ML class list has 80 entries and its confidence output has 80 columns.
A consumer that reads the class list can therefore select a class that does not exist.

### Focus-transition models
| Arm (FOCUS373 repair decision) | Correct of 392 | False changes | Lost previous successes |
| --- | ---: | ---: | ---: |
| Matched control | 301 | 42 | 22 |
| Notification correction | 342 | 18 | 6 |

The current rule requires 0 lost previous successes, so it rejects both arms.
The control has the same recipe as the baseline but loses 22 successes. A large part of each "loss" count is therefore retraining variation.
FOCUS358 is complete: both 30-epoch arms are rejected and gain no native movements.

### Detectors and rules
- tvOS detector: 346/583 reviewed controls on 46 real screens, and 21/46 focused targets.
- iOS 41-class detector: 0.6322 withheld mAP@0.5. The DS-G8 gate needs ≥0.85.
- `resolveTVOSFocus` (the library fallback) has no measured accuracy.

### TTR `a9b3412c`
- HCF switching: `aatv route hcf`, MCP `navigation.hcf`, and `system_configuration.*`.
- Recovery journals and a storage budget.
- `GET /scene/metadata`: bounds and focus, but no effect parameters or z-order.
- 7 native templates. They share 1 skeleton, so count them as 1 lineage.
- Scope: Simulator 26.5 (23L470), en_US. The updated app is not yet qualified on research host.

### Process failures recorded on 2026-10-13
- Mock experiments raised the completed-job count without measurement (RCA-20261013-01).
- The crop-triplet generator writes 210 cases, but only 21 are unique. Its ingest swaps the focused and unfocused labels and leaks copies across splits.
- A shard registered with no sources blocked the FOCUS366 decision.

## 2. What paired HCF captures add

An HCF pair keeps the scene and the focus target fixed and changes only the profile.
For a family with a visible effect, the pair difference maps where the system draws the HCF focus effect.
UIKit already reports the focus ID. The new information is the **effect mask and its geometry**.
TTR reports `focus_effect_segmentation` as unsupported; for qualified families, the pair difference supplies it.

HCF371 scenes already contain 4 focus positions × 2 profiles. Each scene therefore supports 3 differences:

| Difference | What it isolates |
| --- | --- |
| Standard vs HCF, same target | The HCF style at that target |
| Target A vs target B, same profile | The focus movement under that profile |
| Repeat vs original | Capture noise, which must be 0 |

## 3. Automatic high-confidence focus labels

Use a label hierarchy. Admit a label automatically only when independent sources agree.

1. L0: the UIKit observed focus ID, verified before and after capture, plus measured body bounds. This source is authoritative in the Fixture.
2. L1: pair-difference attribution. Extend `scripts/hcf_spatial_audit.py` to emit a mask and the control with the highest difference density.
3. L2: single-frame rules, for example `bright-closed-stroke-v1` and the TTR `HCFFocusRules` bright-surface pass.
4. L3: models. A model can select cases for review. It cannot create a label.

Admission rules:
- If L0 and L1 agree, admit the label and the mask.
- If L0 and L1 disagree, quarantine the case. Report the disagreement rate for each family.
- Set each family's auto-accept rule so that the lower 95% Clopper–Pearson bound on audited precision is at least 0.98.
  With 0 errors, this needs about 150 audited cases per family. Learn-then-Test ([Angelopoulos et al.](https://arxiv.org/abs/2110.01052)) gives the method.
- Search admitted sets for label errors with ObjectLab in cleanlab ([Tkachenko et al.](https://arxiv.org/abs/2309.00832)). Review the worst cases first.

For real apps, no UIKit observation exists. Use these separate labeling functions:
- Remote-driven exploration: drive focus and record which element becomes focused ([Wu et al., UIST 2023](https://arxiv.org/abs/2308.08726)).
- Temporal differencing.
- Accessibility-tree filtering: drop hidden, zero-size, and covered nodes ([Li et al., CHI 2022](https://arxiv.org/abs/2201.04100)).

Combine the functions with a weak-supervision label model ([Ratner et al.](https://arxiv.org/abs/1711.10160)).
TTR states that its navigation-map crops are presentation images, not labels. Real-app use needs maintainer approval.

## 4. Rule-based detector

On aligned frames, classical image processing locates GUI element boundaries better than learned detectors ([Chen et al., FSE 2020](https://arxiv.org/abs/2008.05132)).
The deterministic Fixture therefore makes rules useful for 3 things: as a baseline, as a label teacher, and as a fallback.

- **R-pair (needs 2 frames):** absolute difference or SSIM, then connected components clipped to known or proposed bounds.
- **R-single (needs 1 HCF frame):** a bright closed stroke or a filled row.
  - The current rule reaches 0.713 precision at 0.235 recall.
  - First analyze its 25 wrong selections before tuning it.
- **Cascade:** run the rule first. If the rule abstains, use the model. Report risk–coverage curves ([Geifman and El-Yaniv](https://arxiv.org/abs/1705.08500)).
- **Calibration:** temperature-scale the models on the calibration role before the cascade comparison ([Guo et al.](https://arxiv.org/abs/1706.04599)).

## 5. Process feedback

1. **Replace "0 lost previous successes" with a rule based on the seed-churn floor.**
   - Train the matched control with 3 seeds ([Bouthillier et al.](https://arxiv.org/abs/2103.03098)).
   - Define the *stable successes* as the cases correct in all 3 seeds.
   - Require a candidate to keep the stable successes, and to lose no more of the other cases than the control seeds lose.
   - Under this rule, the notification correction (6 lost, against 22 for the control) can qualify for confirmation.
2. **Count independent groups, not frames.** The HCF368–370 frames are 1 group, and the 7 TTR templates are 1 lineage.
   Report intervals with a cluster bootstrap by scene group ([Field and Welsh](https://doi.org/10.1111/j.1467-9868.2007.00593.x)).
3. **Screen factors together.** Use a resolution-IV fractional factorial for 5–7 generation factors ([NIST e-Handbook](https://www.itl.nist.gov/div898/handbook/pri/section3/pri334.htm)).
   Confirm only the 2–3 factors that matter.
4. **Protect the final audit set.** The 264 HCF development frames, the 392 authored pairs, and the retained suite are inspected, so they are development data.
   Open the HCF371 final audit only once, for a frozen candidate ([Dwork et al.](https://arxiv.org/abs/1506.02629)).
5. **Fit learning curves before scaling.** Measure 3 sizes × 3 seeds ([Hestness et al.](https://arxiv.org/abs/1712.00409)). If the curve is flat, add variety, not volume ([Mayer et al.](https://arxiv.org/abs/1801.06397)).
6. **Store crops for the bulk data.** A 4K PNG uses about 6.2 MB. Store the control windows and masks for all data, and keep full frames for a hashed audit subset.
7. **Lint every registration and admission:**
   - Reject empty shards.
   - Reject duplicate content hashes.
   - Check label polarity against the source sidecar.
   - Check that split groups are disjoint.
   - Report evidence as measured only when the job loaded real model weights and real inputs. This responds to RCA-20261013-01.
8. **Gate deliveries.** Reject a models-package change when the linked decision says `modelAccepted: false`.
   Check that the Core ML class list matches the model's class names.
9. **Batch profile switches.** A profile switch takes 33–95 s, and a capture takes about 4 s. Capture all scenes in 1 profile, then switch once.
10. **Answer TTR's open requests:**
    - Composition v5 support in `fixture_composition.py`, which accepts versions 1–3 only.
    - The consumer contract for compact scenes.
    - HCF data kept separate from ordinary-focus data by default.
    - Shards closed before 70% of quota.
    - The finding that visibility differs between image cards and buttons.

## 6. Proposed experiments

Freeze each threshold before execution. Each result maps to 1 next action.

### Track 0: repair (P0)
| ID | Test | Result → action |
| --- | --- | --- |
| R1 | Review `e890fb79`: compare the class list with the class names, check the HCF371 gates, and check the `NativeUIModelAsset` callers | If a gate is unmet, remove the model from the package or mark it experimental. Record the decision |
| R2 | Correct the HCF375 log entry (crop counts, "withheld") before reading its result | The HCF375 decision uses correct membership and data roles |
| R3 | Registration and admission lint (5.7). Quarantine exp-51 to exp-65 | Stops the recorded defect classes |
| R4 | Qualify the TTR app built locally from `a9b3412c`: recovery and storage, no repeated captures | Pass: use the new HCF controls. Fail: report the exact failure to research-host-TTR |

### Track A: labels (P0/P1)
| ID | Test | Result → action |
| --- | --- | --- |
| A1 | Agreement of L0 and L1 on the admitted HCF371 frames; masks and density argmax | Agreement at least 0.98 at the lower bound: auto-admit image cards |
| A2 | Effect geometry from masks: outline width, growth, and extent past the body | Sets the crop margin (check the 16% in BP-46) and the 64 px window |
| A3 | Visibility survey: buttons, Settings rows, tabs, shelves, and the 7 templates | Visible: add to HCF collection. Not visible: exclude from HCF positive labels |
| A4 | Qualified no-focus scenes | Supplies the no-focus false-selection measurement that HCF371 lacks |

### Track B: rules (P0/P1)
| ID | Test | Result → action |
| --- | --- | --- |
| B1 | Measure `resolveTVOSFocus` on retained native frames | Sets the baseline for every model |
| B2 | Analysis of the outline rule's 25 wrong selections | Identifies the failure modes to fix before tuning the rule |
| B3 | R-pair against L0 on HCF371 pairs, per family | High precision: R-pair becomes the label teacher |
| B4 | Rule-first cascade against each model alone, after calibration: risk–coverage | Picks the HCF routing policy |

### Track C: HCF models (P1)
| ID | Test | Result → action |
| --- | --- | --- |
| C1 | Miss analysis of the 127 crop and 130 detector misses by layout family, size, theme, and position | Shows whether misses come from coverage or from the model |
| C2 | Learning curve: 3 sizes × 3 seeds for the crop candidate | Flat: add variety. Rising: justify the larger HCF stages |
| C3 | Threshold and calibration on the calibration role, not on development frames | Tests whether the 0.52 recall comes from abstention thresholds |
| C4 | Cross-profile matrix: train on Standard or HCF, test on each (extends HCF375) | Transfers: joint model. Does not transfer: separate models |
| C5 | Crop-centric storage pilot: bytes per pair | Within the 250 GiB limit: unblock the large stages |

### Track D: focus transitions (P0/P2)
| ID | Test | Result → action |
| --- | --- | --- |
| D1 | Matched control × 3 seeds: churn floor and stable successes | Replaces the retention rule for every later decision |
| D2 | Notification correction × 3 seeds | Passes the churn rule: freeze it for the audit |
| D3 | Content negatives matched in magnitude, through Fixture `scene-mutation` | Tests the content false-change explanation |
| D4 | Effect-mask auxiliary target for the transition model, 3 seeds | Tests the whole-frame suppression explanation |

### Track E: tvOS detector (P1/P2)
| ID | Test | Result → action |
| --- | --- | --- |
| E1 | Error taxonomy of the 346/583 result by class, size, and style, from retained predictions | Picks the generation factors to vary |
| E2 | Inference at 640 and 1280 px with the existing weights ([SAHI](https://arxiv.org/abs/2202.06934)) | Small misses recover: run a resolution or tiling training test |
| E3 | Short fine-tune: diversity against volume, with a learning curve on the real set | Decides the direction of synthetic data investment |
| E4 | Capture-artifact augmentation: compression and scaling | Keep it only if real recall improves without more false positives |

### Proposals that need maintainer approval
- Frozen pretrained features (DINOv3, FOCUS363 package E).
- Supervised contrastive pretraining on HCF pairs ([Khosla et al.](https://arxiv.org/abs/2004.11362)).
- A Siamese-difference transition architecture ([Daudt et al.](https://arxiv.org/abs/1810.08462)).
- Pseudo-labels on real screens ([Li et al., CVPR 2022](https://arxiv.org/abs/2111.13216)).
- RT-DETR.
- HCF stages larger than 1 GPU-hour.

**Priority:** R1, R2, R3, D1, B1, E1, A1, C1, C3, then the remaining P1 items, then P2.
D1, B1, E1, A1, and C1 cost little and change how later results are read.

## 7. Evidence limits

- No published study measures synthetic-to-real transfer for GUI detectors or focus detection on tvOS. The cited synthetic-data evidence comes from other domains.
- Some cited figures come from secondary summaries. This document cites methods, not their reported numbers.
- The HCF numbers above use development data. They do not estimate final accuracy.
