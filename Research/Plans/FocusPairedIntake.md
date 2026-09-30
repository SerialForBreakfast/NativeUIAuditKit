# FOCUS-PAIRED-INTAKE-01 — approved paired experiment and named archive QA

Completed for review2026-09-29: [integrated handoff](../../reports/work/FOCUS-PAIRED-INTAKE-01/handoff.md).
FDR016 zero eligible checkpoints; native11296usable diagnostics/13duplicates/3holds.
This completion does not authorize another run or data admission.

User approved the [paired-loss proposal](../../reports/work/FOCUS-ARTWORK-AUDIT-01/next-experiment.md)
and named native12/native100 intake in the current chat. Owner: current NUIAK worker.
Implement the explicit paired-loss adapter in the existing trainer, verify it,
freeze/log one FDR016 run, execute once, compare cached metrics, and hand off.
Reuse FDR015 features with exact source/order/hash binding; no encoder inference.
Same363training+9retention pairs/453real selection crops and unchanged gates.
Pair-balanced sampling preserves25%appearance mass;32pairs/64crops per batch,
363pair draws/epoch (last partial batch retained),30epochs,AdamW0.0003,seed42,
fresh577parameter head, BCE plus softplus negative margin at coefficient1.0.

Separately receive the named322,891,996byte native100-r2 and38,274,170byte native12
archives into new local storage, verify hashes and bounded extraction, run existing
native intake/production crop QA, inspect contrast/geometry evidence and account for
all112exported pairs. No new data enters FDR016. No new capture/device operation,
calibration, export, promotion or automatic rerun. Existing protected membership
and historical geometry holds remain intact; new evidence gets its own disposition.

Use existing safe archive/import/crop/report components. Any necessary consumer
compatibility fix must preserve native semantics and reject unknown versions; do
not repair producer evidence. Tests cover paired loss/order/identity/roles/cache
integrity, existing paths and affected intake boundaries. Offline Swift build/test
at integrated handoff. Complete both lanes independently of model success. Publish
metadata-only exact transfer receipts and actionable findings to TTR; sender owns
cleanup. Four outcomes remain separate. Reports under reports/work/FDR-016/ and
reports/work/NATIVE112-INTAKE-01/.
