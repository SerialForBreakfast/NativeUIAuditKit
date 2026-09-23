# FOCUS-COMPRESS-01 — one isolated int8 candidate

2026-09-22. Assigned experiment complete for review; no promotion.

| Outcome | Evidence |
| --- | --- |
| Software verified | 78 Focus tests pass, including eight compression preflight tests; offline Swift build and 93 Swift Testing tests pass (see logs) |
| Data eligible | Existing 12 frozen development crops only; no corpus added or training admission changed |
| Integration qualified | Real int8 conversion, CoreML compilation, production `FocusRingTool` CPU preprocessing/inference and hash-bound parity pass |
| Model gate passed | Not assessed: size and limited conversion-parity checks pass, not six release gates or physical/navigation qualification |

## Result and acceptance

[Comparison](comparison.json) binds preserved FP16 and candidate reports and package
hashes. Candidate: `NativeUITrainer/focus_ring_runs/fdr007-native-incremental/export-03-int8`.
Checkpoint remains FDR-007; experimental ID `fdr007-int8-01`, releaseEligible=false.
Weight-only symmetric int8/per-channel, weight threshold2048, coremltools9.0;
activation/compute precision is not converted into an int8 execution claim.

- Size: **2,612,925 bytes**, down48.1369% from5,038,123. Passes5,000,000-byte gate.
- Max probability difference: **0.000000715255 versus FP16**,0.00000357628 versus Torch.
  All12 decisions remain correct, zero differences at0.5/0.70/0.85; tolerance0.01.
- CPU warm median inference:1.367ms versus1.360ms FP16. Two process-first
  predictions4.270/4.321ms; model load77.760/15.710ms. Not a demonstrated speedup.
- Production recropping median69.364ms versus68.359ms FP16: crop work dominates
  this helper measurement. Profile separately before changing preprocessing.
- The challenge has zero near-threshold cases,6 positive/6 negative crops from one
  Settings screen. Same membership/runtime protocol verified; no generalized
  compression-accuracy claim, ANE claim, or independent test result.
- Source package hash rechecked unchanged:
  `4d43d6f4aedb7d26e820c7c33d79fa4e21b28d64a25a683f03c6219e64ccdf02`.
  Candidate hash `9591f3cc88b555074bfd25762a5cb9944df538414e25acdfd43ac03f29e8dd5c`.
  Compiled hash `a02b3409ba51c5ade491c1bd4301304a640441a9a2296a412514137076baa928`.

`scripts/compress_focus_ring_coreml.py` uses the existing size/path/hash contracts.
Tests reject changed source, collisions, symlinks, source/output overlap, mismatched
reports, production outputs and non-experimental sources. Ordinary tests load no
model. Real parity uses unchanged `scripts/focus_export_parity.py`; no duplicate
cropper, trainer or public API added. Python environment exception is the approved
isolated `focus-export-01` environment; no package installation this turn.

## Commands and timing

`run.py` records exact commands/exits in three `*-execution.json` ledgers. All exit0:
compression2.62s, compilation0.18s, production comparison3.66s. Each subprocess is
bounded180s. `summarize.py` compares retained reports without inference, exclusive
output creation. `PYTHONDONTWRITEBYTECODE=1 <approved-python> -m unittest discover
-s scripts -p 'test_focus*.py'`:78 pass/2.49s (`tests.log`).
Offline `swift build`6.38s, `swift test`93 Swift Testing tests/2.497s plus14 XCTest
tests/0.331s, exit0;
logs `swift-build.log`, `swift-test.log`. Both use disable-automatic-resolution,
manifest-cache local and project cache/config/security/module/TMPDIR paths.
No capture or external-wait time. No training run or experiment ID allocated.

## Handoff

Base `11ce83e6829d7845bd95dea8f4fe15cc1f815a6b`. Existing export, research, task and
TTR diagnostics changes were preserved; P0-C ownership and artifacts untouched.
New source/test/runner/report files plus queue/canonical-plan/catalog/roadmap updates.
See [PER-DATA](../PER-DATA/handoff.md) for the other assigned branch.
Coordination: not applicable—local experiment, no TTR request or integration change.

Next: freeze a broader development challenge including different visible focus
treatments/ambiguous scores, then compare shipped/FP16/int8 on identical membership.
PER-DATA's Photos labels are visual-review leads for a separately assigned comparison,
not callback-grounded training pairs. Preserve both candidates; no automatic new
compression, training, capture or promotion. All bounded experiment criteria are
evidenced; no running process remains.
