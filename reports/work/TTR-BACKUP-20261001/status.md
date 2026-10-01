# TTR destination backup verification

Update October1: producer22:14:46UTC explicitly reports backup15archives/4.88GB
destination receipt verified and capacity restored. Remaining artwork capture is
blocked by timeout/runner cleanup, not backup receipt. This is producer-reported
cleanup/capacity, not consumer deletion or an independently inspected remote disk.
Earlier observations below retain their original times.

The user explicitly assigned verification of the manually copied backup at
`/Volumes/training-drive/data/TTR/backup-transfer-20261001`. This narrowly
authorizes the supplied verifier and receipt, not restarting cancelled external
storage services, migrating the training pipeline or deleting any source.

Verified the destination is on the mounted local APFS training drive. Inspected
the entire Ruby verifier, README and manifest before execution. Confirmed 15
distinct regular archive files, safe filenames, expected sizes, no symlinked
destination or archive, and no pre-existing receipt to overwrite.

Ran the supplied `verify-backup.rb` on Maximum-mini. Exit 0: all 15 archives
match their exact sizes and SHA-256 hashes; total 4,878,703,538 bytes (4.88GB).
Reconciled generated receipt against all manifest entries and manifest hash.
No archive was copied again, extracted, moved or deleted. Receipt remains beside
the backup; a small exact copy is retained here and sent through SharedStatusFile.

Manifest SHA256:
`715075cdade6ab0e0940fa50460b2774babe3c476509b85d634bc55e2ccc0c45`
Inspected verifier SHA256:
`20025e693dbf0699fa0719d8682504f7dbfaa6b7109fef7d21f5ad4fa536f635`

Producer status observed at21:33:32UTC: 42 remaining artwork cases prepared in
seven validated batches; capture paused at9.42GiB free versus10GiB reserve.
Producer asks for destination receipt before reconciling local archive/staging
names and resuming at13GiB free. That cleanup is a separate producer-owned action;
this receipt does not claim it happened or authorize broad deletion.

This is a selective archive backup, not a complete project backup, archive
restoration test, training admission or new capture qualification. Private human
recording remains on the local drive; only verification metadata is returned.

## Publication confirmed

Verification completed2026-10-01T21:53:18Z on Maximum-mini.local. Exact 3,108-byte
receipt SHA256 `ffe7da669b0d520817a20ccf4936560d575de77cc2aee606a4479c0989ffa1d2`
matches drive, repository and published copies. Shared destination:
`/Volumes/SharedStatusFile/nuiak/responses/nuiak-20261001-backup-transfer-receipt/backup-verification-receipt.json`.
Own `packets.TTR-BACKUP-20261001` entry published and read back; safe YAML parsing
and unrelated-content preservation passed. Requested producer acknowledgment via
`nuiak-20261001-backup-transfer-receipt`. Peer acknowledgment, cleanup and capture
resume remain unobserved. No automatic monitor installed.
