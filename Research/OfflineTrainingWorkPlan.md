# Office-independent training preparation

**Date:** 2026-09-19  
**Status:** Implementation plan; no implementation or experiments started by this document.  
**Tracking:** TASK-6a-10 and TASK-6a-11 in [Tasks.md](../Tasks.md).  
**Dispatch:** Revision-4 [ImplementationPlans.md](ImplementationPlans.md) supersedes this document's work-package grouping and acceptance language; retain this document as historical background. ScreenAuditKit now has separately owned SA-A/SA-B packets. Current decisions and gates are in DeliveryDecisions.md.  
**Objective:** Establish a reproducible Run 009 baseline and prepare the data and training pipeline while Office is occupied and TVTestRig implements HarvestIdentity.

**Execution update:** [IterationRoadmap.md](IterationRoadmap.md) and ImplementationPlans revision 4 provide individually dispatchable software, data integration, live qualification and later-model packets. Use those contracts for assignment. A blocked M1/M2 experiment does not block completing its software slice. TVTestRig iteration uses [a source-pinned compatibility loop](TVTestRigIntegrationContract.md) without waiting for recovery or new weights.

## Scope and boundaries

**2026-09-19 revision — dataset recovery comes first.** All 2,000 test image symlinks are broken; train and validation are also incomplete. See [verified availability](../reports/dataset_availability_2026-09-19.md) and [P0 recovery plan](DatasetRecoveryPlan.md). Missing source pixels block M1's actual inference and M2's actual frozen-suite baseline. Tooling and offline fixture tests may continue. The cause is unknown; deletion by an agent is not established. Existing 0.586 metrics remain historical evidence, not current data availability.

Work packages 1–4 belong to NativeUIAuditKit. Work package 5 is a separate ScreenAuditKit handoff. All generated files, caches, logs, and temporary artifacts must stay inside this repository. Existing external datasets may be read but must not be modified. Hardware capture, TVTestRig changes, model promotion, release tagging, macOS training, and the partial-crop training fork are outside this offline scope.

Synthetic test batches validate software behavior; they do not count toward real fixture coverage or acceptance metrics. No model predictions become ground truth. Preserve the synthetic withheld-template holdout and the upstream fixture held-out split independently.

The current live blocker is `identity_preflight` / `identityUnavailable`, documented in [the TVTestRig feedback](../reports/tvtestrig_feedback_2026-09-18.md) and Tasks.md. CurrentState.md and FixtureBatchIngest.md were reconciled with that evidence on 2026-09-19. Office availability is a separate prerequisite even after attestation works.

## Work package 1 — Reproducible per-image reference evaluation

**Priority:** First. **Parent:** TASK-6a-11. **Dependency:** Local Run 009 weights and the existing synthetic test images/labels.

### Implementation sequence

1. Inventory the exact checkpoint, category map, dataset manifest, test labels, installed evaluator version, and existing metric artifacts. Record hashes and counts. Preserve existing baseline artifacts before any new evaluation writes.
2. Document a versioned prediction-artifact contract in Research before changing the evaluator. Include model and corpus hashes, evaluator settings, image identity, dimensions, coordinate convention, class IDs, confidence scores, and original-image boxes. Use repository-relative paths or stable corpus IDs rather than machine-specific paths.
3. Add an optional prediction export to `scripts/eval_phase6a.py`. Reuse the actual inference results; include an explicit record for every image with zero detections. Distinguish successful empty predictions from unreadable images or failed inference.
4. Give new runs unique output directories and record confidence threshold, IoU/NMS settings, image size, preprocessing, device, and package versions. Prevent stale prediction labels from previous runs from contaminating evaluation.
5. Extend `scripts/eval_reference_metrics.py` to reference the exported predictions and verify model/corpus compatibility before computing comparisons. Keep unavailable corpora marked unavailable. Hash stable content separately from run timestamps so integrity and reproducibility are distinguishable.
6. Run Run 009 inference on the existing synthetic holdout and produce aggregate/per-class metrics plus the prediction artifact. Explain any difference from the recorded 0.586 baseline rather than replacing that number without investigation.
7. Correct the stale blocker descriptions and record the evaluation outcome, command, elapsed time, and artifact hashes in Research.

### Deliverables

- Versioned artifact specification and evaluator/exporter changes.
- New run-specific reports beneath `reports/`, with a manifest linking checkpoint, corpus, metrics, and predictions.
- Focused offline tests for empty predictions, coordinate recovery, class IDs, provenance mismatches, missing images, and stale output isolation.

### Acceptance

- Exactly one prediction record per evaluated image; no silently skipped failures.
- Exported boxes and scores correspond to the inference used for metrics, with a tested original-image coordinate conversion.
- Aggregate metrics can be traced to a specific checkpoint and immutable corpus description.
- Cross-model/cross-corpus comparisons fail clearly when incompatible; absent real-device corpora remain unavailable.

## Work package 2 — Freeze a synthetic regression suite

**Priority:** Second. **Parent:** TASK-6a-11. **Dependency:** Work package 1's artifact contract; corpus selection can be prepared earlier.

### Implementation sequence

1. Define a versioned manifest with image/annotation hashes, source corpus and split, template family, platform, class coverage, and dimensions. Select only from the existing synthetic test split, using a deterministic seed and explicit selection criteria.
2. Propose a compact target of approximately 200–300 images, adjusted after inventory. Stratify by available template families, aspect ratios, class frequency, and small-element coverage. Identify missing coverage rather than inventing examples or claims of all-class coverage.
3. Check image-content duplicates, source IDs, and template-family separation against training and validation. Keep related images together. Record suite membership before evaluating a future candidate.
4. Freeze the manifest and evaluate Run 009 through the same prediction/metric path. Include per-class sample counts and undefined metrics for classes without support.
5. Add candidate-versus-baseline reporting, including per-class and small-control changes. Specify which results are informational versus blocking; retain existing DS-G8 thresholds as the shipping authority.

### Deliverables and acceptance

- A checked-in manifest/specification and a Run 009 regression report; images remain in their existing dataset locations.
- Repeated manifest generation is deterministic; changed or missing images/annotations invalidate the suite.
- No suite item is available to training or OHEM. No threshold tuning against this suite.
- The report explicitly calls this a synthetic subset of the existing holdout, not independent real-world evidence. Full DS-G8 evaluation still uses the complete original holdout.
- Changes to suite membership create a new version and require re-evaluation of both compared models.

## Work package 3 — Fixture ingest and corpus assembly hardening

**Priority:** Can proceed alongside work packages 1–2. **Parent:** TASK-6a-10 preparation. **Dependency:** Verified producer contract; final live compatibility awaits an attested harvest.

### Implementation sequence

1. Compare the existing ingest assumptions with the versioned TVTestRig harvest contract using read-only source/docs. Record the producer revision and expected schema. Define required provenance fields from that contract; do not invent an attestation format or manufacture valid identity evidence.
2. Expand `scripts/test_ingest_fixture_batch.py` with small, hand-built inputs covering malformed/missing manifest entries, missing images, empty annotations, unknown classes, invalid/nonfinite boxes, mismatched dimensions, unsettled frames, duplicate IDs, split conflicts, and unsupported versions.
3. Verify baseline-frame deduplication and forced unfocused labels. Detect identical image content or related recipe families crossing train/calibration/held-out boundaries; quarantine/report conflicts rather than silently moving examples.
4. Verify source paths cannot escape the declared input root and output paths cannot escape the project, including symlink cases. Separate test-only synthetic data from eligible training corpora in provenance.
5. Add deterministic corpus assembly: preserve synthetic train/validation/test boundaries, upstream fixture training/calibration/held-out boundaries, and source/platform metadata. Calibration remains excluded from training. Compute class weights from training data only.
6. Produce a composition report with counts by source, split, family, class, and small-object size. Parameterize the blend; choose final proportions only after real class coverage is measured. Audit that neither export nor OHEM reintroduces held-out samples.
7. Resolve the existing schema mismatch: ingest emits tvOS scale=1 while the current annotation schema allows only 2/3. Document and version any schema change before implementation, preserving old annotation compatibility.
8. Document how tvOS fixture examples are used in the 41-class iOS experiment. Shared taxonomy alone is insufficient evidence of platform equivalence; retain platform provenance and report iOS and fixture outcomes separately. This preparation does not close the separate unified-model gate.

### Deliverables and acceptance

- Updated ingest specification, meaningful failure-case tests, and corpus assembly command/report.
- Identical source manifests produce identical corpus membership; no test/calibration leakage or unreported dropped labels.
- Unknown classes are counted and quarantined/dropped according to the established policy, never silently remapped. Batches with no usable labels fail eligibility checks.
- Test fixtures remain visibly synthetic and cannot satisfy real-harvest readiness checks.
- End-to-end live validation remains an open checkbox until genuine attested output exists.

## Work package 4 — Prepare the next 41-class training experiment

**Priority:** After the data contract is settled; configuration work can start earlier. **Parent:** TASK-6a-10 preparation. **Dependencies:** Work packages 1 and 3 for full readiness.

### Implementation sequence

1. Use a descriptive placeholder such as `phase6a_fixture_candidate` during planning. Runs 010–012 already exist; allocate the next sequential run ID from ExperimentLog.md immediately before a real run starts.
2. Specify a fresh fine-tuning run initialized from Run 009 `best.pt`, targeting 150 epochs with cosine scheduling and warmup, as Tasks.md requires. This is distinct from resuming Run 009's optimizer/training state.
3. Add explicit initial-weights and schedule configuration where needed: `train_ios_model.py` currently exposes `--resume`, but no fresh-run checkpoint argument or explicit cosine control. Document the exact resolved hyperparameters, early-stopping policy, seed, batch size, and dataset hashes.
4. Review inherited augmentation settings against the full-frame policy. The trainer currently includes mosaic/scale/flip settings; document the chosen full-frame behavior before changing it. Keep TASK-6a-12's crop experiment gated on completion of 6a-10.
5. Add a validation-only preflight that checks files, taxonomy, splits, available local weights, provenance, cache/output boundaries, and configuration without importing a training run or downloading weights. It must clearly distinguish configuration readiness from missing real-data readiness.
6. Optionally run a short pipeline smoke experiment on eligible existing synthetic data after logging it. The current `--dry-run` trains for two epochs on 5% of data, changes settings, and disables warmup; it does not validate the entire planned schedule. Test schedule construction separately and label smoke results accordingly.
7. Prepare a launch/evaluation runbook, including unique output directories, in-project caches/temp paths, logs, interrupted-run recovery, and model promotion criteria. Preserve Run 009 and previous run artifacts.

### Deliverables and acceptance

- Versioned configuration, validation-only preflight, and launch runbook.
- The resolved run loads the intended checkpoint as initial weights with a fresh optimizer/schedule, uses the intended corpus, and cannot overwrite an existing run.
- Preflight reports actionable failures for absent real fixture data and supports offline configuration testing.
- Any smoke experiment is logged before execution and is explicitly not an accuracy result or proof of harvest readiness.
- The plan is ready to launch once capture, provenance, class coverage, and split checks pass; no full retraining is part of the current planning deliverable.

## Work package 5 — ScreenAuditKit integration handoff

**Priority:** Optional independent workstream. **Parents:** TASK-9-2 and TASK-9-3. **Execution location:** ScreenAuditKit repository, subject to its own instructions. This plan does not authorize edits outside NativeUIAuditKit.

1. Inspect the consumer's actual contract and CLI before implementation; reconcile its current API with NativeUIAuditKit architecture section 12.
2. Add required/forbidden element constraints and minimum confidence with defined validation/error behavior and backward-compatible decoding of contracts without `uiElements`.
3. Wire rule reporting for missing/unexpected elements, bounds, truncation, clipping, target size, and inferred OS mismatch. Define how multiple matching detections are handled.
4. Add `screenaudit validate --native-ui none|coreml`, defaulting to `none`. Explicit CoreML use with unavailable model resources must fail clearly with exit status 1; the no-op path skips native constraints as specified.
5. Verify with an injected deterministic recognizer and offline fixtures: passing/failing constraints, confidence boundaries, no-op behavior, JSON output stability, missing models, and CLI exit status.

**Acceptance:** Existing contracts and default CLI behavior remain compatible; native-rule failures are deterministic and independently testable without Office hardware. Exact file changes and effort remain provisional until the consumer repository is inspected.

## Sequence and milestones

| Milestone | Scope | Evidence of completion |
|---|---|---|
| M1: Baseline complete | Work package 1 | Provenance-linked Run 009 predictions and metrics |
| M2: Repeatable regression | Work package 2 | Frozen synthetic suite plus baseline comparison support |
| M3: Data pipeline ready offline | Work package 3 | Ingest/assembly tests and split/coverage reports |
| M4: Experiment ready for data | Work package 4 | Validated configuration and launch/evaluation runbook |
| Optional consumer delivery | Work package 5 | ScreenAuditKit contract/CLI tests in its own repository |

Run P0-A as an independent recovery lane, alongside H1 compatibility work and software slices. Accept M1/M2 software independently using their defined test evidence; actual inference and frozen-suite qualification still require a usable P0 corpus. If original identity cannot be established, create a new corpus version and new Run 009 baseline; do not compare its score directly with the historical 0.586. M3 offline hardening continues; M4 preflight reports incomplete source data. Full training requires train/validation eligibility and live fixture gates. Tasks.md carries slice status; accepted preparation does not close TASK-6a-10 or claim unavailable corpora are populated.

For implementation changes, read the full mandatory research sequence in AGENTS.md before coding. Use focused Python checks, then required offline `swift build` and `swift test`, with all caches and temporary files directed inside the project. Document non-obvious new failure modes in BestPractices.md. Planning-only changes require link/content review rather than model execution or Swift builds.

## Transition back to hardware

Resume only after Office is available for an authorized capture and TVTestRig's HTTP/IPC adapters attest the same HarvestIdentity. The current coordinator requires container output paths outside this repository; resolve that filesystem-boundary conflict through a compliant producer/export workflow before invoking capture from this task. Historical container staging instructions are not an exception to AGENTS.md.

1. Obtain a small genuine attested batch in a compliant workflow; verify it against the ingest contract and inspect ground-truth overlays.
2. Capture the required corpus, validate its provenance/coverage, and freeze both holdouts before training.
3. Allocate/log the next run, run the pipeline smoke check, and launch the full experiment using the finalized blend.
4. Evaluate fixture held-out mAP@0.5 ≥0.94 and mAP@0.5:0.95 ≥0.78; require toggle/stepperControl AP50 ≥0.88. Badge is a later taxonomy/model milestone, not a 41-class metric.
5. Reassess DS-G8 (synthetic withheld-template mAP@0.5 ≥ 0.85) and report both holdouts independently. Neither the synthetic regression subset nor a fixture-only result can replace these gates.
6. Consider promotion and downstream phases only after the required gates are documented as passed.
