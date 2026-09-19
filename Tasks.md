# NativeUIAuditKit — Tasks

Open work only. Finished phases: [`CompletedTasks.md`](CompletedTasks.md).  
Current snapshot: [`Research/CurrentState.md`](Research/CurrentState.md).  
Streams: [`Research/PhaseMap.md`](Research/PhaseMap.md).

## Status

- `[ ]` Not started
- `[~]` In progress
- `[x]` Done (move the whole task to `CompletedTasks.md` when every AC is `[x]`)
- `[!]` Blocked — see note

Do not put architecture notes, run logs, or IPC war stories in this file. Those go in `Research/` ([index](Research/README.md)).

---

## TASK-6a-10: Full-frame fixture retraining (41-class iOS) [!]

**Blocked on live TVTestRig batch output.** Ingest code is ready. Do not train on empty sidecars or `*_result.json` (model self-predictions). Format and IPC notes: [`Research/FixtureBatchIngest.md`](Research/FixtureBatchIngest.md).

**Requires:** Run 009 diagnosis (holdout mAP@0.5 = 0.586, DS-G8 ≥ 0.850). BP-32.

- [x] `scripts/ingest_fixture_batch.py` + `scripts/test_ingest_fixture_batch.py` (16/16)
- [x] Coordinator IPC unblocked (2026-09-18): using the running TVTestRig.app's own `aatv` binary (not a stale local build) with `HOME` pointed at `NativeUITrainer/.tmp/aatv_home` (symlinked to the real container socket, per `Research/FixtureBatchIngest.md`), `aatv status`/`device list`/`device connect --device-id 8D80F616-...`/`fixture env` all succeeded against real "office" hardware (tvOS 26.6, `AppleTV5,3`). Sandboxed coordinator can only read/write inside its own container — recipes and output dir must live under `~/Library/Containers/com.showblender.TVTestRig/Data/...`, not the checkout.
- [!] **New blocker, not the old one:** `aatv fixture batch` itself fails at a later stage — `identity_preflight` / `identityUnavailable`. Per TVTestRig commit `586050e` ("CHR-04–10: version harvest bundles, bind identity, fail closed without attestation"), landed 2026-09-18: production wiring now *requires* the HTTP and IPC adapters to jointly attest a shared `HarvestIdentity` before any capture; neither adapter does that yet, so it fails closed — **"There is no CLI bypass"** (TVTestRig's own words). This is deliberate, not a bug to route around. Real progress (coordinator + sandbox path requirements) written up; this specific gate is now the sole blocker. See `reports/tvtestrig_feedback_2026-09-18.md`.
- [ ] Authorized Office `aatv fixture batch` — blocked until TVTestRig wires up `HarvestIdentity` attestation for its HTTP/IPC adapters; re-verify ingest against that output once it exists
- [ ] Blend fixture corpus with Phase 6a synthetic set; retrain from Run 009 `best.pt`, 150 epochs, cosine annealing + warmup
- [ ] Evaluate on TVTestRig `held-out` split **and** synthetic withheld-template holdout
- [ ] Per-class AP on small controls (toggle, stepper, badge) ≥ 0.88

**AC:** mAP@0.5 ≥ 0.94 and mAP@0.5:0.95 ≥ 0.78 on the fixture holdout; DS-G8 reassessed on both holdouts before shipping 41-class weights.

---

## TASK-6a-11: Multi-corpus PyTorch reference eval [~]

**Requires:** a 6a-10 candidate, or continue using Run 009 weights as the baseline.

- [x] `scripts/eval_reference_metrics.py` + `reports/pytorch_reference_metrics.json` (SHA-256 `226755b88642d1a68a0f9c3cad4b685d6d874352d48090b910c6b406ea61e405`)
- [x] Honest `available: false` for the three corpora that do not exist yet
- [ ] Per-image predicted boxes / scores / class IDs from `eval_phase6a.py` (needs a full inference pass)
- [ ] Populate `real_device_fixture_holdouts`, `production_tvos_system_holdout`, `frozen_regression_suite` when those image+box sets exist

---

## TASK-6a-12: Partial-crop robustness fork [ ]

**Requires:** TASK-6a-10 complete. Full-frame config stays the shipped default.

- [ ] Mosaic + random-crop aug (0.6×–1.0× bounding areas) as a **fork**, not the default
- [ ] Frozen partial-crop holdout, never merged into the full-frame holdout
- [ ] Full-frame mAP must not regress > 1.0 pt vs 6a-10; crop-holdout mAP improves ≥ 15%
- [ ] Measure and document in `Research/TrainingDataStrategy.md` that resizing a crop to 1920×1080 does not reconstruct missing full-frame context

---

## TASK-6b-R-1: Scale real Apple TV hold-out captures [~]

Pipeline and qualification (R-2, R-3) are done. Remaining:

- [ ] ≥500 held-out real Apple TV screenshots across the app matrix (`dataset/tvos_captures/`, gitignored)

---

## FOCUS-DET-05: FocusRing v1.0 data + retrain [ ]

v0.1 is shipped. Spec: [`Research/FocusRingDetectorSpec.md`](Research/FocusRingDetectorSpec.md).

- [ ] ≥6,000 labeled pairs (or Fixture RPC when it exists)
- [ ] Mix: `gridMatrix` ≥ 2,000, `mediaShelf` ≥ 1,500, `settingsList` ≥ 1,000, `actionDialog` / `heroCarousel` / `focusMaze` ≥ 500 each
- [ ] ≥ 20% `light` and ≥ 20% `highContrast` in `gridMatrix` + `mediaShelf`
- [ ] Hard-negative n ≥ 100 (`light`+`highContrast` × `imageView`+`collectionItem`)
- [ ] All six quality gates, including **non-vacuous** hard-neg FPR ≤ 0.5%
- [ ] Replace bundled `.mlmodelc` only after those gates pass

Office live harvest only. No Home / Select / Settings crawl (BP-40). IPC: [`Research/FixtureBatchIngest.md`](Research/FixtureBatchIngest.md).

---

## Phase 6b-U: Unified iOS + tvOS model [ ]

Keep separate shipped models unless every gate passes.

- [ ] Train a platform-balanced unified candidate
- [ ] No platform loses > 2 pt mAP@0.5 vs its dedicated model on identical holdouts
- [ ] tvOS `tabBar` AP ≥ 0.80 and no toolbar confusion
- [ ] tvOS focus P/R within 2 pt of dedicated model or FocusRing
- [ ] iOS FP does not rise on bottom chrome, status bar, home indicator, Dynamic Island
- [ ] Latency and size stay in budget

---

## Phase 6c: macOS model [ ]

**Requires:** Phase 6a gate (41-class iOS weights that clear DS-G8).

### TASK-6c-1: macOS coordinate spike

- [ ] AppKit Y-flip: `y_flipped = window.contentView.bounds.height - frame.origin.y - frame.height`
- [ ] ±2 pt vs `NSBitmapImageRep` PNG
- [ ] `testMacOSCoordinateFlip` on macOS 15

### TASK-6c-2: Templates + training

- [ ] ≥2,000 macOS images with Y-flipped coordinates
- [ ] mAP@0.5 ≥ 0.80 on withheld-template test
- [ ] `tooltip` AP ≥ 0.70
- [ ] Export `NativeUIDetector_macOS_v1`

---

## Phase 9: ScreenAuditKit integration (remaining)

9-1 (`NativeUIRecognizing`) is done. These live in the ScreenAuditKit repo.

### TASK-9-2: Contract extension [ ]

- [ ] `uiElements` required/forbidden/`minConfidence` on `ScreenAuditScreenContract`
- [ ] Rule IDs: `missingUIElement`, `unexpectedUIElement`, `uiElementBoundsViolation`, `uiElementTruncated`, `uiElementClipped`, `uiElementTargetTooSmall`, `inferredOSMismatch`
- [ ] `NativeUINoOpRecognizer` skips `uiElements` silently

### TASK-9-3: CLI flag [ ]

- [ ] `screenaudit validate --native-ui none|coreml` (default `none`)
- [ ] Missing models package → clear error, exit 1

---

## Track 3: Release leftovers [~]

### TASK-DIST-01: History rewrite (maintainer call) [!]

Working-tree PII is redacted. Real values remain in already-pushed git history. Do not rewrite history without an explicit go-ahead.

- [x] `PROVENANCE.md` written and linked
- [x] Training data audited clean
- [x] Working-tree PII redacted (2026-09-18)
- [!] History rewrite / force-push — deferred on purpose

### TASK-DIST-02: Next release tag [!]

API review is done (`NativeUIDetectionRequest` stays the public name; `FocusRingClassifier` stays internal).

- [x] API decisions in `Research/NativeUIElementDetection.md` §4
- [x] `scripts/verify_models_package_standalone.sh`
- [ ] Tag (e.g. `2.1.0`) after TASK-6a-10 ships DS-G8-passing 41-class weights; CHANGELOG cites that model and the `pytorch_reference_metrics.json` hash
