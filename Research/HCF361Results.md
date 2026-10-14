# HCF361 preparation and first diagnostic results

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

These results do not establish that HCF is untrainable.
The study has no new trained candidate yet.
The [implementation plan](Plans/HCF361.md) defines the path to an experimental Core ML model.

## Measured findings

| Test | Result | What it tells us |
| --- | --- | --- |
| Matched Standard/HCF button | 0 changed pixels in both focused and unfocused comparisons | This pair contains no HCF-specific visual cue. It does not establish why. |
| Artwork focus arrival | 417,423 changed pixels at original resolution | The pair contains visible change. Its missing Standard counterpart prevents an HCF benefit claim. |
| Fixed boundary crop | 44,173 changed pixels within 256 × 256 | Visible change survives this diagnostic view. It does not prove that every change represents focus. |
| FDR021, production Swift crops | 5 of 6 reported labels agree; 1 focused artwork miss | The existing model separates the button pair but misses the artwork cue. |
| FDR038, production Swift crops | 3 of 6 reported labels agree; 3 false positives | This model calls every crop focused. Further training needs strong matched unfocused examples. |

The Standard and HCF button copies are identical. They are not independent successes.
The models use 6 crops from 3 retained pairs. Their source and OS-profile qualification remain incomplete.
Known body boxes provide the crops. These scores do not measure proposal recall or whole-screen selection.
The fixed decision threshold remains 0.85. No threshold tuning occurs.

The pixel diagnostic uses the existing Pillow crop contract.
The model diagnostics use the production Swift cropper instead.
Do not claim that these 2 crop implementations have passed pixel parity in this tranche.

## Learning decision

Prioritize matched native artwork and control examples under both verified profiles.
Keep focused and unfocused examples from the same scenes.
Measure rules and proposal recall before deciding whether the classifier or full-screen detector needs more work.
Do not expand to 50,000 frames before a useful 1,000-frame comparison.
One failed artwork prediction does not justify a new architecture by itself.

## Current execution boundary

research host's Fixture responds on the expected Simulator through port 8080.
The normal `bin/aatv` path points to a missing helper binary.
The inspected Fixture server exposes focus, recipe, and observation APIs, but no OS Focus Style switch.
Its `isDarkerSystemColorsStatus` field does not prove which Focus Style is selected.
Native paired capture needs a verified profile controller with restoration evidence.
peer-host-TTR's existing HCF357 counterpart remains separate assigned work.

## Verification

All 139 focused HCF and queue tests pass. The integrated native Swift build passes.
The sandboxed Swift test attempt records 15 Core ML and Vision issues.
The scoped native-runtime retry passes all 173 tests in 24 suites.
Failed runtime evidence remains in `.build/hcf361-test.log`.
Successful evidence remains in `.build/hcf361-test-native.log`.
No services, certificates, Simulator settings, or running jobs change.

Queue reports remain under `reports/work/research-queue/jobs/hcf361-*`.
Completed execution does not grant data admission, model acceptance, or navigation authority.
