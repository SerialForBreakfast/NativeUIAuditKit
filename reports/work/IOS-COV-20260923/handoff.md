# IOS-COV / DATA-RET integrated offline tranche

2026-09-23. NUIAK architect; base b3f0546. Prior appearance code/reports preserved.
No Simulator input/install, capture, training, model export or git writes performed.

| Outcome | Scope |
|---|---|
| Software verified | Retention inventory/verify/restore actual CLI and29 focused tests pass; offline Swift build and107 tests pass. |
| Data eligible |14,340 existing pairs individually valid; incomplete final membership, split decision and coverage gaps remain. |
| Integration qualified | Full local32,832-file recovery drill passes; not TTR or external-backup qualification. |
| Model gate passed | Not assessed; no new inference/training. |

## Delivered

1. **Fresh authoritative state:** no live generator process; old r5 session is not
   still collecting. Inspected preserved r5 failure, r6 prefix and current fixes.
   Full corpus validator exits1 only for two incomplete split totals and Finder
   `.DS_Store`; all14,340 image/annotation records pass, no decoded duplicates or
   cross-split pixel groups. Full evidence in prefix-audit.json/log.
2. **IOS-COV decision:** source-defined remaining2,600 images preserve16,940 total
   but violate frozen train/test totals. Asked maintainer whether to correct counts
   preserving family assignment or review a revised capture allocation. No default
   decision or relabeling made. coverage.json binds41-class counts to the audit/schema;
   train39/41,val12/41,test12/41. Missing support is broader than webContent.
3. **Recovery implementation:** scripts/corpus_retention.py inventories/seals all
   member paths, sizes and hashes; strict read-only verify; exclusive project-local
   restore. Rejects bad paths, symlinks, corrupt/partial copies and collisions.
   No external-copy/delete/overwrite mode. Local audit/restore retains annotations,
   manifests and rejected-trial evidence, not PNGs alone.
4. **Real recovery exercise:** initial strict inventory/drill caught changing Finder
   metadata; failed output retained. Added explicit recorded `.DS_Store`-only exclusion,
   with unchanged strict image/annotation/member checks. New content inventory
   restored32,832 files/8,904,043,917 bytes successfully; final complete hash check pass.
   No claim of independent storage, final corpus or semantic annotation validation
   follows from matching bytes. Current prefix audit is inherited by exact matching
   content; no unnecessary second full image-decode pass on the identical restore.
5. **Integrated guidance:** queue, CurrentState, iOS platform plan, roadmap,
   RemainingDelivery contract and BP91/92 updated. Source/count decision, coverage
   remediation proposal and backup ownership/verification runbook delivered together.

## Verification and retained failures

- `validate_reconstructed_corpus.py --corpus .build/debug-output/p0c-resume/r6-verified-prefix
  --report reports/work/IOS-COV-20260923/prefix-audit.json`: exit1, expected incomplete
  counts plus unindexed metadata; no per-member error. This is not a corpus pass.
- Retention inventory CLI strict exit0; first restore exit2 at `.DS_Store` hash check.
  Existing destination proves it was not solely pre-output rejection; original
  failure lacked stage attribution. Added preflight/postflight error prefixes.
- Explicit content inventory exit0; new-only full restore exit0, restore-content.log.
  Inventory hash `8bff6257de9ad5a2a67059b39c6cabe7f1d7c1f9653f3866b69564e265735415`.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python -m unittest
  scripts/test_corpus_retention.py scripts/test_reconstructed_corpus.py`:29 pass,
  0.402s before the final error-context change and0.4s after it; final log retained.
- Offline Swift build exit0,6.63s; Swift test exit0,14 XCTest+93 Swift Testing,
  no failures. Project-local TMPDIR/configurable caches; scoped host permission for
  existing Vision/CoreML tests. Swift sources unchanged by final Python refinements.
- Diff and new-link checks; no dataset/model artifact staged or committed.
  Source audit and inventory/restore ran as bounded live processes, not external waits.
  No running process remains from this tranche. No exact speed-up percentage claimed.

## Remaining blockers / continuation

P0-C continuation needs the requested split-count decision and fresh exact-target
setup before generation. No automatic retry of failed r5. Independent backup needs
maintainer-selected destination and owner plus scoped external-copy authority.
IOS-COV needs a later declared coverage/milestone decision, not fabricated absent AP.
All assigned offline review/software/drill deliverables are complete for review;
generation, complete corpus eligibility and external backup are explicitly incomplete.

Local iOS work: shared-status coordination not applicable. Worker-execution and model
workflow skills kept source preservation, change-scoped tests and model gates separate.
Next independent work under the active user goal: offline temporal-focus replay
comparison, reusing retained evidence without touching final evaluation or devices.
