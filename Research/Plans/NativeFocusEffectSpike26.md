# NATIVE-FOCUS-EFFECT-SPIKE-26

Requested October2,2026. Question: can the combined native focus appearance—growth,
shading/highlights and shadow where actually rendered—teach a model to distinguish
focus independently of artwork brightness? One integrated spike, not a new open-ended
corpus program. Existing reviewed data and offline implementation are ready work;
new capture/admission/model execution retain their applicable explicit scope.

## Maintainer clarification — scale and review

### Execution design — October 2, 16:25 UTC

The updated retained pair EBFD748D now passes capture, measured-body validation,
app-owned export and hash-verified USB receipt (24 files,17,345,810 bytes).
Legacy artwork-layout availability is not the additive rendered-body availability.
Use the measured `rendered_body_geometry` contract for native growth.

Generate ten fixed configuration groups,125 pairs each: eight horizontal native
home-icon layouts for training (1,000), two vertical layouts for evaluation (250).
Keep every variant of a configuration in its assigned split; horizontal/vertical
structure is separated. Procedural artwork seeds are disjoint, with city/orbit/
collage for training and checkerboard for evaluation. Vary background luminance,
target position and control aspect ratio. This is a deliberately shifted synthetic
evaluation sharing one renderer, not independent real-app or OS generalization.
Producer calibration labels remain intact; the separately frozen consumer membership
records the maintainer-authorized experiment roles. Qualification pairs are excluded.

Run serial bounded chunks, preserve campaign IDs and per-stage timings, verify each
received file and the existing harvest/observed-focus/rendered-body contracts.
Stop a failing chunk rather than replay uncertain actions. TTR's internal staging
requires a verified-transfer cleanup decision before capacity is exhausted; USB
capacity alone does not solve producer staging. Preserve a10GiB internal reserve.

Measured storage update after175pairs: internal free space is19.58GiB; verified
exports average about11MiB/pair, below the original15.6MB estimate. Preserve the
original plan and use `plan-storage-v2.json` for unstarted chunks8–49, changing only
the internal floor to5GiB plus1GiB consumer pre-dispatch headroom. Membership, recipes,
splits, per-chunk capture/time/byte caps and the active chunk remain identical.
This fits the projected remaining staging without deleting originals; stop if the
measured floor is reached. USB remains the corpus/crop/cache destination.

Compare production per-body16% crops with a fixed before-body window extending20%
on each side for BOTH images. Both use the production Swift crop mechanism;
the latter is explicitly experimental and keeps native enlargement in the pixels.
No focused bounds or labels enter the common-window placement. Guard clipping and
neighbor overlap and retain them as measurable exclusions. Encoding/training config,
resident initialization and run IDs must be pinned before model execution.
Final intake checks expanded context for BOTH input arms. The comparison changes
scale and surrounding context together; it cannot attribute gains solely to growth,
shadow or shading without a separate intervention experiment.
Primary scoring uses only each nominated target, once unfocused and once focused.
Bright distractors appear in the full scenes but are excluded from these crops;
target-pair accuracy therefore does not establish whole-screen selection or accuracy
on those distractors. The common window uses an observed **unfocused** reference
box; arbitrary before-frames where that control is already focused are not qualified
inputs. Retained real-screen scoring applies only to the standard-crop candidate.

First25pair crop qualification found17/50frames with a neighboring body inside the
initial35%context window. Preserve those diagnostic crops; tighten the common window
to20%before encoding, and recheck every frame for neighbour overlap and clipping.
This changes preprocessing only, not captured pixels, annotations or split roles.

Model execution design: two matched Native26-only comparisons reuse the resident
ImageNet MobileNetV3-small prefix and existing partial-tail/MLP implementation.
Encode both crop arms in batches of32, max300seconds per arm and1GiB combined
feature-cache limit. Train each fresh, identically seeded head/tail for at most
1,000 minibatch updates/300seconds on MPS; use a fixed final checkpoint rather than
selecting against the250pair evaluation. Record unequal achieved update counts as
a comparison limitation. Total model execution remains bounded by1,800seconds and
2GiB new cache/checkpoint/results. Crop preparation and approved capture are separately
timed. Evaluation reports both0.5and fixed0.85thresholds, focused misses, unfocused
false calls and both-correct pairs; no claim of improvement on the retained333real
controls without an actual compatible replay. This isolates input representation;
same renderer and small number of structural families still limit generalization.
Replay the pinned FDR021 head on the same500normalized synthetic evaluation crops
as a frozen baseline, using its resident pretrained tail and matching normalization.
This is not a new training run or a substitute for the unchanged real-app benchmark.
After fixed final training, measure training-set fit for diagnosis. Also replay the
normalized-input candidate and FDR021 on the resident, hash-verified315development
plus18retention feature inputs, using the existing representative scorer. This is
evaluation-only under the same1,800second envelope and changes no membership or
selection thresholds. Verify identical prefix/normalization and retained crop hashes
first. The common-window arm has no matching reference boxes for those static real
frames, so its real-app transfer remains unavailable rather than substituting the
wrong input representation.
Record USB image read/decode, accelerator execution and feature-cache write/hash
times separately, with explicit accelerator synchronization. Preserve the encoder
identity, package versions and final training state so both arms can be replayed.
Prepare a deterministic random review queue independently of model failures; keep
failure-selected examples in a separate queue. Report uncertainty by configuration
group rather than treating sibling renders as independent real-app evidence.

### Execution checkpoint — October 2, 15:45 UTC

Maintainer assigned execution and approved Simulator/external storage. Exact booted
target: `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`, tvOS26.5. Normal Simulator and TTR-owned
runtime staging are used; final corpus destination is the approved USB subfolder.

New structural home-icon campaign passed planning and consumer recipe-hash validation
but failed at case validation (`commandRejected`, no accepted pairs). A discriminating
previously qualified canvas-v2 native-image recipe captured one pair in6.149s with
zero rejected pairs. Its current Fixture telemetry explicitly reports
`presentation_bounds_status=unavailable_native_effect_not_measured`, source
`artwork_layout_view_bounds`; focused and unfocused cards both report640×400 layout
rectangles. This is not the repaired measured-body annotation contract and is not
eligible for the requested training corpus. Do not scale this fallback into training.

Direct campaign export fails `persistenceFailed` for both project and USB destinations.
TTR-owned exports succeed, but bounded consumer reads of the supported diagnostic
path do not return and were interrupted. The exact access-layer cause is unresolved;
do not label this a USB filesystem failure. The configured TTR checkout remains
46dce7b and lacks current campaign/Fixture source; local corrected Fixture binary was
not found beside the running build. Request published source revision/commit/push,
then build/install locally. No producer build request.

Postflight: Simulator ready and persisted ownership clear; Fixture settled. No
training launched. Full accepted evidence and resume conditions:
[execution handoff](../../reports/work/NATIVE-FOCUS-EFFECT-SPIKE-26/handoff.md).

### Local USB storage authorization — October2

Maintainer explicitly authorizes large corpus/scratch outputs for this spike under
`/Volumes/training-drive/data/NUIAK`, including a new experiment subfolder. Read-only
inspection found that exact mounted volume and existing NUIAK directory, about1.8TiB
available. This is a new local USB exception, not revival of cancelled SMB/SSH storage
work. Verify the mount before every output session; never create an unmounted local
lookalike. Keep source, environments and compact manifests/status in the repository.
Sandbox permission and importer path compatibility must be satisfied before writing;
capacity alone is not a transfer/write qualification. Preserve originals and measure
USB read/write time separately from generation and feature encoding. If I/O becomes
material, propose bounded cache/staging changes based on measurements. Cleanup of
unrelated logs/build artifacts is a separate scoped decision, not automatic authority.

High priority. Repeated successful human review of the repaired synthetic annotation
path is sufficient to proceed with this spike without another mandatory manual pilot.
Confirmed target1,000training plus250evaluation pairs (2,500screenshots); measure throughput during the
batch. Keep automated integrity/geometry/focus checks and surface exceptions. Start
with supported genuine native-effect controls; arbitrary custom shapes do not inherit
native rendering qualification. Use generated or appropriately licensed artwork.

Optionally retain nested250-versus1,000pair training comparisons with fixed evaluation and
source-group separation, subject to the exact encoding/training execution envelope.
This replaces repeated human pilot approval below, not actual target/runtime discovery
or machine-verifiable membership checks. Review history supports this operational
choice but does not establish a numerical annotation-error rate. Sparse random label
noise and systematic geometry/focus errors must be reported separately; do not silently
admit known invalid records under an assumed error tolerance.

### Spot checks and failure-driven review

Maintainer clarification: preserve occasional human spot checks without making every
batch wait for another review. Keep two separate small queues: a seeded random sample
across generation conditions, and targeted exceptions from geometry checks, optional
Vision/shape/OCR disagreement, missing native focus evidence and model errors. Record
each selection reason. Detector disagreement is advisory, not proof of a bad label;
do not automatically replace native annotations with detector predictions or invent
calibrated confidence. A targeted sample cannot estimate the overall defect rate.

If the spike fails its measured objective, stop scale-up and diagnose before rerunning:
separate generation/annotation errors, lost growth/context in preprocessing, membership
or evaluation mistakes, insufficient diversity and learning/model limitations. Retain
originals and failed results; render before/after/crop examples for the dominant failure
groups. Request one focused review only where human judgment resolves uncertainty.
A subsequent run must name the diagnosed cause, changed variable and expected measurable
effect, within the assigned execution envelope; no unchanged automatic retries.

## Design before execution

1. Inspect the current qualified generator and retained native-effect examples.
   Record which controls use native rendering versus custom focus styles. Do not
   call procedural growth a native-effect sample. Confirm effect support per control.
2. Prepare a small factorial pilot varying artwork brightness/texture, background
   brightness and target position, with bright unfocused distractors. Within a pair,
   retain artwork/layout and change only focus after settling; record observed focus,
   per-frame measured visible body bounds, clipping and capture correlation.
3. Keep body annotations separate from shadow extent. Preserve original frames and
   context; compare the existing independently resized control crops against a
   before-anchored/common-scale paired representation that preserves enlargement.
   Shadow/context inputs must be checked for neighboring-control contamination.
4. Apply automated geometry/integrity checks throughout generation and surface exceptions
   for review. Quantify eligible pairs, failure reasons, time per pair and storage.
   Generate toward the1,250pair target using supported native controls; measure rather
   than assume throughput. Additional manual pilot approval is waived for this spike.
5. Before training, freeze exact eligible membership, initialization, preprocessing,
   metrics and budgets. Compare baseline versus native-effect additions with the same
   architecture where possible; isolate any representation change in its own comparison.
   Apply the assigned local experiment envelope rather than repeated launch approvals.
   A paired model and a single-image model solve different tasks; report them separately.
6. Group entire related layout/recipe families before splitting. Preserve current
   evaluation/retention membership. Use only an already reserved independent real-app
   set for independent claims; otherwise report development results and reserve fresh
   evaluation separately. Never convert repeatedly inspected examples into a new test.

## Success and deliverable

### Measured timing and execution shape — October2

Maintainer requests an actual performance baseline for future parallelism decisions.
Record host/chip/memory, OS/Simulator and producer/consumer versions, image dimensions,
settling configuration, batch size and worker count. Measure wall time separately for
setup, recipe/render/focus settling, capture/PNG encoding, export/transfer, validation,
production crops, feature encoding, training and evaluation where instrumentation is
available. Unknown stage times remain unknown, not inferred from total case duration.
Record successful and failed attempts, retries, bytes, accepted pairs/second, stage
median/p95, total elapsed time and observed peak memory/disk where measurable. Preserve
monotonic same-host timing; cross-host timestamps are not interchangeable clocks.
Later parallel runs must use matched workload/settings and report aggregate throughput,
per-pair latency, errors and resource use, rather than assuming worker-count speedup.

Split confirmed by maintainer:1,000training pairs plus250new source-group-separated evaluation
pairs means1,250pairs/2,500screenshots, about2.59hours of projected case execution and
19.5GB source files before overhead. Freeze new evaluation membership before tuning;
existing real-app/retention results remain a separate transfer check. This clarification
does not silently authorize changing existing splits or counting sibling variants as
independent evaluation.

Read retained structural DATA64 appearance campaign receipts (completed, one accepted
pair per case). Across48cases mean7.306seconds/case. The12native `home_icon` cases
have median6.758seconds, mean7.449seconds, range6.064–14.269seconds. Extrapolation:
1,000pairs≈2.07hours of case execution, excluding setup, batch/export overhead,
retries, intake, encoding and training. These are producer receipt durations, not
a measured Maximum-mini1,000pair run. Native-case retained files average15.61MB,
so1,000pairs project≈15.6GB before downstream outputs. Check disk reserve and avoid
duplicate large staging copies; storage and batch budgets must be explicit.

Existing Fixture source exposes configurable focus settling with minimum150ms.
The retained campaign uses bounded budgets (example24cases/600seconds/1GiB), not
proof that a single1,000case request is supported. Use supported chunking/resume.
Optional throttle tuning is not a prerequisite if existing settling yields verified
stable captures. Do not equate a requested wait with observed readiness.

Keep accessibility appearance settings fixed at the baseline for this native-effect
experiment; do not enable VoiceOver, Hover Text, Reduce Motion or enhanced contrast
as a training aid. Native telemetry provides labels without changing accessibility
rendering. Later accessibility variants are separately identified experiments.

Multi-Simulator generation is unqualified. The inspected local diagnostic runner
explicitly disables parallel testing and selects one Simulator destination; this
does not prove every campaign path has the same limit. Before proposing concurrency,
verify per-target coordinator ownership, distinct Fixture endpoints/output roots,
resource capacity and supported scheduling. Start the estimate from a single worker;
do not promise linear scaling or make parallelism a prerequisite for this spike.

Produce a runnable pilot/benchmark path, measured scale-up estimate, visual paired
examples and a concise result/recommendation. Report dark-focused misses, bright-
unfocused false positives, per-family support, abstentions where applicable, frame
selection errors, unchanged retention, training time and input geometry behavior.
Recommend scale, revise representation or reject based on matched evidence. A larger
corpus or lower training loss alone is not success. Do not promise broad generalization
from one renderer or silently promote/export a candidate.

Resume dependencies: genuine renderer/target scope for new captures; exact machine-
verified data membership before new training data; explicit encoding
and training configuration inside the approved execution envelope. These dependencies
do not block retained-data audit, input-design tests or the throughput harness.
