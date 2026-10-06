# Representative detector workload delivered — October6

WORKER198-B now has a concrete512-example workload instead of an unspecified input
dependency. Existing ROI196sealed membership and evaluator integrity/label checks were
reused. Selected by stable SHA256(imageID) ordering,512unique decoded crops/93parent
groups,41classes. All are existing training crops; no evaluation/data-role changes.
Source checkpoint is Run022; shipped resources remain unchanged.

New `prepare_worker198.py` packs images, labels, exact lineage, source pins, class map,
configuration and checkpoint. Budget1GiBpayload/2GiBtotal; actual1026regular members,
48,935,785expanded bytes. Archive43,357,068bytes, SHA256
`43902bea4f1b58da932a9e61cf88e172eb293cd8702d0bd4104d13beec04073f`.
All archive entry bytes independently rehashed against the manifest after packing.
Two selection tests pass: ordering stability, unique/exact count, missing/duplicate
membership rejection. Actual build/pack completed exit0; no model import/training.

Published with existing shared_transfer receipt flow to
`nuiak/nuiak-worker198-detector512-v1.tar.gz`; exact shared bytes verified. Worker receipt
pending, so no shared copy cleanup. Local originals stay under ignored
`artifacts/detector512-export01`. Request describes bounded extraction and next action.
Request published/read back at `nuiak/requests/nuiak-20261006-worker198-detector512.json`,
SHA256 `4d7a4ca6f0930d23885b82191286e9be87f2c20087e57843908e275956588589`.
Peer acknowledgment is separate and pending.

Important corrected assumption: local Ultralytics8.4.124 versus worker8.4.173 requires
reconciliation; no silent dependency installation. With `nbs=64`, batch count is not
necessarily optimizer-update count. The worker must instrument accumulation/steps
instead of copying the tiny-head audit's64/32update arithmetic. No timing or model
gain is claimed by packaging.

The668focus input path includes GLOBAL146's explicit `external_transfer:false`.
That path was not exported. Do not replace the requested512distinct workload by
repeats of the existing108public procedural tensors. This parallel iOS benchmark
does not displace native tvOS focus priority. Benchmark execution still needs its
reviewed backend/preprocessing/parity contract.

Superseding verification: VISION209 subsequently passed the full serial suite with
no exclusions. After the contract correction,20focused Python tests passed in0.946s,
offline Swift native build exit0, and132tests/17suites passed in4.202s (exit0).
Logs: `.build/worker198-correction-build.log` and `.build/worker198-correction-test.log`.
The native build engine is a documented signing workaround, not a permanent policy.

## Receiver feedback closed locally; next worker stage dispatched

Receipt `joe-big-dog-20261006-worker198-detector512-receipt01` verifies exact archive
bytes/hash and512image/label checks. Worker correctly rejected40539244-byte checkpoint
against our32000000-byte member bound. Pixel hashes used shape-prefixed RGB, while
the worker assumed raw RGB; no file corruption was reported.

Published/read back `nuiak/requests/nuiak-20261006-worker198-detector512-correction01.json`,
SHA256 `2334a8986fbe7d123da307380911b1ff8541708372179a1ccae002415d11a25e`.
It permits only the exact initializer exception, supplies an unambiguous hash test
vector, and authorizes a10-minute/256MiB resident8.4.173CPU/CUDA inference smoke on
the first two examples. Full training benchmark awaits instrumented runner review.
No retransmission, dependency install or production change. Shared archive deliberately
retained until corrected intake acknowledgment; receiver owns its local source copy.
Future packer now includes encoding/limits and checks aggregate/member bounds before
publication. The delivered immutable archive was not changed or repacked.

Feedback-loop acceptance is explicit: receiver returns exact intake and compatibility
evidence plus optimizer-cadence runner; NUIAK reviews before timing execution. Routine
status is not a model pass. Software passed; original training membership eligibility
unchanged; worker integration pending; model gates not assessed. No new training yet.

Independent tvOS work remains source-blocked: read-only GitHub lookup for published
TTR550a2d374801fb99120d3aed4168c1de9e7ef83d returned404 through this connection.
That does not prove the commit is absent remotely; local checkout lacks it. Existing
20pair structural intake/40production crops remain inspection-only, not training data.
Next substantial tranche: review worker smoke/runner and execute matched throughput
arms, while resolving exact TTR source semantics for native focus admission. No new
capture or artwork generation is needed for those outcomes.

## Worker correction response reviewed

Received `worker198-correction01-result.json` and runner-proposal-v3 on SMB.
Worker reports1025files/512pixel hashes verified and exact initializer recovered.
Two-example raw output shape2×45×8400 finite; max absolute error0.0022583,
max relative error0.0005180, allclose at declared atol1e-4/rtol1e-3 passes.
Absolute error above atol alone is not a failure: relative term applies. Reported
post-NMS counts/classes match. Runtime1.354s, peak allocation301042688bytes.
These are peer-reported compatibility results; retained source/evidence requested
with runner return for independent review, not yet a locally replayed benchmark.

Cleared version-policy blocker: worker8.4.173is accepted for within-worker timing,
not equivalent to Mac8.4.124. Full runner is not implemented yet. Published/read
back `nuiak/requests/nuiak-20261006-worker198-runner-implementation01.json`, SHA256
`aa45e9fec1653817c93cc93653dec4e1c2429e1449963fa2afb32925296b91d5`.
It resolves warmup/accumulation policy, requires buffer/state restore checks and
records rectangular-batch padding as a potential timing confound. Worker owns
complete source/tests delivery; NUIAK owns executable review and timed-run approval.
No checkpoint promotion or another compatibility smoke requested.

## Executable runner review

Received14regular files/47753expanded bytes from14984-byte archive,
SHA256 `7df983e9e0225fcf0217d3b18fa8c071d88d5db30e37abaf2097ab94d330c9bc`.
No incoming source executed. Static review plus local resident InfiniteDataLoader
reproduction shows numeric cursor restoration does not reset persistent iterator:
warmup[0,1],[2,3], new iter[4,5], reset then[0,1]. Requested resident-version check
and exact-order regression before GPU execution. Also require examples tied to file
inventory and truthful distinction between custom training-kernel and full trainer
timing. Existing end-order assertion would catch the cursor error too late.

Receipt/review published/read back at `nuiak/responses/nuiak-20261006-worker198-runner-review01.json`,
SHA256 `d82d9008445c4c3a15e08912551b705e048195140a5bdb0f4b196d289fa42686`.
Peer cleanup/acknowledgment separate. Missing offline Swift docc dependency does not
block source review of this Python runner or authorize installation. No benchmark
gain claimed. Worker owns concrete corrected-source return, NUIAK owns acceptance.
