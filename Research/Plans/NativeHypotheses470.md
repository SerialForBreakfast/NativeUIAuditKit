# REVIEW470 — Native hypotheses and matched correction

Owner: Maximum-mini-NUIAK. Standard detection and focus remain first. HCF stays optional.

## Ready diagnostic questions

1. Does baseline-first detector selection retain successes while recovering abstentions?
   Compare retained DETECTOR422-v2 and DETECTOR469R predictions across controls, positions, and robustness.
   Keep crop models, frames, thresholds, and geometry rules fixed. Reject losses and new wrong selections.
2. Do box changes explain bottom-row losses despite focused-control proposals?
   Use T61 on matched old and new reports for row-top, row-bottom, edge-clearance, and small-decoration.
   Separate missing proposals, ambiguous matches, box errors, and score changes.
   Derive any later training correction from training-only measurements, not these development offsets.

The batch contains 20 diagnostics. Each permits 800 s and 100 MB, with 1 attempt.
These are cached checks, not an overnight training workload. Runtime estimates remain unavailable until receipts arrive.
The runner owns execution. No production policy or model changes follow automatically.

## TTR capability evidence

Sillycon-TTR supplies 12 native Fixture frames with overlay ownership and focus annotations.
The received package has 7 distinct PNG hashes and 1 layout group. Repeated events remain separate records.
Its observed transitions include information, confirmation, interruption, and return states.
Interrupted states identify overlay focus and mark underlay focus unavailable.
Unavailable underlay focus is not a known no-focus screen.
Storage verification does not establish native schema compatibility, training admission, or generalization.

The existing T55 importer does not accept this review manifest directly.
It expects a native-control-admission-v1 document with button, row, or tab sources.
The supplied document uses ttr_native_interruption_review and VisualAnnotation records.
The coordinate label says normalized xyxy, but bounds contain x, y, width, and height.
Sillycon-TTR must clarify that contract before conversion. Do not silently reinterpret it.

## New hypothesis plan

| Priority | Test | What the result decides | Requirement |
| --- | --- | --- | --- |
| P0 | Overlay owns focus while underlay observation is unavailable | Whether the consumer needs separate owner and availability fields instead of a no-focus boolean | Qualify a read-only review importer; preserve native and requested focus separately |
| P1 | Same pixels appear in information and returned states | Whether image-only detection can answer action-context questions | Preserve events and action context; do not assign contradictory image labels |
| P1 | Overlay body and focused action require different boxes | Whether body localization or focus selection fails on modal controls | Clarify xywh coordinates; supply reviewed class mapping and visible-body completeness |
| P1 | Interruption and return sequences preserve focus identity | Whether temporal evidence detects a valid return without treating stale underlay focus as current | Existing B405-111; qualify sequence order and settlement evidence |

Reuse B405-048 for overlay input qualification. Reuse B405-111 for modal sequences.
Do not create duplicate producer requests. Missing schema support blocks these branches, not the retained-data diagnostics.
This package cannot establish independent held-out accuracy. Keep all inspected frames in development or contract-test roles.
Training remains blocked until new groups and explicit training admission exist.

## Bounded implementation requirement

Maximum-mini-NUIAK: qualify a read-only adapter from the native interruption review format to development-only records.
First request precise coordinate semantics and class completeness from Sillycon-TTR.
Reject changed hashes, unknown schemas, contradictory focus ownership, ambiguous geometry, and invalid group boundaries.
Preserve requested focus, native focus, overlay ownership, unavailable underlay state, and event identity.
Positive acceptance requires all 12 received records to preserve their source hashes and group.
Negative acceptance requires unavailable underlay state never to become known-none.
Do not build this adapter within a planning-only review. Keep it as a prioritized implementation task.
