# ROBUSTNESS-63 — augmentation comparison and retained-source audit

## Outcome

Translation augmentation improves synthetic robustness but is not ready to replace
either a shipped model or the prior experimental checkpoint.

| Paired localization | DTM009 | DTM010 |
|---|---:|---:|
| Original training pairs |24/24|18/24|
| Reversed training pairs |24/24|17/24|
| Left / right shifts |12/24 /12/24|18/24 /18/24|
| Up / down shifts |12/24 /11/24|22/24 /24/24|
| Settings development |0/5|0/5|

Aggregate shifted pairs:47/96→82/96. Both models still falsely classify all3
unchanged Settings pairs as changed. Original DTM010cells47/48; all6failed pairs
have inaccurate guide after-frame geometry even when scored at the true cell.
No threshold tuning, checkpoint selection or second run.

## Execution and acceptance evidence

- Registered DTM010 before launch. Existing trainer CLI, arm
  `transition-direct-pixels`, protocol `ready/protocol.json`, approval
  `ready/approval.json`, run `robustness63-dtm010`, `--execute --experiment-id DTM010`.
  Exit0,PID21291,120epochs/360updates. Fresh state; same24/5membership.
- ModelSHA `b88b645761cc12042ab53e02db2f6928cee0a881c99d31f3fc96ee0298c28e92`.
  ProtocolSHA `04755955f7d95cb0c628b8dbdfafc2177f189157ef62ad601250c0472b871e9b`.
- Shared analytic transform preserves both endpoint boxes and semantic change.
  Source-resolution black-filled shifts, existing96×64encoder.120valid bank variants,
  zero rejected training variants,2880scheduled examples. Independent NumPy RNG
  preserves Torch initialization/shuffle behavior. ScheduleSHA
  `b3ed86a555adc0510da6045d5aaade4df07e4922bc9f5d165401c79325a4efda`.
- Sealed `evaluation.json`, `sensitivity.json`, `comparison.json`,
  `fit-diagnosis.json`, `cli-parity.json`.169diagnostic evaluations;5off-frame
  Settings shifts rejected. Baseline predictions match checkpoint evaluation.
  Actual image-only CLI parity passes all9retained checkpoints.
- Run22.533s:15.771sintake,6.622sfit/bank setup,0.006scheckpoint,0.133sscoring;
  initial CLI preflight additional. Run output3,591,266bytes. CPU warm median4.222ms,
  p954.310ms excluding PNG load. No capture or external waiting.

82focused Python tests pass (3.234s), including train-only bank, analytic geometry,
rejected variants, deterministic independent schedule, actual trainer control flow
with optimizer updates mocked, unchanged inference and incompatible comparison rejection.
Offline Swift build/test exit0:14XCTest+120Swift Testing. Logs:
`.build/robustness63-{tests-final,swift-build,swift-test,parity,dtm010}.log`.
Comparison initially used a legacy seal validator requiring unrelated flags; fixed
to verify this report's own exact seal/version/scope. Original failure log retained.

## Independent coverage deliverable

`coverage-final.json` revalidates all40native cases in the three-source retained
inventory, not an unbounded filesystem scan or unreceived peer artifacts:

-4valid boundary_unchanged and4valid content_only: observed equal offsets,
  verified cleanup, existing native labels. No condition rewriting or training admission.
-28valid scrolling cases;4historical scroll_moved cases retain their scene-focus
  validation failure. Settings lacks native offset binding and stays unknown.
-No interior no-scroll switch established. The8negatives are composite_card seed71/83,
  not substitutes for the proposed guide/catalog compatibility matrix.

Published the producer-relevant correction in existing SMB `packets.TRANSFER-62`
at20:31UTC; verified mount, unique-key YAML, readback and preservation of every
unrelated field. Existing request ID retained; peer acknowledgment absent. No local
training metrics were published. TTR is asked to preserve existing cases, not recapture.

Software:passed. Existing24/5data eligibility:unchanged;8new training admissions:not
granted. Offline model/CLI integration:passed; live producer integration:not assessed.
Model gate:failed/not qualified. Existing dirty Geometry58–Transfer62 work preserved.
No Git writes, device operations, downloads, export or production changes.

## Next substantial tranche

EXPOSURE-64: one fixed600epoch augmented run matches approximately120exposures per
variant (DTM010averaged24), reporting its5×update cost. In parallel, score the two
frozen models on the8retained native negatives as calibration-only evidence. This
tests optimization and missing negative coverage separately; it is not another
unbounded training loop. Capture, new training membership and promotion keep their gates.
