# Novel SOTA Generation, Training, and Inference Experiments (`EXP418-01` to `EXP418-20`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17.
Catalog range: `B405-229` through `B405-248`. Template range: `T67` through `T86`.
Status: Specification and catalog additions prepared for review. Keep Standard unchanged and HCF optional. The detached runner owns execution.

---

## 1. Executive Summary

`Maximum-mini-NUIAK` designed 20 novel generation, representation, training, inference, and deployment experiments in two tranches (`EXP418-01` to `EXP418-10` and `EXP418-11` to `EXP418-20`). Each experiment addresses a measured bottleneck in [Tasks.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Tasks.md), [Backlog410.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Backlog410.md), [DetectorInference412.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/DetectorInference412.md), [Groom20261017.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Groom20261017.md), [DetectorFocusFollowup.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/DetectorFocusFollowup.md), [DetectorFocusPolicy.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/DetectorFocusPolicy.md), and [TTRMatchedConsumer.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/TTRMatchedConsumer.md).

---

## 2. Portfolio Index — Tranche 1 (`EXP418-01` to `EXP418-10`, `B405-229` to `B405-238`, `T67` to `T76`)

| Exp ID | Catalog ID | Template | Track | Title and Document | Measured Bottleneck Addressed |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `EXP418-01` | `B405-229` | `T67` | `IOS` | [Normalized Wasserstein Distance (NWD) Loss for Tiny UI Controls](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-01-NWD-Tiny-Box-Loss.md) | `pageControl` has `0` detections at IoU 0.5 and `label` loses `1,305` boxes (`74 %` small labels) in Run 013 (`B405-011`, `B405-115`). |
| `EXP418-02` | `B405-230` | `T68` | `REP` | [Fourier Domain Adaptation (FDA) for Synthetic-to-Real Transfer](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-02-Fourier-Domain-Adaptation.md) | Spatial color jitter reduces false focus changes (`587 -> 26`) but loses `72` movement successes (`FOCUS348`) by blurring boundary gradients. |
| `EXP418-03` | `B405-231` | `T69` | `FR` | [Within-Screen Set-Contrastive Focus Ranking (`SupCon` + `ListMLE`)](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-03-Set-Contrastive-Focus-Ranking.md) | Independent per-crop sigmoid scoring misses native tabs/buttons (`B405-169`, `B405-176`) and confuses selected-unfocused tabs with focused tabs (`B405-027`). |
| `EXP418-04` | `B405-232` | `T70` | `REP` | [Coordinate-Aware Boundary-Strip Unwarping (`CoordRing`)](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-04-CoordRing-Boundary-Unwarping.md) | Stretching `1400 x 64 px` rows into `256 x 256` distorts horizontal vs vertical focus ring thickness by `22x` (`B405-075`, `B405-114`). |
| `EXP418-05` | `B405-233` | `T71` | `HCF` | [Signed Moat-Ring Dipole Filter for Theme-Invariant Proposals](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-05-Signed-Moat-Ring-Dipole-Filter.md) | Every existing HCF kernel gets `0 of 4` proposals on light backgrounds because the `160` brightness gate merges the `255` ring into the `245` background (`B405-161`). |
| `EXP418-06` | `B405-234` | `T72` | `TGEN` | [Failure-Guided Counterfactual Twin Synthesis](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-06-Counterfactual-Twin-Synthesis.md) | Random seed sweeps rarely place wide toggles (`B405-016`), selected-unfocused tabs (`B405-027`), or decoy borders (`B405-005`) at matched coordinates. |
| `EXP418-07` | `B405-235` | `T73` | `TV` | [Scale-Gated Dual-Resolution SAHI + Weighted Box Fusion](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-07-Scale-Gated-SAHI-WBF.md) | Full-frame `960 px` gains `74` `listRow` detections but loses `34` large `collectionItem` cards (`B405-121`), and Core ML has a fixed `640 x 640` input. |
| `EXP418-08` | `B405-236` | `T74` | `DEPLOY` | [Margin-Preserving Distillation for Sub-5MB Core ML Palettization](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-08-Margin-Distilled-CoreML-Compression.md) | FP16 Core ML exceeds the `5 MB` gate (`5.04 MB`), while naive 6-bit palettization (`2.61 MB`) shifts logits near the `0.85` threshold (`TEMPLATE395`, `B405-128`). |
| `EXP418-09` | `B405-237` | `T75` | `PAIR` | [Kinematic Phase-Correlation Scroll Decoupling and Action-Graph Decoding](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-09-Kinematic-Scroll-Action-Graph.md) | Before/after difference models confuse list viewport scrolling (`B405-064`) and animated hero banners (`B405-062`) with focus movement or no-ops. |
| `EXP418-10` | `B405-238` | `T76` | `IOS` | [Confident Learning & OCR-Geometry Automated Label-Completeness Auditor](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-10-Confident-Label-Auditor.md) | Run 013 emits `491` high-confidence unmatched iOS boxes (`194` `navigationBar`, `297` `textField`, `B405-129`) and `290` unmatched tvOS boxes (`INFERENCE412`). |

---

## 3. Portfolio Index — Tranche 2 (`EXP418-11` to `EXP418-20`, `B405-239` to `B405-248`, `T77` to `T86`)

| Exp ID | Catalog ID | Template | Track | Title and Document | Measured Bottleneck Addressed |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `EXP418-11` | `B405-239` | `T77` | `FR` | [Null-Space Projected Fine-Tuning (`Null-LoRA` + `LP-FT`)](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-11-Null-Space-Orthogonal-Adaptation.md) | `25 %` native fine-tuning causes `16` false positives on `Sillycon-TTR` and loses Standard diamond decoration; `12.5 %` loses `2` tall HCF controls (`TTRMatchedConsumer.md`, `B405-191`, `B405-195`). |
| `EXP418-12` | `B405-240` | `T78` | `REP` | [Copula Proposal-Error Sampler and Spatial Transformer Crop Refiner (`ProposalSTN`)](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-12-Copula-Proposal-Error-STN.md) | Candidate scores `21/24` on known boxes (`4/4` diamond) but drops to `16/24` (`0.585` diamond) on correlated YOLO11n detector box errors (`DetectorFocusPolicy.md`, `B405-193`, `B405-196`). |
| `EXP418-13` | `B405-241` | `T79` | `FR` | [Group-DRO Minimax Training and Pareto Worst-Family Checkpoint Selection](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-13-Group-DRO-Pareto-Selection.md) | Mean-loss ERM lets easy `artwork` crops dominate while `row` (`4/8`) and `tall` (`2/4`) regress across epochs (`B405-192`, `OR01`, `OR02`). |
| `EXP418-14` | `B405-242` | `T80` | `FR` | [Helmholtz Free-Energy and Split Conformal Abstention Calibration](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-14-Conformal-Energy-Abstention.md) | Fixed `0.85` threshold conflates `no-focus`, `missing proposal` (4 pilot cases), `ambiguous competition` (3 pilot cases), and OOD baseline drift (`B405-182`, `PAPER417-STATES`). |
| `EXP418-15` | `B405-243` | `T81` | `TV` | [Anisotropic Strip Pooling and 1D Projected IoU (`Strip-IoU`) for Wide Rows](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-15-Anisotropic-Strip-IoU-Detector.md) | General detector misses `3 of 4` missing-proposal rows in `DetectorFocusFollowup.md`, `124 of 224` `listRow`s in `B405-121`, and `48` `32–64 px` iOS controls in `B405-186`. |
| `EXP418-16` | `B405-244` | `T82` | `PAIR` | [Prefix-Anchored Weighted Levenshtein Automaton for Clipped-OCR TTR Route Recovery](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-16-Prefix-Anchored-OCR-Route-Matcher.md) | `B405-220` native capture blocked on `Maximum-mini-TTR` (`hcf-a85a5a4e-d7f1-487b-bbbc-fa620f5480fe`) due to right-edge clipped-label OCR variation after `Focus Style`. |
| `EXP418-17` | `B405-245` | `T83` | `REP` | [Background-Inpainted Contextual Counterfactual Crops (`ContextSwap`)](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-17-Contextual-Counterfactual-Crops.md) | Isolates whether the `0.16` outer context ring causes false focus scores without changing control pixel scale (`B405-198`, `RD07`). |
| `EXP418-18` | `B405-246` | `T84` | `TGEN` | [Submodular Facility-Location and BADGE Coreset Selection (`SubmodCoreset`)](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-18-Submodular-BADGE-Coreset.md) | Delivers the P0 `PAPER417-SUBSET` producer comparing random, balanced, scene-breadth (`B405-197`), and BADGE-submodular coreset selection (`B405-181`, `B405-184`) at `7,200` exposure. |
| `EXP418-19` | `B405-247` | `T85` | `FR` | [Geometric Relation Attention and Containment Graph Head (`FocusGraphFormer`)](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-19-Focus-Graph-Relation-Head.md) | Resolves the `3` multi-score ambiguity cases (`1 row`, `2 tabs`) in `DetectorFocusFollowup.md` and parent-child nested box competition (`B405-210`, `B405-219`). |
| `EXP418-20` | `B405-248` | `T86` | `DEPLOY` | [Fisher-Weighted Model Soups and Task-Vector Merging (`FisherSoup`)](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/Experiments/EXP418-20-Fisher-Model-Soup-Merging.md) | Merges existing compatible checkpoints ($\theta_{\text{base}}, \theta_{12.5}, \theta_{25}$) by diagonal Fisher precision (`PM08`) in `< 90 s` without runtime two-model fallback (`B405-203`). |

---

## 4. Template Registry Summary (`T67` to `T86`)

| Template | Adapter Call | Profile | Required Keys | Optional Keys |
| :--- | :--- | :--- | :--- | :--- |
| `T67` | `nwd_detector_train418.run` | `training` | `datasetYaml`, `baseWeights`, `evalLabels`, `epochs`, `seed` | `nwdWeight`, `nwdConstant`, `smallAreaMax`, `imageSize` |
| `T68` | `fda_transfer418.run` | `training` | `manifest`, `styleRefs`, `epochs`, `seed` | `beta`, `blendProb`, `batchSize` |
| `T69` | `set_contrastive_focus418.run` | `training` | `manifest`, `screenGroups`, `epochs`, `seed` | `supconWeight`, `listmleWeight`, `temperature`, `dustbinInit` |
| `T70` | `coord_ring_crop418.run` | `training` | `manifest`, `encodingMode`, `epochs`, `seed` | `stripHeight`, `perimeterWidth`, `marginRatio` |
| `T71` | `dipole_ring_proposals418.run` | `diagnostic` | `manifest`, `kernelVariant` | `dipoleZMin`, `moatContrastMin`, `shortSideQuantile` |
| `T72` | `counterfactual_synthesis418.run` | `diagnostic` | `failureReport`, `twinFamily`, `pairCount`, `seed` | `outputManifest`, `verifyPixelDiff` |
| `T73` | `sahi_wbf_inference418.run` | `diagnostic` | `model`, `labels`, `tileLayout` | `scaleGatePolicy`, `wbfIouThreshold`, `confidence`, `engine` |
| `T74` | `distilled_coreml_compress418.run` | `diagnostic` | `checkpoint`, `calibrationManifest`, `compressionMode` | `marginTemperature`, `flipPenalty`, `maxBytes` |
| `T75` | `kinematic_transition418.run` | `diagnostic` | `pairsManifest`, `detectorModel`, `focusModel` | `scrollPhaseThreshold`, `coneHalfAngleDeg` |
| `T76` | `confident_label_auditor418.run` | `diagnostic` | `primaryPreds`, `secondaryPreds`, `groundTruth`, `renderedBodies` | `ocrReceipts`, `minConfidence`, `iouMatchThreshold` |
| `T77` | `nullspace_focus_train418.run` | `training` | `manifest`, `anchorManifest`, `epochs`, `seed` | `subspaceEnergy`, `lpWarmupEpochs`, `nativeDose`, `batchSize` |
| `T78` | `copula_proposal_stn418.run` | `training` | `trainingMatches`, `manifest`, `epochs`, `seed` | `samplerMode`, `enableStnRefiner`, `stnLossWeight` |
| `T79` | `group_dro_pareto418.run` | `training` | `manifest`, `selectionGroups`, `evaluationGroups` | `mode`, `droEta`, `droSizePenalty`, `epochs`, `seed` |
| `T80` | `conformal_energy_abstention418.run` | `diagnostic` | `calibrationReports`, `evaluationReports` | `alpha`, `temperature`, `oodEnergyThreshold` |
| `T81` | `strip_iou_detector418.run` | `training` | `datasetYaml`, `baseWeights`, `evalLabels`, `epochs`, `seed` | `projIouWeight`, `enableStripPooling`, `imageSize` |
| `T82` | `prefix_ocr_route_matcher418.run` | `diagnostic` | `observationsPath`, `adversarialPath` | `anchorPhrase`, `maxTailCost` |
| `T83` | `context_counterfactual_crops418.run` | `diagnostic` | `cropsManifest`, `model` | `interventionMode`, `haloOuterPx`, `bodyInnerInsetPx` |
| `T84` | `submodular_coreset_subset418.run` | `diagnostic` | `poolManifest`, `targetCount`, `seed` | `selectionStrategy`, `familyQuotas`, `maxViewsPerGroup`, `uncertaintyWeight` |
| `T85` | `focus_graph_relation418.run` | `diagnostic` | `screenFeaturesManifest`, `evaluationReports` | `mode`, `containmentIoaThreshold`, `epochs`, `seed` |
| `T86` | `fisher_model_soup418.run` | `diagnostic` | `checkpoints`, `trainingManifests`, `evaluationReports` | `mergeMode`, `mixingWeights`, `recalibrateBn` |

---

## 5. Phased Execution Waves (Maximizing Discovery per Compute Minute)

1. **Wave 1 — Immediate Zero-Training Unblockers & Cached Diagnostics (`< 6 min` Total CPU)**:
   - `EXP418-16` (`T82`): Prefix-Anchored OCR Route Matcher to unblock `B405-220` native capture on `Maximum-mini-TTR`.
   - `EXP418-20` (`T86`): Fisher-Weighted Model Soup (`FisherSoup`) merging existing $\theta_{\text{base}}$, $\theta_{12.5}$, and $\theta_{25}$ checkpoints in `< 90 s`.
   - `EXP418-14` (`T80`): Helmholtz Free-Energy + Split Conformal Abstention on cached `T57`/`T63` scorecards (`PAPER417-STATES`).
   - `EXP418-17` (`T83`): Scale-Preserving Contextual Counterfactual Crops (`B405-198`) on `Sillycon-TTR` archive and development crops.
   - `EXP418-18` (`T84`): Submodular + BADGE Coreset Selector (`PAPER417-SUBSET`) to prepare `B405-181`, `B405-184`, and `B405-197`.
   - `EXP418-05` (`T71`): Signed Moat-Ring Dipole Filter for light-theme HCF (`B405-161`).
   - `EXP418-07` (`T73`): Scale-Gated `640 px` SAHI + WBF multi-scale detector inference (`B405-121`).
   - `EXP418-10` (`T76`): Confident Learning + OCR Automated Label Auditor (`B405-129`).
2. **Wave 2 — Sub-5MB Deployment & Fast Head/Graph Refiners (`< 15 min` Total)**:
   - `EXP418-19` (`T85`): Geometric Relation Attention & Containment Graph Head (`FocusGraphFormer`) on cached `1280-d` features.
   - `EXP418-08` (`T74`): Margin-Distilled 6-bit Core ML Palettization (`< 5 MB`) for `MODEL-DIST-02`.
   - `EXP418-09` (`T75`): Kinematic Phase-Correlation Scroll & Action-Cone Transition Decoder.
3. **Wave 3 — Targeted Representation & Zero-Forgetting Training (`<= 30 min` per Fit)**:
   - `EXP418-11` (`T77`): Null-Space Projected Fine-Tuning (`Null-LoRA` + `LP-FT`) for zero-forgetting native adaptation.
   - `EXP418-12` (`T78`): Empirical Gaussian Copula Proposal-Error Sampler + `ProposalSTN` crop refiner (`B405-196`).
   - `EXP418-13` (`T79`): Group-DRO Minimax Training + Pareto Worst-Family Checkpoint Selection (`B405-192`).
   - `EXP418-03` (`T69`): Within-Screen Set-Contrastive (`SupCon` + `ListMLE`) Focus Ranking.
   - `EXP418-04` (`T70`): Coordinate-Aware Boundary-Strip Unwarping (`CoordRing`).
   - `EXP418-15` (`T81`): Anisotropic Strip Pooling + 1D Projected IoU (`Strip-IoU`) for wide `listRow` detection.
   - `EXP418-01` (`T67`), `EXP418-02` (`T68`), and `EXP418-06` (`T72`).
