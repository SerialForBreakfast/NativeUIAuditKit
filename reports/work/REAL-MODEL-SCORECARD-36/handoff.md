# Real model scorecard — October 2

## Decision

Prioritize finding the full control body before further isolated focus-classifier
tuning. On this retained corpus, the shipped detector misses more than half of the
reviewed focused targets. A better crop classifier cannot recover an absent box.
Keep native family diversification moving; compare full-screen and crop approaches
on the same source groups once the training inputs and bounded runner are ready.

## Measured results

One fixed production CLI pass: 46 real screenshots, 583 reviewed controls, explicit
tvOS, detector confidence 0.5, OCR disabled, shipped letterbox/NMS and bundled
FocusRing selection. Execution took 5.590 seconds, including subprocess/model loads;
this is not a controlled throughput benchmark. Model identities are in the report.

| Measure | Result |
|---|---:|
| Reviewed bodies localized at IoU .50 | 346 / 583 (59.3%) |
| Reviewed bodies localized at IoU .75 | 316 / 583 |
| Focused targets localized at IoU .50 | 21 / 46 (45.7%) |
| Exact type among localized controls with mapped roles | 265 / 320 |
| Correct final focus on explicitly complete frames | 4 / 7 |
| Remaining complete-frame failures: target body absent | 3 / 7 |

All seven complete frames are Settings variants; 31 screen labels do not mean 31
independent apps. The other 39 frames have useful reviewed boxes but no explicit
completeness confirmation in this frozen inventory. Predictions outside reviewed
boxes remain unreviewed—not automatic false positives. Focus-only tab/other roles
have no detector class mapping. These are reused development examples.

Spot inspection of `recorded-391` confirms the model finds the VoiceOver text but
misses its highlighted row body. This is a proposal failure before focus scoring.
The initial 3/7 report incorrectly penalized a selected duplicate row box. A
regression-tested scorer correction produces 4/7 from identical retained outputs;
the original report is preserved as superseded. This is a metric repair, not a model gain.

- [Canonical scorecard](scorecard-final/scorecard.md) and [machine evidence](scorecard-final/scorecard.json).
- [Original inference inputs](production/inputs.json), [execution receipt](production/execution.json).
- `production/scorecard.*` is superseded; `scorecard-verified` preserves the intermediate correction.

The bundled model is not FDR021 or paired-input FDR036. FDR021's historical 12/14
reviewed complete-screen result and FDR036's 500/500 synthetic result use different
inputs/models and cannot be substituted for this end-to-end baseline.

## Full-screen challenger prepared

Executable preflight exports the exact 46-image diagnostic membership, each reviewed
control's original geometry, focus state, role and 640-letterbox size. Only one body
is shorter than 16 pixels at that size; median height is 36.48 pixels. This does not
measure whether a subtle shadow remains visible. Full images preserve context and
relative scale, unlike independently resized crops.

Resident YOLO11n weights and tvOS trainer are pinned. Training remains a next step:
the current trainer lacks wall-time/output guards, its `--dry-run` actually trains,
and this real diagnostic membership is not a newly admitted training split. Keep
source/layout relatives grouped; ordinary focus-body truth and focus-only output
must not silently change the public element taxonomy. Compare oracle-box crop
performance separately from predicted-box end-to-end performance.

[Prepared inputs and prerequisites](preflight-verified/readiness.md) ·
[Full-screen manifest](preflight-verified/full-screen-preflight.json).

## Independent iOS diagnosis

Replayed retained Run013 outputs on 2,000 withheld screenshots, verifying label hashes
against the existing in-project source dataset. No repeated inference. Deterministic
maximum-cardinality matching at confidence .25 / IoU .50 separates body coverage from
type agreement. These are diagnostic counts, not a replacement AP calculation or the
historical score-ordered greedy confusion matrix.

- **Secondary buttons:** 292/341 localized, 0 correct type. CardDetail source explicitly
  captures secondary actions; preserve those labels. Test coarse button localization
  plus text/context role resolution before more flat-class tuning.
- **Page controls:** 0/600 localized. Half have a short side below 8 pixels at 640.
  This supports a resolution/geometry experiment, not relabeling them.
- **List rows:** 106/700 localized. **Image views:** 358/1,900. Prioritize unseen-layout
  coverage; high addon-family scores did not transfer to these withheld families.
- DS-G8 remains open; independent full-class coverage is still incomplete.

[Machine diagnosis and source hashes](preflight-verified/ios-diagnosis.json).

## Verification and outcome

- 32 focused Python checks passed: new scorers/preflight plus reference, coverage and
  recorded-comparison regressions. [Log](python-tests.log).
- Offline `swift build --skip-update` and `swift test --skip-update` passed:
  14 XCTest + 120 Swift Testing checks. [Build](swift-build.log), [tests](swift-test.log).
- CoreML used scoped host access for normal Apple framework operation; explicit
  outputs and configurable caches stayed project-local. About 2.2 MB of reports before
  final metadata, comfortably inside the 2 GiB envelope. No training run was included.
- One preflight attempt stopped at the generic harvest helper's symlink prohibition.
  Run013 already uses an in-project dataset link; the corrected reader verifies its
  exact known target and hashes, preserving strict harvest rules. Empty failed output
  remains `preflight/`.

Software: passed. Data: valid for the stated diagnostic use, training admission not
changed. Local production CLI integration: passed. Model release gate: not assessed;
real-world reliability remains insufficient. TTR coordination is documented separately
in [coordination](coordination.md).

## Next substantial tranche

1. Run one fixed proposal-recovery comparison on these real frames: shipped detection
   versus optional rectangle/OCR-assisted row candidates, with duplicate/ambiguous
   geometry accounting. Measure focused-target recall before classifier accuracy.
2. Implement the bounded full-screen training entrypoint and map the native family
   coverage request to published TTR source. Build locally; use complete synthetic
   groups and a declared training budget for the crop/full-screen comparison.
3. Advance the iOS coarse-role experiment using retained evidence, and specify the
   separate small-control resolution test. Avoid another unchanged 41-class run.

The scorecard/preparation tranche is complete for review. The next inference/training
experiment needs its stated scope; current source and data-use prerequisites are
listed above rather than treating TTR availability as a blocker for all local work.
