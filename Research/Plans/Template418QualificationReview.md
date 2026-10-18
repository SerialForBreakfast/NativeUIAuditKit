# Review of T67–T86

Owner: Maximum-mini-NUIAK. Date: 2026-10-17.

## Decision

Do not admit the proposed 20 experiments as qualified model work yet.
The source contains useful algorithm prototypes, but several entrypoints do not perform the advertised experiment.
Passing software tests does not establish real image processing, trained checkpoints, or model improvements.
Preserve these modules for correction. Preserve Standard and the existing queue.

## Source findings and next tasks

| Template | Observed execution | Required work before scientific admission |
| --- | --- | --- |
| T67 | Optimizes a box tensor. It does not train YOLO from the supplied checkpoint. | Integrate the loss into the resident detector trainer. Compare against its unchanged loss. |
| T68 | Uses random image patches and writes a formula-based loss curve. | Load pinned training images. Use the transform in real training. Preserve measured phase checks. |
| T69 | Trains small linear layers. Missing features default to repeated focus labels. It does not save those layers. | Reject missing features. Extract pinned features without label leakage. Save and reload the complete candidate. |
| T70 | Uses a random crop and a preset loss curve. | Keep geometry helpers. Apply them to real crops and a compatible trained encoder. |
| T71 | Scores supplied luminance arrays, not full-screen proposals. It assumes HCF implies an expected proposal. | Extract pinned profiles and use observed labels. Measure proposal coverage and wrong selections. |
| T72 | Produces proposed recipes from supplied failure records. It does not capture images. | Validate recipes against TTR's actual schema. Keep generation and capture as separate steps. |
| T73 | Combines supplied full-frame and tile predictions. It does not run sliced inference. | Add verified tile inference and coordinate recovery. Reject missing prediction inputs. |
| T74 | Quantizes numeric arrays and uses fixed estimated package sizes. It does not produce a Core ML package. | Reuse the real exporter. Measure actual package bytes and runtime parity. |
| T75 | Uses supplied positions and scroll offsets. Its queue entrypoint does not call its FFT helper. | Connect pinned frame pairs to measured motion. Keep supplied motion as a separate diagnostic control. |
| T76 | Compares supplied boxes and body evidence. | Verify provenance and independent model evidence. Treat consensus as a review proposal, not ground truth. |
| T77 | Uses a small linear network instead of the production crop encoder. | Integrate projection into the resident crop trainer. Verify complete saved state and matched controls. |
| T78 | Samples supplied errors and tests an identity transform on constant pixels. It writes a preset loss curve. | Use training-only measured correspondences and real crops. Train and save the complete model. |
| T79 | Selects supplied checkpoint summaries and writes a preset loss curve. Missing failure counts default to zero. | Reject missing counts. Connect reweighting and selection to actual training and verified scoring. |
| T80 | Calls empty proposals verified no-focus. Calibration and evaluation apply different score transformations. | Use unknown or abstained for missing proposals. Use identical calibration and evaluation transformations. |
| T81 | Optimizes box tensors and tests pooling on random features. | Integrate loss and pooling into the actual detector. Preserve the baseline architecture comparison. |
| T82 | Compares supplied observation fields and adversarial pairs. | Test retained observations. Keep this offline check separate from TTR's qualified route and recovery. |
| T83 | Constructs flat synthetic crops from luminance values. It does not read retained crop images. | Load pinned original crops. Preserve their geometry and score controlled interventions. |
| T84 | Selects supplied feature rows. Missing features and probabilities have defaults. | Reject missing features. Pin extractor outputs and preserve whole-group selection and rare-class support. |
| T85 | Applies containment suppression to supplied boxes and scores. It does not train a graph head. | Name it as a rule comparison. Test retained cases and report every lost success. |
| T86 | Merges numeric vectors and recalibrates a newly created BatchNorm layer. | Load compatible full checkpoints. Recalibrate their actual layers using training-only inputs. |

These findings come from each module's `run` entrypoint and its called helpers.
The reported 67 passing tests were not independently rerun during this review.
Existing queue tests use synthetic software fixtures. Those fixtures are not training evidence.

## Priority

1. Finish training-only proposal preparation and review real correspondence support.
2. Qualify the resident detector training wrapper with approved, complete train and calibration membership.
3. Connect T78's useful sampler ideas only after measured correspondence support passes review.
4. Adapt T73 and T85 into clearly named prediction comparisons on retained cases.
5. Qualify T72 recipes and T82 observation replay without changing TTR execution ownership.
6. Keep the other research ideas blocked on their exact integration requirements above.

Do not bulk-approve the proposed IDs. Check the current catalog before assigning IDs.
T80 cannot establish verified no-focus from a missing proposal list.
T74 cannot pass a package-size gate from an estimated constant.
No prototype result grants model acceptance or navigation authority.
