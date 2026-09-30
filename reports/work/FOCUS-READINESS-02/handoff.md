# Focus readiness — diagnosis, corpus audit and preflight

Completed retained-evidence tranche. **Prioritize artwork data alignment; do not
repeat FDR016 unchanged.** No model inference, training, capture or admission occurred.

## 1. What is actually failing

Replayed all 29,202 stored FDR015/016 predictions through the existing metric
implementation. Exact ordered memberships and selection rules match. These are
final diagnostic snapshots, not selected checkpoints or independent test results.

| Real selection subset | Positive / negative support | FDR015 TP / FP | FDR016 TP / FP |
|---|---:|---:|---:|
| Buttons |3 / 7|0 / 0|1 / 0|
| Tabs |3 / 21|0 / 0|2 / 0|
| Artwork |18 / 255|0 / 1|0 / 16|
| Rows |9 / 116|0 / 0|0 / 0|
| Other controls |2 / 19|0 / 0|0 / 0|

Threshold remains 0.85. The apparent two-frame improvement is not an artwork
improvement: all 16 false positives are artwork and all 18 artwork positives are
missed. Both models rank the true focus first on 11/13 complete frames; Home ranks
remain 2 and 8. Twenty-seven frames cannot establish complete-frame selection.
FDR016 retention is 12/18, below the existing 18/18 floor. No eligible checkpoint.

The two retained Home sheets were inspected again:
[Computers](../FDR-016/diagnostics/005.png) and
[HotPotatoTV](../FDR-016/diagnostics/006.png). Reviewer observation: the target body
and some title/context survive cropping; competing bright tiles can still win.
This is not evidence that the target vanished through corrupt crop processing.
Resizing each crop removes absolute screen scale; visible native enlargement,
caption context and relative neighbor size are different signals. The existing
native synthetic wrapper convention differs from real icon-body annotation.

**Ranked explanations and next discriminating evidence:**

1. Narrow native artwork appearance: only 24/150 admitted artwork pairs explicitly
   have native-image effects, with three procedural motifs and a fixed four-item
   row. Counterexample: native enlargement is present in those examples, so it is
   false to say we have no native focus data. Test matched bright/dark competitors
   and dense/sparse layouts with trustworthy native labels.
2. Crop-role/context mismatch: compare measured wrapper and nominal image-layout
   crops on the same native frames. Nominal layout is not enlarged presentation
   geometry. Valid hashes and 256-square dimensions do not resolve this question.
3. Representation/learning limitation: the frozen encoder/head may not separate
   real focus cues. Same-data paired loss worsened artwork FP and retention, so
   another identical loss run is unsupported. Fine-tuning is a later controlled
   experiment, not an established fix or a reason to lower thresholds now.

These are hypotheses, not causal proof. No detector predictions were generated;
detector recall/localization remains unmeasured by this reviewed-box comparison.

## 2. Corpus accounting

2,203 distinct image/crop files decoded and hash-verified; 2,237 input references
were rechecked after analysis. Exact membership and the 64 selection exclusions
are retained in [audit.json](audit.json), with hashes in [inputs.json](inputs.json).

| Current admitted training appearance | Pairs |
|---|---:|
| Buttons |119|
| Tabs |17|
| Artwork |150|
| Rows |77|
| Total |363|

Preserved: 726 training crops, nine retention pairs/18 crops, 453 real selection
crops. No changes to sampling, labels, membership or checkpoint rules.

- 24 within-training exact crop duplicate groups contain 37 extra crop occurrences.
  These are crop duplicates, **not 37 redundant pairs**: the corresponding partner
  may differ. Do not delete or reweight them silently.
- Two additional duplicate groups occur within real selection: unfocused controls
  new-20 and new-23 repeat between photos:frame-002 and photos:frame-007. Preserve
  the comparison denominator; report this correlation in future independence work.
- Zero exact crop-pixel overlaps across admitted roles and zero conflicting labels
  among those duplicate groups. This does not establish source independence.
- The retained 96-pair proposal has zero exact crop overlap with admitted members.
  It contains two individual same-state crop duplicates between button/nested-tab
  recipes; no evidence here that either whole pair is redundant.
- Those 96 remain diagnostic-only: 32 native controls, 60 caption-inclusive artwork,
  four caption-free artwork. The original intake's 13 excluded duplicate pairs and
  three geometry holds remain excluded. None becomes training data through this audit.

More files are not the missing win. The remaining gap is controlled, representative
native artwork and independent real coverage, not decode quality or raw pair count.

## 3. Actual trainer preflight and next assembly

[preflight.json](preflight.json) is produced by the real trainer with `--dry-run`,
the pinned FDR016 protocol and no approval. Configuration, source hashes and exact
membership validate in `.venv-yolo`; launch is correctly blocked by
`missing_experiment_approval`. No output run directory was created. The initial
`.venv-review` attempt lacked torch package metadata; its stderr is preserved.
No package was installed and no runtime hash exception was used.

This proves the existing training path is executable in principle, **not that
rerunning it is worthwhile**. No new run number is allocated. A useful new protocol
is deliberately not frozen before choosing geometry and admitting exact members.

Next assembly proposal:

1. Preserve all 363 admitted pairs, nine retention pairs and the exact real
   selection/exclusion sets as the comparable baseline.
2. Use the existing eight-scene/32-pair matched geometry trial as the first data
   decision: caption on/off, brightness swapped between targets/competitors,
   sparse/dense layouts, small/large bodies. These are collection targets, not
   qualification thresholds. Native telemetry supplies labels; no manual redraw
   campaign or successful new model is prerequisite.
3. Compare both explicit crop roles through the implemented production adapter.
   If nominal layout still does not represent real icon-body inputs, do not infer
   presentation bounds. Request the missing measurement or reject that hypothesis.
4. Freeze exact proposed additions/replacements, duplicate dispositions and source
   groups. Admission needs a separate member-bound decision. Related Fixture scenes
   stay in development, never an allegedly independent test.
5. Only then approve one changed-data experiment with fixed comparable metrics,
   0.85 threshold, retention floor, frame guards and no-best-if-ineligible rule.
   Keep further encoder/loss changes separate so the result is interpretable.

Ten existing independent appearance/challenge coverage blockers remain listed in
the audit. This small corpus is not production qualification. No challenge images
were inspected, scored or mined. Export/parity and TTR release testing remain later
assignments after a selected candidate exists.

## Verification and outcomes

- Software: cached-score and paired-protocol tests; actual retained-output checks;
  offline Swift build and 123 Swift tests. Logs are in this directory.
- Data: complete membership, duplicate accounting and file integrity audited;
  geometry convention and independent coverage remain unresolved.
- Integration: actual trainer dry-run validates, requires fresh approval; TTR's
  existing measured-geometry request is still the next producer action.
- Model: unchanged; no new execution, eligible model or release claim.

Coordination: no new producer contract or action; no duplicate shared request was
published. Existing geometry request remains authoritative. Reproduce with
`PYTHONPATH=scripts .venv-review/bin/python reports/work/FOCUS-READINESS-02/audit.py`
and then `verify.py`. The script never imports a model. Existing crop/parity evidence
is reused; no new crop implementation was added.
