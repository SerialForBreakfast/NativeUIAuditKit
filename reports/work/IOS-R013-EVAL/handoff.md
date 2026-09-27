# IOS-R013-EVAL — review-ready

Completed2026-09-27 by current NUIAK evaluation worker. Parent TASK-6a-11.
Scope: approved local epoch91 evaluation, compatible Run009 comparison, necessary
evaluator fixes, verification and status. No retraining, CoreML export, promotion,
device capture, Git writes or external publication.

## Result and recommendation

Run013 improves the exact same2,000 withheld-family cases, but does not qualify.

| Population | Images / supported classes | mAP50 | mAP70 | mAP90 | mAP50–95 |
| --- | --- | --- | --- | --- | --- |
| Run009 withheld baseline | 2,000 /13 | 0.5549 | 0.4310 | 0.2302 | 0.3982 |
| Run013 withheld | 2,000 /13 | 0.6322 | 0.5834 | 0.5299 | 0.5707 |
| Same-input delta | unchanged cases | +0.0773 | +0.1525 | +0.2997 | +0.1725 |
| Run013 addon, within-family only | 400 /33 | 0.9785 | 0.9697 | 0.9696 | 0.9703 |
| Run013 combined, supplementary | 2,400 /38 | 0.8790 | 0.8551 | 0.8375 | 0.8527 |

These are supported-class custom all-point interpolated VOC AP means, not official
COCO/Ultralytics AP. The original historical Run0090.586 has no numerical delta:
its corpus differs. Both compared models use the same retained metric implementation.

**DS-G8 remains open.** The existing0.85 withheld mean is unmet; imageView, listRow,
pageControl and secondaryButton also fall below the historical0.65 class floor
(ExperimentLog Run007 criteria). All41 classes still need independent coverage;
homeIndicator, unknown and webContent have no test support. Addon families overlap
train/validation/test. Reused r6 tests are diagnostics, not an untouched final release
challenge. Release checks outside this assignment remain unrun. No gate threshold
or taxonomy changed; the shipped five-class model remains unchanged.

Next: the [ranked failure/coverage assignment](error_analysis.md), prioritizing
button-role errors, page controls, row/image family transfer, toggle regression and
thin scroll indicators, alongside genuinely independent class coverage. Do not launch
another training run solely to optimize the combined score.

## Inputs, accounting and runtime

- Training already completed106/150 epochs in62.818hours, patience15, best epoch91.
  Best checkpoint SHA-256:
  `88c3cffb51b0b29dd71672fb64f6e60be56757e6de507886ef2f5c2ff86dd9b7`.
- Run009 checkpoint SHA-256:
  `5e233fac9e035cae9c1cb6e8e53f43d4f7868b28e1ee6b5db5c9cabbe3c223f8`.
- Audited all19,740 source-backed pairs:14,540 train /2,800 validation /2,400 test;
  source PNG and sidecar hashes, exported image hashes, full decode/dimensions,
  normalized labels and exact source-to-YOLO conversion. No errors, decoded duplicate
  groups or cross-split pixel duplicates. Family independence remains separately
  limited; exact pixel uniqueness does not prove absence of near-duplicates.
- 2,400/2,400 Run013 records are `ok`; zero failed, missing, duplicate, unexpected or
  empty records. Empty results are valid in the software and explicitly unit-tested.
  36,291 detections retained. Run009 retains2,000/2,000 valid rows (37,739 detections).
- Category map, all member hashes, manifests, evaluator source and runtime versions
  are pinned in [freeze.json](freeze.json) and [preflight.json](preflight.json).
  MPS,640 letterbox, confidence0.001, NMS IoU0.7,max300, no augmentation, unchanged
  class-aware NMS. Operating-point P/R and FP/FN use confidence0.25 and IoU0.50.
- Python3.13.2, torch2.13.0, torchvision0.28.0, Ultralytics8.4.124, NumPy2.3.5,
  Pillow12.3.0. Candidate export including preflight128.24seconds; model loop114.2s;
  complete infer/reuse stage140.7s; metrics30.1s; full corpus preparation219.9s.
- Retained Run009 artifact passed identical image IDs/bytes/labels/settings/map,
  checkpoint and detection/accounting checks. [Reuse receipt](baseline_receipt.json)
  records source hash; no fresh Run009 inference was needed.

## Acceptance evidence

| Assigned requirement | Evidence |
| --- | --- |
| Frozen inputs and integrity/split audit | [freeze](freeze.json), [complete inventory](preflight.json) |
| Two populations, complete union | [withheld manifest](withheld_manifest.json), [addon manifest](addon_manifest.json), [combined manifest](combined_manifest.json); integration test verifies disjointness/union |
| Explicit checkpoint and approved inference | [candidate predictions](candidate_predictions.json), [runtime](inference_runtime.json), [host execution log](inference-host.log) |
| Compatible baseline and same-metric deltas | [baseline predictions](baseline_predictions.json), [baseline scored](baseline_withheld_scored.json), [candidate scored](candidate_withheld_scored.json), comparison section of evaluation.json |
| AP50/70/90/50–95, support, P/R, families | [readable metric tables](metrics.md), [full metric report](evaluation.json) |
| Misses, FP, regressions and prioritized next work | [error analysis](error_analysis.md), confusion/examples and per-family class detail in evaluation.json |
| Software checks and failure paths | [verification](verification.md):23 focused Python tests, offline Swift build,14 XCTest +109 Swift Testing tests; all pass |
| State and run history | Research/ExperimentLog.md, Research/CurrentState.md, Tasks.md; BP-27 correction for mixed-population reporting |

## Outcomes kept separate

- **Software:** complete and verified; explicit-manifest evaluation, frozen byte
  validation, taxonomy binding, compatible comparison and readable reporting work
  end to end. No library API or schema/taxonomy changes.
- **Data:** audited existing r7 bytes and split identities; no data created/altered.
  Partial independent support and within-family addon coverage only. Frozen manifests
  point to retained data through a project-local symlink; they are not a backup.
- **Integration:** local checkpoint→manifest exporter→strict comparison→metrics→report
  exercised. CoreML, consumer/device and TTR integration were not run or qualified.
- **Model gate:** candidate improves this diagnostic comparison, DS-G8 fails/remains
  open, no promotion. No further work is needed to finish this evaluation tranche;
  subsequent data/model work needs a new assignment.

The workflow skills kept inference separately scoped, source/data identities pinned,
unsupported metrics unavailable and completion tied to evidence. Shared coordination
is **not applicable**: no finding changes TTR's next action. Photos acquisition is
independent; no shared-status publication, device reservation or heartbeat was made.
