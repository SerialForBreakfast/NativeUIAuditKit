# FOCUS327: train the detail filters

Maximum-mini-NUIAK owns this approved experiment. It changes no TTR runtime or production model.

## Question and fixed comparison

Can trained detail filters improve decisions that fixed filters cannot separate?
Reuse all FOCUS326 independent images, training roles, weights, and sample order.
Keep FOCUS325-average as initialization. Reuse FOCUS326-independent as the completed control.
Keep the whole-frame model and geometry weights unchanged.
Use original-resolution detail crops with the existing 2-window method.

## Execution

1. Verify retained manifests, image hashes, training views, labels, weights, and cached feature agreement.
2. Check gradients on 32 balanced training examples. Train a discarded probe for 30 epochs.
3. If the probe reduces loss with finite gradients, start 1 fresh candidate.
4. Train the detail filters and output layers for 30 epochs.
5. Compare the fixed last checkpoint against the retained control and previous models.

The learning rate is 0.0001. Batch size is 16. The seed is 42.
Use 2 CPU threads and auxiliary weight 0.25. Keep thresholds at 0.15 and 0.85.
The output limit is 2 GiB. The memory limit is 8 GiB. The standing approval removes the time limit.
Keep outputs in `reports/work/FOCUS-327`. Do not regenerate images or repeat control training.
Record inputs and source hashes before training. Do not use evaluation scores to select checkpoints.

## Tests and acceptance

Test exact agreement between indexed and expanded auxiliary inputs. Reject invalid indices and incompatible shapes.
Verify unchanged whole-frame and geometry weights. Verify checkpoint reload agreement.
Compare native, reversed, replay, nuisance, tiny-control, and placeholder cases.
Report lost previous successes, new successes, false changes, missed changes, and abstentions separately.
Improvement requires native gains without lost previous successes or increased false changes.
Training improvements alone do not establish native performance. These retained checks are development evidence, not untouched evaluation.
Run focused tests and 1 integrated offline Swift build/test pass.

## TTR feedback

Read the reported TTR updates before selecting new producer work. Record missing delivery separately from model work.
Use existing source reviews when the checkout has no new features.
Return measured failures with model hashes and unchanged thresholds. Ask for missing observations, not another broad corpus.
Treat proposed worker changes as suggestions until the maintainer approves them.
Do not use model confidence as a focus label. Keep native observations and authored states distinct.
