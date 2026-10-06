# Retention feasibility212 — reject the shortcut

2026-10-06. CPU-only fixed composition: all Run019 non-page outputs plus all
Run028/211 page outputs. Same identities/dimensions/settings verified; non-page
per-class results asserted equal to019. No classwise winner selection, new inference,
training, threshold search or production integration.

Read-only evaluation exited0 (session26975). Aggregate mAP50=0.8958877117,
mAP50:95=0.8536100398. Page results remain75TP/4FP development and543TP/7FP
retained. Reused evaluations are not new independent qualification.

| Retained class | Support | TP | FP | FN |
|---|---:|---:|---:|---:|
| cancelAction |80|76|73|4|
| mapView |100|100|0|0|
| scrollIndicator |100|0|0|100|
| sheet |24|24|218|0|

Run022/211 detects80cancelAction and26scrollIndicator targets. Restoring019 would
lose four and26hits respectively. Sheet precision remains24/242=9.92%. Scroll
AP50=0.3481 despite zero operating hits: AP and operating recall differ.
Copying a baseline guarantees retention equality, not usefulness. No complete
gate-assessment invocation or model pass is claimed.

Fresh execution needs three models:019full frame,022full-frame proposals and028
crops. No fresh latency measured. **Reject as a production shortcut.** Next work must
improve absolute operating behavior as well as retention; do not repeat replay or
promote on aggregate AP alone. Use corrected worker accounting for candidate design.

Evidence pins:

- 019checkpoint: `ecfb0195250e65d9bbbc0954e9e1714af60685d5e1123d5dd0e0784dcdadb378`
- 019combined predictions: `2bcce3ae03586ff63b723966bb5d612c7f8aeded0234e9f8710896a143260910`
- 019page predictions: `59bd458e90207c6a3b7d14f99bf6ec5100c6c1a38ab2970bbeb7d147f2867895`
- 211evaluation: `2201df77e798395365546ea6669efd4e03ecff702672d0219bf84d950b21897b`

Source artifacts remain in IOS-PLACEMENT-173 and IOS-PRECISION-211. Analysis-only
decision: prior integrated software checks unchanged, not rerun.
