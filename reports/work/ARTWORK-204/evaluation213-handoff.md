# WORKER213 independent evaluation readiness — October 6

Implemented `scripts/evaluate_artwork213.py` with separate prepare/score CLI modes.
Reuses the existing prediction contract and AP implementation; does not infer, train,
select checkpoints or promote. Frozen supplement and ROI manifests are hash-pinned.
All source bytes validate before preparation; role/family/order membership is exact.

Actual preparation: `artifacts/evaluation213-input01`,36 native reserved frames;
24 content-validation and12 abstract diagnostic. Actual checked ROI partitions:
135 fit,37 page,413 combined. No final holdout or DS-G8 claim.
Native content hash: `c9d4f7e8bc0d78907585cfa8f2beeba4568c6c82214939068b498da33430b4f5`.
No raw pixels retransmitted or new roles assigned.

Validation:20 Python tests (including reused evaluator regressions), offline Swift
build exit0,140 Swift Testing and14 XCTest tests passed. Logs:
`.build/evaluation213-build.log`, `.build/evaluation213-test.log`.
Tests exercise real scoring with synthetic predictions, unavailable-class metrics,
wrong checkpoint/settings, missing results, role/family mismatch and output collisions.
These are not model quality results. All pre-existing unrelated edits preserved.

Result intake: verify the named archive and returned config/count evidence first.
Map each arm's unchanged prediction files to native/fit/page/combined.json, then run:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python scripts/evaluate_artwork213.py score \
  reports/work/ARTWORK-204/artifacts/evaluation213-input01 \
  <verified-arm-prediction-directory> <verified-fixed-last-checkpoint> <new-project-report.json>
```

Acceptance reports checkpoint/prediction hashes, input membership and five independent
metric reports. Model gate stays false. It does not replace trainer source/configuration,
572-slot/89-update review or a matched-arm decision. Worker receipt/start remains pending.
Next substantial outcome: intake both bounded runs, compare imageView improvement and
all-class regressions, return case-linked findings and choose one justified follow-on;
eligible TTR native-focus data retains priority when available.

Coordination follow-up published/read back at
`nuiak/responses/nuiak-20261006-worker213-evaluation-ready01.json`:
2710bytes, SHA256 `a9dfa5adb1d3983e870efb88f3c58d1df3a498d4c72dffa948ecbf87069c55b6`.
This provides exact native corpus identity and return layout without another pixel
transfer. Peer acknowledgment remains unobserved. Initial publication invocation
mistakenly treated assertion-only `mounted()` as returning a path; it stopped before
writes. Source inspection and fresh mount verification resolved the review denial;
the approved publication used the helper's verified SHARE constant. No bypass.

## Paired acceptance continuation

Added `pair` mode to the same CLI, reusing the actual scorer and one shared frozen
request set. It validates both checkpoint/prediction identities before reporting all
41class TP/FP/FN/AP deltas per partition. Unsupported AP remains null and operating
regressions remain visible; higher mean AP does not set a promotion gate. Same
checkpoint comparisons reject. It requires no new worker inference or data transfer.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python scripts/evaluate_artwork213.py pair \
  reports/work/ARTWORK-204/artifacts/evaluation213-input01 \
  <control-predictions> <control-fixed-last> <treatment-predictions> <treatment-fixed-last> \
  <new-project-paired-report.json>
```

21focused/shared tests pass, including actual paired scoring, zero deltas, mismatched
membership/support, same-checkpoint rejection and retained FP regressions/null AP.
No candidate return yet; software readiness is not model acceptance. Read-only local
runtime inventory found no matching TTR/Fixture process. No launch, replacement,
capture or service operation attempted; existing producer-source request remains
the relevant tvOS prerequisite rather than another duplicate request.
Integrated offline Swift build/test exit0:140Swift Testing+14XCTest, logs
`.build/paired213-build.log` and `.build/paired213-test.log`; diff check passes.
