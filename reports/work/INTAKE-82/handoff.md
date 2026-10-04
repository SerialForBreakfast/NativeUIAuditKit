# INTAKE-82 — portable intake and admission guards

| Outcome | Evidence |
|---|---|
| Software verified | Nine generated regressions, three retained integration checks; offline Swift build/134 tests pass |
| Data eligible | No new admission;12 table pairs retain prior disposition,24 rich cases remain unsupported |
| Integration qualified | Existing retained intake CLI accounts for36 pairs/72 unique images; no live runtime claim |
| Model gate passed | Not assessed; no model run or promotion |

## Scope delivered

Primary: `intake_native76.verify_selection` now reads the named source receipt,
requires completed export/case identities and exact selected file inventory, and
checks original manifest bytes against input_manifest_sha256/input_manifest_bytes.
Producer source f933e299 SyntheticCampaignCoordinator export distinguishes that
hash from semantic manifest_sha256; neither is silently substituted for the other.
No wire schema or rich recipe compatibility was loosened.

Companion: all five NativeAdmissionTests now construct generated32train/5development
and12proposed records. They no longer depend on ignored private corpora or silently
skip. Exact approval, record/role preservation and cross-split leakage remain tested
through real build_admission/admitted functions. Test-only records are never written
as approved data. Existing native76 corpus tests remain additional integration checks.

New ReceiptTests generate24 tiny selected cases in operation-owned .build temporary
directories. Missing/partial/wrong-version receipts, wrong campaign, changed manifest
hash/size, failed/mismatched cases, bad inventories, duplicate/traversal/member hashes
and extra files fail. Actual CLI replay passes the strengthened outer contract and
still rejects all24 rich examples at invalid_metadata: canvas_selectedIndex.

## Commands and evidence

- `python -m unittest scripts.test_intake82 scripts.test_native77 scripts.test_native76`:
  exit0,12 tests in0.110s; `.build/intake82-tests.log`.
- Portable-only first two modules: exit0,9 tests in0.066s, no skips;
  `.build/intake82-portable.log`.
- `scripts/intake_native76.py --root reports/work/NATIVE-INTAKE-76/received --output
  reports/work/INTAKE-82/intake`: exit0,36pairs/72endpoints/72unique images;
 12inspection-only passes,24unsupported-rich rejections. Raw output `intake/intake.json`
  remains ignored; `.build/intake82-retained.log` records counts.
- Offline Swift build exit0 (1.82s); test exit0,14 XCTest plus120 Swift Testing;
  `.build/intake82-swift-{build,test}.log`. `git diff --check` clean.

The first generated-test run hit exclusive fixture-writer collisions; repaired only
test fixture mutation using the owned temporary file. Production exclusive writers
unchanged. No raw source bytes, historical protocols or old experiment seals modified.
No Git writes, simulator setup, crop regeneration, training or TTR repository edits.
Existing dirty-worktree changes preserved.

## Blocker and next substantial tranche

Read-only TTR HEAD/all-local-ref inspection still reports f933e299; native table
compiler remains native-table-v1. Matching rich-v2 source is absent. Do not fetch or
rewrite another checkout, strip unsupported fields, or recapture the retained24.
Resume BATCH79-A with source-backed strict rich compatibility, observed coverage
reconciliation and exact role proposal. Then bind one grouped missing-coverage
session, including actual small focusable controls, and reserve independent final
groups before the next candidate. Capture/training/promotion approval exists, but
runtime readiness and data/quality gates remain requirements.

No new SMB publication: this is local consumer hardening and does not change TTR's
already-published source-publication/coverage next action. Existing SIZE81 follow-up
and its acknowledgment gap remain unchanged. Worker-execution guidance kept this
as one integrated deliverable with a portable-admission companion, not per-test packets.
