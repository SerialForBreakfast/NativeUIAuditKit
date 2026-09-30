# Approved 32-pair admission

| Outcome | Result | Evidence |
|---|---|---|
| Software verified | Pass | 20 focused tests, offline build and 123 Swift tests |
| Data eligible | Pass for development training candidates only | Native/crop validation and exact 32-pair approval |
| Integration qualified | Pass for data assembly and trainer refusal | Deterministic replay, actual preflight in verification.json |
| Model gate passed | Not assessed | No model execution; existing gates unchanged |

The user's approval applies to the frozen 32 native-control pairs in proposal
`12a46c9861da72d58d5c26b4c6ceac91816ca249f776f3cf9d4e697123e9b028`.
The remaining 64 artwork pairs are held, not admitted. Originals and diagnostic
manifests retain their original status; the separate approval records the change.

| Training appearance | Before | Added pairs | Now |
|---|---:|---:|---:|
| Buttons | 119 | 14 | 133 |
| Tabs | 17 | 9 | 26 |
| Artwork | 150 | 0 | 150 |
| Rows | 77 | 9 | 86 |
| Total | 363 | 32 | 395 |

`approval.json` pins exact source/pair IDs, manifests and crops. `assembly.json`
contains 790 training crops, 18 retention crops and 453 representative-selection
crops; all 1,197 original rows and the 64 selection exclusions are preserved.
Assembly seal: `f99911edfdb3b93656fa13a10ff545c0367da42e8d1201bffd3147b59efb6945`.

Native observation brackets and original frames validated using existing manifest
validation, with production 16%-expanded 256px crop pixel parity. Existing pair,
label, lineage and protected/reserved-overlap guards admitted exactly 32 pairs.
Protected challenge evidence was compared as metadata, never rendered or scored.
Two previously reported equal individual crops remain accounted for; no whole
pair was duplicated and no partner was discarded. Related Fixture sources remain
development-connected, not independent evaluation evidence.

## Outcomes and verification

- Software: 20 focused tests pass, covering exact/changed approval, scope expansion,
  incomplete pairs, label conflicts, leakage, protected lineage and sampler behavior.
  Offline Swift build and 123 tests pass. Logs are retained here.
- Data: 395 candidate pairs admitted; 64 artwork pairs held. Existing equal-appearance
  sampling policy recalculated for new membership, not replaced. Selection policy,
  threshold and original configuration reference remain unchanged.
- Integration: data-only format explicitly rejected by normal trainer preflight.
  `verify.py` replays actual assembly and saves the trainer refusal in `verification.json`.
  It does not create a run or import a model. Historical feature caches are not
  presented as compatible with the larger assembly.
- Model gate: unassessed, all 10 existing qualification blockers preserved. No
  inference, training, export, promotion or new run allocation.

Deterministic replay completed successfully; `verification.json` records 1,197
preserved rows, unchanged source manifest hashes and the real trainer refusal.
Unit tests generate isolated fixtures rather than depending on retained corpora.
Swift's initial nested-sandbox build was denied; the scoped host retry passed with
repository-local caches/output. No security setting was weakened.

Base revision: `e3f46fe`; existing dirty changes were preserved. Changed implementation is this packet's
`assemble.py`/`verify.py`, the explicit data-only refusal in
`scripts/focus_training_preflight.py`, and `scripts/test_focus_control32_admission.py`.
No new reusable operational lesson was established beyond existing admission rules.
All assigned criteria are evidenced; no process remains running for this packet.
Do not overwrite approval/assembly or original source artifacts. Completion is for
review, not a production qualification claim.

Reproduce from repository root with `PYTHONPATH=scripts PYTHONDONTWRITEBYTECODE=1`
and `.venv-yolo/bin/python reports/work/FOCUS-CONTROL32-ADMIT-01/verify.py`;
set TMPDIR to the repository's existing `.build/debug-output/focus-launch/tmp`.
Outputs are immutable-or-identical; modified proposals or approvals are rejected.

## Next action

Receive the new TTR build's approved measured geometry trial and resolve artwork
crop/contrast evidence. Then propose **one changed-data experiment**, with exact
assembly, feature preparation, initialization and success criteria for separate
approval. These control additions do not by themselves address the observed
artwork failure, so another unchanged run is not justified. No additional human
annotation is needed to finish this admission. TTR's next action has not changed;
coordination is not applicable.
