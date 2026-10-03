# STORAGE-LIVE-03 — active iOS SSD inputs

October3: software and storage integration verified. Data roles/eligibility unchanged;
model gates not assessed. No training, inference, capture, promotion, SMB or Git writes.

## Storage and recovery

Copied and verified109,475files/22,643,412,398bytes across r7-combined, r8-page-dot
and addon-v1 to matching registered prefixes under
`/Volumes/training-drive/data/NUIAK/live/NativeUITrainer/reconstructed_corpora/`.
Each `*-copy.json` contains the full sealed membership/hash inventory. r8/addon
reclaim exited0:11,530,385,038bytes (10.74GiB) removed, no tracked files removed.
Single SSD storage is not an independent backup. Current r6 recovery prefix unchanged.

`links.json` records19,740old r8 image-link texts, logical targets and SHA256 values.
Both source/destination bytes were checked before rebinding; all links checked after.
No directory was replaced with a symlink. Historical manifest/label bytes untouched.
Restore source files first, then original link texts; never rerun a partially applied
rebind without inspection. Registry and receipts are copied alongside data in
`live/storage-state-20261003-03/`. Registry SHA256:
`a20f217ea077ea4dd5625a70b147f37cc33924b98264323c4249b21bd7ddf579`.

Internal free space observed21→34GiB; shared blocks and concurrent activity prevent
attributing that change solely to this removal. The SSD has about1.7TiB available.

## Compatibility and findings

- Old r7 export has39,487Git-tracked files. Initial link planning correctly stopped
  at `tracked_link`; no tracked links changed. r7 SSD copy is usable, but its local
  original remains to support those links. Maintainer commands are in the storage guide.
- Initial directory-scan export admitted5,171extra duplicate-named source pairs,
  yielding24,911images. Loader membership comparison rejected it. Preserve
  `NativeUITrainer/yolo_dataset_r7_ssd03` as a failed trial, NEVER training input.
- Added opt-in `export_coco.py --manifest-members-only`: path, duplicate, missing-pair
  and image-hash validation. Corrected isolated export `yolo_dataset_r7_ssd03_frozen`
  has exactly14,540train/2,800validation/2,400test images. All label bytes and image
  target mappings match the retained export. No unmanifested files were deleted.
- `eval_run013.prepare` read the complete SSD source manifest and checked all19,740
  declared image/annotation/export bindings: zero integrity errors and zero cross-split
  decoded-pixel groups. Its report is `eval/preflight.json`; its export path references
  the first trial, whose declared subset is correct but extra files make that trial
  unsuitable for training. Corrected-export membership/labels/targets were separately
  checked in full by `qualify_storage_loader.py`; do not conflate these evidence scopes.
- Actual `train_ios_model.py --validate-only` on rebound r8 passes with14,540/2,800/2,400;
  launchEligible remains false by design. It did not start training or download weights.
- 48samples across all three splits used installed Ultralytics `BaseDataset.load_image`
  (decode/resize), with byte-identical arrays and dimensions. Initial-pass median local
  8.19ms/SSD8.30ms; repeated7.09ms/7.08ms. OS cache not flushed: not cold-disk or full
  epoch/augmentation throughput. Final all-target parity and repeat timings in
  `loader-final.json`; first successful probe in `loader.json`.
- Updated evaluator, exporter and page-regeneration/assembly source reads; cross-volume
  assembly copies rather than assuming hard links work. Prediction/training preflight
  validates registered SSD roots. Outputs/caches remain local. Historical code-pinned
  protocols are not silently rebound to changed source: future runs need fresh pins.

## Verification and remaining action

59focused Python tests pass (`.build/storage03-tests-final.log`), offline Swift build
and134tests pass (`.build/storage03-swift-{build,test}.log`). Python focused suite0.368s;
loader timings recorded per sample. Copy/full-audit elapsed totals were not instrumented.
One inherited mock test initially masked its own mount checks; fixed test composition.
All pre-existing dirty model/code/docs preserved. No new public API or skill changes.

Commands/logs: `storage_yolo_links.py plan/rebind/verify`,
`migrate_artifact_storage.py copy/reclaim`, `export_coco.py --manifest-members-only`,
`eval_run013.prepare`, `train_ios_model.py --validate-only`, and
`qualify_storage_loader.py`. See `.build/storage03-*` for failures and successful checks.
Full post-removal link validation is `.build/storage03-links-post.log`.

Next priority: return to the controlled spatial-localization fit diagnostic and
deconfounded coverage audit for the Focus Transition Model. Pin a specific representation,
fixed epochs/output budget and fresh storage-aware protocol before authorized execution;
DTM002 is still not usable. In parallel, maintainer may untrack the old r7 export, after
which a bounded link-rebind/reclaim pass can remove its remaining local source. No need
to wait for that final cleanup to implement the next model tranche.
