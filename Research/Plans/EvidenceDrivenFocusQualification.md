# Evidence-driven focus qualification — EVIDENCE223

Owner NUIAK; approved measurement-first tranche. Tasks.md alone tracks state.
Implement FOCUS-EVIDENCE, retained FOCUS-TRUTH and FOCUS-BASELINES together.

## Interfaces and implementation

Add internal `focus-evidence-v1` reports to existing transition and schema4 scoring
entrypoints. Rows identify case, connected group, role, condition, truth/decision and
label authority; context pins source/domain, task, model and preprocessing identities.
Unknown truth remains unknown; producer-reported labels yield agreement, not accuracy.
Reject duplicate cases, invalid values and cross-role groups. No public API change.
Preserve original metrics beside new reports. Exact binomial limits are descriptive
only when audited independent eligible trials are supplied, never by default for frames.
Paired group-resampled differences require identical membership/truth and at least
two groups; zero-error results cannot certify safety. Use fixed seed and report counts.

Retained integration reads CROP222 endpoint/union caches, BD12 native48 QA/index,
BD14/27 authored measurement reports and BD25 cached detector dispositions. Bind all
inputs by SHA256 in one manifest, create a new collision-rejecting output directory,
and preserve existing bytes. Derive missing evidence and per-case dispositions, not
new labels. Rank unmatched/geometry iOS candidates and retain deterministic 10% case
sample for review, not automatic correction. Compare frozen reported operating points;
do not tune thresholds or conflate authored and native results.

## Peer handoff

Extend existing BD18 statistics, BD22/25 QA and BD14/27 baseline tasks. One CPU job,
two threads, 2GiB RAM; total additional audit budget 4 CPU hours/256MiB outputs.
Reuse resident source/inputs; no GPU, installs, downloads, capture or new roles.
Each request pins exact named input hashes, expected reports/tests, stop conditions
and acceptance. Preserve Run035 priority and completed evidence. TTR supplies capture-
era source/geometry/observed-focus evidence for named failures, not a new generic
capture request. Publish one immutable amendment with readback; acknowledgment differs.

## Following tranches

### Focus position and visibility investigation — TRANSITION252

Goal: determine whether position or scrolling coverage explains focus-change errors.
Center bias is a hypothesis. Reading direction and initial item order do not establish its cause.
NUIAK owns analysis. TTR owns any required Fixture changes. Big Dog can score a later frozen package.

#### Inputs and authority

Use retained native captures, observed focus identities, per-frame bounds, viewport dimensions, ancestry, roles, and cached predictions.
Pin their hashes and actual coordinate systems before analysis. Keep requested focus separate from observed focus.
This packet covers offline investigation and experiment design. It does not dispatch capture or change running training.
Keep reserved and inspected development groups outside training. New derivatives retain their source group and role.

#### Investigation

1. Inventory available position, clipping, scrolling, and identity evidence. Mark missing fields unknown.
2. Map focus centers and visible box areas before and after each action.
3. Report a fixed 3 by 3 position grid, plus explicit edge, corner, partial-visibility, and invisible categories.
4. Separate focus movement from content movement. A fixed focus box can contain a newly focused item after scrolling.
5. Separate label classes, movement directions, initial item order, and connected groups in coverage reports.
6. Compare missed changes, false changes, abstentions, and localization errors on compatible cached predictions.
7. Report unsupported conditions rather than inventing labels or claiming uniform coverage.

Count independent groups alongside frames. Report start/end position combinations, not only a combined heat map.
Keep content coordinates separate from viewport coordinates. Scrolling can move content beyond the viewport without establishing invisible visual evidence.
If native observations confirm an offscreen identity, retain that fact separately from whether pixels show it.
Do not clamp a fully invisible box to an edge and treat it as a visible target.
An absent or clipped highlight does not establish unchanged focus. Allow unknown and abstention outcomes.

#### Missing-coverage proposal

Freeze quotas before generation. Use balanced categories with seeded variation inside each category, not random selection alone.
Vary initial focus, control order, control size, layout, highlight strength, artwork, and background independently where feasible.
Include these separate cases:

- Focus moves across edges and corners within the viewport.
- Content scrolls while the focus box stays fixed.
- Focus moves away from its usual anchor at the start or end of a list.
- A boundary action produces no movement.
- A focused control enters or leaves partial visibility during a transition.
- Content changes while observed focus stays on the same control.
- Focus becomes unavailable or ambiguous during a transition.

Use actual Fixture rendering for native cases. Image translation alone does not establish realistic scrolling or focus behavior.
Retain capture intervals and sequences when endpoint images cannot establish the event.
Score endpoint focus change separately from temporal readiness. Do not label an intermediate animation as settled.
Prepare one bounded campaign for missing cells. Reuse qualified setup and capture in batches.
First verify current local Fixture support. Ask TTR only for identified missing capabilities, not another general collection request.

#### Matched experiment and acceptance

Design a current-sampling control and position-balanced treatment with equal update budgets and fixed model settings.
Separate weighting changes from new-image effects. Do not attribute gains to position when class or group influence also changes.
Keep realistic-layout evaluation beside the balanced diagnostic. Uniform screen coverage is not a deployment distribution claim.

Acceptance requires a case-linked coverage report, explicit missing evidence, per-condition errors, and a reproducible missing-coverage catalog.
Test coordinate transforms, partially clipped boxes, fully invisible boxes, unchanged identities during scrolling, and changed identities at fixed positions.
Test unknown observations, duplicate-connected groups, and cross-role derivatives.
Report software checks, label eligibility, native integration, and model outcomes separately.
Then execute the selected bounded comparison under the applicable model and capture authority. Do not start an automatic sweep.

### Highest priority — focus improvement cycle

The maintainer selects this goal on October 6: repair 1 important visual failure without losing previous successful behavior.
Reuse TRANSITION205, FOCUSRING206 and existing evidence reports. Do not create a second trainer or intake pipeline.

**1. Select and measure.** NUIAK ranks up to 10 failure types from retained predictions and verified labels.
Each entry records task, source group, error count, support count, impact and suspected cause.
Unknown labels remain unknown. Separate capture, annotation, timing, navigation, proposal and model failures.
Choose the first visual failure with trustworthy labels and a reproducible local recipe.
Record the baseline, fixed scoring rules and minimum useful improvement before generating training variants.

**2. Prepare independent groups.** NUIAK records data roles before tuning.
Group related layouts, recipes, artwork variants and journeys together.
Reserve unfamiliar layout families where available. Existing reviewed calibration cases cannot become unseen final evidence.
If independent native evidence is missing, finish the synthetic experiment and limit its claims explicitly.

**3. Generate locally.** Use the supported local TTR and Fixture path from LOCAL-CAPTURE-232.
Source `0be978b3` supports the 4 verified recipes; it does not establish every requested generation capability.
Check the actual running versions, target ownership, cleanup and storage before each campaign.
Use approved USB storage for bulk outputs after checking the mount and capacity.
Record recipes, seeds, asset rights, version identities, observed focus, rendered bounds, actions and settling evidence.
Include focus changes with fixed content and content changes with fixed focus.
Add boundary no-ops, scrolling and interruptions when the selected failure requires them.
Ask TTR for support only after identifying a missing capability or a failed local check.
Request source changes, not a producer build. TTR can schedule support beside its other priorities.

**4. Validate and train.** Reuse automated integrity, geometry, focus and split checks.
Prepare a reproducible random sample and a separate suspicious-case sample in the existing annotator.
Record evidence-backed admission decisions under the standing authority.
NUIAK keeps short sequential tests local when worker pickup would delay the next decision.
NUIAK sends Big Dog independent batches with exact inputs, roles, initialization, preprocessing and acceptance criteria.
Compare total result time, not GPU time alone. Reuse resident inputs and cached predictions.
Record epochs or updates, storage limits and required returns before launch.
Compare the existing model with one justified candidate. Do not start an automatic sweep.
Big Dog returns checkpoints, predictions, configuration, timing, failure records and exact hashes.

**5. Verify the repair.** NUIAK independently checks returned results and previous successful cases.
Report target errors, false positives, abstentions and correct complete pairs separately.
Use related-group uncertainty rather than treating repeated frames as independent trials.
Training fit does not establish generalization. Compare reserved examples without tuning their thresholds.
If qualification passes, verify Apple preprocessing and model outputs before matched TTR navigation tests.
Keep native-assisted navigation separate from visual-only navigation.
Retain rollback artifacts and report efficacy to TTR.

**Completion:** one reproducible failure-to-repair report links data, training and evaluation.
It states the measured improvement, regressions, unsupported claims and next failure to address.
A failed model comparison still completes the experiment when it provides a supported diagnosis.
It does not complete the overall improvement goal.

FOCUS239 supplies the next controlled comparison after FDR041 fails to repair poster errors.
Change target artwork and backdrop separately. Preserve styles, geometry, text, and focus effects within each composition.
Use the 8 prepared development recipes before another fit. Keep Big Dog's feature comparison independent of local capture.
[Measured diagnosis and next batch](../../reports/work/FOCUS-ARTWORK-239/handoff.md).

**Parallel work:** NUIAK owns local generation and evaluation.
Big Dog reuses BD18/22/25/27 evidence work while awaiting exact model inputs.
TTR reviews missing capabilities asynchronously. Peer availability does not block local diagnosis or supported capture.

VERIFY226 retained inspection narrows the producer follow-up: bind repair09's
capture-era Fixture14/16 and host source/build identities to exact pair IDs; preserve
repair-cal01 diagnostic exclusion. Reuse four tabs/six streaming/one Apple candidate
inspection cases before collection. Source/body review and14production crops do not
automatically admit those cases. Different composite-card versus image-body semantics
must remain explicit. For later205/206 planning, vary foreground art and background
clutter independently while holding layout/target/action constant; preserve each
related family across roles. Poor hero contrast and repeated art are coverage issues,
not automatic geometry failures. See VERIFY226 retained visual review.

FOCUS-LOOP: after source qualification, reuse TRANSITION205/FOCUSRING206 membership
and shared source frames for one resumable campaign. Freeze roles before capture;
report accepted examples/hour and setup/rejection/transfer/intervention costs.
FOCUS-MODEL-SPIKES: only select a challenger after qualified comparison; no three-model
launch. Require eligible membership, matched control, fixed epochs/updates, memory
budget and Apple parity before training. Current evidence does not justify a new model.

## Acceptance

Tests: zero/all/no-support bounds; NaN/invalid counts; repeated/reversed/cross-role
groups; unknown labels; changed inputs/versions; unequal paired membership; output
collisions; partial measurements; preserved causal behavior; original entrypoint
integration. Focused checks then one offline Swift build/test pass. Native efficacy,
loop closure and model gates remain separately blocked where evidence is absent.
One handoff maps all acceptance, hashes, elapsed times, peer delivery and next action.
# REVIEW228 — diagnostic follow-through

Reuse DIAG227 cached proposals and the resident REPLAY219 schedule. Audit unique
training-image/class support separately from repeated slot exposure, verify source
labels and review representative original frames. Report confidence changes on
already inspected development membership without selecting a new operating point.
No new inference, training, label correction or role change. Native qualification
still requires the outstanding capture-era bindings; peer availability does not
block these local diagnostics. Deliver one review and a bounded next hypothesis.
