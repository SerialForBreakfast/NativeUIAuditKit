# Next bounded development run — approval needed

Historical proposal: approved2026-09-29 and executed as FDR013. See
../FDR-013/handoff.md; no eligible checkpoint. This document is not a rerun approval.

Use `qualified/protocol.json` in this folder, protocol SHA256
`1c39256bf41e133d1e9532d35f4b2d6d6f7e24240729eb0375fc04e866326ae7`.
No run number is allocated and no training output exists.

- Data: 363 training pairs, unchanged nine retention pairs; 453 settled real
  reviewed candidates for checkpoint selection only. 64 excluded real labels
  remain accounted. Three geometry-blocked and three duplicate new pairs stay out.
- FDR007 initialization, fresh AdamW, 50/50 native–Fixture sampling, no
  augmentation; 30 epochs, batch 64, learning rate 0.0003, seed 42, 1,800-second cap.
- Use the established resident focus-export-01 environment and verified MPS host
  context. Verify MPS before launching; do not repeat FDR011's CPU fallback.
- Retain 18/18 classifications and per-stratum FDR010 floors at 0.85; improve
  real TP above 3/35 without exceeding 9/418 FP. Preserve at least two correct
  complete-frame selections, zero wrong/multiple. Only eligible epochs can win.
- Minimize frozen balanced real-development BCE, earliest epoch on ties. No
  eligible epoch means no selected checkpoint; `last.pt` is not a substitute.
- After training, compare the selected checkpoint against shipped and FDR010
  on the frozen real-development and separate related-synthetic diagnostics.
  Real selection results are no longer independent evaluation. Keep challenge
  evidence untouched. No export, model promotion or automatic rerun.

Approval must bind the exact protocol, warm-stretch arm and a fresh run name in
a `focus-representative-approval-v1` record, with reviewer/review reference. Log
the sequential run ID before launch. Preparation did not create an approval.

This is a transfer-improvement experiment, not a production qualification claim.
Source-separated qualification and broader coverage remain required for release.
