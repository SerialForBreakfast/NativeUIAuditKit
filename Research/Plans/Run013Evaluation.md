# IOS-R013-EVAL — approved local evaluation tranche

## IOS-DIAG-185 — residual geometry and operating errors

Inputs:184sealed evaluation/predictions, unchanged019/020/021reference predictions,
181proposal and184protocol, original full annotations and training ancestry.
Scope: local read-only evidence analysis plus isolated compact reports/code. No
capture, inference, new training, label edits, role changes or promotion.

Implementation: new diagnosis entrypoint calls181's tested box matching/count
reconciliation helpers and the resident Ultralytics `BaseDataset.set_rectangle`
on an in-memory header/label inventory. No loader/cache/trainer is launched.
This reconstructs source-defined batch shapes without modifying sealed experiments;
record resident source hash and configured stride/pad. Report all class counts but
retain full per-image detail only for the targeted operating-error classes.

1. Verify pins/compatible membership/settings; reuse existing full scorer and181
   case-accounting helpers without changing sealed prior code or metrics.
2. Reconcile all38supported class operating counts against the frozen reports.
   Spatially associate sheet/cancel/map FP at IoU.5 across021/022, recording new,
   retained and resolved cases, confidence and source-family support. Associations
   are not authenticated object identity. Keep absent classes unavailable.
3. Account all31remaining fit misses and96development page outcomes against020/021;
   inspect target center/size error by family/placement and train co-occurrence.
   Distinguish geometry from low confidence; do not prescribe thresholds or more
   epochs merely because aggregate AP rose.
4. Audit actual per-class presentations and rectangular input dimensions under both
   sealed proposals. Decide whether a further replay comparison is justified, or
   whether the unresolved geometry requires a different bounded hypothesis.
5. If justified, freeze one proposal from existing train-only support, preserving
   final evaluation roles and the original gates. Do not launch it in this task.

Tests: deterministic count reconciliation, incompatible artifacts, missing classes,
spatial matching duplicates and proposal role/leakage failures if code is added;
one integrated offline Swift pass only when code changes. Acceptance: exact count
reconciliation and complete case lists, explicit confounds, one evidence-backed
next decision with fixed hypothesis/membership/budget. Handoff four outcomes and
next execution prerequisite. Pair with independent180B/C intake if available;
producer delays do not block this local analysis.

## IOS-GEOMETRY-186 — one localization-loss comparison

185accounting found26KitchenSink localization misses; the24trailing misses have
median height ratio1.853 andIoU.4704 at about4.46resized target pixels. Positive
replay reduced some FP but did not solve fit. Test whether increased localization
loss weight improves box geometry without losing operating precision. This does
not prove loss weighting is the cause; preserve an explicit failed outcome.

Inputs:185sealed proposal,022protocol and evaluated fixed-last reference, same432
existing train members and019initializer. One fresh candidate only: change `box`
from7.5to15; leave cls.5,dfl1.5,10epochs/69updates,batch8,640,MPS,AdamW1e-4,
warmup.25,seed42,rect/full-frame/noaugmentation unchanged. Same2GiBoutput cap and
standing no-wall-limit. No fitting of thresholds, new admission or holdout access.

Implementation: extend existing isolated replay adapter; do not change sealed184
code/inputs. Verify exact data, base config and one-field treatment; new paths and
corpus identifier must never collide with prior artifacts. Log next run ID before
launch, retain fixed-last and actual optimizer-event audit. Reuse022predictions
and unchanged019/020gates; score all216fit/96development/2400retained images.

186binding creates a preserved preparation protocol through179, then derives a
new execution protocol without overwriting the prepared one. Only box loss and
isolated paths/corpus identity differ from022. New execution sources bind185proposal,
186adapter and022reference; recheck each before train/infer/report.

Acceptance: real preparation/training/export/scoring succeed with focused rejection
tests and integrated offline checks; report the original14gates,31prior fit-case
changes and all supported-class deltas plus FP counts. Success requires all original
gates, not simply improved medianIoU. Failed gates yield diagnosis, no automatic
weight sweep or longer run. No export/CoreML/device comparison/promotion in scope.
Software/data/integration/model outcomes remain independent. Training execution uses
standing local authorization once proposal/preflight/logging pass;185itself does
not launch this run. Next after success: independently scoped qualification, not DS-G8.

## IOS-REPLAY-184 — positive-context comparison

Implementation binding: a thin184adapter creates the179-compatible proposal from
sealed181membership, redirects only owned output/config paths in memory, and pins
the adapter/canonical proposal/control protocol in an additional launch binding.
Reuse179prepare/train/infer/report verbatim; no edits to sealed179files or outputs.

Input:181sealed proposal e1f0b6a4dfddd4ecd42ebf499db0ecc8ef25867bbbd8949021078f401dc5882c.
One comparison,432train members:216fit +136unchanged positive replay +80new train
positives replacing empty fillers. New positives:39KitchenSink,24RichContentFeed,
17SystemNavigationShell. Selection used training labels/support and source family
only, never evaluation failure ranking. All full labels and original roles retained.

Extend the existing replay workflow through a new bound configuration/entrypoint,
not edits to sealed179sources or artifacts. Freeze local staging/output, verify all
image/annotation/label hashes, decode images, check coordinate validity, ancestry,
pixel leakage, initial weights, source pins and≥8GiBfree. Proposal config still
references old output/data and is deliberately not executable; resolve fresh paths.

Fresh019last optimizer,10epochs,640,batch8,workers0,seed42,AdamW1e-4,nbs64,warmup.25,
cosine,AMPoff,noaugmentation;540minibatches/69events. Preserve fixed-last and all179
gates. Extra page/button occurrences in added full annotations are an intentional
composition change, not identical total target exposure. Rectangular batch shapes
can differ.2GiBoutputs, standing no-wall-cap. Record next run ID before launch;
do not reuse021weights or launch an automatic retry. Preserve failed candidates.

Tests: source/role/geometry/hash/collision/schedule failures and actual entrypoint
integration. Full offline Swift checks once final code is integrated. Complete
216fit/96exposed-development/2400retained evaluation, reusing control predictions.
Acceptance is the unchanged179development gate vector plus all-class deltas and
case accounting; success alone does not establish DS-G8 or permit production claims.
Failed gates yield a diagnosis/next proposal, not an automatic epoch extension.

## IOS-REPLAY-181 — exposure and operating-error diagnosis

Execution refinement: reconcile every retained image/class against the existing
scorer. Match false-positive boxes spatially at IoU.5 between arms, reporting this
as spatial association, not object identity. Preserve full case lists rather than
the scorer's truncated examples. Pair this local diagnosis with receipt-only intake
of TTR's new artwork pilot; its schema4/v5 semantic qualification is a separate task.

Post-audit decision: do not prescribe more epochs when new false positives already
have high confidence. Freeze a same432/10epoch comparison replacing only80empty-label
replay fillers with80nonempty existing-training images. Keep216fit and136positive
replay members, all labels, initializer, thresholds, schedule and gates unchanged.
Select from train only, excluding original432IDs and pixel duplicates/cross-role
overlap. Greedily maximize summed inverse current per-class image support over all
available classes, then minimize selected family support, then imageID. Never rank
by evaluation errors or select held-out families from their failure counts. This
tests broader labeled context versus empty fillers, not proof that negatives are bad.
Output one sealed exact-membership proposal; launch requires its normal preflight.

Inputs: sealed019/020/021prediction artifacts, unchanged432-member179proposal,
original173training membership and fixed .25/.5 operating thresholds. Reuse all
existing inference. Evidence:179retained AP improves to.896409, yet operating sheet
FP459and cancelFP259 regress, and all33fit geometry misses occur in KitchenSink.

Implement one batch case comparison: verify identical image/settings/category
identities; enumerate introduced/resolved/retained FP and misses for sheet/cancel,
page and scroll; include confidence/IoU/size and family/placement support. Do not
infer all-case behavior from the first100error examples. Reuse complete predictions.
Audit train-only replay class balance,80negative filler contribution and exposure:
021halved placement presentations relative020 and changed LR staircase. Do not
attribute the result exclusively to negative fillers or learning rate without evidence.

Deliver a ranked diagnosis and at most one revised experiment proposal with exact
existing-training membership, target exposures, complete saved optimizer/schedule
settings, fixed-last selection and original retention gates. Decide whether to
preserve exposure or change sampling based on the case audit; record confounds.
No new capture, labels, downloads, public API or evaluation-to-training admission.
Standing training authority applies after qualifying the concrete proposal, not an
automatic repeat of021. Output≤2GiB, no speculative sweep; model promotion requires
all applicable gates. Tests cover incompatible artifacts, incomplete predictions,
case-count conservation and missing class support. Required offline Swift checks
only for integrated code changes; reuse unchanged prediction evidence.

Acceptance: complete case accounting reconciles exact aggregate counts, unsupported
metrics stay unavailable, and the next proposal tests a stated hypothesis rather
than merely increasing epochs. Next action is one qualified logged comparison;
worker180results remain an independent transition-model diagnostic lane.

## IOS-FIT-176 — retention diagnosis and mixed-replay proposal

### IOS-REPLAY-179 execution refinement

Resident trainer inspection found nbs64/batch8 accumulation:540mini-batches do not
mean540optimizer updates. Replay179 uses432images/10epochs and warmup.25epochs,
matching020's14warmup batches and total540mini-batches; compare simulated optimizer
event indices and record actual step events. Preserve the current native cosine
epoch schedule, but report its10-versus20epoch stair-step difference explicitly:
this is a pragmatic compute-matched mixture candidate, not exact schedule isolation.
Keep the176sealed membership unchanged;80hard-negative family images represent
explicit negative evidence for a false-positive problem, not an optimal or unbiased
sample. Full positive class coverage and all annotations remain included. Validate
ancestry using original173split/family/parent lineage before launch; inherited
train overlap among related variants is allowed only within train, never evaluation.
Reuse resident Ultralytics YOLO trainer and eval exporter; do not modify pinned175
sources. One179driver handles prepare/train/infer/report and records callbacks;
live optimizer steps must match the pinned simulation. Existing gates stay fixed.

Use sealed175predictions and173training membership only; no fresh inference,
capture, threshold changes or training in this diagnosis. Verify current seals and
all selected label/image hashes. Case-account sheets and scroll indicators rather
than infer operational recall from AP. Audit omitted training support and placement/
family confidence; scale2/light and scale3/dark remain coupled.

Proposed next comparison: retain all216balanced175training examples and select216
distinct replay images from173's existing train partition, preserving full labels.
Selection uses training labels only, never retained-test errors or scores: target
16images per supported class absent from175; greedily cover largest remaining
deficit sums, then smallest aggregate current class support, then image-ID tie
break. This same ordering fills remaining slots when deficits reach zero. Cap216;
if deficits remain, report them and block
launch rather than silently change the quota. Unsupported webContent stays absent.
Exclude175IDs and duplicate pixel identities, retain ancestry and original roles.
Freeze IDs/refs/selection version as a proposal, not a new corpus admission.

Before any future run, verify full membership, no cross-role pixel/ancestry leakage,
resident data and output isolation through the existing prepare/train/eval entrypoints.
Use Run019fixed-last, fresh AdamW,640,batch8,seed42, existing full-frame settings;
432images for10epochs gives540minibatches, matching020's216×20 (69optimizer updates).
This is a compute-matched mixture comparison, NOT equal target-example exposure:
placement examples appear half as often; batch composition/rectangular grouping and
epoch-based LR/warmup details must be recorded and reconciled before claiming a
single-variable causal ablation. If matching schedule requires code changes, test
and pin them first. Do not retroactively call an unmatched schedule equivalent.
One candidate,2GiB output cap, no automated extension; no run ID until execution.

Development acceptance:≥90%page recall in each training placement; retain at least
Run020's59/96development page hits with≤4FP; retained overall AP50≥Run019 .882978,
sheet AP50≥1.0 and sheet operating TP≥24 withFP≤218, scroll AP50≥.3481,
cancelAction TP≥76/FP≤73 and mapView TP≥100/FP≤0. Report every class delta, not
only gates; use numeric tolerance1e-6 for exact metric comparisons. These stringent
development criteria may reject the candidate and are not production/DS-G8 gates.
If no mixture supports these goals, diagnose before another comparison. Existing
evaluation populations remain exposed diagnostics, never newly independent holdouts.

Deliver complete case/coverage accounting, frozen replay proposal and exact blockers.
No automatic training launch follows this planning/diagnosis packet.

## IOS-FIT-175 — balanced training-fit diagnostic

Hypothesis: concentrated exposure to admitted native placement examples can fit
off-center page boxes under the current architecture/targets. This tests learnability,
not an isolated epoch-versus-sampling effect or a production candidate. Select all
complete leading/center/trailing triads keyed by parent group/tint from174's exact
264training members:72triads/216images,72per placement. Preserve full annotations;
do not invent missing family/theme/tint cells or bring duplicate controls back in.
Run019fixed-last is initialization, fresh optimizer state, no resume. One run,
20epochs,640,batch8,MPS,seed42,workers0; existing full-frame AdamW1e-4/cosine/
warmup.5/bias1e-4/AMPoff/no-augmentation settings. No OHEM. Budget2GiB, verified
local space, standing no-wall-cap. Record Run020 before launch. No automatic retry.

The diagnostic config points train and val at the same selected training pixels
solely for in-sample monitoring. Clearly mark every trainer validation number as
training fit, not independent evidence; no existing corpus split changes. Select
fixed-last only. At terminal success validate saved settings,20finite epochs and
source/checkpoint/data pins, then use existing exporter/scorer on216fit images,
96exposed probes and2400retained images; reuse019predictions. Report placement
TP/FP/FN/AP, box-height and confidence dispositions plus cancelAction recall/FP.
Predeclare fit success as≥90%recall in each placement at.25/.5; failure means
investigate assignment/loss/geometry, not extra epochs. Fit success does not mean
generalization; retained regressions still block candidate use. No promotion,
threshold tuning, capture, changed labels or test-to-training role transfer.

Tests cover deterministic triads, incomplete/duplicate/changed roles, config
monitoring identity, epoch/settings checks, collisions and preserved failed runs.
One integrated offline Swift build/test; actual prepare/train/infer/report evidence.
Deliver one concise handoff and one next evidence-backed experiment proposal.

## IOS-DIAG-174 — training-fit and retention diagnosis

Implementation uses one `diagnostic174.py` prepare/infer/report entrypoint and the
existing exporter, matcher and scorer. The new input manifest contains only the
264admitted unique rows, with full labels and original hashes; it is diagnostic
training membership, not a new evaluation split. Bind source and artifact hashes
before inference and reject collisions or changed evidence before reporting.

Outcome: distinguish failure to learn the new native placement examples from a
training-to-probe rendering/scale/context gap, and explain Run019's retention tradeoff.
Inputs: sealed172admission/173membership, fixed017/019checkpoints, existing173matched
evaluation and171case accounting. Verify hashes and exact264unique training IDs.
Use standing local evaluation authority; no simulator, new labels/data roles,
training, threshold tuning, CoreML export or promotion. Cap new artifacts at1GiB.

Reuse the existing explicit-manifest prediction exporter and strict positive-area
validation. In one batched invocation per checkpoint, score all264new training
frames with frozen640/settings; reuse existing control/candidate predictions for
96probes and2400retained inputs. Do not recapture or re-infer unchanged evaluation.
Report complete accounting, page TP/FP/FN/AP and absent/low-confidence/wrong-box
dispositions at confidence.25/IoU.5. Stratify training by actual placement/tint,
family and recorded scale/theme cells; report coupling rather than imply independent
axes. Compare source and resized box dimensions and image context with the probes.
Oracle-best-IoU diagnostics must stay labeled as oracle, never model decisions.

Independently audit cancelAction matched cases across017/019: lost/gained true
positives, removed/new false positives, confidence/rank and competing classes.
Do not equate fewer false positives with preserved recall or AP. Ground conclusions
in case IDs and stored predictions; visual inspection is targeted to anomalies.

Acceptance: every264training and96probe case accounted for; existing2400case totals
reconcile with173; hash/membership/corruption/empty-prediction tests and actual
CLI integration pass. One integrated offline Swift build/test if code changes;
reuse unchanged evidence otherwise. Deliver one report with failure dispositions,
wall timings, supported versus unresolved explanations and a single next experiment
proposal. Strong training fit plus probe failure supports a domain-gap hypothesis;
poor training fit requires representation/optimization diagnostics first. Neither
case automatically authorizes more epochs or admission of exposed probes. Keep
training-fit, development evaluation and independent qualification distinct.

## IOS-PLACEMENT-173 — one matched native-placement training candidate

Prerequisite:172complete capture/annotation/ancestry audit and explicit accepted
new-versus-reused membership. Do not add redundant controls twice, use rejected
trial images, or substitute partially annotated development probes. Standing local
training authority applies; no further capture, promotion or automatic sweep.

Freeze one new corpus export: repaired165training plus only172's accepted unique
rows, unchanged2800validation/2400test and exposed96page development probes. Reuse
the existing export/label parity checks and verify every resolved input byte before
launch. Keep training-only related groups and the exact deduplication receipt.
Stage bulk only on verified permitted storage; preserve the source corpus/model.

Hypothesis: native placement/tint coverage improves off-center page detection
without the cancelAction/mapView false-positive growth seen with translation. Use
fresh Run013 initialization and Run017's fixed five-epoch configuration with no
translation, same optimizer/warmup/batch/resolution and fixed-last selection. Only
eligible training membership changes. Allocate the next run ID at launch and record
exact resolved configuration, dependency versions, source/checkpoint/data hashes,
output budget2GiB and the standing no-wall-time-limit training override beforehand.

Evaluate the fixed last checkpoint using170's explicit positive-area export policy
and custom metric implementation on identical retained inputs. Reuse the verified
017control artifacts; distinguish official trainer validation from custom reports.
Report overall/per-class AP, page position/renderer strata, operating TP/FP/FN,
low-confidence versus absent/localization failures, latency and complete accounting.
Include cancelAction/mapView false-positive case deltas, not only their recall.
Record wall time separately for combined/page prediction export, including input
validation and model loading. Do not label this model-only latency or compare it
to the reused control's absent/unmatched timing. Failed exports get no successful
timing receipt. Pure cold/warm deployment latency remains a later matched check.

Success for this development experiment requires improved left/native page hits
versus017with no increase in either regressed class's operational false positives
and no retained aggregate AP50 loss. A partial tradeoff remains a diagnosis, not an
accepted replacement. Even success is not DS-G8 or independent final qualification:
the exposed probes are development evidence and withheld class support is incomplete.
No automatic extra epochs, threshold tuning, CoreML export or promotion. Next action
is driven by these matched outcomes, not by training completion alone.

## IOS-NATIVE-172 — one qualified placement/style generation batch

Inputs:171sealed288-frame plan and native159 full-frame recipes/qualified measurement
path; repaired165 corpus lineage and unchanged validation/test manifests. Outcome:
qualified full-annotation training-only variation, not a trained/promoted model.

Implementation correction after first native qualification: post-layout transforms
were overwritten during rendering (all leading/trailing pixels remained centered).
Preserve that24-frame failed batch. Opt-in template-owned layout must set position
and tint during normal UIKit/SwiftUI layout; the capture closure only observes it.
It records resolved tint components and requires subsequent independent visible/
hidden pixel measurement; no global environment switch or production library API.
Qualify24cells first, retrieve/audit them, then run the remaining264without rebuilding
or recapturing accepted cells. Both outputs retain one frozen288-member ancestry.
No first-attempt frame was accepted. Corrected qualification uses a new r2 namespace.
R2 moved controls correctly but KitchenSink's oversized405-point content extended
six points beyond each side of the393-point capture, shifting requested margins.
R3 explicitly sizes the opt-in placement row to the recorded capture width; keep
the two-point center agreement check unchanged. R1/R2 remain rejected evidence.
R3's launch failed before test entry with SpringBoard Busy. After fresh shutdown
state verification, explicitly boot/wait the same simulator; attempt04 reuses the
unchanged R3 build only if its app output is absent. Require Booted preflight for
both phases; no restart/reset/re-signing. Preserve the failed launch receipt.
Attempt04 confirmed the fixed-width row was leading-aligned within the oversized
parent, still six points off for all positions. R4 centers that capture-width row
within the parent using layout (no offset); attempt05 must pass the unchanged gate.
Attempt05 passed24/24independent geometry/full-annotation/duplicate checks and visual
overlay review. Actual tint metadata retains UIKit white1.000000119with1e-6numeric
roundoff tolerance; geometry tolerance remains unchanged. Remaining264are captured
using the same build/runtime; full-corpus duplicate/ancestry checks precede admission.
Admission refinement from actual qualification: a centered semantic-label frame is
pixel-identical to its existing training parent. Still account for all288planned
captures; do not count an existing example twice. Exact same-parent training overlap
may be retained as a redundant control only after annotation equality. Exclude it
from new training membership and report new/reused counts explicitly. Other overlap,
cross-split duplication or conflicting annotations blocks admission. This does not
reduce capture coverage or turn duplicate frames into additional training support.

1. Extend existing UIKitControls/KitchenSink rendering with opt-in placement/tint
   fields, preserving defaults. Resolve leading/trailing against layout direction;
   enforce visible-control safe margins and independently measure rendered geometry.
   Keep all scene annotations, not only page-control boxes. Source/build pins change
   explicitly; do not reuse native159 build qualification for new code.
2. Plan/preflight without mutation; freshly verify the exact approved iOS simulator,
   runtime/toolchain, app identity, disk capacity and unique outputs. Setup/install
   uses the existing simulator authority only after checking current instructions;
   no new runtime downloads, service resets, target substitution or TTR dependency.
3. Qualify the first complete24-cell matrix (four observed source cells×three
   placements×two tints), checking visible/hidden differencing at the existing
   one-pixel tolerance and all full-scene annotations. Inspect representative
   overlays and anomalies; requested style is not proof of rendering.
4. Continue the remaining planned groups in the same owned runtime session with
   persisted completion accounting. Preserve failures/partial output; resume only
   missing groups after state/cleanup review. Do not repeat accepted qualification
   frames or alter quotas. Retain the source scale/theme confounding explicitly.
5. Audit every image/annotation/hash, crop geometry, source ancestry, duplicates and
   train/evaluation separation before admission. Keep a new corpus version; never
   overwrite the165prefix or move development/evaluation groups into training.

Tests: unchanged defaults, placement bounds including RTL, unknown tint/placement,
wrong target, output collision, partial completion, changed source, geometry drift,
duplicates and split contamination. Focused tests then one integrated offline Swift
pass; genuine renderer checks separately. New artifacts limited to2GiB with space
preflight; stop rather than silently raising the cap. Freeze hashes, source/build,
accepted/rejected counts and cleanup evidence in one handoff.

Acceptance:288accounted recipes with full-frame labels, all required cells qualified,
zero accepted duplicate/split leakage, preserved evaluation membership, healthy
postflight, and explicit software/data/integration/model outcomes. If rendering or
integrity fails, preserve evidence and diagnose; no automatic training. Next is one
bounded matched candidate against the retained control, measuring page placement
and cancelAction/mapView false positives as well as aggregate AP. Model gates remain
unassessed in172; exact candidate initialization/configuration is frozen afterward.

## IOS-DIAG-171 — explain residual failures and freeze one native coverage batch

Inputs: completed170 sealed report/four prediction artifacts and unchanged96probe,
2400retained manifests; native159's training-only900-member catalog. No inference,
training, capture or promotion in this diagnostic/planning packet. Preserve all data.
Use existing validation and IoU code to classify every page probe as operating hit,
low-confidence correct geometry, localization miss, or absent candidate. Report all
position/renderer cells, not only overall AP. Audit every cancelAction/mapView truth
and operational false positive with exact one-to-one matching and case identities.

Independent companion: generate a deterministic, source-pinned native batch catalog
using48existing training recipe groups (twelve per observed family×scale/theme cell), each with
leading/center/trailing placement and two explicit tint policies:288planned frames.
The source catalog couples scale2 with light and scale3 with dark; it does not
contain eight independently crossed cells. Preserve and report this confounding,
rather than claiming independent theme/scale coverage or inventing source members.
Keep related variants train-only; no exposed probe reuse, new holdout claim, or
automatic admission. Generator must preserve full-frame annotations, measure visible
indicator pixels using qualified hidden-control differencing, and verify actual
placement/tints before eligibility. Reuse existing UIKit templates and capture
entrypoint; do not turn partially annotated composition probes into full-frame data.
Batch capture is a subsequent integrated renderer extension/qualification assignment,
with one setup, unique outputs, raw evidence, complete accounting and no silent retries.

Acceptance: actual artifact hashes/semantics validated;96probes fully classified;
both regressed classes accounted at unchanged.25/.5; plan deterministically contains
288unique IDs in48train-only ancestry groups with all required cells; tests reject
missing/altered evidence and incomplete source coverage. One offline build/test pass.
Outcome selects targeted data work versus threshold-only tuning without changing the
evaluation threshold. No final-model gate is assessed.

## IOS-TRANSLATION-170 — one matched spatial-augmentation arm

Evaluation repair after terminal Run018: retain failed first exports. Resident
Ultralytics clips detections to original bounds and can return zero-area edge boxes.
Introduce opt-in `discard-zero-area-after-native-clipping-v1` postprocessing for
both017/018 under a new settings hash and isolated evaluation destination. Retain
every rejected detection and per-image input/output counts. Only finite, in-bounds,
ordered zero-area boxes may be discarded; invalid class/confidence, inverted,
nonfinite or out-of-bounds boxes remain failures. No additional clipping, confidence
change or dropped images. Strict prediction-artifact geometry remains unchanged.
Re-export both arms, including all96probes, under this identical policy; validate
rejection accounting before scoring. Results describe the explicit filtered pipeline,
not unchanged historical metrics or proof of CoreML parity. Training is not repeated.

Hypothesis from169: centered-only training encourages location dependence. Reuse
completed017 as control; fresh Run018 from the identical Run013 initializer and
repaired14540/2800/2400membership, five epochs and all corrected165settings, changing
only resident Ultralytics translation from0 to.35. This translates both x and y;
it tests spatial augmentation, not an isolated horizontal effect. No color, scale,
flip, mosaic or renderer changes. Fixed-last, same96development/2400retained metrics.

Before launch validate the actual resident RandomPerspective image/box path,
including partial/fully clipped examples and per-class target filtering. Standard
augmentation clips images and boxes and drops overly truncated/tiny targets;
report that behavior explicitly, not a claim of complete-control preservation.
Do not invent full-frame labels for truncated objects. Preserve original corpus,
no physical operations or new native generation. Reuse existing trainer with an
explicit opt-in; its existing full-frame profile remains unchanged by default.

Freeze initializer,source,dependencies,all staged bytes,control/eval references,
settings and budget before execution. One arm,5epochs,<=2GiBnew outputs,>8GiBfree,
standing no-wall-cap; no sweep/retry after failed run. Reject data/config collisions.
Acceptance: terminal five-epoch receipt, coordinate/clipping tests, complete matched
evaluation including native/position strata and existing-class regression. Improvement
must recover left-position detection without concealing retained-class losses;
development gain alone cannot promote or establish DS-G8.

## IOS-COVERAGE-169 — page support audit before another training campaign

Read the exact017 overlay and hash-verify every training label. Account for all
14540training members and all page-control boxes, including empty labels. Report
family/repaired lineage, normalized center/size ranges and horizontal thirds.
Renderer classification requires generator/source evidence; family names alone
must not become asserted rendering truth. Compare96development probe boxes with
training support without admitting them to training. Use label hashes and existing
pixel audits; no redundant image decode sweep or new inference is required.

Outcome: frozen audit evidence and one justified next comparison, distinguishing
data coverage from architectural claims. Validate malformed/nonfinite/out-of-range
labels and boundary-bin behavior. No capture, new roles, training or promotion in
the audit. Existing native24 source intake is the independent companion when its
source prerequisite arrives; do not duplicate a blocked producer request.

## IOS-PAGE-168 — isolate position and renderer sensitivity

IOS165 diagnosis finds repaired017 has no exported page candidate on all48left
compositions; all18operating hits are centered non-native controls. Native UIKit
has41/48absent candidates and zero operating hits. These balanced catalog axes
are development probes, not a new independent benchmark. Do not assume longer
training or resolution alone repairs this.

Next bounded experiment: reuse frozen96image/label membership and fixed017weights;
compare existing640long-edge inference to one1280long-edge inference through the
existing exporter, with a separately versioned settings contract. Keep confidence,
NMS, class map and coordinate restoration identical. No training, recapture or
data-role changes. Pin source/settings/artifact hashes before inference, reject
output collisions and missing members. Report full AP/FP/FN plus renderer,
horizontal-position, theme and family strata; latency and memory separately.
Higher resolution changes preprocessing, so this is an explicitly controlled
intervention, not a compatible same-settings reference comparison or promotion.

Acceptance: all96members accounted for; existing640results reused; coordinate
restoration and settings-identity tests pass; no relabeling probe examples into
training. Decide whether resolution recovers native/left cases before allocating
new corpus generation. If absent cases remain, audit training position/renderer
support and design one coverage-balanced comparison with fresh final groups.
Budget one inference arm,<=512MiBnew outputs, resident dependencies only.
Independent companion: native24 contract intake when exact producer source arrives;
its absence cannot block this local experiment. No production changes.

## IOS-REPAIR-165 — full-corpus repair comparison

Two fixed fresh fine-tunes from Run013best SHA88c3cffb51b0b29dd71672fb64f6e60be56757e6de507886ef2f5c2ff86dd9b7:
Run014 prior r8, Run015 native159overlay. Full14540train, identical2800val/2400test;
900native replacements differ in pixels and labels, so this estimates the repair
bundle effect, not a labels-only causal effect.666manual repairs remain in both.
Freeze all refs, dataset/source hashes and configuration before execution; verify
all bytes against prior audits, reuse decoded-pixel checks bound to those bytes.
Stage explicit project-local image/label symlinks with isolated loader caches;
no source corpus writes, migration, alias replacement or default dataset change.

Use existing train_ios_model.py opt-in full-frame fine-tune profile:5epochs,640,
batch8,MPS,workers0,seed42,AdamW lr1e-4/lrf.1,cosine,warmup.5epochs,patience0,
all visual/geometric augmentations disabled,rectTrue,AMPfalse,OHEMoff,cachefalse,
plotsfalse,save_period-1. Fixed-last checkpoints for comparison, no selection on
test. Existing profile remains unchanged. Sequential arms, no-wall-limit standing
approval,<=4GiBnew model outputs and sufficient capacity before each launch.
No downloads, paid compute, private transfer, export or promotion. Validate actual
MPS availability before corpus staging; output collision rejects; checkpoint must
be an explicit existing local file, never a model-name download fallback.

Evaluate both fixed-last candidates with existing prediction/export/AP tooling on
identical2400retained test and96page development compositions; compare with retained
Run013reference. Report page AP/geometry and per-class retention, withheld2000and
within-family400separately; unsupported classes unavailable. Test has been exposed
to development; no independent release gate or DS-G8 claim. Missing predictions
block comparison, not silently reduce membership. Failed models remain preserved.
Acceptance: two terminal runs, full image accounting, matched reports and gates,
config/source/data pins plus required focused/offline checks. A live long run is
in progress, not completed. Big Dog163remains an independent asynchronous diagnostic.
Consumer acceptance additionally binds each receipt to its exact arm's fixed-last
path, saved args and five sequential finite epoch rows. Exit0alone cannot qualify
a shortened run or another arm's checkpoint. Verify without modifying live outputs.

Page geometry reporting uses the same96single-page-control compositions and the
existing IoU implementation. For each image report best-IoU candidate at export
threshold and separately at fixed operating confidence.25, with deterministic ties,
IoU, width/height ratios, signed center errors and center-inside. Explicitly count
missing candidates; medians describe candidate-present cases only. Best-IoU is an
oracle diagnostic of available geometry, not the detector's selected prediction.
Keep operational AP/FP/FN alongside it so low-confidence or duplicate boxes cannot
masquerade as detection success. No new inference, threshold tuning or label change.

Correction before first validation: initial Run014inherited warmup_bias_lr.1 despite
lr0.0001. Resident Ultralytics trainer line482uses that bias-specific rate explicitly.
Interrupted014(exit-2) and prevented015; preserve both original launch/log evidence.
Corrected Run016prior/017repaired start fresh from the same Run013weights and same
staged corpora, with warmup_bias_lr=.0001. No checkpoint from014is used. All other
profile settings, epochs, data/evaluation and budgets unchanged. Separate corrected
launch seal; original preparation is reused, not regenerated. Test all optimizer
warmup rates against the intended ceiling, not just displayed base lr. This is a
configuration repair before model-result selection, not a hyperparameter sweep.

Assigned by maintainer 2026-09-27; owner: current NUIAK evaluation worker.
Parent: TASK-6a-11. This is evaluation, comparison and documentation only.

Freeze Run013 epoch-91 best.pt and r7 manifest/YOLO exports, category map,
runtime and evaluator source identities. Audit every member through source
manifest, PNG decoding, byte/pixel hashes, sidecar-to-YOLO correspondence and
split/family checks. Preserve all source data and prior reports.

The 2,000 original r6 test members are a withheld-family diagnostic; the 400
addon test members share all four families with training and are within-family
diagnostics. Report each separately, plus a supplemental combined score.
homeIndicator, unknown and webContent lack test support. Historical testing and
failure-driven development mean the reused r6 cases are not an untouched final
release challenge. No DS-G8 pass can follow from this tranche's partial coverage.

Reuse eval_phase6a.export_predictions and prediction-artifact-v1, explicitly
binding checkpoint and manifest. Settings remain 640, confidence0.001, NMS0.7,
max300, MPS, no augmentation. Reuse compatible Run009 retained predictions on
the exact r6 subset; otherwise perform one explicit Run009 evaluation of that
subset. Recompute both sides using the existing all-point interpolated AP
implementation in eval_ios_r6_baseline; label it custom VOC-style AP, not official
Ultralytics/COCO AP. Report AP50/70/90/50:95 and P/R, misses/FP at confidence0.25,
IoU0.5; include per-family support and geometry results. No threshold tuning.

Only additive local driver/tests and minimal existing-evaluator changes are
needed; no public API, taxonomy or sidecar schema changes. Reports, frozen
manifests, logs and source hashes go to reports/work/IOS-R013-EVAL; configured
caches/temp stay in-project. Missing/corrupt inputs stop inference; failed
prediction rows prevent metric qualification without silently reducing membership.
Known family overlap is reported, not repaired by moving source data.
Explicit input manifests may include optional imageSHA256/labelSHA256 fields;
when present the loader rejects changed bytes before inference. Legacy manifests
without these additive pins remain readable. All source splits receive normalized
label validation. MPS availability and inference elapsed time are recorded locally.

Acceptance: complete2,400-member accounting; separately reported populations;
strict compatible baseline comparison; per-class/family errors and coverage;
focused offline tests plus offline Swift build/test; concise handoff with four
outcomes, all acceptance evidence, exact limitations and prioritized next assignment.
Research/CurrentState, ExperimentLog and Tasks are updated. Local iOS findings
need no SMB publication unless they change TTR's next action. No training,
export, promotion, device capture or new worker is authorized.

## IOS-LABEL-AUDIT149 — follow-up under standing backlog authority

Verify frozen preflight/category hashes and every r7 exported label against its
inventory hash; summarize all41class supports by split/family. Quantify target
box width/height/aspect and short edge at640/1280letterboxing for pageControl,
scrollIndicator,imageView,listRow,toggle,secondaryButton,cancelAction. These are
geometric scales, not measured alternate-resolution accuracy or latency.
Read hash-matched button-role sidecars and retain available text counts, explicitly
marking absent text. Pin current relevant generator source; distinguish source
inspection from proof of which renderer produced historical pixels.

Deliver a complete coverage matrix, source-backed geometry/semantic hypotheses
and actionable new-development/final-family specification. No changed taxonomy,
relabeling of retained cases, training or renderer execution in this audit. Exact
content/family isolation and production gates remain required for the next corpus.

### IOS-NATIVE-PAGE150 — next model-improvement tranche

Prerequisite149now verified. Do not repeat38's40-image resolution sweep or39–42's
666manual-dot repairs. Current r8 has900native container-sized boxes and no page
validation. Record the target policy as the intrinsic rendered page-indicator body,
including any visible native backing, excluding blank full-width layout space.
Do not infer a hit target from this body or change public detector/category APIs.

1. Inventory qualified installed iOS runtime/GeneratorRunner artifacts and exact
   simulator identity before mutation. Standing simulator authority applies, not
   automatic installation/download/reset/signing changes. If unavailable, implement
   source/tests and preserve native qualification as a specific dependency.
2. Reuse NativeUIPageControlView/UIKit page-control renderer. Qualify public intrinsic
   sizing and measured frames against native pixels; do not use private subviews or
   hardcoded dot formulas as unverified truth. Test3/5/7pages,first/middle/last selection,
   light/dark, two canvas widths in one serialized batch. Capture actual clipping,
   rendered backing and bounds; reject ambiguous layouts. Keep this development-only.
3. Build fresh validation compositions independent of the4page-control training
   families and the oldGallery/Onboarding diagnostics: reader-footer and compact
   gallery-inspector layouts, manual/native treatments, varied count/size/placement,
   separate generator families. Freeze the catalog before capture;96development
   examples covering2compositions×2renderers×2themes×3counts×2positions×2seeds.
   New development data is not a final-release holdout; all related variants grouped.
4. If native geometry qualifies, regenerate the exact900native training IDs into a
   new version, retaining r8 and its666manual fixes. Full byte/label/split/duplicate
   audit, unchanged5200old evaluation members. Never edit hardlinked originals.
5. Before a candidate launch, register one matched fixed-budgetRun013-initialized
   comparison with exact admitted membership, settings and storage pins; evaluate
   new validation and old diagnostic families separately. Select neither architecture
   nor threshold from final tests. Define compute/epoch budget from actual available
   worker/local throughput, not a new arbitrary150epoch default. No promotion unless
   independent coverage and existing gates pass; preserve shipped weights.

Full41class challenge remains separate: reserve unrendered recipe-family implementations
for each class before further tuning. The149coverage matrix identifies missing
validation pageControl/progressView/secureField/textField/unknown/webContent and
test homeIndicator/unknown/webContent. Unknown needs explicit reject/abstention
semantics; webContent needs truthful offline source support. Do not fill these gaps
with fake labels, same-family seed splits or a silently reduced taxonomy. Record
generation/admission blockers per class, not a global stop for qualified experiments.

Execution150: Xcode27.0/27A266a and installed iOS26.5 exact UUID
F3EF9DB8-0B0F-4757-B653-D1628269F6FF; scope includes the matching owned GeneratorRunner
test build/install/launch and its normal Simulator/container storage. No download,
service reset, signing repair or unrelated target. Project-local DerivedData, logs,
xcresult and retrieved evidence; new app Documents/native-page150 output only.
First36-case probe:3/5/7pages × first/middle/last × light/dark ×375/430points.
Use existing ScreenshotCapture/AnnotationWriter and native control with fixedSize,
record measured frame and public size(forNumberOfPages:) separately. Apple's
[API contract](https://developer.apple.com/documentation/uikit/uipagecontrol/size%28fornumberofpages%3A%29)
describes minimum control size, not a guaranteed tight visible-pixel box. Qualify
before altering current native templates. Capture bound120seconds, <=256MiB,
unique output required; retain failed observations. No arbitrary dot formula.

Follow-up150after rejected intrinsic hypothesis: qualify a public control-local
transparent render/alpha bound, not private subview geometry.72cases: twoOS-profile
canvases ×3counts ×3selections ×2themes ×2styles(disabled automatic background,
interactive prominent backing). Compare measured alpha bounds with actual composed
pixels from existing captureUIKit. New native-page150-alpha output;120s/256MiB,
same exact simulator and owned build/runtime scope. Do not integrate into production
annotations if backdrop effects or missing alpha fail correspondence. No900rewrite
or96corpus generation before this test passes.

Retained-evidence assessment154: style-specific proposal (alpha for disabled
automatic, public intrinsic frame for interactive prominent) matches72/72existing
composed probes within0.5pt. This is hypothesis support, not production qualification:
prominent public size reused from the earlier same-runtime3xprobe, and actual2x
control bounds were not recorded. Next capture should record actual public frame,
style, interaction, scale and alpha together inside the96real development
compositions, avoiding another isolated-probe-only cycle. Gate each composition
before annotation admission; reject unsupported styles rather than use a universal
padding subtraction. Existing900training boxes remain untouched until that passes.

COMPOSE155executes the frozen96matrix in one batch: reader-footer/gallery-inspector
×native/manual×light/dark×3/5/7pages×left/center placement×seeds7/19. Seed controls
page selection/content; native7disabled automatic, native19interactive prominent.
Use existing NativeUIPageDotsView for manual treatment and existing UIKit capture.
Each scene captured twice, indicator visible then hidden, retaining both original
PNGs and actual frame/style/scale telemetry. Differential measurement is restricted
to this controlled removal, not model-produced labels; unexpected changes outside
the measured control area reject the pair. Exact iOS target and owned runtime
scope150apply. New Documents/native-page155-compositions output,180s/256MiB cap,
no automatic retry; host bound300s. Freeze catalog in source before capture.96pairs
are development-only, not a final holdout. Validate hashes/membership/geometry and
review representative overlays before any production annotation integration.

PAGE156: freeze page-only Run013development baseline on all96qualified compositions
using the existing640letterbox exporter/confidence.001/NMS.7 and custom AP50
implementation. Report pageControl only; other classes unlabeled/unavailable.
Additionally report operational confidence.25 matches atIoU.5 by layout/style/theme,
not a newly selected threshold or DS-G8. Pin checkpoint88c3cffb51b0b29dd71672fb64f6e60be56757e6de507886ef2f5c2ff86dd9b7.
Prepare exact900current r8native train repair inventory with source/label/sidecar
hashes and recipes, preserve5200evaluation members. Do not regenerate yet:
UIKitControls automatic-interactive style is not covered by disabled automatic
COMPOSE155cases. Resolve that style explicitly before modifying annotations.

NATIVE157integrates opt-in controlled-removal bounds in both capture entrypoints,
default annotations unchanged. Find exactly one public UIPageControl, render hidden
reference within the same owned window, restore visibility with defer, reject any
RGBchange>4 outside its frame expanded1pt, preserve original PNG/other annotations.
Retain hidden PNG/public frame/body evidence. Cleanup detaches owned root VC.
Qualify actual UIKitControls/KitchenSink in one24case batch:2families×2profiles×
2themes×3seeds(7,19,31). Exact150target/runtime scope,180s/256MiB,new Documents/
native-page157 output. No original900rewrite until this passes.

Diagnostic matrix reached24cases:4accepted/20outside-control rejections; differences
occur at activity-indicator coordinates. Controlled removal requires the whole
rendered scene's animation time fixed, not UIView.setAnimationsEnabled alone.
Freeze only the owned root CALayer clock before original/reference render; restore
speed/timeOffset/beginTime with defer. No removal of animations or masking of
unrelated differences. Qualify revised24case batch to new native-page157-frozen
output, same bound/target. Existing failed bytes and default capture behavior stay.

NATIVE159: after24/24NATIVE157qualification, regenerate exactly900training IDs
(700UIKitControls,200KitchenSink) from page156-repair-inventory. Freeze recipes,
source hashes and original image/annotation/label hashes before execution. Reuse
existing capture entrypoints and opt-in nativePageEvidence, preserving original
dimensions (KitchenSink393×1100points on both profiles). Keep hidden PNG and
measured container/body per member; exact same source-template recipe behavior.
One exact iOS150target batch, new Documents/native-page159 output,1800seconds and
2GiB bounds, unique destination; stop on failure and retain partial evidence.
Standard owned build/install/runtime scope applies; no system resets/downloads.
Audit all900bytes/sidecars/differential bounds and decoded duplicates before
admission. Old r8,666manual fixes and5200evaluation members stay immutable. Stage
an explicit patch/overlay rather than modifying hardlinks or copying entire corpus.
No model launch until complete new membership and unchanged evaluation verified.
Independent decoded bounds reuse NATIVE157's one-pixel tolerance; check all four
edges, retain deltas, and require sidecar bounds exactly match native receipt bounds.
Do not demand byte-identical color-decoder edge thresholds or silently enlarge
this tolerance. NATIVE159first strict checker stopped at img_014382: left edge
differs one pixel; corrected to the established qualification contract, not relabeled.

Independent companion RESIDUAL160: using hash-bound existing DTM053/054results,
trace center8negative failures to retained source endpoints/groups. Report overlap
of confident errors versus abstentions, changed-pixel fraction and nearest opposite
training example distance (descriptive, not a semantic equivalence test). No new
training, synthetic-label admission or final-holdout access. Keep private source
references local; share only an actionable aggregate finding if it changes TTR work.
# IOS-RESOLUTION-187 — controlled input resolution

Bounded follow-on to186: doubled box weight did not recover any31prior fit failures.
Test whether tiny resized page targets benefit from1280input, rather than another
loss/epoch sweep. Same432eligible training members and019initializer as022; fresh
optimizer,10epochs,batch8,69updates,box7.5and all022remaining settings. Only input
resolution changes. Source inspection amended initial960proposal to resident-supported
1280: exporter only supports640/1280; preserve sealed historical code and explicit
preprocessing contracts. Larger compute is measured, not concealed. No new labels,
capture, eval admission or threshold tuning. Memory probe uses one disposable
forward/backward/AdamW step on maximum-size batch8 with synthetic targets bounded
by maximum training-label count; no persisted weights or candidate initialization.

Before launch: verify022inputs/checkpoints/source pins; calculate exact rectangle
batch shapes, per-class presentations and resized target dimensions. Preflight
MPS memory for batch8 with bounded representative forward/backward diagnostics,
without publishing those weights as the candidate. Record local/verifiedUSB capacity,
2GiB output ceiling and no-wall-limit; no downloads or other-repository edits.
Log sequential run ID and resolved protocol before training. If memory prevents
fixed batch8, retain diagnostics and revise the comparison explicitly.

Use unchanged trainer/evaluator with a reviewed isolated adapter. Verify saved
arguments, all10epochs/69updates and fixed-last checkpoint. Score216fit,96development,
2400retained members with candidate-native1280preprocessing explicitly declared;
compare to retained022control, acknowledging both train/inference resolution change.
Do not claim an isolated training-only effect or equal computational work.
Keep all14original gates; report all38supported class deltas and unavailable classes,
prior31misses, newly lost hits, exact pixels/epoch, elapsed time and storage.

Tests: changed roles/membership/initializer/settings, preprocessing provenance,
output collision, incomplete run and explicit memory failure. Focused tests followed
by one offline Swift build/test. Handoff: software/data/integration/model outcomes
separate, concise experiment result and diagnosis. A failed gate does not trigger
another run. Success still requires independent qualification, not automatic shipping.

## IOS-CROSSOVER-189 — resolution factor accounting

Run024recovers21/31prior fit failures but1280retainedAP falls to.343954. Before
another training proposal, complete two missing inference arms:022@1280and024@640,
using exactly the216fit/96development/2400retained manifests. Reuse verified022@640
and024@1280 predictions. Same frozen thresholds/metric/taxonomy/postprocessing;
explicit size in each artifact. No weights, labels, admissions or thresholds change.
Pin both checkpoints, terminal evaluations and source before inference; project-local
new outputs capped512MiB. Serial MPS inference, no concurrent training. Existing
exporter/scorer only; report preprocessing difference, not a falsely compatible
same-settings comparison. Reconcile all four arms' membership, original14gates,
per-class AP and TP/FP/FN, and exact prior31fit-case transitions. Source/role/geometry
checks remain strict. Diagnostic evidence may inform one later reviewed experiment,
never trigger automatic training or promotion. Test settings and pair completeness,
then required offline build/test once at integrated handoff.

## IOS-REFINE-190 — geometry-only proposal diagnostic

189shows useful1280page geometry but poor class retention and many extra page
predictions. Reuse pinned022@640 and024@1280artifacts only. Preserve every022record,
class and confidence; no new predictions. For pageControl only, form same-image
candidate edges atIoU≥.25and high-resolution confidence≥.25. Change coordinates only
when both original and candidate have exactly one eligible edge; leave ambiguous,
missing or many-to-one matches unchanged. Freeze these rules before execution;
no threshold sweep or outcome-driven rule tuning. No truth enters association.

Produce a versioned diagnostic derivation and audit per prediction, linking both
source hashes. Do not pretend derived coordinates came from022single-pass inference.
Use existing scoring with explicit derivation validation rather than weakening
the prediction contract. All non-page detections must remain byte-identical; exact
membership/order, confidence and total count preserved. Test ambiguous/duplicate,
boundaryIoU, missing proposals, corrupt inputs, partial membership and collisions.

Score216fit/96development/2400retained with original14gates, per-class metrics,
old31failures and newly broken cases. No independent qualification or deployment
claim. Report reliance on two inference paths and their measured costs; no assumed
CoreML parity.≤128MiBnew local output, no training/capture/inference. A failed
diagnostic stops this rule; do not automate new matching rules. Finish integrated
offline build/tests and one evidence handoff with next decision.
