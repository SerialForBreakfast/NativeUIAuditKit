# P0-C reconstruction preflight — 2026-09-19

## Outcome

No reconstruction capture was started. The historical source search remains conclusive: the five documented roots contain zero of the 15,239 expected original pixels. That absence is a recovery condition, not a reason to reuse old labels or to weaken evaluation controls.

The original generator could not produce an eligible replacement corpus: its generation loops assigned a split from `manifest.imageCount + 1` through `splitFor(imageIndex:)`, an 8:1:1 image rotation. Every template family therefore contributed examples to train, validation, and test. This was an evaluation leakage defect, because the architecture requires family holdout and assembly independently rejects cross-split family reuse. The fixed generator now selects splits by declared template family and fails closed for undeclared families.

## Evidence

- Historical generator revisions derived splits from sequential image indices rather than declared families.
- `Research/NativeUIElementDetection.md:630` requires family holdout rather than the generator's within-family split.
- `Research/DatasetRecoveryPlan.md:45-47` requires pinned family splits and validation of family separation.

The revised current suite requests 16,940 image/annotation pairs. With 14 GiB currently free on the repository volume, capacity is workable but tight; capture is allowed only after the family policy, expected count, and active renderer set are frozen.

## Safe work completed before the stop

- Added the gitignored `NativeUITrainer/reconstructed_corpora/` output root.
- Made `NativeUIDatasetGenerator` use only the in-repository `.build/NativeUIDatasetGenerator/DerivedData` path rather than `/tmp` or default external DerivedData.
- Made the destination strictly new-only and individual copies collision-failing.
- Scoped simulator state reset to only the GeneratorRunner app before capture, preventing stale app-container data from contaminating a new corpus. The user authorized this Simulator staging solely for P0-C.
- Confirmed `swift build` and `swift test` pass after the safe orchestration changes.
- Retired the unstable `HardNegative_2` WKWebView capture route. It is not replaced for P0-C; `webContent` is legacy uncovered compatibility metadata.

## Approved split allocation

The maintainer approved family-level splitting on 2026-09-19. The fixed test holdout is `CardDetail`, `WizardStepFlow`, `NotificationCenter`, `GalleryPage`, `MultiSectionForm`, `SettingsToggleDense`, `EmptyState`, and `OnboardingPage`. Validation is `TabViewNavigation`, `SearchResults`, `PickerDateEntry`, and `SettingsDisclosure`. All remaining families, including hard negatives and accessibility variants, are train only. The generator must enforce this allocation and prove no template family crosses a split before capture begins.
