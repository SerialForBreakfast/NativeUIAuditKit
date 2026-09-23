# One candidate — preparation, not execution approval

Use the existing `focus-appearance-experiment-v1` adapter, production cropper and
trainer. No new architecture, trainer, threshold sweep or preprocessing experiment.
The new candidate-dataset assembly binds the validated retention reference; it is
**incomplete until independent evaluation is added in another immutable assembly**.

## Fixed proposed configuration

- Warm initialization: existing proposal's exact FDR-007 best.pt hash, fresh optimizer.
- Arm: warm-stretch; MobileNetV4 conv-small, vendored backbone.
- 30 epochs, batch64, lr0.0003, seed42, maxSeconds1800, augmentation none.
- Existing production 16% expanded, 256×256 crops. Threshold0.85 is fixed for reports.
- Existing221 training-candidate pairs, preserving origins and 50/50 native–Fixture
  sampling mass; no held-out data enters training weights or loaders.
- Native retention:9 pairs/18 exact samples, reference FDR-007 predictions reused
  from FDR-008's logged initial evaluation; accuracy floor1.0 on this known slice.
- Checkpoint selection: minimum equal-source validation BCE among eligible epochs,
  earliest tie. No epoch reaching the retention floor means no selected checkpoint.
- Independent appearance validation and final challenge: missing; no synthetic
  stand-in, development relabeling or unreviewed new-seed exception.
- No experiment ID, approval file or run directory allocated. No training launched.

## Finish and freeze

1. Bind source reservations described in reservation-plan.md before acquisition.
2. Admit complete labeled pairs via existing ingest/extraction, preserving raw bytes.
3. Add hash-bound reviews and v2 membership reservations to a new candidate-input
   revision. Keep this incomplete assembly and prior evidence immutable.
4. Run the existing assembly and actual trainer preflight once on the final data.
   It must reject missing/reused evaluation, changed hashes, leakage and stale approval.
5. Review resolved sampling, exact checkpoint/data hashes, selection and runtime.
   Obtain one explicit approval bound to the final protocol/run/arm, then allocate
   the experiment ID and log it before launch. Approval of this preparation is not
   approval to execute the candidate.

## Post-run comparison contract

Score shipped, FDR-007, FDR-008 and the one selected candidate on identical frozen
membership. Report per-stratum/control/theme positive recall, false-positive rate,
wrong/no/multiple/unique-correct focus decisions and backend-specific latency.
Keep native retention, known development diagnostics and untouched final challenge
separate. Run final challenge after candidate selection, not during training.
Do not treat low-support counts or a pass on this experiment as the six production
FocusRing quality gates. PyTorch/CoreML export parity and promotion stay separately
authorized. Failed results produce a diagnosis, not automatic retraining.

Preflight command template after the final assembly exists (not executed here):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/train_focus_ring_detector.py \
  --experiment-protocol FINAL_PROTOCOL_PATH \
  --experiment-arm warm-stretch --name REVIEWED_NEW_RUN_NAME --preflight
```

`--preflight` has been inspected: it reports blockers and returns before model
imports or training. With approval absent it must remain launch-ineligible. The
current assembly already records all ten missing role/stratum requirements; another
full reconstruction solely to reproduce them adds no new acceptance evidence.
