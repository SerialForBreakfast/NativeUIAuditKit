# Standard proposal and focus comparison

Date: 2026-10-14. Scope: S391-03 and preparation for S391-04.

## Decision

Keep the learned focus baseline. The existing fallback rules do not improve this reviewed set.
Test proposal coverage and overlapping proposals before another focus training run.
Keep HCF separate and optional. No production threshold or model changes.

## Measured comparison

The comparison reuses 46 images and their retained detector outputs at confidence 0.5.
The tool calls the actual Swift fallback with unchanged thresholds and proposal geometry.
It removes learned focus state before the fallback call. It preserves proposal identities, roles, scores, and bounds.

Only 7 frames have complete reviewed focus labels. Other frames cannot establish complete selection accuracy.

| Outcome on complete frames | Retained learned method | Actual fallback |
| --- | ---: | ---: |
| Correct selection | 4 | 3 |
| Focused control absent from proposals | 3 | 3 |
| No selection | 0 | 1 |
| New successes | — | 0 |
| Previous successes lost | — | 1 |

The lost case starts with image hash `2dd62ffba5c49511`.
It contains overlapping `listRow` and `secondaryButton` proposals at the same reviewed row.
Their fallback scores are 0.94855 and 0.95593. Their difference is below the unchanged 0.12 margin.
The fallback abstains. This supports a controlled duplicate-proposal test, not a lower margin chosen from this case.

The comparison takes 4.53 s for 46 images. Median fallback computation takes 61.26 ms per frame.
These timings exclude detector inference. Historical learned timings include other work and do not provide a matched speed comparison.

The existing detector review remains 346 located controls from 583 reviewed controls.
It locates 21 of 46 reviewed focused controls. Partial labels limit other claims.
Historical OS focus profiles remain unqualified. Do not describe all retained images as verified Standard captures.

## Producer preparation

The existing TTR helper accepts 2 matched native collection plans through its running project workspace.
Each plan requests 2 cases. Both use the same 2 seeds, position, background, artwork, and layout.
One requests directional movement. The other requests content-only changes.
Each plan has a 600 s and 100 MB limit. Plan acceptance does not reserve storage or prove capture output fits.

The source contract permits calibration data only. These plans do not supply training data.
Capture still needs verified Standard state, available target ownership, storage, observed focus, and restoration checks.
Keep counterpart captures in the same ancestry group. Two seeds do not prove 2 independent layout families.
The runner owns future capture. This work starts no capture and changes no submitted job or approval.

The first helper attempt resolved its symlink and selected GUI mode. It timed out after 60 s.
The second attempt used the helper name but the wrong workspace. TTR sent no campaign request.
The corrected call preserves the helper name and uses the running app's project workspace. Both plans pass.
All attempts remain available locally.

## Verification

- All 35 focused Python tests pass after the final workspace-option addition.
- The isolated Swift build passes.
- The integrated offline Swift check passes 174 tests in 24 suites, plus the XCTest checks.
- A Swift test verifies that the diagnostic bridge matches the internal runtime function.
- The comparison preserves all 46 proposal sets, including off-screen boxes.
- Initial path and geometry failures remain separate attempts. No original evidence changes.

Local evidence lives under `reports/work/STANDARD392/`.
The successful comparison is `fallback-r4/comparison.json`.
The accepted producer plans are under `producer-pilot-r3/`.
These records contain local paths and remain outside public Git history.

## Next substantial batch

1. Prepare one fixed lower-confidence detector comparison. Cached confidence-0.5 outputs cannot recover discarded proposals.
2. Compare unchanged selection with geometry-based duplicate grouping on development data. Retain all original candidates and decisions.
3. Register the matched native pilot through the existing capture runner after target and Standard-state checks.
4. Prepare size and position variants for rows and collection items using supported native controls.
5. Preserve all previous successes before selecting any training correction.

The broader P01 corpus and deployable lower-threshold comparison remain preparation work, not ready queue capacity.

The implementation and checks after the commit take about 11 min, below the initial 45–75 min estimate.
Reusing retained predictions avoids detector inference and training during this tranche.
