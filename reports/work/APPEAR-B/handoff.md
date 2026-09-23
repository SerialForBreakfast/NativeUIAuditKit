# APPEAR-B — Offline audit and experiment proposal

| Outcome | Result |
|---|---|
| Software verified | New fail-closed audit/planning CLI and regression tests pass; required offline package checks pass. |
| Data eligible | Existing source admission unchanged;202 proposed training pairs,9 native retention-validation,6 protected known challenge. Independent appearance evidence absent. |
| Integration qualified | Actual local audit CLI ran against retained bytes; no new producer, simulator or trainer integration. |
| Model gates | Not assessed; existing score reports verified without new inference. |

## Findings

`proposal.json` freezes422 sample rows (404 candidate training +18 native validation),
source hashes, full connected-component edge reasons, coverage and exact sampling
probabilities. No complete-pair duplicates or crop-label contradictions. Six new
individual crops overlap prior training; all162 Fixture pairs connect across
seeds7/19/101/211. Five components before adding the protected Remotes journey;
no cross-partition conflict. This rules out treating the new seeds as a holdout.

`protected-evidence.json` verifies Remotes6 pairs, source inventory/review hashes
and full frame/crop pixels; joining them produces no partition conflict. Home72
and Photos4 base reviewer boxes remain known visual-development diagnostics;
their eight full frames have no exact pixel overlap with audited training/retention
evidence. Unknown journey lineage and prior inspection prevent independence claims.

Proposed native/Fixture sampling mass is50/50, versus11.11/88.89 previously.
Per-source, per-stratum and per-label mass is explicit; validation never contributes.
This is a hypothesis, not optimality evidence. Full [experiment proposal](experiment-proposal.md)
specifies one future candidate, independent evaluation reservation and launch gates.

## Verification and reproducibility

Actual command from repository root with approved focus-export Python:

`scripts/focus_appearance_proposal.py --previous reports/work/FOCUS-DEV-01/dataset/focus_dataset_manifest.json --appearance dataset/focus_ring/appearance-a2-pilot-intake2/focus_dataset_manifest.json --comparison-protocol reports/work/APPEAR-A2/protocol.json --output reports/work/APPEAR-B/proposal.json`

First attempt rejected a relative-path conversion before publishing any output;
normalized inputs and preserved `audit.log`. Corrected real run:exit0,59.741s,
`audit2.log`. Source bytes are decoded/hashed, prior seals/references checked, direct
receipt and membership validated. Prior pixel-qualified crop geometry is reused
under unchanged manifest/runtime hashes; no redundant recropping or inference.
`protected_audit.py`:exit0, raw/crop evidence verified. No timing recorded for it.
Read-only rescoring reproduced three pilot reports and four Home/Photos checkpoint
reports from fixed samples/scores using existing scoring functions; no model call.

Proposal content hash:
`cd3c8e0ff19961c53cf81abe81e3f3a9f331755d74bd3a2bb63802e67fcd0d0f`.
Membership and weights are deterministic; elapsed time is included in this immutable
audit instance, so a repeat run's whole-report hash need not match.

Tests:123 FocusRing tests pass in4.296s, including transitive lineage/pixels,
contradictions, seed grouping, protected-role conflicts, source-mass invariance,
missing label support, real CLI corruption rejection and output-collision preservation.
Swift build1.90s/exit0;14 XCTest +93 Swift Testing pass. Logs retained here.
No new images displayed, capture, training, weights, public APIs or producer changes.
All outputs local; unrelated dirty work preserved. SMB not applicable: existing
producer request unchanged; this is local data/experiment planning.

## Scope completion and remaining blockers

Assigned offline audit/proposal tranche is complete for review. **The broader
APPEAR-B qualification packet is not complete**: untouched appearance validation
and challenge members do not exist; proposal-to-trainer adapter and exact training
approval remain absent. No fake members or automatic run substituted for them.

Next unblocked implementation is the versioned development-adapter integration
described in the proposal, preserving launch blockers until real evaluation inputs
and approval exist. Independent rendering acquisition remains separately scoped.
Worker-execution guided complete evidence/handoff; model-workflow preserved
preprocessing, source roles and launch boundaries. No processes remain running.
