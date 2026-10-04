# SPATIAL-135 — paired spatial evidence and matched comparison

| Outcome | Result |
|---|---|
| Software verified |22focused Python, offline build and142explicit-serial native checks pass.|
| Data eligible |Existing1299training views unchanged; peer11remain exposed diagnostics. No new labels/roles.|
| Integration qualified |Retained TTR inputs verified; current peer snapshot unchanged/expired. No new live qualification.|
| Model gate passed |Original retention passes for both arms; nuisance/peer efficacy insufficient. No replacement/export/promotion.|

Base1bc11ef; preserved dirty132–134 and OCR changes. Completed full proposal audit,
paired interventions, shared feature preparation and one two-arm training comparison.
No capture, native proposal invocation, Git writes, dependency installation or cleanup.

## Spatial support audit

291unique source images:282existing training endpoints+9peer originals. Reused187
historical image-only proposal frames and generated104with existing bounded raster
detector. Zero empty frames and zero encoded-hash collisions; no target boxes passed
to proposal creation or inference. Among187previously annotated frames,176have
unambiguous geometry and all176retain a proposal atIoU≥0.5. Eleven conflicting
identities remain excluded from precise recall;95Region and9peer images have no
trusted body-box recall. Change labels do not fabricate body labels.

Source masks preserve encoder letterboxing/rounded scale. Baseline DTM031 entrypoint
replays to1e-6 and identical decisions; interventions leave RGB context unchanged.
Inside-only differences retain204/207originals (losses12,107,109); outside96/207.
Both retain226identity probabilities. Inside fixes no peer misses; outside repairs
Survey26's5→6and8→9screen transitions but is not a viable replacement.
The five retained DTM030 misses carry94–99%of difference energy inside proposals;
coverage of changing pixels is not evidence of focused-control identity correctness.

Audit26.022s, of which17.996sproposal preparation. Source-bound reusable cache:
`artifacts/audit/proposals.json`; sealed full results `artifacts/audit/report.json`.
No raw images copied. Masks/coverage and explicit missing truth are retained.

## One controlled training comparison

Frozen DTM031encoder/logit; same1299training views, two1152weight corrections:

- DTM035control: duplicate whole-frame576residual features.
- DTM036: separate576inside/outside residual features, whole RGB context retained.

Both use train-only std scaling, original signed-margin constraints from134,
600epochs Adam0.01 seed42 CPU2threads, fixed-last. Same existing trainer, no sweep.
Proposal masks are fixed across photometric transforms: conditional representation
comparison, not end-to-end proposal-generator robustness. No peer/quantized cases in fit.

| Measure | Raw/raw DTM035 | Local/global DTM036 |
|---|---:|---:|
| Original confident correct |207/207|207/207|
| Exact identity controls |226/226|226/226|
| Contrast-before originals |143/207|171/207|
| Contrast-after originals |136/207|178/207|
| Quantized global originals |121/207|178/207|
| Quantized global negatives |190/226|214/226|
| Quantized half-frame negatives |2/226|0/226|
| Quantized center negatives |16/226|16/226|

Both retain DTM030's five peer misses; two identical peer intervals remain unchanged.
No native-hint aggregate becomes accuracy. Local/global features improve the controlled
global nuisance task, but do not solve real transfer or localized appearance changes.
Reject model replacement. No unplanned fit after seeing these results.

PID24106; preparation31.340s; combined fit/eval1.243s (fits0.613140/0.111589s).
Exact effective-weight/scale reload and identity checks pass. Model checkpoints:

- `NativeUITrainer/focus_ring_runs/spatial135-dtm035/last.pt`, SHA256`b9e5c78508431190fb8804ff255d6c17b6dc1cc10df413e96bbdcc257e4d085a`.
- `NativeUITrainer/focus_ring_runs/spatial135-dtm036/last.pt`, SHA256`7ad9a144c382499843e00bc48980969220baba2d08128474a858662362b979bf`.

`artifacts/ready/protocol.json` pins source/trainer/constraint/scales/cache/model and
membership before fitting. Each run retains execution/result seals and full history;
`artifacts/comparison/report.json` binds both outcomes. Combined output cap2GiB checked.

## Verification and commands

All Python uses resident `.venv-yolo/bin/python` with
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build"`.

- `scripts/spatial135.py --output reports/work/SPATIAL-135/artifacts/audit`:exit0.
- `scripts/train_spatial135.py prepare --ready reports/work/SPATIAL-135/artifacts/ready`:exit0.
- `scripts/train_spatial135.py train --ready reports/work/SPATIAL-135/artifacts/ready --output reports/work/SPATIAL-135/artifacts/comparison`:exit0.
- Six focused suites (`test_train_spatial135`, `test_spatial135`, `test_retention134`, `test_conditioned133`, `test_dual130`, `test_diagnose131`):22pass,0.584s.
- Offline Swift build/test explicit-serial:142tests,exit0. Same project-local cache/config/security/module-cache flags and scoped Vision host context as134. Logs `.build/spatial135-{build,test}.log`. No native source/dependency changes after this pass; final Python extensions have focused integration coverage.

Logs `.build/spatial135-{execution,prepare,training,comparison-tests}.log`; no capture
or external wait time. Fresh source diagnostics and tests, not unchanged corpus rerenders.

## TTR coordination

Published `packets.SPATIAL-135` to the verified
`smb://sillycon.local/SharedStatusFile`, `/Volumes/SharedStatusFile/nuiak/status.yaml`,
at 2026-10-04T20:45:00Z. Duplicate-key-safe YAML readback passed; removing the new
entry reproduces the prior semantic SHA256
`787845593c4e8ffec5ea49c5ffb98220d94f5a542012ae783df0a29e9cd0d82d`.
Other entries and top-level fields were preserved. Followed existing request
`nuiak-20261004-action-negative-coverage` for retained native motion negatives,
not a new broad capture request. Peer acknowledgment of this update is not observed.
Used the shared-status skill's scoped publication/readback protocol; no artifacts
transferred or cleanup performed.

## Next substantial tranche

Review/admit only defensible retained transition labels, separating screen transitions,
same-screen focus moves and uncertain states. One targeted representation comparison
can then test cross-family replay retention with these explicitly exposed roles;
preserve genuinely separate final groups. Seek existing native same-focus/nonidentical
content-motion examples through the already-open TTR negative-coverage request,
not a broad screenshot sweep or more algebraic identity negatives. If none exist,
record the exact missing semantic cells before a separately scoped acquisition.
Body-geometry conflicts remain separate from change-only work. Goal remains active.
