# PROPOSAL-RANK-74 — automatic candidate bank ready for ranking experiment

Same32training/5development pairs, no capture/admission/model training. Automatic
candidate recall atIoU0.5:

| Source | Training endpoints | Development endpoints |
|---|---:|---:|
| Vision rectangles |40/64|10/10|
| Existing fixed raster proposer |64/64|0/10|
| Union |64/64|10/10|

Vision has12ambiguous-positive training endpoints; union40. Keep all overlapping
positives, rather than arbitrarily turning valid boxes into negatives. Candidate
recall is not focus-ranking accuracy or generalization. Opposite per-domain behavior
is an important source-effect confound for the next learned ranker.

Frozen union-bank/inputs.json contains59unique images and2,141automatic candidates,
max59/image, plus pair/group/split references. No focus labels in candidate inputs.
union-bank/supervision.json separately records positive/negative IDs, original
admission/corpus references and every endpoint. No oracle boxes injected.37pair roles
unchanged, development remains exposed and no independent final evaluation exists.

## Efficiency and evidence

- Compiled existing vision_annotation_probe.swift to a separately named local binary;
  optional rectanglesOnly skips OCR, default OCR behavior unchanged.
- prepare_proposal74.py actual run:50deduplicated training images, two≤40image native
  calls,180s bound each. Native3.147s,total21.998s including source validation.
  Original bank outputs850,447bytes. Retained Settings rectangles reused.
- verify-only rechecked raw-to-candidate parity and source hashes without new native
  execution. bank/verification.json binds requests/raw results/receipts and artifacts.
- Fixed raster proposer:50training images5.537s. Subsequent comparison reused those
  results and processed only9development images0.769s. No parameter search.
- Explicit --publish-union produced separate inference/supervision artifacts; actual
  label-free loader validates hashes, geometry, counts, IDs and allowed fields.

Commands/logs: .build/proposal74-{compile,run,verify,raster,raster-complete,union}.log.
Scripts: prepare_proposal74.py, compare_proposal74_sources.py. Results:
bank/report.json, raster-complete.json and union-bank/*.json. Historical initial
Vision-only bank and failed coverage remain preserved, not overwritten.

11focused Python tests pass: deduplication, role isolation, source dimensions/hashes,
native errors/disabled OCR, labels excluded from candidate inputs, empty/multiple
positives and existing proposal comparison tests. Offline Swift build/test pass
14XCTest+120SwiftTesting; native probe compilation and actual execution pass.
git diff --check passes. Outputs project-local, raw SSD inputs read-only. No git writes.

Software verified; existing data roles preserved with derived candidate evidence;
local native/offline integration verified, TTR runtime not assessed; model gates not
passed. SMB not applicable: this local bank changes no producer action.

Next substantial tranche: freeze and test one visual candidate-ranking experiment,
using multi-positive supervision and keeping DTM013 change branch fixed. Verify crop
parity, missing-candidate abstention, training fit, source-stratified development and
runtime cost. Declare/log exact architecture and budget before model execution.
No automatic training/promotion follows merely from100%candidate recall.
