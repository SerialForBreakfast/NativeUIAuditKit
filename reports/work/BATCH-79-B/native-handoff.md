# Approved native admission and DTM017 comparison

Maintainer explicitly approved77's exact twelve-pair calibration→train change, then
authorized capture/training/promotion subject to gates. Completed admission and one
controlled candidate. No capture needed; shipped models remain unchanged.

## Admission and execution

44train/5exposed Settings development, original37records/roles unchanged.12new native
pairs retain unknown scroll and shared Fixture ancestry; no independent final set.
Decision memberSHA2567583cb0951b3a903f4d9cf8efdefcc7671b2dfc58a9444e16c6fd6d5bbecad34.
Existing propose_native77 CLI materializes exact approval after fresh source rebuild.
Admitted corpus/receipt: reports/work/NATIVE-ADMISSION-77/admitted/. Original proposal
and32/5admission preserved. Rich24excluded pending producer source compatibility.

Existing ranker preparer binds admitted supervision separately from image derivatives.
All83images/2337proposals reused with zero crop calls. Added explicit74frame config
while retaining original50frame config; admission, per-frame split/size, multiple
positives, control/reference membership and probability bounds checked before launch.
Original37frozen DTM013probabilities match; new12control results computed once.
DTM016reference and DTM017candidate use identical inputs; no box truth supplied to
inference. One600epoch CPU2thread Adam0.001/seed42/fixed-last run, unchanged network.

## Results

| Group | DTM016 endpoints / paired | DTM017 endpoints / paired | Interpretation |
|---|---|---|---|
| Original32train |64/64;32/32|64/64;32/32|Prior fitting retained|
| Added12native train |5/24;2/12|24/24;12/12|Fits new labels, not held-out performance|
| Exposed5Settings dev |0/10;0/5|1/10;0/5|Transfer still fails|

Frozen change head misses4native transitions: compact-light-s31-p0,
wide-dark-s31-p0,wide-light-s31-p0,wide-light-s31-p5. Native joint success8/12.
No abstentions despite errors; confidence is not calibrated for navigation safety.
No model gate passed. Promotion authorization does not waive these failed gates.

Admission21.096s; preparation25.880s (source audit plus reference/control inference,
zero recrop); fit1.349s,total model execution2.551s. PID42957,exit0. Checkpoint replay
and candidate-order parity pass. Rank-only resident median0.0161ms excludes proposal,
crop,encoding,change model and application costs; not end-to-end latency.

## Verification and preservation

-Actual admission/preparer/trainer/verifier CLI all exit0. Initial trainer exit2 before
 execution: log heading lacked required Run prefix/hash binding; corrected, no model
 retry. .build/native79-{admission,prepare,training,training-r2,replay}.log retained.
-62focused Python tests pass22.726s. Four real-protocol guards additionally verify
 missing approval, wrong batch, changed pins and out-of-range control probabilities.
-Offline Swift build/test succeeds:14XCTest+120SwiftTesting. .build/native79-swift-*.
-Native completion receipt records terminal exit0; original started execution receipt
 preserved. Result/checkpoint references and comparison in native-replay.json.
-Checkpoint SHA256f772463766c4226ec09644050295f83aa9bcd21d140725d9161f34635e8bcbe0.
 Protocol SHA256fbcf14d46e439504ee45614d45947d62da8f8957d3e466cc9a912f22be8bd738.
-All raw artifacts remain local/ignored; no Git writes, external source edits or SMB
 update. Producer's existing source-publication request remains unchanged.

Software verified; new12eligible for the approved development-training experiment;
local input/model integration verified, physical/live producer qualification unchanged;
model gates failed/not established. No production change or final-evaluation claim.

## Next substantial tranche

1. Diagnose DTM017Settings error ranks, content/style shortcuts and DTM013native change
   misses using retained predictions/frames, with full-frame movement kept separate
   from actual focus. Do not repeat unchanged epochs.
2. Define one controlled change-head comparison on44/5and a separate ranker transfer
   hypothesis only after diagnosis. Preserve the new baseline, match inputs and report
   development exposure. Existing authorization permits scoped work, not arbitrary sweeps.
3. In parallel, integrate rich-v2source when published and reconcile missing semantic
   coverage for one batch campaign; do not recapture the already retained36pairs.
