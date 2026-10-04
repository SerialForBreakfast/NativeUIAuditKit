# TRANSFER-62 — sensitivity, stationary intake and status safety

## Result

Frozen DTM009 shows location sensitivity, not merely frame-order sensitivity.

| Condition | Training paired boxes | Raw change | Settings paired boxes |
|---|---:|---:|---:|
| Baseline |24/24|24/24|0/5|
| Reverse |24/24|23/24|0/5|
| Left4% |12/24|24/24|0/5|
| Right4% |12/24|24/24|unavailable:5rejected|
| Up4% |12/24|24/24|0/5|
| Down4% |11/24|22/24|0/5|

169evaluations,5off-frame truth cases rejected, no clipping of labels. All29baseline
predictions match the retained FIT-61 report. Reversal abstains3/24; down abstains3/24;
other training conditions all decided. Settings all decided where eligible, raw
change2/5. Black fill is a distribution change: this is sensitivity evidence, not
proof of one causal defect. No weights or thresholds changed.

## Integrated software and cleanup

- `diagnose_transfer62.py`: frozen membership/model hashes, paired transforms,
  analytic truth, rejection accounting and baseline prediction parity.
- `intake_stationary_transition.py`: explicit inspection-only entrypoint using
  existing version1 envelopes. Legacy consumers retain their condition allowlist.
- Requires verified native focus, unchanged nonempty observed offsets across four
  brackets, both owner bodies visible in both frames, same instance/recipe, ordered
  delivered action/capture receipts, unchanged bytes/sidecars and verified cleanup.
- `update_nuiak_status.py` / `sync_shared_status.py` are now fail-closed retired
  entrypoints. Removed hardcoded stale whole-file writers; no automatic replacement.
- Preserved all pre-existing GEOMETRY58–FIT61 edits, raw inputs and failed evidence.

## Verification

Actual diagnostic CLI used `fit61-dtm009/result.json` and `FIT-61/evaluation.json`,
writing sealed `sensitivity.json`. Exit0. Initial attempts exposed a missing summary
baseline field and missing output parent; both repaired without training or data
changes. Failure logs were overwritten by the successful command log; no failed
capture or corpus evidence was removed.

Focused Python suite:76tests, including actual stationary CLI success/collision,
interior switch, missing/conflicting offsets, altered hashes, wrong run/focus,
cleanup failure, unknown transforms, off-frame rejection and legacy isolation.
Logs: `.build/transfer62-tests-sealed.log`.
Offline Swift build/test:exit0,14XCTest+120Swift Testing. Project-local caches;
scoped host compiler permission, no dependency updates or device operations.
Logs: `.build/transfer62-swift-{build,test}.log`.

No capture/intake of genuine new data, training or external waits. Python focused
checks take about3seconds; diagnostic wall time was not separately instrumented.
Do not infer training performance from this diagnostic run.

## Coordination and independent outcomes

`nuiak-20261003-transfer62-stationary-compatibility` published/read back in verified
SMB `nuiak/status.yaml`, preserving all other content. Peer acknowledgment pending.
[Request and scope](coordination.md). This is compatibility planning only; actual
target/runtime/capture authority and later data admission remain unresolved.

Software verified:passed. Existing data roles unchanged; new stationary data
eligibility:blocked pending genuine input/approval. Producer-specific live
integration:not assessed. Model gates:not passed; no promotion.

## Next substantial tranche

ROBUSTNESS-63: one controlled paired-translation training comparison with unchanged
model/loss/120epochs and24training pairs, plus retained-source coverage audit.
Freeze augmentation schedule before launch, keep Settings scoring-only, record
fit and robustness separately. No extra epochs/sweep after failure. New capture
remains separately authorized and does not block local approved experiment work.
