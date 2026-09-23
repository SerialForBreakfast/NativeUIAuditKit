# FOCUS-RECEIPT-01 — integrated software review

2026-09-23; NUIAK architect. Base b3f0546 plus preserved pre-existing dirty work.
No git writes, model changes, capture, training or TTR source edits.

| Outcome | Evidence |
|---|---|
| Software verified | Offline build exit0;14 XCTest+109 Swift Testing pass;9 focused receipt tests pass. |
| Data eligible | Not assessed; no new dataset. |
| Integration qualified | Request/session/recognizer integration verified locally; live TTR adoption not assessed. |
| Model gate passed | Not assessed; bundled models exercised only as offline integration tests. |

## Contract acceptance

- Optional public Sendable/Codable receipt on detailed results and recognizer output;
  old initializers and old payloads remain valid. Tests remove receipt fields before
  decoding legacy results, not merely roundtrip new payloads.
- Actual request resolution emits backend, fallback reason, policy/thresholds and
  one candidate disposition per focus-stage input. Empty/unsupported/all-failed/mixed
  cases never claim complete scoring. Wire counts are explicit and cross-validated.
- Deterministic tests cover invalid crops, errors, nonfinite/out-of-range probability,
  invalid confidence and policy, no candidates, unsupported roles, ambiguity and ties.
  Successful winner behavior is preserved. Confidence remains in the observation;
  model probability never aliases heuristic score in receipt evidence.
- Actual loader computes bounded compiled-tree identity before/after load. Cold,
  warm and cleared-cache sessions retain matching identity; custom preloaded models
  explicitly have unknown identity. Real request and recognizer propagation tested.
- Throwing manifest/URL entrypoints replace fatal access in operational detector
  paths. Missing/invalid manifest and valid bundled-resource cases tested. Existing
  bundle resources were not removed/corrupted to induce an end-to-end process failure;
  injected manifest failure is narrower evidence, not exhaustive deployment coverage.
- Tree tests reject empty content and symlinks, detect changed bytes and verify repeat
  determinism. Load bracketing is not atomic attestation; see migration limitations.
- New receipt decoding rejects unsupported versions, contradictory aggregate counts,
  duplicate IDs, invalid probabilities and backend mismatches. Receipt absence remains
  backward compatible; there is no previously released receipt wire version to migrate.

## Changed implementation

Sources/NativeUIAuditKit/Detection: FocusExecutionReceipt.swift, FocusModelIdentity.swift,
FocusRingClassifier.swift, NativeUIDetectionRequest.swift, NativeUIDetectionSession.swift.
Integration/NativeUIRecognizing.swift propagates evidence. NativeUIAuditKitModels's
NativeUIModelAsset.swift adds throwing resource access. New focused suites are
FocusExecutionReceiptTests.swift and RecoverableManifestTests.swift. Research contract,
architecture note, Tasks and CurrentState document the additive behavior.

## Verification

All commands run from package root with TMPDIR=.build/ios-retention-check/tmp,
CLANG_MODULE_CACHE_PATH and SWIFT_MODULECACHE_PATH=.build/ios-retention-check/module-cache
(absolute project-prefixed values). Scoped host approval used for offline Swift.
Common flags: --disable-automatic-resolution --manifest-cache local
--cache-path .build/ios-retention-check/cache --config-path .build/ios-retention-check/config
--security-path .build/ios-retention-check/security.

- swift test [flags] --filter FocusExecutionReceiptTests: exit0; wire-tests.log,
  nine tests1.048s after build. Includes real bundled-model request/session tests.
- swift build [flags]: exit0; build-final.log,0.20s incremental, no warnings/errors.
- swift test [flags]: exit0; test-final.log,14 XCTest0.306s and109 Swift Testing2.964s.
- Earlier focused-tests.log records a test macro compilation failure, corrected in
  focused-tests-fixed.log; retained rather than overwritten. Final logs supersede it.
- git diff --check: exit0. No dataset/code generation or simulator test needed.

## Handoff

[Migration](migration.md) defines exact API, digest algorithm, legacy fatal-accessor
limits and safe report-only use. Complete software tranche is ready for review; not
self-accepted or published as a release. Maintainer commits manually. TTR then pins
that revision and validates its own adapter; it must still check screenshot freshness
and independent native evidence. No action authority comes from model agreement.

Next unblocked work: source/API review and peer adapter planning. Evaluation capture
still needs source allocation; native iOS probe execution still needs exact target/
build/storage authority. No process remains running. Shared coordination publication
and acknowledgment are recorded separately in coordination.md.
