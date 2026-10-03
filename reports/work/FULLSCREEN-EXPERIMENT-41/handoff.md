# Full-screen focus experiment and iOS page-dot repair41

Status: **completed for review**. TTR coordination deferred by maintainer.

Longer training worsened this experiment. Preserve the one-epoch baseline and
address layout coverage before another full-screen training comparison.

| Same 500 synthetic screens | One epoch | Ten epochs |
| --- | ---: | ---: |
| Correct screens | 425 (85%) | 194 (38.8%) |
| Missed focused controls | 75 | 306 |
| False focus detections | 0 | 0 |
| Both endpoints correct / 250 pairs | 175 | 28 |
| Top / middle / bottom targets correct | 166 / 107 / 152 | 166 / 28 / 0 |

There were 231 newly failed screens and zero repaired screens.

## Measured outcomes

- Exact native26 full-scene admission:2,000training and500evaluation screens,
  configuration groups0–7and8–9 respectively; original USB pixels read directly.
- FSF001 one epoch:425/500exact screens,425true positives,0false positives,
  75misses. Group8:226/250; group9:199/250. Middle target:107/168correct,
  accounting for61of75misses. This is synthetic development evidence.
  Geometry audit confirms training controls are horizontal rows while both held-out
  configurations are vertical stacks. Focused-body aspect ratios span1.10–1.67in
  training; evaluation groups are1.58and1.79. Thus this is a useful layout/shape
  transfer check within one renderer, not merely unseen artwork on the same positions.
  Each screen has one focused control; zero-visible-focus and ambiguous/multiple-focus
  scenes are not covered by this measurement.
- FSF002: approved fixed10epochs on identical membership/initial weights/settings;
  maintainer removed time caps. Final checkpoint scored all500screens. Epoch-dependent
  learning-rate schedule follows the new duration; seed-pinned MPS is not claimed
  byte-deterministic.
- Failure diagnosis: at candidate confidence .001, the one-epoch model still
  localizes all500targets, versus342for the ten-epoch model. Matching bottom-target
  candidates drop166→24; middle median confidence drops.472→.022. Both models'
  original .25metrics replay exactly. This supports layout-dependent overfitting,
  rather than a modest cutoff-only repair, but does not prove the exact learned cue.
  The diagnostic cutoff is not a newly selected operating threshold.
- iOS:666replacement training members rendered and verified,266MediaCardGrid and
  400ProgressActivity. Page-dot boxes now describe intrinsic dot groups rather than
  full-width rows. Existing exporter produced666replacement YOLO label files, with
  all8,958supported labels checked against annotations. Original corpus retained.

## Evidence and timing

- `admission.json`, `run.json`, `run-long.json`, `time-authority.json`: exact scope.
- `run/training-complete.json`: FSF001 fit238.57seconds, PID50482. Its original
  combined300second receipt is partial because scoring outlasted the old cap.
- `evaluation/receipt.json`, `evaluation/terminal-evaluation.json`: completed
  evaluation-only continuation, PID50915,77.427seconds wall/43.550seconds scoring.
- `baseline-analysis.json`: prediction replay and per-group/target breakdown.
- `run-long/`: FSF002 child PID52128,parent51921; completed exit0. Fit2,392.988s,
  evaluation45.016s, whole child2,473.141s, peak observed outputs47,483,384bytes.
  Final checkpointSHA256 `efa5e0588c903d4c8aa27cee135640815e6fa88be87596cb865092ceed434d1d`.
  Training CSV validation columns are unused placeholders under terminal-only
  scoring; `terminal-evaluation.json` is the actual model-quality measurement.
- `long-analysis.json`, `confidence-diagnosis/summary.json`: final replay and
  same-checkpoint confidence diagnosis; PID54674,84.707s for1,000image inferences
  after byte verification. Full per-image candidates retained locally.
- `page-recipes.json`, `page-export.json`, `page-qa.json`, `page-corpus-patch.json`:
  sealed old membership,1,333exported files/130,162,658bytes,666verified images and
  annotations, no duplicate pixel groups. iOS26.5(Build23F77),159.50seconds rendering.
- `NativeUITrainer/yolo_page_dot_patch_v2/`: image links and replacement labels;
  no second pixel copy, training payloads gitignored.

The repaired corpus is a new current-runtime rendering, not a reconstruction of
historical OS pixels. Its receipt records the actual OS; legacy sidecar OS strings
remain unknown. Validation/test membership remains unchanged.

## Verification

25runner tests,10page repair/export tests,4metric replay tests pass. Offline Swift
build/test passed (14XCTest+120SwiftTesting); native666member capture test passed.
Both500frame evaluations replay; exact membership and frozen checkpoint hashes
are retained. `git diff --check` passes. Original run timeout remains recorded.

## Independent acceptance states

- Software: verified; exact membership, immutable originals, terminal-only scoring,
  approved no-deadline override, output cap and export checks exercised.
- Data: full-scene membership admitted;666member replacement patch verified.
  Full iOS corpus integration/new validation coverage remains future work.
- Integration: local Python training and native iOS generation exercised. TTR
  runtime integration is outside this tranche.
- Model: both experiments measured; FSF002 improvement gate failed. Neither
  establishes real-app accuracy or a release candidate.

## Next substantial tranche

1. Test the fixed one-epoch full-screen baseline on retained real-app development
   inventory; compare focused-body localization with the shipped detector on
   identical frames. Keep partial-label limitations explicit.
2. Combine those failures with the measured layout gap: generate native focus
   examples across horizontal/vertical positions and control families, especially
   wide Settings rows, tabs and Home icons. Reserve groups before training and
   retain existing evaluation roles. New capture/admission requires its scoped assignment.
3. Integrate the666member iOS replacement patch into a new training version and
   decide representative validation coverage before an iOS training comparison.

New inference/training scope and any new data-use decision should be recorded in
the next assigned experiment. CoreML delivery follows measured transfer evidence.
