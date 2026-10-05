# IOS185 — residual-error and exposure audit

Completed2026-10-05; no inference, training, capture, role change or promotion.

Software verified: actual diagnostic/proposal entrypoints,11focused tests and
offline Swift build/142tests pass. Data: reused pinned training/development evidence;
no new admission. Integration: local analysis passed; live TTR not assessed.
Model gates: unchanged184failure, no new model evaluated.

## Findings

All per-class operating counts reconcile against019/020/021/022saved reports.
Full case inventories and spatial FP associations retained in ignored
`artifacts/diagnosis.json`; association atIoU.5 is not object identity.

| Run021→022 retained comparison | Resolved FP | Introduced FP | Lost TP | Gained TP |
|---|---:|---:|---:|---:|
| cancelAction | 148 | 0 | 0 | 0 |
| sheet | 140 | 17 | 0 | 0 |
| mapView | 0 | 11 | 0 | 0 |
| pageControl | 2 | 13 | 25 | 32 |
| scrollIndicator | 25 | 0 | 41 | 17 |

The96page probes separately recover9hits without losing one;2newFP/5resolved.
Against020, however,022loses2probe hits and gains1;11newFP/1resolved.
Sheet FP:319OnboardingPage+17EmptyState; cancel:93CardDetail+18WizardStepFlow;
all11new map FP are GalleryPage. Median FP confidence falls sheet.869→.587 and
cancel.763→.622, but this does not authorize threshold tuning on exposed evaluation.

Fit185positions:022's31misses are26KitchenSink geometry failures and5UIKitControls
low-confidence matches. The24trailing KitchenSink misses have median best-candidate
height ratio1.853, horizontal error.0434target widths andIoU.4704; resized target
height4.4608pixels. These are oracle geometry diagnostics, not deployable selections.
Compared with021,7geometry misses and13low-confidence cases recover;2hits become
low-confidence. Compared with020,22hits become geometry misses. Context replay
has not solved the thin-box fit problem.

## Exposure and computation

Used resident `BaseDataset.set_rectangle` with header/label inventory, not a loader
or rewritten shape formula. Initializer strides independently checked[8,16,32];
training pad0, stride32. Sorting/group IDs and exact batch shapes are retained.

| Run | Page target presentations | Per-epoch input pixels | Epochs |
|---|---:|---:|---:|
|020|4320|42598400|20|
|021|2160|91095040|10|
|022|2550|87818240|10|

021→022page support rises216→255images per epoch; cancel140→179,map16→40,
scroll32→56;sheet16unchanged. Pixels/epoch fall3.6%. Same batch/update schedule
therefore does not mean equal target exposure or identical pixel work. No causal
claim that empty negatives alone caused the earlier failure.

## Next decision and verification

Stop varying replay composition for the next comparison. Frozen186proposal changes
only box-loss weight7.5→15, holding022membership/schedule and019initialization fixed.
It tests the persistent over-tall-box hypothesis while retaining every original
precision/retention gate. It may fail; no threshold changes or automatic sweep.
Proposal remains non-executable until isolated paths, exact preflight and next-run
logging are bound by186. No training launched in185.

- `diagnose185.py`: exit0,60.018s corrected run. First attempt failed before output
  on legacy020protocol structure; explicit checked adapter and regression tests added.
- `proposal185.py`: exit0. Missing-candidate groups now report unavailable geometry,
  not invented zero; regression test covers the initial empty-median failure.
- `test_diagnose18*.py`:8passed; `test_proposal185.py`:3passed.
- Offline final build/serial test exit0; logs `.build/diag185-final-*.log`.
- Diagnosis seal `697bf84aafc867170e2950d960b375bc75ef7aa3eaed5662094b4e59820ea556`.
- Proposal seal `b650a66d8da3c715c70bb2a017cf2e8006d0d86cfe9cfabc90238df689b85b88`.

Pre-existing dirty work preserved; no Git writes. Big Dog180B reports exact resume
after cooperative yield in `worker180-resume-01.json`; no terminal180B/C artifact
available at check. Peer report is not proof of a currently live remote process.
No local dependency or repeated acknowledgment request. SMB update not applicable
for this local iOS diagnosis. Next substantial tranche:186controlled comparison
through complete matched evaluation plus independent180B/C return intake if ready.
