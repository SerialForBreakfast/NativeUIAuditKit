# MARGIN-REPAIR-139 — guard fixed; DTM039 not an efficacy improvement

Completed October 4. Previous turn made progress by identifying the zero-slack
failure; this tranche implemented the repair, qualified it and ran one matched fit.

## Software and model results

New reusable `margin_retention.py` preserves the existing .85/.15 decision boundary.
For gap=baseline signed margin−logit(.85), it requires gap>1e-6 and retains a
reserve=min(.001,gap/2). Slack=gap−reserve is strictly positive. Inputs at/too near
the boundary are rejected for review, not dropped or silently relaxed. Existing
radial head and .999interior factor reused; historical134implementation unchanged.

Real984-case preflight: minimumslack0.0428413, initial gradientnorm19.8431,
first-step radius0.0119290, subsequent gradientnorm0.367076. Positive/negative
signs, adversarial updates, identity, exact-boundary rejection and materialization
tested. New guard fixes the demonstrated zero-slack dead zone; it does not guarantee
that radial projection is an efficient optimizer for this task.

DTM039 retains207original mixed-label examples/226identities and777previous contrast
successes. Admitted native outcomes remain2/5within-screen,0/2screen transitions,
2/2identities: the same five misses. Global-lighting negatives214/226; localized
half0/226, center16/226. No accuracy improvement, export, delivery or promotion.
Two Balance intervals still predict changed but retain unknown-focus labels.

Unlike038, no observed epoch has zero radius or gradient. Radius minimum0.0010378,
final0.00236198; gradient normminimum0.0386692/final0.233128. Raw weightnorm4.26642
versus effective0.0100772: the radial projection heavily contracts the proposed
update. Loss124.357849→124.223465 (minimum119.264946 at122); fixed-last retained,
not cherry-picked best training epoch. This supports testing feasibility/optimizer
geometry next; it does not prove the representation or retained targets incompatible.

## Controlled execution

Same DTM038 bank, labels, weighting, initialization,984constraint membership and
scales, verified by pinned hashes.9native+866contrast views become21650weighted
feature rows; no new labels, acquisition or input representation. Same600epochs,
Adam.01,seed42,CPU2threads,fixed-last,≤2GiB. Existing feature trainer reused.
Observational hooks retain all600raw-head/gradient snapshots and radius history;
they do not change gradients. Optimizer-internal slots are not exposed/saved.

PID31583; fit2.919073s, full entrypoint5.223576s. Checkpoint
`NativeUITrainer/focus_ring_runs/margin139-dtm039/last.pt`, SHA256
`95cbf751aa70e01314c3d4bf4b64e5497b355c8f2b72490241bfe06e9fc69168`.
Raw state and effective weights included; exact materialized output replay passes.
`optimization-trace.npz` plus result radius/loss history permit diagnosis without
retraining. `artifacts/ready/protocol.json` binds139guard/runner,138parent and preflight.
All prior experiment artifacts and dirty132–138/OCR changes preserved.

## Verification and independent outcomes

Resident Python with project-local temp/bytecode settings. Real
`correct_joint139.py prepare` and `train --ready reports/work/MARGIN-REPAIR-139/artifacts/ready`
exit0. Nine focused suites pass32tests(0.490s), covering the corrected guard and unchanged upstream contracts.
Offline Swift build/explicit-serial tests pass142checks (14XCTest+128SwiftTesting).
Logs `.build/margin139-{tests,prepare,training,build,test}.log`. No native source
changed, simulator launched, dependency installed, Git write or system reset.

Software verified. Existing data eligibility unchanged. Fresh live integration not
assessed. Model efficacy failed. Model-workflow skill kept frozen roles, fixed-last
selection and failed-model preservation; synthetic/fitted retention is not deployment.
TTR status still18:46:20Z/expired, with no verified new handoff in this check.
No redundant SMB publication: TTR's next action is unchanged (keep existing models
passive; no requested capture/build). This optimizer result remains local under
the shared-status relevance rule. A deployable candidate or changed evidence request
will trigger the next substantive peer update.

## Next substantial tranche

Before another learned fit, test constrained linear feasibility on the frozen
feature bank: original/contrast preservation plus known native targets, strict
thresholds and original labels. Use only resident numerical tooling; record bounds,
tolerances and primal residuals. Infeasible within a chosen norm bound is not global
infeasibility. A feasible witness would expose an optimizer limitation; then test
a properly constrained optimization method against this radial baseline. If no
reliable feasibility result, report inconclusive rather than claiming a data conflict.
Keep witness fitting exposed/development-only; no export or threshold lowering.
Pair this with source-bound audit of native versus nuisance feature support and
one batched failure report for TTR. Do not keep running unchanged600epoch fits or
request redundant screenshots. New native-motion evidence remains independently useful.
