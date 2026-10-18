# EXP418-08 — Margin-Preserving Knowledge Distillation for Sub-5MB Core ML Palettization (`B405-236` / Template `T74`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `Deployment` (`DEPLOY`). Priority: `P0`.
Parent task: `TEMPLATE395` / `MODEL-DIST-02` / `B405-128`. Template: `T74` (`distilled_coreml_compress418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
`Maximum-mini-NUIAK` faces two deployment bottlenecks for `Sillycon-TTR` (`MODEL-DIST-02`) and package distribution:
1. **Package Size Limit (`TEMPLATE395`)**: Uncompressed FP16 Core ML conversion of `FocusRingDetector` exceeds the 5,000,000-byte (`5 MB`) gate by `38,115` bytes (`5,038,115` bytes).
2. **Quantization Decision Drift (`INFERENCE412`, `B405-128`)**: Post-training weight compression (`int8weights` or `palette6weights`) reduces the package to `2.61 MB`, but standard k-means clustering minimizes uniform Euclidean weight error $\|W - \hat{W}\|_2^2$. Near the `0.85` focus threshold (`logit = 1.7346`), a tiny logit shift of `0.03` flips borderline native control predictions (`row` and `tab` crops scoring `0.84` to `0.86`) from positive to abstention!

### SOTA Method: Activation-Aware & Boundary-Margin Knowledge Distillation for Weight Palettization
Inspired by **Activation-Aware Weight Quantization (AWQ)** (Lin et al., *AWQ: Activation-aware Weight Quantization*) and **Decision-Boundary Margin Distillation**:
1. **Saliency-Weighted Lut Palettization (`awq-palette6`)**: Compute per-channel activation and Fisher gradient importance on the **training crops** for samples whose teacher probability lies in the critical decision band $p_{\text{teacher}} \in [0.50, 0.95]$ (`logit` $\in [0.0, 2.94]$). Scale salient channels before 6-bit / 8-bit k-means palettization so quantization error concentrates in dead channels rather than decision-critical channels.
2. **Post-Compression BatchNorm & Classifier Head Margin Calibration (`margin-distilled-palette6`)**: Freeze the 6-bit palettized convolution weights $\hat{W}$ and run 100 fast calibration steps updating only the BatchNorm affine scales/biases $(\gamma, \beta)$ and final linear bias on the **training set** (never touching development or audit data!) using a boundary-weighted distillation loss:

$$\mathcal{L}_{\text{margin}}(z_S, z_T) = w(z_T) \cdot (z_S - z_T)^2 + \lambda_{\text{flip}} \cdot \text{ReLU}\bigl(-(z_S - \tau)(z_T - \tau)\bigr)$$

where $\tau = \ln(0.85 / 0.15) \approx 1.7346$ and $w(z_T) = 1 + 4 \exp\bigl(-(z_T - \tau)^2 / 0.5\bigr)$ weights borderline examples 5x higher than easy examples.

---

## 2. Controlled Test and Decision Rules

### Hypothesis
Boundary-Margin Distillation after 6-bit palettization keeps the Core ML package under `3.0 MB` (`<= 5,000,000` bytes) while reducing maximum Vision `VNCoreMLRequest` probability error by `>= 50 %` and achieving **0 changed classification decisions** at threshold `0.85` across all difficult development groups.

### Experimental Arms
All arms compress the exact same candidate checkpoint (`jitter413-train-jitter-r2` or `nctrl417-train-mixed`), use only training crops for calibration, and evaluate Vision parity via `FocusRingTool` on the combined artwork + native-control development membership:
1. `control` (`compressionMode = 'naive-palette6'`, `bits = 6`): Standard `coremltools` 6-bit k-means palettization (`T10` baseline).
2. `naive-int8` (`compressionMode = 'naive-int8'`, `bits = 8`): Standard `coremltools` 8-bit linear weight quantization.
3. `awq-palette6` (`compressionMode = 'awq-saliency'`, `bits = 6`): Activation-saliency weighted 6-bit palettization.
4. `margin-distilled-palette6` (`compressionMode = 'margin-distilled'`, `bits = 6`): 6-bit palettization + 100-step training-set BatchNorm/head boundary-margin distillation before Core ML export.

### Mechanical Decision Rule (`gain-without-loss`)
- **Supported**: The compressed `.mlpackage` is `<= 4,800,000` bytes, matches 100 % of FP32 teacher decisions (`changed_decisions == 0`, `lostPriorSuccesses == []`) across all artwork, native button, row, tab, and no-focus development crops in actual Apple `VNCoreMLRequest` inference, and achieves `max_score_error <= 0.002`.
- **Contradicted**: Compression changes any focus decision at `0.85` or exceeds the `5,000,000`-byte package gate.
- **Inconclusive**: Core ML conversion or `FocusRingTool` Vision verification fails.

---

## 3. What This Tells TTR and NUIAK

- **If Supported**:
  - `Maximum-mini-NUIAK` unblocks `B405-081`, `B405-083`, `B405-128`, and `MODEL-DIST-02`.
  - `Sillycon-TTR` and `Maximum-mini-TTR` receive a `~2.6 MB` embedded `.mlmodelc` model that runs on macOS 14+ and tvOS with verified zero decision drift against the PyTorch research checkpoint.
- **If Contradicted**:
  - `Maximum-mini-NUIAK` uses mixed-precision palettization (keeping the first `conv_stem` and final `conv_head` / `classifier` in FP16 while palettizing only the intermediate `UniversalInvertedResidual` stages to 6-bit, which adds only `~45 KB` while protecting input/output dynamic range).

---

## 4. Template `T74` Contract

### Entry in `scripts/hcf_templates395.py`
```python
'T74': (
    {'candidate', 'trainingCrops', 'parityMembership'},
    {'compressionMode', 'bits'},
    'distilled_coreml_compress418.run',
    'artifact',
    'export',
),
```

### Inputs and Parameters
- **Inputs**:
  - `candidate`: Pinned `.pt` model checkpoint to compress and export.
  - `trainingCrops`: Pinned `crops.json` manifest (only `role == 'train'` rows are read for calibration; any access to `development` rows during calibration raises a fatal `calibration_role_leak` error).
  - `parityMembership`: Pinned evaluation manifest scored through `FocusRingTool` (`VNCoreMLRequest`) after export.
- **Parameters**:
  - `compressionMode`: `str` in `{'naive-palette6', 'naive-int8', 'awq-saliency', 'margin-distilled'}`.
  - `bits`: `int` in `{6, 8}`.

### Catalog Plan Block Example (`backlog405.json`)
```json
{
  "template": "T74",
  "owner": "Maximum-mini-NUIAK",
  "jobPrefix": "b405-185-compress",
  "rule": "gain-without-loss",
  "control": "control",
  "question": "On the combined artwork and native-control development membership, does margin-distilled 6-bit Core ML weight palettization keep package size under 5 MB while reducing Vision score error and producing 0 changed decisions against the FP32 checkpoint?",
  "decision": "Support a compressionMode that produces a package <= 4.8 MB with 0 changed decisions at threshold 0.85 and max Vision probability error <= 0.002.",
  "outcomes": {
    "supported": "Qualify margin-distilled-palette6 as the standard T10/T74 export path for MODEL-DIST-02 delivery to Sillycon-TTR.",
    "contradicted": "Keep conv_stem and classifier in FP16 and apply 6-bit palettization only to interior UIB blocks.",
    "inconclusive": "Complete all 4 export and Vision parity arms at an idle boundary."
  },
  "shared": {
    "inputs": {
      "candidate": {"file": "reports/work/research-queue/jobs/jitter413-train-jitter-r2/attempts/1/out/final.pt"},
      "trainingCrops": {"job": "nctrl417-membership-mixed", "output": "crops.json"},
      "parityMembership": {"file": "Research/Experiments/backlog405-native-inputs.json"}
    }
  },
  "arms": [
    {"id": "control", "label": "Naive 6-bit k-means palettization", "parameters": {"compressionMode": "naive-palette6", "bits": 6}},
    {"id": "naive-int8", "label": "Naive 8-bit linear quantization", "parameters": {"compressionMode": "naive-int8", "bits": 8}},
    {"id": "awq-6bit", "label": "Saliency-weighted 6-bit palettization", "parameters": {"compressionMode": "awq-saliency", "bits": 6}},
    {"id": "margin-6bit", "label": "Margin-distilled BN + 6-bit palettization", "parameters": {"compressionMode": "margin-distilled", "bits": 6}}
  ]
}
```

---

## 5. Implementation Plan and Reference Code

### Step-by-Step Implementation Plan
1. **Create `scripts/distilled_coreml_compress418.py`**:
   - Enforce strict role isolation: filter `trainingCrops` to `r['role'] == 'train'` before computing saliency or BN margin calibration.
   - Implement simulated lut weight quantization in PyTorch so `margin-distilled` can fine-tune BatchNorm `(weight, bias)` and `classifier.bias` for 100 steps with `lr = 1e-4` against cached FP32 teacher logits.
   - Export to `.mlpackage`, apply `coremltools` palettization, run `FocusRingTool` (`VNCoreMLRequest`) on `parityMembership`, and record package bytes, `max_score_error`, `changed_decisions`, `cold_seconds`, and `warm_seconds`.
2. **Create `scripts/test_distilled_coreml_compress418.py`**:
   - Test that passing any `development` row into the calibration loader raises `calibration_role_leak`.
   - Test that `quantize_per_channel_lut` and `margin_distillation_step` monotonically reduce boundary logit error on synthetic borderline logits (`1.65` to `1.85`).

### Reference Adapter Code (`scripts/distilled_coreml_compress418.py`)
```python
"""T74: Margin-preserving knowledge distillation and saliency-weighted Core ML palettization."""
import math
import torch
import torch.nn.functional as F
import research_queue as q

OUT = None
MODES = ('naive-palette6', 'naive-int8', 'awq-saliency', 'margin-distilled')
BITS = (6, 8)
THR_LOGIT = math.log(0.85 / 0.15)  # 1.7346010553881064


def parameters(value):
    q.require(isinstance(value, dict) and set(value) == {'compressionMode', 'bits'}, 'compress_parameters')
    mode, bits = value['compressionMode'], value['bits']
    q.require(mode in MODES, 'compress_mode_invalid')
    q.require(bits in BITS, 'compress_bits_invalid')
    return mode, int(bits)


def margin_calibration_loss(student_logits: torch.Tensor, teacher_logits: torch.Tensor) -> torch.Tensor:
    """Distill FP32 teacher logits with 5x focus near the 0.85 threshold and a 10x sign-flip penalty."""
    t = teacher_logits.detach()
    band_weight = 1.0 + 4.0 * torch.exp(-((t - THR_LOGIT) ** 2) / 0.5)
    mse = (student_logits - t).pow(2)
    flip_penalty = F.relu(-(student_logits - THR_LOGIT) * (t - THR_LOGIT))
    return (band_weight * (mse + 10.0 * flip_penalty)).mean()
```

### Resource and Time Budget
- **Preparation**: 60 min.
- **Execution**: 4 export and Vision verification jobs at 90 s to 240 s each (1,800 s ceiling, 2 GiB cap).
- **Review**: 15 min via `backlog_pipeline.py review`.
