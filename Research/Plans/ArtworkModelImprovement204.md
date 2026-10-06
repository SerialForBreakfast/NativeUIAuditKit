# Artwork-backed model improvement — five delivery tranches

October 5, 2026. Tasks.md is the sole state/ownership queue. This is the canonical
execution contract, not evidence of generation, dispatch or model improvement.

## Decision and existing work

Prioritize diverse artwork rendered inside native UI over synthetic imitation of
native focus. FOCUS-RENDER-203 remains a bounded, lower-priority stretch experiment;
its already published request is not cancelled or remotely reprioritized by this
document. Do not interrupt an active peer job. Neither its results nor TTR desktop
availability gates the artwork inventory or independent iOS proposal work.

Reuse GEN-PARITY-199 for the asset planner, IOS-ASSET-200 for the iOS adapter and
RENDER-202 for persistent direct tvOS rendering. Do not create competing importers,
croppers, trainers, queues or capture lifecycle managers. IOS-PROPOSAL-197 remains
independent and high priority: richer art cannot repair a proposal ceiling.

Verified starting evidence: [RENDER-202 intake](../../reports/work/RENDER-202/handoff.md)
accounts for24 generated images,16 review candidates/eight flags and four subject
families. The reported2000-image library is metadata-only here, not admitted data.
Reuse valid existing assets before generating missing coverage. The existing24
and their derivatives remain development-only.

## Common contract and execution boundaries

- Big Dog owns artwork generation and portable scoring under its own assignment.
  NUIAK owns asset admission, native adapters, dataset roles and model acceptance.
  TTR owns producer changes; request exact source/API gaps, not build-only deliveries.
- No installation, weight download, paid service, SSH, Office use or external-repo
  edits. Use approved resident tools. Current standing local simulator/training
  authority applies after exact runtime/data/run preflight; this plan grants no new
  remote execution authority. Publish a bounded peer assignment before expecting work.
- Bulk outputs use verified USB/worker storage with fresh capacity checks and explicit
  budgets. Source, environments and concise evidence stay local. No automatic cleanup.
  Transfers use missing-hash regular-file batches and exact receipts; sender cleans up.
- Keep asset rights/review, native label validity, training admission and model quality
  separate. Artwork supplies content, never control labels or focus ground truth.
- Freeze asset-family/derivative and recipe/scene connected ancestry before capture.
  No connected group crosses train/validation/final evaluation. Development pilot
  assets cannot be recycled into final evaluation. Shared iOS/tvOS artwork is shared
  lineage, not independent cross-platform evidence. Overconnected plans fail before
  capture; do not split connected groups to meet quotas.
- Reserve both unseen-content and unseen-layout diagnostic groups. Report those
  axes separately; unseen content in a known layout is not unseen-app qualification.
  Existing final holdouts remain untouched. Any repeatedly inspected set is development.
- Each tranche hands off one concise report with software, data, integration and model
  outcomes independently, acceptance-to-evidence mapping, hashes, timings and next action.
  Model gates are not assessed in acquisition tranches. Failed candidates are useful
  completed experiments, not promoted models or permission for automatic retraining.

## Tranche 1 — GEN-PARITY-199 + ARTWORK-204: reusable, diverse asset library

**Outcome:** real asset-planner CLI, independently verified inventory and a bounded
coverage campaign ready for native rendering. NUIAK software and Big Dog preparation
can run concurrently without agents editing the same files.

**Inputs:** existing pilot/metadata, [199 contract](GeneratorParity199.md),
[201 model/setup evidence](LocalImageGeneration201.md), installed worker pipeline.
Read inventories first; do not download the reported corpus wholesale.

**Implementation:**
1. Finish199's content-addressed planner and integrate its actual CLI with inventories,
   cache verification, connected ancestry, rights/review filters and missing-hash batches.
2. Freeze a256-slot campaign: four roles × eight subjects × two content compositions
   × four appearance treatments. The earlier three-axis description counted only128;
   both compositions stay in the same role/subject ancestry family, not independent splits.
   Roles: poster, thumbnail, avatar, backdrop. Subjects: drama, comedy, animation,
   sports, news, nature, architecture, abstract. Use role-appropriate fictional motifs
   (e.g. a sports-themed avatar), not forced movie posters for every role.
3. Treatments: dark/sparse, dark/busy, bright/sparse, bright/busy. Record saturation,
   contrast and actual clutter review separately; prompt words do not prove coverage.
   In each role/subject/composition cell, mark one of its four outputs as an explicit distractor
   challenge, rotating border/glow, white panel, circular motif and text-like pattern.
   These64 challenge slots are included in256, not an added budget.
4. Use reviewed existing artwork to fill genuinely matching slots. Generate only gaps,
   at most256 new calls in eight resumable shards of at most32. Freeze slot IDs,
   prompts/seeds/model/settings and reserved asset-family roles first. No automatic
   retries or extra calls to replace rejected outputs; publish unfilled slots.
5. Prompt template: "Original fictional {subject} artwork for a {role}; {appearance};
   {composition}; {challenge if assigned}. Artwork only, no app controls, selection
   state or UI mockup; no required readable typography." Use native text later.
   Inherit one already qualified aspect/resolution per role from201; record actual
   dimensions, model/base revisions, source terms, prompt, seed and hashes.
6. Build cached contact sheets, decode/hash/duplicate audit, per-slot review and
   observed coverage. Near-duplicates are grouped, not claimed independent because
   seeds differ. No automated aesthetic score establishes legal or training clearance.

**Budget:** worker <=4GPU hours/4GiB new outputs, one GPU job at a time without
preempting owned work; no new models. Initial transfer <=128MiB compressed with
<=256MiB expanded contents per batch; inventory first, then selected missing bytes.
Budget exhaustion preserves partial results; generation volume is not acceptance.

**Tests/evidence:**199's real CLI positive/adversarial tests (hash change, collision,
path/link rejection, duplicate IDs, role leakage, unknown schema and pending rights),
focused tests then one offline Swift build/test at integrated code handoff. Campaign
accounts for every slot as reused/generated/rejected/unfilled with evidence, costs
and review effort. No blanket claim that all256 are accepted or independently novel.

**Next:** accepted artwork unlocks native campaigns; gaps become a measured future
request. If worker unavailable, finish planner and existing24 review without blocking199.

## Tranche 2 — IOS-ASSET-200 + RENDER-202: native scenes, one setup per campaign

**Outcome:** reusable native import and bounded matched development captures on each
available platform. Each platform can finish independently; do not wait for both.

**Inputs:** accepted subset from tranche1 (existing pilot sufficient for development),
exact source/build/asset contract, available exact simulator and measured annotation
pipeline. Reconcile TTR source absence recorded in202 before its native arm; iOS does
not inherit that blocker. Preserve original generator behavior without asset options.

**Implementation:** implement hash-bound asset selection, explicit fit/fill/clipping,
native text/controls and raw-to-derived lineage. Reuse200's96-scene matched iOS
proposal and202's24-scene tvOS proposal, not a Cartesian multiplication by256 assets.
Freeze exact recipe/element counts and expected captures before launch. Pair simple,
low-detail and busy content with otherwise fixed layout where the source supports it.
Record missing renderer axes; do not silently simulate unsupported native behavior.
Boot/prepare once, serialize recipe mutations, capture bounded shards of at most48
recipes, validate incrementally and resume only missing planned groups after checking
completion/cleanup. Reuse existing request/settling/recipe timeouts. Preflight an exact
frame/byte estimate against a20GiB campaign cap per platform; stop rather than overflow.

**Verification:** actual entrypoints reject missing/hash-mismatched assets, wrong target,
stale observations, output collisions and partial publication. Prove requested artwork
appears in pixels, and measured labels match native clipping/scale. Test interruption
and resume without duplicate recapture. Keep16%/256px production FocusRing cropping;
do not implement a new cropper. Inspect representative overlays plus every anomaly.
Focused tests and one integrated offline Swift build/test for code changes.

**Acceptance:** all planned cells/targets accounted for, byte/label/lineage checks pass,
healthy postflight, setup/capture/intake timing and accepted scenes/hour recorded.
Unsupported cells remain explicit gaps; partial coverage cannot pass full coverage.
Score fixed current models once on the development campaigns to rank failures.
This is renderer qualification/development diagnosis, not a new final evaluation corpus.

**Next:** freeze new training/validation/reserved groups from the failure analysis for
tranche3, reusing native acquisition. No wholesale admission of pilot images.

## Tranche 3 — TRANSITION-205: content change versus actual focus change

**Outcome:** one measured data-only intervention for the transition model, with
hard-negative improvement and true-transition retention reported together.

**Inputs:** tranche2-qualified renderer and accepted non-evaluation asset families,
current transition reference checkpoint/config and reviewed native scene observations.

**Implementation:** freeze96 new recipe groups across supported layouts/content
families, deterministic64train/16validation/16reserved diagnostic groups; verify
connected ancestry before assignment. For each group capture four labelled contrasts:
focus move/content fixed; focus fixed/content change; both change; neither changes.
Ceiling384 pairs, acquisition shards <=48recipes, <=20GiB raw/derived output. Log
unreachable targets instead of inventing labels. Use observed native focus identities,
not requested moves, feature similarity or model consensus. Keep scroll/overlay changes
out of this first intervention unless separately represented and labelled in its frozen
contract. Benchmark and retain old admitted replay cases to guard forgetting.

Register at most two runs: current-data control and control-plus-qualified-new-data,
same initialization, optimizer, architecture, update budget and preprocessing; reuse a
matching cached control only if all identities/settings match. Freeze numeric updates,
effective batch, storage <=4GiB checkpoints and hashes in ExperimentLog before launch.
These values depend on accepted membership/reference and are a launch prerequisite,
not permission for an unspecified training loop. No simultaneous architecture change.

**Tests/acceptance:** label/role/duplicate checks; real preparation and evaluation CLI;
missing focus telemetry and asymmetric content-change tests; all pair types accounted.
Report changed/no-change errors, confident false changes, abstentions, before/after
localization and joint correctness by source group, plus latency. Preserve existing
model gates. Compare paired group outcomes with uncertainty/support; no invented
percentage gain target or threshold tuning against reserved data. Improvement must
not hide lost true transitions or prior failures. Failed result gets ranked diagnosis.

**Next:** use same qualified raw membership for206 where eligible; frozen evaluation
roles stay unchanged. TTR receives compact case-linked shadow findings, not authority
to drive navigation or an automatically promoted model.

## Tranche 4 — FOCUSRING-206: native focus amid distracting artwork

**Outcome:** one matched FocusRing data comparison targeting artwork recall/false
positives. Reuse tranche3 frames/crops when they actually supply required evidence;
no new capture simply because a different model is being tested.

**Inputs:** qualified native pairs and current FocusRing reference, crop implementation,
six established gates and retained regression membership. Audit coverage across bright
unfocused/dark focused, embedded outline/glow, native style and source family first.
Observed focus callbacks and measured geometry remain label sources. An image with a
drawn border is not automatically a focused positive or a verified negative.

**Implementation:** freeze training-only additions and unchanged evaluation/replay.
Run at most a matched control and treatment with established30epoch MobileNetV4
configuration, identical initialization/update exposure where needed for fair comparison;
record effective sampling/updates and all resolved settings before launch. If data cannot
support that comparison, finish coverage diagnosis rather than lower evidence standards.
Use resident dependencies, <=4GiB model outputs. No architecture or threshold sweep.

**Tests/acceptance:** production crop parity including expansion/clipping, pair integrity,
admission/holdout isolation, complete evaluation accounting and required offline checks.
Report focused recall, unfocused FPR, all six existing gates, unique-focus selection,
per-content/native-style support and latency. Limited coverage means gates unavailable,
not passed. Preserve shipped model; CoreML export/parity and promotion are subsequent
gate-bound decisions, not implied by better PyTorch results. Do not close FR-B/FR-C
or claim physical-device performance using these simulator campaigns.

**Next:** return hard cases to SHADOW-TOPTEN; replenish only demonstrated missing cells.

## Tranche 5 — DETECTOR-207: platform-specific clutter and negative coverage

October6 evidence refinement:200's fixed022benchmark supplies the iOS diagnosis;
reuse its96predictions, do not recapture or reinfer. Grid thumbnail recall falls
80/80→12/80low-detail→3/80busy while hero16/16persists. Check proposal/scale/content
support before choosing data treatment. IMAGE201artwork remains development-only;
CardDetail remains an existing withheld-template family, not new training material.
Any follow-on training uses separately eligible artwork and training-compatible native
families; this diagnostic does not authorize moving its samples into training.

**Outcome:** fixed-model detector benchmark first, then one justified data-only candidate
comparison on the platform with demonstrated benefit potential. iOS and tvOS results
stay separate. IOS-PROPOSAL-197 proceeds independently throughout.

**Inputs:**200/202 labelled native scenes, frozen category maps, existing detector
references/evaluation and proposal-support findings. No generated artwork boxes as UI
truth, no fabricated42nd class and no automatic macOS work before DS-G8.

**Implementation:** score cached/qualified simple-versus-busy development scenes using
production preprocessing. Separate missing proposal, confidence, box fit and artwork
false positives; report per-class and object-size support. Keep small controls legible
at actual model input resolution. Select one error mechanism that native additions
can address, not another run to overcome an unchanged proposal ceiling.
Freeze a bounded follow-on campaign only if required: <=96new recipes/20GiB, explicit
training/reserved asset/layout groups and source-supported controls. Preserve enclosing
and child annotations. Run at most one matched control/treatment pair after registering
exact membership, initialization, epochs/updates, replay and <=8GiB checkpoint budget.
If197 or benchmark evidence shows architecture/proposals rather than data is limiting,
handoff that diagnosis and do not launch this data comparison.

**Acceptance:** genuine labels, native/asset ancestry, all-class retention, operating
TP/FP, AP50/AP50:95 and end-to-end latency per platform. Apply current platform gates;
unsupported classes remain unavailable and artwork counts do not establish DS-G8.
No aggregate cross-platform score hides regressions. Report evaluated candidates even
when rejected, without automatic retraining, model replacement or invented gains.

## Delivery ordering and efficiency

Start199 locally and204 worker preparation in parallel; remote generation begins only
after its bounded assignment is published/accepted under worker rules. Start200/202
with an accepted small subset rather than wait for the whole256-slot campaign. Finish
their software independently of live runtime blockers. Group native collection for205
and206 so shared eligible frames are decoded/cropped once. Keep207 diagnostic scoring
available alongside focus training, but avoid contending for the same GPU/runtime.

Record accepted assets/hour, accepted native scenes/hour, cold setup versus warm work,
intake/review time, bytes reused/transferred and operator interventions. Cache by data,
model and preprocessing hashes. Do not repeat invariant whole-corpus scans after every
helper change. Test changed mechanisms during iteration, one required integrated build/
test pass, and full integrity at freeze. One handoff per tranche, not per internal step.

Execution checkpoint:199planner and actual201inventory integration are complete for
review;204bounded artwork-first assignment is published/read back. Peer acknowledgment
of204 remains pending; active203CPU work is preserved. No native frames or model runs
were launched in this tranche. [Handoff](../../reports/work/ARTWORK-204/handoff.md).
No automatic monitoring is established; Tasks.md remains the execution queue.
