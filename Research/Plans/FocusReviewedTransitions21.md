# FOCUS-REVIEWED-TRANSITIONS-21

Assigned October 1, 2026: finish the reviewed-recording diagnostic path while the
maintainer reviews the seven prepared Settings frames. Reuse retained inputs and
the fixed translation/brightness/growth policy; do not tune against these labels.

## Deliverables

1. Consume an explicit immutable human revision, validate its snapshots and exact
   recording binding, and overlay accepted controls in the endpoint audit. Preserve
   the frozen model protocol; conflicting old/new truth requires resolution.
2. Implement a retrospective pixel comparison CLI. Prediction sees before bounds
   and the two images only. After bounds and labels are scoring evidence, never
   tracking input. Require unique bidirectional geometric correspondence for scored
   controls; count ambiguity, abstention and wrong decisions explicitly.
3. Companion experiment: exercise translation, highlight polarity, growth, duplicate
   targets, missing targets and illumination using the actual pixel/native-crop
   path. Produce a reproducible case report in addition to assertions.
   While review is pending, optionally predict on verified pending after-images
   using accepted before-bounds. Keep these pixel-only observations unscored;
   pending proposals/checkboxes never supply truth or predictor geometry.
4. Integrate saved human review when available, run retained readiness, focused
   tests and offline Swift build/test, and publish one concise result.

## Interpretation

This is a retrospective development diagnostic, not runtime identity qualification.
Equal screen names and geometric overlap are assumptions to audit, not proof of
same-app context. Full-scene accuracy requires completeness on both endpoints;
partial annotations support only per-control diagnostics. Report zero support as
null, and report coverage beside conditional correctness. Preserve unknown context,
unattributed recording gaps and source provenance. No model or threshold selection
uses these results automatically. All artifacts remain project-local.

Limits: at most 32 action pairs and 256 controls per frame per invocation, resident
dependencies, fixed policies, no new model execution or dataset admission.

## Implemented commands

Use `.venv-yolo/bin/python` with project-local `TMPDIR` and bytecode disabled.
`focus_recorded_readiness.py` now accepts optional `--revision` and `--completeness`.
The new `focus_recorded_transition_eval.py` accepts the same arguments:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.build/tmp" .venv-yolo/bin/python \
  scripts/focus_recorded_transition_eval.py \
  --batch reports/work/FOCUS-REGRESSION-V2/office-trial-02/review-batch/batch.json \
  --pending reports/work/FOCUS-CAMPAIGN-09/artifacts/settings-review/batch.json \
  --baseline reports/work/FOCUS-VISUAL-05/artifacts/protocol-v2/protocol.json \
  --revision <saved-human-revision.json> --output <new-project-local-report.json>
```

`--observe-pending` additionally allows an accepted before-frame and verified pending
after-image to produce unscored observations. This mode reads neither mutable
checkboxes nor proposed after-bounds as truth. Different annotation screen labels
remain visible in its report. Scoring excludes changed screen labels pending context
resolution. The prepared `*-transition` labels differ from the older label names;
these naming differences alone neither prove nor disprove a screen transition.

Prediction uses translation-only matching and production crops with equal-size
windows; scoring uses unique, one-to-one same-class overlap at IoU≥0.5. This is a
geometric proxy and can still match unrelated same-class controls; report it as a
retrospective diagnostic rather than persistent identity. Coverage, unscored reasons,
abstentions, confusion counts and conditional correctness are separate fields.

The generated experiment is reproducible with
`scripts/focus_transition_stress.py --output <new-project-local-directory>`.
Its nine cases exercise the real native crop helper. Test success measures these
constructed manipulations, not general real-app focus accuracy.
