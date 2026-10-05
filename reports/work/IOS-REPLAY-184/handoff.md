# IOS184 / Run022 — positive-context comparison

## Delivered scope

Thin isolated adapter reuses179preparation/trainer/exporter/scorer without modifying
its sealed code or artifacts.432existing train members:216fit,136unchanged positive
replay,80diverse labeled replacements for empty fillers. Full image/annotation/label
hashes, decoding, ancestry, split isolation and source pins verified before launch.
No new data admission, capture, evaluation-role change or production modification.

Fresh optimizer from019last; fixed10epochs,640,batch8,workers0,MPS,seed42,AdamW1e-4,
nbs64,warmup.25,cosine,AMPoff,noaugmentation. Same settings/schedule as021except
membership and isolated paths. Co-occurring label exposure and rectangular batch
shapes change intentionally; this is not equal pixel work.2GiBcap/no-wall-limit.

Protocol seal `61feff4f6ae8c45615357246d5869858f331078ebd5f6e2cbcf8df7dd20587e8`.
Launch binding pins adapter,181proposal,179control and resolved protocol.
PID55885; training exit0,943.503s. All10epochs finite;69optimizer indices exactly
match schedule. Fixed-last selection; in-sample monitoring is not validation.
MPS nondeterminism warnings retained; no bitwise reproducibility claim.

## Verification

- `replay184.py prepare`: full432-member preparation passed.
- `python -B -m unittest discover -s scripts -p 'test_replay*.py'`:17tests exit0.
  Includes184binding failures and existing ancestry/collision/schedule/gate checks.
- Offline Swift build and serial tests exit0;142tests (14XCTest +128SwiftTesting).
  Logs `.build/replay184-build.log` and `.build/replay184-test.log`.
- `replay184.py train`: exit0; `completion.json` records exact checkpoint/timing.
- `replay184.py infer` and `report`: exit0; all2712records validated/scored.
  Export progress12.3sfit,5.1spage,123.3sretained (not model-only latency).

Existing controls reused; no recapture or redundant control inference. Pre-existing
dirty changes preserved, no Git writes.

## Result and decision

| Matched measure | Run021 | Run022 |
|---|---:|---:|
| Retained custom AP50 | .896409 | .899967 |
| Page development TP / FP | 49 / 17 | 58 / 14 |
| Page development AP50 | .597936 | .619261 |
| Fit leading/center/trailing TP per72 | 60/72/35 | 68/72/45 |
| Sheet TP / FP | 24 / 459 | 24 / 336 |
| CancelAction TP / FP | 80 / 259 | 80 / 111 |
| MapView TP / FP | 100 / 0 | 100 / 11 |
| ScrollIndicator TP / FP | 50 / 58 | 26 / 33 |

Eight of14unchanged development gates fail. Positive replay improves some operating
errors versus021but does not recover020page59TP/4FP,019sheetFP218/cancelFP73/mapFP0,
or≥90%trailing fit. Sheet AP.985784 and scroll AP.301087 remain below019's1/.3481.
Fit residuals:26KitchenSink localization misses (2leading,24trailing) and5UIKitControls
low-confidence matches (2leading,3trailing). Center72/72retained. All38supported
class deltas are in the sealed report;3unsupported classes remain unavailable.
These are custom matched development metrics, not official COCO or DS-G8 results.

Checkpoint SHA256 `d40ad18f8d7dea266082de153a3cf078845cf2c53bd277735d79aa4d226f8e6d`.
Evaluation seal `58d0f7baff8bdc1a760c9bc657c716b22933603b60c05f49e4d53ce2f95d7f84`.
Training outputs242436606bytes, below2GiBcap. No extraepochs/export/promotion.

Software verified: focused17tests, offline142Swift tests and actual entrypoints.
Data eligible: pinned existing training-only membership; no independent-holdout claim.
Integration: local MPS verified, live TTR/CoreML not assessed. Model gates: failed.

Next185: reuse019–022predictions to fully account remaining geometry/FP failures,
separate context recovery from newly introduced errors, audit target exposure and
freeze one justified next comparison (or reject further replay). No blind extraepochs.
In parallel180A diagnostics received/verified;180B/C remain independent. ART183
requires exact producer source/schema before semantic intake, not another capture.
