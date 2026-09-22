# P0-C ios-41class-r2 — corrected replacement corpus

Frozen before the fresh run, 2026-09-22 UTC. Base revision
`5b24dd0eb9e9b1d0b1927bc93b539e84cb93a5aa` plus the recorded writer/orchestrator fixes.
Exact source hashes: `source-hashes-r2-20260922.txt`.

- Exact target: iPhone 17 Pro UUID `F3EF9DB8-0B0F-4757-B653-D1628269F6FF`.
- Actual renderer: iOS 26.5 build 23F77, Xcode 26.6 build 17F113.
- Destination: `NativeUITrainer/reconstructed_corpora/ios-41class-r2`, new-only.
- Scheme: GeneratorRunnerTests, only GenerateDatasetTests, serial, no model benchmarks.
- Membership: 16,940 PNG/annotation pairs; train 12,340, validation 2,400, test 2,200.
- Family/seed/variation policy: unchanged from [original configuration](reconstruction-configuration.md).
  Test and validation families remain disjoint including accessibility variants.
- Retired: HardNegative_2 and webContent; no synthetic replacement for WebKit.
- BP-28: tabBarItem auto-detection artifacts excluded from annotations and distribution;
  parent tabBar preserved. No remapping or addition to IDs 0–40.
- Writer: v1.0 safe-area keys; true visible-image intersection in Vision boxes;
  out-of-image annotations excluded, clipped elements marked imageBoundary.
- Profile/device labels and simulatorState are generator configuration metadata, not
  proof of running multiple OS versions or applying per-image system status changes.
  Sidecar osVersion currently unknown; the actual renderer is pinned above.

The r1 attempt failed annotation validation and was stopped. Its 1,150 manifested
members plus any partial-family files are preserved in
`.build/debug-output/p0c-resume/failed-capture`; its validation report is retained.
The fresh app-container reset only discards that already preserved, invalid staging copy.
No old dataset, labels, links or historical metrics are modified.

Nine offline validator tests and two bounded iOS writer/split-policy tests pass.
Post-capture acceptance still requires full decoding, paired schema/binding/geometry,
exact membership, class/style support, family/pixel isolation and visual review.
Duplicate or missing members block acceptance; no automatic pruning or split moves.
The maintainer owns retention. Independent backup and Run 009 inference remain separate
steps; this corpus is not historical recovery and cannot reproduce 0.586 by assertion.
