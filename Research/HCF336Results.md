# HCF336 — portable package results

Owner: Maximum-mini-NUIAK.
Date: 2026-10-10.

## Delivered

[FixtureExperiments](../Tools/FixtureExperiments/README.md) is a standalone Swift package with a library and command-line executable.
It has no NUIAK imports, Python dependencies, model dependencies, or network client.
The package uses TTR's existing renderer through a typed adapter. It does not copy the renderer implementation.
Its proposed long-term home remains TTR. Maximum-mini-NUIAK stages the source for review and handoff.

Portable experiment files contain relative asset paths, hashes, jobs, limits, ancestry, and development roles.
Separate host files contain local paths and approved resource limits.
Each attempt records outputs, model-independent runtime identities, timing, and cleanup.
The runner checks complete receipts before skipping jobs.

## Verification

| Check | Result |
| --- | --- |
| Copied package build | Pass; no dependency on the NUIAK package |
| Package tests | 22 pass |
| Real campaigns | 2 relocated campaigns on Maximum-mini |
| Jobs and images | 8 jobs produce 16 images |
| Resume | Each campaign runs 2 jobs, pauses, then completes the remaining 2 |
| Prior results | Both first checkpoints retain identical job records and receipts |
| Pixel comparison | Corresponding decoded images match across the 2 local paths |
| Resource check | Host load above 12 defers the initial launch without creating a campaign |
| NUIAK offline build | Pass |
| NUIAK offline tests | 14 XCTest cases and 173 Swift Testing cases pass |
| Sillycon execution | Pending |

The tested host uses macOS 27.0.1 and Swift 6.4 on Apple Silicon.
The package declares macOS 14 deployment. Runtime support on macOS 14 remains untested.
The source uses Swift 5.9 package syntax. Older toolchains remain untested.

The default Swift build path fails during test signing because of file metadata.
The native Swift build path passes without certificate changes or signing repairs.
The initial agent sandbox also denies the package manifest build. Scoped execution permission resolves that boundary.
Failed build logs remain separate from the final successful tests.

The package tests cover unsafe paths, symlinks, undeclared files, changed inputs, collisions, resource deferral, and exclusive access.
They also cover bounded retries, interrupted checkpoints, cancellation, timeouts, missing images, corrupt images, and wrong focus identities.
The timeout tests stop and reap owned child processes.
The interrupted-checkpoint test does not establish native profile restoration after a host crash.

## Performance scope

Campaign A records 0.900 s across its 4 job totals. Campaign B records 0.766 s.
These totals include rendering and output validation inside each job.
They exclude package builds, renderer compilation, scheduler delay, command startup, and outer campaign checks.
They do not measure native capture speed or accepted training examples per hour.
The reference uses placeholders. Repeated images across relocation tests are deliberate software evidence, not added training diversity.

## Source handoff

Archive: `fixture-experiments-hcf336-v1.tar.gz`.
Size: 16,998 bytes.
SHA-256: `43bee9cdf4ed8aa68a423430309ff20ca037d540d22a85d9aa7bc12890d0d15d`.
The archive contains 20 entries, including source, tests, MIT attribution, documentation, and the portable reference bundle.
It contains no images, models, credentials, compiled binaries, or host configuration.

SMB path: `nuiak/fixture-experiments-hcf336-v1.tar.gz`.
Transfer request: `nuiak-hcf336-source-v1`.
Publication verifies the actual mount, file size, and content hash.
Maximum-mini-NUIAK retains the original. Cleanup requires the matching receiver receipt.

Coordinator stores the ownership request `nuiak-hcf336-portable-01` at cursor 202.
It stores the package handoff `nuiak-hcf336-source-ready-01` at cursor 204.
Exact-ID handoff readback passes. Peer reading, receipt, ownership acceptance, and execution remain unconfirmed.
The handoff includes the bounded qualification command, source pin, stop conditions, and required return evidence.
Final transfer inspection verifies both archive copies. The receiver receipt is still missing, so no shared file is removed.

Sillycon-TTR also reports new template axes at cursor 207. That source remains uncommitted.
Maximum-mini-NUIAK acknowledges the message and preserves TTR's generator as the future recipe source.
The runner does not introduce a second composition planner. The reply is stored and read back at cursor 208.

## Remaining work

1. Sillycon-TTR receives the package and confirms the proposed source destination.
2. Sillycon-TTR runs the supplied reference bundle under its local authority.
3. Maximum-mini-NUIAK compares returned receipts and records host-specific differences.
4. TTR integrates the package after review; NUIAK then uses a thin acquisition client.
5. The native adapter adds verified profile restoration and restart recovery before unattended HCF collection.

No TTR repository files change in this tranche. No Git writes occur.
No recurring service, native capture, training, model change, or production promotion occurs.

## Independent outcomes

Software verification passes locally. Authored integration passes on Maximum-mini only.
Data remains development-only with `trainingEligible=false`.
Native HCF integration and model quality remain unassessed.
Raw evidence stays under ignored `reports/work/HCF-336/`.
