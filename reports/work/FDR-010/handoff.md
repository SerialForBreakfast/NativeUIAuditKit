# FDR-010: run and comparison complete; reject test export

2026-09-29. The approved bounded candidate tranche is complete for review.
The conditional export branch did not qualify. No second run, export, TTR model
installation, challenge scoring or shipped replacement occurred.

| Outcome | Evidence |
|---|---|
| Software verified |Existing trainer and CPU scoring/metrics reused. Six generated adapter tests,14 human-evaluation tests, offline Swift build and123 tests pass. |
| Data eligible |313 training pairs plus nine unchanged retention pairs; exact frozen preflight passed. No benchmark members added to training. Production corpus and independent coverage remain incomplete. |
| Integration |362/362 new candidate scores complete; exact retained baseline memberships and metrics reproduced. CoreML/PyTorch backend difference reported; no export parity claim. |
| Model gate |Failed observer-export conditions; production qualification not established. Keep shipped model. |

## Actual model outcome

Thirty epochs completed on MPS/torch2.7.0, PID21169,16:45:53Z–16:52:21Z.
Execution388.452s, including298.187s pre-execution corpus revalidation;
post-preflight training/selection90.265s. A separate initial preflight also ran.
Epoch29 selected by minimum eligible retention BCE0.000017874388; all30 epochs
preserved18/18 classifications. Retention is nine Settings/Accessibility pairs,
not nine independent families or broad transfer coverage. The selected checkpoint
hash is `775c3197a48169807fb8e20b41df71b4c61c8f152bde82f3ebbd56d25712583d`.
Last epoch30 retained separately, never substituted for the selected checkpoint.

### Same24-frame development benchmark, threshold0.85

| Metric | Shipped | FDR-009 | FDR-010 |
|---|---:|---:|---:|
| Focused controls found /19 |8|4|3|
| Misses |11|15|16|
| False positives /183 |30|8|3|
| Unique-correct complete frames /13 |3|2|2|
| No focus /13 |5|9|11|
| Multiple focus /13 |5|2|0|
| Single wrong selection /13 |0|0|0|

249 crops scored,202 settled candidates used for these crop metrics. Eleven of24
frames have unavailable complete-selection metrics; all old settlement, unresolved
label and incomplete-coverage exclusions are preserved. Human boxes are supplied,
so this is not detector recall or end-to-end navigation qualification.

### Separate eight-frame Home/Photos/Settings regression

113/113 crops scored. Shipped finds4/8 focused controls with11 false positives;
FDR-0091/8 with15; FDR-0100/8 with4. Both Photos pairs pass shipped and fail both
candidates. FDR-010 Photos focused scores are0.0000173 and0.0001283, not near0.85.
Complete-frame selection is unavailable because candidate completeness is unknown.

FDR-010 is more conservative, not a better focus detector. Its90.6% accuracy on
the first set conceals15.8% positive recall. No threshold sweep was performed.
Lowering the threshold is not demonstrated to restore transfer; one Photos pair
even ranks the unfocused crop above the focused crop.

## Evidence-backed next assignment

**Do not repeat this retention-only training policy or scale the same recipes
unchanged. Prepare a representative validation/transfer contract and a full
coverage-driven synthetic campaign before another run.** Keep the existing nine
pairs as a forgetting check, not the sole checkpoint selector.

1. **Representative checkpoint validation:** include separately reserved native
   button/dialog, Settings-row, tab/selected-parent and artwork-tile sources. Preserve
   both real regression sets as development evidence and keep untouched qualification
   separate. Existing real images need no new annotation for this analysis. Do not
   quietly put evaluation members into training or declare sibling recipes independent.
2. **Target positive transfer, not just hard negatives:** real24 recall is1/8 artwork,
   2/6 listRows,0/3 tabs,0/2 otherFocusable; Photos button recall0/3. Collect native
   focused positives with matched competitor-focused negatives and measured geometry.
   Prioritize Photos-style buttons/tab focus, OS row geometry/context, then varied
   artwork/neighbor scenes. Background recolors alone do not address these failures.
3. **Scale as one scoped campaign:** inventory older eligible sources, freeze role/
   family reservations, then use automated native telemetry and resumable delivery
   against the existing6,000-pair scene/theme quotas. Recipe exemplar QA and minimal
   real transfer checks replace manual box drawing at volume. Generation authority,
   exact target/storage and producer capability remain a separate capture assignment.
4. **Starting-model audit:** the FDR-007 warm start is not the shipped baseline.
   Determine its real-source behavior before choosing another initialization; this
   tranche did not add unapproved inference of extra checkpoints. Preserve the
   shipped model's demonstrated Photos capability when defining future selection.

Ranked hypotheses, not proven causes:

- **Selection is unrepresentative — strong evidence:** all30 epochs pass18/18
  Settings retention while the selected model misses24/27 supported real positives
  across the two development sets. Next observation: representative independent
  validation performance, retained separately from final qualification.
- **Source/geometry/context transfer mismatch — supported, not isolated:** all
  three real Photos positives fail despite24 added native-button pairs; new row/tab
  analogs do not improve those control recalls. Reviewed sheets show source-specific
  pill shape, neighbor context and text layout. Counterexample: both native analog
  and real focused rows contain a bright background, so brightness alone is not
  an adequate explanation. Need controlled source/geometry coverage, not causal claims.
- **Initialization/optimization contributes — unresolved:** FDR-009 already loses
  transfer relative to shipped, and FDR-010 uses the same FDR-007 warm initialization.
  This run does not isolate data changes from initialization/selection interactions.

## Reproducibility and verification

- `approval.json`, `preflight.json`, `started.json`, `execution.json`, `training.log`:
  exact authorization/commands/one owned process/exit0/deadline. No network downloads.
- `verification.json`: all epoch scores recomputed using existing selection metrics;
  finite checkpoint, correct selected epoch/hash,18/18 floor and30 epochs verified.
- `comparison-freeze.json`: model/input/runtime/code bindings before inference.
  `batch01/02/03-candidate.json`, `photos-candidate.json`: all predictions/receipts.
- `comparison-summary.json`: same metric implementation across all three models.
  Shipped CoreML CPU scores reused; both candidate paths PyTorch CPU. No latency parity.
- `failure-index.json`:24 misses and7 false positives with exact IDs/images/crops.
  `worst-misses.png`: numbered full-frame context and existing production crops,
  visually inspected. Original labels and images unchanged.
- `export-decision.json`: retention/completeness/FP conditions pass, unique-selection,
  recall and Photos conditions fail; observerExportEligible=false.
- `adapter-tests-v2.log`6,`evaluator-tests.log`14, offline Swift build/test logs.

Initial Photos reuse preflight failed before inference because its legacy v1
coverage predates additive empty `focusRoles`. Verified identical rows/IDs/pairs/
hashes, added strictly empty-only legacy normalization and tests; no label changes,
no old protocol rewrite, no duplicate inference. No library/public API changes.
Existing dirty capture/intake changes from the preceding tranche were preserved.

[Production acceptance evidence map](production-acceptance.md) records the actual
quotas and six quality gates. [Research contract](../../../Research/Plans/FocusLimitedProduction.md).
No human action is needed to finish this run. The next campaign/selection policy
is a new assignment, not an automatically started second experiment.

[TTR coordination](coordination.md): no-export consequence published/read back.
Producer acknowledgment of the earlier row request and reported six nested pairs
was observed; new artifact intake was not performed. No owned processes remain.
