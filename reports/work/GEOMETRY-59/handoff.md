# GEOMETRY-59 — tranche complete, overall training goal active

October3,2026. Continued from24964ec plus preserved uncommitted GEOMETRY-58 work.
No Git writes, data admission changes, capture, export or promotion.

| Outcome | Result |
|---|---|
| Software verified |38Python tests and offline Swift build/134tests pass |
| Data eligible | Existing24train/5exposed-development unchanged; no new admission |
| Integration qualified | Actual trainer/evaluator/diagnosis and five-model prediction CLI parity pass; no live TTR claim |
| Model gate passed | Fail:3/4paired boxes versus required4/4; conditional candidate refused |

DTM006 adds unit GIoU supervision at target cells during training, retaining existing
geometry BCE, cell/change losses and image-only inference. Same four training pairs,
120epochs,96×64,Adam0.001,batch8,seed42,CPU2threads,fixed-last,881,819parameters.
The target-cell oracle remains training/scoring-only, never inference input.

- Paired boxes improveDTM0052/4→3/4; cells8/8,change4/4.
- Geometry L10.03843→0.03065. One light unchanged before-frame height~0.001 instead
  of0.06328 yieldsIoU0.0157; all other fitted endpoints≥0.6884.
- All24train-role rescored, only4fitted: paired9/24,change19/24. Settings5 remains
  paired0/5,change5/5,all5decided. Not reliable localization or calibrated confidence.
- Actual candidate preparation exits1 `memorization_gate_failed`; noDTM007run.
- PID16677 exit0,20.150s including intake/fit/scoring,3,548,976run bytes under2GiB.
  Checkpoint389136af0fd7b837559d724dc17022c088a9f5f5ce86cf70801987ec2dfad8f0.
  Protocol5162da824a8bccf1ecb9d62b13b2e1b10d78cd1fc6b4d5c8b4053b35b6432280.
  Same corpus9735108bf5ae011dfb17c07f7d49c4b42dfba4c9e1e027459a2b377047f589aa.
- Warm CPU median4.274ms,p954.368ms, PNG loading excluded; not a robust speed comparison.

Independent deliverable: `stationary-capture-plan.json` freezes24development cases,
48captures across two historically qualified reference screens, two themes, three
artwork styles, and boundary-noop/interior-switch conditions. Native offsets must
remain unchanged through both brackets; no requested-state labels. All seed83related
variants remain development-connected. Planning CLI/test is deterministic and makes
no runtime calls. Execution is explicitly ineligible until an exact target/Fixture,
capture authority and reviewed interior-switch consumer adapter exist. No false claim
that the current scroll-only adapter can ingest the new condition unchanged.

Verification:38Python tests2.744s; offline Swift build/134tests pass in approved host
context, all configurable output local. Actual trainer/diagnosis/evaluation/parity
entrypoints exit0; parity passesDTM006/005/004/003/002. Expected candidate gate exit1.
`git diff --check` passes. Logs `.build/geometry59-{focused,prepare,dtm006,tests-final,
eval,diagnosis,candidate-gate,parity,swift-build,swift-test}.log`. Raw evidence under
this directory; weights remain gitignored. No active process remains; no external wait
or capture. SMB not applicable to local model iteration/planning.

Next bounded tranche GEOMETRY-60: test target-logit SmoothL1 to address the remaining
collapsed thin extent while holding context/GIoU/data fixed; add per-coordinate
gradient diagnostics. Full candidate remains conditional on4/4fit. The broad goal
is not complete: training fit, independent transfer, missing no-scroll coverage and
production qualification remain open. No automatic unchanged experiment retry.
