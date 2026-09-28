# Current brainstorming

**Last updated:** 2026-09-28 (America/Los_Angeles)  
**Purpose:** living summary of conversations, ideas and proposed follow-ups for maintainer review and prioritization.  
**Current emphasis:** real-world tvOS focus evidence and a reliable TTR capture-to-review loop, leading toward bounded autonomous navigation.

## How to use and maintain this document

- Update after each substantive planning conversation in this chat: summarize new ideas, revise affected items and append a dated conversation entry. This is conversation-driven maintenance, not a background monitor.
- Preserve stable idea IDs. Suggested rank is advisory; the maintainer chooses what to promote, defer or reject.
- Distinguish observed evidence, user preferences, hypotheses, proposals and estimates. Date status observations; do not treat historical readiness as current device availability.
- Record promotion decisions with a date and a link to the canonical plan/task. Do not silently turn discussion into implementation authority.
- **This is not a second execution queue.** [Tasks.md](Tasks.md) remains the sole work/ownership queue; [Research/CurrentState.md](Research/CurrentState.md) records project state. Existing assigned work retains its existing authorization and boundaries.
- When an idea is promoted, put architectural decisions in Research before implementation, define acceptance evidence and identify any needed runtime, transfer, spending or training approval.

## Direction established in today's discussion

1. **Human demonstrations should use TTR's controls, not a separate physical remote.** The human chooses actions initially; the agent can choose them later through the same qualified execution path.
2. **Preserve action sequences from the first session.** Do not collect only isolated stills and lose which buttons were pressed between focus states. Timing and UI settling behavior matter.
3. **Bring real screens into development early.** A small, useful diagnostic loop should precede a large annotation-platform project. Approximately 20–30 distinct screen situations was discussed as a starting collection target, not a qualification threshold.
4. **Keep durable real-world regression examples.** Human-reviewed screens should help preserve known capabilities. Training examples, development regression examples and protected final tests have different roles.
5. **Prefer existing review tools; Swift is not required here.** Build only the NUIAK-specific integration needed for trustworthy import/export and feedback to collection.
6. **Consider Jev as an optional decision/escalation layer.** Preserve useful sequence data now without making capture depend on choosing Jev or another temporal model.
7. **Improve both experiment speed and experimental value.** Investigate CUDA for expensive detector training, while fixing coverage, labeling and geometry gaps before another long run.
8. **Communicate material changes and blockers.** Avoid repeatedly announcing unchanged capture, simulator or device-policy status. Keep terminology and completion claims concrete.

These are discussion directions, not blanket approval for installations, remote control, uploads, model execution or promotion.

## Proposed follow-ups, in suggested priority order

All rows are **pending maintainer prioritization/promotion** as brainstorming items. References to existing packets do not reassign or restart those packets.

| Rank | ID | Proposed follow-up | Reviewable outcome / decision | Dependency or boundary |
| --- | --- | --- | --- | --- |
| 1 | B-01 | Establish the lowest-friction capture-to-review path; retain remote integration as an optional host profile | Max-local Office still delivery/cleanup now demonstrated; next qualify sequence recording and importer round trip. Remote pairing/two-host acceptance remains separate | Local pass avoids requiring Sillycon for every session. It does not qualify remote MCP, automatic host switching or training admission. |
| 2 | B-02 | Specify and verify human-operated TTR action/frame recording before the first new collection | A complete, time-correlated event sequence covering before/after frames, input events, command outcomes, settling and gaps | Confirm whether GUI controls and future agent inputs reach the same recording path. Remote-still support alone does not prove sequence recording. |
| 3 | B-03 | Complete intake of the two existing Photos captures | Original-byte receipt, reviewed per-frame control bounds/states and production crop QA for the operator-confirmed pair | Receive retained originals; do not recapture merely to complete intake. Current ownership/cleanup remains unverified. |
| 4 | B-04 | Define and collect a small real-screen focus benchmark | Approximately 20–30 distinct screen situations, reviewed pairs/competitors and genuine transitions; frozen intended roles and complete accounting | Requires approved session scope and B-02 for action-labeled sequences. Formal human-label admission is a separate decision; current Photos lane is diagnostic-only. |
| 5 | B-05 | Evaluate FDR-009 on the existing frozen development comparison | Same-input comparison against retained baselines on 48 frames, with complete predictions and frame-level focus outcomes | Existing next unassigned task; requires evaluation assignment. No new training, threshold sweep or protected-challenge use. Can proceed independently of TTR integration. |
| 6 | B-06 | Prove a minimal interactive review-tool workflow | Promoted to HUMAN-REVIEW-01; local Labelme stock-editor round trip and crop integration verified on8 retained frames; human batch review/timing next | Maintainer rejected Docker/CVAT as overkill; one local Python/Qt editor first. FiftyOne/triage deferred. No training admission implied. |
| 7 | B-07 | Define failure-to-collection feedback between TTR and NUIAK | Failure record → review → scoped collection request → verified delivery → explicit data-role admission | Capture transport is distinct from durable asynchronous requests and issue coordination. Do not assume EXT-CAP-01 completes both. |
| 8 | B-08 | Audit iOS class coverage, label semantics and geometry | Reviewed class/source/scale matrix, corrected demonstrated defects and a targeted data specification before another full run | Local work does not depend on Photos or TTR. No taxonomy change or new rendering implied. |
| 9 | B-09 | Profile detector training and benchmark a matched CUDA workload | Measured throughput, memory, setup cost and projected cost per comparable experiment; choose local/cloud execution based on evidence | No known M4-to-CUDA multiplier. Spending, uploads and benchmark/model execution require approval. Preserve custom training behavior and evaluation comparability. |
| 10 | B-10 | Specify observer-mode and bounded autonomous navigation qualification | Replayable transitions, task definitions, failure/abstention metrics and explicit permission/stop conditions; first task: reach a visible control and stop | Qualify observation and transitions before selection autonomy. Exact deployed chain must be tested. |
| 11 | B-11 | Evaluate Jev as a narrow second opinion in observer mode | Compare proposed actions with rules and reviewed outcomes; measure caught errors, false escalations, latency and cost | Optional, not a capture prerequisite. Requires approved API/data-sharing scope; no claim that scores are calibrated tvOS action-success probabilities. |
| 12 | B-12 | Investigate temporal focus/transition methods using genuine sequences | Compare frame-difference and action-conditioned approaches against single-frame baselines; document when each helps or fails | Need ordered, correlated observations including no-ops; do not substitute constructed transitions for live evidence. |

## Topic notes

### A. Capture the human demonstrations through the future automation path

**Proposed sequence:** before observation → human action through TTR → command receipt → transition observations → settled after observation → reviewed outcome.

The important invariant is shared execution and recording, not merely a similar-looking on-screen remote. Human and agent callers may differ, but their input semantics, command correlation and outcome verification should match.

Preserve, where actually supported:

- Original frames, exact hashes, target/source identity, session and observation IDs.
- Each input's ID, direction/button, press/release, duration/repeats and gesture parameters; unsupported details remain unavailable.
- Dispatch, acknowledgment and frame timestamps, with a declared clock basis and cross-host correlation/uncertainty. Do not subtract unrelated host clocks as if synchronized.
- All events between observations, including rapid repeats, no-ops, failures and ambiguous completion. Multiple inputs without an intermediate frame do not establish each intermediate focus state.
- Reviewed before/after focus and per-frame control bounds; visible competitors, scrolling, modals and screen transitions.
- Settling observations and timeouts. An accepted input does not prove a focus move; stable pixels alone do not prove the intended state.
- Intended task/goal where known, kept distinct from what actually happened. A human action is demonstration evidence, not automatically an optimal or safe-action label.

Keep raw sequence evidence so pairs, crops and longer journeys can be derived later without reconstructing lost events. Do not automatically add audio, video or other collection beyond the approved scope.

**Capability gap to check:** whether the producer's remote-still workflow records human TTR inputs and associates them with frames. No physical-remote interception is requested.

### B. Real-world data, regression and protected evaluation

Real-device screenshots are real-world data, not synthetic data. Fixture-generated screens supply controlled variations, but more random backgrounds or seeds do not necessarily create independent layouts or sources.

- Start with a small, diverse diagnostic collection instead of waiting for a full annotation platform.
- Review all examples proposed for the initial human-label lane; allow unknown/unresolved labels rather than guessing.
- For focus, review the complete visible candidate set where feasible. One paired target does not establish unique correct focus selection across the frame.
- Assign roles by source/layout/journey and overlap, not random neighboring frames. Adjacent states of one journey must not be scattered across training and purportedly independent tests.
- Preserve a development regression set for repeated iteration. Once failures drive tuning, that set is development-exposed, even if its exact images never enter training.
- Keep a separate protected final test for broader qualification. Thirty situations are an initial target, not proof of arbitrary-app reliability or all-class coverage.
- “Gold” means carefully reviewed reference labels, not infallible labels or permanently independent evidence. Version any corrections and retain their rationale.
- Current Photos importer output remains diagnostic-only. Approve and implement a human-reviewed training/evaluation admission policy explicitly before changing its eligibility.

### C. Human review: use existing tools, preserve NUIAK contracts

Two complementary lanes were discussed:

1. **Find what needs attention:** dataset browsing, random/stratified samples, class filtering, suspected misses, false positives and localization errors.
2. **Inspect and correct:** full-frame context, selectable object lists, label changes, precise box edits, missing-object annotation and explicit uncertainty/reviewer decisions.

Leading proposal: [FiftyOne](https://docs.voxel51.com/getting_started/object_detection/03_finding_mistakes.html) for triage and [CVAT](https://github.com/cvat-ai/cvat) for editing/review, using their [existing integration](https://docs.voxel51.com/tutorials/cvat_annotation.html). Verify selected-version features and edition requirements during a proof of fit. Configure local/self-hosted endpoints explicitly; the documented FiftyOne annotation default must not be assumed to keep screenshots local. These tools do not add Python to the shipped Swift library.

Reuse the existing [Photos importer](scripts/photos_focus_pilot.py) and [Fixture review tooling](scripts/focus_fixture_review.py). They already provide evidence preservation and static sheets, not a full interactive corpus editor. Build a small adapter rather than a second annotation application. Label Studio was also raised as an alternative to assess if custom review forms become the dominant requirement; no tool was selected or installed.

**Bounds convention:** annotate the control, not an arbitrary tight outline of its focus glow. Use verified native geometry where available; otherwise review detector-prefilled boxes with zoom/precise coordinates. Keep per-frame geometry because focus can change appearance or scale. Production FocusRing crops expand 16% on each side and resize to 256×256 using the existing cropper. Do not assume small box errors are harmless for thin controls or dense neighbors.

Model-assisted shapes and disagreement scores are proposals, not ground truth. Keep original labels, predictions and reviewed revisions separate. Connect reviewed failure categories to Fixture recipes or real-source requests; generic annotation tools do not know those project-specific mappings.

### D. Review effort and sampling

The discussion distinguished a small diagnostic session from a mature repeatable audit:

- Run automated integrity, bounds, identity and split checks on every admitted image.
- Combine representative random audits with targeted review of rare classes, new templates and suspected failures. Targeted samples alone do not estimate corpus-wide defect rates.
- Inspect meaningful variants of each new generator template. Near-identical renders do not provide independent evidence against shared generator bugs.
- As an illustrative binomial calculation, zero observed defective images among 300 independent representative reviews gives an approximately 1% one-sided 95% upper defect-rate bound; 600 clean reviews gives approximately 0.5%. This assumes effective error detection and suitable sampling, does not establish per-class quality, and is not a model-accuracy guarantee. [Statistical reference](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm)
- No fixed percentage, mandatory 300-image audit or new qualification threshold was adopted. Time a small first batch and estimate review effort from actual screen density and correction rates.

### E. Roadmap toward production-stable tvOS inspection

1. Qualified capture/delivery and reviewed real-screen evidence.
2. Separate baselines for control detection, focus on reviewed boxes, and focus using detector-produced boxes; evaluate OCR associations where they affect actions.
3. Targeted model/data improvements against frozen development evidence, followed by Core ML verification.
4. Observer mode on genuine input sequences: verify moves, no-ops, scrolling, settling and unexpected transitions without controlling the device.
5. Bounded autonomy: reach a visible control and stop; later allow specifically approved selections and verified returns.
6. Full-chain qualification on unfamiliar sources and realistic interruptions, then controlled expansion with regression checks and rollback.

The system maintains screen identity, navigation history, goal and observation freshness. Similar screenshots must not collapse distinct focus/modal states into one node. A deterministic policy constrains actions despite probabilistic perception: observe → propose → check permission → one action → fresh observation → verify. Unknown state or uncertain completion must not trigger blind retries, especially Select.

Measure task completion, wrong selections, prohibited-action prevention, correct abstentions, unnecessary stops, human interventions, recovery and latency. Set release criteria before the final test. A system that always stops is not useful; one that guesses is not safe. Model scores alone do not qualify navigation.

NUIAK owns perception, review/data admission, evaluation and model delivery. TTR owns authorized execution, leases, capture and transport. A planner may propose actions, but screen text and model confidence never confer authority. Native observations and screenshot predictions remain explicitly distinguished.

### F. Jev, escalation and token efficiency

The intended product is **TypeSafe Jev**, not JEPA/V-JEPA. Its documented `Choice` interface takes state and finite options and returns structured choices/probabilities/confidence. The current documented model accepts text/structured text, not image inputs, and does not offer customer fine-tuning. [Introduction](https://docs.typesafe.ai/introduction) · [Model specifications](https://docs.typesafe.ai/models)

Proposed role: rank narrow semantic alternatives or provide a second opinion alongside ordinary navigation logic. Actions such as Up/Down/Select are a finite vocabulary; UI state and the effects of those actions are not thereby trivial or fully observable.

- Start with observer-mode comparisons against a simple baseline, not live authority.
- Use compact relevant state and explicit allowed choices, including wait/abstain where appropriate.
- Keep exact geometry, clocks, permission enforcement and arithmetic in code.
- On disagreement, stop input and refresh evidence; unresolved cases may escalate to richer reasoning/vision and finally human review.
- Agreement on the same incorrect perception is not independent confirmation. Measure confidence calibration on our task; a choice score is not automatically a probability of successful device action.
- Measure error interception, false escalation, network/runtime latency and token/currency cost. Efficiency claims are not project measurements.
- Bound escalation attempts and costs. More tokens cannot repair missing or stale pixels.
- Preserve action sequences now for multiple future consumers; neither Jev selection nor a temporal-model decision should block recording.

Documented limitations include numerical precision, indirection and adversarial content. API use is external data processing and requires approved scope; no request/data was sent during this discussion. [Limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13)

### G. iOS training evidence and specific fixes

“Bad data” was corrected during discussion: no evidence established widespread corruption or universally wrong labels. The evidence shows coverage gaps, family-transfer failures and hypotheses about semantics/geometry. Run 013 improved the comparable withheld-family score from 0.5549 to 0.6322 but did not qualify.

| Issue | Evidence discussed | Proposed remedy |
| --- | --- | --- |
| Familiar-family success does not transfer broadly | Addon mAP50 0.9785 versus withheld 0.6322 on different populations; listRow/imageView show particularly large family-dependent differences | Diversify composition, control context, scale and sources; use reviewed real examples; avoid merely multiplying cosmetic variants. |
| Model selection has blind spots | Train supports 40/41 classes; validation 35/41 and lacks pageControl, progressView, secureField, textField, unknown and webContent | Class/source/scale inventory and preflight; independently sourced validation examples, not reuse of the protected test. |
| Role confusion | 245 secondaryButton→cancelAction diagnostic associations; one example nearly perfectly localized but misclassified | Audit labeling semantics and source annotations; add contrasts; determine what requires text/context rather than assuming visual intent is observable. |
| Geometry and tiny features | Thin indicator shrinks to roughly 2.25 pixels at 640 preprocessing; page dots also mislocalized | Verify source geometry/conversions first; then bounded resolution or second-pass experiments with runtime/export tradeoffs. Never distort correct labels to fit predictions. |
| Independent-test gaps | Only 13 classes represented in original withheld set; combined test supports 38, with three absent | Deliberate independent coverage specification for all supported classes; separate development and protected final families. |

These are proposed investigations/fixes, not proven causal explanations. [Error analysis](reports/work/IOS-R013-EVAL/error_analysis.md) · [Evaluation handoff](reports/work/IOS-R013-EVAL/handoff.md)

### H. Training hardware, runtime and cost

- Run 013 was **training**, not inference: YOLO11m, 41 classes, batch 8, MPS, 106 epochs in **62.818 hours**, best epoch 91. Earlier spoken references to “41 hours” or holding cloud runtime constant were corrected; 41 was the class count.
- Profile loading, augmentation, custom hard-example sampling, validation, GPU compute, memory pressure and possible CPU fallback. Current script hardcodes MPS and disables image caching; these observations do not prove the bottleneck.
- Compare the same representative PyTorch workload on CUDA before another long detector experiment. Preserve pinned data, custom callbacks, metrics and checkpoint behavior; account for any precision/batch changes.
- Consider smaller-model or short fine-tuning experiments for screening specific hypotheses, measuring accuracy tradeoffs. Do not start with a Swift/framework rewrite.
- The Mac remains useful for capture, review, small FocusRing experiments and Core ML verification. FDR-009's full recorded process was about six minutes, unlike the expensive iOS detector run.
- Illustrative arithmetic only: at $2/hour, a measured 5×/10×/20× speedup on the 62.8-hour workload would imply approximately $25/$13/$6 of training compute. These are not forecasts; setup, idle time, storage and transfer can add cost.
- Published AWS G5 “up to 3.3×” compares with G4dn; Lambda's 2.5–3.1× H100 result compares with A100 on a language-model workload. Neither establishes an M4-to-CUDA speedup for our configuration. [AWS claim](https://aws.amazon.com/ec2/instance-types/g5/) · [Lambda benchmark](https://lambda.ai/blog/deepchat-3-step-training-at-scale-nvidia-h100-sxm5-vs-a100-sxm4)
- No provider, GPU purchase, budget, upload or cloud run was approved. Compare cost per useful experiment, not hourly price alone. Faster hardware does not remedy inadequate training/evaluation coverage.

### I. Rough effort discussed—not commitments

| Scope | Discussion estimate | Important qualification |
| --- | --- | --- |
| Fuller local review integration plus first feedback cycle | 5–9 engineering days | Assumes installation/artifacts work; excludes new TTR producer capabilities. A small diagnostic loop should happen earlier. |
| 300-screen review example | 5–15 reviewer-hours at 1–3 minutes/screen, before substantial corrections | Unmeasured assumption; time the first roughly 30 screens. Not a required starting audit. |
| Capture loop plus initial real-world benchmark | Approximately 1–2 weeks | Requires sustained effort, available hardware/operator and fulfilled integration dependencies. |
| Supervised navigation/perception improvements | Another 2–4 weeks | Depends on measured real-screen failures; not a guaranteed accuracy improvement. |
| Narrow production candidate | Roughly 2–3 months total | Candidate only, conditional on end-to-end gates. No promised arbitrary-app capability. |
| Broad unfamiliar-app, complex interaction coverage | Several months or longer; no defensible firm date | Re-estimate from initial benchmark and task success, not training epoch count. |

### J. Terminology to use consistently

| Term | Meaning here |
| --- | --- |
| Inference | Run fixed model weights to produce predictions. Does not teach the model. |
| Training | Compute predictions/errors and update model weights from examples. |
| Input validation | Check images, metadata and bounds for integrity; can occur during intake or before inference. |
| Model validation | Use labeled development examples to assess/select candidates; may run inference or reuse predictions. |
| Retention/regression check | Check previously covered behavior was not lost. Purpose of a check, not necessarily a distinct stage or independent test. |
| Generalization evaluation | Test transfer to properly separated, unfamiliar source/layout groups. |
| Deployment verification | Verify the converted model, preprocessing and actual runtime behavior. |
| End-to-end qualification | Test the complete perception/control task, including permissions, actions, verification, stopping and recovery. |

FDR-009's 18/18 retention result covers nine familiar focused/unfocused pairs. The retention set also selected the checkpoint, so it is development evidence, not proof of unfamiliar-app navigation.

## Status observations that informed the discussion

These are historical observations, not automatically refreshed live status.

- **Local model evidence:** [FDR-009 handoff](reports/work/FDR-009/handoff.md), [retained focus diagnosis](reports/work/FOCUS-OFFLINE-DIAG-01/handoff.md), and [Run 013 results](reports/work/IOS-R013-EVAL/handoff.md). Earlier focus candidates each uniquely identified focus on only 1/48 frozen validation frames; FDR-009's same-input evaluation remains the documented next step. No shipped-model change was established.
- **TTR producer update read 2026-09-28, timestamp 14:31:43 UTC (07:31 Pacific):** signed development candidate prefix `51652c05`, reported about 93 MB; loopback mutual TLS and a 2.5 MiB three-chunk delivery passed according to producer status. Actual two-host, live simulator and physical Office acceptance were unrun. Local verification checked status schema and exact plan/runbook/response sizes and hashes, not the runtime itself.
- **Interface ownership clarified:** TTR supplies `tvtestrig-remote` and its MCP bridge. NUIAK registers the client and adapts `review-manifest.json`; a separate NUIAK MCP server is not required by that published capture design. Broader durable asynchronous coordination remains separate work.
- **Producer metadata references:** `tvtestrig/ttr-external-capture-plan-rev2-20260928T062700Z.md` and `tvtestrig/ttr-ext-cap-consumer-runbook-20260928T062700Z.md` on the verified shared-status endpoint. The app was not yet published there; new exact-file transfer approval or an authorized matched build is needed. Do not bypass the recorded Maximum-mini release-build pause.
- **Photos:** two operator-confirmed focus-state PNGs exist on the producer side; consumer receipt, bounds review and crop QA remain incomplete. Native Photos focus telemetry is unavailable in the described contract. See [pilot handoff](reports/work/PHOTOS-PILOT-01/handoff.md).

## Dependency traps to avoid

- Do not wait for better models to qualify capture/delivery, or for live TTR availability to do local label/coverage analysis.
- Do not make a full annotation application a prerequisite for a small reviewed diagnostic set.
- Do not choose Jev before preserving model-independent action/frame evidence; conversely, do not require Jev to capture that evidence.
- Do not demand another Photos capture when the actual missing step is receipt of existing originals.
- Do not train on inspected benchmark failures and then call that same benchmark an untouched final test.
- Do not treat training speed, passing software tests, verified delivery, data eligibility and navigation qualification as interchangeable successes.

## Promotion log

2026-09-28 | B-01 (bounded portion) | Maintainer requested fresh TTR status, testing its pairing/registration/Simulator request and feedback | [EXT-CAP-02](reports/work/EXT-CAP-02/handoff.md), [Tasks.md](Tasks.md) | Actual local interface probes completed; live pairing awaits endpoint, human fingerprint confirmation and exact remote target/grant scope. No broad model/data work promoted.

Future entries: `date | idea ID | maintainer decision/priority | canonical task/plan | exact approved scope`.

## Conversation log

### 2026-09-28 — Explain labels visually; restrict annotation to rectangles

- Maintainer requested a visual reference for every editor label, particularly
  Home-screen icons and whether captions belong in their boxes. Generator evidence
  confirms `collectionItem` for the tile with separate `label` caption; focus-only
  review does not require a separate caption target. `homeIndicator` is unrelated.
- Produced41 schematic label examples plus a quick tvOS reference. Distinguish
  control role from focus state and exclude diffuse glow/padding from bounds.
- Made creation rectangle-only with R/E controls and verified the actual two-click
  canvas path. No forced restart or conversion of in-progress human annotations.
- This refines B-06/HUMAN-REVIEW-01; it does not change taxonomy, historical labels,
  training admission or model gates. [Rules](Research/HumanReviewLabelGuide.md).

### 2026-09-28 — One local review editor, no Docker

- Maintainer rejected Docker as disproportionate and approved proceeding with a
  lightweight local Python annotation workflow. B-06 is promoted to HUMAN-REVIEW-01.
- Implemented a pinned stock Labelme editor and a small NUIAK integrity/review
  adapter; no service, database, CVAT or FiftyOne dependency. Eight retained
  frames load; Photos004/005 have explicit manual proposals to review in a batch.
- Installed-editor save/reopen, checkbox editing and production crops are verified
  as software tests. The next human step is reviewing bounds/classes/states and
  explicitly finishing the batch; no chat per control and no training admission.
- Triage/coverage queues remain later work. [Guide](reports/work/HUMAN-REVIEW-01/OperatorGuide.md)
  and [handoff](reports/work/HUMAN-REVIEW-01/handoff.md) hold implementation evidence;
  Tasks.md remains the sole execution queue.

### 2026-09-28 — Local Python annotation/review implementation plan

- Maintainer requested tasks/tranches for the local human review lane. Produced
  [four-tranche plan](Research/Plans/LocalHumanAnnotationReview.md), indexed in
  Tasks.md and the implementation catalog; no installation/code execution assigned.
- B-06 expands into HUMAN-REVIEW-01/02: existing FiftyOne/CVAT integration, real
  edit/export/reimport on8 retained frames first, then defect audit/sampling queues.
- HUMAN-REVIEW-03 binds the real automatic-recorder schema; this does not block
  retained-frame review. HUMAN-REVIEW-04 separately approves human-label admission,
  preserving diagnostic rejection and source-separation rules until that decision.
- Identified real importer mismatch: inline exports report outputWritten=false and
  include large base64 receipts; Photos-only review fields cannot represent Home
  or Settings. Plan an explicit compatible adapter, not rewritten source metadata.
- Local service/dependency setup and Docker storage exceptions require scoped
  approval; no cloud uploads or new inference assumed. Recommended first assignment
  is HUMAN-REVIEW-01 end to end, while TTR recorder work proceeds separately.

### 2026-09-28 — Supervised capture exposed missing per-input images

- Maintainer explicitly rejected chat between presses. Stop checkpoint collection;
  promote B-02's recorder gap as the next P0 integration requirement, not an optional
  convenience. Desired flow: one Start, normal human TTR navigation, one Stop,
  batch review. [Concrete contract](Research/Plans/TTRActionLinkedCapture.md).
- Max-local session has retained8 checkpoint images and9 human TTR input events,
  including both Photos button focus states and a boundary-consistent no-change.
- The user expects each focus movement to retain usable evidence. Actual Settings
  setup logged Right/Up/Select without images between them: current chat-paced
  capture does not meet that expectation. Do not infer missing states from inputs.
- B-02 follow-up is now concrete: action-triggered before/settled-after capture,
  exact event/image binding, rapid-input overlap/gap reporting, no-op retention,
  and optional image-bound OCR evidence. Polling alone cannot guarantee every move.
- Reviewed bounds/states, duplicates and source roles remain separate from raw
  capture. No automatic recorder implementation or training launched here.

### 2026-09-28 — Prefer local TTR when it works

- Maintainer questioned Sillycon coordination overhead and authorized a Max-local
  Office connection/capture test with Office free; then approved permission prompts.
- Fresh connection and actual local screenshot delivery passed after an initial
  timeout. Image shows Home with Photos visibly focused, not the earlier Photos dialog.
- Recommendation: Max-local primary for the next approved session; remote remains
  useful as an optional profile, not a prerequisite or automatic failover.
- Next proposed priority is B-02: prove action/frame recording through human TTR
  controls, then a small reviewed real-screen collection. A still-image success
  alone does not preserve input sequences or admit training data.
- Evidence and exact cleanup: [local test handoff](reports/work/LOCAL-OFFICE-CAPTURE-01/handoff.md).

### 2026-09-28 — TTR consumer test follow-up

- New producer runbook requests a source-built client; its named commit is absent locally, but an existing app now exposes remote helpers. Avoid rebuilding solely from checkout age.
- Actual help/status/register and standalone MCP discovery pass. LAN discovery returned no candidates; no current remote target UUID supplied.
- Identified registration-state propagation omission: supplied project-local state directory is absent from printed MCP JSON. Proposed explicit environment configuration is staged, not installed.
- Shared-interface capture grants are still-only; input-correlated human demonstrations remain a distinct collection capability, not part of this passing local interface check.
- Live test completion is pending human pairing/target scope; see the canonical packet for evidence rather than treating this brainstorming log as execution status.

### 2026-09-28 — Capture, review, autonomous navigation and training efficiency

- Clarified inference/training/validation/retention and the limits of current iOS/focus evidence.
- Discussed real-screen human review, existing tooling, bounding-box conventions and statistical audit caveats; narrowed the initial ambition to a useful small diagnostic loop.
- Checked fresh TTR producer metadata and identified consumer integration as the next handoff; clarified that the packaged TTR MCP bridge already serves the proposed capture interface.
- Established the desired demonstration path: human controls TTR, which records its own inputs and correlated frames; future agent control should use the same execution/recording path.
- Identified raw action history, timing, no-ops and intermediate observations as valuable for future temporal methods and Jev evaluation.
- Outlined observer mode, bounded autonomy, full-chain qualification, escalation and gradual scope expansion, with conditional effort estimates.
- Discussed CUDA economics and corrected unsupported runtime/speedup assumptions; separated hardware turnaround from dataset quality.
- Reviewed five iOS data/evaluation issues and proposed an audit → coverage specification → targeted collection → short experiment sequence.
- Requested this living document so the maintainer can review and promote follow-ups by priority. Documentation creation only; no new execution assignment inferred.

### 2026-09-28 — Batch rectangle reuse

- Highest immediate review friction: visibility checkmarks looked like selection,
  and cross-frame paste was not dependable for the operator. Implemented explicit
  Select all/Copy/Paste, local review IDs and fresh confirmation on pasted boxes.
- Next: save/relaunch and use the Home frames to check the real operator workflow;
  adjust tile scale and focus states, then perform the separately explicit Finish.
- Proposed later follow-up: assess whether focus-state batch editing would help
  after this reuse workflow is tried. Do not infer labels or bulk-confirm unseen boxes.

### 2026-09-28 — Explicit batch completion instead of confirmation busywork

- Maintainer completed tagging and assigned a Finish review action. Saved audit
  found113 rectangles, missing local IDs, eight unknown focus states (IDs6/9 on
  four Home frames), and mostly unchecked confirmation flags.
- Implemented one ready/exception summary with jump-to-frame and named-reviewer
  attestation for the ready subset. Automatic local ID bookkeeping is separate
  from human focus decisions; unresolved frames remain pending.
- Next priority: operator resolves exceptions and confirms the batch, then run
  production crop QA against that immutable revision. Training admission remains
  a separate assignment. No new capture or model run is needed for this step.

### 2026-09-28 — Faster per-image review controls

- Added requested All frame flags on/off for the three current-image assertions;
  kept box focus states and confirmation separate.
- Added Command-Left/Right navigation alongside A/D, retaining unsaved-edit prompts.
- Verified navigation also works after jumping to a Finish review exception.
  Next remains operator completion and revision-bound crop QA, not new tooling scope.

### 2026-09-28 — Human data ready for a role decision

- Joe completed8 frames/113 controls and2 explicit Photos pairs. All113 production
  crops verified;111 distinct crop pixels, no hard integrity/label conflicts.
- Completed HR2 audit with frozen hashes, separate seeded/targeted queues, visual
  crop sheets and a correction/revalidation path. Repeated states stay preserved.
- Highest next decision: reserve this correlated batch for development regression,
  not training, and approve the proposed human-label evaluation lane plus one fixed
  shipped-vs-FDR-009 comparison. No scoring/training has been started.
- Next collection should add matched Settings positives, broader Photos layouts
  and additional focused Home tiles through the action-linked recorder. Quantities
  are collection targets, not new qualification thresholds. Model failures will
  refine priorities after the approved comparison.
-8 positives vs105 negatives makes raw accuracy misleading; report recall, false
  positives and paired outcomes. Complete-frame coverage/source independence remain
  unqualified. [Decision proposal](Research/Plans/HumanFocusAdmissionDecision.md).
