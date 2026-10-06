# GEN-PARITY-199 / ARTWORK-204 — planner and bounded worker dispatch

October5,2026 Pacific (October6UTC). Completed local implementation and dispatch;
Big Dog generation/acceptance are pending, not silently included in software completion.

| Outcome | Result |
|---|---|
| Software verified | Passed25focused Python tests, offline Swift build and142Swift tests |
| Data eligible |24pilot objects byte-verified; rights/review pending, zero render-eligible, no training admission |
| Integration qualified | Actual producer inventory adapter/cache planner exercised; SMB request published/read back; native renderer not assessed |
| Model gate | Not assessed; no model execution or promotion |

## Delivered and evidence

- `scripts/generator_asset_plan.py`: strict versioned normalized inventory, explicit
  cache index, existing shared-transfer hashing, bounded deterministic missing-object
  batches, aliases and connected ancestry checks. No model imports/network/transfer.
- `normalize-image201` preserves original producer records and development roles.
  Candidate-for-review and licence text remain pending assessments, not approvals.
  Derived producer records require a further explicit lineage adapter, not silent loss
  of parent identity. Same-hash conflicting assessments fail rather than bypass review.
-25generated-fixture tests cover real CLIs, exclusive output, unknown versions/fields,
  duplicate IDs/keys/cache entries, size/hash mismatch, missing pixels, symlink/traversal,
  pending/rejected rights/review, non-artwork routing, bounded batching and transitive
  cross-role ancestry through unassigned/blocked bridge records. Test files are created
  under project `.build/debug-output`; tests do not depend on retained reports.
- Actual201inventory normalization and planner verified24cached objects in four groups.
  No missing eligible objects/request bytes; all24remain pending review/rights. Original
  plan and final-code replay compare byte-identically. No raw images copied or decoded
  again; unchanged prior decode evidence remains in RENDER-202.
- Immutable204request published with `cp -n`, `cmp` and duplicate-key-safe YAML readback
  on verified sillycon.local SMB. Exact destination:
  `nuiak/requests/nuiak-20261006-artwork204-campaign.yaml`.
  SHA256`2bee946d76db0fd982cdd5745f753030c36a4fb52f253eaaa3892772923b528e`.
  Artwork-first priority, installed-tool-only generation, no active-job interruption;
 256slots =4roles×8subjects×2compositions×4treatments,64included challenge slots.
  At most256new calls,32/shard,4GPUh/4GiB, missing-hash transfers/receipt cleanup.
  Peer204acknowledgment and generated results remain pending.
-203peer ack/start records identify the original request hash and CPU compositor work
  at04:56:15UTC. This is peer-reported start, not independent completion.

Ignored `artifacts/` retains normalized inventory, explicit cache map, plan/final replay
and logs. Normalized inventory SHA256
`83305a09b0d17e03b267c35f3ff05111c97f52c512388fbcaf6be8d002db16fd`;
plan SHA256`96699e5b323272f1d53ebd2c81a7dc3f90521b1bf64864ab98f8a27e6dfd1af0`.
No generated images or large inventories should be committed.

## Reusable commands and validation

From repository root, with a new output path (omit `--output` for read-only stdout):

```sh
.venv-yolo/bin/python -B scripts/generator_asset_plan.py normalize-image201 \
  --inventory reports/work/RENDER-202/artifacts/render202-metadata-return01/inventory-v1.json
.venv-yolo/bin/python -B scripts/generator_asset_plan.py plan \
  --inventory reports/work/ARTWORK-204/artifacts/image201-normalized.json \
  --cache-index reports/work/ARTWORK-204/artifacts/image201-cache.json \
  --cache-root reports/work/RENDER-202/artifacts/local-image201-review-return01
.venv-yolo/bin/python -B -m unittest discover -s scripts -p test_generator_asset_plan.py
```

Normalized root: `schemaVersion: generator-resource-inventory-v1`, `resources`.
Each resource has id/kind/sha256/bytes/source/sourceRevision/ancestryGroups/dataRole,
rightsStatus/rightsEvidence/reviewStatus/reviewEvidence and optional sourceRecord.
Cache root is explicit; `asset-cache-index-v1` has `files: [{sha256, path}]`, where
path is root-relative and link-free. Only artwork with assigned role and verified
review/rights can enter the missing-byte request. Verified cache bytes additionally
permit render eligibility; trainingAdmission always remains not_assessed.

Focused tests exit0 in0.249s. Initial restricted Swift build failed before compilation
with `sandbox-exec: sandbox_apply: Operation not permitted`; failed log preserved.
Scoped approved build/test used the same offline flags, project-local TMPDIR and
CLANG_MODULE_CACHE_PATH, plus `--cache-path .build/asset204-cache`,
`--config-path .build/asset204-config`, `--security-path .build/asset204-security`.
`swift build --skip-update --disable-automatic-resolution` passed (0.64s reported).
`swift test --skip-update --disable-automatic-resolution --no-parallel` passed:
14XCTest plus128Swift Testing tests,142total, exit0. No dependency downloads, sandbox
disablement or system reset. Final Python-only guard changes retested with25checks;
unchanged Swift evidence reused. Final actual planner replay exit0 and `cmp` exit0.

## Scope preservation and next tranche

Existing dirty IOS196scripts, model/experiment/architecture notes, storage work and
other coordination requests preserved. No Git writes, capture, training, installations,
model changes, raw dataset moves, peer-file edits or automatic monitoring.

Next substantial tranche: review the artwork campaign inventory/missing hashes and
finish IOS-ASSET-200's opt-in native asset adapter with default-path regression tests;
prepare matched native campaigns. In parallel resolve202's exact TTR source/interface
availability without overwriting its dirty checkout. Rights/review decisions and
fresh native runtime qualification precede capture. IOS-PROPOSAL-197 remains an
independent actionable diagnostic if artwork/native source readiness stalls.
