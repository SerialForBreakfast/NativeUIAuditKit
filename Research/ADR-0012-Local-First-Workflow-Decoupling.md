# ADR-0012: Local-First Workflow Decoupling and Governance Streamlining

- Date: 2026-09-30
- Status: Proposed / Active
- Scope: Development workflow, multi-rig integration boundaries, and agent operational protocol across NativeUIAuditKit.
- Relates to: [ADR-0006](ADR-0006-Training-Iteration-Efficiency.md), [ADR-0011](ADR-0011-Measured-Training-Efficiency.md), [WorkerWorkflow](../Research/WorkerWorkflow.md).

---

## 1. Context and Problem Statement

NativeUIAuditKit has experienced severe operational stagnation. Analysis of the project trajectory and recent execution logs reveals two primary systemic causes:

1. **Synchronous External Rig and Network Coupling:**
   Development progress has become tightly coupled to external hardware, network mounts, and peer repositories (`TVTestRig`, `Sillycon`, SMB share `/Volumes/SharedStatusFile`, external disk mounts, and live tvOS Simulators). Tasks regularly stall waiting for peer repository builds, status YAML receipts, file permission errors, or network socket drops. An issue in a peer process halts local ML engineering.

2. **Administrative and Procedural Hypertrophy:**
   To guard against past mistakes, successive layers of defensive protocol were instituted: plan file SHA256 verification, per-file transfer receipts, strict packet isolation, manual multi-step admission preflights, and extensive multi-page handoff documents for microscopic changes (such as adjusting 58 dataset crops or evaluating 4 image frames). AI agents and human contributors now spend 80–90% of their operational budget and context tokens producing administrative compliance artifacts rather than advancing models or shipping code.

This has resulted in "process gridlock": iteration velocity slowed, prompting more defensive process, which slowed velocity further.

---

## 2. Decision Drivers

- **Local Autonomy:** NativeUIAuditKit must be completely buildable, testable, and trainable offline on a single Apple Silicon macOS workstation.
- **Asynchronous Integration:** Peer tools (such as TVTestRig) are valuable data sources and test consumers, but must never be blocking prerequisites for local development.
- **Outcome-Driven Verification:** Verification should be established by passing automated test suites, deterministic evaluation benchmarks, and clean git history—not by extensive manual handoff documentation and hash bookkeeping.
- **Context Efficiency for AI Agents:** Agents must spend their tokens reading code, executing tests, running training benchmarks, and diagnosing failures.

---

## 3. Considered Options

- **Option A (Status Quo):** Maintain multi-rig synchronous coordination via SMB status files, strict packet handoff protocols, and plan SHA256 tracking.
- **Option B (Complete Severance):** Permanently remove TVTestRig integration, delete all coordination code, and abandon hardware validation.
- **Option C (Local-First Decoupling with Asynchronous Ingestion — Selected):** Decouple local development from external hardware. Local synthetic generation, local dataset caching, and offline training become the primary loop. External data from TVTestRig or shared drives is treated as asynchronous batch ingestion. Operational paperwork (handoffs, status YAMLs) is condensed into standard automated test runs, git commits, and benchmark logs.

---

## 4. Decision

We adopt **Option C: Local-First Decoupling with Streamlined Governance**.

### 4.1 Local-First Architecture
1. **Self-Contained Offline Execution:** All primary workflows (model training, evaluation, export, synthetic dataset generation, and CLI scanning) must run completely offline without network mounts, SMB shares, or running peer daemons.
2. **Asynchronous Ingestion Boundary:** Datasets and capture archives from TVTestRig are ingested via versioned, project-local snapshots. Ingestion is decoupled from the training schedule. If the shared mount or peer is unavailable, local work continues unhindered.
3. **Standing Simulator Authority:** Local headless Simulator and offscreen rendering test harnesses are the default development environment; physical device testing is an explicit downstream release stage.

### 4.2 Streamlined Governance
1. **Elimination of Procedural Bureaucracy:** Cease requiring SHA256 hashes of plan text files, per-crop admission preflights, and redundant packet handoff dossiers for routine code and data iterations.
2. **Source of Truth:** Verification is anchored in:
   - `swift test` and Python `pytest` passes.
   - Pinned benchmark results logged to `Research/ExperimentLog.md`.
   - Concise commit descriptions and living snapshot updates in `Research/CurrentState.md`.
3. **Chunk Sizing:** Allow agents to execute meaningful, coherent tranches end-to-end (e.g., implementing an entire CLI subcommand or running a full model evaluation) rather than pausing at arbitrary micro-boundaries to file intermediate status packets.

---

## 5. Consequences

### Positive
- **Velocity Recovery:** Eliminates multi-day gridlock caused by external mount failures, socket timeouts, and peer build lag.
- **Token and Compute Efficiency:** Frees up agent context for core software engineering, data analysis, and model optimization.
- **Reproducibility:** Self-contained local datasets and offline scripts ensure that any contributor or CI pipeline can reproduce results anywhere.

### Negative / Tradeoffs
- **Batch Lag on Real Hardware:** Ingesting TVTestRig data asynchronously means real-world hardware edge cases are discovered during scheduled batch intake rather than in real time.
- **Discipline Required:** Moving away from rigid micro-handoffs requires maintaining strict code cleanliness, clear git commits, and comprehensive automated test suites.
