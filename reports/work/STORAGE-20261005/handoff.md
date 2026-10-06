# October 5 storage cleanup

Scope: archive the inactive r6 verified reconstruction prefix, not active training
corpora, environments, build caches, Draw Things models or Git objects.

Original: `.build/debug-output/p0c-resume/r6-verified-prefix`.
Archive: `/Volumes/training-drive/data/NUIAK/archive-20261005-r6-prefix/r6-verified-prefix`.
Verified USB APFS volume UUID: `FD8D8E36-FAAC-4205-87ED-86134C3582B1`.

Inventory: 32,832 content files, 8,904,043,917 bytes. Finder `.DS_Store`
metadata is excluded from content checks, not images or annotations. Inventory seal:
`8bff6257de9ad5a2a67059b39c6cabe7f1d7c1f9653f3866b69564e265735415`.
The full ignored `r6-prefix-inventory.json` is retained locally and beside the archive;
its file SHA256 is `dd8a099a9b685b978500100a48718c122e1854d3b5731046fe8ae7e41f96180b`.

Copy completed with `cp -Rp`; source and destination content verification using the
existing `scripts/corpus_retention.py verify` command both passed (exit 0).
The exact local prefix was removed afterward. No source code or Git index changes.
Free space remained about 23 GiB after this step: logical removal is not equivalent
to physical APFS reclamation; shared extents/snapshots are possible, not diagnosed.

Recovery: verify the mounted SSD and archived inventory, then use
`scripts/corpus_retention.py restore --inventory reports/work/STORAGE-20261005/r6-prefix-inventory.json --copy /Volumes/training-drive/data/NUIAK/archive-20261005-r6-prefix/r6-verified-prefix --output .build/debug-output/p0c-resume/r6-verified-prefix`.
The destination must be absent. Historical retention drills referencing the prefix
require this restoration first; no symlink or live-reader mapping was introduced.
One external copy is not an independent backup.

## Transfer-package archive

Nine untracked regular archive files were copied, byte-compared with `cmp`, hashed,
then removed locally; all operations exited 0. Extracted captures remain local.
Restore by copying the archived file to its original relative path without overwriting.
Archive root is the directory above plus `transfers/`; original repo paths are retained:

| Original path | SHA256 |
|---|---|
| reports/work/ART-INTAKE-182/artifacts/pilot.tar.gz | d8605c1961914079f6ebac3fba4a87a5351d070a26889b55c854524d1725d7cf |
| reports/work/ART-INTAKE-183/artifacts/pilot.tar.gz | d8605c1961914079f6ebac3fba4a87a5351d070a26889b55c854524d1725d7cf |
| reports/work/SHADOW-REGION-111/artifacts/intake/ttr-settings-region12-20261004-v2.tar.gz | dbc1439b529e7647437b1f6914af7a4fa6f0f8fa62e1315634b0aed49ce80e8d |
| reports/work/SYN-06-BODY/artifacts/received/ttr-rendered-body-geometry-20261001-r1.tar.gz | 8923781a65d128800148a998a6a1ef0460b4f76b830a5df236b3ce0acca7d09c |
| reports/work/SYN-09-ARTWORK/artifacts/received/ttr-artwork-layout-handoff-20261001-r1.tar.gz | 40140d33da43da5071e132904d6dfaca87278675eb8cefce7e9ecdf71874857e |
| reports/work/NATIVE-TRANSITIONS-34/received/ttr-controlled-transitions-20261002-r1.tar.gz | cd2f42c0a05db7c99ce3408aca9fd7d0a9e8a4cfe7263e471fa98b3256438737 |
| reports/work/TTR-UPDATE-43/received/ttr-rich-reference36-20261002-r1.tar.gz | 3105dae538bdffb751e131830da0a4a18a8ecc86794dffcf6094b3d6100b0a98 |
| reports/work/INTAKE-99/received/ttr-native-collection-context-60-20261003.tar.gz | 0c8ddb401c6abe1a3487e9b814d9aac16c9d624c0e9d0f6f27407b31622ca1ef |
| reports/work/FOCUS-INTERRUPTIONS-17/artifacts/received/ttr-interruptions-20261001-r2.tar.gz | ac81aa85be099bcf05fae82acc8b89210adecb76b15c8edd9abd124395d28535 |

Final observed internal free space was about 22 GiB, versus 23 GiB initially.
Concurrent disk activity or APFS retention prevents attributing physical savings;
do not report the logical archived size as measured free-space gain. Draw Things
was running; its downloads/library were not inspected or modified in this scope.

Next substantial cleanup: STORAGE-LIVE-03 still has 39,487 tracked old r7 export
members. Maintainer de-indexing, then verified link rebinding, can unblock reclamation
of the approximately 10 GiB local r7 corpus. Do not delete that corpus first.
See `reports/storage/README.md`. Keep current checkpoints, original captures and
environments. Store new Draw Things model downloads on the SSD via its supported
model-directory setting; no app-library relocation was attempted.
