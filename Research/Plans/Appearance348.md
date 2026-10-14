# FOCUS348 — train against measured appearance failures

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK.

FOCUS347 confirms gamma sensitivity through source images and standard preprocessing.
Gamma 1.5 loses 519 authored successes. Detail-only gamma loses 495.
This evidence supports a controlled augmentation test, not a new architecture.

## Fixed comparison

- Initialize both arms from FOCUS329.
- Use 10 epochs, seed 42, learning rate 0.0001, and batch size 16.
- Use 2 CPU threads and 1,800 s per training job.
- Limit each job to 2 GiB of outputs.
- Preserve all 1,820 original training views and their verified detail crops.
- Reuse the 1,200 approved authored training pairs and their label-matched schedule.
- Give the control unchanged auxiliary images.
- Give the candidate gamma 1.5 auxiliary images from original source pixels.
- Use auxiliary weight 0.25 and preservation weight 1 for both arms.
- Preserve original margins on previously correct training examples.
- Train only the existing detail filters and correction layers.
- Keep the whole-frame branch, geometry, thresholds, and data roles fixed.
- Use final weights. Do not select epochs from evaluation results.

The primary loss still sees every original view in both arms.
The candidate's auxiliary views use standard crop selection after the source transformation.
Record crop selection changes separately. Do not describe these changes as fixed-crop augmentation.
No native development image enters training.

## Evaluation and acceptance

Register 35 measured comparison jobs after both checkpoints complete.
Compare original views, 7 retained sets in 5 jobs, and 20 appearance conditions.
Add 3 jobs for retained identical neighbors and placeholder controls.
Add 6 jobs for the existing disturbance strengths in both frame orders.
These jobs restore the full previous-success suite. They do not introduce a new parameter sweep.
Each diagnostic uses 800 s, 100 MB, and 1 attempt.
Compare both arms with FOCUS329 and with each other.
Report false changes, missed changes, abstentions, coverage, gains, and lost successes.
Require target improvement with no lost previous successes before recommending replacement.
Authored training robustness does not prove native transfer.
Preserve native development uncertainty and incomplete theme coverage.

## Queue review

The remaining queue has 25 placeholder experiments and 18 experiments with missing requirements.
Do not remove their requirements to make the queue appear ready.
Preserve immutable specifications. Register measured successors when the required inputs exist.
Treat the 26 comparisons as model evaluation, not 26 new scientific discoveries.
Track ready execution time and completed decisions alongside job counts.
Do not repeat completed jobs to keep the worker busy.
