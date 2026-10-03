# Spatial56 — diagnostic and coverage tranche complete

October3,2026. Software verified; existing data admission unchanged; local
trainer/prediction/reload integration verified; model gate failed. No capture,
new data roles, export, promotion, Git writes or TTR operations.

Implemented spatial cell/offset/size prediction in the existing ordered-frame trainer,
strict versioned configurations, exact four-member diagnostic selection, conditional
candidate preparation/preflight gate, and legacy checkpoint compatibility. Frozen
execution inputs live in `diagnostic-ready/`; earlier `diagnostic/` is an unexecuted
pre-pin preparation, not a separate experiment. Source corpus hash remains
`9735108bf5ae011dfb17c07f7d49c4b42dfba4c9e1e027459a2b377047f589aa`.

## DTM003 result and decision

PID6966,120epochs/120updates,4Fixture pairs,19.810s execution including repeated
intake/fit/scoring; initial CLI preflight time additional. Output2,400,468bytes.
Checkpoint SHA256 `047d03230e799a458206317aac47a0805f587d888350295bcc0b8fc1641a6bce`.
Protocol SHA256 `7a06f6d582d7498ef9cb1cb15e593e57e62d86be224c15192d32781f4d307518`.

- Exact fitted subset: change4/4, paired boxes0/4. Gate failed; DTM004 never launched.
- Spatial endpoint cell selection0/8, but vertical cells8/8 and horizontal0/8.
  Predicted x8–10 versus target x12; targets rank4–9 in the cell logits.
- Final loss3.0971, decomposed mean cell CE2.9936, geometry L10.08084, change BCE
  approximately8.27e-21. Size/offset learning also remains imperfect: scoring-only
  ground-truth-cell IoU ranges0.008–0.778. This oracle is NOT model accuracy.
- Local spatial heads see15×15input pixels, versus full-frame context in the change
  head. Wider context is a plausible next hypothesis, not an established causal fix.
- All24train-role examples were rescored (only4fitted): paired boxes0/24. Five
  exposed Settings development pairs: raw change5/5, paired boxes0/5, all10boxes
  invalid, all5abstained. Not a reliable detector or production improvement.
- Reload parity and actual prediction CLI pass. Warm CPU median4.156ms,p954.288ms
  excludes PNG loading. Existing DTM002 real-checkpoint prediction parity also passes.

Detailed evidence: `fit-diagnosis.json`, `diagnostic-evaluation.json`, and the run's
`result.json`. Candidate preparation exited1with `memorization_gate_failed` as
required; no automatic retraining or selection from development outcomes.

## Independent coverage audit

`diagnostic-ready/coverage.json` accounts for all29admitted pairs. No exact encoded
input collisions with conflicting targets. Training has12unchanged/displaced,
6changed/stationary and6changed/displaced pairs; zero unchanged/stationary pairs.
Settings has3unchanged/stationary and2changed/displaced. Box displacement is not
scrolling ground truth.5of58endpoint boxes are below4pixels tall at96×64.
Exactly-one-known-focus admission leaves no absent-focus evidence; one renderer
and one exposed journey cannot establish independent app generalization.

Next data specification covers scroll/no-scroll × switch/no-switch with explicit
source truth, real stationary/no-op cases, independent journey grouping, absent-focus
and overlay/animation negatives. It is a local proposal, not a producer assignment or
capture authorization. Shared-status publication is not applicable to this local run.

## Verification and next tranche

25focused Python tests pass1.807s; offline Swift build and134tests pass. Logs:
`.build/spatial56-tests-final.log`, `spatial56-swift-{build,test}.log`,
`spatial56-{preflight,dtm003,diagnostic-eval,fit-diagnosis,candidate-gate,prediction,legacy}.log`.
Numerical test fits are software fixtures, not model evidence. Pre-existing dirty
storage/model/docs preserved; no new public API. Tasks, plan, roadmap, experiment log
and the observed-learning entry are updated.

Recommended next substantial tranche: GLOBAL-CONTEXT-57, full-frame-conditioned
spatial heads with the same preprocessing and exact four-pair gate, then conditional
24/5comparison. Pair with the deconfounded intake specification; do not collect more
of the existing confounded distribution or add epochs before testing the architecture.
Its new representation/execution scope is proposed for review, not already run.
