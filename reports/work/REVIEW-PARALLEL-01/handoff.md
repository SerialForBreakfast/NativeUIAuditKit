# Review-parallel tranche — completed for review

## Independent outcomes

- Software: role-aware freeze/run/render, QA CLI and recorder audit implemented;
  59 focused/legacy Python tests pass. Inference paths use mocks in tests.
- Data: actual batch02 production crop replay89/89,89 distinct crops, no hard audit
  issues. Original diagnostic-only eligibility unchanged; no labels auto-approved.
- Integration: QA CLI exercised on retained real evidence; recorder metadata audit
  completed. No live TTR, transport or autonomous navigation qualification.
- Model gate: not assessed. No inference/training/export/promotion.

Open batch03 untouched. Prior dirty editor changes preserved. No taxonomy, public
Swift API, native journey schema or model changes.

## 1. Role-aware evaluator

`human_focus_roles.py` validates hash-bound revision/crops/completeness and an
exhaustive candidate/auxiliary/unresolved partition. All frames require explicit
settlement and coverage decisions. Unique-selection metrics require a human
completeness receipt, no unresolved members, settled status and exactly one true
focused candidate. Otherwise report unavailable with exclusions, not a reduced
denominator hidden in a whole-batch score. Auxiliary negatives stay separate.
Ties above0.85 mean multiple focus. Missing/duplicate/invalid scores fail the
existing prediction-accounting path. Pair diagnostics require explicitly admitted
existing pair IDs, default none; visual proposals do not become pairs automatically.

Existing `human_focus_evaluation.py freeze/run/render` now accepts approval/protocol
v2 with an `admission` reference; v1 remains supported. Model/runtime/output binding,
source-role audit and maxRuns=1 checks remain. Retained rendering loads no model.
Unmapped focus roles retain their names rather than fabricated detector class IDs.
Human boxes do not measure detector recall or end-to-end navigation quality.

`batch01-admission-draft.json` and `batch02-admission-draft.json` are schema-ready,
sealed **approved:false** proposals, with exact154 candidate/16 auxiliary/1 unresolved
membership across both. No model-execution approval file was created. Original
tab settlement and frame605 candidate completeness/clock-avatar remain decisions.

## 2. One-command immutable review QA

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python \
  scripts/human_review_qa.py PATH/TO/revision.json NEW/QA/OUTPUT \
  --completeness PATH/TO/completeness.json
```

Paths must stay project-local; output must be fresh. Optional `--crops EXISTING`
reuses a verified production crop report. Otherwise use existing16%/256×256 Swift
crop-only path and item/pixel batching limits. No model argument is supplied.
`handoff.json` and `summary.md` include counts, bound inputs, exclusions and failed
stage; `audit/review.html` links numbered evidence. Missing completeness means
unknown, not inferred; wrong receipts fail. Pending frames block qualification.
No annotations are rewritten and no admission follows automatically.

Actual batch02 revision232705Z-8a71fdbe ran through this CLI into `qa-batch02/`:
8 frames/89 crops/89 unique crop pixels, no hard issues. The single near-frame
warning remains Arcade/Search, not an automatic deletion. Source/snapshot bindings
reverified after processing. Batch03 waits for its immutable Finish revision only.

## 3. Retained action audit

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python \
  scripts/human_recording_audit.py RETAINED/batch.json NEW/action-audit.json
```

Evidence: `../FOCUS-REGRESSION-V2/office-trial-02/action-audit-v2.json`;
the earlier exploratory audit is retained. Source schema2 manifest/events are
hash-bound to the retained batch. No new pixels, capture or OCR inference.

-166 actions/dispatches:165 completed,1 failed Down dispatch.
-1082 observations/1009 distinct encoded frame hashes,989 explicit associations.
  All association IDs/hashes resolve; no target mismatch detected.
-159 actions have a post frame after command completion and before next dispatch.
-15 have a declared settled post within that interval;14 pass all conservative
  association checks. The fifteenth also has an early post association.
-151 lack declared settled post;17 include pre-command-completion post frames;
  6 include frames after next dispatch;7 lack an eligible bounded post frame.
  Categories overlap, not a partition.
-Producer gaps:150 inputOverlap,36 advisorySkipped,7 settlementUnavailable.
-Median eligible first-post latency261.27ms; pre-frame age297.74ms; declared-settled
  latency1905.37ms over15 actions. These are metadata timings, not native UI settle
  truth or end-to-end navigation latency.
-Zero repeated pre/post bytes in eligible associations does not establish zero
  no-ops: focus can stay fixed while other pixels animate. No transition labels
  or training eligibility are inferred from button intent/completed dispatch.

Use this recording for timing/correlation diagnostics and reviewed stills, not
supervised transition training yet. Producer next action: clarify timestamps and
post-frame association semantics; consider optional visible settled/pending/overlap
feedback during demonstrations. Preserve raw transitions, distinguish interrupted
actions, never silently throttle ordinary human control or return to chat per press.
Export repair remains separate; no recapture requested.

## Verification and completion

Generated tests exercise partition mutations, changed hashes, missing completeness,
actual role-v2 annotations→crops→admission→freeze→mocked run, legacy evaluator,
candidate/auxiliary separation, unique/wrong/none/multiple, incomplete/disputed/empty
support, retained rendering without runtime, pending/final-challenge/corrupt QA,
CLI reuse, recorder bad links/targets/generations/duplicates/overlap/failure and
determinism.59 tests pass in `.build/human-review/parallel-tests-final.log`.
Offline Swift build and123 tests (14XCTest+109SwiftTesting) pass; logs:
`parallel-build.log`, `parallel-swift-test.log` in the same directory.

No extra reannotation or editor restart required. Remaining dependencies are real
admission decisions, separately assigned inference, and human batch03 completion;
none blocks the delivered software. See coordination.md for producer publication.
