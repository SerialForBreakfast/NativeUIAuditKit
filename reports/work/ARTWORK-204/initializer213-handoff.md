# Run022 native reserve baseline — October 6

Executed the unchanged initializer once through existing prediction export on36
reserved frames, MPS/640/degenerate filtering, exit0 in5.294seconds. Every returned
image identity, label hash, model hash and prediction record validated. No training,
threshold tuning, evaluation-role change or promotion.
Source: `scripts/baseline213.py`; raw results `artifacts/initializer213-baseline01`.

| Partition | ImageView support | TP / FP / FN at0.25 | ImageView AP50 |
|---|---:|---|---:|
| Content validation |120|50 /0 /70|0.64616|
| Abstract diagnostic |60|20 /0 /40|0.35000|

Other supported classes remain in the full report; unsupported classes are unavailable.
For example, collectionItem TP114/120validation and40/60diagnostic. Thus the new
training comparison has substantial image-view recall room, but must also preserve
containers and other controls. This single-template, content-separated diagnostic
does not establish generalization to unseen apps, DS-G8 or tvOS focus.

Local MPS baseline is an absolute diagnostic, not a matched CUDA arm. Primary causal
comparison remains worker029vs030, with pinned versions and fixed-last checkpoints.
Do not interpret cross-backend differences as training gains without qualification.
No further baseline rerun requested. Worker receipt/start13:18UTCmatches exact bundle
and parent hashes; its seven tests and processstart remain peer evidence until return.

Five local focused tests cover cost arithmetic/bounds and baseline collision,
checkpoint mismatch, timeout preservation/no retry. Real inference itself exercises
the positive entrypoint. Existing full offline Swift checks pass; all unrelated edits
preserved. Next: verify worker returned source/config/572slots/89updates and checkpoints,
independently score both arms and return concrete per-class failures and next decision.

Final offline build/test exit0 (140Swift Testing+14XCTest), logs
`.build/baseline213-build.log` and `.build/baseline213-test.log`.
Receipt/start acknowledgment published and read back:
`nuiak/responses/nuiak-20261006-worker213-start-ack02.json`,1575bytes,
SHA256 `7e8b29929d95627a71d90e8f79562b830c200ce61941fd8c26b6b514fe8d4758`.
No worker terminal return observed at handoff. No new polling service established.
