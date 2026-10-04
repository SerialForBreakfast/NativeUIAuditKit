# NUISANCE129 — normalization and alignment diagnostics

Software passed; transformed-data admission not performed; producer integration
and model gates not assessed. Blind affine/combined preprocessing rejected for
original retention loss; alignment not qualified for general motion robustness.

## Corrected result

All six asymmetric lighting conditions recover226/226identity-source negatives
with affine or combined correction. But untouched originals fall207→204, failing
rows0/12/45. Normalization can remove or distort useful focus evidence. Horizontal
alignment retains207/207originals, but after-only shifts remain asymmetric:
left original181→166 and identities76→66; right original174→199 and identities31→76.
Neither mechanism is a safe unconditional production correction.

Corrected run exit0,78.781seconds; final report seal independently recomputed after
JSON reload.10Python and139Swift tests pass; `git diff --check` passes. No training,
weights, thresholds, shipped resources or external-repository changes.

Next substantial experiment: preserve raw and photometrically corrected evidence
as separate signals in one bounded retention-aware comparison. Record new feature
scope and augmentation admission before fitting; require207originals/226identities
retained and nuisance improvements. Shift/cropping labels stay diagnostic until
qualified. TTR's retained real failures remain the independent integration priority.

Frozen DTM031, original433members plus10ASYMMETRIC128conditions. Source images
reverified/encoded once per run, fixed thresholds and no training or native capture.
Three mechanisms: robust affine after→before correction, horizontal[-2,2]alignment,
and their composition. All case scores, fitted parameters, shifts/clipping and
group errors are retained locally. These are not independent model-quality metrics.

## Implementation findings preserved

Initial `artifacts/audit/report.json` must not be used as sealed acceptance evidence.
Two bugs were identified after that run:

1. Trimming could leave a constant-pixel support set and reset the previously
   identifiable slope to1. A mostly-flat synthetic test reproduced8%absolute error.
   Corrected fitter retains the previous slope when new support has no variance.
2. Integer displacement keys in nested dictionaries changed canonical ordering after
   JSON roundtrip. Reuse failed closed with `reuse_binding`; it was not bypassed.
   String keys now preserve roundtrip seals; a regression test covers this.

Original output and failed reuse log preserved; corrected run uses `artifacts/repaired`.
An actual repeated CLI destination was rejected with `output_collision` before work.
No original report, corpus, checkpoint or peer file overwritten. No automatic fit.

SMB publication not required: current passive-only policy and existing retained-case
request unchanged; no new consumer artifact or producer action. Peer status was
checked at entry and still prioritizes Settings boundary evidence. These local
diagnostics deliberately do not operate or interrupt that producer session.

## Commands

Resident Python with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build"`:
`scripts/nuisance129.py --output reports/work/NUISANCE-SEPARATION-129/artifacts/repaired`.
Ten focused tests cover affine recovery, constant support, shift direction/no wrap,
padding, identity, JSON sealing and temporal interventions. Final offline Swift logs
are `.build/nuisance129-final-{build,test}.log`. Raw logs remain project-local.

Correction-only reuse was attempted once and rejected; the corrected full run is
necessary because the original report seal was invalid. This is failure repair,
not selection among model candidates or threshold tuning.
