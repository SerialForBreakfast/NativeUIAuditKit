# NativeUIAuditKit — Agent & Contributor Guidelines

This file governs how AI agents and human contributors work inside the **NativeUIAuditKit** package.
Follow every section. These are not suggestions.

When this package lives inside a monorepo the root `AGENTS.md` also applies and takes precedence
on any cross-cutting concern. When the package lives in its own standalone repository, **this file
is the sole authority**.

---

## What This Package Is

NativeUIAuditKit is a research-first Swift Package building toward a `VNCoreMLRequest`-backed
native Apple UI element detector — a custom equivalent of a hypothetical `VNRecognizeUIElementRequest`.

**Current state: Phase 1 complete.** The coordinate export strategy is proven. No CoreML model or
inference logic exists yet. The primary value right now is the research documentation in `Research/`
and the task roadmap in `Tasks.md`.

Read `Research/NativeUIElementDetection.md` before making any code changes.
Read `Tasks.md` to understand what phase the package is in.
Read `Research/BestPractices.md` before writing any SwiftUI layout, UIKit rendering, coordinate
conversion, or test infrastructure code.

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

## File System Boundary

Work only inside the `NativeUIAuditKit/` package directory. Do not read or write files outside
the package root unless explicitly directed by the user.

The dataset directory (`NativeUIAuditKit-Dataset/`) is gitignored and lives **outside** the package
in a separate location (documented in `Research/NativeUIElementDetection.md`, Section 6.2). Do not
create dataset directories inside the package.

---

## Build and Test Workflow

```bash
# From the package root (directory containing Package.swift)
swift build    # must succeed before any code change is considered done
swift test     # 6 smoke tests must pass
```

Do not use any external build system. Do not require Xcode, simulator, or network access for tests.

**Tests must be fully offline.** The smoke tests verify API shape and Codable correctness only.
Detector tests (Phase 6+) will require `.mlpackage` from the separate `NativeUIAuditKitModels` package.

---

## Best Practices — Read Before You Code

`Research/BestPractices.md` is a living record of mistakes made and lessons learned during
development. It is not optional reading — it exists to prevent repeating known errors.

**Read `Research/BestPractices.md` before working on any of the following:**

| Topic | Relevant entries |
|-------|-----------------|
| SwiftUI element positioning or layout | BP-01 (`.offset()` vs padding), BP-02 (safe area) |
| `GeometryReader` / coordinate capture | BP-01, BP-02, BP-03 (clipping), BP-04 (timing) |
| Writing tests for rendering or coordinates | BP-05 (test the real mechanism), BP-06 (async), BP-07 (`@MainActor`) |
| Xcode project scaffolding | BP-08 (minimal pbxproj), BP-09 (nested class error) |
| Coordinate system conversions | BP-10 (all three reps), BP-11 (scale source), BP-10 (Vision y-flip) |
| Any new generator template | BP-01, BP-02, BP-03, BP-04, BP-10, BP-11 |

**When you discover a new mistake or a better approach, add it to `Research/BestPractices.md`
before closing the task.** Each entry must include: what went wrong, the correct approach, and
why it matters. Do not pad the document with obvious advice — only record findings that were
actually discovered the hard way or that would be non-obvious to a knowledgeable Swift developer.

---

## Research-First Rule

**Before writing any implementation code, update `Research/` first.**

The research documents are the source of truth for architectural decisions. If you are about to:
- Add a new element type → update `Research/NativeUIElementDetection.md` Section 5 first
- Change the sidecar schema → update Section 6 first and bump the schema version
- Change a training approach → update Section 8 first

If a research section is wrong or outdated, correct it in a separate commit before acting on it.

---

## Phase Gate — Do Not Skip Phases

The phases in `Tasks.md` are ordered by dependency. Do not begin Phase N+1 work until Phase N
is complete and its gate condition is documented:

| Gate | Required before |
|------|----------------|
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

## Taxonomy Stability

`NativeUIElementType.rawValue` strings are **stable API** once the schema is tagged `v1.0`.
After that point:
- Adding a case is a minor version bump
- Renaming or removing a case is a major version bump
- Never change a raw value string — it will silently break JSON roundtrips in stored annotations

---

## Dataset and Training — Out of Scope for This Package

The `NativeUIAuditKit` library and test targets must not:
- Generate training data at test time
- Depend on dataset paths on the machine
- Import CreateML or require Python/PyTorch in the test runner

Training scripts, dataset generators, and model evaluation live in separate targets
(`NativeUIDatasetGenerator` app target, future) or outside the repository.
The library only imports the trained `.mlpackage` via `NativeUIAuditKitModels` (separate package).

---

## Model Packaging — Separate Package

The CoreML model ships as a separate optional package (`NativeUIAuditKitModels`) so the core
library stays small and model-free. Do not commit `.mlpackage` files to this repository.

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
7. No dataset artifacts committed to the package repo
