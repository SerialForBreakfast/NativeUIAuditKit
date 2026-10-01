# FOCUS-RETAINED-NEXT-15 — retained-data tranche ready for review

2026-09-30. Owner: current Codex. Scope: retained diversity, actual trainer-input
audit, conditional changed-data proposal and immediate queue reconciliation.

## Result and next action

Review **four** frames, not another broad eight-screen Home batch:
`review-batch-final/batch.json`. Preview: `prepared-review/preview.jpg`.
The existing editor can use Load preset → `packet15-recorded-598`, `728`, `811`,
or `895`. These contain optional raster proposals with placeholder
`focus:otherFocusable` labels; change labels/bounds and discard poor rectangles.
No focus, content approval, settlement or completeness is asserted. Auto-detect's
existing preview remains available if preferable. Do not load a preset on the
wrong frame. No labeling window was opened or existing review overwritten.

| Frame | Reason to review | Limitation |
|---|---|---|
| 598 | Additional focused poster appearance in My List | Same Paramount design system, not a new source |
| 728 | Blue Watch Now state; contrasts with previously reviewed unfocused outlined state742 | Human must confirm focus; do not transfer earlier Watch Now label |
| 811 | Landscape episode cards with different artwork/context | Dynamic hero pixels do not prove focus movement or settled timing |
| 895 | First circular profile versus earlier reviewed third-profile focus | Small matched-content contrast; not broad new coverage |

These are visual preparer observations, not human-confirmed labels. Four optional
presets contain37rectangles (7/8/20/2); notably the circular profile boxes are not
well covered by the raster proposer. Reuse existing profile layout boxes or draw
the missing circles' rectangular control bounds. Exhaustive frame coverage is a
separate human confirmation, not an automatic requirement for every static crop.
Existing user labels remain unchanged. Initial candidate883 was rejected after
full-image inspection as too similar to the already reviewed profile state;
`review-batch/` and its preliminary outputs are retained but superseded.

## Retained inventory and relationships

Existing CLI `scripts/focus_retained_next.py` scanned the project-local received
E93B12DA recording using source manifest/events/files, not a directory filename
guess. All739frame observations accounted for:625unreviewed candidate pixel
representatives,36repeat observations,8already-reviewed,70transition-excluded,
0blocked. All702encoded image files referenced by these events were byte/size,
decode/pixel and target/dimension checked. Fourteen chronological contact sheets
were visually screened. A distinct image is not necessarily a distinct UI: most
are neighboring Home/Settings/search states, transitions tagged unverified, or
changing artwork. This is not625new useful screens.

The comparison uses the existing40-frame human inventory. All four final images
are nonduplicate candidates there. Selection is deterministic recorded membership,
not a model confidence sort. Originals and existing annotations are untouched.
The older trial02 full recording remains outside the project in the historical
TTR app container; this tranche did not access that container. Its24reviewed local
frames are included in the40-frame reference. Thus discovery is exhaustive for
this702-file received recording, not every historical capture on this machine.

Important: the E93B12DA recording also contains Home, Settings and Photos Welcome
(e.g.313/319), despite its admitted eight-frame subset being mostly Paramount.
Those family relationships connect to development evidence. They are not new
independent validation/training opportunities. No such OS frames were added.
Exact admitted training membership remains928; no evidence here proves existing
training crops duplicate the development pixels. Review whole-session relationship
policy before admitting more; do not claim an independent holdout from session IDs.

## What the trainer actually sees

`results/training-audit-final.json` freezes all928training IDs and333validation IDs,
checks all1261crop byte/pixel hashes, checks input/cache receipts and recomputes
weights through the actual `focus_full_fit_experiment.training_weights` function.
All weights/membership match the frozen protocol. No encoder or checkpoint loaded.

| Population | Controls | Focused / unfocused | Total loss mass |
|---|---:|---:|---:|
| Native/Fixture |790|395 /395|80%|
| Human |138|8 /130|20%|
| Human artwork subset |80|6 /74|13.175%|
| Human buttons subset |4|0 /4|0.449%|
| Human rows subset |54|2 /52|6.377%|

Native presentation strata have133button,26tab,150artwork,86row pairs, each20%
of total loss. Both native labels receive40%each; human labels10%each. Each of
eight human frames receives2.5%total loss, split equally between label buckets.
Thus six human focused artwork crops already carry7.5%total loss; merely repeating
those same images will not supply new appearance contrasts. All928examples appear
every update. OHEM, shuffled minibatches and random image augmentation are not used.

Canonical trace: reviewed/native bounds → existing production16%-expanded256×256
stretch crops → RGB float/255 → ImageNet mean[.485,.456,.406] and
std[.229,.224,.225] → frozen MobileNetV3-small576features →577parameter linear
head. FDR020 reuses the FDR017 cache in order with no new encoder execution.
No new cropper or crop-parity experiment was introduced.

Audit groups named `controlBucket` use the evaluator's control-name mapping, which
is NOT the native presentation-aware sampler mapping. Native tabs/rows may be
implemented by buttons/toggles. The separate nativeAppearanceSupport/LossMass
fields preserve the correct training-stratum interpretation.

## One changed-data experiment proposal, not permission to run

`experiment-proposal-final.json` freezes baseline928IDs, unchanged315development
+18retention IDs, and four prospective frame hashes/session. Exact new control
IDs cannot exist until review; they are explicitly null, not guessed. Proposed
intervention: add only confirmed/admitted static controls from these four frames,
keep native loss80%, distribute human20%over the enlarged reviewed frame set
with label balance and duplicate-pixel weighting. No fabricated temporal pair loss.

Keep the frozen encoder, fresh head seed42, AdamW0.01/weight_decay0.01,
1000updates maximum,300model-seconds and600second process deadline. Fullbatch
becomes928+N admitted controls; the proposal retains928as the baseline batch,
not a valid candidate configuration. Generate only the new feature vectors under
separately approved inference, verify unchanged baseline features, then bind a new
versioned protocol/adapter; never edit FDR020's exact928-member guard.

Preserve original training-only five-consecutive fit stop and unchanged guarded
minimum-development-loss/earliest-tie selection every25updates/terminal. No eligible
snapshot means no selected checkpoint. Compare against retained FDR020 predictions
on identical315development and18retention controls; report artwork recall, Photos
FP, all strata and14complete-frame decisions separately. The existing baseline is
14/27TP,3/288FP,9/14unique correct,18/18retention. Predeclared decision: seek more
than1/12artwork hits without exceeding3development FP or losing retention18/18;
also report every stratum regression. This is an experiment decision, not a new
release gate or an independent test. Stop after one approved candidate and review
failure; no automatic retry, threshold sweep, export or promotion.

Actual trainer preflight was exercised with its real CLI and pinned Python3.13
environment: the existing protocol revalidated inputs and then correctly refused
the occupied FDR020 output (`output_collision`,exit2). The conditional proposal
is deliberately not a runnable protocol; the same CLI rejects it
(`changed_protocol`,exit2). These are rejection evidence, NOT candidate readiness.
Earlier Python3.12 attempts failed because that review environment lacks Torch
metadata; preserved logs document this, and the pinned training environment was
used for the completed checks. No environment installation or new run directory.

**Readiness blockers:** human labels/settlement, production crop QA and exact
duplicates, explicit admission/source relationship review, new cached features and
versioned adapter, then separate run approval. This tranche delivers the proposal
and honest preflight boundary; it cannot make an unlabeled changed corpus trainable.

## Verification and outcomes

-21focused/legacy Python tests pass in `.venv-yolo`; new tests use isolated local
  fixtures for corruption/missing images, wrong target, duplicate sequence,
  preservation, import/proposal integration and changed selection rejection.
-Offline Swift build passes;14XCTest+109Swift Testing tests pass. Logs retained here.
-Actual recorder importer validates all four final members. Presets use existing
  validator/import UI; boxes and flags remain untouched in editor documents.
-Completed OHEM/MPS/productivity top-level entries removed from active Tasks;
  existing CompletedTasks entries preserved. New immediate priority list supersedes
  historical next-action prose; unrelated owners and older unresolved queue remain.

Software: verified offline. Data: four diagnostic frames prepared, no admission.
Integration: local recorder→editor/preset path verified; TTR runtime repair unchanged.
Model: unassessed this tranche; shipped models and existing metrics unchanged.
Coordination: not applicable; no new TTR request or shared metadata publication.

Next human action: review these four frames. Then bind the exact accepted controls,
run crop QA and resolve admission—not another unchanged training run.
