# METRICS571 — Incorrect metric references

Owner: Maximum-mini-NUIAK. Date: November 4, 2026.
Authority: Joe requests an immediate audit of incorrect metric references.
This audit withdraws unsupported claims. It does not approve replacement metrics or promote models.

## Findings and corrections

| Finding | Evidence | Correction |
|---|---|---|
| RC561 211/211, precision 1.0, recall 1.0 | rc561_build_holdout.py copies candidate boxes and roles into references | Invalid circular accuracy. Disable generation and scoring. Preserve raw bytes. |
| RC561 replacement reports 82 controls, 50.00% recall, 19.43% precision, and improvement deltas | build_rc561_independent_ground_truth.py hard-codes agent-authored boxes without human review | Also invalid. A plausible lower score does not repair missing reference evidence. |
| WSP 10/10 pill recall | Export script and experiment log use scores above 0.01 instead of acceptance at 0.85 | Describe only a low-score diagnostic. Retain failed development gates. |
| WSP solves catastrophic forgetting | CurrentState and ExperimentLog generalize from retained legacy crops | Withdraw general solution claims. Preserving legacy decisions does not establish real-app focus. |
| Exported checkpoint embeds headline results | wsp_export_winning_model.py hard-codes 270/270 and 10/10 in metadata | Remove hard-coded metric fields. Store provisional status and the evidence reference only. Existing checkpoint bytes stay unchanged. |
| RC561 output proves generalization | ExperimentLog calls 211 predictions detected controls | Record predictions only. Labels do not establish correct controls. |
| SDK focus agreement counts unknown equality | Historical qualification report credits 1/10 unknown focus states | Mark superseded. The corrected qualifier rejects unknown agreement and unresolved-role equality. |
| SDK matching proves complete coverage | Qualification report describes 207 matching rectangles as every visible control | Limit claim to retained draft/reference agreement. Complete visible coverage requires review. |
| Historical focus 100% names the current model implicitly | CompletedTasks preserves Run010 focus result | Name 190/190 historical brightness-selector observations. It is not current FocusRing consumer accuracy. |
| Technical proposal predicts 93.0%, 91.6%, 4.5%, 99.7%, and 6.5 s | docs/nuiak_technical_audit_and_action_plan.md contains no matched execution for these projections | Withdraw numerical projections as evidence. Preserve original table in the audit snapshot. |
| Fixture guarantees exact labels and measured throughput | TVTestRigFixtureIdealVision claims perfect labels and 10,000+ frames per hour | Mark design targets, not measured accuracy. Require visible geometry, actual focus, clocks, and cleanup checks. |
| Legacy crop retention, backend parity, and tiny development sets reach 100% | Multiple scoped historical reports | Retain valid historical counts with their scope. Do not translate them into real-app accuracy. |

## Search scope

The inventory searches repository Markdown, HTML, Python, and Swift, including ignored work reports.
It excludes binaries, environments, raw queue JSON, and individual text files above 2 MB.
Raw RC561 metrics, labels, and manifests receive a separate exact-hash register.
The scan records 11,577 text files and 1,670 candidate references across 784 files.
These are search hits, not 1,670 confirmed false claims. They include CSS widths, split ratios, gates, warnings, and historical diagnostics.
The audit traces the RC561/WSP claims and their secondary references. It does not recompute every historical experiment.

- Before-change references: [inventory](../reports/work/METRICS571/references-before.json).
- Invalid or superseded raw artifacts: [register](../reports/work/METRICS571/invalid-artifacts.json).
- Before-change documents and scripts: [snapshot directory](../reports/work/METRICS571/before/README.md).
- Prior findings: [BreachOfTrustAudit20261103](BreachOfTrustAudit20261103.md).

## A perfect score is a review flag

1. Establish reference labels independently of predictions. Require actual review evidence.
2. Check training exposure, duplicate groups, selection history, and missing cases.
3. Freeze thresholds and score the actual consumer input path.
4. Report counts, class support, complete annotations, abstentions, and execution failures.
5. Distinguish training fit, supplied-box scoring, backend agreement, and independent full-screen evaluation.
6. If references fail, withdraw all dependent accuracy claims. Preserve the raw evidence.
7. Present provisional evidence to Joe before publishing accepted metrics or promoting models.

A 100% value is not automatically false. It is never sufficient evidence by itself.

## Remaining qualification

Keep the 8 exposed RC561 screens as development evidence. Obtain blinded labels and reserve fresh application flows.
Verify SDK geometry and actual focus before automatic labeling. Accessibility drafts alone do not establish complete reference labels.
Preserve Standard, shipped weights, original captures, evaluation exclusions, and previous successes.
No capture, training, inference, export, or promotion occurs in this audit.

## Model registry follow-up

The additional scan covers model contracts, tools, and trainer source. The model registry incorrectly assigns a historical perfect focus result to the current detector. Its comment now identifies the generated-screen scope and different brightness selector. Model values and resource bytes remain unchanged. See [additional references](../reports/work/METRICS571/references-models-tools.json).
