# TRANSITION-SHADOW106 — change-only TTR consumer delivered

October3local / October4UTC. Approved export/delivery, not training, capture,
localization deployment or promotion. NUIAK-owned deliverable complete; TTR owns
its source hook and receiver receipt. No TTR repository edits or Git writes.

## Delivered contract

DTM025 change branch only, checkpoint
`28f10dc5ac2c6a0fb324cabeb778b2acad2539c97f7f9cc48a20c8ff534a9409`.
`FocusTransitionChange.mlpackage` is105,663bytes; compiled model108,365bytes.
CPU-only FP32 Core ML, ordered full RGB frames letterboxed192×128, internally
absdifference/before/after. No boxes, labels, requested focus or telemetry features.
Changed>=0.85,unchanged<=0.15,otherwise uncertain; uncalibrated sigmoid scores.
No alteration to existing single-frame export default or shipped models.

Portable Swift6/macOS15+ source, compiled/source model, manifest, instructions and
synthetic vectors are in `nuiak-transition-shadow-dtm025-v1.zip`:

- 198,134bytes;19members;246,248expanded bytes.
- Archive SHA256 `447f9c208a0c7a50f6d5a79879a01e23b4e4469f49d69c3ba4cfb6c961042cae`.
- Manifest SHA256 `117530ef7f901ec901ffee178dc6381d833261f37d4ca84e3f47514ca7b6e872`.
- Contract SHA256 `31837a325f0fcfabba7a30c07018e18c5acf36418bedb69d3b9c0970583c9e31`.
- Compiled tree SHA256 `194a84672325e6016828bd57c4baa5d7dfda720b8a553631d31c6af5d3951c32`.

Original/archive/extracted evidence is gitignored under `artifacts/`; compact report
and request remain source-controlled candidates. No raw weights, executable binary
or private captures in delivery. Named source files in `Tools/TransitionShadowTool`
are the implementation, not a parallel consumer copy to maintain.

## Acceptance evidence

1. Existing exporter now has explicit `--task transition-change`; native CPU compile
   succeeds. Resident torch2.7/coremltools9 export environment, no installs/downloads.
2. `artifacts/parity-final/parity.json`:240/240exact encoded tensors and threshold
   decisions across113retained real pairs,122derived identity negatives,5synthetic
   pairs;187unique real frames. Max absolute Core ML/PyTorch error2.868473529815674e-7,
   below1e-4. Whole final parity43.902s; no recapture or role changes.
3. Local macOS26.4.1(25E253) timings: median inference0.326ms,p950.672ms;
   preprocessing169.407ms median; batch load9.989–15.444ms. Preprocessing includes
   byte/hash/decode/resize work and dominates. These are local retained-pair timings,
   not TTR end-to-end, cold-machine or device latency claims. Use a bounded passive
   background queue, never wait on navigation for a prediction.
4.24real-CLI contract tests pass: score/off/encode, missing/corrupt/altered pixels,
   unsupported format/orientation/dimensions/version/backend request, viewport
   mismatch, path/symlink escape, unknown/duplicate fields/IDs, batch limit,
   wrong contract/model hashes, modified model and output collision. Off loads
   neither model nor pixels; failed pairs remain failed rather than unchanged.
5.12existing export/parity Python regressions pass; integrated offline Swift
   build/test pass14XCTest+123SwiftTesting. New Swift tests cover nonfinite scores,
   threshold boundaries, duplicate JSON keys and planar color/letterbox semantics.
6. Archive independently extracted with member/size/path/type bounds and every
   manifest member hash checked. The extracted dependency-free Swift package built
   release independently and scored its included synthetic sample with exact input
   hash and matching decision/probability. See `artifacts/portable-check/reply.json`.

Commands/logs (all exit0 for final runs):

```
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python scripts/verify_transition_shadow106.py --tool .build/arm64-apple-macosx/release/TransitionShadowTool --output reports/work/TRANSITION-SHADOW-106/artifacts/parity-final
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python scripts/test_transition_shadow106.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python -m unittest scripts.test_focus_reviewed_export scripts.test_focus_export_parity
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python scripts/package_transition_shadow106.py
```

Explicit outputs/cache environment remain project-local; Apple-managed Core ML/test
cache access used scoped approval. Logs `.build/transition106-{export,compile,
release-final2,parity-final,contract-tests,export-regressions,swift-build,swift-test,
portable-build}.log`. Swift commands use `--disable-sandbox --skip-update` and local
cache/config/security paths; portable build has an independent scratch path.
Output destinations are immutable; repeat checks need new named destinations.

Preserved failed checks: conversion saved a valid package but its initial runtime
load was sandbox-cache denied (not claimed as inference success); first parity
launcher rejected SwiftPM's `.build/release` symlink before inference, corrected
to the resolved executable; a missing Swift `try` was caught/fixed by the build;
packager initially imported the wrong helper and failed before output. No model
retry/training or weakened parity thresholds. Source/tree hashes are rechecked
after model load and at batch completion; this is not an atomic filesystem lock.

## Publication and independent outcomes

Verified `sillycon.local/SharedStatusFile` SMB mount. Archive published via unique
partial then final name under `nuiak/`;198,134bytes/SHA read back exactly. Request
`nuiak-20261004-transition-shadow-dtm025-delivery` is a follow-up to the existing
shadow-feedback request, not a duplicate project. Request YAML hash
`e670110f9668b512692a17e1224af88808f5fdfa9baa63a0b4336b7d24eb7d71`.
Own `packets.TRANSITION-SHADOW-106` published with exact artifact metadata;
other packets/top-level summary preserved. See `coordination.md` for readback.
Receiver copied receipt, exact-request acknowledgment and live hook proof are
pending, separately tracked. No cleanup before matching receipt; original retained.

- Software verified:PASS, native adapter and actual portable consumer execution.
- Data eligibility:unchanged retained development/training roles; no new admission.
- Integration:local portable consumer PASS; live TTR integration NOT ASSESSED.
- Model gates:production/unseen-domain NOT ASSESSED. DTM025 training advancement is
 not independent accuracy. DTM026 localization regression remains rejected.

## Next substantial work

TTR: copy/hash receipt, source build/synthetic check, then integrate into already
authorized passive shadow/review/export; return loaded identity, on/off proof,
scored/failed/dropped counts, latency and independently reviewed error categories.
No additional capture/egress approval inferred. Existing FDR021 remains separate.

NUIAK: RANK-RETENTION105 can proceed independently—batch frozen old/new ranker
logits/features/proposal recall, explain Settings regression, then one explicitly
defined retention-aware comparison under standing training authority. Do not use
exposed Settings as training or call different Fixture seeds independent evaluation.
Feedback intake follows actual receipt/privacy/role eligibility, not peer promises.
