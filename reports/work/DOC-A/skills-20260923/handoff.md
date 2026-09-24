# Agent workflow and SMB guidance maintenance

2026-09-23; DOC-A, NUIAK architect. Documentation/skill maintenance only. Preserved
all pre-existing r6 code/data/reports and the preceding queue-audit changes.

## Changes

- AGENTS and the worker skill route every contributor to compact, task-specific
  operational lessons; no dependency on this chat or automatic skill installation.
- Replaced obsolete model-skill scaleFill/eval_map defaults with model-specific
  YOLO letterboxing and historical Create ML separation. Added approved-interpreter,
  dataless-dependency diagnosis, isolation, split/holdout, crop, evaluation and export
  procedures. No new model architecture, gate or training authorization.
- Updated protected TTR/fixture entrypoints through approved scoped execution;
  retained producer revision7 references with an explicitly local current-contract
  overlay. Updated the skill manifest's changed file hash; two reference hashes unchanged.
- Operational reference covers writer/permission layers, matched running artifacts,
  exact simulator/container identity, native-test execution proof, changed-boundary
  testing, preservation of completed jobs, independent acquisition lanes, source-object
  inspection, requested-versus-observed state, lineage, class support, frame decisions,
  temporal ambiguity, CoreML parity/size and substantial tranche completion.
- Reconciled local SMB copies with the observed approved transfer protocol. Workers
  publish their own packet without a coordinator, only when relevant to TTR–NUIAK.
  Mount path alone is not endpoint verification. The existing mounting helper's
  limited check is explicitly documented; no helper or system code changed.
- Separated publication/readback, acknowledgment, verified transfer, semantic intake
  and sender cleanup. Added bounded conflict/retry handling, size approval, safe archive
  admission and preserved ownership. No raw evidence in YAML or remote execution.
- Added BP-98/99, disambiguated six duplicate BP identifiers with a historical mapping,
  and corrected the active crop-contract reference. Historical incident evidence preserved.

## Verification and behavioral review

Skill-creator quick_validate passes for worker-execution, model workflow, tvtestrig
and fixture-training. Link/anchor and manifest/hash verification run locally; YAML
examples/frontmatter and BP uniqueness checked. Initial broad BP uniqueness check
found five more historical duplicate IDs after fixing95; those were corrected with
title-based migration notes rather than hiding the failure. No Swift rebuild or
simulator run: these are documentation-only changes.

Final checks:201 local links/anchors pass;104 unique BP identifiers; all three TTR
manifest hashes match; two YAML examples and shared-status frontmatter parse with
duplicate-key rejection. Four skill validators pass; `git diff --check` exits0.

Read-only scenario review (not live agent/runtime qualification):

| Situation | Required workflow now discoverable |
|---|---|
| Local iOS work, share absent | No SMB attempt; continue assigned local work |
| A local directory has the share's name | Reject until actual expected smbfs endpoint is verified |
| Concurrent worker changes YAML | Preserve unrelated/unknown fields; one reread/merge, then local draft |
| Peer announces an absent archive | No success receipt; report unpublished source; no alternate-host execution |
| Approved108MB archive delivered | Exact size/hash receipt, separate safe extraction/intake; sender owns cleanup |
| Capture completes, signed CLI export fails | Preserve job; supported matched export only; no recapture |
| Readiness passes but focus observations fail | Label-binding blocker, not permission/security repair |
| CoreML cold import/errno60 | Diagnose stage/residency; no blind reinstall or weight changes |
| New seed/theme produces old pixels | Preserve lineage; no independent-evaluation claim |
| Prose change or helper checkpoint | Prose checks only; finish the full assigned tranche before final handoff |

Software: not applicable (documentation validators pass). Data eligibility unchanged;
live integration/model gates not assessed. No new authority, capture, training, Git
writes, environment setup, security change or dataset cleanup.

## Remaining approval

Resolved by explicit user approval in the next turn. Both SMB guides now match the
repository copies, with standing contributor guide-maintenance authority. Publication
and DOC-A status readback passed; other packet fields unchanged. See coordination.md
for hashes. Peer acknowledgment remains separate; earlier denial below is historical.

Shared-guide publication was denied as an unapproved maintainer-owned cross-machine
edit. The exact patch and [checkpoint](coordination.md) are retained locally; the
repo/skills are updated. Ask explicit approval to update those two shared documents,
then reread/merge and verify before publishing. No peer receipt is claimed.
