# FOCUS-EXPORT-01 — 2026-09-22

| Outcome | Result |
| --- | --- |
| Software verified | Focused safety/identity/parity tests pass;68 focus Python tests and93 offline Swift tests. Genuine conversion/inference entrypoint integration remains unexecuted. |
| Data eligible | Reuse the frozen OS-FOCUS-03 challenge; no new capture, labels or changed eligibility. |
| Integration qualified | Not assessed: no candidate CoreML artifact was produced. |
| Model gate passed | Not assessed; no training, promotion or size/parity/latency claim. |

## Delivered

Base `b13c5ad`; worktree was clean at start. Updated the existing exporter, not
another trainer: experimental model identity/checkpoint hash, weights-only loading,
finite checkpoint checks, new-output/project-boundary/symlink/production-resource
guards, explicit import/trace/conversion stages, and no automatic promotion advice.
`--experimental-id` is now required; canonical command examples updated.

`scripts/focus_export_parity.py` validates frozen reference hash, reviewed source
observations/PNG/crop bytes, membership/labels, runtime, training/challenge isolation,
compiled metadata and checkpoint identity before production CPU inference. It
records probability errors, decisions at0.5/0.70/0.85, ambiguity support, model hashes
and cold/warm timings. Fixed tolerance0.01 plus zero threshold disagreements was
documented before evaluation. Twelve same-app crops cannot establish general parity,
especially near thresholds when scores are saturated. No public library/API changes.

`compile_compare.py` is prepared but **not executed**: unique compiled directory,
180s subprocess bounds, compile→actual parity CLI, artifact hashes and both MiB and
decimal MB size accounting. The prior exporter labels its5MiB calculation “MB”;
report both, do not silently waive a decimal5MB requirement. No package exists yet.

## Concrete runtime blocker

Exact attempted command (host permission approved for normal CoreML caches;
TMPDIR points to `.build/debug-output/focus-launch/tmp`):

```
.venv-yolo/bin/python scripts/export_focus_ring_coreml.py \
  --weights NativeUITrainer/focus_ring_runs/fdr007-native-incremental/weights/best.pt \
  --output-dir NativeUITrainer/focus_ring_runs/fdr007-native-incremental/export-01 \
  --experimental-id fdr007-native-incremental
```

Owned PID82281 started17:08:00Z and was terminated at approximately17:18:12Z,
elapsed612s (manual deadline observation exceeded the600s target by12s), exit143.
No output directory or converted artifact; retained `export.log` is empty because
the executed version lacked pre-import stage logging. That is corrected for the
next attempt. No export rerun was launched. The final symlink preflight/logging
additions were tested after launch; they did not alter the already-running process.

`export-startup-sample.txt` shows Python import/file reads. Open-file observations
advanced through joblib, SciPy BLAS and sparse modules. A separate import-only
probe, with a hard60s timeout and30s Python traceback, printed Torch2.13.0 then
timed out exit124/60.015s. `runtime-probe.log` locates the chain at
coremltools `_deps` line68 → scikit-learn → SciPy stats/interpolate native-module
loading. No model is loaded by this probe. Both owned processes are finished.

The evidence identifies the failing startup boundary, not why native module reads
are slow. There is no permission error, conversion error or TTR involvement.
No security weakening, package install, dependency deletion, alternate environment,
system-service restart or repeated unchanged export was attempted.

## Verification and acceptance

- `python-tests.log`:68 tests, exit0,2.264s; `focused-tests-final.log`:5 export/parity
  tests, exit0 after adding threshold-support reporting. Covers unsafe/missing/
  existing destinations, symlinks, production paths, model identity mismatch,
  changed reference, output collision, duplicate/reordered/invalid scores and
  small probability changes crossing a decision threshold. Ordinary tests use
  deterministic test-only data, not inference.
- `swift-build.log`: exit0,2.88s, no warnings.
- `swift-test.log`: exit0,93 tests,2.320s, normal host CoreML cache approval;
  no simulator/network. No Swift source changes in this tranche.
- `git diff --check`: passed. No git writes or model resource edits.
- Export, compile, size and real parity acceptance: **blocked/not run**, not passed.
- No time waiting for TTR; runtime wait approximately672s across export and probe.
  No new training or simulator operation.

## Resume and next action

First qualify the **local export runtime** with bounded Torch+coremltools import
readiness; diagnose the SciPy native-load/read delay before allocating another
export. If repair needs dependency/environment changes, request that exact scope
rather than altering installed packages implicitly. Once ready, run one externally
deadline-enforced export with a fresh log; the original export destination is absent.
Then use the prepared compile/compare path, inspect actual probability/threshold
differences, size and latency, and finish the genuine integration handoff. Preserve
the shipped model and prior FDR-007/checkpoint/challenge artifacts throughout.

No background work remains. The assigned end-to-end export tranche is incomplete:
local runtime readiness blocks all genuine artifact-dependent criteria; software,
tests, failure diagnosis and documentation are delivered. SMB coordination is not
applicable to this local-only blocker; no noisy shared update was published.
