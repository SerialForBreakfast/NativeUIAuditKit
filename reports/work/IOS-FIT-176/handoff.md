# IOS-FIT-176 — confidence/retention diagnosis and replay proposal

2026-10-05. Completed the assigned diagnosis and froze a training-only replay
proposal. No new inference, training, capture, labels or threshold adjustment.
All calculations reuse175predictions and173admitted membership, verified through
existing sealed readers and prediction validators. No implementation code changed.

## Findings

The175fit set omits15classes supported by the full admitted training corpus.
Sheets have569available training images; scroll indicators700. Both have zero
positive examples in175. Absence supports a replay hypothesis but does not prove
causation: this experiment also changed exposure and optimizer trajectory.

| Page fit stratum | Hits/support | Median matching confidence |
|---|---:|---:|
| Leading KitchenSink | 34/34 | .518 |
| Leading UIKitControls | 36/38 | .767 |
| Center KitchenSink | 34/34 | .582 |
| Center UIKitControls | 38/38 | .829 |
| Trailing KitchenSink | 21/34 | .296 |
| Trailing UIKitControls | 35/38 | .759 |

All18misses have same-class boxes at IoU≥.5 below confidence.25. Thirteen of the
16trailing misses belong to KitchenSink. These medians summarize the maximum
confidence among ground-truth-matching boxes, not runtime oracle selection.
Native theme/scale coupling persists; do not conclude an independent theme effect.

### Retained sheets: ranking/false positives, not disappearance

Support24. Run019 TP24/FP218/FN0 becomes020 TP23/FP235/FN1 at.25/.5.
AP50 falls1.0→.210156; retained predictions at the lower exporter threshold rise
638→1250. All23surviving ground truths stay operating hits; the sole lost hit is
`test/images/img_017560.png`, now a low-confidence match. A large AP drop alongside
nearly preserved recall indicates poorer confidence ordering among true and false
predictions; it is not evidence that79%of sheet boxes disappeared. High old AP also
did not imply good operating precision: old precision was only.0992.

### Retained scroll indicators: an existing operating failure worsens

Support100. Both models have0TP/0FP/100FN at.25/.5. Run019 has59low-confidence
matches and41localization misses;020has34and66. Exactly25low-confidence matches
become localization misses;41prior geometry misses remain. AP50 .3481→.116147
measures degradation below the fixed operating threshold, not lost working hits.
All124sheet/scroll ground-truth cases are retained in the sealed diagnosis.

## Frozen replay proposal

Keep216175placement images and add216unique existing train images. Selection uses
training labels only: deficits toward16images for each supported class absent from
175, then current aggregate class support and stable image ID. Full annotations
are preserved; no pseudo-labels, role changes or retained-test error-driven sampling.
All selected image/label hashes verified; no duplicate pixel identities with fit
members or existing validation/test. Ancestry still needs explicit launch preflight.

Coverage:16each actionSheet,alert,collectionItem,contextMenu,dynamicIsland,mapView,
popover,refreshControl,sheet,sidebar,toolbar,unknown;28tooltip;32scrollIndicator;
32statusBar. All15coverage deficits zero. webContent has no available training
support and remains unavailable. Additional co-occurring classes retained.

Replay family counts:40HardNegative_1,40HardNegative_3;16each RichContentFeed,
SystemNavigationShell,ChromeCoverage,ActionSheet,Alert,OccludedElement,Popover;
14ModalDialogueFlow,8ClippedContent,2ContextMenu. The80hard-negative filler images
are a consequence of the low-current-support rule, not a claimed optimal mixture.
Review this composition before launch; freeze a new version if changed, never edit
the sealed proposal. Do not select replacement replay images using test predictions.

The canonical plan specifies one compute-matched432-image/10epoch proposal from
Run019, versus020's216/20epochs:540nominal batches each. Placement exposure is
halved; rectangular batch composition and epoch-based schedule/warmup require
reconciliation. This is not a clean equal-exposure single-variable experiment.
Current proposal explicitly has launchEligible=false. Implementation, ancestry,
schedule and corpus/config preflight remain required; no new run ID allocated.

## Evidence and verification

- `artifacts/replay-proposal.json` SHA256
  `38d3f3527050792a7b2415b28b6faf7fd55f8c7b8d54d3980f65f7731185a0d3`.
- `artifacts/diagnosis.json` SHA256
  `b35786491677187b2976ac496342a846358f39507691058d5cfc6c52f9b6fac3`.
- Canonical175evaluation seal
  `140e17a933db7766ba215f3175658d3fa2c3986f753d4c769caa4f048f29bf85`.
- Batched analysis/proposal generation20.895seconds, exit0; existing fit175.ready,
  diagnostic174.inputs, prediction validators, membership seals and selected-file
  hashes passed. Later readback confirmed216train rows and family/support totals.
- No new library/script code: existing implementation tests reused; no redundant
  Swift rebuild or model inference. Documentation diff check passed.

Software evidence validated; selected data retains existing training eligibility,
but proposal launch readiness is not established; native integration not assessed;
model gates unchanged/not passed. No TTR-relevant change, so no SMB publication.

## Next substantial tranche

Implement a reusable replay prepare/preflight path in the existing trainer workflow,
test membership/role/hash/collision/schedule failures, explicitly audit filler balance
and ancestry, then register and execute one qualified comparison under standing
training authority. Evaluate the same216/96/2400members and all retention gates in
the canonical plan, including every supported class. Failed gates mean diagnosis,
not automatic extra epochs or lowered thresholds. TTR source intake can proceed
independently when its exact producer revision becomes available.
