# SYN-12 — review to bounded training continuation

Completed: review, admission, encoding and one approved training comparison.
**FDR022 rejected: no eligible checkpoint. FDR021 remains preserved.**

| Outcome | Result |
|---|---|
| Software | Existing tools and saved-prediction validators passed; no implementation changes |
| Data |564native controls admitted after12-frame human sample acceptance; evaluation unchanged |
| Integration | Real local MPS encoding, three-cache join and trainer execution passed |
| Model | Comparison failed; no export, promotion or automatic retry |

- Artwork: user confirmed correct; immutable revision `20261001T155955Z-c9e06ad9`
  records five reviewed frames and46controls. Existing intake-audit validator
  passes4random+1exception samples, no pending selections or changed annotations.
  [Machine result](artwork-review-summary.json). Unselected frames remain pending;
  this is sample acceptance, not approval of every frame or training admission.
- Native3: user approved all three; saved revision `20261001T160553Z-6636ef68`
  validates three frames/14controls with no annotation changes. All three random
  selections and the overlapping exception selection are complete.
  [Machine result](native-review-summary.json). Palette4 was opened
  prefilled queue after confirming no editor remained running and passing Cocoa
  doctor with scoped GUI access. Editor session89116 remained running without errors.
- Startup: restricted Cocoa probe failed with pasteboard/HIService connection
  errors and native exit-6. Scoped GUI execution passed doctor using unchanged
  shared cache. No reinstall, dependency edit or platform fallback. Use the GUI
  execution context directly for subsequent launches.
- Palette4: revision20261001T160952Z-3347612e validates4frames/30controls; all three
  random and one exception selections complete without annotation changes.
  [Machine result](palette-review-summary.json). New sample review totals12frames/
  90controls, plus the earlier SYN-06five-frame/20control acceptance.
- Exact admission: [evidence](admission-evidence.md), [decision](admission.json).
  Existing native assembly CLI exits0, adds exactly564controls to986baseline;
  resulting1550training members preserve333evaluation rows byte-equivalently as
  parsed records. Weight mass1.0,196human controls retain mass0.2. Reused crop
  receipts; no recrop.764blocked candidates and52upstream source-quarantined
  controls remain excluded. Native candidate ledger retains pre-admission
  dispositions; admitted samples and encoding plan are the admission result.
- Assembly: `artifacts/admitted-assembly/focus_dataset_manifest.json`, SHA256
  `df9d0c1d754685f6cc4443caebb4de8ad8ad7687fb0640e49d55053d9ebe5d9e`.
- Encoding proposal: exact564new crops, fixed32-image batches,300second cooperative
  budget and16MiBfeature-cache cap, local MPS/resident frozen encoder. Reuse986
  baseline features. No download, training, export or promotion in encoding scope.
  Output `artifacts/encoded`; explicit approval and completed execution below.
- Encoding protocol preparation exits0: `artifacts/encoding-protocol/protocol.json`
  binds1550training/315development/18retention records and resident runtime. Its
  sole data blocker is `missing_native_feature_cache`; admission blockers are gone.
  Maintainer subsequently approved; cache-bound protocol prepared successfully.
- Training remains the planned fresh linear-head comparison: maximum1000updates/
  300seconds, same selector and0.85metric threshold; post-cache exact approval and
  experiment-log entry supplied for FDR-022 before dispatch, as recorded below.

## Approved encoding result

Maintainer approved the exact564/32/300seconds/16MiB encoding request. Recorded
authorization and protocol-bound approval; one invocation, exit0. Command wrapper
bounded total startup/revalidation/execution at600seconds; elapsed125.232seconds.
Actual encoder/import interval3.224seconds on MPS,564members,1,520,229bytecache;
unchanged backbone and tensor membership/shape/labels/finiteness verified by encoder.
Cache SHA25612836d5d7f5fb747e6448e742f374a4611118c127177c5808ae7142365515f76.
Current/driver allocation snapshots3,783,168/1,093,648,384bytes, not peak memory.
[Feature references](artifacts/encoded/features-reference.json), [log](encoding.log).
Post-cache protocol prepared with no data blockers. No export occurred.

## Approved FDR022 execution and comparison

User approved one bounded run. Actual preflight first returned configurationValid
true with only missing_run_approval (expected exit2); the subsequent exact approval
cleared that gate in the real execute path. No bypass or re-encoding from training.
Protocol2196c2c1285661373bfee5c27f1a549433a1aca3046424a4ff340747519d731c,
arm native-body-full-fit, output `NativeUITrainer/focus_ring_runs/fdr022-native-body`.
PID61890, start09:25:06PDT,153.074seconds total/31.217seconds model runtime, exit0;
1000updates, update-cap stop, fitPassed false, selectedUpdate null, no best.pt.
All40evaluation snapshots fail eligibility; complete-frame check fails39, other
early checks prevent the remaining one qualifying. Last checkpoint is diagnostic
only,4813bytes, SHA256a53eab12cc92f96593d68fb7efc64ecfcf9e966cd60553980e11038932a6f3dd.

| Fixed0.85measure | FDR021selected775 | FDR022terminal1000 (not eligible) |
|---|---:|---:|
| Focused hits |16/27|15/27|
| False positives |3/288|6/288|
| Unique-correct complete frames |12/14|10/14|
| No-focus frames |2|3|
| Multiple-focus frames |0|1|
| Retention correct |18/18|18/18|
| Artwork hits / false positives |2/12;3|2/12;6|
| Row hits / false positives |7/7;0|6/7;0|

Buttons3/3,tabs2/3,other2/2and their zero false positives are unchanged.18incomplete
frames remain unavailable. Selection BCE improves0.716423→0.674482but does not
override the decision gates. No alternative checkpoint was selected after failure.

Four fixed-threshold regressions: focused Settings row recorded-303 falls0.977271
→0.831170; unfocused Home-grid recorded-12 rises0.656952→0.861652; App Store search
recorded-1043 rises0.665913→0.970394; Home photos/frame-001 rises0.794380→0.925483.
Exact IDs and probabilities: [comparison.json](comparison.json).

Verification reused the retained comparison verifier's functions without executing
its historical write entrypoint. Replayed1,551,550training and13,653evaluation
predictions using existing metrics; verified all recorded metrics, exact evaluation
rows, identical initial predictions, eligibility/minimum-loss selection and absence
of best.pt.22runtime/assembly/cache references remain unchanged. FDR021best.pt hash
stillbc1b5978f1febbf86ba57ae51d13c8f0fb68ffa4107e303f2f6ccf57fb0c2ec8.
No code changes; prior software tests remain applicable, no claim of freshly rerun
Swift tests. Diff check passed. All evidence stays project-local.

## Decision and next assignment

The new synthetic data plus changed within-native weights did not improve this
frozen-feature/linear-head model. Good sampled labels and lower training loss do
not establish real-screen transfer. This experiment does not isolate whether
representation, context, procedural visual diversity or weighting caused failure.
Keep the corpus and receipts; do not discard reviewed data or relax0.85.

Proposed next bounded tranche: inspect retained embeddings/crop context and native
versus human weighting/error groups without new inference or training, then specify
one context or partial-backbone experiment. Do not repeat unchanged training or
request more annotation merely because this candidate failed. Any new model arm
requires its own approved configuration. TTR's existing varied-content request is
unchanged; no new peer action or model delivery is requested.

All assigned steps completed; outcome is a rejected development candidate, not an
unfinished training job. Source artifacts, reviews, baseline and failed run preserved.
Coordination: not applicable; no producer next-action change.
