# FOCUS-OFFLINE-DIAG-01 — completed for review

| Outcome | State | Evidence / remaining boundary |
|---|---|---|
| Software verified |Pass|Actual CLI,68 Python tests,offline Swift build/123 tests; source preservation and deterministic output|
| Data eligible |Blocked for training/independent qualification|2,107 image files verified;3,744 cached predictions and230 pairs accounted; independence/Photos coverage unresolved|
| Integration qualified |Offline reporting passes; live TTR blocked|Actual retained artifacts consumed; producer wire schema,consumer adapter and physical qualification separate|
| Model gate passed |Not assessed / unchanged|No new validation inference,training,export,promotion,threshold sweep or challenge analysis|

**Decision: request targeted additional data, not another unchanged training run.**
Both candidates uniquely select1/48 frames and rank true focus strictly first on
only1/48. FDR-008's false-positive reduction masks24 no-focus frames; all44 non-button
targets missed. Candidate geometry/context differs, but this is not causal proof.

## Review artifacts

- [Diagnosis, exact counts and ranked hypotheses](diagnosis.md).
- [230-pair audit, coverage matrix and next assignment](next-assignment.md).
- [95 numbered sheets](analysis-v2/evidence.md), including all unique-correct cases.
- [Frozen index](input-index-v2.json), [diagnostic output](analysis-v2/diagnosis.json),
  [image accounting](analysis-v2/accounting.json), [pair audit](analysis-v2/candidate-coverage.json).
- [EXT-CAP-01 consumer checklist](ext-cap-consumer-checklist.md).
- [Reproduction](reproduce.md), [acceptance verification](verification.md),
  [shared publication/readback](coordination.md).

Implementation: scripts/focus_offline_diagnosis.py and isolated test script.
Research decision preceded code in Research/Plans/OfflineFocusDiagnosis.md.
Existing evaluator/importer/library implementations and protocols unchanged.
Generated JSON/images/logs gitignored and retained locally; concise reports/source/
tests are reviewable changes. No sole-copy artifacts deleted; prior dirty edits preserved.

## Next actions and dependency boundaries

1. Obtain hash-bound source ancestry for missing producer revision/current roles;
   review locally without TTR runtime. Preserve221+9 proposal and all selection gates.
2. Separately authorize source-separated focus-cue/context positives, salient hard
   negatives and complete competitors. Do not train on exposed validation or mine
   protected challenge. No run allocated or launched.
3. TTR reconcile outdated two-frame grant with newer duration-only approval and
   provide exact schema/receipt example. Published/read back under existing request;
   new follow-up acknowledgment pending. Adapter implementation separate assignment.

Two operator-confirmed Photos frames remain **pending original consumer receipt**;
zero admitted pairs, no recapture/transfer request. Native-label availability does
not block capture transport; improved weights do not block TTR. Training waits for
qualified evaluation and separate approval. Offline tranche complete despite these
explicit future dependencies.
