# GEOMETRY-60 — diagnostic passed, full candidate underfits

October3,2026. Goal continuation; prior GEOMETRY-58/59 dirty changes preserved.
No Git writes, new data admission, runtime capture, export or promotion.

| Outcome | Evidence |
|---|---|
| Software verified |40Python tests1.936s; offline Swift build/134tests pass |
| Data eligible | Existing24Fixture train/5Settings exposed-development unchanged |
| Integration qualified | Actual trainer/evaluator/diagnosis/prediction CLI;7checkpoint parity passes |
| Model gate passed | Tiny-fit gate4/4passed; full candidate fails useful fit/transfer, no release qualification |

## DTM007 diagnostic

Same4pairs/120epochs,881,819parameter context model,96×64,Adam0.001,batch8,seed42,
fixed-last. Replace geometry BCE with SmoothL1(beta1) against target logits clamped
at1e-4/1-1e-4; retain GIoU/cell/change losses and decoding. Training labels never
enter prediction. Exact fitted pairs:4/4paired boxes,8/8cells,4/4change. Endpoint IoUs
0.8882–0.9738; geometry L10.006123. This passed the exact source-bound candidate gate.

PID17847 exit0,120updates,16.877s including intake/fit/scoring. Checkpoint
4f6c4bab5152d6901e5d3ac5b388ad1fbfdca2f5de77af90b297def6ef0ead7d;
protocol953287eaf4393e7ff30876ac1cc41ce27652c8c2d355647c0673aaecdcc6988d.
All24train-role rescored, only4fitted:12/24paired,18/24change. Settings0/5paired,
5/5change,3decided2abstain. Warm CPU4.259ms median4.359ms p95, PNG load excluded.

## DTM008 conditional candidate

Fresh initialization on all24admitted training pairs, same architecture/objective,
30epochs/90updates,fixed-last; five Settings cases remain exposed development.
PID17972 exit0,18.806s including intake/fit/scoring. Checkpoint
e98d26bc045690311fafb55d7959a4606080798c2bcdee0af465e42ebdc09bd4;
protocol2092794573ce7fdb2014851c387695781011f9fa203d066aae148f083df64c0a.
Training paired8/24,change12/24(all predicted unchanged),24abstain. Settings0/5paired,
3/5change,5abstain. Loss9.22405→1.95349; last5epochs~1.95–1.97. Not usable navigation.
Warm CPU median4.321ms,p954.518ms; same scoring scope, no controlled speed claim.
Combined run output7,093,951bytes under2GiB; both processes terminal, no extra fit.

## Gradient evidence and verification

`diagnose_geometry_gradients.py` evaluates retainedDTM005/006logits at exact fitted
members. AtDTM006collapsed height, derivatives of mean objective are sigmoidL1
−0.000124,BCE−0.007786,logitSmoothL1−0.125,GIoU−0.007930. This shows stronger
local recovery signal, not optimizer-step size or generalization. Ground-truth cells
are diagnostic-only. `dtm005-gradients.json` and `dtm006-gradients.json` retain sources.
An initial analysis output failed because its parent directory did not yet exist;
writer now creates its validated local parent. No fit repeated; failed log retained.

Analytical tests cover extreme logits, boundary-target clamp, gradient direction,
unchanged architecture, finite combined gradients and checkpoint reload. Existing
tests cover membership/gates and legacy consumers. Actual CLI parity passesDTM008,
007,006,005,004,003,002. `cli-parity.json` pins every artifact.40Python/134Swift tests
pass; scoped host Swift execution keeps configurable caches/temp/logs project-local.
`git diff --check` passes. Logs `.build/geometry60-{focused,prepare,dtm007,dtm008,
candidate-prepare,eval,candidate-eval,diagnosis,gradient5,gradient5-repaired,gradient6,
parity,tests,swift-build,swift-test}.log`. No TTR consequence requiring SMB publication.

Complete assigned tranche: two prescribed runs, gated scale-up, gradient companion,
verification and local status updates. Overall goal remains active: full-corpus fit,
no-scroll coverage, independent transfer and qualification are still incomplete.
Next proposed FIT-61: one120epoch full24pair convergence experiment with unchanged
model/loss/roles, plus explicit fitted-ID summaries and split timing. No automatic
unchanged retry or promotion; capture remains separately authorized.
