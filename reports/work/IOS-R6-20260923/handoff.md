# iOS r6 continuation and six probes

Status: assigned tranche complete for review; no capture process remains running.
Owner: reconstruction worker. User authorized exact-target build/install/capture;
no training, inference, Office or TTR operations. Baseline7588a92 was clean.

## Preserved evidence and lineage

- Exact iPhone17Pro simulator F3EF9DB8-0B0F-4757-B653-D1628269F6FF:
  booted/available, iOS26.5; Xcode26.6/17F113.
- `.build/debug-output/ios-r6-20260923/`: first plan, full prefix audit,
  offline build/test logs and independent catalog. Every14,340 pair passed;
  sole strict audit error was `.DS_Store`. Source remains untouched.
- `.build/debug-output/ios-r6-qualified-20260923/`: exact-content prefix inventory
  with explicit Finder exclusion, successful native build/install and app-file hashes.
  First stride dispatch rejected `.plist` before native launch; failed log retained.
- `.build/debug-output/ios-r6-execution-20260923/`: corrected driver plan and
  cloned unchanged build products, original build identity, prefix inventory/catalog.
  No source rebuild or altered pixels hidden by reuse. Native seed-stride test passed;
  independent Pillow decode confirmed32 unique PNGs in each profile,64 total.
- Independently frozen seed19 catalog-v2 SHA256:
  `637a434c2c888641204709ce9c3712b8001ee289d1b79a0c38dd5cd794f61929`.
  Selected probe-0/1 for UIKitControls, ChromeCoverage and DynamicTypeOverflow;
  all six are development membership. Overflow is fixed AXXXL.

## Delivered corpus and probes

`NativeUITrainer/reconstructed_corpora/ios-41class-r6` contains exactly16,940
accepted pairs:12,540 train /2,400 validation /2,000 test. The native remaining-test
passed after748.084seconds (750.88seconds host execution). All2,600 requested
members were generated; no retry, candidate-bound change or quota reduction occurred.
Seed qualification took20.91seconds; six-probe host execution took4.52seconds.

Content seal: `.build/debug-output/ios-r6-content-seal-20260923/` contains validation,
lineage, inventory, readback and seal JSON. Zero accepted decoded duplicates or
cross-split pixel groups. All14,340 prefix pairs, their assignments/ledger entries
and rejected bytes remain unchanged. All2,323 rejected trials remain separate.
Readback verified38,529 content files /9,512,553,837bytes. Manifest SHA256:
`7980a9f362136b1fb061a91b31d1e662ca5b7ec384d9646024210f8066b56a0b`.
Content inventory seal:
`00346b8b4e29f3574d02b171274995c99724fc485be69924aeebffa5f94292d4`.

The strict directory audit is retained at `.build/debug-output/ios-r6-seal-20260923/`:
its only error was `.DS_Store`. The final content seal explicitly excludes only that
auxiliary name under BP-92; the file was not deleted and no dataset member was
excluded. The full decode audit was reused only after all audited bytes, membership,
manifest/ledger, schema and validator identities reverified; content sealing took59.54s.

Visible support is39/41 train,12/41 validation,13/41 test. Train lacks dynamicIsland
and webContent; full missing-class lists and declared style coverage are in validation.
These structural/coverage results do not prove comprehensive semantic correctness.
The replacement corpus is not historically comparable to the missing original pixels.

All six probes passed independent catalog/target/byte/schema/config/geometry intake,
with no duplicate decoded groups. Every overlay was inspected; see
[visual-review.md](visual-review.md). They remain development-only and separate from
reconstruction/evaluation. No full-catalog sweep or additional visual-axis coverage is claimed.

## Verification and implementation

Project-local offline `swift build` passed; `swift test` passed14 XCTest and109
Swift Testing tests, zero package warnings. Final focused Python suite passed47 tests.
Native build took18.31seconds and passed with existing generator
warnings (unused values, duplicate GalleryPage source, no AppIntents metadata).

The driver provides separate plan/preflight/build/stride/generate/retrieve/probes phases.
Execution requires `--execute`; target and source/prefix hashes are pinned. Staging
is opt-in Documents/reconstruction/ios-r6-20260923, never Documents/dataset.
Xcode process timeouts retain unresolved cleanup and prohibit implicit retries.

Two orchestration defects were corrected, not disguised as capture failures:
the pre-launch `.plist` suffix, and missing retrieval-parent creation. The latter
occurred after successful generation; creating the new local parent and a fresh
container lookup recovered the completed output without recapture. Both have
regression tests. Final driver source includes the retrieval-only recovery path;
historical execution plans retain their original driver hashes. Native Swift source
and compiled-artifact identity did not change during successful generation/probes.
No status overrides were created; capture-window defer cleanup ran with passing
native tests. Raw staging and all failed/preflight evidence remain preserved.

Commands: `continue_ios_reconstruction.py plan/preflight/build/stride/generate/probes`
with explicit `--work` and `--execute` for mutations; exact native commands, target,
environment injection, exit codes and runtimes are retained in `*-result.json` and
the frozen `.xctestrun` files. Final seal used `seal_ios_reconstruction.py --work
.build/debug-output/ios-r6-execution-20260923 --output
.build/debug-output/ios-r6-content-seal-20260923 --validated-report
.build/debug-output/ios-r6-seal-20260923/validation.json`. Intake used all six ordered
case IDs against the independent catalog, not the copy inside the captured bundle.

Offline tests: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python
-m unittest scripts.test_continue_ios_reconstruction scripts.test_seal_ios_reconstruction
scripts.test_validate_visual_probe scripts.test_visual_probe_cli scripts.test_corpus_retention`.
Offline Swift checks use the project-local cache/config/security/TMPDIR setup in
the retained final build/test logs. No Git writes, model changes or pre-existing user
edits were made. Hash index: [artifacts.sha256](artifacts.sha256).

## Independent outcomes and next action

Software: passed (47 Python,123 Swift tests; offline build and native entrypoints).
Data: corpus content integrity passed; six probes qualified for development inspection.
Full training eligibility remains false; incomplete class/semantic coverage is explicit.
Native integration: exact-target build/install,64-image stride,2,600 continuation
and six-probe capture/intake passed. No physical-device inference is established.
Model gates: not assessed. SMB coordination: not applicable (local iOS work).

No independent backup is established. Preserve these ignored local artifacts and
existing r4/r5 evidence; do not clean `.build` or simulator staging. The maintainer
is retention owner; choose an independent destination before any cleanup.
Next tranche: explicitly authorized Run009 baseline on all2,000 replacement test
members, with unsupported-class AP unavailable (not zero). No automatic DS-G8 pass,
training launch or production promotion follows this handoff.
