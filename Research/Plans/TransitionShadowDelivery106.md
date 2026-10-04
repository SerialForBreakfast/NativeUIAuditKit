# TRANSITION-SHADOW-106 — DTM025 change-only consumer delivery

## SHADOW121 — retained feedback is a diagnostic input, not accuracy

TTR's survey24 report says DTM025/030 agree with4/8and5/8native hints; survey26
says6/6and3/6among available hints, plus2unknown. Before fitting more, preserve
both reports, verify internal binding/accounting and request exact original frames,
raw requests/replies, hint observations and separately reviewed focus identity.
Extend the existing feedback CLI with a read-only bounded YAML producer-report
mode. It must not convert producer summaries to verified accuracy, training labels
or execution attestation. Source survey hashes must match across model comparisons;
model/tree/contract identities must match delivered artifacts. Unknown formats fail
closed. Missing case-level truth/probabilities remain missing. Actual receipt matches
authorize cleanup only of the exactv1shared duplicate, never consumer-v2 or originals.

## SHADOW120 — preprocessing throughput with exact compatibility

SHADOW118 measured median preprocessing181ms versus inference0.504ms. Optimize
the existing Swift consumer rather than changing model architecture for this cost.
Request-owned LRU retains at most8encoded RGB frames (8×3×192×128×4bytes=2359296
payload bytes). Each access still validates current path, size and SHA256; cache
hits skip only decoding/resizing, never byte integrity. Cache no failures, raw PNGs
or full-resolution RGB arrays. End request discards state; absent/off reads nothing.
Keep identical integer coefficients, horizontal rounding before vertical rounding,
letterbox and float conversion. Reuse existing438pair parity entrypoint and native
contract suite. Compare against immutable118portable binary on identical order;
report cold versus reused paths and latency, not just theoretical operation counts.
Prove eviction, changed bytes/path rejection and exact preprocessing on all retained
and synthetic pairs. If no material speed benefit, retain diagnosis, not an assumed
optimization. No model export/recompile or source/model identity substitution.

Measured October4: unchanged438pair replay86.159→53.436seconds; median
preprocessing183.869→120.219ms. Cold subset206.251→174.775ms; mixed reuse
180.696→119.298ms. Exact tensor/decision parity438/438 on both consumers.
Consecutive local CPU runs, potentially warm filesystem—not a universal benchmark.
See SHADOW120handoff for portable consumer-v2 receipt; original118delivery retained.

October4 SHADOW118 execution approval: maintainer explicitly approved DTM030
experimental CoreML export, CPU parity and isolated shadow delivery. Feedback
normalization binds each supported model ID to its independently measured compiled
tree; it must reject mixed DTM025/DTM030 artifact identities. No production approval
is inferred from this compatibility delivery.

Maintainer goal: build this for TTR to consume; export and delivery explicitly approved.
No training, recapture, device operation, public library API or production promotion.
NUIAK owns package, standalone Swift source adapter/CLI and parity evidence. TTR owns
its app hook; no edits to TVTestRig repository. Deliver through verified SMB receipt flow.

## Contract and implementation

- Pin DTM025 checkpoint SHA256
  `28f10dc5ac2c6a0fb324cabeb778b2acad2539c97f7f9cc48a20c8ff534a9409`.
  Export only its change branch, not unqualified geometry/ranker outputs.
- Input ordered full before/after RGB frames. Training encoder: preserve aspect,
  black letterbox192x128, nearest-even rounded resized dimensions, Pillow bilinear
  antialiased8bit resampling, planar beforeRGB/afterRGB float32 divided by255.
  Model internally forms abs(after-before),before,after in that order.
- Extend existing export entrypoint with an explicit transition task; use trace,
  isolated FP32 Core ML package initially, CPU-only runtime, no model download.
  Conversion, compilation and actual prediction must pass separately.
- Versioned adapter validates PNG bytes/hash/dimensions/format, model/source contract,
  finite output and exact input shape. Carry pair/action/observation IDs; inference
  inputs exclude labels, candidate boxes and requested focus. Return probability,
  changed at>=0.85, unchanged at<=0.15, otherwise uncertain. Not calibrated confidence.
- Standalone Swift consumer source plus bounded batch CLI; off loads no model and
  emits no predictions. Reuse one loaded model per batch, at most128pairs,20million
  pixels per image,32MiB PNG, matching before/after dimensions; no device commands.
  Strict unknown/duplicate-field, path/hash and output-collision handling. No retries.
- Swift preprocessing parity must be measured against the actual Python encoder,
  not assumed from CoreGraphics interpolation. Unsupported pixel formats fail
  explicitly; never silently change color/alpha/orientation semantics.

## Verification and acceptance

Compare PyTorch/trace/Core ML on all113retained real pairs and122approved identity
negatives, preserving roles. Require abs probability error<=1e-4 and identical
threshold decisions. Validate Swift preprocessing on every187unique source frame,
plus deterministic color/orientation/letterbox examples. Exact encoded tensor bytes
preferred; any mismatch blocks delivery until explained and bounded parity accepted.
Record cold load, warm inference/preprocessing timing and artifact size; no universal
latency/accuracy claims. This is compatibility, not independent model qualification.
Test off, corrupt/missing PNG, wrong hashes, dimensions, unsupported contract/backend,
tampered model, malformed/duplicate IDs, nonfinite probabilities and output collisions.
Run focused tests plus one integrated offline Swift build/test. Preserve failed attempts.

Package only model/adapter/CLI source, metadata, instructions and synthetic test
vectors; no private captures or raw weights. Manifest exact bytes/hashes; verify
archive and clean extraction; publish NUA-owned immutable artifact and request TTR
receipt, source integration and on/off proof. Source paths must be portable.
Readback is delivery, not peer acknowledgment or live TTR qualification. Keep goal
active if required consumer execution evidence is unavailable, while completing
all NUIAK-owned work. Shared statuses remain cross-project consequences only.

## Accepted NUIAK delivery — October3local/4UTC

Implemented and verified:240pair exact encoding/decision parity, max score error
2.868e-7;24real CLI and12export Python tests;137offline Swift tests. Independently
extracted portable source builds and scores the synthetic sample.198,134byte archive
and detailed follow-up request published/read back on verified SMB, preserving
unrelated status. This supplies actual local consumer execution evidence, not
merely a compiled package. [Handoff](../../reports/work/TRANSITION-SHADOW-106/handoff.md)
and [publication](../../reports/work/TRANSITION-SHADOW-106/coordination.md).
TTR owns acknowledgment, copied receipt and live source-hook validation; these remain
open queue items, not implied by delivery. No production/model-quality gate passed.

## SHADOW-CONTRACT110 — optional integration and transition semantics

October4 maintainer continuation: keep TTR supplied with independently testable
contracts while its modules remain optional. Scope: reconcile exact copied receipt;
clarify trained target using collector source; implement a small portable feedback
evaluation/conformance utility and synthetic cases; verify real CLI off, failure
and scored states; publish a metadata addendum and source/test artifacts. No TTR
edits, capture, new training, model re-export or private-image publication.

Training target is focus-owner identity change inferred from ordered pixels,
not highlight-box displacement or any visual difference. Native collector compares
observed focus IDs; reviewed Settings compares matched control identities. Stationary
highlight plus scrolling can still mean changed focus; same identity with animated
content means unchanged. Keep identity, geometry and content relations separate.
Pixels may not contain enough evidence to identify a semantic transition; no reliable
support for stationary-highlight scrolling is established by DTM025. Do not relabel
peer disagreements as successful unchanged detections to avoid this gap.

Consumer evaluation must keep model predictions immutable; join independently
reviewed labels afterward using exact action/observation/image identities. Native
identity hints produce disagreement diagnostics, not verified visual accuracy.
Missing/unknown labels, dropped/skipped/unavailable/failed inference have no accuracy
denominator. Abstention is reported separately from raw scored decisions; scores
are not calibrated confidence. No truth fields enter inference requests.

Deliver test-only normalized cases, not a new TTR export schema. Optional-module
acceptance requires feature-absent and off builds with no model/pixel access, lazy
loads when enabled, independent FDR021/DTM025 capability, bounded queue8, typed
drop/failure/cancellation/stale-result accounting and identical navigation decisions.
Self-reported test records are not attestation of TTR execution. TTR maps its own
four-record exports to the contract and attaches real source/build/test evidence.

Acceptance: focused deterministic tests and actual existing CLI cases, integrated
offline Swift build/test, verified exact receipt and scoped SMB publication/readback.
No claim of live-hook or eight-pair accuracy without received byte-bound evidence.
Next: TTR source publication and allowed tiny export; NUIAK local source build,
case-bound intake, then reviewed independent dataset proposal. Geometry correction
and shadow integration remain independent; one does not block the other.

Delivery October4: [SHADOW110 handoff](../../reports/work/SHADOW-CONTRACT-110/handoff.md)
maps each criterion to evidence. Exact DTM025 receiver receipt is now accepted,
superseding the earlier pending-receipt note. Conformance addendum/archive published
and read back; TTR acknowledgment of this new artifact is not yet established.

## SHADOW-REGION111 — retained Settings feedback intake

Authorized support continuation selects the named Region12 v2 diagnostic archive
now actually present on verified SMB:532823401bytes, SHA256
dbc1439b529e7647437b1f6914af7a4fa6f0f8fa62e1315634b0aed49ce80e8d.
Reuse bounded receipt/extraction; verify107 producer-listed members, image integrity,
action/prediction associations and annotation versus model evidence separation.
Keep project-local intake artifacts ignored. Copy original to verified local USB
`data/NUIAK/archive/tvtestrig/tvtestrig-20261004-settings-region12/<sha>/<filename>`,
verify bytes and retrieve a small member to fresh project-local output. Preserve
originals and all rejected evidence. Publish exact receipt; sender alone owns
shared-copy cleanup. No training admission, screenshot re-publication or model
promotion. Any reviewable disagreement remains development-only with whole Settings
ancestry excluded from independent final evaluation. Source/model/geometry gaps
must be reported, not filled from prediction or filename assumptions.

October4 admission/evaluation/promotion autonomy amendment: independently make
evidence-backed data-role decisions; preserve required qualification gates. For
Region111, first replay shipped experimental DTM025 on all94 retained intervals
using original pixels and the existing CLI. Native identity hints remain a separate
diagnostic comparison until reviewed; no final-evaluation claim. Pin the delivered
model, thresholds and encoding; no tuning or training in this intake comparison.

## REGION-REVIEW112 — complete visual review and one change-head comparison

The following tranche reviews95 selected labels, admits exact94ordered transitions
for change-only supervised training and95identical-frame derived negatives using
the maintainer's autonomous admission authority. [Decision](../../reports/work/REGION-REVIEW-112/admission.md)
defines fixed600epoch DTM025 warm-start hypothesis,202original/217derived membership,
unchanged encoding/optimizer, strict retention gates and no production inference.
Reuse the existing `fit_change_head`, not a second trainer. Freeze all non-change
weights; pin input/source/review/checkpoint hashes and log before launch. Persist
failed result rather than automatically retraining. Review and fitting never make
Settings ancestry independent final evaluation. New real no-op and independent
journey evidence remain required even if this comparison fits perfectly.

## REGION-SIGNAL113 — diagnosis before another fit

Pin DTM025/028 and Region112ready02 tensor/protocol. Compare unchanged forward
predictions against recorded424results before interventions. Evaluate reversed
frame order, difference-only channels and context-only channels on the same424
examples; report prediction changes separately from genuine-data correctness.
For Region94 only, zero difference inside versus outside fixed reviewed focus-strip
screen coordinates mapped through the existing letterbox encoder. This is a
diagnostic mask, not a deployment detector or training box label. Report gradient
sensitivity to the two channel groups; avoid interpreting out-of-distribution
ablations as causal proof or independent generalization. No fitting or threshold
tuning in this diagnostic. Bound batch memory, preserve source bytes and produce
one ranked next-experiment decision with real same-focus motion coverage needs.

## REFLOW117 — explicit exposed-Settings admission and one fit

## SHADOW118 — DTM030 experimental consumer delivery

### COVERAGE119 — complete endpoint and exposure audit

Before consumer qualification, enumerate all original207pairs and unique endpoint
hashes from pinned sources. Score every endpoint paired with itself; compare to
the frozen DTM025base, not merely the226previously constructed negatives. Reverse
all433retained pairs and report categorical/probability stability. Generate a
hash-bound exposure inventory grouping all Fixture-renderer ancestry and all
Settings ancestry as training/exposed; preserve old historical labels/roles.
This is synthetic/metamorphic testing and lineage accounting, not new genuine
evaluation. No weights, data roles or thresholds change. New independent native
evidence remains missing; do not fabricate a reserved cohort from empty membership.

Use existing exporter/portable observer with a second exact modelID/checkpoint
allowlist entry. Preserve DTM025compatibility and fail closed for cross-paired or
unknown identities. Model output remains change-only with fixed0.15/0.85thresholds;
report actual loaded identity. Trace explicit frozen encoder/readout plus residual
pair-minus-self computation; no training helper/cache in the exported graph.
Use resident focus-export-01environment, FP32CPU CoreML, macOS15minimum. Standard
Apple compilation/cache storage is within this approved local export execution;
explicit outputs/caches remain project-local. No installation/download/signing work.
Validate433retained training examples plus5synthetic aspect-ratio cases through
the actual Swift consumer, exact encoding and decisions, probability error≤1e-4.
Record cold load, warm inference and preprocessing separately. Isolated source
package must build/run its synthetic vector independently; no private images, raw
weights or machine paths delivered. Publish archive hash/size and receipt request
under NUA namespace after verified SMB mount; peer receipt and live adoption remain
separate. No promotion based on training-fit or parity.

## REFLOW117 contract

FOCUS116 fixes the reflow negative through local differences but loses13old positive
successes, so reject hard masking. Under autonomous admission authority, move all
five already-exposed legacy Settings pairs together into training and add their
nine unique identical-endpoint derivatives. Preserve immutable old manifests.
These cases already influenced repeated design decisions and share the broader
Settings ancestry with Region training; they are not independent evaluation.
Verify all original image hashes, corpus/admission references and label evidence.
New role record must bind exact five IDs and nine hashes; no new geometry admission.
Use DTM029warm-start, freeze baseline encoder/readout, train only576residual weights
through existing fit_change_head:600epochs,Adam0.01,seed42,CPU2threads,fixed-last,
207original/226derived group means,2GiB outputs,no-wall-time override.
Before run register DTM030. Gate: all207originals confident correct, all226identities
unchanged, no prior confident successes lost, frozen weights and checkpoint replay.
Any pass is training-fit only. Independent new journeys/families remain necessary;
do not export/promote from these numbers. No automatic extra epoch or LR loop.

## FOCUS116 — local difference evidence

Freeze DTM029 and the73legacy pairs with existing box supervision. Transform box
unions into the existing192×128letterbox raster; compare all difference channels,
only differences inside the union, and only differences outside it. Context channels
remain unchanged. Run separately with ground-truth boxes (oracle) and retained
DTM020 selections (image-only proposals); bind proposal/checkpoint identities.
No new cropper: this is a full-frame channel intervention, not FocusRing preprocessing.
Do not infer Region94body boxes or use inconsistent new40geometry. Report missing
scope and both positive/negative outcomes. Invalid/missing boxes fail closed.
Baseline must reproduce retained scores; partition/complement tests must cover
letterboxing and edge clipping. A favorable intervention is evidence for a next
focus-conditioned architecture experiment, not a trained replacement or policy.

## REFLOW115 follow-up audit

The failed row25pair is visibly a value-change/layout-reflow with the same focused
VoiceOver row, not a focus movement. Freeze the current424encoded cases/checkpoints.
Audit exact residual logit decomposition on the4×6pooled feature grid, nearest
training positive/negative feature support, input pixel-difference coverage and
reverse-order categorical consistency. Inspect source images without mutating
Settings. Coarse pooled locations are sensitivity summaries, not box localization
or causal evidence. Preserve all data roles and thresholds; no new trained run
until this explains what current training coverage or representation lacks.
Acceptance: checkpoint/input hashes validated; original predictions reproduced;
summed feature contributions reconstruct correction; every original negative
accounted for; reversal reports no-op/changed/uncertain separately. Test helpers
offline and run integrated repository checks. Send only actionable producer gaps.

## IDENTITY114 — frozen-feature residual

Result: DTM029 completed;92/94Region confident changes, old training retention passes,
217identical predictions exact, but one related Settings negative becomes confidently
wrong. Gate failed. See reports/work/IDENTITY-RESIDUAL-114/handoff.md. No export or
consumer replacement; next diagnostic must distinguish real motion from identity change.

Run one new representation/readout comparison under standing model authority:
DTM025's frozen pooled576features and frozen classifier plus a bias-free linear
correction to centered pair-minus-self features. Zero-initialize correction. Reuse
existing full-frame192×128encoder and `fit_change_head`; feature construction happens
once per fit, not per epoch. Only576new weights train, preserving all baseline weights.
Keep202original/217derived training membership,5related Settings diagnostics and
all424evaluation inputs from REGION112. No new image labels or inference truth.
600epochs,Adam0.01,seed42,CPU2threads,fixed-last,2GiBoutputcap,no-wall-time override.
The learning rate applies to a new zero linear projection, not baseline weights.
Advance only if all94Region changes are confident, no previous confident success
is lost, all217identical checks retain exact baseline probabilities, frozen weights
and saved checkpoint replay pass. Report size/latency/feature cost; do not call a
training-fit pass production qualification. Preserve rejected output; no sweep,
threshold tuning, capture, export or promotion in this experiment.
