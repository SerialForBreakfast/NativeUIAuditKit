# NativeUIAuditKit product roadmap

Repository snapshot: 2026-10-09. Owner: Maximum-mini-NUIAK.

NUIAK detects visible UI elements and focus evidence from screenshots.
The next MVP gives TTR optional models, verified installation, and useful diagnostic results without control of navigation.
Later milestones improve model accuracy, complete the feedback cycle, and expand supported UI types and platforms.

This roadmap groups the existing plans into product milestones. It does not authorize new execution or change acceptance gates.
[Tasks.md](../Tasks.md) remains the only queue for status, priority, and ownership.
[CurrentState.md](CurrentState.md) records results. [ImplementationPlans.md](ImplementationPlans.md) links the detailed work contracts.
Historical experiment entries do not become new work merely because they remain in those files.

## Roadmap at a glance

| Stage | User outcome | Current position | Completion condition |
| --- | --- | --- | --- |
| Existing baseline | Inspect screenshots with local detectors and OCR | Shipped capabilities and research tools exist | Preserve compatible behavior and report model limits |
| MVP A | TTR can optionally get, load, and inspect a verified model | Local package and archive tests pass; public and TTR checks remain | Complete the real download and host test cycle |
| MVP B | TTR can return useful model failures with user consent | Contracts exist; complete live feedback cycle remains open | Review 1 case batch and measure 1 targeted correction |
| Model milestone | Focus and transition models improve without losing previous successes | Current candidates still fail important tests | Pass independent tests and existing model gates |
| Broader detection | Better iOS and tvOS controls, boxes, and screen coverage | Active research; coverage and quality remain incomplete | Pass each platform's separate gates |
| Platform expansion | Additional classes, macOS, and audit consumers | Planned with prerequisites | Meet each feature's stated entry and exit conditions |
| Proposed features | New methods that might resolve measured failures | Not product commitments | A bounded experiment proves useful benefit |

These stages can overlap. Model research does not wait for public model hosting.
The MVP names here describe NUIAK deliverables. They do not rename the coordinator's MVP1 or TTR 0.4.3 RC.
No calendar dates are promised. Required evidence, worker capacity, and accepted scope determine release dates.

## 1 Existing capabilities

| Capability | What exists | Important limit |
| --- | --- | --- |
| iOS element detection | Shipped 5-class detector | The 41-class replacement has not passed DS-G8 |
| tvOS element detection | Shipped detector with 25 active classes | Synthetic benchmark scores do not prove arbitrary real-app accuracy |
| Single-image focus | Shipped FocusRing v0.1 crop classifier | Required hard-negative coverage remains incomplete |
| Text and UI evidence | OCR association, coordinates, and observation reports | Pixels cannot prove hidden accessibility semantics |
| Local tools | Swift inference, screenshot CLI, and stdio MCP interface | Tool execution does not establish model quality |
| Training and evaluation | Seeded generation, intake checks, experiments, and retained comparisons | Each dataset still needs correct labels and approved roles |
| Worker processing | BigDog-NUIAK can run assigned batch computation | Portable inputs and accepted execution scope remain necessary |
| Optional model delivery | Resource-free runtime and local lifecycle tests | Public download and signed TTR execution need end-to-end checks |

The focus tasks remain separate:

- **UI detector:** find elements and their boxes.
- **FocusRing:** estimate focus from 1 element crop.
- **Focus Transition Model:** compare frames to estimate whether focus changes and where.
- **Settling check:** estimate whether a frame sequence is ready for the next observation.

Success on 1 task does not prove success on the others.

## 2 MVP A Optional models in TTR

**Outcome:** TTR uses NUIAK for optional screenshot analysis without bundling every model or changing navigation policy.

### Included features

- Resource-free Swift package product with an explicit model provider.
- Existing bundled products retain their documented behavior.
- Versioned catalog with exact model identity, hashes, task, preprocessing, and host limits.
- Explicit download or local import. No automatic download during build or startup.
- Bounded archive validation before extraction and compilation.
- Verified installation, explicit selection, offline reload, and rollback.
- Typed failures for missing models, corrupt files, incompatible hosts, and failed compilation.
- Protection for active models during replacement or removal.
- Source access, attribution, model terms, and reproducible release inventory.
- Observer results that record the actual loaded model and preprocessing.

### First delivery

REVIEW306 prepares the tvOS element detector and its source archives for public preview.
It does not include downloadable FocusRing, transition, or iOS model releases.
The sanitized checkpoint preserves all 503 tensor storage files.
The final archive matches 25 retained detections. That is integration evidence, not a new accuracy result.

Do not publish the older REVIEW304 or REVIEW305 model ZIPs. Their embedded data contains a personal identifier.
Use the [publication instructions](ModelPublicationReview305.md).

### Remaining work and acceptance

| Work | Owner | Acceptance |
| --- | --- | --- |
| Publish the reviewed preview | Maintainer; Maximum-mini-NUIAK prepares evidence | Exact approved inventory, source access, notices, and separate release identity |
| Verify public downloads | Maximum-mini-NUIAK | Anonymous downloads match catalog and member hashes |
| Test actual TTR integration | Sillycon-TTR; Maximum-mini-NUIAK reviews results | Download, compile, load, restart offline, rollback, and failure tests pass |
| Report host support | Each executing host reports results | Distinguish declared macOS 14 minimum from tested OS and architecture |
| Reconcile communication | BigDog-Coordinator routes; receiving owner acknowledges | Forwarded ID and TTR response exist; stored messages alone do not count |

The local tests cover macOS 27.0.1 arm64. They do not qualify macOS 14 or Intel execution.
TTR reviews its application distribution separately. That review does not create a circular dependency for NUIAK's own preparation.

**Exit:** an actual TTR host consumes the exact preview and returns independently checked results.
**Excluded:** model-driven navigation, automatic promotion, and claims of production focus accuracy.
Contracts: RELEASE300, MODEL-DISTRIBUTION293, and [optional model distribution](Plans/OptionalModelDistribution.md).

## 3 MVP B Useful feedback from TTR

**Outcome:** TTR helps identify real model failures without making predictions into training labels.

### Included features

- Explicit off, local review, and approved transfer modes.
- Bounded storage, queues, sampling, and session limits.
- Case records with image identity, model identity, settings, observed outcomes, and selection reasons.
- Privacy review and consent checks before transfer.
- Compact success summaries with a separate audit sample.
- Representative images for selected failures when transfer is approved.
- Human or native evidence for labels. Model agreement is not proof of correctness.
- Up to 10 supported failure categories, with counts and reproducible case IDs.
- Cached scoring and exact receipts to avoid repeated transfers and inference.
- A targeted capture proposal tied to each selected failure.

### Completion cycle

1. Measure the current model on a reviewed failure.
2. Generate only the missing examples with local TTR or the qualified direct generator.
3. Validate labels, related groups, and dataset roles.
4. Train 1 bounded candidate with fixed settings.
5. Test reserved cases and previous successes.
6. Return the results and the model decision to TTR.

Measure accepted examples per hour, setup time, transfer time, rejection causes, and human interventions.
Do not claim an efficiency gain without a measured baseline.

**Exit:** complete this cycle once with verified receipts and a useful decision.
A rejected candidate can complete the cycle if the result identifies a specific next correction.
**Excluded:** continuous uploads, automatic labels, and navigation authority.
Contracts: FEEDBACK298-A through D, FOCUS-LOOP, and [the feedback plan](Plans/OptInModelFeedback.md).

## 4 Highest priority model improvements

The current priority is reliable focus-change detection, with single-image focus and element detection tracked separately.
The latest small-control test exposes detail loss: both tested transition models miss all 4 accepted changes.
Image-based region proposals find those 4 changes. This supports a detail-preserving comparison, not an immediate model replacement.

| Problem | Planned test or correction | Required result |
| --- | --- | --- |
| Tiny controls and weak focus effects | Compare detail-preserving regions with full-frame inputs | Improve the known misses without losing retained correct results |
| Background changes resemble focus changes | Test content changes, shadows, zooms, and animated backgrounds separately | Reduce false changes without hiding actual focus movement |
| A fix loses previous successes | Use matched controls and a fixed regression set | Report every gain and loss, not only an aggregate score |
| Position and group imbalance | Audit exposure by region, condition, and related group | Cover edges, corners, endpoints, and ordinary central layouts |
| Poor transfer to real apps | Reserve independent app and journey groups | Measure real-app errors separately from Fixture results |
| Uncertain labels and boxes | Review conflicts against frames and native observations | Resolve each case or exclude it with a reason |
| Artwork distracts focus models | Vary artwork while preserving controlled focus comparisons | Improve unfamiliar artwork without learning a placeholder shortcut |
| Scrolling and timing confuse decisions | Compare causal temporal rules and existing models | Report missed changes and premature-ready decisions separately |
| Misleading confidence | Report uncertainty, emitted decisions, and conditional errors | Show support and limits without inventing a safety threshold |
| Slow experimental cycles | Batch compatible captures and reuse cached predictions | Complete larger tests with fewer repeated setup operations |

Use [FOCUS301](Plans/FocusImprovementProgram.md) for the 10 dispatch contracts.
Use [FOCUS302 results](Focus302Results.md) for the immediate detail-loss experiment.
Stop the failed mixture branch. Do not repeat completed fits merely because worker capacity is free.

## 5 Planned model milestones

### Reliable single-image focus

Build the qualified FocusRing corpus and compare a candidate with the shipped model.
Retain at least 6,000 distinct pairs and the scene, theme, and hard-negative quotas.
Use actual observed focus and production crop preprocessing.
Keep development, calibration, and final evaluation groups separate.

The existing held-out gates remain:

| Measure | Required value |
| --- | --- |
| Accuracy | At least 99.0% |
| False-positive rate on unfocused examples | At most 0.5% |
| False-negative rate on focused examples | At most 1.0% |
| Precision at threshold 0.85 | At least 0.98 |
| Recall at threshold 0.85 | At least 0.98 |
| Hard-negative false-positive rate | At most 0.5%, with actual supported examples |

Core ML export also needs preprocessing parity and a package no larger than 5,000,000 bytes.
Simulator success does not replace physical-device qualification.
Contracts: FOCUS-DET-05, FR-B/FR-C, and [FocusRing specification](FocusRingDetectorSpec.md).

### Reliable focus transitions

Complete the detail-loss comparison before selecting another architecture or larger training run.
Evaluate changed focus, unchanged focus, content changes, fixed-box changes, scrolling, overlays, and weak effects separately.
Report both frame orders, localization errors, abstentions, and latency.
Keep experimental Core ML delivery in observer mode until the applicable model gates pass.
Do not apply FocusRing's crop-classification gates to the transition task.
Contracts: FOCUS301, TRANSITION299, and [transition delivery](Plans/TransitionShadowDelivery106.md).

### Broader iOS detection

Repair label policy and unsupported class coverage before claiming a 41-class replacement.
Use cached predictions to review missing boxes and geometry errors. Preserve original labels and previous reports.
Continue fixed iOS experiments independently of tvOS capture availability.

DS-G8 requires withheld-template mAP at IoU 0.5 of at least 0.85, with required class support.
The planned fixture gates also require mAP at IoU 0.5 of at least 0.94 and mAP across 0.5–0.95 of at least 0.78.
Toggle and stepperControl AP at IoU 0.5 require at least 0.88 on supported cases.
No pooled tvOS score can satisfy an iOS gate.
Contracts: SEMANTICS229, TASK-6a-10/11, IOS-COV, and [iOS delivery](Plans/iOSPlatform.md).

### Broader tvOS detection

Expand representative full-screen layouts and supported controls without changing class meanings silently.
Qualify chevron-to-row association, dialogs, buttons, and difficult custom controls.
Keep generated artwork, rendered controls, and observed labels separate.
Complete the separate real-device holdout with at least 500 qualified screenshots under specific device authority.
Contracts: DETECTOR207, TTR-PERCEPTION, TASK-6b-R-1, and [perception delivery](Plans/TTRPerception.md).

## 6 Planned future features

These features already have backlog contracts. Their prerequisites still apply.

| Feature | Benefit | Entry condition and acceptance | Plan |
| --- | --- | --- | --- |
| More downloadable model families | Consumers get only required models | Separate rights, source, export, parity, and catalog checks for each family | [Distribution](Plans/OptionalModelDistribution.md) |
| ScreenAuditKit rules and CLI option | Audit required or forbidden elements and regions | Optional no-op default; compatible contracts; deterministic consumer tests | [Consumer work](Plans/ConsumersAndRelease.md) |
| Partial-crop robustness | Detect controls in incomplete screenshots | Qualified full-frame baseline; crop gain at least 15%; full-frame loss at most 1 percentage point | [Models](Plans/ModelsAndHardware.md) |
| Badge detection | Identify notification dots and counts | Versioned category extension; preserve existing IDs; later supported badge AP at least 0.88 | [Models](Plans/ModelsAndHardware.md) |
| Unified iOS and tvOS candidate | Potentially reduce model management | Compare dedicated baselines; preserve platform gates and hardware budgets | [Models](Plans/ModelsAndHardware.md) |
| macOS detection | Extend analysis to AppKit screens | Existing DS-G8 prerequisite; coordinate test; at least 2,000 images; withheld and tooltip gates | [Models](Plans/ModelsAndHardware.md) |
| Richer native generation | Better artwork, controls, themes, and full-screen layouts | Licensed assets; observed bounds; reproducible recipes; separate evaluation ancestry | [Generator parity](Plans/GeneratorParity199.md) |
| Reusable artwork corpus | Reduce repeated generation and improve visual diversity | Reviewed licensing, exact asset hashes, controlled compositions, and measured usefulness | [Artwork program](Plans/ArtworkModelImprovement204.md) |
| Native focus-effect reproduction | Make targeted growth, shadow, tint, and clipping examples | Fit measured captures; test separate native cases; report approximation error | [Effect measurement](Plans/NativeFocusEffectMeasurement.md) |
| Screen and row identity | Improve evidence for route reuse and backtracking | Qualify real journeys, scrolling, changing values, and localization | [Perception](Plans/TTRPerception.md) |
| VoiceOver alignment | Compare visual focus with semantic focus | Dedicated observed metadata and separate labels; never inferred from pixels alone | [Alignment](ADR-0007-VoiceOver-Navigation-Focus-Alignment.md) |
| OS appearance monitoring | Detect quality loss after OS or rendering changes | Versioned baseline sets and per-condition comparison; no automatic retraining | [Corpus lifecycle](ADR-0017-Corpus-Lifecycle-and-OS-Support.md) |

The macOS screenshot detector is separate from running existing models on a Mac.
The latter already supports local testing. It does not establish macOS UI detection accuracy.
The proposed model release tags are separate from a later library release containing qualified 41-class weights.

## 7 Proposed features

These ideas are not approved product commitments. Existing proposals remain proposals unless Tasks.md records an accepted scope.

| Proposal | Possible benefit | First useful test | Decision condition |
| --- | --- | --- | --- |
| Screen-context classifier | Distinguish layouts and overlays to select relevant evidence | Compare rules and a small classifier on reserved screens | Improve focus decisions without more confident errors |
| Lightweight difference or correlation head | Compare matching regions more directly | Matched experiment against the existing transition model | Better conditional errors within memory and latency limits |
| Temporal tracker | Use several frames to reduce timing errors | Compare against existing causal stability rules | Fewer premature-ready decisions without excessive waiting |
| Unfamiliar-screen score | Abstain on screens outside supported coverage | Frozen normal examples and separate unfamiliar screens | Useful risk reduction at reported coverage and cost |
| Human correction interface | Turn real failures into reviewed examples | Bounded before/action/after review with none and uncertain choices | Reliable labels with measured review effort |
| Optional app-specific adapter | Adapt a small component without replacing general models | Offline comparison on separate app groups | Improve that app while preserving other supported cases |
| Action-conditioned transition model | Learn how screens respond to remote keys | Audit qualified frame/key/next-frame sequences first | Show value beyond simpler visual and temporal baselines |
| Foundation-model interpretation | Explain verified UI evidence in natural language | Read-only comparison against structured evidence | Useful explanations without fabricated facts or action authority |
| Learned image similarity for review | Find near-duplicate content and split risks | Compare with exact pixel hashes and manual review | Find useful candidates without deleting intentional focus pairs |
| Quantized or alternative encoder | Reduce size or latency, or retain small details | Fixed model comparison with Apple conversion checks | Demonstrable accuracy and runtime benefit |

Relevant proposals: [screen context](ADR-0022-Screen-Context-for-Focus-and-Navigation.md), [foundation models](ADR-0016-Evidence-Bound-Foundation-Model-Semantics.md), and [evidence-driven experiments](Plans/EvidenceDrivenFocusQualification.md).

To promote a proposal into planned work:

1. Name the measured failure and intended user benefit.
2. Identify eligible inputs and a fixed comparison.
3. Record scope, owner, compute budget, and stop conditions in Tasks.md.
4. Define acceptance before execution.
5. Keep the feature only if the result supports its cost and risk.

## 8 Ownership and efficient delivery

| Owner | Responsibility |
| --- | --- |
| Maximum-mini-NUIAK | Model contracts, data admission, Apple validation, release preparation, and final acceptance |
| Maximum-mini-TTR | Local TTR and Fixture runtime used for specifically authorized capture |
| Sillycon-TTR | TTR source changes, optional integration, capture hooks, and application navigation policy |
| BigDog-NUIAK | Portable training, cached scoring, label-review candidates, and batch audits after accepted dispatch |
| BigDog-Coordinator | Cross-project routing, acknowledgments, and execution coordination within its qualified scope |
| Maintainer | Git writes, release publication, and decisions outside standing execution authority |

Batch compatible capture recipes within one prepared runtime session.
Give BigDog-NUIAK immutable input packages and bounded comparisons that do not block local analysis.
Keep Core ML, signed application, and Apple-runtime checks on an appropriate Mac.
Use exact transfer receipts. Preserve originals and remove shared copies only under the agreed receipt rules.
Stored, forwarded, accepted, running, completed, and independently verified remain separate states.

## 9 Next substantial work batches

| Order | Complete outcome | Parallel work | Stop condition |
| --- | --- | --- | --- |
| 1 | Publish and qualify the privacy-corrected optional tvOS preview | Freeze the small-control comparison from retained evidence | Public release needs the maintainer; host qualification needs actual TTR results |
| 2 | Diagnose and test 1 detail-preserving transition correction | BigDog-NUIAK audits cached labels and group exposure | Stop a failed hypothesis; preserve the full regression report |
| 3 | Complete 1 opt-in feedback cycle | Prepare missing real-app evaluation groups | Uncertain labels block admission, not software work |
| 4 | Improve single-image focus and artwork transfer | Continue the independent iOS label-policy experiment | Separate model gates and evaluation roles remain unchanged |
| 5 | Complete broader platform qualification and selected consumer work | Prepare gated future-feature inputs | Do not start gated models or change taxonomies without their prerequisites |

These batches describe sequencing, not newly dispatched assignments.
Check Tasks.md and current worker ownership before execution.

## 10 Boundaries that remain

- NUIAK reports perception evidence. TTR decides whether an action is authorized.
- A screenshot cannot prove hidden accessibility traits, VoiceOver identity, or exact private view classes.
- Native Fixture data does not establish real-app or physical-device performance.
- Model agreement and successful parsing do not create trustworthy labels.
- A public preview does not approve model promotion or navigation authority.
- No unrestricted capture, automatic training loop, or private-image upload follows from this roadmap.
- New model families retain their own licensing, privacy, data, and performance checks.

Use this roadmap for product scope. Use the linked plans for implementation and Tasks.md for the next authorized work.
