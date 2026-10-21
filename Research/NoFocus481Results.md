# NOFOCUS481 — Repair the no-focus review

## Decision

Use the existing development-capture validator for the retained no-focus frames.
The previous review incorrectly calls a validator for focused control captures.
Its `controls_version` failure does not require another capture.
Keep the original failed capture and review unchanged.

## Verified evidence

- The original restoration receipts pass the strict review checks.
- The compatible validator accepts the retained frames with their existing development roles.
- The 2 profile frames have identical pixels. The validator preserves both events in 1 image record.
- The input plan remains ineligible for training. This review does not admit labels for training.
- All 9 successor specifications pass admission checks and receive exact approval.
- All 18 focused tests pass. Tests cover failed restoration, unexpected focus, changed sources, and unsafe fallback decisions.
- Existing Swift validation remains applicable. This change does not modify Swift code or active trainer imports.

The new adapter has a separate module. The running iOS graph keeps its pinned sources.
The runner executes the review before its 8 dependent comparisons.
Queue completion remains required. Local validation does not establish a model improvement.

## Independent reserve

B405-256 adds 4 T66 comparisons on completed button, row, tab, and decoration reports.
Each comparison uses fixed high-first fallback against high-confidence selection on identical scores.
Report Standard first. Report optional HCF separately.
Require gains without lost successes or new wrong selections before recommending further qualification.
Preserve no-focus limitations until the separate no-focus comparisons finish.

These jobs reuse verified outputs. They require no training, inference, or capture.
Each job has an 800 s limit and a 100 MB output limit.
The earlier T66 button comparison takes 0.22 s. These are useful diagnostics, not overnight training.

## Rehearsal and queue snapshot

IOS480 control training remains active at this check. No matched rehearsal result is available yet.
The mixed fit remains pending. Its scoring and reports depend on the training results.
Across these 3 campaigns, 1 job runs, 6 jobs are pending, and 37 jobs await dependencies or conditions.
The pending jobs are the mixed fit, the no-focus review, and 4 cached comparisons.
The runner remains continuous and reports no error. No restart occurs.

## Next decision

Review both iOS arms against Run013, the native-only candidate, and each other on the same 6 conditions.
Reject lost previous successes. Do not promote a model from training diagnostics.
Then review the no-focus and fallback results together before choosing another correction.

## Local evidence

- `reports/work/NOFOCUS481/validation.json`
- `reports/work/NOFOCUS481/preflight.json`
- `reports/work/NOFOCUS481/compiled.json`
- `reports/work/NOFOCUS481/admission.json`
- `Research/Experiments/batches/B405-256.json`
- `reports/work/REHEARSAL480/qualified/compiled.json`

Raw receipts and capture records remain local. Standard behavior and shipped models remain unchanged.

## Subsequent rehearsal update

The iOS control arm completes its retained comparisons against Run013.
It gains 40 detections and loses 47 previous detections. The replacement gate rejects it.
The mixed-data fit remains active. Its matched comparison is still pending.
These are inspected development results, not release qualification.

The shared trainer emits the historical message `Train HCF full-screen detector` for iOS training.
The dashboard now maps that exact message to `Train UI element detector` in its display code.
All 7 dashboard description tests pass, including preservation of the original event.
The read-only companion on port 8766 now serves the corrected display code.
Its 12 display and transport tests pass. A live HTTP check confirms the correction.
The experiment runner keeps process 17481 and continues `ios480-mixed-train` during the companion reload.
The active trainer, raw progress events, and source pins remain unchanged.

The mixed-data results remain pending at this review. The no-focus review and 4 cached comparisons remain approved and pending.
Do not choose another training correction before the matched report completes.
The approved graph already includes scoring, regression diagnostics, and terminal comparisons.
