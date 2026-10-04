# RETAINED-ADAPT-137 — DTM037 native-case adaptation

Completed October 4, 2026 against base1bc11ef plus preserved dirty132–136/OCR work.
The prior goal turn made concrete progress through explicit admission. This tranche
integrated that record and completed the planned single600epoch experiment.

## Outcome

DTM037 fits all nine newly admitted intervals: five within-screen moves, two screen
transitions and two identical controls. It repairs the five previously retained
DTM030 misses **on now-exposed training data**, not an independent holdout. All207
original mixed-label examples and226derived identities retain correctness.

| Correct decisions | DTM036 | DTM037 |
|---|---:|---:|
| Original cases |207/207|207/207|
| Derived identities |226/226|226/226|
| Admitted within-screen |2/5|5/5|
| Admitted screen transitions |0/2|2/2|
| Admitted identical controls |2/2|2/2|
| Quantized global originals |178/207|151/207|
| Quantized global negatives |214/226|41/226|
| Half-frame negatives |0/226|0/226|
| Center-region negatives |16/226|59/226|

The two excluded Balance intervals predict changed, but remain unknown for focus
correctness. No new native independent accuracy, crop/box metric or latency claim.
Candidate rejected as a replacement: original retention is insufficient when
previously improved nuisance behavior regresses. TTR keeps current passive models.

The representation can fit the retained failures. Final constraint radius1 means
this fit was not limited by the old-case radial constraint at completion. It does
not prove generalization or that the architecture is sufficient for all focus tasks.
The narrow native-only loss traded away global-lighting behavior; do not respond
with more unchanged epochs or more duplicate screenshots.

## Implementation and reproducibility

`scripts/adapt_retained137.py` is a thin adapter to existing spatial135 caches,
retention134 constraint and `fit_change_features` trainer. Existing source/cache
contracts remain immutable; no duplicate encoder, trainer or cropper introduced.

- Exact ADMISSION136 hash, producer manifests/request hashes, member bytes, pair IDs,
  native-hint consistency and action/capture chronology checked before preparation
  and again before fit. False pixel-stability flags remain in source evidence.
- Exact DTM036 checkpoint/logits/scales replayed on every cached condition before
  use; nine unique intervals become30weighted rows for equal three-family means.
  Two unknown examples never enter loss or scales. Scales remain frozen from135.
- Zero1152weight correction atop frozen DTM036; old207cases constrain its margins.
  No synthetic nuisance examples enter this fit. Encoder/proposals unchanged.
-600epochs Adam0.01 seed42 CPU2threads fixed-last, standing training authority,
  ≤2GiB outputs. No automatic retry, sweep, capture, export, promotion or Git writes.
- PID27941; fit0.505792s, full fit-entrypoint2.849828s including verification.
  Loss206.675598→0.000147279. These are small cached-head fits, not full-network
  training speed claims. No simulator startup or external wait required.

Checkpoint `NativeUITrainer/focus_ring_runs/retained137-dtm037/last.pt`, SHA256
`8de7602ee5e65aeead3c5916874f0bf819b78def8aed8b548509f7fcc84860bf`.
Source/config/admission/feature hashes pinned in
`artifacts/ready/protocol.json`; run execution/result files retain history and all
probabilities. Exact materialized-checkpoint replay and identity invariance pass.

## Verification

Resident `.venv-yolo/bin/python`, `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts
TMPDIR="$PWD/.build"`:

- `scripts/adapt_retained137.py prepare --ready reports/work/RETAINED-ADAPT-137/artifacts/ready`:exit0.
- Same entrypoint `train`:exit0.
- Repeated preparation into the same destination:expected exit1 `output_collision`,
  before source/model work. Existing output preserved, not a failed fit/retry.
- Seven focused suites:26tests pass,0.615s. Cover equal weighting, unknown labels,
  duplicate/excluded membership, changed admission bytes, incompatible roles,
  identity invariance, radial retention and prior spatial/feature contracts.
- Offline Swift build and explicit serial tests:exit0,14XCTest+128SwiftTesting=142.
  Existing scoped native Vision host access and project-local caches/config/security
  paths; no system reset. Logs `.build/retained137-{build,test,tests,prepare,training,collision}.log`.
- `git diff --check` passes. No protected test change or dependency installation.

Model-workflow skill kept exact role admission, fixed initialization, source parity
and held-out limits explicit; worker workflow completed integration/fit/verification
as one tranche. Software verified; scoped data eligible; no fresh live integration;
model deployment gate failed. Existing independent evaluation restrictions remain.

## TTR publication

Published/read back `packets.RETAINED-ADAPT-137` in the verified
`/Volumes/SharedStatusFile/nuiak/status.yaml` at20:59:39Z. Other semantic fields
preserved (SHA256 after removing own entry:
`f401de0036a6b642f8633858f6f5701f638c556a2c9aa37add6dc5b7edae311f`).
Peer snapshot remains18:46:20Z/expired; no new live readiness inferred. Peer
acknowledgment of this result not observed. Existing negative-coverage request ID
reused; no new build/capture or candidate adoption requested. No transfer or cleanup.

## Next substantial tranche

Use one preregistered joint native/nuisance comparison with explicit replay weights
and preservation gates for previously correct nuisance examples, rather than a
native-only objective. Freeze which constructed augmentations are training and
which remain stress diagnostics before launch; report those roles separately.
Measure the Pareto trade-off against DTM036 and DTM037 on identical inputs, with
all207originals/226identities required. Finish one bounded fit and diagnosis, not
an automatic sweep. In parallel accept any source-bound TTR native-motion inventory;
otherwise keep existing request open without recapture or acknowledgment chasing.
No model becomes navigation authority solely by passing exposed replay cases.
