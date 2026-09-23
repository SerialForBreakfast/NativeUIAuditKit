# Size enforcement and evaluation audit — 2026-09-22

## Delivered

Exporter now enforces the existing literal5MB specification as **5,000,000 logical
bytes**, not5MiB. Reports carry byte limit, decimal MB, binary MiB and versioned
`decimal-bytes-v1` gate semantics. All package files count; missing/empty/symlink
packages reject. Oversize artifacts and reports survive with exit1 for diagnosis.
No production precision, architecture, crop behavior or threshold changed.

One fresh real export, `export-02-sizegate`, produced5,038,119 bytes and correctly
exited1 after4.053s (`sizegate-execution.json`, `sizegate-export.log`). It remains
experimental. Its four-byte difference from export-01 reflects different identity
metadata; this is not a model-size improvement. Original export/parity evidence
was preserved, and no unnecessary recompile/inference was run on this failed gate.

Original package breakdown: weights4,969,536 bytes, model graph67,970 bytes,
manifest617 bytes. The38,123-byte overage cannot be assumed removable housekeeping.
No executable graph/weights were deleted, no limit relaxed, no new quantized
candidate silently substituted for the specified FP16 baseline.

## Existing-evidence audit

FDR-007 protocol sources: Settings root/general/apps are training;
Settings accessibility is validation. Remotes is the separate development
challenge. These are not multiple independent apps or varied focus treatments.
Do not relabel training/validation screens as a new untouched evaluation set.
Home trials remain failed/unqualified; Fixture pilot remains unqualified.

On the frozen12 Remotes crops, both shipped and candidate have **zero** predictions
within0.01 of any0.5/0.70/0.85 threshold. Shipped has2 ambiguity-band predictions;
candidate has0. Candidate probabilities are saturated, approximately0 or1. Thus
the strong export parity result establishes neither near-threshold calibration nor
generalization across themes/custom controls. No new qualifying imagery was found
in the scoped existing protocol/challenge evidence. No images were synthesized,
relabelled from predictions or captured in this tranche.

## Verification

-70 focused Python tests passed in3.828s (`sizegate-python-tests.log`), including
  exact5,000,000 boundary, one-byte overage, combined metadata/weight membership,
  MiB-versus-MB distinction, missing/empty and symlink failures. Printed6000-pair
  toy-corpus counts are test fixtures, not newly captured data.
- Offline Swift build passed3.23s;93 tests passed2.684s, retained sizegate logs.
- Real exporter exit1 plus retained failed size report validates caller behavior.
- `git diff --check` passed. No git writes, training or model promotion.

Software verified; existing development-data eligibility unchanged; prior parity
integration retained for export-01 only; overall model gates not passed. This
tranche completes gate correctness and existing-evidence assessment, **not** the
objective of a smaller qualified model. SMB not applicable; no TTR state changed.

## Next substantial work

1. Separate reviewed compression experiment: preserve FP16 as reference; consider
   Apple's per-channel8-bit weight compression without training or activation
   quantization. This changes the weight-storage contract and needs explicit
   approval; it is not an FP16-gate waiver. One isolated artifact, checkpoint/input
   hashes, measured bytes, same frozen thresholds/tolerance, production CPU parity
   and latency. Failed parity yields diagnosis, not a compression sweep. Even a
   pass on12 crops is experimental until broader evidence exists.
   [Apple API](https://apple.github.io/coremltools/docs-guides/source/opt-quantization-api.html).
2. Separately authorize a capture matrix for different visual treatments: qualified
   Fixture light/dark/high-contrast controls when available, or native Home only
   after stable native tile labels. Freeze whole journey/recipe groups before
   capture; preserve current development lineages outside future final tests.
   For near-threshold diagnostics, use a distinct development subset and report
   score-based selection; never curate the final test from model failures.

Neither new capture/style mutation nor compressed-model execution occurred.
