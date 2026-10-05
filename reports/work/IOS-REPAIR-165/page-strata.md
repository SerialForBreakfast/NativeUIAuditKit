# Page failure stratification — October5

Joined all96sealed page-report image IDs exactly to the frozen compose155 catalog;
both report seals verified. No inference, pixel changes or new labels. Source
controller places `left=true` at x28points, otherwise horizontally centered.

|Axis, each48 images|016 no candidate|017 no candidate|016 oracle operating hit|017 oracle operating hit|
|---|---:|---:|---:|---:|
|Left|45|48|0|0|
|Centered|15|18|7|18|
|Native UIKit|35|41|0|0|
|Non-native|25|25|7|18|
|Light|35|32|3|8|
|Dark|25|34|4|10|
|Reader footer|28|36|0|9|
|Gallery inspector|32|30|7|9|

Absence means no class candidate at actual export confidence.001. The geometry
analyzer applies no additional threshold for its export population; that does not
mean the exporter used confidence0. Oracle operating hit
means best-IoU exported candidate also satisfies confidence>=.25 and IoU>=.5;
it is not a replacement for confidence-ordered matching. Totals happen to match
the existing operational TP counts7and18. Correlated marginal axes must not be
treated as independent causal estimates or summed together.

Repaired count3/5/7 probes (32each) have21/22/23absences and8/6/4oracle hits.
Seeds7/19 (48each) have30/36absences and8/10hits. Improvement is concentrated in
centered non-native controls, not general renderer/position robustness. Training
coverage, tiny rendered features and learned location priors remain hypotheses.

Next: one explicit higher-resolution inference comparison before spending another
full training campaign. Keep these exposed probes development-only and reserve
new final groups for any subsequent coverage-driven training. Native24 TTR source
is still unavailable locally; existing request remains sufficient, no recapture.
