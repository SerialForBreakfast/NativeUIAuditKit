# TVTestRig Fixture Batch Ingest

**As of:** 2026-09-18  
**Related:** TASK-6a-10 in [`../Tasks.md`](../Tasks.md), [`tvOSTrainingStrategy.md`](tvOSTrainingStrategy.md), BP-28, BP-40–BP-45  
**Scripts:** `scripts/ingest_fixture_batch.py`, `scripts/test_ingest_fixture_batch.py`

How NativeUIAuditKit consumes `aatv fixture batch` output. Do not re-derive this from chat history.

---

## What the harvester writes

On-disk layout (TVTestRig FIX-Synth-02, 2026-09-18):

```
<id>_unfocused.png
<id>_focused.png
<id>_metadata.json
manifest.json          ← TVTestRig train / calibration / held-out split
```

Metadata uses canonical snake_case: `element_id`, `taxonomy_class`, `normalized_bounds` (`HarvestPairMetadataFile`). `GET /scene` returns non-empty `elements` with `scene_width/height: 1920×1080`.

The 41-class taxonomy still matches `Research/schemas/category_map.json` index-for-index (`Scripts/native-ui-tvos-decoder-manifest.json` in TVTestRig).

---

## Ingest rules (`ingest_fixture_batch.py`)

- Convert to `annotation.schema.json` v1.0 sidecars for `export_tvos_coco.py`.
- Unknown `taxonomy_class` values are dropped and counted, never remapped (BP-28).
- Deduplicate the shared baseline `_unfocused.png` per recipe. Force those elements' `isFocused=false`. The baseline frame is reused across every focus step; its `elements` list reflects whichever row is focused — ingesting it naively would label glow on a frame where nothing is glowing.
- Full-frame preservation: no ROI cropping. Perception-layer deltas/dedup are for capture *selection* only.
- Honor TVTestRig `manifest.json` splits. `held-out` is a second holdout, distinct from the synthetic withheld-template split.
- Refuse to write outside the package.

Offline self-test: `scripts/test_ingest_fixture_batch.py` (16/16 against hand-built fixtures matching this layout).

---

## Do not use as training labels

Every JSON sidecar under `dataset/` checked 2026-09-18 (including `tvos_fixture_captures/`) had `"elements": []` until live harvest. Files named `*_result.json` next to captures are **the current model's own predictions**, not ground truth. Training on them is circular.

---

## Current blockers (live batch)

1. **Coordinator IPC.** `aatv fixture batch` needs the TVTestRig macOS coordinator over local IPC, not only the fixture HTTP endpoint. `open TVTestRig.app --args --project <path>` left a live process, but `aatv status` / `doctor` / `fixture batch` returned `serviceUnavailable`. Filed as [`reports/tvtestrig_feedback_2026-09-18.md`](../reports/tvtestrig_feedback_2026-09-18.md). Reproduces on Simulator; not an Office-hardware issue.
2. **Office hardware.** TVTestRig's own notes: live office harvest is a separate authorized run. Do not trigger it unprompted. Re-verify this ingest format against real batch output before training.

FocusRing live harvest (`scripts/harvest_focus_pairs.py --live`) is a *different* path: N-way navigate inside TVTestRigFixture, container socket via `NativeUITrainer/.tmp/aatv_home`. That path already produced 1,500 pairs. Do not confuse it with `aatv fixture batch`.

---

## IPC notes (FocusRing / aatv)

- Coordinator socket lives at `~/Library/Containers/com.showblender.TVTestRig/Data/.tvtr/.tvtr/s`.
- `aatv --project <checkout>` looks at the repo `.tvtr/s` and reports `serviceUnavailable` for the sandboxed Debug GUI.
- Do not set `TVTESTRIG_PROJECT` for that GUI (sandbox cannot write the checkout).
- Point `HOME` at `NativeUITrainer/.tmp/aatv_home` with a symlink to the container socket. Never set `HOME` to the container Data root (`Evidence/Sessions` listdir hangs).
- Do not listdir container `Evidence/Sessions`.
- Closed-loop `navigate --count 1` only (BP-40). No Home, no Select, no Settings crawl.
