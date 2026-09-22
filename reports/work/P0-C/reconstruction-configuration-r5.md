# P0-C ios-41class-r5 — verified continuation

Frozen 2026-09-22 UTC. Same authorized iPhone 17 Pro UUID, iOS 26.5/23F77,
Xcode 26.6/17F113, taxonomy, family partitions, profile slots, 32-candidate bound,
and 16,940 target as [r4](reconstruction-configuration-r4.md).

## Source and lineage

- Prefix: exactly 7,500 manifested r4 images (6,100 train / 600 validation / 800 test),
  from its 27 completed generation methods. Retain their original PNG/JSON bytes,
  seeds and filenames. Their actual rendering build is pinned by r4's source/runtime
  records, not retroactively called an r5 build.
- Prefix validation and byte-preserving copy: `r5-prefix-validation-20260922.json`.
  Manifest SHA-256 `bfec7cfc5d74bed4f30b8bb68d957b3bb411efdfe9ffeadaf9ed1197422860bc`.
  Continuation ledger SHA-256 `51f95b21cd14ac5ae08999c5334125a73b296a87542125fbd762d9d4ca106284`.
  Keep all 666 complete-prefix duplicate rejections. The 103 uncommitted accepted
  references and 349 MenuButton rejection records are omitted from the continuation,
  **not deleted**: the complete failed r4 evidence remains preserved separately.
- Remaining 9,440 images: `source-hashes-r5-20260922.txt` and
  `runtime-hashes-r5-20260922.txt`. Rendering changes only MenuButton's seeded row
  content and duplicate menu-item identities; MenuButton has no accepted prefix members.
  Runner changes add isolated probes and a persisted fail-stop guard, not new splits.
- Exact source patch: `source-patch-r5.patch`, SHA-256
  `269c08939e862db403a707a5137c22632c1fe4774f3f107e62b869ed3bc378a3`.
- `r5-continuation-plan.json` pins the completed/remaining test methods. The plan
  checks every prefix family/original-seed tuple against the completed source recipes,
  and verifies the unchanged total of 16,940. Candidate seeds reduce modulo 1,000,000
  to their original slot; no slot or partition is moved.

## Execution

The reviewed local driver `.build/debug-output/p0c-resume/continue_r5.py` has SHA-256
`92ef7da68c2b6398434ce5cac0c7562f49a6d2c017873066ed740dfccff7581c`.
Its `--execute` action verifies source/runtime pins and exact app-container identity,
requires empty app dataset staging, copies/verifies the prefix, and invokes only the
31 remaining generation methods plus the balance report. No automatic retry or app
reset occurs. The same fixed simulator status override is cleared in `finally` and
its exit code is reported. Source/runtime state must remain frozen during capture.

New-only final destination: `NativeUITrainer/reconstructed_corpora/ios-41class-r5`.
On test failure, retain staging in `.build/debug-output/p0c-resume/r5-continuation-failed-evidence`
instead; no completed-corpus destination is published. The normal fresh generator
still reproduces the full recipe catalog; this continuation records both build epochs
explicitly and does not claim identical bytes from re-rendering across runtimes.

## Preflight and remaining gates

Eight native tests passed. Independent validation covers 108 all-family pairs,
200 distinct MenuButton pairs, 26 navigation pairs and 12 status pairs; see
`r5-preflight-validation-20260922.json`. Fourteen Python tests and 92 offline Swift
tests pass. The frozen v1.0 cellular enum and 16% FocusRing policy are unchanged;
this is iOS reconstruction, not FocusRing/TTR work.

Full membership, complete ledger, duplicate/leakage/coverage reports, representative
visual review, exporter read-only compatibility and restore verification remain
required after capture. No inference, training, promotion or independent external
backup is authorized or claimed. Historical Run 009 0.586 remains non-comparable.

Operational observation after launch: Xcode's test installation migrated the data
container from `BBCF6A26-31DF-4FB3-AF3D-C092E7334AF9` to
`88AC0AA8-2D4B-4227-A312-2412848577D9`, preserving the verified prefix. The exact
simulator and bundle ID did not change. The running driver's old-container final
copy must be replaced by an explicit postflight copy from a freshly resolved
container, after test success and override cleanup. Record that retrieval correction
separately from native-test results; no capture restart or provenance upgrade follows.
