# FDR014 — controlled appearance-sampling experiment

2026-09-29. User: “Ok try that” after diagnosis of FDR013 sampling imbalance.
Authorized: implement/test sampler correction and one bounded training/comparison.
No new data, capture, threshold changes, export, promotion or automatic rerun.

Keep all FDR013 samples, selection guards/weights, FDR007 initialization, fresh
optimizer,30epochs,batch64,lr0.0003,seed42,noaugmentation,MPS and1800s cap unchanged.
Change training sampling only: buttons/tabs/artwork/rows each25%, each label50%
within a stratum, uniform examples within each stratum/label. This intentionally
replaces50/50native–Fixture; native Settings no longer has a guaranteed50% share.

Derive appearance from hash-bound retained Fixture recipe presentation. Flat tabs
and parentless nested tabs are tabs; nested child buttons remain buttons. Native
OS Settings rows are rows; fallback control mapping covers button, collection/image,
row/toggle controls. Reject unclassified members, conflicting pair strata and any
evaluation row in sampling. Public taxonomy and labels remain unchanged.

Add a versioned sampler experiment adapter, retaining legacy policy behavior.
Pin membership mapping and actual training probabilities; verify deterministic
WeightedRandomSampler draws at seed42 over30epochs before launch. Preserve all
453real selection crops/64exclusions and9retention pairs. Run unit/real caller
checks and offline Swift build/test, log FDR014 before execution. Evaluate selected
checkpoint only if eligible; otherwise replay stored epoch predictions and diagnose.
Compare with FDR013 under the same backend/configuration; do not call reused real
selection evidence independent qualification.

Outcome 2026-09-29: implemented and executed once as FDR014. Actual sampling
verified; all30epochs completed, no eligible checkpoint. Rebalancing alone did not
solve real-screen transfer. See reports/work/FDR-014/results.md for controlled
comparison, guard replay and the contrast/geometry audit next assignment.
