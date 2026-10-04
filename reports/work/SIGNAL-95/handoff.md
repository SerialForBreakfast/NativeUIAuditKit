# SIGNAL-95 — resolution evidence and matched-negative coverage

Completed73pair×3resolution diagnostic plus independent source/label coverage audit.
No training, capture, threshold selection, role changes or model replacement.
Prior goal turn was progress; this turn provides evidence changing next collection
and experiment choices. Overall goal remains open.

## What the pixels establish

All96×64encodings match CONTEXT93's saved arrays exactly. The same bilinear/letterbox
convention at192×128and384×256 retains more signal, but also more no-op variation.
Truth-box unions are explicitly diagnostic regions, never prediction inputs.

| Example | Whole-frame absolute difference96→192→384 | Truth-region96→192→384 |
|---|---|---|
| rich wide dark p2(change) |.000678→.000911→.001299|.002134→.003560→.005800|
| rich wide light p2(change) |.000720→.000950→.001325|.002155→.003592→.005847|
| rich compact light p2(change) |.003998→.006052→.006891|.039608→.073175→.086094|
| nostalgex city-light scroll(no-op) |.003370→.004393→.005307|.018799→.029792→.039868|

All48training change pairs remain nonidentical at every resolution. Four of20no-ops
are exactly identical at every resolution. Median training no-op difference rises
.003401→.004422→.005333; changed median.050288→.051545→.052459. Therefore a simple
difference-energy threshold cannot separate the cited difficult cases; this does
not prove that a spatial learned model cannot separate them. Sparse information
survives at96×64; we have not proved a resolution bottleneck or qualified a larger
model. Larger-frame memory/work costs rise4×at192and16×at384before architecture.

## Independent source/label audit

| Training source | Changed | Unchanged |
|---|---:|---:|
| reference |12|12|
| retained negatives |0|8|
| nativeTable |12|0|
| nativeActions |24|0|

All36native positives lack matched native negative coverage in the admitted corpus.
This is a distribution gap, not proof it caused the failures. Five Settings examples
remain exposed development; no role change or invented negative label.

Published/read back `nuiak/status.yaml` packetSIGNAL-95, request
`nuiak-20261004-action-negative-coverage`: align TTR's planned native negatives with
observed boundary/no-op same-focus, changing-content same-focus, and changed identity
with scrolling-stationary boxes. Native brackets/actions/geometry/ancestry required;
unsupported cells stay explicit. Request is a bounded capability/plan request under
producer authority, not a grant of capture or training roles. Unrelated status
preserved by parsed digest; peer acknowledgment pending. Version16source is still
absent from local TTRHEAD50ff7fd8; previous receipt/intake blocker unchanged. No
unchanged runtime retry or alternative remote execution.

## Evidence and verification

Actual CLI `scripts/diagnose_signal95.py --output reports/work/SIGNAL-95/diagnostic-r2`
exit0,10.556s including source verification and decoding,219numeric records. Initial
diagnostic retained separately (8.634s) before adding persisted coverage accounting.
No rendered image tree or repeated simulator setup. Report includes protocol/source
bindings, implementation hash, all rows, group summaries and no-training flags.

12Python tests pass (signal95,change80,temporal68), covering original encoding parity,
sparse-detail preservation, role/source distinctions, malformed dimensions/boxes,
model adaptation parity and previous temporal behavior. Offline Swift build/test
exit0:14XCTest+120SwiftTesting, logs `.build/signal95-{build,test}.log`. Diff check clean.
Only numeric diagnostic artifacts ignored; concise handoff and tests are source.

Next substantial tranche: one predeclared192×128paired-context change-head comparison
using the same68/5roles, DTM018zero-expanded initialization,600epochs/fixed-last,
frozenDTM020boxes and0.85confidence, comparing DTM022and retainedDTM018. Require
old44/no-op confident retention and correction of the native p2misses; no threshold
tuning or automatic follow-up. Combine with source-backed layout28compatibility if
version16arrives; otherwise local experiment is independent. Preserve received data
and existing shared receipt; no new capture required for the local comparison.

Software verified; data eligibility unchanged; local encoding integration verified;
new producer integration blocked on source; model gates not assessed. No production
claim, and no justification yet for a large corpus sweep or longer unchanged run.
