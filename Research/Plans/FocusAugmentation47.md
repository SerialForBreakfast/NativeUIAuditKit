# FOCUS-AUGMENTATION-47 — approved training comparison

Maintainer approved the proposed tranche after46. Owner: Codex. Use existing
admitted2,000training/500exposed development frames, source initializer, seed42,
batch8,640px and one epoch. USB originals remain read-through; code, caches, weights
and compact outputs remain project-local. No new annotation/admission or producer
dependency. Two fixed-last runs, serialized MPS, total2GiB output budget. The existing
explicit no-time-limit amendment applies; track actual training updates and elapsed time.

- FSF003: translate=.05,scale=0. Random translation up to5%of model input dimensions.
- FSF004: translate=.05,scale=.20. Same translation plus isotropic scale0.8–1.2.
- Baseline: retained FSF001, otherwise identical one-epoch configuration.

Extend the current closed runner contract with optional augmentation-v1; omitted
field preserves exact zero-augmentation behavior. Only translation/scale are exposed;
rotation, flips, colors, mosaic and multi-scale remain unchanged. Validate real
Ultralytics transforms/box clipping and evaluation isolation before fitting. The actual
read-through dataset sets rect=False even though historical args.yaml records
rect=True: reason from the real caller rather than args alone.

Use the existing terminal500-frame evaluator, then replay46's30-image detail/position
diagnostic panel on both fixed checkpoints (all seven input variants: ordinary640,
ordinary1280,top/center/bottom,aligned±128;420inferences) and the same46real development
screens (92inferences). Keep.25operating/.001retained candidates/.7NMS/IoU.50; retain
false positives, known negatives and unknown geometry separately. Original500+30+
46are exposed development evidence, never independent final tests. No model promotion.

Completion: both scoped fits and fixed evaluations (or concrete execution blocker),
integration/transform tests, offline Swift checks, comparable exposure/timing receipts,
and prioritized next work based on ordinary accuracy AND alignment/scale robustness.

## Completed outcome

FSF003/004 both500/500synthetic exact screens; translation-only real localization
8/46with19known-unfocused detections, versus baseline1/46with46. Translation+scale
9/46but68known-unfocused detections. Tested640padding failures resolve, while native
family/reference and1280robustness gaps persist. Prefer FSF003 for the next diverse-data
comparison. Both fits,512follow-up passes, replay and repository tests complete.
See [handoff](../../reports/work/FOCUS-AUGMENTATION-47/handoff.md) for caveats and evidence.
