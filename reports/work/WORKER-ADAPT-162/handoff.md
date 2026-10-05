# WORKER-ADAPT-162 — three fixed comparisons complete

October4,2026. DTM055/056/057 initialize independently verified worker050/051/052.
Same668admitted rows,120epochs,Adam1e-4,batch16,seed42,CPU2threads,fixed-last.
No new labels, private transfer, capture, export or production replacement.

| Result | DTM055 | DTM056 | DTM057 |
| --- | ---: | ---: | ---: |
| Training correct /668 |661|667|646|
| Reversed correct /668 |661|667|643|
| Global appearance correct /226 |226|226|226|
| Left appearance correct /226 |226|226|193|
| Center appearance correct /226 |34|19|37|
| Center false changes |25|81|176|
| Center abstentions |167|126|13|

Parents scored226/226,180/226,158/226on center diagnostics. Adaptation improves
native training fit but loses local appearance robustness. These are retained,
exposed diagnostics, not an independent accuracy estimate. No candidate qualifies.
EarlierDTM054fit668/668and center207/226is a useful comparison, not production proof.

Evidence: `artifacts/result.json` links sealed per-run result, initializer hashes,
checkpoint hashes, config, training hashes, history, source pins and probabilities.
Process70701completed all three; total run times135.609/136.041/133.908seconds.
Checkpoint CPU replay bit-identical; non-change weights frozen by existing trainer.
Focused combined Python tests59pass, including native decoded-edge regression;
unchanged integrated Swift build/test evidence remains native159's offline pass.

Outcomes: software verified; existing training membership eligible; worker-to-local
PyTorch integration qualified; model gates failed. No claim of CoreML qualification.

Next substantial comparison should test preserving robust features while adapting,
after Big Dog's eight-mask diagnostic distinguishes where invariance fails. First
freeze a hypothesis and acceptance contract; do not automatically extend epochs or
admit counterfactual local patches as native labels. TTR's matched native same-focus
appearance evidence remains a complementary source, not a prerequisite for diagnostics.
