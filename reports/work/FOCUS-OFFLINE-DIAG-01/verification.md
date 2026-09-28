# Verification and acceptance mapping

2026-09-27 local /2026-09-28 UTC. Completed for review, not self-accepted.
Base HEAD `be85889adb30fb931de9671d22250a8397f983a3`; read-only Git.
Pre-existing dirty research/task/Photos/coordination edits preserved. No producer
source edits, Git writes, installs, downloads or new validation inference.

## Executed checks

- Actual `freeze`/`report` CLI completes against retained evidence. Authoritative
  input-index-v2.json and analysis-v2/:3,744 predictions reproduce original metrics
  and frame decisions;2,107 image paths accepted, zero blocked/excluded;460 assembly
  rows /230 pairs audited;95 numbered sheets. Sources rechecked after reporting.
- **68 Python tests pass**,2.341s:16 new diagnosis tests plus unchanged surface,
  visual-comparison, appearance-experiment and mixed-assembly suites.
  [Final log](python-tests-final.log). Earlier65-test pass retained in python-tests.log.
- **Offline Swift build passes**,5.57s, no compiler warnings/errors.
  [Build log](swift-build.log).
- **Offline Swift tests pass:**14 XCTest +109 Swift Testing, zero failures and
  compiler warnings/errors. [Test log](swift-test.log).
- `git diff --check` passes. Shared/local YAML safely parses with duplicate-key
  rejection; shared packet readback equals local entry, all other bytes unchanged.
- Nine representative pages visually inspected; exact IDs and review limitations
  in diagnosis.md. No challenge image viewed or used for selection.

Python uses resident focus-export-01 Python3.12.9, `-B`, PYTHONDONTWRITEBYTECODE=1,
project scripts PYTHONPATH, `.build/focus-offline-check/tmp` TMPDIR. Command:

```text
-m unittest -v test_focus_offline_diagnosis test_focus_surface_evaluation
 test_focus_visual_comparison test_focus_appearance_experiment test_focus_mixed_assembly
```

Swift build/test use `--disable-automatic-resolution --manifest-cache local`;
cache/config/security/module-cache/TMPDIR under `.build/focus-offline-check/`.
Scoped normal-host compiler/runtime execution approved; explicit artifacts and
configurable caches project-local. No simulator or device dispatch. Required
repository tests retain their existing behavior, not a new model evaluation.
The new CLI never invokes inference/crop helpers; Pillow renders retained crops
alongside display-only frame previews, processing one frame at a time.

## Acceptance-to-evidence map

| Criterion | Observable evidence |
|---|---|
| Frozen protocol/predictions/crops/assembly |input-index-v2.json:34 metadata/code dependencies,2,107 image references; original model/runtime identities in pinned protocol; before/after hashes|
| Metric reproduction, paired/frame distinction |diagnosis.json results.*.reproduced; actual complete artifact counts; isolated test for paired metrics and all four frame decisions|
| Distributions/differences/ranks/margins |results.*.distributions,paired,ranks; rank intervals for ties, null unsupported/empty summaries; no selector change|
| Source/control/appearance and visual diagnosis |95 indexed sheets; diagnosis.md visual observations and ranked hypotheses with counterexamples and next observations|
|221+9 audit and proposal preservation |candidate-coverage.json:230 pairs,460 exact bounds, source/control/style/label summaries, unchanged sampling/selection/configuration/eligibility|
| Next collection/experiment decision |next-assignment.md: coverage matrix, failure→evidence→role→acceptance, quantities explicitly collection targets; no run allocated|
| Local provenance review |Read-only missing-object check at exact producer revision; existing intake blockers and prior overlap evidence; exact missing ancestry/resume condition|
| Actual Photos importer mapping |ext-cap-consumer-checklist.md: source-backed envelopes/epochs/limits, raw provenance and human review; no speculative adapter|
| Invalid hashes/protocols/predictions |Changed pixels/metadata and missing artifact; version/threshold/variant drift; missing/reordered/duplicate/bool/None/NaN/Inf/out-of-range scores rejected|
| Incomplete/conflicting inputs |Pair/control/frame/bounds binding, complete candidate counts, protected candidate roles, corrupt PNG with valid hash, invalid geometry; no silent reduced score set|
| Challenge rejection/source preservation |Challenge group rejected with forged validation role; unbound inventory rejected before pixel reads; source hashes unchanged through actual CLI|
| Determinism/no execution |Two isolated actual CLI trees byte-identical; invocation functions patched to throw; no torch/coremltools import in new standalone tests|
| Integration/handoff/status |68 Python,Swift build/123 tests; research/queue updated; only actionable consumer-contract metadata published|

## Repairs and limitations

Initial freeze rejected separately named but byte/pixel-identical paired/competition
crops; corrected identity comparison, not the source artifacts. Some assembly rows
omit proposedRole; absence is accepted only when explicit use remains allowed;
contradictory/protected roles are rejected. No gate was relaxed.

V1 left152 bounds unknown because assembly omitted them. V2 joins exact APPEAR-A2
source metadata and resolves all460. Complete neighbor context remains unknown on
422 rows; recovered geometry does not certify candidate completeness. Source-bound
metadata reports three neighbors for38 rows. An early inspection beforev2 finished
returned FileNotFoundError; the completed CLI returned0. Sandbox denied one read-only
ps request; no retry/escalation, normal tool-session completion was used.

Existing460-crop production parity and actual assembly/trainer preflight are reused
from APPEAR-EVAL-RESERVE-20260927, not rerun. Existing Photos importer tests remain
unchanged and are reused from PHOTOS-PILOT-01. Source independence, Photos native
coverage, exact wire schema/adapter and physical qualification remain open.
