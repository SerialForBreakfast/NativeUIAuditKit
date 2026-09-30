# FOCUS-RESET-01 — complete for review

The approved reset, including the named weight download and one frozen-feature
baseline, is complete. Full acceptance mapping and execution evidence:
[FDR-015 handoff](../FDR-015/handoff.md); [results](../FDR-015/results.md).

- Software verified:93focused Python tests, offline Swift build and14XCTest+
  109Swift Testing tests pass. Actual diagnostic and trainer entrypoints exercised.
- Data verified for existing development scope only: unchanged363training pairs,
  nine retention pairs,453real selection crops and64exclusions. No evaluation
  members moved into training; no new corpus qualification.
- Integration verified: official10,306,551byte weights downloaded/hash-checked,
  frozen encoder/BN with ordered cached features, actual MPS run30epochs and full
  stored-score replay. No speculative adapter or dependency install.
- Model gate failed:0eligible checkpoints; no export/promotion. Final ranking
  improves5/13→11/13 compared with FDR014's final snapshot, but FDR014 epoch1 already
  ranked11/13. Fixed0.85 yields0/35real positives and retention9/18. No best.pt.

The original cached-score diagnosis and eight-page visual inspection remain in
[findings](findings.md), with final source-bound replay in `final-evidence/report.json`.
It verifies14,601scores/488image-crop files, identifies13complete/27excluded frames,
and separates ranking, strict ambiguity checks and winner-above-threshold logic.
All refer to reviewed boxes and reused development data, not end-to-end
detector/CoreML qualification. No labels, thresholds or challenge inputs changed.

FDR015 provides another14,601verified scores. Home artwork remains wrong in both
complete Home cases; Settings-related8/8 and tabs3/3 rank correctly. Next assignment
is the existing matched-artwork/context audit and a separately approved grouped
ranking/calibration experiment—not more unchanged synthetic scale or a repeat run.
No new annotation requested for this reset.

The worker-execution/model-workflow procedures kept inputs, runtime, authorization
and four outcomes separate. Research was updated before implementation. Prior
unrelated working-tree edits retained; no Git writes. No running process, retry or
monitor. TTR coordination is not applicable because this local result changes no
producer action. Large artifacts are project-local/gitignored; no backup claimed.
