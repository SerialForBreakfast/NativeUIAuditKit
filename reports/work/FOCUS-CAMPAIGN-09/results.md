# Reviewed artwork comparison — no model improvement

October1,2026. **The added-data model learned all12new crops, but did not improve
the unchanged real-screen evaluation.** PreserveFDR021; neither new run produced
an eligible checkpoint. No export, promotion or repeat run.

## Matched outcome

Both new models trained100updates with identical initialization, evaluation,
architecture and optimizer. Only training membership and its prescribed fixture
weight redistribution differed. These are development-exposed screens, not an
independent release test. Numbers below are terminal diagnostics, not selected models.

| Model | Training controls | Focused artwork found | False positives | Complete screens correct | Retention |
| --- | ---: | ---: | ---: | ---: | ---: |
| RetainedFDR021 reference | 1550 | 2/12 | 3 | 12/14 | 18/18 |
| FDR031 matched control | 1550 | 3/12 | 24 | 12/14 | 18/18 |
| FDR032 plus six pairs | 1562 | 3/12 | 25 | 12/14 | 18/18 |

Both new runs found17/27focused development controls. Buttons3/3, tabs2/3, rows7/7,
other2/2 stayed unchanged. Each ended with one multiple-focus and one no-focus
complete screen. Partial/unavailable screens are not silently counted correct.
At all ten common evaluation updates, additions never improved artwork hits;
at update40 they reduced hits3→2. Some early false-positive changes vary, but no
evaluation passes the predeclared gate. Terminal changes fix one false positive
and introduce two. No post-hoc checkpoint or threshold selection.

## What this establishes

The data reached the model. All12new training controls are confidently correct:
focused scores0.99975–1.0; unfocused0.0000154–0.0003746. Their annotations and
production crops are not the remaining blocker for this experiment. Learning
these particular synthetic examples did not transfer to the real artwork cases.

This does **not** establish that synthetic data cannot work, nor distinguish data
diversity from weighting or representation as the sole cause. Six pairs contain
only three designs on one shared layout family and contribute0.695%of training
weight. Scaling near-identical pairs is not demonstrated to help.

## Verified execution

- FDR031 PID95644:242.687seconds; FDR032 PID95905:243.741seconds;100updates each.
  Both hit the update cap, not the time cap. No interrupted/partial comparison.
-12new prefix encodings in1.83seconds;1883existing values reused. Frozen prefix
  identity matched. Both tails changed; batch normalization remained unchanged.
- All20saved evaluations replay exactly from retained predictions. Identical initial
  predictions; byte-identical315development+18retention memberships.
- Post-review312/312crop hashes match pre-review output. Six reviewed screens,
  156controls, zero corrections. Explicit maintainer development-training admission;
  original producer calibration manifests untouched.
-42focused Python tests pass. Actual CLI preflights pass for both arms; six negative
  CLI cases reject missing/wrong approval, wrong output, changed seal/config and
  changed cache membership. Offline Swift build has no warnings;134tests pass.
- New corpus/cache/run artifacts total266,273,165bytes; model execution+encoding
  approximately488.26seconds, below2GiB/1800seconds. No download or device operation.

Evidence: [analysis](analysis.json), [admission](training-admission.md),
`artifacts/cli-negative-checks-complete.json`, `artifacts/output-budget.json`,
`comparison-tests-final.log`, `comparison-swift-build.log`, `comparison-swift-test.log`.
Reproduce retained metric replay with:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python reports/work/FOCUS-CAMPAIGN-09/analyze.py --output reports/work/FOCUS-CAMPAIGN-09/artifacts/analysis-replay.json
```

The analysis writer refuses to overwrite existing evidence; preserve or choose a
new output when intentionally rerunning. Do not rerun training for metric replay.

## Next meaningful work

1. Inspect the remaining42case delivery for genuinely new artwork/contrast/layout
   coverage before admitting it. TTR owns its current timeout/cleanup repair;
   neither new human redraws nor recapture of these accepted six is needed.
2. Before another model run, specify which transfer limitation the new data or
   representation addresses. More samples of the same three designs is not a
   demonstrated fix. Any weighting experiment must be explicit and separately
   compared, not quietly mixed into data expansion.
3. Separate existing Settings follow-up remains ready for seven endpoint reviews;
   it does not block artwork work and does not require another neural model.

Outcomes: software **passed**, exact data admission **passed**, retained bundle
integration **passed**, model improvement gate **failed**. FDR021 remains unchanged.
