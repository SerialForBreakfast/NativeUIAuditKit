# Approved expanded cleanup — October 3

Completed. Internal free space increased from17GiB at start to39GiB at final
observation (~22GiB recovered this tranche; ~33GiB since original5.9GiB baseline).
No app uninstall, simulator erase, service reset, model change or Git write.

## Removed

- Inactive Xcode DerivedData folders `TVTestRig-bfjtodidumtdyagsgxcmwrmheuxr`
  and `JoesProxy-dxemdjtrbsmajlcxomqjmywpxhsk`, approximately4.2GiB combined.
  Rebuild on demand; no backup needed. Fresh process inspection confirmed the
  running TTR and its companion use `TVTestRig-fssavpzkujakgqggjglqjvvrtyoo`,
  which remains intact. No GeneratorRunner or xcodebuild process was running.
- GeneratorRunner `Documents/dataset` and `Documents/reconstruction`, only in
  simulator `F3EF9DB8-0B0F-4757-B653-D1628269F6FF`, container
  `C8AB9407-5AEE-427B-8350-B4B6C6B31A46`. Container metadata verified app identity
  `com.nativeuiauditkit.generatorrunner`. App and other Documents/probes preserved.

76,464files/19,641,582,180bytes (~18.29GiB) were exact SHA256duplicates of retained
repo corpus members and deleted without additional backup.899unique files totaling
111,619,790bytes (~106.4MiB) were copied to:

`/Volumes/training-drive/data/NUIAK/archive-20261003/generator-unique/`

Every source and retained/archive copy was rehashed before removal. Membership
was rechecked; source symlinks/nonregular files rejected. All77,363files were accounted
for. No Finder metadata exception was needed. Exact empty source directories were
removed after file deletion; neither simulator installation nor other app data changed.

## Evidence and recovery

- `generator-relocation.json` records every original path, SHA256, byte count,
  retained path and action. A byte-identical copy is on the SSD beside unique data.
- `generator-cleanup-complete.json` records final counts; `generator-cleanup.log`
  records progress/completion. One-off implementation `.build/cleanup-generator-20261003.py`.
- Archive volume freshly verified local APFS `/dev/disk25s1` at
  `/Volumes/training-drive`, distinct from internal storage; mount identity rechecked
  before deletion. Device identifiers can change on later mounts.
- Exit0 for both cleanup operations. Active TTR app path and removal of both inactive
  build folders verified after operation. Repo retained data was read/hash-verified,
  never modified. Existing uncommitted code/model work remains intact.

Recovery is normally unnecessary: these are retrieved generator outputs. If needed,
use the relocation journal's retained file and original path, check SHA256 before
copying, and obtain current exact-container/runtime write authority. Do not copy
blindly into an old app-container UUID. Unique files now have one archive copy, not
a redundant backup; the unchanged repo retains the duplicate members.

No full Swift/model tests were rerun for data-only cleanup. Verification was complete
byte accounting, process/mount/app-identity checks and diff review. No SMB interaction.

Next substantial storage tranche remains migration-aware path resolution for remaining
repo bulk data, followed by real consumer read/load verification on the SSD. Avoid
removing the active tvOS simulator or running TTR build merely to gain more space.
