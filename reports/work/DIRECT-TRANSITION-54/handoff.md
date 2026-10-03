# DTM001 — approved candidate executed, not ready for use

October3,2026. User approved the exact24Fixture/train,5Settings/development split and
one30epoch candidate. Original source metadata/proposal preserved; scoped admission
records the change. No capture, export, production replacement, downloads or Git writes.

| Outcome | Result |
|---|---|
| Software verified |65Python checks and134offline Swift tests passed|
| Data eligible |Exact29member split admitted for this development experiment only|
| Integration qualified |Actual trainer and saved-checkpoint reload passed; live TTR not exercised|
| Model gates |Production gates not assessed; candidate fails useful paired localization|

## Results

| Metric | Training24 | Settings development5 |
|---|---:|---:|
| Raw change/no-change correct |24|2|
| Both focus boxesIoU≥0.5 |2|0|
| Confident joint success |2|0|
| Decided / abstained |24/0|3/2|
| Mean before-boxIoU |0.4023|0.0401|
| Mean after-boxIoU |0.3954|0.0045|

Settings: both true changes classified correctly, all3unchanged examples wrong at
the raw0.5threshold. At fixed0.85confidence,1false change is emitted and2unchanged
cases abstain. None localize both boxes sufficiently. The old measurement baseline
emits1correct unchanged decision and abstains4times; it is not a comparable box
regressor. Five exposed pairs are not a final benchmark or a reliable population estimate.

This is not just domain transfer: localization is weak even on training. Low combined
loss(0.753225→0.009214)does not imply boxIoU success. A localization-sensitive loss/
representation deserves the next controlled test; these results do not establish
that more epochs, higher resolution or a larger model would fix it. No retuning done.

## Execution and verification

- Preflight exit0: `scripts/train_focus_ring_detector.py --experiment-protocol
  reports/work/DIRECT-TRANSITION-54/protocol.json --experiment-arm transition-direct-pixels
  --experiment-approval reports/work/DIRECT-TRANSITION-54/approval.json --name direct54-dtm001 --preflight`.
- Actual execution: same command with `--execute --experiment-id DTM001`, exit0.
  Interpreter `.venv-yolo/bin/python`, `PYTHONDONTWRITEBYTECODE=1`.30epochs,
  90batches/optimizer updates, scratch initialization, CPU2threads,Adam0.001,
  batch8,seed42,96×64orderedRGB, fixed-last. Run-reported15.896seconds includes
  revalidation/fit/scoring. Process PID unavailable because host `ps` was denied;
  tool session6075completed. Logs `.build/direct54-{preflight,training}.log`.
- Saved-checkpoint evaluator CLI exit0: `scripts/evaluate_direct_transition.py
  --result NativeUITrainer/focus_ring_runs/direct54-dtm001/result.json --output
  reports/work/DIRECT-TRANSITION-54/checkpoint-evaluation.json`. Revalidates roles,
  source/config/code/dependency pins and membership; actual predictions match all5
  terminal development predictions. Training rescoring is diagnostic, not selection.
-20warm samples across5Settings pairs: median4.099ms,p954.160ms. First measured
  pair15.728ms, load478.439ms. Resize+forward+box decoding on CPU; PNG loading excluded.
  First pair is not process-cold startup. No on-device/CoreML latency claim.
-65focused Python tests2.412s; `.build/direct54-python-tests.log`. New tests reject
  changed checkpoint decisions/probabilities/boxes and prevent classification success
  being reported as joint localization success.134Swift checks pass; logs
  `.build/direct54-swift-{build,test}.log`. Preserved unchanged53verification evidence.
-Checkpoint616,661bytes, run625,127bytes (well below2GiB).5.2GiB available at preflight.
  Raw weights and detailed JSON remain gitignored. No promotion eligibility inferred
  from size or execution success.

## Pins and next tranche

- Corpus: `9735108bf5ae011dfb17c07f7d49c4b42dfba4c9e1e027459a2b377047f589aa`
- Protocol: `9b4255f08a9d54ac778de1a76766cacc031c77112f7d19c1681ee6626b5b8439`
- Checkpoint: `151b88d06c6403c0f8ab0d7e7866cfb19d69b0207f42931f5e785e9d27199e18`
- Result: `bd88bb4434c1269ba3003266ac4de77d92782eb75d0689f3ba0b16167af3fff8`
- Checkpoint evaluation: `f41c8de112d726f145438f11394ab2cbaabdca56e042dcacf38f795e01df3a22`

Next: freeze one localization-first experiment using the same admitted split,
box-sensitive objective and explicit before/after localization diagnostics. Require
training-fit evidence before interpreting transfer; retain the same development
thresholds and report no-op errors. A second run needs its own approved scope—none
was launched automatically. Larger independent data remains necessary for qualification.
SMB not applicable: no new producer requirement, transfer or runtime finding; local
model results stay in NUIAK. Existing cleanup requests are untouched.
