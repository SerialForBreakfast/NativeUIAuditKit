# Native detector comparisons — 2026-10-17

Owner: Maximum-mini-NUIAK. Tasks: B405-178 and B405-179.

## Decision to make

Identify the next detector repair from native development images.
Keep focus training independent from detector diagnostics.

- iOS: compare Run 009 and Run 013 on identical native images.
- tvOS: separate missing geometry from incorrect classes on identical production predictions.
- Focus: review the matched native-control fits when their dependent evaluations finish.

## Data and controls

iOS uses 180 retained T46 frames across 45 families, 2 layouts, and 2 appearances.
Related layouts and appearances keep their original family-and-seed groups.
ChromeCoverage, MapOverlays, and TabViewNavigation remain excluded after B405-135.
The adapter preserves exported bounds. It excludes covered controls and retains body-probe limitations.
These are development images. They are not an independent final audit.

tvOS uses 24 Standard development images across 6 groups from NCTRL417.
The adapter uses measured visible bodies and the original Fixture taxonomy.
The source classes are `primaryButton`, `listRow`, and `menuButton`.
The layout families remain button, row, and tab. A family name does not replace a class label.
The adapter verifies source artifacts, image hashes, dimensions, groups, and duplicate consistency.

Both iOS models use 640 px, confidence 0.50, and NMS IoU 0.45 through the existing PyTorch inference implementation.
tvOS uses the existing production CLI at confidence 0.50 with OCR off.
The comparisons reuse T42 matching at IoU 0.50.
Unmatched predictions remain unreviewed. They are not confirmed false positives.

## Queue

The existing compiler registers 27 diagnostic jobs:

| Track | Preparation | Inference | Cached analysis | Total |
| --- | ---: | ---: | ---: | ---: |
| iOS | 6 | 12 | 0 | 18 |
| tvOS | 3 | 3 | 3 | 9 |

T55 prepares native labels. T56 runs the existing inference implementations without requiring an older scorecard.
An optional PyTorch baseline pins the matched labels, backend, image size, confidence, and NMS settings.
T56 emits ordinary scorecards and bundles for existing T42 analysis.
The detached runner owns execution. Existing fits and submitted specifications remain unchanged.

Each job retains an 800 s ceiling and 100 MB output cap.
The aggregate ceiling is 6 h and 2.7 GB. This ceiling is not a runtime estimate.
Native inference timing remains unmeasured for these inputs. Reports record inference time separately.
Preparation jobs verify labels before inference. Failed dependencies block their consumers.

The compiler change adds contracts only. The active training execution closure excludes the compiler and both new adapters.
Software tests cover retained input preparation through isolated queues and exact reuse of matcher results.
The first native inference results establish runtime qualification. Software predictions do not establish detector accuracy.

## Result rules

For iOS, report each gained detection and lost previous success by class and layout.
If Run 013 loses controls, preserve those cases before preparing targeted training.
Use appearance and layout metadata to test whether failures concentrate in a specific condition.

For tvOS, compare class-aware results with class-agnostic results from the same predictions.
If geometry succeeds but classification fails, investigate taxonomy or class training.
If both fail, prioritize localization examples and proposal coverage.
Keep focused and unfocused results separate.

If inference fails, preserve the attempt and diagnose the exact adapter or input failure.
Register a successor only after a specific correction passes tests.
These development comparisons do not promote a model.

## First completed comparison batch

At 20:28 UTC, 10 of 27 jobs complete with verified output hashes.
The first 90 iOS frames contain 1,052 eligible labels.
Run 009 detects 870 labels. Run 013 detects 944 labels.
Run 013 gains 108 detections and loses 34 previous successes.
The losses include 20 labels, 10 list rows, 2 cancel actions, and 2 disclosure groups.
These are native development results, not a new trained model or a real-app benchmark.

The 3 matched comparisons qualify the native PyTorch inference path on these inputs.
Each inference job takes about 3.3–6.0 s inside inference and 4.0–6.7 s including worker startup.
This is useful diagnostic work, not an overnight compute load.
The remaining layout and tvOS results still require review.
Software validation passes 32 tests. Swift sources remain unchanged; the prior 176-test result retains its documented exclusion.

## Follow-up tranche

Review all completed focus and detector results together.
Select one measured repair per qualified track.
Prepare matched training with fixed membership, equal exposure, retained successes, and separate development groups.
The detector training adapter remains a separate prerequisite for new iOS and tvOS fits.
