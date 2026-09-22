# P0-C ios-41class-r3 — distinct native reconstruction

Frozen 2026-09-22 UTC after maintainer approval to preserve counts by expanding
deterministic variants. Base revision `5b24dd0eb9e9b1d0b1927bc93b539e84cb93a5aa`
plus source changes pinned in `source-hashes-r3-20260922.txt`.

- Exact target: iPhone 17 Pro `F3EF9DB8-0B0F-4757-B653-D1628269F6FF`.
- Actual runtime: iOS 26.5 build 23F77; Xcode 26.6 build 17F113.
- New-only destination: `NativeUITrainer/reconstructed_corpora/ios-41class-r3`.
- Accepted counts unchanged: 16,940 = 12,340 train + 2,400 validation + 2,200 test.
- Taxonomy IDs 0–40 and complete-family allocation unchanged; no webContent route.
- Candidate policy: [authorized decision](next-corpus-decision.md). Preserve profile,
  accessibility settings and family/split per slot; try original seed + attempt ×
  1,000,000, at most 32 candidates. Exhaustion fails rather than shrinking quotas.
- Deduplicate accepted images using decoded sRGB premultiplied RGBA bytes, dimensions
  included. Independently audit with Python decoded RGB hashes after capture.
- Preserve rejected PNG/JSON pairs under `rejected/` and their accepted-member
  bindings in `capture-ledger.json`; they are not training/evaluation membership.
- Native navigation respects chrome safe areas; search geometry comes from the
  actual UISearchTextField. Map tiles use top-leading layout and date-label geometry
  excludes positioning padding. Writer fixes from r2 remain in force.
- HardNegative_1 gets deterministic low-saturation backdrop/contrast variation;
  stopped spinner and empty annotation policy are unchanged.
- Painted ChromeCoverage clock/signal/Wi-Fi/charge uses declared status configuration.
  Cellular full-scale uses four painted bars. No battery-health or actual network-state
  claims. Other generator status metadata is configuration, not proof of per-image
  system overrides. Actual launcher override is fixed and cleared on normal exit.
- OS/device/theme labels are requested rendering-profile metadata; actual runtime is
  the single pinned simulator. Do not count profiles as separate OS qualification.

Before launch: six bounded native tests passed, covering all 54 families × two
profiles, thirteen native-navigation families × two profiles, frozen schema geometry,
family allocation, candidate rejection/exhaustion, and fourteen fixed-clock status
axis images. Twelve offline Python validation tests pass. Full counts, rejection
ledger, duplicate/leakage, coverage, visual review and recovery still require audit.

Earlier attempts remain preserved and invalid. This is a new baseline corpus, never
historical pixel recovery. No model inference, training or promotion is authorized.
Retention owner and backup limitations: [retention/recovery](retention-and-recovery.md).
