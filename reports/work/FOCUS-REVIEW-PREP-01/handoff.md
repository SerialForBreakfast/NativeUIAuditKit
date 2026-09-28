# FOCUS-REVIEW-PREP-01 — complete for review

2026-09-28. Owner: current NUIAK review-tool worker. Repository worker workflow used:
research contract first, actual CLI/editor integration, generated negative cases,
retained-input verification, offline package checks, then status reconciliation.
Existing dirty work preserved; no git writes or vendor edits.

## Outcomes

| Area | Outcome |
|---|---|
| Software | Implemented and verified: queue/coverage CLI, optional completeness receipt, scoped Finish review, rectangle double-click editing |
| Data | Existing8 originals and8 saved annotation files verified unchanged; no new labels or real completeness assertion. Diagnostic smoke set only |
| Integration | Local CLI and actual pinned Qt editor paths verified. Recorder/producer integration remains separate; no speculative transport adapter |
| Model gate | Unassessed; no new inference, training, export, promotion or threshold change |

## Acceptance evidence

- **Efficient workflow:** [checklist](operator-checklist.md) defines Apple apps,
  Settings and safe OS UI, first6–8 frames, then8-frame batches, exclusions and stop
  conditions. No chat per input, no per-control timing/metadata form, no reannotation
  of the completed smoke set. Preparer supplies coverage metadata once per screen.
- **Queue integration:** `human_regression_review.py prepare` freezes family/layout
  rotation, max3 states/layout by default,8-frame slices and all dispositions.
  Actual editor `--queue --batch-index` uses the same IDs as Finish review;
  directory/search/drop changes cannot silently expand membership.
- **Duplicates:** same decoded pixels plus screen/context and compatible proposals
  yield a canonical reference. Conflicting proposals block the group. Near matches
  are not collapsed. Raw evidence/timeline retained; v1 duplicate pointers and
  admission behavior unchanged. Unit fixtures exercise both exact and conflict paths.
- **Completeness:** one optional unchecked Finish checkbox for all Ready frames.
  Receipt binds exact revision, reviewer, annotation snapshots and pixels. Software
  reviewers cannot assert it; changed membership/labels/images fail validation.
  Original `completeFrameCandidates` stays false. Future frame-level metrics need
  a separately assigned consumer of this receipt; it is not a qualification pass.
- **Editing:** actual Qt double-click tests cover zoom/offset coordinate conversion,
  topmost overlapping shape, cancel, edit/save/reload, blank area and drawing mode.
  Uses stock label dialog; no polygon mode or vendor-package modifications.
- **Actual Finish integration:** generated-fixture Qt button test writes a scoped
  completeness receipt while hidden annotation bytes remain unchanged. A second
  dialog test verifies only selected rows display and completeness starts unchecked.
- **Coverage:** [final report](coverage-report.json) reports selected/reviewed/
  pending/complete/blocked counts and family/class/state/focus-treatment support.
  Missing treatments stay unknown. Layout counts are not independence evidence.

## Retained CLI exercise

`smoke-coverage-metadata.json` describes the known Home, Photos Welcome and Settings
screens. `smoke-queue.json` selected7 frames, deferred the fourth Home state by
layout cap, and accounted for all8. There are no exact full-frame duplicates here.
This is a dry-run selection demonstration, not replacement of the existing8-frame
benchmark or a request to review it again. Complete-frame assertions remain absent.

`verification.json` binds the original batch and Joe's immutable revision and verifies
all8 current annotation files still equal their saved snapshots. Selected support:
3 Home,3 Photos Welcome,1 Settings; shelves/cards, navigation/toolbars and overlays
remain unrepresented. `smoke-coverage.json` is the initial CLI receipt before adding
the explicit unknown focus-treatment column; `coverage-report.json` is final.

## Verification

- `python-tests.log`:168 tests pass, including14 new queue/completeness fixtures
  and154 existing review/intake/evaluator tests. No model run.
- `editor-tests.log`:4 actual offscreen Qt interaction tests pass. Pinned Labelme
  emits existing file-handle ResourceWarnings; no test failures. Finish dialog PNG
  in `.build/human-review/gui-tests/finish-review.png` visually inspected, no clipping.
- `swift-build.log`: offline build passes, no compiler warnings/errors.
- `swift-test.log`:14 XCTest +109 Swift Testing tests pass.
- `git diff --check`: passes. All writes project-local. Test fixtures are generated
  and deleted by their existing local test cleanup; no user evidence deleted.

The editor process was not restarted or interrupted: save/close confirmation was
requested but not received during implementation. Changes apply on its next launch.
No further annotation is needed to complete this software tranche.

## Next assignment

First qualify the repaired action-linked recorder under the existing operator
scope, then prepare the first varied Apple/system mini-batch using this queue.
Have the human review it once and measure friction before expanding collection.
No circular dependency on a new model or training run. Full-frame scoring admission,
new human review, new recording and model execution are separate assignments.

Shared coordination: **not applicable**. Offline review changes do not change TTR's
existing recorder-repair request. No SMB publication or peer acknowledgment claimed.
