# FDR-012 — approved training/comparison tranche complete for review

| Outcome | Result |
|---|---|
| Software verified | Pass: existing trainer/evaluator,33focused tests, exact baseline metric replay |
| Data eligible | Pass for325+9 bounded development and frozen evaluation roles; not production qualification |
| Integration qualified | Pass for same-process MPS training and829/829retained-crop candidate scores; no new producer runtime or CoreML export tested |
| Model gate passed | Fail for approved real-transfer criterion; production qualification not established |

## Acceptance evidence

| Assigned criterion | Evidence/result |
|---|---|
| Approved replacement, no CPU fallback/resume | approval.json,backend.json; PID54962MPS verified before invoking existing trainer |
| Exact325+9 protocol, fresh FDR007 initialization | trainer preflight.json; protocol6699a6e689e33ae916fab21a437b9de0c31a7dd62bce4c2f1881561e77e6adac |
| Bounded30epoch run | execution.json:exit0,396.55seconds total; experiment-result.json:90.70seconds training,30epochs |
| Retention floor and frozen selection | selection-verification.json:30epochs replayed,epoch29 minimum eligible BCE,18/18correct |
| Fair real/synthetic comparisons | comparison-freeze.json, six candidate files,comparison-summary.json; exact predictions/identities/metric replay |
| Complete accounting |517real+312synthetic scores,0failed/missing/invalid;64real nonprimary entries retained in per-benchmark metrics |
| Decision and next assignment | results.md,real-errors.json; real TP/FP worse, no export;44-pair intake plus representative selection proposal next |
| Verification and handoff |33focused tests pass; local state/log/queue reconciled; TTR consequence published/read back |

## Result

Selected best.pt SHA256 `b079f4c756af52889b055cda2a3a87d4310be9fe518703a1d28704b49dbd044c`
at `NativeUITrainer/focus_ring_runs/related-synth-development-mps/weights/best.pt`.
No alternative epoch selection after evaluating real inputs. Retention18/18 does
not prevent regression: real focused recall3/35→1/35 and false positives9→15
versus FDR010. Synthetic unique-correct18/50→20/50 is reported separately.
Results and exact changed sample IDs are in results.md and real-errors.json.

## Verification and command paths

Existing `scripts/train_focus_ring_detector.py --experiment-protocol
reports/work/RELATED-SYNTH-ADMIT-01/proposal/focus_dataset_manifest.json
--experiment-approval reports/work/FDR-012/approval.json --experiment-arm
warm-stretch --name related-synth-development-mps --execute --experiment-id FDR-012`.
Launched via same-process runpy after required MPS assertion, scoped approved host
execution and owned-child1,800second supervisor. started.json records executable
and exact invocation; execution.json records exit0/time. Resident focus-export-01,
PyTorch2.7.0. Cache/log/output configuration project-local.

Existing `human_focus_evaluation.infer/metrics`,
`focus_representative_validation.summarize`, retained `FDR-010/compare.combine`
and `focus_retention_experiment.selection_metrics` reused via inline orchestration.
No new evaluator, model architecture, taxonomy, cropper or Swift source changes.
Candidate inference CPU, shipped retained CoreML CPU; no parity/latency claim.

Tests: `PYTHONPATH=scripts .venv-review/bin/python -m unittest
scripts.test_focus_training_extension scripts.test_focus_retention_experiment
scripts.test_human_focus_evaluation scripts.test_focus_representative_validation`:
33passed in2.844seconds,exit0. No full Swift rerun for unchanged implementation.
All source protocols, original images, prior scores and interrupted FDR-011 weights
preserved. Base revision e3f46fe3c9eedb46b5fa37cd4c814e3b807208d0; pre-existing
dirty files preserved. No git writes.

## Boundaries and continuation

No ongoing worker process, capture, new transfer, training retry, threshold sweep,
challenge scoring, export or promotion. The assigned run and comparison are
complete even though the model failed. This is not a data-admission reversal.
No causal claim that related synthetic data is inherently harmful: a single run
cannot isolate appearance, context, optimization and selection effects.

Next proposed assignment: receive already-published44pairs, run existing intake
and source-bound crop QA, audit actual coverage, then specify representative
selection and exact next experiment for approval. Do not ask humans to redraw
native-labeled pairs. No additional training is authorized by this handoff.

TTR metadata consequence published/read back; peer acknowledgment pending.
See coordination.md for exact destinations, preserved unrelated-state digest and
the producer coverage question. All assigned acceptance evidence is present;
there is no remaining safe authorized execution in this tranche.
