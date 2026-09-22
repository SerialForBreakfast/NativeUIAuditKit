# Perception evidence and integrated acceptance review

2026-09-22; assigned architect tranche: PER-01 inventory/label-coverage review and
PER-02/04/05/06 offline acceptance. No capture, producer operations, inference or training.
Owner: NUIAK architect. Starting revision `d3171ec5976e55cf413a7eb782f8c185789d3cf9`;
working tree clean. P0-C and other assignments are outside this scope.

## Completion contract

1. Re-audit the explicitly supplied `dataset/focus_ring` manifest and flat
   `dataset/tvos_captures` directory; preserve every original. Review available visual
   evidence for benchmark leads, not fabricated labels or callbacks. Account for all
   members and unsupported strata; quarantine is a report decision, not a file move.
2. Inspect actual PER-02/04/05/06 entrypoints and evidence against canonical contracts.
   Repair demonstrated integration defects with regression tests. Keep source kinds,
   coordinates, provenance, failure states and action authority explicit; these are
   separate benchmark contracts, not an automatically composable live controller.
3. Rerun focused suites plus offline package checks. Record per-packet acceptance,
   remaining real-data blockers, exact capture requirements and next action in
   `reports/work/PERCEPTION-ACCEPTANCE/handoff.md`; Tasks.md remains the only queue.

## Research-first corrections under review

PER-02 currently lets an empty prediction payload stand for successful empty detection,
and counts a localized chevron with an explicit unknown row as a wrong row link.
Require explicit `chevrons` and `dialog` fields (empty array/null remain valid) and
distinguish association abstention from a claimed wrong row. This preserves the existing
wire version while tightening malformed-input rejection; add an additive metric counter.
PER-05's helper reply must also reject out-of-frame change rectangles: otherwise a
corrupt rectangle outside the selected foreground can be mistaken for stability.
Bind every returned rectangle to its compared frame dimensions and retain failure
accounting instead of evaluating an invalid measurement.
Do not upgrade any imported artifact, parsed source string, or synthetic observation to
training eligibility. Existing result files remain historical and are not overwritten.
