# FOCUS-VISUAL-05 — four-cell comparison complete

October 1, 2026. Owner: Codex. **No candidate passed; preserve FDR021.**
The useful result is a measurable appearance-coverage gap, not a release claim.

## Results

Exact unchanged FDR023 membership: 1,550 training, 315 development and 18 retention
controls. Fixed 0.85 threshold and source weights. Development is exposed, not an
independent final examination. Four assigned runs; no fifth run or export.

| Model/input | Updates | Focus hits /27 | False positives /288 | Artwork hits /12 | Unique-correct frames /14 |
|---|---:|---:|---:|---:|---:|
| FDR021 retained baseline | — | 16 | 3 | 2 | 12 |
| FDR027 frozen, detail | 100 | 14 | 3 | 0 | 11 |
| FDR028 frozen, detail+context | 100 | 14 | 33 | 0 | 7 |
| FDR029 partial backbone, detail | 100 | 17 | 24 | 3 | 12 |
| FDR030 partial backbone, detail+context | 87 | 16 | 23 | 2 | 10 |

Candidate rows are **terminal diagnostics, not selected checkpoints**: all selected
updates are null and no saved snapshot passes the existing eligibility or strict
comparison. All terminal retention results are18/18. Eighteen incomplete development
frames are explicitly unavailable for complete-frame selection, not counted as
successes or failures. FDR027 has one wrong selection; FDR028/029/030 have5/1/3
multiple-selection frames. Candidate-level false positives and frame-level outcomes
have different membership/denominators.

All39 saved evaluations replay exactly through the existing metric implementation.
Initial predictions are identical across all four arms. At the last shared update80,
artwork hits are0/0/3/2 and false positives1/31/23/23; none passes. FDR030 reached its
cooperative300-second limit (300.878 model seconds including terminal work); it is
not a100-update or convergence result. No alternative checkpoint was cherry-picked.
See [replay](analysis.json), [replay script](analyze.py), and
[predeclared contract](../../../Research/Plans/FocusVisual05.md).

## Why the improved annotations still did not produce a better model

The annotations now describe bodies more accurately, but that does not establish
appearance coverage. A post-hoc retained-pixel audit found:

| Appearance population | Mostly-white body / total |
|---|---:|
| Unfocused training collection items | 0 /554 |
| Focused training collection items | 0 /242 |
| Unfocused development artwork | 57 /181 |
| Focused development artwork | 4 /12 |
| FDR029 terminal false positives | 21 /24 |

Descriptor: within the central192×192 pixels of each256×256 retained crop, more
than65% have minRGB>220 and maxRGB−minRGB<25. This is an explanatory descriptor,
**not a new classifier, threshold policy, or universal definition of white artwork**.
White examples do exist in other training roles:104/149 unfocused and129/142 focused
primary buttons meet the descriptor. Therefore this is a role/appearance coverage
gap, not an assertion that the entire training set lacks white pixels.

All24 FDR029 false positives are artwork;21 belong to Home/Home-top-shelf families,
one to Home-lower-grid and two to App Store families. There are23 distinct decoded
crop hashes, but related screens mean these are not24 independent sources.
Reviewer inspection of the highest-scoring false positive (`photos:frame-003:new-6`,
0.999996) shows an unfocused white YouTube tile while Photos is visibly enlarged.
This supports an appearance-shortcut hypothesis; it does not prove causation or
that filling this gap alone will solve transfer. [Audit and exact IDs](appearance-audit.json),
[reproducer](appearance_audit.py).

Partial training did update visual weights and improved artwork hits relative to
its matched frozen arm, but false positives invalidate that improvement. This
particular context representation did not fix the errors. We have not tested a
fully trainable backbone, a different training schedule, or an aspect-fit training
arm; this is not evidence that those entire architecture families cannot work.

## Implementation and acceptance evidence

- Production16%-expanded detail crops unchanged. Candidate-centered context uses
  a fixed viewport-relative window and a label-free spatial mask, not a tight
  candidate resize or focus label.32/32 available growth comparisons preserve scale.
 49 wide controls exceed the context window; detail remains available for each.
 13 deterministic numbered sheets plus inspected tab context cover input behavior.
  [Input review](artifacts/input-v2/review.md).
- Cached only immutable MobileNetV3-small prefix[:9] activations, not final features
  downstream of trainable layers. Both partial arms change tail[9:] weights; both
  frozen arms do not. All batch-normalization state/affine weights stay frozen.
  Label-free masks identify the candidate during pooling. Shared tail across streams.
- Exact weighted whole-corpus gradients accumulated in32-control microbatches;
  tests verify equivalence, deadline cancellation, changed hashes/protected roles,
  cache membership, actual trainer dispatch and no early stop at training fit.
-78 focused Python tests pass; offline `swift build` and14 XCTest+120 Swift Testing
  tests pass. Logs: `tests.log`, `swift-build.log`, `swift-test.log`.
- Prefix encoding and all attempts total887.975 process seconds, below1800;
  final runner-accounted artifacts419,248,074 bytes, below2GiB. Prefix cache below512MiB.
  All four trained candidates exit0; FDR030 stops at the cooperative time cap.
- Initial input diagnostic metadata (pair identity/projected dimensions) was corrected
  in input-v2 before encoding. A counts-reader encoding startup and missing adapter
  `warmCheckpoint` training startup failed before optimization; receipts retained,
  budget charged and caller tests added. No extra trained candidate was substituted.
- The historical trainer startup banner still names MobileNetV4; sealed protocol,
  actual factory and cache identify MobileNetV3-small for these arms. The banner is
  not architecture evidence. No source change was made mid-run to alter sealed code.

## Next coherent tranche — appearance coverage before another model run

1. Inspect TTR's already-published composition delivery, using verified receipt/intake,
   for the specific gap before requesting new capture. Producer publication is not
   consumer acceptance. This transfer was not part of the completed four-run scope.
2. Inventory bright/white artwork, logos and blank placeholders in both focus states,
   with the same asset and layout across each pair, visible competitors and measured
   rendered-body bounds. Include dark/bright backgrounds and independently selected
   but unfocused parent tabs. Reuse good existing data; do not redraw correct boxes.
3. Freeze source/asset/recipe ancestry and preserve development/challenge separation.
   New related crops are not independent evaluation. Review a stratified prefilled
   sample, plus geometry/label anomalies; do not burden the human with every letter
   or repeated unchanged screen. Agree collection targets after inventory, not a
   speculative huge corpus or new qualification threshold.
4. Then run a matched data-only comparison against the same recipe/control, preserving
   source budgets, fixed0.85 and all non-artwork/retention requirements. Success must
   reduce false positives without losing focused hits; only then consider export.

This next tranche needs assignment; no additional capture/training was dispatched.
The existing TTR white-artwork request was followed up with these exact acceptance
needs; [coordination record](coordination.md) separates publication from acknowledgment.

## Independent outcomes

- Software: integrated and tested; four actual CLI runs and saved-metric replay pass.
- Data: existing admitted membership preserved; new appearance gap documented.
  No new data admitted, no source labels changed, no protected challenge inspected.
- Integration: no new TTR runtime or CoreML integration qualification. Metadata only.
- Model gate: failed for all four candidates. FDR021 and shipped behavior unchanged.
