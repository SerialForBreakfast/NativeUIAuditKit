# FROZEN-ADAPT-164 — matched feature-freeze comparison

Two fixed120epoch experiments completed; no additional sweep. DTM058/059initialize
worker050/051, respectively; existing668admitted rows,Adam1e-4,batch16,seed42,CPU2.
Only existing linear decision layers8/10learn; all convolutions/geometry bit-exact.
Existing trainer extended with explicit checked linearOnly scope, default unchanged.

| Outcome | DTM058 | DTM059 |
| --- | ---: | ---: |
| Training correct /668 |655|659|
| Reversal correct /668 |654|659|
| Region correct /94 |83|89|
| Reviewed native correct /9 |9|9|
| Global/left correct /226 |226/226|226/226|
| Center correct /226 |142|20|
| Center false changes / abstentions |51/33|70/136|

Both fail combined fit and robustness. DTM058center correct count improves over
full-branch055(34→142), but confident false changes also increase25→51. DTM059
is close to056's19correct. Thus feature freezing is not a sufficient solution,
and a single accuracy count would conceal safety-relevant changes in abstention.
All results retained development/training evidence, not independent evaluation.

PID74073; per-run elapsed63.760/60.289seconds. `artifacts/result.json` links sealed
protocols, hashes, membership, source pins, histories, full predictions and fixed-last
weights. Reload replay exact; all frozen state tensors verified bit-identical by
the real training path.55focused Python tests pass including real architecture
freeze/determinism/invalid-scope checks. Swift verification details recorded below.

Fresh Swift build passed. Default test invocation stalled in concurrent Vision/OCR
waits (sample `.build/frozen164-test-sample.txt`); stopped only owned74390/74102after
stack preservation. One existing Vision test passed alone, then full
`swift test --skip-build --skip-update --no-parallel` passed142tests, exit0.
Logs `.build/frozen164-{build,test,vision-isolated,serial-test}.log` retained.
No service reset, test edit, assertion removal or runtime installation. A single
recovery does not establish the precise concurrency root cause. Diff check passed.

Companion: read-only900member iOS geometry comparison at
`../NATIVE-159/geometry-comparison.md` supports testing corrected labels at640before
changing resolution. No data mutation, capture or model launch for that comparison.

Outcomes: Python training software verified; existing data admission unchanged;
local PyTorch integration qualified, no CoreML export; model gates failed.
No Git writes, external/private transfer or production replacement.

Next: worker163spatial evidence plus genuine same-focus appearance controls should
guide a retention-constrained objective or representation comparison, not more epochs.
In parallel, preregister an iOS repaired-versus-prior-corpus training comparison with
identical Run013 initialization and evaluation, since the data fix is now qualified.
