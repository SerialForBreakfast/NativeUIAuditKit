# ADR-0025 — portable experiment runner

Status: proposed ownership and interface. The maintainer requests this design; TTR integration requires its owner's agreement.
Implementation update: [HCF336](HCF336Results.md) delivers a standalone package and local relocation evidence. TTR acceptance remains pending.
Date: 2026-10-10.
Extends [ADR-0019](ADR-0019-Batched-Renderer-and-Asset-Pipeline.md) and [HCF335](Plans/HCF335.md).

## Decision

Make acquisition a separate, optional TTR experiment tool. Keep model evaluation and training in NUIAK.
Prefer a small Swift package in the TTR repository, with a library and a command-line executable.
TTR can call the library or launch the executable. Neither path requires NUIAK or its model packages.
Sillycon-TTR and Maximum-mini-TTR use the same versioned tool and experiment bundle.
Do not create a third repository or a second scheduler now.

The portable package is now staged in NUIAK. Its TTR ownership and native adapter remain proposed.
Keep the existing Python runner as a tested prototype until the replacement passes equivalent checks.
Do not maintain two production acquisition engines after migration.

## Why the prototype cannot be copied alone

`focus_batch_harness.py` imports `human_annotation_review`, which imports other NUIAK tools.
It requires Pillow, NUIAK's root resolver, and repository-specific paths.
Its plan records absolute renderer, artwork, and Python paths.
Its working directory, lock, and Swift cache depend on NUIAK's checkout.
It also assumes four layouts and 1080p output inside its execution logic.
Those choices suit the local test, but they prevent independent use on Sillycon.

## Ownership

| Component | Proposed owner | Responsibility |
| --- | --- | --- |
| Experiment runner | TTR | Jobs, recovery, resource claims, renderer adapters, and capture receipts |
| Native Fixture adapter | TTR | Exact target, observed focus, profile changes, restoration, and session cleanup |
| Experiment definitions | NUIAK | Hypothesis, requested coverage, data roles, ancestry, and fixed budgets |
| Evaluation adapter | NUIAK | Crops, model inputs, cached predictions, metrics, and training admission |
| Existing scheduler | Host owner | Start approved jobs when resources permit; inspect structured results |
| Artwork and model computation | BigDog-NUIAK | Produce approved inputs and run compatible non-Apple jobs |

TTR's desktop interface stays optional for authored rendering.
Native jobs still use the permissions and runtime that their supported TTR interface requires.
The command-line tool does not bypass the app sandbox or create device authority.
BigDog-NUIAK can prepare bundles and process outputs. It cannot run native Apple rendering on Linux.

## Package boundary

Proposed package name: `FixtureExperiments`.
Proposed executable name: `fixture-experiment`. These names are not existing interfaces.
Use Foundation for state and process control. Use CryptoKit and ImageIO for hashes and image checks on macOS.
Keep AppKit rendering and Simulator calls inside specific adapters, not the job engine.
Reuse TTR's renderer and native controls. Do not copy their implementation into NUIAK.

Ship source with tests and a command-line build path. A release can also supply a checked executable.
Record the minimum macOS version and required toolchain after testing; do not infer support from NUIAK's deployment target.
Do not require Python, PyTorch, NUIAK models, coordinator credentials, or a network connection for authored execution.
Do not install dependencies or download assets automatically.

## Portable experiment bundle

Separate the experiment from the machine that runs it.
The portable bundle contains these files:

- `experiment.json`: schema, experiment ID, jobs, adapter requirements, limits, roles, and ancestry groups.
- `assets/`: approved artwork with relative names, sizes, and hashes.
- `expected.json`: required outputs, counts, and validation rules.
- `LICENSES/`: asset and source attribution where required.

Use relative paths inside the bundle. Reject absolute paths, traversal, symlinks, duplicate names, and unexpected executables.
Hash the bundle's declared files. Reject missing or changed files before execution.
Do not embed shell commands, Python expressions, credentials, machine names, or absolute source paths in jobs.
Use an allowlisted adapter identifier and typed parameters instead.

Each machine supplies a separate local configuration:

- Approved input, output, cache, and temporary directories.
- Installed adapter paths and expected versions or hashes.
- Explicit Simulator UUID and endpoint, when required.
- Host resource limits and a shared location for resource claims.

Write resolved paths, OS version, runtime identities, and executable hashes into the attempt receipt.
Keep that receipt local unless its fields pass the existing transfer policy.
Different machine paths must not change experiment membership or job identity.

## Execution and recovery

Expose `validate`, `preflight`, `run`, `status`, `cancel`, and `reconcile` operations.
Keep planning and validation free of runtime mutations.
Return versioned JSON and documented exit codes for complete, deferred, failed, cancelled, and unresolved-cleanup outcomes.
Keep process launch separate from job acceptance.

Use a foreground runner under the existing scheduler. Permit optional detached launch for direct operator use.
Do not create a resident service or poll indefinitely inside the tool.
Accept a bounded job count per invocation. Resume through the same experiment ID and checked receipt.

Store immutable attempt records plus an atomic current checkpoint.
Skip only jobs whose completed outputs still match their receipts.
Record setup, rendering, validation, cleanup, and total times separately.
Preserve failed outputs. Never turn a partial directory into a completed result by renaming it alone.

Use shared host resource claims across callers and output directories.
An experiment-specific lock alone cannot protect a shared Simulator.
The TTR app and command-line adapter must use the same native ownership mechanism before both can operate safely.
Do not clear a claim solely because it is old or its recorded PID disappeared.
Check the prior attempt and cleanup state before allowing another native mutation.

Persist the original profile before changing it. Verify restoration after cancellation or failure.
If a process dies, the next invocation reconciles the journal before starting new jobs.
If restoration remains uncertain, stop native jobs and report the exact required recovery.
The runner cannot guarantee restoration while the host is off. It can guarantee that unresolved restoration blocks new native work.

Retry transient reads only within a fixed adapter policy and retry count.
Do not automatically repeat uncertain device inputs, profile changes, or captures.
Authored jobs can use new attempt directories after explicit or bounded scheduler retries.
Give the scheduler a retry limit; do not let repeated invocations retry a permanent failure forever.

## Results and model experiments

Export PNGs, annotations, capture evidence, and a versioned receipt.
Record authored effects and observed native focus as different label sources.
Record observed profile state separately from requested profile state.
Keep all counterparts and derivatives in their assigned ancestry group.
Passing the producer checks establishes file and interface validity, not training admission.

NUIAK imports results through its existing validators.
NUIAK then runs evaluation or training as a separate approved job.
Cache predictions by model, preprocessing, settings, and input hashes.
The acquisition tool does not launch model sweeps or change shipped models.

## Alternatives

Keeping the tool in NUIAK forces TTR to inherit unrelated research dependencies.
Copying the current Python script preserves hidden dependencies and creates two maintenance paths.
A standalone Python package is possible, but adds an interpreter and Pillow requirement to TTR hosts.
A small Swift package better matches TTR's native tooling and avoids those runtime dependencies.
A new shared repository adds release and ownership work before a second independent consumer needs it.

## Qualification and migration

1. Agree on the TTR package owner and supported adapter interfaces.
2. Freeze a portable bundle schema and a small reference bundle.
3. Extract the engine and port the existing fault tests without changing renderer behavior.
4. Run the same bundle from unrelated directory paths on both Macs without importing NUIAK.
5. Compare job membership, receipt structure, and geometry. Report pixel differences instead of assuming cross-OS identity.
6. Test cancellation, restart recovery, changed inputs, full output storage, and competing callers.
7. Qualify native profile restoration before admitting unattended HCF jobs.
8. Replace NUIAK acquisition with a thin client after both hosts pass.

Preserve HCF335's evidence and old manifests. Use a new schema for portable plans; do not silently rewrite sealed plans.
The initial milestone is authored execution on both Macs, not native HCF training readiness.
Native qualification and NUIAK's matched model comparison follow as separate checks within the larger delivery tranche.
