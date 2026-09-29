# Canvas consumer compatibility — offline handoff

Software verified:34 Python tests plus offline Swift build/123 tests pass.
Data eligible:unchanged, development-only; no canvas runtime data admitted.
Integration:generated canvas bundle through actual CLI and production cropper passes;
live canvas integration remains unrun. Model gate:unassessed, no model execution.

## Implementation and verification

- harvest_sidecar_v2 accepts only the source-pinned canvas-v1 fields/ranges,
  grid_matrix/standard, integer geometry and Boolean showLabels. Canonical canvas
  suffix participates in recipe hash and derived family identity. Null/absence
  preserves old hashes. Unknown fields/types/ranges and stale family IDs reject.
- harvest_target_coverage validates optional receipt accounting. Accepted target
  identities exactly equal manifest recipeFile/expectedFocus members. Duplicate,
  missing, wrong, nonterminal outcomes and contradictory native inventories reject.
  Excluded/interrupted/unattempted/rejected members remain explicitly incomplete;
  unavailable recipes and inventories without native evidence cannot be complete.
- Existing validate_bundle callers receive normalized targetCoverage. The actual
  ttr_focus_manifest CLI preserves it in output and prints it; revalidation detects
  alterations. Historical manifests without this field remain valid when their
  original receipts do not provide it. No public API, taxonomy or native schema change.
- Generated4/24 inventories test completeness and every partial outcome. Generated
  v2 canvas bundle exercises native brackets, integrity, CLI and production crops.
  Hash expectation is source-derived, not an independently emitted producer vector.
- Retained four/nine dock bundles revalidated read-only:4/8 rows accepted, legacy
  coverage unavailable. Their separately recorded manual qualification is preserved.

Commands: Python unittest test_ttr_canvas test_ttr_appearance test_ttr_sidecar_v2
test_harvest_bundle_validation (34 pass); offline Swift build/test (123 pass).
Logs:.build/human-review/canvas-{consumer-tests,build,swift-test}.log.
git diff --check passed. Human batch03/editor untouched.

## Bounded4/24 live acceptance checklist (not executed)

1. Obtain approval for specific clean-canvas source integration, matched Debug
   host/Fixture build/install/replacement and the named Simulator. Fresh ownership,
   readiness, exact artifact identities and endpoint/process binding required.
2. Freeze grid-4 and grid-24 preparation recipes from verified source archive
   fa74eb83828ff12704f3a3da54d0d5f4ae2562a02327cbb404296a512615f60d.
   Require actual resolved recipe hashes/canvas family IDs to match consumer output.
3. Grid4 first; only proceed to24 after native labels, exports and crops pass.
   Proposed cap:two jobs,20 minutes,1GB evidence. Enforce via advertised controls
   or supervised stop at boundaries; missing enforceable limits block dispatch.
4. Freeze expected native eligible membership at4/24. Check each ID captured exactly
   once with settled brackets and measured bounds; targetCoverage complete=true,
   counts accepted4/24, no unavailable/unverified recipes or omissions. A receipt
   alone cannot prove the external expected recipe list: compare the frozen two-job
   plan independently. Receipt recipe names are filenames, not authenticated identity.
5. Verify every file/hash and production16%/256 crop. Inspect neutral reference and
   each target-focused frame for debug chrome, clipping, unexpected reference glow,
   focus scaling and one active native target. Layout fit is not proven by source.
6. Preserve partial failures and use export-only recovery; no unchanged recapture.
   Recheck target health/ownership after both terminal jobs. Keep diagnostic-only.

No grid64, scrolling, competitor-negative claim, automatic training or campaign
resume is authorized. Reference-negative pairs remain intentional current semantics.
Competitor negatives and cleanup-unknown resume are separate producer follow-ups.
