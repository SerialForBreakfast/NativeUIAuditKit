# Eight structural sample checks — one batch

The sample covers composite cards, hero cards, home icons and ranked rows, with
focused and unfocused target examples. All rectangles and labels are prefilled.
All eight frames were loaded through the installed annotator in an offscreen check;
22rectangles loaded, each frame has one focused control, and none was preapproved.

For each frame, check:

1. The rectangle follows the visible control body, including focus enlargement,
   excluding the shadow/glow. Clipped controls should use their visible body.
2. The focused circle matches the visibly focused control. Selected content and
   artwork brightness alone are not focus.
3. Roles and included controls are sensible. Flag anything uncertain rather than
   correcting a systemic producer error repeatedly.

Use the frame flags and Finish review after all eight. The review confirms sampled
annotation quality; the separate source-role decision determines training use.

Queue: `artifacts/campaign-intake/attempt-001/audit/combined-queue.json`.
The queue carries its exact batch reference; launch through the existing
`human_review_editor.py --queue <queue> --batch-index 1` flow with that batch and a
project-local runtime. Keep the prepared queue together, not two frames at a time.

[Successful UI check](artifacts/review-ui/result.json).
