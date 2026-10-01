# SYN-03 — native batch crop QA and review handoff

**Human-review correction,2026-09-30 PDT:** focused artwork visibly grows beyond
the exported uniform wrapper rectangles. Geometry alignment for these growth
samples is not accepted; training remains held.60/60below is crop execution, not
rendered-body correctness. See `Research/Requests/TTR-Rendered-Control-Bounds.md`
and `coordination.md` for the published repair request. Original artifacts unchanged.

Completed for review,2026-10-01 UTC. No runtime/device operation, training,
inference, admission or promotion. TTR independently supplied current emitted data.

## Acceptance evidence

| Assigned outcome | Observed result |
| --- | --- |
| Actual consumer path | `scripts/fixture_batch_review.py` imports existing native sidecars, production cropper, random/exception audit, existing editor and Finish review |
| Current emitted data | `artifacts/live-review-r2/report.json`: image1,row1,tabs3 captured pairs;10frames;60/60crops |
| Sampling burden |10frames,8eligible after2exact aliases;3random plus3exception selections overlap into5unique review frames; population/seed/exclusions in audit plan |
| Source preservation | `emitted-verification.json`:79manifest members verified before/after;58repair members in `delivery-verification.json` |
| Partial accounting | Rows campaign `halted_budget_exhausted`,one completed case/one unattempted; target exclusions remain in each bundle's coverage, no whole-campaign pass |
| Negative | Untouched corrupt derivative rejected by full sidecar importer at `scene_alias_conflict`; direct inventory validator independently rejects `visible_outside_frame` |
| Compatibility | Source-pinned hero/contrast recipe identity; corrected secondaryButton and legacy primaryButton supported without relabeling; other hierarchy checks retained |
| Retained regression |3prior pairs/6frames,36/36crops; no renewed human approval requested |
| Annotation integration | Installed offscreen Qt smoke: queue filtering, rectangle prefill, unconfirmed flags, clean load; real Finish preview/apply covered by isolated software tests |
| Tests |46TTR,26fixture (includes11batch-review),12bundle,135human tests pass; Swift build,120Swift Testing+14XCTest pass; diff check clean |

The10reported same-control focus-change relationships are derived from5captured
pairs (targets and competitors), **not10independent captures**. This is diagnostic
data, not an independent validation split despite producer directory names.

Observed sheets show artwork controls,8settings rows and selected-parent tabs.
On the child-focused tab frame, Browse is selected/unfocused while Popular is
focused. Production crops retain those distinct labels. Measured wrapper rectangles
do not claim to segment enlargement, shadows or glow. Agent visual inspection is
not human verification or model qualification.

## Reproduce batch QA

From the repository root, use a fresh output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/fixture_batch_review.py \
 --bundle reports/work/SYN-03/artifacts/emitted/ttr-emitted-native-acceptance-20261001-r1/image/splits/validation/image \
 --bundle reports/work/SYN-03/artifacts/emitted/ttr-emitted-native-acceptance-20261001-r1/rows/splits/validation/rows \
 --bundle reports/work/SYN-03/artifacts/emitted/ttr-emitted-native-acceptance-20261001-r1/tabs/splits/validation/tabs \
 --protected-metadata reports/work/APPEAR-B/protected-evidence.json \
 --output reports/work/SYN-03/artifacts/replay-next --count 3 --exception-limit 3
```

All input outcomes are retained. CLI exits2 when any bundle rejects; accepted
bundles still receive QA. Failed crop work retains intake and explicit failure;
it does not emit a completed report. Source changes invalidate the sealed batch.
Protected metadata/splits/byte hashes are checked before source image decoding.

## Prepared human review (not opened automatically)

Startup repair,2026-09-30 PDT: the original manual launch crashed on Next because
Labelme's deferred directory-first callback escaped the sampled queue. Constructor
now starts empty, then populates and loads the chosen queue synchronously.136human
tests and actual five-frame forward/backward traversal pass; saved JSON unchanged.
Swift build and120+14tests pass. GUI launch also needs the existing Qt framework
lookup below when plugins are copied into the local hidden-file workaround cache.

```sh
DYLD_FRAMEWORK_PATH="$PWD/.venv-review/lib/python3.12/site-packages/PyQt5/Qt5/lib" \
PYTHONDONTWRITEBYTECODE=1 .venv-review/bin/python scripts/human_review_editor.py \
 reports/work/SYN-03/artifacts/live-review-r2/audit/review/batch.json \
 --queue reports/work/SYN-03/artifacts/live-review-r2/audit/combined-queue.json \
 --batch-index 1 --runtime reports/work/SYN-03/artifacts/annotation-runtime
```

Verify proposed control bounds and actual focus; selected Browse is not another
focused control. Labels and rectangles are already populated. Finish review records
only the human's explicit approvals. Native coverage is instrumented/partial, so
do not auto-assert exhaustive annotation from native inventory alone.

## Next boundary

SYN-02/03 representative integration is no longer waiting on TTR.30new source recipes
map60coverage slots but this proof renders only3representative older recipes.
SYN-04 still needs source/structure/content role review; colors/seeds alone do not
create independent evaluation. SYN-05 offline resume/accounting can now build on
this path, while TTR qualifies broader combinations. No new training run is assigned.
Coordination result is in `coordination.md`; sender owns shared-copy cleanup.
