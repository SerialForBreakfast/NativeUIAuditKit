# iOS sheet visibility for detector training

Scope: opaque, stationary system sheets on the two measured lists. Use original, clean screenshots as detector inputs. Use white and black calibration fills only to measure the sheet silhouette. Inspect the clean surface and verify stable decisions across coverage thresholds. Withhold unknown opacity or mismatched masks.

| Underlying control | Detector label |
|---|---|
| Fully visible | Keep its original clipped interactive body and canonical role. |
| Partly visible, one connected region | Keep the tight axis-aligned rectangle around the visible region. Record its mask-derived visible fraction and original body separately. |
| Fully covered | Record the control as hidden by the sheet. Emit zero boxes for this control. |
| Multiple disconnected fragments | Preserve fragment coordinates. Withhold the full image from current rectangular-box training. |
| Presented sheet | Emit one dialog box around the opaque sheet body. Exclude its dimming layer and shadow. |

Resolve the row and accessory separately. A covered accessory does not remove a visible row. Keep captions owned by their controls. Modal presentation may disable interaction with a visible underlay. The detector describes visible geometry; navigation must use modal state independently.

Use four-connected source pixels and half-open top-left rectangles. Keep each original group across scales and presentation states. These are iOS development rules. The existing tvOS Q3 v1.0 key retains its own documented underlay convention.

[Verifier](../../scripts/verify_sheet_visibility610.py) · [Visibility implementation](../../scripts/ios_sheet_visibility610.py)


## Translucent and moving surfaces — Simulator pilot

Measure the sheet footprint and the evidence for each underlying control independently. Keep a full control box behind a translucent sheet only when its own body remains observable. A tint change alone cannot establish a control edge. If the measurement cannot distinguish an edge, record it as unresolved. Withhold a complete training frame that contains an unresolved control.

In the colored-list pilot, the row occupies the viewport width. The verifier checks both horizontal boundaries. Each independently actionable accessory has four contrast checks. These are recipe-specific observations; other materials and controls need suitable reference measurements. A matched opaque render checks whether the covered control loses its edge evidence.

Use the compositor image for motion geometry. The display-link trace supplies a range of possible presentation positions across the screenshot interval. Admit a settled sample only after repeated positions agree and the measured sheet edges match native geometry. Retain moving frames as related temporal development evidence. Neither a callback nor elapsed delay alone proves settlement.
