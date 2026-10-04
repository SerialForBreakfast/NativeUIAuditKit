# Qualified native rich rows: 24 pairs / 48 endpoint images

Use `qualified-cases.json` as the admission candidate inventory. Its 24 unchanged per-case bundles are under `corpus/splits/validation/`. They retain native labels, child/layout/body geometry, focus growth, viewport/offset observations, input/capture receipts, environment references and original hashes. No Office images or binaries are included.

12 appearance pairs cover compact/wide rows × dark/light backgrounds × first/middle/last targets, seed31, with a real focused competitor. Their viewport is stationary, all 24 common-window crop images pass, and zero crops need image-edge padding clamps. UIKit renders the focus effect; secondary text/icons/accessories and their measured children are present.

12 directional pairs comprise 8 retained no-scroll focus movements and 4 replacement scrolling focus movements. Their 52 common windows are measured; 14 unavailable/clipped/missing-endpoint windows remain explicitly excluded. Use full frames and per-frame geometry for scrolling; do not silently treat an absent control as an unfocused crop.

Four original directional cases had hidden/visible membership conflicts. Their image bundles are NOT included. `excluded-cases.json` links their original hashes to separately qualified replacements. Original full-campaign manifests/receipts remain unchanged under `source-provenance/` for ancestry; they can list excluded cases and must not replace the qualified selection. The two retained and replacement batches preserve all accepted originals.

Start review at `review/appearance/index.html`, `review/rich-directional-01/index.html`, and `review/rich-directional-replacement-02/index.html`. Magenta boxes show measured bodies. These are calibration candidates with shared `fixture_procedural_renderer_v1` ancestry, not independent holdout evidence. NUIAK owns training admission/model evaluation.

Self-service: coverage request version14, renderer_contract native-table-rich-v1, through existing campaign plan/generate/export/resume CLI/MCP. Original requests are in source-provenance. Appearance uses up to860points of viewport; directional uses480points. Build source through maintainer Git publication. Product hashes identify local validation only.
