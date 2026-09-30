# One concrete decision remains before training

The40 newly reviewed pairs are admitted as **training candidates**, not merely
test-only screenshots. The immutable extension contains313 training pairs and the
unchanged9 retention pairs. No additional human annotation is needed for these
native Fixture examples. Full protocol hash:
`cabd9dc9bac2a4a5192f7e004cd596c9878aa06bab46151d546b2f0fc97c032f`.

The original selection policy needs independent appearance validation and final
challenge support across five strata. Adding related synthetic controls does not
provide that independence. In particular, button/row/tab analogs are not genuine
Photos, and flat selected tabs are not selected-parent/active-child navigation.
The old one-run FDR-009 approval is already consumed; it is not reused.

## Recommended bounded development experiment — awaiting maintainer decision

Use the existing separately versioned retention-selected development policy with
the new corpus; the full protocol remains unchanged and blocked for qualification.
Prepared proposal hash:
`8dd1a45090ed372157dbcd453cb3d77f770db4fb54cc0118a34141fdc2e2399a`.

- FDR-007 warm weights; fresh AdamW;50/50 native–Fixture source sampling.
- 313 training pairs,9 retained validation pairs; no real regression examples in training.
- At most30 epochs/1,800seconds,batch64,learning rate0.0003,seed42,no augmentation.
- Production16%-expanded256×256 stretch, threshold0.85 unchanged.
- Select the lowest-retention-BCE epoch only among epochs preserving18/18
  retention classifications; earliest tie. No eligible epoch means no selected model.
- One run only, then compare fixed inputs with shipped and FDR-009 on the existing
  24-frame real-world development benchmark. Report per-control misses, false
  positives and complete-frame unique/wrong/no/multiple selection—not training fit.
- An improving eligible result may support the originally requested opt-in TTR
  test-artifact export/parity work. No production promotion, gate waiver, model
  replacement, protected challenge scoring or automatic retraining.

No approval file, run ID or training output has been allocated. An affirmative
decision must be bound to the exact proposal/runtime and new run before execution.
If full independent qualification is preferred instead, next acquire/verify the
missing source-separated strata; do not train another nominally qualified run on
this related corpus. The new source/admission artifacts remain usable either way.
