# LOCALIZE-69 — missing joint geometry support, shared encoding verified

FrozenDTM012/013, unchanged32training/5development. No training/capture/role changes.

## Diagnosis

Actual training labels have only three width×height combinations in96×64input space:
11.08×20.50(24endpoints),76.05×4.05(24),16.49×16.49(16). Settings is~39×3.45–4.12.
Marginal width/height ranges obscure this missing joint combination.
Training centerx15.78–48.23; Settings72.35–72.61. Old±4%translation support still
ends near52.1. All10Settings horizontal centers,7vertical centers and5heights lie
outside unaugmented training ranges. This suggests a coverage/extrapolation problem,
not proof of causality or evidence that resolution never matters.

DTM013Settings mean absolute input-pixel errors: center20.61horizontal/3.76vertical,
extent21.71width/12.40height. Correct grid cells0/10,localized endpoints0/10,invalid2/10.
Scoring-only substitutions of the true center, extents or grid cell each still
localize0/10. Failure involves both placement and geometry; clipping would not fix it.
DTM012also has0/10correct cells/localized endpoints,invalid1/10. Training64/64endpoint
localization remains correct for both models. No labels were changed or used in
prediction; oracle substitutions are diagnostic only.

## Efficiency and parity

The existing evaluator now encodes each pair/condition once for both models.
Internal `infer_encoded` shares the same decoder/decision contract as image-only
`infer`; `raw_image_box` permits error inspection without admitting invalid boxes.
Memory stays bounded to one current pair/condition, not a whole image corpus.

All1,218shift predictions and148counterfactual predictions reproduce the retained
TEMPORAL-68report;20rejected cells match. Both real image-only CLI outputs also match.
No stored training protocol was rewritten to current code. Frozen replay performed
fresh native intake; training cache pins still reject changed code.

| Stage | Seconds |
|---|---:|
| Fresh native intake |19.115|
| PNG decoding |2.985|
| Shared encoding/resize |9.489|
| Forward/input validation/box decode |0.681|
| Total including diagnostics and other overhead |35.232|

Post-intake16.117sversus prior25.592stotal with warm intake. Differing scopes and
host conditions mean this is not a controlled speed benchmark. Encoding dominates
forward computation, consistent with the smaller model not reducing pair latency.

## Verification and evidence

Actual command,exit0:
`scripts/evaluate_data67.py --candidate
NativeUITrainer/focus_ring_runs/temporal68-dtm013/result.json --output
reports/work/LOCALIZE-69/replay.json --temporal --localization-replay
reports/work/TEMPORAL-68/comparison.json`.

Both `focus_direct_transition.py --request
reports/work/TEMPORAL-68/prediction-request.json --model <retained checkpoint>
--output reports/work/LOCALIZE-69/<model>-cli.json` invocations exited0 and pass
stored prediction parity; no expensive corpus rebuild was required for these checks.

Artifacts: `replay.json` (all errors/oracles/stage times), `coverage.json` (joint
support), `cli-parity.json`, `provenance.json` (current inference code/runtime pins,
separate from untouched historical training protocols). Generated payloads stay local.
84focused Python tests pass4.598s. Offline Swift build/test exit0,
14XCTest+120Swift Testing. Logs`.build/localize69-*`;`git diff --check`passes.
Tests reject invalid encoding/dtypes/ranges/sizes, verify raw invalid boxes remain
rejected, geometry diagnostics don't affect predictions, and legacy behavior persists.
Prior dirty work preserved; no Git writes, external mutations or deleted evidence.

Software verified;data roles unchanged;offline inference/CLI integration verified;
production model gates still not passed. SMB not applicable: this does not change
the producer's existing requested capability or authorize a capture campaign.

## Next substantial tranche

COVERAGE-70: two predeclared600epoch augmentation arms, broader translations versus
horizontal compression plus the same translations, sameDTM013architecture and32/5
roles. Validate once, prepare both banks and batch evaluation. This tests missing
right-side half-width geometry explicitly rather than blindly adding pixels/epochs.
Report rejected views, joint coverage, exposure and black-fill/distortion limitations.
No capture or independent evaluation claim; native no-scroll positives and genuinely
independent real-UI qualification remain required. Overall goal remains incomplete.
