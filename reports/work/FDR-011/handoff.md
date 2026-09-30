# FDR-011 — interrupted execution, comparison preparation complete

| Outcome | Status | Evidence |
|---|---|---|
| Software verified | Pass for unchanged paths | 33 focused tests; baseline metric replay |
| Data eligible | Pass for bounded development | Approved325+9 assembly and actual trainer preflight; not production qualification |
| Integration qualified | Failed training launch context | CPU selected instead of intended baseline MPS; scoped host probe finds MPS |
| Model gate passed | Not assessed | Training interrupted; no selected checkpoint or candidate comparison |

## Execution and failure

User approved one exact bounded run and its frozen comparisons. Existing trainer
started at20:36:43Z,PID51386, same resident focus-export-01 interpreter/PyTorch2.7.0.
Data preflight passed. Restricted execution reported device=cpu, whereas FDR-010
used MPS. Read-only host-context probe confirmed mpsBuilt=true,mpsAvailable=true.
This launch-context mistake is ours, not a TTR/data blocker.

Stopped only the owned child at20:45:44Z,exit-15,541.19seconds including preflight.
Three epochs completed by the time termination was delivered. The initial
restricted stop returned EPERM; scoped stop succeeded and supervisor exited.
No trainer remains running. Partial best.pt/last.pt preserved and hash-indexed in
verification.json; neither is selected, evaluated, exported or promoted.

Configuration was325training pairs/650crops plus9retention pairs/18crops,
FDR007 initialization,fresh optimizer,30epochs,batch64,lr0.0003,seed42,
50/50 native/Fixture sampling,no augmentation,16%/256production crops,
threshold0.85,1,800second cap. Minimum retention BCE among18/18correct was the
unchanged selection rule; interrupted weights cannot substitute for completion.

## Completed independent work

- comparison-freeze.json binds all40 real-development frames/517scores across
  five original protocols, plus50related synthetic pairs/312scores separately.
- Existing shipped and FDR010 predictions were validated against exact membership,
  hashes, complete finite scores and the existing metric implementation. Baseline
  metric replay passes. Human approvals and native synthetic provenance were
  reconstructed through the existing admission/validation functions.
- Supplemental baseline report uses the representative summary wrapper; replay
  verified that wrapper rather than comparing it to an inner metrics object.
- All33tests pass: test_focus_training_extension,test_focus_retention_experiment,
  test_human_focus_evaluation,test_focus_representative_validation. See focused-tests.log.
- No new implementation code, model inference, crop regeneration, threshold changes,
  capture or protected-challenge scoring. Swift rebuild is not required for this
  unchanged-code execution/documentation tranche.
- Updated Tasks,CurrentState,ExperimentLog and BestPractices. Existing dirty work
  preserved; no git writes or external coordination mutations.

## Exact resume condition and recommendation

Approve one replacement bounded MPS run, same325+9 data/configuration and frozen
comparisons, fresh output directory and new logged execution identity. Verify
MPS availability in the exact approved host launch context before importing the
trainer into that process; fail closed rather than fall back. Do not resume the
partial optimizer/checkpoint or count this as a valid model-quality result.

Then compare only the selected replacement checkpoint using the existing CPU
candidate evaluator, retaining shipped-CoreML versus candidate-PyTorch backend
disclosure. No export/promotion is implied. No more capture/annotation is needed
to execute this already-prepared comparison.

The assigned training-and-comparison tranche is incomplete. Safe independent
preparation and verification are complete; replacement training needs new authority
because the approved scope explicitly excluded an automatic second run. TTR
coordination is not applicable: this local launch failure does not change its
capture or repair assignment. No shared-status update or peer acknowledgment claimed.
