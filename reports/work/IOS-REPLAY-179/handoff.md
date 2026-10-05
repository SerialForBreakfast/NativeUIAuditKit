# IOS-REPLAY-179 — mixed replay comparison

Status: complete comparison; development acceptance failed. No promotion.

## Scope and evidence

New runner reuses resident Ultralytics training and existing strict prediction/scoring
entrypoints. Frozen176proposal retained:216balanced page-placement images plus216
already-admitted replay images, including80negative fillers. All432image/label bytes
and parsed labels validate; no evaluation-role or duplicate-pixel admission. Original
training parents checked; full annotations retained. Monitoring is in-sample only.

Run021: fresh019last,10epochs,batch8,640,AdamW1e-4,nbs64,seed42,cosine,warmup.25,
AMPoff,workers0,full-frame/noaugmentation.540minibatches,69planned optimizer updates,
14warmupbatches. Event schedule matches020, epoch-cosine staircase does not. This
is a practical compute-matched replay comparison, not a pure schedule-isolated test.
Actual optimizer calls are recorded for terminal equality. MPS warns about some
nondeterministic operators; seeded execution does not establish bitwise reproducibility.

Sealed protocol: `attempt02/artifacts/protocol.json`, seal
`2f562bcff3b984e64459c7165b517c0ee3490868e481a6d16ae73707c8c70b07`.
PID48746; fixed-last checkpoint selection,2GiBoutput ceiling,standing no-wall-cap.
Initial prepare failed before training on string/Path hashing; its partial artifacts
are preserved. No failed training resumed, no shipped resource changed.

## Verification

- `scripts/replay179.py prepare`: corrected attempt02 exit0, real432-member intake.
- `python -B -m unittest discover -s scripts -p test_replay179.py`:4tests passed,
  including role/duplicate/ancestry/changed-membership/evaluation-overlap failures,
  output collision, gradient accumulation and acceptance failure behavior.
- Prior `test_fit175.py`:4tests passed unchanged.
- Offline `swift build --disable-automatic-resolution`: exit0,3.38s after scoped
  sandbox escalation. Default concurrent tests stalled; stopped only owned helper
  and parent. `swift test --disable-automatic-resolution --no-parallel`:exit0,
  142tests (14XCTest +128SwiftTesting). Logs `.build/replay179-*` retain both attempts.
- Training startup saved args match every frozen field. No TTR/device dependency.

## Terminal results

Training exit0,1036.055s;10finite epochs,69actual optimizer calls exactly match
the plan. Fixed-last SHA256
`550ea6fb3823f4b4d0a23249bd28dcd459f8565f65484307bbd41395f83b337a`.
`replay179.py infer` and `report` exit0;216fit +96development +2400retained
records validated/scored. Combined prediction progress125.4s (not model-only
latency). Existing019/020predictions reused, no second control inference.
Evaluation seal `24b7fe0807bbfd70c9b7981fb43dfa6a41ba5c4f6079d7a3319f7b7b20907b51`.

| Measure | Run019 | Run020 | Run021 |
|---|---:|---:|---:|
| Retained custom AP50 | .882978 | .871533 | .896409 |
| Page development TP/96 | 19 | 59 | 49 |
| Page development AP50 | .343791 | .627804 | .597936 |
| Fit leading/center/trailing TP/72 | 0/62/8 | 70/72/56 | 60/72/35 |
| Sheet TP / FP | 24 / 218 | 23 / 235 | 24 / 459 |
| Sheet AP50 | 1.0 | .210156 | 1.0 |

Candidate page FP17 fails≤4. CancelAction TP80/FP259 fails FP≤73; mapView100TP/0FP
passes. ScrollIndicator AP.25 fails≥.3481 even though operating TP improved0→50;
FP58. All14frozen gates are explicitly reported: retained aggregate,center fit,
sheet AP/TP,cancel TP,map TP/FP pass; seven others fail. All38supported class deltas
reported; absent classes stay unavailable. These are custom matched metrics, not
official Ultralytics/DS-G8 results.

All33fit localization misses are KitchenSink; another13KitchenSink and3UIKitControls
cases are low-confidence matches. Replay restored sheet ranking, but did not retain
the stronger page fit. Half the page presentations and changed LR staircase prevent
a clean causal claim about replay alone. Perfect sheet AP can coexist with459FP:
AP ranking after full recall does not establish operating-point usefulness.

## Outcomes

Software verified: preparation, tests, actual trainer/exporter/scorer all passed.
Data eligible: existing training-only membership, no new admission or holdout claim.
Integration: local PyTorch/MPS path verified; live TTR/CoreML not assessed.
Model: development gates failed; no DS-G8 or production promotion.

Next substantial tranche: IOS181complete019/020/021case audit and one evidence-backed
exposure/sampling proposal, then its qualified comparison; independently intake180
worker returns when available. Do not recapture or tune thresholds against this result.

Big Dog180A/B/C dispatch is independent; see ../WORKER-180/coordination.md.
Pre-existing dirty work and staging were preserved; no Git writes.
