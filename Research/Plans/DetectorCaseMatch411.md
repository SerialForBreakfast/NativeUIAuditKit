# CASEMATCH411 — T42 detector-case-match (ENG405-02)

Date: 2026-10-15. Owner: Maximum-mini-NUIAK. Status: adapter complete; 15 jobs registered and approved.

## Purpose

T42 matches cached detector predictions to labels per object. It performs no new inference.
It reports per-class gains and lost prior successes between a baseline and a candidate.
A lost prior success is a label that the baseline detects and the candidate does not.

## Contract

- Template: `T42` in `scripts/hcf_templates395.py`. Adapter: `scripts/detector_case_match411.py`.
- Input: 1 pinned `bundle` (`detector-case-inputs-v1`). The bundle pins the predictions, the labels, and the category map.
- Parameters: `slice` (`class`, `geometry`, `position`, `screen`), `classes`, `groups`, `matching` (`class-aware`, `class-agnostic`).
- Matching: greedy, one to one, in score order, IoU 0.5. This is the `eval_run013.score` rule.
- Each label gets 1 status per model: `detected`, `wrong-class`, `mislocalized`, or `missed`.
  - `wrong-class`: a box of another class overlaps the label at IoU 0.5 or more.
  - `mislocalized`: an eligible box overlaps at IoU 0.1 or more, but no match occurs.
- Outputs: `benchmark_summary.json` (`gains`, `lostPriorSuccesses`, `slices`, `decisions`, `modelAccepted=false`) and `cases.json` (per-object rows).
- Unmatched predictions are not reviewed false positives. The summary reports them as `unmatchedPredictions`.

## Input bundles

| Bundle | Role | Models | Labels | Label review |
| --- | --- | --- | --- | --- |
| `Research/Experiments/detector-case-ios-r013.json` | withheld-diagnostic | Run 009 and Run 013, 2,000 withheld images, confidence 0.25 | `NativeUITrainer/yolo_dataset_r7_ssd03_frozen` YOLO labels, hash-checked against `withheld_manifest.json` | unknown |
| `Research/Experiments/detector-case-tvos-sc36.json` | development | `nativeui-tvos-v3.0` only, 46 real frames, confidence 0.5 | REAL-MODEL-SCORECARD-36 reviewed control bounds | reviewed (frames incomplete) |

The Run 013 baseline receipt names a path in an older checkout.
The adapter uses the local copy `reports/work/IOS-R6-BASELINE-20260923/prediction_artifact.json` only after these checks:

- The receipt hash equals the hash of the local copy.
- The checkpoint hash is the same.
- The detections for each image are the same.

The tvOS bundle has 1 model. Its jobs describe misses and report no gains or losses.

## Qualification

- Class-aware detections per class equal the `tp` values in `reports/work/IOS-R013-EVAL/evaluation.json` for both models.
- Class-agnostic tvOS detections per role equal the scorecard `localized50` counts.
- Queue tests use an isolated queue. They cover a positive job, a changed input (`input_changed`), and a final-audit role (`bundle_role`).

## Limits

- The source sidecars record no toggle on, off, or disabled variation, and no progress determinate or indeterminate state.
  B405-016 and B405-017 therefore slice by geometry. State questions stay blocked until state labels exist.
- No reviewed tvOS `tabBar` or `toolbar` labels exist. B405-108 cannot measure the tvOS tabBar AP gate.
- The withheld iOS set is a reused diagnostic set, not a final challenge. No model is accepted from T42 results.

## Wave 2 extensions, 2026-10-15

T42 gains these options. Earlier jobs keep their exact specs and results.

- Slice `state`: the label focus state (tvOS `focused` or `unfocused`; iOS `unknown`). Unmatched boxes share the bin `prediction`.
- Slice `edge`: a label or box within 2 px of the image border is `edge`, otherwise `interior`.
  This is a geometric proxy for clipping. It is not reviewed clipping metadata.
- Matching `class-aware-suppressed`: only the candidate arm gets 1 fixed cross-class suppression at IoU 0.5.
  The highest score wins. The baseline arm stays unchanged, so lost prior successes are the labels that the suppression removes.
- Each missed label records `fit`, the relation of its nearest eligible box:
  - `larger`: the box covers 80 % or more of the label, with 1.5 times its area or more.
  - `smaller`: the label covers 80 % or more of the box, with 1.5 times its area or more.
  - `offset`: the boxes overlap without either relation.
  - `None`: no eligible box overlaps the label.

  Summaries count fits per slice as `missFit`.
- Bundle `detector-case-ios-r013-all.json` is the same Run 009/013 bundle at confidence 0.001. It reads every stored prediction.

## T50 — Vision rectangle proposals

- Adapter: `scripts/vision_proposals415.py`. Tool: `.build/vision-probe/vision_annotation_probe`, compiled from `scripts/vision_annotation_probe.swift`.
- Inputs: `labels`, `baseline` (stored tvOS scorecard), and `tool`. Parameters: `proposals` (`none` or `rectangles`) and `slice`.
- The probe uses VNDetectRectanglesRequest with fixed settings: 40 observations, minimum size 0.01, and confidence 0.5.
- Rectangles carry no class, so both arms use class-agnostic matching.
- The `none` arm must reproduce the stored scorecard: 346 of 583 controls located.
- Tests: `scripts/test_vision_proposals415.py` covers the control arm, the rectangle arm, and a changed tool (`input_changed`).
