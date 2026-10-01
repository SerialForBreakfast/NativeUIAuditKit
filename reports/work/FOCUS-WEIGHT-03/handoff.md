# FDR023 weight-control result and approval-policy proposal

October 1, 2026. **Comparison completed; candidate rejected. Keep FDR021.**

| Fixed 0.85 metric | FDR021 selected775 | FDR022 terminal (no selection) | FDR023 selected275 |
|---|---:|---:|---:|
| Focused hits /27 |16|15|13|
| False positives /288 |3|6|2|
| Unique-correct complete frames /14 |12|10|10|
| Artwork hits /12 |2|2|1|
| Retention correct /18 |18|18|18|

FDR023 has four no-focus frames, zero wrong/multiple selections. Tabs regress2/3→1/3
and rows7/7→6/7; buttons3/3and other2/2unchanged. It passes the older checkpoint
selection guards but fails the stricter predeclared comparison against FDR021.
All40evaluation snapshots were replayed exactly using the existing metric code.
No snapshot exceeds2artwork hits. Terminal1000is not a substitute selected candidate:
TP15,FP5,unique10,multiple1. [Full comparison](comparison.json).

This isolates the changed weighting policy on identical1550training/333evaluation
membership, initialization and frozen feature caches. Initial predictions exactly
match FDR022. ReducedFPdoes not compensate for missed focus. The weighting confound
is repaired, but that alone does not solve real-screen transfer. This does not prove
that a particular replacement architecture will succeed.

## Execution evidence

User explicitly approved the one-run request; [authorization](authorization.md) and
[bound approval](approval.json). Protocol:
`438ceeeeb1eeb6c0627f49da19a01febafb62e5559d0b6c85a51718d23fb2767`.
No context features, encoding, downloads, threshold changes or protected tests.

Initial restricted PID65333passed input validation but could not access MPS;
zero updates/checkpoints, only preflight.json. Its directory is preserved under
`startup-blocked/`, with `execution.log` and [receipt](execution-receipt.json).
Scoped host probe confirmed MPS availability. Same approved protocol then ran as
PID65517with remaining470second outer allowance; exit0,152.902seconds total,
31.301training seconds. Combined invocation time274.871seconds remains below600.
No CPU fallback, scientific retry, service change or source-data deletion.

[MPS execution receipt](mps-execution-receipt.json), log `mps-execution.log`.
Output: `NativeUITrainer/focus_ring_runs/fdr023-weight-continuity`.
1000updates, update cap, fitPassed=false,17eligible snapshots; selected275.
Best checkpoint SHA256:
`a533cc21265c39e786aa0c05d2fcb6798abbe4ae246e5e2abc78310ecf820c22`.
Last checkpoint SHA256:
`ebecd6f91ebc9acf4f189f32c6e46823e2c99db69451ef15365de3dfb66c8dfb`.
Neither is exported or promoted.

Software: existing verified trainer/metrics used, no implementation changes or new
build required. Data: same admitted membership/cache hashes validated. Integration:
actual MPS cache join and weighting execution passed. Model comparison: failed.
Coordination: not applicable; no TTR action changes.

## Approval friction and next step

The extra confirmation was imposed by the repository's separately approved-run
rule, not by the cost or technical risk of this small fit. Recommend one approval
for a bounded local experiment tranche instead of each launch: proposed maximum
three justified comparisons, five training minutes each, thirty minutes total,
using agreed data/gates. External access, paid compute, scope changes and releases
stay separate. [Proposed policy](../../../Research/Plans/LocalExperimentApprovalEnvelope.md).
“Maybe we should loosen” is not interpreted as blanket standing authorization;
AGENTS.md and the approval checks are unchanged.

Next meaningful model work: specify and compare the growth-preserving context-fusion
representation against FDR021 on identical membership/source budgets, including
detector-box sensitivity. Prepared scene/mask inputs already exist; no new manual
annotation or TTR build is needed to start that design. Do not repeat this head fit.
