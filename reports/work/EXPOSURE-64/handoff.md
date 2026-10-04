# EXPOSURE-64 — fit restored; transfer remains unqualified

| Evidence | DTM009 | DTM010 | DTM011 |
|---|---:|---:|---:|
| Original training box pairs |24/24|18/24|24/24|
| Four shifted conditions |47/96|82/96|96/96|
| Reversed box pairs |24/24|17/24|23/24|
| Settings box pairs |0/5|0/5|0/5|
| Retained negative box pairs |0/8|0/8|0/8|
| Negative false-change decisions |4|0|2|
| Negative abstentions |0|2|2|

DTM011's shifts were training augmentations:96/96does not establish unseen-transform
or real-UI generalization. Settings raw change2/5for all3models. The8negatives form
4decoded-pixel connected groups/8unique frames, same Fixture renderer ancestry.
Four are boundary no-ops, four content mutations; no condition or data-role changes.

## Implementation and execution

Reused trainer/preparer with explicit600epoch configuration. Same architecture,
loss, seed, optimizer,24/5membership and120variant bank; first120epoch losses and
augmentation counts exactly matchDTM010.14400samples/1800updates versus2880/360;
individual variants92–146exposures. Final loss0.12283. No second experiment.

Registered DTM011 before actual trainer CLI execution with
`--experiment-arm transition-direct-pixels --name exposure64-dtm011
--experiment-id DTM011 --execute` and `ready/{protocol,approval}.json`.
Exit0,PID22387. ProtocolSHA
`b101d83c982322e39c3b573402d2db4b8dc237d70d70519c46061e288cf3728c`.
ModelSHA `2fa1b8d8d47f8700256997ef61263ad9c4f5a69897c1bd517d744a008d9570b6`.
Run output3,692,168bytes;29.071s wrapper:17.398sintake,11.532sfit/setup,
0.006scheckpoint,0.134sscoring. Initial CLI preflight additional. Warm CPU median
4.347ms/p954.498ms excludes PNG loading. No capture or external waiting.

## Verification and independent deliverable

- Sealed `evaluation.json`, `sensitivity.json`, `comparison.json` show24/24fit,
 169diagnostic evaluations with5off-frame targets rejected and reload parity.
- Actual prediction CLI parity passes10retained checkpoints (`cli-parity.json`).
- New `evaluate_retained_negatives64.py` revalidates original package/sidecars,
 native geometry/focus/offsets, cleanup and bytes; no labels enter inference.
 `negatives.json` evaluates the two frozen prior models; `candidate-negatives.json`
 adds the completed fixed-last candidate, with no effect on selection/training.
- Connected-component accounting prevents treating duplicated before/after frames
 as independent support. No raw evidence was edited or calibration data admitted.
-85Python tests pass in3.391s; offline Swift build/test exit0,14XCTest+120Swift
 Testing. Logs `.build/exposure64-{tests,swift-build,swift-test,parity}.log`.
 `.build/exposure64-exposure-audit.log` proves exact120epoch prefix equality.
- Preserved all prior Geometry58–Robustness63dirty work and checkpoint evidence.

Software:passed. Existing training data eligibility:unchanged; new negative training
admission:not granted. Offline model/CLI integration:passed; live producer integration:
not assessed. Model qualification:failed/not established. No Git writes, devices,
downloads, export or production changes. SMB not applicable to these local model
results; existing producer compatibility request remains separate.

## Next substantial tranche

GENERALIZATION-65: freeze all3models, test unseen shift magnitudes/diagonals and
duplicated-frame zero-visual-difference inputs. Prepare an exact8pair negative-data
admission proposal, still pending human approval, and rank missing positive no-scroll
and visual-style coverage. No additional training on the unchanged bank.
