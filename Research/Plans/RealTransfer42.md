# Real transfer and repaired iOS corpus integration42

Maintainer continuation after41. Owner: Codex. Complete three connected outcomes:

1. Evaluate the fixed FSF001 one-epoch full-screen model on the exact46reviewed
   real screenshots already used by scorecard36. Existing diagnostic/development
   roles remain unchanged. Resident YOLO, MPS,640px, NMS.7, one pass at candidate
   confidence.001 with the operating result fixed at.25. Maximum46inferences and
   128MiB outputs; user removed time constraints. Use retained production predictions
   for comparison, not a new production pass. Report focused-body recall atIoU
   .50/.70/.90, multiple/none/wrong/correct decisions on the7complete screens,
   and AP atthoseIoUs on complete screens only. Partial-label unmatched predictions
   remain unreviewed. This is a deployed-operating-point comparison, not isolation
   of architecture from training data/threshold differences.
2. Integrate the666approved replacements into a new full iOS dataset version using
   links to existing pixels. Preserve every train/validation/test ID and unchanged
   annotation; use the existing exporter. Verify all source bytes, decoded duplicate
   groups, exact replacement set and unchanged validation/test hashes. Keep old data.
   Establish actual page-control validation support and identify missing coverage;
   corpus integration does not dispatch another iOS training run.
3. Produce an actionable native-layout coverage specification informed by real
   transfer and the41position failure. Separate training diversity from independent
   reserved evaluation. TTR coordination remains deferred; new capture is scoped
   in the proposal rather than inferred from the existence of a generator.

Focused tests, offline Swift build/test and one Markdown handoff complete the tranche.
Private real screenshots remain local. No threshold selection from these results.

## Coverage decision after the measured real-screen failure

FSF001 locates only1/46reviewed focused bodies at.25, versus21/46shipped proposals.
All7complete screens receive no focus.46predictions overlap known unfocused
controls;11additional predictions on partially annotated screens are unreviewed.
This rejects the current artwork-only full-screen model as the replacement path.
Keep the production path as baseline and use FSF001 only as an experimental baseline.

### Next native corpus — concrete consumer requirements

| Priority / family | Real support now | Required native scenes | Proposed train / development pairs |
| --- | ---: | --- | ---: |
| Artwork / icons | 21 focused collection items | Home-like icon grid, portrait shelves, landscape shelves, mixed hero/sidebar screens | 400 / 100 |
| Settings rows | 16 focused list rows | Short and wide rows, nested navigation, selected parent with focused child, leading icons and trailing values | 300 / 75 |
| Buttons / dialogs | 4 primary buttons | Filled, outlined and text buttons; two-button dialogs; long labels | 200 / 50 |
| Tabs | 3 tab items | Selected-but-unfocused parent tab, focused tab, content-focused state beneath tabs | 100 / 25 |

Two reviewed `otherFocusable` controls need concrete native-role mapping; do not
silently call them artwork. The1,000/250pair proposal is a capacity target, not
an admitted corpus or a claim these native renderers are available locally.

Generation rules:

- Every training family must include top/middle/bottom and left/center/right
  focused positions. Horizontal and vertical layouts both belong in training.
  Vary density and body aspect within each family; do not let position predict focus.
- Within each pair, hold content/layout fixed and move actual ordinary focus.
  Record observed focus callbacks and final visible bodies after enlargement,
  plus layout/interaction bounds separately when available. Preserve shadows/context
  in full screenshots. Decorative descendants are not separate focus targets.
- Cross bright/dark artwork with bright/dark backgrounds and native focus effects;
  include bright unfocused distractors. Match target-role and position distributions
  across content brightness. Typography, icons and hierarchy are required diversity,
  not just recolored placeholder cards.
- Use ordinary accessibility settings for the primary appearance run. Assisted
  verification remains separately attributed and is not substituted into ordinary
  model input. Record OS/runtime, renderer source, assets/licenses and recipe seed.
- Freeze scene-template/source ancestry and asset groups before capture. Different
  seeds, crops or focus endpoints of the same recipe stay together. Reserve distinct
  scene compositions for development while retaining each native primitive's training
  coverage. These are same-renderer development groups, not a real-app final test.
- Add a separately counted no-visible-focus/occlusion stress set; do not pretend
  ordinary one-focus pairs cover those cases. Unknown native truth is excluded,
  not converted to unfocused. Human review combines random samples and flagged cases.

Availability checkpoint: only native artwork generation is locally proven for this
experiment family. Native wide-row/button/tab mappings must be checked against the
current TTR source/runtime before capture. This is a producer-neutral requirement,
not a claimed CLI schema or a request for a producer-built binary. TTR communication
is deferred per maintainer; consuming builds remain local from published source.

Next experiment: fix the corpus first, then compare an unchanged FSF001 baseline
with one matched mixed-layout/control-family training run, reporting the same real
development inventory and reserved synthetic geometry/selection metrics. Synthetic
success alone is insufficient: real focused-body coverage must at least reach the
current21/46proposal baseline and complete-screen outcomes must preserve4/7correct
before considering that branch for TTR. Those small reused sets are development
gates, not a release accuracy promise. Keep checkpoint/threshold selection separate
from any future independent real-app test.

## iOS validation decision

The new linked r8 corpus preserves14,540train/2,800validation/2,400test images.
All666approved corrections stay in training; no evaluation frames move into it.
There are1,566training pageControls and600test pageControls, but zero in validation.
The666manual-dot labels now measure intrinsic groups; the other900native controls
still reflect wider UIKit/SwiftUI containers. That is a geometry-policy difference,
not proof that every one of those900annotations is incorrect.

Recommend defining the detector target as the visible/intrinsic page-indicator body,
with interaction/container geometry attributed separately. First qualify public
native sizing/capture for KitchenSink and UIKitControls, then regenerate exact
affected training IDs in another version if that policy is accepted. Retain r8 as
the verified666-member repair; do not silently expand that correction.

Reserve new page-control development scenes (manual and native, different dot
counts, sizes, backgrounds and active-page positions) before hyperparameter
selection. Use fresh source-grouped compositions; keep the existing600exposed test
examples as diagnostic comparison. This new reservation/capture and subsequent
iOS training require the next explicit scope. The current tranche delivers a usable
full export, with the validation and geometry limitations made visible.
