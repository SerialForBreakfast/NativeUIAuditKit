# Usable FocusRing delivery through the simulator

**Scoped execution amendment, 2026-09-22:** follow the explicitly authorized
[parallel acquisition tranche](ParallelTVOSAcquisition.md). Its direct development
pilot and shipped baseline do not authorize scale collection, candidate training,
Office use or promotion. Repaired runtime alone does not waive label qualification.

Revision 1, 2026-09-20. Highest dispatch priority; [Tasks.md](../../Tasks.md)
is the sole state/ownership queue. Preserve active assignments. Follow the
[worker contract](../WorkerWorkflow.md) and mandatory pre-code research reading.
This plan adds model/application follow-ons to the dataset-only
[SIM-DATA contracts](SimulatorDatasets.md); it does not authorize their execution.

## Delivery and shared acceptance contract

**Direct-lane amendment:** TVGEN-03 may provide the qualified pilot/baseline and
TVGEN-04 the qualified scale corpus under ADR-0009. FR-SIM-BASE accepts that same
evidence, not duplicate inference. FR-SIM-CAND accepts either source's corpus only
after scale-schema, quota, split and eligibility review. Development-only v1.4
cannot be passed directly to training. TTR-specific comparison remains FR-SIM-TTR.
Detailed direct contracts: [RemainingDelivery.md](RemainingDelivery.md).

SIM-DATA-01 and SIM-DATA-02 proceed independently, then SIM-DATA-03 qualifies
genuine capture. FR-SIM-BASE benchmarks the shipped model before SIM-DATA-04
scale-up; FR-SIM-CAND trains one candidate; FR-SIM-TTR evaluates its usefulness.
SIM-DATA-05 is secondary and never blocks this path.

Use the pilot as development evidence only. Freeze recipe-group assignments before
scale-up; keep all pilot seeds, related variants and duplicate content out of final
validation/test. Target new training coverage from pilot errors without lowering quotas.
Do not select final test cases from candidate failures or tune on final test results.
All reports bind model hashes, producer/build identities, corpus membership, preprocessing,
thresholds and evaluator version. Missing/failed inference is not a successful negative.

Workers report software verified, data eligible, integration qualified and model gate
passed independently, with commands, exit codes, counts, hashes and limitations in
`reports/work/<packet-id>/handoff.md`. Software edits require focused adversarial tests
and offline repository build/test checks. No public API change is assumed. Source presence,
mock success, model accuracy and navigation success are distinct claims.

## FR-SIM-BASE — Shipped-model baseline and evaluation protocol

**Parent:** FOCUS-DET-05. **Inputs:** accepted SIM-DATA-03 pilot, SIM-DATA-02 manifest,
actual shipped compiled FocusRing artifact and metadata, existing evaluation/crop code.
**Scope:** targeted evaluation/report tooling, crop parity tests and additive reports.
Offline tool implementation may be dispatched before pixels; baseline inference requires
an explicit assignment and the genuine pilot. No capture, training or producer edits.

1. Resolve the shipped artifact by bytes/metadata rather than a guessed version label.
   Record its hash and optional checkpoint correspondence; do not substitute an unmatched
   PyTorch checkpoint when the shipped CoreML model is the baseline.
2. Evaluate fixture-ground-truth pairs with frame-specific boxes, 16% expansion and
   256×256 crops. Compare consumer crops with production preprocessing at edges, clipping,
   non-square frames and focused scaling. Request TTR caller-to-scorer parity evidence;
   direct ROI cropping alone does not prove expansion is absent upstream.
3. Report accuracy, FPR, FNR, precision/recall at the shipped-model comparison point of
   0.85 and hard-negative FPR, support counts and failures by theme, family and control.
   This is an apples-to-apples baseline checkpoint, not a decision to deploy all future
   candidates at 0.85. Empty groups are not passes.
4. Freeze the evaluator and split protocol. Record prioritized development errors and the
   exact training-coverage response before scale-up; final holdout remains untouched.
   Candidate threshold selection is intentionally deferred until the complete planned
   30-epoch curve is available; no intermediate checkpoint may establish it.

**Tests:** known positive/negative scores, missing artifact, failed inference, zero support,
wrong dimensions, frame-specific geometry, corrupt membership and identical-run determinism.
**Acceptance:** complete pilot accounting, reproducible shipped-model report, crop checks
and frozen protocol. Poor baseline accuracy is a finding, not a reason to hide results.
Unresolved TTR parity blocks claims about TTR, not the NUA baseline itself.
**Next:** SIM-DATA-04 with development-informed coverage; final model gates not assessed.

## FR-SIM-CAND — One trained and exported experimental candidate

**Parent:** FOCUS-DET-05. **Inputs:** accepted FR-SIM-BASE and SIM-DATA-04 corpus,
eligible partitions and separately authorized smoke/training/export assignment.
**Scope:** existing FocusRing training/evaluation/export scripts, targeted tests, isolated
run artifacts and experiment records. Never overwrite shipped resources or source data.

1. Validate corpus hashes, ≥6,000 distinct pairs, scene/theme quotas, ≥100 held-out
   hard negatives and all four required theme/type combinations. Exclude development
   groups from final holdouts and enforce group/content leakage checks.
2. Record a resolved configuration and next sequential experiment ID before execution.
   Use the established vendored MobileNetV4 baseline: 256 input, batch 64, 30 epochs,
   LR 3e-4, horizontal flip 0.5 only. Pin initialization/local weights and random seeds;
   no downloads, new augmentation experiment, silent resume or hyperparameter sweep.
3. Run only the assigned bounded smoke and one candidate. Complete the planned 30 epochs
   before selecting anything; select the best checkpoint using validation data, never test
   data. Then select one operating threshold from that checkpoint's validation membership
   against the predeclared objective; record the full curve, objective, selected epoch and
   value, and validation counts, then lock it before opening the final holdout. Also report
   the fixed 0.85 comparison point so it remains directly comparable with the shipped
   baseline. Report resource failures without automatic retries.
4. Evaluate untouched test membership at the locked candidate threshold: accuracy ≥99%,
   unfocused FPR ≤0.5%, focused FNR ≤1%, precision and recall each ≥0.98, hard-negative
   FPR ≤0.5%. Report the same metrics at 0.85 as a non-gating shipped-baseline comparison.
   Report separate hard-negative theme/type counts and rates; never a vacuous pass.
5. Export via the existing trace-based CoreML path. Verify identical-input PyTorch/CoreML
   scores and threshold decisions, report maximum/mean score differences and all decision
   disagreements; any unexplained disagreement blocks export acceptance. Verify FP16
   package ≤5 MB and existing output/metadata contract. Do not claim packaged deployment.

**Tests:** missing/ineligible data, leakage, output collisions, fresh-vs-resume isolation,
failed inference, empty denominators, export input/output parity and missing resources.
**Acceptance:** logged single candidate, complete six-gate report, shipped-model comparison
on identical final membership, export parity evidence and artifact hashes. Passing gates
qualifies only the stated simulator scope. Failed gates yield diagnosis and a separately
reviewed next experiment, not a loop.
**Next:** FR-SIM-TTR for a passing experimental candidate. Physical FR-B/FR-C remain open.

## FR-SIM-TTR — TTR focus and navigation comparison

**Parent:** FOCUS-DET-05. **Owner boundary:** NUA owns evaluation inputs/intake;
TVTestRig owns any producer/scorer/harness changes under a separate accepted assignment.
**Inputs:** accepted candidate/export, shipped artifact, frozen held-out fixture frames,
and TTR acknowledgment/evidence for candidate selection and preprocessing parity.
Offline fake-backed harness work can proceed before training; actual simulator execution
requires exact target, runtime and explicit operation authority.

1. Require explicit isolated model selection and loaded-artifact hash. Missing candidate
   must fail clearly, never silently score using the bundled model. Preserve default routing.
2. Score shipped and candidate models on identical frames/candidate boxes. Separate this
   classifier-only comparison from end-to-end TTR detection/proposal/navigation results.
   Keep all other settings and thresholds fixed. Fixture telemetry supplies truth only;
   it must not choose the focus winner or navigation action.
3. Before either model runs, freeze at least one reachable start/goal scenario per supported
   family/theme cell using final held-out recipe groups. Pin starts, goals, seeds, expected
   reachability, action limit and timeout in the accepted scenario manifest. Reset each trial
   identically under owned simulator authority. Unsupported cells are gaps, not successes.
4. Report focus-selection accuracy, wrong-focus and no-focus decisions, goal-reaching rate,
   action counts, inference/end-to-end latency and aborted trials per model and cell.
   Separate runtime failures from model errors. Check Fixture health after owned cleanup;
   preserve ambiguous/partial trials and stop instead of automatic retry.
5. A useful-improvement recommendation requires no regression in aggregate wrong-focus
   rate or goal-reaching rate and improvement in at least one of those measures. Otherwise
   report no demonstrated navigation improvement, even if classifier gates passed.
   Report sample counts and paired outcomes; do not generalize beyond tested simulator scope.

**Tests:** deterministic fake model selection, wrong artifact, missing model, crop parity,
no-focus/ambiguous scores, telemetry isolation, cancellation/timeouts, incomplete trial and
postflight failure. Genuine comparisons must name actual models and runtime builds.
**Acceptance:** reproducible paired reports, honest benefit/no-benefit conclusion and TTR
intake acknowledgment. Completion of comparison is distinct from candidate acceptance.
**Next:** separate authorized physical validation/promotion decision; Office stays released.

## Coordination and authority

Initial producer reference remains `c6ec816bd94e9526f890e4894ad6a71f9e840e58`.
The local checkout observed on 2026-09-20 is
`d57131341ef29b08958ab5a8dc21beff88507ac2`; require compatibility reconciliation and
actual app/helper/fixture build evidence, not an automatic pin upgrade.
Request TTR to verify existing capture, settling, crop parity, isolated candidate selection,
paired comparison and healthy teardown; implement only evidenced gaps under its own queue.
No SSH, Sillycon runtime mutation, Office use, Settings mapping or VoiceOver datasets.
Publishing a request is not peer acceptance or execution authority.
