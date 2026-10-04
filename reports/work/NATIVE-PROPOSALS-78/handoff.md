# NATIVE-PROPOSALS-78 — candidate coverage ready without new capture

Extended existing prepare_proposal74 entrypoint with explicit calibration inspection.
Revalidated77's12native-table source pairs; no admission or train/development relabeling.
The24source images fed one rectangles-only Vision request and unchanged raster
proposer. Focus labels only scored candidate outputs afterward; no oracle boxes added.

| Method | Endpoint coverage at IoU0.5 | Multiple positives |
|---|---:|---:|
| Vision |24/24|1|
| Raster |24/24|0|
| Union |24/24|24|

196automatic union candidates,max11per frame; retain all overlapping positives for
the later ranker. This establishes available geometry, not focus-selection accuracy.
bank-host/inputs.json is calibration-proposals-v1 with trainingEligible:false;
training-bank loader rejection tested. Raw native output, request, source hashes,
timing receipt and separate scoring report retained. No simulator or TTR runtime used.

## Execution and efficiency

Existing .build/debug-output/proposal74/probe/source hashes match74's recorded inputs.
First restricted execution exited0 but returned per-frame Vision errors. Wrapper
initially raised before saving raw output; fixed to retain structured failures first.
One-frame diagnostic retained NSOSStatusErrorDomain-6662: CVPixelBuffer creation failed
at455×256BGRA. This is a native execution-context failure, not missing source images.
Scoped normal-host execution succeeded without binary/recipe changes, service resets,
signing repair, simulator setup or permission weakening. All configurable temp output
project-local. Use this known scoped execution context for future equivalent probes.

Successful24image batch0.8615s native,total4.1090s including source validation/raster.
No claim of simulator lifecycle speedup or end-to-end training throughput. Inputs can
be reused after explicit role binding; there is no reason to regenerate these proposals
when77approval arrives. No automatic model execution follows proposal coverage.

Command: prepare_proposal74.py --calibration-proposal
reports/work/NATIVE-ADMISSION-77/proposal/proposal.json --output
reports/work/NATIVE-PROPOSALS-78/bank-host --probe .build/debug-output/proposal74/probe.
Exit0; original failed attempt in bank/, diagnostic preserved. .build/native78-*.log.
49focused Python tests pass0.620s; offline Swift build/test14XCTest+120SwiftTesting pass.
git diff --check passes; all prior dirty changes preserved. No SMB update: no changed
producer action, existing source-publication request remains valid independently.

Software verified; calibration geometry coverage verified; native probe integration
verified; model gates not assessed.77role approval still pending. Rich24not included;
local TTR HEAD remainsf933e299. No capture, admission, training, export or promotion.

Next substantial tranche after the maintainer's12pair role decision: materialize44/5
admission, combine retained74+78candidate inputs under explicit roles, prepare only
new crops once, and predeclare one native-transfer ranker comparison. Preserve exposed
Settings status, exact DTM013change control, unknown table scroll and final ancestry
exclusions. No full re-extraction, unchanged retraining loop or recapture required.
