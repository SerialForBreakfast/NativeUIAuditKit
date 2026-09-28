# FDR-009 — bounded Simulator development run completed

2026-09-27 local /2026-09-28 UTC. One approved run completed; no repeat, export,
promotion, new capture or protected final-challenge scoring.

| Outcome | Result | Evidence / boundary |
|---|---|---|
| Software verified | pass |106 Python tests; offline Swift build with no warnings and123 tests pass; actual assembly, trainer preflight and execution integrated. |
| Data eligible | pass for approved development use |273 training pairs/546 crops;9 native retention pairs/18 crops. Immutable original221+9 plus52 admitted Fixture pairs preserved. No independent Photos/appearance qualification. |
| Integration qualified | pass for local trainer path |Pinned resident Python/PyTorch/MPS runtime; exact checkpoint/data/code checks; real30-epoch execution and selected-artifact verification. No remote TTR or physical-device qualification. |
| Model gate passed | not assessed for full qualification |Retention floor passes18/18; all ten original independent-coverage blockers remain. No generalization, export-parity or release claim. |

## Result

Process PID13076 ran2026-09-28T06:26:37.297968Z–06:32:27.846988Z and exited0.
Whole process350.552s, including launch-time data/crop revalidation; post-preflight
training/result phase79.808s. Both remain below the1,800-second cap. All30 epochs
met the frozen retention floor. **Epoch3** minimizes retention BCE among eligible
epochs; earliest-tie selection was preserved. `last.pt` is epoch30, not selected.

| Same-run MPS retention metric | FDR-007 initialization | Selected FDR-009 |
|---|---:|---:|
| Support |9 focused +9 unfocused crops |same18 crops |
| TP / FN / FP / TN at0.85 |9 /0 /0 /9 |9 /0 /0 /9 |
| Accuracy |18/18 |18/18 |
| Retention BCE |0.000007347030 |0.000004791201 |

Training loss was0.113968 in epoch1 and0.000611891 in epoch30. These are sampled
training losses, not an independent accuracy test. The tiny retention-loss reduction
does not demonstrate a usable transfer improvement; this set was also used to select
the checkpoint and has prior development exposure. Do not describe it as a new test.

Selected raw checkpoint:
`NativeUITrainer/focus_ring_runs/fdr009-simulator-retention/weights/best.pt`, SHA256
`e6e37ddc32c173ddf13e1e52756995a53cbbe1e1af18aa0e6da58b5767e47584`.
Last checkpoint SHA256
`3c86595ba3e4cf78cc8959f40e2d53c085d138054bff1df781776e19d5da7ab8`.
Both remain local/unpromoted. No shipped model changed.

## Frozen contract and implementation

Maintainer approval: [authorization](authorization.md), then exact `approval.json`.
Protocol `9c525a6f1f6698417a2a4af299e13b97459b53cbf3002511cd12f93821f3423f`
is `focus-retention-experiment-v1`, separate from the unchanged full appearance
extension `53d358966d36e0c36387eae84e9cdf488fb46676885ad908986fe5b8d445a4de`.
The latter's coverage blockers were neither deleted nor passed. The new protocol
checks its source by actual reconstruction, preserves membership/sampling, pins
runtime/code, and requires its own protocol/output-bound approval.

FDR-007 strict warm weights, fresh AdamW,30epochs,batch64,lr0.0003,seed42,no augmentation;
50/50 expected native–Fixture sampling mass, not a guarantee of equal counts in every
sampled batch.40 native +233 Fixture training pairs; nine native retention pairs.
Production16% expansion/256×256 stretch/RGB÷255 unchanged. Only18/18-retention epochs
may be selected; minimum retention BCE, earliest tie; no eligible epoch means no best.
No random split of the related Fixture recipes or evaluation members added to train.

Runtime: Python3.12.9,torch2.7.0,numpy1.26.4,Pillow11.3.0,macOS26.4.1/arm64; actual
device `mps`, approved resident focus-export-01 environment. FDR-007 was originally
trained with a different Torch version; this is not a controlled data-only ablation.
The before/after retention results above are both from this same pinned execution.

Changed reusable implementation:

- `scripts/focus_retention_experiment.py`: explicit development-only assembly/preflight and retention selector.
- Existing `focus_mixed_assembly.py`, `focus_learning_experiment.py`, `focus_training_preflight.py`: new-version dispatch and ordinary-dataset rejection.
- Existing `train_focus_ring_detector.py`: new policy dispatch/configuration guard and earliest-tie rule; no replacement trainer.
- `scripts/test_focus_retention_experiment.py`: real caller preflight plus approval, runtime, membership, score and selection regressions.

Read-only Git base was `be85889adb30fb931de9671d22250a8397f983a3` with existing dirty
work preserved. No Git writes, public Swift API/taxonomy change or producer-repository edit.

## Acceptance evidence

| Criterion | Observable evidence |
|---|---|
| Explicit approval and pre-launch log |`approval.json`, `authorization.md`, `Research/ExperimentLog.md` FDR-009 entry |
| Frozen data/model/runtime |`frozen-index.json`, `protocol/focus_dataset_manifest.json`; source extension reconstructed by preflight and launch |
| Existing caller integration |`assembly.log`, `preflight.json` exit0, empty stderr; actual trainer execution exit0 |
| Stale/missing approval and changed runtime rejection |New tests; positive preflight never imports Torch or creates training output |
| Membership/configuration/score guards |New tests reject extra partitions, unexpected blockers, changed inputs, invalid/nonfinite scores, missing/duplicate predictions and configuration overrides |
| Retention floor / tie / no eligible epoch |New pure-selector tests and actual trainer dispatch; recorded30/30 eligible epochs; verified saved epoch3 rather than final epoch30 |
| Legacy behavior |`focused-tests.log`:47 passing; `legacy-regressions.log`:59 passing, including earlier development/appearance/extension callers |
| Required offline package checks |`swift-build.log`:exit0, no warnings; `swift-test.log`:14 XCTest+109 Swift Testing pass |
| Bounded one-run execution |`started.json`, `execution.json`, `training.log`; one owned child, no retry;30/30 epochs within deadline |
| Post-run verification |`verification.json` and `verification.log`: recomputed every epoch's selection metrics from retained scores, checked finite checkpoint tensors/hashes and selected/last epochs; no new inference |

Model result and all epoch predictions:
`NativeUITrainer/focus_ring_runs/fdr009-simulator-retention/experiment-result.json`.
Verification used `verify.py`; the actual launch used `run.py`, whose exact command
and timestamps are retained in `execution.json`. Both use the pinned interpreter.
Large reports/weights remain gitignored, not independently backed up by this work.

## Next assignment and completion boundary

**Evaluate FDR-009 on the frozen48 development-validation frames at0.85 against the
retained compatible three-model comparison.** Use original boxes and production
crops, report complete candidate accounting and unique correct/wrong/no/multiple
focus plus misses/false positives. Do not tune on these results, score final challenge,
export or train again. This evaluation needs its own assignment; it was not part
of the one-run approval. Native Photos coverage and source independence remain open.

No new reusable mistake was observed; this work applies BP-107's distinction
between training admission and independent qualification. A lower retention loss
does not change the peer's next action: TTR still owns the nine-control bracket
diagnosis and EXT-CAP work. Shared coordination is **not applicable**; no SMB access
or status publication was performed for this local model run.

All authorized implementation, preflight, training, verification and local handoff
work is complete for review. The owned process exited; no background run remains.
The selected weights, original corpus, full-gate assembly and frozen protocol must
not be overwritten. The next meaningful work is transfer evaluation, not more epochs.
