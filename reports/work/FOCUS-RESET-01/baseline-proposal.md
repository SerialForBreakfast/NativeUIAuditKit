# One pretrained frozen-feature comparison — approved as FDR-015

Purpose: compare broad ImageNet features against the existing narrowly initialized
FocusRing lineage without another full-backbone optimization run. Not production
training, a promise of improvement, or a single-variable pretraining ablation:
backbone architecture and required normalization also differ.

## Exact proposed inputs and method

- Official torchvision `MobileNet_V3_Small_Weights.IMAGENET1K_V1`, documented9.8MB.
  Source: https://download.pytorch.org/models/mobilenet_v3_small-047dcff4.pth
  Store only under `NativeUITrainer/pretrained/` after explicit approval; verify
  the publisher's hash prefix, record full SHA256 and exact bytes, load weights-only.
  No training images or screenshots leave the machine.
- Existing `.venv-yolo` imports verified in2.13seconds: PyTorch2.13.0,
  torchvision0.28.0. `pretrained-runtime-probe.json` records the bounded import.
  Official weights subsequently downloaded and verified; receipt in
  `pretrained-weight-receipt.json`. The resident export environment lacks
  torchvision; do not install into it. No dependency repair is required for the
  verified existing environment. Pin backend before execution; no silent fallback.
- Exact FDR014363training pairs,9retention pairs,453real selection crops and64
  exclusions. Preserve source/pair membership and appearance weights. The only
  already admitted native OS training is40Settings pairs; this remains a limitation.
  No Photos, Home or App Store evaluation member moves into training.
- Reuse retained16%-expanded256×256production crops. Preserve the whole crop, not
  torchvision's default224center crop that would remove border context. Normalize
  RGB with the published ImageNet mean/std. Record this deliberate input adaptation;
  do not call it a production preprocessing change or exact default-weight recipe.
- Freeze pretrained feature extractor and batch-normalization statistics; extract
  features once, then train one linear binary head. No backbone updates, augmentation,
  grid search, threshold sweep or external model service.
- Proposed fixed head budget:30epochs, batch64, AdamW lr0.0003, seed42, existing
  appearance-balanced sampler,1800second cap. Same exact real/retention selection
  rules; no eligible epoch means no selected model. Keep initial and every epoch's
  scores, ranking and strict/runtime-style outcomes. Normalize any learned features
  using training members only; never fit on selection data.
- Integrate the explicit experimental representation in the existing trainer,
  with tests proving frozen parameters/BN, normalization, exact membership and
  unchanged legacy behavior. Record the run in ExperimentLog before execution.

## Acceptance and stopping

Judge retained fixed-threshold correctness/wrong decisions and ranking against
FDR014 on identical supported inputs. Report backend/version differences; no latency
or CoreML parity claim. Do not pick a post-hoc favorable snapshot as an eligible
checkpoint. A failed baseline is still evidence for a representation/data decision,
but must not trigger another automatic run or a lower threshold.

If representation improves ranking but confidence remains unreliable, separately
design grouped calibration. If it does not beat simple geometric baselines, investigate
target/context features and actual matched contrast coverage before additional scale.

Approval received for the named weights; frozen-feature adapter and tests implemented.
FDR-015 execution evidence and its final outcome live in `../FDR-015/`.
This proposal describes the fixed experiment, not a claim of model qualification.

Reference: [official weights and preprocessing](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.mobilenet_v3_small.html).
