# EXP418-12 — Copula Proposal-Error Sampler and Spatial Transformer Crop Refiner (`ProposalSTN`, `B405-240` / Template `T78`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `Representations` (`REP`). Priority: `P0`.
Parent task: `B405-193` / `B405-196` / `B405-204`. Template: `T78` (`copula_proposal_stn418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [DetectorFocusFollowup.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/DetectorFocusFollowup.md) and [DetectorFocusPolicy.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/DetectorFocusPolicy.md), `Maximum-mini-NUIAK` proved that `FocusRingClassifier` performance drops sharply when switching from ground-truth body boxes to real YOLO11n detector proposals:
- On the 24 native pilot events per profile, the candidate scores **`21 of 24` on known control boxes**, but drops to **`16 of 24` on detector boxes**.
- On the Standard diamond-decoration hard case (`B405-201`), known boxes pass (`4 of 4`), whereas detector boxes drop the focused control's score to `0.585` (below the `0.85` threshold).
- On tall HCF controls (`TTRMatchedConsumer.md`), the `12.5 %` model scores `4 of 4` on known boxes, but drops to `2 of 4` on combined detector-plus-ring boxes.

Why does generic uniform crop jitter (`B405-138`, independent uniform offsets in `[-4, +4] px`) fail to close this gap? Because real YOLO11n detector errors $\mathbf{e} = (\delta_{cx}, \delta_{cy}, \delta_{\log w}, \delta_{\log h})$ are **strongly non-Gaussian and coupled across dimensions**:
- On wide `listRow` controls, detector boxes systematically truncate the right accessory chevron ($\delta_{cx} < 0, \delta_{\log w} < 0$).
- On tall poster cards with drop shadows or top titles, detector boxes systematically shift the top or bottom boundary ($\delta_{cy} \neq 0, \delta_{\log h} > 0$).

### SOTA Method: Empirical Gaussian Copula Error Modeling + Differentiable Spatial Transformer Crop Alignment (`ProposalSTN`)
This experiment combines two complementary SOTA mechanisms under `B405-193` and `B405-196`:
1. **Training-Only Empirical Copula Proposal-Error Sampler (`copula-sampler`)** (Nelsen, *An Introduction to Copulas*; Sklar's Theorem):
   - Using strictly **training-split** detector-to-body matches ($\text{IoU} \ge 0.50$), estimate the empirical marginal CDFs $\hat{F}_1(\delta_{cx}), \hat{F}_2(\delta_{cy}), \hat{F}_3(\delta_{\log w}), \hat{F}_4(\delta_{\log h})$ and the $4 \times 4$ latent normal correlation matrix $\hat{\Sigma}_Z$ of $Z_j = \Phi^{-1}(\hat{F}_j(e_j))$ per control family.
   - Sample realistic correlated proposal perturbations during crop training without ever touching development or audit frames (`DetectorFocusPolicy.md` line 82).
2. **Differentiable Spatial Transformer Crop Refiner (`ProposalSTN`)** (Jaderberg et al., *Spatial Transformer Networks*, NeurIPS 2015):
   - Attach a tiny `4-parameter` scale-and-translation localization regressor $g_\psi(f_{\text{early}}) \to (\hat{t}_x, \hat{t}_y, \hat{s}_x, \hat{s}_y)$ to stage-2 of `MobileNetV4ConvSmall`.
   - Before computing the final focus logit, `ProposalSTN` warps the `256 x 256` crop tensor via differentiable bilinear sampling (`F.grid_sample`) to align the noisy detector box back to the canonical `0.16`-margin control body frame, supervised by an auxiliary $L_1$ box-alignment loss against the true body coordinates during training.

---

## 2. Controlled Test Design

- **Pinned Dataset**: Training-only detector/body matches for fitting the Copula sampler; `7,200` training samples (`seed 371`); evaluated on the 8 full-screen `T57` comparison sets (`B405-208`) and `B405-204` (`T61`) geometry audit cases.
- **Arms**:
  1. `uniform-jitter` (Control): Existing independent uniform crop jitter (`B405-138`).
  2. `copula-error-only`: Trained with the training-split Empirical Gaussian Copula error sampler, unchanged architecture.
  3. `copula-plus-stn`: Trained with the Copula error sampler + `ProposalSTN` differentiable crop alignment head.
- **Decision Rules**:
  - **Supported**: `copula-error-only` or `copula-plus-stn` recovers the Standard diamond-decoration detector-box case (`score >= 0.85`), recovers the `2` tall HCF controls (`4 of 4`), and improves full-screen detector-box native selection above `16/24` with `0` lost known-box successes.
  - **Contradicted**: Realistic training proposal errors do not improve detector-box focus selection over `uniform-jitter`, proving the remaining failures are missing proposals (`IoU < 0.50`) rather than crop alignment sensitivity.
  - **Inconclusive**: Complete all 8 `T57` case sets before deciding.
  - **Regression Gate**: Reject any arm that uses development/audit offsets in training or loses any known-box selection.

---

## 3. What This Tells `Maximum-mini-TTR`, `Sillycon-TTR`, and `Maximum-mini-NUIAK`

1. **For `Maximum-mini-NUIAK` (`B405-193`, `B405-196`)**: Directly answers `FOCUS-PIPELINE-NEXT-02` and `FOCUS-PIPELINE-ERROR-PREP` by testing both data-side realistic error sampling (`Copula`) and model-side canonical alignment (`ProposalSTN`).
2. **For `Sillycon-TTR`**: Makes `FocusRingClassifier` robust to real-time `UIElementDetector` box jitter on live app screens where ground-truth accessibility frames are unavailable.

---

## 4. New Template Contract (`T78`)

Register `T78` in [`scripts/hcf_templates395.py`](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/scripts/hcf_templates395.py) at an idle runner boundary:

```python
"T78": (
    {"trainingMatches", "manifest", "epochs", "seed"},
    {"samplerMode", "enableStnRefiner", "stnLossWeight"},
    "copula_proposal_stn418.run",
    "artifact",
    "training",
),
```

---

## 5. Implementation Plan and Reference Code

### Step 1 — Empirical Gaussian Copula Sampler & `ProposalSTN` (`scripts/copula_proposal_stn418.py`)

```python
"""T78 adapter: Empirical Copula proposal-error sampler and Spatial Transformer crop refiner."""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.stats import norm


class EmpiricalCopulaErrorSampler:
    """Fits a 4D Gaussian Copula on training-only (dcx, dcy, dlogw, dlogh) detector errors."""

    def __init__(self, errors: np.ndarray, seed: int = 371) -> None:
        assert errors.ndim == 2 and errors.shape[1] == 4 and len(errors) >= 16
        self.sorted_marginals = np.sort(errors, axis=0)
        n = len(errors)
        ranks = np.argsort(np.argsort(errors, axis=0), axis=0)
        u = (ranks + 1.0) / (n + 1.0)
        z = norm.ppf(np.clip(u, 1e-4, 1.0 - 1e-4))
        self.cov = np.cov(z, rowvar=False) + np.eye(4) * 1e-4
        self.rng = np.random.default_rng(seed)

    def sample(self, count: int) -> np.ndarray:
        z_samples = self.rng.multivariate_normal(np.zeros(4), self.cov, size=count)
        u_samples = norm.cdf(z_samples)
        n = len(self.sorted_marginals)
        indices = np.clip((u_samples * (n - 1)).astype(int), 0, n - 1)
        out = np.empty_like(u_samples)
        for dim in range(4):
            out[:, dim] = self.sorted_marginals[indices[:, dim], dim]
        return out


class ProposalSTNRefiner(nn.Module):
    """Lightweight 4-parameter affine Spatial Transformer that snaps noisy proposal crops to body bounds."""

    def __init__(self, in_channels: int = 3) -> None:
        super().__init__()
        self.localization = nn.Sequential(
            nn.Conv2d(in_channels, 16, kernel_size=5, stride=4, padding=2),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.Conv2d(16, 32, kernel_size=3, stride=4, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(32, 4),
        )
        nn.init.zeros_(self.localization[-1].weight)
        nn.init.zeros_(self.localization[-1].bias)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        # delta = [tx, ty, log_sx, log_sy], bounded to [-0.20, +0.20]
        delta = 0.20 * torch.tanh(self.localization(x))
        tx, ty, lsx, lsy = delta[:, 0], delta[:, 1], delta[:, 2], delta[:, 3]
        sx, sy = torch.exp(lsx), torch.exp(lsy)
        zeros = torch.zeros_like(tx)
        theta = torch.stack([
            torch.stack([sx, zeros, tx], dim=-1),
            torch.stack([zeros, sy, ty], dim=-1),
        ], dim=1)
        grid = F.affine_grid(theta, list(x.shape), align_corners=False)
        warped = F.grid_sample(x, grid, mode="bilinear", padding_mode="border", align_corners=False)
        return warped, delta
```

### Step 2 — Verification
- Add unit tests in `scripts/test_copula_proposal_stn418.py` verifying that `EmpiricalCopulaErrorSampler` rejects any input record whose `role != "training"` and that `ProposalSTNRefiner` initializes as an exact identity transform (`|warped - x|_max < 1e-5`).
