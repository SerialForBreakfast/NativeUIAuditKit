# P0-C reconstruction configuration — `ios-41class-r1`

**Frozen:** 2026-09-19 UTC before capture; revised after the retired WKWebView route.  **Identity:** a newly rendered replacement corpus; it is not the unavailable historical corpus and must not be compared directly with historical Run 009 metrics.

## Generator provenance

| Field | Value |
|---|---|
| Base repository revision | `9697e59fcf740bacd338c202b2ea67c6b3a7654e` |
| `GenerateDatasetTests.swift` SHA-256 | `1853d5efbdbceafe0519dcb5f4cc2cfc049df326eedc2f0a49d18a21f102ab46` |
| `NativeUIDatasetGenerator/Sources/main.swift` SHA-256 | `2654a85778fa048b33348d9da4d4366c1b03e51c90d8a7f4600551c87358bbb6` |
| Scheme | `GeneratorRunnerTests`, serial execution only |
| Render target | iPhone 17 Pro, iOS 26.5 Simulator, UDID `F3EF9DB8-0B0F-4757-B653-D1628269F6FF` |
| App-container handling | Uninstall only `com.nativeuiauditkit.generatorrunner` before generation; do not erase or alter the simulator otherwise |
| Build output | `.build/NativeUIDatasetGenerator/DerivedData` |
| Destination | `NativeUITrainer/reconstructed_corpora/ios-41class-r1` (must not exist before copy) |

The generator rotates the existing deterministic per-family seeds, visual profiles, pixel scales (2 and 3), device configurations, simulator status metadata, Dynamic Type, locale, and accessibility variants. It will generate 16,940 new PNG/annotation pairs: 12,340 train, 2,400 validation, and 2,200 test. `HardNegative_2` and active `webContent` generation are retired and excluded; the 41-class legacy taxonomy remains frozen, with `webContent` reported as uncovered. The expected data size is approximately 2.25 GiB; capture plus in-repository copy requires roughly twice that transiently. The repository volume has 12.7 GiB free at freeze time.

## Split policy

| Split | Complete template families |
|---|---|
| Test | `CardDetail`, `WizardStepFlow`, `NotificationCenter`, `GalleryPage`, `MultiSectionForm`, `SettingsToggleDense`, `EmptyState`, `OnboardingPage` |
| Validation | `TabViewNavigation`, `SearchResults`, `PickerDateEntry`, `SettingsDisclosure` |
| Train | Every other declared family, including all hard negatives and all accessibility variants of their base family |

The policy is fail-closed: a new generator family causes a precondition failure unless it is explicitly declared. The isolated policy XCTest passed before this configuration was frozen.

## Acceptance and retention

After capture, validation must verify each manifest member's PNG signature/dimensions/SHA-256, paired annotation, split membership, no cross-split family or content reuse, and class/style coverage. The maintainer owns retention. This gitignored in-checkout corpus is not an independent backup; an external backup requires a separate authorization.
