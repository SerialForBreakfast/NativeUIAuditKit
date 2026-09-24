---
name: tvos-fixture-training
description: Capture and validate fixture-ground-truth tvOS training data for NativeUIAuditKit, including paired FocusRing crops and synthetic layouts. Requires separately authorized target and capture scope.
---

# NUIAK fixture training supplement

Read [TVTestRig operation](../tvtestrig/SKILL.md) and
[interface contracts](../tvtestrig/references/interfaces.md) first. Use this supplement
for NUIAK data constraints, not as an alternative device protocol. Current user
restrictions—including a simulator pause—override availability of a command.

## Before capture

- Verify the actual running local app and its matching helper before assuming a remote
  host is required. CLI mode may use the same app executable; inspect the installed
  entrypoint. Never mix binaries or retarget/restart an occupied GUI automatically.
- Bind the exact authorized device and Fixture endpoint from fresh evidence. Discovery,
  pairing, connected control, active capture and settled focus are different claims.
- Inspect controller/capture ownership; acquire only required resources and release only
  resources this task owns. Shared status is coordination, not a lock or remote executor.
- Use the existing fixture batch path for a bounded recipe smoke. Historical multi-tab
  scripts are not substitutes. Pin recipe/source/build identities and expected targets.
- Keep outputs in approved NUIAK paths unless the user explicitly authorizes another
  runtime/output location. Status/messages are metadata-only; separately assigned
  artifact copies follow the [SMB receipt protocol](../../../reports/coordination/Instructions.md#explicit-receipt-based-artifact-exception--2026-09-23).
- Physical rendering can supply real Apple TV focus effects. Simulator pixels do not
  qualify device shaders/parallax, performance or physical navigation.

## Paired focus capture and labels

For producer changes, use [the exact-build repair loop](../../../Research/WorkerExecution/references/operational-lessons.md#ttr-featurerepair-qualification).
Reuse completed jobs and original bytes when only export/intake failed; no recapture
or producer rebuild for a consumer hash/schema mismatch. Pin producer serialization
vectors and preserve legacy/null semantics before actual ingest/crop tests. A partial
schema override must not weaken required sidecar fields; dispatch declared versions.

1. Capture a resting baseline, then one focused state per supported interactive element.
2. Verify producer-reported settled focus and matching scene/frame evidence. A 150ms
   delay or visually stable image alone does not prove correct focus.
3. Preserve each frame's actual boxes, including focused scaling and clipping. Extract
   FocusRing crops with 16% expansion and 256×256 geometry; retain raw-byte lineage.
4. Accept labels only from fixture ground truth. Prediction files such as
   `_result.json` are diagnostics, not annotations or authoritative class counts.
5. Validate sidecars against their declared supported schema version, not an assumed
   universal v1.0. Unknown labels remain excluded, not guessed from missing rings.
6. Visual focus and semantic VoiceOver/navigation alignment are separate. Do not require
   or fabricate alignment metadata for visual-only examples; validate it when present.

## Validation and cleanup

Validate complete receipt/index, paths, all hashes, decodable images, annotations,
split membership and expected/captured/rejected counts. Reject partial publication,
unknown versions, conflicting telemetry and altered bytes without repairing evidence.
Integrity alone does not authenticate source or approve training.

Keep paired/related recipe seeds and duplicate content in one partition; multiple
distinct element pairs from one seed within a split are valid. Freeze final evaluation
groups independently of development failures. Coverage uses ground-truth counts and
actual scene totals; hard negatives require verified unfocused evidence.

Preserve partial/invalid trials; no blind retry or manual promotion of staging output.
Verify Fixture health after owned teardown, not just foreground return or process
presence. Report capture, cleanup, data eligibility, integration and model quality
separately. Do not train, promote, change settings, or expand the capture from this skill.
