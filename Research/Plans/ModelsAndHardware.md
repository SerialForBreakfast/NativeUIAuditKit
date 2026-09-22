# Model and hardware packets

**Revision:** 4, 2026-09-19. Read the [common contract](../ImplementationPlans.md#common-execution-contract), [accepted decisions](../DeliveryDecisions.md), and assigned packet only. All assignments are NUA-owned except device operations executed through TVTestRig's authorized workflow. Tasks.md is the sole state/ownership queue. Relevant skills: nativeui-model-workflow for train/eval/export; tvos-fixture-training and tvos-safe-navigation for actual capture. Do not treat historical skill commands as overriding project boundaries.

All runs use unique in-project output/cache/temp locations and local dependencies. Log actual training before starting; no automatic experiment sweeps. These packets describe later execution authority required at dispatch, not authority granted by writing the plan. Required offline software checks apply to code changes; hardware evidence never substitutes for those checks.

## TRAIN-S — Bounded full-frame smoke execution

**Parent:** TASK-6a-10. **Inputs:** accepted P5-B, eligible real corpora and explicit smoke assignment. **Scope:** train_ios_model.py invocation, isolated artifacts, ExperimentLog entry; no full run or promotion.

Allocate/log the next run ID, checkpoint/corpus/config hashes and output path. Execute the existing two-epoch smoke behavior with its deviations recorded (5% data and inactive warmup where applicable). Validate data loading, fresh checkpoint initialization, output saves and completion. Verify schedule configuration separately; do not claim inactive warmup was exercised.

**Acceptance:** exit code/runtime, effective settings, logs/checkpoint readability and exact coverage limitations. On deterministic failure diagnose before retrying; no full-run fallback. **Next:** TRAIN-F if accepted.

## TRAIN-F — 41-class full-frame training

**Parent:** TASK-6a-10. **Inputs:** P5-B, accepted smoke evidence, explicit full-run assignment. **Scope:** one logged 150-epoch-target candidate with fresh optimizer/schedule from Run 009 best.pt; no new taxonomy, automatic sweeps or promotion.

Revalidate frozen inputs and unique outputs, allocate the experiment ID, log before launch. Use accepted blend, cosine/warmup/patience settings. Preserve last/best/backup checkpoints and record intentional early stop versus crash. Resume only this run from a verified epoch checkpoint when assigned; do not silently restart or change parameters. Failure returns diagnosis and a proposed next experiment.

**Acceptance:** completed or deliberately early-stopped candidate, logs/effective config, checkpoint hashes and experiment outcome. Crash is not completion. **Next:** TRAIN-Q.

## TRAIN-Q — Dual-holdout qualification

**Parent:** TASK-6a-10. **Inputs:** TRAIN-F candidate, frozen eligible fixture and synthetic holdouts, P1/P2 evaluator. **Scope:** evaluation and report; no promotion.

Evaluate independently: fixture mAP50 ≥0.94, mAP50:95 ≥0.78, toggle/stepperControl AP50 ≥0.88; synthetic withheld-template DS-G8 mAP50 ≥0.85. Report per-class support, absent classes, per-platform results and comparison compatibility. Badge is excluded from this 41-class gate. Missing support cannot yield a passing per-class gate. Run compact regression diagnostics without substituting them for complete holdouts.

**Acceptance:** pass/fail for each gate with model/corpus/settings hashes. Any failure retains current shipped models and returns a diagnosis, not a retraining loop. **Next on pass:** REL-A, macOS gate readiness, crop fork; later model work is not a release prerequisite.

## FR-A — FocusRing software/data readiness

**Parent:** FOCUS-DET-05. **Inputs:** FocusRingDetectorSpec, manifest and packaged metadata; BP-46/47, K-10. **Files:** harvest/train/eval FocusRing scripts and focused tests; spec/version-label docs; no compiled-resource mutation or live capture.

Inspect packaged model metadata and FDR-001 history; distinguish actual modelID/versionString from qualification milestone labels, correcting prose without relabeling weights. Add coverage/pair-integrity/seed-split checks and reject model-prediction labels. Retain vendored MobileNetV4, 16% crop expansion, 256×256 RGB training input and trace-based export.

Prepare a recipe manifest meeting gridMatrix ≥2,000, mediaShelf ≥1,500, settingsList ≥1,000, and actionDialog/heroCarousel/focusMaze ≥500 each. Require light and highContrast each ≥20% within gridMatrix and mediaShelf. Hold out ≥100 hard negatives across light/highContrast × imageView/collectionItem with every combination nonempty; report counts and FPR by combination.

Implement the additive ADR-0007 alignment envelope and a fail-closed manifest validator.
Its five source-backed matrix rows are normal directional alignment, VoiceOver exploration,
VoiceOver traversal, intentional fixture fault, and absent producer state. Expected
exploration/traversal decoupling is a policy-negative control, not a visual-model error.
Unknown state must remain `notAssessable`; do not reconstruct it from captions or pixels.

**Acceptance:** offline tests for missing pair, wrong crop geometry, split leakage, unlabeled samples, underfilled scene/theme quota, empty hard-negative strata, and every ADR-0007 malformed/missing-matrix case. Recipe and validation reports do not claim collected data. **Next:** FR-B.

## FR-B — Qualified FocusRing harvest

**Parent:** FOCUS-DET-05. **Inputs:** FR-A recipe, available/authorized Office window, verified supported capture path and compliant output boundary. **Scope:** fixture-only closed-loop capture; no Home/Select/Settings crawl or training.

The [Office delivery amendment](OfficeFocusRing.md) is canonical for smoke → physical
pilot/shipped baseline → scale-up → one candidate sequencing. The ADR-0007 matrix above
belongs to separately assigned semantic capture/policy work; it is not a visual FR-B
prerequisite. Present alignment metadata must still validate. Physical execution
needs its own authority; the scoped parallel simulator assignment does not authorize it.

Collect incrementally; validate each completed batch before accepting counts. Keep paired/related seed samples in one split and preserve source/capture evidence. Exclude unsettled, duplicate, malformed or untrusted-label samples. Check cumulative scene/theme/hard-negative quotas and stop at a complete ≥6,000-pair corpus, retaining rejection reasons.

**Acceptance:** eligible manifest with genuine ground truth, complete quota/split report, held-out hard-negative strata all populated. Unavailable device or failed identity stops dependent capture without disturbing offline work. **Next:** FR-C.

## FR-C — FocusRing candidate and export qualification

**Parent:** FOCUS-DET-05. **Inputs:** FR-B corpus; explicit training/export assignment. **Files/output:** existing FocusRing scripts and isolated candidate directory; no automatic bundled-resource replacement.

Log first; use established MobileNetV4 baseline: 30 epochs, batch 64, LR 3e-4, HFlip-only first candidate, no vertical flip, no timm import. Preserve validation/test seed separation. Evaluate accuracy ≥99%, unfocused FPR ≤0.5%, focused FNR ≤1%, precision/recall at 0.85 each ≥0.98, and non-vacuous hard-negative FPR ≤0.5% including required strata reporting.

Export with torch.jit.trace to FP16 CoreML; preserve output/threshold metadata and ≤5 MB package gate. Compare exported decisions and probabilities against PyTorch on held-out crops; report numerical error and whether any decision changes cause a gate failure. Optional-model fallback remains intact.

After qualification, the Office plan specifies separately authorized TTR comparison of
shipped/candidate focus decisions and navigation. Telemetry scores outcomes only.

**Acceptance:** all six gates supported by sample counts, package size/export parity and traceable artifacts. Threshold tuning uses validation only. Promotion requires a separate qualified release assignment. **Next:** REL-A for the chosen model; failures return diagnosis.

## R-A — Real tvOS holdout capture specification

**Parent:** TASK-6b-R-1. **Inputs:** existing hardware-qualification reports/manifests, tvOSTrainingStrategy and navigation skills. **Scope:** inventory and capture-plan/validation tooling/tests; no device operation.

Inventory existing qualified frames and ground-truth availability; count unique content, not filenames. Derive the app/surface matrix from existing qualification evidence and record per-cell target counts totaling ≥500, source/OS/device provenance, deduplication, annotation status and approved navigation boundary. Unknown app availability is a capture prerequisite, not authority to install/log in/purchase. Document safe progress counters and resume behavior.

**Acceptance:** reviewed matrix, counters distinguish screenshots from labeled mAP examples, no prediction-as-ground-truth path, offline invalid/duplicate/provenance tests. **Next:** R-B.

## R-B — Incremental real-device captures

**Parent:** TASK-6b-R-1. **Inputs:** R-A matrix, authorized available device/app scope and compatible capture path. **Scope:** approved closed-loop capture only.

Verify app/focus state after each permitted navigation step. Capture unique frames and matching provenance into in-project storage; validate before incrementing matrix counts. Stop on boundary uncertainty, destructive action, missing authorization or identity failure. Preserve partial progress; no blind retry/crawl expansion.

**Acceptance:** ≥500 unique qualified screenshots covering the approved matrix; labeled/unlabeled counts separated. **Next:** R-C.

## R-C — Freeze and benchmark tvOS holdout

**Parent:** TASK-6b-R-1 / TASK-6a-11 production corpus. **Inputs:** R-B complete manifest and shipped tvOS model. **Scope:** freeze/hash, inference and report; no training.

Validate immutable membership and genuine annotation support. Benchmark the shipped model; report latency and qualitative coverage for screenshot-only sets. Compute mAP only for trustworthy image+box ground truth with disclosed coverage; keep the reference corpus unavailable for quantitative comparison when labels are absent. Do not manufacture annotations to close the task.

**Acceptance:** frozen capture evidence and truthful benchmark/availability report. Capture-scale parent can close on its capture AC; quantitative reference requirement remains open when ground truth is absent. **Next:** future model comparisons.

## MAC-A — macOS coordinate spike

**Parent:** TASK-6c-1. **Inputs:** documented DS-G8 pass; architecture coordinate rules/BP-10. **Files:** diagnostic AppKit spike, coordinate tests and Research spike report; no training.

Render known rectangles on macOS 15, convert AppKit bottom-left content coordinates to top-left screenshot pixels, and compare against actual PNG geometry. Cover nonzero bounds/content offsets and display scale; do not assume window chrome equals content coordinates.

**Acceptance:** ≤±2-point error with rendered evidence and testMacOSCoordinateFlip; all cases verified before generator implementation. **Next:** MAC-B.

## MAC-B — macOS generator and corpus

**Parent:** TASK-6c-2. **Inputs:** MAC-A accepted conversion and frozen taxonomy. **Files:** AppKit generator target/templates and tests, in-project generated artifacts, corpus manifests. Respect existing platform-target boundaries.

Add generator-direct boxes and reproducible family/seed metadata. Produce ≥2,000 macOS images with family-separated train/validation/test, including tooltip examples across withheld and training styles. Validate pixels/boxes, coverage, content hashes and split isolation before declaring trainable. Never import AppKit rendering into the portable library.

**Acceptance:** valid complete corpus, tooltip support and family split audit, generator tests. **Next:** MAC-C after explicit train/export assignment.

## MAC-C — macOS candidate and packaging evidence

**Parent:** TASK-6c-2. **Inputs:** MAC-B and accepted YOLO evaluation pipeline; log actual run before execution. **Scope:** separate model training/evaluation/export, not automatic promotion.

Train a separate candidate and evaluate frozen withheld templates. Require mAP50 ≥0.80 and tooltip AP50 ≥0.70 with nonzero support. Verify CoreML coordinate/label parity and resource loading; prepare NativeUIDetector_macOS_v1 packaging evidence without replacing other platforms' models.

**Acceptance:** gates, export tests, manifests and report hashes; candidate remains unshipped pending release review. **Next:** REL-A.

## BADGE-A — Append-only taxonomy and decoder compatibility

**Parent:** TASK-BADGE-01. **Inputs:** DeliveryDecisions §4, current enum/category map/annotation schema and model manifests; BP-28. Specification work is independent; production 41-class mapping remains frozen. **Files:** architecture §5/6, versioned taxonomy/schema, enum/model-decoder metadata and focused tests when separately assigned for code.

Define badge as notification/status dot/count marker, not ordinary button/decorative text. Append ID 41 without sorting/reassigning IDs 0–40. Publish minor taxonomy/library version and dataset taxonomy-change version. Retain old map and declare each model's taxonomy; legacy bundled descriptors explicitly use their existing maps. Unknown model/map combinations fail clearly rather than defaulting to latest. Preserve container boxes alongside badge boxes in the new annotation version.

**Acceptance:** old raw values/IDs and old annotations round-trip unchanged; old model outputs decode identically; new 42-class fixture decodes badge; mismatch rejected; compatibility cases supplied for producer/consumer. No weights are relabeled as 42-class. **Next:** BADGE-B after current 41-class milestone.

## BADGE-B — Badge corpus and candidate

**Parent:** TASK-BADGE-01. **Inputs:** accepted 41-class milestone, BADGE-A mapping/decoder, eligible corpus/generation plan. **Scope:** separately logged generation/train/eval candidate assignment; no alteration of historical 41-class artifacts.

Add generator-direct dot/count badge boxes covering position, size, theme/contrast and hard negatives; preserve enclosing annotations. Create a new corpus/model version and baseline with reliable class/style coverage. Evaluate badge AP50 ≥0.88 on supported holdouts and the applicable full-frame gates. Report existing-class metrics separately from the 42-class mean; comparisons use compatible maps or explicitly defined common-class projections.

**Acceptance:** coverage/leakage audits, badge support and gates, decoder/export parity; no undifferentiated 41-vs-42 mean comparison. **Next:** REL-A when qualified.

## CROP-A — Crop fork and frozen evaluation definition

**Parent:** TASK-6a-12. **Inputs:** accepted TASK-6a-10 baseline; TrainingDataStrategy partial-capture rules. **Files:** separate augmentation/config and holdout-transform tests/spec; no full-frame default changes.

Define seeded area-fraction crops 0.6–1.0, transform/clip boxes against visible pixels using existing partial-element rules, and keep crop manifest separate from the full-frame holdout. Freeze source IDs/crop parameters and paired baseline evaluations before candidate tuning. Explain why resizing cannot reconstruct context. Enable mosaic/crop only in the experimental fork.

**Acceptance:** deterministic transform tests and image/box alignment, no cross-split leakage, unchanged full-frame config and explicit relative-gain definition. **Next:** CROP-B.

## CROP-B — Crop candidate qualification

**Parent:** TASK-6a-12. **Inputs:** CROP-A and explicit experiment assignment. **Scope:** one logged candidate plus both holdout evaluations, no default-model replacement.

Evaluate baseline and candidate identically. Require full-frame loss ≤0.01 absolute mAP50 and crop relative gain ≥0.15. A zero baseline cannot pass the relative gate by division convention; escalate that criterion for a documented amendment. Report per-class and partial-element support.

**Acceptance:** both gates with compatible evidence; failures retain full-frame model and yield diagnosis. Passing fork remains experimental until separately promoted. **Next:** architect disposition.

## UNI-A — Unified-model experiment readiness

**Parent:** Phase 6b-U. **Inputs:** eligible iOS/tvOS corpora, accepted dedicated-model baselines, compatible taxonomy. **Scope:** balanced sampler/config and tests, per-platform benchmark/budget contract; no training.

Freeze dedicated reference results on identical platform holdouts. Specify platform-balanced training, train-only sampling and explicit label maps. Retain separate model routing. Freeze focus evaluation, chrome FP definition and hardware budgets before training; use published budgets where defined, and obtain a documented numeric budget for uncovered platforms rather than guessing a pass criterion.

**Acceptance:** deterministic balance/no-leakage tests, compatible per-platform references and numeric deployment criteria recorded. **Next:** UNI-B only after readiness accepted.

## UNI-B — Unified candidate and comparison

**Parent:** Phase 6b-U. **Inputs:** UNI-A and explicit logged experiment assignment. **Scope:** train/eval/export qualification, not routing replacement.

Require no platform mAP50 loss >0.02 vs dedicated baselines; tvOS tabBar AP50 ≥0.80 with confusion report; focus precision/recall each within 0.02; no increased iOS FP on bottom chrome/statusBar/homeIndicator/dynamicIsland; declared size/latency budgets met on named physical hardware. Missing hardware measurements leave that gate open.

**Acceptance:** every gate reported independently; aggregate mAP cannot mask platform regressions. Keep dedicated models until a separate release/routing decision. **Next:** REL-A or experiment diagnosis.
