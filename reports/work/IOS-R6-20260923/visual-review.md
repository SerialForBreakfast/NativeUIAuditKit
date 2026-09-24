# Six native visual probes — 2026-09-23

Reviewed all six annotation overlays after strict intake passed against independently
retained catalog-v2 seed19, SHA256
`637a434c2c888641204709ce9c3712b8001ee289d1b79a0c38dd5cd794f61929`.
Exact targetF3EF9DB8-0B0F-4757-B653-D1628269F6FF, iOS26.5,
1179×2556 pixels,3× profile. Probe membership remains development-only.
Raw files and overlays: `.build/debug-output/ios-r6-execution-20260923/` under
`visual-probes/` and `overlays/`. Independent intake: `probe-intake.json`.

| IDs / image files | Observed result | Limits |
|---|---|---|
| UIKitControls:19:probe-0/1; probe-000/001 | Actual dark/light rendering; slider, segmented control, spinner, progress, page dots, toggle, secure field and Reset All bounds align with rendered control extents. | The selected segment is visually Dark in both; it is content state, not the appearance selector. Twelve UIControl observations report enabled=true, selected=false. These are native UIControl getters, not `UISwitch.isOn` or selected-segment identity. Other states remain null. No disabled-state coverage claim. |
| ChromeCoverage:19:probe-0/1; probe-002/003 | Black/white backgrounds and contrasting text, status artwork, rows, tooltip and scroll indicator are visible; boxes align. Clock changes09:41→12:30; connectivity/battery artwork visibly differs. | These are controlled synthetic chrome drawings, not changed OS settings. Several axes change together, so this is not an isolated charging/contrast experiment. Stage Manager chip stays `unknown`; no new taxonomy class is implied. SwiftUI states are null. |
| DynamicTypeOverflow:19:probe-0/1; probe-004/005 | Dark/light rendering, six visibly oversized and truncated labels; overlay boxes align with constrained label frames. Known issue `dynamicTypeOverflow` is retained. | AXXXL is fixed. Text clipping/truncation is inside control bounds, not image-boundary clipping: excluded=false/occluded=false is consistent with that narrower annotation meaning. No multiple-size rendering claim. States are null. |

Every selected ID, image/annotation hash, PNG dimensions, schema1.2/config and
coordinate relation passed intake; zero decoded duplicate groups. Review qualifies
these six representative development renderings only. It does not qualify the144-case
catalog, complete visual-axis coverage, a training addon, model quality or DS-G8.
The receipt remains unchanged (`captured_pending_visual_review`); this review record
supplies the separate agent visual assessment, not a rewritten capture receipt.
