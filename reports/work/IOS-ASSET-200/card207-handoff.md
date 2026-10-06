# DETECTOR207 — fixed card crops and worker feedback closure

2026-10-06. Implemented actual prepare/infer/report CLI in `scripts/card207.py`,
reusing roi193 crop/annotation/restoration and existing strict exporter/scorer.
No new cropper, trainer, native capture or role change. Run022 remains fixed.

236prediction-selected crops from96development frames; no truth selects a window.
MPS crop inference34.703s, no repeated full-frame pass. Identical windows within a
frame are grouped. Parent/non-imageView metrics are asserted unchanged per group.

| imageView operating TP/FP | Baseline | Crop composition |
|---|---:|---:|
| Grid procedural,80targets |80/0|80/6|
| Grid lower detail,80targets |12/0|28/0|
| Grid busy,80targets |3/0|20/1|
| Detail,16targets per condition |16/0|16/0|

Independent per-frame one-to-one assignment audit:33recovered, zero lost original
matches;143→176total TP. Seven addedFP. Lower-detail AP50 decreases .49970→.49192
despite TP growth; busy AP50 improves .29950→.39548. These custom composite scores
include thresholded crop donors, not an unchanged single-model confidence ranking.

**Decision:** context/scale helps, but this rule is not production-ready. Do not
promote or tune thresholds on these frames. Sixty busy targets remain missed.
Next: review already retained204thumbnail families and freeze a training-compatible
nested-image campaign, retaining this fixed crop comparison as development evidence.
Preserve parent and child labels; CardDetail/IMAGE201remain development-only.

Verification: five focused tests pass; positive real CLI prepared/inferred/reported
all frames; strict source/model/input/crop identities validated. Required offline
Swift build passes;139tests/19suites pass4.193s. Logs `.build/card207-{build,test,inference}.log`.
Protocol source pins were reverified after final review; no source drift accepted.
Actual CLI repeat-prepare exits1 with output_collision, preserving all results.
Reporting1.725s; full output33,197,452bytes, below the1GiB cap. Final focused tests
rerun5/5pass and diff whitespace check passes. No known required check left unrun.

Artifacts under `artifacts/card207-01/` (ignored):

- Protocol SHA256 `f09f8758e723c14be27a2748b786b7f782b6890027c4b06e8e2abf82f5356957`
- Predictions SHA256 `4840ac814a9bfb07c1fdd772fa551386402861adf9c078258f1e42e5dcae2366`
- Report SHA256 `09a0da5aa322be36b1b81c12e88ea97aeb03db9306d6581ae2a5c0e1069657b6`

Companion: corrected Big Dog report received65,218bytes/9members, independently
matched all41class counts/AP across both models and all585windows. Two correction
tests locally pass; no GPU repeat. Six full tests are peer evidence. Transfer,
acceptance and sender cleanup are separate. See WORKER-198/paired-review.md.

Outcomes: software verified; data remains development-only; local inference integration
passed; model gate not assessed/no promotion. TTR native capture-source binding still
limits205/206. No Git writes, installs, external-repository edits or monitoring.
