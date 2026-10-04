# COVERAGE-70 — batched comparisons complete, transfer not solved

Both predeclared600epoch comparisons ran through train_focus_ring_detector.py,
transition-direct-pixels arm, exact ready/{broad,compressed}/protocol.json and
approval.json, names coverage70-dtm014/coverage70-dtm015. Exit0; no new capture,
admission, export or promotion. Original32train/5development roles unchanged.

| Model | Own augmentation bank joint fit | Original training joint fit | Settings change | Settings paired boxes |
|---|---:|---:|---:|---:|
| DTM013 reference | not trained on these banks |32/32|5/5|0/5|
| DTM014 broad |120/120|32/32|5/5|0/5|
| DTM015 compressed |152/152|32/32|4/5|0/5|

Compressed training provides24right-side half-width thin-row endpoints, versus zero
in broad training. This added support alone did not solve exposed Settings transfer.
Black fill/distortion and discrete view exposure remain limitations. Each candidate
fits its own bank, not the other bank: DTM01432/152compressed paired boxes;
DTM01532/120broad. No generalization or final evaluation claim.

One native intake21.234s + bank construction10.872s; total preparation32.757s.
Warm verification/loading0.198/0.183s. Run wrappers11.513/11.668s including
intake0.384/0.387s and fit10.988/11.146s. Approximately1.4MiB outputs each,
well below combined2GiB cap. PIDs/hashes recorded in ExperimentLog.

Shared evaluator:1,827 probe scores,222 duplicated-frame scores,20 rejected
pair-condition cells, plus816 augmentation-bank scores. Total16.861s. Recorded
intake0.183s, shared encoding9.408s and forward/decode1.016s exclude additional
bank-scoring time, which remains in total. PNG loading is separately in comparison.
These are stage measurements, not controlled simulator lifecycle speed claims.

Verification:88focused Python tests pass3.565s; offline Swift build/test pass,
14XCTest+120Swift Testing. Actual image-only CLI parity passes both candidates;
reference baseline and candidate development predictions match retained results.
Logs .build/coverage70-*; results comparison.json, preparation.json, cli-parity.json.
Initial launch rejected the combined experiment heading before any training; separate
registered headings repaired it, retaining the failed log. No unsafe retry or new arm.

Software verified; data remains development-only beyond admitted fitting membership;
offline trainer/evaluator integration verified; live producer not assessed; model
gates not passed. SMB not applicable: no new producer action. Prior changes preserved.

Next substantial tranche: CAMPAIGN-71 reusable campaign journal, incremental intake
and model-independent preprocessing cache identities. Then a separately authorized
native coverage campaign, not unchanged epochs on these exposed examples.
