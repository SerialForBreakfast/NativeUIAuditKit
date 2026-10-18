# EXP418-02 — Fourier Domain Adaptation (FDA) for Synthetic-to-Real Transfer (`B405-230` / Template `T68`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `Representations` (`REP`). Priority: `P1`.
Parent task: `FOCUS348` / `TASK-6a-10`. Template: `T68` (`fda_transfer418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
`Maximum-mini-NUIAK` trains detectors and focus classifiers on synthetic frames from `GeneratorRunner` (iOS) and `Maximum-mini-TTR` Fixture (tvOS). Synthetic frames have uniform backgrounds or procedural gradients. Real apps on `Sillycon-TTR` have blurred media backdrops (`UIBlurEffect`, Liquid Glass translucency), wallpaper bleed, and display tone mapping.

In [BestPractices.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/BestPractices.md) (`FOCUS348`), spatial appearance augmentation reduced false focus changes from `587` to `26`, but lost `72` movement successes (`444` down to `372`). Spatial color jitter and blur alter the local pixel gradients that define focus rings, shadows, and glyph edges.

### SOTA Method: Fourier Domain Adaptation (FDA)
**Fourier Domain Adaptation (FDA)** (Yang & Soatto, *FDA: Fourier Domain Adaptation for Semantic Segmentation*) separates domain style from geometric structure in the frequency domain:
- In a 2D Discrete Fourier Transform $\mathcal{F}(I) = \mathcal{A}(I) \cdot e^{j \mathcal{P}(I)}$, the **phase spectrum** $\mathcal{P}(I)$ encodes high-level semantics, exact edge locations, stroke widths, and focus ring offsets.
- The **low-frequency amplitude spectrum** $\mathcal{A}(I)$ within a small center window of radius $\beta \in (0, 0.05]$ encodes global luminance, color cast, and background material statistics.

By replacing only the lowest $\beta \times H \times \beta \times W$ amplitude coefficients of a synthetic training image with those from a real calibration frame while keeping the synthetic phase $\mathcal{P}(I_{\text{syn}})$ 100 % intact, FDA transfers real-screen illumination and backdrop statistics without blurring or shifting any UI boundary.

---

## 2. Controlled Test and Decision Rules

### Hypothesis
Training the `FocusRingDetector` crop classifier with phase-preserving low-frequency amplitude swaps (`fdaBeta` in `{0.01, 0.03, 0.05}`) improves generalization to unseen background themes (`B405-161` light backgrounds and real tvOS backdrops) while losing 0 successes on retained Standard, HCF, and native-control development groups.

### Experimental Arms
All arms use `fdr038-retention234` initialization, seed `371`, batch `16`, 30 epochs, fixed-last selection, and the matched `NCTRL417` membership (`7,200` samples per epoch). Only `fdaBeta` changes:
1. `control` (`fdaBeta = 0.00`): Unchanged synthetic pixels. Must reproduce the exact control weights and scores.
2. `fda-001` (`fdaBeta = 0.01`): Swap only the central 1 % low-frequency amplitude (DC + first-order background gradient).
3. `fda-003` (`fdaBeta = 0.03`): Swap the central 3 % low-frequency amplitude.
4. `fda-005` (`fdaBeta = 0.05`): Swap the central 5 % low-frequency amplitude.

### Mechanical Decision Rule (`gain-without-loss`)
- **Supported**: An FDA arm gains `>= 4` correct selections on unseen background-theme or real-app development groups while losing `0` successes on the 74 retained `HCF402` development frames and reserved native-control groups.
- **Contradicted**: Every `fdaBeta > 0` arm loses prior successes on retained groups (as `FOCUS348` did) or gains `0` selections on unseen background themes.
- **Inconclusive**: Reference amplitude bank hashes fail verification or any evaluation arm is incomplete.

---

## 3. What This Tells TTR and NUIAK

- **If Supported**:
  - `Maximum-mini-NUIAK` gains a label-safe, edge-preserving domain adaptation step that closes the gap between synthetic Fixture captures and real tvOS/iOS apps.
  - `Maximum-mini-TTR` does not need to build complex wallpaper-blur shaders for every Fixture archetype; `Maximum-mini-NUIAK` can inject real spectral statistics during training from a small pinned bank of 32 calibration spectra.
- **If Contradicted**:
  - `Maximum-mini-NUIAK` establishes that even low-frequency amplitude changes interfere with the MobileNetV4 stem's absolute brightness thresholds.
  - Future domain transfer must rely on explicit local contrast normalization (`EXP418-05` / `T71`) or native backdrop rendering inside `Maximum-mini-TTR`.

---

## 4. Template `T68` Contract

### Entry in `scripts/hcf_templates395.py`
```python
'T68': (
    {'configuration', 'initialization', 'membership', 'referenceSpectra'},
    {'fdaBeta', 'seed'},
    'fda_transfer418.run',
    'training',
    'training',
),
```

### Inputs and Parameters
- **Inputs**:
  - `configuration`: Pinned training config JSON (`fda-transfer-config-v1`).
  - `initialization`: Pinned starting checkpoint (`fdr038-retention234/weights/best.pt`).
  - `membership`: Pinned `crops.json` producer output.
  - `referenceSpectra`: Pinned `.npz` / `.json` bank of low-frequency amplitude patches extracted from admitted calibration frames (contains no raw image pixels or evaluation frames).
- **Parameters**:
  - `fdaBeta`: `float` in `{0.0, 0.01, 0.03, 0.05}`.
  - `seed`: `int` in `{371, 372, 373}`.

### Catalog Plan Block Example (`backlog405.json`)
```json
{
  "template": "T68",
  "owner": "Maximum-mini-NUIAK",
  "jobPrefix": "b405-179-fda",
  "rule": "gain-without-loss",
  "control": "control",
  "question": "On the matched 7,200-sample crop training membership, does phase-preserving Fourier Domain Adaptation (fdaBeta 0.01, 0.03, 0.05) improve cross-theme focus selection without losing retained successes?",
  "decision": "Support the smallest fdaBeta that gains at least 4 selections on cross-theme development groups with 0 lost successes on retained artwork and native-control groups.",
  "outcomes": {
    "supported": "Adopt phase-preserving FDA in crop training and run paired seeds 372 and 373.",
    "contradicted": "Reject frequency amplitude mixing and keep unchanged crop pixels.",
    "inconclusive": "Complete all arms and T37/T41 regression evaluations before deciding."
  },
  "shared": {
    "inputs": {
      "configuration": {"file": "Research/ResearchSpecs/EXP418/t56-fda-config.json"},
      "initialization": {"file": "NativeUITrainer/focus_ring_runs/fdr038-retention234/weights/best.pt"},
      "membership": {"job": "nctrl417-membership-mixed", "output": "crops.json"},
      "referenceSpectra": {"file": "Research/Experiments/fda-calibration-spectra418.json"}
    },
    "parameters": {"seed": 371}
  },
  "arms": [
    {"id": "control", "label": "fdaBeta 0.00 (no swap)", "parameters": {"fdaBeta": 0.0}},
    {"id": "fda-001", "label": "fdaBeta 0.01", "parameters": {"fdaBeta": 0.01}},
    {"id": "fda-003", "label": "fdaBeta 0.03", "parameters": {"fdaBeta": 0.03}},
    {"id": "fda-005", "label": "fdaBeta 0.05", "parameters": {"fdaBeta": 0.05}}
  ]
}
```

---

## 5. Implementation Plan and Reference Code

### Step-by-Step Implementation Plan
1. **Create `scripts/fda_transfer418.py`**:
   - Validate `fdaBeta` in `{0.0, 0.01, 0.03, 0.05}` and `seed` in `{371, 372, 373}`.
   - Implement `fda_swap_batch(images, ref_amps, beta, rng)` using `torch.fft.rfft2` / `torch.fft.fft2`.
   - Ensure deterministic pairing: for a given `(epoch, sample_index, seed)`, select the exact same reference spectrum index so runs are 100 % reproducible.
   - Measure edge-gradient preservation (Sobel correlation between original and FDA-adapted crops must exceed `0.98`).
2. **Create `scripts/test_fda_transfer418.py`**:
   - Verify that `fdaBeta = 0.0` returns the input tensor with `0.0` difference.
   - Verify that phase angle $\angle \mathcal{F}(I_{\text{out}})$ equals $\angle \mathcal{F}(I_{\text{in}})$ across all frequencies.
   - Run an isolated queue test for positive and negative validation paths.

### Reference Adapter Code (`scripts/fda_transfer418.py`)
```python
"""T68: Phase-preserving Fourier Domain Adaptation (FDA) for synthetic-to-real crop training."""
import torch
import research_queue as q

OUT = None
BETAS = (0.0, 0.01, 0.03, 0.05)
SEEDS = (371, 372, 373)


def parameters(value):
    """Validate and return (fdaBeta, seed)."""
    q.require(isinstance(value, dict) and set(value) == {'fdaBeta', 'seed'}, 'fda_parameters')
    beta, seed = value['fdaBeta'], value['seed']
    q.require(beta in BETAS, 'fda_beta_invalid')
    q.require(seed in SEEDS, 'fda_seed_invalid')
    return float(beta), int(seed)


def apply_fda_batch(images: torch.Tensor, ref_low_amp: torch.Tensor, beta: float) -> torch.Tensor:
    """Swap central (beta * H, beta * W) amplitude of [B, C, H, W] float32 images in [0, 1]."""
    if beta <= 0.0:
        return images
    _, _, h, w = images.shape
    bh, bw = max(1, int(round(h * beta))), max(1, int(round(w * beta)))
    cy, cx = h // 2, w // 2
    fft_src = torch.fft.fftshift(torch.fft.fft2(images, dim=(-2, -1)), dim=(-2, -1))
    amp = torch.abs(fft_src)
    phase = torch.angle(fft_src)
    amp[:, :, cy - bh:cy + bh, cx - bw:cx + bw] = ref_low_amp[:, :, :2 * bh, :2 * bw]
    reconstructed = torch.fft.ifft2(torch.fft.ifftshift(amp * torch.exp(1j * phase), dim=(-2, -1)), dim=(-2, -1)).real
    return reconstructed.clamp(0.0, 1.0)
```

### Resource and Time Budget
- **Preparation**: 45 min to 90 min.
- **Execution**: 4 training jobs (about 550 s each, 1,800 s ceiling, 2 GiB cap) plus T37/T41 scoring jobs (20 s each).
- **Review**: 15 min via `backlog_pipeline.py review`.
