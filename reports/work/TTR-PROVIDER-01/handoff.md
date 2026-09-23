# TTR-PROVIDER-01 — source-backed contract response

2026-09-23. NUIAK architect. No source behavior/API changes in this assessment.

Software: not newly assessed. Data eligibility, live integration and model gates:
not assessed. This is a confirmed current-capability response, not feature completion.

Inspected actual current request selection, loader, both focus resolvers, classifier
outputs, detailed result API and mandatory model accessors. Confirmed TTR's backend
uncertainty is real; no supported field distinguishes full model scoring from heuristic
or skipped candidates. health.focus is derived from final focused observations, not
execution completeness. Both branches populate the same score/confidence fields.

Rehashed local tvOS manifest and FocusRing weight bytes against the peer contract's
packaged identities; both match. This does not establish the peer's loaded artifact
or execute inference. Current HEAD b3f054657ff8163ae4631163dac4c75666a9cf75 is newer
than the peer pin but retains the public provenance gap; do not prescribe a version
update as if it resolves it.

Detailed evidence and full implementation acceptance:
Research/Plans/FocusExecutionReceipt.md. Source anchors:
NativeUIDetectionRequest.performDetailed,loadFocusClassifierIfAvailable,
resolveTVOSFocusML,resolveTVOSFocus; FocusRingClassifier.classify;
NativeUIModelAsset load/resource/manifest accessors.

Next software packet FOCUS-RECEIPT-01 explicitly scopes public receipt additions,
load-bound identity and cache propagation, per-candidate accounting, compatibility
tests and consumer migration. Existing trained candidates remain unpromoted.
No new package build needed for this document-only response; source/hash and
diff/content checks performed. Worker/model guidance separates packaging identity
from execution evidence. Shared publication/readback tracked in coordination.md.
