# PER-02 chevron-and-dialog benchmark

`scripts/perception_benchmark.py` is the integrated entry point:

```sh
.venv-yolo/bin/python scripts/perception_benchmark.py \
  --manifest <perception-benchmark.json> \
  --predictions <perception-predictions.json> \
  --output reports/work/PER-02/report.json
```

It validates the PER-01 manifest before scoring, accepts an explicitly unavailable adapter
without inventing empty predictions, and scores actual proposals separately from oracle-box
component behavior. The report separates localization, row association, end-to-end disclosure
recall, decorative-arrow false positives, abstentions, dialog/button/focus errors, and the
safety-critical destructive-as-benign count. It recommends no training when eligible physical
benchmark evidence or assigned inference is absent; a measured gap can only request review with
held-out support, latency budget, and numeric gates supplied before training.

Verification: `scripts/test_perception_benchmark.py` covers exact and wrong-row proposals,
destructive dialog misclassification, stale focus, prediction-derived labels, malformed
relations, duplicate-content leakage, incomplete predictions, missing/changed evidence bytes,
successful CLI execution, and output collisions (5 passed).

| Outcome | Status |
|---|---|
| Software verified | Passed (offline, deterministic) |
| Data eligible | Not assessed; inventory has no reviewed benchmark members |
| Integration qualified | Not assessed; shipped/TTR prediction adapters were not assigned |
| Model gate passed | Not applicable; no training recommendation is justified |

Next unblocked action: provide reviewed, partitioned benchmark entries and a separately assigned
prediction adapter; do not train from the current unreviewed capture inventory.
