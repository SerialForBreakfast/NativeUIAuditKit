# TEMP-LIVE: Temporal visual-verification spike

## TEMP-FOCUS-02 — brightness and paired-change spike (2026-10-01)

### Assigned execution — 2026-10-01

**Outcome:** retained-evidence tranche completed; see
[results](../../reports/work/TEMP-FOCUS-02/handoff.md). Settings rule matches baseline,
not an improvement; universal brightness rejected. Genuine action-linked evaluation
remains open because no timing-valid retained action has both endpoints represented
in the accepted reviewed annotations. No fresh model execution or training occurred.

User assigned pending experiments and simple spikes. Execute a retained-evidence
tranche now: verify the supplied artwork metadata correction; compare FDR021 cached
scores with fixed brightness rules on the unchanged333 development/retention controls;
measure before/after scalar changes on existing same-control state pairs; audit the
retained Office action recording for reviewed, settled endpoints. No new model loads,
training, capture, split reassignment or human approval inference. Artwork training
cannot proceed while capture correlation and sampled acceptance remain missing.

Freeze this exploratory policy before measuring: use production256 crops; summarize
center192 pixels (body proxy, not a new cropper) with Rec.709-weighted encoded-RGB
luma, bright-neutral fraction(minRGB>220,range<25), and center-minus-outer-band mean.
Brightness rule requires luma>=0.60 and neutral fraction>=0.45; at frame level use
existing fixed0.85 selection metrics on binary rule decisions. A settings-scoped
hybrid substitutes that rule only for independently annotated settings families;
this is an oracle-context diagnostic, not a validated runtime Settings recognizer.
Also report model/rule agreement-only decisions. Fixed signed temporal luma delta
>=0.08 indicates arrival, <=-0.08 departure; otherwise unknown. Global motion,
missing tracking, clipping or unsettled input must be unavailable to any runtime
proposal. Downsample16/32/64/192body sizes are numerical sensitivity checks only,
not candidate thresholds to optimize after results. Preserve raw geometry growth
separately. Constructed pairs/no-op controls remain explicitly noncausal diagnostics.
No held-out qualification or model-selection claim from this already exposed set.

Maintainer requested adding this spike after reviewing the older results. Planning
owner: Codex; retained execution completed above, genuine follow-up remains in Tasks.md. This section is the current scoped
focus experiment proposal, not a claim that the older interruption spike ran.
No new capture, inference, fitting or TTR dispatch occurs in this planning task.

**Plain question:** Does comparing a control before and after a press identify
focus more reliably than looking at the after image alone, and can simple rules
do the job without another neural model?

### 1. Audit the available evidence first

Inventory retained TTR exports for actual ordered before/action/after sequences,
frame correlation, settled states, observed focus and stable control matching.
Pair counts alone do not establish a temporal corpus: independently rendered
focused/unfocused examples can support a static paired diagnostic but cannot prove
that a press moved focus, settling time, tracking or live navigation performance.
Record exact usable counts by settings rows, buttons, tabs and artwork; missing
sequences are a scoped collection request, not permission to fabricate ordering.
Use retained valid evidence without waiting for the deferred diverse-UI library.

Group by source/layout ancestry and session before splitting. Keep paired frames,
neighboring frames, cosmetic variants and derived recipes in the same split.
Previously inspected examples are development data. Tune only on development;
freeze rules before untouched grouped evaluation. If support is too small or no
untouched groups exist, report exploratory evidence rather than a generalization win.

### 2. Compare simple, inspectable signals

Reuse existing frame-change primitives and measured/detected control boxes. Build
small deterministic pixel summaries: interior luminance distribution and bright
pixel fraction, contrast against a surrounding band, edge/ring contrast, and changes
in those quantities across matched frames. Preserve raw viewport-relative width,
height and area changes: resizing each box to the same size erases growth evidence.
Declare the color/luminance conversion and resize method; use lossless source
pixels, not JPEG artifacts. Test several downsample sizes on development only and
measure whether compression removes thin highlights. Do not change production
FocusRing preprocessing as a side effect of this experiment.

Mask or separately account for text/artwork and clipped/occluded regions where
possible; a white poster is not focus. A same-control increase relative to its own
prior appearance can be informative, but global brightness shifts, changing media,
scrolling and animation can produce the same signal. Pairwise change also cannot
settle unchanged focus, initial-screen focus or uncertain control correspondence.
Keep an explicit unavailable/uncertain result for these cases.

### 3. Matched comparison arms

1. Current retained FDR021 single-frame decisions with unchanged fixed threshold.
2. Simple single-frame brightness/contrast rule, without model scores.
3. Before/after rule using matched-control change, growth and competitor evidence.
4. FDR021 plus paired-change verification, with explicit disagreement/abstention.

Report settings-only results separately from mixed UI results. A settings-specific
rule may be useful, but must be scoped by a validated runtime context signal—not
by a hidden ground-truth screen label. Test wrong/missing context classification.
Treat existing native focus as scoring truth, never a visual feature or decision
shortcut. Report oracle/native bounds and actual detected-box performance separately;
do not silently match controls using IDs unavailable to the deployed visual path.

A tiny learned classifier on these summaries is a possible follow-up, not required
to call this spike useful. Fit only under an assigned experiment envelope, using
independent native/human labels—not heuristic predictions as ground truth. To feed
these signals into a later model, version the feature contract and ensure every
feature is available at inference; train-only before images are not legitimate inputs
for a single-screenshot model. First establish incremental benefit of each signal.

### 4. Required stress cases and decision

Include bright unfocused artwork, subtle focused rows, dark focus, selected but
unfocused parents, focus leaving/arriving, no movement at a boundary, unchanged
focus, full-screen brightness changes, video/carousel motion, scrolling, overlays,
transitions, partial clipping, wrong tracking, missing/stale/reordered frames and
settled versus unsettled observations. Record absent strata, not synthetic passes.

Before held-out scoring, fix the comparison policy and acceptable false-selection,
abstention and latency limits. Report correct/wrong/no/multiple selection per frame,
transition verification errors, per-family support, coverage versus abstention,
and per-stage latency. Use paired differences and uncertainty at the independent
journey/family level; correlated frames do not supply independent confidence.
Existing release gates remain unchanged.

**Deliverables:** executable offline replay comparison with negative tests, exact
evidence inventory/split, readable example overlays, per-arm results and a decision:
use a settings-scoped rule, pursue a general temporal model, or reject the added
complexity. Offline build/tests and actual caller integration are required for
implementation completion. No automatic threshold sweep, promotion or live control.
The old 0/9 versus6/9 result used older shipped-model scores and is historical only;
it is not the baseline score of FDR021.

**Next executable scope when assigned:** inventory → feature/rule implementation →
development calibration → frozen replay evaluation → evidence-backed recommendation.
Do not split this into one-helper handoffs. If genuine sequences are missing, finish
software and explicitly limited static diagnostics, and specify only the missing
ordered capture evidence needed to complete the real transition comparison.

## Assigned development precursor: TEMP-FOCUS-DEV (2026-09-23)

Under the continuing unblocked-work assignment, NUIAK owns one offline temporal
focus diagnostic using retained, reviewed appearance frames and hash-bound cached
model scores. No capture, training, new model inference or producer edits. Reuse
TransitionTool production change regions and FrameSimilarity; do not implement
another image differencer/cropper. Current native element geometry is an explicitly
oracle-proposal diagnostic, not a YOLO end-to-end result.

Freeze inputs/policy before measurements. Compare single-frame unique focus at0.85,
diff-only unique changed-control localization, and a conservative model+change
intersection; no-change falls back to single-frame in the combined arm. Require
at least1% changed-region bounding-box overlap and a10-percentage-point lead over
the next candidate for diff selection. These are experimental fixed probes, not
calibrated thresholds. Regions only rank existing control boxes, never supply labels
or replace boxes. Truth enters scoring only after decisions.

Include retained reference→focus pairs, explicitly constructed focus-A→focus-B
replays, and identical-frame no-change controls. Constructed replays are **not**
recorded button-press journeys; no focus-settling/action-timing claim. All examples
remain development, correlated by recipe. Report per-kind/model correct/wrong/
abstained decisions, selected IDs, change coverage and primitive/process timings.
Keep unknown dimensions, altered bytes, invalid boxes/scores, ambiguity, unrelated
background change and output collision negative tests. Preserve invalid attempts.

Deliver real entrypoint/software tests, actual retained-image comparison and a
decision about the next genuine-journey experiment. This does not close TEMP-LIVE's
interruption matrix, independent held-out evaluation or live TTR qualification.

Parent task: `TEMP-LIVE` in `Tasks.md`. Plan revision: 1, 2026-09-22.
Execution state and owner: proposed / unassigned in `Tasks.md`.
Owning repository: NativeUIAuditKit for the replay evaluator and evidence contract;
TVTestRig owns any eventual live automation integration. Canonical catalog link:
`Research/ImplementationPlans.md`.

## Assignment contract

- **Outcome and why now:** determine whether a before/after visual guardrail makes
  TTR automation materially safer than fresh native state plus a single-frame NUIAK
  observation. The decision is about transition validation and agent explanations,
  not general image recognition or a new model.
- **Execution tranche:** one offline, frozen replay spike. It builds a versioned
  interruption/transition corpus, runs all comparison arms on identical inputs,
  produces a decision report, and either recommends a bounded simulator confirmation
  or documents that the temporal path is not justified. Packet checkpoints do not
  end the assigned tranche.
- **Dependencies:** accepted PER-05 causal sequence scorer and change-region
  contract; a pinned NUIAK detector/FocusRing artifact; Fixture or independently
  reviewed replay truth for every case. No completed TTR integration is required
  for the offline spike.
- **Slice boundary:** synthetic/Fixture replay may prove evaluator software and a
  design decision only. It cannot establish live TTR integration, device behavior,
  general model quality, training eligibility, or action authority.
- **In scope:** deterministic before/after replay, controlled Fixture mock overlays,
  candidate-box provenance, native/single-frame/temporal comparison, error taxonomy,
  latency accounting, and a predeclared adoption decision.
- **Explicit non-goals:** no real FaceTime/call, Apple-ID/sign-in, notification,
  mirroring, account, purchase, or device-setting event; no deep-linking an external
  app; no system mutation; no model training, promotion, new taxonomy, or automatic
  TTR action. A mock does not claim pixel equivalence to an Apple system overlay.
- **Allowed files and operations when separately assigned:** project-local evaluator,
  deterministic Fixture/replay generator, schemas/tests and reports under
  `reports/work/TEMP-LIVE/`; offline inference on pinned local models. Any Fixture
  launch, simulator capture, TTR change, or live confirmation needs its own exact
  target and operation authority.
- **Coordination:** the proposed producer capability is published as
  `nuiak-20260922T191858Z-live-visual-verification` in
  `nuiak/status.yaml`, packet `TTR-LIVE-VISUAL-VERIFY-REQUEST-20260922`. This plan
  is not a peer assignment or an acknowledgment of that request.
- **Relevant design:** `ADR-0009`, `FocusRingDetectorSpec.md`,
  `Plans/TTRPerception.md` PER-05, `schemas/transition-sequences-v1.md`, BP-40
  through BP-47, and the `tvos-fixture-training`, `tvos-safe-navigation`,
  `tvtestrig`, and `nativeui-model-workflow` skills when their operations enter scope.
- **Known behavior:** PER-05 already measures causal frame similarity and change
  regions. NUIAK currently uses current-frame YOLO element boxes, expands each side
  by 16%, redraws a 256x256 top-left crop, then scores FocusRing. It does not use a
  visual difference rectangle as an element box and does not currently compare time
  steps.
- **Stop conditions:** stop the affected case on missing, stale, reordered, altered
  or unlabeled frames; ambiguous focus; unavailable model; or a requested operation
  beyond replay authority. Preserve the invalid case and complete the remaining
  offline cases. Escalate live-target authority separately; never repair missing
  truth from expected input or a model prediction.

## Test matrix and truth

Each sequence contains a before frame, one bounded intended action, and after frames
with frame IDs, hashes, dimensions, timestamps, native/Fixture observation source,
expected transition and reviewed actual outcome. The decision function sees only
causal information. Truth joins only after it emits a decision.

| Stratum | Controlled example | Expected guardrail outcome | Truth source | Training use |
|---|---|---|---|---|
| Normal focus move | Fixture directional focus A to B | `agreement` only when current focus and expected B agree | observed Fixture focus plus same-frame bounds | eligible only under a separate corpus review |
| Expected dialog | Known inert Fixture dialog opens | `agreement` only for declared dialog/button state | observed Fixture scene and bounds | eligible only under separate review |
| Unexpected inert alert | Fixture overlay replaces the expected focused scene | `unexpected_context` and stop | Fixture scenario declaration plus reviewed pixels | test-only; never system-alert training truth |
| Context replacement | Fixture mock destination replaces the current scene | `screen_changed` and stop | Fixture scenario declaration plus reviewed pixels | test-only |
| Benign visual motion | Background/carousel/loading decoration changes while focus remains stable | do not falsely report focus transition | Fixture/replay ground truth | test-only unless independently admitted |
| Focus animation/crossfade | Frames are visually unstable during a legitimate move | `wait` or `uncertain`, then a correct final decision | timestamped Fixture/replay truth | test-only |
| Stale/reordered/missing frame | Replay intentionally breaks continuity | `unavailable` or `uncertain`, never approval | manifest fault declaration | test-only |
| Native/pixel disagreement | Native/Fixture focus and visual candidate intentionally disagree | stop with `focus_disagreement` | independently declared expected/actual fields | test-only; do not train labels from disagreement |

The mock classes stand in for broad categories such as sign-in prompts, call/video
takeovers, mirroring overlays, notification banners, and unplanned deep links. They
test the required safe reaction—recognize an unexpected context and stop—without
claiming that a controlled Fixture overlay reproduces each service's exact pixels.

## Comparison arms and attribution

Run every valid sequence through these arms with the same pinned inputs:

1. **Native-only baseline:** fresh TTR/Fixture focus and expected transition. This
   records what native state alone would decide.
2. **Single-frame visual guardrail:** current-frame NUIAK YOLO observations and
   FocusRing scores, compared with native/expected state. This is the first live
   feature candidate; it does not require a prior frame.
3. **Temporal visual guardrail:** arm 2 plus PER-05 frame similarity/change regions
   from before to after. Change regions may rank which detected controls deserve
   attention, but must never become semantic element boxes.
4. **Oracle-geometry diagnostic:** only where same-frame Fixture/native bounds are
   trustworthy, substitute them for YOLO boxes to separate proposal/box errors from
   crop-classifier errors. Oracle geometry is invisible to the non-oracle decisions.

All arms retain the same source image identity. The temporal arm uses current-frame
YOLO or exact same-frame verified native geometry for control crops. A diff rectangle
may include glow, animation, multiple controls or unrelated pixels and is therefore
not a valid crop origin.

## Metrics and adoption decision

Report, by stratum and source kind:

- dangerous false approval: would continue after an unexpected/incorrect outcome;
- false stop: rejects a correct settled expected outcome;
- correct interruption detection and correct expected-transition confirmation;
- abstention/uncertainty rate and reason; stale/invalid input rejection;
- detector proposal coverage, focus-crop score, native/visual disagreement, and
  oracle-geometry delta, so a failure is not blamed on the wrong component;
- per-stage and end-to-end replay latency, frame count and raster reuse/copy count.

Before scoring held-out cases, freeze a written decision rule with the maintainer:
the temporal arm must reduce dangerous false approvals over both baselines without
an unacceptable increase in false stops, unresolved cases, latency or duplicate raster
work. Numeric bounds belong in that frozen rule after the baseline budget is measured,
not invented after results are known. Zero-support strata are unavailable.

## Implementation steps

1. Extend the accepted `transition-sequences-v1` work only additively, or define a
   companion spike manifest, with expected/actual transition fields, image identity,
   candidate-geometry provenance and explicit mock category. Reject an unreviewed
   or prediction-derived truth field.
2. Build a deterministic project-local replay generator for the matrix. Fixture
   controls and overlays must have stable IDs, observed focus and measured bounds.
   Retain all invalid/partial sequences; do not overwrite existing PER-05 fixtures.
3. Implement an offline comparator that invokes the existing PER-05 primitives and
   the actual NUIAK detection/focus entrypoint. Produce bounded structured receipts;
   never emit PNG/base64 to the report or agent channel. Test each comparison arm
   against the same image hashes.
4. Add adversarial tests for diff-as-box misuse, stale/reordered frames, changed
   dimensions, missing model, absent/no/multiple focus, out-of-frame geometry,
   unknown mock type, mid-animation, duplicate raster copy and disagreement handling.
5. Freeze development/validation/test journey groups, artifact hashes, policies and
   adoption rule before held-out scoring. Execute replay, inspect errors by stratum,
   and write the decision report.
6. If the result meets the frozen rule, propose—not execute—a single separately
   authorized simulator confirmation using a fresh frame pair. If not, keep the
   single-frame request and document why temporal integration is not worth adopting.

## Training boundary

This spike does **not** train a temporal model or an interruption classifier. The
best first behavior is policy-based: an unrecognized screen/overlay, disagreement,
staleness or low confidence becomes `uncertain` and stops automation.

Only a repeatable error isolated by the component metrics can justify future training:

- A FocusRing visual-style miss needs separately eligible, genuinely rendered,
  focused/unfocused crop data under the existing FocusRing corpus and gate rules.
- A YOLO proposal miss needs separately eligible element annotations and its own
  detector evaluation; mock change regions cannot become boxes or labels.
- A context/overlay classification proposal needs a separate versioned taxonomy,
  provenance, privacy review, held-out coverage and explicit architecture decision.

Neither controlled mock overlays nor unreviewed account/call/mirroring screenshots
are training data. Real asynchronous system states remain optional future evidence,
not a prerequisite for the safety spike.

## Acceptance evidence

| Criterion | Verification | Expected evidence |
|---|---|---|
| Matrix covers normal, expected, unexpected, unstable and invalid paths | Manifest/rubric review and deterministic replay | per-stratum counts and no silent omissions |
| Diff never supplies semantic crop bounds | Adversarial tests and receipt inspection | geometry provenance is YOLO or same-frame verified native only |
| All three decision arms are comparable | Same frame hashes/model/policy across replay | arm-by-arm report with attribution fields |
| Safety behavior is fail-closed | stale, disagreement, absent-model and unknown-context tests | no incorrect `agreement` on invalid cases |
| Cost is measured | cold/warm and per-stage timing plus raster accounting | latency/frame/copy report, not an estimate |
| Adoption claim is honest | frozen rule and held-out group report | recommend simulator confirmation or decline temporal path |
| Training boundary is preserved | manifest admission tests and review | mocks excluded from training/corpus eligibility |

Expected outcome states after a completed offline spike: software verified may pass;
data eligible is not applicable for test-only mocks; integration qualified and model
gate passed remain not assessed. Handoff lives at
`reports/work/TEMP-LIVE/handoff.md`, with the shared request/readback cited but peer
acknowledgment reported separately.
