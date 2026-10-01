# FDR021 RGB — experimental observer delivery

Candidate: `focus-ring-experimental-fdr021-reviewed-contrast-rgb-v1`.
Request: `nuiak-20261001-fdr021-rgb-consumer`. No new training/export was performed.

Use the enclosed `artifact-index.json` for exact package and compiled tree hashes.
The archive hash is a separate transport identity, reported by the sender. Manifest
paths are archive-relative; legacy evidence paths in the index are NUIAK-local.
Only model directories, compatibility source and compact evidence are enclosed.

The package is opt-in and `releaseEligible=false`. Existing known artwork failures
remain.333 frozen examples passed local CPU crop/input/score parity; that is neither
TTR runtime proof nor ANE/backend parity. No autonomous control is authorized.

## Consumer acceptance

1. Verify archive size/SHA, bounded paths/member sizes, per-file hashes and both
   model tree identities. Return exact receiver receipt before sender cleanup.
2. Confirm the isolated candidate loader and compatible NUIAK build. Review enclosed
   source by context; do not replace a whole source file over newer consumer changes.
   There is no assertion that the ordinary public request API exposes an override.
3. Require `inputPixelContract=png-straight-rgb-v1`, threshold0.85 and ambiguity0.70.
   Reject missing/unknown contract for this candidate; do not silently fall back
   and label that fallback a candidate result. Preserve16%expansion/256×256 cropping.
4. In a separately assigned observer replay, report build/source, candidate ID,
   loaded model tree hash, actual CPU/GPU/ANE policy/backend, crop/input identities,
   elapsed timings and every scored/failed/missing control. No device actions.
5. Compare against the same retained frames and boxes. OCR/accessibility hints may
   be diagnostic evidence, never substituted for model scores or focus truth.

## Rollback

Keep bundled model bytes and default configuration untouched. Candidate-off restores
the existing default path; no copy-over or destructive swap. On loading/contract/
inference failure, report candidate unavailable. Any default fallback is separately
identified, not successful candidate execution. No global model registration,
promotion, checkpoint cleanup or system setting change is part of this delivery.
