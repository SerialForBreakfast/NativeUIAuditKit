# Six prefilled checks — human-approved October 1, 2026

Maintainer confirmed “perfect alignment set. approved”. Saved revision contains
six reviewed frames;44others remain blocked. [Acceptance](sample-acceptance.md).
The preparation/launch instructions below are retained as history, not a request
to repeat the completed review.

October1PDT review session: opened all six together at the maintainer's request.
Native Cocoa startup passed (`58c915aa5d40484ca60fa1d92d1cb05d`); process11474
remained running after launch, log `review-launch.log`. No prior editor was running.
Human acceptance and training-use designation remain pending.

All six open together using the existing annotation flow. Nothing needs drawing
from scratch. Check the focused control, actual enlarged image-body bounds and
the unfocused white/pale target when the neighboring card has focus. Bounds exclude
the shadow and separate title footer under this producer's image-body contract.
The selected Discover tab is not necessarily input-focused.

From the repository root, when no unsaved annotation window is open:

```sh
env PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.build/tmp" \
  .venv-review/bin/python scripts/human_review_editor.py \
  reports/work/FOCUS-INTAKE-13/artifacts/intake/audit/review/batch.json \
  --queue reports/work/FOCUS-INTAKE-13/artifacts/intake/audit/random-queue.json \
  --runtime reports/work/FOCUS-CAMPAIGN-09/artifacts/editor-runtime
```

No `--batch-index`: this is one six-frame queue. The editor performs its existing
startup check. No unsaved window was touched.
All review/content/settled approvals and shape confirmations were unset at preparation;
the active review may now change them.

Seed42 simple random sample from50frames: three focused targets, three unfocused;
white and pale artwork, dark and light named/background variants. These are related
catalog layouts, not independent real-world examples or a high-confidence defect bound.
The recipe's top-level `theme` remains dark even for light background variants;
use the rendered background/composition, not that field, to assess appearance.

The separate exception queue is retained, not silently discarded. All50frames have
the same two flags: selected-but-unfocused control and nonfocusable/unsupported
taxonomy exclusion. They do not mean50distinct box defects. Review the selected tab
and excluded decorative hero once in context; any actual defect requires broader
investigation. No automatic waiver, confirmation or training admission follows.

Human review and training-use designation remain separate. I recommend prioritizing
new structural examples over admitting these merely to run the same experiment again.
