# CAMPAIGN-71 — offline campaign batching and reusable inputs

Delivered through existing consumer/trainer boundaries; no capture/training/data-role
change/export/promotion. Earlier dirty work and all historical protocols preserved.

- Append-only sealed event chain, expected-head conflict checks and exclusive writes.
  Planned/running/completed/accepted/rejected/interrupted states. Unknown running work
  requires reconciliation; fresh destinations prevent overwrite/reused attempts.
- Exact case/recipe/visual-axis bindings, runtime receipt matching and cleanup checks.
  Receipts are local evidence, not authenticated identity or execution authority.
- Existing strict stationary consumer handles each new completed case. Repeated
  accepted intake rechecks source hashes without re-decoding. Validator dependency
  changes invalidate reuse. Final freeze checks all membership and decoded duplicates;
  produces only a development inspection corpus, never training admission.
- Prepared-input v3 opt-in separates input-dependent functions/dependencies from
  model code. Full training protocol pins remain unchanged; v1/v2 preserve old strict
  behavior. Source/labels/roles/transform changes still invalidate inputs.

Actual CLI: prepare_transition_inputs.py --corpus
reports/work/GENERALIZATION-65/admission/corpus.json --admission
reports/work/GENERALIZATION-65/admission/admission.json --output
.build/campaign71-scoped-bank --scoped-input-pins, exit0.32pairs/160views,
exact legacy x/y tensor parity. Existing training_bank used by two configurations
loads in0.171/0.169s; reuse.json pins manifest and configuration hashes. No model run.

Verification: generated native-evidence fixtures exercise actual intake, two batches,
missing-only resume, accepted evidence preservation, complete freeze and real status
CLI. Negative tests cover changed bytes/validators/transforms, partial completion,
wrong target/theme/case, uncertain cleanup, stale writer, collisions and source roles.
Focused tests and offline Swift build/test logs: .build/campaign71-*.
Swift14XCTest+120Swift Testing pass.69focused Python tests pass; tests-complete log.
git diff --check passes. Initial test fixture/diagnostic flag failures repaired;
failure logs retained. No SMB coordination required for local software work.

Known boundary: journal records externally executed operations; it does not control
a simulator or prove producer support for session reuse. Partial event/intake writes
fail closed and require inspected reconciliation, not automatic restart. Full-corpus
freeze still decodes images; only repeated intermediate work is cached.

Software verified offline; existing admitted data unchanged; offline integration
verified, live integration not assessed; model gates unchanged/not passed.

Next substantial tranche: source-pin producer bindings for the24-case/6-batch native
stationary campaign, reconcile its unsupported theme/control cells, and execute one
authorized healthy runtime session only when readiness and scope are confirmed.
In parallel, use retained data for transfer-error analysis rather than another
unchanged training run. Reserve genuinely independent evaluation groups before scale.
