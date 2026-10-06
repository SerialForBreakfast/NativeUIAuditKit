# Persistent trailing misses — October 6

Read-only replay of retained Run027/028 results; no inference, training, threshold
change or data-role change. This is training-fit diagnosis, not independent quality.

## Result

Both extra-proposal arms fail on exactly the same14of216fit images. All14are
KitchenSink/dark/trailing (8system-blue,6semantic-label). Recomputed actual proposal
windows and crop-label dispositions:13clip the page control;1excludes it entirely.
All14best-IoU boxes are identical to retained Run022 full-frame predictions. Both
arms reject an extra donor with `no_unique_donor`; their unchanged errors do not
demonstrate that the newly trained crop detector failed on a complete target.

Best IoU ranges0.43206–0.48800, below the unchanged0.5criterion. Truth height is
23.001source pixels; inherited predictions are taller. The low-confidence extra
proposal lies near the center, while the target is trailing. For example,
`placement171-img_004903-trailing-system-blue` has truth x932.99988–1062.99996,
but the proposed window ends at x888. The crop contains none of the target.

The pre-existing fixed-grid proposal geometry fully contains each of these14truths
in at least one window. This is an oracle containment diagnostic, not permission
to select windows using labels, evidence of model recall, or justification to ship
an expensive tiling pipeline. Theme and scale are coupled in this source; no
independent dark-theme causal claim is supported.

## Verification

Used existing `roi197_compare`, `eval_run013` validation, `roi193.labels`,
`diagnostic174.pages` and the frozen proposal rule. Validated both prediction
artifacts against their original crop manifests/checkpoint/settings, recomputed
merges and asserted exact equality with saved fit-derived results. Asserted
identical failed IDs, original first-pass membership of every best box, and
computed containment without changing predictions. Both read-only commands exited0;
combined runtime2.59seconds, no GPU use.

Input hashes under `artifacts/training01`:

- control/extra-proposal/fit-derived.json: `22fd1fe07712c4ee4cd17708f4ebd0642585de5c1678fe9079c428d02b33f3b6`
- treatment/extra-proposal/fit-derived.json: `26c06a073429677cbd91c100097abdee2eb9b58bf45944e7bd0224b523bf4734`
- control/extra-proposal/protocol.json: `9881198c745373ed32c938d960261989ab4488d246483990e67a43ae73fc0e93`
- treatment/extra-proposal/protocol.json: `a7412bdc454a1fce9ecb95e148b9ff37fa08de95e917004c004ee30c813d2dd0`

## Next decision

### Follow-up: existing paths are complementary

Read-only inspection found all14extra-path failures are already operating hits in
both refinement arms, with one fully containing operating window each. Registered
a fixed composition in Run013Evaluation before testing: retain refined predictions,
then append original-rule admitted extra donors only when no refined operating
page box overlaps atIoU>=0.5. No truth-based routing or threshold changes.

Revalidated both arms' crop artifacts, recomputed existing refinement and extra
merges, and asserted all non-page detections unchanged. CPU-only fit replay exited0
in2.18seconds. Each arm adds17donors, suppresses0:216/216TP,24FP,0FN, with72/72hits
at each placement. AP50=.9798043111; AP50:95=.8693291207control and.8617962195treatment.
This beats extra-only202TP/38FP on training-fit sources, not held-out evidence.

This supersedes tiling as the first next hypothesis: integrate/test the composition
of existing paths before adding capture, more windows or training. The extra-path
coverage diagnosis remains true; it was not the complete system's capability.
No retained evaluation was used for this diagnostic rule or scored with it yet.

First test a bounded truth-independent proposal-coverage alternative on training
sources, including negative windows and cost. Separate raw crop detector quality
from proposal selection and donor admission. Freeze any rule before retained
evaluation; do not tune it on that set. Reuse fixed checkpoints before considering
another training run. Native-focus work remains higher priority when source-bound
inputs arrive. Current model gates still fail and shipped models remain unchanged.
