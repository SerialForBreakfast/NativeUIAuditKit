# One-run training request — October 1, 2026 PDT

Protocol `2196c2c1285661373bfee5c27f1a549433a1aca3046424a4ff340747519d731c`:
`artifacts/training-protocol/protocol.json`. Data blockers: none. Actual trainer
preflight is required; no execution from preparation alone.

- Proposed run FDR-022, arm `native-body-full-fit`, output
  `NativeUITrainer/focus_ring_runs/fdr022-native-body` (fresh destination).
-1550training controls =986baseline +564admitted native;1354native/196human,
  native/human loss80/20. Exact315development+18retention records unchanged.
- Frozen ImageNet MobileNetV3-small576feature encoder; all features already cached.
  Fresh577parameter linear head, seed42, AdamWlr0.01,weightDecay0.01; full batch1550.
- At most1000updates/300training seconds, evaluation every25updates, unchanged
  five-consecutive-fit stop and minimum-balanced-real-BCE guarded selector.
 600second outer process deadline includes full input validation/startup.
- Production16%/256straight-RGB preprocessing, no augmentation or threshold sweep.
- Compare selected checkpoint at0.85against FDR021: artwork hits strictly above2/12;
  overall TP≥16/27, FP≤3/288; unique-correct frames≥12/14; zero wrong/multiple;
  retention18/18; buttons/tabs/rows/other lose no TP or gain FP relative to baseline.
  These are development comparison criteria, not production qualification.
- Stop and report failures/regressions. No automatic retry, later arm, export,
  deployment or promotion. Preserve all existing artifacts.

Exact one-run approval is requested through this chat; no approval is presumed.
