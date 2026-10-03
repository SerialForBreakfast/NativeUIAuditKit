# FOCUS-AUGMENTATION-47 — completed

## Outcome

Position variation fixes the measured alignment failure and improves real artwork
transfer. It does not supply the missing row, button, tab and scene coverage.
Translation-only is the better next experimental baseline; scale variation increases
wrong real detections enough to outweigh its one additional matched target.

| Fixed metric | FSF001 baseline | FSF003 position | FSF004 position + size |
|---|---:|---:|---:|
| Exact synthetic development screens | 425/500 | 500/500 | 500/500 |
| Both frames of pair correct | 175/250 | 250/250 | 250/250 |
| Synthetic extra detections | 0 | 0 | 0 |
| Native panel, ordinary640 target located | 15/18 | 18/18 | 18/18 |
| Native panel, unaligned top/bottom | 0/18 each | 18/18 each | 18/18 each |
| Native panel,1280 target located | 0/18 | 1/18 | 6/18 |
| Reference panel, ordinary640 | 0/12 | 0/12 | 0/12 |
| Real target located | 1/46 | 8/46 | 9/46 |
| Detections on reviewed unfocused real controls | 46 | 19 | 68 |
| Unreviewed predictions on partial real frames | 11 | 1 | 14 |
| Correct selection on complete real screens | 0/7 | 0/7 | 0/7 |

Target localization uses IoU≥.50 and confidence≥.25. It is not equivalent to a
unique correct selection: FSF004's bottom-padding case includes one multiple-selection
screen; its1280results include19known-negative detections and only one clean focus
selection. All seven complete real screens still return no focus in both new arms.
Partial-frame unknown geometry remains separate from known wrong detections.

Real gains are confined to collectionItems:8/21and9/21. Both models still miss all
16listRows,4primaryButtons,3tabItems and2otherFocusable targets. Reference guide/catalog
full-body matches remain0/12in every tested variant. Training recipes originally offer
only eight focused-body sizes at640; more artwork alone does not broaden geometry.

## Controlled comparison and implementation

- Same original initializer, seed42,2,000training images,500development images,
  batch8,640px and one epoch; fixed-last checkpoints, no threshold fitting.
- FSF003 translate=.05/scale=0; FSF004 translate=.05/scale=.20. Other augmentation
  remains zero. Contract validation rejects unknown, invalid or out-of-range options.
- Both process250batches and31optimizer updates. Baseline has the same nominal
  exposure/schedule but lacks direct optimizer-update instrumentation.
- Actual loader uses square inputs (`rect=False`), including the historical baseline.
  Saved trainer `rect=True` did not describe the custom dataset's effective behavior.
- Actual resident transform tests cover pixel/box movement, scale and clipping;
  training-only64-frame probes in each arm retained all labels, with no boundary touches.
  That sample does not claim every possible random transform is unclipped.
- Original USB images are read directly. Compact contracts, weights and logs stay local.
  Existing train/evaluation separation and terminal-only evaluation remain enforced.

## Timing and verification

FSF003 PID84183:245.94s fitting,46.22s terminal evaluation,519.47s including parent
validation/execution. FSF004 PID84577:248.16s fitting,46.12s evaluation,519.76s total.
Each arm's peak observed output is about45MiB. Follow-up PID84853:512inferences in
21.90s, covering30images×7variants×2models plus46real images×2models.

All1,500terminal rows (baseline plus two runs) are rescored and pair membership checked.
All512follow-up rows reproduce their scores and aggregate report; transformed geometry
is reconstructed independently.77Python test executions pass (some inherited runner
tests execute in more than one suite), plus offline Swift build and134Swift tests.
The tranche remains below its2GiB output cap. No image-copy staging was needed.

Evidence:

- [Contracts and source pins](contracts/sources.json), [authority](contracts/authority.json)
- [Terminal comparison and geometry inventory](terminal-comparison.json)
- [Follow-up protocol](comparison/protocol.json), [results](comparison/summary.json)
- [Replay result](comparison-replay.log), [real training-loader probe](loader-probe.json)
- [First execution](translation-execution.json), [second execution](translation-scale-execution.json)
- `*-tests.log`, `swift-build.log`, `swift-test.log` in this directory.

These are one-seed comparisons on previously exposed development/calibration data.
They establish an actionable improvement on these inputs, not universal accuracy or
an independent benchmark. Both checkpoints remain experimental; production is unchanged.
Coordination is not applicable: this tranche changes local training and evaluation,
with no new producer contract or runtime request.

## Next substantial tranche

1. Qualify current TTR export and the retained native-button/grid-density plans;
   inspect actual widget families and prioritize missing shapes, sizes and layouts.
2. Define exact diverse training membership and whole-family holdouts, paired-content
   focus transitions and bright/dark unfocused distractors. Obtain any required new
   capture/admission scope together; existing61reference images retain calibration roles.
3. Ingest the approved batch, run a matched FSF003 translation-only data comparison,
   and score unchanged synthetic, real and reference challenges. Produce one grouped
   failure review driven by wrong selections and misses.

Broader native-family coverage comes before a scale sweep or longer unchanged fitting.
Annotation remains an exception-driven check, consistent with the maintainer's clean
reviews. Independent true generalization requires future untouched app/layout families.
