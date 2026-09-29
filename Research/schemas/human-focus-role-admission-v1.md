# Human focus role admission v1 — development only

Implemented by `scripts/human_focus_roles.py`; consumed by the existing evaluator
using `human-focus-evaluation-approval-v2` and `human-focus-development-evaluation-v2`.
No change to diagnostic revision-v2, detector taxonomy or native journey schemas.

Required fields:

- `version: human-focus-role-admission-v1`; existing diagnostic FLAGS and seal.
- `approved: true`, nonempty `reviewer` and `authorizationReference`,
  `role: development-regression`. These must reflect actual separate approval.
- `revision`, `crops`: project-local path/SHA256 references to immutable evidence.
- `completeness`: optional path/SHA256 reference to the matching human receipt;
  null means no frame can be declared complete.
- `populations`: `candidate`, `auxiliary`, `unresolved` lists, collectively covering
  every reviewed sample exactly once. Auxiliary samples must be unfocused.
- `frames`: every frame exactly once with `id`, `settlement` (settled/disputed/unknown),
  `coverage` (complete/incomplete/unknown), and nonempty `reason` if either is not
  settled/complete. Complete coverage requires human attestation and no unresolved
  sample in that frame; admission decisions can be stricter than the original receipt.
- `pairIDs`: optional, defaults empty. Only existing audited pair identities may be
  selected; both members must be candidates in settled frames. Cross-frame
  local ordinal IDs do not establish additional pairs.

Use separate population meanings for analysis; never rewrite source labels. Crop
candidate metrics exclude settlement-disputed frames explicitly. Frame outcomes
require complete candidate coverage and exactly one true focused candidate;
zero/multiple truth focus remains unavailable. At fixed0.85, predictions yield
unique_correct/wrong/no_focus/multiple_focus. Auxiliary scores never enter selection.
Unresolved samples and excluded frames remain visible in accounting. Missing or
invalid predictions fail comparison with existing failure receipts.

Approval-v2 retains all v1 execution approval fields and adds `admission` reference.
It still pins exact samples, audited selected pairs, coverage, two models, role
inventories, output and one launch. `freeze` validates, `run` executes only after
that separate approval, `render` consumes compatible retained results without
model/runtime loading. The global completeFrameCandidates flag stays false: only
explicit supported frame outcomes are qualified, never an entire corpus by default.

Current unapproved examples: reports/work/REVIEW-PARALLEL-01/batch01-admission-draft.json
and batch02-admission-draft.json. No approvals are inferred from these drafts.
