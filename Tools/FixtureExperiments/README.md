# FixtureExperiments

A standalone macOS library and command-line runner for bounded authored rendering.
This package has no NUIAK, Python, model, or network dependency.
TTR integration and execution on Sillycon remain separate qualification steps.

## Requirements

- Swift 5.9 package syntax or newer.
- macOS 14 deployment target. The current live test uses macOS 27.0.1 and Swift 6.4.
- TTR's approved `render-headless-screen.swift` source and a locally compiled executable.
- Approved local input and output directories.

The package does not include or modify TTR's renderer.
The initial adapter supports its `contract-v1-headless-focus` output at 1080p.
It supports `shelf`, `grid`, `hero_detail`, and `top_nav_shelf` layouts.
It does not provide native HCF switching, native capture, or training admission.
Do not use its lock as a Simulator reservation.

## Build and test

Run these commands from this package's directory.
All explicit build and test output stays under `.work`.

```sh
mkdir -p .work/tmp .work/cache .work/tests
export TMPDIR="$PWD/.work/tmp"
export CLANG_MODULE_CACHE_PATH="$PWD/.work/cache"
export FIXTURE_EXPERIMENT_TEST_ROOT="$PWD/.work/tests"
swift build --build-system native --scratch-path .work/build --disable-automatic-resolution --jobs 2
swift test --build-system native --scratch-path .work/build --disable-automatic-resolution --jobs 2 --no-parallel
```

The executable is `.work/build/debug/fixture-experiment`.
Use the native Swift build path to avoid the default Xcode test-signing path.
Do not remove signing protections or change certificates to run these tests.

## Portable qualification

```sh
bash Scripts/qualify.sh /absolute/path/render-headless-screen.swift /absolute/path/new-approved-work
```

An optional third argument sets the host load limit. The default is 8.
For peer qualification, pass the supplied reference bundle as the fourth argument. Do not regenerate it with changed source.
The host configuration rejects a renderer source hash that differs from the supplied experiment.
The script builds once, tests, compiles the renderer once, and creates 2 identical experiment bundles.
Each relocated bundle runs 4 layouts in 2 batches. Both campaigns remain development-only.
It stops if resource checks defer work. It does not wait indefinitely or retry failed jobs.
Inspect the saved JSON before resuming a deferred campaign with the commands below.
The script needs normal process permissions for low-priority child execution.
If an agent sandbox denies that operation, request scoped approval. Do not weaken system permissions.

## Commands

`configure` writes a new host configuration with checked source and executable hashes.
It requires `--workspace`, `--renderer`, `--renderer-source`, and `--output`.
All callers for this authored renderer must share the same host workspace to share its lock.
Keep this configuration local. It contains absolute host paths.

`make-reference` writes a new portable bundle.
It requires `--output` and `--renderer-source-sha256`.
The reference uses placeholders, not a diverse training corpus.

`validate --bundle BUNDLE` checks hashes, paths, versions, expected images, roles, and typed jobs without runtime mutation.
`preflight --bundle BUNDLE --host HOST` also checks the installed renderer, free space, and host load.
`run --bundle BUNDLE --host HOST --max-jobs 10` runs a bounded foreground batch.
Use the existing host scheduler or an approved background shell to call it asynchronously.
The tool installs no scheduler or service.

`status --bundle BUNDLE --host HOST` checks completed receipts before reporting progress.
`cancel --workspace WORKSPACE --experiment-id ID` writes the owned stop marker.
Cancellation remains available if renderer or bundle inputs change.
`reconcile --bundle BUNDLE --host HOST` requires the shared lock before marking an interrupted attempt.
Use `run --retry-failed` to retry an interrupted or failed job in a new directory.
Use `run --clear-cancel` to remove only this campaign's stop marker under the shared lock.
Combine both flags when a cancelled attempt needs a retry.

Failed jobs do not retry automatically. Each job permits at most 2 attempts by default, with a hard maximum of 3.
Changed input, host, or runner identities require a new reviewed campaign. Do not edit an existing checkpoint to bypass them.
The runner preserves incomplete output. Reconciliation never promotes partial output to success.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Operation completed or read-only check passed |
| 1 | Failure; inspect the reason and retained evidence |
| 75 | Resources busy, or the requested batch ends before campaign completion |
| 76 | A previous attempt needs reconciliation |
| 130 | Cancellation |

Distinguish `paused_batch` from `deferred_resources` in JSON. Exit code 75 alone does not identify the reason.
Process launch does not establish work acceptance.

## Data contract

The experiment declares source domain, development role, ancestry groups, jobs, limits, and required renderer source hash.
Assets and `expected.json` use relative paths, byte counts, and SHA-256 hashes.
The host file pins the installed executable and source. A source hash does not prove how a supplied executable was built.
Compile the executable from reviewed source and retain the build log.
Jobs cannot contain executable commands. The host operator selects the trusted renderer.

Receipts record every output hash, decoded-pixel hashes, dimensions, focus identity, ancestry, runtime identities, and elapsed times.
Decoded hashes use sRGB premultiplied RGBA through CoreGraphics. They are not the Python prototype's RGB hash contract.
Authored bounds describe intended geometry. Successful checks do not prove visual accuracy, native labels, or model quality.
Output uses `trainingEligible=false` throughout this adapter.

The lock remains open in the renderer if its parent exits. A second caller cannot enter until the renderer closes it.
The runner terminates only its owned process group after timeout or cancellation.
No native resources exist in this adapter. Native restoration needs a separately qualified TTR adapter.

## Library integration

Import `FixtureExperiments` without model dependencies.
Construct `Runner` with bundle URL, host configuration URL, and the host executable's SHA-256.
Call `preflight`, `run`, `status`, `cancel`, or `reconcile` off the main thread.
`run` is blocking. TTR must supply a background task or use the CLI process.
Use `requestCancellation` when inputs have changed and normal runner construction fails.
Keep TTR's sandbox grants and native ownership rules. This library grants no folder or device access.

## License and ownership

This package uses the included MIT license. Preserve its attribution when transferring it.
TTR retains the renderer and its license. The reference bundle contains no external artwork.
The package is staged in NUIAK for review. Its proposed long-term home is TTR; owner acceptance remains required.
