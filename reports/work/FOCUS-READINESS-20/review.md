# Next human review: seven retained Settings frames

These are the existing pending frames, not another capture or a repeat of approved
artwork samples. Open the whole batch together; nothing needs copying between windows.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-review/bin/python scripts/human_review_editor.py \
  reports/work/FOCUS-CAMPAIGN-09/artifacts/settings-review/batch.json \
  --runtime reports/work/FOCUS-READINESS-20/artifacts/editor-runtime
```

Save/close any other annotation window first; the editor runs its native startup
check. Adjust proposed rectangles where rows moved, mark the actually focused control,
check completeness and leave uncertain frames pending. Do not mark settled solely
because the recorder selected a post-input frame. Use Finish review to save a revision.

Frames: **299, 310, 378, 391, 409, 446 and482**. Reviewing all seven completes missing
endpoint annotation for seven recorded actions. If time is limited,299/378/391
complete three. All seven are the recommended single review; no forced subdivision.
The other seven timing-ready actions need endpoints outside this prepared set.

This enables the next transition evaluation step; it does not yet verify same-screen
context, control correspondence, training use or successful navigation. No revised
labels have been inferred or approved automatically.
