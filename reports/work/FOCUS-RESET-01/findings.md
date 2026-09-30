# Focus reset: what the retained evidence actually shows

2026-09-29. Offline replay only; no new inference, threshold fitting or training.
Authoritative output: `final-evidence/report.json`. Earlier `evidence/` and
`verified-evidence/` are preserved; final replay pins the diagnostic implementation
and historical metric sources without requiring unchanged trainer code.

## Scoreboard

All 14,601 initial/epoch scores reproduce the existing selector. All 488 distinct
referenced real image/crop files verified; 453 real candidates retain original
labels. Of 40 frame policies, 13 support complete-frame decisions and 27 remain
explicitly unavailable. The 13 comprise eight Settings-related, three App Store
tabs and two Home frames. These are reused development data, not independent tests.

| Diagnostic | Starting checkpoint | Epoch 1 | Epoch 30 |
|---|---:|---:|---:|
| Focus ranked first, ignoring threshold | 8/13 | 11/13 | 5/13 |
| Runtime-style correct / wrong / no focus at0.85 | 2 / 1 / 10 | 2 / 2 / 9 | 2 / 1 / 10 |
| Independent-threshold correct / multiple / wrong / no focus | 2 / 0 / 1 / 10 | 2 / 2 / 0 / 9 | 2 / 1 / 0 / 10 |
| Crop AUROC | 0.654 | 0.685 | 0.601 |

Fixed simple baselines on those same13frames: uniform random choice expects
1.398correct (10.76%); top-left annotated candidate gets5; largest annotated area
gets8 (ties contribute fractional expected correctness). These use reviewed boxes,
not production detector proposals, and are not autonomous navigation policies.
Always-unfocused would get92.27% binary crop accuracy yet never identify focus.
Raw accuracy is therefore a misleading headline for this imbalanced set.

The runtime-style calculation isolates highest-score-above-threshold logic with
Float32 comparison. It is NOT a full runtime replay: detector recall, supported
role filtering and CoreML score parity are not reproduced. In particular diagnostic
`focus:tabItem` annotations do not themselves establish production detector support.
Tied native winners are explicitly unavailable rather than assigned an invented order.

The strict gate remains useful as an ambiguity check and is unchanged. It must not
be described as identical to the shipped winner-takes-all decision. At epoch1 the
two multiple-positive frames become wrong choices under winner-takes-all, not wins.
The attractive11/13 ranking result cannot justify promotion or lower thresholds.
Only stored scores exist for that epoch; no recovered early checkpoint is claimed.

## Eight-page crop inspection

Pages are deterministic: first two positive IDs per appearance group, with each
frame's highest-scoring unfocused competitor at the final epoch. This is a small
inspection panel, not an exhaustive or random label audit. Agent visual observations
below neither change human labels nor prove causality.

| Pages | Observation | Consequence to test |
|---|---|---|
| 001–002, Photos buttons | White focused/gray unfocused distinction remains visible. Wide text/buttons become heavily stretched. | No obvious gross wrong-region extraction in these examples; compare features that preserve useful shape/context. |
| 003–004, App Store tabs | Focused Arcade/Purchased pill remains visible. Unfocused neighbor crop contains part of its white focused neighbor. | A model may respond to a neighboring highlight rather than the target; distinguish crop center from context. |
| 005–006, Home artwork | Full frame shows enlarged focused tile and title. Square crops reduce relative-size context; unfocused bright/white artwork looks superficially similar. | Test geometry/context and matched same-artwork contrasts; brightness alone is unsafe. |
| 007–008, Settings rows | Correct target region and white row visible; text is severely stretched. A neighboring unfocused row includes the edge of the white focused row. | Neighbor context helps location but can contaminate independent crop labels; test target-aware features. |

Inspection found no evident vertical flip or wrong target in these eight pages.
It does not prove all crops/labels are correct. Use the existing production crops;
do not silently change preprocessing or redraw annotations based on this panel.

## Decision

Do not expand collection or rerun the old model as the immediate response.
The first learning comparison should test a broadly pretrained frozen representation
on the same approved training data. Training ranking decays8→11→5 across the shown
snapshots while familiar training loss falls; investigate representation/overfitting,
not just sample count. This is an observed development trajectory, not causal proof.

Keep screen-relative ranking and calibration separate. A future ranking objective
is conditional on the frozen-feature comparison and suitable complete training
frames; never repurpose incomplete frame labels as exhaustive competition sets.
Calibration needs a separately assigned grouped split; no fitting on these13frames.

`baseline-proposal.md` specifies the single comparison, subsequently approved and
completed as FDR015. See `../FDR-015/results.md`: ranking improves at the final
snapshot, but fixed-threshold/retention gates fail; no selected checkpoint.
No new human annotation is needed to complete the current diagnosis. Existing real
evaluation screens remain out of training. Broader real training data remains a
separate admission decision if the approved corpus cannot teach transfer.
