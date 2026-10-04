# LOCAL-ROBUSTNESS-126 — two local model experiments

Software: passed. Source data: existing admitted/exposed membership unchanged.
Integration: no new producer qualification. Model gates: not assessed; diagnostic
robustness failures, not independent accuracy. No training, capture or promotion.

## Outcomes

Frozen DTM030 reproduces all433 historical decisions exactly before interventions.
All207 original transitions and226identical pairs accounted for. DTM025 base and
DTM030 candidate evaluated on identical transformed tensors; case-level scores,
failure indices and source/checkpoint pins retained in `artifacts/audit/report.json`.

| Input intervention | Old108 | Settings5 | Region94 | Identity226 |
|---|---:|---:|---:|---:|
| Unchanged |108|5|94|226|
| 0.8x |97|5|88|226|
| 0.8x+0.1 |101|4|84|226|
| 0.8x+0.2 |106|4|83|226|

Counts are confident-correct against existing labels, not new independent truth.
Dim produces2confident wrong decisions; contrast1; bright0. Other losses abstain.
Transforms are bounded, monotonic and common to both frames, but also alter padding.
They are not native themes or admitted augmentation. They justify investigating
appearance sensitivity, not claiming these errors occur on actual device captures.

Residual attribution: multipliers0,0.25,0.5,0.75,1 yield Region confident-correct
0,0,36,84,94. Identity correction is exactly zero. Full correction preserves all
original training successes; reducing it is not a supported deployment fix.
77/433 logits exceed absolute20; saturation is descriptive, not calibrated confidence.
No multiplier or threshold selected. Shipped and experimental model files unchanged.

## Verification

Actual CLI: `scripts/robustness126.py --output reports/work/LOCAL-ROBUSTNESS-126/artifacts/audit`
under resident Python with project-local temp/bytecode disabled, exit0;6.955seconds.
Report seal `782b99449e2e46adccdf065766a30a0dbd11bd5c7749d32fa408febb5b5e3edb`.
Input tensor hash unchanged.9 focused tests pass (robustness126,reflow117,identity
residual). Offline Swift build and139tests pass (14XCTest+125Swift Testing);
logs `.build/robustness126-{build,test}.log`. `git diff --check` passes.
No simulator startup, transfer or external wait needed. Existing dirty files preserved.

## Next substantial tranche

Use source image dimensions and production encoding to separate content-only from
padding-only interventions, reusing all prepared inputs. If content sensitivity
persists, freeze one paired robustness fit with original retention/identity gates
and separately reported transformed-data performance. Do not add speculative labels
or claim new independent evidence. Retained TTR survey26 replay remains independent
and can join diagnosis when delivered; it is not prerequisite for this local work.

SMB not applicable: no new peer interface, artifact or required TTR action. Existing
passive-only deployment boundary unchanged. Model-workflow skill kept preprocessing,
membership and promotion claims separate throughout.
