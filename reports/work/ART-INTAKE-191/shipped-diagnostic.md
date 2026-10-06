# Shipped FocusRing on retained ART191 pairs — inspection only

October6. All20structurally reviewed pairs/40frames scored via the actual
`ttr_focus_manifest.py --review-schema4-subset --review-model` entrypoint.
No fabricated training manifest or admitted labels. Actual runtime uses CPU-only
CoreML, per-endpoint visible-body bounds, production16%expansion/256×256crop.

Shipped artifact SHA256:
`9e5ba294e545b4ae0c54aa5d483b1a1f681b6c30477882700b4dbe139b9c66b7`.
Scores: `artifacts/schema4-shipped-diagnostic01/review-scores.json`, SHA256
`d4a3f7b0f8acb9b37d3ae90f71c1d269a03535349318ad2164a5a7cb700384b3`.
Model, runtime and full inspected membership rechecked after scoring.

Only8/20pairs have positive focused-minus-unfocused probability; the range is
−0.82305909 to+0.4140625. This is not accuracy or a quality gate: roles are
producer-reported pending source qualification,18pairs have clipped focused bodies,
and these selected cases are not a representative independent evaluation set.
No threshold was selected/tuned. The three largest reversals are identified in
`reports/coordination/art191-shipped-diagnostic.json` for retained-case investigation.

Further stratification of the same cached scores (no inference rerun): the two
unclipped pairs are streaming-catalog-dark(1.0focused/1.0unfocused) and
streaming-catalog-light(0.8378906/0.81640625). Thus clipping alone cannot explain
poor separation; this does not identify its causal source. At the existing0.85
comparison threshold,8/20reported-focused and8/20reported-unfocused endpoints
exceed the threshold. The existing0.70–0.85ambiguity band contains1focused and
2unfocused endpoints. These are descriptive counts, not trustworthy recall/FPR.
Per-endpoint resize may normalize growth; appearance sensitivity is another
hypothesis. Neither is proven by this selected set. Prefer a future qualified
matched native-growth/no-growth contrast over a threshold sweep on these cases.

Five bounded helper processes loaded the model:43.71ms first load,2.71–3.04ms later
loads. These are model-load observations, not end-to-end navigation latency or a
warm inference benchmark. Crop/score process completed successfully; no new capture,
training, dependencies or artifact changes. Existing source-contract blocker remains.

Tests:21focused Python tests passed(0.932s), including invalid probabilities,
changed inputs, preserved unadmitted status and legacy paths. Offline native Swift
build passed; full serial suite132tests/17suites passed in4.099s(exit0), recorded
in `.build/schema4-score-test.log`. `git diff --check` passed.

Published and exact-byte read back at
`nuiak/responses/nuiak-20261006-art191-shipped-diagnostic.json`, SHA256
`12f9bafac81e7ecae4ef8e00eab890f55ec6ad22456d247af91cb778678184a0`.
Peer acknowledgment remains separate and pending.

Next: resolve source/geometry semantics on the retained worst cases, then freeze
eligible native membership for a matched candidate comparison. Big Dog's separate
512-image compatibility stage is already dispatched; no acknowledgment yet at this
turn's initial check. Software is verified; training eligibility and model gates
are not established. This diagnostic does not reopen final evaluation ancestry.
