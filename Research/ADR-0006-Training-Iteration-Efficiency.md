# ADR-0006: Training Iteration Efficiency on Apple Silicon (MPS)

- **Status:** Approved for Run 009+ (Run 008 baseline preserved)
- **Date:** 2026-08-29
- **Deciders:** NativeUIAuditKit Architecture & ML Engineering
- **Applies to:** Phase 6a (41-class YOLO11m), Dataset Pipeline, Apple Silicon Training Host (Mac Mini M4)
- **Related:**
  - [`Research/BestPractices.md`](BestPractices.md) (BP-25 through BP-35)
  - [`Research/ExperimentLog.md`](ExperimentLog.md) (Run 007, Run 008)
  - [`Research/TrainingRunbook.md`](TrainingRunbook.md)
  - [`Research/NativeUIElementDetection.md`](NativeUIElementDetection.md)

---

## 1. Context & Problem Statement

Phase 6a expands the NativeUIAuditKit detector from a 5-class prototype to the full 41-class native Apple UI taxonomy using YOLO11m on Apple Silicon (Metal Performance Shaders / MPS backend).

A typical full training run spans 100 epochs (with patience-15 early stopping) across ~12,000–20,000 annotated screenshots. On the dedicated host machine (Mac Mini M4), full training cycles (such as Run 007) require **24 to 40 hours of continuous wall-clock time**.

While foundational MPS stability has been established (automatic mixed precision AMP, rectangular batching `rect=True`, single-process training, `caffeinate` keep-alive, and power-loss resume watchdog), several operational and I/O bottlenecks constrain iteration velocity:
1. **Excessive checkpoint serialization** writes ~154 MB every epoch (~29 min), causing unnecessary flash wear and I/O thrash.
2. **CPU-bound per-epoch metric plotting** generates 41-class confusion matrices and PR curves on every validation step.
3. **Conservative batch sizing** (`batch=4`, utilizing only ~4.6 GB of unified memory) leaves GPU compute units under-occupied on machines with 24 GB or 32 GB RAM.
4. **Host memory contention** from background processes (e.g., booted iOS Simulators and Xcode instances holding several gigabytes of unified memory).
5. **Filesystem stalls** when tools traverse flat directories containing tens of thousands of images (e.g. `dataset/dataset/train`).

### Invariant Constraint: Run 008 Integrity
**Run 008 must NOT be altered while active.** Run 008 is an ablation on dataset regeneration and chrome coverage against Run 007. Maintaining an identical training configuration between Run 007 and Run 008 is required for scientific validity. All changes decided in this ADR apply to **subsequent runs (Run 009+)** and immediate **host machine hygiene**.

---

## 2. Decision Drivers

- **Iteration Velocity:** Reduce training turnaround time from ~24–36 hours down to ~12–18 hours per full run.
- **Hardware Architecture Alignment:** Maximize Apple Silicon unified memory bandwidth and GPU compute utilization without triggering swap or thermal throttling.
- **Scientific & Metric Integrity:** Preserve exact mAP@0.5 evaluation semantics, OHEM hard-example oversampling, mosaic augmentation, and early-stopping validation fidelity.
- **Filesystem & Process Safety:** Prevent APFS directory lockups, out-of-disk failures, and MPS context contention (`errno 11`).

---

## 3. Evaluated Dimensions & Options

| Dimension | Baseline (Run 007 / 008) | Option A | Option B | Selected Decision |
|---|---|---|---|---|
| **Checkpoint I/O** | `save_period=1` (writes ~154MB every epoch, ~15GB/run) | `save_period=5` (snapshot every 5 epochs) | `save_period=-1` (save only `last.pt` & `best.pt`) | **`save_period=-1`** (with `last.prev.pt` backup) |
| **Metric Plots** | `plots=True` (generates 41x41 confusion matrices & curves every epoch) | `plots=False` during train; generate on eval | `plots=True` with downsampled classes | **`plots=False`** (rely on `results.csv` during train) |
| **Batch Size** | `batch=4` (~4.6 GB memory) | `batch=8` (scaled `lr0`) | AutoBatch (`--batch -1`) | **`batch=8` on ≥24GB RAM** (AutoBatch fallback) |
| **Host Memory** | Simulator booted / Xcode open in background | Quit Simulator app & idle Xcode | `simctl shutdown all` | **Quit Simulator & idle tools** |
| **Dataset Access** | Directory globbing (`Path.glob("*")`) | Text file manifests (`train.txt`, `val.txt`) | Database/SQLite indexing | **Text file manifests (`train.txt`)** |
| **MPS Concurrency**| Single process | Concurrent eval/train | Background CoreML export | **Strict Single-Process Exclusivity** |
| **Dataset Caching**| `cache=False` (stream from disk) | `cache=ram` (load all images to RAM) | `cache=disk` | **`cache=False`** (prevent swap blowup) |
| **Worker Threads** | `workers=4` | `workers=8` | `workers=2` | **`workers=4`** (optimal for MPS IPC) |
| **Model Family** | YOLO11m (41-class capacity) | YOLO11n (faster, lower capacity) | YOLO11s | **Maintain YOLO11m** for 41-class gate |

---

## 4. Decisions

### D1: Eliminate Per-Epoch Snapshot I/O Churn (`save_period=-1`)
- **Decision:** Set `save_period=-1` (or `--save-period -1`) for Run 009+.
- **Rationale:** Writing full optimizer and model weights (~154 MB) every epoch consumes ~15.4 GB of disk writes per 100 epochs. Intermediate epoch checkpoints (`epoch45.pt`, etc.) provide zero accuracy benefit and risk filling ephemeral disk volumes. Ultralytics automatically maintains `best.pt` and `last.pt`.
- **Resilience Strategy:** The in-package `on_model_save` callback will continue to mirror `last.pt` to `last.prev.pt` to guarantee recovery against power interruption during a write (BP-30).

### D2: Disable Per-Epoch Visual Metric Plotting (`plots=False`)
- **Decision:** Pass `plots=False` to `model.train()` for all production runs.
- **Rationale:** Rendering 41-class confusion matrices, precision-recall curves, and validation batch mosaic PNGs on CPU at every epoch boundary adds cumulative minutes of compute and file I/O. All loss, precision, recall, and mAP metrics are already tracked numerically in `results.csv`.
- **Evaluation Rule:** Visual curves and confusion matrices will be generated once at the completion of training or during dedicated evaluation via `scripts/eval_yolo_map.py` / `scripts/eval_map.swift`.

### D3: Increase Batch Size on Unified Memory ≥24 GB (`batch=8` / AutoBatch)
- **Decision:** 
  - On 16 GB machines: maintain `batch=4` (~4.6 GB working set).
  - On ≥24 GB / 32 GB machines (e.g. M4 Mac Mini 24GB+): increase default batch size to `batch=8` (estimated ~8–9 GB working set).
  - When batch size is doubled (`4 → 8`), scale initial learning rate `lr0` according to linear scaling rules (or verify Ultralytics internal scaling).
  - Enable `--batch -1` (AutoBatch) in `train_ios_model.py` for automated hardware profiling when transitioning across devices.
- **Rationale:** Increasing batch size from 4 to 8 improves tensor core utilization on Apple Silicon MPS, amortizes kernel dispatch overhead, and reduces per-epoch step counts by 50%, targeting a 20–35% reduction in total wall-clock duration.

### D4: Host Memory Hygiene & Simulator Lifecycle
- **Decision:** Always quit the `Simulator.app` and close idle Xcode instances prior to launching long-running training or dataset generation.
- **Rationale:** Booted simulator runtimes (`com.apple.CoreSimulator.CoreSimulatorDevice`) reserve 3–6 GB of unified memory. Because Apple Silicon shares memory between CPU and GPU, reclaimable host memory directly prevents GPU allocation throttling and swap usage.
- **Guardrail:** Do not execute destructive commands such as `xcrun simctl erase` or `shutdown all` without explicit contributor request; simply quitting the Simulator application is sufficient.

### D5: Strict Line-Delimited File Lists for Dataset Operations
- **Decision:** Mandate text file manifests (`train.txt`, `val.txt`, `test.txt`) for all dataset ingestion, class-weight calculation, and YOLO training pipelines. Prohibit calls to `os.listdir()`, `Path.glob()`, or `iterdir()` on large flat directories such as `dataset/dataset/train`.
- **Rationale:** Flat APFS directories containing >10,000 files suffer severe directory-enumeration stalls on macOS, causing scripts to hang indefinitely before processing begins. Pre-indexing into plain text manifests eliminates directory scanning latency completely.

### D6: Enforce Strict Single-Process Serialization on MPS
- **Decision:** Prohibit parallel or background ML tasks (such as simultaneous Core ML exports, validation scripts, or secondary training dry-runs) while an MPS training run is active.
- **Rationale:** Metal Performance Shaders lacks CUDA-grade memory preemption. Concurrent Metal device allocations trigger `MPS backend out of memory` / `errno 11` crashes and GPU watchdog faults.

### D7: Rejection of Counterproductive Optimizations
1. **Reject `cache=ram`:** Pre-loading 12,000–20,000 uncompressed UI images into unified memory exceeds 12–16 GB, causing severe swap paging. Keep `cache=False` (or `cache='disk'`).
2. **Reject `workers > 4`:** Increasing dataloader workers on macOS introduces Python multiprocessing IPC overhead across Darwin Mach ports without improving GPU feeding. Maintain `workers=4`.
3. **Reject Disabling OHEM or Mosaic:** OHEM (Online Hard Example Mining) and Mosaic augmentations are critical to achieving the DS-G8 generalization target on 41 native UI classes. They must not be sacrificed for speed.
4. **Reject `torch.compile` on MPS:** `compile=False` remains mandatory. PyTorch MPS graph capture does not yet deliver stable performance gains on Apple Silicon.
5. **Reject Downgrading to YOLO11n:** YOLO11n is insufficient for 41-class detection across dense UI layouts; capacity requires YOLO11m.

---

## 5. Machine Hygiene & Operational Checklist

Before starting any post-Run 008 training run on the Mac Mini:
- [ ] **Quit Simulator & Xcode:** `osascript -e 'quit app "Simulator"'`
- [ ] **Verify Disk Space:** Confirm `> 50 GB` available on `/System/Volumes/Data`.
- [ ] **Check Thermals & Power:** Verify Mac Mini has unobstructed airflow; confirm Low Power Mode is disabled in System Settings.
- [ ] **Ensure Process Exclusivity:** `ps aux | grep python | grep train` confirms no other training/eval process is active.
- [ ] **Activate Keep-Alive:** Run under `caffeinate -dimsu` or via `scripts/watch_phase6a.py`.

---

## 6. Consequences & Trade-offs

### Positive
- **30–45% Faster Turnaround:** Combining `batch=8`, eliminating per-epoch plotting, and removing `save_period=1` write cycles reduces expected 100-epoch training time from ~28–32 hours to ~16–19 hours on M4 hardware.
- **Zero Flash I/O Churn:** Eliminates >14 GB of ephemeral checkpoint writes per run, protecting SSD endurance and preventing disk-exhaustion crashes.
- **Reliable Automation:** File-list dataset ingestion prevents APFS filesystem hangs.

### Negative & Mitigations
- **No Intermediate Checkpoint History:** If early epochs need inspection, intermediate weights (`epochN.pt`) will not exist.
  - *Mitigation:* `last.pt`, `last.prev.pt`, and `best.pt` provide complete recovery and optimal weights. Full numerical logs are recorded in `results.csv`.
- **Delayed Visual Inspection:** Curves and confusion matrices are not updated live in the run directory.
  - *Mitigation:* `results.csv` gives instant numerical progress; post-run `eval_yolo_map.py` renders complete visualization in seconds.
