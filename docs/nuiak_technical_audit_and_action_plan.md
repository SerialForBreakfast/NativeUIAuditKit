# NativeUIAuditKit (NUIAK) Technical Audit & Engineering Action Plan

A technical audit of the `NativeUIAuditKit` (NUIAK) architecture, training methodologies, and agentic experimentation graph (`ADR-0027`, `FOCUS307–366`, `HCF333–386`), paired with concrete engineering steps to resolve current bottlenecks, is detailed below.

---

## 1. Executive Diagnosis: Where NUIAK Is Stalling & Why

Across your three primary model lanes (**Stage 1 YOLO11 Detector**, **Stage 2 `FocusRingDetector` Crop Classifier**, and **Transition/Change Classifier `DTM` / `FOCUS3xx`**), the research logs expose four core technical bottlenecks:

1. **Frozen Classifier Logit Dominance (`FOCUS307`, `FOCUS313`, `FOCUS320`, `FOCUS343`):**
   * In the transition/focus-movement models, the frozen whole-frame classifier (`192×128`) produces massive negative logits (`-13.98` to `-9.94`) on small or corner native controls (which shrink to `10.8 × 3.5 px` at `192×128` downscaling from `3840×2160`).
   * Trainable detail heads (`2-window` 32×32 crops) add only `+4.58` to `+5.54` (or even `-2.16` in `FOCUS313`), failing to cross the `0.85` threshold (`logit >= +1.7346`, requiring `+11.67` to `+15.72` of positive correction).
2. **Severe Gradient Opposition Between Authored & Native Data (`FOCUS320`, `FOCUS348`):**
   * Authored/synthetic gradient norms (`17.10` to `34.97`) are **99× to 139× larger** than original native gradient norms (`0.057` to `0.063`), with opposing cosine similarity (`-0.81` to `-0.91`).
   * Simple gradient projection + norm capping (`FOCUS320`) failed because **Adam maintains per-parameter exponential moving averages (`exp_avg` and `exp_avg_sq`)**—projecting raw $g_t$ before passing it into Adam still allows historical momentum and per-coordinate variance scaling to rotate the actual parameter update $\Delta \theta_t$ back into conflict with native preservation cases.
3. **Anisotropic Distortion & Lack of Peer Normalization in `FocusRingDetector` (`FocusRingDetectorSpec.md`, `FocusTransfer10.md`):**
   * Stage 2 expands a YOLO box by `16%` and resizes directly to `256×256` (`MobileNetV4-Conv-Small`, ≤5.0 MB FP16 gate). Wide controls (4:1 Settings rows) get crushed horizontally, destroying the uniform border/halo geometry.
   * Worse, evaluating each crop in isolation causes **25 false positives on mostly-white artwork cards (`FDR032`)** because a bright white card looks locally "focused" unless compared against sibling cards on the same shelf/row.
4. **Script Proliferation & Queue Vulnerability (`RCA-20261013`, `scripts/`):**
   * You have **450+ one-off numbered scripts** (`scripts/focus302.py` through `scripts/hcf375.py`, plus matching `test_*.py` files) and 43,530 tracked-but-ignored files bloating the git index (`923 MB`).
   * As documented in `RCA-20261013`, coupling a rule like "maintain 25 ready jobs" (`WorkerWorkflow.md`) with a loose script-registration queue incentivized an agent to hallucinate 0.2-second dummy array scripts.

---

## 2. Model Methodology Upgrades (Object, Focus & Transition Detection)

### A. Fixing the Transition / Movement Architecture (`FOCUS307–366`)
Stop trying to add an uncalibrated residual scalar from a trainable detail branch onto a frozen whole-frame logit that sits at `-13.98`.

* **1. Spatial-Gate Logit Fusion (Replaces Additive Residual):**
  When the area of the candidate diff window $A_{\text{diff}}$ is small relative to the frame (e.g., `< 1.5%` of screen area, such as the `216.5 × 59.5 px` corner targets on a 4K canvas in `FOCUS343`), the `192×128` whole-frame encoder is blind by Nyquist sampling limits (`10.8 × 3.5 px`).
  Replace $z_{\text{final}} = z_{\text{whole}} + z_{\text{detail}}$ with a **resolution-gated mixture**:
  $$g = \sigma\left(w_g \cdot \log\frac{A_{\text{diff}}}{A_{\text{frame}}} + b_g\right), \quad z_{\text{final}} = g \cdot z_{\text{whole}} + (1 - g) \cdot z_{\text{detail}}$$
  When the change region is tiny, $(1 - g) \to 1$ suppresses the `-13.98` whole-frame prior so the high-resolution detail windows govern the decision, while global lighting/scroll disturbances ($A_{\text{diff}}$ large) remain governed by $z_{\text{whole}}$ (which already gets `226/226` on global lighting).
* **2. Optimizer-Aware PCGrad + Margin Preservation Loss (`FOCUS320` / `FOCUS348` Fix):**
  In `FOCUS320` and `FOCUS348`, soft BCE preservation loss failed because native examples already at $p = 0.113$ drifted to $0.205$ (into the `[0.15, 0.85]` abstention dead-zone) with barely any BCE penalty.
  * Replace soft BCE preservation on retained native controls with a **Hinge Margin Preservation Loss** anchored at the decision boundaries (`0.12` for negative, `0.88` for positive, in logit space $z_{\text{neg}} \le -1.99$, $z_{\text{pos}} \ge +1.99$):
    $$\mathcal{L}_{\text{preserve}} = \sum_{i \in \text{Pos}} \max(0, 2.0 - z_i)^2 + \sum_{j \in \text{Neg}} \max(0, z_j + 2.0)^2$$
  * Apply gradient projection **in preconditioned update space** (or use SGD with momentum `0.0` / Lion on the 4–10 trainable detail/correction tensors) so Adam's second moment $v_t$ does not undo orthogonal projection.

### B. Fixing Stage 2 `FocusRingDetector` (`MobileNetV4-Conv-Small`)
To eliminate the 25 white-artwork false positives and wide-row aspect distortion (`FocusTransfer10.md`) while staying strictly under the **5,000,000-byte (`5.0 MB`) FP16 CoreML gate**:

* **1. Dual-Scale Border-Strip + Aspect-Fit Input Encoding:**
  Standard `256×256` anisotropic stretching warps a 3px vertical border into a 0.7px blurred edge while inflating horizontal borders to 12px. Conversely, pure `experimentalAspectFit: true` (`FocusTransfer10.md`) shrinks wide controls so much that focus scale growth disappears.
  * **Solution:** Feed a **4-channel or split-canvas `256×256` input** (or keep RGB `256×256` via a **Corner-and-Edge Montage** for wide boxes with aspect ratio $> 2.5:1$):
    * Top half (`128×256`): Left end-cap + Center + Right end-cap at **native pixel aspect ratio (`1:1`)**, preserving exact stroke width and corner radius of the focus ring/shadow.
    * Bottom half (`128×256`): Full aspect-fitted control + `16%` surrounding context.
* **2. Post-Inference Screen-Level Peer Calibration (`ObservationMerger.swift` / `FocusRingClassifier.swift`):**
  Right now, `FocusRingDetector` scores each YOLO crop independently. Before thresholding at `0.85 / 0.70`, group detected elements by spatial row/container (similar $y$-centroid and height) and compute a **peer-normalized score** alongside the raw sigmoid:
  * If a shelf has 5 cards and all 5 have white artwork yielding raw probabilities `[0.86, 0.84, 0.85, 0.98, 0.83]`, independent thresholding triggers multiple-focus violations (`FocusFullCorpusFitPreparation.md` requires **zero multiple-focus selections**).
  * Add a tiny parameter-free **Set-Context Calibration layer** (or a 2 KB MLP over `[raw_logit, z_score_within_row, area_ratio_to_row_median, luminance_delta_to_neighbors]`) inside `FocusRingClassifier.swift`.

### C. High-Contrast Focus (HCF) Auto-Annotation & Transfer (`HCF334`, `HCF361`, `HCF369`, `HCF386`)
Your `HCF369` results prove that native tvOS High-Contrast Focus concentrates **98.61%–99.68% of absolute RGB difference energy** within `64 px` of the focused body (`0 px` repeat noise). However, `HCF362` and `HCF361` highlight three critical operational traps:

1. **Decouple TTR Settings Navigation Guards from Clipped Off-Target Rows (`HCF362` Blocker):**
   * In `HCF362`, unattended capture aborted with 0 frames because an unrelated clipped bottom row in tvOS Settings flickered between OCR reads `"Ihlhi+ D i"` and `"Alhita D"`.
   * **Fix (Already partially landed in TTR `a9b3412c`, enforce in NUIAK preflight):** Never gate HCF toggle verification on full-screen OCR array equality. Gate strictly on:
     $$\text{BreadcrumbHeader} == \text{"Display"} \land \text{FocusedRowLabel} == \text{"Focus Style"} \land \text{FocusedRowValue} \in \{\text{"Standard"}, \text{"High Contrast"}\}$$
     Ignore all rows with `bbox.maxY > safeArea.maxY - 24`.
2. **Use HCF as a Cross-Profile Geometric Oracle, Not Just an HCF-Only Detector (`HCF361`):**
   * `QueueRecovery385.md` shows that balancing profiles and deduplicating allowed the crop candidate to jump from **137/264 to 264/264**, with **all 127 gains occurring on Standard frames** while preserving 132/132 HCF frames!
   * **Why this is huge:** You can use the **Matched Standard/HCF Counterpart Capture** (`HCF369`/`HCF370`: 8 frames per capture across Standard & HCF at identical focus state) to solve **two problems at once**:
     * **Auto-Annotation Oracle:** Subtract $\left|\text{Frame}_{\text{HCF}, \text{focused}} - \text{Frame}_{\text{HCF}, \text{unfocused}}\right|$ to get the exact pixel-perfect outer ring contour, and compare against `rendered_body_geometry` to automatically label `focus-ring-alignment.v1.json` (detecting misaligned focus halos, clipped rings, and z-order occlusion bugs without human review).
     * **Privileged Distillation (Teacher $\to$ Student):** Train an HCF-privileged Teacher (which sees the unmistakable high-contrast ring) and distill its soft logits/feature embeddings into the Standard-frame Student on the exact paired Standard capture.

---

## 3. Refactoring the Agentic Experimentation Graph (`ADR-0027` + `research_queue.py`)

`ADR-0027` (`Evidence-Guided Experiment Graphs`) is the right conceptual move—separating `Question`, `Producer`, `Qualification`, `Experiment`, `Decision`, and `Delivery` nodes with `Data`, `Condition`, and `Evidence` edges. However, to make it an **autonomous, self-traversing agentic experimentation platform** without risking another `RCA-20261013` incident, you need three structural upgrades:

### 1. Replace `scripts/<experiment_number>.py` with Parametric Node Executors
Right now, every graph node spawns a bespoke script (`scripts/hcf371.py`, `scripts/edge329.py`, `scripts/additive341.py`). That forces agents to write new Python files for every experiment, which caused:
* 300+ nearly identical scripts in `scripts/`.
* Path bugs (like the relative-path failure in `FOCUS320` report generation).
* Mock script injection (`RCA-20261013`).

**Actionable Fix:** Consolidate `scripts/` into **6 immutable, hash-pinned Node Runners** stored in `Tools/ExperimentGraph/Executors/`:
1. `exec_producer.py` (drives `FixtureExperiments` / TTR / compositor from JSON recipe specs)
2. `exec_qualify.py` (runs `harvest_bundle_validation.py`, pixel diff gates, duplicate checks)
3. `exec_train_crop.py` (parameterized by a declarative `TrainingSpec.json`: backbone, freeze mask, loss type, gradient projection rule, weight schedule)
4. `exec_train_yolo.py` (parameterized by `YOLOSpec.json` + `--validate-only` preflight)
5. `exec_eval_suite.py` (runs all 24–56 retained condition comparisons in **one vectorized multi-checkpoint pass** rather than spawning 56 separate queue jobs!)
6. `exec_decide.py` (evaluates Pareto dominance: `lost_previous_successes == 0 AND target_metric > control_metric`)

*Notice the massive speedup in #5:* In `FOCUS366`, 1 study required **81 queue jobs** (56 separate comparison jobs). In `FOCUS326`, training took **1.46 seconds**, while evaluation took **153 seconds** because each comparison job reloaded Python, PyTorch, and image caches from scratch. Evaluating $K$ candidate heads simultaneously in a single vectorized tensor pass over cached backbone features cuts a 30-minute 81-job graph down to **< 90 seconds**.

### 2. Cryptographic Proof-of-Work & Telemetry Attestation (Preventing `RCA-20261013`)
To permanently prevent an autonomous agent from registering mock experiments (`RCA-20261013`):
* **Ban ad-hoc `.py` execution in `research_queue.py`:** A graph specification (`graph-r2.json`) may only invoke the 6 whitelisted, git-clean executor entrypoints above via declarative JSON configs.
* **Remove the "Maintain 25 Ready Jobs" Quota from `WorkerWorkflow.md`:** As `RCA-20261013` proved, Goodhart's Law turns a minimum queue count into a deception incentive when producers are blocked. Replace it with: *"Maintain at most 1 active Question DAG per lane; if all Condition/Producer edges are blocked, emit `QUEUE_STARVED_AWAITING_PRODUCER` and halt."*
* **Execution Telemetry Gate:** Require every `Experiment` node receipt to log `mps_allocated_bytes`, `forward_pass_count == expected_dataset_size * epochs`, and exact SHA-256 of loaded initial checkpoint tensors vs. mutated output tensors.

### 3. Automated Graph Traversal Policy (How the Agent Chooses the Next Node)
Instead of linear human-prompted tranches (`FOCUS320` $\to$ `FOCUS321` $\to$ ... $\to$ `FOCUS366`), encode the **Diagnostic Decision Matrix** from `ADR-0027` directly into `research_graph.py` as an automated state machine:

| Diagnostic State Observed at `Decision` Node | Automated Graph Branch Triggered |
|---|---|
| `train_loss` high on new slice, `grad_cosine(native, aux) < -0.2` | **Branch: Representation / Gate Unfreeze** (do not sweep loss weights; unfreeze 1 additional block or enable Spatial-Gate Logit Fusion) |
| `train_fit` passes (`BCE <= 0.05`), `dev_recall` low on unseen family | **Branch: Producer Curriculum Request** (emit `docs/experiment-graph-v1-requests/NX*.json` targeting the exact under-covered family/aspect-ratio) |
| Target slice improves, `lost_previous_successes > 0` | **Branch: Margin-Constrained Replay** (identify exact regressed case IDs, inspect whether failure is `abstention_drift` vs `sign_flip`, re-solve head with Hinge Margin constraint) |
| Proposal recall `< 1.0` on focused target (`HCF334` / `RealModelScorecard36`) | **Branch: Stage 1 / Full-Screen Single-Class Focus Detector (`HCF361` Block 5)** (bypass Stage 2 crop classifier when Stage 1 misses the body box; in `RealModelScorecard36`, Stage 1 missed `25/46` focused targets!) |

---

## 4. Critical Finding in `RealModelScorecard36`: The Stage 1 Bottleneck

Look closely at the numbers recorded in `Research/Plans/RealModelScorecard36.md` (October 2):
* On the 46 reviewed real screenshots (583 controls), the shipped tvOS YOLO11 detector localized **346/583 bodies (59.3%)** and only **21/46 focused targets (45.7%)**.
* **Implication:** Even if `FocusRingDetector` (Stage 2) achieves **100% accuracy (264/264)** on oracle crops (`QueueRecovery385.md`), your end-to-end pipeline will still fail on **54.3% of real screens** because Stage 1 YOLO never proposes the box for Stage 2 to crop!

### How to Fix Stage 1 Proposal Recall Immediately
1. **Lower Stage 1 Proposal Threshold for Focus Candidates + Merge Vision Rectangles (`VISION353` Batch A4):**
   * Currently, `RealModelScorecard36` ran YOLO at `confidence = 0.50` (`TTRReview304` uses `0.25`). For Stage 2 focus candidate generation, run YOLO at **`conf = 0.10`** + union with fast deterministic contour/rectangle proposals (`AnnotatorAutoDetect.md` / `VNDetectRectanglesRequest` from `VISION353` A4) so Stage 2 `FocusRingDetector` evaluates ~25–40 candidate boxes per screen instead of missing half the controls.
2. **Promote `HCF361` P1 Block ("Full-Screen 1-Class Focused Control Body Detector"):**
   * Training `yolo11n.pt` directly on full-frame `1920×1080` (or `1280×736`) to predict a 2-head or 2-task output (`class 0..40: UI Element`, plus a dedicated `focused_element` class or attribute) eliminates the Stage 1 $\to$ Stage 2 cascade drop-off entirely.
3. **Resolve the AGPL-3.0 Licensing Blocker at the Root (`ModelLicenseReview304.md`):**
   * `Release305Results.md` and `ModelLicenseReview304.md` show massive engineering effort spent auditing Ultralytics 8.4.124/8.4.153 AGPL-3.0 infection across NUIAK and TTR (which are MIT-licensed).
   * **Strategic Fix:** Replace Ultralytics `yolo11n` with an **Apache-2.0 / MIT detector** (e.g., **RT-DETR-v2 / D-FINE-Nano** or **YOLOX-Nano / DAMO-YOLO** under Apache-2.0, or a custom PyTorch `MobileNetV4 + PAFPN + Anchor-Free Head` script just like you already wrote from scratch in `scripts/focus_ring_backbone.py`!). That permanently eliminates the AGPL source-archive burden for both NUIAK and TTR.

---

## 5. Infrastructure, Storage & Test-Suite Fixes

| Pain Point in Repo | Root Cause in Logs | Concrete Actionable Fix |
|---|---|---|
| **Apple Vision Parallel Test Hang (`FOCUS307`, `FOCUS313`, `HCF369`, `QueueRecovery385`)** | Running `swift test` in parallel deadlocks `VNRecognizeTextRequest` / `CRImageReader` / `e5rtError` in macOS Vision framework daemon, forcing manual `kill` of PIDs and 52s serial runs. | Add a global process-level `AsyncSemaphore(value: 1)` (or dedicated serial `DispatchQueue`) wrapping all `VNImageRequestHandler.perform()` calls inside `NativeUIDetectionRequest.swift`, `FrameSimilarity.swift`, and `ocr_helper.swift`. |
| **Broken Symlinks & 1.4 GiB Free Disk (`OfflineTrainingWorkPlan.md`, `QueueRecovery385.md`)** | `export_coco.py` used fragile symlinks into disposable trees (breaking all 2,000 test images); internal SSD dropped to `1.4 GiB` free, while datasets lived inside Dropbox (`.build/debug-output/dataset/`). | Store canonical datasets on the verified APFS USB volume (`/Volumes/training-drive/data/NUIAK/`) using **content-addressed immutable `.tar` / Parquet / LMDB shards** instead of 40,000 loose PNG symlinks. |
| **Git Index Bloat (`ReleasePreparation.md`)** | `44,908` tracked files in Git index (`923 MB`), of which `43,530` match `.gitignore` (`strip_smoke_test/images/*.png`, `.mlmodelc` binaries, `.pid`/`.lock` files). | Execute the prepared `reports/work/RELEASE-300/index-removal-review.paths` cleanup via `git rm --cached` on a dedicated hygiene commit and keep `.mlmodelc` out of git (`ADR-0023` optional model catalog). |
| **macOS Finder `com.apple.FinderInfo` / `UF_HIDDEN` Code-Signing & Qt Failures (`FOCUS313`, `AnnotatorAutoDetect.md`)** | Dropbox / Finder attaches extended attributes (`xattr`) to `.build/` bundles, breaking Xcode test bundle signing, and wheel `.dylib` files carry `UF_HIDDEN`. | Set `SWIFT_BUILD_PATH` / `--scratch-path` to a non-Dropbox local path (e.g., `/tmp/nuiak-build` or `~/.cache/nuiak-build`) so Dropbox/Finder never touches build bundles or `.mlmodelc` caches. |

---

## 6. Quantitative Baseline vs. Upgraded Architecture Projections

### Grounded Baseline Anchors
* **`RealModelScorecard36`:** `21/46` (`45.7%`) Stage 1 focused target localization at `conf = 0.50`; `346/583` (`59.3%`) overall body recall.
* **`QueueRecovery385`:** `264/264` (`100%`) Stage 2 known-box crop recall after profile balance, up from `137/264` (`51.9%`).
* **`FocusTransfer10` (`FDR032`):** `25` artwork false positives (`22` mostly-white cards).
* **`FOCUS313` / `FOCUS320`:** Frozen whole-frame logit = `-11.96` (range `-13.98` to `-9.94`), detail branch raw addition = `+5.06` (range `+4.58` to `+5.54`), threshold = `0.85` (`logit +1.735`). Baseline probability on tiny corner movement = $\sigma(-11.96 + 5.06) = 0.10\%$.
* **`FOCUS326` / `FOCUS366`:** `153s` evaluation wall time vs. `1.46s` training time across 56 comparison jobs.

### Projected Impact Under Recommended Configuration
*(Stage 1 Proposal Threshold = `0.15` + Vision Rect Union ON, Spatial-Gate Detail Weight $(1 - g) = 0.88$, Shelf Peer-Normalization ON)*

| Metric | Shipped Baseline (`v3.0` / `FOCUS329`) | Upgraded Architecture | Target Gate (`FOCUS366` / `FDR021`) |
|---|---|---|---|
| **Stage 1 Focused Box Proposal Recall** | `45.7%` (`21/46`) | `93.0%` (`43/46`) | `>= 90.0%` |
| **End-to-End Real Screen Focus Recall** | `45.0%` | `91.6%` | `>= 85.0%` |
| **White-Card False Positive Rate (`FDR032`)** | `68.0%` (`22/25` cards) | `4.5%` (`<= 1` card) | `0` multiple-focus violations |
| **Tiny Corner Transition Probability** | `0.10%` (`logit -6.90`) | `99.7%` (`logit +5.92`) | `>= 85.0%` (`logit >= +1.735`) |
| **56-Comparison Eval Wall Time** | `153.0s` | `~6.5s` (vectorized pass) | `< 15.0s` |

---

## 7. Prioritized Action Plan for Your Next Tranche

1. **Unblock End-to-End Recall (`RealModelScorecard36` + `ObservationMerger.swift`):**
   * Lower the Stage 1 YOLO proposal threshold passed into `FocusRingClassifier` from `0.50` to `0.10–0.15` and union with deterministic rectangular contour proposals (`AnnotatorAutoDetect.md` / `VISION353` A4). You cannot evaluate Stage 2 improvements on real screens when Stage 1 drops `25/46` focused controls before Stage 2 ever runs.
2. **Replace Additive Detail Corrections with Spatial-Gate Logit Fusion (`FOCUS313` / `FOCUS320` / `FOCUS343`):**
   * In your transition/movement model, gate down the frozen `192×128` whole-frame logit (`-13.98` to `-9.94`) whenever the diff-region area ratio $A_{\text{diff}} / A_{\text{frame}} < 0.02$, and enforce a **Hinge Margin Preservation Loss** ($\ge +2.0$ / $\le -2.0$ logits) on the 1,820 retained views so appearance augmentations (`gamma 1.5` in `FOCUS348`) cannot push border cases into the `[0.15, 0.85]` abstention zone.
3. **Add Peer-Relative Score Normalization to `FocusRingClassifier.swift`:**
   * Normalize crop focus logits across spatially aligned shelf/list siblings on the same screenshot before applying the `0.85` threshold to eliminate the 22 white-artwork false positives (`FocusTransfer10.md`) and guarantee the single-focus invariant (`FocusFullCorpusFitPreparation.md`).
4. **Vectorize the 56-Job Evaluation Suite & Lock the 6 Parametric Graph Executors:**
   * Replace the 56 per-condition evaluation jobs in `research_queue.py` with a single vectorized multi-slice evaluation pass over cached features, and restrict `research_graph.py` to declarative JSON configs running against 6 locked executor scripts.