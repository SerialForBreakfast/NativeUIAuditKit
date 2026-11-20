# iOS framework taxonomy alignment

Status: proposed implementation sequence. Maximum-mini-NUIAK owns this work.

Use the tvOS class order for shared concepts. Maintain a separate iOS rule table for platform-specific constructions. Keep the historical iOS API and 5-class model decoder versioned. Report canonical classes first. Use legacy names only when reproducing old outputs.

| Priority | Deliverable | Acceptance |
|---|---|---|
| 1 | Emit construction and observation records from UIKitForm and one SwiftUI form. Join by instance ID, scene revision and screenshot digest. | A secure and ordinary input both emit textField. Filled and text-style actions both emit button. Preserve security, style and action role as attributes with provenance. |
| 2 | Project each visible object with a versioned rule and one disposition. Preserve ownership, reasons, source bounds and clipped bounds. | Same-action content belongs to its parent. A separate action keeps its target. An unclassified visible object withholds the full training frame. Check completeness against an independent inventory. |
| 3 | Qualify UIKitControls and UIKitList on compact and large profiles. Add matched UIKit and SwiftUI cases for equivalent controls. | A UISwitch emits toggle. A slider never emits toggle. A plain UIView row needs construction or interaction evidence before classification. An independently actionable child switch retains its own box. |
| 4 | Verify iOS geometry and data separation before expanding training. | Check all 4 edges against independent native or pixel references at 2× and 3×. Read the final class and box through the actual loader. Reject swapped images, missing owners, clipped-box errors and duplicate action labels. |
| 5 | Compare candidates on identical real-app flows with frozen roles and thresholds. | Report canonical roles, style and security breakdowns, omissions and unsupported controls. Count independent groups. Keep training examples and related variants outside qualification. |

Keep touch action bounds, visible content, selection, keyboard focus and accessibility focus distinct. Record unknown focus when the relevant observer supplies no evidence. Qualify the tvOS numerical geometry tolerance on iOS before making an iOS release claim.

Decide the iOS-only slider policy explicitly. Start a diagnostic slider role using UISlider and SwiftUI Slider examples. Require separate source groups, independent track and thumb evidence, and a matched test against true switches. Review that evidence before freezing another class index. Until that decision, record each slider and its disposition. An unresolved slider withholds the full frame.

The Form pilot checked 10 final boxes on 2 training seeds against a pinned template. It established transport for button, textField and bar. Its mapping still uses template IDs and legacy strings. It does not establish general construction-based intake across iOS.

[Shared tvOS contract](../Contracts/tvos-framework-projection-v1.md) · [Form projection](../../scripts/ios_form_projection606.py) · [Pilot evidence](../../reports/work/IOS606/qualification.json)
