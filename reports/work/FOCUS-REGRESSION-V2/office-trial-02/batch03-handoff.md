# Batch 3 — retained diverse states

Prepared eight frames in `review-batch-03/batch.json` and launched the existing
rectangle editor. Completed batches and originals are unchanged.

| Frame | Visual selection rationale (not confirmed labels) |
|---|---|
| 306 | Settings, Remotes and Devices row highlighted |
| 536 | Home Settings tile with Settings top-shelf background |
| 724 | Populated App Store featured cards, Prime Video card |
| 751 | App Store Now Streaming shelf, Paramount+ tile |
| 858 | App Store categories and ranked Top Free rows |
| 1043 | Search keyboard plus results, YouTube TV card |
| 1087 | Lower search results, Pluto TV card |
| 1105 | Same results layout, Fubo card |

All eight retain producer `postInputUnverified` roles. Human settlement, content
approval, labels and bounds remain pending; no flags were preconfirmed. Different
frames from this recording are related development evidence, not independent sources.
The two lower results frames intentionally preserve different focus targets rather
than discarding them for similar backgrounds. Artwork also varies.

Verification: existing `human_recording_review.prepare` and `validate` succeeded;
all eight original hashes, dimensions and pixel digests checked; no exact pixel
duplicates within batch or against the prior sixteen frames. Editor PNG hashes
match raw imports. All initial shape lists empty and frame flags false.
Selection contact sheet: `review-batch-03/selection.jpg` (gitignored).

Software: existing tools reused without implementation changes; no new build/test
required. Data: ready for human diagnostic review, not training admission.
Integration: actual editor launched with no startup error (session95155).
Model gate: unassessed; no inference/training. Shared coordination: not applicable,
no changed TTR next action. Optional Suggest box remains default-off. Presets and
copy/paste remain available; bounds/focus must be checked per frame.

Next: human annotation and Finish review; then validate the immutable revision
and perform production crop QA. Pending or unsettled examples remain excluded.
