# Batch02 partial production crop QA

## Superseding complete revision — 23:27Z

Verified new human revision20260928T232705Z-8a71fdbe:8 reviewed frames/89 reviewed
controls, completeness attested for all8. Production crop QA89/89 completed;89
distinct decoded crops. Full audit now succeeds, no hard issues. One near-frame
warning recorded-951/971 is Arcade versus Search focus in the same related layout;
retain both. Reports:qa-batch02/final-crops/crop-qa.json and
qa-batch02/final-audit/audit.json; review sheets in final-audit/review.html.
All previous partial evidence remains unchanged. Support8 focused/81 unfocused.
Across latest two completed batches:16 frames/171 reviewed controls,16 focused.
Diagnostic-only; no model execution or training admission. Producer-unverified
frame249 now has human settled attestation, not retroactive native settlement.

Historical partial run below is superseded, not deleted.

Input revision20260928T231403Z-405f04f0 remains immutable. Actual production crop
CLI completed70/70 controls from7 reviewed frames, all256×256 using production16%
expansion.70 distinct decoded crop pixels; zero exact crop-pixel overlap with the
first batch's82. Membership/hash evidence:qa-batch02/crops/crop-qa.json.
Support:7 focused/63 unfocused;30 collectionItem,21 otherFocusable,18 tabItem,1 label.

The eighth frame recorded-249 is explicitly blocked, not omitted from the source
revision. Its19 boxes remain pending. Full audit attempt exited2 invalid_control_id
because the immutable pending snapshot has unassigned IDs (Finish originally
blocked on tiny negative boundary rounding). Failure receipt retained at
qa-batch02/audit/failure.json. Do not call this a whole-batch audit pass. No labels
rewritten and no inference/training. Next: scoped boundary tolerance fix, then
operator confirmation into a new revision, followed by complete QA/audit.

Two latest reviewed batches total15 frames/152 crops,15 focused/137 unfocused;
not152 matched pairs and not training admission. Existing FDR-009 used273 training
pairs and9 retention pairs, but preservation did not establish broad transfer.
Retain new session for development regression under the pending admission proposal.

Near-term training collection proposal: existing24-pair target (12 artwork/Home,
6 native buttons,6 Settings) plus proposed8–12 matched tab pairs,32–36 total.
These are initial collection targets, not qualification thresholds or assurance
of model gains. Use separate training-assigned sources; preserve complete neighbors,
both states for the same control, difficult unfocused negatives, role/geometry QA
and source-disjoint validation. Training execution still requires explicit approval.
Full FocusRingv1 gate remains6000 eligible pairs plus its existing appearance,
independence, hard-negative and real-transfer requirements; count alone cannot pass.
