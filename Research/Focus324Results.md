# FOCUS324 — detail features before scalar compression

Owner: Maximum-mini-NUIAK.

**Decision: reject the candidate.** Retained features improve some native decisions, but the correction loses many distraction successes.
Production models remain unchanged. Sillycon-TTR must not replace its current model with this candidate.

## Model results

Counts show correct decisions unless the row names false changes.

| Measure | FOCUS313 | FOCUS319 | FOCUS323 | FOCUS324 |
| --- | ---: | ---: | ---: | ---: |
| Native / 640 | 598 | 581 | 581 | 595 |
| Native development / 40 | 33 | 38 | 38 | 40 |
| Inspected reserved native / 52 | 51 | 52 | 52 | 52 |
| Replay / 668 | 668 | 646 | 646 | 651 |
| Reversed native / 640 | 602 | 579 | 579 | 591 |
| Reversed replay / 668 | 666 | 644 | 644 | 642 |
| Lighting / 226 | 226 | 226 | 226 | 226 |
| Left distraction / 226 | 144 | 160 | 161 | 70 |
| Left false changes / 226 | 82 | 53 | 53 | 75 |
| Center false changes / 226 | 99 | 136 | 136 | 133 |
| Tiny forward changes / 4 | 0 | 0 | 0 | 0 |
| Placeholder movement / 8 | 2 | 8 | 8 | 7 |

Against FOCUS319, the candidate gains 14 native decisions without losing a native success.
The 14 gains include 12 training cases and 2 development artwork cases. Both development gains replace abstentions.
The candidate preserves all 52 previously inspected reserved decisions. These cases are not a new untouched audit.
It loses 90 left-distraction successes. False changes increase by 22, and abstentions increase by 68 on that set.
Reversed replay loses 6 successes and gains 4. Placeholder movement loses 1 success to abstention.
Native results retain 2 misses and 43 abstentions. All 8 tiny forward/reversed changes remain misses.
All 8 identical tiny pairs remain correct. Placeholder arrival remains 14/16.
The candidate fails 12/24 nuisance strength and order checks against DTM085.
Case-linked comparisons include DTM085 and FOCUS313, FOCUS319, FOCUS320, FOCUS321, FOCUS322, and FOCUS323.

## What the feature audit establishes

The frozen model retains 32 context features and 32 pooled detail features before its scalar readout.
The audit preserves both image-selected windows and their original-resolution pixels.
It uses the existing 1,820 training views and 240 approved authored pairs. No development cases enter fitting.

| Training-only diagnostic | Weighted margin shortfall |
| --- | ---: |
| Original scores | 0.276883 |
| Constrained correction from detail features | 0.253348 |
| Constrained correction from context and detail | 0.164669 |

Detail features reduce this shortfall by 8.5%. Combined features reduce it by 40.5%.
The combined solution justifies the registered candidate. It does not establish generalization.
Original training correctness rises from 1,649/1,820 to 1,690/1,820.
Authored training correctness rises from 217/240 to 235/240.
Authored movement reaches 80/80. Artwork-only correctness reaches 75/80, with 5 false changes.
The fit preserves all 1,866 protected correct training decisions. It does not protect unseen decisions automatically.

The audit reports each source group, authored layout, and condition separately.
Of the original training views, 1,048 have measured minimum body dimensions of at least 16 encoded pixels.
Another 104 have minimum dimensions from 8 to 16 pixels. Measurements remain unavailable for 668 replay views.
No measured original training view falls below 8 pixels. Authored views remain separate from these native size counts.
This corpus does not independently vary native effect strength. The audit makes no strength-separation claim.

## Why another readout fit is not the next step

After evaluation, a diagnostic maximizes each tiny-case score under the same training constraints and coefficient bounds.
Even those separate ideal scores range from -2.214 to -0.229. The required change score is 1.735.
Thus this bounded readout family cannot solve any of the 8 tiny changes while preserving its constraints.
This result does not prove that every larger bound, feature encoder, or model fails.
Each bound uses different coefficients. The diagnostic saves no weights and selects no candidate.
All 8 tiny feature vectors are closer to a negative training example than a positive example after training-only normalization.
That distance is descriptive. It is not calibrated confidence or proof of conflicting labels.

The evidence supports 2 distinct problems: weak tiny-effect features and poor protection against unrelated visual changes.
More fitting over the same scores is not justified. More identical synthetic volume is also not justified.
The next comparison must change the visual evidence or learned detail representation, with a matched control.

## Implementation and verification

The runner reuses existing image preparation, feature branches, constrained fitting, and evaluation.
It adds 65 residual coefficients. Training-only means and standard deviations normalize the 64 features.
The minimum standard deviation is 0.001. Coefficients stay within [-1, 1]. Thresholds stay at 0.15 and 0.85.
Original weights and authored exposure remain unchanged. The authored objective keeps coefficient 0.25.
The runner uses the audit solution directly. It performs no second fit or evaluation-based selection.
All 36 frozen tensors remain unchanged. Cached/image probability error is 0, and checkpoint reload preserves scores.
The smallest float32 constraint slack is -0.000000988, within the existing 0.00002 numerical tolerance.
No protected training decision is lost. The float32 objective matches the solver result.

All 65 focused tests pass in 1.403 s. The offline Swift build passes in 4.37 s.
All 14 XCTest tests and 173 serial Swift Testing tests pass. Swift Testing takes 54.121 s.
The tests also find and fix an empty-set failure in the shared solver diagnostic.
If no correct training decisions need protection, the diagnostic now reports unavailable slack instead of failing.

The audit takes 87.57 s. Candidate construction through complete evaluation takes 155.67 s.
Candidate construction and training checks take 0.14 s. Image preparation and evaluation dominate runtime.
Outputs occupy about 2.9 MB before final documentation. Inputs and production models remain untouched.
No capture, external computation, download, export, or Core ML qualification occurs.

## Evidence and outcomes

Retain raw evidence under `reports/work/FOCUS-324/`. Keep generated data and checkpoints outside Git.

| Evidence | SHA-256 |
| --- | --- |
| Feature cache | `713a511c0790aae623c2d669571b4da5ae03abcbede33e3ce60e9ffc464faf99` |
| Audit | `6fbe2362b74ae9a2dc1d57fa4f16dfe6cfc848db784c6344e2852002eddf40ce` |
| Candidate | `9d4a3dc9d20ded25cf1b58e01f3d85c7716a32900e7c7d1612f7e359a6548744` |
| Comparison | `f5739b8660449f9ade2b5dde51b09f03ebe716d9d804f4d98472389dcacb6be6` |
| Tiny-case diagnostic | `5e7dba099f9b30c1f0ee8195087729ce51129ae9689e71607bb94eb793f4ad18` |

- Software verification: passed.
- Data eligibility: unchanged approved roles; no new admission.
- TTR integration: not assessed in this model experiment.
- Model requirements: failed; no promotion.

The coordinator stores the result at cursor 156 but reports no provider delivery.
The SMB fallback publishes `nuiak/responses/nuiak-focus324-result-01.json`. Exact size, hash, and readback pass.
Sillycon-TTR acknowledgment remains unconfirmed. The message tells Sillycon-TTR to retain its current model.

## Next substantial tranche

FOCUS325 is proposed, not started. Maximum-mini-NUIAK owns the next local comparison.

1. Measure what the detail encoder retains before global pooling, using existing training positives and content-only negatives.
2. Freeze a small, position-balanced training set with independently varied control size and separation.
3. Reuse approved artwork and existing rendering tools. Keep authored labels distinct from native observations.
4. Test a matched data-only control and 1 justified detail-encoder correction. Preserve all original views and thresholds.
5. Compare native gains, tiny changes, reversals, and nuisance successes together. Reject a trade that only moves failures.

Before execution, fix the feature design, eligible input hashes, 2 run configurations, and output limits.
Do not reuse the tiny development cases or their related groups for training.
The accepted outcome requires more useful native decisions without losing previous successes or increasing false changes.
Use local tools first. Any new Sillycon-TTR work requires a separate approved request.
