# POOL167 — controlled comparison complete; candidate rejected

One preregistered DTM060candidate, same DTΜ049initializer/668admitted rows/120epochs/
Adam1e-4/batch16/seed42/CPU2threads/uniform weights as retainedDTM054. Global spatial
mean broadcast4×6 replaces adaptive4×6; parameter count/shapes unchanged but spatial
functional capacity reduced. No new labels or private transfer. Exact control
data/config/initializer pins verified; retained control predictions reproduced.

PID82148completed120epochs in147.237training seconds; total181.968s. Explicit
pooling-tagged checkpoint reload passes, geometry unchanged. Seven focused tests
and offline Swift build/serialized tests pass. Logs `.build/pool167*`; full sealed
results/protocol at `NativeUITrainer/focus_ring_runs/pool167-dtm060/`.

| Measure | DTM054 control | DTM060 global pooling |
| --- | ---: | ---: |
| Full admitted fit |668/668|610/668|
| Reversal fit |668/668|601/668|
| Original108 retention |108/108|61/108|
| Region94 retention |94/94|84/94|
| Reviewed native9 |9/9|9/9|
| Local center unchanged/changed/abstain |207/6/13|39/0/187|
| Public bottom unchanged/changed/abstain |0/176/2|151/0/27|

Decision: reject replacement. Appearance alarms fall, but many cases become
abstentions and real-transition fit regresses. This does not prove pooling caused
every prior failure or that longer training cannot fit; it rejects this fixed
budget/initialization candidate. Counterfactual diagnostics remain distinct from
native performance. No automatic retry, new admission, export or promotion.

Software verified; existing data roles preserved; local checkpoint integration
verified; model retention gate failed. Production/TTR models unchanged.

Next substantial tranche: preserve spatial detail in a bounded representation
diagnostic, test separation of appearance-only versus real-focus changes using
existing admitted native cases, then preregister one matched alternative. Do not
train on ambiguous localized controls. Complete IOS165and compare both fixed-last
candidates in parallel; its settings/source remain untouched by this experiment.
