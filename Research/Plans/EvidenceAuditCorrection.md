# Evidence audit correction — 2026-09-21

Assigned scope: review the supplied audit transcript, preserve its three reports,
and repair evidenced false-readiness paths. No training, new model inference,
device operation, labeling, producer changes or wholesale PER packet completion.
Owner: architect. Tasks.md remains the queue.

1. Add reproducible local audit of every declared legacy crop and supplied capture:
   bounded PNG decode, dimensions, hashes, missing members, duplicate bytes and
   normalized split/seed overlap. Integrity is not label review or training eligibility.
2. Make the historical evaluator reject missing members and invalid probabilities,
   refuse empty hard-negative passes, require explicit isolated output/backend,
   and distinguish explicitly requested legacy diagnostics from qualified evaluation.
   Do not execute it on real weights in this assignment.
3. Prevent metadata-only physical readiness from claiming data eligibility. Preserve
   its inspection utility; full physical pipeline integration remains PER-04.
4. Require image decode/dimension verification for real perception CLI evidence;
   separate unknown semantic abstention from destructive-as-informational errors.
5. Test through actual entrypoints, run offline repository checks, and issue a
   corrected handoff identifying which pasted claims were not supported.

Acceptance: deterministic audit on supplied local evidence without input mutation;
negative tests for corrupt/missing/changed bytes, split leakage, zero support,
unknown semantics and output collisions; reports never promote integrity to truth.
Next: independent annotation/provenance recovery where possible, or qualified capture.
Existing crop-only heuristic labels cannot be requalified by changing manifest fields.

## Operator interfaces

```sh
.venv-yolo/bin/python scripts/audit_training_evidence.py \
  --focus dataset/focus_ring --captures dataset/tvos_captures \
  --output reports/work/EVIDENCE-AUDIT/new-audit.json
```

Audit outputs account for all declared crops and flat-directory sidecars/orphans,
with per-member failures rather than silently shrinking membership. Source captures
and predictions remain unreviewed; audit never grants eligibility. It reads no
unlisted capture subtrees and does not modify datasets.

Historical evaluator now requires exactly one `--weights` or `--mlpackage` and a
new project-local `--output-dir`; no fallback backend or overwrite. Legacy input
additionally requires `--diagnostic-only`, still rejects missing/corrupt/leaking
membership, and emits no passing model gate. Qualified numeric evaluation requires
v1.3 runtime crops, full byte/label contract, quota checks and corpus approval.
Execution remains separately assigned; this amendment did not run real inference.
Hard-negative FPR is null for zero support, requires ≥100 and all four strata to
pass. Deployment/export parity and promotion are separate even after numeric gates.

`physical_focus_readiness.py` remains metadata inspection, never data eligibility.
PER-04's full ingest/extraction/evaluation integration is still an explicit remaining
task. The remaining PER-02 baseline adapters/slices/provenance work is not closed by
these targeted semantic/integrity corrections.
