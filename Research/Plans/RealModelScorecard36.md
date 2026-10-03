# REAL-MODEL-SCORECARD-36

User approved the recommended substantial tranche October2: real-screen baseline,
coverage-driven focus/full-screen challenger preparation, and iOS correction decision.
Use existing reviewed private pixels locally; no new capture or data-role changes.

Run the shipped tvOS detector + bundled production focus path on all46 unique
reviewed screenshots frozen in challenge31 inventory (583 controls,7 explicitly
complete frames). Verify inventory seal, source references and image hashes first.
Explicit tvOS, confidence0.5, OCR off to isolate detector output. Preserve actual
loaded identities and winner policy; bundled FocusRing is not FDR021. At most46images,
300seconds inference wall time,2GiB new output, one fixed pass without threshold search.
Reuse CLI/preprocessing. Explicit outputs/temp stay project-local; normal Apple
framework host caches permitted for the assigned runtime.

Score class-agnostic deterministic maximum-cardinality matching at IoU0.50/0.75.
Separate reviewed-control localization recall, exact role agreement on matched boxes,
and selected-focus correctness. Labels cover focusable controls, not every text or
container: unmatched detections are unreviewed, not automatic false positives.
Complete-frame focus scoring needs explicit completeness and one focused truth.
Unsupported focus-only roles remain explicit, with no tabItem→tabBar remapping.
This reused corpus is development evidence, not an independent benchmark.
Reuse FDR021/FDR036 results with their own denominators; retain predictions for replay.

Independent deliverables: (1) executable full-screen preparation/preflight reporting
label completeness, role/source-group coverage, resident trainer/model availability,
and a controlled experiment proposal without training/admission; (2) iOS retained
Run013 error/coverage recomputation and generator source audit to rank corrections.
No repeat iOS inference needed. Focused tests plus full offline Swift checks at handoff.
One integrated Markdown handoff; publish only actionable TTR consequences.

Completed October 2: 346/583 bodies localized, 21/46 focused targets localized,
4/7 complete Settings frames correctly selected. Score focus from the actual selected
box, independently of which duplicate the recall matcher assigned. Retained raw
predictions were replayed after that tested metric correction. Full-screen diagnostic
inputs and the independent 2,000-frame iOS error replay are complete. See
[handoff](../../reports/work/REAL-MODEL-SCORECARD-36/handoff.md) for canonical evidence,
verification and the next proposal-recovery / bounded-training tranche.
