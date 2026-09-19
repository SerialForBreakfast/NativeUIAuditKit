# Phase 6a dataset availability inspection

Read-only inspection on 2026-09-19. No data, links, manifests, labels, or historical reports were changed. This report establishes current availability, not deletion cause or time.

## Method and results

Read `NativeUITrainer/yolo_dataset_41class/{train,val,test}.txt` line by line. For each listed image, check `is_file`, `is_symlink`, target existence, and its corresponding `<split>/labels/<stem>.txt`. No broad image directory scan was used. Existing image counts below mean resolvable files, not verified decodable PNGs or verified historical identity.

| Split | Manifest entries / unique paths | Resolvable images | Broken symlinks | Existing labels |
|---|---:|---:|---:|---:|
| train | 11,984 / 11,984 | 1,441 | 10,543 | 11,984 |
| val | 3,056 / 3,056 | 360 | 2,696 | 3,056 |
| test | 2,000 / 2,000 | 0 | 2,000 | 2,000 |

`dataset/dataset/train/` does not exist at inspection time. `dataset/dataset/validation/` exists; its existence alone says nothing about recoverable image content. The representative test link `test/images/img_001801.png` points to the absent `dataset/dataset/train/img_001801.png` under this checkout. Full target inventory and recovery-source search remain future work.

## Evidence hashes (SHA-256)

| Artifact | Hash |
|---|---|
| train.txt | `d72f210f9e904194d7c4e521fcae8423826c34e2cb651fbe483a53b60bb56006` |
| val.txt | `e1161811c7fabc0137b931083d6fb6318aa5976c4a467d4d0b80c0d4596b1f18` |
| test.txt | `6411c14856a526c82963a25ae9f06a844c351a3a5fd7615f01140c82840db9d7` |
| reports/eval_results_phase6a.json | `1597ec69b4290a085c1f1e28215379689537b7e0a693e0df67302766bb602058` |

The preserved report identifies `phase6a_r009`, evaluation time `2026-09-15T18:51:18Z`, 2,000 images, and mAP50 `0.585669`. This is historical evidence, not evidence that inference can run now. The hashes above identify surviving artifacts; they do not prove the identity of missing image bytes.

## Unknowns

- Whether source files were deleted, moved, are on an unavailable volume, or exist in a backup/other checkout.
- Who or what changed the source tree, and when. Directory timestamps do not establish responsibility.
- Whether original per-image hashes or an immutable corpus archive survive.
- Whether apparently surviving images decode and match the original corpus.

Next action: assign [P0 dataset recovery assessment](../Research/DatasetRecoveryPlan.md). Preserve surviving evidence and avoid rerunning exporters or cleaning broken links before that assessment.
