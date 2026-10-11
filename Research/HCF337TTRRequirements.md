# HCF337 — data requirements for TTR synthetic templates and review

Owner: Maximum-mini-NUIAK (training requirements and evaluation).
Producer tooling owner: Sillycon-TTR.
Request: `ttr-synthetic-review-needs-v2-20261010`, forwarded as
`chat-forward-cb7bea7be079dec7690a9da37c1fdb473036a9d372e6a478` at cursor 213.
Date: 2026-10-11.

This document aligns requirements only. It does not admit evidence, approve capture, or start training.
Rank: MUST blocks the HCF pilot. NEXT improves current open models. LATER waits for a parent gate.

## 1. Models and missing data

| Model or task | Current evidence | Top 3 missing strata | Rank |
| --- | --- | --- | --- |
| HCF focus assistance: optional rules plus shared FocusRing; a separate model is undecided | 1 journey, 7 unique images, 6 analysis frames (HCF333/HCF334). No no-focus frames. | 1. The same scenes under Default and High Contrast in independent layout families. 2. Verified no-focus and distracting-border frames. 3. Competing highlights and clock or profile badges. | MUST |
| Ordinary single-frame focus and the focus-change model | Native correctness 592/640 (FOCUS329). Tiny changes 0/4. | 1. Focused bodies under 15 encoded pixels; native training has none. 2. Competing highlights and left distractions with verified truth. 3. Unfamiliar wide artwork. | MUST for 1–2, NEXT for 3 |
| Element boxes: tvOS YOLO11n `nativeui-tvos-v3.0` | Mostly synthetic training. Independent real-app evaluation is open (TASK-6b-R-1, EVAL-90). | 1. Full frames from untouched real-app families with verified boxes for every visible class. 2. Dense adjacent cards and modal-over-parent screens as full frames with boxes. 3. Classes with low tvOS support. | NEXT |
| Transitions and no-op | Reserved results 51/52 (TRANSITION290). | 1. Re-captures of an identical state, for true no-op under render noise. 2. Weak native focus effects. 3. Real interruptions with a verified rendered change. | NEXT |
| OCR and text | Apple Vision. NUIAK does not train OCR. Data only tests text anchors and fusion. | 1. Truncated text with the known full string. 2. Dense adjacent rows. 3. SF Symbols next to text. | LATER |

## 2. Input format and preprocessing

- Deliver lossless, opaque, 8-bit sRGB PNG files.
- If the producer renders with alpha, flatten it on the rendered background before export.
- Do not convert pixels to linear light. HCF-COLOR263 measured more error in every group with linear blending.
- Keep native resolution. Record pixel dimensions and capture scale in the sidecar.
- Do not upscale 1920×1080 to 3840×2160. Both sizes are acceptable when the scale is explicit.
- Detector: NUIAK uses the full frame. It letterboxes to 640×640 with gray 114 padding.
- Boxes: top-left pixel `x, y, width, height` in the delivered image, plus normalized `[xMin, yMin, xMax, yMax]`.
- FocusRing: NUIAK expands each detector box by 16% per side, clamps it, and resizes the crop to 256×256 RGB in `[0, 1]`.
- Do not send crops as a substitute for full frames. NUIAK makes crops from the full frame (BP-46).
- Focus-change model: send pairs of full frames with equal dimensions. NUIAK makes the comparison crops.
- Smallest important target: the focused body's short side after NUIAK encoding.
  Native training covers 15.06–27.02 encoded pixels. Tiny development cases measure 2.93 pixels (FOCUS310).
  Request controls near 3, 6, 12, and 24 encoded pixels. Report each target's short side in delivered pixels.

## 3. Realism, controlled distortion, and rejection

Clean set: native-rendered frames from the real app or Fixture under a recorded profile. Apply no post-processing.

Challenge set: 1 controlled distortion per stratum, with its parameter recorded.
Useful distortions are mid-animation timing, compression level, brightness or contrast of the video path, and scale.
Keep each distortion in a named stratum. Do not mix challenge frames into the clean set.

Not useful as truth: drawn rings that imitate focus, text pasted after rendering, and linear-light recoloring.

Reject the item when any of these conditions is true:

- A change is claimed, but the before and after frames are identical.
- A referenced file is missing, or its size or hash does not match.
- A box extends outside the image or has no area.
- A class name is not in `Research/schemas/category_map.json`. NUIAK drops it and does not remap it (BP-28).
- A label comes from model output, such as a `*_result.json` file.
- Focus truth comes from a rule or a model instead of the runtime focus state.
- The profile is unknown, or the frame was captured before the scene reported a settled state.
- A duplicate frame is counted as a new example.

## 4. Review tags and uncertainty

Paired frames with native-bound overlays are sufficient when each sidecar contains the runtime focus ID and element bounds for that frame.

Use 3 separate tags. Do not combine them into 1 score.

- Realism: native, near-native, or unrealistic.
- Usefulness: new stratum, duplicate, or off-goal.
- Annotation concern: box, focus, class, text, or none.

"Uncertain" is a valid answer. An uncertain item stays out of training and evaluation until a second reviewer resolves it.
If reviewers disagree, keep both answers. The item stays out until the disagreement is resolved.
The review tool must never edit labels automatically.

## 5. Sample size and required failure cases

Pilot size: the existing 48-screen HCF development plan.
It contains 12 scenes, 4 layout families, 2 profiles, and 2 focus positions.
Add at least 8 verified no-focus frames and 8 distracting-border frames.
Reserve 1 layout family before any fit.

Include these failure patterns on purpose:

- HCF334 frame 32: the correct control scores 0.987, but another control wins.
- HCF334 frame 34: a clock-area box wins, but the outlined placeholder icon is focused.
- Tiny focus changes near 3 encoded pixels.
- Left-distraction layouts and wide artwork.

Do not reuse frames from the retained HCF-NATIVE261 journey. They are inspected development evidence.

## 6. Proposed fixed-budget ablation

Use the same model, initialization, epochs, and evaluation for each arm. Use a fixed number of added examples per arm.

1. A0: current training data.
2. A1: A0 plus procedural content at fixed layouts.
3. A2: A0 plus coherent realistic content at the same fixed layouts.
4. A3: the better of A1 and A2, plus structural diversity at fixed content.

Evaluate every arm only on untouched real or native families. Report results by family group with intervals.
If no arm beats A0 on untouched groups without regressions, stop the ablation.

## 7. Metrics and promotion

Use identical membership for every method. Count layout-family and scene groups, not frames.

- Wrong-focus rate: a confident selection of a control that is not focused. This includes false focus confirmation. It is the primary safety metric.
- Miss rate, abstention rate, and coverage.
- No-focus specificity: abstention on verified no-focus frames.
- Localization: IoU of the selected box against truth, and box error in pixels.
- Ordinary-profile non-regression: no lost previous successes on retained regression sets.
- Latency: warm p50 and p95 per image on the same host. Report first-image setup separately.
- Uncertainty: bootstrap intervals that resample groups.

Promote only if all of these conditions are true:

- Wrong focus does not increase.
- Ordinary focus has no regressions.
- The gain also holds on the reserved family.

Rule and model agreement is not an acceptance rule. In HCF334, agreement kept only 3 of 5 reviewed rule proposals.

## 8. Current exposure and leakage rules

Current HCF inventory:

- HCF-NATIVE261: 8 entries, 7 unique images, 1 journey. Development only and inspected.
- HCF335 and HCF336 authored images: development only, `trainingEligible=false`.
- No HCF evaluation set exists yet.

TTR must not do these things:

- Reuse reserved-family layouts, scenes, seeds, or recipes in development or training batches.
- Return NUIAK model scores or predictions as labels.
- Reuse retained regression frames.
- Show evaluation frames in review pages that tune generators.

## Missing inputs from Sillycon-TTR

1. A committed profile command contract.
2. Restart-restoration evidence for profile changes.
3. Per-frame runtime focus ID and a profile receipt in each sidecar.
4. A verified way to produce no-focus frames.
