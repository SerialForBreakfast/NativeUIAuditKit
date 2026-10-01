# Composition D1 — six prefilled verification frames

Two randomly selected, nonduplicate frames per layout, seed 42. This is a small
geometry/label sanity check, not statistical qualification or training approval.
Every visible focusable candidate is already boxed, including tabs. No redraw is
needed unless a proposal is actually wrong. Original calibration roles remain intact.

Check that the green box is the actually focused control, orange controls are
unfocused, and boxes follow each rendered body—including enlargement—not its glow
or a fixed layout slot. A selected parent tab may look highlighted without holding
input focus. Check missing controls, but do not annotate decorative backgrounds/text.
If any frame is ambiguous, leave it pending rather than force approval.

Exact sample IDs, original hashes and queues are in [coverage.json](artifacts/coverage.json).
These are consumer production-body overlays, not producer common-window crops.

## Catalog

![Catalog sample 1](/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/FOCUS-APPEARANCE-06/artifacts/review-preview/01-catalog-v1.png)

![Catalog sample 2](/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/FOCUS-APPEARANCE-06/artifacts/review-preview/02-catalog-v1.png)

## Detail

![Detail sample 1](/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/FOCUS-APPEARANCE-06/artifacts/review-preview/03-detail-v1.png)

![Detail sample 2](/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/FOCUS-APPEARANCE-06/artifacts/review-preview/04-detail-v1.png)

## Library

![Library sample 1](/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/FOCUS-APPEARANCE-06/artifacts/review-preview/05-library-v1.png)

![Library sample 2](/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/FOCUS-APPEARANCE-06/artifacts/review-preview/06-library-v1.png)

## Optional editor review

From the repository root, choose one layout at a time (`catalog-v1`, `detail-v1`,
`library-v1`). Save and close before opening the next. The supported launcher runs
the Qt startup check automatically; do not launch bare Labelme.

```sh
review_layout=catalog-v1
PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.build/tmp" .venv-review/bin/python scripts/human_review_editor.py \
  "reports/work/FOCUS-APPEARANCE-06/artifacts/final-$review_layout/audit/review/batch.json" \
  --queue "reports/work/FOCUS-APPEARANCE-06/artifacts/final-$review_layout/audit/combined-queue.json" \
  --runtime "reports/work/FOCUS-APPEARANCE-06/artifacts/editor-runtime-$review_layout"
```

Only the two queued images should appear. Confirm frame flags only after checking
their meanings. Finish review saves a diagnostic revision; it does not admit training
data. No annotation window was launched by this preparation tranche.
