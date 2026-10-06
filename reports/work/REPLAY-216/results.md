# REPLAY216 — independent return acceptance

October6. Execution accepted as an experiment; candidate promotion rejected.
Received78,665,144bytes, SHA256
c449fcdfd47ff239da6fecaf9d84a417167967422c51660d1028bf0af2f317d6.
All51regular archive members fit the assigned bounds;113,294,488expanded bytes.
Raw return preserved at `artifacts/return01/payload`; no peer source executed.

Source review: wrapper matches start pins; prior213adapter unchanged. Trainer diff
only introduces original-source-ID validation selection rather than taking first512
enlarged slots. Independently verified both validation-order files against the frozen
resident512IDs. Same optimizer, initialization, square640/no-shuffle/no-augmentation,
fresh state and existing inference export. Start request-name typo retains explicit
canonical correction without source mutation or restart.

Both arms have10epochs,393batches/epoch,245continuous accumulation updates; reported
training durations1179.433/1191.432seconds. Records are consistent with the contract;
they are remote execution evidence, not locally observed GPU execution. All1242
prediction records independently pass model/corpus/settings/hash checks.

| Measurement | Control031 | Treatment032 | Existing reference |
|---|---:|---:|---:|
| Native validation imageView TP/120 |42|87|—|
| Combined raw-ROI label TP / FP |383 /545|406 /354|—|
| Fit progressView TP/124 |34|25|—|
| Composed fit page TP / FP |216 /4|216 /4|216 /4|
| Composed development page TP / FP |74 /4|74 /4|75 /4|
| Composed retained page TP / FP |528 /9|530 /15|543 /7|

Composition keeps022fullframe,028refinement and211aliases fixed, varying only the
extra-ROI donor. All non-page detections/metrics unchanged. Treatment gains two
retained matches versus control but adds six false positives; neither beats the
reference. Fit pass is not retention qualification. RawROI native improvements
must not conceal these consumer-level regressions.

Case diagnosis reconciles all ten raw reports: large-label matches lose80/gain103;
thin progress-view targets lose12/gain3; fit menuButton loses9/gains0. Do not call
this a pure small-object problem. Five fit training overlaps remain diagnostic.

Artifacts SHA256:

- training-review01.json:9ffa7c8a8be48fc679e71168ed8c8cd6777c1594ed72ca7becac5310c38ab03a
- paired01.json:c8fc23cc093a7abd374f17ea7de9e33b1e02ba65a568831e32d15517d1fb7f22
- composition01.json:5476b5ac655dbe58505b8477694112f2bb439c05107f9d89c8b97a68e11daf4b
- case-diagnosis01.json:31cdcb9daa3ebf9e961ca7e5a8a7ad8ad7e99d191463a30808bec4d7203ccba2

The6.8MB/114431node training log legitimately exceeded generic inventory limits.
Explicit216-only8MiB/150000node budgets preserve default4MiB/100000nodes, depth32,
duplicate-key and nonfinite rejection; status parser unchanged. Reviewer recognizes
the actual control/last.pt and treatment/last.pt paths without rewriting raw evidence.
59focused tests pass; integrated offline Swift checks recorded below.

Next substantial tranche: design one matched whole-model retention comparison
incorporating the audited189fullframes (40supported classes), preserving fixed
native/reserved membership and consumer evaluation. No automatic retry/extraepochs.
tvOS source-binding work remains independent and higher priority when qualified.

Offline Swift build and140Swift Testing+14XCTest pass (`.build/return216-*`).
Exact return receipt and independent findings published/read back at
`nuiak/responses/nuiak-20261006-worker216-acceptance.json`; peer acknowledgment and
sender cleanup pending. No peer files deleted; local checkpoint originals retained.
