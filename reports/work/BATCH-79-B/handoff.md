# BATCH-79-B — incremental image preparation

Software slice complete; data-role decision and candidate run remain pending. No
capture, inference, training, admission, export, promotion or Git writes. Existing
dirty work and prior banks/protocols preserved; SMB not applicable to this local work.

## Implemented

Existing focus_candidate_ranker.py now accepts --derivatives-only --inputs PATH
--cache-root PATH with --prepare NEW_OUTPUT. Produces inspection derivatives only,
no protocol/approval. Accepts sealed existing candidates or calibration proposals;
the old training-bank loader rejects the resulting inspection manifest.

The same encoder/cache is wired into ordinary preparation through optional
--cache-root. Immutable per-image entries bind original bytes, actual dimensions,
ordered geometry, encoder/pipeline source, production runtime/adapter and NumPy/Pillow.
Roles, labels and model head configuration do not alter pixel derivatives; supervised
membership/admission checks remain separate. Partial/corrupt entries fail closed;
new outputs are exclusive. No overwrite, automatic repair or historical resealing.

## Actual retained-data results

| CLI preparation | Images reused/new | Crop calls | Caller preparation seconds |
|---|---:|---:|---:|
| Cold original bank |0/59|59|10.692|
| Append calibration images |59/24|24|2.113|
| Warm combined inspection |83/0|0|0.344|

Original2141encodings and crop PNG hashes exactly match RANK75's retained bank.
Incremental2337encodings match warm output exactly; unchanged prefix remains exact.
These are preprocessing timings, not simulator or training speedup measurements.
Combined inspection preserves original source records and does not establish a new
training corpus.12native pairs retain calibration roles;77approval remains necessary.
Source images were not regenerated. Cache under .build/batch79-derivatives is disposable
derived storage, not the sole raw-data copy. Arrays/reports retained locally and ignored.

## Verification

- Actual CLI cold/incremental/warm exit0; .build/batch79-{cold,incremental,warm}.log.
- Automated retained-array comparison: verification.json, all equality assertions pass.
-62focused Python tests pass22.610s: test_batch79,test_rank75,test_native77,test_campaign71.
  Generated fixtures cover warm no-call behavior, appended frames, changed geometry/
  dependencies, model-only/role-neutral reuse, changed bytes, corrupt tensors, partial
  entry refusal, invalid dimensions/bounds, runtime change, label-contaminated candidates,
  output collisions and inspection-manifest rejection. Existing admission/journal tests
  retain role/leakage protections. Real Swift crop helper cold/uncached/warm parity passes.
-Offline Swift build succeeds1.71s;14XCTest+120SwiftTesting pass. Logs
  .build/batch79-swift-{build,test}.log. git diff --check passes.
-Artifact policy gap repaired: reports/work NumPy .npy/.npz outputs ignored; no files
  deleted or Git index changed. No package rebuild needed for subsequent prose/ignore edits.

Software verified; existing admitted data unchanged/new inputs inspection-only;
local production crop integration verified, TTR live integration not assessed;
model gates not assessed. Candidate execution is not complete.

Next substantial tranche: after77's exact role decision, materialize44/5admission,
assemble role-bound supervision using retained derivatives and define one controlled
native-transfer comparison. Extend the ranker's old fixed32/5/50frame protocol and
DTM013control membership explicitly; cache availability does not waive those checks.
In parallel, qualify retained rich24when its source is published, then reconcile
missing coverage for one authorized campaign. No recapture or unchanged model rerun.
