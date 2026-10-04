# REGION-SIGNAL113 — frozen-model input diagnosis

Completed424encoded examples, six interventions, two pinned models and per-channel
logit-gradient summaries. DTM025/028weights remain unchanged. Baseline probabilities
match REGION112within1e-6; no new training, data admission, capture or promotion.

| DTM028 Region condition | Confident change responses /94 |
| --- | ---: |
| Original |26|
| Reverse before/after |26|
| Difference channels only |79|
| Context channels only |0|
| Differences in inspected focus strip only |0|
| Differences outside inspected strip only |20|

Interventions are artificial inputs, **not labeled evaluation examples**. Fixed
inspection-strip mask maps3840×2160to192×128letterbox at[104,89,186,102]; it is
not a production focus detector or admitted geometry. No claims of causal proof.

Crucial counter-evidence: removing context makes all217identical examples uncertain
with probability≈0.64536. DTM025remains confident unchanged on those same inputs.
DTM028context-only gives Region≈0.24609, matching its identical-frame uncertainty.
Reversing order changes no categorical decisions in either model. Mean absolute
logit input gradients remain stronger per difference channel than context channel
(DTM028Region0.01655vs0.001025); therefore "only context matters" is not supported.

Conclusion: Region fine-tuning changed the response to zero difference and is
sensitive to surrounding scrolling. Neither removing context nor adjusting a
threshold is justified. A model can respond to real differences yet lack the
semantic distinction between content motion and focus-owner change.

## Verification

- `diagnose_region113.py --output reports/work/REGION-SIGNAL-113/artifacts/audit02`:
 exit0,5.299seconds, batches16. Inputs/weights bound to existing protocol/checkpoints;
 no native setup, full-corpus pixel decoding or external waits.
- ReportSHA256 `26e6c8686d243d4e1335c515a1db54c607a335ce0215f94c808f0e8df401c4c6`.
-26Python tests pass (region113,shadow111,shadow_feedback_contract). Masks preserve
 context/original inputs, spatial masks are complementary, reversal preserves
 difference, unsupported modes/shapes reject, and decision changes count cases once.
 Initial audit01preserved; audit02corrects only categorical-change double counting
 when a response crosses both thresholds. Scores unchanged.
- Offline Swift build/tests pass14XCTest+123SwiftTesting, logs `.build/region113-*`.
 No existing source/model/worker changes removed. No Git writes.

Software:passed. Data eligibility:no change. TTR live integration:not assessed.
Model gate:no candidate; DTM028remains rejected and DTM025passive-only.

## Next substantial comparison

Implement a correction around frozen DTM025 whose output is structurally zero on
identical inputs. Candidate formula: base logit plus a trainable pair score minus
the mean score for its two identical-frame pairs. Identical endpoints cancel the
correction exactly; initialize final residual projection to zero to preserve baseline.
Reuse paired encoding and existing training/evaluation machinery, prove frozen-base
and zero-correction invariants, and pin one600epoch comparison on current admitted
202transitions/217identity checks before launch. Keep old real-negative retention
and unchanged0.15/0.85gates. No oracle inspection window or native hints at inference.

This is a testable architectural hypothesis, not an assured fix. It still can mistake
motion for focus; TTR should supply retained, independently labeled same-focus
animation/scrolling/no-op cases and propose separate unseen layout groups. Existing
Region ancestry remains training/exposed. No automatic sweep or production claim.

Shared feedback published/read back at
`nuiak/responses/nuiak-20261004-region113-negative-controls.yaml` plus own packet.
Exact local bytes and duplicate-key-rejecting YAML pass. It refines the existing
request: retain original frames and find real negative-control coverage, not
another positive-only capture or a new diff-only adapter. No pixel transfer.
Peer snapshot08:20:21Zreports survey15and optional adapters; acknowledgment of this
new feedback remains unobserved. No monitoring scheduled.
