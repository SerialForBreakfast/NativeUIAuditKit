# RANK-METRIC108 — bounded reference scoring

October4,2026. Completed; **reject ranker replacement**. Preserve DTM020 and the
already-delivered DTM025 change observer. No new capture, data-role change, training,
export, model promotion, external writes or Git writes.

## Results on identical inputs

Frozen COLLECTION104:108training pairs and5exposed Settings development pairs;
187unique frames /5022candidate crops. References contain4799candidates from178
training frames only (387positive,4412negative), preserving Fixture ancestry.
Same-frame exclusions do not make related recipes independent evaluation.

| Ranker with fixed DTM025 change | Old training joint | New training joint | Settings joint |
|---|---:|---:|---:|
| Retained DTM020 |66/68|4/40|2/5|
| Rejected DTM027 |66/68|40/40|0/5|
| Reference scorer, same-frame excluded |65/68|40/40|5/5|
| Reference scorer, self-allowed replay |66/68|40/40|5/5|

Unique-frame correctness with same-frame exclusion:121/122old,56/56new,9/9Settings.
All five prior Settings successes retained; one old success lost. Self replay is
trivial training retrieval, not a reason to waive that failure. Two old change
abstentions are unchanged. There is **no calibrated localization abstention rule**;
reported abstentions use the existing fixed0.85change rule only.

All five Settings pairs pass (before/after IoU):

| Pair suffix | Before | After |
|---|---:|---:|
|3FF537A2-B493-4FF6-BEDC-EB8D3622A9FA|0.9061|0.9108|
|F27D94F4-634C-4E6C-BFFA-2AF9B74F2B6C|0.9049|0.8917|
|6677A2C0-81C7-447D-A9B8-A5D9C0324DC0|0.8917|0.8916|
|CCE16196-2B88-46FB-9FE3-905FEA276591|0.8511|0.9390|
|6E7FDFAA-3F75-42C5-9266-2C4AB0ADCC48|0.9385|0.9343|

These Settings screens were already exposed during development. No independent
test accuracy, TTR navigation success or production gate is established.

## Old failure diagnosis

Frame727c03d5… is the after image of
`reference-nostalgex_guide-s83-v0-city-light-scroll_moved` (3840×2160).
Source bytes verified and visually inspected: the green focus border spans the
whole Harbor row. Ground truth is[408,1168,3042,162]. Both competing candidates
cover its right-hand portion, not a different row:

- Selected vision-3:[1517.62,1197.85,1917.81,107.68], IoU0.41904,
  contrast−0.03122255.
- Available positive raster-3:[1512,1182,1926,132], IoU0.51589,
  contrast−0.03694907.

The narrow candidate wins by0.00572652 despite worse extent. Both have the same
nearest positive reference (36acb2f3…,raster-2); their nearest negatives are two
different candidates in b6b4826f…. This establishes an extent-ranking failure,
not missing proposals or proof of lost low-resolution information. The passing
proposal is itself marginal. No label, threshold or special-case fallback changed.
Full IDs, geometry, distances, neighbor provenance and affected pair are in JSON.

## Implementation and cost

`scripts/focus_metric_reference.py`: versioned training-only bank; finite float32
770features; stable reference ties; max8192references,80queries per call; one query
and512references per distance block. Direct float64 differences/in-place square
avoid cancellation. No labels supplied with queries. Existing production crop
encoding and existing pair evaluator reused; no new cropper/trainer.

`scripts/evaluate_metric108.py` constructs/reloads the hash-bound bank, verifies
source/admission roles, replays DTM020/027 checkpoints, evaluates both reference
modes and independently matches **all5022scores exactly** to the naive oracle.
Preserves earlier diagnostic outputs; canonical result is `artifacts/verified/`.

- Tensor14,780,920bytes; NPY14,781,048bytes; provenance manifest1,106,957bytes.
- Distance block scratch upper bound4,734,976bytes, excluding bank/metadata.
- Whole diagnostic process peak RSS742,375,424bytes includes PyTorch controls,
  source/candidate reports and the deliberately unbounded-per-query naive oracle;
  this is not measured deployment memory of the chunked scorer.
- Same-frame-excluded scoring: first frame121.34ms, median71.25ms,p95 128.20ms;
  total13.145s for187frames. Self replay median70.41ms.
- DTM020 median0.0206ms and DTM027median0.0152ms in local CPU/2thread replay.
  These measure encoded-feature scoring only, not image decoding, proposals,
  production crops, cold model load or end-to-end device latency.
- Complete diagnostic44.40s, including17.07s independent numerical oracle.
  Zero simulator launches, new native crop invocations or external waits.

The bank is much larger/slower than the learned head. No Core ML package exists
for it; compliance with deployment size, latency and confidence requirements is
not claimed. Compression or pruning would need its own fidelity comparison.

## Verification and acceptance

22focused/regression Python tests pass (5metric,6representation,6retention,
5collection). Covers multi-block/permutation/tie parity, tiny distances, exclusions,
empty support, missing provenance/development references, duplicate references,
invalid tensors, oversized query batch, modified bytes and unsupported manifests.
One initial test incorrectly attempted to overwrite an immutable test manifest;
fixed to create a new negative fixture. Production collision protection retained.
Offline Swift build/test exit0:14XCTest+123SwiftTesting. Logs:
`.build/metric108-swift-build.log`, `.build/metric108-swift-test.log`.

Commands (root; local TMPDIR, no bytecode):

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build" .venv-yolo/bin/python -m unittest scripts.test_metric108 scripts.test_representation107 scripts.test_retention105 scripts.test_collection104
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build" .venv-yolo/bin/python scripts/evaluate_metric108.py --output reports/work/RANK-METRIC-108/artifacts/verified
```

The evaluation destination now exists: use a new destination only for a justified
rerun, never overwrite it. Evaluation JSON SHA256:
`817780473ef6af80debc3099bf1722e29fb2cc4882a8982fdcc7edb6d20e8cdb`.

Outcomes: **software verified**; **data eligibility unchanged** (training/exposed
development only); **offline integration verified, live TTR not assessed**;
**replacement retention failed, production model gates not assessed**.

Preserved all pre-existing changes and evidence. Added only scorer/evaluator/tests,
ignored local artifacts, task/plan/state/lesson updates and this handoff. No SMB
publication: TTR's next action remains integrating the delivered DTM025 observer,
so this local rejected candidate does not change its assignment. No new peer
acknowledgment or current runtime status asserted.

## Next substantial tranche

RANK-GEOMETRY109: batched extent/proposal-order audit on all187frames; freeze one
justified geometry-aware ranking-loss comparison using existing training labels,
same architecture and cache; evaluate against DTM020 and this reference control
with unchanged retention gates. No larger backbone or threshold sweep assumed.
In parallel, accept permitted TTR shadow feedback when actually delivered; absent
delivery must not stall local work. Independent reviewed journeys remain needed
before any generalization or navigation-quality claim.
