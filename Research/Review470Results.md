# REVIEW470 — Fallback and geometry results

All 20 diagnostics complete. No job fails.

## Standard result

With the fixed candidate crop classifier, baseline-first detector fallback increases correct selections from 58 to 60 across 91 inspected development events.
It loses no previous successes and adds no wrong selections. All 3 no-focus abstentions remain correct.
The retained wrong selection remains wrong. This rule does not repair a unique but incorrect baseline selection.
The 2 gains occur in row-top and edge-clearance conditions.
These are development results, not release qualification. HCF remains a separate optional comparison.

## Geometry result

| Condition | Old matched controls | New matched controls | Total controls |
| --- | ---: | ---: | ---: |
| Row-bottom | 94 | 96 | 96 |
| Row-top | 88 | 96 | 96 |
| Edge-clearance | 1 | 8 | 32 |
| Small-decoration | 3 | 24 | 32 |

These counts include paired profiles and repeated controls. They are not independent sample counts.
The bottom-row losses persist despite improved proposal coverage. Crop selection needs a separate correction.
All 3 lost bottom-row cases also fail known-box selection under the candidate classifier.
Several unfocused controls receive high scores. Box geometry alone does not explain these losses.
Do not use these development offsets for training.

## CROP471 next experiment

Measure the expanded detector on admitted training-only frames through T88.
Verify unchanged production crops through T91 before training.
Replace only uniquely matched native crop boxes with measured proposals. Keep exposure and development pixels fixed.
Use the reusable training graph for 1 fit, 17 retained scoring conditions, and complete comparison reports.
The fit uses 30 epochs, seed 371, fixed-last selection, 1 attempt, 1,800 s, and 2 GiB.
The previous comparable fit takes 28.1 min. Preparation and scoring add time that is not yet estimated.
This is useful longer work, but it does not fill an entire night.

Keep the known Standard tab loss and consumer failures in the review. No model replaces Standard or iOS automatically.
All 5 preparation jobs pass. Independent review verifies 53 unchanged crops by decoded pixels.
Both arms preserve 8,352 rows, including 7,200 training rows. Development rows remain identical.
The fit now has approval. The runner executes it without a restart.
At handoff, training runs. The batch has 5 completed preparation jobs and 49 dependent jobs.
The approved graph contains 26 jobs. Another 24 jobs compare known-box and full-screen scoring across 12 conditions.
Those jobs preserve frozen DETECTOR469R boxes. A combined full-screen decision still needs binding after the trained model exists.

## TTR schema status

Sillycon-TTR replies through message 1018.
The received native review package remains preserved. Storage receipt is complete; consumer admission is not.
The existing importer expects native-control-admission-v1, not ttr_native_interruption_review.
Sillycon-TTR confirms normalized top-left xywh coordinates. The legacy xyxy attribute describes the original source encoding.
An immutable revised manifest still needs explicit encoding and scoped body/class completeness.
Maximum-mini-NUIAK supplies the importer contract and identifies the development-only conversion requirement.
The contract publication passes readback. Coordinator message 1023 records storage, not confirmed peer delivery.
Follow-up review reads replies 1022 and 1026 with the verified history request fields.
The prior failure comes from unsupported request fields, not unavailable TTR history.
Both metadata deliveries pass exact transfer checks. No images are copied again.
Revision 2 preserves 12 events, 7 image hashes, and 1 group. All 45 objects pass coordinate consistency checks.
Original image and sidecar hashes match. Covered controls retain unknown focus.
Classes remain unreviewed. Capture profiles remain unavailable.
The separate review adapter and class review remain required. Training admission remains false.
Requested underlay focus, observed overlay focus, and unavailable underlay focus must remain separate fields.
One authored layout cannot establish independent coverage or training admission.

## Evidence

Fallback: `reports/work/research-queue/jobs/supplemental470-*/attempts/1/out/benchmark_summary.json`.
Geometry: `reports/work/research-queue/jobs/geometry470-*/attempts/1/out/benchmark_summary.json`.
Next graph: `reports/work/CROP471/graph/compiled.json`.
