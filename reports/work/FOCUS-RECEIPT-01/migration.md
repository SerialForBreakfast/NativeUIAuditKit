# Focus execution receipt v1 — consumer migration

2026-09-23; additive uncommitted NUIAK API, not yet TTR's pinned dependency.

`NativeUIDetailedDetectionResult.focusExecution` and
`NativeUIObservations.focusExecution` are optional `FocusExecutionReceipt` values.
Both default to nil for old callers and decode old JSON without the field. Request,
session and recognizer adapters propagate the actual resolver evidence. Existing
modality health retains its historical meaning; `health.focus == .empty` does not
establish successful negative model inference.

```swift
let result = try await session.performDetailed(on: screenshot)
guard let receipt = result.focusExecution,
      receipt.backend == .coreML,
      receipt.modelScoringComplete,
      let artifactDigest = receipt.modelDigest else {
    // Report unknown/partial/fallback, not model agreement.
    return
}
// Match candidate.observationID to result.elements[].id.
// Require disposition == .scored for each compared target, and inspect its
// isFocused plus the observation's isAmbiguousFocus/focusConfidence.
// Record artifactDigest, policy and thresholds alongside the comparison.
```

This is report-only eligibility, not navigation permission, capture freshness,
detector completeness, label truth or model quality. Probability is a model score;
confidence remains separate in the observation and is not calibrated probability.
Unsupported roles are accounted for but not scored. Empty sets are never complete.
The receipt enumerates detector observations entering focus resolution, not later
OCR-only elements. No heuristic probability is manufactured.

Wire fields explicitly include attemptedPredictions, successfulPredictions,
failedPredictions and modelScoringComplete. Counts derive from dispositions; decoding
rejects inconsistent totals, unsupported versions, duplicate observation IDs, invalid
probabilities and backend/disposition mismatches. This detects malformed evidence,
not a malicious sender that fabricates an internally consistent receipt.

Fallback reasons: disabled, model_missing, model_load_failed. Invalid model thresholds
yield backend unavailable, reason invalid_thresholds, zero attempted predictions.
Successful finite-score winner/ambiguity behavior is unchanged. Invalid probability
or confidence now becomes an explicit failed prediction, not usable score evidence.

## Model identity and resource loading

compiled-tree-sha256-v1 sorts regular files by relative path. Each record contains
relativePath + NUL + decimalByteCount + NUL + lowercaseFileSHA256 + newline.
SHA256 covers UTF-8 `compiled-tree-sha256-v1\n` followed by those records. Root paths
are excluded. Child symlinks/nonregular files, empty trees, unreadable entries,
newline/NUL names, more than1024 files or directories, files over64MiB or total
content over128MiB fail identity loading. Directory traversal errors throw.

The loader hashes before and after loading and requires equality; the classifier
holds that digest across warm/session cache reuse. Custom preloaded models default
to unknown identity. This is bounded load-bracket correlation, not atomic filesystem
attestation: adversarial change-and-restore during loading is not excluded. Model
resources must not change during loading. No per-frame disk hash replaces the
identity retained with the loaded instance.

NativeUIModelAsset.requiredModelURL(forTVOS:) and requiredManifest(forTVOS:) are
throwing resource accessors. Operational detector load/request/session paths use
them and propagate failure instead of empty success. Legacy nonthrowing URL/manifest
properties retain historical fatal behavior; direct callers must migrate. Missing/
invalid manifest errors are sanitized. CoreML runtime errors are not claimed
universally path-redacted; identity/scoring diagnostics contain no resource paths.

## Next action

Review this API and adopt after the maintainer publishes a package revision. TTR
owns its adapter tests for old-nil, heuristic, partial, unknown-identity and complete
model receipts. Live inference and navigation still require their own qualification.
No model changed and no appearance-evaluation source gap is solved by this receipt.
