# FOCUS-ARTWORK-AUDIT-01 — complete for review

| Outcome | State | Evidence |
|---|---|---|
| Software verified | Pass for scoped audit | Actual150pair audit; four helper checks;16existing contract tests; offline Swift build,14XCTest+109Swift Testing |
| Data eligible | Existing use unchanged; no new admission | 300crops/559frame-crop files hash/pixel checked, all150paired IDs accounted, no identical within-pair crop pixels |
| Integration qualified | Metadata handoff only; new archive intake not run | Two producer metadata hashes verified; native12/native100 NOT downloaded/accepted; packet publication/readback verified |
| Model gate passed | Not assessed here; FDR015 failed unchanged | No inference, training, recalibration, export or promotion |

## Acceptance

- Complete artwork inventory: `audit.json`, exact FDR015 protocol/source references,
  all150pairs and geometry/content/effect/ancestry accounting. Original hashes
  verified again after rendering; metadata fallback bound to frozen frame bytes.
- Visual diagnosis: all seven sheets/27source representatives inspected and one
  native-image full frame checked. Retained Home failure pages from FDR015 reused.
  No newly invented crops or labels. Unknown effect metadata stays unspecified.
- Concrete findings: only24explicit native-image pairs; three procedural motifs,
  two backgrounds, one sparse row structure, no supplied artwork assets. All150
  reported areas unchanged by focus. This is a transfer-risk diagnosis, not causal
  proof or automatic rejection. [Findings](findings.md).
- Next action: one exact paired-loss frozen-feature experiment proposed, with
  unchanged guards and explicit separate calibration prerequisites. No new run ID
  or model implementation. [Proposal](next-experiment.md).
- Producer consequence: follow-up under existing
  `nuiak-20260929-focus-representative-results`, asking box/caption semantics and
  prioritizing retained contrast evidence. No new capture or source edit authorized.

Verification commands: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts
.venv-review/bin/python reports/work/FOCUS-ARTWORK-AUDIT-01/audit.py` exit0;
first inline diagnostic attempt hit an incorrect pixel_digest call before outputs,
corrected by using the existing(root,record) interface. No data mutation occurred.
Helper tests exercise valid image, changed file hash, changed pixel hash and
outside-project path rejection (`audit-helper-tests.json`). Existing reset,
sampler and fixture-review tests:16pass (`focused-tests.log`). Offline Swift
build/test with automatic resolution disabled and project-local cache/config/
security/TMPDIR:pass (`swift-build.log`,`swift-test.log`). Diff check passes.

Only report-local audit code and research/task documentation changed; trainer,
metric implementations and production library untouched this tranche. Existing
unrelated dirty-tree work retained. No Git writes or temporary outputs outside
the project. Generated evidence is gitignored, not independently backed up.

Remaining: approve implementation+one paired-loss experiment; separately assign
named native12/native100 receipt and crop/contrast QA. Producer metadata already
lists the artifacts, so new capture is not a prerequisite for that intake. No
need for human redraw now. No active process or automatic monitor. The assigned
audit/proposal is complete; further execution is a new assignment, not unfinished
audit work. Coordination details: [coordination.md](coordination.md).
