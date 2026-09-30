# Exact next development run proposal — not launched

Dataset:325training pairs (313preserved+12new),9unchanged retention pairs;
650training crops/18retention crops. Assembly and every prior row verified.
Protocol SHA256:
`6699a6e689e33ae916fab21a437b9de0c31a7dd62bce4c2f1881561e77e6adac`.
`proposal/focus_dataset_manifest.json` freezes configuration/runtime and extension.

- Initialize FDR007 best.pt, SHA256
  `a5c7f2f44368feb4ec81477aab33f1e0f5e2f380c43fb5d9ebca3bd26c3499f0`.
- Fresh optimizer;30epochs maximum, batch64,lr0.0003,seed42,1,800second cap.
-50/50 logical native/Fixture training sampling; no augmentation or crop changes.
- Keep threshold0.85; select minimum retention BCE among epochs preserving18/18
  correct retention labels, earliest tie. No eligible epoch means no checkpoint.
- Proposed unique output name: `related-synth-development-candidate`.
  No run number or execution approval issued. Resident focus-export-01 runtime
  is pinned in the protocol. Trainer preflight must be checked before execution.

## Evaluate the change, not a new benchmark

Compare the selected candidate with shipped and FDR010 at0.85 on the five frozen
real-development protocols in evaluation-lanes.json:24reviewed real frames,8prior
Home/Photos/Settings frames and8supplemental frames. Report actual supported
sample/frame membership, per-control recall and false positives, and unique/wrong/
no/multiple selection only where candidate completeness is attested. Do not invent
missing full-frame accuracy. Reuse compatible baseline scores; verify identities.

Report SYNTH05's50pairs separately as related-synthetic performance. Do not merge
this score into a real-transfer or independent-qualification average. Do not choose
epochs/thresholds after seeing real results. Existing untouched qualification stays
reserved. Training loss/retention improvement alone is not a successful outcome.

Recommend continuing only if real-development recall improves versus FDR010 without
increased false positives, no supported stratum regresses unnoticed, and retention
is preserved. Report comparison against shipped separately; beating FDR010 alone
is not sufficient for release. This is a proposed experimental success criterion,
not a replacement for production gates. Any new export requires its own scope and
the previously documented transfer/parity conditions; no export is authorized here.

This isolates the12-pair data addition under the previous training configuration.
It is a small development experiment, not proof that325pairs constitute a production
corpus. TTR collection and runtime repairs are not prerequisites for this run.
