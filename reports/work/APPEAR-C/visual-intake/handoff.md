# Delivered appearance intake — completed for review

2026-09-23, approximately 06:11–06:18 UTC. No capture or model operation.

| Outcome | Result |
|---|---|
| Software verified | Existing appearance-v1 implementation unchanged; previous 43 Python/107 Swift tests and build evidence reused. Six real intake/extraction CLI calls exit0 |
| Data eligible | Pass for simulator development:10 pairs,20 unique crops; training and independent evaluation not approved |
| Integration qualified | Pass for these three delivered appearance-v1/sidecar-v2 bundles only |
| Model gate passed | Not assessed; no inference, training or promotion |

## Evidence and acceptance

User delivered `dataset/tvos_captures/appearance-visual-20260922/`. Archive
`nuiak-appearance-visual.tar.gz` is116122181 bytes and matches expected SHA256
`d80f14887c399e85c738ba3705096fc4ad6d116d37a38c5ca36d872919b5764a`.
All55 unique archive paths are relative regular files/directories:52 files,
no symlinks, traversal or special members. Extracted into a new project-local tree
`dataset/tvos_captures/appear-c-visual-intake-20260923/`; original delivery untouched.
Delivered helper scripts were not executed. Four auxiliary handoff/build documents
remain separate from the48 exported bundle files (117093955 bytes).

- `integrity.json`: strict completed-receipt/index/PNG/sidecar/native-bracket checks,
  exact producer manifest hashes, full local file hashes and counts.3 grid-artwork,
  3 dock-bright,4 media-placeholder pairs; zero unknown classes. Grid/dock each
  intentionally exclude one disabled tile from focus targets.
- `visual-review.md`, six contact sheets: all reference/focused states and20
  production16%/256×256 crops reviewed. Focus borders agree with native labels;
  bright unfocused and gray artwork are visible. No label inferred from model output.
- Three `*-cli.log` files: actual build_simulator_focus_manifest and
  harvest_focus_pairs --ttr-sidecar-v2 --visual-review calls exit0. Source/build
  context retained; source reported fb47e39a084a2ff20cdf34b85458f1e1ebbdca8a dirty.
  Delivered host/Fixture receipts pin tree2ff6e33c/ff813f1f respectively; this is
  producer-reported provenance, not an independent rebuild or authenticated target.
- `reservation.json`: three hash-frozen v1.5 reviewed-fixture manifests under
  `dataset/focus_ring/appear-c-visual-{grid-artwork,dock-bright,media-placeholder}`.
  All10 pairs stay development, with seed7 siblings grouped across presets/layouts.
 20 distinct crop pixels; zero exact frame/crop matches against458 prior samples
  pinned by APPEAR-B proposal/protected evidence and prior APPEAR-C reservation.
  This scoped exact-match audit does not establish semantic independence or audit
  every historical corpus. Related seed7 data must never be split into final evaluation.
- `preflight.json`: all three datasets correctly remain launch-ineligible.

Read-only validation/rendering took seconds; bounded prior-pixel audit approximately
one minute. No external wait, recapture, Swift rebuild or repeated suite was needed.
Only diagnostic reports/scripts and queue/snapshot changed this turn. Preserve all
pre-existing dirty software and research edits recorded in the prior handoff.

## Scope and next work

Three dark/regular/seed7 recipes prove the new intake path, not all themes, motifs,
scrolling or independent focus treatments. Existing grid/dock2×2 caption mismatch
and media title truncation remain visible; crops preserve complete focus borders.
Physical-device rendering and postflight were not reprobed here; producer historical
postflight remains separate from independent consumer acceptance.

TTR06:13:24Z status reports source/offline follow-up for high-contrast,Photos-like,
blank-placeholder and family IDs, but explicitly no signed/new-family visual evidence.
Do not equate that work with qualified new data or recapture this delivered archive.
Next NUIAK work: APPEAR-B1 development proposal/adapter integration, preserving these
seed7 groups as development; next joint step is bounded new-family qualification
under a separate capture assignment, followed by independent evaluation reservation.
No training run is authorized by this intake receipt.

Worker and fixture-training skills enforced native label binding, production crops,
immutable membership and separate data/model outcomes. Shared-status result is in
`../coordination.md`; publication/readback is not peer acknowledgment. Intake scope
is complete for review; independent-family qualification remains an explicit gap.
