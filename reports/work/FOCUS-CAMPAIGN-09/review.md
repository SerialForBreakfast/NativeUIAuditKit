# Prepared human review

Nothing needs drawing from scratch for the synthetic sample. Check that the
green focused control and enlarged body bounds match the picture; the other
bright white target must remain unfocused when its neighbor has focus. The
selected Discover tab can remain bright without being input-focused. Inspect
all shown rectangles for obvious errors. Do not include the shadow in bounds.

Six screens, three two-frame queues. All approvals are unset. These checks
do not automatically approve training use or independent evaluation.

| Design | Source batch (under `artifacts/intake-v3/`) | Queue |
|---|---|---|
| White mark | `white-mark-1/theme-state-review/review/batch.json` | `white-mark-1/theme-state-review/combined-queue.json` |
| Pale mark | `pale-mark-1/theme-state-review/review/batch.json` | `pale-mark-1/theme-state-review/combined-queue.json` |
| Placeholder | `placeholder-1/theme-state-review/review/batch.json` | `placeholder-1/theme-state-review/combined-queue.json` |

Use the existing `.venv-review/bin/python scripts/human_review_editor.py BATCH
--queue QUEUE --runtime reports/work/FOCUS-CAMPAIGN-09/artifacts/editor-runtime`
from the repository root, with the full project-relative paths above. It runs
the native startup check automatically. Save/close between queues; never launch
a replacement over an unsaved editor. Native doctor passed in the host context.

## Six native annotation previews

### White mark: dark/unfocused and light/focused

![White dark](/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/FOCUS-CAMPAIGN-09/artifacts/intake-v3/white-mark-1/theme-state-review/frame-699508f47124e4b61e3c00ff.png)
![White light](/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/FOCUS-CAMPAIGN-09/artifacts/intake-v3/white-mark-1/theme-state-review/frame-ccf540510baa7f5c381b4441.png)

### Pale mark: dark/focused and light/unfocused

![Pale dark](/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/FOCUS-CAMPAIGN-09/artifacts/intake-v3/pale-mark-1/theme-state-review/frame-731a04d421f17d6dc6a6e447.png)
![Pale light](/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/FOCUS-CAMPAIGN-09/artifacts/intake-v3/pale-mark-1/theme-state-review/frame-547130c250567bd9e2deb4bb.png)

### Placeholder: dark/unfocused and light/focused

![Placeholder dark](/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/FOCUS-CAMPAIGN-09/artifacts/intake-v3/placeholder-1/theme-state-review/frame-2a600ecad88cdee172909438.png)
![Placeholder light](/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/FOCUS-CAMPAIGN-09/artifacts/intake-v3/placeholder-1/theme-state-review/frame-0049c0a6f81c7460509f4295.png)

## Later: seven real Settings endpoints

Batch: `artifacts/settings-review/batch.json` (no queue argument). Seven frames
already have rectangle proposals. They came from related screens, so adjust any
shifted rows, add missing visible controls, and mark the genuinely focused item.
No focus state, content approval or settlement was copied. Only mark settled if
the retained image supports it; unverified capture roles remain preserved.

These are for the before/after experiment, not required for the artwork training
comparison. Prioritize 299, 391 and 482 if reviewing a smaller subset first;
remaining endpoints cover additional screen transitions. Finish review may leave
uncertain frames pending. The old approved endpoints remain untouched.

![Recovered Settings endpoints](/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/FOCUS-CAMPAIGN-09/artifacts/settings-review/overview.png)
