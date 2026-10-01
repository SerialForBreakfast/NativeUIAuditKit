# Native-body visual acceptance — September 30, 2026 PDT

Scope: agent inspection, not a replacement for the user's human sample or a claim
that every emitted control was visually checked. Native measured rectangles are
proposals until accepted under the existing corpus policy. No source annotations
were changed.

Six representative side-by-side overlays in
`artifacts/native-body-review/geometry/` were inspected:

| Frame | Observation |
| --- | --- |
| 002 / 613886646931c9fb4ebdb976 | Light dialog focused action box follows enlarged white button; excludes shadow and dialog container |
| 006 / c0579f468279c9dccab67c76 | General row body extends beyond original layout box; adjacent resting rows remain bounded |
| 012 / 8c891f4c125ede91a51166b8 | Focused Discover tab distinguished from selected-but-unfocused Library; artwork bodies exclude captions |
| 016 / a605e5718f9d04c018f253ac | Focused artwork child grows; selected Library parent is not labeled focused; caption remains outside body |
| 018 / 6f66020cb4d4509e54c111ef | Dark wide button grows; ordinary neighboring buttons retain resting bounds |
| 024 / f4d67c60a1f652784f299a62 | Light wide button body matches enlargement, excluding shadow |

The focused General256×256production crop was also inspected. Its anisotropic
shape follows the existing fixed-size preprocessing, not a geometry-export error;
no preprocessing change was made.

All154expected crops passed automated production QA. Eight excluded dialog-container
observations are nonfocusable containers, not eight missing action boxes. Semantic
child exclusions remain recorded. Original16capture pairs create28derived
same-control relationships; do not call these28new captures. Target-limit exclusions
remain visible in each bundle's targetCoverage, so this is not exhaustive traversal.

The three-image native audit queue is prefilled but not human-approved. The earlier
five-frame/twenty-control user acceptance remains limited to SYN-06-BODY. No request
to redraw or reapprove those accepted images is made.

## Palette/long-row follow-on

All nine bundles pass intake and320/320crops. Agent inspected the high-contrast
long/duplicate rows (`012-frame-90154e3afb6d3bbe4099830b.png`), high-contrast tabs
(`036-frame-283281df72e446f4beec8556.png`) and light long/duplicate rows
(`018-frame-3810dd7dc2bfd4c112f249d2.png`) under `artifacts/palette-review/geometry/`.
Focused solid bodies follow enlargement; duplicate text does not collapse control
identity, selected tabs are distinct from focus and shadows remain outside boxes.
This is representative agent review, not an exhaustive visual or human pass.

The palette review queue contains four unique images (three seeded-random images
plus exception coverage after union/deduplication). It is prefilled and unreviewed.
Source archive's174listed members remain unchanged after QA. Across the three
body batches, local original-image SHA grouping independently reproduces77unique
images/126observations and the producer's exact four cross-recipe overlap entries.
Keep those connections together; neither duplicates nor appearance-only variants
create independent validation data. No split was assigned.
