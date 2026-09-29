# Focus development test cycle — 2026-09-29

**Tranche incomplete: benchmark delivered; new training/export blocked by corpus readiness.**

| Outcome | Result |
|---|---|
| Software | Existing QA/evaluator exercised on real data;14 focused tests pass. No implementation changes or new Swift build required. |
| Data |24 frames/249 crops verified;202 settled candidate crops supported. No new training admission. |
| Integration | Production crop and CoreML/PyTorch CPU comparison complete. No new TTR model package delivered. |
| Model gate | Not passed. FDR-009 loses recall and unique selection despite fewer false positives. Shipped model unchanged. |

## Results at the unchanged0.85 threshold

Both models produced249/249 scores, zero failed predictions, three completed
comparisons with successful postflight validation. Metrics use the same existing
implementation. CoreML CPU and PyTorch CPU differ; this is not export parity or a
latency comparison. Human boxes are supplied: detector recall is not measured.

| Settled candidate metric | Shipped | FDR-009 epoch3 |
|---|---:|---:|
| Focused controls found /19 |8|4|
| Recall |42.1%|21.1%|
| Misses |11|15|
| False positives /183 unfocused |30|8|
| Unique-correct complete frames /13 |3|2|
| No focus /13 |5|9|
| Multiple focus /13 |5|2|
| Single wrong selection /13 |0|0|

FDR-009 is more conservative, not a better navigation model. Neither result
supports reliable autonomous focus selection. High aggregate accuracy would hide
the missed focused controls and negative-heavy class balance.

Support:97 collectionItem crops (8 positives),60 listRows (6),24 tabItems (3),
20 otherFocusable rows (2),1 searchField (0). FDR-009 recalls2/8 collection items,
2/6 listRows,0/3 tabs and0/2 otherFocusable rows. The original Photos benchmark
remains separate; these24 frames add no Photos positives.

## Accounting and review exceptions

All original annotations remain immutable. Of249 controls:202 settled candidates,
18 candidates on settlement-disputed frames656/676/687,16 auxiliary annotations,
13 unresolved controls. No formally admitted matched pairs. Duplicate sensitivity
is included in summary.json; repeated screens are not independent source groups.

Complete-frame metrics support13/24 frames. Eleven remain unavailable: three
settlement-disputed tabs,605 incomplete/unresolved, and seven batch03 contexts with
unknown/incomplete coverage. Frame306 is the sole batch03 complete-frame member.
All supported crop classifications remain usable even without frame completeness.

Batch03 QA passed78/78 with no hard integrity issues. Visual semantic review found
1087/1105 contain app cards, five per frame labeled searchField, all six per frame
unfocused, while Fubo appears enlarged/focused. All12 controls are unresolved in
the analysis partition, not silently corrected. Frame1043 omits keyboard keys;
no per-letter manual review requested. These exceptions do not block other frames.

## Training blocker, with actual checks

The frozen FDR-009 corpus still has273 training pairs plus9 retention pairs.
971 unique referenced files passed byte and decoded-pixel verification. The new
dock-repair manifests contain4+8 pairs;24/24 production crops replay identically,
with no exact crop-pixel matches to the old corpus. Both manifests remain test-only,
development partition, with no trainingApproval. They cover only collectionItem,
use reference-baseline negatives and do not fill native Photos/Settings/tab gaps.

Actual trainer preflight on the nine-item dataset exits2: zero train/validation
pairs, missing required partition, underfilled quota, runtime_crop_parity_required.
That is the generic full-data entrypoint's rejection, not a failure of the24-crop
production replay or a prescribed quota for a separately approved small experiment.
Its default random-init/augmentation config is NOT a proposed new run.

No FDR-010 allocated; no training, export, promotion or challenge scoring performed.
The maintainer authorized a justified new candidate; permission to train is not the
missing piece. The missing piece is an eligible, gap-addressing corpus. Repeating
273 unchanged pairs would not fulfill the assigned plan. Test-only dock data is not
quietly relabeled into training. A narrow admission decision alone would still
not establish that these12 pairs address the measured failures.

## Exact next assignment

1. Qualify the already-received clean Fixture canvas on the specified Simulator
   under separate deployment/capture authority; use the existing bounded4/24
   checklist. This is a integration check, not a training-volume target.
2. Prioritize native-looking white/gray buttons and wide Settings rows, tabs with
   selected-but-unfocused parent appearance, then artwork tiles with surrounding
   competitors. Record target-focused and target-unfocused/competitor-focused
   states, per-state native bounds, identity, settled brackets and full coverage.
   Existing first collection targets12 artwork,6 button,6 row pairs remain targets,
   not qualification thresholds; add tab cases based on this measured0/3 result.
3. Freeze new training-only recipe/source groups outside both human sessions and
   protected evaluation, validate raw pixels/crops, then bind the explicit
   training admission and one-run configuration. Do not require another large
   human annotation batch or every keyboard letter before this can progress.
4. Execute one logged candidate, retaining the retention floor and checkpoint
   rule; evaluate this frozen benchmark plus the existing Photos regression.
5. Only a justified candidate proceeds to CoreML parity/size checks and an opt-in
   TTR observer package with artifact hash, threshold, preprocessing, known gaps,
   rollback identity and default-off loading. No autonomous-control promotion.

## Evidence and verification

- batch01/02/03-protocol.json: frozen models, runtime, code, input hashes and roles.
- batch03-qa/handoff.json: production QA; audit/review.html: visual review sheet.
- batch01/02/03-comparison/comparison.json: complete predictions and backend receipts.
- summary.json: reproducible aggregation through existing metrics, exact exclusions.
- batch01/02/03-errors/index.json:68 numbered context/crop error sheets (12/31/25).
- corpus-audit.json: corpus identity, verified files and new-pair replay/dispositions.
- new-data-preflight.log: actual exit2 readiness rejection, no training side effects.
- evaluator-tests.log:14 tests pass, including intentional failed-score receipts.

Execution used the resident focus-export-01 Python, PYTHONDONTWRITEBYTECODE=1
and project-local TMPDIR. Existing human_review_qa CLI exited0; three
human_focus_evaluation freeze/run operations completed, retained render replay
completed for all three; unittest discover test_human_focus*.py exited0.
git diff --check passed. Bulky PNG evidence is gitignored and retained locally.
TTR coordination consequence published/read back with unrelated entries preserved;
see coordination.md. Peer acknowledgment is not claimed.

Initial batch01-admission.json omitted diagnostic flags and was rejected before
freezing/inference. Preserved as failed preparation evidence; all executed protocols
bind corrected *-admission-v2.json. This did not consume or repeat a model run.

No source-code changes. No background processes remain owned by this tranche at
handoff. Original review files, model weights and training data are preserved.
Resume condition: separately scoped Fixture deployment/capture and a verified new
training corpus/admission; then the already requested model cycle can continue.
