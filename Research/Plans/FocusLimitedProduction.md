# Focus: measured progression toward a limited production release

2026-09-29. Maintainer approved the bounded candidate and limited-production
milestone after clarification that 313 related training pairs are development-scale,
not production qualification. Owner: current NUIAK model-workflow worker.

## Current authorized tranche

One FDR-010 run against the frozen retention proposal
`8dd1a45090ed372157dbcd453cb3d77f770db4fb54cc0118a34141fdc2e2399a`:
313 training pairs, nine retention pairs, FDR-007 initialization, fresh AdamW,
50/50 native–Fixture sampling, 30 epochs maximum, 1,800-second cap, batch64,
lr0.0003, seed42, no augmentation. Retain minimum retention BCE among epochs
with18/18 classifications correct at0.85; no eligible epoch means no selected
checkpoint. No automatic second run, threshold sweep or final-challenge scoring.

Compare the selected checkpoint on the frozen24-frame real-screen benchmark and
the separate eight-frame Home/Photos/Settings regression. Reuse compatible retained
shipped/FDR-009 predictions and the existing inference/metric implementation;
never rename FDR-010 as FDR-009 to fit a hardcoded evaluator role. A report-local
adapter may bind a new explicit candidate identity while preserving old protocols.
Check exact membership, hashes, predictions, roles and preprocessing before reuse.
All exclusions and incomplete candidate sets remain explicit. Report baseline
backend differences, not export parity or directly comparable latency.

Legacy Photos compatibility: its original v1 approval predates the additive empty
`coverage.focusRoles` field. Actual member IDs, rows, pairs and input hashes match.
The report adapter may omit this field only when absent in the old v1 approval and
exactly empty in the fresh audit. Preserve originals and reject any nonempty or
other coverage difference; v2 role admissions remain exact.

Conditional export is for opt-in observer testing only. It requires eligible
retention, complete valid predictions, improved complete-frame unique selection
over both baselines on the24-frame set, no increase in its single-wrong selections,
and no regression in aggregate recall/false positives against shipped on either
benchmark or either Photos pair. These conservative test-artifact conditions are
not new production qualification thresholds. If unmet, retain results and return
one measured next-data/model assignment, without exporting a misleading candidate.
Passing permits existing CoreML export/parity/size checks and a default-off test
artifact; no shipped replacement, installation or autonomous control is authorized.

## Production acceptance contract: scope and remaining evidence

First target is an observer identifying active focus on settled approved Home,
Settings, Apple-app tab/content and Photos-button screens, with explicit unsupported
and ambiguous outcomes. Keyboard, overlays, nested navigation and OS-version drift
must have separately measured coverage before claiming support. Human boxes in the
current benchmark do not measure detector/OCR or end-to-end navigation performance.

Keep three distinct data lanes: training families; repeatedly used development
regression; untouched source-separated qualification. Do not split related recipes,
journeys or duplicate pixels across those lanes. Real benchmark members never enter
training. Native Fixture labels reduce annotation effort but do not prove OS transfer.

Production release continues to require the existing corpus/coverage/independence,
physical-transfer and model gates; this plan does not waive the documented6,000-pair
requirement or substitute nine retention pairs for qualification. Audit all existing
gates and map each to evidence before release. Where a product acceptance criterion
is unspecified, record it as unresolved—not a pass or an invented numeric target.
Measure per-stratum recall/false positives and complete-frame unique/wrong/no/multiple
focus, then deployed CoreML parity/size and end-to-end permitted-task success,
wrong actions, safe stops and recovery. Navigation authority remains separately gated.

Earliest deliverable is a measured candidate decision from this run, not a claim of
production readiness. Next collection is ranked by actual failures: automated native
Fixture variation plus minimal real-source checks. No speculative volume campaign,
new human annotation batch, hardware capture or tool installation in this tranche.
