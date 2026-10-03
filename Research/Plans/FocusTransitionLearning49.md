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

Acceptance: fitted-subset and full-partition metrics clearly distinguished; no
ground-truth-cell oracle reported as model accuracy; exact gate decision and ranked
remaining data/model weaknesses. Existing shipped models and five exposed Settings
development examples remain unchanged. Select/request new data only under its own
authority; do not let producer availability block this local representation test.
