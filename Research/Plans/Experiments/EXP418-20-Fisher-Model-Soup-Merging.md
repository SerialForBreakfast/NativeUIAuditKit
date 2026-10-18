# EXP418-20 — Fisher-Weighted Model Soups and Task-Vector Merging (`FisherSoup`, `B405-248` / Template `T86`)

Owner: `Maximum-mini-NUIAK`. Date: 2026-10-17. Track: `Deployment` (`DEPLOY`) and `Standard FocusRing` (`FR`). Priority: `P0`.
Parent task: `PM08` / `OR10` / `B405-195` / `TTRMatchedConsumer.md`. Template: `T86` (`fisher_model_soup418.run`).

---

## 1. Goals and SOTA Foundation

### Observed Bottleneck
In [TTRMatchedConsumer.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/TTRMatchedConsumer.md), [DetectorFocusPolicy.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/DetectorFocusPolicy.md), and [ResearchSources417.md](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/Research/Plans/ResearchSources417.md) (`PM08 Model Soups`, `OR10`), `Maximum-mini-NUIAK` already trained multiple compatible `MobileNetV4ConvSmall` checkpoints from the exact same initialization (`seed 371`), each with complementary strengths and weaknesses:
- **Retained Baseline Checkpoint ($\theta_{\text{base}}$)**: `4/4` on Standard diamond decoration, `4/4` on tall HCF controls, low false-positive rate (`7` vs `16`) on `Sillycon-TTR` archive crops, but only `4/24` on native buttons, rows, and tabs.
- **12.5 % Native-Exposure Checkpoint ($\theta_{12.5}$)**: Recovers `8/8` native tabs and `4/4` Standard diamond decoration, `7/8` buttons, **but loses 2 tall HCF controls (`4/4 -> 2/4`) and adds 2 wrong row selections**.
- **25 % Native-Exposure Checkpoint ($\theta_{25}$)**: Recovers `21/24` known-box native controls (`16/24` detector-box) and `4/4` tall HCF controls, **but loses Standard diamond decoration (`3/4`) and produces 16 false positives on `Sillycon-TTR`**.

Why did runtime fallback (`B405-203`, running $\theta_{\text{base}}$ when $\theta_{25}$ abstains) fail? Because runtime fallback **doubles model memory/storage** and **unions the false positives of both models** (`+3` wrong selections in `B405-203`)! And why is uniform weight averaging $\frac{1}{2}(\theta_{\text{base}} + \theta_{25})$ suboptimal? Because isotropic averaging gives equal weight to parameters that $\theta_{\text{base}}$ does not care about and parameters that are critical to $\theta_{\text{base}}$'s diamond/tall decision boundary.

### SOTA Method: Fisher-Information Weighted Model Merging + BatchNorm Exact Recalibration (`FisherSoup`)
Combining **Model Soups** (Wortsman et al., *Model Soups: Averaging Weights of Multiple Fine-Tuned Models Improves Accuracy Without Increasing Inference Time*, ICML 2022) and **Fisher-Weighted Merging** (Matena & Raffel, *Merging Models with Fisher-Weighted Averaging*, NeurIPS 2022):
1. **Diagonal Empirical Fisher Precision Estimation**:
   For each trained checkpoint $\theta^{(m)}$ ($m \in \{\text{base}, 12.5\%, 25\%\}$) on its respective **training-split** cohort $\mathcal{D}_{\text{train}}^{(m)}$, compute the per-parameter diagonal Fisher Information:

$$F_k^{(m)} = \frac{1}{|\mathcal{D}_{\text{train}}^{(m)}|} \sum_{(x, y) \in \mathcal{D}_{\text{train}}^{(m)}} \left( \frac{\partial \mathcal{L}_{\text{BCE}}(x, y; \theta^{(m)})}{\partial \theta_k} \right)^2 + \epsilon$$

   By Laplace's approximation, the log-posterior around $\theta^{(m)}$ is quadratic with precision matrix $\text{diag}(F^{(m)})$.
2. **Closed-Form Maximum A Posteriori (MAP) Parameter Merge**:
   The parameter vector $\theta_{\text{Fisher}}$ that minimizes the sum of Fisher-weighted Mahalanobis distances to all checkpoints is:

$$\theta_{\text{Fisher}, k} = \frac{\sum_{m=1}^M \lambda_m F_k^{(m)} \theta_k^{(m)}}{\sum_{m=1}^M \lambda_m F_k^{(m)}}$$

   If parameter $k$ has high curvature $F_k^{(\text{base})}$ on decorative diamond/tall training examples and near-zero curvature on native tabs, $\theta_{\text{Fisher}, k}$ automatically locks onto $\theta_k^{(\text{base})}$. Conversely, if parameter $k$ is activated only by native tab/button borders ($F_k^{(25\%)} \gg F_k^{(\text{base})}$), $\theta_{\text{Fisher}, k}$ adopts $\theta_k^{(25\%)}$!
3. **Training-Split BatchNorm Running-Stat Recalibration (`BN-Reset`)**:
   After merging weights $\theta_{\text{Fisher}}$, run 1 fast forward-only pass (`< 10 s`, zero gradient steps) over the combined training manifest to recompute exact BatchNorm running means and variances $(\mu_{\text{BN}}, \sigma_{\text{BN}}^2)$ so internal layer activations have zero covariate shift.

---

## 2. Controlled Test Design

- **Pinned Inputs**: Existing trained checkpoints $\theta_{\text{base}}$, $\theta_{12.5}$, and $\theta_{25}$ (zero new training runs required!), training-only manifests for Fisher estimation and BN recalibration, evaluated across all 8 full-screen `T57` case sets (`B405-208`) and the 2 `Sillycon-TTR` cohorts (`B405-205`).
- **Arms**:
  1. `single-checkpoints` (Control): Individual $\theta_{\text{base}}$, $\theta_{12.5}$, and $\theta_{25}$ scorecards.
  2. `uniform-soup-bn`: Isotropic weight average $\theta_{\text{uni}} = (1 - \alpha)\theta_{\text{base}} + \alpha \theta_{25}$ ($\alpha \in \{0.25, 0.50, 0.75\}$) + training-split `BN-Reset`.
  3. `fisher-soup-bn`: Coordinate-wise Fisher-weighted merge of $(\theta_{\text{base}}, \theta_{12.5}, \theta_{25})$ + training-split `BN-Reset`.
- **Decision Rules**:
  - **Supported**: `fisher-soup-bn` (or `uniform-soup-bn`) preserves `4/4` on Standard diamond decoration, `4/4` on tall HCF controls, and `6/6` no-focus abstentions while retaining `>= 16/24` detector-box native selections (`8/8` tabs, `>= 7/8` buttons) in a **single checkpoint with zero inference overhead**.
  - **Contradicted**: Both `uniform-soup-bn` and `fisher-soup-bn` still lose either Standard diamond decoration or native tab/button selections, proving that the checkpoints reside in incompatible loss basins requiring `EXP418-11` (`Null-LoRA`) training.
  - **Inconclusive**: Verify that weight shapes, initialization ancestry, and training-only BN recalibration pass before scoring.
  - **Regression Gate**: Reject any merged checkpoint that loses any retained baseline success or uses development/audit frames during Fisher or BatchNorm computation.

---

## 3. What This Tells `Maximum-mini-TTR`, `Sillycon-TTR`, and `Maximum-mini-NUIAK`

1. **For `Maximum-mini-NUIAK` (`PM08`, `DetectorFocusPolicy.md`)**: Tests whether we can immediately synthesize a passing candidate from the checkpoints we **already spent compute training today** in **under 90 seconds** of CPU/MPS time!
2. **For `Sillycon-TTR` (`MODEL-DIST-02`)**: Produces a single standard `MobileNetV4ConvSmall` weight file (no multi-model fallback or architecture changes) ready for `EXP418-08` (`T62` / `T74`) sub-5MB Core ML palettization.

---

## 4. New Template Contract (`T86`)

Register `T86` in [`scripts/hcf_templates395.py`](file:///Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit/scripts/hcf_templates395.py) at an idle runner boundary:

```python
"T86": (
    {"checkpoints", "trainingManifests", "evaluationReports"},
    {"mergeMode", "mixingWeights", "recalibrateBn"},
    "fisher_model_soup418.run",
    "artifact",
    "diagnostic",
),
```

---

## 5. Implementation Plan and Reference Code

### Step 1 — Fisher-Weighted Model Merger and BN Recalibrator (`scripts/fisher_model_soup418.py`)

```python
"""T86 adapter: Fisher-Weighted Model Soups and BatchNorm Recalibration (PM08)."""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


def compute_diagonal_fisher(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    device: torch.device,
    eps: float = 1e-8,
) -> dict[str, torch.Tensor]:
    """Computes empirical diagonal Fisher information on a training-only DataLoader."""
    model.eval()
    fisher: dict[str, torch.Tensor] = {
        name: torch.zeros_like(param, device=device, dtype=torch.float32)
        for name, param in model.named_parameters()
        if param.requires_grad
    }
    total_samples = 0
    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device).float()
        model.zero_grad(set_to_none=True)
        logits = model(images).squeeze(-1)
        loss = F.binary_cross_entropy_with_logits(logits, labels, reduction="sum")
        loss.backward()
        batch_sz = int(images.shape[0])
        total_samples += batch_sz
        with torch.no_grad():
            for name, param in model.named_parameters():
                if param.requires_grad and param.grad is not None:
                    fisher[name] += (param.grad.detach().float() ** 2) / batch_sz

    denom = float(max(total_samples, 1))
    for name in fisher:
        fisher[name] = (fisher[name] / denom) + eps
    return fisher


@torch.no_grad()
def merge_checkpoints_fisher(
    state_dicts: list[dict[str, torch.Tensor]],
    fishers: list[dict[str, torch.Tensor]],
    lambdas: list[float],
) -> dict[str, torch.Tensor]:
    """Merges compatible state_dicts coordinate-wise weighted by lambda_m * F_k^(m)."""
    assert len(state_dicts) == len(fishers) == len(lambdas) and len(state_dicts) >= 2
    merged: dict[str, torch.Tensor] = {}
    for key in state_dicts[0]:
        t0 = state_dicts[0][key]
        if not t0.is_floating_point():
            merged[key] = t0.clone()
            continue
        if key in fishers[0]:
            num = torch.zeros_like(t0, dtype=torch.float32)
            den = torch.zeros_like(t0, dtype=torch.float32)
            for sd, fi, lam in zip(state_dicts, fishers, lambdas):
                weight = float(lam) * fi[key].to(t0.device, dtype=torch.float32)
                num += weight * sd[key].to(t0.device, dtype=torch.float32)
                den += weight
            merged[key] = (num / den.clamp_min(1e-12)).to(dtype=t0.dtype)
        else:
            # Running mean/var buffers are recomputed by recalibrate_batchnorm_stats
            total_lam = sum(lambdas)
            acc = sum(float(lam) * sd[key].float() for sd, lam in zip(state_dicts, lambdas)) / max(total_lam, 1e-8)
            merged[key] = acc.to(dtype=t0.dtype)
    return merged


@torch.no_grad()
def recalibrate_batchnorm_stats(
    model: nn.Module,
    training_loader: torch.utils.data.DataLoader,
    device: torch.device,
) -> None:
    """Recomputes exact BatchNorm running_mean and running_var on the combined training set."""
    for module in model.modules():
        if isinstance(module, nn.modules.batchnorm._BatchNorm):
            module.reset_running_stats()
            module.momentum = None  # Cumulative moving average
    model.train()
    for images, _ in training_loader:
        model(images.to(device))
    model.eval()
```

### Step 2 — Verification
- Create `scripts/test_fisher_model_soup418.py` to verify that when $F^{(1)}$ dominates on subset $A$ of coordinates and $F^{(2)}$ dominates on subset $B$, `merge_checkpoints_fisher` preserves $\theta^{(1)}_A$ and $\theta^{(2)}_B$ to within `< 1e-5`, and rejects any non-training manifest during Fisher or BatchNorm recalibration.
