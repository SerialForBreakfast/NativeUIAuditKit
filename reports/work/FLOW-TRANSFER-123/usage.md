# Exact SMB transactions

Use `scripts/shared_transfer.py` from the NUIAK root with resident `.venv-yolo`.
Transaction input is a small version1JSON/YAML file under the project. The two
adjacent real examples pin current completedv1and pendingv2deliveries.

Read-only default (no folders, receipts or staging created):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/shared_transfer.py reports/work/FLOW-TRANSFER-123/pending-v2.json
```

`--action publish|receive|cleanup` without `--execute` checks input prerequisites only,
returning inputs_verified_execution_not_proven rather than promising runtime success.
Only add `--execute` for an explicitly assigned named transaction. A guide or peer
message does not authorize a transfer/deletion. `cleanup` on pendingv2correctly
rejects its missing receipt; do not use its predecessor's receipt. Permission errors
require scoped sandbox approval, never a different share or service.

Required transaction keys: version(integer1), requestID, sharedPath, localPath,
bytes(positive integer), sha256, receiptPath(null or TVTestRig-owned relative path).
Project-local original/destination and all parent directories must already exist
where relevant. No symlinks/traversal; no rewriting status/guides through this tool.
Mount must be verified SMB on sillycon.local or documented IP; no automatic mounting.

- Publish: NUIAK-owned path only; verifies local original, unique staging, exclusive
  final rename and readback. Existing identical final means already_verified;
  different content fails without overwrite. No executable transfer by implication.
- Receive: peer-owned source only; copy to new local destination, return exact
  receiverReceipt metadata on stdout. Capture output in project-local report and
  publish the receipt through owned metadata flow. No automatic unpacking, labels,
  training admission or peer-file cleanup. Source remains retained.
- Cleanup: requires matching copied_and_verified peer receipt with exact request,
  path/size/hash, retained original verification and current shared bytes. Deletes
  only the exact NUIAK shared duplicate. Missing shared file is reported as already
  absent, not proof that this invocation deleted it. No timestamps/expiry criteria.

Interrupted staging uses a deterministic `.nuiak-transfer-<digest>.partial` next to
the destination. A fully verified stage can resume without copying; incomplete or
mismatched stage fails and stays for diagnosis. Do not delete or overwrite it just
to retry; inspect and obtain appropriate cleanup authority. Commands are idempotent
for completed exact transactions, not a distributed lock. Producer artifacts must
remain immutable; competing writers or ambiguous filesystem outcomes require
reconciliation, not blind retries. No promise of atomicity across source and receipt.

Exit0 means the reported inspection/action succeeded, not training eligibility.
Exit2 includes a typed reason; retain partial evidence. No background monitoring,
mounting, permissions changes, archive extraction or device control is installed.
Large files stream in1MiBchunks with declared-byte cap; free-space check reserves
an additional1MiB but is not a forecast of other concurrent workload needs.

macOS exclusive publication uses resident SDK's `renamex_np(RENAME_EXCL)`; an
unsupported filesystem fails without a replacement fallback. Local real-file tests
exercise this behavior. **Live October4 check: this SMB mount rejects both exclusive
rename and separately tested atomic hard-link publication with errno45/ENOTSUP.**
The real workflow response remains complete in staging, not published. Inspection
reports staging status/path. Do not weaken this into an overwriting rename or expose
a partial final artifact. Outbound publication needs a reviewed supported protocol;
local receive publication and receipt checks remain independently useful.
