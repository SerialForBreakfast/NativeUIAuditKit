# Frozen input index — Joe Office review

Reviewer Joe explicitly completed all8 frames/113 controls at2026-09-28T18:47:53Z.
These files and originals were verified, not edited. Hashes are SHA256.

| Artifact | SHA256 |
| --- | --- |
| [Finish receipt](../HUMAN-REVIEW-01/office-batch/review-revisions/20260928T184752Z-15f34d37/receipt.json) |`0a5fa6e9990d03256b886e7fbcf6dd1ccfa6d662d458667d3e061ff6944a93b6`|
| [Human revision](../HUMAN-REVIEW-01/office-batch/review-revisions/20260928T184752Z-15f34d37/revision/revision.json) |`8a9efa923a4bbab65e42900b13897f846ec272138cea34528d97ec5b1fbb275f`|
| [Production crop report](../HUMAN-REVIEW-01/human-crops-joe-20260928/crop-qa.json) |`a8b8d995fb61c5c1dd81d1b4d93ca0c617dc6af7bb92411ad9237b88b9320e7b`|
| [Final audit](joe-final-20260928/audit.json) |`92e1cd69bc44dd50eb67048fe83e1ef9d34c61929dc28d6a60a25a920e1ce9df`|

The audit's `inputs` enumerates exact batch, original frames, raw evidence,
editor snapshots and all113 crops. Crop report pins source/runtime and ordered
membership. Production preprocessing:16% expansion,256×256, top-left pixel xywh,
`FocusRingClassifier.makeCrop-v1`; bounded16 items/80M decoded pixels.

- Crop source hash: `37bfaa55be5fa0e8ead574211e6ac7e7772a74ae3653e2ac9df158c3a16554a3`.
- Helper hash: `c099d89f293e1b059d7fa0ba301fb81f1e1fadfbf5bdbcc6eb14fea353ad5f09`.
- Runtime: macOS26.4.1,arm64. No model argument or model load.
- Eight1920×1080 frames, one source session,113 crops/111 distinct crop pixels.
- Earlier `joe-20260928/` audit is retained preliminary evidence; final authoritative
  audit output for this tranche is `joe-final-20260928/`.

Local free space was38GiB before processing; no deletion or transfer was needed.
Same-volume originals/revisions are provenance preservation, not an independent backup.
