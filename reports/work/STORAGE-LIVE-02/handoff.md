# STORAGE-LIVE-02 — retained prefix and dependency audit

October3: completed bounded retention migration; active iOS migration deferred until
the explicit STORAGE-LIVE-03 consumer contract passes. No model/device/Git operations.

Moved `.build/debug-output/p0c-resume/r5-verified-prefix` to the same logical suffix
under `/Volumes/training-drive/data/NUIAK/live/`. Local APFS mount verified as
`/dev/disk25s1`; no incoming links found in trainer/dataset/report/debug trees and
no matching script/research references. No claim of a whole-disk reference audit.

Existing `migrate_artifact_storage.py copy` and `reclaim` commands exited0:
16,334files,6,182,843,541bytes (5.76GiB), no tracked files removed. Both copies were
hash-verified before removal; complete SSD inventory verified afterward through
`artifact_storage.resolve_input`. Finder metadata is excluded and may remain local.
Inventory SHA256: `570f0f83543508f3236858b0ac44bbbd297a5983e849a8f0365dd23ec05a6a11`.
Receipt: `r5-copy.json`, SHA256
`52b07281634dd6c250642d7b213b4cf601824088bcb6089436f1c84d3c2e5155`.
Registry SHA256: `d964d5720de68b1fb7419de7c00dae10addd8f4a4941dd23f9decb5d5deeb8e8`.

Actual `focus_direct_transition.py --sources reports/work/DIRECT-TRANSITION-53/sources.json
--output reports/work/STORAGE-LIVE-02/transition-inventory` exited0:29pairs,0exclusions,
unchanged hash `9735108bf5ae011dfb17c07f7d49c4b42dfba4c9e1e027459a2b377047f589aa`.
Its generated proposal does not authorize a run or change data roles.
11 storage regression tests passed. No implementation code changed; previous integrated
Swift results reused. A post-check command initially had a parenthesis typo; corrected
read-only verification exited0. Final diff review required before handoff.

`p0c-resume` footprint fell15GiB→9.4GiB. Internal free space was approximately21GiB
both before and after; APFS sharing/concurrent activity means logical bytes reclaimed
are not a physical free-space guarantee. No system/update files removed.

Outcomes: storage verification passed; existing eligibility unchanged; active transition
input integration passed; model gates not assessed. No semantic requalification of r5.
One SSD copy is not an independent backup. Restore using the receipt and operations
guide; never overwrite existing local changes or alter sealed manifests.

Remaining: r7 has absolute YOLO links, direct evaluator reads and regeneration/assembly
path assumptions. r6 contains retained lineage/link targets. They remain local, as do
tvOS dataset trees whose complete legacy-consumer compatibility was not established.
Next substantial tranche is STORAGE-LIVE-03: qualify these readers plus versioned exports,
measure real input loading without training, then reclaim verified corpus copies.
SMB is not applicable. All pre-existing model/code/document edits preserved.
