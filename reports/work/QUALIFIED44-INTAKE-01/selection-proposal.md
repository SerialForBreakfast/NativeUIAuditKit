# Representative checkpoint selection — proposal for approval

Replace retention-only checkpoint selection with a real-development selection
objective. This is a proposed experiment change, not an implemented trainer,
new qualification threshold, run allocation, or training authorization.

## Exact data roles

Use the five real protocols named batch01, batch02, batch03, photos and supplement
in `reports/work/FDR-012/comparison-freeze.json`, SHA256
`e9a31369ded7c51b622fa30531b0e2ca747ba9f208a0b9c034ac1ede9394630c`.
That freeze pins exact protocol hashes and sample IDs. Preserve all517 entries;
the existing settled-candidate filter yields453 (35positive/418negative).
The64 auxiliary, disputed or unsettled entries remain diagnostic, never silently
made eligible. These40 frames have already been development-exposed; explicitly
declare their new checkpoint-selection use before a future run. Never train on them.

Keep the original nine retention pairs unchanged. The50 related synthetic pairs
remain a separately reported diagnostic, not the selection objective. Protected
challenge evidence remains unopened and unscored. Source independence is not
established by these40 frames or by their screen-family labels.

## Proposed selection rule

At the unchanged0.85 threshold, an eligible epoch must:

- Preserve18/18 retention classifications.
- Match or improve FDR-010 TP and FP counts in each real stratum: buttons0/0,
  tabs0/0, artwork1/9, rows2/0, other0/0 (TP must not fall; FP must not rise).
- On the13 already-complete real frames, preserve at least2 unique-correct,
  with0 wrong and0 multiple. Incomplete frames cannot establish this outcome.
- Improve total real focused detections above3/35, with no more than9/418 FP.

Among eligible epochs choose minimum real-development balanced binary
cross-entropy, earliest epoch on a tie. Give buttons, tabs, artwork and rows
equal25% mass, then positives/negatives equal mass within each stratum. Within
each stratum/label bucket, give each existing screen-family string equal mass,
then each distinct decoded crop equal mass; repeated identical crops split that
weight. Contradictory labels for identical pixels block preflight. Screen-family
weighting reduces repeated-screen dominance; it is NOT independent-source weighting.
Keep other controls in the regression guards and report, outside this four-stratum
objective. Missing required buckets or predictions invalidate selection. No eligible
epoch means no selected checkpoint. Use numerically stable BCE without changing
reported probabilities or inference decisions.

These count limits are a proposed bounded development experiment, not production
accuracy claims. FDR-012 fails them on artwork, rows and complete-frame selection.
No alternative FDR-012 epoch was scored to manufacture a passing candidate.

## Next implementation assignment

Implement and test the selection adapter, with an explicit new role manifest and
per-sample weights frozen before execution. Test all guards, duplicates, tied loss,
empty buckets, missing scores, and no-eligible-epoch behavior. Reuse production
crops and existing metrics. Verify preflight, then request a bounded run approval.
Candidate data may include the38 member-bound eligible pairs in
`pair-dispositions.json`, preserving325 existing training and9 retention pairs:
potential363+9, not yet assembled/admitted. Keep the three geometry cases quarantined.
Do not wait for their repair to implement selection. Review the separately running
TTR100-pair campaign only under a subsequent assigned receipt; do not blindly
merge it or treat quantity as coverage. An untouched source-separated test remains
necessary before any broad release claim.
