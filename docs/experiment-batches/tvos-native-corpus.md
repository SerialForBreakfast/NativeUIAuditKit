# Native tvOS corpus trial

The tvOS Simulator produced 300 distinct training screenshots in 60 related layout groups. Each of 6 screen families contributes 50 images.
The families cover search, settings, shelves, detail, playback and presented sheets. All states share one generator lineage.
These provisional results describe the generated corpus. Real-app transfer and training outcomes remain unmeasured.

The admission check retains a decision for each of 405 attempted screen IDs. Repeat and hidden-control images support verification only.
The initial 300 attempts supplied 218 eligible screens before replacements. Corrections addressed duplicate shelf states, playback overlap, focused fields and sheet action bounds.
The final membership keeps 200 original frames and 100 verified replacements. Related states stay together in training.

## Detection labels

The normal loader reproduced all 1,845 accepted boxes at 0 px maximum edge error.
For 190 frames, the visible bodies passed direct checks at both pixel-difference thresholds.
For 110 frames, a matched resting button established its body beneath the focus effect. The checks compared native ownership, body geometry and local pixels.

| Role | Instances |
|---|---:|
| Button | 850 |
| Cell | 445 |
| Segmented control | 300 |
| Picture | 100 |
| Text field | 50 |
| Dialog | 50 |
| Indicator | 50 |
| Toggle, bar and page control | 0 each |

## Focus observations

The original shelf renderer could move native focus between 2 controls with identical rendered pixels.
A replacement renderer applied a custom 4 pt border in the native focus callback.
This produced 10 matched swaps. The frozen full-screen rule selected the wrong target on all 20 endpoints.
Standard localized the focused target at IoU of at least 0.50 on 10 endpoints.
Nine of these received a scored cell proposal. One received an image-view proposal.

The next detector comparison can measure transfer to independent app screens.
The focus results support separate tests for missing proposals and wrong selections among available controls.
The corpus contains no independent qualification partition or measured improvement to a shipped model.

[Renderer and validation instructions](../../scripts/corpus640/README.md)
