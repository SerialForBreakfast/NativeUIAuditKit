# Twelve-image reference review

One grouped queue, all twelve images together. Boxes and focus states are prefilled.
The sample includes catalog artwork and guide rows, appearance changes, moved focus
after scrolling and unchanged focus after scrolling. All twelve have distinct pixels.

Check the visible control body bounds and the single focused control. For catalog
cards, the box includes the card title/body and follows enlargement. For guide rows,
check the full highlighted row; these rows change highlight without growing.
Partially clipped/offscreen controls were deliberately excluded by the producer.
This is review of the supplied visible controls, not a claim every partly visible
focusable control has an annotation. Leave completeness unchecked when uncertain.

The producer currently calls both families `primaryButton`. Those source classes
are preserved; this review primarily checks geometry and focus. Native Settings
rows and detector-specific taxonomy mapping are separate follow-up work.

Launch from the repository root, with the normal desktop execution context:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-review/bin/python scripts/human_review_editor.py \
  reports/work/REFERENCE-IMPORT-44/review-final/audit/review/batch.json \
  --queue reports/work/REFERENCE-IMPORT-44/review-final/audit/combined-queue.json \
  --runtime reports/work/REFERENCE-IMPORT-44/editor-runtime
```

Save corrections, then use Finish review. Calibration status remains in place until
the exact data-use decision. Ordinary corpus admission is not inferred from a crop check.

[Whole-corpus visual previews](review-final/review.md) ·
[Frozen review queue](review-final/audit/combined-queue.json) ·
[Crop QA](review-final/crops/crop-qa.json)
