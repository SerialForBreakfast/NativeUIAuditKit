# WORKER198-D executable evaluation slice

Removed a NUIAK-owned input blocker while local Run028 trains. New packaging CLI
`scripts/prepare_worker198_eval.py` reuses strict prediction manifests and completed
Run027 readiness verification. No inference or training occurs during packaging.
135fit diagnostic,37page development,413combined retained windows;585total.
All relocated manifests preserve exact content hashes/IDs/bytes; paths and manifest
file hashes change explicitly. Roles remain diagnostic/evaluation, never training.

Package includes the existing exporter, prediction-artifact module, centroid helper,
category map, frozen proposal mapping and verified fixed-last Run027 checkpoint.
Every file and archive member verified. New output; no old input/output overwritten.
Source locations and immutable original manifest refs remain in metadata; worker
must use portable manifest paths, not attempt to resolve Mac paths.

Published/read back archive `nuiak/nuiak-worker198-eval027-v1.tar.gz`,45,130,794bytes,
SHA256 `9c4bc722cbb74c80646eb03b5412123e12560979212d26ded7be66b8b40a6070`.
Assignment `nuiak/requests/nuiak-20261006-worker198-eval027.json`,3,469bytes,
SHA256 `4d37920883329bd66a75544e9f6a9f71cc6faa8d2e93a4cb3a5939e6ac4242ac`.
Peer receipt/start/terminal result are pending, not inferred from publication.
Sender cleanup waits for exact receiver receipt; retain local originals.

Superseding peer observation: exact receipt `worker198-eval027-receipt01.json`
reports copied/verified and bounded extraction at10:27:32UTC;1180members,
50,161,721expanded bytes. File/size/hash match this transaction. Start01 at
10:29:29UTC reports PID155914,matching Run027 hash,resident8.4.173/CUDA12.8,
two threads,nice10 and supplied exporter unchanged. Wrapper sourceSHA256
`e8b9934f4d9889d3ffb732e1f7b9fd9efab12c623fc869ceaa6263d18339c538`.
cuDNN TF32 reports enabled while matmul TF32 is disabled: preserve this in backend
evidence, not presumed parity. This is peer-reported launch, not terminal success.
Receipt clears delivery dependency; shared-copy cleanup remains not performed.

Worker scope: existing exporter API, CUDA0/640 and original degenerate policy;
1800seconds/1GiB, one GPU job, no retry/install/training/threshold tuning. Return
all predictions and failures with environment/source/timing evidence. CUDA8.4.173
is not assumed equivalent to MPS8.4.124. NUIAK retains merged-report acceptance and
fixed-sample backend validation after local GPU becomes free. Reuse dataset with
later verified Run028 checkpoint supplement, not another full transfer.

Verification:3focused packaging tests pass0.020seconds (relocation, changed source,
collision, duplicate paths and archive budgets); actual585member input load and
archive replay pass. Offline Swift build exit0;132tests/17suites pass7.302seconds.
Logs `.build/worker198-eval-{build,test}.log`; `git diff --check` passes.

Outcomes: software verified; data eligibility unchanged and inference-only;
transfer verified but worker integration pending; model gates unassessed.
Next substantial outcome is worker predictions plus matched027/028evaluation,
not another setup benchmark. Native focus source-binding remains independently pending.

## Terminal prediction intake

Return archive1,100,328bytes,SHA256
`23699be642603683901c7900c0fecf1830b45c9d32fedd894e5011c5f967c17b`;
17regular files/5,987,181expanded bytes safely received. Full wrapper/test source
reviewed, never executed. Supplied exporter/dependencies and manifest byte-match.
Independent strict validator passes all135/37/413records against ORIGINAL manifests,
checkpoint,taxonomy,settings,coordinates and degenerate-box accounting;0empty/failed.
Reported execution15.982831seconds, peak allocated382,712,832bytes. Four peer-run
tests retained. No local inference replay, merged quality or backend parity yet.

Wrapper checks budgets after each export, not during a stalled call: request outer
timeout before futureRun028, not a repeat of the successful16secondRun027. Terminal
reuses start identity/timestamp; request distinct completion metadata going forward.
Neither changes the exact validated prediction bytes. Preserve flags/environment for
paired comparison. Exact receipt/acceptance draft:
`reports/coordination/worker198-eval027-acceptance01.json`.
Published/read back `nuiak/responses/nuiak-20261006-worker198-eval027-acceptance01.json`,
2,653bytes,SHA256 `9bca56f37623e4652a4c16628b60cd013aec2871e13f6f1f9d2d5159fca6df8d`.
Peer acknowledgment and cleanup remain separate. No production change.
