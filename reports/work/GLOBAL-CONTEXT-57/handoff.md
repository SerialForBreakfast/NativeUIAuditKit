# GLOBAL-CONTEXT-57 — completed for review

October3,2026; clean starting checkout7753dc7. No pre-existing changes overwritten.

| Outcome | Result |
|---|---|
| Software verified | Pass:29Python tests; offline Swift build and134tests; actual trainer/prediction/intake CLIs |
| Data eligible | Existing24train/5exposed-development admission unchanged; no new admission |
| Integration qualified | Local model checkpoint/CLI parity passes; no new TTR qualification |
| Model gate passed | Fail: diagnostic paired boxes0/4; full candidate correctly blocked |

## Controlled result

DTM004 adds pooled spatial context residuals to existing local cell/geometry heads.
Same96×64input, four training members,120epochs, seed42,Adam0.001 and losses as
DTM003. Model595,291→881,819parameters. Training loss7.04483→0.178018.
Cell selection improves0/8→8/8; raw change4/4; paired localization remains0/4.
Cell CE2.99362→0.08753; geometry L10.08084→0.08116. Predicted heights approach
zero. Correct cells do not establish correct box extent or generalization.

Model SHA256 `bc0cad5ee140c4c89a3e810f97b56ae4fd585fd6c8c9de6dc7e6b67f9ef829f0`.
Protocol `41ca7a8fdff64adb88fa44158909ccb4808ac3cd939c112bbbe7bf9d0d9cc0d2`.
Run17.150seconds including intake/fit/scoring,3,549,011bytes. Tool session96587
exit0; OS PID unavailable. No process remains. Warm CPU median4.232ms,p954.291ms
(20samples, PNG load excluded). Previous4.156ms is contextual, not a robust speed claim.

All24train-role pairs rescored, only4fitted: change17/24, paired0/24. Exposed Settings
5: change5/5 but paired0/5; all5emit decisions despite incorrect geometry. The current
decision threshold measures change confidence, not localization confidence. Not usable
for navigation. Candidate preparation exits1 `memorization_gate_failed`; noDTM005.
No capture, downloads, role changes, export, promotion or Git writes.

## Independent intake deliverable

`scripts/transition_intake_coverage.py` validates versioned metadata and actual evidence
reference hashes, unique pair IDs, journey/pixel cross-partition isolation, source-label
types and all12partition×scroll×change cells. Unknown scroll is rejected, not defaulted.
Output always trainingEligible=false. Caller pixel hashes and source semantics still
need source-specific validation; this is neither authentication nor dataset admission.
Tests include real CLI output collision/changed evidence, false model labels and leakage.
The canonical plan records required fields; no historical records were fabricated.

## Verification and retained evidence

- `prepare_context57.py diagnostic`: exit0; same corpus SHA256
  `9735108bf5ae011dfb17c07f7d49c4b42dfba4c9e1e027459a2b377047f589aa`.
- Existing `train_focus_ring_detector.py` actual execute path: exit0, logged first.
- `evaluate_direct_transition.py` and `diagnose_spatial56.py --result ...`: exit0;
  `diagnostic-evaluation.json` and `fit-diagnosis.json` preserve full decomposition.
  Ground-truth-cell oracle remains scoring-only, never prediction input.
- `qualify_context57.py`: exit0; real prediction CLI parity forDTM004/003/002,
  image-only requests. `cli-parity.json` records exact artifacts and parameter counts.
-29focused Python tests:2.213s. Required offline Swift build/test pass after scoped
  host execution. Initial restricted build failed `sandbox_apply: Operation not
  permitted`; no code/security changes to bypass it. Caches/logs remain project-local.
- Logs `.build/context57-{prepare,dtm004,eval,diagnosis,candidate-gate,cli,tests-final,
  swift-build,swift-build-host,swift-test}.log`; raw artifacts retained locally.

Completed scope: context hypothesis tested, failed gate diagnosed, intake contract/CLI
delivered, legacy behavior preserved and queue/plan/log/lesson updated. SMB not applicable:
this local result does not require TTR to change its implementation or execute work.
External wait time zero; no live capture/intake. Full source intake is included in
run/evaluation time, not a claim about pure training speed.

Next substantial tranche: proposed GEOMETRY-58, isolate geometry-logit supervision
with the same fit gate, conditional full candidate, plus retained-source observation
inventory for deconfounded acquisition. Requires assignment of that new experiment;
no further fit is authorized as an automatic retry within Context57.
