# Focus Transition Model — transition learning49

Assigned October3,2026: audit retained genuine before/after evidence, freeze the
guarded-rule baseline at action level, integrate a learnable temporal candidate and
execute one comparison only if exact training membership is already admitted.
Owner/state: Tasks.md. This extends temporal work, not single-frame FocusRing.

## Initial candidate and boundaries

The first candidate is a small three-class softmax head over **paired visual
measurements**, not another independently scored single-frame classifier. Reuse
`focus_recorded_transition_eval.predict`, production16%/256px crops and
`settings_focus_stability.crop_metrics`. Features include signed brightness change,
absolute changes, spatial coverage, scale ratios and tracking quality. Only ordered
before/after pixels, before candidate boxes and pixel tracking enter prediction;
reviewed after identity/geometry and focus are scoring labels, never input features.
This is a deliberately simple trainable baseline before a new neural image encoder.
It may not distinguish pixel-identical changes with different semantic causes.

Per-control outputs: unchanged, arrival, departure, or abstention. Reuse the existing
scene corroborator with unresolved-background rejection. Full action success requires
both correct identities for a move, or all eligible controls unchanged. Incomplete
coverage cannot become a whole-screen success; screen changes and missing identity
remain unavailable. No action is issued and no public API or production model changes.

## Deliverables

1. Audit original sealed Settings23 and transitions34 reports, their retained input
   references, membership, data roles and baseline scores. Preserve all rejected
   movement cases. Aggregate action metrics separately from per-control metrics.
   Shared endpoints/journey/renderer ancestry must remain in one data partition.
2. Define a versioned measurement corpus and preflight that preserve original role,
   source report/control identity, label evidence, completeness and baseline. Never
   admit calibration, unknown truth, prediction labels or generated tests implicitly.
   Require a separate exact-member data-use decision to propose train/development roles.
3. Add a temporal adapter to the existing FocusRing experiment dispatcher and CLI.
   Use train-only feature normalization, a fixed seed and 30 epochs. This head uses
   deterministic full-batch gradient
   descent, learning rate0.05,L2=0.0001. Fixed-last evaluation, no threshold search.
   Frozen confidence0.85; report abstentions and raw accuracy separately. No downloads,
   backbone encoding or GPU required. Numerical unit tests are software fixtures,
   never model-performance evidence.
4. Test real planning/train CLI routing, source tampering, nonfinite measurements,
   order-sensitive features, unchanged controls, missing labels/classes, duplicate
   identities, source/journey/pixel leakage, train-only scaling, output collision,
   false calibration admission and full-scene incomplete coverage. Run required
   offline Swift build/test once after integration.

## Training prerequisite and acceptance

First audit does not change existing roles: Settings is exposed development and
TTR34 calibration; the rejected four movement cases are not labels. A trainable
protocol must bind an explicit admission record, exact corpus hash, source member
assignments, both train and development groups, all three labels in each, and no
shared journey/ancestry/endpoints across groups. The admission names the human
decision/reference; a JSON boolean is a record of authority, not authority itself.
Class support checks are minimum software safety, not sufficient sample-size proof.
Pinned `endpointImages` references are required for Settings training admission;
native reports already carry them. Decode PNGs to RGBA with dimensions in the hash.
Missing pixel evidence blocks launch; identical decoded content cannot cross splits
even when PNG metadata/file hashes differ. Maximum 4,096 control records per protocol.
Historical absolute-metric absence has an explicit feature mask; it is not a stable
frame assertion. Source/missingness shortcuts remain a candidate-evaluation risk.

## Entrypoints and evidence

Inventory: `scripts/focus_transition_learning.py --sources <sources.json> --output
<new-report-directory>`. It writes an audit and a sealed-by-hash protocol with no
admission. Sources contain pinned report references, group identity and optional
`endpointImages` references. Raw reports remain unchanged.

Preflight/launch use `scripts/train_focus_ring_detector.py --experiment-protocol
<protocol.json> --experiment-arm transition-measurements --name <unique-name>`.
Use `--preflight` first. A real launch additionally needs `--execute`, the exact logged
`--experiment-id` and `--experiment-approval`; no flag admits data implicitly.

Prediction uses `scripts/focus_transition_learning.py --request <request.json>
--model <last.json> --output <new-result.json>`. The versioned request accepts only
before/after image references, before boxes and verified context. Prediction results
remain advisory; supplied context is not authenticated target identity.

October 3 result: 17 retained usable pairs, four rejected movement cases; 76 scorable
control comparisons (55 correct, zero wrong, 21 abstentions). No complete-screen
action qualifies for scoring. Only two actual switches from one exposed Settings
journey; accepted native examples are unchanged. Candidate launch blocked, not run.
See [handoff](../../reports/work/FOCUS-TRANSITION-49/handoff.md).

The run requires tranche-derived execution approval and an ExperimentLog entry
binding protocol/arm/output. This assignment covers one local candidate within2GiB;
the standing no-wall-time-limit override applies, while30epochs stay fixed.
If there is no eligible corpus, finish the audit, actual integrated candidate code,
tests and exact intake requirements; do not fit on calibration data to manufacture
a successful run. No new capture, external transfers, export or promotion.

Handoff: one concise report with automated audit/test evidence, four independent
outcomes, training go/no-go and missing membership. Next priority is independently
grouped genuine switches plus no-op/content/scroll negatives; preserve exposed
Settings/TTR evidence as diagnostic challenges unless explicitly reassigned.

## Reference transition50 continuation

October3 continuation:49 covered only Settings23/native34, omitting the already
received reference36 corpus validated in44. Reuse accepted-case membership and
strict `validate_case`, native-navigation observation mode and existing pixel
comparison/crop functions. Extend the existing transition audit entrypoint with an
explicit reference-delivery mode; legacy16-case behavior remains unchanged.

Score all24 actual transitions; separately account for12appearance-only cases and
producer-rejected trials. Native after boxes/identity score predictions but must not
enter pixel tracking. Retain absolute crop metrics for learning; guarded Settings
rules on reference UIs remain cross-domain diagnostics. Unknown/clipped controls
prevent full-screen qualification even when the observed focus relation is known.

Accept a distinct versioned sealed reference report in49's collector. Record shared
renderer ancestry rather than treating themes, seeds, campaign directories or two
screen families as independent datasets. Add a source-group/class/feature readiness
report and whole-group partition feasibility check. It proposes no admission and
does not change roles. Use new immutable outputs; no unchanged old replay.

Acceptance: actual CLI validates and accounts for36accepted cases, replays24ordered
pairs, reports per-condition/family/control/action results and exact exclusions;
learner consumes the sealed result. Adversarial membership/partial data tests and
required offline package checks pass. Source references/roles remain intact.
One conditional candidate remains blocked unless data admission and separated
move-bearing groups genuinely exist. Correct the old global no-native-moves claim
and publish a request34 follow-up, not a duplicate repair or capture assignment.

### Maintainer execution amendment — October3

The maintainer explicitly authorizes TTR generation and training needed for this
transition tranche. Bound the first new acquisition to8reference transition cases:
guide/catalog × seeds97/101 × scroll_moved/scroll_unchanged, ordinary rendering.
Use the freshly discovered local tvOS26.5 simulator9026ECA9-77DB-4AE6-8FE6-BB239E9571FA,
matching running app/helper, managed workspace and verified Fixture endpoint. Normal
TTR/Simulator runtime storage is in scope; explicit exports/logs remain NUIAK-local.
No Office, service reset, installation, new backbone or production promotion.

Reserve all new Fixture membership as a candidate training source after strict intake;
retain the exposed real Settings journey for development only (not independent final
evaluation). Do not split the shared Fixture renderer between train/development.
Producer `calibration` metadata is retained verbatim; any consumer training admission
must cite this explicit decision and exact accepted membership, not change sidecars.
Missing arrival/departure pixel features still block this measurement-head candidate.
Budget8cases/10minutes/1GiB new capture plus the existing2GiB/30epoch candidate cap.
Start only after fresh ownership/target/endpoint checks; preserve uncertain failure
and owned cleanup. No automatic equivalent retry or fitting on invented labels.

## Correspondence51 — retained-pixel comparison

Continue locally while50 cleanup is unresolved. Test one frozen `wide-template-v1`
tracker:90% central body at maximum512px width, versus70%/256px existing tracker.
Hypothesis: retaining peripheral row text improves identity correspondence. Keep
correlation/peak-gap thresholds, reciprocal checks, search limits and fixed-size
production crop geometry unchanged. No after labels enter prediction, no parameter
sweep, capture, training or default replacement. This is not a new neural encoder.

Replay all24 retained reference actions through the actual audit entrypoint. Compare
identical case/control membership and native-identity correctness separately from
classification. Preserve calibration roles and inspect positive-state feature
availability. Reuse frozen original baseline; include negative/duplicate-texture and
truth-exclusion regressions. A failed hypothesis is a completed comparison, not a
reason to loosen gates. Any improvement remains experimental until Settings and
independent evidence establish transfer. Record elapsed runtime and exact pins;
run focused Python tests plus one integrated offline Swift build/test. Deliver one
comparison and next acquisition/algorithm decision; do not train on calibration.

## Feature correspondence52

One opt-in `feature-consensus-v1` diagnostic uses ORB descriptors over gradient
magnitude (polarity-insensitive), max1280px viewport width,3000features. Mutual
nearest-neighbor matches require0.7distance ratio and Hamming distance≤48. Match
within the existing bounded before-box search region; no after boxes or labels.
Require6matches,≥70%translation-consistent inliers within max3px/3%body height,
and spatial support≥16px horizontal/6px vertical at working resolution. Use median
inlier displacement, preserve crop size, and retain existing clipping checks.
No learned encoder, fabricated correlation score, threshold sweep or default switch.

Replay24reference actions and5Settings actions using production crops. Compare
identity, positive support, wrong matches and abstentions against frozen50/23;
no additional wrong identity matches permits consideration, not automatic adoption.
Test polarity, translation, duplicate/missing features, geometry, malformed input
and real CLI routing. Independently audit whether correspondence or appearance
measurements still block positive learning. Preserve all calibration roles; reject
experimental feature reports in the default learner. Training remains conditional
on qualified new membership and consumer support. No live retry while50cleanup is
unresolved. Complete integrated tests, report and actionable TTR coordination only
if the outcome changes the peer's next action.

Result52:24reference and5Settings actions replayed. Native correct identities43→86,
wrong5→0; positive0/12. Settings correct identity unchanged45, but both departures
now abstain; unchanged-control gains hide that loss. Do not adopt. Scoring-only
displacement audit found6/12native positives with≥6stationary and≥6native-motion
matches; visual review confirms fixed textured artwork behind scrolling guide rows.
Single-translation consensus is insufficient for those layered examples. No claim
that more iterations of the measurement head will fix unavailable input features.
Next architectural proposal: direct paired-image prediction with after identity/boxes
as labels only, plus deconfounded no-scroll-switch/scroll-no-switch coverage. Preserve
hard layered cases. New encoder execution remains an explicit experiment decision.

## Direct paired-image53

User assigned this tranche after52. Build a scratch six-channel CNN taking ordered
full RGB frames, aspect-fit96×64 with black padding. Three stride2convolutions
8/16/24channels,64unit hidden layer, eight sigmoid box coordinates and a change logit.
Targets: before/after focused boxes as normalized cx/cy/w/h in letterboxed space,
and semantic focus change. Box displacement alone is not semantic change. No tracker,
native geometry, text or IDs enter inference; this is not a FocusRing crop change.

Reconstruct strict reference36and reviewed Settings labels/pixels; preserve source
roles and whole-renderer/journey groups. Exclude endpoints lacking exactly one known
focused box. Partial inventories stay partial: known-focus localization is not
proof of absent focus or complete scene coverage. Reuse trainer dispatch with explicit
`transition-direct-pixels` arm.30epochs, CPU Adam lr0.001/batch8/seed42, fixed-last,
2GiB outputs, no wall-time cap. BCE change plus box MSE. Report box IoU≥0.5,
raw change accuracy, confidence0.85abstentions and latency; no threshold sweep.

Preflight binds exact admission/membership, source/config/code hashes, group/action/
decoded-pixel isolation, both change states per partition and isolated output. Existing
calibration sources need explicit role decisions; new approved capture membership
can qualify only after genuine intake. Complete inventory, trainer/prediction CLI,
adversarial/model tests and offline package checks. A real fit is conditional on
admitted data; numerical fixture optimization is software evidence only. No capture
retry, download, export, promotion or implicit reclassification of retained evidence.

### Execution54 approval — October3

Maintainer approved the exact53proposal:24Fixture/train and5Settings/development,
one fixed30epoch direct-image candidate. New admission/protocol/approval files in
`reports/work/DIRECT-TRANSITION-54/` preserve the old unapproved proposal. DTM001
uses the unchanged53architecture/configuration; no tuning, automatic retry or model
promotion. Complete held-out development scoring, loaded-checkpoint parity/latency,
training-fit diagnosis and a concise failure/next-experiment report. Extra read-only
checkpoint evaluation is diagnostic only, never checkpoint selection or training.

### Localization55 — approved controlled comparison and metadata companion

October3 maintainer continuation authorizes one DTM002 comparison on the existing
24 Fixture/train and5 Settings/development admission. Freeze all DTM001 settings,
architecture, epochs, seed and thresholds; replace box MSE with mean generalized-IoU
loss plus mean absolute coordinate error, retaining unit-weight change BCE. Hypothesis:
overlap-sensitive gradients improve training localization, unlike a small coordinate
MSE that can hide large relative errors on narrow controls. No additional run or sweep
is planned. Fixed-last30epochs, resident CPU dependencies, no wall-time cap,2GiB total.
Report per-endpoint IoU, invalid boxes, normalized center/size errors, change errors,
joint decisions and latency on both partitions. Compare frozen DTM001 evidence without
rerunning or modifying it; five exposed Settings pairs are development, not qualification.

Preserve legacy checkpoint/configuration loading and strict configuration rejection;
test identical/disjoint boxes, finite nonzero gradients, coordinate conventions,
actual trainer/prediction/evaluation entrypoints and one integrated offline Swift pass.
Log/pin the new implementation and execution authorization before launching. Stop after
the declared comparison and diagnose failure rather than changing the split or thresholds.
Independent companion: TASK-DOC-01 packaged FocusRing metadata reconciliation against
the actual resource/registry, distinguishing artifact version from unmet v1.0 quality
milestone. No protected skill, shipped weight, capture, export or promotion changes.

## Spatial56 — spatial fit diagnostic and deconfounded coverage audit

October3 maintainer approves this next substantial tranche. Keep the existing exact
24Fixture/train and5Settings/development admission,96×64ordered RGB preprocessing,
CPU/Adam0.001/seed42/batch8, confidence0.85 and fixed-last selection. Replace only
the localization representation: stride4shared convolution features (24×16 grid),
two spatial cell classifiers and per-cell sigmoid x/y offsets plus normalized width/
height. Change head reads shared visual features. No truth, IDs or boxes at inference.
Train cell cross entropy plus L1 offset/size regression at target cells and unchanged
change BCE, unit weights. Decode the highest-scoring cell per endpoint plus its learned
offset/size; report invalid/clipped predictions honestly. This is an experimental
representation, not a public API or calibrated confidence change.

First audit all admitted pairs for identical encoded images with differing targets;
report semantic change versus endpoint displacement and source-group support. Do not
claim a shifted box proves scrolling, or claim coverage of no-focus/dialog cases not
labeled in this corpus. Keep the five exposed Settings examples development-only.

DTM003: deterministic first two changed and first two unchanged training IDs,120epochs.
This is a training-only memorization diagnostic, not new data-role admission. Proceed
to DTM004 only if all four pairs have both endpoint IoUs≥0.5 and correct raw change.
DTM004: same spatial implementation, all24training pairs,30epochs, score5development
pairs without tuning. Maximum two runs, combined2GiB outputs, no wall-time cap under
standing approval; no downloads or automatic retries. Log/pin each run before launch.
If DTM003 fails, preserve results and finish diagnosis/coverage audit, not another fit.

Integrate legacy checkpoint loading and actual trainer/prediction/evaluation entrypoints.
Test spatial target geometry, gradients, strict configs, serialization parity and no
label-input leakage; focused tests plus one offline Swift pass. Report training fit,
per-endpoint errors, raw change, abstentions and latency separately. Deliver one handoff,
ranked data/architecture gaps and an actionable next tranche; no TTR capture or SMB
publication unless a concrete producer request changes its next action.

### Spatial56 result

DTM003 finished120epochs on four fixed train members: change4/4,paired boxes0/4;
vertical cells8/8but horizontal0/8. Mean cell CE2.9936 dominates the remaining loss.
Local15×15pixel receptive field is a plausible context limitation; not proof of cause.
The actual candidate preparation refused `memorization_gate_failed`, so DTM004 did
not run. All24train-role pairs were rescored but only4were fitted. No promotion.

### Next proposal — global-context57 and deconfounded intake

October3 execution assignment: maintainer requested the next tranche. Freeze a
context residual decoder: existing encoder → adaptive average pool4×6 → flatten
576 → linear64/ReLU → linear3840, reshaped into2cell and8geometry residual maps.
Add these to the unchanged local heads; keep the change head, loss and input fixed.
This retains coarse spatial order and gives every output cell full-frame context.
DTM004 is the120epoch diagnostic (the earlier conditional DTM004 never launched);
DTM005 is conditional30epoch candidate. Maximum two runs,2GiB combined outputs.
Independent deliverable: executable metadata-only intake validation of observed
focus change versus observed scrolling, evidence references and journey partitions.
It reports coverage, never grants data admission or fabricates scrolling from boxes.

Implementation outcome: give both spatial classification and geometry heads access
to full-frame features rather than only15×15local neighborhoods. Keep96×64 input,
the existing grid/loss, admitted24/5roles, confidence and seed fixed to isolate context.
Do not hardcode observed row centers or infer widths from labels at prediction time.
Retain old model/config decoding and frozen prior reports.

Proposed execution envelope for review: same four IDs,120epochs and the same4/4fit
gate. Only on pass, one30epoch all24/5comparison.2GiB total, no wall-time cap; log
new protocols/IDs before launch. Never combine a context change with a resolution,
dataset or threshold change in the same comparison. No automatic retry if it fails.
Tests: spatial geometry, finite gradients, complete field of view, image-only prediction,
checkpoint/legacy parity, actual CLI/preflight rejection and one offline package pass.

Independent intake specification: require source-truth semantic focus change and
explicit scroll state separately, covering all four scroll/no-scroll × switch/no-switch
cells. Request real no-op/stationary examples rather than inventing repeated-frame
labels. Record before/after settled identity, boxes, frame hashes, action receipts,
source/journey grouping and cleanup. Keep related journeys in one partition and
reserve genuinely independent evaluation before failure-driven selection. Current
coverage has no unchanged/stationary training pairs; displacement alone cannot fill
the scroll matrix. A proposal is not a producer assignment or capture authorization.

Metadata contract `transition-intake-coverage-v1`: records require a unique `id`,
`journeyGroup`, `partition` (train/development/evaluation), boolean `focusChanged`
and independently observed boolean `scrolled`, `labelSource` (fixture-observed or
human-reviewed), two `decodedFrameHashes`, and hash-bound project-local references
`beforeObservation`, `afterObservation`, `actionReceipt`, `cleanupReceipt`.
The metadata validator checks reference bytes, rejects duplicate IDs, journey/pixel
cross-partition leakage and unknown labels, and reports all12partition×scroll×change
cells. It cannot authenticate caller labels or verify their semantic relation to
images: source-specific intake must do that before admission. Missing/unknown scroll
observations stay in a pending review queue, never default to false. No current29pair
member is silently converted to this contract. Real no-op captures must be distinct
observations, not copied frames. Future acquisition should populate the four training
cells plus independent journey groups reserved before model-driven selection.
CLI: `scripts/transition_intake_coverage.py --input MANIFEST --output NEW_REPORT`.
This tool always reports trainingEligible=false; its coverage is metadata evidence,
not a new training approval or proof that caller-supplied pixel hashes were decoded.

Acceptance: fitted-subset and full-partition metrics clearly distinguished; no
ground-truth-cell oracle reported as model accuracy; exact gate decision and ranked
remaining data/model weaknesses. Existing shipped models and five exposed Settings
development examples remain unchanged. Select/request new data only under its own
authority; do not let producer availability block this local representation test.

### Context57 result

DTM004 at120epochs selects8/8correct fitted center cells, versus0/8forDTM003;
change4/4 but paired boxes0/4. Geometry saturates, especially height near zero.
Parameter count595,291→881,819; warm CPU4.156→4.232ms on these measurements,
not a controlled hardware performance benchmark. Model output3.55MB; no CoreML export.
The exact candidate gate refused DTM005. Prediction CLI parity passes for DTM004,
DTM003 and DTM002. Metadata intake delivers coverage/reference validation only.

### Next proposal — geometry58

Assigned October3: “Do Geometry58 and cleanup any tech debt that is low hanging fruit.”
DTM005 is the diagnostic (previous conditional DTM005 never launched); DTM006 is
the conditional candidate. Reuse parameterized preparation/parity tools rather than
copy them; remove hardcoded spatial-loss cell count and add PID to future receipts.
No numerical changes beyond geometry BCE-with-logits; preserve older model decoding.

Inputs: unchanged29pair admission, exact4diagnostic IDs and frozen DTM004 results.
Hypothesis: sigmoid-followed-by-L1 geometry can saturate and lose useful gradients;
supervising the existing geometry logits with binary cross entropy against the same
fractional0–1coordinate targets may avoid that failure. This treats coordinates as
bounded regression targets, not calibrated class probabilities.
Keep context architecture, input, seed, optimizer, unit loss weighting, cell/change
objectives and sigmoid decoding fixed. Change only geometry loss. Test analytically
that extreme negative height logits get finite, nonzero correcting gradients; test
coordinate endpoints, serialization, strict configs and unchanged old predictions.
On assignment: one120epoch diagnostic and, only if all4have correct change and both
IoUs≥0.5, one30epoch24/5candidate. Two runs/2GiB/no wall-time cap; fixed-last, no
data-role change, automatic retry, capture, export or promotion. Log runs before launch.
Report cell/geometry losses, saturation, paired IoU, change, abstention and latency.
Failure ends fitting with diagnosis; success is development evidence, not release.

Independent companion: inspect retained source observations read-only for explicit
scroll/change/action/cleanup evidence. Produce a source-field-to-intake mapping and
missing-evidence inventory. Do not infer scrolling from bounding-box displacement,
rewrite historical captures, relabel journeys or fabricate receipt references.
Acceptance: integrated trainer/CLI and focused/offline package checks, exact gate
decision, comparison toDTM004, and actionable missing-data requests ready for review.

### Geometry58 result

DTM005: same4pairs/120epochs, correct cells8/8, change4/4, paired boxes2/4 versus
DTM0040/4. Geometry L1 halves0.08116→0.03843; sigmoid collapse is removed but dark
before-frame heights remain approximately twice the target. Conditional DTM006
correctly refused. No larger fit or promotion. Same881,819parameters.

Inventory `reports/work/GEOMETRY-58/source-inventory-reviewed.json` verifies sources
without changing admission. Fixture semantic inventory exposes stable bracketed
`scroll_container_id`/`scroll_offset_points`: all24training pairs truly scroll,
12switch/12unchanged. Action receipt exists for12navigation actions; all24have
mutation receipts and verified embedded cleanup. These are pointers into preserved
evidence, not invented new receipt files. Settings5has completed action events and
human-reviewed focus relations, but no bound explicit scroll/cleanup labels in the
inspected evidence chain. Unknown remains unknown. No new capture request published.

### Next proposal — geometry59

October3 goal continuation selects this bounded experiment tranche. DTM006 is the
diagnostic (the earlier conditional run did not launch); DTM007 is conditional.
Same two-run/2GiB envelope. Preserve GEOMETRY-58 changes and evidence uncommitted.

Hypothesis: remaining thin-row extent errors need overlap-sensitive supervision,
not just bounded-coordinate regression. RetainDTM005architecture, geometry BCE,
96×64input, exact four IDs, seed/optimizer/thresholds. Add a unit-weight GIoU loss
on decoded target-cell boxes while retaining cell CE and change BCE. The target cell
is training-only, as already used by geometry supervision; inference remains argmax.
This differs fromDTM002: that test lacked the spatial/context architecture and logit
geometry objective. Do not claim that previous failure predicts this result.

On assignment: one120epoch diagnostic, conditional30epoch24/5candidate only after
all4correct change and both IoUs≥0.5; combined2GiB/no wall-time cap, fixed-last.
Test differentiable decode and finite correcting gradients for thin/oversized boxes,
same-image prediction/legacy parity and strict protocol bindings; run focused and
offline package checks. Report endpoint IoU/size, cells, change and abstentions.
No resolution/threshold/data changes, automatic retry, export or promotion.

Independent deliverable: frozen no-scroll acquisition specification covering both
switch/no-switch with native offset observations, action or mutation receipts and
cleanup; reserve journey groups before capture. Existing data remains development.
Identify a qualified renderer and required runtime authority without launching it.
Acceptance: exact model gate decision plus executable capture matrix for review;
capture and new data admission remain separately authorized.

### Geometry59 result and no-scroll acquisition contract

DTM006 improves diagnostic paired fit2/4→3/4; all8cells and4change labels correct.
One light unchanged before height remains~0.001 (target0.06328); paired gate fails.
No DTM007. Retain fixed-last and original thresholds, not a near-pass exception.

`scripts/plan_stationary_transitions.py --output NEW_JSON` emits the frozen24case
development matrix:2instrumented reference screens (nostalgex_guide/stingray_catalog)
×2themes×3artwork styles×2conditions(boundary_noop/interior_switch),seed83variant0.
Historical source qualification: TTR-UPDATE-43 rich-reference36 corpus, manifest
d2f82c3199f7d18224654751a9afcac55a5d3c28a815cba0e9060cc05ab3610d.
This identifies a previously used renderer, not a currently authorized/ready runtime.
The matrix requires48total independent captures across24pairs, a single observed
directional action per case, and stable equal native offsets across both brackets.
Related seed variants remain development-connected; no independent final-eval claim.
No automatic retry, no Office fallback, reject automatic scroll/clipping/unknown cleanup.
Current consumer recognizes boundary_unchanged and scroll conditions but not an
interior no-scroll switch; a reviewed adapter extension is required before intake.
Planner marks executionEligible=false; runtime UUID, matching Fixture and explicit
capture/storage assignment remain prerequisites. No capture is launched by this plan.

### Next proposal — geometry60

Selected by October3 goal continuation. DTM007 diagnostic and conditionalDTM008;
the earlier conditionalDTM007never launched. Preserve previous dirty work/evidence.

Hypothesis: fractional-target BCE gives a small recovery gradient to a collapsed
thin extent; target-logit SmoothL1 can provide a stronger correcting signal.
Replace only geometry BCE with SmoothL1(beta1) between raw logits and
logit(clamp(target,1e-4,1-1e-4)); retainDTM006cell CE/GIoU/change BCE, architecture,
decode,96×64,seed42,Adam0.001,exact4IDs/120epochs. Targets at cell boundaries use
the declared clamp; inference unchanged. Do not hardcode observed box sizes.
Before launch, test gradient direction/magnitude for collapsed height, upper/lower
coordinate limits, finite gradients and legacy serialization. Record coordinate-level
gradient and saturation diagnostics for retainedDTM005/006 on their exact fitted IDs.
One diagnostic then conditional30epoch24/5candidate only after unchanged4/4gate;
two runs/2GiB/no wall-time cap. No data-role change, capture, export or promotion.
Failure yields decomposition and a new reviewed hypothesis, never an unchanged retry.

### Geometry60 result

DTM007passes4/4paired boxes,8/8cells,4/4change; endpoint IoUs0.888–0.974.
Retained collapsed-height gradient analysis shows logitSmoothL1−0.125 versus
BCE−0.007786 and sigmoidL1−0.000124 (each mean objective). This supports a stronger
local correcting signal, not a general guarantee. DTM00830epoch24/5candidate
then underfits: train8/24paired boxes and12/24raw change,24abstain; Settings0/5paired,
3/5raw change,5abstain. No usable model/promotion. Keep all prior evidence immutable.

### Next proposal — fit61

Selected October3 by persistent goal. DTM009 is one fresh full120epoch run. Before
reporting changes, seal exact historicalDTM007pins and AST fingerprints for numerical
preprocessing/model/fit/inference functions. Gate compatibility requires those functions
unchanged, unchanged spatial model source/dependencies and the original4/4artifacts;
only direct wrapper/config registration, evaluator reporting and new preparation may differ.

Hypothesis: the24pair fit needs more optimization than the30epoch baseline; distinguish
this from architecture/data-transfer limitations. One fresh120epoch run with exact
DTM00824/5membership, architecture, objectives,96×64,seed42,Adam0.001,batch8 and
fixed-last. No checkpoint selection, threshold tuning, new data or automatic retry.
Prerequisite: retainedDTM0074/4gate bound to its historical artifacts, with explicit
compatibility evidence for any reporting-only source changes. Do not simply disable
code pins.2GiB/no wall-time cap; log protocol/approval before launch. Compare all24
fit IoUs/change/abstentions plus5exposed development, not independent final accuracy.
Success means full fit can be assessed, not automatic release; failure must separate
cell, geometry and change gradients before another architecture experiment.

Independent reporting deliverable: distinguish actually fitted IDs from other train-role
members in evaluation summaries and record fit/intake/scoring time separately. Preserve
legacy result readers and hashes; do not rewrite historical reports. Tests require
membership mismatch rejection, correct4/24summaries, nonnegative timing and CLI parity.
Run focused/offline package checks. No capture/export/promotion; missing no-scroll and
independent evaluation data remain separate acquisition/admission requirements.

### Fit61 result

DTM009120epochs fits all24pairs: paired/change24/24,48/48cells,minIoU0.7596.
Settings0/5paired,2/5change,3false changes. Numerical AST/source compatibility kept
the historical4/4gate intact across reporting-only changes. New fittedMembership
summaries do not confuse untrained train-role rows with actual fit. Phase timing
shows15.73sintake versus4.86sfit within20.73swrapper; initial CLI preflight additional.
No claim that more epochs fixed transfer. Shift priorities to distribution/coverage.

### Next tranche — transfer62

Inputs: frozenDTM009checkpoint/results and unchanged admitted24/5source membership;
GEOMETRY-59stationary matrix and GEOMETRY-58source inventory. No new training.
Implement bounded image-only diagnostic transformations: baseline, reversed frame
order, and paired shifts ±4%width or ±4%height with black fill, applying exactly the
same translation to both images and analytic target boxes. Reject transformed targets
outside the frame rather than clipping their truth. Maximum174pair evaluations.
Compare paired IoU, change, abstention and errors by source/condition; shifts are
synthetic sensitivity diagnostics, not newly admitted data or real navigation trials.
Reversed ordering reverses box truth but preserves semantic change; no copied-frame
example is presented as a genuine no-op. Do not tune thresholds or select new weights.

Independent software deliverable: extend the versioned source-condition consumer
for genuine interior no-scroll switch and boundary no-op cases using deterministic
fixtures. Preserve old scroll/content cases. Require stable native per-container
offsets across all capture brackets, observed focus relation, exact instance/recipe,
action receipt ordering, image/annotation integrity and verified cleanup. Unknown
offsets never default tofalse. Detect actual producer contract gaps before requesting
features already present. Test missing/conflicting offsets, unobserved focus, automatic
scroll, wrong instance, altered bytes and partial cleanup. No current historical
record is relabeled or automatically admitted.

Prepare a bounded producer compatibility/capture request from the frozen24case
matrix, clearly pending exact-target/capture authorization. Publish only actionable
producer/consumer metadata through the verified SMB protocol; if unavailable, retain
local request as unpublished. No SSH, Office operations, simulator launch or capture.
Acceptance: ranked sensitivity report, real consumer CLI fixtures plus offline checks,
precise remaining source/runtime authority and request delivery state. Independent
final evaluation remains unavailable; existing exposed Settings stays development.

Consumer extension: `stationary-transition-intake-v1` is a NUIAK report, not a
producer wire-version demand. Accept existing version-1 transition-case envelopes
with explicitly opted-in `interior_switch` or `boundary_noop` conditions only in
the stationary CLI. Reuse all existing endpoint/receipt validations; require
verified cleanup, no mutation receipt, observed requested endpoint identities,
and identical nonempty native container offsets across all four scene brackets.
Legacy callers keep their original condition allowlist. This extension is inspection
evidence only; new captures still require separate admission and execution authority.

#### TRANSFER-62 outcome

169/174evaluations executed;5Settings right-shifts rejected because truth leaves
the frame. Training baseline/reversal paired24/24; left/right/up12/24,down11/24.
Settings remains0/5where eligible. Reversal change23/24; shifted change22–24/24.
Thus translation sensitivity is stronger than order sensitivity in this bounded test;
black padding confounds a causal attribution. All29baseline predictions match the
frozen report. Stationary CLI is fixture-tested, not live qualified or admitted.
Compatibility request published/read back; peer acknowledgment pending.

### Next tranche — robustness63

Hypothesis: deterministic paired translations during training improve location
robustness without architecture growth. One fixed120epoch comparison using only
the same24admitted training pairs, DTM009architecture/loss/seed/batch/optimizer.
No backbone/encoding change. Training chooses baseline or ±4%axis shifts with a
pinned RNG schedule; transform both images and analytic truth together, reject
off-frame targets, record counts. Settings5and diagnostic transforms remain scoring
only; no threshold/checkpoint selection. Fixed-last, CPU, no-wall-time-limit standing
override,≤2GiBoutputs. Log/pin the run before execution under the local experiment
envelope; no second run follows automatically. Compare the same six diagnostic
conditions, raw/decided change, paired IoU and abstention toDTM009. A training fit
regression or no translation benefit yields diagnosis, not a sweep or promotion.

Companion: inventory retained source manifests for genuinely stationary observations
using the new strict adapter where contracts match; do not reinterpret older scroll
cases, admit new data, transfer unassigned artifacts or launch devices. Reconcile
any relevant peer compatibility reply; missing peer response blocks only live intake.
Deliver one comparison report, source-coverage/gap report, actual CLI regression tests
and integrated offline checks. Capture, independent final evaluation, export and
promotion retain separate authority. If augmentation is not supported by the current
admission contract, report that exact authority conflict before training.

Implementation detail frozen before launch: precompute baseline/left/right/up/down
at source resolution, then reuse the existing96×64encoder. Independent NumPy
RNG seed42selects one valid condition uniformly per training row per epoch; Torch
initialization/shuffle RNG remains unchanged. Record schedule SHA and per-epoch
counts. Invalid target variants are excluded before sampling, never clipped or
substituted silently. This changes training augmentation only, not source membership
or the inference encoding. DTM009full-fit evidence is the historical capacity gate;
bind its exact model/protocol/evaluation and unchanged spatial architecture source.
The prior admission's historical30epoch limitation is not reused as execution
approval: the current goal-selected120epoch tranche supplies its own protocol-bound
execution record under the standing local experiment envelope.

#### ROBUSTNESS-63 outcome

DTM010improves shifted pairs47/96→82/96but original24/24→18/24 and reversed
24/24→17/24. Settings0/5unchanged. Original cells47/48; all6failedpairs are guide
after geometry, not missing cell context. No promotion. Schedule samples2880pairs
from120variants(~24exposures/view on average), versusDTM009120exposures/view.
This is not an equal-exposure optimization comparison despite equal update count.
Retained native audit also found4valid old boundary no-ops and4content-only no-scroll
cases with verified cleanup. Preserve legacy conditions; no automatic training admission.

### Next tranche — exposure64

Hypothesis: DTM010's original-fit regression reflects reduced exposure per augmented
view, not an unavoidable geometry tradeoff. One fresh fixed600epoch run with exactly
the DTM010bank/schedule rule/seed/loss/architecture/24training pairs/5development
pairs, fixed-last, CPU,≤2GiB,no-wall-time-limit override. This yields14400sampled
pairs/~120per variant, matching DTM009's average exposure, but costs5×DTM010updates;
report both exposure and compute. No learning-rate or threshold change, checkpoint
selection, second run, capture/export/promotion. Log/pin before launch. Compare
original/reversed/shifted pairs to both prior checkpoints; separately report whether
24/24original fit returns and whether shifted accuracy is retained. Settings remains
exposed development; fitting synthetic shifts does not establish real-domain transfer.

Independent deliverable: extend frozen-model evaluation to the8validated historical
no-scroll negatives (4boundary_unchanged,4content_only) with source/byte/native
geometry/cleanup verification. Do not rewrite producer conditions, treat content
mutation as navigation, or admit them for training. Label only observed known-focus
endpoint relations, retain group/seed lineage and report duplicate-connected support.
EvaluateDTM009andDTM010without tuning, report false changes, boxes and abstentions.
These are calibration diagnostics, not a new independent final holdout. Missing
native evidence blocks only that case, with full accounting. Deliver tests, results,
one handoff and ranked coverage/architecture next steps—not an automatic sweep.

Execution detail: use the existing augmentation preparation/training entrypoints
with an explicit matched-exposure configuration, not a second trainer. Preserve
DTM010's first120epoch RNG schedule as the prefix of the600epoch schedule. New
negative evaluation uses existing legacy validation unmodified and reports connected
decoded-frame components; repeated before/after pixels are not independent samples.

After the fixed-last run, also score DTM011 on the same8retained calibration
negatives, without changing checkpoint selection or thresholds. This is inference
only and cannot alter the already completed experiment.

#### EXPOSURE-64 outcome

DTM011restores24/24original and96/96trained-shift pairs, reversal23/24; first120epoch
history exactly matchesDTM010. Settings0/5persists. All3models localize0/8retained
negative pairs. Decided false changesDTM009/010/011:4/0/2; abstentions0/2/2.
Thus extra exposure resolves fitting, not transfer. No additional epochs justified
on this unchanged bank. Four connected pixel groups among8negative cases, not8
independent journeys. Legacy conditions and calibration roles remain intact.

### Next tranche — generalization65

FreezeDTM009/010/011; no training, thresholds or source-role changes. Use unchanged
24/5admitted membership for a bounded interpolation/extrapolation diagnosis:
axis shifts±2%and±6%(8conditions), four diagonal±4%x/±4%yconditions, and original
baseline. Same source-resolution black fill and analytic targets; off-frame truth
rejected, never clipped. Maximum1131evaluations(29×13×3). These exact transforms
were not training augmentations, but their source scenes were; report that distinction.
Do not describe them as independent evaluation or genuine navigation.

Separately evaluate before/before and after/after duplicated-image inputs on those
same29sources/models(max174). These counterfactuals have zero visual difference,
not real action/no-op labels. Report predicted change and box consistency without
inventing frame freshness, action receipts or semantic no-op accuracy. This tests
whether the model responds to scene appearance without temporal evidence. Compare
all frozen models; no checkpoint or threshold selection based on these probes.

Companion: prepare an exact hashed8pair training-role proposal from EXPOSURE-64's
validated negative corpus, with human approval explicitly pending, related-group
exclusions and genuine switch coverage gaps. Do not relabel/retrain on these pairs.
Rank needed no-scroll positive, scene/layout and light-theme diversity; reconcile
only actionable changes into the existing TTR compatibility request. No capture,
runtime takeover, Office, new artifact transfer or promotion. Output one diagnostic
report, one pending admission proposal and a concrete next model/data decision.

Probe implementation: retain the exact fixed4%transform behavior through a shared
integer-pixel translation function. Pin all3checkpoints and original evaluation
artifacts; require baseline prediction parity for all29members before accepting
the new report. Counterfactual output reports decision frequency and predicted
box-to-box overlap only, never semantic accuracy. The data proposal is a separate
non-executable schema with approved:false, source hashes and immutable membership.

#### Maintainer amendment — exact eight-pair admission, 2026-10-03

The maintainer approved “Approve the eight-pair data-role change.” Create a new
32-train / 5-development admission, preserving the original 29 records and roles.
The eight added calibration records must be rebuilt from native case evidence;
model predictions never supply labels. Bind the approved proposal membership hash
`8fea86952cf5e027fc150affdd8c264dbd6d830b87909f3ad4aaafc1dd6d9eb5`.
Keep old corpus/admission artifacts unchanged and all related groups excluded from
final evaluation. Extend the existing collector with an optional negative source;
the original two-source behavior must retain its corpus hash. Verify counts,
lineage and split isolation through the real collector/admission entrypoints.
This amendment authorizes data admission only, not capture, training or promotion.
The next candidate should hold DTM011 architecture and augmentation fixed to test
the data change; report original 24 and added eight fitting results separately.

### Next tranche — prepared66

Finish approved GENERALIZATION-65 admission and add a reusable prepared-input path
to the existing direct trainer, not a second trainer. No new model run or capture
in this software tranche. Cold preparation revalidates native sources, corpus and
explicit admission, then writes an isolated, bounded translation bank using existing
encoding/geometry. Record exact membership, roles, code/dependency pins, raw source
references, bank hashes and rejected transforms. Keep original raw artifacts.

Warm preflight verifies content hashes of referenced source/evidence/admission files
and relevant implementation/dependency identities, but does not decode/rebuild every
native case. Cache loss/corruption fails closed; no automatic hidden rebuild. Loading
uses non-pickle arrays with bounded shapes, exact dtype and finite values. A cache is
not data admission or model execution authority; existing protocol/gate/run checks
remain. Legacy protocols without a prepared input retain the old path.

Verify cold/warm tensor and schedule parity, missing/changed source bytes, changed
roles/pins, corrupted arrays, collision and non-training membership. Run the actual
preparer/reader on the newly admitted 32/5 corpus; report wall time and byte size.
Integrate the trainer's real preflight and fit input boundary without launching a
model; record that the old 24-pair model gate still rejects the expanded corpus.
Next DATA-67 must explicitly bind that original fit evidence to the unchanged
24-pair subset before a single 32-pair data-only candidate can execute. Do not
weaken the existing gate merely to exercise cache integration.

#### GENERALIZATION-65 / PREPARED-66 results

1,086 transform evaluations, 15 rejected pair-condition cells and 174 duplicated
frame probes. All 87 baseline predictions match retained results. Every model calls
18/48 duplicated training inputs and 10/10 duplicated Settings inputs changed.
Settings localization remains zero; no final evaluation or model selection occurred.
The original proposal remains unapproved as historical evidence; a separate explicit
decision and new admission now authorize the eight exact training additions.

New corpus SHA256:
`335620b1bf79189e04f50a69f35bbac3c5e2d384784897c176ad32d27f8698bb`.
Prepared bank: 32 pairs, 160 variants, 23,598,720 tensor bytes; cold 30.082s, warm
0.214s, real preflight 0.394s to expected original-gate rejection. No model launch.
Raw-source hashes are still verified on warm use; semantic decoding is not repeated.
Cache is disposable `.build` output, not an independent backup or admission record.

### Next tranche — data67

Outcome: one expanded-data candidate and batched diagnostic comparison, using
the approved 32/5 admission and unchanged DTM011 architecture, seed, loss, optimizer,
augmentation and 600-epoch fixed-last budget. No wall-time cap under the maintainer
amendment; retain the 2GiB output cap. Register the run before execution under the
standing experiment envelope; the data-only approval is not run authority.

1. Add an explicit expanded-membership gate. Verify the original 24 training and
   five development records/roles exactly against the original corpus and fit
   evidence, then verify the eight additions against the exact approved decision.
   Reject lost/changed originals, extra members, role drift or changed architecture.
   Preserve existing 24-pair gate behavior for historical configurations.
2. Prepare/reuse inputs once after final code pins. Log and execute one candidate,
   no automatic retries or architecture sweep. Keep independent model initialization.
3. Evaluate candidate and DTM011 together on identical approved membership. Separate
   original 24 fitting, added eight fitting, exposed Settings, unseen transforms and
   zero-difference counterfactuals; none are independent final qualification.
4. Report changes in true/false change decisions, abstentions, paired localization,
   per-condition support and preparation/training/scoring time. Use the same metrics
   and thresholds; never tune on reserved final groups. Added negatives change class
   balance (12 changed / 20 unchanged), which must be reported, not silently reweighted.
5. Test both legacy and expanded gates, actual preflight/CLI and cache equivalence;
   run one integrated offline verification and produce one comparative handoff.

Acceptance is truthful experiment evidence, not a promised score. If appearance
shortcuts persist, propose a separately scoped temporal-representation comparison
and genuine no-scroll positive acquisition. No capture/export/promotion or new TTR
assignment in DATA-67. Existing asynchronous producer request remains separate.

DATA-67 execution detail: use a versioned expanded gate that reconstructs the original
corpus from its exact unchanged prefix and verifies its historical corpus hash,
admission and full-fit result. Rebuild the new admission from the explicit eight-pair
decision; do not accept subset inclusion alone. One cold prepared-bank build after
final code pins. Compare frozen DTM011 and the new candidate together on all37pairs,
original plus16shift conditions (the prior13conditions plus4trained axis shifts),
and148duplicated-frame probes, maximum1,258shift evaluations. Decode each source pair
once per evaluator and reuse both loaded models. Preserve reference baseline parity.
Fixed600epochs now mean2,400updates/19,200samples rather than1,800/14,400; report
this33%compute increase and class-balance change, not an equal-compute causal claim.
The existing image-only CLI parity helper should also consume the prepared corpus
when present, retaining the legacy path otherwise. This avoids repeating native
intake merely to select one already-admitted development pair for CLI verification.

#### DATA-67 outcome

DTM012fits original24and added8, including all128trained translations. Original
unseen axis2%localizations76/96→89/96 and6%65/96→79/96, but diagonal75/96→62/96.
Settings remains0/5; duplicated original inputs still18/48raw change predictions,
Settings10/10. Added data fixes its own fitting failures, not general temporal
reasoning. No additional unchanged training is justified by this result.
Prepared run intake0.386s, fit/setup12.971s; batch comparison25.509s with only2.953s
PNG decode. Cold bank26.991s, counted separately.78Python/134Swift tests pass.

### Next tranche — temporal68

Hypothesis: a change head operating on explicit between-frame differences will
reduce appearance-only shortcuts while preserving localization. This is a declared
architecture experiment, not a hidden extension of DATA-67's data-only comparison.
Select and document one compact difference-only change branch before coding; retain
the ordered RGB geometry backbone/heads,96×64encoding,32/5roles and same600epochs,
optimizer,seed,batch,fixed-last selection. Do not add inferred/synthetic labels or
replace native truth with a pixel-difference rule. Absolute differences can reflect
content/scrolling, so genuine negative conditions must stay represented separately.

Implementation must retain legacy checkpoint loading and demonstrate matching
initialization for unchanged geometry parameters. Give the new architecture its own
declared configuration and compatibility gate, rather than weakening historical
architecture pins. Verify null-difference, reversal and changed-content behavior at
the input/shape level without claiming semantic correctness from those unit tests.
Prepared-bank reuse must remain content/encoding bound; unrelated architecture
changes should eventually avoid cold rebuilding identical tensors, but no pin bypass.

Under the applicable assigned local experiment envelope, log one600epoch candidate,
2GiB/no-wall-time-cap, and compare against frozenDTM012 using the existing grouped
batch evaluation. Report original/new fitting, exposed Settings, duplicated frames,
shift robustness, latency and parameter cost. No automatic follow-up run or promotion.
If change improves but localization does not, report that distinction explicitly.

Companion: freeze a proposed acquisition coverage matrix for genuine no-scroll
positive switches, native themes/control geometries and hard negatives. Inventory
retained evidence first; group related cases and reserve future evaluation before
capture. Plan one qualified session with bounded resumable batches and producer
capability checks, not a simulator launch per case. Runtime/capture remains separately
authorized and unexecuted. Deliver one handoff with the candidate result and concrete
remaining acquisition needs; local model work must not wait for TTR acknowledgment.

Selected TEMPORAL-68 variant: absolute RGB difference of the two already aspect-fit
96×64frames, through3→8→16→24convolutions (3×3,strides2/2/1), pooled4×6,
Linear576→32→1 with ReLU. This replaces only the old change head; geometry retains
the exact existing encoder/cell/geometry/context modules and their seeded initial
weights. Shared geometry no longer receives change-loss gradients, an explicit
architecture difference to report. The change branch is frame-order invariant and
receives identical zero inputs for any duplicated frame; its output is learned,
not a hardcoded no-change answer. No label or threshold changes.
Keep the old spatial module byte-for-byte unchanged for legacy/gate compatibility;
new module/configuration carries the difference branch. Gate on DTM012's32pair fit
evidence plus the existing exact expanded-data admission. One600epoch candidate,
not an adaptive search. Reuse the batched evaluator via an explicit temporal mode.

#### TEMPORAL-68 outcome

DTM013 retains32/32fit and128/128trained shifts. Settings raw change5/5, false changes0,
but localized0/5and both true moves abstain on invalid boxes. Duplicate-frame raw
change becomes0/48original,0/16added,0/10Settings. All development, not qualification.
Architecture315,235parameters versus881,819; observed pair medians15.34ms versus
15.42ms show no meaningful latency claim. Final checkpoint1,268,673bytes, no export.
81Python/134Swift checks; both actual image-only CLI paths match stored predictions.

Acquisition companion reuses the exact existing24case catalog, grouped into12recipe
groups and6batches of4cases (600s/job,120s/case), one proposed qualified session.
Retained inventory has zero strict stationary-contract candidates; the eight admitted
legacy negatives must not be recaptured or relabeled. Native high-contrast/layout
coverage remains a source-capability gap. All proposed seed83cases are related
development evidence, not reserved independent evaluation. No runtime operation.

### Next tranche — localize69

FreezeDTM012/013 and existing37pair membership. Decompose all endpoint errors into
center/extent, invalid-border and effective96×64target dimensions, grouped by
original24/added8/Settings5. Inspect input-space distributions to distinguish low
resolution, annotation convention and unseen geometry hypotheses; do not claim a
cause solely from five exposed cases. Use the existing decode/geometry functions
and raw logits for invalid boxes; no label repair or clipping to manufacture success.
Compare unchanged geometry initialization, loss-gradient routing and recorded model
outputs without training or changing thresholds. Preserve source/backend hashes.

Companion: reuse each encoded ordered image tensor across the two frozen models in
the existing evaluator. Validate exact prediction/decision parity with the image-only
entrypoint, bound memory by one pair/condition and record PNG-decode, resize/encode
and forward/decode timing separately. No new input resolution, inference API or
public library API is assumed. Existing callers retain identical behavior.

Deliver one geometry failure report and a justified next architecture/data experiment
(e.g. resolution or candidate-based localization only if supported by evidence), with
the unchanged data/authorization boundaries. Do not execute another unchanged run.
The existing session acquisition plan can be reviewed without blocking this work;
larger acquisition needs qualified producer capabilities and a separate capture scope.

LOCALIZE-69 implementation: expose internal encoded-input inference while preserving
the existing image-only result contract. Refactor raw coordinate decoding so invalid
boxes can be diagnosed without silently clipping them. In one frozen replay, decode
each source pair once, encode each transformed pair once for both models, and compute
endpoint center/extent/border/cell-rank diagnostics on the74baseline endpoints per
model. Ground-truth-center/extent/cell substitutions are scoring-only oracles, never
predictions. Revalidate source membership once on entry and require parity for every
stored TEMPORAL-68 prediction, including rejected cells and counterfactuals. Old
training protocols are not edited or repinned to new inference code. Warm preparation
pins still reject changes for training; the explicitly frozen replay uses fresh native
intake instead of bypassing those pins. Report that one-time intake cost separately.

#### LOCALIZE-69 outcome

1,366stored predictions and20rejected cells reproduce exactly.148baseline model
endpoints diagnosed. DTM013Settings correct cells0/10,localized0/10,invalid2/10;
mean absolute center errors20.61/3.76input pixels and extent errors21.71/12.40.
Scoring-only center/extent/cell oracles each localize0/10. No box clipping/label repair.
Training has only11.08×20.5,76.05×4.05and16.49×16.49size combinations; Settings39×~4
falls between marginal ranges but outside their actual joint support. All10Settings
centersx72.35–72.61 exceed trainingmax48.23and old±4%augmented max~52.07.
Five Settings heights are below training minimum4.05; that alone does not explain
the large horizontal error. Coverage/domain mismatch is a hypothesis, not proven
causality from five exposed examples.

Fresh intake19.115s,PNG decode2.985s,shared encoding9.489s,forward/box decode0.681s,
total35.232s including diagnostics. Post-intake16.117sversus previous25.592stotal
with warm intake; report differing timing scopes.84Python/134Swift checks pass.

### Next tranche — coverage70

Outcome: two fixed comparisons that separate position coverage from combined
position/extent coverage, using DTM013architecture and unchanged32train/5development
admission. No inference resolution, loss, labels, thresholds or data-role changes.
Under assigned local experiment authority, use two600epoch fresh runs,seed42,Adam
0.001,batch8,2GiB combined outputs,no-wall-time cap; fixed-last, no automatic sweep.

Arm1: existing baseline plus four source-resolution paired translations, horizontal
±25%viewport width and vertical±15%height. Arm2: baseline plus the same four shifts
after horizontal compression0.5around image center, leaving vertical scale1.0.
Both frames receive exactly the same affine transform and integer raster placement;
transform labels with the actual rounded resize ratio/offset. Reject off-frame target
boxes, never clip them. Black fill and non-native distortion are explicit limitations.
No new synthetic examples gain independent corpus/admission status.

Before launch, validate one corpus snapshot and generate both deterministic banks
from it. Report valid/rejected views and resulting joint position/shape support,
including whether right-side half-width rows become represented. Do not lower bounds
or silently resample to force coverage. Keep baseline available for every pair; fixed
seeded per-pair sampling and600epochs imply different per-view exposures when views
are rejected, which must be reported. This is development-driven hypothesis testing,
not final holdout tuning or a claim of native rendering realism.

Integrate into the existing trainer/preparer/batched evaluator with versioned policies
and unchanged legacy paths. Test rounded affine geometry, no label leakage, both
frames aligned, out-of-bounds rejection, deterministic membership/schedules, separate
cache identity per policy and legacy parity. Freeze protocol/pins after code settles.

Evaluate frozenDTM013plus both candidates together on original/added fitting, exposed
Settings, zero-difference and the existing shift probes. Report center/extent and
paired IoU, raw/usable change decisions, abstentions and timing. A gain only on these
exposed cases does not establish generalization; native no-scroll positive/data
diversity gaps and independent final qualification remain. Failed arms get diagnosis,
not another automatic run. No Simulator/TTR operation, export or promotion.

COVERAGE-70 cache contract: prepared-input v2 explicitly records augmentation policy;
v1 remains original4%only. Real preflight and fit require the policy to match model
configuration. Prepare both banks through one source-validation operation and decode
each raw pair once across policies. Preserve separate schedules/view rejection counts
and protocol identities. Both models retain DTM013seeded parameters and inference
contract; only training views differ. Compare reference plus both candidates together
using shared encoded inputs, including baseline checkpoint parity for all models.

COVERAGE-70 outcome: both arms completed600epochs; own-bank paired geometry/change
fit120/120 and152/152. Both retain32/32 original membership fit, but exposed Settings
paired localization remains0/5. DTM014 change5/5,DTM0154/5. No further automatic run.
See reports/work/COVERAGE-70/handoff.md for shared-input timing and evidence.

### CAMPAIGN71 — campaign-to-corpus batching

Inputs: existing stationary acquisition campaign/inventory, source-specific consumer
validators, prepared-input v2, actual producer capability declarations when available.
Authority: local software/tests only; no launch/capture/install or new data-role choice.

1. Extend existing campaign planner with immutable case/group identities, target/build
requirements, per-case budgets and fresh output destinations. Plan coverage for several
experiments together; retain related-group isolation and separate final reservations.
2. Add an append-preserving journal: planned, running, completed-unvalidated, accepted,
rejected, interrupted. Verify output/receipt hashes before reusing accepted work.
Unknown running state requires reconciliation, not recapture. Resume missing cases only.
3. Reuse a healthy authorized runtime across bounded batches. Session preflight does
not replace per-capture identity/focus/geometry checks. Canary once per changed runtime
contract, postflight each batch, teardown only owned resources at campaign end.
Implement/test this boundary offline; actual runtime integration remains gated.
4. Incrementally validate new immutable shards with existing entrypoints. Preserve
partial/rejected evidence. Freeze a corpus version only after full membership, hash,
label, duplicate and cross-group leakage checks; never silently shrink the plan.
5. Scope prepared-cache keys to data/labels/roles, preprocessing/augmentation and
relevant implementation/dependency versions. Keep training-code pins separate. Prove
model-only edits permit input reuse, while transform/role/source edits invalidate it.
Never retrofit old protocol hashes or waive source integrity to obtain a cache hit.
6. One predeclared experiment group uses the frozen corpus and shared evaluation.
Record cold preparation, warm load, capture/setup/cleanup, verification, fit and human
wait separately. One integrated handoff; no per-helper mandatory turn boundaries.

Tests: interrupted/partial batches, stale or mismatched runtime, collisions, changed
bytes/roles/transforms, corrupt tensors, unacknowledged cleanup, duplicate identities,
concurrent journal edits, resume equivalence and model-only cache reuse. Deterministic
fakes must exercise real caller boundaries. Required offline Swift checks once at
integrated handoff. No claims of simulator lifecycle speedups without live measurement.

Acceptance: one offline campaign can interrupt/resume without duplicating accepted
members; two model configurations reuse identical verified inputs; changes invalidate
only affected derivatives; failure leaves recoverable evidence. Next action is a
separately authorized live campaign after current producer support is verified.

Implementation contract: opt-in prepared-input v3 scopes pins to preprocessing,
admission and source-validation functions/dependencies; v1/v2 retain strict legacy
pins. Training protocols still pin all model code. Do not silently migrate old caches.
Campaign journal is local append-only numbered sealed events linked to previous hash,
with exclusive file creation and expected revision. No lock takeover. It records
external operation evidence, never dispatches device commands. Planned case bindings
must include exact producer case/recipe bytes before intake; journal acceptance means
inspection acceptance, never training admission. Runtime identity and cleanup evidence
are checked at each completion. Rejected/interrupted work needs explicit reconciliation
and a fresh attempt destination. Cached intake verifies every referenced source hash.

CAMPAIGN-71 delivered offline interface:
`scripts/stationary_campaign_journal.py init --plan PLAN --bindings BINDINGS --root NEW_DIR`.
Bindings contain `runtime` (simulatorID,fixtureRunID,buildSHA256) and a `cases` map
of planned IDs to exact producer case-file path/hash references. ReferencePack
screen/seed/variant/artworkStyle and actual recipe theme must match the planned axes.
Missing source-supported axes block binding, not silently reduce coverage.
`status --root DIR` returns head/revision and missing/reconciliation lists.
`start|complete|interrupt|reconcile --root DIR --case ID --receipt FILE --expected-head HASH`
records external evidence; start additionally requires `--destination NEW_PATH`.
Receipts bind runtime,caseID,observedAtUTC,authorityReference; start needs ready=true,
complete needs responsive=true,cleanupVerified=true and exact destination. Reconcile
needs cleanupVerified=true,retryAuthorized=true. These are evidence records, not
device authorization or proof of authenticated runtime identity.
`intake --root DIR --case ID --evidence RAW_CASE --expected-head HASH` calls the
existing strict stationary consumer. `freeze --root DIR --output NEW_FILE` requires
all cases accepted, rechecks hashes and decoded-pixel duplicates, and emits a
development-only inspection corpus. It is not the training admission manifest.
Uncertain running jobs never become missing work automatically. Partial journal or
intake writes fail closed and remain evidence; manual reconciliation is required.

Use `prepare_transition_inputs.py --corpus CORPUS --admission ADMISSION --output
NEW_BANK --scoped-input-pins` for v3. Old paths remain v2. No old manifests are
rewritten. Real32-pair verification produced160views matching legacy tensors exactly;
two model configurations reused them in0.171/0.169s through the existing training-bank
entrypoint, without launching a model. Native capture remains unqualified by this work.

### COMPATIBILITY72 — producer contract binding

Read-only source audit of local TTR revision f933e2994ae07a967267dd00ed9d61d63b3cef7c.
Reuse CampaignRunnerSession (connect once, status on subsequent acquire, disconnect
at invocation finish). Do not request or implement another remote-session manager.
Producer CampaignTransition uses focus_moved/boundary_unchanged. Add explicit
consumer semantic mappings to interior_switch/boundary_noop, preserve original wire
specification and require existing strict no-scroll/focus/cleanup evidence. Legacy
scroll intake unchanged; a name never proves no scrolling. Test both names, actual
consumer entrypoint and mutation/offset failures. Bind journal cases using this same
mapping; never rewrite signed/hash-bound producer evidence to rename a condition.

RichReferenceCoverageCompiler only emits appearance,scroll_unchanged,scroll_moved.
Native table directional planner emits focus_moved but current help marks table capture
feasibility-only. Source presence is not execution eligibility. Distinguish reference
backdrop light/dark from recipe theme. Report unresolved matrix cells rather than
invent source-supported recipes. Deliver source hashes, focused/offline checks and
an existing TRANSFER-62 follow-up; no capture, training or another-repository writes.

### PROPOSALS73 — candidate coverage diagnostic

Use the admitted five Settings development pairs, original pre-review proposal
batches and source-validated human review as scoring-only truth. Reuse frozen
COVERAGE-70 predictions, checking exact image/membership/model hashes. No fresh
model inference or capture. Report actual proposal presence and focus-box recall
separately from unavailable proposal provenance. Empty saved lists do not prove
an independently run detector failed. Diagnose snapping predicted boxes to human
box pools using nearest-center and maximum-IoU rules with deterministic ties;
these are explicitly oracle-pool diagnostics, never deployable results. Reject
invalid predicted boxes rather than reconstructing discarded coordinates.
Tests cover empty/missing pools, invalid geometry, ties, unrelated source hashes,
and exclusion of focus labels from selection. Record per-endpoint and paired
accounting. Deliver a bounded candidate-input contract and next data-source decision.

PROPOSALS-73 found retained Vision rectangle results in the source-bound semantic
artifact, independent of the empty annotation-proposal lists. Existing rectangles
cover10/10focus endpoints atIoU0.5 (nine unique images; bestIoU0.851–0.939), with
19–24proposals per image. This is automatic rectangle coverage, not correct focus
ranking or UI-element detection precision. Frozen coordinate snapping remains poor.

Next bounded contract — PROPOSAL-RANK-74: inventory source-compatible training-side
candidate coverage on the unchanged32admitted pairs; use existing Vision/production
preprocessing infrastructure rather than another capture pipeline. Candidate input
contains image hashes, source/revision/settings, IDs and geometry only. Human/native
focus states and after correspondence enter labeling/scoring only. Never replace
missing automatic proposals with truth boxes except in a separately named oracle arm.
Freeze actual and oracle bank memberships separately; retain all five Settings cases
as exposed development and all related groups excluded from final evaluation.
First software tranche supplies candidate recall/ambiguity accounting, missing-box
abstention, deterministic pairing and source-hash tests. A subsequent explicitly
scoped visual-ranking experiment compares matched inputs with the existing direct
baseline; no unchanged coordinate-regression rerun and no threshold tuning here.

PROPOSAL-RANK-74 execution scope: local native Vision rectangle extraction on the
existing32admitted training pairs only, deduplicated by source hash, using the existing
probe with an opt-in rectangles-only request. Preserve old OCR/default behavior;
build a separately named project-local executable. At most64training endpoints,
40unique images per invocation,180seconds per invocation,256MiB new output budget.
Use verified read-only SSD mappings without copying raw corpora or widening writes.
Reuse pinned retained Settings rectangle results (no fresh development inference).
Freeze label-free candidate inputs separately from supervised target/coverage metadata.
Targets are multi-positive IoU≥0.5, missing-positive cases remain explicit; no filtering
to manufacture readiness. Check positive ambiguity/negative support, exact frame roles,
and native request revision parity before proposing a ranker. No training/model export.

After the first automatic bank exposed missing positives, compare the already-existing
human_auto_boxes raster proposer on the same deduplicated training images, without
parameter tuning or passing existing/human boxes. Report fixed Vision/raster/union
recall separately and keep originals. This local fallback comparison is included in
the feasibility tranche; no automatic membership reduction or model launch.

Outcome: Vision40/64training and10/10development; fixed raster64/64training and
0/10development. Union64/64+10/10, with40multi-positive training endpoints and no
ambiguous development positives. Both sources remain used, without source-dependent
routing learned from development truth. Frozen v2 union inputs allow≤80candidates;
actual max59,2,141candidates/59images. Supervision is a separate artifact, all37pair
roles unchanged. No oracle pool substituted for automatic proposals.

Next experiment proposal: one candidate visual ranker with multi-positive objective
(negative log summed probability over IoU-positive proposals), explicit no-candidate
abstention and per-source/multiplicity reporting. Use production crop infrastructure
for any crops, exclude source IDs/confidence/focus labels from learned visual inputs,
retain actual candidate recall as a separate ceiling. Keep DTM013 raw change branch
frozen for the first comparison so geometry selection is the only changed component.
Freeze architecture/epochs/seed/outputs and log before any run under applicable model
experiment authority. No automatic training, export or promotion in PROPOSAL-RANK-74.

### RANK75 — visual ranking and crop batching

Goal-selected local experiment tranche under standing authority: one new candidate,
600epochs,seed42,Adam0.001,CPU2threads,fixed-last,2GiB total output,no wall-time cap.
New architecture explicitly scoped: production16%/256crop, then declared16×16RGB
bilinear visual encoding,flatten768→Linear32→ReLU→Linear1. No coordinates, source
IDs, detector confidence, native focus or semantic text as learned inputs. Multi-positive
frame loss is logsumexp(all scores)-logsumexp(positive scores). Average equally over
50unique training frames, preserving all64training endpoint labels and32pairs; duplicate
frame positive sets must agree. One full-frame-set update per epoch. Settings remains
development-only. Fixed600epochs is an optimization diagnostic, no adaptive reruns.
Select top score, ties by stable candidate ID; abstain on missing candidates/invalid
input. This is uncalibrated top-one ranking, not a confidence-qualified deployment.
Reuse DTM013 frozen change probabilities on identical pair membership; do not retrain
or change its threshold. Report focus endpoint/paired geometry and joint change accuracy.

Independent efficiency companion: request-local image reuse in existing FocusRingTool,
count decoded-pixel budget over distinct source images, reject conflicting hashes for
one path, keep per-item bounds checks and128item cap. New opt-in candidate batching
in existing adapter; old16item callers preserved. Verify shared-vs-single crop pixels,
hash mismatch and bounds failures through actual executable. No second cropper/trainer:
wire ranker preflight/execution through train_focus_ring_detector.py and existing
experiment dispatcher. Cache image-only crop encodings once, supervision separately.
Pin bank, runtime, encoding, dependencies and code before launch; log protocol/run first.
Tests cover missing/multiple positives, label-free ranking, candidate order, train/dev
isolation, output collision, code/source/tensor changes and runtime crop parity. Final
offline Swift build/tests once after integration; no production export or model swap.

RANK75 outcome: DTM016fits64/64training endpoints/32pairs;0/10Settings/0pairs,
correct candidate ranks20–27. Frozen DTM013change remains5/5Settings. Both candidate
existence and training fit are established, native visual transfer is not.59Python
tests and134Swift tests pass; checkpoint replay and order parity verified. Crop bank
29.639s once,600epoch fit1.014s,warm load0.130s. Future cache reuse checks original
encoding dependency versions, not only the next run's environment. No retraining.
Next: supported native stationary campaign binding and qualified appearance coverage,
with independent final groups reserved before tuning. See RANK-75 handoff.

### NATIVE-INTAKE76 — retained native coverage and throughput

Standing approved intake/coordination backlog selection. Inputs: exact published
tvtestrig-20261003-native-table-directional12, native-rich24, throughput-review and
grouped-workflow-review-r2 artifacts. Copy immutable named bytes to project-local
ignored storage, verify size/hash, use existing bounded archive checks and publish
exact receipt under NUA namespace. Sender owns deletion; receipt does not approve labels.
Validate all indexed images/sidecars, native observations, geometry, completion and
stationary/scroll relations through existing consumers. Report unsupported versions
without rewriting raw evidence. Account for all36reported pairs; known shared renderer
ancestry stays calibration/inspection, not independent final evaluation or training.
Inspect source declarations and retained diagnostics for actual case bindings; local
TTR source remains read-only and cannot establish uncommitted producer implementation.
Companion: assess two published throughput reports, separate measurements from claims,
and update batching guidance with source-backed supported behavior and exact gaps.
Tests cover parameterized receiver defaults/path restrictions/integrity and applicable
consumer extensions; one integrated offline build/test after code. No runtime/capture,
training, data-role decision, Git write or external repository mutation. If source
is absent, return a specific compatibility report while completing integrity/accounting.

Source f933e299 includes NativeTable version1 geometry and native-navigation mode;
extend that exact consumer recipe/endpoint contract only. NativeTable version2 rich
content is absent from this checkout and remains blocked pending source publication.
Unknown scroll offsets in the older12pair export stay unknown, not stationary.

Outcome:36pairs/72distinct decoded images verified,12NativeTable-v1directional cases
pass strict inspection with unknown scroll;24rich-v2cases remain unsupported.
Existing no-scroll consumer still refuses old12offset evidence. All4artifact receipts
published/read back, no sender cleanup claim.57Python/134Swift checks pass. Next source
publication for NativeTable-v2/rich contract and grouped scripts; no producer binary
or recapture. Source FixtureAppearance.swift SHA256
d84d421693e106e4b55b265997bcd6adc23c1953135d1235e7e9aec63df4408e.

### NATIVE-ADMISSION77 — exact native role proposal

Inputs:76inspection report/raw native-table12 and65admitted32train/5development
corpus. Rebuild all12labels through source-pinned directional/native-body validators;
compare source hashes, byte/decoded overlap, group ancestry, themes and target geometry
against existing membership. Propose12calibration→train only, preserving all37old
records/roles and whole-renderer exclusion from final evaluation.44train/5development
is a proposal, not admission; all12new cases are changed, scroll unknown. The24rich-v2
cases remain excluded pending source uptake. Independent implementation companion:
extend existing direct collector with optional native-table source and explicit-role
admission builder using exact membership digest, positive maintainer decision and
original corpus binding. No implicit acceptance from sourceRole, inspection pass,
standing goal or available pixels. Test absent/mismatched approvals, changed original
roles/membership, leakage and source corruption, plus actual prospective CLI. One
integrated offline check. Finish with one reviewable proposal; training stays gated.

77outcome:12new pairs6light/6dark,all changed,unknown scroll,zero cross-corpus decoded
overlap under existing RGBA hash convention. Original37records unchanged. Prospective
49record collector rebuild matches exactly;44train/5development assignments tested
in memory only. No admission file written. Member digest
7583cb0951b3a903f4d9cf8efdefcc7671b2dfc58a9444e16c6fd6d5bbecad34.
13Python/134Swift checks pass. Next requires maintainer role decision; no implicit
approval from the goal or producer calibration metadata.

### NATIVE-PROPOSALS78 — calibration coverage before training

Use77pending proposal as an exact membership reference, then revalidate original
native labels. One batch of up to24unique retained PNGs through existing source-pinned
Vision rectangles-only probe (180s cap), plus unchanged raster proposer. No images
leave the machine; no simulator operation. Ground truth only scores outputs after
generation. Preserve raw response, image refs/dimensions, implementation hashes and
per-endpoint recall/ambiguity at fixedIoU0.5. Report per-source recall and missing
controls without filling gaps with labels. Candidate outputs remain calibration,
training-ineligible; schema does not relabel them train/development to fit an older
loader. Integrate through existing prepare_proposal74 entrypoint and regression tests.
Companion outcome is a reusable batch/raw artifact for future approved crop preparation,
not another native call after approval. No new model run, role or source admission.

78outcome: Vision24/24covered,1ambiguous; raster24/24covered,0ambiguous;
union24/24covered,24ambiguous,196candidates/max11per image. Successful native batch
0.862s,total4.109s. Restricted invocation failed CVPixelBuffer(-6662); diagnostic
and original execution retained, scoped host-access comparison succeeded. No restart
or producer edit.49Python/134Swift tests pass. Inputs are calibration-only and reject
the existing training-bank loader;77decision required before role-bound bank expansion.

### BATCH79 — retained data to reusable experiment campaign

Outcome: eliminate experiment-by-experiment acquisition and preparation. Reuse71's
journal,74/78's automatic proposals,75's production crop bank and the existing trainer.
This contract groups deliverables; it does not grant capture, data-role or training
authority. Tasks.md alone tracks ownership/status. No new lifecycle controller,
parallel trainer, parameter sweep or retrospective cache resealing.

**Inputs and current inventory:**32admitted training pairs and5exposed Settings
development pairs;12table calibration pairs whose exact77role proposal is pending;
24retained rich-v2pairs awaiting published source compatibility. The74bank contains
2141candidates/59images;78contains196candidates/24calibration images. The table pairs'
scroll state is unknown. Shared Fixture ancestry is not independent final evaluation.

**A — Retained-source compatibility and coverage:** Read the published rich-v2 source
revision before extending existing strict validators; preserve historical v1/v2 wire
evidence. Exercise actual intake on all24retained bundles and report each rejection
with its field/stage. Derive coverage by observed condition, theme, native control and
geometry; distinguish requested from observed axes. Reconcile this against the existing
24case/48frame stationary qualification catalog before requesting additional pixels.
Never treat table unknown-scroll pairs as satisfying stationary cells. Deliver exact
coverage gaps and one role proposal for any additional qualified members. Acceptance:
all retained members accounted, raw bytes unchanged, actual consumer entrypoint plus
positive/negative compatibility tests; zero silent unsupported-field stripping.

**B — Incremental inputs and controlled comparison:** Extend the existing ranker
preparation entrypoint to reuse an image-only derivative cache keyed by source bytes,
candidate geometry, production crop implementation/runtime and encoding dependencies.
Maintain a separate role/supervision-bound experiment manifest. Test the implementation
with generated fixtures before approval; materialize the44/5admission only upon the
explicit77decision. Do not make the calibration schema acceptable to the old training
loader or overwrite old protocols. Combine approved74/78members, verify unchanged
derivative dependencies and prepare only new or invalidated entries. Keep multi-positive
labels separate from proposal generation. Acceptance: cold/warm/incremental tensor
parity; counters prove unchanged images are not recropped; changed bytes, transforms,
dependencies, roles and duplicate ancestry fail or invalidate correctly. A model-only
edit must reuse inputs while still producing a newly pinned model protocol.

After admission, predeclare one native-transfer comparison against DTM016 on identical
compatible membership/settings, with fixed DTM013change control. Record hypotheses,
epochs, dependencies and authorization before launch; no run is authorized merely by
this plan. Compare old/new training support separately from exposed Settings results,
with errors, abstentions and end-to-end stage timings. Failure is a decision, not an
automatic next candidate. Retain existing models; no export or promotion.

**C — One missing-coverage session:** Bind the existing stationary catalog to actual
supported producer case files and runtime contracts. Its present size is24cases in
six4case jobs,120s/case and600s/job; retain those bounds until a separately reviewed
change. It is a development qualification matrix, not a full training corpus. Remove
a planned capture only with explicit evidence that retained data satisfies the same
semantic cell and permitted role; preserve the original catalog and reconciliation.
Request exact target/build/endpoint/storage/session and case scope together. Capture
only after approval and fresh readiness. Use existing CampaignRunnerSession lifecycle;
one healthy runtime, serial jobs/export initially, per-case evidence, per-job health,
owned-resource cleanup. Stop on uncertainty; never replay ambiguous mutations.

Use71journal for missing-only resume and incremental intake. It records evidence; it
does not execute commands. A supported producer invocation must be verified rather
than inferred from the journal. Freeze membership and run the complete final integrity,
duplicate and ancestry audit; unchanged-focus identical frames must remain accounted,
not discarded as useless duplicates. Reserve genuinely independent final groups in a
separate approved source plan, not by slicing this renderer's related variants.

**Integrated verification/handoff:** Focused changed-path tests during work, one offline
Swift build/test at integrated code handoff; no rebuild for this prose contract. Test
interruption/resume, collisions, stale identity, uncertain cleanup, partial export,
changed validators and unauthorized roles. Record cold setup, successful capture,
rejected attempts, export, intake, preprocessing, fit/evaluation and waits separately;
show unique semantic coverage as well as throughput. Software, data eligibility,
producer integration and model gates remain separate. One handoff per assigned tranche,
not one per helper. Source waiting blocks A/C, not B's offline implementation. Missing
role approval blocks admission/model execution, not compatibility or cache tests.

B implementation boundary: add opt-in `--derivatives-only --inputs PATH --cache-root
PATH` to the existing ranker preparer. This emits an inspection-only derivative
manifest and no protocol/approval. Accept sealed existing candidate inputs or the
calibration-only proposal schema; never upgrade its role. Cache one immutable entry
per source-byte/ordered-geometry/size/preprocessing identity. Role changes may reuse
these pixels but must still pass the separate admission/supervision boundary.
Partial or corrupted cache entries fail closed, not overwrite. Existing preparation
may opt into the same cache; legacy default/protocol formats remain compatible.
Measure cold, warm and appended-image preparation and prove exact legacy tensor parity
on retained inputs. No new candidate is launched in this software tranche.

Maintainer continuation now approves the exact77data-role change and explicitly
authorizes capture/training/promotion subject to existing gates. Selected next tranche:
materialize44train/5development, bind retained83image derivatives, evaluate fixed
DTM013change control and DTM016ranker on all49pairs, then train one DTM017ranker.
Keep600epochs,seed42,Adam0.001,CPU2threads,fixed-last selection and unchanged768→32→1
network; full-batch unique training frames increase50→74. Hypothesis: native-table
examples improve native focus ranking versus synthetic-only DTM016, without changing
representation. Report original32/new12fitting separately from five exposed Settings
pairs; no independent-final claim.2GiB outputs,no-wall-time cap, no automatic retraining.
No new capture needed; no promotion unless applicable gates pass. Preserve old models,
raw sources, roles and protocols. Use existing trainer dispatcher, not a new trainer.

### CHANGE80 — native change adaptation and ranking diagnosis

Under the maintainer's explicit training approval, one DTM018 comparison fine-tunes
only DTM013's change submodule, retaining its exact architecture and all geometry
parameters bit-for-bit. Fixed600epochs,full44pair batch,Adam0.0001,seed42,CPU2threads,
baseline96×64paired encodings,no augmentation,standard BCE-with-logits,fixed-last.
Initialization is DTM013, not random; this is supervised adaptation, not a repeat of
DTM013's joint/augmented training. All44train labels participate, including20unchanged;
five Settings pairs remain exposed development only. Compare old/new raw change,
confidence/abstention and joint results with frozen DTM017boxes. One run,2GiB,no wall
cap; failed gates produce diagnosis, not another automatic run. No capture/promotion.

Independent diagnostic: use retained DTM016/017ranks and proposal geometry to quantify
Settings false selections. Record pixel-size/context-loss hypotheses, not a causal
claim or post-hoc filter presented as qualification. No tuning on final data exists.
Reuse existing encoding, model and trainer dispatcher; test change-only gradient scope,
unchanged geometry weights, checkpoint reload, admission/label/membership/approval
rejection. Prepare image tensors once and compare both models on identical inputs.

### SIZE81 — restore candidate scale to visual ranking

One DTM019comparison under current training approval: unchanged44/5membership,
83images/2337proposal crops,600epochs/full74frame batch,Adam0.001,seed42,CPU2threads,
fixed-last. Append normalized original candidate width/height to the768RGB inputs;
no x/y position, source/app identity, predicted focus or labels enter inference.
Expand first linear layer768→770inputs with the two new columns initialized to zero;
common visual weights/bias/output use the same initialization as DTM017. The model
can learn scale, not a hand-coded minimum-size filter. Architecture/output budget
remains bounded2GiB; no automatic follow-up candidate, capture or promotion.

Compare against retained DTM017on exact membership and retain DTM013control for the
ranker-only comparison. Separately report joint scores using accepted experimental
DTM018change probabilities, clearly identified rather than silently swapping control.
Companion: audit positive/negative proposal size support by admitted source and split;
small true controls absent from this corpus remain an explicit qualification gap.
Reuse original image derivatives (no recrop), rebind only new protocol/model code,
test size normalization, malformed dimensions, no position dependence, legacy loader
compatibility, initialization equivalence, checkpoint replay and candidate ordering.

### INTAKE82 — portable intake and admission regression boundary

While rich-v2 source is unavailable, strengthen the existing retained-selection
entrypoint: verify export receipt completion, campaign/case identity, original
manifest byte hash/length and exact selected file inventory before semantic intake.
Use input_manifest_sha256 for bytes, not the distinct semantic manifest_sha256
(producer SyntheticCampaignCoordinator export contract at f933e299). Preserve all
raw evidence and continue rejecting unsupported rich recipes. No data-role changes.
Replace retained-corpus-dependent admission unit tests with generated 32+5+12 records;
add generated 24-case receipt tests for missing/partial/mismatched/corrupt evidence.
Exercise strict selection on all retained24 cases and the actual intake CLI to a
new output, accounting for all36 pairs without claiming rich compatibility. Existing
live-corpus checks may remain integration-only, not the sole regression coverage.

### NATIVE83 — retained collection intake and local runtime diagnosis

Receive the named native-collection36 archive/report through the existing bounded
receiver and publish exact receipts. Extend the existing native intake CLI with an
inspection-only collection mode: four completed campaign receipts,36 selected cases,
all408 receipt-listed members and72 endpoint images checked; account for unsupported
consumer contracts rather than accepting producer self-assessment. No renderer schema
relaxation, data admission or new crop/training path. Report declared coverage separately
from independently validated geometry. Keep same Fixture ancestry out of final evaluation.
Companion: fresh matching-helper exact-target readiness, without capture over unknown
cleanup. Preserve operation identity and request source/recovery action via owned SMB
metadata. No automatic restart, repeated reconciliation or physical fallback.
One focused Python suite and integrated offline Swift pass; no training/capture.
