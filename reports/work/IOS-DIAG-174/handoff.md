# IOS-DIAG-174 — training-fit and retention diagnosis complete

Software verified; existing training data eligible for diagnostic scoring only;
local inference/report integration passed; no model gate passed or promotion.

## Findings

Run019 did not learn off-center placement reliably even on its264added training
images. This contradicts a diagnosis of *only* unfamiliar-probe domain shift.

| Training population | Run017 hits | Run019 hits |
|---|---:|---:|
| Centered72 |43|62|
| Leading96 |0|0|
| Trailing96 |0|11|
| All264 |43|73|

At confidence.25/IoU.5, training page FP96→8; custom AP50 .180870→.326185,
AP50:95 .097534→.154155. This is training fit, not held-out performance.
Run019leading cases:74localization misses,16low-confidence matches,6absent.
Trailing:65localization misses,11low-confidence matches,9absent,11hits.
Centered:62hits,10low-confidence matches. All264cases and family/tint/scale-theme
strata are retained. Source scale/theme coupling remains explicit.

Oracle-best-IoU page boxes have median height ratios2.452leading/2.615trailing,
versus1.349centered. Median horizontal center errors are−.29/+6.35/−.31source
pixels respectively. These describe oracle geometry, not model-selected outputs.
Small vertical geometry is a concrete failure signature; architecture/loss cause
is not proven. Training page boxes are4.46–8.64pixels tall at640long edge;
probes5.76–19.28pixels. Training median5.76, probe median7.51. Merely assuming
probes are smaller is unsupported. Representative leading native source
`placement171-img_004901-leading-semantic-label` was visually inspected: the
left-side dot row is present and not clipped; previous172pixel/label audit retained.

All96probes reconciled for each model. Run019left/native probes still0/48each;
left non-native24:12absent,9localization misses,3low-confidence matches; left
native24allabsent. Centered native24:15absent,9low-confidence; centered non-native
24:19hits,5low-confidence. Exposed probes remain development-only.

## Cancel-action retention

All2400retained-image results reconcile with173.110case IDs change cancelAction
TP/FP/FN:102FP removed,4new FP,4lost TP. Thus171→73FP includes a recall loss,
not just better rejection. MapView removes1FP and preserves100/100TP.

Lost cancelAction IDs (under `test/images/`):

- img_017546.png: correctly placed cancel box, confidence.1634; overlapping label.1811.
- img_017554.png: no retained cancel prediction; overlapping label.2801/link.1194.
- img_017560.png: correctly placed cancel box, confidence.1569; label.2276.
- img_017562.png: correctly placed cancel box, confidence.0398; label.2620/listRow.0587.

Competing labels are observations, not proven causal suppression. No confidence
threshold was changed and absent means absent from the retained export.

## Evidence and checks

Implementation: `scripts/diagnostic174.py` prepare/infer/report, reusing existing
exporter, classifier/matcher and scorer; tests `scripts/test_diagnostic174.py`.
Actual commands used `.venv-yolo/bin/python`, `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONPATH=scripts`; inference explicitly MPS, resident dependencies only.

- Corrected prepare87147, infer63947 and report43650 all exit0.264members/arm;
  017wall export16.109s,01914.252s including validation/loading, not model latency.
- Initial inference stopped before model launch: default reference size limit
  rejected the checkpoint. Original prepared evidence preserved in `artifacts/`;
  explicit256MiBcheckpoint bound and regression assertion fixed it; successful
  source-pinned attempt uses `attempt02/artifacts/`. No capture/training retry.
-13focused tests pass, `.build/diagnostic174-tests.log`, including inherited
  matcher/disposition tests plus exact membership, changed bytes/roles, duplicate/
  missing members, collision, wrong settings, successful/failed inference entrypoints.
- Offline Swift build/test session34667 exit0; logs
  `.build/diagnostic174-build.log`, `.build/diagnostic174-swift-tests.log`.
- [Diagnosis](attempt02/artifacts/diagnosis.json) SHA256
  `6298e97101f32f1d43af60ccfced37fb2afec9307634902b679550a8b5a718e1`.
  Linked protocol pins both checkpoints,264members, source/label hashes, previous
  evaluation and code. Existing96probe/2400retained exports reused without inference.
- All source labels/pixels and prior dirty work preserved. No Git writes, SMB
  publication, TTR changes, training or promotion. SMB is not applicable to this
  local diagnostic. Output budget1GiB checked; no external waits required.

## Recommended next substantial tranche

One controlled balanced training-fit experiment on a frozen subset of already
eligible native training groups, with leading/center/trailing represented equally.
Use fixed initialization, budget and preprocessing, report box-height/IoU and
confidence evolution separately, and retain cancelAction behavior as a guardrail.
This is a diagnostic of learnability/exposure, not a candidate for shipping. Freeze
the precise subset/epochs before launch under standing training authority; do not
train on the exposed probes. If geometry still will not fit training examples,
investigate target assignment/loss gradients before collecting more data. If it
fits, investigate sampling exposure and generalization with one controlled full-
corpus comparison. No automatic multi-run sweep or promotion follows this handoff.
Independently resume TTR native24 intake only once the exact source contract exists
locally; this local iOS diagnosis does not justify additional TTR capture.
