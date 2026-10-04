# JOINT-REPLAY-138 — DTM038 and zero-slack constraint diagnosis

Completed October 4. Previous goal turn made concrete progress through native
adaptation and a measured robustness regression. One preregistered joint run was
executed here; no automatic second fit, capture, export or promotion.

## Result and diagnosis

DTM038's final effective correction is zero: it reproduces DTM036's decisions,
retaining207original cases/226identities and all777protected contrast cases, but
still missing five of nine admitted native intervals. Quantized global negatives
remain214/226; half-frame0/226 and center16/226. Not a new useful model.

This run does **not** show joint learning is impossible. The radial constraint has
one zero-slack example: contrast-before index153 (constraint row333), signed margin
1.7784423828125, between the decision boundary logit(.85)≈1.7346 and the extra
margin floor≈1.7846. The current rule gives that example no allowed decrease at all.
An adverse direction on that one example forces the entire correction radius to0.

Evidence: loss starts124.357849, improves to123.382797 at epoch41, returns exactly
to baseline at42 and ends at baseline at600; final radius0. Initial gradient norm
19.8431 and first-step radius0.006079 show it was not initially dead. A deterministic
unit reproducer with a1.75margin case and adverse correction demonstrates both
radius0 and zero weight gradients. Together these identify a limitation in the
constraint mechanism, not missing labels or a proven feature-capacity limit.
The actual raw optimizer state was not retained, so the exact epoch42 parameter
trajectory is not claimed reconstructed. Preserve raw state/radius history next time.

## Execution

`scripts/joint_replay138.py` reuses the137source-bound admission loader,135cached
features,134constraint and original feature trainer. No prior sealed source changed.
DTM036/scales/encoder/proposals frozen. Nine admitted native intervals plus866existing
contrast views, equal five-family means through21650deterministically repeated
feature rows.875logical source views, not875independent images; no repeated decoding.
Constraints:207originals+385contrast-before+392contrast-after=984. Quantized and
localized diagnostics are not in the fit or constraint selection. No new data roles.

600epochs Adam0.01 seed42 CPU2threads, fixed-last,1152new correction weights,
≤2GiB outputs. PID29537; fit2.710115s, whole entrypoint4.980705s. Feature bank<100MiB;
44GiB free internal space checked. No native device operation or external wait.
Checkpoint `NativeUITrainer/focus_ring_runs/joint138-dtm038/last.pt`, SHA256
`7a92efd861b5f1eb8a39d312f6a87d4d4ec9190d2396fd0ae4483945a5d9b43c`.
`artifacts/ready/protocol.json` binds membership/config/source/cache hashes and
constraint indices before fit. Execution/result files preserve all probabilities,
history, checkpoint identity and timing. Exact saved-checkpoint replay passes.

## Verification

Resident `.venv-yolo/bin/python`, `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts
TMPDIR="$PWD/.build"`; `joint_replay138.py prepare` and `train`, each with
`--ready reports/work/JOINT-REPLAY-138/artifacts/ready`, exit0.
Eight focused suites:29tests pass(0.775s), including exact family weighting,
constraint selection, role rejection and the zero-gradient reproducer. Offline
Swift build and explicit serial tests pass:14XCTest+128SwiftTesting=142; no native
source changed after that run. Logs `.build/joint138-{tests,prepare,training,build,test}.log`.
`git diff --check` passes. Existing dirty132–137/OCR work preserved; no Git writes.

Software verified. Existing data eligibility unchanged. No new live integration.
Model efficacy gate failed. Model-workflow skill prevented a fit/retention pass
from being advertised as independent accuracy or a replacement candidate.

## Next substantial tranche

Repair the optimization guard before another full comparison: preserve the actual
.85/.15 correctness boundary with strictly positive numerical reserve where the
baseline permits, rather than freezing the margin of near-boundary examples.
Explicitly handle exact-boundary cases; test feasible adverse directions, conflicting
constraints, identity invariance, gradient flow and materialized replay. Do not
lower classification thresholds or drop difficult examples. Check source-bound
minimum slack and first-step movement in preflight; retain raw optimizer/radius
history. Then perform one fixed corrected joint fit on identical membership and
weights, compare against DTM036/037/038, and diagnose any residual failure. No more
unchanged fits or broad collection is justified by this result.

TTR's snapshot remained18:46:20Z/expired; no new runtime readiness or native-motion
inventory verified. Existing negative-coverage request remains complementary.

Published/read back `packets.JOINT-REPLAY-138` in verified
`/Volumes/SharedStatusFile/nuiak/status.yaml` at21:07:19Z; unrelated semantic fields
preserved (SHA256 `25585dc637b2f5b83e241fce0aacdc66b1d78bc3ec9bf37f874f2a3bcdb2b128`).
Peer acknowledgment not observed. The message identifies our local optimizer issue,
not a producer blocker, and requests no new build/capture or model adoption.
