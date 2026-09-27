# Training efficiency: audit, measure, then adopt

Canonical contracts for TRAIN-EFF-A/B/C. [ADR-0011](../ADR-0011-Measured-Training-Efficiency.md)
records rationale; [Tasks](../../Tasks.md) alone records state and ownership.
This plan authorizes no training, pause/resume, profiling, simulator or external action.

## Integrated delivery and common boundaries

The deliverable is a reproducible effective-configuration audit, a bounded measured
throughput comparison, and an evidence-backed configuration/adoption decision—not
three isolated helpers. Complete each assigned packet through real entrypoint
integration, failure tests and handoff. A+B can be one substantial assignment only
when an exclusive compute window and benchmark execution are explicitly approved.
Until then, A is independently useful and does not block FocusRing software work.

Read the model-workflow skill, WorkerWorkflow, ADR-0011, the relevant ExperimentLog
entry, current trainer/OHEM code and existing preflight tests. Inspect ownership and
dirty files before editing. Use current interfaces rather than copying historical
commands. `--dry-run` performs training; it is not a planning command.

Inputs must identify source revision plus dirty-source hashes, interpreter/dependency
versions, model/checkpoint/category-map hashes, data manifest/splits, settings and
metric implementation. Never overwrite an active run, its source corpus, caches or
checkpoint files. Do not copy a checkpoint while its writer may be replacing it;
use an owner-designated immutable snapshot after a safe boundary.

Evidence goes to project-local `reports/work/TRAIN-EFF-<letter>/`; bulky logs,
profiles and weights use new gitignored `NativeUITrainer/` experiment destinations
under ArtifactRetention. Commit only concise summaries and reference hashes, by the
maintainer. Set all tool caches/temporary output project-local before imports. No
dependency upgrades/downloads, git writes, TTR operations or SMB status noise.

Every handoff includes acceptance-to-evidence mapping, commands/exits, hashes,
elapsed implementation/test/compute/wait time, preserved pre-existing edits,
remaining blockers, and next unblocked assignment. Report software, data, integration
and model outcomes separately; benchmark success is not a model-quality gate.

## TRAIN-EFF-A

### Outcome and inputs

An integrated read-only run auditor and offline-tested benchmark specification that
make the next execution decision possible. Start from Run 013 logs, saved arguments,
CSV, installed source and trainer/OHEM callbacks—not a fresh model load. The audit
must distinguish saved intent, source-derived behavior and runtime-confirmed facts.

### Authority and implementation

1. Reconcile the live interpreter/build when permitted using read-only metadata;
   retain denied/unknown facts explicitly. Pin source hashes without importing Torch
   or initializing MPS. Read append-only logs as a timestamped snapshot; do not hash
   a changing log as though it were immutable experiment evidence.
2. Generate a versioned effective-configuration report: initialization/resume mode,
   corpus counts and coverage, actual image shapes, workers, AMP, rect/mosaic,
   optimizer, accumulation/effective batch, warmup, stopping fitness and checkpoint
   cadence. Unobserved effective values remain inferred/unknown with source evidence.
3. Reconcile generic versus UI initialization and augmentation intent with the run
   owner. Do not reinterpret unrecorded departures as approval or failure. Check r7
   split/coverage claims against manifests without repeatedly decoding the corpus.
4. Audit OHEM batch-loss proxy, synchronization, cache invalidation, labels/image
   alignment and rectangular-batch metadata after replacement. Audit last/best/mirror
   recovery semantics. Separate confirmed behavior from hypotheses and proposed fixes.
5. Implement an offline planning/reporting entrypoint and benchmark configuration
   contract around the existing trainer. Reuse existing preflight and callback seams;
   do not build another trainer. New tooling must default to no model imports or
   mutation. Defer changes to files owned by the active training worker until release.
6. Freeze a small training-only benchmark membership and proposed B matrix, including
   memory/headroom, timing boundaries, output paths, compute budget and stop behavior.
   Record exact future commands from implemented interfaces, not speculative flags.

### Verification and acceptance

Test actual planning/report CLI with saved-config overrides, missing/truncated logs,
unknown version/runtime, missing fields, bad hashes, output collisions and prohibited
model imports. Deterministic callback fixtures exercise batch-proxy accounting,
rectangular replacement and cache lifetime; tests must use the real callback seam,
not a reimplementation. Any confirmed correctness defect gets a bounded repair
proposal before benchmarking; do not silently patch the running experiment.

Accept when the audit reconciles or explicitly marks every listed setting unknown,
the real offline entrypoint passes tests, and B has an executable frozen proposal.
For code changes run focused tests then one integrated offline `swift build` and
`swift test`; documentation-only review does not require these expensive checks.
Runtime verification may remain blocked while software is verified.

**Blocker/resume:** conflicting file ownership blocks only overlapping edits; missing
process access blocks runtime confirmation, not source audit. GPU work awaits B's
authorization and exclusive window. **Next:** review B matrix and approve that window.

## TRAIN-EFF-B

### Outcome, prerequisites and authority

A measured performance recommendation with confidence/variance and stage-cost
evidence. Requires accepted A contract, resolved correctness risks, explicit bounded
benchmark authorization and confirmed exclusive MPS access. The run owner must finish
or separately approve a safe pause; this packet cannot interrupt Run 013 itself.
Use immutable local weights and A's training-only membership. Log benchmark runs
before execution; allocate IDs under the existing experiment convention at launch.

### Implementation and execution

1. Freeze at most six configurations and a maximum 90-minute wall-clock budget,
   including setup/profiling. Start with batch 8 control, then 16 and optionally 32
   if memory headroom permits. Keep architecture, 640 resolution, data ordering,
   initialization and augmentations fixed. Record unavoidable shape differences.
2. For each configuration use the same 512 timed training examples after ten warmup
   batches, with at least two repetitions; record warmup work separately. Freeze
   ordering of arms and restore identical initial state per repetition. This is a
   throughput sample, not convergence evidence or equal-training-budget evidence.
3. Report images/second and step latency distribution, cold initialization/cache
   time, process/unified-memory pressure where available, MPS allocation, and any
   fallback/warnings. Synchronize at measurement boundaries for asynchronous MPS
   timing; do not add per-step synchronization solely for profiling.
4. Measure validation, epoch-end OHEM and checkpoint work on pinned representative
   inputs using the real paths. Do not extrapolate a 512-example epoch-end cost as
   a measured full-corpus cost. Identify nested/overlapping timers and unattributed
   time. Optional bounded profiler trace only if coarse timing leaves a useful question.
5. Spend remaining arms only on the largest evidenced cost: compatible cache policy
   or OHEM instrumentation/ablation. An OHEM-off result changes training semantics;
   it is diagnostic until C tests quality. Workers/AMP changes unsupported by the
   installed backend are not ordinary tuning knobs.
6. Compare accumulation, effective batch, optimizer updates and weight-decay scaling
   for every arm. A throughput winner with different optimizer semantics needs C,
   not a claim of transparent acceleration. Record output integrity and finite loss.

### Verification and acceptance

Pre-execution tests cover wrong target/backend, active compute ownership, insufficient
memory budget, mismatched inputs, output collision, nonfinite loss, missing stage data
and safe budget exhaustion. Do not force an OOM to measure capacity. On instability,
stop that arm, preserve diagnostics and request review; no automatic retry or service
reset. Budget exhaustion leaves unrun comparisons unavailable, never fabricated.

Accept with reproducible control repetitions, per-arm accounting, measured versus
estimated costs clearly marked, and a recommendation that may be “keep current
settings.” Do not declare a win within run-to-run variation. Provide an estimated
whole-run saving with assumptions and setup costs, not a promised percentage.
No final test evaluation or model promotion occurs.

**Blocker/resume:** missing compute window/approval stops execution only. **Next:**
freeze C's selected configuration and quality protocol, or retain the baseline if
there is no supported benefit. Do not expand into a hyperparameter search.

## TRAIN-EFF-C

### Outcome, prerequisites and authority

Integrated adoption safeguards and one bounded, separately authorized learning
comparison, followed by a continue/resume/new-experiment recommendation. Requires
reviewed A/B evidence, released file ownership, immutable eligible inputs, and an
explicit training budget. No training approval follows from accepting this document.

### Implementation and execution

1. Select one primary question from B: safe throughput tuning, compatible Run 009
   UI initialization versus generic weights, or OHEM policy. Do not combine changed
   initialization, sampling, batch and architecture into an uninterpretable result.
   Smaller-model screening is optional future work unless explicitly selected.
2. Freeze two arms maximum, exact local checkpoints/category maps, validation
   membership and per-class support, seed, optimizer policy, epoch/wall-clock cap,
   evaluation cadence and acceptable quality-regression limits before execution.
   Limits need architect acceptance; missing limits block launch, not software work.
3. Implement accepted settings through existing trainer/preflight entrypoints with
   requested/effective receipts. Preserve defaults unless explicitly adopting a new
   default; no force-AMP or hidden backend fallback. Test configuration-only mode,
   fresh initialization, resume isolation, callback alignment and output collision.
4. Log and run the approved comparison in isolated outputs, selecting checkpoints
   only with validation. Report validation quality versus both elapsed time and
   examples/optimizer updates, per-class regressions, stability and total overhead.
   Keep test groups untouched. A short pilot cannot establish full convergence or DS-G8.
5. Deliver a decision with exact configuration, continuation cost and evidence:
   keep Run 013; propose an authorized exact-state resume; or propose a separately
   identified new experiment. Never load new weights into a “resume” silently.
   Preserve shipped and historical models and both successful/failed pilot outputs.

### Verification and acceptance

Focused real-entrypoint tests plus one integrated offline build/test pass for code
changes. Reuse unchanged evidence. Acceptance requires enforced mode boundaries,
complete measured comparison, frozen quality criteria applied without post-hoc
relaxation, and a reviewable adoption/rollback proposal. A failed or inconclusive
pilot is a valid recorded outcome, not permission to run another candidate.

**Blocker/resume:** unapproved learning budget, unresolved taxonomy/checkpoint/data
compatibility or missing quality limits blocks training. **Next:** maintainer chooses
the documented continuation/new-run proposal; full qualification and promotion retain
their existing independent gates. No automatic production change or retraining loop.
