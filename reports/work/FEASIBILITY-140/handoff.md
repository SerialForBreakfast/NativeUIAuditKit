# FEASIBILITY-140 — completed diagnostic, numerical outcome inconclusive

One preregistered fitted witness solve completed with status1 (time limit),
82,746iterations and no verified feasible witness. Solver60.080997s, whole entrypoint
62.250013s, PID32816. This neither proves feasibility nor infeasibility. No model
checkpoint was emitted; original DTM036/other failed candidates remain unchanged.

## Scope and implementation

`linear_feasibility.py` uses residentSciPy1.18.1HiGHS dualsimplex to minimize correction
infinity norm without an upper norm bound.993fixed constraints:984prior protection
plus9reviewed native intervals;1152correction dimensions. Targetlogit(.85)+.001,
unchanged inference thresholds, row-scaled inequalities,1e-8solver tolerances,
60secondsolverbudget. Original-space violation≤1e-6 and float32head/reload gates
are required before accepting a witness. No arbitrary successful status is enough.

`feasible140.py` revalidates the existing138protocol and exact source/admission/cache
bindings, records the problem hashes before solve, and routes any witness through
the existing transition head. UnknownBalance and quantized/localized diagnostic
labels never enter constraints. No new capture, data role, private transfer, export,
promotion orGit writes. Resident environment only; no dependency installation.

Frozen result: `NativeUITrainer/focus_ring_runs/feasible140-dtm040/result.json`.
Problem/source pins: `artifacts/ready/protocol.json`. The saved timeout is terminal;
no retry/resume was started after observation ended or after worker onboarding.

## Independent conditioning diagnostic

Read-only analysis of the same signed constraint matrix (993×1152):18zero rows,
82zero columns. Nonzero absolute coefficients range4.72197e-11to21.84359. After
row scaling, largest singular value291.8497; numerical rank967at7.46538e-11tolerance,
but only683singular values exceed1e-6times the largest. Rank varies with tolerance;
this is evidence of near-dependence, not proof that labels conflict. No singular
directions were discarded or constraints weakened. No second fitting objective run.

These diagnostics narrow the next numerical experiment: test an equivalent
formulation/scaling and a different suitable solver method, with the same
original-space acceptance check. Do not merely increase the same iteration budget
or report a numerical timeout as an architectural impossibility.

### Exact-conflict and residual-scale audit

Fresh source-bound `correct_joint139.inputs()` read-only audit after worker intake:
all 18 zero-correction-feature rows already satisfy the target (minimum slack
1.74064196). Nine exact repeated-feature groups cover 34 rows; none has an
incompatible positive lower bound and negative upper bound. This excludes those
simple contradictions, not general linear infeasibility.

Five missed native intervals have signed baseline logits -350.35657, -412.05389,
-411.36670, -311.78485 and -458.75702. Largest required signed residual is
460.49262. Nonzero column L2 norms span 0.0454269 to 55.97293. Large wrong-sign
baseline confidence and unequal feature scales are concrete numerical burdens;
neither is proof of unlearnable labels. Audit completed in 2.7959 seconds, exit 0,
without optimization, checkpoint creation, data-role changes or capture.

Next comparison should explicitly preserve the original-coordinate norm objective
when column scaling: transforming variables without transforming the norm bounds
would silently change the experiment. Zero columns may be fixed at zero and
already-satisfied zero rows removed exactly; no near-singular directions may be
discarded as if they were exactly zero. Verify every original constraint and actual
float32 inference before claiming a witness. A new solve still needs its own
preregistered run; none was launched during this audit.

## Verification

Real `scripts/feasible140.py --ready reports/work/FEASIBILITY-140/artifacts/ready`
returned exit0 with explicit solver status1, not a successful-model claim. Wrapper
success means the diagnostic completed and preserved its outcome.
Unit coverage includes feasible minimum norm, contradictory labels, zero-feature
identity constraints, rescaling, invalid inputs and the60secondbudget contract.
Focused suite: 35 Python tests passed in 0.548 seconds. Integrated offline Swift
build and serial test pass: 142 checks passed. `git diff --check` passed.
Logs `.build/feasible140-{tests,run,build,test}.log`. Same resident Python,
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build"`; conditioning
analysis used two BLAS threads. Offline Swift used existing project-local caches
and explicit serial native checks. No production code changed in this tranche.

Software verified independently of numerical outcome. Existing data eligible for
this scoped diagnostic only. Fresh live integration not assessed. Model gate not
assessed: no witness. Model-workflow skill preserved this distinction and prevented
an unsupported feasibility or generalization claim.

## Coordination and continuation

Maintainer redirected the active solve to joe-big-dog onboarding; exact solver
handle was resumed until its terminal result, then software verification completed.
Worker smoke request published/read back separately under WORKER-SMOKE141. At this
check only the worker hello exists; no acknowledgment/process/result. TTR remains
18:46:20Z/expired. No redundant peer status write for this local numerical timeout.

Next substantial tranche: (1) independently review the worker result when available,
qualifying training versus allocation and checking requested seeds/metrics/replay;
(2) one preregistered equivalent, numerically conditioned feasibility comparison,
with bounded execution and original-space residual checks; (3) select optimizer
or representation work only from that evidence. Do not send private training data
to the worker or ask for installs under the synthetic-smoke assignment.
