# Eight prefilled artwork verification frames

[Numbered visual preview](artifacts/analysis-final/review.md).

No work is required while you are remote. These are prepared for later review,
not approved annotations. There are four families: blank placeholders, faint
placeholders, pale marks and white marks. Each queue has one focused and one
unfocused target drawn randomly with seed42 from its supported state population.
This small sanity sample does not establish a population defect rate.

Check the green box against actual input focus, the enlarged body bounds, and
missing/incorrect controls. Orange boxes are unfocused. A selected parent tab
can remain highlighted while input focus is on an artwork tile. Boxes exclude
the glow/shadow; do not redraw correct boxes or fill optional descriptions.

The supported editor launcher checks Qt automatically. Choose one family, save
and close before the next; do not start bare Labelme:

```sh
review_family=white_owned_mark
PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.build/tmp" .venv-review/bin/python scripts/human_review_editor.py \
  "reports/work/FOCUS-ARTWORK-08/artifacts/balanced-review/$review_family/review/batch.json" \
  --queue "reports/work/FOCUS-ARTWORK-08/artifacts/balanced-review/$review_family/combined-queue.json" \
  --runtime "reports/work/FOCUS-ARTWORK-08/artifacts/editor-runtime-$review_family"
```

Other values: `pale_owned_mark`, `blank_placeholder`, `faint_placeholder`.
Only the two queued frames should appear. Use Finish review when correct; leave
uncertain cases pending. Human visual approval does not erase missing capture
provenance or silently admit data into training.
