# Role taxonomy 1.2 (2026-11-22)

Joe, in chat on 2026-11-22: "Add role types".
This is a software contract only. It adds no model weights, no training data and no model promotion.

## Why

The TRAIN666 detectors (D1, and arm F of [H3](../Plans/H3Focus666.md)) use the role labels of `scripts/roles559.py`.
The Swift library accepted only the 41 legacy labels, and `NativeUIElementType` had no case for 8 roles.
On AX-dev, Swift dropped all `cell` and `button` boxes of D1: 296 of 358 boxes (seed 371) and 280 of 361 (seed 372).

## Taxonomy and identity

Taxonomy 1.2 is taxonomy 1.1 followed by the `append` entries of `category_map.v1.2.json`.
IDs 0–41 keep their meanings. The 8 new IDs are:

| ID | Role | Supercategory | Legacy types that the role covers (`roles559`) |
|---|---|---|---|
| 42 | `button` | controls | `primaryButton`, `secondaryButton`, `destructiveButton`, `cancelAction`, `menuButton`, `link`, `disclosureGroup` |
| 43 | `picture` | content | `imageView`, `mapView` |
| 44 | `adjustable` | controls | `slider`, `stepperControl`, `picker`, `colorWell` |
| 45 | `cell` | containers | `listRow`, `collectionItem` |
| 46 | `bar` | chrome | `navigationBar`, `tabBar`, `toolbar`, `sidebar`, `statusBar` |
| 47 | `dialog` | containers | `alert`, `actionSheet`, `sheet`, `popover`, `contextMenu`, `tooltip` |
| 48 | `indicator` | indicators | `activityIndicator`, `progressView`, `scrollIndicator`, `refreshControl`, `homeIndicator`, `dynamicIsland` |
| 49 | `container` | containers | `webContent` |

The other 4 roles (`textField`, `toggle`, `segmentedControl`, `pageControl`) already have the same raw value as a legacy type.
A role is coarser than a legacy type. A role observation does not claim the finer legacy type.

`categoryMapSHA256` uses the method of [badge-category-binding-v1](badge-category-binding-v1.md).

| Version | Resolved taxonomy SHA256 |
|---|---|
| 1.2 | `05c0f47c7d81d676271627ee85e0374fb99a57f408ca15a25d1642963be642c2` |

## Model manifests

- Only a manifest with `taxonomyProfile: nativeui-category-binding-v1` and `taxonomyVersion: "1.2"` can emit the role types.
- A manifest without a profile keeps the frozen legacy label set. The shipped iOS and tvOS manifests do not change.
- A role model declares its own channel order, for example D1's 10 channels.

## Focus candidates

`cell`, `button`, `adjustable` and `bar` are focus candidates in Swift, with the legacy focusable types.
This matches `tvbench._is_focusable_class` for role models, which produced the H1 and H3 scores.
`bar` is a candidate because it covers `tabBar`. A legacy model never emits `bar`, so legacy results do not change.

## Audit rules

- `button` is an interactive control (44 × 44 pt target check).
- `bar` is edge chrome and a container.
- `cell`, `dialog` and `container` are containers.
- `picture`, `adjustable` and `indicator` join no rule set, because their legacy types are mixed in those sets.
- The heuristic focus path keeps its `collectionItem` rim check. A `cell` does not get it. Role models use the comparative selector.

## Not in this version

- No annotation schema permits a role type. `AnnotationWriter` rejects a role type before it writes a file.
- The arm F `focused` class is not an element type. It is focus evidence. Its Swift handling waits for the arm F result.
- No role model is bundled or accepted.
