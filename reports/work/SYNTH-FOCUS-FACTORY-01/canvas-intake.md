# Clean-canvas source intake and integration decision

2026-09-29 UTC; current NUIAK Fixture worker. This is source inspection, not
installation or rendered qualification. Batch03 editor reopened (PID45873,
tool session39363); existing saved edits preserved, no second editor found.

## Receipt

Request: tvtestrig-20260929-synthetic-canvas-source.
Named source: tvtestrig/ttr-synthetic-canvas-7ddd182b-20260929T002441Z.tar.gz.
Expected and independently verified:842765 bytes; SHA256
fa74eb83828ff12704f3a3da54d0d5f4ae2562a02327cbb404296a512615f60d.
Copied into fresh gitignored received/canvas storage. Existing safe_members
validator checked282 members,3357499 expanded bytes; links/special files,
traversal, collisions and excessive sizes prohibited. All91 handoff-manifest
files and50 proposed source files/base hashes verified. Approximately34GiB free
before receipt. Originals retained; sender owns shared-copy cleanup.

## Reconciliation against current Max checkout

50 proposed files:21 already current,13 equal the earlier dock handoff,6 match
the declared base,8 new,2 differ only in trailing newlines. The latter are
WorkspaceExperience.swift and ActionLinkedRecorderTests.swift; byte hashes differ
but stripping final LF bytes makes each identical to the proposal. Preserve local
normalization. No semantic conflict identified in this hash/base reconciliation;
this is not a complete code review. No producer files changed.

## Verified contract and gaps

| Area | Source evidence / consumer consequence |
|---|---|
| Clean canvas | appearance.canvas version1; columns1–8, spacing16–80, inset40–160, 24-bit backgroundRGB, showLabels boolean; grid_matrix/standard only |
| Rendering | Eager fully visible grid, geometry based on actual viewport; headers/ticker suppressed. Native probes retained. No scrolling canvas yet |
| Pair semantics | Neutral2×2 reference control remains focusable. Existing reference-baseline classification pairs, not competitor-focused negative pairs |
| Coverage | Optional targetCoverage in harvest-receipt.json; accepted/rejected/unattempted/excluded_by_limit/interrupted and unavailableRecipes. Missing coverage must remain unavailable |
| Identity | Canvas canonical string is appended to appearance digest and family ID; legacy absence retains original identity |
| Consumer | Actual appearance_digest_source on all three supplied recipes rejects appearance_fields. This is expected fail-closed behavior, not a producer runtime failure |
| Examples | Recipe JSON4/24/64 supplied; no rendered bundle or pinned emitted hash vector supplied in this archive |
| Campaign | SyntheticCampaignCoordinator not changed by this package. Previously identified interrupted_cleanup_unknown resume concern remains for unattended collection |

Directly passing preparation recipes to recipe_hash also rejects recipe_numbers
because step_index is absent; those files are preparation inputs, not emitted
resolved sidecars. Do not misreport that as a producer defect or fill missing
fields in captured evidence.

Producer reports59 host tests passed/2 live skips, six model checks, unsigned Fixture
compile. These are producer reports, not tests executed by this consumer.

## Next integrated tranche and approval boundary

1. Approve integration of this specific clean-canvas delta into local TTR,
   matched Debug host/Fixture build/install and replacement of the current TTR.
   Earlier runtime approval covered the dock repair, not this new feature deployment.
2. Run only grid4 then grid24 on the previously selected Simulator after fresh
   ownership/readiness and exact endpoint binding. Bound time/disk; no grid64 or
   unattended campaign. Preserve native reference and each target frame.
3. Implement the source-pinned consumer canvas identity/range checks, tests for
   malformed fields and legacy parity, and receipt-coverage validation. Verify
   against actual producer resolved hash vectors/bundles, not guessed sidecars.
4. Export retained jobs, validate native brackets, complete eligible-ID accounting,
   production crops and clean-frame visuals. Diagnostic-only until admission.
5. Competitor negatives and campaign cleanup/resume remain follow-up requirements;
   they do not prevent this bounded rendering qualification.

Software: source integrity/reconciliation passed; new consumer implementation pending.
Data: no new rendered data; training eligibility unassessed.
Integration: not run for canvas; existing dock qualification remains valid.
Model: unassessed; no model operation. Annotation proceeds independently.

No executable source changed this turn; no Swift build/test required for this intake.
Resume requires explicit new feature deployment/Simulator qualification approval;
the precise source contract is now retained locally for consumer implementation.
