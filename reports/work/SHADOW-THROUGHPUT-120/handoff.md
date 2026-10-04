# SHADOW120 — lower-overhead native transition consumer

Selected from SHADOW-FEEDBACK-01's measured resource-overhead work while TTR
imports DTM030. Finished implementation, actual caller integration, full parity,
portable package verification and cross-project delivery. No new model/roles,
capture, training, export, production promotion or Git writes.

## Result and acceptance

| Evidence | Delivered118 | Consumer120 |
|---|---:|---:|
| Exact encoded tensor hashes |438/438|438/438|
| Exact threshold decisions |438/438|438/438|
| Max PyTorch/CoreML probability error |5.364e-7|5.364e-7|
| Median preprocessing |183.869ms|120.219ms|
| Entire438pair replay |86.159s|53.436s|
| Cold-pair median (95pairs) |206.251ms|174.775ms|
| Mixed-reuse median (343pairs) |180.696ms|119.298ms|

Consecutive CPU replays on identical images/order/batches; filesystem may be warm.
Median preprocessing34.6%lower, total38.0%lower. No universal timing, statistically
replicated benchmark or independent accuracy claim. Model-only inference remained
~0.54ms; pixel preparation remains dominant. No full-resolution cache retained.

Integer resizing shares RGB weight/index work without changing coefficients,
rounding stages or tensor conversion. Request-owned LRU stores at most8encoded
frames/2359296payload bytes. This is not total peak memory. Each hit independently
checks current path/size/bytes SHA256. No filename/timestamp trust; no global or
cross-request state. CLI off path never calls the encoder. Stateless path preserved.

Tests prove eviction, actual-byte mutation rejection despite existing cache entry,
symlink rejection even for known hashes, request isolation and exact cached versus
stateless tensors.139offline Swift tests (14XCTest+125SwiftTesting),24actual CLI
contract tests and2Python cache-accounting tests pass. Actual native parity covers
all438retained/synthetic cases. Standalone extracted source builds and scores its
synthetic vector with exact expected tensor/decision/score. Text portability scan
finds no machine home paths. No private captures/raw weights/executables in archive.

## Reproducible evidence

- `scripts/benchmark_shadow120.py`: sealed artifacts/attempt02/comparison.json;
  delivered/optimized/parity.json and per-batch requests/replies/exit codes.
- Existing verifier, native CLI test suite and generic packager reused.
  `scripts/package_shadow120.py` requires measured benefit plus exact parity and
  reuses identical model bytes, not export/recompile.
- Logs `.build/shadow120-{focused,release,benchmark02,cli-tests,python,build,test,
  package,portable-build,portable-run}.log`; all completed commands exited0.
- Initial benchmark exited1 before inference: standard Swift release symlink
  rejected by artifact-path validator. Failed artifacts/delivered/request-0.json
  and `.build/shadow120-benchmark.log` retained. Corrected to exact architecture
  binary with fresh attempt02; integrity policy unchanged.
- Original118archive, compiled model, checkpoint and all unrelated dirty edits
  preserved. New isolated source package has19members,866723expanded bytes.

## Delivery

Verified SMB `smb://sillycon.local/SharedStatusFile` and sufficient capacity.
Archive `nuiak/nuiak-transition-shadow-dtm030-consumer-v2.zip`,208121bytes,
SHA256 `33aeee7b85e7bb851d53c3caaf22e8ba3ff0eda886bf9fe66f692b6ee7d3d5c4`.
Source preserved under artifacts/attempt02/package. Unique staged publication and
exact byte readback passed. Follow-up
`nuiak/responses/nuiak-20261004-dtm030-consumer-throughput.yaml` references existing
request `nuiak-20261004-dtm030-shadow-delivery`, not another feature assignment.
Own status entry published/read back with duplicate-key validation and all unrelated
semantic content preserved. TTR16:17UTC reported discovering/importing DTM030;
no exact copy receipt or consumer-v2 acknowledgment yet. No shared cleanup performed.

Outcomes: software passed; data eligibility unchanged/not applicable; NUIAK CPU
and portable integration passed; TTR adoption pending; model gates not assessed.

Next substantial tranche: reconcile exact versioned TTR receipt, ingest approved
on/off and reviewed disagreement evidence, and reserve genuinely new source-bound
journey groups for a matched DTM025/DTM030 evaluation before tuning. Include real
no-ops/content-only motion and scrolling, not merely identical-frame negatives.
Geometry109still requires corrected source boxes; current exposed Fixture/Settings
ancestry cannot establish independent final performance. Do not interrupt TTR's
ongoing survey or repeat unchanged training while waiting for those inputs.
