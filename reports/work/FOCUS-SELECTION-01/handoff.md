# Representative selection and expanded candidate preflight

Owner: current NUIAK model worker, 2026-09-29.

## Implemented

New versioned representative experiment adapter is integrated through the real
trainer's protocol loader, validation loop, checkpoint selection and ordinary
dataset rejection. Legacy retention/appearance protocols remain unchanged.
Selection metrics reuse existing crop/frame metrics, with frozen 0.85 thresholds.
Eligibility requires retention and real-regression guards before weighted BCE
can select a checkpoint; earliest ties and no-eligible behavior are preserved.

`qualified/protocol.json` is the final immutable preparation artifact. The earlier
`protocol.json` and `final/protocol.json` are intermediate development snapshots,
not launchable authority.
Final protocol SHA256:
`1c39256bf41e133d1e9532d35f4b2d6d6f7e24240729eb0375fc04e866326ae7`.

363 training pairs (726 crops), nine unchanged retention pairs (18 crops),
453 real selection crops (35 positive / 418 negative). All 668 prior assembly
rows are exactly preserved. 38 new pairs admitted by exact reviewed membership;
three geometry failures and three duplicates remain excluded. No original source,
QA manifest, label, crop or previous assembly was rewritten. Existing selection
reference is retained as `priorSelection`. Native/Fixture sampling mass is 50/50.

All 517 real labels remain accounted: 453 selection and 64 excluded with reasons
and source references. Forty frames are retained in policy; only 13 support
complete-frame decisions. These are development selection data, never training
or independent qualification. Related synthetic diagnostics and protected challenge
membership are not scored or opened for analysis in this tranche.

## Evidence

`inputs.json` pins prior assembly, final pair review, FDR012 comparison freeze and
reserved-pixel metadata. Preparation rechecks original native manifests, geometry,
crop/runtime contracts, file/pixel hashes, conflicting labels, exact duplicates,
source relationships, split isolation and frozen real membership. Existing crop
parity validation is reused; no new model inference or capture occurs.

`qualified-audit.json`: retained FDR010 scores reproduce 2 unique-correct / 11 no-focus;
the new improvement guard rejects unchanged performance. FDR012's saved scores
also fail artwork, rows and complete-frame guards. The audit supplies synthetic
perfect retention scores only to isolate these real guards: it is NOT a new
retention measurement or retrospective selection of an unscored FDR012 epoch.
Missing, duplicate and invalid retained predictions are rejected. Selection rows
are absent from training sampling. Objective mass is 25% each for buttons, tabs,
artwork and rows; other controls retain guards but have zero objective weight.

77 focused tests passed, including legacy selectors and new actual trainer
preflight/epoch-dispatch tests, hash/seal/runtime changes, stale approval,
ordinary-admission rejection, review membership, unsupported strata, duplicates,
missing buckets/scores, invalid scores, ties and incomplete-frame guards.
Offline Swift build passed without warnings; 14 XCTest + 109 Swift Testing passed.
Logs: `focused-tests-final.log`, `swift-build-final.log`, `swift-test-final.log`.

Reproduce preparation with resident focus-export-01 Python:
`scripts/focus_representative_experiment.py --inputs reports/work/FOCUS-SELECTION-01/inputs.json --output <fresh-project-local-file>`.
Reproduce saved-score audit with `.venv-review/bin/python scripts/focus_representative_audit.py --protocol reports/work/FOCUS-SELECTION-01/qualified/protocol.json --output <fresh-project-local-file>`.
Set `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=scripts` and project-local TMPDIR.
Generated evidence is gitignored/local, not a claim of an independent backup;
retain source artifacts in place. No cleanup or Git writes were performed.

## Next decision

Actual trainer command: resident focus-export-01 Python,
`scripts/train_focus_ring_detector.py --experiment-protocol reports/work/FOCUS-SELECTION-01/qualified/protocol.json --experiment-arm warm-stretch --name representative-development-candidate --preflight`.
Expected exit2; `qualified-preflight.json` has configurationValid=true and exactly
one blocker, missing_experiment_approval. Stderr is empty, no run directory exists.

Software: verified (77 focused tests and required offline package checks).
Data: eligible for this bounded development proposal, not broad production.
Integration: actual assembly, retained-score audit and trainer preflight passed;
launch remains unauthorized. Model gate: not assessed, all qualification blockers
preserved, shipped weights unchanged. Coordination: not applicable; no changed
TTR next action. No subprocess remains from this tranche.

Review [run-proposal.md](run-proposal.md) and approve that exact bounded run and
subsequent development comparison. No additional annotation or TTR repair is
required for that proposal. Production qualification and export remain separate.
