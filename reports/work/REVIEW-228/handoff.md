# REVIEW228 — exposure, confidence and source-semantic review

## Completed outcome

Audited all249 resident Run035 training sources and reconciled all41 weighted class
counts against the frozen1758-slot schedule. Verified image/label hashes and train
roles. Reviewed six original training frames with label/listRow overlays and checked
the responsible Swift source. No inference, training, capture, relabeling, threshold
selection, data-role change or promotion occurred.

| Class | Distinct training images | Distinct instances | Instances per epoch |
|---|---:|---:|---:|
| label |210|845|5200|
| listRow |84|434|3906|
| progressView |16|17|153|
| pageControl |79|79|231|
| toggle |24|53|477|

Progress support is11 KitchenSink,4 UIKitControls and1 ProgressActivity image.
Page support includes60 native artwork frames; repeated slots are not new visual
evidence. The previous034→035 exposure intervention reduced progress900→153 and
page1588→231 instances/epoch. This is a plausible mechanism, not causal proof.

## Confidence diagnostic on previously inspected development frames

Per-GT best same-class score with IoU>=.5, not unique matching:

| Class/support | Cached qualifying geometry022→035 | Score>=.25 022→035 | Median available score022→035 |
|---|---:|---:|---:|
| pageControl/600 |573→524|249→359|.197→.787|
| progressView/200 |200→200|199→180|.584→.596|
| toggle/1787 |1587→1387|1387→1387|.978→.989|

Toggle loses200 below-.25 qualifying proposals in the exported cache even though
operating TP is unchanged. Page gains confidence on many examples while losing
qualifying proposals on others. This is not a uniform confidence shift; lowering
one threshold is not an established repair. Cache absence is conditional on the
existing .001 export floor and NMS, not proof the network produced no raw geometry.
No new threshold, ranking metric or deployment gate was selected.

## Source-semantic finding

Reviewed AccountProfileForm, Alert, AlertWithTextField, ChromeCoverage, ColorPicker
and ContextMenu training examples (IDs/paths in artifacts02/report.json). Red boxes
mark label, blue listRow; other classes were deliberately not drawn. Thus uncovered
text in these overlays is not automatically a missing annotation.

`ContextMenuTemplate.swift` explicitly captures Swift Button action rows under
`label_action_*`. Architecture section5 defines label as standalone non-interactive
text. All13 resident ContextMenu sidecars, hash-verified, contain41 label_action
annotations typed label. The rendered sample shows row-sized boxes on Continue,
Decline and Delete. This is a source/taxonomy inconsistency requiring a policy and
versioned repair, not license to rewrite historical labels. Capture-era source
equivalence is not asserted solely from current code. AccountProfileForm also
mixes separately captured field-name text with container classes; resolve the child
text policy across templates before blanket missing-label fixes.

## Next substantial tranche

SEMANTICS229: reconcile interactive action/child-text taxonomy across ContextMenu,
form and menu templates; define an explicit mapping using existing categories,
audit affected training membership and preserve immutable original reports. Implement
the generator correction with tests only after recording that mapping in Research.
Generate/review a bounded versioned training-only repair; never rewrite retained
evaluation or claim inspected examples are fresh holdout.

Then design one matched replay comparison using only qualified training sources:
same initialization/epochs/optimizer-update budget and native60 membership; vary
only sampling exposure to underrepresented controls. Freeze the schedule and tests
before launch. Evaluate full-frame retention, native performance and FP tradeoffs;
do not repeat the known ROI/full-frame conflation. SEMANTICS229 must first establish
whether this is a sensible next run or a label-policy repair is prerequisite.

## Verification, preservation and coordination

Actual analysis `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python
reports/work/REVIEW-228/analyze.py` completed exit0. Initial attempt stopped because
native manifests keep hashes in the file inventory, not each example; empty initial
artifacts directory preserved. Corrected analysis uses each pinned file inventory.
All41 exposure totals reconcile; report pins schedule/proposal/script hashes.
Context-menu audit preserves all13 sidecar hashes and current generator source hash.
16 existing focused tests pass with `PYTHONPATH=scripts`; first invocation without
that import path failed before tests. No production Swift/Python entrypoint changed;
reuse unchanged integrated Swift evidence from REPLAY219/EVIDENCE223.

Peer listing still exposes the previously reviewed worker219-complete03 and TTR
repair09 as latest returns. No new source-binding acceptance observed. Existing
DIAG227 request remains published; no duplicate status or new recapture request.
This local iOS diagnosis does not change TTR's next action, so no SMB write needed.

Software: hash/count assertions and16 focused checks pass; data: unchanged roles,
semantic repair pending; integration: offline only; model gates: not assessed.
No Git writes, deletion, or modification of existing artifact bytes.
