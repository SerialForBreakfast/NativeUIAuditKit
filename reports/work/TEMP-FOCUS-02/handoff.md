# Settings brightness and before/after spike — October 1, 2026

**Decision:** pursue a Settings-scoped visual check; reject a universal brightness
rule and reject replacing FDR021 with this hybrid. The simple rule matches the
existing model on these Settings examples, not a measured model improvement.
The assigned retained-evidence tranche is complete; genuine transition evaluation
remains blocked on reviewed endpoints, not on implementing another neural model.

| Outcome | Result |
| --- | --- |
| Software | Fixed-rule CLI integrated with existing selection metrics;39 Python tests, offline Swift build and134 Swift tests pass |
| Data | Existing exposed development/retention and static training pairs only; no new admission |
| Integration |48 corrected recipe bindings and96 PNG hashes verified; screenshot-time correlation still unavailable; no live Settings recognizer/actuation qualification |
| Model | No new model execution, encoding, training, export or promotion; FDR021 preserved |

## Results that answer the immediate questions

The frozen policy uses production256 crops, center192 body proxy, encoded-RGB
luma>=0.60 and bright-neutral fraction>=0.45. This is a diagnostic rule, not a
calibrated focus probability. No threshold search or after-results tuning occurred.

| Same315 development controls /14 eligible complete frames | Focused hits /27 | False positives /288 | Unique-correct frames | No selection | Multiple selections |
| --- | ---: | ---: | ---: | ---: | ---: |
| Retained FDR021 |16|3|12|2|0|
| Brightness everywhere |19|58|12|0|2|
| Brightness only in known Settings families, FDR021 elsewhere |16|3|12|2|0|
| Require both brightness and model positive |14|0|11|3|0|

All four retain18/18 on the separate retention controls. Another18 frames are
explicitly unavailable under the existing completeness/settlement policy, not
silently counted as successes. Binary-rule outputs use existing confusion/frame
counts; their BCE or apparent probability confidence is not a meaningful comparison.

**Settings-specific:**91 reviewed development controls across Settings,
accessibility, app settings and VoiceOver settings:9 positives/82 negatives, all
correct for both brightness and FDR021. With18retention controls, this is109/109
control classifications, not109 independent screens. Settings identity and boxes
are provided by retained annotations here. We did NOT build or qualify an app/
screen recognizer, detector-box pipeline, or general Settings accuracy claim.

**Before/after:** all9native same-control Settings pairs brighten on focus; luma
increase0.639–0.750. The fixed0.08delta recognizes all9arrivals. Model plus delta
also recognizes9/9, equal to the model alone on those positive endpoints. Across
112retained Fixture same-control pairs:54expected arrivals,1opposite-direction
signal,57unknown. Reverse-direction and identical-image no-op probes are retained
in the report. These pairs were constructed from known states, not genuine recorded
presses; they do not measure navigation verification or image matching.

**White artwork counterexample:** on the received48pairs/96crops, brightness
calls all96focused:48TP/48FP. All48matched luma changes fall below the delta rule's
decision threshold. Retained FDR021 scores on those exact crops are32TP/40TN/8FP/
16FN. Thus brightness alone cannot solve this artwork gap, even with both images.

**Small-image sensitivity:**557crop summaries took1.86seconds in the first pass,
including local reads/decode, not end-to-end TTR latency. Downsampling the192body
to16or32 changes7binary brightness decisions;64changes1;192changes0. Mean luma
barely changes, but thresholded white-pixel fractions do. Do not assume tiny-image
mean agreement proves preservation of subtle highlights. No downsample size was
selected for deployment.

## Genuine recording audit and exact remaining dependency

Re-ran the existing recording analyzer on hash-verified Office trial02 events:
166actions,14pass conservative association/timing checks. Joined accepted model-
protocol annotations by exact encoded image hash:39reviewed image identities,
11actions with a reviewed pre-frame,11with a reviewed settled post-frame,
**zero timing-valid actions with both reviewed endpoints**. This audits the admitted
model-protocol scope, not every unadmitted edit elsewhere. Full per-action reasons
are retained; no action was silently excluded or labeled from command intent.

Next useful input is paired endpoint review of retained timing-valid Settings
actions, with actual focused control in both frames and unchanged-screen/motion
checks. First resolve the retained files and prepare missing endpoints, reusing
the already-reviewed side; do not request a new recording by default. A runtime
Settings context gate and visual control correspondence remain separate proof
requirements. Until then, genuine transition accuracy is unavailable.

## Artwork evidence repair

Copied/verified named correction archive106,207bytes,
SHA256`5e3ab434a0e554499cac70b3ae5558eb1dd34f122e22f0adc9e1514ede3a4d02`;
17indexed files,32tar entries,554,508expanded bytes. No included producer code run.
Verified all48normalized recipe hashes against retained originals, preserved earlier
raw hash references, compared every other pair field unchanged, verified96PNGhashes.
Correction is retained as a separate overlay; original archive/index unchanged.
Host before/frame/after timestamps were explicitly not recorded, so training remains
unadmitted. This tranche's authorization does not substitute for sampled acceptance
or missing source evidence. No light-artwork retraining was launched.

## Reproduction and evidence

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.build/tmp" PYTHONPATH=scripts \
.venv-yolo/bin/python scripts/focus_brightness_spike.py \
 --protocol reports/work/FOCUS-VISUAL-05/artifacts/protocol-v2/protocol.json \
 --baseline NativeUITrainer/focus_ring_runs/fdr021-reviewed-contrast/experiment-result.json \
 --growth reports/work/FOCUS-GROWTH-01/geometry-analysis.json \
 --output reports/work/TEMP-FOCUS-02/artifacts/REPLAY-NEW
```

- [Fixed policy and complete results](artifacts/brightness-final/result.json):333evaluation controls,557hashed production crops; actual FDR021 selected checkpoint775, baseline counts reproduced.
- [Full-frame examples](artifacts/supplement/review.md): deterministic Settings and false-positive cases, not new human acceptance.
- [Artwork probe](artifacts/supplement/artwork.json), [journey inventory](artifacts/journey-audit.json), [correction audit](artifacts/correction-audit.json).
- `audit_evidence.py` uses existing safe receiver/member checks and action analyzer; `supplement.py` uses the same fixed feature implementation.
- `python-tests-final.log`:39tests pass. Initial test command named a nonexistent recording-audit module; failed log retained, corrected to existing test module. No source fix or scientific retry involved.
- `swift-build.log`:offline build passes,1.63s, no warnings. `swift-test.log`:14XCTest+120SwiftTesting pass. No model runtime changes.

No unchanged head retraining, threshold sweep, source reassignment, model replacement,
protected-test access or new device operation. The broader diverse-source UI corpus
remains deferred. Remaining temporal work is recorded in Tasks.md, not falsely closed.
