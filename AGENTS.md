# NativeUIAuditKit — Agent & Contributor Guidelines

This file governs how AI agents and human contributors work inside the **NativeUIAuditKit** package.
Follow every section. These are not suggestions.

When this package lives inside a monorepo the root `AGENTS.md` also applies and takes precedence
on any cross-cutting concern. When the package lives in its own standalone repository, **this file
is the sole authority**.

---

## What This Package Is

NativeUIAuditKit is a research-first Swift Package building a `VNCoreMLRequest`-backed native Apple
UI element detector — a custom equivalent of a hypothetical `VNRecognizeUIElementRequest`.

**Current state: Phase 6 — Model Training (iOS 5-class prototype)**

- Phases 0–5b: **Complete.** Scaffold, coordinate spike, taxonomy (41 classes), schema v1.0, dataset
  generator (SwiftUI + UIKit templates, 16,440 images), known-bad generator, Phase 5b extended templates.
- Phase 6: **In progress.** Training the first 5-class Create ML model (alert, navigationBar,
  primaryButton, textField, toggle). Three training runs attempted; Run 003 (strip-tiled) is the
  current active training run.
- Phases 6a–7: **Blocked** on Phase 6 gate (mAP@0.5 ≥ 0.70 on withheld test set).

**Before making any code changes, read in this order:**
1. `Research/NativeUIElementDetection.md` — architecture authority
2. `Research/BestPractices.md` — mistakes already made; do not repeat them
3. `Research/Phase6LessonsLearned.md` — Phase 6 specific: training API bugs, coordinate pitfalls, evaluation workflow
4. `Research/ExperimentLog.md` — all training runs, outcomes, what changed and why
5. `Tasks.md` — phase gate status and remaining work

---

## HIGHEST PRIORITY — File System Boundary (Absolute Rule)

**Never write any file outside the project directory.** This includes:

- `/tmp/` or any system temporary directory — **forbidden, no exceptions**
- `~/` (home directory) outside the project — forbidden
- `~/Desktop/`, `~/Downloads/`, `~/Documents/` (outside the project) — forbidden
- Any path not rooted inside the `NativeUIAuditKit/` package directory

This applies to **all output**: debug images, test artifacts, overlay renders, rendered PNGs, JSON
reports, logs, training logs, scripts, diagnostic output — everything. If a command or tool call
would write outside the project root, do not run it. Find an in-project path instead.

**In-project paths for common output:**

| Output type | Where it goes |
|---|---|
| Training logs | `NativeUITrainer/training.log` |
| Diagnostic scripts | `scripts/` |
| Reports and plots | `reports/` |
| Test artifacts and smoke test output | within the relevant target's subdirectory |
| Ephemeral debug output | `.build/debug-output/` |

Violation of this rule is a critical error. Check before executing any file-writing shell command.

---

## System Safety — Prohibited Commands

Never run the following without explicit written approval:
- Any `sudo` or `su` command
- `killall`, `kill` targeting any system daemon
- `xcrun simctl erase`, `delete`, or `shutdown all`
- `rm -rf` on any directory outside `.build/`
- Any command that modifies macOS system state or developer certificates
- `git push --force` on any branch
- Any command that uploads screenshots or training data to external services

---

## Git — Read-Only for Agents

**Never use git to write.** Do not run:
- `git commit`, `git push`, `git merge`, `git rebase`, `git reset`, `git stash`
- Any other git command that writes to the repository

Read-only git commands are fine: `git status`, `git diff`, `git log`, `git show`.

The user commits manually. Stage files if asked, but never commit.

---

## Build and Test Workflow

```bash
# From the package root (directory containing Package.swift)
swift build    # must succeed before any code change is considered done
swift test     # all tests must pass
```

Do not use any external build system. Do not require Xcode, simulator, or network access for tests.

**Tests must be fully offline.** The smoke tests verify API shape and Codable correctness only.
Detector tests (Phase 6+) will require `.mlpackage` from the separate `NativeUIAuditKitModels` package.

---

## Phase 6 — Model Training State

This section documents the current Phase 6 state precisely enough that a new agent can pick up
without re-reading the full conversation history.

### Current training infrastructure

| File | Purpose |
|---|---|
| `NativeUITrainer/Sources/main.swift` | CLI entry point (`--dataset`, `--output`) |
| `NativeUITrainer/Sources/CreateMLExporter.swift` | Converts custom JSON → Create ML format; generates horizontal strips when `stripFraction > 0` |
| `NativeUITrainer/Sources/TrainingConfig.swift` | `Codable` training configuration; `default` uses 25,000 iterations, 22% strip fraction |
| `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/ModelRegistry.swift` | `ModelDescriptor` and `ModelRegistry.iOS` descriptor |
| `NativeUIAuditKitModels/Package.swift` | Declares `.mlpackage.mlmodel` as a resource |
| `Sources/NativeUIAuditKit/Detection/NativeUIDetectionRequest.swift` | 3-pass inference: fullImage + SAHI tiles + horizontal strips |

### Training run command

```bash
# Always run from the NativeUIAuditKit package root
nohup swift run NativeUITrainer \
  --dataset <path-to-dataset-root> \
  --output  NativeUIAuditKitModels/Sources/NativeUIAuditKitModels \
  >> NativeUITrainer/training.log 2>&1 &
echo "PID: $!"
```

**Log is at `NativeUITrainer/training.log`.** Tail it to check progress:
```bash
tail -30 NativeUITrainer/training.log
```

Check if still running:
```bash
ps aux | grep NativeUITrainer | grep -v grep
```

### After training completes — mandatory evaluation sequence

1. `swift scripts/test_model_predictions.swift` — single-image spot check; confirm alert IoU > 0.9
2. `swift scripts/eval_map.swift` — full 1,364-image mAP evaluation
3. **Do NOT use `MLObjectDetector.evaluation(on:)`** — it returns mAP≈0 for portrait images due to a `.scaleFit` bug. Use `scripts/eval_map.swift` (uses `.scaleFill`). See BP-25 and `Research/Phase6LessonsLearned.md` §3.

### Critical inference rules (do not violate)

- **Always use `.scaleFill`** on `VNCoreMLRequest.imageCropAndScaleOption`. `.scaleFit` causes ~2× width blowup on portrait screenshots → IoU drops below 0.5 → everything is a false positive.
- **Annotation coordinates are normalized [0,1]**, not pixels. The Vision→CreateML conversion is: `cx = vn.x + vn.w/2`, `cy = 1.0 - vn.y - vn.h/2`. See `Research/Phase6LessonsLearned.md` §2.
- **The model file** written by `MLObjectDetector.write(to:)` is `NativeUIDetector_v1.mlpackage.mlmodel` (flat file, NOT a `.mlpackage` directory). The `Package.swift` resource declaration must use the `.mlmodel` suffix.

### DS-G gate status

| Gate | Condition | Status |
|---|---|---|
| DS-G5 | Per-class mAP ≥ 0.50 for all 5 iOS classes | ❌ Failing: navBar=0.00, textField=0.00 |
| DS-G6 | Withheld-template mAP ≥ 0.70 on iOS model | ❌ Not yet (overall mAP = 0.336 on Run 002) |
| DS-G7 | All 41 classes meet instance floors | ⏳ After 41-class training (Phase 6a) |

Run 003 (strip-tiled, currently in progress) is expected to fix the navBar/textField AP=0 failure.

---

## Best Practices — Read Before You Code

`Research/BestPractices.md` is a living record of mistakes made and lessons learned. It is not
optional reading. It prevents repeating known errors.

**Read `Research/BestPractices.md` before working on any of the following:**

| Topic | Relevant entries |
|---|---|
| SwiftUI element positioning or layout | BP-01 (`.offset()` vs padding), BP-02 (safe area) |
| `GeometryReader` / coordinate capture | BP-01, BP-02, BP-03 (clipping), BP-04 (timing) |
| Writing tests for rendering or coordinates | BP-05 (test the real mechanism), BP-06 (async), BP-07 (`@MainActor`) |
| Xcode project scaffolding | BP-08 (minimal pbxproj), BP-09 (nested class error) |
| Coordinate system conversions | BP-10 (all three reps), BP-11 (scale source), BP-10 (Vision y-flip) |
| Any new generator template | BP-01, BP-02, BP-03, BP-04, BP-10, BP-11, BP-15 |
| Adding a new SPM target or Xcode project | BP-15 (platform boundary rule) |
| Training or inference with Create ML / Vision | BP-25 (scaleFit bug), BP-26 (anchor assignment) |
| Writing evaluation scripts | BP-25 — use `.scaleFill`, never `evaluation(on:)` |

**When you discover a new mistake or a better approach, add it to `Research/BestPractices.md`
before closing the task.** Each entry must include: what went wrong, the correct approach, and
why it matters. Do not pad the document with obvious advice.

---

## Research-First Rule

**Before writing any implementation code, update `Research/` first.**

The research documents are the source of truth for architectural decisions. If you are about to:
- Add a new element type → update `Research/NativeUIElementDetection.md` Section 5 first
- Change the sidecar schema → update Section 6 first and bump the schema version
- Change a training approach → update Section 8 first, and add an entry to `Research/ExperimentLog.md`

If a research section is wrong or outdated, correct it in a separate commit before acting on it.

---

## Experiment Logging Rule

**Every training run must be recorded in `Research/ExperimentLog.md` before it starts and updated
when it completes.** Include:
- Run ID (sequential)
- Date, elapsed time, PID
- Exact configuration (iterations, strip fraction, dataset size)
- Outcome (per-class metrics or error)
- Diagnosis and action taken

This prevents re-running experiments that were already tried and failed.

---

## Phase Gate — Do Not Skip Phases

The phases in `Tasks.md` are ordered by dependency. Do not begin Phase N+1 work until Phase N
is complete and its gate condition is documented:

| Gate | Required before |
|---|---|
| Coordinate spike documented in `Research/CoordinateSpike.md` | Phase 3 (dataset generation) |
| Taxonomy frozen in `NativeUIElementType` enum | Phase 2 schema |
| Schema tagged `v1.0` in `annotation.schema.json` | Phase 3 (generation at scale) |
| 5,000+ annotated images, UIKit generator complete | Phase 6 (model training) |
| mAP@0.5 ≥ 0.70 on withheld-template test set | Phase 7 (OCR fusion) |

---

## Generic-First Rule

`Sources/NativeUIAuditKit/` must contain **zero** references to:
- RA11y, quest names, game mechanics, or any specific app
- Hardcoded file paths for any consuming project
- Specific device UDIDs or simulator configurations

This package will be extracted to a standalone repository. Any RA11y-specific adapter code
belongs in the RA11y repository, not here.

---

## Access Control

Default to the most restrictive access that still compiles:
- `private` — single file
- `internal` — within the module (default; prefer this for implementation details)
- `public` — only when a consumer of the library needs it

Do not make types `public` speculatively. Every `public` symbol needs a doc comment.

---

## Concurrency

Swift 6 strict concurrency. Every new type must be `Sendable`. No `@MainActor` on data types.
No `Task.detached` without documented justification. No global mutable state.

---

## Platform Boundary Rule — No Compiler Flags in View Code

SwiftUI templates and UIKit rendering code are **iOS-only**. The macOS SPM orchestrator target must never compile them. Violating this forces `#if canImport(UIKit)` / `#if os(iOS)` guards into every view file, which is a maintenance hazard.

**The correct split:**

| Layer | Target | Platform |
|---|---|---|
| `CaptureTypes.swift` (shared value types) | `NativeUIDatasetGenerator` SPM | macOS |
| `Sources/` (orchestration, annotation, manifest) | `NativeUIDatasetGenerator` SPM | macOS |
| `Templates/` (SwiftUI views, `ScreenshotCapture`) | `GeneratorRunner` Xcode project | iOS |

**Rules:**
- Templates must import `SwiftUI` (and `UIKit` where needed) with no `#if` guards.
- The SPM target declares `exclude: ["Templates"]` so it never sees iOS-only files.
- The iOS Xcode project references shared `Sources/` Swift files by relative path.
- If you are about to add `#if canImport(UIKit)` to a SwiftUI view body, stop — the file is in the wrong target.

See `Research/BestPractices.md` **BP-15** for the full rationale.

---

## Taxonomy Stability

`NativeUIElementType.rawValue` strings are **stable API** once the schema is tagged `v1.0`.
After that point:
- Adding a case is a minor version bump
- Renaming or removing a case is a major version bump
- Never change a raw value string — it will silently break JSON roundtrips in stored annotations

---

## Dataset and Training — Location Rules

- The dataset lives **outside** the repository: `NativeUIAuditKit-Dataset/` (path is documented in `Research/NativeUIElementDetection.md` Section 6.2). Do not create dataset directories inside the package.
- `NativeUITrainer/` is an in-package Swift executable target. Training produces the `.mlpackage.mlmodel` file that goes into `NativeUIAuditKitModels/`.
- The library (`Sources/NativeUIAuditKit/`) must not import CreateML or depend on dataset paths.
- Scripts in `scripts/` are standalone Swift files runnable via `swift <script>.swift`; they are diagnostic tools, not part of the library.

---

## Model Packaging — Separate Package

The CoreML model ships as a separate optional package (`NativeUIAuditKitModels`) so the core
library stays small and model-free. Do not commit `.mlpackage` or `.mlpackage.mlmodel` files to
this repository.

When the model is unavailable, `NativeUIDetectionRequest.perform(on:sidecar:)` throws
`NativeUIDetectionError.modelUnavailable`. This is the correct behavior — never silently
return empty results or fall back to a degraded mode without surfacing the reason.

---

## Before Committing

1. `swift build` — zero errors, zero warnings
2. `swift test` — all smoke tests pass
3. No RA11y-specific strings in `Sources/`
4. No hardcoded absolute paths
5. `Research/` updated if an architectural decision was made
6. `Tasks.md` updated with current phase status
7. `Research/ExperimentLog.md` updated if a training run was started or completed
8. No dataset artifacts committed to the package repo
9. No files written outside the project directory
