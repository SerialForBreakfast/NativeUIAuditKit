# External training storage — status2026-09-30

## Cancelled — supersedes all next actions below

User cancelled external shared-drive and SSH/SFTP/rsync plans. Use project-local
evidence and existing verified SharedStatusFile/tvtestrig hash/receiver-receipt flow.
No retry, migration, mount or system cleanup authorized; not an active focus blocker.

User's closure supplies later evidence not independently rerun here: authenticated
enumeration eventually advertised both shares, internal shares worked, external
mounts still failed after share recreation, APFS reformat and File Sharing Full Disk
Access refresh/restart. Filesystem and privacy causes remain unproven. User reports
TCC request983.152 authValue0 for smbd SystemPolicyAllFiles; other requests did not
prove external-volume denial. Redacted bind-tree logs cannot identify exact share.
User enabled Remote Login; reported read-only SSH attempt stopped at strict host-key
verification, with no authenticated session/transfer/mutation. Disk-image experiment
was proposed but not performed. No agent reformat or migration occurred.

Remote Login was last user-reported enabled; shutdown is unverified. If enabled
only for this abandoned workaround, user may disable it. No automatic setting edits.
Producer-local diagnostic paths supplied by user: .local-work/training-share-mount,
.local-work/share-unavailable-check-20260930,.local-work/storage-status-20260930,
.local-work/ssh-storage-check,.local-work/storage-cancelled-20260930. These are
reported evidence locations, not assumed NUIAK files or authorization to alter them.

Process correction: repeated retries/recreation after unchanged results added no
evidence. Future diagnosis needs a distinct failing boundary and falsifiable check;
do not present stale-path/filesystem/privacy hypotheses as causes. No formatting or
broader remote service without evidence and explicit scope.

## Historical observations (superseded)

Updated09:05PDT /16:05UTC. Local disk/share rechecked; no new remote login test.

- Local drive renamed to training: exFAT, `/dev/disk6s2`, approximately1.8TiB free;
  existing `/Volumes/training/data_training`. Old Crucial X9 mount path absent.
- Fresh disk query verifies same volume UUID F673FB8B-97D3-39F6-AF8A-AEA44CC42ED9
  and partition UUID6E1B6421-621C-4E34-B729-577503A66D84, identifying the same storage.
- Fresh Max share query shows SMB name data_training targeting the new folder,
  shared1/read-only0/guest-access1. Guest flag is not proof of effective anonymous
  access or intended security; no permissions changed. Prior listener445 check worked.
  Share registration alone does not prove authenticated remote access.
- Latest user-pasted Sillycon `smbutil view //josephmccraw@192.168.1.21` failed
  authentication. Earlier Finder errors said share absent; neither proves exFAT
  is the cause. No successful remote mount or verified write receipt exists.
- Next operator check: Max File Sharing Options/account enabled for SMB, followed
  by successful authenticated share listing from Sillycon. Do not repeatedly try
  passwords or broaden permissions. Never paste credentials into status/chat.
- After authentication: resolve actual remote mount, verify volume/destination,
  then separately scoped small write/readback test before data migration. Preserve
  manifests and originals; no migration/deletion/reformat undertaken or authorized.

Outcomes: software not applicable; local storage observed; cross-host integration
blocked at authentication; data admission/model gates unchanged and not assessed.
No training/capture performed. Earlier focus geometry and optional Vision producer
blockers unchanged by this status-only reconciliation; no fresh runtime check claimed.

Coordination: see coordination.md. SharedStatusFile is currently not mounted, so
the new authentication finding is not yet delivered to TTR.
