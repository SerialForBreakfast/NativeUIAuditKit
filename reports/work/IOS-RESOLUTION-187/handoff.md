# IOS187 / Run024 — completed, model gates failed

Selected full scope: one source-pinned resolution comparison, its2712-image
evaluation and prior-failure accounting, plus independent TRANSITION-CONTRAST188.
188is complete;187training and matched evaluation completed. No promoted candidate.

## Executed

- Resident exporter supports640/1280, not960; plan amended before execution to1280.
  Existing sealed trainer/exporter/scorer sources untouched.
- Same432train members and019initialization as022; box7.5,10epochs,batch8,nbs64,
  warmup.25,69updates,seed42,AdamW1e-4,AMPoff,rect/full-frame/noaugmentation.
- Input pixels per epoch87,818,240→333,578,240 (3.7985×);2550page presentations
  across run unchanged. Not equal compute or isolated training-only resolution.
- Attempt01failed checkpoint-size bound before model loading;02loaded frozen
  gradients;03completed disposable step but failed dictionary-loss serialization.
  Evidence retained. These were implementation failures, not capacity failures.
- Corrected04memory probe passed finite forward/backward and one disposable AdamW
  step, max8×3×1280×736/32labels per image,6.109s. No weights saved. Driver allocation
  19,471,007,744bytes exceeds recommended19,069,665,280slightly; training has limited
  headroom. No concurrent MPS work, batch fallback or system memory override.
- Run024 launched PID65093, unified session20462, from fresh unchanged019weights.
  Source protocol SHA256 `b64f7028c909f1b38cc3d3d1d429bfbc2ab6fdb4df9cf6f03f98d16d5c5d8838`.
  Logs/state: `attempt04/artifacts/`; run: `NativeUITrainer/yolo_runs/resolution187-r024`.
- Live follow-up: epoch1 completed including in-sample validation in297.499s;
  epoch2started on the same session. Finite monitoring losses and AP50 .44882;
  this is training-set monitoring, not retained or independent qualification.
  No terminal receipt yet. Saved arguments independently match every protocol field.
-16focused tests passed. Offline Swift build/142tests passed after integrated code;
  `.build/resolution187-{focused,build,test}.log`. Pre-existing changes preserved;
  no Git writes. Raw artifacts ignored.

## Terminal result — no restart or extension

10epochs/69updates,3185.207seconds,exit0. Fixed-last checkpoint SHA256
`ec41e3796a08a96d19e80114e667c9ef66eef93a9729431a50871a940f4e4a81`.
All2712images inferred and validated against explicit1280settings; retained inference
280.2seconds, plus fit/page.233MiBmodel-run outputs+37MiBevidence, below2GiBceiling.

| Metric | Run022@640 | Run024@1280 |
|---|---:|---:|
| Retained custom AP50 |.899967|.343954|
| Page TP / FP /96 |58 /14|70 /158|
| Fit leading / center / trailing, each72 |68 /72 /45|69 /69 /59|
| Sheet TP / FP |24 /336|20 /353|
| Cancel TP / FP |80 /111|17 /198|
| Map TP / FP |100 /11|34 /165|
| Scroll TP / FP |26 /33|34 /112|

21of31prior fit misses recover;10remain low-confidence.9prior hits become
low-confidence. No remaining fit geometry misses.24prior trailing geometry failures
medianheight ratio1.0684andIoU.77045 versus1.853/.4704. Higher resolution helps
this geometry but collapses retained performance;11of14original gates fail.
38supported classes reported, homeIndicator/unknown/webContent unavailable, not zero.
Result seal `5d8074399a9913728328e7de2fa1a737030e9e2fe157e3daa700fc78ebcaf596`.

Software passed; original training membership unchanged/eligible; terminal MPS and
prediction integration passed; model gates failed, no production promotion.189now
completes two missing fixed-checkpoint inference cells (022@1280,024@640) to identify
resolution sensitivity before another training hypothesis. No new weights or labels.

### Preserved original continuation instructions

Poll the same live session20462 first. Read execution/completion receipts and saved
args/results.csv. An observation timeout is not failure and does not permit a retry.
If training completes exit0, run `scripts/resolution187.py infer`, then `report`
with resident `.venv-yolo/bin/python -B` and project-local cache/temp environment.
Inference needs scoped MPS execution; no concurrent model run. Both entrypoints
verify pins, memory receipt, terminal10epochs/69updates and fixed-last checkpoint.
Failed training requires diagnosis, not restart or silent batch reduction.

The acceptance checks originally pending below are now evidenced above: terminal
training,2712predictions, per-class/gate report,31prior-case accounting and checkpoint.
No export/promotion.
Local-only iOS coordination is not an SMB update. The188native contrast reuses an
existing TTR request and retained24cases; exact source remains unavailable locally.
